from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests

import shellhub.models.device
from shellhub.exceptions import ShellHubApiError


class ShellHub:
    _username: str
    _password: str
    _endpoint: str
    _access_token: Optional[str]

    def __init__(self, username: str, password: str, endpoint: str) -> None:
        self._username: str = username
        self._password: str = password
        self._endpoint: str = endpoint
        self._access_token: Optional[str] = None

        self._login()

    def __repr__(self) -> str:
        return f"<ShellHub username={self._username} endpoint={self._endpoint}>"

    def __str__(self) -> str:
        return self._endpoint

    def _login(self) -> None:
        try:
            response = requests.post(
                f"{self._endpoint}/api/login",
                json={
                    "username": self._username,
                    "password": self._password,
                },
            )
        except requests.exceptions.ConnectionError:
            raise ValueError("Incorrect endpoint. Is the server up and running ?")

        if response.status_code == 401:
            raise ShellHubApiError("Incorrect username or password")
        elif response.status_code != 200:
            response.raise_for_status()
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
            f"{self._endpoint}{endpoint}{params if params else ''}",
            headers={
                "Authorization": f"Bearer {self._access_token}",
            },
            json=json,
        )
        return response

    def _get_devices(
        self, query_params: Optional[Dict[Any, Any]] = None
    ) -> "List[shellhub.models.device.ShellHubDevice]":
        response = self.make_request(endpoint="/api/devices", method="GET", query_params=query_params)

        response.raise_for_status()

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
        response = self.make_request(endpoint=f"/api/devices/{uid}", method="GET")
        if response.status_code == 404:
            raise ShellHubApiError(f"Device {uid} not found.")
        elif response.status_code != 200:
            response.raise_for_status()
        return shellhub.models.device.ShellHubDevice(self, response.json())
