import threading
import time
import requests
import json
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.init_screen import InitScreen
from screens.aircraft_detect_screen import AircraftDetect
from kivy.config import Config

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

# Path where aircraft data will be saved
OUTPUT_FILE = os.path.expanduser("~/ADS-B_Rasp_Pi/json_output/test_output.json")
DUMP1090_URL = "http://localhost:8080/data/aircraft.json"

def fetch_aircraft_loop():
    while True:
        try:
            response = requests.get(DUMP1090_URL, timeout=5)
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

            # Make sure directory exists
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, "w") as f:
                json.dump(results, f, indent=2)

            print(f"Saved {len(results)} aircraft to {OUTPUT_FILE}")

        except Exception as e:
            print(f"Error fetching or saving data: {e}")

        time.sleep(5)

class TrackerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InitScreen(name="loading"))
        sm.add_widget(AircraftDetect(name="detect_ac"))
        sm.current = "loading"
        return sm

if __name__ == "__main__":
    # Start background fetch thread
    threading.Thread(target=fetch_aircraft_loop, daemon=True).start()

    # Start Kivy app as usual
    TrackerApp().run()
