import csv
from pathlib import Path

INPUT_FILE = Path("input.csv")
OUTPUT_FILE = Path("output.csv")

def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {INPUT_FILE.resolve()}")

    with INPUT_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    open_rows = [r for r in rows if (r.get("status") or "").strip().upper() == "OPEN"]

    if not open_rows:
        print("Keine OPEN-Zeilen gefunden.")
        return

    # gleiche Spalten wie input
    fieldnames = reader.fieldnames
    if not fieldnames:
        raise ValueError("CSV hat keine Header-Zeile (Spaltennamen).")

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(open_rows)

    total_minutes = sum(int(r["minutes_saved"]) for r in open_rows if (r.get("minutes_saved") or "").isdigit())

    print(f"Gefiltert: {len(open_rows)} OPEN-Zeilen")
    print(f"Output: {OUTPUT_FILE.resolve()}")
    print(f"Gesparte Minuten (Summe OPEN): {total_minutes}")

if __name__ == "__main__":
    main()