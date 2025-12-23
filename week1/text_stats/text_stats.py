from collections import Counter
import re
from pathlib import Path

INPUT_FILE = Path("input.txt")
OUTPUT_FILE = Path("report.txt")

def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9äöüÄÖÜß]+", text.lower())

    stopwords = {
        "und", "oder", "für", "der", "die", "das", "ein", "eine", "einer",
        "ich", "du", "wir", "ihr", "sie", "es",
        "ist", "sind", "war", "waren", "sein",
        "mit", "ohne", "zu", "im", "in", "am", "an", "auf", "von", "bei",
        "dass", "wie", "was", "wenn", "weil", "aber", "auch", "nicht",
    }

    return [t for t in tokens if t not in stopwords]

def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {INPUT_FILE.resolve()}")

    text = INPUT_FILE.read_text(encoding="utf-8")
    tokens = tokenize(text)

    if not tokens:
        print("Keine Wörter gefunden.")
        return

    counts = Counter(tokens)
    top10 = counts.most_common(10)

    lines = []
    lines.append(f"Datei: {INPUT_FILE.name}")
    lines.append(f"Wörter gesamt: {len(tokens)}")
    lines.append("")
    lines.append("Top 10 Wörter:")
    for word, n in top10:
        lines.append(f"{word}: {n}")

    report = "\n".join(lines)

    print(report)
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"\nReport gespeichert in: {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    main()