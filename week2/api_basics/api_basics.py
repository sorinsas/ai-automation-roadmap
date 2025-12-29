import json
from pathlib import Path
from urllib.request import urlopen

URL = "https://api.github.com/rate_limit"
OUTPUT = Path("result.json")

def main() -> None:
    with urlopen(URL) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Werte aus /rate_limit rausziehen
    rate = data.get("rate", {})
    resources = data.get("resources", {})

    core = resources.get("core", {})
    search = resources.get("search", {})

    print("RATE (gesamt) limit:", rate.get("limit"))
    print("RATE (gesamt) remaining:", rate.get("remaining"))
    print("RATE (gesamt) reset:", rate.get("reset"))

    print("CORE remaining:", core.get("remaining"), "von", core.get("limit"))
    print("SEARCH remaining:", search.get("remaining"), "von", search.get("limit"))

    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\nGespeichert: {OUTPUT.resolve()}")

if __name__ == "__main__":
    main()