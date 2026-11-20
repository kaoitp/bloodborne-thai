"""Collect the notices shipped with the installer archives."""

from importlib.metadata import distribution
from pathlib import Path
from shutil import copyfile
import sys


destination = Path(sys.argv[1])
destination.mkdir(parents=True, exist_ok=True)
fonttools = distribution("fonttools")
fonttools_license = next(
    path for path in fonttools.files if path.name == "LICENSE" and path.parent.name == "licenses"
)
copyfile(fonttools.locate_file(fonttools_license), destination / "fontTools.txt")

if sys.platform == "win32":
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
else:
    if sys.version_info[:2] != (3, 13):
        raise SystemExit("Use Python 3.13 to build the Linux installer.")
    python_license = Path("licenses/Python-3.13.txt")
    copyfile("licenses/zlib.txt", destination / "zlib.txt")
copyfile(python_license, destination / "Python.txt")
