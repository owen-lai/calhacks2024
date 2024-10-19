from uagents import Agent, Context, Model
 
 
 
class Message(Model):
    message: str

class PDF(Model):
    text: str
 
SignatureAgent = Agent(
   name="SignatureAgent",
   port=11000,
   seed="SignatureAgent secret phrase",
   endpoint=["http://127.0.0.1:8001/submit"],
)
 
print(ReceiverAgent.address)
 
@SignatureAgent.on_message(model=Message)
async def message_handler(ctx: Context, sender: str, msg: Message):
   ctx.logger.info(f"Received message from {sender}: {msg.message}")
 
   # send the response
   await ctx.send(sender, Message(message="Cool! Let's get started!"))
 
 
if __name__ == "__main__":
   SignatureAgent.run()
