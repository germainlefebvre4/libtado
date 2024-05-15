import os
from libtado.api import Tado
import json
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError
from datetime import date
import pytest

TADO_USERNAME = os.getenv("TADO_USERNAME", None)
TADO_PASSWORD = os.getenv("TADO_PASSWORD", None)
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET", None)

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)


def test_jsonschema_consumptionOverview_is_valid():
    monthYear = date.today().strftime("%Y-%m") # 2023-09
    country = "FRA"
    response = tado.get_consumption_overview(monthYear=monthYear, country=country)

    schema = json.loads(Path("schemas/consumptionOverview.jsonschema").read_text())
    
    assert validate(instance=response, schema=schema) == None


def test_jsonschema_consumptionOverview_is_invalid():
    monthYear = date.today().strftime("%Y-%m") # 2023-09
    country = "FRA"
    response = tado.get_consumption_overview(monthYear=monthYear, country=country)

    schema = json.loads(Path("schemas/fake_schema.jsonschema").read_text())

    with pytest.raises(ValidationError) as e:
        validate(instance=response, schema=schema)
