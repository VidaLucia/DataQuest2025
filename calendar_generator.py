from datetime import datetime

def create_calendar_events(parsed_data):
    calendar = []
    for item in parsed_data.get("assignments", []):
        calendar.append({
            "title": item["title"],
            "date": datetime.strptime(item["due_date"], "%Y-%m-%d"),
            "type": "Assignment"
        })
    for item in parsed_data.get("tests", []):
        calendar.append({
            "title": item["title"],
            "date": datetime.strptime(item["date"], "%Y-%m-%d"),
            "type": "Test"
        })
    return calendar
