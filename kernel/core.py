import json
import os
import threading
import time
from pathlib import Path

from .handler import exception_handler
from .logger import LOGGER, logging
from .module import module
from .nats import nats
from .scheduler import scheduler
from .setup import setup

CONFIG_PATH = ".config/config.json"
SETUP = setup()
NATS = nats()
SCHEDULER = scheduler()


class core:

    """
    The core class is the architetor class for all other classes in the kernel.
    It handles all the actions in the simulation.
    """

    @exception_handler
    def __init__(self):
        """
        Constructor that initializes the Core object.
        """
        self.enable = {}
        self.imported_modules = {}
        self.dir = Path(__file__).resolve().parent
        self.__load_json()

    @exception_handler
    def __load_json(self):
        """
        This method load/refreshes the settings from the config.json file.
        """
        LOGGER.debug(f"Refreshing config.json")
        self.settings = json.load(open(self.dir / CONFIG_PATH))

    @exception_handler
    def __update_modules(self):
        """
        This method updates the modules section of the config.json file and saves
        the module names and the order of initialization in the core object.
        """
        LOGGER.debug(f"Updating modules")
        SETUP.update_modules(root_dir=self.dir)
        self.__load_json()
        self.module_names = self.__check_correct_format()
        LOGGER.debug(f"Updating order")
        self.orders = SETUP.update_orders(root_dir=self.dir)
        LOGGER.debug(f"Updating synchronization and clock")

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
    def __update_logger(self):
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
    def __init_nats(self):
        """
        This method sends a message to the NATS server.
        """
        LOGGER.debug(f"Initialize NATS")
        NATS.init()

    @exception_handler
    def __check_correct_format(self):
        """
        This method checks if the config.json file is in the correct format.
        """
        LOGGER.debug(f"Checking the modules")
        self.__check_modules()
        # @TODO: Perhaps add other checkups here?

    @exception_handler
    def __check_modules(self):
        """
        This method checks if the modules are correctly configured.
        It must have a name and an id. If it does not have "enabled" or "dependecy",
        we assume they are True and None, respectively.
        """
        ids = ["communication", "mobility", "AI", "3D"]
        names = []
        for module in self.settings["modules"].items():
            LOGGER.info(f"module information: {module[:]}")
            if "name" not in module[1] or not module[1]["name"].strip():
                raise ValueError("Your module must have a non-empty name")
            elif "id" not in module[1] or module[1]["id"] not in ids:
                raise ValueError(f"ID must be one of {ids}")
            elif "enabled" not in module[1]:
                self.enable[module[1]["name"].strip().lower()] = True
            elif "enabled" in module[1]:
                self.enable[module[1]["name"].strip().lower()] = module[1]["enabled"]
            elif "dependency" in module[1]:
                path = self.dir.parent / "modules/"
                for dependency in module[1]["dependency"].items():
                    if dependency[1].lower() not in [
                        filename.lower() for filename in os.listdir(path)
                    ]:
                        raise ValueError(f"{dependency} is not presented in modules")
                    elif (
                        str(dependency[1]).lower() == module[1]["name"].strip().lower()
                    ):
                        names.append(module[1]["name"].strip().lower())
                        raise ValueError(
                            f"{dependency[1]} can't be dependent on itself"
                        )
        return names

    @exception_handler
    def initialize(self):
        """
        This method initializes the core object:
        - Updates the modules
        - Updates the logger
        - Sets the scheduler
        - Initializes the NATS message exchanger
        - Do initialize all installed modules
        """
        LOGGER.debug(f"Initializing")
        self.__update_modules()
        self.__update_logger()
        self.__set_scheduler()
        self.__thread(func=self.__init_nats)

        """
        Here, we should initialize the modules based on the order of initialization.
        This is important since some modules may depend on others. For example, the
        airsim module must be initialized before the sionna module, for some reason.
        """
        LOGGER.debug(f"Initializing modules")
        for module_name, _ in sorted(self.orders.items(), key=lambda x: x[1]):
            if self.enable[module_name]:
                self.__init_module(module_name)
                # @BUG: The form module is being initialized before the finalization of previous module
                # while not self.imported_modules[module_name].is_init():
                #    self.__wait(timeout=.2)
                #    pass
        LOGGER.debug(f"{self.imported_modules}")

    @exception_handler
    def __set_scheduler(self):
        """
        This method sets the scheduler for the simulation.
        """
        self.sync, self.time = SETUP.update_sync(config_path=self.dir / CONFIG_PATH)
        LOGGER.debug(f"Configured as Time: {self.time}, Sync: {self.sync}")
        SCHEDULER.set_time_type(self.time)
        SCHEDULER.set_sync_type(self.sync)

    @exception_handler
    def __thread(self, func, *args):
        """
        This method runs some object in a separated thread.
        """
        thread = threading.Thread(target=func, args=args, daemon=False)
        LOGGER.debug(f"Running {func} in a thread {thread.name}")
        thread.start()
        thread.join()

        # @TODO: Should we return the thread?
        # return thread

    @exception_handler
    def __init_module(self, module_name=""):
        """
        This method initializes a module.

        @param module_name: The name of the module to be initialized.
        """
        LOGGER.debug(f"Initializing {module_name}")
        module_class = getattr(
            __import__(f"modules.{module_name}", fromlist=[module_name]), module_name
        )
        self.imported_modules[module_name] = module_class()
        if not isinstance(self.imported_modules[module_name], module):
            raise ValueError(f"{module_name} is not a module instance")
        self.__thread(func=self.imported_modules[module_name].initialize)

    @exception_handler
    def __wait(self, timeout=0.2):
        """
        This method waits for a certain amount of time.

        @param timeout: The amount of time to wait.
        """
        time.sleep(timeout)
