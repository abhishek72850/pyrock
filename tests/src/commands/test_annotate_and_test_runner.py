import os
from unittest.mock import patch

import sublime
from PyRock.src.constants import PyRockConstants

from tests.base import PyRockTestBase
from PyRock.src.commands.annotate_and_test_runner import AnnotateAndTestRunnerCommand


class TestAnnotateAndTestRunnerCommand(PyRockTestBase):
    def setUp(self):
        self.maxDiff = None
        self.test_runner_cmd = AnnotateAndTestRunnerCommand(test=True)

    def tearDown(self):
        pass

    def _open_test_fixture_file(self):
        test_file_view = sublime.active_window().open_file(
            fname=os.path.join(
                PyRockConstants.PACKAGE_TEST_FIXTURES_DIR, 'test_fixture.py'
            )
        )

        # wait for view to open
        # while test_file_view.is_loading():
        #     pass

        return test_file_view


    @patch("PyRock.src.settings.SettingsTestConfigField._get_value")
    def test_run(self, mocked_get_test_config):
        mocked_get_test_config.return_value = {
            "enabled": True,
            "test_framework": "pytest",
            "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
            "test_runner_command": ["pytest"]
        }
        test_file_view = self._open_test_fixture_file()

        region_key = f"pyrock-gutter-icon-{test_file_view.id()}"

        annotated_regions = test_file_view.get_regions(region_key)

        self.assertEqual(len(annotated_regions), 3)

    @patch("os.path.exists")
    @patch("PyRock.src.commands.annotate_and_test_runner.AnnotateAndTestRunnerCommand._run_test_command")
    @patch("sublime.load_settings")
    def test_click_on_annotated_html(
        self,
        mocked_load_settings,
        mocked_run_test_command,
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
        mocked_os_path_exists.return_value = True

        test_file_view = self._open_test_fixture_file()

        self.test_runner_cmd.run(test_file_view)
        self.test_runner_cmd._execute_test("0")

        test_command = """
            set -e
            . "/Users/abhishek/venv/bin/activate"
            cd "/Users/abhishek/"
            pytest tests/fixtures/test_fixture.py::MyTestCase
            deactivate
        """

        mocked_run_test_command.assert_called_once_with(
            test_command
        )

    @patch("PyRock.src.commands.output_panel.OutputPanel.show")
    @patch("PyRock.src.settings.SettingsTestConfigField._get_value")
    def test_run_test_command(
        self,
        mocked_get_test_config,
        mocked_panel_show,
    ):
        mocked_get_test_config.return_value = {
            "enabled": True,
            "test_framework": "pytest",
            "working_directory": PyRockConstants.PACKAGE_TEST_FIXTURES_DIR,
            "test_runner_command": ["pytest"]
        }

        test_file_view = self._open_test_fixture_file()

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
        self.assertTrue(test_command in output_text)

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
