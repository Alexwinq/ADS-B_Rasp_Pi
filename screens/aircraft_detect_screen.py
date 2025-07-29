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

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
TAN_COLOR = get_color_from_hex("#D2B48C")

class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)