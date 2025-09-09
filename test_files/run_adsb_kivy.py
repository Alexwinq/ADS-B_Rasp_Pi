import json
import subprocess
import threading
import time
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

DUMP1090_PATH = "/usr/bin/dump1090-fa"
JSON_DIR = "/home/alex/dump1090-json"  # Make sure this folder exists and dump1090-fa has write permission
JSON_FILE = f"{JSON_DIR}/aircraft.json"

class ADSBApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dump_process = None
        self.label = None

    def start_dump1090(self):
        # Start dump1090-fa in background writing JSON
        # Using sudo may be required depending on your setup
        self.dump_process = subprocess.Popen([
            "sudo", DUMP1090_PATH,
            "--net",
            "--write-json", JSON_DIR,
            "--gain", "-10"
        ])

    def stop_dump1090(self):
        if self.dump_process:
            self.dump_process.terminate()
            self.dump_process.wait()

    def build(self):
        self.label = Label(text="Starting ADS-B...", font_size='20sp')
        self.start_dump1090()

        # Schedule periodic update every 2 seconds
        Clock.schedule_interval(self.update_display, 2)
        return self.label

    def update_display(self, dt):
        try:
            with open(JSON_FILE, 'r') as f:
                data = json.load(f)
            aircraft_list = data.get("aircraft", [])
            if not aircraft_list:
                self.label.text = "No aircraft detected."
            else:
                display_text = "Aircraft detected:\n"
                for ac in aircraft_list[:10]:
                    flight = ac.get("flight")
                    if not flight:
                        flight = "Unknown Flight"
                    altitude = ac.get("altitude")
                    if altitude is None:
                        altitude = "Unknown Altitude"
                    else:
                        altitude = f"{altitude} ft"
                    display_text += f"{flight} @ {altitude}\n"
                self.label.text = display_text
        except Exception as e:
            self.label.text = f"Error fetching data:\n{e}"

    def on_stop(self):
        # Stop dump1090 process on app exit
        self.stop_dump1090()

if __name__ == '__main__':
    ADSBApp().run()
