# # # # # # # # # import re
# # # # # # # # # import cv2
# # # # # # # # # import numpy as np
# # # # # # # # # import pytesseract
# # # # # # # # # from PIL import Image

# # # # # # # # # # Configure tesseract path if necessary (uncomment if on Windows)
# # # # # # # # # # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# # # # # # # # # def extract_invoice_data(image_path_or_pil):
# # # # # # # # #   """Processes an invoice image, performs OCR with bounding boxes,

# # # # # # # # #   and extracts Vendor Name, Company Address, Invoice Number, and Total using
# # # # # # # # #   Regex.
# # # # # # # # #   """
# # # # # # # # #   if isinstance(image_path_or_pil, str):
# # # # # # # # #     image = Image.open(image_path_or_pil)
# # # # # # # # #   else:
# # # # # # # # #     image = image_path_or_pil

# # # # # # # # #   # Convert PIL image to OpenCV format
# # # # # # # # #   img_cv = np.array(image)
# # # # # # # # #   gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

# # # # # # # # #   # Run Tesseract OCR to get text data with bounding boxes (word-level)
# # # # # # # # #   ocr_data = pytesseract.image_to_data(
# # # # # # # # #       gray, output_type=pytesseract.Output.DICT
# # # # # # # # #   )

# # # # # # # # #   full_text_lines = []
# # # # # # # # #   word_boxes = []

# # # # # # # # #   n_boxes = len(ocr_data['text'])
# # # # # # # # #   for i in range(n_boxes):
# # # # # # # # #     word = ocr_data['text'][i].strip()
# # # # # # # # #     if word:
# # # # # # # # #       x, y, w, h = (
# # # # # # # # #           ocr_data['left'][i],
# # # # # # # # #           ocr_data['top'][i],
# # # # # # # # #           ocr_data['width'][i],
# # # # # # # # #           ocr_data['height'][i],
# # # # # # # # #       )
# # # # # # # # #       word_boxes.append(
# # # # # # # # #           {
# # # # # # # # #               'text': word,
# # # # # # # # #               'coordinates': [
# # # # # # # # #                   int(x),
# # # # # # # # #                   int(y),
# # # # # # # # #                   int(x + w),
# # # # # # # # #                   int(y + h),
# # # # # # # # #               ],  # [xmin, ymin, xmax, ymax]
# # # # # # # # #           }
# # # # # # # # #       )
# # # # # # # # #       full_text_lines.append(word)

# # # # # # # # #   full_text = ' '.join(full_text_lines)

# # # # # # # # #   # --- REGEX EXTRACTION LOGIC ---

# # # # # # # # #   # 1. Invoice Number Pattern (e.g., INV-2023-001, Invoice # 12345)
# # # # # # # # #   inv_pattern = r'(?:Invoice\s*(?:No|Number|#)?[:\s]*)?([A-Z0-9\-]{4,20})'
# # # # # # # # #   inv_match = re.search(
# # # # # # # # #       r'(?:INV|Invoice)[\s\-#]*([A-Z0-9\-]+)', full_text, re.IGNORECASE
# # # # # # # # #   )
# # # # # # # # #   invoice_number = inv_match.group(0) if inv_match else 'Not Found'
# # # # # # # # #   inv_coords = get_coordinates_for_text(invoice_number, word_boxes)

# # # # # # # # #   # 2. Total Amount Pattern (e.g., Total: $150.00, Grand Total 1,200.50)
# # # # # # # # #   total_pattern = r'(?:Total|Amount Due|Balance Due)[:\s]*\$?([\d,]+\.\d{2})'
# # # # # # # # #   total_match = re.search(total_pattern, full_text, re.IGNORECASE)
# # # # # # # # #   total_value = total_match.group(0) if total_match else 'Not Found'
# # # # # # # # #   total_coords = get_coordinates_for_text(total_value, word_boxes)

# # # # # # # # #   # 3. Vendor Name & Address (Heuristic: usually located in the top section of the receipt)
# # # # # # # # #   # Taking top-most text blocks for vendor name and address simulation
# # # # # # # # #   top_blocks = [wb for wb in word_boxes if wb['coordinates'][1] < 150]
# # # # # # # # #   vendor_name = (
# # # # # # # # #       ' '.join([b['text'] for b in top_blocks[:3]])
# # # # # # # # #       if top_blocks
# # # # # # # # #       else 'Unknown Vendor'
# # # # # # # # #   )
# # # # # # # # #   vendor_coords = (
# # # # # # # # #       top_blocks[0]['coordinates'] if top_blocks else [0, 0, 0, 0]
# # # # # # # # #   )

# # # # # # # # #   company_address = (
# # # # # # # # #       ' '.join([b['text'] for b in top_blocks[3:10]])
# # # # # # # # #       if len(top_blocks) > 3
# # # # # # # # #       else 'Address Not Found'
# # # # # # # # #   )
# # # # # # # # #   address_coords = (
# # # # # # # # #       top_blocks[3]['coordinates'] if len(top_blocks) > 3 else [0, 0, 0, 0]
# # # # # # # # #   )

# # # # # # # # #   # Constructing the structured JSON output
# # # # # # # # #   structured_output = {
# # # # # # # # #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# # # # # # # # #       'company_address': {
# # # # # # # # #           'value': company_address,
# # # # # # # # #           'coordinates': address_coords,
# # # # # # # # #       },
# # # # # # # # #       'invoice_number': {
# # # # # # # # #           'value': invoice_number,
# # # # # # # # #           'coordinates': inv_coords,
# # # # # # # # #       },
# # # # # # # # #       'total': {'value': total_value, 'coordinates': total_coords},
# # # # # # # # #   }

# # # # # # # # #   return structured_output


# # # # # # # # # def get_coordinates_for_text(search_text, word_boxes):
# # # # # # # # #   """Helper to aggregate coordinates for matched text fragments."""
# # # # # # # # #   matched_boxes = [wb for wb in word_boxes if wb['text'] in search_text]
# # # # # # # # #   if not matched_boxes:
# # # # # # # # #     return [0, 0, 0, 0]

# # # # # # # # #   xmin = min([b['coordinates'][0] for b in matched_boxes])
# # # # # # # # #   ymin = min([b['coordinates'][1] for b in matched_boxes])
# # # # # # # # #   xmax = max([b['coordinates'][2] for b in matched_boxes])
# # # # # # # # #   ymax = max([b['coordinates'][3] for b in matched_boxes])
# # # # # # # # #   return [xmin, ymin, xmax, ymax]

# # # # # # # # import re
# # # # # # # # import cv2
# # # # # # # # import numpy as np
# # # # # # # # import pytesseract
# # # # # # # # from PIL import Image

# # # # # # # # # Configure tesseract path if necessary (uncomment if on Windows)
# # # # # # # # # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# # # # # # # # def extract_invoice_data(image_path_or_pil):
# # # # # # # #   """Processes an invoice image, performs OCR with bounding boxes,

# # # # # # # #   and extracts Vendor Name, Company Address, Invoice Number, and Total using
# # # # # # # #   refined Regex patterns.
# # # # # # # #   """
# # # # # # # #   if isinstance(image_path_or_pil, str):
# # # # # # # #     image = Image.open(image_path_or_pil)
# # # # # # # #   else:
# # # # # # # #     image = image_path_or_pil

# # # # # # # #   # Convert PIL image to OpenCV format
# # # # # # # #   img_cv = np.array(image)
# # # # # # # #   gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

# # # # # # # #   # Run Tesseract OCR to get detailed word-level layout data
# # # # # # # #   ocr_data = pytesseract.image_to_data(
# # # # # # # #       gray, output_type=pytesseract.Output.DICT
# # # # # # # #   )

# # # # # # # #   word_boxes = []
# # # # # # # #   n_boxes = len(ocr_data['text'])

# # # # # # # #   for i in range(n_boxes):
# # # # # # # #     word = ocr_data['text'][i].strip()
# # # # # # # #     if word:
# # # # # # # #       x, y, w, h = (
# # # # # # # #           ocr_data['left'][i],
# # # # # # # #           ocr_data['top'][i],
# # # # # # # #           ocr_data['width'][i],
# # # # # # # #           ocr_data['height'][i],
# # # # # # # #       )
# # # # # # # #       word_boxes.append(
# # # # # # # #           {
# # # # # # # #               'text': word,
# # # # # # # #               'coordinates': [
# # # # # # # #                   int(x),
# # # # # # # #                   int(y),
# # # # # # # #                   int(x + w),
# # # # # # # #                   int(y + h),
# # # # # # # #               ],  # [xmin, ymin, xmax, ymax]
# # # # # # # #           }
# # # # # # # #       )

# # # # # # # #   # Reconstruct line text for context searching
# # # # # # # #   full_text_lines = []
# # # # # # # #   current_line_y = -1
# # # # # # # #   current_line_words = []

# # # # # # # #   # Sort word boxes top-to-bottom, left-to-right loosely by y coordinate
# # # # # # # #   sorted_boxes = sorted(word_boxes, key=lambda b: (b['coordinates'][1] // 15, b['coordinates'][0]))
  
# # # # # # # #   full_text = ' '.join([b['text'] for b in sorted_boxes])

# # # # # # # #   # --- REFINED EXTRACTION LOGIC ---

# # # # # # # #   # 1. Invoice Number Extraction (Looking for numbers following labels like 'Invoice no', 'Invoice #', etc.)
# # # # # # # #   invoice_number = 'Not Found'
# # # # # # # #   inv_coords = [0, 0, 0, 0]
  
# # # # # # # #   inv_match = re.search(
# # # # # # # #       r'(?:Invoice\s*(?:no|number|num|#)|INV[\s\-#]*)[^\w]*([A-Z0-9\-]{3,15})',
# # # # # # # #       full_text,
# # # # # # # #       re.IGNORECASE,
# # # # # # # #   )
# # # # # # # #   if inv_match:
# # # # # # # #     invoice_number = inv_match.group(1)
# # # # # # # #     inv_coords = get_coordinates_for_text(invoice_number, sorted_boxes)

# # # # # # # #   # 2. Total Amount Extraction (Catching 'Invoice total', 'Grand Total', 'TOTAL', etc.)
# # # # # # # #   total_value = 'Not Found'
# # # # # # # #   total_coords = [0, 0, 0, 0]

