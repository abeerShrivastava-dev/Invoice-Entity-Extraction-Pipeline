"""Invoice entity extraction (vendor, billing address, invoice number, total).

Pipeline
  1. Multi-pass OCR (plain + inverted grayscale, two page-segmentation modes),
     merged by box overlap. No hard binarization: it destroys small text, and
     the inverted pass recovers white-on-colour text (banners, total boxes).
  2. Rebuild lines -> column segments from word boxes.
  3. Locate each entity from its own anchors (labels + geometry).

Requires: opencv-python, numpy, pillow, pytesseract (+ the Tesseract binary).
"""
import difflib
import re
from collections import Counter
from dataclasses import dataclass
from statistics import median

import cv2
import numpy as np
import pytesseract
from PIL import Image

TARGET_WIDTH = 2400   # upscale target for OCR (capped by MAX_SCALE)
MAX_SCALE = 6.0
MIN_CONF = 30
COLUMN_GAP = 2.0      # gap (x word height) that splits a line into columns
OCR_PSMS = (11, 6)    # sparse text + single block; results are merged

NOT_FOUND = [0, 0, 0, 0]


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------
@dataclass(eq=False)
class Word:
  text: str
  x0: float
  y0: float
  x1: float
  y1: float
  conf: float = 0.0

  @property
  def h(self):
    return self.y1 - self.y0

  @property
  def yc(self):
    return (self.y0 + self.y1) / 2


@dataclass(eq=False)
class Seg:
  """A run of words on one line with no large horizontal gap (one 'cell')."""

  words: list

  def __post_init__(self):
    self.text = ' '.join(w.text for w in self.words)
    self.x0 = min(w.x0 for w in self.words)
    self.y0 = min(w.y0 for w in self.words)
    self.x1 = max(w.x1 for w in self.words)
    self.y1 = max(w.y1 for w in self.words)
    self.h = median(w.h for w in self.words)
    self.yc = (self.y0 + self.y1) / 2


def _box_of(items):
  return [int(min(i.x0 for i in items)), int(min(i.y0 for i in items)),
          int(max(i.x1 for i in items)), int(max(i.y1 for i in items))]


def _span_box(seg, start, end):
  """Box of the words of `seg` that overlap char span [start, end)."""
  pos, hit = 0, []
  for w in seg.words:
    w0, w1 = pos, pos + len(w.text)
    if w0 < end and w1 > start:
      hit.append(w)
    pos = w1 + 1
  return _box_of(hit or [seg])


def _norm(t):
  return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', t.lower())).strip()


# --------------------------------------------------------------------------
# OCR + layout reconstruction
# --------------------------------------------------------------------------
def _overlap(a, b):
  ix = min(a.x1, b.x1) - max(a.x0, b.x0)
  iy = min(a.y1, b.y1) - max(a.y0, b.y0)
  if ix <= 0 or iy <= 0:
    return 0.0
  inter = ix * iy
  union = (a.x1 - a.x0) * a.h + (b.x1 - b.x0) * b.h - inter
  return inter / union if union > 0 else 0.0


def _ocr_pass(gray, scale, psm, off_x=0.0, off_y=0.0, pad=0):
  d = pytesseract.image_to_data(
      gray, config=f'--oem 3 --psm {psm}', output_type=pytesseract.Output.DICT)
  words = []
  for i, raw in enumerate(d['text']):
    text = raw.strip()
    try:
      conf = float(d['conf'][i])
    except ValueError:
      conf = -1
    if conf < MIN_CONF or not re.search(r'[A-Za-z0-9#$€£₹%]', text):
      continue
    x, y = d['left'][i] - pad, d['top'][i] - pad
    w, h = d['width'][i], d['height'][i]
    words.append(Word(text, x / scale + off_x, y / scale + off_y,
                      (x + w) / scale + off_x, (y + h) / scale + off_y, conf))
  return words


