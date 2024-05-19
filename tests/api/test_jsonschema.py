import os
from libtado.api import Tado
import json
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError
from datetime import date
import pytest
from tests.api import utils

TADO_USERNAME = os.getenv("TADO_USERNAME", None)
TADO_PASSWORD = os.getenv("TADO_PASSWORD", None)
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET", None)

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)


def test_jsonschema_get_air_comfort_geoloc_is_valid():
    with open("schemas/get_air_comfort_geoloc.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_air_comfort_geoloc()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_air_comfort_is_valid():
    with open("schemas/get_air_comfort.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_air_comfort()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_capabilities_is_valid():
    with open("schemas/get_capabilities.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_capabilities()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_consumption_overview_is_valid():
    with open("schemas/get_consumption_overview.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_consumption_overview()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_devices_is_valid():
    with open("schemas/get_devices.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_devices()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_early_start_is_valid():
    with open("schemas/get_early_start.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_early_start()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_energy_insights_is_valid():
    with open("schemas/get_energy_insights.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_energy_insights()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_energy_settings_is_valid():
    with open("schemas/get_energy_settings.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_energy_settings()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_home_is_valid():
    with open("schemas/get_home.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_home()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_installations_is_valid():
    with open("schemas/get_installations.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_installations()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_invitations_is_valid():
    with open("schemas/get_invitations.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_invitations()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_me_is_valid():
    with open("schemas/get_me.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_me()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_mobile_devices_is_valid():
    with open("schemas/get_mobile_devices.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_mobile_devices()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_report_is_valid():
    with open("schemas/get_report.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_report()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_schedule_is_valid():
    with open("schemas/get_schedule.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_schedule()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_state_is_valid():
    with open("schemas/get_state.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_state()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_users_is_valid():
    with open("schemas/get_users.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_users()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_weather_is_valid():
    with open("schemas/get_weather.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_weather()
    assert validate(instance=res, schema=schema) == None

def test_jsonschema_get_zones_is_valid():
    with open("schemas/get_zones.json", "r") as file:
        schema = json.load(file)
    res = utils.TestApi.get_zones()
    assert validate(instance=res, schema=schema) == None
