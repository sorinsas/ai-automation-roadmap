import argparse
import csv
import json
import re
from datetime import datetime, date
from pathlib import Path
from typing import Any

OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)

DEFAULT_RATE = 70
DEFAULT_PEOPLE = 1
DEFAULT_STATUS = "OPEN"  # wir setzen alle generierten Tasks erstmal als OPEN

FIELDS_CSV = ["title", "owner", "due_date", "priority", "status", "minutes_saved_per_week"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Meeting Notes -> JSON -> CSV -> ROI Report")
    p.add_argument("--notes", type=str, default="meeting_notes.txt", help="Pfad zu Meeting Notes txt")
    p.add_argument("--offline", action="store_true", help="Offline Testdaten statt OpenAI verwenden")
    p.add_argument("--rate", type=int, default=DEFAULT_RATE, help="Stundensatz EUR/h")
    p.add_argument("--people", type=int, default=DEFAULT_PEOPLE, help="Teamgröße")
    p.add_argument("--status", type=str, default=DEFAULT_STATUS, help="Status für Tasks (OPEN/DONE/...)")
    return p.parse_args()


def euro(minutes: int, hourly_rate: int) -> float:
    return (minutes / 60) * hourly_rate


def extract_minutes(title: str, notes: str) -> int:
    """
    Versucht Minuten aus Zeilen wie 'ROI-Report erstellen (90)' zu lesen.
    Wenn nix gefunden wird, 0.
    """
    # Suche exakt nach einer Zeile, die den Title enthält und (Zahl) hat
    # Sehr simpel, reicht fürs Mini-Produkt.
    pattern = re.compile(rf"{re.escape(title)}\s*\((\d+)\)", re.IGNORECASE)
    m = pattern.search(notes)
    return int(m.group(1)) if m else 0


def build_tasks_offline(notes: str, status: str) -> dict[str, Any]:
    # Offline: wir tun so als ob die KI Tasks extrahiert hat
    base = [
        {"title": "ROI-Report erstellen", "owner": "Sorin", "due_date": "Freitag", "priority": "high"},
        {"title": "Feedback geben", "owner": "Claudia", "due_date": None, "priority": "medium"},
        {"title": "3 Kunden ansprechen", "owner": None, "due_date": "nächste Woche", "priority": "high"},
        {"title": "Demo-Video erstellen", "owner": "Sorin", "due_date": "Mittwoch", "priority": "medium"},
    ]
    for t in base:
        t["status"] = status.upper()
        t["minutes_saved_per_week"] = extract_minutes(t["title"], notes)
    return {"tasks": base}


def build_tasks_openai(notes: str, status: str) -> dict[str, Any]:
    """
    Nutzt OpenAI, wenn verfügbar. Wenn Quota/Key fehlt, sollst du mit --offline laufen.
    """
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:
        raise RuntimeError("OpenAI SDK nicht verfügbar. Installiere `pip install openai` oder nutze --offline.") from e

    client = OpenAI()
    prompt = f"""
Du extrahierst Aufgaben aus Meeting-Notizen.
Gib ausschließlich gültiges JSON zurück, ohne Erklärung, ohne Markdown.

Schema:
{{
  "tasks": [
    {{
      "title": "string",
      "owner": "string|null",
      "due_date": "string|null",
      "priority": "low|medium|high"
    }}
  ]
}}

Meeting-Notizen:
{notes}
""".strip()

    resp = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )

    text = resp.output_text.strip()
    data = json.loads(text)  # wenn kein JSON => JSONDecodeError

    # Zusatzfelder ergänzen (status + minutes)
    tasks = data.get("tasks", [])
    for t in tasks:
        title = str(t.get("title", "")).strip()
        t["status"] = status.upper()
        t["minutes_saved_per_week"] = extract_minutes(title, notes)

    return {"tasks": tasks}


