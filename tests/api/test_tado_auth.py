import json
from urllib.parse import parse_qs

import pytest
import requests
import responses

from libtado.api import DeviceActivationStatus, Tado

TOKEN_URL = "https://login.tado.com/oauth2/token"
DEVICE_AUTHORIZE_URL = "https://login.tado.com/oauth2/device_authorize"
ME_URL = "https://my.tado.com/api/v2/me"


def _token_response(refresh_token="new-refresh-token", expires_in=599):
    return {
        "access_token": "test-access-token",
        "token_type": "bearer",
        "expires_in": expires_in,
        "refresh_token": refresh_token,
    }


def _device_authorize_response():
    return {
        "device_code": "test-device-code",
        "user_code": "TESTCODE",
        "verification_uri": "https://login.tado.com/device",
        "verification_uri_complete": "https://login.tado.com/device?user_code=TESTCODE",
        "expires_in": 300,
        "interval": 0,
    }


class TestConstruction:
    def test_construct_with_saved_refresh_token(self, mocked_responses):
        mocked_responses.add(responses.POST, TOKEN_URL, json=_token_response(), status=200)
        mocked_responses.add(responses.GET, ME_URL, json={"homes": [{"id": 12345}]}, status=200)

        tado = Tado("saved-refresh-token")

        assert tado.device_activation_status == DeviceActivationStatus.COMPLETED
        assert tado.id == 12345
        assert tado.refresh_token == "new-refresh-token"
        assert tado.access_headers["Authorization"] == "Bearer test-access-token"

        token_request_body = parse_qs(mocked_responses.calls[0].request.body)
        assert token_request_body["grant_type"] == ["refresh_token"]
        assert token_request_body["refresh_token"] == ["saved-refresh-token"]


class TestRefreshAuth:
    def test_noop_when_refresh_at_in_future(self, tado_unauthenticated, mocked_responses):
        assert tado_unauthenticated.refresh_auth() is True
        assert len(mocked_responses.calls) == 0

    def test_refreshes_when_force_refresh(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.POST, TOKEN_URL, json=_token_response(), status=200)

        assert tado_unauthenticated.refresh_auth(force_refresh=True) is True

        assert len(mocked_responses.calls) == 1
        assert tado_unauthenticated.refresh_token == "new-refresh-token"

    def test_refreshes_when_expired(self, tado_unauthenticated, mocked_responses):
        from datetime import datetime, timedelta, timezone

        tado_unauthenticated.refresh_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        mocked_responses.add(responses.POST, TOKEN_URL, json=_token_response(), status=200)

        assert tado_unauthenticated.refresh_auth() is True
        assert len(mocked_responses.calls) == 1

    def test_force_refresh_failure_returns_false(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.POST, TOKEN_URL, json={"error": "invalid_grant"}, status=400)

        assert tado_unauthenticated.refresh_auth(force_refresh=True) is False

    def test_non_force_refresh_failure_raises(self, tado_unauthenticated, mocked_responses):
        from datetime import datetime, timedelta, timezone

        tado_unauthenticated.refresh_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        mocked_responses.add(responses.POST, TOKEN_URL, json={"error": "invalid_grant"}, status=400)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.refresh_auth()


class TestLoginDeviceFlow:
    def test_success(self, tado_unauthenticated, mocked_responses):
        tado_unauthenticated.device_activation_status = DeviceActivationStatus.NOT_STARTED
        mocked_responses.add(
            responses.POST, DEVICE_AUTHORIZE_URL, json=_device_authorize_response(), status=200
        )

        status = tado_unauthenticated.login_device_flow()

        assert status == DeviceActivationStatus.PENDING
        assert tado_unauthenticated.device_code == "test-device-code"
        assert tado_unauthenticated.user_code == "TESTCODE"
        assert tado_unauthenticated.device_verification_check_interval == 0
        assert "TESTCODE" in tado_unauthenticated.device_verification_url

    def test_raises_when_already_started(self, tado_unauthenticated, mocked_responses):
        tado_unauthenticated.device_activation_status = DeviceActivationStatus.PENDING

        with pytest.raises(Exception, match="started already"):
            tado_unauthenticated.login_device_flow()


