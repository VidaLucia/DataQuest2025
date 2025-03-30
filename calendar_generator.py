from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import uuid
import json

def export_json_to_ics(data, output_path):
    cal = Calendar()
    cal.add('prodid', '-//Course Calendar Export//example.com//')
    cal.add('version', '2.0')

    tz = pytz.timezone("America/Toronto")

    # === Assignments as Events ===
    for assignment in data.get("assignments", []):
        title = assignment.get("title", "Untitled Assignment")
        due_date = assignment.get("due_date")
        due_time = assignment.get("due_time", "23:59")

        if due_date and due_date != "N/A":
            try:
                dt_start = datetime.strptime(
                    f"{due_date} {due_time if due_time != 'N/A' else '23:59'}", "%Y-%m-%d %H:%M"
                )
                dt_start = tz.localize(dt_start)
                dt_end = dt_start + timedelta(hours=1)

                event = Event()
                event.add("uid", str(uuid.uuid4()))
                event.add("summary", f"Assignment: {title}")
                event.add("dtstart", dt_start)
                event.add("dtend", dt_end)
                event.add("description", f"Assignment due: {title}")
                event.add("dtstamp", datetime.now(tz))
                cal.add_component(event)
            except Exception as e:
                print(f"Error processing assignment '{title}':", e)

    # === Tests as Events ===
    for test in data.get("tests", []):
        title = test.get("title", "Untitled Test")
        date = test.get("date")
        time = test.get("time", "09:00")

        if date and date != "N/A":
            try:
                dt_start = datetime.strptime(
                    f"{date} {time if time != 'N/A' else '09:00'}", "%Y-%m-%d %H:%M"
                )
                dt_start = tz.localize(dt_start)
                dt_end = dt_start + timedelta(hours=2)

                event = Event()
                event.add("uid", str(uuid.uuid4()))
                event.add("summary", f"Test: {title}")
                event.add("dtstart", dt_start)
                event.add("dtend", dt_end)
                event.add("description", f"Test: {title}")
                event.add("dtstamp", datetime.now(tz))
                cal.add_component(event)
            except Exception as e:
                print(f"Error processing test '{title}':", e)

    # === Recurring Class Schedule as Events ===
    day_map = {
        "Monday": "MO", "Tuesday": "TU", "Wednesday": "WE",
        "Thursday": "TH", "Friday": "FR", "Saturday": "SA", "Sunday": "SU"
    }

    for session in data.get("schedule", []):
        if "name" not in session:
            session["name"] = "Class Session"
        days = session.get("days", [])
        time_range = session.get("time")
        location = session.get("location", "TBD")

        if time_range == "N/A" or not days:
            continue

        try:
            start_str, end_str = time_range.split("–")
            bydays = [day_map[day] for day in days if day in day_map]
            term_start = datetime(2025, 1, 6)
            start_day_idx = list(day_map.keys()).index(days[0])
            first_occurrence = term_start + timedelta(days=(start_day_idx - term_start.weekday()) % 7)

            start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_str.strip(), "%H:%M").time()

            dt_start = tz.localize(datetime.combine(first_occurrence, start_time))
            dt_end = tz.localize(datetime.combine(first_occurrence, end_time))

            event = Event()
            event.add("uid", str(uuid.uuid4()))
            event.add("summary", session.get("name", "Class Session"))
            event.add("location", location)
            event.add("dtstart", dt_start)
            event.add("dtend", dt_end)
            event.add("dtstamp", datetime.now(tz))
            event.add("rrule", {
                "FREQ": "WEEKLY",
                "BYDAY": bydays,
                "UNTIL": tz.localize(datetime(2025, 4, 9))
            })
            cal.add_component(event)
        except Exception as e:
            print("Error processing schedule:", e)

    # === Study Blocks as Events ===
    for block in data.get("study_blocks", []):
        title = block.get("title", "Study Block")
        date = block.get("date")
        time = block.get("time")

        if not date or not time:
            continue

        try:
            dt_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            dt_start = tz.localize(dt_start)
            dt_end = dt_start + timedelta(hours=1)

            event = Event()
            event.add("uid", str(uuid.uuid4()))
            event.add("summary", title)
            event.add("dtstart", dt_start)
            event.add("dtend", dt_end)
            event.add("description", f"Scheduled study session for: {title}")
            event.add("dtstamp", datetime.now(tz))
            cal.add_component(event)
        except Exception as e:
            print(f"Error processing study block '{title}':", e)

    # === Save to .ics ===
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())
        print(f"Exported Google Calendar compatible .ics to: {output_path}")


# === Example usage ===
if __name__ == "__main__":
    with open("data/user_pdfs/syllabus_matched.json", "r") as f:
        data = json.load(f)
    export_json_to_ics(data, "course_calendar.ics")
