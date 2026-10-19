import pytest
import requests
import responses as responses_lib

from libtado.api import TadoAuthError, TadoError, TadoHTTPError, TadoRateLimitError
from libtado.exceptions import error_from_response


def _response(status, headers=None):
    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.GET, "https://example.test/x", status=status, headers=headers or {})
        return requests.get("https://example.test/x")


def test_success_maps_to_none():
    assert error_from_response(_response(200)) is None


@pytest.mark.parametrize("status", [400, 404, 500])
def test_http_error_mapping(status):
    resp = _response(status)
    err = error_from_response(resp)
    assert type(err) is TadoHTTPError
    assert isinstance(err, TadoError)
    assert isinstance(err, requests.exceptions.HTTPError)
    assert err.status_code == status
    assert err.response is resp
    with pytest.raises(requests.exceptions.HTTPError):
        raise err


def test_rate_limit_error_mapping():
    err = error_from_response(_response(429), retry_after=3600)
    assert isinstance(err, TadoRateLimitError)
    assert isinstance(err, TadoHTTPError)
    assert err.status_code == 429
    assert err.retry_after == 3600


def test_auth_error_is_tado_error():
    assert isinstance(TadoAuthError("x"), TadoError)
    assert not isinstance(TadoAuthError("x"), requests.exceptions.HTTPError)
