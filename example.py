from libtado.api import Tado
import webbrowser   # only needed for direct web browser access

t = Tado(token_file_path='/tmp/.libtado-refresh-token')
# OR: t = Tado(saved_refresh_token='my-refresh-token')

status = t.get_device_activation_status()

if status == "PENDING":
    url = t.get_device_verification_url()

    # to auto-open the browser (on a desktop device), un-comment the following line:
    webbrowser.open_new_tab(url)

    t.device_activation()

    status = t.get_device_activation_status()

if status == "COMPLETED":
    print("Login successful")
else:
    print(f"Login status is {status}")

print(t.get_me())
print(t.get_home())
print(t.get_zones())
print(t.get_state(1))
