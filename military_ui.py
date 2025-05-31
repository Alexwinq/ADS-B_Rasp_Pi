from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.config import Config

# Fullscreen and hide mouse
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'show_cursor', '0')

# Optional: Register a custom military-style font
LabelBase.register(name="Military", fn_regular="VT323-Regular.ttf")  # Make sure the font file is present

# COLORS
MILITARY_GREEN = get_color_from_hex("#00FF00")  # Bright green
BLACK = get_color_from_hex("#000000")

class InitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]

        self.label = Label(
            text="Initializing.",
            font_size=48,
            color=MILITARY_GREEN,
            font_name="Military",
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))

        self.layout = BoxLayout(orientation='vertical', padding=50)
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)

        # Animate dots every 0.5s
        Clock.schedule_interval(self.animate_dots, 0.5)
        # Move to next screen after 8 seconds
        Clock.schedule_once(self.goto_main_screen, 8)

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Initializing{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def goto_main_screen(self, dt):
        self.manager.current = 'main'

    def goto_main_screen(self, dt):
        self.manager.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=20)
        button = Button(
            text="Begin scanning for aircraft",
            font_size=32,
            size_hint=(0.6, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=BLACK,
            color=MILITARY_GREEN,
            font_name="Military"
        )
        layout.add_widget(button)
        self.add_widget(layout)

class MilitaryApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(InitScreen(name='init'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    MilitaryApp().run()
