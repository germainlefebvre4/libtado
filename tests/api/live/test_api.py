import os
from datetime import date
from dateutil.relativedelta import relativedelta
import pytest


pytestmark = pytest.mark.live

TADO_BRIDGE_AUTHKEY = os.getenv("TADO_BRIDGE_AUTHKEY", None)


class TestApi:
    def test_get_ratelimit_info(self, tado):
        rate_limit_info = tado.get_rate_limit_info()

        assert rate_limit_info.granted_calls >= 0
        assert rate_limit_info.remaining_calls is not None
        assert rate_limit_info.granted_calls_period_in_seconds == 86400
        assert rate_limit_info.ratelimit_resets_at_utc is None

    def test_get_zones(self, tado):
        response = tado.get_zones()

        assert isinstance(response, list)
        assert len(response) > 0
        assert response[0]["id"] == 1

    @pytest.mark.skipif(not TADO_BRIDGE_AUTHKEY, reason="TADO_BRIDGE_AUTHKEY not set")
    def test_get_boiler_state(self, tado):
        response = tado.get_boiler_state(TADO_BRIDGE_AUTHKEY)

        assert isinstance(response, dict)

        KEYS = ["state", "deviceWiredToBoiler", "hotWaterZonePresent", "boiler"]
        assert all(name in response for name in KEYS)
        assert isinstance(response["state"], str)
        assert isinstance(response["hotWaterZonePresent"], bool)
        KEYS = ["type", "serialNo", "thermInterfaceType", "connected", "lastRequestTimestamp"]
        assert all(name in response["deviceWiredToBoiler"] for name in KEYS)
        KEYS = ["celsius", "timestamp"]
        assert all(name in response["boiler"]["outputTemperature"] for name in KEYS)

    def test_get_capabilities(self, tado):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_capabilities(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_devices(self, tado):
        response = tado.get_devices()

        assert isinstance(response, list)

    def test_get_early_start(self, tado):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_early_start(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_home(self, tado):
        response = tado.get_home()

        assert isinstance(response, dict)

    def test_get_home_id(self, tado):
        response = tado.get_home_id()

        assert isinstance(response, int)

    def test_get_installations(self, tado):
        response = tado.get_installations()

        assert isinstance(response, list)

    def test_get_invitations(self, tado):
        response = tado.get_invitations()

        assert isinstance(response, list)

    def test_get_me(self, tado):
        response = tado.get_me()

        assert isinstance(response, dict)

    def test_get_mobile_devices(self, tado):
        response = tado.get_mobile_devices()

        assert isinstance(response, list)

    def test_get_schedule(self, tado):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_schedule(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_state(self, tado):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_state(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_users(self, tado):
        response = tado.get_users()

        assert isinstance(response, list)

    def test_get_weather(self, tado):
        response = tado.get_weather()

        assert isinstance(response, dict)

    # def test_set_early_start(self):
    #     response = tado.set_early_start()

    #     assert isinstance(response, dict)

    # def test_set_temperature(self):
    #     temp_current = tado.get_state(1)["setting"]["temperature"]["celsius"]
    #     tado.set_temperature(1, temp_current)
    #     temp_changed = tado.get_state(1)["setting"]["temperature"]["celsius"]

    #     assert temp_changed == temp_changed

    # def test_end_manual_control(self):
    #     response = tado.end_manual_control()

    #     assert isinstance(response, dict)

    def test_get_report(self, tado):
        ZONE_ID = tado.get_zones()[0]["id"]
        yesterday  = str(date.today() + relativedelta(days=-1))
        response = tado.get_report(ZONE_ID, yesterday)

        assert isinstance(response, dict)

    def test_get_air_comfort(self, tado):
        response = tado.get_air_comfort()

        assert isinstance(response, dict)

    def test_get_air_comfort_geoloc(self, tado):
        GEO_LATITUDE = 50.6312013
        GEO_LONGITUDE = 2.9070787
        response = tado.get_air_comfort_geoloc(GEO_LATITUDE, GEO_LONGITUDE)

        assert isinstance(response, dict)

    def test_set_cost_simulation(self, tado):
        monthYear = date.today().strftime("%Y-%m") # 2023-09
        country = "FRA"
        response = tado.get_consumption_overview(monthYear=monthYear, country=country)
        consumption_sum = sum([x["consumption"] for x in response["monthlyAggregation"]["requestedMonth"]["consumptionPerDate"]])

        if consumption_sum == 0:
            pytest.skip("not enough activity to test cost simulation")

        country = "FRA"
        payload = {
            "temperatureDeltaPerZone": [
                {
                    "zone": 1,
                    "setTemperatureDelta": -1
                },
                {
                    "zone": 1,
                    "setTemperatureDelta": -1
                },
                {
                    "zone": 1,
                    "setTemperatureDelta": -1
                },
                {
                    "zone": 1,
                    "setTemperatureDelta": -1
                }
            ]
        }
        response = tado.set_cost_simulation(country=country, ngsw_bypass=True, payload=payload)

        assert isinstance(response, dict)

    def test_get_consumption_overview(self, tado):
        # Get current datetime and convert to "YYYY-MM" format
        monthYear = date.today().strftime("%Y-%m") # 2023-09
        country = "FRA"
        response = tado.get_consumption_overview(monthYear=monthYear, country=country)

        assert isinstance(response, dict)

    def test_get_energy_settings(self, tado):
        response = tado.get_energy_settings()

        assert isinstance(response, dict)

    # def test_get_energy_insights(self):
    #     start_date = "2023-09-01"
    #     end_date = "2023-09-30"
    #     country = "FRA"
    #     response = tado.get_energy_insights(start_date=start_date, end_date=end_date, country=country)

    #     assert isinstance(response, dict)
