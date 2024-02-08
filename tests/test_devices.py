import pytest

from shellhub.exceptions import ShellHubApiError
from tests.utils import MOCKED_DOMAIN_URL


def test_repr(shellhub_device):
    assert repr(shellhub_device) == "ShellHubDevice(name=default, online=True, namespace=dev, status=accepted)"


def test_str(shellhub_device):
    assert str(shellhub_device) == shellhub_device.uid


class TestGetDevices:
    def test_get_no_devices(self, shellhub, requests_mock):
        mock_response = []
        requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices", json=mock_response)
        devices = shellhub.get_all_devices()
        assert len(devices) == 0

    def test_get_incorrect_status(self, shellhub):
        with pytest.raises(ValueError):
            shellhub.get_all_devices(status="incorrect_status")

    @pytest.mark.parametrize(
        "status",
        [
            "accepted",
            "pending",
            "rejected",
            "removed",
            "unused",
        ],
    )
    def test_correct_status(self, shellhub, requests_mock, status):
        mock_response = [
            {
                "uid": "1",
                "name": "default",
                "identity": {"mac": "06:04:ju:le:s7:08"},
                "info": {
                    "id": "ubuntu",
                    "pretty_name": "Ubuntu 20.04.2 LTS",
                    "version": "v0.14.1",
                    "arch": "amd64",
                    "platform": "docker",
                },
                "public_key": "-----BEGIN RSA PUBLIC KEY-----\nxxx\nxxx\nxxx"
                "\nxxx\nxxx\nxxx\n-----END RSA PUBLIC KEY-----\n",
                "tenant_id": "1",
                "last_seen": "1970-01-01T00:00:00Z",
                "online": True,
                "namespace": "dev",
                "status": "accepted",
                "status_updated_at": "1970-01-01T00:00:00Z",
                "created_at": "1970-01-01T00:00:00Z",
                "remote_addr": "0.0.0.0",
                "position": {"latitude": 0, "longitude": 0},
                "tags": [],
                "public_url": False,
                "public_url_address": "",
                "acceptable": False,
            }
        ]
        requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices", json=mock_response)
        devices = shellhub.get_all_devices(status=status)
        assert len(devices) == 1


class TestGetDevice:
    def test_device_not_found(self, shellhub, requests_mock):
        requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=404)
        with pytest.raises(ShellHubApiError):
            shellhub.get_device("1")

    def test_get_device(self, shellhub, requests_mock):
        mock_response = {
            "uid": "1",
            "name": "default",
            "identity": {"mac": "06:04:ju:le:s7:08"},
            "info": {
                "id": "ubuntu",
                "pretty_name": "Ubuntu 20.04.2 LTS",
                "version": "v0.14.1",
                "arch": "amd64",
                "platform": "docker",
            },
            "public_key": "-----BEGIN RSA PUBLIC KEY-----\nxxx\nxxx\nxxx\n"
            "xxx\nxxx\nxxx\n-----END RSA PUBLIC KEY-----\n",
            "tenant_id": "1",
            "last_seen": "1970-01-01T00:00:00Z",
            "online": True,
            "namespace": "dev",
            "status": "accepted",
            "status_updated_at": "1970-01-01T00:00:00Z",
            "created_at": "1970-01-01T00:00:00Z",
            "remote_addr": "0.0.0.0",
            "position": {"latitude": 0, "longitude": 0},
            "tags": [],
            "public_url": False,
            "public_url_address": "",
            "acceptable": False,
        }
        requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices/1", json=mock_response)
        device = shellhub.get_device("1")

        assert device.uid == "1"
        assert device.name == "default"
        assert device.mac_address == "06:04:ju:le:s7:08"
        assert device.info.id == "ubuntu"
        assert device.info.pretty_name == "Ubuntu 20.04.2 LTS"
        assert device.info.version == "v0.14.1"
        assert device.info.arch == "amd64"
        assert device.info.platform == "docker"
        assert (
            device.public_key
            == "-----BEGIN RSA PUBLIC KEY-----\nxxx\nxxx\nxxx\nxxx\nxxx\nxxx\n-----END RSA PUBLIC KEY-----\n"
        )
        assert device.tenant_id == "1"
        assert device.last_seen == "1970-01-01T00:00:00Z"
        assert device.online
        assert device.namespace == "dev"
        assert device.status == "accepted"
        assert device.status_updated_at == "1970-01-01T00:00:00Z"
        assert device.created_at == "1970-01-01T00:00:00Z"
        assert device.remote_addr == "0.0.0.0"
        assert device.tags == []
        assert not device.acceptable


class TestDeleteDevice:
    def test_delete_device(self, shellhub_device, requests_mock):
        requests_mock.delete(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=200)
        assert shellhub_device.delete()

    def test_delete_device_already_deleted(self, shellhub_device, requests_mock):
        requests_mock.delete(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=404)
        with pytest.raises(ShellHubApiError):
            shellhub_device.delete()


