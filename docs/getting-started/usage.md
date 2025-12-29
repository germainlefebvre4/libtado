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

## Optional: Saving on API requests by specifying your Home ID

Each Tado account has a Home, which by itself has a unique ID. 
This number is needed to retrieve any details from your heating system.
It should never change, unless moving and setting up a new system on your account.

By default, libtado makes a request to the `/me` API to retrieve it. 
Up until September 2025, this was the preferred method, as the API had unlimited use, 
and this made it very easy to get started. 
But with the strict rate limits which Tado now has introduced, this can lead to unnecessary API calls.

If creating `tado.api()` objects often, such as in the CLI or commandline scripts,
you can avoid making this API call every time by retrieving your `home_id` once,
 then specifying it in the constructor of `libtado.api`:

```python
from libtado.api import Tado

t = Tado(token_file_path='/path/to/a/secure/folder/tado-credentials.json')
tado_home_id = t.get_home_id()
# store the value of tado_home_id somewhere, such as in a file, or hard-code it in your script.
```

In successive calls, pass home_id to `tado.api()`:

```python
from libtado.api import Tado
tado_home_id = 1234567 # previously returned value of t.get_home_id()
t = Tado(token_file_path='/path/to/a/secure/folder/tado-credentials.json', home_id=tado_home_id)
```

The library should now use this as your Home ID and not call the `/me` API to get it.
