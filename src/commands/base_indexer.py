import os
import re
from typing import List, Tuple
import sublime
from sublime import Window
from ..settings import PyRockSettings
from ..constants import PyRockConstants
from ..logger import Logger
from pathlib import Path
import subprocess
import json
import time


logger = Logger(__name__)
path = Path(__file__)


class BaseIndexer:
    def _generate_serialized_settings(self):
        settings = {
            "IMPORT_SCAN_DEPTH": PyRockSettings().IMPORT_SCAN_DEPTH.value,
            "INDEX_CACHE_DIRECTORY": PyRockConstants.INDEX_CACHE_DIRECTORY,
            "IMPORT_INDEX_FILE_NAME": PyRockConstants.IMPORT_INDEX_FILE_NAME
        }

        settings_path = os.path.join(path.parent.parent, 'serialized_settings.json')

        with open(settings_path, "w") as f:
            json.dump(settings, f)

    def _get_indexer_script_path(self):
        return os.path.join(path.parent.parent, 'scripts', 'indexer.py')
    
    def _is_indexing_needed(self) -> bool:
        file_path = os.path.join(PyRockConstants.INDEX_CACHE_DIRECTORY, PyRockConstants.IMPORT_INDEX_FILE_NAME)
        return os.path.exists(file_path)

    def _track_indexer_progress(self, window: Window, process: subprocess.Popen) -> bool:
        start_time = time.perf_counter()
        script_success: bool = False
        log_errors: bool = False
        # Progress tracker
        for line in iter(process.stdout.readline, ""):
            output = line.decode('utf-8').strip()
            # Kill process after 20 sec
            if (time.perf_counter() - start_time) > 20:
                error_reason = f"Indexing stopped due to timeout at {output}%"
                logger.warning(error_reason)
                self._command_error_evidence.append(error_reason)
                process.terminate()
                script_success = False
                break
            
            if log_errors:
                # Collect error generated from script
                self._command_error_evidence.append(output)
            elif re.match(r"^([1-9]|[1-9][0-9]|100)$", output):
                logger.debug(f"Indexing imports...{output}%")
                window.status_message(f"Indexing imports...{output}%")
                if 95 <= int(output) <= 100:
                    script_success = True
            elif "FAILED_INDEXING" in output:
                script_success = False
                log_errors = True
            
            if output == "" or output is None:
                break
        return script_success

    def _collect_cmd_error_output(self, process: subprocess.Popen):
        # Collect error generated from command
        for line in iter(process.stderr.readline, ""):
            output = line.decode('utf-8').strip()
            if len(output) == 0 or output == "" or output is None:
                break
            logger.debug(output)
            self._command_error_evidence.append(output)
    
    def _run_import_indexer(self, window: Window, indexer_command: str) -> Tuple[bool, str]:
        process = subprocess.Popen(
            indexer_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        message: str = ""
        script_success: bool = self._track_indexer_progress(window, process)

        if not script_success:
            if len(self._command_error_evidence) > 0:
                logger.error("\n".join(self._command_error_evidence))
            else:
                self._collect_cmd_error_output(process)
                message = "\n".join(self._command_error_evidence)
                logger.error(message)
        
        return script_success, message

    def _get_import_command(self) -> str:
        unix_env_bash = """
            set -e
            source "{venv_path}"
            python -u "{indexer_script_path}"
            deactivate
        """
        unix_without_env_bash = """
            set -e
            python -u "{indexer_script_path}"
        """

        windows_env_bash = """
            "{venv_path}"
            python -u "{indexer_script_path}"
            deactivate
        """
        windows_without_env_bash = """
            python -u "{indexer_script_path}"
            deactivate
        """

        if sublime.platform() in [
            PyRockConstants.PLATFORM_LINUX,
            PyRockConstants.PLATFORM_OSX
        ]:
            if PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value:
                import_command = unix_env_bash.format(
                    venv_path=PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value,
                    indexer_script_path=self._get_indexer_script_path()
                )
            else:
                import_command = unix_without_env_bash.format(
                    indexer_script_path=self._get_indexer_script_path()
                )
        else:
            if PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value:
                import_command = windows_env_bash.format(
                    venv_path=PyRockSettings().PYTHON_VIRTUAL_ENV_PATH.value,
                    indexer_script_path=self._get_indexer_script_path()
                )
            else:
                import_command = windows_without_env_bash.format(
                    indexer_script_path=self._get_indexer_script_path()
                )

        return import_command
    
    def _run_indexer(self, window: Window, force=False):
        if self._is_indexing_needed() and not force:
            logger.debug("Indexing not needed")
            window.status_message("Indexing not needed")
            return

        self._command_error_evidence: List[str] = []

        self._generate_serialized_settings()

        window.set_status_bar_visible(True)

        window.status_message("Indexing imports...")

        import_command: str = self._get_import_command()
        
        logger.debug(f"Import shell command using: {import_command}")
        success, message = self._run_import_indexer(window, import_command)
        logger.debug(f"Indexing result: {success}")

        if success:
            window.status_message("Finished imports...")
        else:
            sublime.error_message(f"Indexing Failed\n\n{message}")
