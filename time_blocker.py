from datetime import timedelta

def generate_time_blocks(calendar):
    blocks = []
    for event in calendar:
        if event["type"] == "Assignment":
            # Add 3 work sessions before due date
            for i in range(1, 4):
                blocks.append({
                    "title": f"Work on {event['title']}",
                    "date": event["date"] - timedelta(days=i)
                })
        elif event["type"] == "Test":
            # Add 3 study sessions before test
            for i in range(1, 4):
                blocks.append({
                    "title": f"Study for {event['title']}",
                    "date": event["date"] - timedelta(days=i)
                })
    return blocks
