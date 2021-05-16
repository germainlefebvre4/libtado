#! /usr/bin/env python3

import click
import datetime
from dateutil.parser import parse
from dateutil import tz
import libtado.api

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--username', '-u', required=True, envvar='TADO_USERNAME', help='Tado username')
@click.option('--password', '-p', required=True, envvar='TADO_PASSWORD', help='Tado password')
@click.option('--client-secret', '-c', required=True, envvar='TADO_CLIENT_SECRET', help='Tado client secret')
@click.pass_context
def main(ctx, username, password, client_secret):
  """
  Example
  =======
  This script provides a command line client for the Tado API.

  You can use the environment variables TADO_USERNAME, TADO_PASSWORD and
  TADO_CLIENT_SECRET instead of the command line options.

  Call 'tado COMMAND --help' to see available options for subcommands.
  """

  ctx.obj = libtado.api.Tado(username, password, client_secret)


@main.command()
@click.option('--zone', '-z', required=True, type=int, help='Zone ID')
@click.pass_obj
def capabilities(tado, zone):
  """Display the capabilities of a zone."""
  click.echo(tado.get_capabilities(zone))


@main.command(short_help='Display all devices.')
@click.pass_obj
def devices(tado):
  """
  Display all devices. If you have unsupported devices it will show you the
  JSON output.
  """
  devices = tado.get_devices()
  for d in devices:
    if d['deviceType'] == 'GW03':
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Operation: %s' % d['gatewayOperation'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
    elif d['deviceType'] == 'VA01':
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
      click.echo('Mounted: %s (%s)' % (d['mountingState']['value'], d['mountingState']['timestamp']))
    elif d['deviceType'] == 'IB01':
      # V2 internet bridge
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
      click.echo('Pairing: %s' % d['inPairingMode'])
    elif d['deviceType'] == 'VA02':
      # V2 smart radiator thermostat
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
      click.echo('Mounted: %s (%s)' % (d['mountingState']['value'], d['mountingState']['timestamp']))
      click.echo('Battery State: %s' % d['batteryState'])
    elif d['deviceType'] == 'RU02':
      # V2 smart wall theromstat
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
      click.echo('Battery State: %s' % d['batteryState'])
    elif d['deviceType'] == 'SU02':
      # Wireless Temperature Sensor
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
      click.echo('Battery State: %s' % d['batteryState'])
    elif d['deviceType'] == 'BR02':
      # Wireless Receiver
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
    else:
      click.secho('Device type %s not supported. Please report a bug with the following output.' % d['deviceType'], fg='black', bg='red')
      d['serialNo'] = 'XXX'
      d['shortSerialNo'] = 'XXX'
      click.echo(d)
    click.echo('')


@main.command(short_help='Display or change the early start feature of a zone.')
@click.option('--zone', '-z', required=True, type=int, help='Zone ID')
@click.option('--set', '-s', type=click.Choice(['on', 'off']))
@click.pass_obj
def early_start(tado, zone, set):
  """Display the current early start configuration of a zone or change it."""
  if set:
    if set == 'on':
      tado.set_early_start(zone, True)
    elif set == 'off':
      tado.set_early_start(zone, False)
  else:
    click.echo(tado.get_early_start(zone))


@main.command()
@click.pass_obj
def home(tado):
  """Display information about your home."""
  home= tado.get_home()
  click.echo('Home: %s (%i)' % (home['name'], home['id']))
  click.echo('Created: %s' % parse(home['dateCreated']).astimezone(tz.tzlocal()).strftime('%c'))
  click.echo('Installation Complete: %s' % home['installationCompleted'])
  click.echo(home)


@main.command()
@click.pass_obj
def mobile(tado):
  """Display all mobile devices."""
  click.echo(tado.get_mobile_devices())


@main.command()
@click.pass_obj
def users(tado):
  """Display all users of your home."""
  users = tado.get_users()
  for u in users:
    click.echo('User: %s <%s>' % (u['name'], u['email']))
  click.echo(users)


@main.command(short_help='Tell me who the Tado API thinks I am.')
@click.pass_obj
def whoami(tado):
  """
  This command authenticates against the Tado API and asks for details about
  the account you used to login. It is helpful to verify if your credentials
  work.
  """
  me = tado.get_me()
  click.echo('Name: %s' % me['name'])
  click.echo('E-Mail: %s' % me['email'])
  click.echo('Username: %s' % me['username'])
  click.echo('Locale: %s' % me['locale'])
  click.echo('Homes: %s' % me['homes'])
  click.echo('Mobile Devices: %s' % me['mobileDevices'])


@main.command(short_help='Get the current state of a zone.')
@click.option('--zone', '-z', required=True, type=int, help='Zone ID')
@click.pass_obj
def zone(tado, zone):
  """
  Get the current state of a zone. Including temperature, humidity and
  heating power.
  """
  zone = tado.get_state(zone)
  click.echo('Desired Temperature : %s' % zone['setting']['temperature']['celsius'])
  click.echo('Current Temperature: %s' % zone['sensorDataPoints']['insideTemperature']['celsius'])
  click.echo('Current Humidity: %s%%' % zone['sensorDataPoints']['humidity']['percentage'])
  click.echo('Heating Power : %s%%' % zone['activityDataPoints']['heatingPower']['percentage'])
  click.echo('Mode : %s' % zone['tadoMode'])
  click.echo('Link : %s' % zone['link']['state'])

