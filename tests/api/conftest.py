from datetime import datetime, timedelta, timezone

import pytest
import responses as responses_lib

from libtado.api import Tado

HOME_ID = 12345
ACCESS_TOKEN = "test-access-token"
REFRESH_TOKEN = "test-refresh-token"


@pytest.fixture
def tado_unauthenticated():
    """A `Tado` instance built without performing any of `__init__`'s network I/O.

    `refresh_at` is set far in the future so `refresh_auth()` (called by every
    `_api_*_call` method) is a no-op.
    """
    instance = Tado.__new__(Tado)
    instance.id = HOME_ID
    instance.token_file_path = None
    instance.refresh_token = REFRESH_TOKEN
    instance.refresh_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    instance.access_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "User-Agent": "python/libtado",
    }
    return instance


@pytest.fixture
def mocked_responses():
    """An active `responses` mock registry for the duration of a test."""
    with responses_lib.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
