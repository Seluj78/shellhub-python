import re
import subprocess

from packaging import version


cat_cmd = subprocess.Popen(("cat", "shellhub/__init__.py"), stdout=subprocess.PIPE)
output = subprocess.check_output(("grep", "__version__"), stdin=cat_cmd.stdout).decode("utf-8").strip()
cat_cmd.wait()


# Regular expression pattern to find the version
version_pattern = r'__version__ = "([0-9]+\.[0-9]+\.[0-9]+)"'

# Search for the pattern and extract the version
match = re.search(version_pattern, output)
if match:
    current_version = match.group(1)
else:
    raise ValueError("Version not found in __init__.py")

previous_version = (
    subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"]).decode("utf-8").replace("v", "").strip()
)

print(f"Current version:  {current_version}")
print(f"Previous version: {previous_version}")


if version.parse(current_version) <= version.parse(previous_version):
    print("Version has not been incremented.")
    exit(1)
else:
    print("Version has been incremented.")
    exit(0)
