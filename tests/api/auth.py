import os
from libtado.api import Tado

TADO_REFRESH_TOKEN = os.environ.get("TADO_REFRESH_TOKEN", "")
TADO_CREDENTIALS_FILE = os.environ.get("TADO_CREDENTIALS_FILE")
tado = Tado(TADO_REFRESH_TOKEN, TADO_CREDENTIALS_FILE)
status = tado.get_device_activation_status()
if status == "PENDING":
    tado.device_activation()
