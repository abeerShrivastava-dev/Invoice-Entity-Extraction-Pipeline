# import gradio as gr
# from ocr_engine import extract_invoice_data


# def process_invoice(image):
#   """Gratio wrapper function to process uploaded invoice image and return JSON."""
#   if image is None:
#     return {"error": "Please upload a valid invoice image."}

#   # Call extraction logic from ocr_engine.py
#   extracted_data = extract_invoice_data(image)
#   return extracted_data


# # Build Gradio Blocks UI
# with gr.Blocks(theme=gr.themes.Soft()) as demo:
#   gr.Markdown('# 📄 AI-Powered Invoice Entity Extraction Pipeline')
#   gr.Markdown(
#       'Upload an invoice or receipt image to extract Vendor Name, Company'
#       ' Address, Invoice Number, and Total with coordinates in structured'
#       ' JSON.'
#   )

#   with gr.Row():
#     with gr.Column():
#       input_image = gr.Image(type='pil', label='Upload Invoice Image')
#       submit_btn = gr.Button('Extract Entities', variant='primary')

#     with gr.Column():
#       output_json = gr.JSON(label='Structured JSON Output (Values & Coordinates)')

#   submit_btn.click(
#       fn=process_invoice, inputs=input_image, outputs=output_json
#   )

# if __name__ == '__main__':
#   demo.launch(server_name='127.0.0.1', server_port=7860, share=False)

# import pathlib
# import sys
# import gradio as gr
# from ocr_engine import extract_invoice_data

# # --- WINDOWS / BROTLI SECURITY POLICY AUTO-PATCH ---
# try:
#   import gradio.brotli_middleware as bm
#   from starlette.middleware.base import BaseHTTPMiddleware

#   class PassThroughBrotliMiddleware(BaseHTTPMiddleware):

#     async def dispatch(self, request, call_next):
#       return await call_next(request)

#   bm.BrotliMiddleware = PassThroughBrotliMiddleware
# except Exception:
#   pass
# # ---------------------------------------------------


# def process_invoice(image):
#   """Gratio wrapper function to process uploaded invoice image and return JSON."""
#   if image is None:
#     return {"error": "Please upload a valid invoice image."}

#   # Call extraction logic from ocr_engine.py
#   extracted_data = extract_invoice_data(image)
#   return extracted_data


# # Build Gradio Blocks UI
# with gr.Blocks(theme=gr.themes.Soft()) as demo:
#   gr.Markdown("# 📄 AI-Powered Invoice Entity Extraction Pipeline")
#   gr.Markdown(
#       "Upload an invoice or receipt image to extract **Vendor Name**, **Company"
#       " Address**, **Invoice Number**, and **Total** with coordinates in"
#       " structured JSON."
#   )

#   with gr.Row():
#     with gr.Column():
#       input_image = gr.Image(type="pil", label="Upload Invoice Image")
#       submit_btn = gr.Button("Extract Entities", variant="primary")

#     with gr.Column():
#       output_json = gr.JSON(label="Structured JSON Output (Values & Coordinates)")

#   submit_btn.click(fn=process_invoice, inputs=input_image, outputs=output_json)

# if __name__ == "__main__":
#   demo.launch(server_name="127.0.0.1", server_port=7860, share=False)

# import sys
# import types

# # --- MOCK BROTLI IN MEMORY TO BYPASS WINDOWS DLL BLOCK ---
# fake_brotli = types.ModuleType("brotli")
# fake_brotli.MODE_FONT = 0
# fake_brotli.MODE_GENERIC = 0
# fake_brotli.MODE_TEXT = 0


# class DummyCompressor:

#   def compress(self, data):
#     return data


# fake_brotli.Compressor = DummyCompressor
# sys.modules["brotli"] = fake_brotli
# # --------------------------------------------------------

# import gradio as gr
# from ocr_engine import extract_invoice_data


# def process_invoice(image):
#   """Gratio wrapper function to process uploaded invoice image and return JSON."""
#   if image is None:
#     return {"error": "Please upload a valid invoice image."}

#   # Call extraction logic from ocr_engine.py
#   extracted_data = extract_invoice_data(image)
#   return extracted_data


# # Build Gradio Blocks UI
# with gr.Blocks(theme=gr.themes.Soft()) as demo:
#   gr.Markdown("# 📄 AI-Powered Invoice Entity Extraction Pipeline")
#   gr.Markdown(
#       "Upload an invoice or receipt image to extract **Vendor Name**, **Company"
#       " Address**, **Invoice Number**, and **Total** with coordinates in"
#       " structured JSON."
#   )

#   with gr.Row():
#     with gr.Column():
#       input_image = gr.Image(type="pil", label="Upload Invoice Image")
#       submit_btn = gr.Button("Extract Entities", variant="primary")

#     with gr.Column():
#       output_json = gr.JSON(label="Structured JSON Output (Values & Coordinates)")

#   submit_btn.click(fn=process_invoice, inputs=input_image, outputs=output_json)

# if __name__ == "__main__":
#   demo.launch(server_name="127.0.0.1", server_port=7860, share=False)

# import sys
# import types

