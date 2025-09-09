import subprocess
import threading
import time
import json
import os
import requests

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.init_screen import InitScreen
from screens.aircraft_detect_screen import AircraftDetect  # You should have this

# Start dump1090-fa in the background
def start_dump1090():
    try:
        print("Starting dump1090-fa...")
        subprocess.Popen([
            "/usr/bin/dump1090-fa",
            "--quiet",
            "--net",
            "--write-json", "/home/alex/ADS-B_Rasp_Pi/json_output"
        ])
    except Exception as e:
        print(f"Error starting dump1090-fa: {e}")

# Fetch aircraft from localhost and save to test_output.json
def fetch_aircraft_loop():
    url = "http://localhost:8080/data/aircraft.json"
    output_file = "/home/alex/ADS-B_Rasp_Pi/json_output/test_output.json"

    while True:
        try:
            response = requests.get(url, timeout=2)
            data = response.json()
            aircraft = data.get("aircraft", [])

            results = []
            for ac in aircraft:
                if "lat" in ac and "lon" in ac:
                    results.append({
                        "hex": ac.get("hex", "unknown"),
                        "lat": ac["lat"],
                        "lon": ac["lon"],
                        "alt_baro": ac.get("alt_baro", 0),
                        "gs": ac.get("gs", 0),
                        "flight": ac.get("flight", "").strip(),
                        "seen": ac.get("seen", 0)
                    })

            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)

        except Exception as e:
            print(f"[fetch_aircraft_loop] Error: {e}")

        time.sleep(5)


class ADSBApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InitScreen(name='init'))
        sm.add_widget(AircraftDetect(name='detect_ac'))
        return sm


if __name__ == '__main__':
    # Start dump1090-fa
    start_dump1090()

    # Start background aircraft fetching thread
    threading.Thread(target=fetch_aircraft_loop, daemon=True).start()

    # Run Kivy app
    ADSBApp().run()
