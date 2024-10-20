from uagents import Agent, Context, Model
import fitz
import json
import requests
from PIL import Image
#import pytesseract
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
 
#print(SignatureAgent.address)
 
@SignatureAgent.on_message(model=PDF)
#@SignatureAgent.on_event("startup")
async def message_handler(ctx: Context, sender: str, pdf: PDF):
#async def message_handler(ctx: Context):
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
   name_keywords = ["PRINT NAME"]
   sellername_keywords = ["PRINT SELLER"]
   identification_keywords = ["IDENTIFICATION NUMBER"]
   yearmodel_keywords = ["YEAR MODEL"]
   make_keywords = ["MAKE"]
   licenseplate_keywords = ["LICENSE PLATE"]
   motorcycle_keywords = ["MOTORCYCLE ENGINE"]
   sellingprice_keywords = ["SELLING PRICE"]
   giftvalue_keywords = ["GIFT VALUE"]
   mo_keywords = ["MO"]
   day_keywords = ["DAY"]
   yr_keywords = ["YR"]
   address_keywords = ["MAILING ADDRESS"]
   city_keywords = ["CITY"]
   state_keywords = ["STATE"]
   zip_keywords = ["ZIP"]
   phone_keywords = ["PHONE #"]
   dealer_keywords = ["DEALER #"]

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

                           page.insert_image(fitz.Rect(x+50, y, x+50+width, y+height), filename=temp_signature_image)

                           os.remove(temp_signature_image)

                       elif any(keyword in text for keyword in date_keywords):
                           print(f"Date field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")

                           x, y, X, Y = span['bbox']

                           current_date = datetime.now().strftime("%m/%d/%Y")
                           page.insert_text((x, y+20), current_date, fontsize=10)

                       elif any(keyword in text for keyword in name_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           name = "Andy Yang"

                           page.insert_text((x, y+20), name, fontsize=10)
                       elif any(keyword in text for keyword in sellername_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           name = "Andy Yang"

                           page.insert_text((x, y-10), name, fontsize=10)

                       elif any(keyword in text for keyword in identification_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           identification = "JTMWF4DV8C5047998"

                           page.insert_text((x, y+20), identification, fontsize=10)

                       elif any(keyword in text for keyword in yearmodel_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           yr_model = "2022"

                           page.insert_text((x, y+20), yr_model, fontsize=10)

                       elif any(keyword in text for keyword in make_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           make = "Motorcycle"

                           page.insert_text((x-10, y+20), make, fontsize=10)
                       elif any(keyword in text for keyword in licenseplate_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           license_no = "6SAM123"

                           page.insert_text((x, y+20), license_no, fontsize=10)
                       elif any(keyword in text for keyword in motorcycle_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           motorcycle_no = "52WVC10338"

                           page.insert_text((x, y+20), motorcycle_no, fontsize=10)
                       elif any(keyword in text for keyword in sellingprice_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           selling_price = "$5000"

                           page.insert_text((x, y-10), selling_price, fontsize=10)
                       elif any(keyword in text for keyword in giftvalue_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           gift_value = "N/A"

                           page.insert_text((x, y-10), gift_value, fontsize=10)
                       elif any(keyword in text for keyword in mo_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           mo = datetime.now().strftime("%m   %d    %Y")

                           page.insert_text((x, y-10), mo, fontsize=10)
                       elif any(keyword in text for keyword in address_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           address = "7605 Carraway Ave"

                           page.insert_text((x, y+20), address, fontsize=10)
                       elif any(keyword in text for keyword in city_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           city = "Springfield"

                           page.insert_text((x, y+20), city, fontsize=10)
                       elif any(keyword in text for keyword in state_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           state = "CA"

                           page.insert_text((x, y+20), state, fontsize=10)
                       elif any(keyword in text for keyword in zip_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           zipno = "95050"

                           page.insert_text((x, y+20), zipno, fontsize=10)
                       elif any(keyword in text for keyword in phone_keywords):
                           print(f"Name field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           phoneno = "5105028382"

                           page.insert_text((x, y+20), phoneno, fontsize=10)
                       elif any(keyword in text for keyword in dealer_keywords):
                           print(f"Dealer # field found on page {page_number + 1}")
                           print(f"Text: {text}")
                           print(f"Coordinates: {span['bbox']}")
                           x, y, X, Y = span['bbox']
                           dealerno = "8083204822"

                           page.insert_text((x, y+20), dealerno, fontsize=10)

















   # Save the updated PDF with changes
   pdf_document.save("scanned_for_signature.pdf")
   pdf_document.close()

   os.remove(pdf_name)

   print("Signed PDF saved to scanned_for_signature.pdf")

if __name__=="__main__":
    SignatureAgent.run()
