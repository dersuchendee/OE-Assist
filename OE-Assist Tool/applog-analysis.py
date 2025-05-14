import re
import csv
from datetime import datetime

logfile = "app.log"

# Regex patterns to detect events
login_re    = re.compile(r"User '([^']+)' logged in at .* with ordering '([^']+)'")
moved_re    = re.compile(r"User '([^']+)' moved from intro to questions")
answer_re   = re.compile(r"User '([^']+)' answered question (\d+) with '([^']+)' and difficulty (\d+)")
get_q_re    = re.compile(r'GET /question/(\d+)')
finished_re = re.compile(r"User '([^']+)' has finished the questionnaire")

def parse_timestamp(line):
    # Assumes the timestamp is at the very start of the line, e.g.
    # "2025-03-31 08:49:07,197 - INFO - ..."
    timestamp_str = line.split(" - ")[0]
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")

# List to hold all sessions
all_sessions = []
current_session = None

with open(logfile, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Check for a login event
        login_match = login_re.search(line)
        if login_match:
            # If there is an unfinished session, add it first.
            if current_session is not None:
                all_sessions.append(current_session)
            username = login_match.group(1)
            ordering = login_match.group(2)
            current_session = {
                "username": username,
                "ordering": ordering,
                "start_time": None,
                "end_time": None,
                "questions": {}  # keys will be question numbers
            }
            continue

        # Check for "moved from intro to questions" (session start)
        moved_match = moved_re.search(line)
        if moved_match and current_session is not None and moved_match.group(1) == current_session["username"]:
            current_session["start_time"] = parse_timestamp(line)
            continue

        # Check for GET /question/X events (to record question start time)
        get_q_match = get_q_re.search(line)
        if get_q_match and current_session is not None:
            q_num = int(get_q_match.group(1))
            if q_num not in current_session["questions"]:
                current_session["questions"][q_num] = {}
            # Record start time only if not already set
            if "start_time" not in current_session["questions"][q_num]:
                current_session["questions"][q_num]["start_time"] = parse_timestamp(line)
            continue

        # Check for an answer event
        answer_match = answer_re.search(line)
        if answer_match and current_session is not None and answer_match.group(1) == current_session["username"]:
            q_num = int(answer_match.group(2))
            answer = answer_match.group(3)
            difficulty = int(answer_match.group(4))
            if q_num not in current_session["questions"]:
                current_session["questions"][q_num] = {}
            current_session["questions"][q_num]["answer"] = answer
            current_session["questions"][q_num]["difficulty"] = difficulty
            # Use the answer event's timestamp as the question's end time
            current_session["questions"][q_num]["end_time"] = parse_timestamp(line)
            continue

        # Check for finished questionnaire event (session end)
        finished_match = finished_re.search(line)
        if finished_match and current_session is not None and finished_match.group(1) == current_session["username"]:
            current_session["end_time"] = parse_timestamp(line)
            all_sessions.append(current_session)
            current_session = None
            continue

# If a session was still open at the end, add it
if current_session is not None:
    all_sessions.append(current_session)

# Determine the maximum question number across all sessions
max_q = 0
for session in all_sessions:
    if session["questions"]:
        max_q = max(max_q, max(session["questions"].keys()))

# Define CSV column headers:
fieldnames = ["username", "ordering", "start_time", "end_time"]
for q in range(max_q + 1):
    fieldnames.extend([f"q{q}_start", f"q{q}_end", f"q{q}_answer", f"q{q}_difficulty"])

# Write out the CSV file
with open("user_sessions.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for session in all_sessions:
        row = {
            "username": session["username"],
            "ordering": session["ordering"],
            "start_time": session["start_time"],
            "end_time": session["end_time"]
        }
        for q in range(max_q + 1):
            q_data = session["questions"].get(q, {})
            row[f"q{q}_start"] = q_data.get("start_time")
            row[f"q{q}_end"] = q_data.get("end_time")
            row[f"q{q}_answer"] = q_data.get("answer")
            row[f"q{q}_difficulty"] = q_data.get("difficulty")
        writer.writerow(row)

print("CSV exported to user_sessions.csv")
