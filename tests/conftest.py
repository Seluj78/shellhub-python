import pytest
import requests_mock as r_mock

from shellhub import ShellHub
from tests.utils import MOCKED_DOMAIN_URL


@pytest.fixture(scope="function")
def shellhub():
    with r_mock.Mocker() as m:
        # Mock the login URL
        login_url = f"{MOCKED_DOMAIN_URL}/api/login"
        mock_response = {
            "token": "jwt_token",
        }
        m.post(login_url, json=mock_response)

        # Create an instance of ShellHub with mocked login
        shellhub_instance = ShellHub(username="john.doe", password="dolphin", endpoint=MOCKED_DOMAIN_URL)

        yield shellhub_instance


@pytest.fixture(scope="function")
def shellhub_device(shellhub, requests_mock):
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
    ]
    requests_mock.get(f"{MOCKED_DOMAIN_URL}/api/devices", json=mock_response)
    return shellhub.get_all_devices()[0]
