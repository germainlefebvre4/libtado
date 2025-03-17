# Usage

After you installed libtado you can easily test it by using the included [`cli`](../cli/usage.md) like this:

``` { shell .copy }
tado --credentials-file /path/to/a/secure/folder/tado-credentials.json whoami
```

To use the library in your own code you can start with this:

``` python
import libtado.api
import webbrowser   # only needed for direct web browser access

t = tado.api(token_file_path='/path/to/a/secure/folder/tado-credentials.json')

status = t.get_device_activation_status()

if status == "PENDING":
    url = t.get_device_verification_url()

    # to auto-open the browser (on a desktop device), un-comment the following line:
    # webbrowser.open_new_tab(url)

    t.device_activation()

    status = t.get_device_activation_status()

if status == "COMPLETED":
    print("Login successful")
else:
    print(f"Login status is {status}")
```

Check out `all available API methods <api>` to learn what you can to with libtado.
