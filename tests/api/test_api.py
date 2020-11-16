import os
import requests
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from libtado.api import Tado

TADO_USERNAME = os.getenv("TADO_USERNAME", None)
TADO_PASSWORD = os.getenv("TADO_PASSWORD", None)
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET", None)

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)


class TestApi:
    def test_get_zones(self):
        response = tado.get_zones()

        assert isinstance(response, list)
        assert len(response) > 0

        KEYS = ["id", "name", "type", "dateCreated", "deviceTypes", "devices", "reportAvailable", "supportsDazzle", "dazzleEnabled", "dazzleMode", "openWindowDetection"]
        assert all(name in response[0] for name in KEYS)
        KEYS = ["deviceType", "serialNo", "shortSerialNo", "currentFwVersion", "connectionState", "characteristics", "batteryState", "duties"]
        assert all(name in response[0]["devices"][0] for name in KEYS)
        
        assert response[0]["id"] == 1

    def test_get_capabilities(self):
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

    def test_get_devices(self):
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

    def test_get_early_start(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_early_start(ZONE_ID)

        assert isinstance(response, dict)
        KEYS = ["enabled"]
        assert all(name in response for name in KEYS)

    def test_get_home(self):
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

    def get_installations(self):
        response = tado.get_home()

        assert isinstance(response, list)

    def test_get_invitations(self):
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

    def test_get_me(self):
        response = tado.get_me()

        assert isinstance(response, dict)
        KEYS = ["name", "email", "username", "id", "homes", "locale", "mobileDevices"]
        assert all(name in response for name in KEYS)

    def test_get_mobile_devices(self):
        response = tado.get_mobile_devices()

        assert isinstance(response, list)
        KEYS = ["name", "id", "settings", "location", "deviceMetadata"]
        assert all(name in response[0] for name in KEYS)
        KEYS = ["geoTrackingEnabled", "onDemandLogRetrievalEnabled", "pushNotifications"]
        assert all(name in response[0]["settings"] for name in KEYS)
        KEYS = ["stale", "atHome", "bearingFromHome", "relativeDistanceFromHomeFence"]
        assert all(name in response[0]["location"] for name in KEYS)
        KEYS = ["platform", "osVersion", "model", "locale"]
        assert all(name in response[0]["deviceMetadata"] for name in KEYS)

    def test_get_schedule(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_schedule(ZONE_ID)

        assert isinstance(response, dict)
        KEYS = ["id", "type"]
        assert all(name in response for name in KEYS)

    def test_get_state(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_state(ZONE_ID)

        assert isinstance(response, dict)
        KEYS = ["tadoMode", "geolocationOverride", "geolocationOverrideDisableTime", "preparation", "setting", "overlayType", "overlay", "openWindow", "nextScheduleChange", "nextTimeBlock", "link", "activityDataPoints", "sensorDataPoints"]
        assert all(name in response for name in KEYS)
        KEYS = ["type", "power", "temperature"]
        assert all(name in response["setting"] for name in KEYS)
        KEYS = ["start", "setting"]
        assert all(name in response["nextScheduleChange"] for name in KEYS)
        KEYS = ["start"]
        assert all(name in response["nextTimeBlock"] for name in KEYS)
        KEYS = ["heatingPower"]
        assert all(name in response["activityDataPoints"] for name in KEYS)
        KEYS = ["insideTemperature", "humidity"]
        assert all(name in response["sensorDataPoints"] for name in KEYS)

    def test_get_users(self):
        response = tado.get_users()

        assert isinstance(response, list)
        KEYS = ["name", "email", "username", "id", "homes", "locale", "mobileDevices"]
        assert all(name in response[0] for name in KEYS)

    def test_get_weather(self):
        response = tado.get_weather()

        assert isinstance(response, dict)
        KEYS = ["solarIntensity", "outsideTemperature", "weatherState"]
        assert all(name in response for name in KEYS)
        KEYS = ["type", "percentage", "timestamp"]
        assert all(name in response["solarIntensity"] for name in KEYS)
        KEYS = ["celsius", "fahrenheit", "timestamp", "type", "precision"]
        assert all(name in response["outsideTemperature"] for name in KEYS)
        KEYS = ["type", "value", "timestamp"]
        assert all(name in response["weatherState"] for name in KEYS)

    # def test_set_early_start(self):
    #     response = tado.set_early_start()

    #     # assert isinstance(response, dict)
    #     # KEYS = ["name", "email", "username", "id", "homes", "locale", "mobileDevices"]
    #     # assert all(name in response for name in KEYS)

    # def test_set_temperature(self):
    #     temp_current = tado.get_state(1)["setting"]["temperature"]["celsius"]
    #     tado.set_temperature(1, temp_current)
    #     temp_changed = tado.get_state(1)["setting"]["temperature"]["celsius"]
        
    #     assert temp_changed == temp_changed

    # def test_end_manual_control(self):
    #     response = tado.end_manual_control()

    #     # assert isinstance(response, dict)
    #     # KEYS = ["name", "email", "username", "id", "homes", "locale", "mobileDevices"]
    #     # assert all(name in response for name in KEYS)

    def test_get_report(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        yesterday  = str(date.today() + relativedelta(days=-1))
        response = tado.get_report(ZONE_ID, yesterday)

        assert isinstance(response, dict)
        KEYS = ["zoneType", "interval", "hoursInDay", "measuredData", "stripes", "settings", "callForHeat", "weather"]
        assert all(name in response for name in KEYS)
        
        KEYS = ["from", "to"]
        assert all(name in response["interval"] for name in KEYS)
        
        KEYS = ["measuringDeviceConnected", "insideTemperature", "humidity"]
        assert all(name in response["measuredData"] for name in KEYS)
        KEYS = ["timeSeriesType", "valueType", "dataIntervals"]
        assert all(name in response["measuredData"]["measuringDeviceConnected"] for name in KEYS)
        KEYS = ["from", "to", "value"]
        assert all(name in response["measuredData"]["measuringDeviceConnected"]["dataIntervals"][0] for name in KEYS)
        
        KEYS = ["timeSeriesType", "valueType", "dataIntervals"]
        assert all(name in response["stripes"] for name in KEYS)
        KEYS = ["from", "to", "value"]
        assert all(name in response["stripes"]["dataIntervals"][0] for name in KEYS)
        KEYS = ["stripeType", "setting"]
        assert all(name in response["stripes"]["dataIntervals"][0]["value"] for name in KEYS)
        KEYS = ["type", "power", "temperature"]
        assert all(name in response["stripes"]["dataIntervals"][0]["value"]["setting"] for name in KEYS)
        KEYS = ["celsius", "fahrenheit"]
        assert all(name in response["stripes"]["dataIntervals"][0]["value"]["setting"]["temperature"] for name in KEYS)
        
        KEYS = ["timeSeriesType", "valueType", "dataIntervals"]
        assert all(name in response["settings"] for name in KEYS)
        KEYS = ["from", "to", "value"]
        assert all(name in response["settings"]["dataIntervals"][0] for name in KEYS)
        KEYS = ["type", "power", "temperature"]
        assert all(name in response["settings"]["dataIntervals"][0]["value"] for name in KEYS)
        KEYS = ["celsius", "fahrenheit"]
        assert all(name in response["settings"]["dataIntervals"][0]["value"]["temperature"] for name in KEYS)
        
        KEYS = ["timeSeriesType", "valueType", "dataIntervals"]
        assert all(name in response["callForHeat"] for name in KEYS)
        
        KEYS = ["condition", "sunny", "slots"]
        assert all(name in response["weather"] for name in KEYS)
        KEYS = ["from", "to", "value"]
        assert all(name in response["weather"]["condition"]["dataIntervals"][0] for name in KEYS)
        KEYS = ["from", "to", "value"]
        assert all(name in response["weather"]["sunny"]["dataIntervals"][0] for name in KEYS)
        KEYS = ["from", "to", "value"]
        assert all(name in response["weather"]["sunny"]["dataIntervals"][0] for name in KEYS)
        KEYS = ["04:00", "08:00", "12:00", "16:00", "20:00"]
        assert all(name in response["weather"]["slots"]["slots"] for name in KEYS)
        KEYS = ["state", "temperature"]
        assert all(name in response["weather"]["slots"]["slots"]["04:00"] for name in KEYS)
        KEYS = ["celsius", "fahrenheit"]
        assert all(name in response["weather"]["slots"]["slots"]["04:00"]["temperature"] for name in KEYS)

    def test_get_air_comfort(self):
        response = tado.get_air_comfort()

        assert isinstance(response, dict)
        KEYS = ["freshness", "comfort"]
        assert all(name in response for name in KEYS)
        
        KEYS = ["value", "lastOpenWindow"]
        assert all(name in response["freshness"] for name in KEYS)
        
        KEYS = ["roomId", "temperatureLevel", "humidityLevel", "coordinate"]
        assert all(name in response["comfort"][0] for name in KEYS)
        KEYS = ["radial", "angular"]
        assert all(name in response["comfort"][0]["coordinate"] for name in KEYS)

    def test_get_air_comfort_geoloc(self):
        GEO_LATITUDE = 50.6312013
        GEO_LONGITUDE = 2.9070787
        response = tado.get_air_comfort_geoloc(GEO_LATITUDE, GEO_LONGITUDE)

        assert isinstance(response, dict)
        KEYS = ["roomMessages", "outdoorQuality"]
        assert all(name in response for name in KEYS)
        
        KEYS = ["roomId", "message", "visual", "link"]
        assert all(name in response["roomMessages"][0] for name in KEYS)
        
        KEYS = ["aqi", "pollens", "pollutants"]
        assert all(name in response["outdoorQuality"] for name in KEYS)
        KEYS = ["value", "level"]
        assert all(name in response["outdoorQuality"]["aqi"] for name in KEYS)
        
        KEYS = ["dominant", "types"]
        assert all(name in response["outdoorQuality"]["pollens"] for name in KEYS)
        KEYS = ["level"]
        assert all(name in response["outdoorQuality"]["pollens"]["dominant"] for name in KEYS)
        KEYS = ["localizedName", "type", "localizedDescription", "forecast"]
        assert all(name in response["outdoorQuality"]["pollens"]["types"][0] for name in KEYS)
        KEYS = ["localizedDay", "date", "level"]
        assert all(name in response["outdoorQuality"]["pollens"]["types"][0]["forecast"][0] for name in KEYS)
        
        KEYS = ["localizedName", "scientificName", "level", "concentration"]
        assert all(name in response["outdoorQuality"]["pollutants"][0] for name in KEYS)
        KEYS = ["value", "units"]
        assert all(name in response["outdoorQuality"]["pollutants"][0]["concentration"] for name in KEYS)
