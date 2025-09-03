from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget

import os
import json

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
LabelBase.register(name="VT323", fn_regular=font_path)

TAN_COLOR = get_color_from_hex("#D2B48C")


class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.latitude = 37.7749
        self.longitude = -122.4194
        self.current_index = 0
        self.aircraft_list = []

        root_layout = FloatLayout()

        # Top bar with aircraft count (left) and GPS (right)
        top_bar = BoxLayout(size_hint=(1, 0.1), padding=10, spacing=10)

        self.count_label = Label(
            text="Aircraft 0 of 0",
            font_size=18,
            color=TAN_COLOR,
            font_name=font_path,
            halign="left",
            valign="middle"
        )
        self.count_label.bind(size=self.count_label.setter('text_size'))

        self.gps_label = Label(
            text="Lat: ---, Lon: ---",
            font_size=18,
            color=TAN_COLOR,
            font_name=font_path,
            halign="right",
            valign="middle"
        )
        self.gps_label.bind(size=self.gps_label.setter('text_size'))

        top_bar.add_widget(self.count_label)
        top_bar.add_widget(self.gps_label)

        # *** Update GPS label text here with the hardcoded lat/lon ***
        self.update_gps(self.latitude, self.longitude)

        root_layout.add_widget(top_bar)

        # Buttons layout for Prev / Next
        btn_layout = BoxLayout(size_hint=(1, 0.1), padding=10, spacing=10, pos_hint={"top": 0.9})

        self.prev_button = Button(text="< Prev", size_hint=(0.2, 1))
        self.prev_button.bind(on_press=self.show_prev)

        self.next_button = Button(text="Next >", size_hint=(0.2, 1))
        self.next_button.bind(on_press=self.show_next)

        btn_layout.add_widget(self.prev_button)
        btn_layout.add_widget(Widget())  # Spacer in the middle
        btn_layout.add_widget(self.next_button)

        root_layout.add_widget(btn_layout)

        # ScrollView for aircraft data display
        self.data_label = Label(
            text="",
            font_size=24,
            color=TAN_COLOR,
            font_name="VT323",
            halign='left',
            valign='top',
            size_hint_y=None,  # height dynamic
            text_size=(self.width - 40, None),
        )
        self.data_label.bind(texture_size=self.update_label_height)
        self.bind(size=self.update_label_width)

        scrollview = ScrollView(
            size_hint=(1, 0.7),
            pos_hint={"top": 0.8}
        )
        scrollview.add_widget(self.data_label)

        root_layout.add_widget(scrollview)

        self.add_widget(root_layout)

    def update_label_height(self, instance, texture_size):
        instance.height = texture_size[1]

    def update_label_width(self, instance, value):
        self.data_label.text_size = (self.width - 40, None)
        self.data_label.texture_update()

    def update_gps(self, lat, lon):
        self.latitude = lat
        self.longitude = lon
        self.gps_label.text = f"Lat: {lat:.4f}, Lon: {lon:.4f}"

    def update_data(self, json_data):
        self.aircraft_list = json_data
        self.current_index = 0
        self.update_display()

    def update_display(self):
        total = len(self.aircraft_list)
        if total == 0:
            self.count_label.text = "Aircraft 0 of 0"
            self.data_label.text = "No aircraft detected"
            self.prev_button.disabled = True
            self.next_button.disabled = True
        else:
            self.count_label.text = f"Aircraft {self.current_index + 1} of {total}"
            aircraft = self.aircraft_list[self.current_index]
            formatted_text = json.dumps(aircraft, indent=2)
            self.data_label.text = formatted_text
            self.prev_button.disabled = (self.current_index == 0)
            self.next_button.disabled = (self.current_index == total - 1)

    def show_prev(self, instance):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def show_next(self, instance):
        if self.current_index < len(self.aircraft_list) - 1:
            self.current_index += 1
            self.update_display()