# # # # # # # #   total_match = re.search(
# # # # # # # #       r'(?:Invoice\s*total|Grand\s*total|Total|Balance\s*due)[:\s]*[\$]?\s*([\d,]+\.\d{2})',
# # # # # # # #       full_text,
# # # # # # # #       re.IGNORECASE,
# # # # # # # #   )
# # # # # # # #   if total_match:
# # # # # # # #     total_value = total_match.group(1)
# # # # # # # #     total_coords = get_coordinates_for_text(total_value, sorted_boxes)

# # # # # # # #   # 3. Vendor Name & Address Extraction (Top section blocks)
# # # # # # # #   top_blocks = [wb for wb in sorted_boxes if wb['coordinates'][1] < 200]
  
# # # # # # # #   # Filter out generic header words like 'TAX', 'INVOICE', 'LOGO'
# # # # # # # #   filtered_vendor_blocks = [
# # # # # # # #       b for b in top_blocks if b['text'].upper() not in ['TAX', 'INVOICE', 'LOGO']
# # # # # # # #   ]

# # # # # # # #   vendor_name = (
# # # # # # # #       ' '.join([b['text'] for b in filtered_vendor_blocks[:2]])
# # # # # # # #       if filtered_vendor_blocks
# # # # # # # #       else 'Unknown Vendor'
# # # # # # # #   )
# # # # # # # #   vendor_coords = (
# # # # # # # #       filtered_vendor_blocks[0]['coordinates']
# # # # # # # #       if filtered_vendor_blocks
# # # # # # # #       else [0, 0, 0, 0]
# # # # # # # #   )

# # # # # # # #   company_address = (
# # # # # # # #       ' '.join([b['text'] for b in filtered_vendor_blocks[2:8]])
# # # # # # # #       if len(filtered_vendor_blocks) > 2
# # # # # # # #       else 'Address Not Found'
# # # # # # # #   )
# # # # # # # #   address_coords = (
# # # # # # # #       filtered_vendor_blocks[2]['coordinates']
# # # # # # # #       if len(filtered_vendor_blocks) > 2
# # # # # # # #       else [0, 0, 0, 0]
# # # # # # # #   )

# # # # # # # #   # Constructing final structured JSON output with exact coordinate mapping
# # # # # # # #   structured_output = {
# # # # # # # #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# # # # # # # #       'company_address': {
# # # # # # # #           'value': company_address,
# # # # # # # #           'coordinates': address_coords,
# # # # # # # #       },
# # # # # # # #       'invoice_number': {
# # # # # # # #           'value': invoice_number,
# # # # # # # #           'coordinates': inv_coords,
# # # # # # # #       },
# # # # # # # #       'total': {'value': total_value, 'coordinates': total_coords},
# # # # # # # #   }

# # # # # # # #   return structured_output


# # # # # # # # def get_coordinates_for_text(search_text, word_boxes):
# # # # # # # #   """Aggregates precise bounding coordinates for matched text values."""
# # # # # # # #   search_tokens = search_text.split()
# # # # # # # #   matched_boxes = []

# # # # # # # #   for token in search_tokens:
# # # # # # # #     for wb in word_boxes:
# # # # # # # #       if token.lower() in wb['text'].lower() and wb not in matched_boxes:
# # # # # # # #         matched_boxes.append(wb)
# # # # # # # #         break

# # # # # # # #   if not matched_boxes:
# # # # # # # #     return [0, 0, 0, 0]

# # # # # # # #   xmin = min([b['coordinates'][0] for b in matched_boxes])
# # # # # # # #   ymin = min([b['coordinates'][1] for b in matched_boxes])
# # # # # # # #   xmax = max([b['coordinates'][2] for b in matched_boxes])
# # # # # # # #   ymax = max([b['coordinates'][3] for b in matched_boxes])
  
# # # # # # # #   return [int(xmin), int(ymin), int(xmax), int(ymax)]

# # # # # # # import re
# # # # # # # import cv2
# # # # # # # import numpy as np
# # # # # # # import pytesseract
# # # # # # # from PIL import Image


# # # # # # # def extract_invoice_data(image_path_or_pil):
# # # # # # #   """Processes an invoice image, performs OCR, and extracts specific

# # # # # # #   invoice fields with precise coordinate mapping.
# # # # # # #   """
# # # # # # #   if isinstance(image_path_or_pil, str):
# # # # # # #     image = Image.open(image_path_or_pil)
# # # # # # #   else:
# # # # # # #     image = image_path_or_pil

# # # # # # #   # Convert PIL image to OpenCV format
# # # # # # #   img_cv = np.array(image)
# # # # # # #   gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
# # # # # # #   img_height, img_width = gray.shape[:2]

# # # # # # #   # Run Tesseract OCR
# # # # # # #   ocr_data = pytesseract.image_to_data(
# # # # # # #       gray, output_type=pytesseract.Output.DICT
# # # # # # #   )

# # # # # # #   word_boxes = []
# # # # # # #   n_boxes = len(ocr_data['text'])

# # # # # # #   for i in range(n_boxes):
# # # # # # #     word = ocr_data['text'][i].strip()
# # # # # # #     if word:
# # # # # # #       x, y, w, h = (
# # # # # # #           ocr_data['left'][i],
# # # # # # #           ocr_data['top'][i],
# # # # # # #           ocr_data['width'][i],
# # # # # # #           ocr_data['height'][i],
# # # # # # #       )
# # # # # # #       word_boxes.append(
# # # # # # #           {
# # # # # # #               'text': word,
# # # # # # #               'coordinates': [int(x), int(y), int(x + w), int(y + h)],
# # # # # # #           }
# # # # # # #       )

# # # # # # #   # Full text for regex matching
# # # # # # #   full_text = ' '.join([b['text'] for b in word_boxes])

# # # # # # #   # --- 1. INVOICE NUMBER EXTRACTION ---
# # # # # # #   invoice_number = 'Not Found'
# # # # # # #   inv_coords = [0, 0, 0, 0]

# # # # # # #   # Search explicitly for invoice number patterns after labels
# # # # # # #   inv_match = re.search(
# # # # # # #       r'(?:invoice\s*(?:no|number|num|#)|inv[\s\-#]*)\s*[:.]?\s*([A-Z0-9\-]{2,15})',
# # # # # # #       full_text,
# # # # # # #       re.IGNORECASE,
# # # # # # #   )
# # # # # # #   if inv_match:
# # # # # # #     invoice_number = inv_match.group(1)
# # # # # # #     inv_coords = get_coordinates_for_text(invoice_number, word_boxes)
# # # # # # #   else:
# # # # # # #     # Fallback pattern for code formats like US-001 or standalone codes near top right
# # # # # # #     top_right_words = [
# # # # # # #         b
# # # # # # #         for b in word_boxes
# # # # # # #         if b['coordinates'][0] > img_width * 0.6
# # # # # # #         and b['coordinates'][1] < img_height * 0.25
# # # # # # #     ]
# # # # # # #     for b in top_right_words:
# # # # # # #       if re.match(r'^[A-Z0-9\-]{3,10}$', b['text']) and not any(
# # # # # # #           kw in b['text'].upper() for kw in ['INVOICE', 'DATE', 'LOGO']
# # # # # # #       ):
# # # # # # #         invoice_number = b['text']
# # # # # # #         inv_coords = b['coordinates']
# # # # # # #         break

# # # # # # #   # --- 2. TOTAL AMOUNT EXTRACTION ---
# # # # # # #   total_value = 'Not Found'
# # # # # # #   total_coords = [0, 0, 0, 0]

# # # # # # #   # Search for total variations (Grand Total, Invoice Total, Total, etc.)
# # # # # # #   total_match = re.search(
# # # # # # #       r'(?:grand\s*total|invoice\s*total|total\s*due|total)[:\s]*[\$]?\s*([\d,]+\.\d{2})',
# # # # # # #       full_text,
# # # # # # #       re.IGNORECASE,
# # # # # # #   )
# # # # # # #   if total_match:
# # # # # # #     total_value = total_match.group(1)
# # # # # # #     total_coords = get_coordinates_for_text(total_value, word_boxes)
# # # # # # #   else:
# # # # # # #     # Fallback: look for currency amounts in the bottom right section
# # # # # # #     bottom_right_words = [
# # # # # # #         b
# # # # # # #         for b in word_boxes
# # # # # # #         if b['coordinates'][0] > img_width * 0.5
# # # # # # #         and b['coordinates'][1] > img_height * 0.5
# # # # # # #     ]
# # # # # # #     amounts = []
# # # # # # #     for b in bottom_right_words:
# # # # # # #       amt_match = re.search(r'[\$]?([\d,]+\.\d{2})', b['text'])
# # # # # # #       if amt_match:
# # # # # # #         amounts.append((float(amt_match.group(1).replace(',', '')), b))
# # # # # # #     if amounts:
# # # # # # #       # Usually the grand total is the largest value or last listed amount at the bottom
# # # # # # #       amounts.sort(key=lambda x: x[0], reverse=True)
# # # # # # #       total_value = f"${amounts[0][0]:.2f}"
# # # # # # #       total_coords = amounts[0][1]['coordinates']

# # # # # # #   # --- 3. VENDOR NAME & ADDRESS EXTRACTION ---
# # # # # # #   # Focus strictly on the top-left portion of the document
# # # # # # #   header_words = [
# # # # # # #       b
# # # # # # #       for b in word_boxes
# # # # # # #       if b['coordinates'][1] < img_height * 0.25
# # # # # # #       and b['coordinates'][0] < img_width * 0.6
# # # # # # #   ]
# # # # # # #   # Filter out structural labels
# # # # # # #   filtered_header = [
# # # # # # #       b
# # # # # # #       for b in header_words
# # # # # # #       if b['text'].upper()
# # # # # # #       not in ['TAX', 'INVOICE', 'DATE', 'BILL', 'TO', 'LOGO', 'SHIP']
# # # # # # #   ]

# # # # # # #   vendor_name = 'Unknown Vendor'
# # # # # # #   vendor_coords = [0, 0, 0, 0]
# # # # # # #   company_address = 'Address Not Found'
# # # # # # #   address_coords = [0, 0, 0, 0]

# # # # # # #   if filtered_header:
# # # # # # #     # Group top words by line (similar Y coordinates)
# # # # # # #     first_y = filtered_header[0]['coordinates'][1]
# # # # # # #     name_words = [
# # # # # # #         b for b in filtered_header if abs(b['coordinates'][1] - first_y) < 15
# # # # # # #     ]
# # # # # # #     vendor_name = ' '.join([b['text'] for b in name_words])
# # # # # # #     vendor_coords = get_coordinates_for_text(vendor_name, word_boxes)

