import json
import time
from pathlib import Path

# Path to dump1090 JSON output
json_path = Path("/run/dump1090-fa/aircraft.json")

while True:
    if not json_path.exists():
        print("dump1090 JSON file not found. Is dump1090 running?")
        break

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        print(f"\n{len(data['aircraft'])} aircraft detected:")
        for ac in data['aircraft']:
            hex_id = ac.get("hex", "N/A")
            lat = ac.get("lat", "N/A")
            lon = ac.get("lon", "N/A")
            alt = ac.get("alt_baro", "N/A")
            callsign = ac.get("flight", "N/A")
            print(f" - {callsign} ({hex_id}) at {alt} ft over ({lat}, {lon})")

    except json.JSONDecodeError:
        print("Waiting for valid data...")

    time.sleep(1)
