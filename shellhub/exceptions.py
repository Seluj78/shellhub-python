class ShellHubBaseException(Exception):
    pass


class ShellHubApiError(ShellHubBaseException):
    pass


class ShellHubAuthenticationError(ShellHubBaseException):
    pass


class DeviceNotFoundError(ShellHubApiError):
    pass
