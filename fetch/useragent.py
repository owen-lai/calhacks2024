"""
This agent can ask a question to the AI model agent and display the answer.
"""
from re import sub
from uagents import Agent, Context, Model
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GmailAPI.getemail import get_latest_email
from GmailAPI.sendemail import gmail_create_draft

agent = Agent(
    name="UserAgent",
    port=8000,
    seed="UserAgent secret phrase",
    endpoint=["http://127.0.0.1:8000/submit"]
)

# Write your question here
thread_id, message_id, subject, sender, body = get_latest_email()
QUESTION = f"Sender Email: {sender}, Body: {body}"

AI_MODEL_AGENT_ADDRESS = (
    "agent1qwckwhmmyp5zl3d67dn2r844v4nt0ygcaxwpglr3vn0e83lagfujq86a38n"
)

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


@agent.on_event("startup")
async def ask_question(ctx: Context):
    """Send question to AI Model Agent"""
    #ctx.logger.info(f"Hello, my address is {ctx.address}.")
<<<<<<< HEAD
    print("here 1")
    ctx.logger.info(f"Asking question to AI model agent: {QUESTION}")
    await ctx.send(AI_MODEL_AGENT_ADDRESS, Request(text=QUESTION))
=======
    ctx.logger.info(f"Asking question to AI model agent: {EMAIL}")
    await ctx.send(AI_MODEL_AGENT_ADDRESS, Request(text=EMAIL))
>>>>>>> edcef9844b853dbfec24cbace172405c420a949f

@agent.on_message(model=Data)
async def handle_data(ctx: Context, sender: str, data: Data):
    """Log response from AI Model Agent """
    print("here 2")
    gmail_create_draft(subject=subject, body=data.body, recipient=data.recipient, threadID=thread_id, messageID=message_id)
    ctx.logger.info(f"Got response from AI model agent: {data}")

@agent.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    """log error from AI Model Agent"""
    print("here 3")
    ctx.logger.info(f"Got error from AI model agent: {error}")

if __name__ == "__main__":
    agent.run()
    
