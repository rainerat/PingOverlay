import json
import os

DEFAULT_SETTINGS = {
    "host": "google.com",
    "green_threshold": 50,
    "yellow_threshold": 100,
    "show_settings_on_startup": True,
    "click_through": False
}

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

class Settings:
    def __init__(self):
        self.data = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.data.update(json.load(f))
            except Exception:
                pass  # Ignore errors, use defaults

    def save(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def reset(self):
        self.data = DEFAULT_SETTINGS.copy()
        self.save()