PyRock
================
[![Sublime Text][sublime-shield]][sublime-url]
[![Plugin Download][plugin-download-shield]][plugin-download-url]
[![Code Coverage][code-coverage-shield]][code-coverage-url]
[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Release][release-shield]][release-url]

-----------------------------

Sublime plugin to generate import statement for python


![Demo](https://github.com/abhishek72850/pyrock/assets/18554923/449b3817-171b-4a64-a0dd-13d7c6af9852)


Features
--------
- Generate's Import statement
- Copy Import statement
- Generate and copy `django` or `pytest` supported test path
- Run `django` or `pytest` tests
- Supports virtual enviroment

Upcoming Features
-----------------
- Autocomplete
- Project level plugin settings

Installation
------------
- From sublime package control install package enter name `PyRock`
- OR
- Clone this git repo and put it in your sublime packages folder

Settings
--------
```json
{
    "paths_to_scan": [], // Not used as of now
    "python_venv_path": "",
    "python_interpreter_path": "", // Not used as of now
    "log_level": "info",
    "import_scan_depth": 4,
    "test_config": {
        "enabled": false, // Enable or disable run test feature, default false
        "test_framework": "", // django or pytest
        "working_directory": "", // Working directory of your project
        "test_runner_command": [], // Command to execute when clicking `Run as test`
    }
}
```
- `paths_to_scan`: This is still in development, it will have no effect as of now.
- `python_interpreter_path`: This is still in development, it will have no effect as of now.
- `python_venv_path` : Specifies which python env to use when indexing files, if not given it will choose the default python interpreter of your system (Make sure you have set any default python, otherwise it will not be able to index). It takes the full path to `activate` file of the virtual environment, for example:
  ```
  "python_venv_path": "/Users/abhishek/venv/bin/activate"
  ```
- `log_level`: By default set to `info`, accepted values `info`, `debug`, `error`, `warning`
- `import_scan_depth`: This defines how deep it will scan any python package, the higher the number the more deep it will go, `4` is an optimal depth, you can increase it but it will also increase the time to index all files, so change it carefully.

- `test_config.enabled`
    - **Description**: Enable or disable run test feature
    - **Type**: `str`
    - **Allowed Values**: `true` or `false`
    - **Default**: `false`
    > ⚠️ If its `false` then it will ignore all other settings in `test_config`

- `test_config.test_framework`
    - **Description**: Defines what library is used for running the test
    - **Type**: `str`
    - **Allowed Values**: `django` or `pytest`
    - **Default**: NA
    > ⚠️ This assumes that `django` or `pytest` is pre-installed in your python env

- `test_config.working_directory`
    - **Description**: Working directory of your project, this will be used to define what is the root of project
    - **Type**: `str`
    - **Allowed Values**: Valid Path
    - **Default**: NA
    - **Example**:
        ```
        "working_directory": "/Users/abhishek/django-app/"
        ```

- `test_config.test_runner_command`
    - **Description**: Command to execute when clicking `Run as test`
    - **Type**: `List[str]`
    - **Allowed Values**: NA
    - **Default**: NA
    - **Example**
        ```json
        // For Django
        "test_runner_command": ["python", "manage.py", "test", "--keepdb"]

        // For Pytest
        "test_runner_command": ["pytest"] 
        ```

Usage
-----
- Upon installation it automatically reads the settings and scans your python environment for packages and index them.
  You will see progress of indexing in status bar, like this:
  <br><img width="399" alt="Indexing progress" src="https://github.com/abhishek72850/pyrock/assets/18554923/35315978-ddf1-46e5-a44e-57f437ac1dea">

- For some reason if indexing didn't happened or you want to re-index after you have removed/installed packages in your python environment, you can do so by calling `Re-Index Imports` from command pallate or just right-click to open menu and under `PyRock` you will see `Re-Index Imports`
<br><img width="760" alt="Re-index" src="https://github.com/abhishek72850/pyrock/assets/18554923/f0de1a36-1233-476e-8ad6-1c9fada109f2">

- To generate python import, select the text (min 2 characters) then right click and under `PyRock` click `Import Symbol`, it will show you the suggestion out which you select any and it will add that import statement into your python script.
  <img width="589" alt="Import symbol" src="https://github.com/abhishek72850/pyrock/assets/18554923/eb1421ff-4304-40f5-aca8-eaea84c96145">
  <img width="584" alt="import suggestions" src="https://github.com/abhishek72850/pyrock/assets/18554923/a64fadef-9554-4840-929b-72a93f27c799">

- To Run Tests:
    - Write your tests and save it as `test_*.py`, the file name has to be prefixed with `test_`
    - Then as you save it will show `Run as test` annotation on individual test class and methods, if you click on any of them it will run that particular test
    > If in between you want to run another test you can simply click on the `Run as test` but this will terminate any running test and starts the new one.
    <img width="691" alt="Screenshot 2024-05-12 at 4 05 26 PM" src="https://github.com/abhishek72850/pyrock/assets/18554923/4d424ca9-eef0-448b-9d07-f5bf43dd60d5">
![Run test demo](https://github.com/abhishek72850/pyrock/assets/18554923/512c05a2-be75-4b6b-b17e-e6af4f1026bd)


Key Bindings
------------
- By default key bindings for this plugin are disabled, to enable it you simply goto `Preferences` -> `Package Settings` -> `PyRock` -> `Key Bindings` and then copy paste from left view to your right view and uncomment it or you can copy the below directly to your right view and save it:
```
[
  // Both of the key binding generate import statement suggestions for the selected text
  {
    "keys": ["super+shift+;"],
    "command": "py_rock",
    "args": { "action": "import_symbol" }
  },
  {
    "keys": ["ctrl+shift+;"],
    "command": "py_rock",
    "args": { "action": "import_symbol" }
  }
]
```

Compatibility
-------------
- Require Sublime Text version >= 4
- Works for `Python Imports` only
- Best experience with linter support [Optional]


[code-coverage-shield]: https://img.shields.io/codecov/c/github/abhishek72850/pyrock/master?style=for-the-badge
[code-coverage-url]: https://codecov.io/gh/abhishek72850/pyrock
[contributors-shield]: https://img.shields.io/github/contributors/abhishek72850/pyrock.svg?style=for-the-badge
[contributors-url]: https://github.com/abhishek72850/pyrock/graphs/contributors
[stars-shield]: https://img.shields.io/github/stars/abhishek72850/pyrock.svg?style=for-the-badge
[stars-url]: https://github.com/abhishek72850/pyrock/stargazers
[issues-shield]: https://img.shields.io/github/issues/abhishek72850/pyrock.svg?style=for-the-badge
[issues-url]: https://github.com/abhishek72850/pyrock/issues
[release-shield]: https://img.shields.io/github/v/release/abhishek72850/pyrock.svg?style=for-the-badge
[release-url]: https://img.shields.io/github/v/release/abhishek72850/pyrock
[sublime-shield]: https://img.shields.io/badge/Made%20For-Sublime%204-ff9800?logo=sublime%20text&style=for-the-badge
[sublime-url]: https://www.sublimetext.com/
[plugin-download-shield]: https://img.shields.io/packagecontrol/dt/PyRock?style=for-the-badge
[plugin-download-url]: https://packagecontrol.io/packages/PyRock
