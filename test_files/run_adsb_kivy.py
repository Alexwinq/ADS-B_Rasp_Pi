import json
import subprocess
import os
from time import sleep

JSON_INPUT_FILE = "/home/alex/dump1090-json/aircraft.json"
JSON_OUTPUT_FILE = "/home/alex/ADS-B_Rasp_Pi/json_output/test_output.json"
DUMP1090_PATH = "/usr/bin/dump1090-fa"

def start_dump1090():
    # Start dump1090-fa in background and write JSON
    return subprocess.Popen([
        "sudo", DUMP1090_PATH,
        "--net",
        "--gain", "-10",
        "--write-json", "/home/alex/dump1090-json"
    ])

def parse_and_save_aircraft():
    while True:
        try:
            with open(JSON_INPUT_FILE, "r") as f:
                data = json.load(f)

            aircraft_list = data.get("aircraft", [])
            output = []

            for ac in aircraft_list:
                # Filter only aircraft with position data
                if ac.get("lat") is not None and ac.get("lon") is not None:
                    entry = {
                        "hex": ac.get("hex", "N/A"),
                        "lat": ac.get("lat"),
                        "lon": ac.get("lon"),
                        "alt_baro": ac.get("altitude") or ac.get("alt_baro", None),
                        "gs": ac.get("gs", None),
                        "flight": ac.get("flight", "").strip(),
                        "seen": round(ac.get("seen", 0), 1)
                    }
                    output.append(entry)

            # Save to output file in your JSON format
            with open(JSON_OUTPUT_FILE, "w") as out:
                json.dump(output, out, indent=2)

        except Exception as e:
            print(f"Error: {e}")

        sleep(2)

if __name__ == "__main__":
    print("Starting dump1090-fa and logging aircraft data...")
    process = start_dump1090()

    try:
        parse_and_save_aircraft()
    except KeyboardInterrupt:
        print("Stopping...")
        process.terminate()
        process.wait()
