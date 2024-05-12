import os
import sublime

class PyRockConstants:
    PACKAGE_NAME = 'PyRock'
    PACKAGE_SETTING_NAME = 'pyrock.sublime-settings'
    INDEX_CACHE_DIRECTORY = os.path.join(sublime.cache_path(), PACKAGE_NAME)
    IMPORT_INDEX_FILE_NAME = 'py_rock_imports.json'
    ABSOLUTE_PACKAGE_ASSETS_DIR = os.path.join(
        sublime.packages_path(), PACKAGE_NAME, 'assets'
    )
    RELATIVE_PACKAGE_ASSETS_DIR = os.path.join(
        'Packages', PACKAGE_NAME, 'assets'
    )
    PACKAGE_TEST_FIXTURES_DIR = os.path.join(
        sublime.packages_path(), PACKAGE_NAME, 'tests', 'fixtures'
    )

    PACKAGE_TEST_RUNNER_OUTPUT_PANEL = "pyrock_test_runner"

    DEFAULT_IMPORT_SCAN_DEPTH = 4
    MIN_IMPORT_SCAN_DEPTH = 1
    MAX_IMPORT_SCAN_DEPTH = 6

    PLATFORM_OSX = "osx"
    PLATFORM_LINUX = "linux"
    PLATFORM_WINDOWS = "windows"

    DJANGO_TEST_FRAMEWORK = "django"
    PYTEST_TEST_FRAMEWORK = "pytest"
