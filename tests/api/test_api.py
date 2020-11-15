import os
import requests
from libtado.api import Tado

TADO_USERNAME = os.getenv("TADO_USERNAME", None)
TADO_PASSWORD = os.getenv("TADO_PASSWORD", None)
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET", None)

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)


# def test_set_temperature():
#     temp_current = tado.get_state(1)["setting"]["temperature"]["celsius"]
#     tado.set_temperature(1, temp_current)
#     temp_changed = tado.get_state(1)["setting"]["temperature"]["celsius"]
    
#     assert temp_changed == temp_changed

def test_get_zones():
    response = tado.get_zones()

    assert isinstance(response, list)
    assert len(response) > 0

    KEYS = ["id", "name", "type", "dateCreated", "deviceTypes", "devices", "reportAvailable", "supportsDazzle", "dazzleEnabled", "dazzleMode", "openWindowDetection"]
    assert all(name in response[0] for name in KEYS)
    KEYS = ["deviceType", "serialNo", "shortSerialNo", "currentFwVersion", "connectionState", "characteristics", "batteryState", "duties"]
    assert all(name in response[0]["devices"][0] for name in KEYS)
    
    assert response[0]["id"] == 1

def test_get_capabilities():
    ZONE_ID = tado.get_zones()[0]["id"]
    response = tado.get_capabilities(ZONE_ID)

    assert isinstance(response, dict)
    
    KEYS = ["type", "temperatures"]
    assert all(name in response for name in KEYS)
    KEYS = ["celsius", "fahrenheit"]
    assert all(name in response["temperatures"] for name in KEYS)
    KEYS = ["min", "max", "step"]
    assert all(name in response["temperatures"]["celsius"] for name in KEYS)
    assert all(name in response["temperatures"]["fahrenheit"] for name in KEYS)

def test_get_devices():
    response = tado.get_devices()

    assert isinstance(response, list)
    assert len(response) > 0
    
    DEVICES_BU = [x for x in response if x["deviceType"] == "BU01"]
    KEYS = ["deviceType", "serialNo", "shortSerialNo", "currentFwVersion", "connectionState", "characteristics", "isDriverConfigured"]
    assert all(name in DEVICES_BU[0] for name in KEYS)
    KEYS = ["value", "timestamp"]
    assert all(name in DEVICES_BU[0]["connectionState"] for name in KEYS)
    KEYS = ["capabilities"]
    assert all(name in DEVICES_BU[0]["characteristics"] for name in KEYS)

    DEVICES_GW = [x for x in response if x["deviceType"] == "GW03"]
    KEYS = ["deviceType", "serialNo", "shortSerialNo", "currentFwVersion", "connectionState", "characteristics", "inPairingMode"]
    assert all(name in DEVICES_GW[0] for name in KEYS)
    KEYS = ["value", "timestamp"]
    assert all(name in DEVICES_GW[0]["connectionState"] for name in KEYS)
    KEYS = ["capabilities"]
    assert all(name in DEVICES_GW[0]["characteristics"] for name in KEYS)

    DEVICES_RU = [x for x in response if x["deviceType"] == "RU01"]
    KEYS = ["deviceType", "serialNo", "shortSerialNo", "currentFwVersion", "connectionState", "characteristics", "batteryState"]
    assert all(name in DEVICES_RU[0] for name in KEYS)
    KEYS = ["value", "timestamp"]
    assert all(name in DEVICES_RU[0]["connectionState"] for name in KEYS)
    KEYS = ["capabilities"]
    assert all(name in DEVICES_RU[0]["characteristics"] for name in KEYS)

    DEVICES_VA = [x for x in response if x["deviceType"] == "VA01"]
    KEYS = ["deviceType", "serialNo", "shortSerialNo", "currentFwVersion", "connectionState", "characteristics", "mountingState", "batteryState"]
    assert all(name in DEVICES_VA[0] for name in KEYS)
    KEYS = ["value", "timestamp"]
    assert all(name in DEVICES_VA[0]["connectionState"] for name in KEYS)
    KEYS = ["capabilities"]
    assert all(name in DEVICES_VA[0]["characteristics"] for name in KEYS)
    KEYS = ["value", "timestamp"]
    assert all(name in DEVICES_VA[0]["mountingState"] for name in KEYS)

def test_get_early_start():
    ZONE_ID = tado.get_zones()[0]["id"]
    response = tado.get_early_start(ZONE_ID)

    assert isinstance(response, dict)
    KEYS = ["enabled"]
    assert all(name in response for name in KEYS)

def test_get_home():
    response = tado.get_home()

    assert isinstance(response, dict)
    KEYS = ["id", "name", "dateTimeZone", "dateCreated", "temperatureUnit", "partner", "simpleSmartScheduleEnabled", "awayRadiusInMeters", "installationCompleted", "incidentDetection", "autoAssistFreeTrialEnabled", "usePreSkillsApps", "skills", "christmasModeEnabled", "showAutoAssistReminders", "contactDetails", "address", "geolocation", "consentGrantSkippable"]
    assert all(name in response for name in KEYS)
    KEYS = ["name", "email", "phone"]
    assert all(name in response["contactDetails"] for name in KEYS)
    KEYS = ["addressLine1", "addressLine2", "zipCode", "city", "state", "country"]
    assert all(name in response["address"] for name in KEYS)
    KEYS = ["latitude", "longitude"]
    assert all(name in response["geolocation"] for name in KEYS)

def get_installations():
    response = tado.get_home()

    assert isinstance(response, list)

def test_get_invitations():
    response = tado.get_invitations()

    assert isinstance(response, list)
    KEYS = ["token", "email", "firstSent", "lastSent", "inviter", "home"]
    assert all(name in response[0] for name in KEYS)
    KEYS = ["id", "name", "dateTimeZone", "dateCreated", "temperatureUnit", "partner", "simpleSmartScheduleEnabled", "awayRadiusInMeters", "installationCompleted", "incidentDetection", "autoAssistFreeTrialEnabled", "usePreSkillsApps", "skills", "christmasModeEnabled", "showAutoAssistReminders", "contactDetails", "address", "geolocation", "consentGrantSkippable"]
    assert all(name in response[0]["home"] for name in KEYS)
    KEYS = ["supported", "enabled"]
    assert all(name in response[0]["home"]["incidentDetection"] for name in KEYS)
    KEYS = ["name", "email", "phone"]
    assert all(name in response[0]["home"]["contactDetails"] for name in KEYS)
    KEYS = ["latitude", "longitude"]
    assert all(name in response[0]["home"]["geolocation"] for name in KEYS)

def test_get_me():
    response = tado.get_me()

    assert isinstance(response, dict)
    KEYS = ["name", "email", "username", "id", "homes", "locale", "mobileDevices"]
    assert all(name in response for name in KEYS)
