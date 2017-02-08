# -*- coding: utf-8 -*-

"""tado

This module provides bindings to the API of https://www.tado.com/ to control
your smart thermostats.

Example:
  import tado.api
  t = tado.api('Username', 'Password')
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

class Tado:
  headers        = { 'Referer' : 'https://my.tado.com/' }
  access_headers = headers
  api            = 'https://my.tado.com/api/v2'

  def __init__(self, username, password):
    self.username = username
    self.password = password
    self._login()
    self.id = self.get_me()['homes'][0]['id']

  def _login(self):
    self.session = requests.Session()
    url='https://my.tado.com/oauth/token'
    data = { 'client_id'  : 'tado-webapp',
             'grant_type' : 'password',
             'password'   : self.password,
             'scope'      : 'home.user',
             'username'   : self.username }
    request = self.session.post(url, data=data, headers=self.access_headers)
    response = request.json()
    self.access_token = response['access_token']
    self.refresh_token = response['refresh_token']
    self.access_headers['Authorization'] = 'Bearer ' + response['access_token']
    # We need to talk to api v1 to get a JSESSIONID cookie
    self.session.get('https://my.tado.com/api/v1/me', headers=self.access_headers)

  def _api_call(self, cmd, data=False, method='GET'):
    def call_delete(url):
      return self.session.delete(url, headers=self.access_headers)
    def call_put(url, data):
      return self.session.put(url, headers=self.access_headers, data=json.dumps(data))
    def call_get(url):
      return self.session.get(url, headers=self.access_headers)

    url = '%s/%s' % (self.api, cmd)
    if method == 'DELETE':
      return call_delete(url)
    elif method == 'PUT' and data:
      return call_put(url, data).json()
    elif method == 'GET':
      return call_get(url).json()
    else:
      print("What?")

  def refresh_auth(self):
    url='https://my.tado.com/oauth/token'
    data = { 'client_id'     : 'tado-webapp',
             'grant_type'    : 'refresh_token',
             'refresh_token' : self.refresh_token,
             'scope'         : 'home.user'
           }
    request = self.session.post(url, data=data, headers=self.headers)
    response = request.json()
    self.access_token = response['access_token']
    self.refresh_token = response['refresh_token']
    self.access_headers['Authorization'] = 'Bearer ' + self.access_token

  def get_capabilities(self, zone):
    data = self._api_call('homes/%i/zones/%i/capabilities' % (self.id, zone))
    return data

  def get_devices(self):
    data = self._api_call('homes/%i/devices' % self.id)
    return data

  def get_home(self):
    data = self._api_call('homes/%i' % self.id)
    return data

  def get_installations(self):
    data = self._api_call('homes/%i/installations' % self.id)
    return data

  def get_me(self):
    data = self._api_call('me')
    return data

  def get_mobile_devices(self):
    data = self._api_call('homes/%i/mobileDevices' % self.id)
    return data

  def get_schedule(self, zone):
    data = self._api_call('homes/%i/zones/%i/schedule/activeTimetable' % (self.id, zone))
    return data

  def get_state(self, zone):
    data = self._api_call('homes/%i/zones/%i/state' % (self.id, zone))
    return data

  def get_weather(self):
    data = self._api_call('homes/%i/weather' % self.id)
    return data

  def get_zones(self):
    data = self._api_call('homes/%i/zones' % self.id)
    return data
