import os
from libtado.api import Tado

from dotenv import load_dotenv
load_dotenv()


TADO_USERNAME = os.environ["TADO_USERNAME"]
TADO_PASSWORD = os.environ["TADO_PASSWORD"]
TADO_CLIENT_SECRET = os.environ["TADO_CLIENT_SECRET"]

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)

# print(tado.get_me())
# print(tado.get_home())
# print(tado.get_invitations())
# print(tado.get_zones())
# print(tado.get_installations())
# print(tado.get_state(1))
# print(tado.get_mobile_devices())
# print(tado.get_report(1, "2023-12-12"))
# print(tado.get_energy_consumption("2022-09-01", "2022-09-30", "FRA", True))
# print(tado.get_energy_savings("2022-09", "FRA"))
# print(tado.get_consumption_overview("2023-09", "FRA", True))
# print(tado.get_enery_settings())
# print(tado.get_energy_insights("2023-09-01", "2023-09-30", "FRA", True))
# print(tado.get_schedule_blocks(1, 1))
# print(tado.get_schedule_block_by_day_type(1, 1, "MONDAY_TO_FRIDAY"))
print(tado.end_manual_control(1))
# print(tado.refresh_auth())
print(tado.set_away_configuration(6, "HEATING", "MEDIUM", 16))