# # # # # # #     address_words = [
# # # # # # #         b for b in filtered_header if b not in name_words and b['coordinates'][1] > first_y
# # # # # # #     ]
# # # # # # #     if address_words:
# # # # # # #       company_address = ' '.join([b['text'] for b in address_words[:6]])
# # # # # # #       address_coords = address_words[0]['coordinates']

# # # # # # #   # Final structured output JSON
# # # # # # #   structured_output = {
# # # # # # #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# # # # # # #       'company_address': {
# # # # # # #           'value': company_address,
# # # # # # #           'coordinates': address_coords,
# # # # # # #       },
# # # # # # #       'invoice_number': {
# # # # # # #           'value': invoice_number,
# # # # # # #           'coordinates': inv_coords,
# # # # # # #       },
# # # # # # #       'total': {'value': total_value, 'coordinates': total_coords},
# # # # # # #   }

# # # # # # #   return structured_output


# # # # # # # def get_coordinates_for_text(search_text, word_boxes):
# # # # # # #   """Aggregates precise bounding coordinates for matched text values."""
# # # # # # #   search_tokens = str(search_text).replace('$', '').split()
# # # # # # #   matched_boxes = []

# # # # # # #   for token in search_tokens:
# # # # # # #     for wb in word_boxes:
# # # # # # #       if token.lower() in wb['text'].lower() and wb not in matched_boxes:
# # # # # # #         matched_boxes.append(wb)
# # # # # # #         break

# # # # # # #   if not matched_boxes:
# # # # # # #     return [0, 0, 0, 0]

# # # # # # #   xmin = min([b['coordinates'][0] for b in matched_boxes])
# # # # # # #   ymin = min([b['coordinates'][1] for b in matched_boxes])
# # # # # # #   xmax = max([b['coordinates'][2] for b in matched_boxes])
# # # # # # #   ymax = max([b['coordinates'][3] for b in matched_boxes])

# # # # # # #   return [int(xmin), int(ymin), int(xmax), int(ymax)]

# # # # # # import re
# # # # # # import cv2
# # # # # # import numpy as np
# # # # # # import pytesseract
# # # # # # from PIL import Image


# # # # # # def extract_invoice_data(image_path_or_pil):
# # # # # #   """Processes an invoice image, performs OCR, and extracts specific

# # # # # #   invoice fields using multi-pattern regex and coordinate mapping.
# # # # # #   """
# # # # # #   if isinstance(image_path_or_pil, str):
# # # # # #     image = Image.open(image_path_or_pil)
# # # # # #   else:
# # # # # #     image = image_path_or_pil

# # # # # #   # Convert PIL image to OpenCV format
# # # # # #   img_cv = np.array(image)
# # # # # #   gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
# # # # # #   img_height, img_width = gray.shape[:2]

# # # # # #   # Run Tesseract OCR with detailed word boxes
# # # # # #   ocr_data = pytesseract.image_to_data(
# # # # # #       gray, output_type=pytesseract.Output.DICT
# # # # # #   )

# # # # # #   word_boxes = []
# # # # # #   n_boxes = len(ocr_data['text'])

# # # # # #   for i in range(n_boxes):
# # # # # #     word = ocr_data['text'][i].strip()
# # # # # #     if word:
# # # # # #       x, y, w, h = (
# # # # # #           ocr_data['left'][i],
# # # # # #           ocr_data['top'][i],
# # # # # #           ocr_data['width'][i],
# # # # # #           ocr_data['height'][i],
# # # # # #       )
# # # # # #       word_boxes.append(
# # # # # #           {
# # # # # #               'text': word,
# # # # # #               'coordinates': [int(x), int(y), int(x + w), int(y + h)],
# # # # # #           }
# # # # # #       )

# # # # # #   # Construct full text for fallback and global scans
# # # # # #   full_text = ' '.join([b['text'] for b in word_boxes])

# # # # # #   # --- 1. ROBUST INVOICE NUMBER EXTRACTION ---
# # # # # #   invoice_number = 'Not Found'
# # # # # #   inv_coords = [0, 0, 0, 0]

# # # # # #   # Cascading regex patterns for invoice numbers (handles 1001, 12345, US-001, etc.)
# # # # # #   inv_patterns = [
# # # # # #       r'(?:invoice\s*(?:no|number|num|#)|inv[\s\-#]*)\s*[:.]?\s*([A-Z0-9\-]{2,15})',
# # # # # #       r'(?:P\.O\.#|PO#|Order\s*#)\s*[:.]?\s*([A-Z0-9\-]{2,15})',
# # # # # #       r'\b(US-\d{3,4})\b',  # Specific format for sample 2
# # # # # #       r'\b(INV-?\d{3,6})\b',
# # # # # #   ]

# # # # # #   for pattern in inv_patterns:
# # # # # #     match = re.search(pattern, full_text, re.IGNORECASE)
# # # # # #     if match:
# # # # # #       candidate = match.group(1)
# # # # # #       # Ensure we didn't accidentally grab a generic label word
# # # # # #       if candidate.upper() not in ['INVOICE', 'TAX', 'TOTAL', 'DATE']:
# # # # # #         invoice_number = candidate
# # # # # #         inv_coords = get_coordinates_for_text(invoice_number, word_boxes)
# # # # # #         break

# # # # # #   # Fallback for top-right standalone alphanumeric invoice codes if regex misses
# # # # # #   if invoice_number == 'Not Found':
# # # # # #     top_right_candidates = [
# # # # # #         b
# # # # # #         for b in word_boxes
# # # # # #         if b['coordinates'][0] > img_width * 0.5
# # # # # #         and b['coordinates'][1] < img_height * 0.3
# # # # # #     ]
# # # # # #     for b in top_right_candidates:
# # # # # #       text = b['text']
# # # # # #       if (
# # # # # #           re.match(r'^[A-Z0-9\-]{3,10}$', text)
# # # # # #           and text.upper() not in ['INVOICE', 'LOGO', 'TOTAL', 'DATE']
# # # # # #       ):
# # # # # #         invoice_number = text
# # # # # #         inv_coords = b['coordinates']
# # # # # #         break

# # # # # #   # --- 2. ROBUST TOTAL AMOUNT EXTRACTION ---
# # # # # #   total_value = 'Not Found'
# # # # # #   total_coords = [0, 0, 0, 0]

# # # # # #   # Cascading patterns for total amounts (handles $1 500.00, $8,798, $154.06, etc.)
# # # # # #   total_patterns = [
# # # # # #       r'(?:invoice\s*total|grand\s*total|total\s*due|total)[:\s]*[\$]?\s*([\d,]+\.?\d{0,2})',
# # # # # #       r'(?:balance\s*due)[:\s]*[\$]?\s*([\d,]+\.?\d{0,2})',
# # # # # #   ]

# # # # # #   for pattern in total_patterns:
# # # # # #     match = re.search(pattern, full_text, re.IGNORECASE)
# # # # # #     if match:
# # # # # #       total_value = match.group(1)
# # # # # #       total_coords = get_coordinates_for_text(total_value, word_boxes)
# # # # # #       if not total_value.startswith('$') and any(
# # # # # #           char.isdigit() for char in total_value
# # # # # #       ):
# # # # # #         total_value = f'${total_value}'
# # # # # #       break

# # # # # #   # Fallback: scan bottom-right quadrant for currency figures if regex fails
# # # # # #   if total_value == 'Not Found':
# # # # # #     bottom_right_words = [
# # # # # #         b
# # # # # #         for b in word_boxes
# # # # # #         if b['coordinates'][0] > img_width * 0.45
# # # # # #         and b['coordinates'][1] > img_height * 0.45
# # # # # #     ]
# # # # # #     valid_amounts = []
# # # # # #     for b in bottom_right_words:
# # # # # #       clean_txt = b['text'].replace('$', '').replace(',', '')
# # # # # #       if re.match(r'^\d+\.\d{2}$', clean_txt):
# # # # # #         valid_amounts.append((float(clean_txt), b))

# # # # # #     if valid_amounts:
# # # # # #       # Grand total is typically the largest amount or bottom-most number
# # # # # #       valid_amounts.sort(key=lambda x: x[0], reverse=True)
# # # # # #       total_value = f'${valid_amounts[0][0]:,.2f}'
# # # # # #       total_coords = valid_amounts[0][1]['coordinates']

# # # # # #   # --- 3. TARGETED VENDOR & ADDRESS EXTRACTION ---
# # # # # #   # Isolate top-left header zone
# # # # # #   header_words = [
# # # # # #       b
# # # # # #       for b in word_boxes
# # # # # #       if b['coordinates'][1] < img_height * 0.28
# # # # # #       and b['coordinates'][0] < img_width * 0.55
# # # # # #   ]
# # # # # #   # Filter noise words
# # # # # #   filtered_header = [
# # # # # #       b
# # # # # #       for b in header_words
# # # # # #       if b['text'].upper()
# # # # # #       not in ['TAX', 'INVOICE', 'DATE', 'BILL', 'TO', 'LOGO', 'SHIP', 'TAX']
# # # # # #   ]

# # # # # #   vendor_name = 'Unknown Vendor'
# # # # # #   vendor_coords = [0, 0, 0, 0]
# # # # # #   company_address = 'Address Not Found'
# # # # # #   address_coords = [0, 0, 0, 0]

# # # # # #   if filtered_header:
# # # # # #     # Group top line by Y-proximity
# # # # # #     first_y = filtered_header[0]['coordinates'][1]
# # # # # #     name_words = [
# # # # # #         b for b in filtered_header if abs(b['coordinates'][1] - first_y) < 18
# # # # # #     ]
# # # # # #     vendor_name = ' '.join([b['text'] for b in name_words])
# # # # # #     vendor_coords = get_coordinates_for_text(vendor_name, word_boxes)

# # # # # #     address_words = [
# # # # # #         b for b in filtered_header if b not in name_words and b['coordinates'][1] > first_y
# # # # # #     ]
# # # # # #     if address_words:
# # # # # #       company_address = ' '.join([b['text'] for b in address_words[:7]])
# # # # # #       address_coords = address_words[0]['coordinates']

# # # # # #   # Final JSON structured dictionary
# # # # # #   structured_output = {
# # # # # #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# # # # # #       'company_address': {
# # # # # #           'value': company_address,
# # # # # #           'coordinates': address_coords,
# # # # # #       },
# # # # # #       'invoice_number': {
# # # # # #           'value': invoice_number,
# # # # # #           'coordinates': inv_coords,
# # # # # #       },
# # # # # #       'total': {'value': total_value, 'coordinates': total_coords},
# # # # # #   }

# # # # # #   return structured_output


