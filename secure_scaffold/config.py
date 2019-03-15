
import os
import importlib

SETTINGS_MODULE_VAR = "SETTINGS_MODULE"

SETTINGS_MODULE = os.getenv(SETTINGS_MODULE_VAR)

settings = importlib.import_module(SETTINGS_MODULE)
