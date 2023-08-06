PyRock
================
[![Build][build-shield]][build-url]
[![Code Coverage][code-coverage-shield]][code-coverage-url]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

-----------------------------

Sublime plugin to generate import statement for python

Features
--------
- Generate's Import statement
- Supports virtual enviroment

Upcoming Features
-----------------
- AI autocomplete
- Copy python import statement (module, class, method)
- Copy python path (module)
- Copy unittest path (module, class, method)

Installation
------------
- From sublime package control install package enter name `PyRock`
- OR
- Clone this git repo and put it in your sublime packages folder

Settings
--------
```
{
    "paths_to_scan": [], // Not used as of now
    "python_venv_path": "",
    "python_interpreter_path": "", // Not used as of now
    "log_level": "info",
    "import_scan_depth": 4
}
```
- `paths_to_scan`: This is still in development, it will have no effect as of now.
- `python_interpreter_path`: This is still in development, it will have no effect as of now.
- `python_venv_path` : Specifies which python env to use when indexing files, if not given it will choose the default python interpreter of your system (Make sure you have set any default python, otherwise it will not be able to index). It takes the full path to `activate` file of the virtual environment, for example:
  ```
  "python_venv_path": "~/home/venv/bin/activate"
  ```
- `log_level`: By default set to `info`, accepted values `info`, `debug`, `error`, `warning`
- `import_scan_depth`: This defines how deep it will scan any python package, the higher the number the more deep it will go, `4` is an optimal depth, you can increase it but it will also increase the time to index all files, so change it carefully.

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

Compatibility
-------------
- Require Sublime Text version > 3
- Works for `Python Imports` only


[build-shield]: https://img.shields.io/travis/abhishek72850/pyrock.svg?style=for-the-badge
[build-url]: https://travis-ci.org/abhishek72850/pyrock
[code-coverage-shield]: https://img.shields.io/codecov/c/github/abhishek72850/pyrock/master?style=for-the-badge
[code-coverage-url]: https://codecov.io/gh/abhishek72850/pyrock
[contributors-shield]: https://img.shields.io/github/contributors/abhishek72850/pyrock.svg?style=for-the-badge
[contributors-url]: https://github.com/abhishek72850/pyrock/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/abhishek72850/pyrock.svg?style=for-the-badge
[forks-url]: https://github.com/abhishek72850/pyrock/network/members
[stars-shield]: https://img.shields.io/github/stars/abhishek72850/pyrock.svg?style=for-the-badge
[stars-url]: https://github.com/abhishek72850/pyrock/stargazers
[issues-shield]: https://img.shields.io/github/issues/abhishek72850/pyrock.svg?style=for-the-badge
[issues-url]: https://github.com/abhishek72850/pyrock/issues
