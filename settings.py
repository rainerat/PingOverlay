import json
import os
import sys

DEFAULT_SETTINGS = {
    "host": "google.com",
    "green_threshold": 50,
    "yellow_threshold": 100,
    "show_settings_on_startup": True,
    "click_through": False
}

def get_settings_path():
    """Get the path to the settings file, ensuring it's in a persistent location."""
    if getattr(sys, 'frozen', False):
        # Running as executable - save to user's AppData folder
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        settings_dir = os.path.join(appdata, 'PingOverlay')
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, 'settings.json')
    else:
        # Running as script - save in the same directory as the script
        return os.path.join(os.path.dirname(__file__), "settings.json")

SETTINGS_FILE = get_settings_path()

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
            print(f"Settings saved to: {SETTINGS_FILE}")
        except Exception as e:
            print(f"Failed to save settings: {e}")
            print(f"Settings file path: {SETTINGS_FILE}")

    def reset(self):
        self.data = DEFAULT_SETTINGS.copy()
        self.save()