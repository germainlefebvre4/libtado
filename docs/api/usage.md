# API Usage

Usage:

``` { .python .select .copy }
from libtado.api import Tado

api = Tado(token_file_path='/path/to/a/secure/folder/tado-credentials.json')
```

## Rate limiting

`Tado(..., max_retries=2, max_retry_wait=30)` controls how HTTP 429 responses
are handled. See the [FAQ](../faq.md) for details.

## Exceptions

All errors raised by libtado derive from `libtado.exceptions.TadoError`
(also importable from `libtado.api`):

```
TadoError
 +-- TadoAuthError       device login flow problems (started twice, code expired, ...)
 +-- TadoHTTPError       non-success HTTP status; has .status_code and .response
      +-- TadoRateLimitError   HTTP 429; has .retry_after (seconds or None)
```

`TadoHTTPError` is also a `requests.exceptions.HTTPError`.

``` python
from libtado.api import TadoError, TadoHTTPError

try:
    api.get_zones()
except TadoHTTPError as e:
    print(e.status_code)
except TadoError as e:
    print(e)
```

## Logging

libtado never prints. It logs through the standard `logging` module under the
`libtado` logger (silent unless you configure logging). Login progress is
logged at INFO, rate-limit retries and skipped schedule day types at WARNING:

``` python
import logging
logging.basicConfig(level=logging.INFO)
```

`set_schedule_blocks()` raises `ValueError` for a `schedule` other than 0, 1
or 2, and `set_schedule_block_by_day_type()` emits a `DeprecationWarning`.

For API Reference see [API Reference](../api/reference.md)
