# -*- coding: utf-8 -*-

"""libtado

This module provides bindings to the API of https://www.tado.com/ to control
your smart thermostats.

Example:
  import tado.api
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

import json
import requests
import time

class Tado:
  json_content        = { 'Content-Type': 'application/json'}
  api                 = 'https://my.tado.com/api/v2'
  api_acme            = 'https://acme.tado.com/v1'
  api_minder          = 'https://minder.tado.com/v1'
  api_energy_insights = 'https://energy-insights.tado.com/api'
  api_energy_bob      = 'https://energy-bob.tado.com'
  timeout        = 15

  def __init__(self, username, password, secret):
    self.username = username
    self.password = password
    self.secret = secret
    self._login()
    self.id = self.get_me()['homes'][0]['id']

  def _login(self):
    """Login and setup the HTTP session."""
    url='https://auth.tado.com/oauth/token'
    data = { 'client_id'     : 'tado-web-app',
             'client_secret' : self.secret,
             'grant_type'    : 'password',
             'password'      : self.password,
             'scope'         : 'home.user',
             'username'      : self.username }
    request = requests.post(url, data=data, timeout=self.timeout)
    request.raise_for_status()
    response = request.json()
    self.access_token = response['access_token']
    self.token_expiry = time.time() + float(response['expires_in'])
    self.refresh_token = response['refresh_token']
    self.access_headers = {'Authorization': 'Bearer ' + response['access_token']}

  def _api_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()

  def _api_acme_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
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
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
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
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api_energy_insights, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()


  def _api_energy_bob_call(self, cmd, data=False, method='GET'):
    """Perform an API call."""
    def call_delete(url):
      r = requests.delete(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_put(url, data):
      r = requests.put(url, headers={**self.access_headers, **self.json_content}, data=json.dumps(data), timeout=self.timeout)
      r.raise_for_status()
      return r
    def call_get(url):
      r = requests.get(url, headers=self.access_headers, timeout=self.timeout)
      r.raise_for_status()
      return r

    self.refresh_auth()
    url = '%s/%s' % (self.api_energy_bob, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()


  def refresh_auth(self):
    """Refresh the access token."""
    if time.time() < self.token_expiry - 30:
      return
    url='https://auth.tado.com/oauth/token'
    data = { 'client_id'     : 'tado-web-app',
             'client_secret' : self.secret,
             'grant_type'    : 'refresh_token',
             'refresh_token' : self.refresh_token,
             'scope'         : 'home.user'
           }
    try:
      request = requests.post(url, data=data, timeout=self.timeout)
      request.raise_for_status()
    except:
      self._login()
      return
    response = request.json()
    self.access_token = response['access_token']
    self.token_expiry = time.time() + float(response['expires_in'])
    self.refresh_token = response['refresh_token']
    self.access_headers['Authorization'] = 'Bearer ' + self.access_token

  def get_capabilities(self, zone):
    """
    Parameters:
      zone (int): The zone ID.

    Returns:
      temperatures (dict): The temperature capabilities of the zone.
      type (str): The temperature type of the zone.

    Example:
      ```json
      {
        'temperatures': {
          'celsius': {'max': 25, 'min': 5, 'step': 1.0},
          'fahrenheit': {'max': 77, 'min': 41, 'step': 1.0}
        },
        'type': 'HEATING'
      }
      ```
    """
    data = self._api_call('homes/%i/zones/%i/capabilities' % (self.id, zone))
    return data

  def get_devices(self):
    """
    Returns:
      (list): All devices of the home as a list of dictionaries.

    Example:
      ```json
      [
        {
          'characteristics': { 'capabilities': [] },
          'connectionState': {
            'timestamp': '2017-02-20T18:51:47.362Z',
            'value': True
          },
          'currentFwVersion': '25.15',
          'deviceType': 'GW03',
          'gatewayOperation': 'NORMAL',
          'serialNo': 'SOME_SERIAL',
          'shortSerialNo': 'SOME_SERIAL'
        },
        {
          'characteristics': {
            'capabilities': [ 'INSIDE_TEMPERATURE_MEASUREMENT', 'IDENTIFY']
          },
          'connectionState': {
            'timestamp': '2017-01-22T16:03:00.773Z',
            'value': False
          },
          'currentFwVersion': '36.15',
          'deviceType': 'VA01',
          'mountingState': {
            'timestamp': '2017-01-22T15:12:45.360Z',
            'value': 'UNMOUNTED'
          },
          'serialNo': 'SOME_SERIAL',
          'shortSerialNo': 'SOME_SERIAL'
        },
        {
          'characteristics': {
            'capabilities': [ 'INSIDE_TEMPERATURE_MEASUREMENT', 'IDENTIFY']
          },
          'connectionState': {
            'timestamp': '2017-02-20T18:33:49.092Z',
            'value': True
          },
          'currentFwVersion': '36.15',
          'deviceType': 'VA01',
          'mountingState': {
            'timestamp': '2017-02-12T13:34:35.288Z',
            'value': 'CALIBRATED'},
          'serialNo': 'SOME_SERIAL',
          'shortSerialNo': 'SOME_SERIAL'
        },
        {
          'characteristics': {
            'capabilities': [ 'INSIDE_TEMPERATURE_MEASUREMENT', 'IDENTIFY']
          },
          'connectionState': {
            'timestamp': '2017-02-20T18:51:28.779Z',
            'value': True
          },
          'currentFwVersion': '36.15',
          'deviceType': 'VA01',
          'mountingState': {
            'timestamp': '2017-01-12T13:22:11.618Z',
            'value': 'CALIBRATED'
           },
          'serialNo': 'SOME_SERIAL',
          'shortSerialNo': 'SOME_SERIAL'
        }
      ]
      ```
    """
    data = self._api_call('homes/%i/devices' % self.id)
    return data

  def get_device_usage(self):
    """
    Get all devices of your home with how they are used

    Returns:
      (list): All devices of home as list of dictionaries.
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

    Example:
      ```json
      {
        'enabled': True
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

    Example:
      ```json
      {
        'address': {
          'addressLine1': 'SOME_STREET',
          'addressLine2': None,
          'city': 'SOME_CITY',
          'country': 'SOME_COUNTRY',
          'state': None,
          'zipCode': 'SOME_ZIP_CODE'
        },
        'contactDetails': {
          'email': 'SOME_EMAIL',
          'name': 'SOME_NAME',
          'phone': 'SOME_PHONE'
        },
        'dateTimeZone': 'Europe/Berlin',
        'geolocation': {
          'latitude': SOME_LAT,
          'longitude': SOME_LONG
        },
        'id': SOME_ID,
        'installationCompleted': True,
        'name': 'SOME_NAME',
        'partner': None,
        'simpleSmartScheduleEnabled': True,
        'temperatureUnit': 'CELSIUS'
      }
      ```
    """
    data = self._api_call('homes/%i' % self.id)
    return data

  def get_home_state(self):
    """
    Get information about the status of the home.

    Returns:
      (dict): A dictionary with the status of the home.
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

    Example:
      ```json
      [
        {
          'email': 'SOME_INVITED_EMAIL',
          'firstSent': '2017-02-20T21:01:44.450Z',
          'home': {
            'address': {
              'addressLine1': 'SOME_STREET',
              'addressLine2': None,
              'city': 'SOME_CITY',
              'country': 'SOME_COUNTRY',
              'state': None,
              'zipCode': 'SOME_ZIP_CODE'
            },
            'contactDetails': {
              'email': 'SOME_EMAIL',
              'name': 'SOME_NAME',
              'phone': 'SOME_PHONE'
            },
            'dateTimeZone': 'Europe/Berlin',
            'geolocation': {
              'latitude': SOME_LAT,
              'longitude': SOME_LONG
            },
            'id': SOME_ID,
            'installationCompleted': True,
            'name': 'SOME_NAME',
            'partner': None,
            'simpleSmartScheduleEnabled': True,
            'temperatureUnit': 'CELSIUS'
          },
          'inviter': {
            'email': 'SOME_INVITER_EMAIL',
            'enabled': True,
            'homeId': SOME_ID,
            'locale': 'SOME_LOCALE',
            'name': 'SOME_NAME',
            'type': 'WEB_USER',
            'username': 'SOME_USERNAME'
          },
          'lastSent': '2017-02-20T21:01:44.450Z',
          'token': 'SOME_TOKEN'
        }
      ]
      ```
    """

    data = self._api_call('homes/%i/invitations' % self.id)
    return data

  def get_me(self):
    """
    Get information about the current user.

    Returns:
      (dict): A dictionary with information about the current user.

    Example:
      ```json
      {
        'email': 'SOME_EMAIL',
        'homes': [
          {
            'id': SOME_ID,
            'name': 'SOME_NAME'
          }
        ],
        'locale': 'en_US',
        'mobileDevices': [],
        'name': 'SOME_NAME',
        'username': 'SOME_USERNAME',
        'secret': 'SOME_CLIENT_SECRET'
      }
      ```
    """

    data = self._api_call('me')
    return data

  def get_mobile_devices(self):
    """Get all mobile devices."""
    data = self._api_call('homes/%i/mobileDevices' % self.id)
    return data

  def get_schedule_timetables(self, zone):
    """
    Gets the schedule timetables supported by the zone

    Parameters:
      zone (int): The zone ID.

    Returns:
      (dict): The schedule types.
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


    Example:
      ```json
      {
        'id': 1,
        'type': 'THREE_DAY'
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
    return self._api_call('homes/%i/zones/%i/schedule/activeTimeTable' % (self.id, zone), payload, method='PUT')

  def get_schedule_blocks(self, zone, schedule):
    """
    Gets the blocks for the current schedule on a zone

    Parameters:
      zone (int):      The zone ID.
      schedule (int): The schedule ID to fetch.

    Returns:
      (list): The blocks for the requested schedule.
    """

    return self._api_call('homes/%i/zones/%i/schedule/timetables/%i/blocks' % (self.id, zone, schedule))


  def set_schedule_blocks(self, zone, schedule, blocks):
    """
    Sets the blocks for the current schedule on a zone

    Parameters:
      zone (int): The zone ID.
      schedule (int): The schedule ID.
      blocks (list): The new blocks.

    Returns:
      (list): The new configuration.
    """

    payload = blocks
    return self._api_call('homes/%i/zones/%i/schedule/timetables/%i/blocks' % (self.id, zone, schedule), payload, method='PUT')


  def get_state(self, zone):
    """
    Get the current state of a zone including its desired and current temperature. Check out the example output for more.

    Parameters:
      zone (int): The zone ID.

    Returns:
      (dict): A dictionary with the current settings and sensor measurements of the zone.

    Example:
      ```json
      {
        'activityDataPoints': {
          'heatingPower': {
            'percentage': 0.0,
            'timestamp': '2017-02-21T11:56:52.204Z',
            'type': 'PERCENTAGE'
          }
        },
        'geolocationOverride': False,
        'geolocationOverrideDisableTime': None,
        'link': {'state': 'ONLINE'},
        'overlay': None,
        'overlayType': None,
        'preparation': None,
        'sensorDataPoints': {
          'humidity': {
            'percentage': 44.0,
            'timestamp': '2017-02-21T11:56:45.369Z',
            'type': 'PERCENTAGE'
          },
          'insideTemperature': {
            'celsius': 18.11,
            'fahrenheit': 64.6,
            'precision': {
              'celsius': 1.0,
              'fahrenheit': 1.0
            },
            'timestamp': '2017-02-21T11:56:45.369Z',
            'type': 'TEMPERATURE'
          }
        },
        'setting': {
          'power': 'ON',
          'temperature': {
            'celsius': 20.0,
            'fahrenheit': 68.0
          },
          'type': 'HEATING'
        },
        'tadoMode': 'HOME'
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
      (dict): A dictionary with the default overlay settings of the zone.

    Example:
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
    """Get all users of your home."""
    data = self._api_call('homes/%i/users' % self.id)
    return data

  def get_weather(self):
    """
    Get the current weather of the location of your home.

    Returns:
      (dict): A dictionary with weather information for your home.

    Example:
      ```json
      {
        'outsideTemperature': {
          'celsius': 8.49,
          'fahrenheit': 47.28,
          'precision': {
            'celsius': 0.01,
            'fahrenheit': 0.01
          },
          'timestamp': '2017-02-21T12:06:11.296Z',
          'type': 'TEMPERATURE'
        },
        'solarIntensity': {
          'percentage': 58.4,
          'timestamp': '2017-02-21T12:06:11.296Z',
          'type': 'PERCENTAGE'
        },
        'weatherState': {
          'timestamp': '2017-02-21T12:06:11.296Z',
          'type': 'WEATHER_STATE',
          'value': 'CLOUDY_PARTLY'
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

    Example:
      ```json
      [
        { 'dateCreated': '2016-12-23T15:53:43.615Z',
          'dazzleEnabled': True,
          'deviceTypes': ['VA01'],
          'devices': [
            {
              'characteristics': {
                'capabilities': [ 'INSIDE_TEMPERATURE_MEASUREMENT', 'IDENTIFY']
              },
              'connectionState': {
                'timestamp': '2017-02-21T14:22:45.913Z',
                'value': True
              },
              'currentFwVersion': '36.15',
              'deviceType': 'VA01',
              'duties': ['ZONE_UI', 'ZONE_DRIVER', 'ZONE_LEADER'],
              'mountingState': {
                'timestamp': '2017-02-12T13:34:35.288Z',
                'value': 'CALIBRATED'
              },
              'serialNo': 'SOME_SERIAL',
              'shortSerialNo': 'SOME_SERIAL'
            }
          ],
          'id': 1,
          'name': 'SOME_NAME',
          'reportAvailable': False,
          'supportsDazzle': True,
          'type': 'HEATING'
        },
        {
          'dateCreated': '2016-12-23T16:16:11.390Z',
          'dazzleEnabled': True,
          'deviceTypes': ['VA01'],
          'devices': [
            {
              'characteristics': {
                'capabilities': [ 'INSIDE_TEMPERATURE_MEASUREMENT', 'IDENTIFY']
              },
              'connectionState': {
                'timestamp': '2017-02-21T14:19:40.215Z',
                'value': True
              },
              'currentFwVersion': '36.15',
              'deviceType': 'VA01',
              'duties': ['ZONE_UI', 'ZONE_DRIVER', 'ZONE_LEADER'],
              'mountingState': {
                'timestamp': '2017-01-12T13:22:11.618Z',
                'value': 'CALIBRATED'
              },
              'serialNo': 'SOME_SERIAL',
              'shortSerialNo': 'SOME_SERIAL'
            }
          ],
          'id': 3,
          'name': 'SOME_NAME ',
          'reportAvailable': False,
          'supportsDazzle': True,
          'type': 'HEATING'
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

    Example:
      ```json
      {
        'enabled': True
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

    * "MANUAL": The zone will be set on the desired temperature until you change it manually.
    * "AUTO": The zone will be set on the desired temperature until the next automatic change.
    * INTEGER: The zone will be set on the desired temperature for INTEGER seconds.

    Example:
      ```json
      {
        'setting': {
          'power': 'ON',
          'temperature': {'celsius': 12.0, 'fahrenheit': 53.6},
          'type': 'HEATING'
        },
        'termination': {
          'projectedExpiry': None,
          'type': 'MANUAL'
        },
        'type': 'MANUAL'
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

  def end_manual_control(self, zone):
    """End the manual control of a zone."""
    self._api_call('homes/%i/zones/%i/overlay' % (self.id, zone), method='DELETE')

  def get_away_configuration(self, zone):
    """
    Get the away configuration for a zone

    Parameters:
      zone (int): The zone ID.

    Returns:
      (dict): A dictionary with the away configuration.
    """

    data = self._api_call('homes/%i/zones/%i/awayConfiguration' % (self.id, zone))
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
    Parameters:
      zone (int): The zone ID.
      date (str): The date in ISO8601 format. e.g. "2019-02-14".

    Returns:
      (dict): The daily report.

    """
    data = self._api_call('homes/%i/zones/%i/dayReport?date=%s' % (self.id, zone, date))
    return data

  def get_heating_circuits(self):
    """
    Gets the heating circuits in the current home

    Returns:
      (list): List of all dictionaries for all heating circuits.
    """

    data = self._api_call('homes/%i/heatingCircuits' % self.id)
    return data

  def get_incidents(self):
    """
    Gets the ongoing incidents in the current home

    Returns:
      (dict): Incident information.
    """

    data = self._api_minder_call('homes/%i/incidents' % self.id)
    return data

  def get_installations(self):
    """
    Gets the ongoing installations in the current home

    Returns:
      (list): List of all current installations
    """

    data = self._api_call('homes/%i/installations' % self.id)
    return data

  def get_temperature_offset(self, device_serial):
    """
    Gets the temperature offset of a device

    Returns:
      (dict): A dictionary that returns the offset in 'celsius' and 'fahrenheit'.

    Example:
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
      device_serial (Str): The serial number of the device.
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

    Example:
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

  def get_air_comfort_geoloc(self, latitude, longitude):
    """
    Get all zones of your home.

    Parameters:
      latitude (float): The latitude of the home.
      longitude (float): The longitude of the home.

    Returns:
      (list): A dict of lists of dictionaries with all your rooms.

    Example:
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

    Example:
      ```json
      {
          "boiler":{
              "present":true,
              "id":17830,
              "found":true
          },
          "underfloorHeating":{
              "present":false
          }
      }
      ```
    """
    data = self._api_call('homes/%i/heatingSystem' % (self.id))
    return data


  def get_running_times(self, from_date):
    """
    Get all running times of your home.

    Returns:
      (list): A dict of your running times.

    Example:
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

    Example:
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

    Example:
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
              ],
          }
      }
      ``
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

    Example:
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
          "home":283787,
          "hideCommunityNews":false
      }
      ```
    """
    data = self._api_energy_bob_call('%i/%s?country=%s&ngsw-bypass=%s' % (self.id, monthYear, country, ngsw_bypass))
    return data
