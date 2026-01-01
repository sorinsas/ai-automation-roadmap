import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)

MODEL = "gpt-4o-mini"

def main() -> None:
    client = OpenAI()

    meeting_notes = """
    Wir haben entschieden:
    - Sorin macht bis Freitag einen ersten ROI-Report aus tasks.csv.
    - Claudia prüft die Texte und gibt Feedback.
    - Wir wollen nächste Woche 3 Kunden ansprechen.
    - Sorin erstellt am Mittwoch ein Demo-Video.
    Offene Fragen:
    - Welcher Stundensatz soll im Report stehen?
    - Soll das Tool auch DONE Aufgaben berücksichtigen?
    """

    prompt = f"""
Du bist ein Assistent, der aus Meeting-Notizen Aufgaben extrahiert.
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
{meeting_notes}
"""

    try:
        resp = client.responses.create(
            model=MODEL,
            input=prompt,
        )

        text = resp.output_text.strip()

        # 1) JSON validieren
        data = json.loads(text)

        # 2) Speichern
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_json = OUT_DIR / f"tasks_{ts}.json"
        out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        print("OK. JSON gespeichert:", out_json.resolve())
        print("Anzahl Tasks:", len(data.get("tasks", [])))

    except json.JSONDecodeError as e:
        print("FEHLER: Antwort war kein gültiges JSON.")
        print("Original-Text:")
        print(text)
        print("\nJSON Fehler:", e)

    except Exception as e:
        print("FEHLER:", repr(e))

if __name__ == "__main__":
    main()