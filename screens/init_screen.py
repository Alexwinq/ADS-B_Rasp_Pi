import json
import os
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

JSON_OUTPUT_FILE = "/home/alex/ADS-B_Rasp_Pi/json_output/test_output.json"

class InitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(text="Waiting for aircraft...", font_size='18sp')
        self.add_widget(self.label)
        Clock.schedule_interval(self.update_data, 2)

    def update_data(self, dt):
        if not os.path.exists(JSON_OUTPUT_FILE):
            self.label.text = "Waiting for data..."
            return

        try:
            with open(JSON_OUTPUT_FILE, 'r') as f:
                aircraft = json.load(f)

            if not aircraft:
                self.label.text = "No aircraft currently detected."
                return

            text = f"Aircraft detected: {len(aircraft)}\n\n"

            for ac in aircraft[:5]:  # show up to 5
                text += (
                    f"Flight: {ac.get('flight', 'Unknown')}\n"
                    f"ICAO: {ac.get('hex')}\n"
                    f"Alt: {ac.get('alt_baro')} ft\n"
                    f"Speed: {ac.get('gs')} knots\n"
                    f"Lat: {ac.get('lat')}, Lon: {ac.get('lon')}\n"
                    f"Seen: {ac.get('seen')} sec ago\n"
                    f"{'-'*30}\n"
                )

            self.label.text = text

        except Exception as e:
            self.label.text = f"Error loading data:\n{e}"
