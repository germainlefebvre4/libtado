# Usage

After you installed libtado you can easily test it by using the included [`cli`](../cli/usage.md) like this:

``` { shell .copy }
tado --username USERNAME --password PASSWORD whoami
```

To use the library in your own code you can start with this:

``` python
import tado.api
t = tado.api('Username', 'Password')
print(t.get_me())
```

Check out `all available API methods <api>` to learn what you can to with libtado.
