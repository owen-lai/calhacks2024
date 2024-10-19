"""
This agent can respond to plain text questions with data from an AI model and convert it into a machine readable format.
"""
from uagents import Agent, Context, Model
import os
import requests
import json


agent = Agent(
    name="OpenAIAgent",
    port=8001,
    seed="OpenAIAgent secret phrase",
    endpoint=["http://127.0.0.1:8001/submit"]
)
# Provide an API key for OPEN AI: https://platform.openai.com/account/api-keys
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
# You can add the API key as a secret or environment variable
if OPENAI_API_KEY == None:
    raise Exception("You need to provide an API key for OPEN AI to use this example")

# Configuration for making requests to OPEN AI 
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MODEL_ENGINE = "gpt-3.5-turbo"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}


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


def get_completion(context: str, prompt: str, max_tokens: int = 1024):
    """Send a prompt and context to the AI model and return the content of the completion"""
    data = {
        "model": MODEL_ENGINE,
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(OPENAI_URL, headers=HEADERS, data=json.dumps(data))
        messages = response.json()['choices']
        message = messages[0]['message']['content']
        return message
    except Exception as ex:
        return None

    print("Got response from AI model: " + message)
    return message


def get_data(ctx: Context, request: str):
    """Instruct the AI model to retrieve data and context for the data and return it in machine readable JSON format"""
    context = '''    
    You are a helpful agent who can provide approriate replies to incoming emails in a machine readable format.
    
    Please follow these guidelines:
    1. Try to answer the question as accurately as possible, using only reliable sources.
    2. Rate your confidence in the accuracy of your answer from 0 to 1 based on the credibility of the data publisher and how much it might have changed since the publishing date.
    3. In the last line of your response, provide the information in the exact JSON format: {"value": value, "unit": unit, "timestamp": time, "confidence": rating, "source": ref, "notes": summary}
        - value is the numerical value of the data without any commas or units
        - unit is the measurement unit of the data if applicable, or an empty string if not applicable
        - time is the approximate timestamp when this value was published in ISO 8601 format
        - rating is your confidence rating of the data from 0 to 1
        - ref is a url where the data can be found, or a citation if no url is available
        - summary is a brief justification for the confidence rating (why you are confident or not confident in the accuracy of the value)
    '''

    response = get_completion(context, request, max_tokens=300)
    print(response)
    try:
        data = json.loads(response.splitlines()[-1])
        msg = Data.parse_obj(data)
        return msg
    except Exception as ex:
        exception(f"An error occurred retrieving data from the AI model: {ex}")
        return Error(text="Sorry, I wasn't able to answer your request this time. Feel free to try again.")

@agent.on_message(model=Request)
async def handle_request(ctx: Context, sender: str, request: Request):
    ctx.logger.info(f"Got request from {sender}: {request.text}")
    response = get_data(ctx, request.text)
    await ctx.send(sender, response)

if __name__ == "__main__":
    agent.run()
    
