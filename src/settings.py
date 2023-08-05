import os
from typing import Any
import sublime
from sublime import Settings
from .constants import PyRockConstants
from .exceptions import InvalidImportDepthScan, InvalidPythonVirtualEnvPath, InvalidLogLevel


class PyRockSettingsFieldBase:
    def __init__(
        self,
        field_name: str,
        settings: Settings,
        field_value: Any = None,
        default_value: Any = None,
    ) -> None:
        self._field_name = field_name
        self._settings = settings
        self._field_value = field_value
        self._default_value = default_value

        self._initialize()

    @property
    def name(self):
        return self._field_name

    @property
    def value(self):
        return self._field_value
    
    @property
    def default_value(self):
        return self._default_value

    def _get_value(self) -> Any:
        return self._settings.get(
            self._field_name
        ) or self._default_value
    
    def _validate(self):
        """
            Default validator does nothing
        """
        pass

    def _initialize(self):
        self._field_value = self._get_value()
        self._validate()

class SettingsImportScanDepthField(PyRockSettingsFieldBase):
    def _validate(self):
        import_scan_depth: int = self._field_value

        if PyRockConstants.MIN_IMPORT_SCAN_DEPTH < import_scan_depth > PyRockConstants.MAX_IMPORT_SCAN_DEPTH:
            raise InvalidImportDepthScan(
                f"Import scan depth should be in range of {PyRockConstants.MIN_IMPORT_SCAN_DEPTH} to {PyRockConstants.MAX_IMPORT_SCAN_DEPTH}"
            )

class SettingsPythonVirtualEnvPathField(PyRockSettingsFieldBase):
    def _validate(self):
        venv_path: str = self._field_value

        if venv_path is not None and not os.path.exists(venv_path):
            raise InvalidPythonVirtualEnvPath

class SettingsPythonInterpreterPathField(PyRockSettingsFieldBase):
    def _validate(self):
        python_path: str = self._field_value

        if python_path is not None and not os.path.exists(python_path):
            raise InvalidPythonVirtualEnvPath

class SettingsPythonLogLevel(PyRockSettingsFieldBase):
    def _validate(self):
        import logging
        self._field_value = self._field_value.upper()

        log_level_map = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }

        if log_level_map.get(self._field_value) is None:
            raise InvalidLogLevel


class PyRockSettings:
    def __init__(self):
        PyRockSettings.parse()

    @classmethod
    def parse(cls):
        settings = sublime.load_settings(PyRockConstants.PACKAGE_SETTING_NAME)

        cls.IMPORT_SCAN_DEPTH = SettingsImportScanDepthField(
            "import_scan_depth",
            settings,
            default_value=PyRockConstants.DEFAULT_IMPORT_SCAN_DEPTH,
        )

        cls.PYTHON_VIRTUAL_ENV_PATH = SettingsPythonVirtualEnvPathField(
            "python_venv_path",
            settings,
        )

        cls.PYTHON_INTERPRETER_PATH = SettingsPythonInterpreterPathField(
            "python_interpreter_path",
            settings,
        )

        cls.LOG_LEVEL = SettingsPythonLogLevel("log_level", settings, default_value="INFO")
