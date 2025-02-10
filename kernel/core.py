import json
import os
import threading
from pathlib import Path

from .asynchronous import Async
from .handler import handler
from .logger import LOGGER, logging
from .module import module
from .nats import NATS
from .process import PROCESS
from .setup import setup
#from .synchronous import Sync

CONFIG_PATH = ".config/config.json"
SETUP = setup()


class core:

    """
    The core class is the architetor class for all other classes in the kernel.
    It handles all the actions in the simulation.
    """

    __scheduler = None
    __orders = None
    __enable = None
    __dependencies = None
    __imported_modules = None
    __dir = None
    __settings = None

    @handler.exception_handler
    def __init__(self):
        """
        Constructor that initializes the Core object.
        """
        self.__orders = {}
        self.__enable = {}
        self.__dependencies = {}
        self.__imported_modules = {}
        self.__dir = Path(__file__).resolve().parent
        self.__load_json()
        handler.register_signals()

    @handler.exception_handler
    def __load_json(self):
        """
        This method load/refreshes the settings from the config.json file.
        """
        LOGGER.debug(f"Refreshing config.json")
        self.__settings = json.load(open(self.__dir / CONFIG_PATH))

    @handler.exception_handler
    def __update_modules(self):
        """
        This method updates the modules section of the config.json file and saves
        the module names and the order of initialization in the core object.
        """
        LOGGER.debug(f"Updating modules")
        SETUP.update_modules(root_dir=self.__dir)
        self.__load_json()
        self.module_names = self.__check_correct_format()

    @handler.exception_handler
    def get_config_json(self):
        """
        This method returns the settings from the config.json file.
        """
        LOGGER.debug(f"Getting config.json")
        return self.__settings

    @handler.exception_handler
    def get_modules(self):
        """
        This method returns all the modules configuration from the config.json file.
        """
        LOGGER.debug(f"Getting modules")
        return self.__settings["modules"]

    @handler.exception_handler
    def __update_logger(self):
        """
        This method sets the logger for the core object.
        """
        log_conf = self.__settings["config"]["logger"]
        if log_conf["log"]:
            log_level = getattr(logging, log_conf["log_level"].upper())
            # @TODO: Fix update to debug level (for some reason it is not working)
            LOGGER.setLevel(log_level)
            LOGGER.info(f"Logger set to {log_conf['log_level']}")

    @handler.exception_handler
    def __init_nats(self):
        """
        This method sends a message to the NATS server.
        """
        LOGGER.debug(f"Initialize NATS")
        NATS.init()

    @handler.exception_handler
    def __check_correct_format(self):
        """
        This method checks if the config.json file is in the correct format.
        """
        LOGGER.debug(f"Checking the modules")
        self.__check_modules()
        self.__check_inter_module_circular_dependencies()
        # @TODO: Perhaps add other checkups here?

    @handler.exception_handler
    def __check_modules(self):
        """
        This method checks if the modules are correctly configured.
        It must have a name and an id. If it does not have "enabled" or "dependency",
        we assume they are True and None, respectively.
        """
        ids = {"communication", "mobility", "AI", "3D"}
        path = self.__dir.parent / "modules/"
        available_modules = {filename.lower() for filename in os.listdir(path)}

        for _, module_info in self.__settings["modules"].items():
            enabled = module_info.get("enabled", True)
            if not isinstance(enabled, bool):
                raise ValueError("The 'enabled' field must be a boolean")

            self.__enable[module_info["name"].strip().lower()] = enabled

            if enabled:
                LOGGER.info(f"Module information: {module_info}")

                name = module_info.get("name", "").strip()
                if not name:
                    raise ValueError("Your module must have a non-empty name")

                module_id = module_info.get("id")
                if module_id not in ids:
                    raise ValueError(f"ID must be one of {ids}")

                dependencies = module_info.get("dependency", {})
                deps = []
                for _, dep_list in dependencies.items():
                    LOGGER.debug(f"Checking dependencies {dep_list}")
                    for dependency in dep_list:
                        dependency_lower = dependency.lower()
                        if dependency_lower not in available_modules:
                            raise ValueError(f"{dependency} is not present in modules")
                        if dependency_lower == name.lower():
                            raise ValueError(
                                f"{dependency} can't be dependent on itself"
                            )
                        if (
                            not self.__settings["modules"]
                            .get(dependency_lower, {})
                            .get("enabled", True)
                        ):
                            raise ValueError(
                                f"{dependency} is not enabled, can't be dependent on a not enabled module"
                            )
                        deps.append(dependency_lower)
                self.__dependencies[name] = deps

                order = module_info.get("order")
                if order is None:
                    raise ValueError("Your module must have an order of initialization")

                """
                @TODO: Although it works great to call it here, it shouldn't be here
                """
                self.__update_order(name, order)

    @handler.exception_handler
    def initialize(self):
        """
        This method initializes the core object:
        - Updates the modules
        - Updates the logger
        - Sets the scheduler
        - Initializes the NATS message exchanger
        - Do initialize all installed modules
        """
        LOGGER.debug(f"Starting...")
        self.__update_logger()
        self.__update_modules()
        LOGGER.debug(f"Updating synchronization and clock")
        self.__set_scheduler()
        self.__thread(func=self.__init_nats)

        """
        Here, we should initialize the modules based on the order of initialization.
        This is important since some modules may depend on others. For example, the
        airsim module must be initialized before the sionna module, for some reason.
        """
        LOGGER.debug(f"Initializing modules")
        for module_name, _ in sorted(self.__orders.items(), key=lambda x: x[1]):
            if self.__enable[module_name]:
                self.__init_module(module_name)
        LOGGER.debug(f"Modules initialized: {self.__imported_modules}")

        self.__execute_steps_in_loop()

    @handler.exception_handler
    def __set_scheduler(self):
        """
        This method sets the scheduler for the simulation.
        """
        s_type, t_type = SETUP.update_sync(config_path=self.__dir / CONFIG_PATH)
        LOGGER.debug(f"Configured as Time: {t_type}, Sync: {s_type}")
        if s_type.lower() == "async":
            self.__scheduler = Async()
        elif s_type.lower() == "sync":
            raise ValueError("Sync scheduler not implemented yet")
            self.__scheduler = Sync()
        else:
            raise ValueError(f"Scheduler type {s_type} not recognized")

    @handler.exception_handler
    def __thread(self, func, *args, name=""):
        """
        This method runs some object in a separated thread.
        """

        thread = threading.Thread(target=func, args=args, daemon=False, name=name)
        LOGGER.debug(f"Running in a thread {thread.name.upper()}")
        thread.start()
        thread.join()

    @handler.exception_handler
    def __init_module(self, module_name=""):
        """
        This method initializes a module.

        @param module_name: The name of the module to be initialized.
        """
        LOGGER.debug(f"Initializing {module_name.upper()}")
        module_class = getattr(
            __import__(f"modules.{module_name}", fromlist=[module_name]), module_name
        )
        self.__imported_modules[module_name] = module_class()
        if not isinstance(self.__imported_modules[module_name], module):
            raise ValueError(f"{module_name} is not a module instance")
        """
        The module initialization must start a new thread and subprocess. In the same thread, the 
        """
        self.__thread(
            func=PROCESS.create_process(
                self.__imported_modules[module_name].initialize,
                wait=True,
                process_name=module_name.upper(),
            ),
            name=module_name,
        )

    @handler.exception_handler
    def __update_order(self, name, order):
        """
        This method updates the order of initialization of the modules.

        @param name: The name of the module.
        @param order: The order of initialization.
        """
        self.__orders[name] = order

    @handler.exception_handler
    def __execute_steps_in_loop(self):
        """
        This method executes the steps of the modules in a loop.
        """
        LOGGER.debug(f"Executing steps in loop")
        LOGGER.debug(f"Updating modules in scheduler")
        #self.__scheduler.update_modules(self.__imported_modules)
        self.__scheduler.update_modules(self.__dependencies)
        LOGGER.debug(f"Starting loop execution...")
        self.__scheduler.execute_steps_in_loop()

    @handler.exception_handler
    def __check_inter_module_circular_dependencies(self):
        """
        This method checks if there are circular dependencies between modules.
        E.g., Sionna depends on Airsim, and Airsim depends on Sionna.
        """
        LOGGER.debug(f"Checking circular dependencies")
        for module_name, deps in self.__dependencies.items():
            for dep in deps:
                if dep in self.__dependencies:
                    if module_name in self.__dependencies[dep]:
                        raise ValueError(
                            f"Circular dependency between {module_name} and {dep}"
                        )

        pass
