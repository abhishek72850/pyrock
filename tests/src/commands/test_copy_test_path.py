import sublime
from unittest.mock import patch

from PyRock.src.constants import PyRockConstants

from tests.base import PyRockTestBase


class TestCopyTestPathCommand(PyRockTestBase):
    def setUp(self):
        self.maxDiff = None
        self.test_file_view = None

    def tearDown(self):
        pass

    def test_copy_django_class_test_path(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            # Wait 4 second to make sure test fixture file has opened
            yield 4000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("sublime.load_settings") as mocked_load_settings, \
        patch("os.path.exists") as mocked_os_path_exists, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations:

            mocked_load_settings.return_value = {
              "python_venv_path": "/Users/abhishek/venv/bin/activate",
              "log_level": "debug",
              "test_config": {
                  "enabled": True,
                  "test_framework": "pytest",
                  "working_directory": "/Users/abhishek/",
                  "test_runner_command": ["pytest"],
              }
            }
            mocked_os_path_exists.return_value = True

            class TestSymbol:
                path = test_file_view.file_name()
                display_name = "tests/fixtures/test_fixture.py"
            mocked_symbol_locations.return_value = [TestSymbol()]

            test_file_view.sel().clear()
            test_file_view.sel().add(sublime.Region(53, 63))

            selected_text = test_file_view.substr(test_file_view.sel()[0])
            self.assertEqual(selected_text, "MyTestCase")

            test_file_view.run_command(
                "py_rock", args={"action": "copy_test_path", "test": True})

            expected_import_statement = sublime.get_clipboard()
            self.assertEqual(
                expected_import_statement, "tests/fixtures/test_fixture.py::MyTestCase"
            )

    def test_copy_django_class_method_test_path(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            # Wait 4 second to make sure test fixture file has opened
            yield 4000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("PyRock.src.settings.SettingsTestConfigField._get_value") as mocked_get_test_config, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations:

            mocked_get_test_config.return_value = {
                "enabled": True,
                "test_framework": "pytest",
                "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
                "test_runner_command": ["pytest"]
            }

            class TestSymbol:
                path = test_file_view.file_name()
                display_name = "tests/fixtures/test_fixture.py"
            mocked_symbol_locations.return_value = [TestSymbol()]

            test_file_view.sel().clear()
            test_file_view.sel().add(sublime.Region(83, 105))

            selected_text = test_file_view.substr(test_file_view.sel()[0])
            self.assertEqual(selected_text, "test_long_running_task")

            test_file_view.run_command(
                "py_rock", args={"action": "copy_test_path", "test": True})

            expected_import_statement = sublime.get_clipboard()
            self.assertEqual(
                expected_import_statement,
                "tests/fixtures/test_fixture.py::MyTestCase::test_long_running_task"
            )

    def test_copy_django_individual_method_test_path(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            # Wait 4 second to make sure test fixture file has opened
            yield 4000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("PyRock.src.settings.SettingsTestConfigField._get_value") as mocked_get_test_config, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations:

            mocked_get_test_config.return_value = {
                "enabled": True,
                "test_framework": "pytest",
                "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
                "test_runner_command": ["pytest"]
            }

            class TestSymbol:
                path = test_file_view.file_name()
                display_name = "tests/fixtures/test_fixture.py"
            mocked_symbol_locations.return_value = [TestSymbol()]

            test_file_view.sel().clear()
            test_file_view.sel().add(
                sublime.Region(
                    272 if sublime.platform() == PyRockConstants.PLATFORM_OSX else 271,
                    286 if sublime.platform() == PyRockConstants.PLATFORM_OSX else 285
                )
            )

            selected_text = test_file_view.substr(test_file_view.sel()[0])
            self.assertEqual(selected_text, "test_iam_alone")

            test_file_view.run_command(
                "py_rock", args={"action": "copy_test_path", "test": True})

            expected_import_statement = sublime.get_clipboard()
            self.assertEqual(
                expected_import_statement, "tests/fixtures/test_fixture.py::test_iam_alone"
            )

    def test_copy_pytest_class_test_path(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            # Wait 4 second to make sure test fixture file has opened
            yield 4000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("PyRock.src.settings.SettingsTestConfigField._get_value") as mocked_get_test_config, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations:
            mocked_get_test_config.return_value = {
                "enabled": True,
                "test_framework": "pytest",
                "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
                "test_runner_command": ["pytest"]
            }

            class TestSymbol:
                path = test_file_view.file_name()
                display_name = "tests/fixtures/test_fixture.py"
            mocked_symbol_locations.return_value = [TestSymbol()]

            test_file_view.sel().clear()
            test_file_view.sel().add(sublime.Region(53, 63))

            selected_text = test_file_view.substr(test_file_view.sel()[0])
            self.assertEqual(selected_text, "MyTestCase")

            test_file_view.run_command(
                "py_rock", args={"action": "copy_test_path", "test": True})

            expected_import_statement = sublime.get_clipboard()
            self.assertEqual(
                expected_import_statement, "tests/fixtures/test_fixture.py::MyTestCase"
            )

    def test_copy_pytest_class_method_test_path(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            # Wait 4 second to make sure test fixture file has opened
            yield 4000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("PyRock.src.settings.SettingsTestConfigField._get_value") as mocked_get_test_config, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations:
            mocked_get_test_config.return_value = {
                "enabled": True,
                "test_framework": "pytest",
                "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
                "test_runner_command": ["pytest"]
            }

            class TestSymbol:
                path = test_file_view.file_name()
                display_name = "tests/fixtures/test_fixture.py"
            mocked_symbol_locations.return_value = [TestSymbol()]

            test_file_view.sel().clear()
            test_file_view.sel().add(sublime.Region(83, 105))

            selected_text = test_file_view.substr(test_file_view.sel()[0])
            self.assertEqual(selected_text, "test_long_running_task")

            test_file_view.run_command(
                "py_rock", args={"action": "copy_test_path", "test": True})

            expected_import_statement = sublime.get_clipboard()
            self.assertEqual(
                expected_import_statement,
                "tests/fixtures/test_fixture.py::MyTestCase::test_long_running_task"
            )

    def test_copy_pytest_individual_method_test_path(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            # Wait 4 second to make sure test fixture file has opened
            yield 4000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("PyRock.src.settings.SettingsTestConfigField._get_value") as mocked_get_test_config, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations:
            mocked_get_test_config.return_value = {
                "enabled": True,
                "test_framework": "pytest",
                "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
                "test_runner_command": ["pytest"]
            }

            class TestSymbol:
                path = test_file_view.file_name()
                display_name = "tests/fixtures/test_fixture.py"
            mocked_symbol_locations.return_value = [TestSymbol()]

            test_file_view.sel().clear()
            test_file_view.sel().add(
                sublime.Region(
                    272 if sublime.platform() == PyRockConstants.PLATFORM_OSX else 271,
                    286 if sublime.platform() == PyRockConstants.PLATFORM_OSX else 285
                )
            )

            selected_text = test_file_view.substr(test_file_view.sel()[0])
            self.assertEqual(selected_text, "test_iam_alone")

            test_file_view.run_command(
                "py_rock", args={"action": "copy_test_path", "test": True})

            expected_import_statement = sublime.get_clipboard()
            self.assertEqual(
                expected_import_statement,
                "tests/fixtures/test_fixture.py::test_iam_alone"
            )
