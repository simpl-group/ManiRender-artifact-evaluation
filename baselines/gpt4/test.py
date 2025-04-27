# -*- coding:utf-8 -*-


import os
from openai import OpenAI
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.jsonlines')

# https://platform.openai.com/usage
OPENAI_KEY = ""
assert len(OPENAI_KEY) > 0, ValueError("Please set your OpenAI Key.")
GPT4O = "gpt-4o-2024-08-06"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_KEY}"
}

client = OpenAI(api_key=OPENAI_KEY)
response = client.chat.completions.create(
    messages=[{
        "role": "user",
        "content": "Say this is a test",
    }],
    model="gpt-4o-mini",
)
print(response._request_id)
