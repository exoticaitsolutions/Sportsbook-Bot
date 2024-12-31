import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the google_credentials path from the .env file
OPENAI_KEY = os.getenv('OPENAI_KEY')

def chat_gpt_integration(messages):
    openai.api_key = OPENAI_KEY
    messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": messages}
            ]
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you're using GPT-4
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            # Extract the assistant's response
    assistant_response = response.choices[0].message['content'].strip()
    print("Response => ",assistant_response,"  ")
    return assistant_response