import json
import re
import os
import signal
import subprocess
import traceback
from string import Template
from typing import List, Tuple, Union

import sublime
from sublime import FindFlags, Region, RegionFlags, View

from ..constants import PyRockConstants
from ..logger import Logger
from ..settings import PyRockSettings
from ..utils import is_test_file
from .output_panel import OutputPanel
from .unittest_path_generator import TestPathGenerator

logger = Logger(__name__)


CLASS_NAME_ONLY_REGEX = r'^(?:class)\s+([a-zA-Z_0-9]\w*)\s*\((?:[^\)]*\):)?'
TEST_METHOD_START_REGEX = r'^ *def\s+(test_[a-zA-Z_0-9]\w*)\s*\((?:[^\)]*\):)?'


class CustomTemplate(Template):
    delimiter = '$'


class AnnotateAndTestRunnerCommand:

    def __init__(self, test: bool = False):
        self._test = test
        self._process = None
        self._command_error_evidence = []
        self._test_process_file_path = os.path.join(
            PyRockConstants.INDEX_CACHE_DIRECTORY, 'test_process.json'
        )
        self._initilize_test_process_pid_storage()

    def _initilize_test_process_pid_storage(self):
        if not os.path.exists(self._test_process_file_path):
            logger.debug("Creating empty process list file")

            with open(self._test_process_file_path, 'w') as f:
                json.dump([], f)

    def _get_test_command(self, test_path: str) -> str:
        unix_env_bash = """
            set -e
            . "{venv_path}"
            cd "{working_directory}"
            {run_test_command} {test_path}
            deactivate
        """
        unix_without_env_bash = """
            set -e
            cd "{working_directory}"
            {run_test_command} {test_path}
        """

        if sublime.platform() in [
            PyRockConstants.PLATFORM_LINUX,
            PyRockConstants.PLATFORM_OSX
        ]:
            if PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value:
                test_command = unix_env_bash.format(
                    venv_path=PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value,
                    working_directory=PyRockSettings().TEST_CONFIG.WORKING_DIR,
                    run_test_command=" ".join(
                        PyRockSettings().TEST_CONFIG.TEST_RUNNER_COMMAND),
                    test_path=test_path,
                )
            else:
                test_command = unix_without_env_bash.format(
                    working_directory=PyRockSettings().TEST_CONFIG.WORKING_DIR,
                    run_test_command=" ".join(
                        PyRockSettings().TEST_CONFIG.TEST_RUNNER_COMMAND),
                    test_path=test_path,
                )
        else:
            working_directory = PyRockSettings().TEST_CONFIG.WORKING_DIR.replace(
                '\\', '\\\\'
            )
            run_test_command = " ".join(
                PyRockSettings().TEST_CONFIG.TEST_RUNNER_COMMAND
            ).replace('\\', '\\\\')

            if PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value:
                venv_path = PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value.replace(
                    '\\', '\\\\'
                )
                test_command = [
                    venv_path, '&&', 'cd', working_directory, '&&', run_test_command, test_path, 'deactivate'
                ]
            else:
                test_command = ['cd', working_directory, '&&', run_test_command, test_path]

        return test_command

    def _kill_existing_running_tests(self):
        existing_process = []

        with open(self._test_process_file_path, 'r') as f:
            existing_process = json.load(f)

        logger.debug(f"existing process {existing_process}")

        for process_pid in existing_process:
            if sublime.platform() in [
                PyRockConstants.PLATFORM_LINUX,
                PyRockConstants.PLATFORM_OSX
            ]:
                try:
                    os.kill(process_pid, signal.SIGKILL)
                except Exception:
                    logger.debug(f"unable to kill {process_pid}")
            else:
                # Windows
                os.system(f"taskkill /F /PID {process_pid} > nul 2>&1")

        with open(self._test_process_file_path, 'w') as f:
            json.dump([], f)

    def _get_test_process_pids(self) -> List[int]:
        test_framework = PyRockSettings().TEST_CONFIG.TEST_FRAMEWORK

        if sublime.platform() in [
            PyRockConstants.PLATFORM_LINUX,
            PyRockConstants.PLATFORM_OSX
        ]:
            if test_framework == PyRockConstants.DJANGO_TEST_FRAMEWORK:
                command = 'pgrep -f "manage.py test"'
            elif test_framework == PyRockConstants.PYTEST_TEST_FRAMEWORK:
                command = 'pgrep -f "pytest"'
        else:
            # Windows
            if test_framework == PyRockConstants.DJANGO_TEST_FRAMEWORK:
                command = """wmic process where "name='python.exe' or name='pythonw.exe'" get commandline,processid | find "manage.py test" """
            elif test_framework == PyRockConstants.PYTEST_TEST_FRAMEWORK:
                command = """wmic process where "name='python.exe' or name='pythonw.exe'" get commandline,processid | find "pytest.exe" """

        output = None
        pid_list = []

        try:
            output = subprocess.check_output(command, shell=True, text=True)
        except subprocess.CalledProcessError:
            logger.debug("No process found")

        if output:
            if sublime.platform() in [
                PyRockConstants.PLATFORM_LINUX,
                PyRockConstants.PLATFORM_OSX
            ]:
                pid_list = list(map(int, output.strip().split("\n")))
            else:
                pid_list = []
                for pid_line in output.split('\n'):
                    if matchd_pid := re.search(r'\d+', pid_line):
                        pid_list.append(
                            int(matchd_pid.group())
                        )
            logger.debug(f"PID list: {pid_list}")

        return pid_list

    def _show_test_output_panel(self, test_command: str) -> OutputPanel:
        output_panel = OutputPanel(
            name=PyRockConstants.PACKAGE_TEST_RUNNER_OUTPUT_PANEL,
            word_wrap=True
        )

        if PyRockSettings().LOG_LEVEL.value == "DEBUG":
            output_panel.writeln("Running Command: ")
            output_panel.writeln(test_command)
        output_panel.flush()
        output_panel.show()
        return output_panel

    def _register_existing_test_process(self):
        # Fetch existing running process id's, if any
        existing_process = []
        with open(self._test_process_file_path, 'r') as f:
            existing_process = json.load(f)

        existing_process = existing_process + self._get_test_process_pids()
        logger.debug(f"All test process running: {existing_process}")

        with open(self._test_process_file_path, 'w') as f:
            json.dump(existing_process, f)

    def _track_test_progress_on_output_panel(self, test_command: str):
        output_panel = self._show_test_output_panel(test_command)

        for index, line in enumerate(self._process.stdout):
            if index == 0:
                # Latest process will start running by now, and
                # we will get all those process ids and register it
                self._register_existing_test_process()

            output = line.decode('utf-8').strip()
            if output == "" or output is None:
                continue

            # output test result
            output_panel.writeln(output)
            output_panel.flush()

    def _run_test_command(
        self, test_command: Union[str, List]
    ) -> Tuple[bool, str]:
        message: str = ""
        script_success: bool = False

        try:
            self._process = subprocess.Popen(
                test_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stderr with stdout
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            message = str(e)
            return script_success, message

        self._track_test_progress_on_output_panel(test_command)
        self._process.wait()

        if self._process.returncode == 0:
            script_success = True
        else:
            message = str(self._process.returncode)

        self._process = None
        logger.debug("Finished process")

        return script_success, message

    def _execute_test(self, href: str):
        regions = self.view.get_regions(self.region_key)

        selected_region_index = int(href)
        logger.debug(f"Selected region index: {selected_region_index}")

        for region in regions:
            logger.debug(
                f"View Region {region.to_tuple()}: {self.view.substr(self.view.full_line(region))}"
            )

        selected_region = regions[selected_region_index]
        logger.debug(
            f"Selected test region: {selected_region.to_tuple()}: {self.view.substr(self.view.full_line(selected_region))}"
        )

        # prepare test path
        test_path = TestPathGenerator.generate(
            selected_region, self.view, PyRockSettings().TEST_CONFIG.TEST_FRAMEWORK
        )
        logger.debug(f"Test path: {test_path}")

        # get test command
        test_command = self._get_test_command(test_path)
        logger.debug(f"Test command: {test_command}")

        self._kill_existing_running_tests()

        self.view.window().destroy_output_panel(PyRockConstants.PACKAGE_TEST_RUNNER_OUTPUT_PANEL)

        if self._test:
            self._run_test_command(test_command)
        else:
            # invoke command to run test
            sublime.set_timeout_async(
                lambda: self._run_test_command(test_command),
                0
            )

    def _generate_run_test_annotated_html(
        self,
        matched_regions: List[Region]
    ) -> List[str]:
        run_test_icon_path = os.path.join(
            PyRockConstants.ABSOLUTE_PACKAGE_ASSETS_DIR, 'debug-start.png'
        ).replace('\\', '/')

        annotations_html_path = os.path.join(
            PyRockConstants.ABSOLUTE_PACKAGE_ASSETS_DIR, 'run_test_annotation.html'
        )

        annotations_html_template = CustomTemplate(
            open(annotations_html_path, 'r').read()
        )

        annotations_html_list: List[str] = []

        for index, region in enumerate(matched_regions):
            logger.debug(f"{index} Test regions {region.to_tuple()} : {self.view.substr(self.view.full_line(region))}")
            annotations_html_list.append(
                annotations_html_template.substitute(
                    run_test_region_index=index,
                    image_file=run_test_icon_path
                )
            )
        return annotations_html_list

    def run(self, view: View):
        self.view = view
        if not PyRockSettings().TEST_CONFIG.ENABLED:
            logger.info("Test config not enabled")
            return

        if self.view.file_name() is None or (self.view.file_name() and not is_test_file(self.view.file_name())):
            logger.info("Not a test file, returning")
            return

        class_matched_regions: List[Region] = self.view.find_all(
            pattern=CLASS_NAME_ONLY_REGEX,
            flags=FindFlags.IGNORECASE
        )
        logger.debug(f"Class Matched regions list: {class_matched_regions}")

        test_method_matched_regions: List[Region] = self.view.find_all(
            pattern=TEST_METHOD_START_REGEX,
            flags=FindFlags.IGNORECASE
        )
        logger.debug(f"Test Matched regions list: {test_method_matched_regions}")

        matched_regions = list(
            sorted(
                class_matched_regions + test_method_matched_regions,
                key=lambda region: region.to_tuple()[0]
            )
        )

        if len(matched_regions) == 0:
            logger.debug(
                "No matching regions found for class or test method, returning")
            return

        # Prepare run test annotated htmls for matched regions
        annotations_html_list = self._generate_run_test_annotated_html(matched_regions)

        test_gutter_icon_path = os.path.join(
            PyRockConstants.RELATIVE_PACKAGE_ASSETS_DIR,
            "beaker.png"
        )
        if sublime.platform() == PyRockConstants.PLATFORM_WINDOWS:
            test_gutter_icon_path = test_gutter_icon_path.replace('\\', '/')

        self.region_key = f"pyrock-gutter-icon-{self.view.id()}"

        logger.debug(f"Region key: {self.region_key}")

        self.view.add_regions(
            key=self.region_key,
            regions=matched_regions,
            scope='icon',
            icon=test_gutter_icon_path,
            flags=RegionFlags.HIDDEN,
            annotations=annotations_html_list,
            annotation_color='green',
            on_navigate=self._execute_test
        )
