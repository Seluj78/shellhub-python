import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from urllib.parse import urlparse

import requests

import shellhub.models.device
from shellhub.exceptions import DeviceNotFoundError
from shellhub.exceptions import ShellHubApiError
from shellhub.exceptions import ShellHubAuthenticationError
from shellhub.exceptions import ShellHubBaseException


class ShellHub:
    _username: str
    _password: str
    _endpoint: str
    _url: str
    _access_token: Optional[str]
    _use_ssl: bool

    def __init__(self, username: str, password: str, endpoint_or_url: str, use_ssl: bool = True) -> None:
        self._username = username
        self._password = password
        self._use_ssl = use_ssl
        self._url, self._endpoint = self._format_and_validate_url(endpoint_or_url)
        self._access_token = None

        self._login()

    def _format_and_validate_url(self, endpoint: str) -> Tuple[str, str]:
        """
        Format and validate the URL provided by the user. If the URL doesn't start with http:// or https://, it will
        :param endpoint: The URL provided by the user for the shellhub instance
        :return: A tuple containing the full URL and the base endpoint
        """

        # Adjust the endpoint based on the _use_ssl flag
        if not endpoint.startswith(("http://", "https://")):
            protocol = "https://" if self._use_ssl else "http://"
            endpoint = protocol + endpoint

        # Validate the URL (basic check)
        if not self._is_valid_url(endpoint):
            raise ShellHubBaseException("Invalid URL provided.")

        # Use urlparse to extract the base endpoint without the scheme
        parsed_url = urlparse(endpoint)
        base_endpoint = parsed_url.netloc

        return endpoint, base_endpoint  # Return both full URL and base endpoint

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        Check if the URL provided is valid
        :param url: The URL to be checked
        :return: True if the URL is valid, False otherwise
        """
        pattern = re.compile(
            r"^https?:\/\/"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:\/[^\s]*)?$",
            re.IGNORECASE,
        )  # optional path
        return re.match(pattern, url) is not None

    def __repr__(self) -> str:
        return f"<ShellHub username={self._username} url={self._url}>"

    def __str__(self) -> str:
        return self._url

    def _login(self) -> None:
        try:
            response = requests.post(
                f"{self._url}/api/login",
                json={
                    "username": self._username,
                    "password": self._password,
                },
            )
        except requests.exceptions.ConnectionError:
            raise ShellHubBaseException("Incorrect endpoint. Is the server up and running ?")

        if response.status_code == 401:
            raise ShellHubAuthenticationError("Incorrect username or password")
        elif response.status_code != 200:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise ShellHubApiError(e)
        else:
            self._access_token = response.json()["token"]

    def make_request(
        self,
        endpoint: str,
        method: str,
        query_params: Optional[Dict[Any, Any]] = None,
        json: Optional[Dict[Any, Any]] = None,
    ) -> requests.Response:
        params = ""
        if query_params:
            params = "?"
            for key, value in query_params.items():
                params += f"{key}={value}&"
            params = params[:-1]

        response: requests.Response = getattr(requests, method.lower())(
            f"{self._url}{endpoint}{params if params else ''}",
            headers={
                "Authorization": f"Bearer {self._access_token}",
            },
            json=json,
        )

        if response.status_code == 401:
            self._login()
            response = getattr(requests, method.lower())(
                f"{self._url}{endpoint}{params if params else ''}",
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                },
                json=json,
            )
            if response.status_code == 401:
                raise ShellHubApiError(f"Couldn't fix request with a token refresh: {response.text}")

        return response

    def _get_devices(
        self, query_params: Optional[Dict[Any, Any]] = None
    ) -> "List[shellhub.models.device.ShellHubDevice]":
        response = self.make_request(endpoint="/api/devices", method="GET", query_params=query_params)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ShellHubApiError(e)

        devices = []
        for device in response.json():
            devices.append(shellhub.models.device.ShellHubDevice(self, device))
        return devices

    def get_all_devices(
        self, status: Optional[str] = None, query_params: Optional[Dict[Any, Any]] = None
    ) -> "List[shellhub.models.device.ShellHubDevice]":
        """
        Get all devices from ShellHub. Default gets all devices
        """
        if not query_params:
            query_params = {}
        if status:
            if status not in ["accepted", "rejected", "pending", "removed", "unused"]:
                raise ValueError("status must be one of accepted, rejected or pending")
            query_params["status"] = status
        devices = []
        page = 1
        while True:
            devices_response = self._get_devices(query_params={"page": page, "per_page": 100, **query_params})
            devices += devices_response
            if len(devices_response) < 100:
                break
            page += 1
        return devices

    def get_device(self, uid: str) -> "shellhub.models.device.ShellHubDevice":
        """
        Get a device from ShellHub by its UID
        :param uid: The UID of the device
        :return: A ShellHubDevice object
        """
        response = self.make_request(endpoint=f"/api/devices/{uid}", method="GET")
        if response.status_code == 404:
            raise DeviceNotFoundError(f"Device {uid} not found.")
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise ShellHubApiError(e)
            else:
                return shellhub.models.device.ShellHubDevice(self, response.json())
