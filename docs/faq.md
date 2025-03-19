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
