import subprocess
import time

aircraft_list = []

process = subprocess.Popen(
    ["dump1090-fa", "--interactive"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

for line in process.stdout:
    if line.startswith("Hex") or line.strip() == "":
        continue  # Skip header and blank lines

    parts = line.split()
    if len(parts) >= 11:
        aircraft = {
            "hex": parts[0],
            "flight": parts[3],
            "altitude": parts[4],
            "speed": parts[5],
            "heading": parts[6],
            "lat": parts[7],
            "lon": parts[8],
            "timestamp": time.time()
        }

        # Only save if coordinates are valid
        try:
            lat = float(aircraft["lat"])
            lon = float(aircraft["lon"])
            aircraft_list.append(aircraft)
        except ValueError:
            pass

    # You could refresh every 10 seconds
    if time.time() - aircraft_list[0]["timestamp"] > 10:
        # Save to file, or update a radar screen
        print(f"Tracked {len(aircraft_list)} aircraft:")
        for ac in aircraft_list:
            print(f"{ac['flight']} at {ac['lat']}, {ac['lon']}")
        aircraft_list.clear()
