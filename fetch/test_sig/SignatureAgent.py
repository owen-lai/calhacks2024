from uagents import Agent, Context, Model
import fitz
import json
import requests
from PIL import Image
import os

def download_pdf(url, output_pdf_path):
    """Download the PDF from a Google Drive link."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF to {output_pdf_path}")
    else:
        raise Exception(f"Failed to download the PDF. Status code: {response.status_code}")
 
class Message(Model):
    message: str

class PDF(Model):
    path: str
 
SignatureAgent = Agent(
   name="SignatureAgent",
   port=11000,
   seed="SignatureAgent secret phrase",
   endpoint=["http://127.0.0.1:11000/submit"],
)
 
print(SignatureAgent.address)
 
@SignatureAgent.on_event("startup")
async def message_handler(ctx: Context):
   """Log response from AI Model Agent """
   json_file = "easy-pdf.json"
   # Load the JSON file
   with open(json_file, 'r') as file:
       data = json.load(file)
   
   # Extract the link to the PDF attachment
   for part in data['payload']['parts']:
       if part['mimeType'] == 'application/pdf' and 'attachmentLink' in part:
           pdf_link = part['attachmentLink']
           pdf_name = part['filename']
           break
   else:
       raise ValueError("No PDF attachment link found in the JSON.")
   
   # Download the PDF
   download_pdf(pdf_link, pdf_name)

   # Process the PDF
   ctx.logger.info(f"Got a request to process the PDF file at: {pdf_name}")
   pdf_document = fitz.open(pdf_name)
   #clutter = []

   for page_number in range(len(pdf_document)):
       page = pdf_document.load_page(page_number)
       print(f"Scanning page {page_number + 1}...")
       
       # Extract text and metadata, like bounding boxes
       blocks = page.get_text("dict")["blocks"]
       
       # Search for "Signature" or "Sign Here"
       for block in blocks:
           if "lines" in block:  # Block contains text
               for line in block["lines"]:
                   for span in line["spans"]:
                       text = span["text"]
                       if "Signature" in text or "Sign Here" in text or "SIGNATURE" in text:
                           print(f"Signature field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")  # Bounding box coordinates
                           # span['bbox'] is where we need to paste the signature

                           x, y, X, Y = span['bbox']
                           signature_image = Image.open("signature.png")
                           width, height = 70, 30
                           temp_signature_image = "temp_signature.png"
                           signature_image.save(temp_signature_image)

                           page.insert_image(fitz.Rect(x, y, x+width, y+height), filename=temp_signature_image)

                           os.remove(temp_signature_image)

   # Save the updated PDF with changes
   pdf_document.save("scanned_for_signature.pdf")
   pdf_document.close()

   os.remove(pdf_name)

   print("Signed PDF saved to scanned_for_signature.pdf")

if __name__=="__main__":
    SignatureAgent.run()
