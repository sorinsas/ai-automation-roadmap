import csv
from pathlib import Path
from datetime import date
import argparse

INPUT_FILE = Path("tasks.csv")
OUTPUT_FILE = Path("report.md")

STATUS_FILTER = "OPEN"
HOURLY_RATE_EUR = 70  # <- hier kannst du später ändern

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ROI Report aus CSV erstellen")
    parser.add_argument("--rate", type=int, default=HOURLY_RATE_EUR, help="Stundensatz in EUR (z.B. 70)")
    parser.add_argument("--status", type=str, default=STATUS_FILTER, help="Status-Filter (z.B. OPEN)")
    parser.add_argument("--input", type=str, default=str(INPUT_FILE), help="Input CSV Datei (z.B. tasks.csv)")
    parser.add_argument("--output", type=str, default=str(OUTPUT_FILE), help="Output Report Datei (z.B. report.md)")
    return parser.parse_args()

def euro(minutes: int, hourly_rate: int) -> float:
    return (minutes / 60) * hourly_rate

def main() -> None:
    args = parse_args()

    input_file = Path(args.input)
    output_file = Path(args.output)
    status_filter = args.status.strip().upper()
    hourly_rate = args.rate

    if not input_file.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {input_file.resolve()}")

    with input_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    filtered = [
        r for r in rows
        if (r.get("status") or "").strip().upper() == status_filter
    ]

    total_minutes = 0
    for r in filtered:
        m = r.get("minutes_saved_per_week") or "0"
        total_minutes += int(m)

    total_hours = total_minutes / 60

    weekly_eur = euro(total_minutes, hourly_rate)
    monthly_eur = weekly_eur * 4
    yearly_eur = weekly_eur * 52

    lines = []
    lines.append(f"# ROI Report ({date.today().isoformat()})")
    lines.append("")
    lines.append(f"**Filter:** status = `{status_filter}`")
    lines.append(f"**Stundensatz:** {hourly_rate} €/h")
    lines.append("")
    lines.append("## Gefilterte Tasks")
    lines.append("")
    lines.append("| id | task | minutes_saved_per_week |")
    lines.append("|---:|------|------------------------:|")

    for r in filtered:
        lines.append(f"| {r['id']} | {r['task']} | {r['minutes_saved_per_week']} |")

    lines.append("")
    lines.append("## Ergebnis")
    lines.append("")
    lines.append(f"- Minuten pro Woche (Summe): **{total_minutes}**")
    lines.append(f"- Stunden pro Woche (Summe): **{total_hours:.2f}**")
    lines.append(f"- € pro Woche: **{weekly_eur:.2f} €**")
    lines.append(f"- € pro Monat (~4 Wochen): **{monthly_eur:.2f} €**")
    lines.append(f"- € pro Jahr (~52 Wochen): **{yearly_eur:.2f} €**")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Das ist eine grobe ROI-Schätzung basierend auf Minuten-Ersparnis.")
    lines.append("- In echten Projekten ergänzt man: Fehlerreduktion, Qualität, Risiko, Durchlaufzeit.")

    report = "\n".join(lines)
    output_file.write_text(report, encoding="utf-8")
    print(f"Report geschrieben: {output_file.resolve()}")

if __name__ == "__main__":
    main()