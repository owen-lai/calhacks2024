from uagents import Agent, Context, Model
import fitz 

 
class Message(Model):
    message: str

class PDF(Model):
    path: str
 
SignatureAgent = Agent(
   name="SignatureAgent",
   port=11000,
   seed="SignatureAgent secret phrase",
   endpoint=["http://127.0.0.1:8001/submit"],
)
 
print(ReceiverAgent.address)
 
@SignatureAgent.on_message(model=PDF)
async def message_handler(ctx: Context, sender: str, filepath: PDF):
   """Log response from AI Model Agent """
    ctx.logger.info(f"Got response from AI model agent: {data}")
    #open pdf 
    pdf_document = fitz.open(filepath)

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        print(f"Scanning page {page_number + 1}...")
        
        # Extract text and metadata, like bounding boxes
        blocks = page.get_text("dict")["blocks"]
        
        # Search for "Signature" or "Sign Here"
        for block in blocks:
            if "lines" in block:  # Block contains text
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if "Signature" in text or "Sign Here" in text:
                            print(f"Signature field found on page {page_number + 1}")
                            print(f"Text: {text}")
                            print(f"Coordinates: {span['bbox']}")  # Bounding box coordinates
                            # span['bbox'] is where we need to paste the signature

                            # CODE HERE FOR THE PDF EDITTING API

    # Save the updated PDF with changes
    pdf_document.save("scanned_for_signature.pdf")
    pdf_document.close()

 
 
if __name__ == "__main__":
   SignatureAgent.run()
