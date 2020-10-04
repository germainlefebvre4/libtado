import sys
from libtado.api import Tado

t = Tado(sys.argv[1], sys.argv[2], sys.argv[3])

print(t.get_me())
# print(t.get_home())
# print(t.get_installations())
# print(t.get_invitations())
# print(t.get_report(1, "2020-10-04"))
# print(t.get_schedule(1))
# print(t.get_state(1))
print(t.get_users())
# print(t.get_weather())
# print(t.get_mobile_devices())
# print(t.get_zones())
