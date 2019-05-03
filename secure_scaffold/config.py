import os
import importlib

from secure_scaffold import settings as defaults

SETTINGS_MODULE_VAR = "SETTINGS_MODULE"

SETTINGS_MODULE = os.getenv(SETTINGS_MODULE_VAR)

settings = importlib.import_module(SETTINGS_MODULE)


def get_setting(name):
    value = getattr(settings, name, None)

    if value is not None:
        return value
    try:
        return getattr(defaults, name)
    except AttributeError:
        raise AttributeError(f'Setting "{name}"" does not exist, please define it.')

