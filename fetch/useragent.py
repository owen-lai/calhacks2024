"""
This agent can ask a question to the AI model agent and display the answer.
"""
from uagents import Agent, Context, Model

agent = Agent(
    name="UserAgent",
    port=8000,
    seed="UserAgent secret phrase",
    endpoint=["http://127.0.0.1:8000/submit"]
)

# Write your question here
EMAIL = "Hi Andy, I love you. Write me a message back saying hi!"

AI_MODEL_AGENT_ADDRESS = (
    "agent1qwckwhmmyp5zl3d67dn2r844v4nt0ygcaxwpglr3vn0e83lagfujq86a38n"
)

class Request(Model):
    text: str


class Error(Model):
    text: str


class Data(Model):
    value: float
    unit: str
    timestamp: str
    confidence: float
    source: str
    notes: str


@agent.on_event("startup")
async def ask_question(ctx: Context):
    """Send question to AI Model Agent"""
    #ctx.logger.info(f"Hello, my address is {ctx.address}.")
    ctx.logger.info(f"Asking question to AI model agent: {EMAIL}")
    await ctx.send(AI_MODEL_AGENT_ADDRESS, Request(text=EMAIL))

@agent.on_message(model=Data)
async def handle_data(ctx: Context, sender: str, data: Data):
    """Log response from AI Model Agent """
    ctx.logger.info(f"Got response from AI model agent: {data}")

@agent.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    """log error from AI Model Agent"""
    ctx.logger.info(f"Got error from AI model agent: {error}")

if __name__ == "__main__":
    agent.run()
    