# # # # # # def get_coordinates_for_text(search_text, word_boxes):
# # # # # #   """Aggregates precise bounding coordinates for matched text values."""
# # # # # #   search_tokens = str(search_text).replace('$', '').replace(',', '').split()
# # # # # #   matched_boxes = []

# # # # # #   for token in search_tokens:
# # # # # #     for wb in word_boxes:
# # # # # #       if token.lower() in wb['text'].lower() and wb not in matched_boxes:
# # # # # #         matched_boxes.append(wb)
# # # # # #         break

# # # # # #   if not matched_boxes:
# # # # # #     return [0, 0, 0, 0]

# # # # # #   xmin = min([b['coordinates'][0] for b in matched_boxes])
# # # # # #   ymin = min([b['coordinates'][1] for b in matched_boxes])
# # # # # #   xmax = max([b['coordinates'][2] for b in matched_boxes])
# # # # # #   ymax = max([b['coordinates'][3] for b in matched_boxes])

# # # # # #   return [int(xmin), int(ymin), int(xmax), int(ymax)]

# # # # # import re
# # # # # import cv2
# # # # # import numpy as np
# # # # # import pytesseract
# # # # # from PIL import Image


# # # # # def extract_invoice_data(image_path_or_pil):
# # # # #   """Processes an invoice image line-by-line, extracts target entities

# # # # #   using anchor-based label matching, and maps precise bounding boxes.
# # # # #   """
# # # # #   if isinstance(image_path_or_pil, str):
# # # # #     image = Image.open(image_path_or_pil)
# # # # #   else:
# # # # #     image = image_path_or_pil

# # # # #   img_cv = np.array(image)
# # # # #   gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
# # # # #   img_height, img_width = gray.shape[:2]

# # # # #   # Run Tesseract OCR for detailed word and block data
# # # # #   ocr_data = pytesseract.image_to_data(
# # # # #       gray, output_type=pytesseract.Output.DICT
# # # # #   )

# # # # #   word_boxes = []
# # # # #   n_boxes = len(ocr_data['text'])
# # # # #   for i in range(n_boxes):
# # # # #     word = ocr_data['text'][i].strip()
# # # # #     if word:
# # # # #       x, y, w, h = (
# # # # #           ocr_data['left'][i],
# # # # #           ocr_data['top'][i],
# # # # #           ocr_data['width'][i],
# # # # #           ocr_data['height'][i],
# # # # #       )
# # # # #       word_boxes.append(
# # # # #           {
# # # # #               'text': word,
# # # # #               'coordinates': [int(x), int(y), int(x + w), int(y + h)],
# # # # #           }
# # # # #       )

# # # # #   # Group words into structured lines based on vertical Y proximity
# # # # #   lines = []
# # # # #   sorted_boxes = sorted(word_boxes, key=lambda b: (b['coordinates'][1], b['coordinates'][0]))
  
# # # # #   current_line = []
# # # # #   last_y = -1
# # # # #   for wb in sorted_boxes:
# # # # #     y = wb['coordinates'][1]
# # # # #     if last_y == -1 or abs(y - last_y) < 12:
# # # # #       current_line.append(wb)
# # # # #       last_y = y if last_y == -1 else (last_y + y) // 2
# # # # #     else:
# # # # #       if current_line:
# # # # #         lines.append(current_line)
# # # # #       current_line = [wb]
# # # # #       last_y = y
# # # # #   if current_line:
# # # # #     lines.append(current_line)

# # # # #   # Reconstruct text line strings for searching
# # # # #   line_texts = [' '.join([w['text'] for w in line]) for line in lines]

# # # # #   # --- 1. INVOICE NUMBER EXTRACTION ---
# # # # #   invoice_number = 'Not Found'
# # # # #   inv_coords = [0, 0, 0, 0]

# # # # #   for line in lines:
# # # # #     line_str = ' '.join([w['text'] for w in line])
# # # # #     # Look for label anchors like 'Invoice number', 'Invoice no', 'Invoice #'
# # # # #     match = re.search(
# # # # #         r'(?:invoice\s*(?:no|number|num|#)|inv[\s\-#]*)\s*[:.]?\s*([A-Z0-9\-]{2,15})',
# # # # #         line_str,
# # # # #         re.IGNORECASE,
# # # # #     )
# # # # #     if match:
# # # # #       candidate = match.group(1)
# # # # #       if candidate.upper() not in ['INVOICE', 'TAX', 'TOTAL']:
# # # # #         invoice_number = candidate
# # # # #         inv_coords = get_box_for_phrase(invoice_number, word_boxes)
# # # # #         break

# # # # #   # Fallback: scan top right for alphanumeric codes if anchor missed
# # # # #   if invoice_number == 'Not Found':
# # # # #     for wb in word_boxes:
# # # # #       if (
# # # # #           wb['coordinates'][0] > img_width * 0.5
# # # # #           and wb['coordinates'][1] < img_height * 0.3
# # # # #       ):
# # # # #         txt = wb['text']
# # # # #         if (
# # # # #             re.match(r'^[A-Z0-9\-]{3,10}$', txt)
# # # # #             and txt.upper() not in ['INVOICE', 'TAX', 'LOGO', 'DATE']
# # # # #         ):
# # # # #           invoice_number = txt
# # # # #           inv_coords = wb['coordinates']
# # # # #           break

# # # # #   # --- 2. TOTAL AMOUNT EXTRACTION ---
# # # # #   total_value = 'Not Found'
# # # # #   total_coords = [0, 0, 0, 0]

# # # # #   for line in lines:
# # # # #     line_str = ' '.join([w['text'] for w in line])
# # # # #     # Anchor to labels like 'Invoice total', 'Grand Total', 'TOTAL'
# # # # #     match = re.search(
# # # # #         r'(?:invoice\s*total|grand\s*total|total\s*due|invoice\s*total|total)[:\s]*[\$]?\s*([\d,]+\.\d{2})',
# # # # #         line_str,
# # # # #         re.IGNORECASE,
# # # # #     )
# # # # #     if match:
# # # # #       total_value = f"${match.group(1)}"
# # # # #       total_coords = get_box_for_phrase(match.group(1), word_boxes)
# # # # #       break

# # # # #   # Fallback for totals split across words (e.g. '$1 650.00')
# # # # #   if total_value == 'Not Found':
# # # # #     for i, line_str in enumerate(line_texts):
# # # # #       if re.search(
# # # # #           r'(?:invoice\s*total|grand\s*total|total)', line_str, re.IGNORECASE
# # # # #       ):
# # # # #         # Look at the current line or the next line for a monetary amount
# # # # #         search_block = line_str
# # # # #         if i + 1 < len(line_texts):
# # # # #           search_block += ' ' + line_texts[i + 1]
# # # # #         amt_match = re.search(r'[\$]?\s*([\d,]+\.\d{2})', search_block)
# # # # #         if amt_match:
# # # # #           total_value = f"${amt_match.group(1)}"
# # # # #           total_coords = get_box_for_phrase(amt_match.group(1), word_boxes)
# # # # #           break

# # # # #   # --- 3. VENDOR NAME & ADDRESS EXTRACTION ---
# # # # #   vendor_name = 'Unknown Vendor'
# # # # #   vendor_coords = [0, 0, 0, 0]
# # # # #   company_address = 'Address Not Found'
# # # # #   address_coords = [0, 0, 0, 0]

# # # # #   # Isolate top-left header zone where company info lives
# # # # #   header_lines = [
# # # # #       line
# # # # #       for line in lines
# # # # #       if line[0]['coordinates'][1] < img_height * 0.25
# # # # #       and line[0]['coordinates'][0] < img_width * 0.5
# # # # #   ]

# # # # #   valid_header_words = []
# # # # #   for line in header_lines:
# # # # #     for wb in line:
# # # # #       txt = wb['text']
# # # # #       if txt.upper() not in [
# # # # #           'TAX',
# # # # #           'INVOICE',
# # # # #           'DATE',
# # # # #           'BILL',
# # # # #           'TO',
# # # # #           'LOGO',
# # # # #           'SHIP',
# # # # #           'TAX INVOICE',
# # # # #       ]:
# # # # #         valid_header_words.append(wb)

# # # # #   if valid_header_words:
# # # # #     # First line/words in header are typically the vendor name
# # # # #     first_y = valid_header_words[0]['coordinates'][1]
# # # # #     name_tokens = [
# # # # #         w for w in valid_header_words if abs(w['coordinates'][1] - first_y) < 15
# # # # #     ]
# # # # #     vendor_name = ' '.join([w['text'] for w in name_tokens])
# # # # #     vendor_coords = get_box_for_phrase(vendor_name, word_boxes)

# # # # #     # Subsequent lines contain address info
# # # # #     address_tokens = [
# # # # #         w for w in valid_header_words if w not in name_tokens and w['coordinates'][1] > first_y
# # # # #     ]
# # # # #     if address_tokens:
# # # # #       company_address = ' '.join([w['text'] for w in address_tokens[:8]])
# # # # #       address_coords = address_tokens[0]['coordinates']

# # # # #   # Final structured JSON output
# # # # #   structured_output = {
# # # # #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# # # # #       'company_address': {
# # # # #           'value': company_address,
# # # # #           'coordinates': address_coords,
# # # # #       },
# # # # #       'invoice_number': {
# # # # #           'value': invoice_number,
# # # # #           'coordinates': inv_coords,
# # # # #       },
# # # # #       'total': {'value': total_value, 'coordinates': total_coords},
# # # # #   }

# # # # #   return structured_output


# # # # # def get_box_for_phrase(phrase, word_boxes):
# # # # #   """Finds precise aggregate bounding coordinates for a target string."""
# # # # #   tokens = str(phrase).replace('$', '').replace(',', '').split()
# # # # #   matched = []
# # # # #   for token in tokens:
# # # # #     for wb in word_boxes:
# # # # #       if token.lower() in wb['text'].lower() and wb not in matched:
# # # # #         matched.append(wb)
# # # # #         break

# # # # #   if not matched:
# # # # #     return [0, 0, 0, 0]

# # # # #   xmin = min([b['coordinates'][0] for b in matched])
# # # # #   ymin = min([b['coordinates'][1] for b in matched])
# # # # #   xmax = max([b['coordinates'][2] for b in matched])
# # # # #   ymax = max([b['coordinates'][3] for b in matched])
# # # # #   return [int(xmin), int(ymin), int(xmax), int(ymax)]

# # # # import re
# # # # import cv2
# # # # import numpy as np
# # # # import pytesseract
# # # # from PIL import Image


