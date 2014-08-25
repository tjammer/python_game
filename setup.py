import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"],
                     "excludes": ["tkinter", "numpy", "email"],
                     "include_files":
                     ["maps\phrantic.svg", "maps\phrantic.svg",
                      "maps\\blank.svg", "maps\\blank.svg"],
                     "create_shared_zip": False,
                     "optimize": 1}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="python_game",
      version="0.1",
      description="python game",
      options={"build_exe": build_exe_options},
      executables=[Executable("main.py", base=base,
                   appendScriptToExe=True,
                   appendScriptToLibrary=False)])
