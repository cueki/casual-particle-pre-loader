import json
from pathlib import Path


class SettingsManager:
    # listen up students, in this class we will learn how to write java getters and setters
    def __init__(self, settings_file="app_settings.json", metadata_file="addon_metadata.json"):
        self.settings_file = Path(settings_file)
        self.metadata_file = Path(metadata_file)
        self.settings = self._load_settings()
        self.addon_metadata = self._load_metadata()

    def _load_settings(self):
        default_settings = {
            "last_directory": "",
            "addon_selections": [],
            "matrix_selections": {},
            "prop_filter_checkbox": False
        }

        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")

        return default_settings

    def _load_metadata(self):
        default_metadata = {
            "addon_contents": {},
            "addon_metadata": {}
        }

        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading addon metadata: {e}")

        return default_metadata

    def save_settings(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def save_metadata(self):
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.addon_metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving addon metadata: {e}")

    def get_last_directory(self):
        return self.settings.get("last_directory", "")

    def set_last_directory(self, directory):
        self.settings["last_directory"] = directory
        self.save_settings()

    def get_addon_selections(self):
        return self.settings.get("addon_selections", [])

    def set_addon_selections(self, selections):
        self.settings["addon_selections"] = selections
        self.save_settings()

    def get_matrix_selections(self):
        return self.settings.get("matrix_selections", {})

    def set_matrix_selections(self, selections):
        self.settings["matrix_selections"] = selections
        self.save_settings()

    def get_prop_filter_state(self):
        return self.settings.get("prop_filter_checkbox", False)

    def set_prop_filter_state(self, enabled):
        self.settings["prop_filter_checkbox"] = enabled
        self.save_settings()

    def get_addon_metadata(self):
        return self.addon_metadata.get("addon_metadata", {})

    def set_addon_metadata(self, metadata):
        self.addon_metadata["addon_metadata"] = metadata
        self.save_metadata()

    def get_addon_contents(self):
        metadata = self.get_addon_metadata()
        return {name: data.get('files', []) for name, data in metadata.items()}
