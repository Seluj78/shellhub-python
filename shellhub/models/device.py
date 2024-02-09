from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

import requests

import shellhub.models.base
from shellhub.exceptions import DeviceNotFoundError
from shellhub.exceptions import ShellHubApiError


class ShellHubDeviceInfo:
    id: str
    pretty_name: str
    version: str
    arch: str
    platform: str

    def __init__(self, device_info_json: Dict[str, str]):
        self.id = device_info_json["id"]
        self.pretty_name = device_info_json["pretty_name"]
        self.version = device_info_json["version"]
        self.arch = device_info_json["arch"]
        self.platform = device_info_json["platform"]

    def __repr__(self) -> str:
        return (
            f"ShellHubDeviceInfo(id={self.id}, pretty_name={self.pretty_name}, "
            f"version={self.version}, arch={self.arch}, platform={self.platform})"
        )

    def __str__(self) -> str:
        return self.pretty_name


class ShellHubDevice:
    uid: str
    name: str
    mac_address: str
    info: ShellHubDeviceInfo
    public_key: str
    tenant_id: str
    last_seen: datetime
    online: bool
    namespace: str
    status: str
    status_updated_at: datetime
    created_at: datetime
    remote_addr: str
    tags: List[str]
    acceptable: bool

    def __init__(self, api_object: shellhub.models.base.ShellHub, device_json):  # type: ignore
        self._api = api_object

        self.uid = device_json["uid"]
        self.name = device_json["name"]
        self.mac_address = device_json["identity"]["mac"]
        self.info = ShellHubDeviceInfo(device_json["info"])
        self.public_key = device_json["public_key"]
        self.tenant_id = device_json["tenant_id"]
        self.last_seen = self._safe_isoformat_to_datetime(device_json["last_seen"])
        self.online = device_json["online"]
        self.namespace = device_json["namespace"]
        self.status = device_json["status"]
        self.status_updated_at = self._safe_isoformat_to_datetime(device_json["status_updated_at"])
        self.created_at = self._safe_isoformat_to_datetime(device_json["created_at"])
        self.remote_addr = device_json["remote_addr"]
        self.tags = device_json["tags"]
        self.acceptable = device_json["acceptable"]

    @staticmethod
    def _safe_isoformat_to_datetime(date_string: str) -> datetime:
        # Replace "Z" with "+00:00" to indicate UTC in a format compatible with Python 3.7-3.10.
        if date_string.endswith("Z"):
            date_string = date_string[:-1] + "+00:00"
        try:
            # Direct conversion using fromisoformat
            return datetime.fromisoformat(date_string)
        except ValueError:
            try:
                # For Python versions that do not handle offset-aware datetimes well in fromisoformat
                # This part is more of a catch-all to ensure even non-standard or unexpected formats
                # might be parsed, but primarily, the first attempt should work for ISO 8601 formats.
                # Note: strptime might not be necessary if fromisoformat works after the 'Z' to '+00:00' replacement,
                # but it's here as an example if further customization is needed.
                return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError as e:
                # If the first attempt fails due to the format not being exactly ISO 8601 after 'Z' replacement,
                # this additional attempt can catch other variations. This might not be strictly necessary,
                # depending on your input formats.
                raise ShellHubApiError(f"Invalid date string: {date_string} (Couldn't convert to datetime)") from e

    def delete(self) -> bool:
        """
        Delete the device from the API
        :return: True if the device was deleted, False otherwise
        """
        response = self._api.make_request(endpoint=f"/api/devices/{self.uid}", method="DELETE")
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise DeviceNotFoundError(f"Device {self.uid} not found.")
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise ShellHubApiError(e)
            else:
                return False

    def rename(self, name: Optional[str] = None) -> bool:
        """
        Set a new name for the device. If no name is provided, the name will be the mac address of the device
        """
        if not name:
            name = self.mac_address.replace(":", "-")
        response = self._api.make_request(endpoint=f"/api/devices/{self.uid}", method="PUT", json={"name": name})
        if response.status_code == 200:
            self.name = name
            return True
        elif response.status_code == 404:
            raise DeviceNotFoundError(f"Device {self.uid} not found.")
        elif response.status_code == 409:
            raise ShellHubApiError(f"Device with name {name} already exists.")
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise ShellHubApiError(e)
            else:
                return False

    def accept(self) -> bool:
        """
        Accept the device if it is pending
        :return: True if the device was accepted, False otherwise
        """
        if self.status != "pending":
            raise ShellHubApiError(f"Device {self.uid} is not pending.")

        response = self._api.make_request(endpoint=f"/api/devices/{self.uid}/accept", method="PATCH")
        if response.status_code == 200:
            self.refresh()
            return True
        elif response.status_code == 404:
            raise DeviceNotFoundError(f"Device {self.uid} not found.")
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise ShellHubApiError(e)
            else:
                return False

    def refresh(self) -> None:
        """
        Refresh the device information from the API
        :return: None
        """
        response = self._api.make_request(endpoint=f"/api/devices/{self.uid}", method="GET")
        if response.status_code == 404:
            raise DeviceNotFoundError(f"Device {self.uid} not found.")
        elif response.status_code == 200:
            self.__init__(self._api, response.json())  # type: ignore
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise ShellHubApiError(e)

    @property
    def sshid(self) -> Optional[str]:
        """
        Fabricates the SSHID of the devices from the namespace, name and endpoint
        :return: SSHID of the device
        """
        if self.acceptable:
            return None
        return f"{self.namespace}.{self.name}@{self._api._endpoint}"

    def __repr__(self) -> str:
        return (
            f"ShellHubDevice(name={self.name}, online={self.online}, namespace={self.namespace}, status={self.status})"
        )

    def __str__(self) -> str:
        return self.uid
