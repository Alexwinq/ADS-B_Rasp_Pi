from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase
from kivy.uix.floatlayout import FloatLayout

import os
import json

# Set up font and color
font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
TAN_COLOR = get_color_from_hex("#D2B48C")

class InitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]

        # Root layout: allows free positioning
        root_layout = FloatLayout()

        # Main loading text
        box_layout = BoxLayout(orientation='vertical', padding=50, size_hint=(1, 1))
        self.label = Label(
            text="Scanning for Aircraft.",
            font_size=48,
            color=TAN_COLOR,
            font_name=font_path,
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))
        box_layout.add_widget(self.label)

        # GPS label top-right
        self.gps_label = Label(
            text="Lat: ---, Lon: ---",
            size_hint=(0.4, 0.1),
            pos_hint={'right': 0.98, 'top': 0.98},
            font_size=18,
            color=TAN_COLOR,
            font_name=font_path,
            halign="right",
            valign="top"
        )
        self.gps_label.bind(size=self.gps_label.setter('text_size'))

        # Add both to root
        root_layout.add_widget(box_layout)
        root_layout.add_widget(self.gps_label)
        self.add_widget(root_layout)

        # Schedule updates
        Clock.schedule_interval(self.animate_dots, 0.5)
        Clock.schedule_interval(self.update_gps, 1)
        Clock.schedule_interval(self.check_for_aircraft_data, 5)

        # Simulated GPS values
        self.latitude = 37.7749
        self.longitude = -122.4194

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Scanning for Aircraft{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def update_gps(self, dt):
        self.gps_label.text = f"Lat: {self.latitude:.4f}, Lon: {self.longitude:.4f}"

    def check_for_aircraft_data(self, dt):
        json_path = os.path.join(os.path.dirname(__file__), "..", "json_output", "test_output.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    data = f.read().strip()
                    if data:
                        json_data = json.loads(data)
                        if isinstance(json_data, list) and json_data:
                            # Aircraft found, go to next screen
                            self.manager.get_screen('detect_ac').update_data(json_data)
                            self.manager.current = 'detect_ac'
            except Exception as e:
                print(f"Error reading JSON: {e}")
