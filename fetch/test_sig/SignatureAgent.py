from uagents import Agent, Context, Model
import fitz
import json
import requests
from PIL import Image
#import cv2
import pytesseract
from pdf2image import convert_from_path
import os
import numpy as np
from datetime import datetime

json_file = "easy-pdf.json"

def download_pdf(url, output_pdf_path):
    """Download the PDF from a Google Drive link."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF to {output_pdf_path}")
    else:
        raise Exception(f"Failed to download the PDF. Status code: {response.status_code}")

def parse_json_for_attachments(json_file):
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
   return pdf_link, pdf_name

 
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
 
@SignatureAgent.on_message(model=PDF)
async def message_handler(ctx: Context, sender: str, pdf: PDF):
   """Log response from AI Model Agent """
   ctx.logger.info(f"Got request from {sender}: {pdf.path}")
   # Parse the Json File and Download PDF
   #pdf_link, pdf_name = parse_json_for_attachments(json_file)
   pdf_name = pdf.path
   # Process the PDF
   ctx.logger.info(f"Got a request to process the PDF file at: {pdf_name}")
   pdf_document = fitz.open(pdf_name)
   pages = convert_from_path(pdf_name, dpi=300)
   signature_keywords = ["Signature", "Sign Here", "SIGNATURE", "SIGN HERE"]
   date_keywords = ["Date", "DATE", "Date Signed", "DATE SIGNED"]
   name_keywords = ["PRINT NAME", "NAME"]

   #Load the upsampler using OpenCV DNN Super Resolution module
   #sr = cv2.dnn_superres.DnnSuperResImpl_create()
   #sr.readModel("ESPCN_x3.pb")
   #sr.setModel("espcn", 3)

   for page_number, page_image in enumerate(pages):
       page = pdf_document.load_page(page_number)
       blocks = page.get_text("dict")["blocks"]
       print(f"Scanning page {page_number + 1}...")
       '''gray_image = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2GRAY)
       #gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
       #gray_image = cv2.fastNlMeansDenoising(gray_image, None, 30, 7, 21)
       #gray_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
       #rgb_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGB)
       #gray_image = sr.upsample(np.array(rgb_image))
       #cv2.imshow('Thresholded Image', gray_image)
       #cv2.waitKey(0)
       #cv2.destroyAllWindows()
       
       # Extract text and metadata, like bounding boxes
       blocks = page.get_text("dict")["blocks"]
       data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT)
        
       # Search for "Signature" or "Sign Here"
       n_boxes = len(data['level'])
       for i in range(n_boxes):
           text = data['text'][i].strip()
           if any(keyword in text for keyword in signature_keywords):
               print(f"Signature field found on page {page_number + 1}")
               print(f"Text: {text}")
               print(f"Coordinates: {(255*255*data['left'][i]/(382*709), 255*255*data['top'][i]/(382*709), 255*255*data['width'][i]/(382*709), 255*255*data['height'][i]/(382*709))}")
               x, y = 255*255*data['left'][i]/(382*709), 255*255*data['top'][i]/(382*709)
               signature_image = Image.open("signature.png")
               width, height = 50, 20
               temp_signature_image = "temp_signature.png"
               signature_image.save(temp_signature_image)

               page.insert_image(fitz.Rect(x, y, x+width, y+height), filename=temp_signature_image)
               os.remove(temp_signature_image)'''
       
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

                           page.insert_image(fitz.Rect(x+70, y-10, x+70+width, y-10+height), filename=temp_signature_image)

                           os.remove(temp_signature_image)

                       if any(keyword in text for keyword in date_keywords):
                           print(f"Date field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")

                           x, y, X, Y = span['bbox']

                           current_date = datetime.now().strftime("%m/%d/%Y")
                           page.insert_text((x, y+20), current_date, fontsize=10)

                       if any(keyword in text for keyword in name_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           name = "Andy Yang"

                           page.insert_text((x, y+20), name, fontsize=10)


   # Save the updated PDF with changes
   pdf_document.save("scanned_for_signature.pdf")
   pdf_document.close()

   os.remove(pdf_name)

   print("Signed PDF saved to scanned_for_signature.pdf")

if __name__=="__main__":
    SignatureAgent.run()
