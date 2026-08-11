import json
import os

import pytest

from libtado.api import Tado


def _has_usable_credentials_file(path):
    if not path or not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    return bool(data.get("refresh_token"))


@pytest.fixture(scope="session")
def tado():
    refresh_token = os.environ.get("TADO_REFRESH_TOKEN", "")
    credentials_file = os.environ.get("TADO_CREDENTIALS_FILE")

    if not refresh_token and not _has_usable_credentials_file(credentials_file):
        pytest.skip("no Tado live credentials configured")

    client = Tado(refresh_token, credentials_file)
    if client.get_device_activation_status() == "PENDING":
        client.device_activation()

    return client
