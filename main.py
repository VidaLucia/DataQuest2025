from pdf_parser import extract_text_from_pdf
from llm_syllabus_parser import extract_schedule_info
from llm_assignment_parser import extract_assignment_info  # You'll need to create this
from calendar_generator import create_calendar_events
from time_blocker import generate_time_blocks
import json
import os

def process_pdf(pdf_path, pdf_type):
    text = extract_text_from_pdf(pdf_path)
    
    
    if pdf_type == "syllabus":
        parsed_json = extract_schedule_info(text)
    elif pdf_type == "assignment":
        parsed_json = extract_assignment_info(text)
    else:
        print(f"Unknown PDF type: {pdf_type}")
        return

    if not parsed_json:
        print(f"No data returned from LLM for {pdf_path}")
        return

    try:
        parsed_data = json.loads(parsed_json)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON for {pdf_path}:", e)
        print("Raw LLM output was:\n", parsed_json)
        return

    calendar = create_calendar_events(parsed_data)
    blocks = generate_time_blocks(calendar)

    print(f"\nProcessed: {pdf_path}")
    print("Calendar Events:")
    for event in calendar:
        print(f"{event['date'].strftime('%Y-%m-%d')} - {event['type']}: {event['title']}")

    print("\n📚 Time Blocks:")
    for block in sorted(blocks, key=lambda b: b['date']):
        print(f"{block['date'].strftime('%Y-%m-%d')} - {block['title']}")

def process_directory(base_path):
    for root, dirs, files in os.walk(base_path):
        current_dir = os.path.basename(root)
        
        # Process files in Syllabus directory
        if current_dir == "Syllabus":
            for file in files:
                if file.endswith(".pdf"):
                    pdf_path = os.path.join(root, file)
                    process_pdf(pdf_path, "syllabus")
        
        # Process files in Assignments directory
        elif current_dir == "Assignments":
            for file in files:
                if file.endswith(".pdf"):
                    pdf_path = os.path.join(root, file)
                    process_pdf(pdf_path, "assignment")

if __name__ == "__main__":
    base_path = "data/user_pdfs"
    process_directory(base_path)
