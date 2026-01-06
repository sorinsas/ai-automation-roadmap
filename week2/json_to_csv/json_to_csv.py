import json
import csv
from pathlib import Path

INPUT = Path("tasks.json")
OUTPUT = Path("tasks.csv")

FIELDS = ["title", "owner", "due_date", "priority"]

def main() -> None:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])

    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for t in tasks:
            row = {k: t.get(k) for k in FIELDS}
            writer.writerow(row)

    print("CSV geschrieben:", OUTPUT.resolve())
    print("Tasks:", len(tasks))

if __name__ == "__main__":
    main()