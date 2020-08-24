.. _api:

=====================
Available API Methods
=====================

Most of the functions receive JSON from the API and translate it to a Python dictionary or a list of Python dictionaries. So the return value will depend on the behaviour of the API.

****
Tado
****

.. autoclass:: libtado.api.Tado
    :members:


class libtado.api.Tado(username, password)
end_manual_control(zone)
End the manual control of a zone.

get_capabilities(zone)
Parameters:	zone (int) – The zone ID.
Returns:	The capabilities of a tado zone as dictionary.
Return type:	dict
Example

{
  'temperatures': {
    'celsius': {'max': 25, 'min': 5, 'step': 1.0},
    'fahrenheit': {'max': 77, 'min': 41, 'step': 1.0}
  },
  'type': 'HEATING'
}
get_devices()
Returns:	All devices of the home as a list of dictionaries.
Return type:	list
Example

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
get_early_start(zone)
Get the early start configuration of a zone.

Parameters:	zone (int) – The zone ID.
Returns:	A dictionary with the early start setting of the zone. (True or False)
Return type:	dict
Example

{ 'enabled': True }
get_home()
Get information about the home.

Returns:	A dictionary with information about your home.
Return type:	dict
Example

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
get_installations()
It is unclear what this does.

Returns:	Currently only an empty list.
Return type:	list
Example

[]
get_invitations()
Get active invitations.

Returns:	A list of active invitations to your home.
Return type:	list
Example

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
get_me()
Get information about the current user.

Returns:	A dictionary with information about the current user.
Return type:	dict
Example

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
  'username': 'SOME_USERNAME'
}
get_mobile_devices()
Get all mobile devices.

get_schedule(zone)
Get the type of the currently configured schedule of a zone.

Parameters:	zone (int) – The zone ID.
Returns:	A dictionary with the ID and type of the schedule of the zone.
Return type:	dict
Tado allows three different types of a schedule for a zone:

The same schedule for all seven days of a week.
One schedule for weekdays, one for saturday and one for sunday.
Seven different schedules - one for every day of the week.
Example

{
  'id': 1,
  'type': 'THREE_DAY'
}
get_state(zone)
Get the current state of a zone including its desired and current temperature. Check out the example output for more.

Parameters:	zone (int) – The zone ID.
Returns:	A dictionary with the current settings and sensor measurements of the zone.
Return type:	dict
Example

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
get_users()
Get all users of your home.

get_weather()
Get the current weather of the location of your home.

Returns:	A dictionary with weather information for your home.
Return type:	dict
Example

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
get_zones()
Get all zones of your home.

Returns:	A list of dictionaries with all your zones.
Return type:	list
Example

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
refresh_auth()
Refresh an active session.

set_early_start(zone, enabled)
Enable or disable the early start feature of a zone.

Parameters:	
zone (int) – The zone ID.
enabled (bool) – Enable (True) or disable (False) the early start feature of the zone.
Returns:	
The new configuration of the early start feature.

Return type:	
dict

Example

{'enabled': True}
set_temperature(zone, temperature, termination='MANUAL')
Set the desired temperature of a zone.

Parameters:	
zone (int) – The zone ID.
temperature (float) – The desired temperature in celsius.
termination (str/int) – The termination mode for the zone.
Returns:	
A dictionary with the new zone settings.

Return type:	
dict

If you set a desired temperature less than 5 celsius it will turn of the zone!

The termination supports three different mode:

“MANUAL”: The zone will be set on the desired temperature until you change it manually.
“AUTO”: The zone will be set on the desired temperature until the next automatic change.
INTEGER: The zone will be set on the desired temperature for INTEGER seconds.
Example

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

