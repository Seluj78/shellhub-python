import pytest

from shellhub import ShellHub
from shellhub import ShellHubApiError


def test_login(requests_mock):
    login_url = "http://localhost.shellhub/api/login"
    mock_response = {
        "token": "jwt_token",
    }
    requests_mock.post(login_url, json=mock_response)
    shellhub = ShellHub(username="john.doe", password="dolphin", endpoint="http://localhost.shellhub")
    assert shellhub._access_token == mock_response["token"]


def test_incorrect_endpoint():
    with pytest.raises(ValueError):
        ShellHub(username="john.doe", password="dolphin", endpoint="http://localhost.shellhub")


def test_incorrect_username_password(requests_mock):
    login_url = "http://localhost.shellhub/api/login"
    mock_response = {
        "detail": "Incorrect username or password",
    }
    requests_mock.post(login_url, json=mock_response, status_code=401)
    with pytest.raises(ShellHubApiError):
        ShellHub(username="john.doe", password="dolphin", endpoint="http://localhost.shellhub")


def test_repr(shellhub):
    assert repr(shellhub) == "<ShellHub username=john.doe endpoint=http://localhost.shellhub>"


def test_str(shellhub):
    assert str(shellhub) == shellhub._endpoint
