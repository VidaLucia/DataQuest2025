from pdf_parser import extract_text_from_pdf
from llm_syllabus_parser import extract_schedule_info
from llm_assignment_parser import extract_assignment_info  # You'll need to create this
from calendar_generator import export_json_to_ics
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

    print(f"\nProcessed: {pdf_path}")


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


def run_manual_matching():
    """Run manual assignment matching for selected course."""
    base_path = "data/user_pdfs"
    
    # List available courses
    courses = [d for d in os.listdir(base_path) if d.startswith("Course")]
    if not courses:
        print("\nNo courses found in", base_path)
        return

    # Show available courses
    print("\nAvailable courses:")
    for i, course in enumerate(courses, 1):
        print(f"{i}. {course}")

    # Let user select course
    while True:
        try:
            choice = input("\nSelect course number (or 'q' to quit): ").strip().lower()
            if choice == 'q':
                return
            course_idx = int(choice) - 1
            if 0 <= course_idx < len(courses):
                course_path = os.path.join(base_path, courses[course_idx])
                merged_json = match_assignments_interactive(course_path)
                if merged_json:
                    print(f"\nSuccessfully matched assignments for {courses[course_idx]}")
                break
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")


def match_assignments_interactive(course_path: str) -> dict:
    """Match assignments interactively with a side-by-side interface."""
    
    # Load syllabus JSON
    syllabus_dir = os.path.join(course_path, "Syllabus", "parsed")
    syllabus_json = None

    for file in os.listdir(syllabus_dir):
        if file.endswith("_parsed.json"):
            with open(os.path.join(syllabus_dir, file), 'r') as f:
                syllabus_json = json.load(f)
                break
    
    if not syllabus_json or 'assignments' not in syllabus_json:
        print("No valid syllabus JSON found")
        return None

    # Load assignment JSONs
    assignments_dir = os.path.join(course_path, "Assignments", "parsed")
    assignment_files = []
    if os.path.exists(assignments_dir):
        for file in os.listdir(assignments_dir):
            
            if file.endswith("_parsed.json"):
                with open(os.path.join(assignments_dir, file), 'r') as f:
                    assignment_json = json.load(f)
                    assignment_files.append((file, assignment_json))
    if not assignment_files:
        print("No assignment JSONs found to match")
        return syllabus_json

    # Track which assignments have been matched
    matched_assignments = set()
    
    while True:
        print("\n=== Assignment Matching Interface ===")
        print("\nSyllabus Assignments:")
        for i, assignment in enumerate(syllabus_json['assignments'], 1):
            print(f"{i}. {assignment.get('title', 'Untitled')} "
                  f"(Due: {assignment.get('due_date', 'Not specified')})")

        print("\nParsed Assignment Files:")


        for i, (filename, json_data) in enumerate(assignment_files, 1):
            if isinstance(json_data, dict) and 'assignment' in json_data:
                assignments = json_data['assignment']
                if isinstance(assignments, list):
                    for assignment in assignments:
                        title = assignment.get('title', 'Untitled')
                        due_date = assignment.get('due_date', 'Not specified')
                        print(f"{i}. {filename}: {title} (Due: {due_date})")
                else:
                    print(f"{i}. {filename} has 'assignment' key but it's not a list.")
            else:
                print(f"{i}. {filename} skipped (no valid 'assignment' key or not a dict).")

        print("\nEnter two numbers to match (e.g., '1 2' matches syllabus item 1 with assignment 2)")
        print("Or enter 'q' to finish matching")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            break
            
        try:
            syllabus_idx, assignment_idx = map(int, choice.split())
            if (1 <= syllabus_idx <= len(syllabus_json['assignments']) and 
                1 <= assignment_idx <= len(assignment_files)):
                
                # Get the assignment data
                _, assignment_json = assignment_files[assignment_idx - 1]
                assignments = assignment_json.get('assignment', [])

                if assignments:
                    parsed_assignment = assignments[0]
                    syllabus_assignment = syllabus_json['assignments'][syllabus_idx - 1]

                    # Only update title and difficulty
                    # Update all relevant fields
                    for field in ['title', 'difficulty', 'weight', 'due_time']:
                        if field in parsed_assignment:
                            syllabus_assignment[field] = parsed_assignment[field]

                    matched_assignments.add(assignment_idx)
                    print("\n Successfully matched assignments!")

                else:
                    print("\n No assignment data found in the selected file")
            else:
                print("\n Invalid assignment numbers")
        except (ValueError, IndexError):
            print("\n Invalid input format. Please enter two numbers separated by space")

    # Save updated syllabus JSON
    output_path = ("data/user_pdfs/syllabus_matched.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(syllabus_json, f, indent=4, ensure_ascii=False)
    print(f"\nSaved matched assignments to: {output_path}")
    
    return syllabus_json

def edit_schedule():
    path = "data/user_pdfs/syllabus_matched.json"

    if not os.path.exists(path):
        print("No matched syllabus file found.")
        return

    with open(path, "r") as f:
        data = json.load(f)

    def show_section(name, entries, fields):
        print(f"\n{name} Entries:")
        for idx, item in enumerate(entries, 1):
            summary = " | ".join(f"{field}: {item.get(field, 'N/A')}" for field in fields)
            print(f"{idx}. {summary}")

    while True:
        print("\n=== Edit Schedule Menu ===")
        print("1. Edit Assignments")
        print("2. Edit Tests")
        print("3. Edit Class Schedule")
        print("q. Go back")

        section_choice = input("\nChoose section to edit: ").strip().lower()
        if section_choice == 'q':
            break

        if section_choice == '1':
            section_name = "Assignments"
            key = "assignments"
            fields = ["title", "due_date", "due_time"]
        elif section_choice == '2':
            section_name = "Tests"
            key = "tests"
            fields = ["title", "date", "time"]
        elif section_choice == '3':
            section_name = "Schedule"
            key = "schedule"
            fields = ["name","days", "time", "location"]
        else:
            print("Invalid option.")
            continue

        items = data.get(key, [])
        if not items:
            print(f"No {section_name.lower()} found.")
            continue

        show_section(section_name, items, fields)

        entry_input = input(f"\nEnter entry number to edit or 'd <num>' to delete, or 'b' to go back: ").strip().lower()
        if entry_input == 'b':
            continue
        elif entry_input.startswith('d '):
            try:
                idx = int(entry_input[2:]) - 1
                if 0 <= idx < len(items):
                    deleted = items.pop(idx)
                    print(f"Deleted {section_name[:-1]}: {deleted.get('title', deleted)}")
                else:
                    print("Invalid number.")
            except:
                print("Invalid delete command.")
        else:
            try:
                idx = int(entry_input) - 1
                if 0 <= idx < len(items):
                    entry = items[idx]
                    print(f"Editing {section_name[:-1]}: {entry.get('title', entry)}")
                    for field in fields:
                        current = entry.get(field, "")
                        new_val = input(f"{field} [{current}]: ").strip()
                        if new_val:
                            if field == "days":
                                entry[field] = [d.strip().capitalize() for d in new_val.split(',')]
                            else:
                                entry[field] = new_val
                    print("Entry updated.")
                else:
                    print("Invalid number.")
            except:
                print("Invalid input.")

        # Save after each edit
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            print("Saved changes.")

if __name__ == "__main__":
    while True:
        print("\n=== PDF Processing and Assignment Matching Tool ===")
        print("1. Process PDFs and create JSON files")
        print("2. Manually match assignments")
        print("3. Edit Schedule")
        print("4. Compile into Calender")
        print("q. Quit")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == '1':
            process_directory("data/user_pdfs")
            print("\nFinished processing PDFs")
        elif choice == '2':
            run_manual_matching()
        elif choice == '3':
            edit_schedule()
        elif choice == '4':
            with open("data/user_pdfs/syllabus_matched.json", "r") as f:  # Replace with your actual file
                data = json.load(f)
            export_json_to_ics(data,"course_calendar.ics")
        else:
            print("Invalid option. Please try again.")
