"""
This agent can ask a question to the AI model agent and display the answer.
"""
from email import message
from re import sub
import time
from uagents import Agent, Context, Model
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GmailAPI.getemail import get_latest_email
from GmailAPI.sendemail import gmail_create_draft
from InvitationAgent import is_email_invitation

agent = Agent(
    name="UserAgent",
    port=8000,
    seed="UserAgent secret phrase",
    endpoint=["http://127.0.0.1:8000/submit"]
)

AI_MODEL_AGENT_ADDRESS = (
    "agent1qwckwhmmyp5zl3d67dn2r844v4nt0ygcaxwpglr3vn0e83lagfujq86a38n"
)

SIGNATURE_AGENT_ADDRESS = "agent1qwfq7d60ue0s90gyff0xxm8sq76vlem26kg7m6y54y0tr2zv2xymyr4zh5f"

INVITATION_AGENT_ADDRESS = "agent1q282j36p24ugscjyhwn7yn59l66f6l8neudff2pp6ve2tgasae59xhcm7jw"

class Request(Model):
    text: str


class Error(Model):
    text: str


class Data(Model):
    subject: str
    body: str
    recipient: str
    timestamp: str
    confidence: float
    source: str
    notes: str

class EmailInfo:
    thread_id: int
    message_id: int
    subject: str
    sender: str
    body: str
    labelIds: list[str]
    pdfPath: str
    in_reply_to: str
    references: str

class PDF(Model):
    path: str

class Message(Model):
   message: str
 

email = EmailInfo()


@agent.on_interval(5.0)
async def ask_question(ctx: Context):
    """Send question to AI Model Agent"""
    #ctx.logger.info(f"Hello, my address is {ctx.address}.")
    email.thread_id, email.message_id, email.subject, email.sender, email.body, email.labelIds, email.pdfPath, email.in_reply_to, email.references = get_latest_email()
    path = is_email_invitation(get_service(), 'me', email.message_id)
    if "UNREAD" in email.labelIds:
        QUESTION = f"Sender Email: {email.sender}, Body: {email.body}"
        ctx.logger.info(f"Asking question to AI model agent: {QUESTION}")
        if email.pdfPath:
            await ctx.send(SIGNATURE_AGENT_ADDRESS, PDF(path=email.pdfPath))
        elif path != "": # if there is a path to a ics file
            await ctx.send(INVITATION_AGENT_ADDRESS, Message(str="hi"))
        await ctx.send(AI_MODEL_AGENT_ADDRESS, Request(text=QUESTION))
        

@agent.on_message(model=Data)
async def handle_data(ctx: Context, sender: str, data: Data):
    """Log response from AI Model Agent """
    pdfpath = None
    if email.pdfPath:
        pdfpath = email.pdfPath
    gmail_create_draft(subject=email.subject, body=data.body, recipient=data.recipient, threadID=email.thread_id, messageID=email.message_id, in_reply_to=email.in_reply_to, references=email.references, filepath=pdfpath)
    ctx.logger.info(f"Got response from AI model agent: {data}")

@agent.on_message(model=Message)
async def handle_data(ctx: Context, sender: str, msg: Message):
    """Log response from Invitation Agent """
    # gmail_create_draft(subject=email.subject, body=data.body, recipient=data.recipient, threadID=email.thread_id, messageID=email.message_id, in_reply_to=email.in_reply_to, references=email.references, filepath=pdfpath)
    ctx.logger.info(f"Got response from Invitation agent: {msg}")

@agent.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    """log error from AI Model Agent"""
    ctx.logger.info(f"Got error from AI model agent: {error}")

if __name__ == "__main__":
    agent.run()
