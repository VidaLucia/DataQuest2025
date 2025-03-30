import json
from datetime import datetime, timedelta, time
from collections import defaultdict

# Constants
STUDY_HOURS_START = 9  # 9:00 AM
STUDY_HOURS_END = 2 + 24  # 2:00 AM next day => 26
MAX_BLOCKS_PER_DAY_PER_ITEM = 3
DIFFICULTY_MULTIPLIER = [0.5, 0.6, 0.7, 0.85, 1, 1.10, 1.20, 1.5, 2, 2.5]
WEIGHT_HOUR_MAP = [(70, 30), (40, 20), (15, 10), (5, 3), (3, 1)]

# Get base hours based on weight
def get_base_hours(weight):
    if weight == 0:
        weight = 5
    for threshold, hours in WEIGHT_HOUR_MAP:
        if weight >= threshold:
            return hours
    return 0

# Get multiplier based on difficulty (1–10)
def get_multiplier(difficulty):
    if difficulty == 0:
        difficulty = 6
    return DIFFICULTY_MULTIPLIER[min(9, max(0, difficulty - 1))]

# Parse time range string (e.g., '13:30–15:30') to time objects
def parse_time_range(time_range):
    try:
        start_str, end_str = time_range.split('–')
        start = datetime.strptime(start_str.strip(), '%H:%M').time()
        end = datetime.strptime(end_str.strip(), '%H:%M').time()
        return start, end
    except:
        return None, None

# Get blocked class hours per day
def build_class_schedule(schedule):
    class_blocks = defaultdict(list)
    for item in schedule:
        days = item.get("days", [])
        time_range = item.get("time", "")
        start, end = parse_time_range(time_range)
        if not start or not end:
            continue
        for day in days:
            class_blocks[day].append((start, end))
    return class_blocks

# Check if a given datetime conflicts with class schedule
def is_class_conflict(dt, class_blocks):
    weekday = dt.strftime("%A")
    blocks = class_blocks.get(weekday, [])
    for start, end in blocks:
        if start <= dt.time() < end:
            return True
    return False

# Check if time is within allowed study hours
def is_study_time(dt):
    hour = dt.hour + dt.minute / 60
    return STUDY_HOURS_START <= hour or hour < 2

# Generate 1-hour blocks
def generate_blocks(item, due_date_str, is_test, class_blocks):
    title = item.get("title", "Untitled")
    weight = item.get("weight", 5)
    difficulty = item.get("difficulty", 6)
    course = item.get("course", "")
    block_type = "test" if is_test else "assignment"

    if is_test:
        hours_needed = 15 if weight > 15 else 6
        start_date = datetime.strptime(due_date_str, "%Y-%m-%d") - timedelta(days=14)
    else:
        base_hours = get_base_hours(weight)
        multiplier = get_multiplier(difficulty)
        hours_needed = int(round(base_hours * multiplier))
        start_date = datetime.strptime(due_date_str, "%Y-%m-%d") - timedelta(days=14)

    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    blocks = []
    daily_blocks = defaultdict(int)
    current = start_date.replace(hour=STUDY_HOURS_START, minute=0)

    while current <= due_date and hours_needed > 0:
        if is_study_time(current) and not is_class_conflict(current, class_blocks):
            key = (current.date(), title)
            if daily_blocks[key] < MAX_BLOCKS_PER_DAY_PER_ITEM or due_date - current < timedelta(days=2):
                block = {
                    "title": f"{'Study for ' if is_test else 'Work on '}{title}",
                    "date": current.strftime("%Y-%m-%d"),
                    "time": current.strftime("%H:%M"),
                    "type": block_type
                }
                blocks.append(block)
                daily_blocks[key] += 1
                hours_needed -= 1
        current += timedelta(minutes=60)
    return blocks

# Main function to build all blocks
def generate_time_blocks(json_data):
    all_blocks = []
    class_blocks = build_class_schedule(json_data.get("schedule", []))

    items = sorted(
        json_data.get("assignments", []) + json_data.get("tests", []),
        key=lambda x: (
            x.get("due_date") or x.get("date"),
            -x.get("weight", 0),
            -x.get("difficulty", 6)
        )
    )

    for item in items:
        is_test = "date" in item
        date_field = "date" if is_test else "due_date"
        if not item.get(date_field):
            continue
        blocks = generate_blocks(item, item[date_field], is_test, class_blocks)
        all_blocks.extend(blocks)

    return {"blocks": all_blocks}


