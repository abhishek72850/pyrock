import os
from typing import Any
import sublime
from sublime import Settings
from .constants import PyRockConstants
from .exceptions import (
    InvalidImportDepthScan,
    InvalidPythonVirtualEnvPath,
    InvalidLogLevel,
    InvalidTestConfig
)


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

class SettingsTestConfigField(PyRockSettingsFieldBase):
    def _get_value(self) -> Any:
        return self._settings.get(
            self._field_name
        ) or self._default_value

    def _validate(self):
        if not isinstance(self._field_value, dict):
            raise InvalidTestConfig

        self.ENABLED = self._field_value.get('enabled', False)
        self.TEST_FRAMEWORK = None
        self.WORKING_DIR = None
        self.TEST_RUNNER_COMMAND = None

        if self.ENABLED:
            self.TEST_FRAMEWORK = self._field_value.get("test_framework")
            if self.TEST_FRAMEWORK not in [PyRockConstants.DJANGO_TEST_FRAMEWORK, PyRockConstants.PYTEST_TEST_FRAMEWORK]:
                raise InvalidTestConfig(f"Invalid test framework {self.TEST_FRAMEWORK}")

            self.WORKING_DIR = self._field_value.get("working_directory")
            if self.WORKING_DIR is None or (self.WORKING_DIR and not os.path.exists(self.WORKING_DIR)):
                raise InvalidTestConfig(
                    f"Invalid or not existing working directory {self.WORKING_DIR}"
                )

            self.TEST_RUNNER_COMMAND = self._field_value.get("test_runner_command")
            if not isinstance(self.TEST_RUNNER_COMMAND, list):
                raise InvalidTestConfig("Invalid runner command format")

class PyRockSettings:
    def __init__(self):
        self.parse()

    def parse(self):
        settings = sublime.load_settings(PyRockConstants.PACKAGE_SETTING_NAME)

        self.IMPORT_SCAN_DEPTH = SettingsImportScanDepthField(
            "import_scan_depth",
            settings,
            default_value=PyRockConstants.DEFAULT_IMPORT_SCAN_DEPTH,
        )

        self.PYTHON_VIRTUAL_ENV_PATH = SettingsPythonVirtualEnvPathField(
            "python_venv_path",
            settings,
        )

        self.PYTHON_INTERPRETER_PATH = SettingsPythonInterpreterPathField(
            "python_interpreter_path",
            settings,
        )

        self.LOG_LEVEL = SettingsPythonLogLevel(
            "log_level", settings, default_value="INFO"
        )

        self.TEST_CONFIG = SettingsTestConfigField(
            "test_config", settings, default_value={}
        )
