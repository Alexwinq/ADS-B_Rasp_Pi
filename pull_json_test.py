import json
import time
import os

AIRCRAFT_FILE = "/home/alex/dump1090-json/aircraft.json"

# Optional: map hex to tail numbers
hex_to_tail = {
    "a7302f": "N12345",
    "ab4af1": "N67890",
}

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

def display_aircraft(ac):
    hexid = ac.get("hex", "???")
    lat = ac.get("lat", "N/A")
    lon = ac.get("lon", "N/A")
    alt = ac.get("alt_baro", "N/A")
    speed = ac.get("gs", "N/A")  # ground speed
    flight = ac.get("flight", "").strip()
    seen = ac.get("seen", 0)

    tail = hex_to_tail.get(hexid.lower(), "Unknown")

    print(f"--- Aircraft Detected ---")
    print(f"  ICAO Hex : {hexid}")
    print(f"  Tail #   : {tail}")
    print(f"  Flight   : {flight}")
    print(f"  Altitude : {alt} ft")
    print(f"  Speed    : {speed} knots")
    print(f"  Lat/Lon  : {lat}, {lon}")
    print(f"  Last seen: {seen:.1f} sec ago")
    print(f"-------------------------")

def main():
    index = 0

    while True:
        aircraft = load_aircraft_with_position()

        if not aircraft:
            print("No aircraft with position found.\n")
        else:
            ac = aircraft[index % len(aircraft)]
            print(f"\nAircraft {index % len(aircraft) + 1} of {len(aircraft)}")
            display_aircraft(ac)
            index += 1

        time.sleep(10)

if __name__ == "__main__":
    main()
