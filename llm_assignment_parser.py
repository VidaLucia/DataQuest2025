from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from API.env
load_dotenv("API.env")

# Retrieve API key from env variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def extract_assignment_info(text):
    prompt = f"""
    From the following assignment information, extract information.

    - title
    - due_date (format: YYYY-MM-DD)
    - due_time (format: HH:MM or "N/A" if not clearly specified)
    - difficulty (estimated from 1 to 10, where 1 = very easy and 10 = very difficult)

    Guidelines:
    - If the time is vague or not given, return "N/A"
    - Estimate difficulty based on clues in the text (length, instructions, weight, or description) 
    - there should be a negative weight shift on difficulty for assignments that only require writing
    Return as valid JSON, like this:
    {{
      "assignment": [
        {{
          "title": "Assignment 1: Intro to Python",
          "due_date": "2025-04-10",
          "due_time": "23:59",
          "difficulty": 4
        }}
        
      ]
    }}
    There should only be one assignment 
    Course Info:
    {text}
    """

    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2)

    return response.choices[0].message.content
