
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

if not api_key or api_key == "your_actual_api_key_here":
    print("ERROR: API key is missing or still a placeholder.")
elif not model:
    print("ERROR: OPENAI_MODEL is missing.")
else:
    print("SUCCESS: API configuration loaded.")
    print(f"Model configured: {model}")
