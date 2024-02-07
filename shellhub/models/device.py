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
    last_seen: str
    online: bool
    namespace: str
    status: str
    status_updated_at: str
    created_at: str
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
        self.last_seen = device_json["last_seen"]
        self.online = device_json["online"]
        self.namespace = device_json["namespace"]
        self.status = device_json["status"]
        self.status_updated_at = device_json["status_updated_at"]
        self.created_at = device_json["created_at"]
        self.remote_addr = device_json["remote_addr"]
        self.tags = device_json["tags"]
        self.acceptable = device_json["acceptable"]

    def delete(self) -> bool:
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
        if not self.acceptable:
            raise ShellHubApiError(f"Device {self.uid} is not acceptable.")

        response = self._api.make_request(endpoint=f"/api/devices/{self.uid}/accept", method="POST")
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

    def __repr__(self) -> str:
        return (
            f"ShellHubDevice(name={self.name}, online={self.online}, namespace={self.namespace}, status={self.status})"
        )

    def __str__(self) -> str:
        return self.uid
