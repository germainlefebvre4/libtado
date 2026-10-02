# FAQ

## Why variables `TADO_USERNAME` and `TADO_PASSWORD` are not working anymore?

Starting the 21st of March 2025, the Tado authentication workflow will definitely change to OAuth2 device code grant flow.

!!! info

    Here is the link to the official announcement: [Tado Support Article - How do I authenticate to access the REST API?](https://support.tado.com/en/articles/8565472-how-do-i-authenticate-to-access-the-rest-api)

The direction that Tado is taking is to enforce security and privacy by using OAuth2. This is a good thing, as it will prevent the need to store your username and password in plain text in your environment variables.
But the consequences of that change are that library handles differently the authentication process.

!!! warning

    Now, you have to use the `TADO_CREDENTIALS_FILE` or `TADO_REFRESH` variables to authenticate.

You can find more documentation on how to authenticate in the [**CLI Configuration**](./cli/configuration.md) section.

## Every operation fails with HTTP Error 429. Why is this happening?

If this happens, you've probably reached the API
[rate limit](https://help.tado.com/en/articles/12165739-limitation-for-rest-api-usage).
This is something which has been introduced by Tado in September 2025.

Libtado uses the REST API to get information from, and to control your Tado system.

If this happens, you'll have to wait for the rate limit to be reset.
This can take up to **24 hours**.

The limit will be higher, but not unlimited, if you have the Auto Assist / AI Assist subscription.

You can use the function [`get_rate_limit_info`](./api/reference.md#libtado.api.Tado.get_rate_limit_info) to see how many API calls you still have left.