def _dark_blocks(gray, max_blocks=12):
  """Solid dark regions (banners, filled total boxes) that hold light text."""
  h, w = gray.shape
  k = max(3, w // 120)
  dark = (gray < 140).astype(np.uint8) * 255
  opened = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
  n, _, stats, _ = cv2.connectedComponentsWithStats(opened)
  blocks = []
  for i in range(1, n):
    x, y, bw, bh, area = stats[i]
    if (area >= 0.002 * h * w and bw >= 6 * k and bh >= 3 * k
        and area / float(bw * bh) >= 0.4 and bw * bh <= 0.9 * h * w):
      blocks.append((area, x, y, bw, bh))
  return [b[1:] for b in sorted(blocks, reverse=True)[:max_blocks]]


def _merge_passes(candidates):
  """Cluster overlapping words from different passes; majority text wins."""
  clusters = []
  for w in sorted(candidates, key=lambda w: -w.conf):
    for c in clusters:
      if _overlap(w, c[0]) >= 0.4:
        c.append(w)
        break
    else:
      clusters.append([w])
  merged = []
  for c in clusters:
    votes = Counter(w.text for w in c)
    top = max(votes.values())
    merged.append(max((w for w in c if votes[w.text] == top),
                      key=lambda w: w.conf))
  return merged


LABEL_VOCAB = ['invoice', 'subtotal', 'total', 'amount', 'balance', 'payable',
               'number', 'billed', 'grand']


def _canonicalize(words):
  """Repair OCR damage to label words ('Inveice' -> 'invoice')."""
  for w in words:
    core = re.sub(r'[^A-Za-z]', '', w.text)
    if len(core) < 5 or core.lower() in LABEL_VOCAB:
      continue
    m = difflib.get_close_matches(core.lower(), LABEL_VOCAB, n=1, cutoff=0.76)
    if m:
      w.text = w.text.replace(core, m[0].capitalize() if core[0].isupper()
                              else m[0])
  return words


def _ocr_words(pil_img):
  gray0 = cv2.cvtColor(np.array(pil_img.convert('RGB')), cv2.COLOR_RGB2GRAY)
  scale = min(MAX_SCALE, max(1.0, TARGET_WIDTH / gray0.shape[1]))
  gray = (cv2.resize(gray0, None, fx=scale, fy=scale,
                     interpolation=cv2.INTER_CUBIC) if scale > 1.0 else gray0)

  candidates = []
  for img in (gray, 255 - gray):          # normal + inverted (light-on-dark)
    for psm in OCR_PSMS:
      candidates.extend(_ocr_pass(img, scale, psm))

  # Light text on solid dark blocks: OCR each block as its own inverted crop.
  for x, y, bw, bh in _dark_blocks(gray0):
    x0, y0 = max(0, x - 2), max(0, y - 2)
    crop = gray0[y0:y + bh + 2, x0:x + bw + 2]
    crop = 255 - crop
    if scale > 1.0:
      crop = cv2.resize(crop, None, fx=scale, fy=scale,
                        interpolation=cv2.INTER_CUBIC)
    pad = 20
    crop = cv2.copyMakeBorder(crop, pad, pad, pad, pad, cv2.BORDER_CONSTANT,
                              value=int(np.median(crop)))
    for psm in OCR_PSMS:
      candidates.extend(_ocr_pass(crop, scale, psm, x0, y0, pad))

  return _canonicalize(_merge_passes(candidates))


def _build_segments(words):
  """Group words into lines by vertical centre, then split into columns."""
  lines = []
  for w in sorted(words, key=lambda w: w.yc):
    if lines:
      cur = lines[-1]
      mean_yc = sum(x.yc for x in cur) / len(cur)
      med_h = median(x.h for x in cur)
      if abs(w.yc - mean_yc) <= 0.45 * max(w.h, med_h):
        cur.append(w)
        continue
    lines.append([w])

  segs = []
  for line in lines:
    line.sort(key=lambda w: w.x0)
    h = median(w.h for w in line)
    groups = [[line[0]]]
    for prev, w in zip(line, line[1:]):
      if w.x0 - prev.x1 > COLUMN_GAP * h:
        groups.append([w])
      else:
        groups[-1].append(w)
    segs.extend(Seg(g) for g in groups)
  return sorted(segs, key=lambda s: (s.y0, s.x0))


def _right_of(seg, segs):
  c = [s for s in segs if s is not seg
       and abs(s.yc - seg.yc) <= 0.6 * max(s.h, seg.h)
       and s.x0 >= seg.x1 - 0.5 * seg.h]
  return sorted(c, key=lambda s: s.x0)


def _below(seg, segs, max_gap=2.0):
  c = [s for s in segs if s is not seg
       and -0.3 * seg.h <= s.y0 - seg.y1 <= max_gap * seg.h
       and s.x1 >= seg.x0 - seg.h and s.x0 <= seg.x1 + seg.h]
  return sorted(c, key=lambda s: (s.y0, s.x0))


# --------------------------------------------------------------------------
# Invoice number
# --------------------------------------------------------------------------
_ID = r'(?=[A-Z0-9\-/]*\d)([A-Z0-9][A-Z0-9\-/]{1,24})'   # must contain a digit
_ID_TOKEN = re.compile(_ID, re.I)
_INV_LABEL = r'(?:invoice|inv)\s*(?:no\.?|number|num\.?|#|id)'

INV_PRIMARY = re.compile(r'\b' + _INV_LABEL + r'\s*[:#\-.]*\s*' + _ID, re.I)
INV_LABEL_ONLY = re.compile(r'\b' + _INV_LABEL + r'\s*[:#\-.]*\s*$', re.I)
INV_SECONDARY = [
    re.compile(r'\b(?:no|nr)\s*[:.#]\s*' + _ID, re.I),      # "NO: INV-123"
    re.compile(r'\b(?:invoice|inv)\s*[:#]\s*' + _ID, re.I),
    re.compile(r'\binvoice\s+' + _ID, re.I),                # "INVOICE 12345"
    re.compile(r'\b(?:order|receipt|ref(?:erence)?)\s*(?:no\.?|number|#)'
               r'\s*[:#\-.]*\s*' + _ID, re.I),
]


def _extract_invoice_number(segs):
  for seg in segs:
    m = INV_PRIMARY.search(seg.text)
    if m:
      return m.group(1).strip('-/'), _span_box(seg, m.start(1), m.end(1))

  for seg in segs:
    if INV_LABEL_ONLY.search(seg.text):
      for nb in _right_of(seg, segs)[:2] + _below(seg, segs)[:2]:
        m = _ID_TOKEN.search(nb.text)
        if m:
          return m.group(0).strip('-/'), _span_box(nb, m.start(), m.end())

  for pat in INV_SECONDARY:
    for seg in segs:
      m = pat.search(seg.text)
      if m:
        return m.group(1).strip('-/'), _span_box(seg, m.start(1), m.end(1))
  return 'Not Found', NOT_FOUND


# --------------------------------------------------------------------------
# Total
# --------------------------------------------------------------------------
AMOUNT = re.compile(
    r'(?<![\w/])(?P<cur>[$€£₹]|Rs\.?|INR|USD|EUR|GBP)?\s*'
    r'(?P<num>\d{1,3}(?:,\d{2,3})+(?:\.\d{1,2})?'   # 1,234.50 / 1,23,456
    r'|\d{1,3}(?: \d{3})+\.\d{2}'                     # 1 234.50 (space thousands)
    r'|\d+\.\d{2}|\d+)(?![\w/])', re.I)

TOTAL_TIERS = [  # highest priority first
    re.compile(r'\b(?:grand\s*total|total\s*(?:amount\s*)?(?:due|payable)'
               r'|amount\s*(?:due|payable)|balance\s*due|invoice\s*total'
               r'|total\s*amount|net\s*payable)\b', re.I),
    re.compile(r'(?<!sub)(?<!sub\s)\btotal\b'
               r'(?!\s*(?:tax|gst|vat|discount|qty|quantity))', re.I),
    re.compile(r'\bsub\s*total\b', re.I),
]


def _is_precise(m):
  num = m.group('num')
  return bool(m.group('cur')) or '.' in num or ',' in num or ' ' in num


def _find_amount(text, strict=False):
  fallback = None
  for m in AMOUNT.finditer(text):
    if _is_precise(m):
      return m
    if not strict and fallback is None:
      fallback = m
  return fallback


def _fmt_amount(m):
  cur, num = (m.group('cur') or '').strip(), m.group('num')
  if not cur:
    return num
  return f'{cur} {num}' if cur[-1].isalpha() or cur.endswith('.') \
      else f'{cur}{num}'


def _amount_near(seg, after_label, segs, allow_below, label_end=0):
  m = _find_amount(after_label)
  if m:
    return (_fmt_amount(m),
            _span_box(seg, label_end + m.start(), label_end + m.end()))
  for nb in _right_of(seg, segs)[:3]:
    m = _find_amount(nb.text)
    if m:
      return _fmt_amount(m), _span_box(nb, m.start(), m.end())
  if allow_below:
    for nb in _below(seg, segs, max_gap=2.5)[:2]:
      m = _find_amount(nb.text, strict=True)
      if m:
        return _fmt_amount(m), _span_box(nb, m.start(), m.end())
  return None


TAX_LABEL = re.compile(
    r'\b(?:sales\s*tax|tax|gst|vat|igst)\b(?!\s*(?:invoice|id|rate|code|no))',
    re.I)


def _to_float(text):
  m = _find_amount(text)
  return float(re.sub(r'[, ]', '', m.group('num'))) if m else None


def _labeled_amount(segs, pat, allow_below=False):
  for seg in reversed(segs):
    m = pat.search(seg.text)
    if m:
      found = _amount_near(seg, seg.text[m.end():], segs, allow_below, m.end())
      if found:
        return _to_float(found[0])
  return None


def _reread_amount(gray0, box):
  """Re-OCR a value box zoomed in, digits-only, both polarities."""
  x0, y0, x1, y1 = box
  pad = max(3, int(0.5 * (y1 - y0)))
  crop = gray0[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad]
  if crop.size == 0:
    return []
  base = float(np.clip(48.0 / max(1, y1 - y0), 2.0, 12.0))
  readings = []
  for img in (crop, 255 - crop):
    for z in (0.75 * base, base, 1.5 * base):
      big = cv2.resize(img, None, fx=z, fy=z, interpolation=cv2.INTER_CUBIC)
      big = cv2.copyMakeBorder(big, 20, 20, 20, 20, cv2.BORDER_CONSTANT,
                               value=int(np.median(big)))
      txt = pytesseract.image_to_string(
          big, config='--oem 3 --psm 7 '
          '-c tessedit_char_whitelist=0123456789$€£₹.,').strip()
      m = _find_amount(txt, strict=True)
      if m:
        readings.append(float(re.sub(r'[, ]', '', m.group('num'))))
  return readings


def _settle_total(value, box, gray0, segs):
  """Pick the most trustworthy reading of the total.

  Candidates are only real OCR readings (original + zoomed re-reads). The
  subtotal + tax identity breaks ties; it never invents a number.
  """
  orig = _to_float(value)
  if orig is None or box == NOT_FOUND:
    return value
  readings = [orig] + _reread_amount(gray0, box)
  sub = _labeled_amount(segs, TOTAL_TIERS[2])
  tax = _labeled_amount(segs, TAX_LABEL)
  if sub is not None and tax is not None:
    target = round(sub + tax, 2)
    if any(abs(r - target) < 0.011 for r in readings):
      best = target
      return _restyle(value, best)
  best, votes = Counter(round(r, 2) for r in readings).most_common(1)[0]
  return value if votes < 2 and best != round(orig, 2) else _restyle(value, best)


def _restyle(original, number):
  """Format `number` like the original string (currency, separators)."""
  m = _find_amount(original)
  cur = (m.group('cur') or '').strip() if m else ''
  old = m.group('num') if m else ''
  decimals = len(old.split('.')[1]) if '.' in old else 0
  body = f'{number:,.{decimals}f}'
  if ' ' in old:
    body = body.replace(',', ' ')
  elif ',' not in old:
    body = body.replace(',', '')
  if not cur:
    return body
  return f'{cur} {body}' if cur[-1].isalpha() or cur.endswith('.') \
      else f'{cur}{body}'


def _extract_total(segs, img_h):
  bottom_up = list(reversed(segs))
  for tier, pat in enumerate(TOTAL_TIERS):
    for seg in bottom_up:
      m = pat.search(seg.text)
      if not m:
        continue
      found = _amount_near(seg, seg.text[m.end():], segs, tier == 0, m.end())
      if found:
        return found

  best = None  # fallback: largest precise amount in lower 60% of the page
  for seg in segs:
    if seg.yc < 0.4 * img_h:
      continue
    for m in AMOUNT.finditer(seg.text):
      if _is_precise(m):
        val = float(re.sub(r'[, ]', '', m.group('num')))
        if best is None or val > best[0]:
          best = (val, m, seg)
  if best:
    _, m, seg = best
    return _fmt_amount(m), _span_box(seg, m.start(), m.end())
  return 'Not Found', NOT_FOUND


# --------------------------------------------------------------------------
# Vendor + billing address
# --------------------------------------------------------------------------
BILL_TO = re.compile(
    r'^(?:(?:bill(?:ed)?|sold|invoice)\s*t[o0]\b|t[o0]\s*:)\s*[:\-]?\s*', re.I)
FROM_LABEL = re.compile(
    r'^(?:from|seller|vendor|supplier|issued\s*by|sold\s*by)\b\s*[:\-]?\s*',
    re.I)
STOP_LINE = re.compile(
    r'\b(?:ship(?:ped)?\s*to|invoice|date|due|terms|p\.?o\.?|description'
    r'|qty|quantity|item|rate|amount|total|payment|from)\b', re.I)
VENDOR_NOISE = re.compile(
    r'\b(?:invoice|date|due|phone|tel|fax|e-?mail|gstin|vat|bill\s*to'
    r'|ship\s*to|page|original|receipt|logo|zip)\b|@|www\.|https?:', re.I)
ADDRESS_LIKE = re.compile(
    r'^\d+[\s,]|\b\d{4,}\b|\b(?:street|st|road|rd|ave|avenue|blvd|lane|ln'
    r'|drive|dr|suite|floor|city|state|country|box)\b[.,]?', re.I)
DOMAIN_LIKE = re.compile(r'^\S+\.(?:com|net|org|io|co|in)\b', re.I)
COMPANY_SUFFIX = re.compile(
    r'\b(?:inc|llc|ltd|limited|corp|corporation|co|company|gmbh|pvt|plc|llp'
    r'|lp|ag|enterprises|industries|solutions|technologies|services|group'
    r'|traders|stores|agency|studio)\b', re.I)


BILL_TO_LOOSE = re.compile(
    r'^(?!ship|deliver|attn)[A-Za-z]{3,9}\s+to\s*:\s*|^bill(?:ed)?\s*:?\s*$',
    re.I)


def _label_match(segs, regex, need_colon_or_empty=False):
  for seg in segs:
    t = seg.text.strip()
    m = regex.match(t)
    if not m:
      continue
    rest = t[m.end():].strip()
    if need_colon_or_empty and rest and ':' not in t[:m.end()]:
      continue
    return seg, rest
  return None, ''


def _is_vendor_candidate(seg):
  t = seg.text.strip()
  if len(t) < 3 or sum(c.isalpha() for c in t) < 3:
    return False
  if VENDOR_NOISE.search(t) or DOMAIN_LIKE.match(t) or ADDRESS_LIKE.search(t):
    return False
  return sum(c.isdigit() for c in t) / len(t) <= 0.25


def _repeat_count(cand, segs):
  n = _norm(cand.text)
  if len(n) < 5:
    return 0
  return sum(1 for s in segs if s is not cand and abs(s.y0 - cand.y0) > cand.h
             and n in _norm(s.text))


def _stack_lines(cands):
  """Join vertically adjacent, similarly sized, aligned lines (logo text
  such as 'Future' / 'Graphics') into one candidate."""
  out = []
  for s in sorted(cands, key=lambda s: (s.y0, s.x0)):
    if out:
      prev = out[-1]
      small, big = sorted((prev.h, s.h))
      if (small >= 0.7 * big and 0 <= s.y0 - prev.y1 <= 0.8 * prev.h
          and abs(s.x0 - prev.x0) <= 2 * prev.h):
        out[-1] = Seg(prev.words + s.words)
        continue
    out.append(s)
  return out


def _pick_vendor(segs, img_h, limit_y):
  top = _stack_lines([s for s in segs if s.y1 <= 0.45 * img_h
                      and s.y0 < limit_y and _is_vendor_candidate(s)])
  if not top:
    return None
  max_h = max(s.h for s in top)

  def score(s):
    return (s.h / max_h + (1.0 if COMPANY_SUFFIX.search(s.text) else 0.0)
            + 1.5 * min(_repeat_count(s, segs), 1))

  best = max(top, key=lambda s: (round(score(s), 2), -s.y0))
  # A logo often OCRs as a prefix of the full name printed elsewhere
  # ("Future" -> "Future Graphics"): prefer the fuller, name-like string.
  nb = _norm(best.text)
  longer = [s for s in segs if s is not best and _norm(s.text).startswith(nb)
            and len(_norm(s.text)) > len(nb) and len(s.text.split()) <= 6
            and not any(c.isdigit() for c in s.text)]
  return min(longer, key=lambda s: s.y0) if longer else best


def _aligned(s, start, tol):
  return abs(s.x0 - start.x0) <= tol or abs(s.x1 - start.x1) <= tol


def _collect_block(start, segs, first_text='', max_lines=6, first_gap=2.6):
  """Walk down the column under `start` (left- or right-aligned)."""
  lines = [first_text] if first_text else []
  used = [start]
  last = start
  tol = 2.5 * start.h
  while len(lines) < max_lines:
    limit = (first_gap if len(used) == 1 else 1.6) * last.h
    cands = [s for s in segs if s not in used
             and s.y0 >= last.y1 - 0.3 * last.h
             and _aligned(s, start, tol)
             and (s.y0 - last.y1) <= limit]
    if not cands:
      break
    nxt = min(cands, key=lambda s: (s.y0, s.x0))
    if STOP_LINE.search(nxt.text):
      break
    lines.append(nxt.text)
    used.append(nxt)
    last = nxt
  return lines, used


def _extract_party(segs, img_h):
  bill_seg, bill_rest = _label_match(segs, BILL_TO)
  if not bill_seg:  # label damaged by OCR ("invoice to:" -> "woke to:")
    bill_seg, bill_rest = _label_match(segs, BILL_TO_LOOSE)
  from_seg, from_rest = _label_match(segs, FROM_LABEL, need_colon_or_empty=True)

  # ---- vendor ----
  vendor = ('Unknown Vendor', NOT_FOUND)
  vendor_seg, vendor_block = None, []
  if from_seg:
    lines, used = _collect_block(from_seg, segs, first_text=from_rest,
                                 max_lines=4)
    if lines:
      name_seg = used[0] if from_rest else (used[1] if len(used) > 1 else None)
      if name_seg:
        vendor = (lines[0], _box_of([name_seg]))
        vendor_block = used
  else:
    limit_y = bill_seg.y0 if bill_seg else float('inf')
    vendor_seg = _pick_vendor(segs, img_h, limit_y)
    if vendor_seg:
      vendor = (vendor_seg.text.strip(), _box_of([vendor_seg]))
      _, vendor_block = _collect_block(vendor_seg, segs, max_lines=4,
                                       first_gap=1.6)

  # ---- billing address ----
  address = ('Address Not Found', NOT_FOUND)
  if bill_seg:
    lines, used = _collect_block(bill_seg, segs, first_text=bill_rest)
    body = used if bill_rest else used[1:]
    if lines and body:
      address = (', '.join(lines), _box_of(body))
  else:
    # Unlabeled layout: the customer is the first name-like block that is not
    # the vendor's own block (or the vendor's logo text).
    vn = _norm(vendor[0])
    excluded = set(map(id, vendor_block))
    # The vendor's name is often printed again with its own address block.
    for s in segs:
      if (vn and s is not vendor_seg and s.y1 <= 0.6 * img_h
          and vn in _norm(s.text)):
        excluded.update(id(b) for b in _collect_block(
            s, segs, max_lines=4, first_gap=1.6)[1])
    cands = [s for s in segs
             if id(s) not in excluded and s.y1 <= 0.6 * img_h
             and _is_vendor_candidate(s)
             and not (vn and _norm(s.text) and _norm(s.text) in vn)]
    if cands:
      first = min(cands, key=lambda s: (s.y0, s.x0))
      lines, used = _collect_block(first, segs, max_lines=5)
      address = (', '.join([first.text] + lines), _box_of(used))
  return vendor, address


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def extract_invoice_data(image_path_or_pil):
  """Return {field: {'value': str, 'coordinates': [x0, y0, x1, y1]}}.

  Coordinates are in the original image's pixel space.
  """
  image = (Image.open(image_path_or_pil)
           if isinstance(image_path_or_pil, str) else image_path_or_pil)
  img_h = image.size[1]

  words = _ocr_words(image)
  segs = _build_segments(words) if words else []

  inv_val, inv_box = _extract_invoice_number(segs)
  total_val, total_box = _extract_total(segs, img_h)
  gray0 = cv2.cvtColor(np.array(image.convert('RGB')), cv2.COLOR_RGB2GRAY)
  total_val = _settle_total(total_val, total_box, gray0, segs)
  (vendor_val, vendor_box), (addr_val, addr_box) = _extract_party(segs, img_h)

  return {
      'vendor_name': {'value': vendor_val, 'coordinates': vendor_box},
      'company_address': {'value': addr_val, 'coordinates': addr_box},
      'invoice_number': {'value': inv_val, 'coordinates': inv_box},
      'total': {'value': total_val, 'coordinates': total_box},
  }


if __name__ == '__main__':
  import json
  import sys

  print(json.dumps(extract_invoice_data(sys.argv[1]), indent=2))