# # --- MOCK BROTLI IN MEMORY WITH ACCEPTED ARGUMENTS ---
# fake_brotli = types.ModuleType("brotli")
# fake_brotli.MODE_FONT = 0
# fake_brotli.MODE_GENERIC = 0
# fake_brotli.MODE_TEXT = 0


# class DummyCompressor:

#   def __init__(self, *args, **kwargs):
#     pass

#   def compress(self, data):
#     return data


# fake_brotli.Compressor = DummyCompressor
# sys.modules["brotli"] = fake_brotli
# # --------------------------------------------------------

# import gradio as gr
# from ocr_engine import extract_invoice_data


# def process_invoice(image):
#   """Gratio wrapper function to process uploaded invoice image and return JSON."""
#   if image is None:
#     return {"error": "Please upload a valid invoice image."}

#   # Call extraction logic from ocr_engine.py
#   extracted_data = extract_invoice_data(image)
#   return extracted_data


# # Build Gradio Blocks UI (theme parameter moved to launch for Gradio 6.0+)
# with gr.Blocks() as demo:
#   gr.Markdown("# 📄 AI-Powered Invoice Entity Extraction Pipeline")
#   gr.Markdown(
#       "Upload an invoice or receipt image to extract **Vendor Name**, **Company"
#       " Address**, **Invoice Number**, and **Total** with coordinates in"
#       " structured JSON."
#   )

#   with gr.Row():
#     with gr.Column():
#       input_image = gr.Image(type="pil", label="Upload Invoice Image")
#       submit_btn = gr.Button("Extract Entities", variant="primary")

#     with gr.Column():
#       output_json = gr.JSON(label="Structured JSON Output (Values & Coordinates)")

#   submit_btn.click(fn=process_invoice, inputs=input_image, outputs=output_json)

# if __name__ == "__main__":
#   demo.launch(
#       server_name="127.0.0.1", server_port=7860, share=False, theme="soft"
#   )

# import sys
# import types

# # --- MOCK BROTLI IN MEMORY WITH ALL REQUIRED METHODS ---
# fake_brotli = types.ModuleType("brotli")
# fake_brotli.MODE_FONT = 0
# fake_brotli.MODE_GENERIC = 0
# fake_brotli.MODE_TEXT = 0


# class DummyCompressor:

#   def __init__(self, *args, **kwargs):
#     pass

#   def compress(self, data):
#     return data

#   def flush(self, *args, **kwargs):
#     return b""

#   def finish(self, *args, **kwargs):
#     return b""


# fake_brotli.Compressor = DummyCompressor
# sys.modules["brotli"] = fake_brotli
# # --------------------------------------------------------

# import gradio as gr
# from ocr_engine import extract_invoice_data


# def process_invoice(image):
#   """Gratio wrapper function to process uploaded invoice image and return JSON."""
#   if image is None:
#     return {"error": "Please upload a valid invoice image."}

#   # Call extraction logic from ocr_engine.py
#   extracted_data = extract_invoice_data(image)
#   return extracted_data


# # Build Gradio Blocks UI
# with gr.Blocks() as demo:
#   gr.Markdown("# 📄 AI-Powered Invoice Entity Extraction Pipeline")
#   gr.Markdown(
#       "Upload an invoice or receipt image to extract **Vendor Name**, **Company"
#       " Address**, **Invoice Number**, and **Total** with coordinates in"
#       " structured JSON."
#   )

#   with gr.Row():
#     with gr.Column():
#       input_image = gr.Image(type="pil", label="Upload Invoice Image")
#       submit_btn = gr.Button("Extract Entities", variant="primary")

#     with gr.Column():
#       output_json = gr.JSON(label="Structured JSON Output (Values & Coordinates)")

#   submit_btn.click(fn=process_invoice, inputs=input_image, outputs=output_json)

# if __name__ == "__main__":
#   demo.launch(
#       server_name="127.0.0.1", server_port=7860, share=False, theme="soft"
#   )

import gradio as gr
from ocr_engine import extract_invoice_data


def process_invoice(image):
  """Gratio wrapper function to process uploaded invoice image and return JSON."""
  if image is None:
    return {"error": "Please upload a valid invoice image."}

  # Call extraction logic from ocr_engine.py
  extracted_data = extract_invoice_data(image)
  return extracted_data


# Build Gradio Blocks UI
with gr.Blocks() as demo:
  gr.Markdown("# 📄 Invoice Entity Extraction Pipeline")
  gr.Markdown(
      "Upload an invoice or receipt image to extract **Vendor Name**, **Company"
      " Address**, **Invoice Number**, and **Total** with coordinates in"
      " structured JSON."
  )

  with gr.Row():
    with gr.Column():
      input_image = gr.Image(type="pil", label="Upload Invoice Image")
      submit_btn = gr.Button("Extract Entities", variant="primary")

    with gr.Column():
      output_json = gr.JSON(label="Structured JSON Output (Values & Coordinates)")

  submit_btn.click(fn=process_invoice, inputs=input_image, outputs=output_json)

if __name__ == "__main__":
  demo.launch(
      server_name="127.0.0.1", server_port=7860, share=False, theme="soft"
  )
