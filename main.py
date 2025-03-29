from pdf_parser import extract_text_from_pdf
from llm_parser import extract_schedule_info
from calendar_generator import create_calendar_events
from time_blocker import generate_time_blocks
import json

def main(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    parsed_json = extract_schedule_info(text)

    if not parsed_json:
        print("No data returned from LLM. Check your API quota or fallback settings.")
        return

    try:
        parsed_data = json.loads(parsed_json)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Raw LLM output was:\n", parsed_json)
        return

    calendar = create_calendar_events(parsed_data)
    blocks = generate_time_blocks(calendar)

    print("\n Calendar Events:")
    for event in calendar:
        print(f"{event['date'].strftime('%Y-%m-%d')} - {event['type']}: {event['title']}")

    print("\n📚 Time Blocks:")
    for block in sorted(blocks, key=lambda b: b['date']):
        print(f"{block['date'].strftime('%Y-%m-%d')} - {block['title']}")

if __name__ == "__main__":
    pdf_path = "data/user_pdfs/sample_syllabus.pdf"
    main(pdf_path)
    pdf_path = "data/user_pdfs/sample_syllabus2.pdf"
    main(pdf_path)
