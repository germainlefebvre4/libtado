from libtado.api import Tado
import webbrowser

tado = Tado(token_file_path='/tmp/.libtado-refresh-token')
# OR: t = Tado(saved_refresh_token='my-refresh-token')

status = tado.get_device_activation_status()

if status == "PENDING":
    url = tado.get_device_verification_url()
    webbrowser.open_new_tab(url)
    tado.device_activation()
    status = tado.get_device_activation_status()

if status == "COMPLETED":
    print("Login successful")
else:
    print(f"Login status is {status}")

print(tado.get_me())
print(tado.get_home())
print(tado.get_zones())
print(tado.get_state(1))
