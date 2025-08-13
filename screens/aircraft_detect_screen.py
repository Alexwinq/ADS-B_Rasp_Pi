from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.app import App
import os
import json

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
TAN_COLOR = get_color_from_hex("#D2B48C")

class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20)
        self.data_label = Label(
            text="",  # Start empty since data should exist when this screen is shown
            font_size=24,
            color=TAN_COLOR,
            font_name=font_path,
            halign='left',
            valign='top'
        )
        self.data_label.bind(size=self.data_label.setter('text_size'))

        self.layout.add_widget(self.data_label)
        self.add_widget(self.layout)

    def update_data(self, json_data):
        formatted_text = json.dumps(json_data, indent=2)
        self.data_label.text = formatted_text
