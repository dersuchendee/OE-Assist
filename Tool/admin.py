import csv

def load_responses():
    responses = []
    try:
        with open('responses.csv', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                responses.append(row)
    except FileNotFoundError:
        print("responses.csv not found.")
    return responses

def load_data():
    data = []
    try:
        with open('data.csv', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print("data.csv not found.")
    return data

def aggregate_counts(responses, data):
    # Create a dictionary to store counts for each cqid for each answer type.
    counts = {}
    for r in responses:
        cqid = r['cqid']
        answer = r['modelled_or_not'].strip()  # This could be "Yes", "No", or "I don't know"
        if cqid not in counts:
            counts[cqid] = {"Yes": 0, "No": 0, "I don't know": 0}
        # Increment count for the given answer (if it matches one of our keys)
        if answer in counts[cqid]:
            counts[cqid][answer] += 1
        else:
            # In case of unexpected answers, you can add them here
            counts[cqid][answer] = 1

    # Combine with data.csv to include the CQ text.
    aggregated = []
    for row in data:
        cqid = row['cqid']
        aggregated.append({
            'cqid': cqid,
            'cq': row['cq'],
            'yes_count': counts.get(cqid, {}).get("Yes", 0),
            'no_count': counts.get(cqid, {}).get("No", 0),
            'idk_count': counts.get(cqid, {}).get("I don't know", 0)
        })
    return aggregated

def main():
    responses = load_responses()
    data = load_data()

    if not responses or not data:
        print("Missing responses.csv or data.csv data.")
        return

    print("=== Responses from responses.csv ===")
    for r in responses:
        print(f"User: {r['user']}, CQID: {r['cqid']}, Modelled: {r['modelled_or_not']}, Difficulty: {r['difficulty']}")

    aggregated = aggregate_counts(responses, data)
    print("\n=== Aggregated Counts per CQ ===")
    for agg in aggregated:
        print(f"CQID: {agg['cqid']} | CQ: {agg['cq']} | Yes: {agg['yes_count']} | No: {agg['no_count']} | I don't know: {agg['idk_count']}")

if __name__ == '__main__':
    main()
