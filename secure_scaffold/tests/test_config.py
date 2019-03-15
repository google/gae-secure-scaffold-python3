
import os
from unittest import mock


def test_import_settings():
    mock_settings_module = mock.MagicMock()
    os.environ['SETTINGS_MODULE'] = 'settings.development'

    with mock.patch.dict('sys.modules', **{
            'settings': mock_settings_module,
            'settings.development': mock_settings_module,
            'development.submodule': mock_settings_module,
    }):
        from secure_scaffold.config import settings
        assert settings.submodule == mock_settings_module.submodule
