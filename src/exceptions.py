'''
    PyRock exceptions module
'''

class PyRockBaseException(Exception):
    def __init__(self, error_code: str, message: str = ""):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


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


class VersionBlocked(PyRockBaseException):
    def __init__(
        self,
        message: str = "This plugin version is blocked",
        error_code: str = "PR0004",
    ):
        super().__init__(error_code, message)


class SublimePackageBlacklisted(PyRockBaseException):
    def __init__(
        self,
        message: str = "This sublime package is blacklisted",
        error_code: str = "PR0005",
    ):
        super().__init__(error_code, message)


class NonBypassNotification(PyRockBaseException):
    def __init__(
        self,
        message: str = "Unable to bypass the notification",
        error_code: str = "PR0006",
    ):
        super().__init__(error_code, message)


class SublimeVersionNotSupported(PyRockBaseException):
    def __init__(
        self,
        message: str = "Current sublime version is not supported.",
        error_code: str = "PR0007",
    ):
        super().__init__(error_code, message)


class InvalidAPIStatus(PyRockBaseException):
    def __init__(
        self,
        message: str = "API returned with invalid status",
        error_code: str = "PR0008",
    ):
        super().__init__(error_code, message)