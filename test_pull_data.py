import subprocess
import time

aircraft_list = []
last_report_time = time.time()

# Start dump1090-fa as a subprocess
process = subprocess.Popen(
    ["dump1090-fa", "--interactive"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

print("Started dump1090-fa... listening for aircraft.")

try:
    for line in process.stdout:
        line = line.strip()

        # Skip empty lines or headers
        if not line or line.startswith("Hex"):
            continue

        parts = line.split()
        if len(parts) >= 11:
            try:
                lat = float(parts[7])
                lon = float(parts[8])
            except ValueError:
                continue  # Skip aircraft with invalid position

            aircraft = {
                "hex": parts[0],
                "flight": parts[3],
                "altitude": parts[4],
                "speed": parts[5],
                "heading": parts[6],
                "lat": lat,
                "lon": lon,
                "timestamp": time.time()
            }

            aircraft_list.append(aircraft)

        # Every 10 seconds, print and clear the list
        if time.time() - last_report_time >= 10:
            last_report_time = time.time()

            if aircraft_list:
                print(f"\n[Update @ {time.strftime('%H:%M:%S')}] Tracked {len(aircraft_list)} aircraft:")
                for ac in aircraft_list:
                    print(f"  {ac['flight']} | Alt: {ac['altitude']} | Lat: {ac['lat']} | Lon: {ac['lon']}")
                aircraft_list.clear()
            else:
                print(f"\n[Update @ {time.strftime('%H:%M:%S')}] No aircraft with valid positions detected.")

except KeyboardInterrupt:
    print("\nInterrupted by user. Exiting.")
    process.terminate()
