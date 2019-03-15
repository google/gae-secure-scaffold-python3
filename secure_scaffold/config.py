
import os
import importlib

ENVIRONMENT_VARIABLE = "SETTINGS_MODULE"

SETTINGS_MODULE = os.getenv(ENVIRONMENT_VARIABLE)

settings = importlib.import_module('settings.' + SETTINGS_MODULE)
