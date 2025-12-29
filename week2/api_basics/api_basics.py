import json
from pathlib import Path
from urllib.request import urlopen

URL = "https://api.github.com/rate_limit"
OUTPUT = Path("result.json")

def main() -> None:
    with urlopen(URL) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # 3 Werte rausziehen
    current_user_url = data.get("current_user_url")
    emojis_url = data.get("emojis_url")
    rate_limit_url = data.get("rate_limit_url")

    print("current_user_url:", current_user_url)
    print("emojis_url:", emojis_url)
    print("rate_limit_url:", rate_limit_url)

    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\nGespeichert: {OUTPUT.resolve()}")

if __name__ == "__main__":
    main()