import pytest

from shellhub import ShellHub
from shellhub import ShellHubAuthenticationError
from shellhub import ShellHubBaseException
from tests.utils import MOCKED_DOMAIN_URL


def test_login(requests_mock):
    login_url = f"{MOCKED_DOMAIN_URL}/api/login"
    mock_response = {
        "token": "jwt_token",
    }
    requests_mock.post(login_url, json=mock_response)
    shellhub = ShellHub(username="john.doe", password="dolphin", endpoint=MOCKED_DOMAIN_URL)
    assert shellhub._access_token == mock_response["token"]


def test_incorrect_endpoint():
    with pytest.raises(ShellHubBaseException):
        ShellHub(username="john.doe", password="dolphin", endpoint=MOCKED_DOMAIN_URL)


def test_incorrect_username_password(requests_mock):
    login_url = f"{MOCKED_DOMAIN_URL}/api/login"
    mock_response = {
        "detail": "Incorrect username or password",
    }
    requests_mock.post(login_url, json=mock_response, status_code=401)
    with pytest.raises(ShellHubAuthenticationError):
        ShellHub(username="john.doe", password="dolphin", endpoint=MOCKED_DOMAIN_URL)


def test_repr(shellhub):
    assert repr(shellhub) == f"<ShellHub username=john.doe endpoint={MOCKED_DOMAIN_URL}>"


def test_str(shellhub):
    assert str(shellhub) == shellhub._endpoint