@main.command(short_help='Show current status.')
@click.pass_obj
def status(tado):
  """
  Show the current home status in a list form
  """

  def time_str(time_str):
    given_time = parse(time_str).astimezone(tz.tzlocal())
    now = datetime.datetime.now().replace(tzinfo=tz.tzlocal())

    if (given_time - now).days < 1:
      return given_time.strftime('%H:%M') # As Time
    elif (given_time - now).days < 7:
      return given_time.strftime('%A') # Monday,..
    else:
      return given_time.strftime('%Y-%-m-%-d') # Date

  def show_heating(st):
    zone = i['id']

    cur_temp = st['sensorDataPoints']['insideTemperature']['celsius']
    cur_hum = st['sensorDataPoints']['humidity']['percentage']

    if st['link']['state'] != 'ONLINE':
      setting = '-x-'  # Disconnected in tado-style
    elif st['setting']['power'] != 'ON':
      setting = st['setting']['power']
    else:
      setting = '%4.1fC' % (st['setting']['temperature']['celsius'])

    type_s = ''
    if st['overlayType'] and st['tadoMode'] != 'AWAY':
      type_s = st['overlayType']
    elif st['tadoMode'] != 'HOME':
      type_s = st['tadoMode'];

    next_s = ''
    if st['tadoMode'] != 'AWAY':
      if st['overlay'] != None:
        if 'termination' in st['overlay'] and st['overlay']['termination']['type'] == 'MANUAL':
          next_s = '-+-'
        elif st['overlay']['termination']['projectedExpiry'] != None:
          next_s = '-' + ('%s' % time_str(st['overlay']['termination']['projectedExpiry']))
        else:
          next_s = '-+-'
      elif st['nextScheduleChange'] != None:
        next_s = '-' + ('%s' % time_str(st['nextScheduleChange']['start']))

    extra = ''
    if st['openWindow'] != None:
      extra += ' Window open'
    for d in i['devices']:
      if d['batteryState'] != 'NORMAL':
        extra += ' Battery %s' % d['batteryState']

    heat_s = int(st['activityDataPoints']['heatingPower']['percentage'])
    if heat_s == 0:
      heat_s = ''
    else:
      heat_s = '%i%%' % heat_s

    click.echo('%-14s %2d %3s %5s %-8s %6s  %3.2fC %3.1f%%%s' % (
      i['name'], zone, heat_s, setting, next_s, type_s, cur_temp, cur_hum, extra))

  def show_hot_water(st):
    zone = i['id']

    if st['link']['state'] != 'ONLINE':
      setting = '-x-'  # Disconnected in tado-style
    elif st['setting']['power'] != 'ON':
      setting = st['setting']['power']
    else:
      setting = '%4.1fC' % (st['setting']['temperature']['celsius'])

    type_s = ''
    if st['overlayType'] and st['tadoMode'] != 'AWAY':
      type_s = st['overlayType']
    elif st['tadoMode'] != 'HOME':
      type_s = st['tadoMode'];

    next_s = ''
    if st['tadoMode'] != 'AWAY':
      if st['overlay'] != None:
        if 'termination' in st['overlay'] and st['overlay']['termination']['type'] == 'MANUAL':
          next_s = '-+-'
        elif st['overlay']['termination']['projectedExpiry'] != None:
          next_s = '-' + ('%s' % time_str(st['overlay']['termination']['projectedExpiry']))
        else:
          next_s = '-+-'
      elif st['nextScheduleChange'] != None:
        next_s = '-' + ('%s' % time_str(st['nextScheduleChange']['start']))

    extra = ''
    if st['openWindow'] != None:
      extra += ' Window open'
    for d in i['devices']:
      if d['batteryState'] != 'NORMAL':
        extra += ' Battery %s' % d['batteryState']

    click.echo('%-14s %2d %3s %5s %-8s %6s  %6s %5s%s' % (
      i['name'], zone, '', setting, next_s, type_s, '', '', extra))

  zone_info = tado.get_zones()

  for i in zone_info:
    st = tado.get_state(i['id'])
    if i['type'] == 'HEATING':
      show_heating(st)
    elif i['type'] == 'HOT_WATER':
      show_hot_water(st)


@main.command(short_help='Get configuration information about all zones.')
@click.pass_obj
def zones(tado):
  """Get configuration information about all zones."""
  zones = tado.get_zones()
  for zone in zones:
    click.secho('%s (ID: %s)' % (zone['name'], zone['id']), fg='green', bg='black')
    click.echo('Created: %s' % zone['dateCreated'])
    click.echo('Type: %s' % zone['type'])
    click.echo('Device Types: %s' % ', '.join(zone['deviceTypes']))
    click.echo('Devices: %i' % len(zone['devices']))
    click.echo('Dazzle: %s' % zone['dazzleEnabled'])


@main.command()
@click.option('--zone', '-z', required=True, type=int, help='Zone ID')
@click.option('--temperature', '-t', required=True, type=int, help='Temperature')
@click.option('--termination', '-x', default='MANUAL', help='Termination settings')
@click.pass_obj
def set_temperature(tado, zone, temperature, termination):
  """Set the desired temperature of a zone."""
  tado.set_temperature(zone, temperature, termination=termination)


@main.command()
@click.option('--zone', '-z', required=True, type=int, help='Zone ID')
@click.pass_obj
def end_manual_control(tado, zone):
  """End manual control of a zone."""
  tado.end_manual_control(zone)


if __name__ == "__main__":
  main()
