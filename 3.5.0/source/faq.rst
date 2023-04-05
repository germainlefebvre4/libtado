.. _faq:

==========================
Frequently Asked Questions
==========================

*********************************
How to retrieve the client secret
*********************************

**Option #1: Do nothing**

The library wil automatically retrieve the client secret on following the steps at *Options #2*.

**Option #2: From the application `env.js`**

Retrieve the `CLIENT_SECRET` before running the script otherwise you will get a `401 Unauthorized Access`.
The latest `CLIENT_SECRET` can be found at [https://my.tado.com/webapp/env.js](https://my.tado.com/webapp/env.js).  It will look something like this:

**Option #3: From the developer mode**

An alternative way to get your `CLIENT_SECRET` is to enable the Developper Mode when logging in and catch the Headers. You will find the form data like this :
::

    client_id: tado-web-app
    client_secret: fndskjnjzkefjNFRNkfKJRNFKRENkjnrek
    grant_type: password
    password: MyBeautifulPassword
    scope: home.user
    username: email@example.com

Then you just have to get the value in the attribute `client_secret`. You will need it to connect to your account through Tado APIs. The `client_secret` never dies so you can base your script on it.
