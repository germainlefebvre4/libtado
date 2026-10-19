---
hide:
  - navigation
---
# Authentication

The device login flow no longer prints to the terminal or exits the process.
After construction, check the status and show the URL yourself:

``` python
from libtado.api import Tado

api = Tado(token_file_path="tado-credentials.json")
if api.get_device_activation_status() == "PENDING":
    print("Log in at:", api.get_device_verification_url())
    api.device_activation()
```

The same URL is logged at INFO on the `libtado` logger. Flow problems (started
twice, not started, expired code) raise `TadoAuthError`.

::: libtado.api.Tado
    options:
      members:
        - __init__
        - login_device_flow
        - check_device_activation
        - device_activation
        - device_ready
        - refresh_auth
        - save_token
        - load_token
        - set_oauth_token
        - get_device_activation_status
        - get_device_verification_url
        - get_rate_limit_info
