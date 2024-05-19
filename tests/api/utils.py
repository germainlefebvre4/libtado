import os
from datetime import date
from dateutil.relativedelta import relativedelta
from libtado.api import Tado

TADO_USERNAME = os.getenv("TADO_USERNAME", None)
TADO_PASSWORD = os.getenv("TADO_PASSWORD", None)
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET", None)

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)


class TestApi:
    def get_zones():
        response = tado.get_zones()
        return response

    def get_capabilities():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_capabilities(ZONE_ID)
        return response

    def get_devices():
        response = tado.get_devices()
        return response

    def get_early_start():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_early_start(ZONE_ID)
        return response

    def get_home():
        response = tado.get_home()
        return response

    def get_installations():
        response = tado.get_home()
        return response

    def get_invitations():
        response = tado.get_invitations()
        return response

    def get_me():
        response = tado.get_me()
        return response

    def get_mobile_devices():
        response = tado.get_mobile_devices()
        return response

    def get_schedule():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_schedule(ZONE_ID)
        return response

    def get_state():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_state(ZONE_ID)
        return response 

    def get_users():
        response = tado.get_users()
        return response

    def get_weather():
        response = tado.get_weather()
        return response

    def get_report():
        ZONE_ID = tado.get_zones()[0]["id"]
        yesterday  = str(date.today() + relativedelta(days=-1))
        response = tado.get_report(ZONE_ID, yesterday)
        return response

    def get_air_comfort():
        response = tado.get_air_comfort()
        return response

    def get_air_comfort_geoloc():
        GEO_LATITUDE = 50.6312013
        GEO_LONGITUDE = 2.9070787
        response = tado.get_air_comfort_geoloc(GEO_LATITUDE, GEO_LONGITUDE)
        return response

    def set_cost_simulation():
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
        return response

    def get_consumption_overview():
        # Get current datetime and convert to "YYYY-MM" format
        monthYear = date.today().strftime("%Y-%m") # 2023-09
        country = "FRA"
        response = tado.get_consumption_overview(monthYear=monthYear, country=country)
        return response

    def get_energy_settings():
        response = tado.get_energy_settings()
        return response

    def get_energy_insights():
        start_date = "2023-09-01"
        end_date = "2023-09-30"
        country = "FRA"
        response = tado.get_energy_insights(start_date=start_date, end_date=end_date, country=country)
        return response
