# DataQuest2025 | AI Calendar generator

A smart tool that extracts information from university course PDFs (syllabi and assignments), uses a language model to parse them, and builds a custom calendar with deadlines and scheduled study blocks.

## Features
- Uses LLMs to parse complex PDF syllabi and assignment instructions

- Organizes and merges all course data into one structured JSON

- Interactive matching of assignments to syllabus entries

- Automatically generates study/work blocks:

- Based on due dates, weight, and difficulty

- Avoids class time and sleep hours (2AM–9AM)

- Exports to .ics calendar format (Google/Apple/Outlook compatible)

- Command-line editing of assignments, tests, and class schedule

## Project Structure
```
DataQuest2025/
├── main.py                   # Main CLI loop
├── block_generator.py        # Scheduling logic
├── calendar_generator.py     # Export to .ics
├── pdf_parser.py             # Extract text from PDFs
├── llm_syllabus_parser.py    # LLM logic to parse syllabi
├── llm_assignment_parser.py  # LLM logic to parse assignments
├── data/
│   └── user_pdfs/            # Store course PDFs, parsed JSONs
│     └── CourseName/         # Name of the course
│       └──Syllabus/          # The syllabus
│       └── Assignments/      # Assignment pdfs
└── generated_blocks.json     # Output: 1-hour study/work
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/VidaLucia/DataQuest2025.git
cd DataQuest2025
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
   - Copy `API.env.template` to `API.env`
   - Replace `your_api_key_here` with your OpenAI API key
4. In user_pdfs create a new folder and 2 subfolders 'Syllabus' and 'Assignments'
5. Populate the folders with pdfs
6. Run the program:
```bash
python main.py
```
7. click 1, followed by 2 to set up all JSON files
### Command Lines
```
Select 1. Compiles the PDFs using openai's 4-o model into json files
Select 2. Manually matches any assignments from the assignments folder with any of the registered assignments in the syllabus json
Select 3. Edit # allows for adjusting any already registered json values
Select 4. Export as a .ics file # will allow you to just port your schedule into an importable format
Select 5. Allocates study time #Creates generated_blocks.json with smart 1-hour sessions, then merges it into your full course calendar.
```


### Future Goals
- Implement a front end UI for enabling smoother matching of assignments with the syllabus
- Enhanced assignment difficulty prediction
- Machine learning for better time allocation
- Multiple calendar platform support
- Mobile app development
- Integration with learning management systems
- Add in a note parser as well

### Acknowledgements
- I would like to sincerely thank Ken Jiang and Alex Caraman for their valuable input and collaboration. Their ideas on integration and our thoughtful discussions greatly contributed to the development of this project.
