import os
from datetime import date
from dateutil.relativedelta import relativedelta
from libtado.api import Tado
from tests.api import utils
import pytest

TADO_REFRESH_TOKEN = os.environ["TADO_REFRESH_TOKEN"]
TADO_CREDENTIALS_FILE = os.environ["TADO_CREDENTIALS_FILE"]
tado = Tado(TADO_REFRESH_TOKEN, TADO_CREDENTIALS_FILE)
status = tado.get_device_activation_status()
if status == "PENDING":
    tado.device_activation()
