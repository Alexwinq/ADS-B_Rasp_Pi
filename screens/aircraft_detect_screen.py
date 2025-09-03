from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
import os
import json
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.uix.floatlayout import FloatLayout

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
LabelBase.register(name="VT323", fn_regular=font_path)

TAN_COLOR = get_color_from_hex("#D2B48C")



class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', padding=20)
        root_layout = FloatLayout()
        scrollview = ScrollView(size_hint=(1, 1))
        self.latitude = 37.7749
        self.longitude = -122.4194

        self.data_label = Label(
            text="",
            font_size=24,
            color=TAN_COLOR,
            font_name="VT323",
            halign='left',
            valign='top',
            size_hint_y=None,  # height is dynamic
            text_size=(self.width, None),  # Initial value, will update dynamically
        )
        self.data_label.bind(texture_size=self.update_label_height)
        self.bind(size=self.update_label_width)

        scrollview.add_widget(self.data_label)
        self.layout.add_widget(scrollview)
        self.add_widget(self.layout)
        # GPS coordinates label positioned top-right via pos_hint
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
        root_layout.add_widget(self.gps_label)

    def update_label_height(self, instance, texture_size):
        instance.height = texture_size[1]

    def update_label_width(self, instance, value):
        # Update text_size width to label width for wrapping text nicely
        self.data_label.text_size = (self.width - 40, None)  # minus padding
        # Force re-render
        self.data_label.texture_update()

    def update_data(self, json_data):
        formatted_text = json.dumps(json_data, indent=2)
        self.data_label.text = formatted_text
