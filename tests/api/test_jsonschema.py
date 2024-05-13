import os
from libtado.api import Tado
import json
from pathlib import Path
from jsonschema import validate
from datetime import date

TADO_USERNAME = os.getenv("TADO_USERNAME", None)
TADO_PASSWORD = os.getenv("TADO_PASSWORD", None)
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET", None)

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)


def test_package_json_is_valid():
    monthYear = date.today().strftime("%Y-%m") # 2023-09
    country = "FRA"
    response = tado.get_consumption_overview(monthYear=monthYear, country=country)

    schema = json.loads(Path("schemas/consumptionOverview.json").read_text())
    assert validate(instance=response, schema=schema)


def test_unittest_json_is_valid():
    response = {
        "unit": "kWh",
    }

    schema = json.loads(Path("schemas/test.json").read_text())
    validate(instance=response, schema=schema)
