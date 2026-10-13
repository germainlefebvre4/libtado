import json
import logging
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import pytest
import requests
import responses

from libtado.api import (
    DeviceActivationStatus,
    Tado,
    TadoHTTPError,
    TadoRateLimitError,
    _parse_retry_wait,
)

HOME_ID = 12345

API = "https://my.tado.com/api/v2"
ACME = "https://acme.tado.com/v1"
MINDER = "https://minder.tado.com/v1"
INSIGHTS = "https://energy-insights.tado.com/api"
BOB = "https://energy-bob.tado.com"

ZONES = f"{API}/homes/{HOME_ID}/zones"
RL_HEADERS = {"ratelimit-policy": '"perday";q=100;w=86400', "ratelimit": '"perday";r=42'}


@pytest.fixture
def sleeps(monkeypatch):
    calls = []
    monkeypatch.setattr("libtado.api.time.sleep", calls.append)
    return calls


class TestSession:
    def test_calls_share_one_session(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.GET, ZONES, json=[], status=200)
        tado_unauthenticated.get_zones()
        session = tado_unauthenticated._http_session
        tado_unauthenticated.get_zones()
        assert session is not None
        assert tado_unauthenticated._http_session is session

    def test_two_instances_do_not_share_session(self, tado_unauthenticated):
        other = Tado.__new__(Tado)
        assert tado_unauthenticated._get_session() is not other._get_session()
        assert Tado._http_session is None


class TestUniformHosts:
    @pytest.mark.parametrize("base", [API, ACME, MINDER, INSIGHTS, BOB])
    def test_rate_limit_headers_and_errors(self, tado_unauthenticated, mocked_responses, base):
        call = getattr(tado_unauthenticated, {
            API: "_api_call", ACME: "_api_acme_call", MINDER: "_api_minder_call",
            INSIGHTS: "_api_energy_insights_call", BOB: "_api_energy_bob_call",
        }[base])
        mocked_responses.add(responses.GET, f"{base}/ok", json={"a": 1}, headers=RL_HEADERS)
        mocked_responses.add(responses.GET, f"{base}/missing", status=404)
        mocked_responses.add(responses.DELETE, f"{base}/gone", status=204)
        mocked_responses.add(responses.POST, f"{base}/made", status=204)

        assert call("ok") == {"a": 1}
        assert tado_unauthenticated.get_rate_limit_info().remaining_calls == 42
        with pytest.raises(TadoHTTPError) as exc:
            call("missing")
        assert exc.value.status_code == 404
        assert call("gone", method="DELETE") is None
        assert call("made", data={"x": 1}, method="POST") is None

    def test_put_without_data_sends_nothing(self, tado_unauthenticated, mocked_responses, caplog):
        with caplog.at_level(logging.WARNING, logger="libtado"):
            assert tado_unauthenticated._api_call("x", data=None, method="PUT") is None
        assert len(mocked_responses.calls) == 0
        assert "nothing was sent" in caplog.text


class TestParseRetryWait:
    def test_ratelimit_t(self):
        assert _parse_retry_wait({"ratelimit": '"perday";r=0;t=123'}) == 123

    def test_retry_after_seconds(self):
        assert _parse_retry_wait({"Retry-After": "7"}) == 7

    def test_retry_after_http_date(self):
        date = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=20), usegmt=True)
        assert 15 <= _parse_retry_wait({"Retry-After": date}) <= 20

    def test_ratelimit_wins_over_retry_after(self):
        assert _parse_retry_wait({"ratelimit": '"perday";r=0;t=5', "Retry-After": "99"}) == 5

    @pytest.mark.parametrize("headers", [{}, {"Retry-After": "soon"}, {"ratelimit": '"perday";r=3'}])
    def test_unusable(self, headers):
        assert _parse_retry_wait(headers) is None


