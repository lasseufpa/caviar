import glob
import json
import os


class setup:
    """
    This class is used to load and update the settings
    from the config.json file with the installed modules.
    """

    def __init__(self):
        """
        Constructor that initializes the Setup object.
        """
        pass

    def update_modules(
        self, root_dir: str, mod_path: str = "modules/*/.config/config.json"
    ):
        """
        This method updates the modules section of the config.json file.
        It searches for module config files in the ../modules/*/.config/ directory,
        loads them, and updates the modules section in the config.json file.

        @param root_dir: The root directory to search for module config files.
        @param mod_path: The path pattern to search for module config files.
        """

        module_paths = glob.glob(str(root_dir.parent / mod_path))
        new_modules = {}
        for path in module_paths:
            with open(path, "r") as file:
                module_config = json.load(file)
                module_name = module_config["module"]["name"]
                new_modules[module_name] = module_config["module"]
        config_path = root_dir / ".config/config.json"
        with open(config_path, "r") as file:
            settings = json.load(file)

        settings["modules"] = new_modules
        with open(config_path, "w") as file:
            json.dump(settings, file, indent=4)
            file.flush()
            os.fsync(file.fileno())

    def update_orders(self, root_dir, order_path="modules/*/.config/config.json"):
        """
        This method updates the orders section of the config.json file.
        It searches for order config files in the ../orders/*/.config/ directory,
        loads them, and updates the orders section in the config.json file.

        @param root_dir: The root directory to search for order config files.
        @param order_path: The path pattern to search for order config files.
        """
        order_paths = glob.glob(str(root_dir.parent / order_path))
        new_orders = {}

        for path in order_paths:
            with open(path, "r") as file:
                order_config = json.load(file)
                order = int(order_config["module"]["order"])
                name = str(order_config["module"]["name"])
                if order in new_orders.values():
                    raise ValueError(
                        f"Order {order} of initialization is already configured for another module."
                    )
                new_orders[name] = order
        return new_orders

    def update_sync(self, config_path: str):
        """
        This method updates the synchronization and clock of the scheduler.

        __Syncronization__:
        * SYNC: In this case, the events are scheduled based on a sequence queue, where the third module only starts after the first and second modules have finished.
        * ASYNC: In this case, the events are scheduled based on a independent queue, where the third module can start at any time, since the necessary information is available.

        __Clock__:
        * Virtual-time: In this case, the events are scheduled based on a virtual time, where the time is controlled by the simulation.
        * Real-time: In this case, the events are scheduled based on the real time, where the time is controlled by the system clock.

        @param config_path: config.json file path.
        """
        sync_type = ""
        time_type = ""
        with open(config_path, "r") as file:
            config_json = json.load(file)
            sync_type = str(config_json["scheduler"]["type"])
            time_type = str(config_json["scheduler"]["time"])
        return sync_type, time_type
