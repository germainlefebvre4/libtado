import os
from datetime import date
from dateutil.relativedelta import relativedelta
from libtado.api import Tado

TADO_USERNAME = os.getenv("TADO_USERNAME", None)
TADO_PASSWORD = os.getenv("TADO_PASSWORD", None)
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET", None)

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)


class TestApi:
    def get_capabilities():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_capabilities(ZONE_ID)
        return response

    def get_devices():
        response = tado.get_devices()
        return response

    def get_device_usage():
        response = tado.get_device_usage()
        return response

    def get_early_start():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_early_start(ZONE_ID)
        return response

    def get_home():
        response = tado.get_home()
        return response

    def get_home_state():
        response = tado.get_home_state()
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

    def get_schedule_timetables():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_schedule_timetables(ZONE_ID)
        return response

    def get_schedule():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_schedule(ZONE_ID)
        return response

    def get_schedule_blocks():
        ZONE_ID = tado.get_zones()[0]["id"]
        SCHEDULE_ID = tado.get_schedule(ZONE_ID)["id"]
        response = tado.get_schedule_blocks(ZONE_ID, SCHEDULE_ID)
        return response

    def get_schedule_block_by_day_type():
        ZONE_ID = tado.get_zones()[1]["id"]
        # SCHEDULE = tado.get_schedule(ZONE_ID)
        SCHEDULE_ID = tado.get_schedule(ZONE_ID)["id"]
        SCHEDULE_BLOCK_DAY_TYPE = tado.get_schedule_blocks(ZONE_ID, SCHEDULE_ID)[0]["dayType"]
        response = tado.get_schedule_block_by_day_type(ZONE_ID, SCHEDULE_ID, SCHEDULE_BLOCK_DAY_TYPE)
        return response

    def get_state():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_state(ZONE_ID)
        return response

    def get_measuring_device():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_measuring_device(ZONE_ID)
        return response

    def get_default_overlay():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_default_overlay(ZONE_ID)
        return response

    def get_users():
        response = tado.get_users()
        return response

    def get_weather():
        response = tado.get_weather()
        return response

    def get_zones():
        response = tado.get_zones()
        return response

    def get_away_configuration():
        ZONE_ID = tado.get_zones()[0]["id"]
        response = tado.get_away_configuration(ZONE_ID)
        return response

    def get_report():
        ZONE_ID = tado.get_zones()[0]["id"]
        yesterday  = str(date.today() + relativedelta(days=-1))
        response = tado.get_report(ZONE_ID, yesterday)
        return response

    def get_heating_circuits():
        response = tado.get_heating_circuits()
        return response

    def get_incidents():
        response = tado.get_incidents()
        return response

    def get_installations():
        response = tado.get_home()
        return response

    def get_air_comfort():
        response = tado.get_air_comfort()
        return response

    def get_air_comfort_geoloc():
        GEO_LATITUDE = 50.6312013
        GEO_LONGITUDE = 2.9070787
        response = tado.get_air_comfort_geoloc(GEO_LATITUDE, GEO_LONGITUDE)
        return response

    def get_heating_system():
        response = tado.get_heating_system()
        return response

    def get_running_times():
        FROM_DATE = str(date.today() + relativedelta(days=-1))
        response = tado.get_running_times(FROM_DATE)
        return response

    def get_zone_states():
        response = tado.get_zone_states()
        return response

    # def get_energy_consumption():
    #     response = tado.get_energy_consumption()
    #     return response

    # def get_energy_savings():
    #     MONTH = date.today().strftime("%Y-%m")
    #     COUNTRY = "FRA"
    #     response = tado.get_energy_savings(MONTH, COUNTRY)
    #     return response

    def set_cost_simulation():
        country = "FRA"
        payload = {
            "temperatureDeltaPerZone": [{
                "zone": 6,
                "setTemperatureDelta": -1,
            }]
        }
        response = tado.set_cost_simulation(country=country, ngsw_bypass=True, payload=payload)
        return response

    def get_consumption_overview():
        monthYear = date.today().strftime("%Y-%m") # 2023-09
        country = "FRA"
        response = tado.get_consumption_overview(monthYear=monthYear, country=country)
        return response

    def get_consumption_details():
        monthYear = date.today().strftime("%Y-%m")
        response = tado.get_consumption_details(monthYear=monthYear)
        return response

    def get_energy_settings():
        response = tado.get_energy_settings()
        return response

    # def get_energy_insights():
    #     previous_month = date.today() + relativedelta(months=-1)
    #     first_day_previous_month = previous_month.replace(day=1)
    #     last_day_previous_month = previous_month.replace(day=28)
    #     start_date = f'{first_day_previous_month.strftime("%Y-%m-%d")}'
    #     end_date = f'{last_day_previous_month.strftime("%Y-%m-%d")}'
    #     country = "FRA"
    #     response = tado.get_energy_insights(start_date=start_date, end_date=end_date, country=country)
    #     return response
