import os
from datetime import date
from dateutil.relativedelta import relativedelta
from libtado.api import Tado
from tests.api import utils
import pytest

TADO_REFRESH_TOKEN = os.environ["TADO_REFRESH_TOKEN"]
TADO_CREDENTIALS_FILE = os.environ["TADO_CREDENTIALS_FILE"]
tado = Tado(TADO_REFRESH_TOKEN, TADO_CREDENTIALS_FILE)

tado.device_activation()


class TestApi:
    def test_get_zones(self):
        response = utils.TestApi.get_zones()

        assert isinstance(response, list)
        assert len(response) > 0
        assert response[0]["id"] == 1

    def test_get_capabilities(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_capabilities(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_devices(self):
        response = tado.get_devices()

        assert isinstance(response, list)

    def test_get_early_start(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_early_start(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_home(self):
        response = tado.get_home()

        assert isinstance(response, dict)

    def get_installations(self):
        response = tado.get_home()

        assert isinstance(response, list)

    def test_get_invitations(self):
        response = tado.get_invitations()

        assert isinstance(response, list)

    def test_get_me(self):
        response = tado.get_me()

        assert isinstance(response, dict)

    def test_get_mobile_devices(self):
        response = tado.get_mobile_devices()

        assert isinstance(response, list)

    def test_get_schedule(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_schedule(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_state(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_state(ZONE_ID)

        assert isinstance(response, dict)

    def test_get_users(self):
        response = tado.get_users()

        assert isinstance(response, list)

    def test_get_weather(self):
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

    def test_get_report(self):
        ZONE_ID = tado.get_zones()[0]["id"]
        yesterday  = str(date.today() + relativedelta(days=-1))
        response = tado.get_report(ZONE_ID, yesterday)

        assert isinstance(response, dict)

    def test_get_air_comfort(self):
        response = tado.get_air_comfort()

        assert isinstance(response, dict)

    def test_get_air_comfort_geoloc(self):
        GEO_LATITUDE = 50.6312013
        GEO_LONGITUDE = 2.9070787
        response = tado.get_air_comfort_geoloc(GEO_LATITUDE, GEO_LONGITUDE)

        assert isinstance(response, dict)

    def test_set_cost_simulation(self):
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

    def test_get_consumption_overview(self):
        # Get current datetime and convert to "YYYY-MM" format
        monthYear = date.today().strftime("%Y-%m") # 2023-09
        country = "FRA"
        response = tado.get_consumption_overview(monthYear=monthYear, country=country)

        assert isinstance(response, dict)

    def test_get_energy_settings(self):
        response = tado.get_energy_settings()

        assert isinstance(response, dict)

    # def test_get_energy_insights(self):
    #     start_date = "2023-09-01"
    #     end_date = "2023-09-30"
    #     country = "FRA"
    #     response = tado.get_energy_insights(start_date=start_date, end_date=end_date, country=country)

    #     assert isinstance(response, dict)