class TestCheckDeviceActivation:
    def _prepare(self, tado_unauthenticated):
        tado_unauthenticated.device_code = "test-device-code"
        tado_unauthenticated.device_verification_check_interval = 0
        tado_unauthenticated.device_verification_url_expires_at = None
        return tado_unauthenticated

    def test_success(self, tado_unauthenticated, mocked_responses):
        tado = self._prepare(tado_unauthenticated)
        mocked_responses.add(responses.POST, TOKEN_URL, json=_token_response(), status=200)

        assert tado.check_device_activation() is True
        assert tado.refresh_token == "new-refresh-token"

    def test_authorization_pending(self, tado_unauthenticated, mocked_responses):
        tado = self._prepare(tado_unauthenticated)
        mocked_responses.add(
            responses.POST, TOKEN_URL, json={"error": "authorization_pending"}, status=400
        )

        assert tado.check_device_activation() is False

    def test_expired_token_exits(self, tado_unauthenticated, mocked_responses):
        tado = self._prepare(tado_unauthenticated)
        mocked_responses.add(responses.POST, TOKEN_URL, json={"error": "expired_token"}, status=400)

        with pytest.raises(SystemExit):
            tado.check_device_activation()

    def test_generic_http_error_raises(self, tado_unauthenticated, mocked_responses):
        tado = self._prepare(tado_unauthenticated)
        mocked_responses.add(responses.POST, TOKEN_URL, json={"error": "server_error"}, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado.check_device_activation()


class TestDeviceActivation:
    def test_raises_when_not_started(self, tado_unauthenticated):
        tado_unauthenticated.device_activation_status = DeviceActivationStatus.NOT_STARTED

        with pytest.raises(Exception, match="not yet started"):
            tado_unauthenticated.device_activation()

    def test_polls_until_activated(self, tado_unauthenticated, mocked_responses):
        tado_unauthenticated.device_activation_status = DeviceActivationStatus.PENDING
        tado_unauthenticated.device_code = "test-device-code"
        tado_unauthenticated.device_verification_check_interval = 0
        tado_unauthenticated.device_verification_url_expires_at = None

        mocked_responses.add(
            responses.POST, TOKEN_URL, json={"error": "authorization_pending"}, status=400
        )
        mocked_responses.add(responses.POST, TOKEN_URL, json=_token_response(), status=200)
        mocked_responses.add(responses.GET, ME_URL, json={"homes": [{"id": 12345}]}, status=200)

        tado_unauthenticated.device_activation()

        assert tado_unauthenticated.device_activation_status == DeviceActivationStatus.COMPLETED
        assert tado_unauthenticated.id == 12345
        assert tado_unauthenticated.user_code is None
        assert tado_unauthenticated.device_verification_url is None


class TestOAuthTokenAndFileIO:
    def test_set_oauth_token(self, tado_unauthenticated):
        tado_unauthenticated.token_file_path = None

        refresh_token = tado_unauthenticated.set_oauth_token(_token_response())

        assert refresh_token == "new-refresh-token"
        assert tado_unauthenticated.refresh_token == "new-refresh-token"
        assert tado_unauthenticated.access_headers["Authorization"] == "Bearer test-access-token"

    def test_load_token_missing_file(self, tado_unauthenticated, tmp_path):
        token_file = tmp_path / "token.json"
        tado_unauthenticated.token_file_path = str(token_file)

        assert tado_unauthenticated.load_token() is True
        assert token_file.exists()
        assert tado_unauthenticated.refresh_token is None

    def test_load_token_empty_file(self, tado_unauthenticated, tmp_path):
        token_file = tmp_path / "token.json"
        token_file.write_text(json.dumps({}))
        tado_unauthenticated.token_file_path = str(token_file)

        assert tado_unauthenticated.load_token() is True
        assert tado_unauthenticated.refresh_token is None

    def test_load_token_existing_token(self, tado_unauthenticated, tmp_path):
        token_file = tmp_path / "token.json"
        token_file.write_text(json.dumps({"refresh_token": "stored-refresh-token"}))
        tado_unauthenticated.token_file_path = str(token_file)

        assert tado_unauthenticated.load_token() is True
        assert tado_unauthenticated.refresh_token == "stored-refresh-token"

    def test_load_token_no_file_path(self, tado_unauthenticated):
        tado_unauthenticated.token_file_path = None

        assert tado_unauthenticated.load_token() is False

    def test_save_token_no_token_file_path(self, tado_unauthenticated):
        tado_unauthenticated.token_file_path = None

        tado_unauthenticated.save_token()  # should not raise

    def test_save_token_no_refresh_token(self, tado_unauthenticated, tmp_path):
        token_file = tmp_path / "token.json"
        tado_unauthenticated.token_file_path = str(token_file)
        tado_unauthenticated.refresh_token = None

        tado_unauthenticated.save_token()

        assert not token_file.exists()

    def test_save_token_writes_refresh_token(self, tado_unauthenticated, tmp_path):
        token_file = tmp_path / "nested" / "token.json"
        tado_unauthenticated.token_file_path = str(token_file)
        tado_unauthenticated.refresh_token = "stored-refresh-token"

        tado_unauthenticated.save_token()

        assert json.loads(token_file.read_text()) == {"refresh_token": "stored-refresh-token"}
