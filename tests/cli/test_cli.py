import pytest
import responses
from click.testing import CliRunner

from libtado.__main__ import main

TOKEN_URL = "https://login.tado.com/oauth2/token"
DEVICE_AUTHORIZE_URL = "https://login.tado.com/oauth2/device_authorize"
API = "https://my.tado.com/api/v2"


def _token():
    return {"access_token": "a", "expires_in": 599, "refresh_token": "r"}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("TADO_REFRESH_TOKEN", "TADO_CREDENTIALS_FILE", "TADO_HOME_ID"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def rsps():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as r:
        yield r


class TestCli:
    def test_pending_login_shows_url(self, rsps):
        rsps.add(responses.POST, DEVICE_AUTHORIZE_URL, json={
            "device_code": "d", "user_code": "ABC", "verification_uri": "https://login.tado.com/device",
            "expires_in": 300, "interval": 0})
        rsps.add(responses.POST, TOKEN_URL, json=_token(), status=200)
        rsps.add(responses.GET, f"{API}/me", json={"homes": [{"id": 1}]})
        rsps.add(responses.GET, f"{API}/homes/1/zones/1/capabilities", json={"type": "HEATING"})

        result = CliRunner().invoke(main, ["capabilities", "--zone", "1"])

        assert result.exit_code == 0, result.output
        assert "https://login.tado.com/device?user_code=ABC" in result.output
        assert "You have until" in result.output

    def test_rate_limited_command(self, rsps):
        rsps.add(responses.POST, TOKEN_URL, json=_token(), status=200)
        rsps.add(responses.GET, f"{API}/homes/1/zones/1/capabilities", status=429,
                 headers={"ratelimit": '"perday";r=0;t=3600'})

        result = CliRunner().invoke(main, ["-t", "tok", "-i", "1", "capabilities", "--zone", "1"])

        assert result.exit_code == 1
        assert "rate limit" in result.output
        assert "3600" in result.output
        assert "Traceback" not in result.output

    def test_http_error_is_one_line(self, rsps):
        rsps.add(responses.POST, TOKEN_URL, json=_token(), status=200)
        rsps.add(responses.GET, f"{API}/homes/1/zones/1/capabilities", status=404)

        result = CliRunner().invoke(main, ["-t", "tok", "-i", "1", "capabilities", "--zone", "1"])

        assert result.exit_code == 1
        assert "404" in result.output
        assert "Traceback" not in result.output
