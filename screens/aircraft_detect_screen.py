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

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
LabelBase.register(name="VT323", fn_regular=font_path)

TAN_COLOR = get_color_from_hex("#D2B48C")

class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', padding=20)

        scrollview = ScrollView(size_hint=(1, 1))

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