class TestRenameDevice:
    def test_rename_device_new_name(self, shellhub_device, requests_mock):
        requests_mock.put(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=200)
        shellhub_device.rename("new_name")

        assert shellhub_device.name == "new_name"

    def test_rename_non_existent_device(self, shellhub_device, requests_mock):
        requests_mock.put(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=404)
        with pytest.raises(ShellHubApiError):
            shellhub_device.rename("new_name")

    def test_rename_conflict(self, shellhub_device, requests_mock):
        requests_mock.put(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=409)
        with pytest.raises(ShellHubApiError):
            shellhub_device.rename("new_name")

    def test_rename_original_name(self, shellhub_device, requests_mock):
        requests_mock.put(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=200)
        shellhub_device.rename("default")

        assert shellhub_device.name == "default"

        requests_mock.put(f"{MOCKED_DOMAIN_URL}/api/devices/1", status_code=200)
        shellhub_device.rename()

        assert shellhub_device.name == "06-04-ju-le-s7-08"


class TestRefreshDevice:
    def test_refresh_unknown_device(self, shellhub_device, requests_mock):
        requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices/2", status_code=404)
        shellhub_device.uid = "2"
        with pytest.raises(ShellHubApiError):
            shellhub_device.refresh()

    def test_refresh_device(self, shellhub_device, requests_mock):
        mock_response = {
            "uid": "2",
            "name": "default",
            "identity": {"mac": "06:04:ju:le:s7:08"},
            "info": {
                "id": "ubuntu",
                "pretty_name": "Ubuntu 20.04.2 LTS",
                "version": "v0.14.1",
                "arch": "amd64",
                "platform": "docker",
            },
            "public_key": "-----BEGIN RSA PUBLIC KEY-----\nxxx\nxxx\nxxx\n"
            "xxx\nxxx\nxxx\n-----END RSA PUBLIC KEY-----\n",
            "tenant_id": "1",
            "last_seen": "1970-01-01T00:00:00Z",
            "online": True,
            "namespace": "dev",
            "status": "accepted",
            "status_updated_at": "1970-01-01T00:00:00Z",
            "created_at": "1970-01-01T00:00:00Z",
            "remote_addr": "0.0.0.0",
            "position": {"latitude": 0, "longitude": 0},
            "tags": [],
            "public_url": False,
            "public_url_address": "",
            "acceptable": False,
        }
        requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices/1", json=mock_response)

        assert shellhub_device.uid == "1"

        shellhub_device.refresh()

        assert shellhub_device.uid == "2"


class TestAcceptDevice:
    def test_not_acceptable_device(self, shellhub_device):
        shellhub_device.acceptable = False
        with pytest.raises(ShellHubApiError):
            shellhub_device.accept()

    def test_accept_notfound_device(self, shellhub_device, requests_mock):
        requests_mock.post(f"{MOCKED_DOMAIN_URL}/api/devices/1/accept", status_code=404)
        shellhub_device.acceptable = True
        with pytest.raises(ShellHubApiError):
            shellhub_device.accept()

    def test_accept_device(self, shellhub_device, requests_mock):
        mock_response = {
            "uid": "2",
            "name": "default",
            "identity": {"mac": "06:04:ju:le:s7:08"},
            "info": {
                "id": "ubuntu",
                "pretty_name": "Ubuntu 20.04.2 LTS",
                "version": "v0.14.1",
                "arch": "amd64",
                "platform": "docker",
            },
            "public_key": "-----BEGIN RSA PUBLIC KEY-----\nxxx\nxxx\nxxx\n"
            "xxx\nxxx\nxxx\n-----END RSA PUBLIC KEY-----\n",
            "tenant_id": "1",
            "last_seen": "1970-01-01T00:00:00Z",
            "online": True,
            "namespace": "dev",
            "status": "accepted",
            "status_updated_at": "1970-01-01T00:00:00Z",
            "created_at": "1970-01-01T00:00:00Z",
            "remote_addr": "0.0.0.0",
            "position": {"latitude": 0, "longitude": 0},
            "tags": [],
            "public_url": False,
            "public_url_address": "",
            "acceptable": False,
        }
        requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices/1", json=mock_response)
        requests_mock.post(f"{MOCKED_DOMAIN_URL}/api/devices/1/accept", status_code=200)

        shellhub_device.acceptable = True
        shellhub_device.accept()

        assert not shellhub_device.acceptable


class TestDeviceSSHID:
    def test_get_sshid(self, shellhub_device, shellhub):
        assert shellhub_device.sshid == f"{shellhub_device.namespace}.{shellhub_device.name}@{shellhub._endpoint}"

    def test_acceptable_device_sshid(self, shellhub_device, shellhub):
        shellhub_device.acceptable = True
        assert shellhub_device.sshid is None
