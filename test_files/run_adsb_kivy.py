import subprocess
import json
import time
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

DUMP1090_PATH = "/usr/bin/dump1090-fa"
JSON_DIR = "/home/alex/dump1090-json"
JSON_FILE = f"{JSON_DIR}/aircraft.json"

class ADSBApp(App):
    def build(self):
        self.label = Label(text="Starting dump1090-fa...", font_size='20sp')
        # Start dump1090-fa as a subprocess
        self.dump_process = subprocess.Popen([
            DUMP1090_PATH,
            "--net",
            "--write-json", JSON_DIR,
            "--gain", "-10"
        ])
        # Wait a moment to let dump1090 create files
        time.sleep(2)
        # Schedule periodic data updates
        Clock.schedule_interval(self.update_data, 5)
        return self.label

    def update_data(self, dt):
        try:
            with open(JSON_FILE, "r") as f:
                data = json.load(f)
        except Exception as e:
            self.label.text = f"Error reading JSON:\n{e}"
            return

        aircraft_list = data.get("aircraft", [])
        if not aircraft_list:
            self.label.text = "No aircraft detected."
        else:
            display_text = "Aircraft detected:\n"
            for ac in aircraft_list[:10]:
                flight = ac.get("flight", "N/A")
                altitude = ac.get("altitude", "N/A")
                display_text += f"{flight} @ {altitude} ft\n"
            self.label.text = display_text

    def on_stop(self):
        # Make sure to terminate dump1090 process when the app closes
        if self.dump_process.poll() is None:  # still running
            self.dump_process.terminate()
            self.dump_process.wait()

if __name__ == "__main__":
    ADSBApp().run()
