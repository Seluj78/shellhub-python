import io
import re
import subprocess
import sys
from os import path


def read(*names, **kwargs):
    with io.open(path.join(path.dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")) as file:
        return file.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def version():
    return find_version("../dst_package/__init__.py")


if __name__ == "__main__":
    current_version = version()
    latest_tag_id = subprocess.getoutput("git rev-list --tags --max-count=1")
    last_version = subprocess.getoutput(f"git describe --tags {latest_tag_id}")

    print(f"Current version: {current_version}")
    print(f"Last version: {last_version}")

    if current_version == last_version.replace("v", ""):
        sys.exit(
            f"Package version hasn't changed. "
            f"Latest version from tags is {last_version} and version from __init__ is {current_version}"
        )