# # # # def extract_invoice_data(image_path_or_pil):
# # # #   """Processes an invoice image using spatial region mapping and anchor

# # # #   extraction to reliably capture entities and bounding boxes.
# # # #   """
# # # #   if isinstance(image_path_or_pil, str):
# # # #     image = Image.open(image_path_or_pil)
# # # #   else:
# # # #     image = image_path_or_pil

# # # #   img_cv = np.array(image)
# # # #   gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
# # # #   img_height, img_width = gray.shape[:2]

# # # #   # Run Tesseract OCR
# # # #   ocr_data = pytesseract.image_to_data(
# # # #       gray, output_type=pytesseract.Output.DICT
# # # #   )

# # # #   word_boxes = []
# # # #   n_boxes = len(ocr_data['text'])
# # # #   for i in range(n_boxes):
# # # #     word = ocr_data['text'][i].strip()
# # # #     if word:
# # # #       x, y, w, h = (
# # # #           ocr_data['left'][i],
# # # #           ocr_data['top'][i],
# # # #           ocr_data['width'][i],
# # # #           ocr_data['height'][i],
# # # #       )
# # # #       word_boxes.append(
# # # #           {
# # # #               'text': word,
# # # #               'coordinates': [int(x), int(y), int(x + w), int(y + h)],
# # # #           }
# # # #       )

# # # #   # Sort words top-to-bottom, left-to-right
# # # #   sorted_boxes = sorted(word_boxes, key=lambda b: (b['coordinates'][1], b['coordinates'][0]))
# # # #   full_text = ' '.join([b['text'] for b in sorted_boxes])

# # # #   # --- 1. INVOICE NUMBER (Strict Anchor Search) ---
# # # #   invoice_number = 'Not Found'
# # # #   inv_coords = [0, 0, 0, 0]

# # # #   # Look for explicit label pairings
# # # #   for i, wb in enumerate(sorted_boxes):
# # # #     txt_lower = wb['text'].lower()
# # # #     if any(
# # # #         kw in txt_lower
# # # #         for kw in ['invoice', 'inv', 'order', 'p.o.', 'no.', 'no']
# # # #     ):
# # # #       # Check the next 3 words in sequence for the actual value
# # # #       for j in range(1, 4):
# # # #         if i + j < len(sorted_boxes):
# # # #           next_wb = sorted_boxes[i + j]
# # # #           candidate = next_wb['text'].strip(':#.,')
# # # #           # Ensure candidate looks like an invoice ID (e.g. 1001, 12345, US-001)
# # # #           if (
# # # #               len(candidate) >= 2
# # # #               and candidate.upper()
# # # #               not in ['INVOICE', 'DATE', 'DUE', 'TAX', 'TOTAL', 'NO']
# # # #               and not candidate.lower().startswith('01/')
# # # #           ):
# # # #             invoice_number = candidate
# # # #             inv_coords = next_wb['coordinates']
# # # #             break
# # # #       if invoice_number != 'Not Found':
# # # #         break

# # # #   # Fallback for invoice number via regex if loop misses
# # # #   if invoice_number == 'Not Found':
# # # #     match = re.search(
# # # #         r'(?:invoice\s*(?:no|number|#)|inv[\s\-#]*)\s*[:.]?\s*([A-Z0-9\-]{2,15})',
# # # #         full_text,
# # # #         re.IGNORECASE,
# # # #     )
# # # #     if match and match.group(1).upper() not in ['INVOICE', 'TAX']:
# # # #       invoice_number = match.group(1)
# # # #       inv_coords = get_box_for_phrase(invoice_number, word_boxes)

# # # #   # --- 2. TOTAL AMOUNT (Bottom-Right / Label Scan) ---
# # # #   total_value = 'Not Found'
# # # #   total_coords = [0, 0, 0, 0]

# # # #   # Search near total labels
# # # #   for i, wb in enumerate(sorted_boxes):
# # # #     txt_lower = wb['text'].lower()
# # # #     if 'total' in txt_lower or 'amount' in txt_lower or 'balance' in txt_lower:
# # # #       # Scan ahead for the monetary amount
# # # #       for j in range(1, 5):
# # # #         if i + j < len(sorted_boxes):
# # # #           next_wb = sorted_boxes[i + j]
# # # #           clean_amt = next_wb['text'].replace('$', '').replace(',', '')
# # # #           if re.match(r'^\d+\.\d{2}$', clean_amt):
# # # #             total_value = (
# # # #                 next_wb['text']
# # # #                 if '$' in next_wb['text']
# # # #                 else f"${next_wb['text']}"
# # # #             )
# # # #             total_coords = next_wb['coordinates']
# # # #             break
# # # #       if total_value != 'Not Found':
# # # #         break

# # # #   # Fallback: scan bottom right quadrant for the largest currency value
# # # #   if total_value == 'Not Found':
# # # #     bottom_right = [
# # # #         b
# # # #         for b in word_boxes
# # # #         if b['coordinates'][0] > img_width * 0.45
# # # #         and b['coordinates'][1] > img_height * 0.4
# # # #     ]
# # # #     amounts = []
# # # #     for b in bottom_right:
# # # #       clean = b['text'].replace('$', '').replace(',', '')
# # # #       if re.match(r'^\d+\.\d{2}$', clean):
# # # #         amounts.append((float(clean), b))
# # # #     if amounts:
# # # #       amounts.sort(key=lambda x: x[0], reverse=True)
# # # #       total_value = f"${amounts[0][0]:,.2f}"
# # # #       total_coords = amounts[0][1]['coordinates']

# # # #   # --- 3. VENDOR NAME & ADDRESS (Top-Left Bounding Box Extraction) ---
# # # #   # Filter strictly to the top-left section, excluding header artifacts
# # # #   top_left_words = [
# # # #       b
# # # #       for b in sorted_boxes
# # # #       if b['coordinates'][1] < img_height * 0.25
# # # #       and b['coordinates'][0] < img_width * 0.55
# # # #       and b['text'].upper()
# # # #       not in [
# # # #           'TAX',
# # # #           'INVOICE',
# # # #           'TAX INVOICE',
# # # #           'LOGO',
# # # #           'DATE',
# # # #           'BILL',
# # # #           'TO',
# # # #           'SHIP',
# # # #       ]
# # # #   ]

# # # #   vendor_name = 'Unknown Vendor'
# # # #   vendor_coords = [0, 0, 0, 0]
# # # #   company_address = 'Address Not Found'
# # # #   address_coords = [0, 0, 0, 0]

# # # #   if top_left_words:
# # # #     # First line of top-left is the Vendor Name
# # # #     first_y = top_left_words[0]['coordinates'][1]
# # # #     name_tokens = [
# # # #         b for b in top_left_words if abs(b['coordinates'][1] - first_y) < 15
# # # #     ]
# # # #     vendor_name = ' '.join([b['text'] for b in name_tokens])
# # # #     vendor_coords = get_box_for_phrase(vendor_name, word_boxes)

# # # #     # Subsequent lines are the address
# # # #     address_tokens = [
# # # #         b
# # # #         for b in top_left_words
# # # #         if b not in name_tokens and b['coordinates'][1] > first_y
# # # #     ]
# # # #     if address_tokens:
# # # #       company_address = ' '.join([b['text'] for b in address_tokens[:6]])
# # # #       address_coords = address_tokens[0]['coordinates']

# # # #   # Final structured JSON
# # # #   structured_output = {
# # # #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# # # #       'company_address': {
# # # #           'value': company_address,
# # # #           'coordinates': address_coords,
# # # #       },
# # # #       'invoice_number': {
# # # #           'value': invoice_number,
# # # #           'coordinates': inv_coords,
# # # #       },
# # # #       'total': {'value': total_value, 'coordinates': total_coords},
# # # #   }

# # # #   return structured_output


# # # # def get_box_for_phrase(phrase, word_boxes):
# # # #   """Aggregates precise bounding coordinates for a target string."""
# # # #   tokens = str(phrase).replace('$', '').replace(',', '').split()
# # # #   matched = []
# # # #   for token in tokens:
# # # #     for wb in word_boxes:
# # # #       if token.lower() in wb['text'].lower() and wb not in matched:
# # # #         matched.append(wb)
# # # #         break

# # # #   if not matched:
# # # #     return [0, 0, 0, 0]

# # # #   xmin = min([b['coordinates'][0] for b in matched])
# # # #   ymin = min([b['coordinates'][1] for b in matched])
# # # #   xmax = max([b['coordinates'][2] for b in matched])
# # # #   ymax = max([b['coordinates'][3] for b in matched])
# # # #   return [int(xmin), int(ymin), int(xmax), int(ymax)]

# # # import re
# # # import cv2
# # # import numpy as np
# # # import pytesseract
# # # from PIL import Image


# # # def extract_invoice_data(image_path_or_pil):
# # #   """Processes an invoice image by slicing it into targeted regions of

# # #   interest (ROIs) using OpenCV, eliminating cross-contamination between
# # #   headers, invoice numbers, and totals.
# # #   """
# # #   if isinstance(image_path_or_pil, str):
# # #     image = Image.open(image_path_or_pil)
# # #   else:
# # #     image = image_path_or_pil

# # #   # Convert PIL image to OpenCV format
# # #   img_cv = np.array(image)
# # #   if len(img_cv.shape) == 3:
# # #     gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
# # #   else:
# # #     gray = img_cv

# # #   img_height, img_width = gray.shape[:2]

# # #   # ==========================================
# # #   # 1. OpenCV ROI (Region of Interest) Slicing
# # #   # ==========================================

# # #   # Zone A: Top-Left (Vendor Name & Address)
# # #   roi_vendor = gray[0 : int(img_height * 0.3), 0 : int(img_width * 0.6)]

# # #   # Zone B: Top-Right (Invoice Number, Dates)
# # #   roi_invoice_num = gray[0 : int(img_height * 0.35), int(img_width * 0.45) : img_width]

# # #   # Zone C: Bottom-Right (Totals, Subtotals, Tax)
# # #   roi_totals = gray[int(img_height * 0.45) : img_height, int(img_width * 0.4) : img_width]

# # #   # ==========================================
# # #   # 2. Targeted OCR Processing per Zone
# # #   # ==========================================

