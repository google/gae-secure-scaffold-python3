import importlib
import os
from unittest import mock

from secure_scaffold import config


def test_import_settings():
    mock_settings_module = mock.MagicMock()
    os.environ['SETTINGS_MODULE'] = 'settings.development'

    with mock.patch.dict('sys.modules', **{
            'settings': mock_settings_module,
            'settings.development': mock_settings_module,
            'development.submodule': mock_settings_module,
    }):
        importlib.reload(config)
        assert config.settings.submodule == mock_settings_module.submodule

    os.environ['SETTINGS_MODULE'] = ''

    importlib.reload(config)
