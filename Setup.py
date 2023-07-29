from cx_Freeze import setup, Executable
import sys

# Dependências são automaticamente detectadas, mas pode precisar de ajustes finos.
build_exe_options = {
    "packages": ["os", "datetime", "subprocess", "requests", "tkinter", "pandas", "sys", "webbrowser", "time", "collections"],
    "include_files": ["intervalos12.py", "App.py", "index.html", "static/"],
    "includes": ["tkinter", "pandas", "webbrowser", "asyncio", "aiohttp","os", "datetime", "subprocess", "requests", "sys", "time", "collections"]
}

# GUI applications require a different base on Windows (the default is for
# a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Invictus Analyses",
    version = "1.1",
    description = "Aplicação Invictus Live",
    options = {"build_exe": build_exe_options},
    executables = [Executable("inter.py", base=base)]
)