# # #   # Helper function to run OCR on a specific ROI and return words with adjusted global coordinates
# # #   def run_ocr_on_roi(roi_img, offset_x=0, offset_y=0):
# # #     data = pytesseract.image_to_data(
# # #         roi_img, output_type=pytesseract.Output.DICT
# # #     )
# # #     boxes = []
# # #     for i in range(len(data['text'])):
# # #       word = data['text'][i].strip()
# # #       if word:
# # #         x, y, w, h = (
# # #             data['left'][i] + offset_x,
# # #             data['top'][i] + offset_y,
# # #             data['width'][i],
# # #             data['height'][i],
# # #         )
# # #         boxes.append(
# # #             {
# # #                 'text': word,
# # #                 'coordinates': [int(x), int(y), int(x + w), int(y + h)],
# # #             }
# # #         )
# # #     return boxes

# # #   vendor_boxes = run_ocr_on_roi(roi_vendor, 0, 0)
# # #   inv_boxes = run_ocr_on_roi(
# # #       roi_invoice_num, int(img_width * 0.45), 0
# # #   )
# # #   total_boxes = run_ocr_on_roi(
# # #       roi_totals, int(img_width * 0.4), int(img_height * 0.45)
# # #   )

# # #   # ==========================================
# # #   # 3. Entity Extraction from Isolated Zones
# # #   # ==========================================

# # #   # --- INVOICE NUMBER EXTRACTION (from Top-Right Zone) ---
# # #   invoice_number = 'Not Found'
# # #   inv_coords = [0, 0, 0, 0]
# # #   inv_full_text = ' '.join([b['text'] for b in inv_boxes])

# # #   # Match patterns like '1001', '12345', 'US-001' after labels
# # #   inv_match = re.search(
# # #       r'(?:invoice\s*(?:no|number|num|#)|inv[\s\-#]*|order\s*#|p\.o\.#)\s*[:.]?\s*([A-Z0-9\-]{2,15})',
# # #       inv_full_text,
# # #       re.IGNORECASE,
# # #   )
# # #   if inv_match:
# # #     invoice_number = inv_match.group(1)
# # #     inv_coords = get_box_for_phrase(invoice_number, inv_boxes)
# # #   else:
# # #     # Fallback: grab the first valid alphanumeric code in top-right that isn't a label
# # #     for b in inv_boxes:
# # #       txt = b['text']
# # #       if (
# # #           re.match(r'^[A-Z0-9\-]{3,10}$', txt)
# # #           and txt.upper() not in ['INVOICE', 'DATE', 'DUE', 'TAX', 'TOTAL', 'LOGO']
# # #           and not txt.startswith('01/')
# # #       ):
# # #         invoice_number = txt
# # #         inv_coords = b['coordinates']
# # #         break

# # #   # --- TOTAL AMOUNT EXTRACTION (from Bottom-Right Zone) ---
# # #   total_value = 'Not Found'
# # #   total_coords = [0, 0, 0, 0]
# # #   total_full_text = ' '.join([b['text'] for b in total_boxes])

# # #   total_match = re.search(
# # #       r'(?:invoice\s*total|grand\s*total|total\s*due|amount\s*due|total)[:\s]*[\$]?\s*([\d,]+\.\d{2})',
# # #       total_full_text,
# # #       re.IGNORECASE,
# # #   )
# # #   if total_match:
# # #     amt = total_match.group(1)
# # #     total_value = f'${amt}' if not amt.startswith('$') else amt
# # #     total_coords = get_box_for_phrase(amt, total_boxes)
# # #   else:
# # #     # Fallback: find the largest currency-formatted amount in the bottom-right zone
# # #     amounts = []
# # #     for b in total_boxes:
# # #       clean = b['text'].replace('$', '').replace(',', '')
# # #       if re.match(r'^\d+\.\d{2}$', clean):
# # #         amounts.append((float(clean), b))
# # #     if amounts:
# # #       amounts.sort(key=lambda x: x[0], reverse=True)
# # #       total_value = f'${amounts[0][0]:,.2f}'
# # #       total_coords = amounts[0][1]['coordinates']

# # #   # --- VENDOR NAME & ADDRESS EXTRACTION (from Top-Left Zone) ---
# # #   vendor_name = 'Unknown Vendor'
# # #   vendor_coords = [0, 0, 0, 0]
# # #   company_address = 'Address Not Found'
# # #   address_coords = [0, 0, 0, 0]

# # #   valid_vendor_words = [
# # #       b
# # #       for b in vendor_boxes
# # #       if b['text'].upper()
# # #       not in ['TAX', 'INVOICE', 'TAX INVOICE', 'LOGO', 'DATE', 'BILL', 'TO']
# # #   ]

# # #   if valid_vendor_words:
# # #     # Sort top-left words by vertical position
# # #     valid_vendor_words.sort(key=lambda b: b['coordinates'][1])
# # #     first_y = valid_vendor_words[0]['coordinates'][1]
    
# # #     # First line represents the vendor name
# # #     name_tokens = [
# # #         b for b in valid_vendor_words if abs(b['coordinates'][1] - first_y) < 15
# # #     ]
# # #     vendor_name = ' '.join([b['text'] for b in name_tokens])
# # #     vendor_coords = get_box_for_phrase(vendor_name, vendor_boxes)

# # #     # Remaining lines represent the address
# # #     address_tokens = [
# # #         b
# # #         for b in valid_vendor_words
# # #         if b not in name_tokens and b['coordinates'][1] > first_y
# # #     ]
# # #     if address_tokens:
# # #       company_address = ' '.join([b['text'] for b in address_tokens[:6]])
# # #       address_coords = address_tokens[0]['coordinates']

# # #   # Final structured JSON output
# # #   structured_output = {
# # #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# # #       'company_address': {
# # #           'value': company_address,
# # #           'coordinates': address_coords,
# # #       },
# # #       'invoice_number': {
# # #           'value': invoice_number,
# # #           'coordinates': inv_coords,
# # #       },
# # #       'total': {'value': total_value, 'coordinates': total_coords},
# # #   }

# # #   return structured_output


# # # def get_box_for_phrase(phrase, word_boxes):
# # #   """Aggregates precise bounding coordinates for a target string."""
# # #   tokens = str(phrase).replace('$', '').replace(',', '').split()
# # #   matched = []
# # #   for token in tokens:
# # #     for wb in word_boxes:
# # #       if token.lower() in wb['text'].lower() and wb not in matched:
# # #         matched.append(wb)
# # #         break

# # #   if not matched:
# # #     return [0, 0, 0, 0]

# # #   xmin = min([b['coordinates'][0] for b in matched])
# # #   ymin = min([b['coordinates'][1] for b in matched])
# # #   xmax = max([b['coordinates'][2] for b in matched])
# # #   ymax = max([b['coordinates'][3] for b in matched])
# # #   return [int(xmin), int(ymin), int(xmax), int(ymax)]

# # import re
# # import cv2
# # import numpy as np
# # import pytesseract
# # from PIL import Image


# # def extract_invoice_data(image_path_or_pil):
# #   """Processes an invoice image using OpenCV ROIs and refined anchor

# #   extraction for vendor name, billing address, invoice number, and totals.
# #   """
# #   if isinstance(image_path_or_pil, str):
# #     image = Image.open(image_path_or_pil)
# #   else:
# #     image = image_path_or_pil

# #   img_cv = np.array(image)
# #   if len(img_cv.shape) == 3:
# #     gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
# #   else:
# #     gray = img_cv

# #   img_height, img_width = gray.shape[:2]

# #   # ==========================================
# #   # 1. OpenCV ROI (Region of Interest) Slicing
# #   # ==========================================
# #   roi_vendor = gray[0 : int(img_height * 0.35), 0 : int(img_width * 0.6)]
# #   roi_invoice_num = gray[0 : int(img_height * 0.35), int(img_width * 0.45) : img_width]
# #   roi_totals = gray[int(img_height * 0.4) : img_height, int(img_width * 0.35) : img_width]

# #   def run_ocr_on_roi(roi_img, offset_x=0, offset_y=0):
# #     data = pytesseract.image_to_data(
# #         roi_img, output_type=pytesseract.Output.DICT
# #     )
# #     boxes = []
# #     for i in range(len(data['text'])):
# #       word = data['text'][i].strip()
# #       if word:
# #         x, y, w, h = (
# #             data['left'][i] + offset_x,
# #             data['top'][i] + offset_y,
# #             data['width'][i],
# #             data['height'][i],
# #         )
# #         boxes.append(
# #             {
# #                 'text': word,
# #                 'coordinates': [int(x), int(y), int(x + w), int(y + h)],
# #             }
# #         )
# #     return boxes

# #   vendor_boxes = run_ocr_on_roi(roi_vendor, 0, 0)
# #   inv_boxes = run_ocr_on_roi(
# #       roi_invoice_num, int(img_width * 0.45), 0
# #   )
# #   total_boxes = run_ocr_on_roi(
# #       roi_totals, int(img_width * 0.35), int(img_height * 0.4)
# #   )

# #   # ==========================================
# #   # 2. Entity Extraction
# #   # ==========================================

# #   # --- INVOICE NUMBER ---
# #   invoice_number = 'Not Found'
# #   inv_coords = [0, 0, 0, 0]
# #   inv_full_text = ' '.join([b['text'] for b in inv_boxes])

# #   inv_match = re.search(
# #       r'(?:invoice\s*(?:no|number|num|#)|inv[\s\-#]*|order\s*#|p\.o\.#)\s*[:.]?\s*([A-Z0-9\-]{2,15})',
# #       inv_full_text,
# #       re.IGNORECASE,
# #   )
# #   if inv_match:
# #     invoice_number = inv_match.group(1)
# #     inv_coords = get_box_for_phrase(invoice_number, inv_boxes)
# #   else:
# #     for b in inv_boxes:
# #       txt = b['text']
# #       if (
# #           re.match(r'^[A-Z0-9\-]{3,10}$', txt)
# #           and txt.upper() not in ['INVOICE', 'DATE', 'DUE', 'TAX', 'TOTAL', 'LOGO']
# #           and not txt.startswith('01/')
# #       ):
# #         invoice_number = txt
# #         inv_coords = b['coordinates']
# #         break

# #   # --- TOTAL (Supports Grand Total, Invoice total, Sub total fallbacks) ---
# #   total_value = 'Not Found'
# #   total_coords = [0, 0, 0, 0]
# #   total_full_text = ' '.join([b['text'] for b in total_boxes])

# #   # Cascading search for specific total labels
# #   total_patterns = [
# #       r'(?:grand\s*total|invoice\s*total|total\s*due|amount\s*due|sub\s*total|total)[:\s]*[\$]?\s*([\d,]+\.\d{2})',
# #       r'(?:grand\s*total|invoice\s*total|sub\s*total|total)[:\s]*[\$]?\s*([\d,]+)',  # handles integers if decimals missing
# #   ]

