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
        # If parsed_json is already a dictionary, no need to parse

        if isinstance(parsed_json, dict):
            parsed_data = parsed_json
        else:
            # Clean the JSON string before parsing
            cleaned_json = parsed_json.strip()
            # Handle code block wrappers like ```json
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json.strip("`")
                if cleaned_json.lower().startswith("json"):
                    cleaned_json = cleaned_json[4:].strip()
            cleaned_json = cleaned_json.replace("'", '"')
            parsed_data = json.loads(cleaned_json)
        # Save the parsed data to a JSON file
        output_dir = os.path.join(os.path.dirname(pdf_path), "parsed")
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + "_parsed.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)
            print(f"Saved parsed data to: {output_path}")

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON for {pdf_path}:", e)
        print("Raw LLM output was:\n", parsed_json)
        return
    except Exception as e:
        print(f"Unexpected error processing {pdf_path}:", e)
        return

    calendar = create_calendar_events(parsed_data)
    blocks = generate_time_blocks(calendar)

    print(f"\nProcessed: {pdf_path}")
    print("All done")

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