def write_json(data: dict[str, Any], ts: str) -> Path:
    path = OUT_DIR / f"tasks_{ts}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_csv(tasks: list[dict[str, Any]], ts: str) -> Path:
    path = OUT_DIR / f"tasks_{ts}.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS_CSV)
        w.writeheader()
        for t in tasks:
            row = {k: t.get(k) for k in FIELDS_CSV}
            w.writerow(row)
    return path


def write_roi_report(tasks: list[dict[str, Any]], ts: str, rate: int, people: int, status_filter: str) -> Path:
    # Nur Tasks mit passendem Status für ROI
    filtered = [t for t in tasks if str(t.get("status", "")).upper() == status_filter.upper()]

    total_minutes = 0
    for t in filtered:
        m = t.get("minutes_saved_per_week") or 0
        try:
            total_minutes += int(m)
        except Exception:
            pass

    total_hours = total_minutes / 60
    weekly_single = euro(total_minutes, rate)
    weekly_team = weekly_single * people
    monthly_team = weekly_team * 4
    yearly_team = weekly_team * 52

    path = OUT_DIR / f"roi_report_{ts}.md"

    lines = []
    lines.append(f"# ROI Report ({date.today().isoformat()})")
    lines.append("")
    lines.append(f"**Status-Filter:** `{status_filter.upper()}`")
    lines.append(f"**Stundensatz:** {rate} €/h")
    lines.append(f"**Teamgröße:** {people}")
    lines.append("")
    lines.append("## Tasks (gefiltert)")
    lines.append("")
    lines.append("| title | owner | due_date | priority | minutes_saved_per_week |")
    lines.append("|------|-------|----------|----------|------------------------:|")
    for t in filtered:
        lines.append(
            f"| {t.get('title','')} | {t.get('owner','') or ''} | {t.get('due_date','') or ''} | "
            f"{t.get('priority','')} | {t.get('minutes_saved_per_week',0)} |"
        )

    lines.append("")
    lines.append("## Ergebnis")
    lines.append("")
    lines.append(f"- Minuten pro Woche (Summe): **{total_minutes}**")
    lines.append(f"- Stunden pro Woche (Summe): **{total_hours:.2f}**")
    lines.append(f"- € pro Woche (pro Person): **{weekly_single:.2f} €**")
    lines.append(f"- € pro Woche (Team): **{weekly_team:.2f} €**")
    lines.append(f"- € pro Monat (Team): **{monthly_team:.2f} €**")
    lines.append(f"- € pro Jahr (Team): **{yearly_team:.2f} €**")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    args = parse_args()

    notes_path = Path(args.notes)
    if not notes_path.exists():
        raise FileNotFoundError(f"Notes Datei nicht gefunden: {notes_path.resolve()}")

    notes = notes_path.read_text(encoding="utf-8")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        if args.offline:
            data = build_tasks_offline(notes, status=args.status)
        else:
            data = build_tasks_openai(notes, status=args.status)

        # JSON validiert sich hier automatisch, weil wir entweder dict bauen
        # oder json.loads(...) gemacht haben.
        tasks = data.get("tasks", [])
        if not isinstance(tasks, list):
            raise ValueError("Ungültiges Format: 'tasks' ist keine Liste.")

        json_path = write_json(data, ts)
        csv_path = write_csv(tasks, ts)
        report_path = write_roi_report(tasks, ts, rate=args.rate, people=args.people, status_filter=args.status)

        print("OK Pipeline fertig:")
        print("JSON:", json_path.resolve())
        print("CSV:", csv_path.resolve())
        print("REPORT:", report_path.resolve())
        print("Tasks:", len(tasks))

    except json.JSONDecodeError as e:
        print("FEHLER: OpenAI Antwort war kein gültiges JSON.")
        print("JSON Fehler:", e)
        print("Tipp: Nutze --offline oder verbessere Prompt.")
    except Exception as e:
        print("FEHLER:", repr(e))
        print("Tipp: Teste erstmal mit --offline.")


if __name__ == "__main__":
    main()