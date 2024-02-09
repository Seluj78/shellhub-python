# Increment versions here according to SemVer
__version__ = "0.2.4"

from .models.device import ShellHubDevice, ShellHubDeviceInfo
from .models.base import ShellHub
from .exceptions import (
    ShellHubApiError,
    ShellHubAuthenticationError,
    DeviceNotFoundError,
    ShellHubBaseException,
)


__all__ = [
    "ShellHub",
    "ShellHubDevice",
    "ShellHubDeviceInfo",
    "ShellHubApiError",
    "ShellHubAuthenticationError",
    "DeviceNotFoundError",
    "ShellHubBaseException",
]
