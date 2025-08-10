import json
import time
import os

#AIRCRAFT_FILE = "/home/alex/dump1090-json/aircraft.json"
AIRCRAFT_FILE = "/run/dump1090-fa/aircraft.json"

# Optional: map hex to tail numbers
hex_to_tail = {
    "a7302f": "N12345",
    "ab4af1": "N67890",
}

OUTPUT_DIR = "../json_output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "aircraft_status.json")

def load_aircraft_with_position():
    if not os.path.exists(AIRCRAFT_FILE):
        return []

    with open(AIRCRAFT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    aircraft = data.get("aircraft", [])
    positioned = [ac for ac in aircraft if "lat" in ac and "lon" in ac]
    return positioned

def summarize_aircraft(ac):
    hexid = ac.get("hex", "???")
    lat = ac.get("lat", "N/A")
    lon = ac.get("lon", "N/A")
    alt = ac.get("alt_baro", "N/A")
    speed = ac.get("gs", "N/A")
    flight = ac.get("flight", "").strip()
    seen = ac.get("seen", 0)

    tail = hex_to_tail.get(hexid.lower(), "Unknown")

    return {
        "ICAO Hex": hexid,
        "Tail #": tail,
        "Flight": flight,
        "Altitude (ft)": alt,
        "Speed (knots)": speed,
        "Latitude": lat,
        "Longitude": lon,
        "Last Seen (sec ago)": round(seen, 1)
    }

def save_aircraft_to_json(aircraft):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summarized = [summarize_aircraft(ac) for ac in aircraft]

    data = {
        "timestamp": time.time(),
        "total_aircraft": len(summarized),
        "aircraft": summarized
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def display_aircraft(ac_summary):
    print(f"--- Aircraft Detected ---")
    for key, value in ac_summary.items():
        print(f"  {key:17}: {value}")
    print(f"-------------------------")

def main():
    while True:
        aircraft = load_aircraft_with_position()

        if not aircraft:
            print("No aircraft with position found.\n")
        else:
            summaries = [summarize_aircraft(ac) for ac in aircraft]
            print(f"\nDetected {len(summaries)} aircraft with position.")
            for summary in summaries:
                display_aircraft(summary)

        save_aircraft_to_json(aircraft)
        time.sleep(5)

if __name__ == "__main__":
    main()