# #   for pat in total_patterns:
# #     match = re.search(pat, total_full_text, re.IGNORECASE)
# #     if match:
# #       amt = match.group(1)
# #       total_value = f'${amt}' if not amt.startswith('$') else amt
# #       total_coords = get_box_for_phrase(amt, total_boxes)
# #       break

# #   # Fallback: largest currency value in the bottom right quadrant
# #   if total_value == 'Not Found':
# #     amounts = []
# #     for b in total_boxes:
# #       clean = b['text'].replace('$', '').replace(',', '')
# #       if re.match(r'^\d+(\.\d{2})?$', clean):
# #         amounts.append((float(clean), b))
# #     if amounts:
# #       amounts.sort(key=lambda x: x[0], reverse=True)
# #       total_value = f"${amounts[0][0]:,.2f}"
# #       total_coords = amounts[0][1]['coordinates']

# #   # --- VENDOR NAME & BILLING ADDRESS ("Bill To" / "To") ---
# #   vendor_name = 'Unknown Vendor'
# #   vendor_coords = [0, 0, 0, 0]
# #   company_address = 'Address Not Found'
# #   address_coords = [0, 0, 0, 0]

# #   # Sort vendor box words by vertical alignment
# #   sorted_v_boxes = sorted(vendor_boxes, key=lambda b: (b['coordinates'][1], b['coordinates'][0]))
  
# #   valid_vendor_words = [
# #       b
# #       for b in sorted_v_boxes
# #       if b['text'].upper()
# #       not in ['TAX', 'INVOICE', 'TAX INVOICE', 'LOGO', 'DATE', 'SHIP']
# #   ]

# #   if valid_vendor_words:
# #     first_y = valid_vendor_words[0]['coordinates'][1]
# #     name_tokens = [
# #         b for b in valid_vendor_words if abs(b['coordinates'][1] - first_y) < 15
# #     ]
# #     base_vendor = ' '.join([b['text'] for b in name_tokens])
    
# #     # Requirement 1: Add 1st line of address / recipient block to vendor name if present
# #     remaining_tokens = [
# #         b for b in valid_vendor_words if b not in name_tokens and b['coordinates'][1] > first_y
# #     ]
    
# #     first_address_line = ""
# #     if remaining_tokens:
# #       next_y = remaining_tokens[0]['coordinates'][1]
# #       addr_line_tokens = [b for b in remaining_tokens if abs(b['coordinates'][1] - next_y) < 15]
# #       first_address_line = ' '.join([b['text'] for b in addr_line_tokens])
      
# #     if first_address_line and not any(kw in first_address_line.upper() for kw in ['BILL', 'TO', 'BILL TO']):
# #       vendor_name = f"{base_vendor} - {first_address_line}"
# #     else:
# #       vendor_name = base_vendor
      
# #     vendor_coords = get_box_for_phrase(base_vendor, vendor_boxes)

# #   # Requirement 2: Anchor address extraction using "Bill To" / "To" keywords
# #   full_vendor_text = ' '.join([b['text'] for b in vendor_boxes])
# #   bill_to_match = re.search(r'(?:bill\s*to|to)\s*[:.]?', full_vendor_text, re.IGNORECASE)
  
# #   if bill_to_match or remaining_tokens:
# #     # Extract lines appearing after the 'Bill To' label or standard header offset
# #     addr_words = [
# #         b for b in valid_vendor_words 
# #         if b not in name_tokens and b['coordinates'][1] > (first_y + 20)
# #     ]
# #     if addr_words:
# #       company_address = ' '.join([b['text'] for b in addr_words[:7]])
# #       address_coords = addr_words[0]['coordinates']

# #   # Final structured JSON output
# #   structured_output = {
# #       'vendor_name': {'value': vendor_name, 'coordinates': vendor_coords},
# #       'company_address': {
# #           'value': company_address,
# #           'coordinates': address_coords,
# #       },
# #       'invoice_number': {
# #           'value': invoice_number,
# #           'coordinates': inv_coords,
# #       },
# #       'total': {'value': total_value, 'coordinates': total_coords},
# #   }

# #   return structured_output


# # def get_box_for_phrase(phrase, word_boxes):
# #   """Aggregates precise bounding coordinates for a target string."""
# #   tokens = str(phrase).replace('$', '').replace(',', '').split()
# #   matched = []
# #   for token in tokens:
# #     for wb in word_boxes:
# #       if token.lower() in wb['text'].lower() and wb not in matched:
# #         matched.append(wb)
# #         break

# #   if not matched:
# #     return [0, 0, 0, 0]

# #   xmin = min([b['coordinates'][0] for b in matched])
# #   ymin = min([b['coordinates'][1] for b in matched])
# #   xmax = max([b['coordinates'][2] for b in matched])
# #   ymax = max([b['coordinates'][3] for b in matched])
# #   return [int(xmin), int(ymin), int(xmax), int(ymax)]

# """Invoice entity extraction (vendor, billing address, invoice number, total).

# Approach: OCR the whole page once, rebuild lines and column segments from the
# word boxes, then locate each entity from its own anchors (labels + layout)
# instead of fixed page regions.

# Requires: opencv-python, numpy, pillow, pytesseract (+ the Tesseract binary).
# """
# import re
# from dataclasses import dataclass
# from statistics import median

# import cv2
# import numpy as np
# import pytesseract
# from PIL import Image

# TARGET_WIDTH = 2000      # upscale small scans to roughly this width for OCR
# MIN_CONF = 30            # drop low-confidence OCR words
# COLUMN_GAP = 2.0         # gap (x word height) that splits a line into columns
# OCR_CONFIG = '--oem 3 --psm 6'  # try --psm 4 or 11 for unusual layouts


# # --------------------------------------------------------------------------
# # Data structures
# # --------------------------------------------------------------------------
# @dataclass(eq=False)
# class Word:
#   text: str
#   x0: float
#   y0: float
#   x1: float
#   y1: float

#   @property
#   def h(self):
#     return self.y1 - self.y0

#   @property
#   def yc(self):
#     return (self.y0 + self.y1) / 2


# @dataclass(eq=False)
# class Seg:
#   """A run of words on one line with no large horizontal gap (one 'cell')."""

#   words: list

#   def __post_init__(self):
#     self.text = ' '.join(w.text for w in self.words)
#     self.x0 = min(w.x0 for w in self.words)
#     self.y0 = min(w.y0 for w in self.words)
#     self.x1 = max(w.x1 for w in self.words)
#     self.y1 = max(w.y1 for w in self.words)
#     self.h = median(w.h for w in self.words)
#     self.yc = (self.y0 + self.y1) / 2


# def _box_of(items):
#   return [
#       int(min(i.x0 for i in items)),
#       int(min(i.y0 for i in items)),
#       int(max(i.x1 for i in items)),
#       int(max(i.y1 for i in items)),
#   ]


# def _value_box(seg, value):
#   """Tight box around the word containing `value`, else the whole segment."""
#   v = value.lower()
#   for w in seg.words:
#     if v in w.text.lower():
#       return _box_of([w])
#   return _box_of([seg])


# # --------------------------------------------------------------------------
# # OCR + layout reconstruction
# # --------------------------------------------------------------------------
# def _preprocess(pil_img):
#   gray = cv2.cvtColor(np.array(pil_img.convert('RGB')), cv2.COLOR_RGB2GRAY)
#   scale = 1.0
#   if gray.shape[1] < TARGET_WIDTH:
#     scale = TARGET_WIDTH / gray.shape[1]
#     gray = cv2.resize(gray, None, fx=scale, fy=scale,
#                       interpolation=cv2.INTER_CUBIC)
#   gray = cv2.medianBlur(gray, 3)
#   _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#   return bw, scale


# def _ocr_words(bw, scale):
#   data = pytesseract.image_to_data(
#       bw, config=OCR_CONFIG, output_type=pytesseract.Output.DICT
#   )
#   words = []
#   for i, raw in enumerate(data['text']):
#     text = raw.strip()
#     try:
#       conf = float(data['conf'][i])
#     except ValueError:
#       conf = -1
#     if not text or conf < MIN_CONF:
#       continue
#     x, y = data['left'][i], data['top'][i]
#     w, h = data['width'][i], data['height'][i]
#     words.append(Word(text, x / scale, y / scale,
#                       (x + w) / scale, (y + h) / scale))
#   return words


# def _build_segments(words):
#   """Group words into lines by vertical centre, then split lines into columns."""
#   lines = []
#   for w in sorted(words, key=lambda w: w.yc):
#     if lines:
#       cur = lines[-1]
#       mean_yc = sum(x.yc for x in cur) / len(cur)
#       mean_h = sum(x.h for x in cur) / len(cur)
#       if abs(w.yc - mean_yc) <= 0.6 * max(w.h, mean_h):
#         cur.append(w)
#         continue
#     lines.append([w])

#   segs = []
#   for line in lines:
#     line.sort(key=lambda w: w.x0)
#     h = median(w.h for w in line)
#     groups = [[line[0]]]
#     for prev, w in zip(line, line[1:]):
#       if w.x0 - prev.x1 > COLUMN_GAP * h:
#         groups.append([w])
#       else:
#         groups[-1].append(w)
#     segs.extend(Seg(g) for g in groups)
#   return sorted(segs, key=lambda s: (s.y0, s.x0))


# def _right_of(seg, segs):
#   c = [
#       s for s in segs
#       if s is not seg
#       and abs(s.yc - seg.yc) <= 0.6 * max(s.h, seg.h)
#       and s.x0 >= seg.x1 - 0.5 * seg.h
#   ]
#   return sorted(c, key=lambda s: s.x0)


# def _below(seg, segs, max_gap=2.0):
#   c = [
#       s for s in segs
#       if s is not seg
#       and -0.3 * seg.h <= s.y0 - seg.y1 <= max_gap * seg.h
#       and s.x1 >= seg.x0 - seg.h
#       and s.x0 <= seg.x1 + seg.h
#   ]
#   return sorted(c, key=lambda s: (s.y0, s.x0))


# # --------------------------------------------------------------------------
# # Invoice number
# # --------------------------------------------------------------------------
# _ID = r'(?=[A-Z0-9\-/]*\d)([A-Z0-9][A-Z0-9\-/]{1,24})'  # must contain a digit
# _ID_TOKEN = re.compile(_ID, re.I)
# _INV_LABEL = r'(?:invoice|inv)\s*(?:no\.?|number|num\.?|#|id)'

