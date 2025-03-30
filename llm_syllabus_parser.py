from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from API.env
load_dotenv("API.env")

# Retrieve API key from env variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def extract_schedule_info(text):
    prompt = f"""
    From the following course information, extract:

    1. A list of assignments:
        - title
        - due_date (YYYY-MM-DD)
        - due_time (HH:MM or "N/A" if not clearly specified)
        - weight (percentage of final grade, e.g. 20)
        - difficulty (have this set to a default of 0) 

    2. A list of tests:
        - title
        - date (YYYY-MM-DD)
        - time (HH:MM or "N/A" if not clearly specified)
        - weight (percentage of final grade)

    3. The course schedule:
        - name of the course
        - days of the week (e.g. Monday, Wednesday)
        - time (e.g. 10:30–11:30 or "N/A")
        - location (if mentioned)

    Guidelines:
    - Name of the course should be the course code followed by the course name if possible if there are multiple different course codes
    - The assignment titles should be as descriptive as possible using words from the syllabus
    - If the time is vague or not given, return "N/A"
    - If weight is not given, use your best judgement based on previous assignments of similar name and if not additional information is available return 0
    - The total weight of everything should add up to 100 unless there are bonus marks mentioned
    - If schedule is not mentioned, return an empty list
    - If schedule has no date and location do not include it in the schedule section

    Format the output as JSON:
    {{
      "assignments": [...],
      "tests": [...],
      "schedule": [
        {{
          "name": "4931G: Introduction to Advance Medicine" 
          "days": ["Monday", "Wednesday"],
          "time": "10:30–11:30",
          "location": "Room 101"
        }}
      ]
    }}

    Course Info:
    {text}
    """

    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2)

    return response.choices[0].message.content
