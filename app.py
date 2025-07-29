from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.init_screen import InitScreen
from screens.aircraft_detect_screen import AircraftDetect
# Later: from screens.home_screen import HomeScreen

class TrackerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InitScreen(name="loading"))
        sm.add_widget(AircraftDetect(name="detect_ac"))
        sm.current = "loading"
        return sm

if __name__ == "__main__":
    TrackerApp().run()