# INV_PRIMARY = re.compile(r'\b' + _INV_LABEL + r'\s*[:#\-.]*\s*' + _ID, re.I)
# INV_LABEL_ONLY = re.compile(r'\b' + _INV_LABEL + r'\s*[:#\-.]*\s*$', re.I)
# INV_SECONDARY = [
#     re.compile(r'\b(?:invoice|inv)\s*[:#\-]\s*' + _ID, re.I),
#     re.compile(r'\binvoice\s+' + _ID, re.I),           # "INVOICE 12345"
#     re.compile(r'\b(?:order|receipt|ref(?:erence)?)\s*(?:no\.?|number|#)'
#                r'\s*[:#\-.]*\s*' + _ID, re.I),
# ]


# def _extract_invoice_number(segs):
#   # 1. explicit "Invoice No / Number / #" with value in the same cell
#   for seg in segs:
#     m = INV_PRIMARY.search(seg.text)
#     if m:
#       val = m.group(1).strip('-/')
#       return val, _value_box(seg, val)

#   # 2. label alone in its cell: value is to the right or directly below
#   for seg in segs:
#     if INV_LABEL_ONLY.search(seg.text):
#       for nb in _right_of(seg, segs)[:2] + _below(seg, segs)[:2]:
#         m = _ID_TOKEN.search(nb.text)
#         if m:
#           val = m.group(0).strip('-/')
#           return val, _value_box(nb, val)

#   # 3. looser patterns
#   for pat in INV_SECONDARY:
#     for seg in segs:
#       m = pat.search(seg.text)
#       if m:
#         val = m.group(1).strip('-/')
#         return val, _value_box(seg, val)

#   return 'Not Found', [0, 0, 0, 0]


# # --------------------------------------------------------------------------
# # Total
# # --------------------------------------------------------------------------
# AMOUNT = re.compile(
#     r'(?<![\w/])(?P<cur>[$€£₹]|Rs\.?|INR|USD|EUR|GBP)?\s*'
#     r'(?P<num>\d{1,3}(?:,\d{2,3})+(?:\.\d{1,2})?|\d+\.\d{2}|\d+)(?![\w/])',
#     re.I,
# )

# TOTAL_TIERS = [  # highest priority first
#     re.compile(r'\b(?:grand\s*total|total\s*(?:amount\s*)?(?:due|payable)'
#                r'|amount\s*(?:due|payable)|balance\s*due|invoice\s*total'
#                r'|total\s*amount|net\s*payable)\b', re.I),
#     re.compile(r'(?<!sub)(?<!sub\s)\btotal\b'
#                r'(?!\s*(?:tax|gst|vat|discount|qty|quantity))', re.I),
#     re.compile(r'\bsub\s*total\b', re.I),
# ]


# def _is_precise(m):
#   num = m.group('num')
#   return bool(m.group('cur')) or '.' in num or ',' in num


# def _find_amount(text, strict=False):
#   """First 'real-looking' amount; bare integers only when not strict."""
#   fallback = None
#   for m in AMOUNT.finditer(text):
#     if _is_precise(m):
#       return m
#     if not strict and fallback is None:
#       fallback = m
#   return fallback


# def _fmt_amount(m):
#   cur, num = (m.group('cur') or '').strip(), m.group('num')
#   if not cur:
#     return num
#   return f'{cur}{num}' if not cur[-1].isalpha() and cur[-1] != '.' \
#       else f'{cur} {num}'


# def _amount_near(seg, after_label, segs, allow_below):
#   m = _find_amount(after_label)
#   if m:
#     return _fmt_amount(m), _value_box(seg, m.group('num'))
#   for nb in _right_of(seg, segs)[:3]:
#     m = _find_amount(nb.text)
#     if m:
#       return _fmt_amount(m), _value_box(nb, m.group('num'))
#   if allow_below:
#     for nb in _below(seg, segs)[:2]:
#       m = _find_amount(nb.text, strict=True)
#       if m:
#         return _fmt_amount(m), _value_box(nb, m.group('num'))
#   return None


# def _extract_total(segs, img_h):
#   bottom_up = list(reversed(segs))
#   for tier, pat in enumerate(TOTAL_TIERS):
#     for seg in bottom_up:
#       m = pat.search(seg.text)
#       if not m:
#         continue
#       found = _amount_near(seg, seg.text[m.end():], segs, tier == 0)
#       if found:
#         return found

#   # Fallback: largest precise amount in the lower 60% of the page
#   best = None
#   for seg in segs:
#     if seg.yc < 0.4 * img_h:
#       continue
#     for m in AMOUNT.finditer(seg.text):
#       if _is_precise(m):
#         val = float(m.group('num').replace(',', ''))
#         if best is None or val > best[0]:
#           best = (val, m, seg)
#   if best:
#     _, m, seg = best
#     return _fmt_amount(m), _value_box(seg, m.group('num'))
#   return 'Not Found', [0, 0, 0, 0]


# # --------------------------------------------------------------------------
# # Vendor + billing address
# # --------------------------------------------------------------------------
# BILL_TO = re.compile(
#     r'^(?:(?:bill(?:ed)?|sold|invoice)\s*to\b|to\s*:)\s*[:\-]?\s*', re.I)
# STOP_LINE = re.compile(
#     r'\b(?:ship(?:ped)?\s*to|invoice|date|due|terms|p\.?o\.?|description'
#     r'|qty|quantity|item|rate|amount|total|payment)\b', re.I)
# VENDOR_NOISE = re.compile(
#     r'\b(?:invoice|date|due|phone|tel|fax|e-?mail|gstin|vat|bill\s*to'
#     r'|ship\s*to|page|original|receipt|logo)\b|@|www\.|https?:', re.I)
# COMPANY_SUFFIX = re.compile(
#     r'\b(?:inc|llc|ltd|limited|corp|corporation|co|company|gmbh|pvt|plc|llp'
#     r'|lp|ag|enterprises|industries|solutions|technologies|services|group'
#     r'|traders|stores)\b', re.I)


# def _is_vendor_candidate(seg):
#   t = seg.text.strip()
#   if len(t) < 3 or sum(c.isalpha() for c in t) < 3:
#     return False
#   if VENDOR_NOISE.search(t):
#     return False
#   return sum(c.isdigit() for c in t) / len(t) <= 0.25


# def _extract_vendor(segs, img_h, limit_y):
#   top = [
#       s for s in segs
#       if s.y1 <= 0.35 * img_h and s.y0 < limit_y and _is_vendor_candidate(s)
#   ]
#   if not top:
#     return None
#   with_suffix = [s for s in top if COMPANY_SUFFIX.search(s.text)]
#   if with_suffix:
#     return with_suffix[0]
#   max_h = max(s.h for s in top)
#   return next(s for s in top if s.h >= 0.85 * max_h)  # biggest font, topmost


# def _collect_block(start, segs, first_text='', max_lines=6):
#   """Walk down the column beneath `start`, stopping at labels or big gaps."""
#   lines = [first_text] if first_text else []
#   used = [start]
#   last = start
#   while len(lines) < max_lines:
#     cands = [
#         s for s in segs
#         if s not in used
#         and s.y0 >= last.y1 - 0.3 * last.h
#         and abs(s.x0 - start.x0) <= 2.5 * start.h
#         and (s.y0 - last.y1) <= 1.6 * last.h
#     ]
#     if not cands:
#       break
#     nxt = min(cands, key=lambda s: (s.y0, s.x0))
#     if STOP_LINE.search(nxt.text):
#       break
#     lines.append(nxt.text)
#     used.append(nxt)
#     last = nxt
#   return lines, used


# def _extract_party(segs, img_h):
#   # Billing block anchored on "Bill To" (topmost / leftmost occurrence)
#   bill_seg, rest = None, ''
#   for seg in segs:
#     m = BILL_TO.match(seg.text.strip())
#     if m:
#       bill_seg, rest = seg, seg.text.strip()[m.end():].strip()
#       break

#   limit_y = bill_seg.y0 if bill_seg else float('inf')
#   vendor_seg = _extract_vendor(segs, img_h, limit_y)

#   vendor = ('Unknown Vendor', [0, 0, 0, 0])
#   if vendor_seg:
#     vendor = (vendor_seg.text.strip(), _box_of([vendor_seg]))

#   address = ('Address Not Found', [0, 0, 0, 0])
#   if bill_seg:
#     lines, used = _collect_block(bill_seg, segs, first_text=rest)
#     body = used[1:] if not rest else used
#     if lines:
#       address = (', '.join(lines), _box_of(body or used))
#   elif vendor_seg:  # no "Bill To": fall back to lines under the vendor name
#     _, used = _collect_block(vendor_seg, segs, max_lines=3)
#     below = used[1:]
#     if below:
#       address = (', '.join(s.text for s in below), _box_of(below))

#   return vendor, address


# # --------------------------------------------------------------------------
# # Public API
# # --------------------------------------------------------------------------
# def extract_invoice_data(image_path_or_pil):
#   """Extract vendor name, billing address, invoice number and total.

#   Returns {field: {'value': str, 'coordinates': [x0, y0, x1, y1]}} with
#   coordinates in the original image's pixel space.
#   """
#   image = (Image.open(image_path_or_pil)
#            if isinstance(image_path_or_pil, str) else image_path_or_pil)
#   img_h = image.size[1]

#   bw, scale = _preprocess(image)
#   words = _ocr_words(bw, scale)
#   if not words:
#     return {
#         'vendor_name': {'value': 'Unknown Vendor', 'coordinates': [0, 0, 0, 0]},
#         'company_address': {'value': 'Address Not Found',
#                             'coordinates': [0, 0, 0, 0]},
#         'invoice_number': {'value': 'Not Found', 'coordinates': [0, 0, 0, 0]},
#         'total': {'value': 'Not Found', 'coordinates': [0, 0, 0, 0]},
#     }
#   segs = _build_segments(words)

#   inv_val, inv_box = _extract_invoice_number(segs)
#   total_val, total_box = _extract_total(segs, img_h)
#   (vendor_val, vendor_box), (addr_val, addr_box) = _extract_party(segs, img_h)

#   return {
#       'vendor_name': {'value': vendor_val, 'coordinates': vendor_box},
#       'company_address': {'value': addr_val, 'coordinates': addr_box},
#       'invoice_number': {'value': inv_val, 'coordinates': inv_box},
#       'total': {'value': total_val, 'coordinates': total_box},
#   }


# if __name__ == '__main__':
#   import json
#   import sys

#   print(json.dumps(extract_invoice_data(sys.argv[1]), indent=2))

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