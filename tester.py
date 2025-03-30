import json

response_string =  '''
{
  "assignments": [
    {
      "title": "Five-minute, policy elevator pitch",
      "due_date": "2025-03-31",
      "due_time": "08:00",
      "weight": 15
    }
  ],
  "tests": [
    {
      "title": "In class quiz 1",
      "date": "2025-01-30",
      "time": "N/A",
      "weight": 8
    },
    {
      "title": "In class quiz 2",
      "date": "2025-03-13",
      "time": "N/A",
      "weight": 8
    },
    {
      "title": "In class quiz 3",
      "date": "2025-04-03",
      "time": "N/A",
      "weight": 8
    },
    {
      "title": "Midterm examination",
      "date": "2025-03-01",
      "time": "N/A",
      "weight": 26
    },
    {
      "title": "Final Exam",
      "date": "2025-04-07",
      "time": "N/A",
      "weight": 35
    }
  ],
  "schedule": [
    {
      "days": ["Thursday"],
      "time": "14:30–16:30",
      "location": "N/A"
    }
  ]
}
'''
assignment_data = json.loads(response_string)