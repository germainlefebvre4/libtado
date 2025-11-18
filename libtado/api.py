# -*- coding: utf-8 -*-

"""libtado

This module provides bindings to the API of https://www.tado.com/ to control
your smart thermostats.

Example:
  import libtado.api
  t = tado.api('Username', 'Password', 'ClientSecret')
  print(t.get_me())

Disclaimer:
  This module is in NO way connected to tado GmbH and is not officially
  supported by them!

License:
  Copyright (C) 2017  Max Rosin

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import enum
import json
import os
import sys
from datetime import timedelta, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests
import time

class RateLimitInfo:

  def __init__(self, ratelimit_policy_header: str = None, ratelimit_header: str = None):
    """
    Determines the current status of Tado API rate limit based on 2 HTTP headers (ratelimit and ratelimit-policy).
    Granted_calls indicates how many calls are granted in the given priod (`granted_calls_period_in_seconds`)
    Remaining_calls indicates how many calls are left, which is reset back to granted_calls at `ratelimit_resets_at_utc`
    If the time at which the rate limit is reset is not given, `ratelimit_resets_at_utc` will be None.
    :param ratelimit_header Value of the 'ratelimit' HTTP header.
    :param ratelimit_policy_header Value of the 'ratelimit-policy' HTTP header.
    """
    self.granted_calls = None
    self.granted_calls_period_in_seconds = None
    self.remaining_calls = None
    self.ratelimit_resets_at_utc = None

    if not ratelimit_policy_header or not ratelimit_header:
      return

    # Parse key/value pairs from headers

    # example ratelimit-policy header value: "perday";q=20000;w=86400
    policy_data = self._parse_header(ratelimit_policy_header)

    # example ratelimit header value (according to tado): "perday";r=0;t=123
    # example ratelimit header value (self-observed): "perday";r=15153
    limit_data = self._parse_header(ratelimit_header)

    # Extract data
    granted_calls = int(policy_data.get("q", -1))
    self.granted_calls = granted_calls if granted_calls > -1 else None
    granted_calls_period_in_seconds = int(policy_data.get("w", -1))
    self.granted_calls_period_in_seconds = granted_calls_period_in_seconds if granted_calls_period_in_seconds > -1 else None
    remaining_calls = int(limit_data.get("r", -1))
    self.remaining_calls = remaining_calls if remaining_calls > -1 else None

    reset_in_seconds = int(limit_data.get("t", -1))
    # If limit_data includes 't': Compute reset time (current time + 't', seconds until reset)
    if reset_in_seconds > -1:
      self.ratelimit_resets_at_utc = datetime.now(timezone.utc) + timedelta(seconds=reset_in_seconds)
    else:
      # Reset time is not given.
      self.ratelimit_resets_at_utc = None

  def _parse_header(self, header_value: str) -> dict:
    """
    Parses a HTTP header string like '"perday";q=20000;w=86400'
    into {'policy': 'perday', 'q': '20000', 'w': '86400'}
    :param header_value string value of the HTTP header
    """
    parts = [p.strip() for p in header_value.split(";") if p.strip()]
    data = {}

    # The first part is usually the policy name (quoted)
    if parts:
      data["policy"] = parts[0].strip('"')

    # Remaining parts are key=value
    for part in parts[1:]:
      if "=" in part:
        k, v = part.split("=", 1)
        data[k.strip()] = v.strip()
    return data


class StrEnum(str, enum.Enum):
  """Backport of Python 3.11's StrEnum"""
  pass

class DeviceActivationStatus(StrEnum):
  """Device Activation Status Enum"""

  NOT_STARTED = "NOT_STARTED"
  PENDING = "PENDING"
  COMPLETED = "COMPLETED"

