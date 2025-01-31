import json
import glob


class setup:
    """
    This class is used to load and update the settings
    from the config.json file with the installed modules.
    """

    def __init__(self):
        pass

    def update_modules(self, root_dir, mod_path="modules/*/.config/config.json"):
        """
        This method updates the modules section of the config.json file.
        It searches for module config files in the ../modules/*/.config/ directory,
        loads them, and updates the modules section in the config.json file.

        @param mod_path: The path pattern to search for module config files.
        @param root_dir: The root directory to search for module config files.
        """

        module_paths = glob.glob(str(root_dir.parent / mod_path))
        new_modules = {}

        for path in module_paths:
            with open(path, "r") as file:
                module_config = json.load(file)
                module_name = module_config["module"]["name"]
                new_modules[module_name] = module_config["module"]

        # Load the existing settings from the config.json file
        config_path = root_dir / ".config/config.json"
        with open(config_path, "r") as file:
            settings = json.load(file)

        settings["modules"] = new_modules

        # Save the updated settings back to the config.json file
        with open(config_path, "w") as file:
            json.dump(settings, file, indent=4)
