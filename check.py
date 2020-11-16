import sys
import os
from libtado.api import Tado


TADO_USERNAME = os.getenv("TADO_USERNAME")
TADO_PASSWORD = os.getenv("TADO_PASSWORD")
TADO_CLIENT_SECRET = os.getenv("TADO_CLIENT_SECRET")

tado = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_CLIENT_SECRET)

# print(tado.get_me())
# print(tado.get_home())
# print(tado.get_zones())
# print(tado.get_state(1))
# print(tado.get_mobile_devices())


res = tado.get_air_comfort_geoloc(50.6312013,2.9070787)
print(res)
print()
# print(list(res.keys()))
# print(list(res["outdoorQuality"].keys()))
# print([ {x: type(res["outdoorQuality"]["pollens"][x])} for x in res["outdoorQuality"]["pollens"]])
# print([ {x: type(res["outdoorQuality"]["pollens"]["dominant"][x])} for x in res["outdoorQuality"]["pollens"]["dominant"]])
# print([ {x: type(res["outdoorQuality"]["pollens"]["types"][0][x])} for x in res["outdoorQuality"]["pollens"]["types"][0]])
# print([ {x: type(res["outdoorQuality"]["pollens"]["types"][0]["forecast"][0][x])} for x in res["outdoorQuality"]["pollens"]["types"][0]["forecast"][0]])
print([ {x: type(res["outdoorQuality"]["pollutants"][0][x])} for x in res["outdoorQuality"]["pollutants"][0]])
print([ {x: type(res["outdoorQuality"]["pollutants"][0]["concentration"][x])} for x in res["outdoorQuality"]["pollutants"][0]["concentration"]])