class TestRetry:
    def test_429_then_200(self, tado_unauthenticated, mocked_responses, sleeps):
        mocked_responses.add(responses.GET, ZONES, status=429, headers={"Retry-After": "2"})
        mocked_responses.add(responses.GET, ZONES, json=[{"id": 1}], status=200)
        assert tado_unauthenticated.get_zones() == [{"id": 1}]
        assert sleeps == [2]

    def test_wait_from_ratelimit_header(self, tado_unauthenticated, mocked_responses, sleeps):
        mocked_responses.add(responses.GET, ZONES, status=429, headers={"ratelimit": '"perday";r=0;t=4'})
        mocked_responses.add(responses.GET, ZONES, json=[], status=200)
        tado_unauthenticated.get_zones()
        assert sleeps == [4]

    def test_http_date_fallback(self, tado_unauthenticated, mocked_responses, sleeps):
        date = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=10), usegmt=True)
        mocked_responses.add(responses.GET, ZONES, status=429, headers={"Retry-After": date})
        mocked_responses.add(responses.GET, ZONES, json=[], status=200)
        tado_unauthenticated.get_zones()
        assert len(sleeps) == 1 and 5 <= sleeps[0] <= 10

    def test_rate_limit_info_updated_by_429(self, tado_unauthenticated, mocked_responses, sleeps):
        mocked_responses.add(responses.GET, ZONES, status=429, headers={
            "ratelimit-policy": '"perday";q=100;w=86400', "ratelimit": '"perday";r=0;t=86400'})
        with pytest.raises(TadoRateLimitError):
            tado_unauthenticated.get_zones()
        info = tado_unauthenticated.get_rate_limit_info()
        assert info.remaining_calls == 0 and info.granted_calls == 100

    def test_retries_exhausted(self, tado_unauthenticated, mocked_responses, sleeps):
        mocked_responses.add(responses.GET, ZONES, status=429, headers={"Retry-After": "1"})
        with pytest.raises(TadoRateLimitError) as exc:
            tado_unauthenticated.get_zones()
        assert exc.value.retry_after == 1
        assert len(mocked_responses.calls) == 3  # 1 + max_retries(2)
        assert sleeps == [1, 1]

    def test_long_wait_fails_fast(self, tado_unauthenticated, mocked_responses, sleeps):
        mocked_responses.add(responses.GET, ZONES, status=429, headers={"Retry-After": "3600"})
        with pytest.raises(TadoRateLimitError) as exc:
            tado_unauthenticated.get_zones()
        assert exc.value.retry_after == 3600
        assert sleeps == [] and len(mocked_responses.calls) == 1

    def test_no_wait_info_fails_fast(self, tado_unauthenticated, mocked_responses, sleeps):
        mocked_responses.add(responses.GET, ZONES, status=429)
        with pytest.raises(TadoRateLimitError) as exc:
            tado_unauthenticated.get_zones()
        assert exc.value.retry_after is None
        assert sleeps == [] and len(mocked_responses.calls) == 1

    def test_max_retries_zero(self, tado_unauthenticated, mocked_responses, sleeps):
        tado_unauthenticated.max_retries = 0
        mocked_responses.add(responses.GET, ZONES, status=429, headers={"Retry-After": "1"})
        with pytest.raises(TadoRateLimitError):
            tado_unauthenticated.get_zones()
        assert sleeps == [] and len(mocked_responses.calls) == 1

    def test_constructor_options(self, mocked_responses):
        mocked_responses.add(responses.POST, "https://login.tado.com/oauth2/token", json={
            "access_token": "a", "expires_in": 599, "refresh_token": "r"})
        tado = Tado("tok", home_id=1, max_retries=0, max_retry_wait=5)
        assert (tado.max_retries, tado.max_retry_wait) == (0, 5)
        assert Tado.__new__(Tado).max_retries == 2

    def test_500_sent_once(self, tado_unauthenticated, mocked_responses, sleeps):
        mocked_responses.add(responses.GET, ZONES, status=500)
        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_zones()
        assert len(mocked_responses.calls) == 1 and sleeps == []

    def test_throttled_put_replays_body(self, tado_unauthenticated, mocked_responses, sleeps):
        url = f"{API}/homes/{HOME_ID}/zones/1/x"
        mocked_responses.add(responses.PUT, url, status=429, headers={"Retry-After": "1"})
        mocked_responses.add(responses.PUT, url, json={"ok": True}, status=200)
        assert tado_unauthenticated._api_call("homes/%i/zones/1/x" % HOME_ID, {"a": 1}, "PUT") == {"ok": True}
        bodies = [json.loads(c.request.body) for c in mocked_responses.calls]
        assert bodies == [{"a": 1}, {"a": 1}]

    def test_retry_logs_warning_and_stdout_silent(self, tado_unauthenticated, mocked_responses, sleeps, caplog, capsys):
        mocked_responses.add(responses.GET, ZONES, status=429, headers={"Retry-After": "1"})
        mocked_responses.add(responses.GET, ZONES, json=[], status=200)
        with caplog.at_level(logging.WARNING, logger="libtado"):
            tado_unauthenticated.get_zones()
        assert any(r.levelno == logging.WARNING and "retrying" in r.message for r in caplog.records)
        assert capsys.readouterr().out == ""


class TestLoggingAndWarnings:
    def test_device_flow_logs_url_not_stdout(self, mocked_responses, caplog, capsys):
        mocked_responses.add(responses.POST, "https://login.tado.com/oauth2/device_authorize", json={
            "device_code": "d", "user_code": "ABC", "verification_uri": "https://login.tado.com/device",
            "expires_in": 300, "interval": 0})
        tado = Tado.__new__(Tado)
        with caplog.at_level(logging.INFO, logger="libtado"):
            assert tado.login_device_flow() == DeviceActivationStatus.PENDING
        assert "https://login.tado.com/device?user_code=ABC" in caplog.text
        assert tado.get_device_verification_url() == "https://login.tado.com/device?user_code=ABC"
        assert capsys.readouterr().out == ""

    def test_inapplicable_day_types_warning(self, tado_unauthenticated, mocked_responses, caplog):
        mocked_responses.add(responses.PUT, f"{API}/homes/{HOME_ID}/zones/1/schedule/timetables/0/blocks/MONDAY_TO_SUNDAY", json={})
        blocks = [{"dayType": "MONDAY_TO_SUNDAY"}, {"dayType": "SATURDAY"}]
        with caplog.at_level(logging.WARNING, logger="libtado"):
            tado_unauthenticated.set_schedule_blocks(1, 0, blocks)
        assert "SATURDAY" in caplog.text

    def test_deprecated_setter_warns(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.PUT, f"{API}/homes/{HOME_ID}/zones/1/schedule/timetables/0/blocks/MONDAY_TO_SUNDAY", json={})
        with pytest.warns(DeprecationWarning):
            tado_unauthenticated.set_schedule_block_by_day_type(1, 0, "MONDAY_TO_SUNDAY", [{"dayType": "MONDAY_TO_SUNDAY"}])
