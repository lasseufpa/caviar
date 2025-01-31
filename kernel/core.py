import os
import json
from pathlib import Path
from .logger import logging, LOGGER
from .setup import setup
from .handler import exception_handler
from .nats import nats

CONFIG_PATH = ".config/config.json"
SETUP = setup()
NATS = nats()

"""
The core class is the architetor class for all other classes in the kernel.
It handles all the actions in the simulation.
"""


class core:
    @exception_handler
    def __init__(self):
        """
        Constructor that initializes the Core object.
        """
        self.dir = Path(__file__).resolve().parent
        json_path = self.dir / CONFIG_PATH
        self.settings = json.load(open(json_path))

    @exception_handler
    def update_modules(self):
        """
        This method updates the modules section of the config.json file.
        """
        LOGGER.debug(f"Updating modules")
        self.check_correct_format()
        SETUP.update_modules(root_dir=self.dir)

    @exception_handler
    def get_config_json(self):
        """
        This method returns the settings from the config.json file.
        """
        LOGGER.debug(f"Getting config.json")
        return self.settings

    @exception_handler
    def get_modules(self):
        """
        This method returns all the modules configuration from the config.json file.
        """
        LOGGER.debug(f"Getting modules")
        return self.settings["modules"]

    @exception_handler
    def update_logger(self):
        """
        This method sets the logger for the core object.
        """
        log_conf = self.settings["config"]["logger"]
        if log_conf["log"]:
            log_level = getattr(logging, log_conf["log_level"].upper())
            # @TODO: Fix update to debug level (for some reason it is not working)
            LOGGER.setLevel(log_level)
            LOGGER.info(f"Logger set to {log_conf['log_level']}")

    @exception_handler
    def init_nats(self, url, subject, message):
        """
        This method sends a message to the NATS server.
        """
        LOGGER.debug(f"Initialize NATS")
        self.settings["config"]["nats"]
        NATS.init(url, subject, message)

    @exception_handler
    def check_correct_format(self):
        """
        This method checks if the config.json file is in the correct format.
        """
        LOGGER.debug(f"Checking the modules")
        self.check_modules()

    @exception_handler
    def check_modules(self):
        """
        This method checks if the modules are correctly configured.
        It must have a name and an id. If it does not have "enabled" or "dependecy",
        we assume they are True and None, respectively.
        """
        ids = ["communication", "mobility", "AI", "3D"]
        for module in self.settings["modules"].items():
            LOGGER.debug(f'module information: {module[:]}')
            if "name" not in module[1] or not module[1]["name"].strip():
                raise ValueError("Your module must have a non-empty name")
            elif "id" not in module[1] or module[1]["id"] not in ids:
                raise ValueError(f"ID must be one of {ids}")
            elif "enabled" not in module:
                module["enabled"] = True
            elif "dependency" in module:
                path = self.dir.parent / "modules/*"
                for dependency in module["dependency"]:
                    if dependency not in os.listdir(path) or dependency is module[1]["name"].strip():
                        raise ValueError(f"{dependency} is not presented in modules")
