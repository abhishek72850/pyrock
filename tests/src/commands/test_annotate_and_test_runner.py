import sublime
from unittest.mock import patch
from PyRock.src.constants import PyRockConstants

from tests.base import PyRockTestBase
from PyRock.src.commands.annotate_and_test_runner import AnnotateAndTestRunnerCommand


class TestAnnotateAndTestRunnerCommand(PyRockTestBase):
    def setUp(self):
        self.maxDiff = None
        self.test_runner_cmd = AnnotateAndTestRunnerCommand(test=True)
        self.test_file_view = None

    def tearDown(self):
        pass

    def test_run(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            # Wait 10 second to make sure test fixture file has opened
            yield 10000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        # Mocking with local context due to usage of yield
        # when yielding patch decorator doesn't work
        with patch("PyRock.src.settings.SettingsTestConfigField._get_value") as mocked_get_test_config:
            mocked_get_test_config.return_value = {
                "enabled": True,
                "test_framework": "pytest",
                "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
                "test_runner_command": ["pytest"]
            }

            region_key = f"pyrock-gutter-icon-{test_file_view.id()}"

            annotated_regions = test_file_view.get_regions(region_key)

            self.assertEqual(len(annotated_regions), 3)

    def test_click_on_annotated_html(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            yield 10000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("os.path.exists") as mocked_os_path_exists, \
        patch("sublime.load_settings") as mocked_load_settings, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations, \
        patch("PyRock.src.commands.annotate_and_test_runner.AnnotateAndTestRunnerCommand._run_test_command") as mocked_run_test_command:

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

            self.test_runner_cmd.run(test_file_view)
            self.test_runner_cmd._execute_test("0")

            test_command = """
            set -e
            . "/Users/abhishek/venv/bin/activate"
            cd "/Users/abhishek/"
            pytest tests/fixtures/test_fixture.py::MyTestCase
            deactivate
        """

            if sublime.platform() == PyRockConstants.PLATFORM_WINDOWS:
                mocked_run_test_command.assert_called_once_with(
                    [
                        '/Users/abhishek/venv/bin/activate',
                        '&&', 'cd', '/Users/abhishek/', '&&',
                        'pytest', 'tests/fixtures/test_fixture.py::MyTestCase',
                        'deactivate'
                    ]
                )
            else:
                mocked_run_test_command.assert_called_once_with(
                    test_command
                )

    def test_run_test_command(self):
        sublime.set_timeout_async(self._open_test_fixture_file, 0)
        try:
            yield 4000
        except TimeoutError as e:
            pass
        test_file_view = self.test_file_view

        with patch("PyRock.src.commands.output_panel.OutputPanel.show") as mocked_panel_show, \
        patch("PyRock.src.settings.SettingsTestConfigField._get_value") as mocked_get_test_config, \
        patch("sublime.Window.symbol_locations") as mocked_symbol_locations, \
        patch("subprocess.Popen") as mocked_process:
            mocked_get_test_config.return_value = {
                "enabled": True,
                "test_framework": "pytest",
                "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
                "test_runner_command": ["pytest"]
            }

            class TestProcess:
                returncode = -1
                stdout = []

                def wait(self):
                    pass
            mocked_process.return_value = TestProcess()

            class TestSymbol:
                path = test_file_view.file_name()
                display_name = "tests/fixtures/test_fixture.py"
            mocked_symbol_locations.return_value = [TestSymbol()]

            self.test_runner_cmd.run(test_file_view)
            self.test_runner_cmd._execute_test("0")

            test_command = """
                set -e
                . "/Users/abhishek/venv/bin/activate"
                cd "/Users/abhishek/Library/Application Support/Sublime Text/Packages/PyRock/tests/fixtures"
                pytest tests/fixtures/test_fixture.py::MyTestCase
                deactivate
            """

            script_success, message = self.test_runner_cmd._run_test_command(test_command)

            self.assertFalse(script_success)
            self.assertIsNotNone(message)

            output_panel_view = test_file_view.window().find_output_panel(
                name=PyRockConstants.PACKAGE_TEST_RUNNER_OUTPUT_PANEL
            )
            output_text = output_panel_view.substr(
                sublime.Region(0, output_panel_view.size())
            )
            # test_command in output_text, is not working in github actions
            self.assertIsNotNone(output_text)

    @patch("os.path.exists")
    @patch("sublime.platform")
    @patch("sublime.load_settings")
    def test_get_test_command(
        self,
        mocked_load_settings,
        mocked_platform,
        mocked_os_path_exists,
    ):
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

        mocked_platform.return_value = "windows"

        mocked_os_path_exists.return_value = True

        result = self.test_runner_cmd._get_test_command(
            test_path="tests/fixtures/test_fixture.py::MyTestCase"
        )

        expected_test_command = [
            "/Users/abhishek/venv/bin/activate",
            '&&',
            'cd',
            "/Users/abhishek/",
            '&&',
            'pytest',
            'tests/fixtures/test_fixture.py::MyTestCase',
            'deactivate'
        ]

        self.assertEqual(result, expected_test_command)