class Tado:
  json_content             = { 'Content-Type': 'application/json'}
  access_headers           = None
  api                      = 'https://my.tado.com/api/v2'
  api_acme                 = 'https://acme.tado.com/v1'
  api_minder               = 'https://minder.tado.com/v1'
  api_energy_insights      = 'https://energy-insights.tado.com/api'
  api_energy_bob           = 'https://energy-bob.tado.com'
  client_id_device         = '1bb50063-6b0c-4d11-bd99-387f4a91cc46' # API client ID
  device_activation_status = DeviceActivationStatus.NOT_STARTED
  device_code              = None
  device_verification_check_interval = None
  device_verification_url  = None
  device_verification_url_expires_at = None
  id                       = None
  ratelimit_info           = RateLimitInfo()
  refresh_at               = datetime.now(timezone.utc) + timedelta(minutes=10)
  refresh_token            = None
  timeout                  = 15
  user_code                = None

  def __init__(self, saved_refresh_token: str = None, token_file_path: str = None):
    self.token_file_path = token_file_path

    if (saved_refresh_token or self.load_token()) and self.refresh_auth(
            refresh_token=saved_refresh_token, force_refresh=True
    ):
      self.device_ready()
    else:
      self.device_activation_status = self.login_device_flow()

  def get_device_activation_status(self) -> DeviceActivationStatus:
    return self.device_activation_status

  def get_device_verification_url(self) -> str:
    return self.device_verification_url

  def set_oauth_token(self, response) -> str:
    access_token = response['access_token']
    expires_in = float(response['expires_in'])
    refresh_token = response['refresh_token']

    self.refresh_token = refresh_token
    # We subtract 30 seconds from the correct refresh time.
    # Then we have a 30 seconds timespan to get a new refresh_token
    self.refresh_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in) - timedelta(seconds=30)

    self.access_headers = {
      'Authorization': f'Bearer {access_token}',
      'User-Agent': 'python/libtado',
    }

    self.save_token()

    return refresh_token

  def load_token(self) -> bool:
    if not self.token_file_path:
      return False
    if not os.path.exists(self.token_file_path):
      f = open(self.token_file_path, "w")
      f.write(json.dumps({}))
      f.close()


    with open(self.token_file_path, encoding="utf-8") as f:
      data = json.load(f)
      self.refresh_token = data.get("refresh_token")

    return True


  def refresh_auth(self, refresh_token: str = None, force_refresh = False) -> bool:
    if self.refresh_at >= datetime.now(timezone.utc) and not force_refresh:
      return True

    url='https://login.tado.com/oauth2/token'
    data = {
      'client_id'     : self.client_id_device,
      'grant_type'    : 'refresh_token',
      'refresh_token' : refresh_token or self.refresh_token
    }
    response = requests.post(url, data=data, timeout=self.timeout)

    if response.status_code != 200 and force_refresh:
      return False
    else:
      response.raise_for_status()

    self.set_oauth_token(response.json())
    return True

  def save_token(self):
    if not self.token_file_path or not self.refresh_token:
      return

    token_dir = os.path.dirname(self.token_file_path)
    if token_dir and not os.path.exists(token_dir):
      Path(token_dir).mkdir(parents=True, exist_ok=True)

    with open(self.token_file_path, "w", encoding="utf-8") as f:
      json.dump(
        {"refresh_token": self.refresh_token},
        f,
      )

  def login_device_flow(self) -> DeviceActivationStatus:
    if self.device_activation_status != DeviceActivationStatus.NOT_STARTED:
      raise Exception("The device has been started already")

    url='https://login.tado.com/oauth2/device_authorize'
    headers = { 'User-Agent': 'python/libtado', 'Referer': 'https://app.tado.com/' }
    data = { 'client_id'     : self.client_id_device,
             'scope'         : 'offline_access' }
    request = requests.post(url, headers=headers, data=data, timeout=self.timeout)
    request.raise_for_status()
    response = request.json()

    user_code = urlencode({'user_code': response['user_code']})
    visit_url = f"{response['verification_uri']}?{user_code}"
    self.device_code = response['device_code']
    self.user_code = response['user_code']
    self.device_verification_check_interval = response['interval']
    self.device_verification_url = visit_url


    print("Please visit the following URL in your Web browser to log in to your Tado account:", visit_url)

    expires_in_seconds = response["expires_in"]
    self.device_verification_url_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
    # print the expiry time in the user's local timezone.
    device_verification_url_expires_at_local_tz = datetime.now() + timedelta(seconds=expires_in_seconds)

    print(
      "Waiting for you to complete logging in. You have until",
      device_verification_url_expires_at_local_tz.strftime("%Y-%m-%d %H:%M:%S"),
    )

    return DeviceActivationStatus.PENDING

  def check_device_activation(self) -> bool:
    if self.device_verification_url_expires_at is not None and datetime.timestamp(datetime.now(timezone.utc)) > datetime.timestamp(self.device_verification_url_expires_at):
      raise Exception("User took too long to enter key")

    # Await the desired interval, before polling the API again
    time.sleep(self.device_verification_check_interval)

    url='https://login.tado.com/oauth2/token'
    headers = { 'User-Agent': 'python/libtado', 'Referer': 'https://app.tado.com/' }
    data={
      'client_id': self.client_id_device,
      'device_code': self.device_code,
      'grant_type': "urn:ietf:params:oauth:grant-type:device_code",
    }
    request = requests.post(url, headers=headers, data=data, timeout=self.timeout)
    if request.status_code == 200:
      self.set_oauth_token(request.json())
      print("")
      return True

    # The user has not yet authorized the device, let's continue
    if request.status_code == 400 and request.json()['error'] == 'authorization_pending':
      print(".", end="")
      return False

    if request.status_code == 400 and request.json()['error'] == 'expired_token':
      print("")
      print("Unfortunately, you took too long to log in to Tado. Please try running your script again and log in with the new link shown on screen.")
      print("The program will now exit.")
      sys.exit(1)

    print("")
    request.raise_for_status()

  def device_activation(self) -> None:
    if self.device_activation_status == DeviceActivationStatus.NOT_STARTED:
      raise Exception("The device flow has not yet started")

    while True:
      if self.check_device_activation():
        break

    self.device_ready()

  def device_ready(self):
    self.id = self.get_me()['homes'][0]['id']
    self.user_code = None
    self.device_verification_url = None
    self.device_activation_status = DeviceActivationStatus.COMPLETED

  def _api_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_post(url, data):
      r = requests.post(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api, cmd)
    if method == 'DELETE':
      res = call_delete(url)
      if res.status_code == 204:
        return None
      return res.json()
    elif method == 'PUT' and data:
      res = call_put(url, data)
      if res.status_code == 204:
        return None
      return res.json()
    elif method == 'GET':
      return call_get(url).json()
    elif method == 'POST':
      return call_post(url, data).json()

  def _api_acme_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api_acme, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()

  def _api_minder_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api_minder, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()


  def _api_energy_insights_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_post(url, data):
      r = requests.post(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api_energy_insights, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()
    elif method == 'POST' and data:
      return call_post(url, data).json()


  def _api_energy_bob_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      self.ratelimit_info = self._update_rate_limit_info(r, self.ratelimit_info)
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api_energy_bob, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()


  def get_capabilities(self, zone):
    """
    Get the capabilities of a zone.

    Parameters:
      zone (int): The zone ID.

    Returns:
      temperatures (dict): The temperature capabilities of the zone.
      type (str): The temperature type of the zone.

    ??? info "Result example"
        ```json
        {
          "temperatures": {
            "celsius": {
              "max": 25,
              "min": 5,
              "step": 1.0
            },
            "fahrenheit": {
              "max": 77,
              "min": 41,
              "step": 1.0
            }
          },
          "type": "HEATING"
        }
        ```
    """
    data = self._api_call('homes/%i/zones/%i/capabilities' % (self.id, zone))
    return data

  def get_devices(self):
    """
    Get all devices of your home.

    Returns:
      (list): All devices of the home as a list of dictionaries.

    ??? info "Result example"
        ```json
        [
          {
            "characteristics": {
              "capabilities": []
            },
            "connectionState": {
              "timestamp": "2017-02-20T18:51:47.362Z",
              "value": True
            },
            "currentFwVersion": "25.15",
            "deviceType": "GW03",
            "gatewayOperation": "NORMAL",
            "serialNo": "SOME_SERIAL",
            "shortSerialNo": "SOME_SERIAL"
          },
          {
            "characteristics": {
              "capabilities": ["INSIDE_TEMPERATURE_MEASUREMENT", "IDENTIFY"]
            },
            "connectionState": {
              "timestamp": "2017-01-22T16:03:00.773Z",
              "value": False
            },
            "currentFwVersion": "36.15",
            "deviceType": "VA01",
            "mountingState": {
              "timestamp": "2017-01-22T15:12:45.360Z",
              "value": "UNMOUNTED"
            },
            "serialNo": "SOME_SERIAL",
            "shortSerialNo": "SOME_SERIAL"
          },
          {
            "characteristics": {
              "capabilities": ["INSIDE_TEMPERATURE_MEASUREMENT", "IDENTIFY"]
            },
            "connectionState": {
              "timestamp": "2017-02-20T18:33:49.092Z",
              "value": True
            },
            "currentFwVersion": "36.15",
            "deviceType": "VA01",
            "mountingState": {
              "timestamp": "2017-02-12T13:34:35.288Z",
              "value": "CALIBRATED"},
            "serialNo": "SOME_SERIAL",
            "shortSerialNo": "SOME_SERIAL"
          },
          {
            "characteristics": {
              "capabilities": ["INSIDE_TEMPERATURE_MEASUREMENT", "IDENTIFY"]
            },
            "connectionState": {
              "timestamp": "2017-02-20T18:51:28.779Z",
              "value": True
            },
            "currentFwVersion": "36.15",
            "deviceType": "VA01",
            "mountingState": {
              "timestamp": "2017-01-12T13:22:11.618Z",
              "value": "CALIBRATED"
            },
            "serialNo": "SOME_SERIAL",
            "shortSerialNo": "SOME_SERIAL"
          }
        ]
        ```
    """
    data = self._api_call('homes/%i/devices' % self.id)
    return data

  def get_device_usage(self):
    """
    Get all devices of your home with how they are used.

    Returns:
      entries (list): All devices of home as list of dictionaries.

    ??? info "Result example"
        ```json
        {
          "entries": [
            {
              "type": "RU01",
              "device": {
                "deviceType": "RU01",
                "serialNo": "RU3174041856",
                "shortSerialNo": "RU3174041856",
                "currentFwVersion": "54.20",
                "connectionState": {
                  "value": true,
                  "timestamp": "2024-01-01T23:57:43.265Z"
                },
                "characteristics": {
                  "capabilities": [
                    "INSIDE_TEMPERATURE_MEASUREMENT",
                    "IDENTIFY"
                  ]
                },
                "batteryState": "NORMAL"
              },
              "zone": {
                "discriminator": 1,
                "duties": [
                  "UI"
                ]
              }
            },
            {
              "type": "VA01",
              "device": {
                "deviceType": "VA01",
                "serialNo": "VA4291823104",
                "shortSerialNo": "VA4291823104",
                "currentFwVersion": "54.20",
                "connectionState": {
                  "value": true,
                  "timestamp": "2024-01-02T00:08:51.296Z"
                },
                "characteristics": {
                  "capabilities": [
                    "INSIDE_TEMPERATURE_MEASUREMENT",
                    "IDENTIFY"
                  ]
                },
                "mountingState": {
                  "value": "CALIBRATED",
                  "timestamp": "2023-10-18T08:32:04.640Z"
                },
                "mountingStateWithError": "CALIBRATED",
                "batteryState": "NORMAL",
                "childLockEnabled": false
              },
              "zone": {
                "discriminator": 11
              }
            },
            {
              "type": "BU01",
              "device": {
                "deviceType": "BU01",
                "serialNo": "BU4274718464",
                "shortSerialNo": "BU4274718464",
                "currentFwVersion": "81.1",
                "connectionState": {
                  "value": true,
                  "timestamp": "2024-01-02T00:00:02.365Z"
                },
                "characteristics": {
                  "capabilities": []
                },
                "isDriverConfigured": true
              }
            },
            {
              "type": "GW03",
              "device": {
                "deviceType": "GW03",
                "serialNo": "GW2754808064",
                "shortSerialNo": "GW2754808064",
                "currentFwVersion": "47.2",
                "connectionState": {
                  "value": true,
                  "timestamp": "2024-01-01T23:55:19.317Z"
                },
                "characteristics": {
                  "capabilities": [
                    "RADIO_ENCRYPTION_KEY_ACCESS"
                  ]
                },
                "inPairingMode": false
              }
            }
          ]
        }
        ```
    """

    data = self._api_call('homes/%i/deviceList' % self.id)
    return data

  def get_early_start(self, zone):
    """
    Get the early start configuration of a zone.

    Parameters:
      zone (int): The zone ID.

    Returns:
      enabled (bool): Whether early start is enabled or not.

    ??? info "Result example"
        ```json
        {
          "enabled": True
        }
        ```
    """
    data = self._api_call('homes/%i/zones/%i/earlyStart' % (self.id, zone))
    return data

  def get_home(self):
    """
    Get information about the home.

    Returns:
      id (int): The ID of your home.
      address (dict): The address of your home.
      contactDetails (dict): The contact details of your home.
      dateTimeZone (str): The timezone of your home.
      geolocation (dict): The geolocation of your home.
      installationCompleted (bool): Whether the installation is completed or not.
      name (str): The name of your home.
      partner (dict): The partner of your home.
      simpleSmartScheduleEnabled (bool): Whether simple smart schedule is enabled or not.
      temperatureUnit (str): The temperature unit of your home.

    ??? info "Result example"
        ```json
        {
          "address": {
            "addressLine1": "SOME_STREET",
            "addressLine2": None,
            "city": "SOME_CITY",
            "country": "SOME_COUNTRY",
            "state": None,
            "zipCode": "SOME_ZIP_CODE"
          },
          "contactDetails": {
            "email": "SOME_EMAIL",
            "name": "SOME_NAME",
            "phone": "SOME_PHONE"
          },
          "dateTimeZone": "Europe/Berlin",
          "geolocation": {
            "latitude": SOME_LAT,
            "longitude": SOME_LONG
          },
          "id": SOME_ID,
          "installationCompleted": True,
          "name": "SOME_NAME",
          "partner": None,
          "simpleSmartScheduleEnabled": True,
          "temperatureUnit": "CELSIUS"
        }
        ```
    """
    data = self._api_call('homes/%i' % self.id)
    return data

  def get_home_state(self):
    """
    Get information about the status of the home.

    Returns:
      presence (str): The presence of the home.
      presenceLocked (bool): Whether the presence is locked or not.

    ??? info "Result example"
        ```json
        {
          "presence": "HOME",
          "presenceLocked": false
        }
        ```
    """
    data = self._api_call('homes/%i/state' % self.id)
    return data

  def set_home_state(self, at_home):
    """
    Set at-home/away state

    Parameters:
      at_home (bool): True for at HOME, false for AWAY.
    """

    if at_home:
      payload = {'homePresence': 'HOME'}
    else:
      payload = {'homePresence': 'AWAY'}

    self._api_call('homes/%i/presenceLock' % self.id, payload, method='PUT')


  def get_invitations(self):
    """
    Get active invitations.

    Returns:
      (list): A list of active invitations to your home.

    ??? info "Result example"
        ```json
        [
          {
            "email": "SOME_INVITED_EMAIL",
            "firstSent": "2017-02-20T21:01:44.450Z",
            "home": {
              "address": {
                "addressLine1": "SOME_STREET",
                "addressLine2": None,
                "city": "SOME_CITY",
                "country": "SOME_COUNTRY",
                "state": None,
                "zipCode": "SOME_ZIP_CODE"
              },
              "contactDetails": {
                "email": "SOME_EMAIL",
                "name": "SOME_NAME",
                "phone": "SOME_PHONE"
              },
              "dateTimeZone": "Europe/Berlin",
              "geolocation": {
                "latitude": SOME_LAT,
                "longitude": SOME_LONG
              },
              "id": SOME_ID,
              "installationCompleted": True,
              "name": "SOME_NAME",
              "partner": None,
              "simpleSmartScheduleEnabled": True,
              "temperatureUnit": "CELSIUS"
            },
            "inviter": {
              "email": "SOME_INVITER_EMAIL",
              "enabled": True,
              "homeId": SOME_ID,
              "locale": "SOME_LOCALE",
              "name": "SOME_NAME",
              "type": "WEB_USER",
              "username": "SOME_USERNAME"
            },
            "lastSent": "2017-02-20T21:01:44.450Z",
            "token": "SOME_TOKEN"
          }
        ]
        ```
    """

    data = self._api_call('homes/%i/invitations' % self.id)
    return data

  def set_invitation(self, email):
    """
    Send an invitation to a user.

    Parameters:
      email (str): The email of the user to invite.

    Returns:
      (dict): The invitation information.

    ??? info "Result example"
        ```json
        {
            "token": "44483e1d07qf439&8b786fc0372ec315",
            "email": "SOME_EMAIL",
            "firstSent": "2024-03-19T12:54:38.591Z",
            "lastSent": "2024-03-19T12:54:38.591Z",
            "inviter": {
                "name": "SOME_NAME",
                "email": "SOME_EMAIL",
                "username": "SOME_MAIL",
                "enabled": true,
                "id": "5c22a9b6d5018000088dba4a",
                "homeId": 123456,
                "locale": "fr",
                "type": "WEB_USER"
            },
            "home": {
                "id": 123456,
                "name": "Domicile",
                "dateTimeZone": "Europe/Paris",
                "dateCreated": "2018-12-25T20:58:28.674Z",
                "temperatureUnit": "CELSIUS",
                "partner": null,
                "simpleSmartScheduleEnabled": true,
                "awayRadiusInMeters": 1999.68,
                "installationCompleted": true,
                "incidentDetection": {
                    "supported": true,
                    "enabled": true
                },
                "generation": "PRE_LINE_X",
                "zonesCount": 4,
                "skills": [
                    "AUTO_ASSIST"
                ],
                "christmasModeEnabled": true,
                "showAutoAssistReminders": true,
                "contactDetails": {
                    "name": "SOME_NAME",
                    "email": "SOME_EMAIL",
                    "phone": "SOME_PHONE_NUMBER"
                },
                "address": {
                    "addressLine1": "SOME_POSTAL_ADDRESS",
                    "addressLine2": null,
                    "zipCode": "SOME_POSTCODE",
                    "city": "SOME_CITY",
                    "state": null,
                    "country": "FRA"
                },
                "geolocation": {
                    "latitude": 12.3456789,
                    "longitude": 1.23456
                },
                "consentGrantSkippable": true,
                "enabledFeatures": [
                    "CLIMATE_REPORT_AS_WEBVIEW",
                    "EIQ_SETTINGS_AS_WEBVIEW",
                    "ENERGY_IQ_V2_ONBOARDING",
                    "HIDE_BOILER_REPAIR_SERVICE",
                    "KEEP_WEBAPP_UPDATED",
                    "OWD_SETTINGS_AS_WEBVIEW",
                    "SMART_SCHEDULE_AS_WEBVIEW"
                ],
                "isAirComfortEligible": true,
                "isBalanceAcEligible": false,
                "isEnergyIqEligible": true,
                "isHeatSourceInstalled": false,
                "isBalanceHpEligible": false
            }
        }
        ```
    """
    payload = { 'email': email }
    return self._api_call('homes/%i/invitations' % (self.id), data=payload, method='POST')

  def delete_invitation(self, token):
    """
    Delete an invitation.

    Parameters:
      token (str): The token of the invitation to delete.

    Returns:
      (None): None.
    """
    return self._api_call('homes/%i/invitations/%s' % (self.id, token), method='DELETE')

  def get_me(self):
    """
    Get information about the current user.

    Returns:
      (dict): A dictionary with information about the current user.

    ??? info "Result example"
        ```json
        {
          "email": "SOME_EMAIL",
          "homes": [
            {
              "id": SOME_ID,
              "name": "SOME_NAME"
            }
          ],
          "locale": "en_US",
          "mobileDevices": [],
          "name": "SOME_NAME",
          "username": "SOME_USERNAME",
          "secret": "SOME_CLIENT_SECRET"
        }
        ```
    """

    data = self._api_call('me')
    return data

  def get_mobile_devices(self):
    """
    Get all mobile devices.

    Returns:
      (list): List of dictionaries with information about the mobile devices.

    ??? info "Result example"
        ```json
        [
          {
            "name": "Germain",
            "id": 1234567,
            "settings": {
              "geoTrackingEnabled": true,
              "specialOffersEnabled": true,
              "onDemandLogRetrievalEnabled": true,
              "pushNotifications": {
                "lowBatteryReminder": true,
                "awayModeReminder": true,
                "homeModeReminder": true,
                "openWindowReminder": true,
                "energySavingsReportReminder": true,
                "incidentDetection": true,
                "energyIqReminder": false
              }
            },
            "location": {
              "stale": false,
              "atHome": true,
              "bearingFromHome": {
                "degrees": 123.45611789012345,
                "radians": 1.2345678901234567
              },
              "relativeDistanceFromHomeFence": 0.0
            },
            "deviceMetadata": {
              "platform": "iOS",
              "osVersion": "17.1.2",
              "model": "iPhone11,2",
              "locale": "fr"
            }
          }
        ]
        ```
    """
    data = self._api_call('homes/%i/mobileDevices' % self.id)
    return data

  def get_schedule_timetables(self, zone):
    """
    Gets the schedule timetables supported by the zone

    Parameters:
      zone (int): The zone ID.

    Returns:
      (list): List of schedule types.

    ??? info "Result example"
        ```json
        [
          {
            "id": 0,
            "type": "ONE_DAY"
          },
          {
            "id": 1,
            "type": "THREE_DAY"
          },
          {
            "id": 2,
            "type": "SEVEN_DAY"
          }
        ]
        ```
    """

    data = self._api_call('homes/%i/zones/%i/schedule/timetables' % (self.id, zone))
    return data

  def get_schedule(self, zone):
    """
    Get the type of the currently configured schedule of a zone.

    Parameters:
      zone (int): The zone ID.

    Returns:
      (dict): A dictionary with the ID and type of the schedule of the zone.

    Tado allows three different types of a schedule for a zone:

    * The same schedule for all seven days of a week.
    * One schedule for weekdays, one for saturday and one for sunday.
    * Seven different schedules - one for every day of the week.


    ??? info "Result example"
        ```json
        {
          "id": 1,
          "type": "THREE_DAY"
        }
        ```
    """

    data = self._api_call('homes/%i/zones/%i/schedule/activeTimetable' % (self.id, zone))
    return data

  def set_schedule(self, zone, schedule):
    """
    Set the type of the currently configured schedule of a zone.

    Parameters:
      zone (int): The zone ID.
      schedule (int): The schedule to activate.
                      The supported zones are currently
                        * 0: ONE_DAY
                        * 1: THREE_DAY
                        * 2: SEVEN_DAY
                      But the actual mapping should be retrieved via get_schedule_timetables.

    Returns:
      (dict): The new configuration.
    """

    payload = { 'id': schedule }
    return self._api_call('homes/%i/zones/%i/schedule/activeTimetable' % (self.id, zone), payload, method='PUT')

  def get_schedule_blocks(self, zone, schedule):
    """
    Gets the blocks for the current schedule on a zone

    Parameters:
      zone (int): The zone ID.
      schedule (int): The schedule ID to fetch.

    Returns:
      (list): The blocks for the requested schedule.

    ??? info "Result example"
        ```json
        [
          {
            "dayType": "MONDAY_TO_FRIDAY",
            "start": "00:00",
            "end": "06:30",
            "geolocationOverride": false,
            "setting": {
              "type": "HEATING",
              "power": "ON",
              "temperature": {
                "celsius": 21.2,
                "fahrenheit": 70.16
              }
            }
          },
          {
            "dayType": "MONDAY_TO_FRIDAY",
            "start": "06:30",
            "end": "00:00",
            "geolocationOverride": false,
            "setting": {
              "type": "HEATING",
              "power": "ON",
              "temperature": {
                "celsius": 21.0,
                "fahrenheit": 69.8
              }
            }
          },
          {
            "dayType": "SATURDAY",
            "start": "00:00",
            "end": "08:00",
            "geolocationOverride": false,
            "setting": {
              "type": "HEATING",
              "power": "ON",
              "temperature": {
                "celsius": 21.0,
                "fahrenheit": 69.8
              }
            }
          },

          [...]

          {
            "dayType": "SUNDAY",
            "start": "08:00",
            "end": "00:00",
            "geolocationOverride": false,
            "setting": {
              "type": "HEATING",
              "power": "ON",
              "temperature": {
                "celsius": 21.0,
                "fahrenheit": 69.8
              }
            }
          }
        ]
        ```
    """

    return self._api_call('homes/%i/zones/%i/schedule/timetables/%i/blocks' % (self.id, zone, schedule))

  def set_schedule_blocks(self, zone, schedule, blocks):
    """
    Sets the block for the current schedule on a zone

    Parameters:
      zone (int): The zone ID.
      schedule (int): The schedule ID.
      blocks (list): The new blocks.

    Returns:
      (list): The new configuration.
    """

    if (schedule in [0, 1, 2]):
      possible_day_types = [
          [
              "MONDAY_TO_SUNDAY"
          ],
          [
              "MONDAY_TO_FRIDAY",
              "SATURDAY",
              "SUNDAY"
          ],
          [
              "MONDAY",
              "TUESDAY",
              "WEDNESDAY",
              "THURSDAY",
              "FRIDAY",
              "SATURDAY",
              "SUNDAY"
          ]
      ]

      blocks_grouped = {}
      for block in blocks:
          day_type = block['dayType']
          if day_type not in blocks_grouped:
              blocks_grouped[day_type] = []
          blocks_grouped[day_type].append(block)

      inapplicable_day_types = []
      blocks_by_day = []
      for day_type in possible_day_types[schedule]:
          if day_type in blocks_grouped:
              blocks_by_day.append({
                  'dayType': day_type,
                  'blocks_for_day': blocks_grouped[day_type]
              })
      used_day_types = {b['dayType'] for b in blocks_by_day}
      for day_type in blocks_grouped:
          if day_type not in used_day_types:
              inapplicable_day_types.append(day_type)

      httpresponses = []
      for day in blocks_by_day:
          day_type = day['dayType']
          payload = day['blocks_for_day']
          if not payload:
              continue

          httpresponses.append(self._api_call('homes/%i/zones/%i/schedule/timetables/%i/blocks/%s' %
                                (self.id, zone, schedule, day_type), payload, method='PUT'))

      if (len(inapplicable_day_types) > 0):
          message = f"Not every 'day_type' was compatible with schedule {schedule}. The following 'day_type's were not set: {', '.join(inapplicable_day_types)}."
          print(message)
      return httpresponses
    else:
      print("Operation failed: 'schedule' must have value 0, 1 or 2.")


  def get_schedule_block_by_day_type(self, zone, schedule, day_type):
    """
    Gets the blocks for the current schedule on a zone

    Parameters:
      zone (int): The zone ID.
      schedule (int): The schedule ID to fetch.
      day_type (str): The day_type to fetch. e.g. MONDAY_TO_FRIDAY, "MONDAY", "TUESDAY" etc

    Returns:
      (list): The blocks for the requested day type schedule.

    ??? info "Result example"
        ```json
        [
          {
            "dayType": "MONDAY_TO_FRIDAY",
            "start": "00:00",
            "end": "06:30",
            "geolocationOverride": false,
            "setting": {
              "type": "HEATING",
              "power": "ON",
              "temperature": {
                "celsius": 21.2,
                "fahrenheit": 70.16
              }
            }
          },
          [...]
        ]
        ```
    """

    return self._api_call('homes/%i/zones/%i/schedule/timetables/%i/blocks/%s' % (self.id, zone, schedule, day_type))

  def set_schedule_block_by_day_type(self, zone, schedule, day_type, blocks):
    print("This method has been depreciated. Use 'set_schedule_blocks()' instead.")
    return self.set_schedule_blocks(zone, schedule, blocks)

  def get_state(self, zone):
    """
    Get the current state of a zone including its desired and current temperature. Check out the example output for more.

    Parameters:
      zone (int): The zone ID.

    Returns:
      (dict): A dictionary with the current settings and sensor measurements of the zone.

    ??? info "Result example"
        ```json
        {
          "activityDataPoints": {
            "heatingPower": {
              "percentage": 0.0,
              "timestamp": "2017-02-21T11:56:52.204Z",
              "type": "PERCENTAGE"
            }
          },
          "geolocationOverride": False,
          "geolocationOverrideDisableTime": None,
          "link": {
            "state": "ONLINE"
          },
          "overlay": None,
          "overlayType": None,
          "preparation": None,
          "sensorDataPoints": {
            "humidity": {
              "percentage": 44.0,
              "timestamp": "2017-02-21T11:56:45.369Z",
              "type": "PERCENTAGE"
            },
            "insideTemperature": {
              "celsius": 18.11,
              "fahrenheit": 64.6,
              "precision": {
                "celsius": 1.0,
                "fahrenheit": 1.0
              },
              "timestamp": "2017-02-21T11:56:45.369Z",
              "type": "TEMPERATURE"
            }
          },
          "setting": {
            "power": "ON",
            "temperature": {
              "celsius": 20.0,
              "fahrenheit": 68.0
            },
            "type": "HEATING"
          },
          "tadoMode": "HOME"
        }
        ```
    """

    data = self._api_call('homes/%i/zones/%i/state' % (self.id, zone))
    return data

  def get_measuring_device(self, zone):
    """
    Gets the active measuring device of a zone

    Parameters:
      zone (int): The zone ID.

    Returns:
      (dict): A dictionary with the current measuring informations.
    """

    data = self._api_call('homes/%i/zones/%i/measuringDevice' % (self.id, zone))
    return data

  def get_default_overlay(self, zone):
    """
    Get the default overlay settings of a zone

    Parameters:
      zone (int): The zone ID.

    Returns:
      terminationCondition (dict): The termination condition of the overlay.

    ??? info "Result example"
        ```json
        {
          "terminationCondition": {
            "type": "TADO_MODE"
          }
        }
        ```
    """
    data = self._api_call('homes/%i/zones/%i/defaultOverlay' % (self.id, zone))
    return data

  def get_users(self):
    """
    Get all users of your home.

    Returns:
      (list): A list of dictionaries with all your users.

    ??? info "Result example"
        ```json
        [
          {
            "name": "Germain",
            "email": "an_email@adress.com",
            "username": "an_email@adress.com",
            "id": "5c1234b1d0123456789dba1a",
            "homes": [
              {
                "id": 1234567,
                "name": "Domicile"
              }
            ],
            "locale": "fr",
            "mobileDevices": [
              {
                "name": "Germain",
                "id": 1234567,
                "settings": {
                  "geoTrackingEnabled": true,
                  "specialOffersEnabled": true,
                  "onDemandLogRetrievalEnabled": true,
                  "pushNotifications": {
                    "lowBatteryReminder": true,
                    "awayModeReminder": true,
                    "homeModeReminder": true,
                    "openWindowReminder": true,
                    "energySavingsReportReminder": true,
                    "incidentDetection": true,
                    "energyIqReminder": false
                  }
                },
                "location": {
                  "stale": false,
                  "atHome": true,
                  "bearingFromHome": {
                    "degrees": 0.0,
                    "radians": 0.0
                  },
                  "relativeDistanceFromHomeFence": 0.0
                },
                "deviceMetadata": {
                  "platform": "iOS",
                  "osVersion": "17.1.2",
                  "model": "iPhone11,2",
                  "locale": "fr"
                }
              }
            ]
          }
        ]
        ```
    """
    data = self._api_call('homes/%i/users' % self.id)
    return data

  def get_weather(self):
    """
    Get the current weather of the location of your home.

    Returns:
      (dict): A dictionary with weather information for your home.

    ??? info "Result example"
        ```json
        {
          "outsideTemperature": {
            "celsius": 8.49,
            "fahrenheit": 47.28,
            "precision": {
              "celsius": 0.01,
              "fahrenheit": 0.01
            },
            "timestamp": "2017-02-21T12:06:11.296Z",
            "type": "TEMPERATURE"
          },
          "solarIntensity": {
            "percentage": 58.4,
            "timestamp": "2017-02-21T12:06:11.296Z",
            "type": "PERCENTAGE"
          },
          "weatherState": {
            "timestamp": "2017-02-21T12:06:11.296Z",
            "type": "WEATHER_STATE",
            "value": "CLOUDY_PARTLY"
          }
        }
        ```
    """

    data = self._api_call('homes/%i/weather' % self.id)
    return data

  def get_zones(self):
    """
    Get all zones of your home.

    Returns:
      (list): A list of dictionaries with all your zones.

    ??? info "Result example"
        ```json
        [
          {
            "dateCreated": "2016-12-23T15:53:43.615Z",
            "dazzleEnabled": True,
            "deviceTypes": ["VA01"],
            "devices": [
              {
                "characteristics": {
                  "capabilities": ["INSIDE_TEMPERATURE_MEASUREMENT", "IDENTIFY"]
                },
                "connectionState": {
                  "timestamp": "2017-02-21T14:22:45.913Z",
                  "value": True
                },
                "currentFwVersion": "36.15",
                "deviceType": "VA01",
                "duties": ["ZONE_UI", "ZONE_DRIVER", "ZONE_LEADER"],
                "mountingState": {
                  "timestamp": "2017-02-12T13:34:35.288Z",
                  "value": "CALIBRATED"
                },
                "serialNo": "SOME_SERIAL",
                "shortSerialNo": "SOME_SERIAL"
              }
            ],
            "id": 1,
            "name": "SOME_NAME",
            "reportAvailable": False,
            "supportsDazzle": True,
            "type": "HEATING"
          },
          {
            "dateCreated": "2016-12-23T16:16:11.390Z",
            "dazzleEnabled": True,
            "deviceTypes": ["VA01"],
            "devices": [
              {
                "characteristics": {
                  "capabilities": ["INSIDE_TEMPERATURE_MEASUREMENT", "IDENTIFY"]
                },
                "connectionState": {
                  "timestamp": "2017-02-21T14:19:40.215Z",
                  "value": True
                },
                "currentFwVersion": "36.15",
                "deviceType": "VA01",
                "duties": ["ZONE_UI", "ZONE_DRIVER", "ZONE_LEADER"],
                "mountingState": {
                  "timestamp": "2017-01-12T13:22:11.618Z",
                  "value": "CALIBRATED"
                },
                "serialNo": "SOME_SERIAL",
                "shortSerialNo": "SOME_SERIAL"
              }
            ],
            "id": 3,
            "name": "SOME_NAME ",
            "reportAvailable": False,
            "supportsDazzle": True,
            "type": "HEATING"
          }
        ]
        ```
    """

    data = self._api_call('homes/%i/zones' % self.id)
    return data

  def set_zone_name(self, zone, new_name):
    """
    Sets the name of the zone

    Parameters:
      zone (int): The zone ID.
      new_name (str): The new name of the zone.

    Returns:
      (dict): A dictionary with the new name of the zone.
    """

    payload = { 'name': new_name }
    data = self._api_call('homes/%i/zones/%i/details' % (self.id, zone), payload, method='PUT')
    return data

  def set_early_start(self, zone, enabled):
    """
    Enable or disable the early start feature of a zone.

    Parameters:
      zone (int): The zone ID.
      enabled (bool): Enable (True) or disable (False) the early start feature of the zone.

    Returns:
      (boolean): Whether the early start feature is enabled or not.

    ??? info "Result example"
        ```json
        {
          "enabled": True
        }
        ```
    """

    if enabled:
      payload = { 'enabled': 'true' }
    else:
      payload = { 'enabled': 'false' }

    return self._api_call('homes/%i/zones/%i/earlyStart' % (self.id, zone), payload, method='PUT')

  def set_temperature(self, zone, temperature, termination='MANUAL'):
    """
    Set the desired temperature of a zone.

    Parameters:
      zone (int): The zone ID.
      temperature (float): The desired temperature in celsius.
      termination (str/int): The termination mode for the zone.

    Returns:
      (dict): A dictionary with the new zone settings.

    If you set a desired temperature less than 5 celsius it will turn of the zone!

    The termination supports three different mode:

    * `MANUAL`: The zone will be set on the desired temperature until you change it manually.
    * `AUTO`: The zone will be set on the desired temperature until the next automatic change.
    * `INTEGER`: The zone will be set on the desired temperature for INTEGER seconds.

    ??? info "Result example"
        ```json
        {
          "setting": {
            "power": "ON",
            "temperature": {
              "celsius": 12.0,
              "fahrenheit": 53.6
            },
            "type": "HEATING"
          },
          "termination": {
            "projectedExpiry": None,
            "type": "MANUAL"
          },
          "type": "MANUAL"
        }
        ```
    """

    def get_termination_dict(termination):
      if termination == 'MANUAL':
        return { 'type': 'MANUAL' }
      elif termination == 'AUTO':
        return { 'type': 'TADO_MODE' }
      else:
        return { 'type': 'TIMER', 'durationInSeconds': termination }
    def get_setting_dict(temperature):
      if temperature < 5:
        return { 'type': 'HEATING', 'power': 'OFF' }
      else:
        return { 'type': 'HEATING', 'power': 'ON', 'temperature': { 'celsius': temperature } }

    payload = { 'setting': get_setting_dict(temperature),
                'termination': get_termination_dict(termination)
              }
    return self._api_call('homes/%i/zones/%i/overlay' % (self.id, zone), data=payload, method='PUT')

  def end_manual_control(self, zone: int):
    """
    End the manual control of a zone.

    Parameters:
      zone (int): The zone ID.

    Returns:
      (None): None

    ??? info "Result example"
        ```json
        None
        ```
    """
    self._api_call('homes/%i/zones/%i/overlay' % (self.id, zone), method='DELETE')

  def get_away_configuration(self, zone):
    """
    Get the away configuration for a zone

    Parameters:
      zone (int): The zone ID.

    Returns:
      type (str): The type of the away configuration.
      preheatingLevel (str): The preheating level of the away configuration.
      minimumAwayTemperature (dict): The minimum away temperature of the away configuration.

    ??? info "Result example"
        ```json
        {
          "type": "HEATING",
          "preheatingLevel": "COMFORT",
          "minimumAwayTemperature": {
            "celsius": 16.0,
            "fahrenheit": 60.8
          }
        }
        ```
    """

    data = self._api_call('homes/%i/zones/%i/awayConfiguration' % (self.id, zone))
    return data

  def set_away_configuration(self, zone, equipment_type, preheating_level, minimumAwayTemperatureCelcius):
    """
    Set the away configuration for a zone

    Parameters:
      zone (int): The zone ID.
      equipment_type (str): The change type. e.g. HEATING, HOT_WATER
      preheating_level (str): The preheating level. e.g. OFF, ECO, MEDIUM, CONFORT
      minimumAwayTemperatureCelcius (float): The minimum temperature in celsius.
    """

    payload = { 'type': equipment_type, 'preheatingLevel': preheating_level, 'minimumAwayTemperature': { 'celsius': minimumAwayTemperatureCelcius } }

    data = self._api_call('homes/%i/zones/%i/awayConfiguration' % (self.id, zone), data=payload, method='PUT')
    return data

  def set_open_window_detection(self, zone, enabled, seconds):
    """
    Get the open window detection for a zone

    Parameters:
      zone (int): The zone ID.
      enabled (bool): If open window detection is enabled.
      seconds (int): timeout in seconds.
    """

    payload = { 'enabled' : enabled, 'timeoutInSeconds': seconds }

    data = self._api_call('homes/%i/zones/%i/openWindowDetection' % (self.id, zone), data=payload, method='PUT')
    return data

  def get_report(self, zone, date):
    """
    Get the report for a zone on a specific date.

    Parameters:
      zone (int): The zone ID.
      date (str): The date in ISO8601 format. e.g. "2019-02-14".

    Returns:
      (dict): The daily report.

    ??? info "Result example"
        ```json
        {
          "zoneType": "HEATING",
          "interval": {
            "from": "2023-12-11T22:45:00.000Z",
            "to": "2023-12-12T23:15:00.000Z"
          },
          "hoursInDay": 24,
          "measuredData": {
            "measuringDeviceConnected": {
              "timeSeriesType": "dataIntervals",
              "valueType": "boolean",
              "dataIntervals": [
                {
                  "from": "2023-12-11T22:45:00.000Z",
                  "to": "2023-12-12T23:15:00.000Z",
                  "value": true
                }
              ]
            },
            "insideTemperature": {
              "timeSeriesType": "dataPoints",
              "valueType": "temperature",
              "min": {
                "celsius": 18.12,
                "fahrenheit": 64.62
              },
              "max": {
                "celsius": 19.67,
                "fahrenheit": 67.41
              },
              "dataPoints": [
                {
                  "timestamp": "2023-12-11T22:45:00.000Z",
                  "value": {
                    "celsius": 19.59,
                    "fahrenheit": 67.26
                  }
                },
                [...]
              ]
            },
            "humidity": {
              "timeSeriesType": "dataPoints",
              "valueType": "percentage",
              "percentageUnit": "UNIT_INTERVAL",
              "min": 0.549,
              "max": 0.605,
              "dataPoints": [
                {
                  "timestamp": "2023-12-11T22:45:00.000Z",
                  "value": 0.567
                },
                [...]
              ]
            }
          },
          "stripes": {
            "timeSeriesType": "dataIntervals",
            "valueType": "stripes",
            "dataIntervals": [
              {
                "from": "2023-12-12T05:00:00.000Z",
                "to": "2023-12-12T07:43:23.594Z",
                "value": {
                  "stripeType": "HOME",
                  "setting": {
                    "type": "HEATING",
                    "power": "ON",
                    "temperature": {
                      "celsius": 19.0,
                      "fahrenheit": 66.2
                    }
                  }
                }
              },
              [...]
            ]
          },
          "settings": {
            "timeSeriesType": "dataIntervals",
            "valueType": "heatingSetting",
            "dataIntervals": [
              {
                "from": "2023-12-11T22:45:00.000Z",
                "to": "2023-12-11T23:00:00.000Z",
                "value": {
                  "type": "HEATING",
                  "power": "ON",
                  "temperature": {
                    "celsius": 18.0,
                    "fahrenheit": 64.4
                  }
                }
              },
              [...]
            ]
          },
          "callForHeat": {
            "timeSeriesType": "dataIntervals",
            "valueType": "callForHeat",
            "dataIntervals": [
              {
                "from": "2023-12-11T22:45:00.000Z",
                "to": "2023-12-12T13:59:08.402Z",
                "value": "NONE"
              },
              [...]
            ]
          },
          "weather": {
            "condition": {
              "timeSeriesType": "dataIntervals",
              "valueType": "weatherCondition",
              "dataIntervals": [
                {
                  "from": "2023-12-11T22:45:00.000Z",
                  "to": "2023-12-11T22:45:42.875Z",
                  "value": {
                    "state": "NIGHT_CLOUDY",
                    "temperature": {
                      "celsius": 8.79,
                      "fahrenheit": 47.82
                    }
                  }
                },
                [...]
              ]
            },
            "sunny": {
              "timeSeriesType": "dataIntervals",
              "valueType": "boolean",
              "dataIntervals": [
                {
                  "from": "2023-12-11T22:45:00.000Z",
                  "to": "2023-12-12T23:15:00.000Z",
                  "value": false
                }
              ]
            },
            "slots": {
              "timeSeriesType": "slots",
              "valueType": "weatherCondition",
              "slots": {
                "04:00": {
                  "state": "NIGHT_CLOUDY",
                  "temperature": {
                    "celsius": 8.12,
                    "fahrenheit": 46.62
                  }
                },
                [...]
              }
            }
          }
        }
        ```
    """
    data = self._api_call('homes/%i/zones/%i/dayReport?date=%s' % (self.id, zone, date))
    return data

  def get_heating_circuits(self):
    """
    Gets the heating circuits in the current home

    Returns:
      (list): List of all dictionaries for all heating circuits.

    ??? info "Result example"
        ```json
        [
          {
            "number": 1,
            "driverSerialNo": "BU4274718464",
            "driverShortSerialNo": "BU4274718464"
          }
        ]
        ```
    """

    data = self._api_call('homes/%i/heatingCircuits' % self.id)
    return data

  def get_incidents(self):
    """
    Gets the ongoing incidents in the current home

    Returns:
      incidents (list): List of all current incidents.

    ??? info "Result example"
        ```json
        {
          "incidents": []
        }
        ```
    """

    data = self._api_minder_call('homes/%i/incidents' % self.id)
    return data

  def set_incident_detection(self, enabled):
    """
    Set the incident detection for the home

    Parameters:
      enabled (bool): Enable or disable the incident detection.

    Returns:
      (None): None

    ??? info "Result example"
        ```json
        None
        ```
    """
    payload = { 'enabled': enabled }

    return self._api_call('homes/%i/incidentDetection' % self.id, payload, method='PUT')

  def get_installations(self):
    """
    Gets the ongoing installations in the current home

    Returns:
      (list): List of all current installations

    ??? info "Result example"
        ```json
        []
        ```
    """

    data = self._api_call('homes/%i/installations' % self.id)
    return data

  def get_temperature_offset(self, device_serial):
    """
    Gets the temperature offset of a device

    Parameters:
      device_serial (str): The serial number of the device.

    Returns:
      (dict): A dictionary that returns the offset in 'celsius' and 'fahrenheit'.

    ??? info "Result example"
        ```json
        {
          "celsius": 0.0,
          "fahrenheit": 0.0
        }
        ```
    """

    data = self._api_call('devices/%s/temperatureOffset' % device_serial)
    return data

  def set_temperature_offset(self, device_serial, offset):
    """
    Sets the temperature offset of a device

    Parameters:
      device_serial (str): The serial number of the device.
      offset (float): the temperature offset to apply in celsius.

    Returns:
      (dict): A dictionary that returns the offset in 'celsius' and 'fahrenheit'.
    """

    payload = { 'celsius':  offset }

    return self._api_call('devices/%s/temperatureOffset' % device_serial, payload, method='PUT')

  def get_air_comfort(self):
    """
    Get all zones of your home.

    Returns:
      freshness (dict): A dictionary with the freshness of your home.
      comfort (list): A list of dictionaries with the comfort of each zone.

    ??? info "Result example"
        ```json
        {
          "freshness":{
            "value":"FAIR",
            "lastOpenWindow":"2020-09-04T10:38:57Z"
          },
          "comfort":[
            {
              "roomId":1,
              "temperatureLevel":"COMFY",
              "humidityLevel":"COMFY",
              "coordinate":{
                "radial":0.36,
                "angular":323
              }
            },
            {
              "roomId":4,
              "temperatureLevel":"COMFY",
              "humidityLevel":"COMFY",
              "coordinate":{
                "radial":0.43,
                "angular":324
              }
            }
          ]
        }
        ```
    """
    data = self._api_call('homes/%i/airComfort' % self.id)
    return data

  def get_air_comfort_geoloc(self, latitude, longitude) -> dict:
    """
    Get all zones of your home.

    Parameters:
      latitude (float): The latitude of the home.
      longitude (float): The longitude of the home.

    Returns:
      (dict): A dict of lists of dictionaries with all your rooms.

    ??? info "Result example"
        ```json
        {
          "roomMessages":[
            {
              "roomId":4,
              "message":"Bravo\u00a0! L\u2019air de cette pi\u00e8ce est proche de la perfection.",
              "visual":"success",
              "link":null
            },
            {
              "roomId":1,
              "message":"Continuez \u00e0 faire ce que vous faites\u00a0! L'air de cette pi\u00e8ce est parfait.",
              "visual":"success",
              "link":null
            }
          ],
          "outdoorQuality":{
            "aqi":{
              "value":81,
              "level":"EXCELLENT"
            },
            "pollens":{
              "dominant":{
                "level":"LOW"
              },
              "types":[
                {
                  "localizedName":"Gramin\u00e9es",
                  "type":"GRASS",
                  "localizedDescription":"Poaceae",
                  "forecast":[
                    {
                      "localizedDay":"Auj.",
                      "date":"2020-09-06",
                      "level":"NONE"
                    },
                    {
                      "localizedDay":"Lun",
                      "date":"2020-09-07",
                      "level":"NONE"
                    },
                    {
                      "localizedDay":"Mar",
                      "date":"2020-09-08",
                      "level":"NONE"
                    }
                  ]
                },
                {
                  "localizedName":"Herbac\u00e9es",
                  "type":"WEED",
                  "localizedDescription":"Armoise, Ambroisie, Pari\u00e9taire",
                  "forecast":[
                    {
                      "localizedDay":"Auj.",
                      "date":"2020-09-06",
                      "level":"NONE"
                    },
                    {
                      "localizedDay":"Lun",
                      "date":"2020-09-07",
                      "level":"NONE"
                    },
                    {
                      "localizedDay":"Mar",
                      "date":"2020-09-08",
                      "level":"NONE"
                    }
                  ]
                },
                {
                  "localizedName":"Arbres",
                  "type":"TREE",
                  "localizedDescription":"Aulne, Fr\u00eane, Bouleau, Noisetier, Cypr\u00e8s, Olivier",
                  "forecast":[
                    {
                      "localizedDay":"Auj.",
                      "date":"2020-09-06",
                      "level":"NONE"
                    },
                    {
                      "localizedDay":"Lun",
                      "date":"2020-09-07",
                      "level":"NONE"
                    },
                    {
                      "localizedDay":"Mar",
                      "date":"2020-09-08",
                      "level":"NONE"
                    }
                  ]
                }
              ]
            },
            "pollutants":[
              {
                "localizedName":"Mati\u00e8re particulaire",
                "scientificName":"PM<sub>10</sub>",
                "level":"EXCELLENT",
                "concentration":{
                  "value":8.75,
                  "units":"\u03bcg/m<sup>3</sup>"
                }
              },
              {
                "localizedName":"Mati\u00e8re particulaire",
                "scientificName":"PM<sub>2.5</sub>",
                "level":"EXCELLENT",
                "concentration":{
                  "value":5.04,
                  "units":"\u03bcg/m<sup>3</sup>"
                }
              },
              {
                "localizedName":"Ozone",
                "scientificName":"O<sub>3</sub>",
                "level":"EXCELLENT",
                "concentration":{
                  "value":23.86,
                  "units":"ppb"
                }
              },
              {
                "localizedName":"Dioxyde de soufre",
                "scientificName":"SO<sub>2</sub>",
                "level":"EXCELLENT",
                "concentration":{
                  "value":1.19,
                  "units":"ppb"
                }
              },
              {
                "localizedName":"Monoxyde de carbone",
                "scientificName":"CO",
                "level":"EXCELLENT",
                "concentration":{
                  "value":266.8,
                  "units":"ppb"
                }
              },
              {
                "localizedName":"Dioxyde d'azote",
                "scientificName":"NO<sub>2</sub>",
                "level":"EXCELLENT",
                "concentration":{
                  "value":5.76,
                  "units":"ppb"
                }
              }
            ]
          }
        }
        ```
    """
    data = self._api_acme_call('homes/%i/airComfort?latitude=%f&longitude=%f' % (self.id, latitude, longitude))
    return data


  def get_heating_system(self):
    """
    Get all heating systems of your home.

    Returns:
      (list): A dict of your heating systems.

    ??? info "Result example"
        ```json
        {
          "boiler":{
            "present": true,
            "id": 17830,
            "found": true
          },
          "underfloorHeating":{
            "present": false
          }
        }
        ```
    """
    data = self._api_call('homes/%i/heatingSystem' % (self.id))
    return data


  def get_running_times(self, from_date):
    """
    Get all running times of your home.

    Parameters:
      from_date (str): The date in ISO8601 format. e.g. "2019-02-14".

    Returns:
      (list): A dict of your running times.

    ??? info "Result example"
        ```json
        {
          "runningTimes":[
            {
              "runningTimeInSeconds":0,
              "startTime":"2022-08-18 00:00:00",
              "endTime":"2022-08-19 00:00:00",
              "zones":[
                {
                  "id":1,
                  "runningTimeInSeconds":0
                },
                {
                  "id":6,
                  "runningTimeInSeconds":0
                },
                {
                  "id":11,
                  "runningTimeInSeconds":0
                },
                {
                  "id":12,
                  "runningTimeInSeconds":0
                }
              ]
            }
          ],
          "summary":{
            "startTime":"2022-08-18 00:00:00",
            "endTime":"2022-08-19 00:00:00",
            "totalRunningTimeInSeconds":0
          },
          "lastUpdated":"2022-08-18T05:07:44Z"
        }
        ```
    """
    data = self._api_minder_call('homes/%i/runningTimes?from=%s' % (self.id, from_date))
    return data


  def get_zone_states(self):
    """
    Get all zone states of your home.

    Returns:
      (list): A dict of your zone states.

    ??? info "Result example"
        ```json
        {
          "zoneStates":{
            "1":{
              "tadoMode":"HOME",
              "geolocationOverride":false,
              "geolocationOverrideDisableTime":"None",
              "preparation":"None",
              "setting":{
                "type":"HEATING",
                "power":"ON",
                "temperature":{
                  "celsius":19.0,
                  "fahrenheit":66.2
                }
              },
              "overlayType":"None",
              "overlay":"None",
              "openWindow":"None",
              "nextScheduleChange":{
                "start":"2022-08-18T16:00:00Z",
                "setting":{
                  "type":"HEATING",
                  "power":"ON",
                  "temperature":{
                    "celsius":20.0,
                    "fahrenheit":68.0
                  }
                }
              },
              "nextTimeBlock":{
                "start":"2022-08-18T16:00:00.000Z"
              },
              "link":{
                "state":"ONLINE"
              },
              "activityDataPoints":{
                "heatingPower":{
                  "type":"PERCENTAGE",
                  "percentage":0.0,
                  "timestamp":"2022-08-18T05:34:32.127Z"
                }
              },
              "sensorDataPoints":{
                "insideTemperature":{
                  "celsius":24.13,
                  "fahrenheit":75.43,
                  "timestamp":"2022-08-18T05:36:21.241Z",
                  "type":"TEMPERATURE",
                  "precision":{
                    "celsius":0.1,
                    "fahrenheit":0.1
                  }
                },
                "humidity":{
                  "type":"PERCENTAGE",
                  "percentage":62.2,
                  "timestamp":"2022-08-18T05:36:21.241Z"
                }
              }
            },
            "6":{
              "tadoMode":"HOME",
              "geolocationOverride":false,
              "geolocationOverrideDisableTime":"None",
              "preparation":"None",
              "setting":{
                "type":"HEATING",
                "power":"ON",
                "temperature":{
                  "celsius":19.5,
                  "fahrenheit":67.1
                }
              },
              "overlayType":"None",
              "overlay":"None",
              "openWindow":"None",
              "nextScheduleChange":{
                "start":"2022-08-18T07:00:00Z",
                "setting":{
                  "type":"HEATING",
                  "power":"ON",
                  "temperature":{
                    "celsius":18.0,
                    "fahrenheit":64.4
                  }
                }
              },
              "nextTimeBlock":{
                "start":"2022-08-18T07:00:00.000Z"
              },
              "link":{
                "state":"ONLINE"
              },
              "activityDataPoints":{
                "heatingPower":{
                  "type":"PERCENTAGE",
                  "percentage":0.0,
                  "timestamp":"2022-08-18T05:47:58.505Z"
                }
              },
              "sensorDataPoints":{
                "insideTemperature":{
                  "celsius":24.2,
                  "fahrenheit":75.56,
                  "timestamp":"2022-08-18T05:46:09.620Z",
                  "type":"TEMPERATURE",
                  "precision":{
                    "celsius":0.1,
                    "fahrenheit":0.1
                  }
                },
                "humidity":{
                  "type":"PERCENTAGE",
                  "percentage":64.8,
                  "timestamp":"2022-08-18T05:46:09.620Z"
                }
              }
            }
          }
        }
        ```
    """
    data = self._api_call('homes/%i/zoneStates' % (self.id))
    return data

  def get_energy_consumption(self, startDate, endDate, country, ngsw_bypass=True):
    """
    Get enery consumption of your home by range date

    Parameters:
      startDate (str): Start date of the range date.
      endDate (str): End date of the range date.
      country (str): Country code.
      ngsw_bypass (bool): Bypass the ngsw cache.

    Returns:
      (list): A dict of your energy consumption.

    ??? info "Result example"
        ```json
        {
          "tariff": "0.104 €/kWh",
          "unit": "m3",
          "consumptionInputState": "full",
          "customTariff": false,
          "currency": "EUR",
          "tariffInfo":{
            "consumptionUnit": "kWh",
            "customTariff": false,
            "tariffInCents": 10.36,
            "currencySign": "€",
          "details":{
            "totalCostInCents": 1762.98,
            "totalConsumption": 16.13,
            "perDay": [
              {
                "date": "2022-09-01",
                "consumption": 0,
                "costInCents": 0
              },{
                "date": "2022-09-02",
                "consumption": 0,
                "costInCents": 0
              },{
                "date": "2022-09-03",
                "consumption": 0.04,
                "costInCents": 0.4144
              }
            ]
          }
        }
        ```
    """
    data = self._api_energy_insights_call('homes/%i/consumption?startDate=%s&endDate=%s&country=%s&ngsw-bypass=%s' % (self.id, startDate, endDate, country, ngsw_bypass))
    return data

  def get_energy_savings(self, monthYear, country, ngsw_bypass=True):
    """
    Get energy savings of your home by month and year

    Parameters:
      monthYear (str): Month and year of the range date.
      country (str): Country code.
      ngsw_bypass (bool): Bypass the ngsw cache.

    Returns:
      (list): A dict of your energy savings.

    ??? info "Result example"
        ```json
        {
          "coveredInterval":{
            "start":"2022-08-31T23:48:02.675000Z",
            "end":"2022-09-29T13:10:23.035000Z"
          },
          "totalSavingsAvailable":true,
          "withAutoAssist":{
            "detectedAwayDuration":{
              "value":56,
              "unit":"HOURS"
            },
            "openWindowDetectionTimes":9
          },
          "totalSavingsInThermostaticMode":{
            "value":0,
            "unit":"HOURS"
          },
          "manualControlSaving":{
            "value":0,
            "unit":"PERCENTAGE"
          },
          "totalSavings":{
            "value":6.5,
            "unit":"PERCENTAGE"
          },
          "hideSunshineDuration":false,
          "awayDuration":{
            "value":56,
            "unit":"HOURS"
          },
          "showSavingsInThermostaticMode":false,
          "communityNews":{
            "type":"HOME_COMFORT_STATES",
            "states":[
              {
                "name":"humid",
                "value":47.3,
                "unit":"PERCENTAGE"
              },
              {
                "name":"ideal",
                "value":43.1,
                "unit":"PERCENTAGE"
              },
              {
                "name":"cold",
                "value":9.5,
                "unit":"PERCENTAGE"
              },
              {
                "name":"warm",
                "value":0.1,
                "unit":"PERCENTAGE"
              },
              {
                "name":"dry",
                "value":0,
                "unit":"PERCENTAGE"
              }
            ]
          },
          "sunshineDuration":{
            "value":112,
            "unit":"HOURS"
          },
          "hasAutoAssist":true,
          "openWindowDetectionTimes":5,
          "setbackScheduleDurationPerDay":{
            "value":9.100000381469727,
            "unit":"HOURS"
          },
          "totalSavingsInThermostaticModeAvailable":false,
          "yearMonth":"2022-09",
          "hideOpenWindowDetection":false,
          "home":123456,
          "hideCommunityNews":false
        }
        ```
    """
    data = self._api_energy_bob_call('%i/%s?country=%s&ngsw-bypass=%s' % (self.id, monthYear, country, ngsw_bypass))
    return data

  def set_cost_simulation(self, country, ngsw_bypass=True, payload=None):
    """
    Trigger Cost Simulation of your home

    Parameters:
      country (str): Country code.
      ngsw_bypass (bool): Bypass the ngsw cache.
      payload (dict): Payload for the request.

    Other parameters: Payload
      payload (dict): Payload for the request.

    ??? info "Payload example"
        ```json
        {
          "temperatureDeltaPerZone": [
            {
              "zone": 1,
              "setTemperatureDelta": -1
            },
            {
              "zone": 6,
              "setTemperatureDelta": -1
            },
            {
              "zone": 11,
              "setTemperatureDelta": -1
            },
            {
              "zone": 12,
              "setTemperatureDelta": -1
            }
          ]
        }
        ```

    Returns:
      consumptionUnit (str): Consumption unit
      estimationPerZone (list): List of cost estimation per zone

    ??? info "Result example"
        ```json
        {
          "consumptionUnit": "m3",
          "estimationPerZone": [
            {
              "zone": 1,
              "consumption": -1.6066000000000038,
              "costInCents": -176
            },
            {
              "zone": 6,
              "consumption": -1.1184999999999974,
              "costInCents": -122
            },
            {
              "zone": 11,
              "consumption": -1.412700000000008,
              "costInCents": -154
            },
            {
              "zone": 12,
              "consumption": -1.6030000000000015,
              "costInCents": -175
            }
          ]
        }
        ```
    """

    data = self._api_energy_insights_call('homes/%i/costSimulator?country=%s&ngsw-bypass=%s' % (self.id, country, ngsw_bypass), data=payload, method='POST')
    return data

  def get_consumption_overview(self, monthYear, country, ngsw_bypass=True):
    """
    Get energy consumption overview of your home by month and year

    Parameters:
      monthYear (str): Month and year of the range date.
      country (str): Country code.
      ngsw_bypass (bool): Bypass the ngsw cache.

    Returns:
      consumptionInputState (str): Consumption input state
      currency (str): Currency
      customTariff (bool): Custom tariff
      energySavingsReport (dict): Energy savings report
      monthlyAggregation (dict): Monthly aggregation
      tariffInfo (dict): Tariffication information
      unit (str): Measurement unit

    ??? info "Result example"
        ```json
        {
          "currency": "EUR",
          "tariff": "0.104 €/kWh",
          "tariffInfo": {
            "currencySign": "€",
            "consumptionUnit": "kWh",
            "tariffInCents": 10.36,
            "customTariff": false
          },
          "customTariff": false,
          "consumptionInputState": "full",
          "unit": "m3",
          "energySavingsReport": {
            "totalSavingsInPercent": 4.7,
            "yearMonth": "2023-09"
          },
          "monthlyAggregation": {
            "endOfMonthForecast": {
              "startDate": "2023-10-13",
              "endDate": "2023-10-31",
              "totalConsumption": 3.82,
              "totalCostInCents": 417.52,
              "consumptionPerDate": [
                {
                  "date": "2023-10-14",
                  "consumption": 0.2122222222222222,
                  "costInCents": 23.2
                },
                [...] // 17 more days
                {
                  "date": "2023-10-31",
                  "consumption": 0.2122222222222222,
                  "costInCents": 23.2
                }
              ]
            },
            "requestedMonth": {
              "startDate": "2023-10-01",
              "endDate": "2023-10-13",
              "totalConsumption": 1.5,
              "totalCostInCents": 163.95,
              "consumptionPerDate": [
                {
                  "date": "2023-10-01",
                  "consumption": 0,
                  "costInCents": 0
                },
                [...] // 12 more days
                {
                  "date": "2023-10-13",
                  "consumption": 0,
                  "costInCents": 0
                }
              ]
            },
            "monthBefore": {
              "startDate": "2023-09-01",
              "endDate": "2023-09-30",
              "totalConsumption": 1.2799999999999998,
              "totalCostInCents": 139.9,
              "consumptionPerDate": [
                {
                  "date": "2023-09-01",
                  "consumption": 0,
                  "costInCents": 0
                },
                [...] // 29 more days
                {
                  "date": "2023-09-30",
                  "consumption": 0.36,
                  "costInCents": 39.35
                }
              ]
            },
            "yearBefore": {
              "startDate": "2022-10-01",
              "endDate": "2022-10-31",
              "totalConsumption": 22.569999999999997,
              "totalCostInCents": 2466.86,
              "consumptionPerDate": [
                {
                  "date": "2022-10-01",
                  "consumption": 0.67,
                  "costInCents": 73.23
                },
                [...] // 30 more days
                {
                  "date": "2022-10-31",
                  "consumption": 0.65,
                  "costInCents": 71.04
                }
              ]
            }
          }
        }
        ```
    """

    data = self._api_energy_insights_call('homes/%i/consumptionOverview?month=%s&country=%s&ngsw-bypass=%s' % (self.id, monthYear, country, ngsw_bypass))
    return data

  def get_consumption_details(self, monthYear, ngsw_bypass=True):
    """
    Get energy consumption details of your home by month and year

    Parameters:
      monthYear (str): Month and year of the range date. e.g. "2022-09".
      ngsw_bypass (bool): Bypass the ngsw cache.

    Returns:
      isInPreferredUnit (bool): Is in preferred unit
      summary (dict): Summary
      graphConsumption (dict): Graph consumption
      consumptionComparison (dict): Consumption comparison
      heatingHotWaterSplit (dict): Heating hotwater split
      roomBreakdown (dict): Room breakdown
      heatingInsights (dict): Heating insights
      showAddData (bool): Show add data


    ??? info "Result example"
        ```json
        {
            "isInPreferredUnit": true,
            "summary": {
                "costInCents": 12618.34,
                "costForecastInCents": null,
                "averageDailyCostInCents": 407.04322580645163,
                "consumption": 115.449,
                "consumptionForecast": null,
                "averageDailyConsumption": 3.7241612903225807,
                "unit": "m3",
                "tariff": {
                    "unit": "kWh",
                    "unitPriceInCents": 10.36
                }
            },
            "graphConsumption": {
                "unit": "m3",
                "monthlyAggregation": {
                    "endOfMonthForecast": null,
                    "requestedMonth": {
                        "startDate": "2024-12-01",
                        "endDate": "2024-12-31",
                        "hasDomesticHotWater": false,
                        "totalConsumption": 115.449,
                        "totalCostInCents": 12618.34,
                        "consumptionPerDate": [
                            {
                                "date": "2024-12-01",
                                "consumption": 3.721,
                                "costInCents": 406.7,
                                "hotWater": null,
                                "heating": 3.721,
                                "hasData": true
                            },
                            [...] // 29 more days
                        ]
                    },
                    "monthBefore": {
                        "startDate": "2024-11-01",
                        "endDate": "2024-11-30",
                        "hasDomesticHotWater": false,
                        "totalConsumption": 82.69,
                        "totalCostInCents": 9037.85,
                        "consumptionPerDate": [
                            {
                                "date": "2024-11-01",
                                "consumption": 1.471,
                                "costInCents": 160.78,
                                "hotWater": null,
                                "heating": 1.471,
                                "hasData": true
                            },
                            [...] // 29 more days
                        ]
                    },
                    "yearBefore": {
                        "startDate": "2023-12-01",
                        "endDate": "2023-12-31",
                        "hasDomesticHotWater": false,
                        "totalConsumption": 105.242,
                        "totalCostInCents": 11502.74,
                        "consumptionPerDate": [
                            {
                                "date": "2023-12-01",
                                "consumption": 7.89,
                                "costInCents": 862.36,
                                "hotWater": null,
                                "heating": 7.89,
                                "hasData": true
                            },
                            [...] // 29 more days
                        ]
                    }
                }
            },
            "consumptionComparison": {
                "consumption": {
                    "comparedToMonthBefore": {
                        "percentage": 40,
                        "trend": "INCREASE",
                        "requestedMonth": "2024-12",
                        "comparedToMonth": "2024-11"
                    },
                    "comparedToYearBefore": {
                        "percentage": 10,
                        "trend": "INCREASE",
                        "requestedMonth": "2024-12",
                        "comparedToMonth": "2023-12"
                    }
                },
                "cost": {
                    "comparedToMonthBefore": {
                        "percentage": 40,
                        "trend": "INCREASE",
                        "requestedMonth": "2024-12",
                        "comparedToMonth": "2024-11"
                    },
                    "comparedToYearBefore": {
                        "percentage": 10,
                        "trend": "INCREASE",
                        "requestedMonth": "2024-12",
                        "comparedToMonth": "2023-12"
                    }
                }
            },
            "heatingHotWaterSplit": null,
            "roomBreakdown": {
                "unit": "m3",
                "requestedMonth": {
                    "perRoom": [
                        {
                            "id": 1,
                            "name": "Maison",
                            "consumption": 45.772999999999996,
                            "costInCents": 5002.9
                        },
                        ...
                    ],
                    "startDate": "2024-12-01",
                    "endDate": "2024-12-31"
                },
                "yearBefore": {
                    "perRoom": [
                        {
                            "id": 1,
                            "name": "Maison",
                            "consumption": 39.895,
                            "costInCents": 4360.44
                        },
                        ...
                    ],
                    "startDate": "2023-12-01",
                    "endDate": "2023-12-31"
                }
            },
            "heatingInsights": {
                "heatingHours": {
                    "diff": 54,
                    "trend": "INCREASE",
                    "comparedTo": "2023-12"
                },
                "outsideTemperature": {
                    "diff": 1,
                    "trend": "DECREASE",
                    "comparedTo": "2023-12"
                },
                "awayHours": {
                    "diff": 25,
                    "trend": "DECREASE",
                    "comparedTo": "2023-12"
                }
            },
            "showAddData": true
        }
        ```
    """

    data = self._api_energy_insights_call('homes/%i/consumptionDetails?month=%s&ngsw-bypass=%s' % (self.id, monthYear, ngsw_bypass))
    return data

  def get_energy_settings(self, ngsw_bypass=True):
    """
    Get energy settings of your home

    Parameters:
      ngsw_bypass (bool): Bypass the ngsw cache.

    Returns:
      homeId (int): Home ID
      dataSource (str): Data source
      consumptionUnit (str): Consumption unit
      preferredEnergyUnit (str): Preferred energy unit
      showReadingsBanner (bool): Show readings banner

    ??? info "Result example"
        ```json
        {
          "homeId": 123456,
          "dataSource": "meterReadings",
          "consumptionUnit": "m3",
          "preferredEnergyUnit": "m3",
          "showReadingsBanner": false
        }
        ```
    """

    data = self._api_energy_insights_call('homes/%i/settings?ngsw-bypass=%s' % (self.id, ngsw_bypass))
    return data

  def get_energy_insights(self, start_date, end_date, country, ngsw_bypass=True):
    """
    Get energy insights of your home

    Parameters:
      start_date (str): Start date of the range date.
      end_date (str): End date of the range date.
      country (str): Country code.
      ngsw_bypass (bool): Bypass the ngsw cache.

    Returns:
      consumptionComparison (dict): Consumption comparison
      costForecast (dict): Cost forecast
      weatherComparison (dict): Weather comparison
      heatingTimeComparison (dict): Heating time comparison
      awayTimeComparison (dict): Away time comparison
      heatingHotwaterComparison (dict): Heating hotwater comparison

    ??? info "Result example"
        ```json
        {
          "consumptionComparison": {
            "currentMonth": {
            "consumed": {
              "energy": [
                {
                  "toEndOfRange": 1.5,
                  "unit": "m3",
                  "perZone": [
                    {
                      "zone": 1,
                      "toEndOfRange": 0.6025913295286759
                    }
                  ]
                },
                {
                  "toEndOfRange": 15.83,
                  "unit": "kWh",
                  "perZone": [
                    {
                      "zone": 1,
                      "toEndOfRange": 6.36
                    }
                  ]
                }
              ]
            },
            "dateRange": {
              "start": "2023-10-01",
              "end": "2023-10-13"
            }
            },
            "comparedTo": {
              "consumed": {
                "energy": [
                  {
                    "toEndOfRange": 16.9,
                    "unit": "m3",
                    "perZone": [
                    {
                      "zone": 1,
                      "toEndOfRange": 6.098444101091741
                    }
                    ]
                  },
                  {
                    "toEndOfRange": 178.3,
                    "unit": "kWh",
                    "perZone": [
                    {
                      "zone": 1,
                      "toEndOfRange": 64.34
                    }
                    ]
                  }
                ]
              },
              "dateRange": {
                "start": "2022-10-01",
                "end": "2022-10-13"
              }
              }
          },
          "costForecast": {
            "costEndOfMonthInCents": 417.5
          },
          "weatherComparison": {
            "currentMonth": {
              "averageTemperature": 17.2,
              "dateRange": {
                "start": "2023-10-01",
                "end": "2023-10-13"
              }
            },
            "comparedTo": {
              "averageTemperature": 12.7,
              "dateRange": {
                "start": "2022-10-01",
                "end": "2022-10-13"
              }
            }
          },
          "heatingTimeComparison": {
            "currentMonth": {
              "heatingTimeHours": 13,
              "dateRange": {
                "start": "2023-10-01",
                "end": "2023-10-14"
              }
            },
            "comparedTo": {
              "heatingTimeHours": 155,
              "dateRange": {
                "start": "2022-10-01",
                "end": "2022-10-14"
              }
            }
          },
          "awayTimeComparison": {
            "currentMonth": {
              "awayTimeInHours": 39,
              "dateRange": {
                "start": "2023-10-01",
                "end": "2023-10-13"
              }
            },
            "comparedTo": {
              "awayTimeInHours": 74,
              "dateRange": {
                "start": "2022-10-01",
                "end": "2022-10-13"
              }
            }
          },
          "heatingHotwaterComparison": null
        }
        ```
    """

    data = self._api_energy_insights_call('homes/%i/insights?startDate=%s&endDate=%s&country=%s&ngsw-bypass=%s' % (self.id, start_date, end_date, country, ngsw_bypass))
    return data

  def set_heating_system_boiler(self, payload):
    """
    Set heating system boiler status

    Parameters:
      payload (dict): The payload to send to the API.

    Other parameters: Payload
      payload (dict): Payload for the request.

    ??? info "Payload example"
        ```json
        {
          "present":true,
          "found":true,
          "id":"17830"
        }
        ```

    Returns:
      No returned value.
    """

    return self._api_call('homes/%i/heatingSystem/boiler' % (self.id), data=payload, method='PUT')

  def set_zone_order(self, payload, ngsw_bypass=True):
    """
    Set zone order

    Parameters:
      ngsw_bypass (bool): Bypass the ngsw cache.
      payload (dict): The payload to send to the API.

    Other parameters: Payload
      payload (list): Payload for the request.

    ??? info "Payload example"
        ```json
        [
          {
            "id": 1
          },
          {
            "id": 6
          },
          {
            "id": 11
          },
          {
            "id": 12
          }
        ]
        ```
    """
    return self._api_call('homes/%i/zoneOrder?ngsw-bypass=%s' % (self.id, ngsw_bypass), data=payload, method='PUT')

  def _update_rate_limit_info(self, r: requests.Response, previous_info: RateLimitInfo) -> RateLimitInfo:
    """
    Constructs current statistics about Tado API rate limit.
    :param r: Response from Tado API
    :param previous_info: Prevoius rate limit info, used in case the response did not include the correct headers.
    :return: tado rate limit info
    """
    if not r or not r.headers:
      if previous_info:
        # keep previous state if this response did not include any headers at all.
        return previous_info
      else:
        # value will be unknown.
        return RateLimitInfo()

    ratelimit_policy_header = r.headers.get('ratelimit-policy')
    ratelimit_header = r.headers.get('ratelimit')

    if not ratelimit_header or not ratelimit_policy_header:
      if previous_info:
        # keep previous state if this response did not include the required ratelimit headers.
        return previous_info
      else:
        # value will be unknown.
        return RateLimitInfo()

    return RateLimitInfo(ratelimit_policy_header, ratelimit_header)

  def get_rate_limit_info(self) -> RateLimitInfo:
    """
    Returns Your account's usage limit and remaining API calls for the Tado API.
    :return: Object containing how many API calls are allowed to the Tado API, and how many are left in current window.
    """
    return self.ratelimit_info
