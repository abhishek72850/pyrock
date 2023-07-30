'''
    PyRock exceptions module
'''
from typing import Type
from src.logger import get_logger


logger = get_logger(__name__)


class PyRockBaseException(Exception):
    def __init__(self, error_code: str, message: str = ""):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
        logger.error(f"{message}:{error_code}")


class InvalidImportDepthScan(PyRockBaseException):
    def __init__(
        self,
        message: str = "Provided import scan depth value is not in valid range",
        error_code: str = "PR0001",
    ):
        super().__init__(error_code, message)


class InvalidPythonVirtualEnvPath(PyRockBaseException):
    def __init__(
        self,
        message: str = "Provided python virtual env path is invalid or doesn't exist",
        error_code: str = "PR0002",
    ):
        super().__init__(error_code, message)


class InvalidLogLevel(PyRockBaseException):
    def __init__(
        self,
        message: str = "Provided log level is invalid",
        error_code: str = "PR0003",
    ):
        super().__init__(error_code, message)
