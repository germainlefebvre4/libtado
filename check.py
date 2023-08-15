import os
from libtado.api import Tado

from dotenv import load_dotenv
load_dotenv()


TADO_USERNAME = os.environ["TADO_USERNAME"]
TADO_PASSWORD = os.environ["TADO_PASSWORD"]
TADO_CLIENT_SECRET = os.environ["TADO_CLIENT_SECRET"]

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)

# print(tado.get_me())
print(tado.get_home())
print(tado.get_invitations())
# print(tado.get_zones())
# print(tado.get_state(1))
# print(tado.get_mobile_devices())
# print(tado.get_energy_consumption("2022-09-01", "2022-09-30", "FRA", True))
# print(tado.get_energy_savings("2022-09", "FRA"))
