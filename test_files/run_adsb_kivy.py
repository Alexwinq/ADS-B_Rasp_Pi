import json
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

JSON_PATH = "/home/alex/dump1090-json/aircraft.json"

class ADSBApp(App):
    def build(self):
        self.label = Label(text="Loading aircraft data...", font_size='20sp')
        Clock.schedule_interval(self.update_data, 5)
        return self.label

    def update_data(self, dt):
        try:
            with open(JSON_PATH, "r") as f:
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

if __name__ == "__main__":
    ADSBApp().run()
