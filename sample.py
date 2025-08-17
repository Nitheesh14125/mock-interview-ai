import os
from openai import OpenAI

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
print("DEBUG: OPENAI_API_KEY =", OPENAI_KEY)

client_chat = OpenAI(api_key=OPENAI_KEY)
