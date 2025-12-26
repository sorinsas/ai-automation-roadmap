import csv
import logging
from pathlib import Path

LOG_FILE = Path("app.log")

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ],
    )

def filter_csv(input_path: Path, output_path: Path, status_filter: str = "DONE") -> int:
    if not input_path.exists():
        raise FileNotFoundError(f"Input-Datei nicht gefunden: {input_path}")

    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError("CSV hat keine Header-Zeile (Spaltennamen).")

        rows = list(reader)

    filtered = [
        r for r in rows
        if (r.get("status") or "").strip().upper() == status_filter.upper()
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(filtered)

    return len(filtered)

def main() -> None:
    setup_logging()

    # Du kannst hier schnell umschalten:
    input_path = Path("good.csv")   # test: "bad.csv"
    output_path = Path("out.csv")

    try:
        logging.info("Starte Filter: input=%s output=%s", input_path, output_path)
        n = filter_csv(input_path, output_path, status_filter="OPEN")
        logging.info("Fertig. Gefilterte Zeilen: %s", n)
        logging.info("Output gespeichert: %s", output_path.resolve())
    except Exception as e:
        logging.exception("Fehler: %s", e)

if __name__ == "__main__":
    main()