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
