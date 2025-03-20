#! /usr/bin/env python3

import click
import datetime
import time
from dateutil.parser import parse
from dateutil import tz
import libtado.api
from libtado.cli_utils import MutuallyExclusiveOption


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--refresh-token', '-t', required=False, envvar='TADO_REFRESH_TOKEN', cls=MutuallyExclusiveOption, help='A Tado refresh token, retrieved from prior authentication with Tado', mutually_exclusive=["credentials_file"])
@click.option('--credentials-file', '-f', required=False, envvar='TADO_CREDENTIALS_FILE', cls=MutuallyExclusiveOption, help='Full path to a file in which the Tado credentials will be stored and read from', mutually_exclusive=["refresh_token"])
@click.pass_context
def main(ctx, refresh_token, credentials_file):
  """
  Example
  =======
  This script provides a command line client for the Tado API.

  You can use the environment variables TADO_REFRESH_TOKEN and
  TADO_CREDENTIALS_FILE instead of the command line options.

  The first time you will have to login using a browser. The command
  will show an URL to perform the login.

  If using the credentials-file option or variable, the login will
  be stored so you don't have to do this next time.

  Call 'tado COMMAND --help' to see available options for subcommands.
  """

  ctx.obj = libtado.api.Tado(refresh_token, credentials_file)
  status = ctx.obj.get_device_activation_status()
  if status == "PENDING":
      ctx.obj.device_activation()


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
    elif d['deviceType'] == 'VA02E':
      # V2 smart radiator thermostat Basic
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
      click.echo('Mounted: %s (%s)' % (d['mountingState']['value'], d['mountingState']['timestamp']))
      click.echo('Battery State: %s' % d['batteryState'])
    elif d['deviceType'] == 'RU01':
      # V2 smart wall theromstat
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
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
      click.echo('Battery State: %s' % d['batteryState'])
    elif d['deviceType'] == 'BU01':
      # ???
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
    elif d['deviceType'] == 'WR01':
      # Smart AC
      click.echo('Serial: %s' % d['serialNo'])
      click.echo('Type: %s' % d['deviceType'])
      click.echo('Firmware: %s' % d['currentFwVersion'])
      click.echo('Connection: %s (%s)' % (d['connectionState']['value'], d['connectionState']['timestamp']))
    elif d['deviceType'] == 'WR02':
      # Smart AC
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
      type_s = st['tadoMode']

    next_s = ''
    if st['tadoMode'] != 'AWAY':
      if st['overlay'] is not None:
        if 'termination' in st['overlay'] and st['overlay']['termination']['type'] == 'MANUAL':
          next_s = '-+-'
        elif st['overlay']['termination']['projectedExpiry'] is not None:
          next_s = '-' + ('%s' % time_str(st['overlay']['termination']['projectedExpiry']))
        else:
          next_s = '-+-'
      elif st['nextScheduleChange'] is not None:
        next_s = '-' + ('%s' % time_str(st['nextScheduleChange']['start']))

    extra = ''
    if st['openWindow'] is not None:
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
      type_s = st['tadoMode']

    next_s = ''
    if st['tadoMode'] != 'AWAY':
      if st['overlay'] is not None:
        if 'termination' in st['overlay'] and st['overlay']['termination']['type'] == 'MANUAL':
          next_s = '-+-'
        elif st['overlay']['termination']['projectedExpiry'] is not None:
          next_s = '-' + ('%s' % time_str(st['overlay']['termination']['projectedExpiry']))
        else:
          next_s = '-+-'
      elif st['nextScheduleChange'] is not None:
        next_s = '-' + ('%s' % time_str(st['nextScheduleChange']['start']))

    extra = ''
    if st['openWindow'] is not None:
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


@main.command()
@click.pass_obj
def heating_system(tado):
  """Display heating systems status of your home.."""
  heating_system = tado.get_heating_system()
  if heating_system['boiler']['present']:
    click.echo('Boiler: Present')
    click.echo('  Found: %s' % heating_system['boiler']['found'])
    click.echo('  ID: %s' % heating_system['boiler']['id'])
  else:
    click.echo('Boiler: Absent')
  if heating_system['underfloorHeating']['present']:
    click.echo('Underfloor Heating: Present')
    click.echo('  Found: %s' % heating_system['underfloorHeating']['found'])
    click.echo('  ID: %s' % heating_system['underfloorHeating']['id'])
  else:
    click.echo('Underfloor Heating: Absent')


@main.command()
@click.pass_obj
@click.option('--from-date', '-d', required=False, type=str, help='From date')
def heating_running_times(tado, from_date):
  """Display heating system running times of your home."""
  if not from_date:
    from_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
  running_times = tado.get_running_times(from_date)

  click.echo('Heating running times from %s' % from_date)

  click.echo('Summary:')
  click.echo('  Total Running Time (seconds): %s' % running_times['summary']['totalRunningTimeInSeconds'])
  click.echo('')

  click.echo('Running time from date to date (seconds)')
  for rt in running_times['runningTimes']:
    click.echo('From %s to %s' % (rt['startTime'][:-9], rt['endTime'][:-9]))
    click.echo('  Global: %s' % rt["runningTimeInSeconds"])
    click.echo('  By zone:')
    for zone in rt['zones']:
      click.echo('    %s: %s' % (zone['id'], zone['runningTimeInSeconds']))


@main.command()
@click.pass_obj
def zone_states(tado):
  """Get the states of a zone."""
  zone_states = tado.get_zone_states()
  # print(zone_states)

  for zone,state in zone_states['zoneStates'].items():
    # print(zone)
    # print(state)
    click.echo('Zone %s:' % (zone))
    click.echo('  Mode: %s' % (state['tadoMode']))
    click.echo('  Heating:')
    click.echo('    Power: %s' % (state['setting']['power']))
    click.echo('    Temperature (celsius): %s' % (state['setting']['temperature']['celsius']))
    click.echo('  Humidity (percent): %s' % (state['sensorDataPoints']['humidity']['percentage']))


@main.command()
@click.pass_obj
@click.option('--from-date', '-df', required=True, type=str, help='From date')
@click.option('--to-date', '-dt', required=True, type=str, help='To date')
@click.option('--country', '-c', required=True, type=str, help='Country code')
@click.option('--ngsw-bypass', '-ng', required=False, type=bool, help='NGSW Bypass')
def energy_consumption(tado, from_date, to_date, country, ngsw_bypass=True):
  """Get the energy consumption of your home."""
  # if not from_date:
  #   from_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

  energy_consumption = tado.get_energy_consumption(from_date, to_date, country, ngsw_bypass)

  click.echo('Energy consumption from %s to %s' % (from_date, to_date))
  click.echo('')

  click.echo('Summary:')
  click.echo('  Total Consumption (%s): %s' % (energy_consumption['tariffInfo']['consumptionUnit'], energy_consumption['details']['totalConsumption']))
  click.echo('  Total Cost (%s): %s' % (energy_consumption['currency'], energy_consumption['details']['totalCostInCents']))
  click.echo('')

  click.echo('Consumption from day to day:')
  for rt in energy_consumption['details']['perDay']:
    click.echo('  Day %s ' % (rt['date']))
    click.echo('    Consumption: %s' % rt["consumption"])
    click.echo('    Cost (%s): %s' % (energy_consumption['currency'], rt["costInCents"]))


@main.command()
@click.pass_obj
@click.option('--month-date', '-d', required=True, type=str, help='Month year (i.e. 2022-09)')
@click.option('--country', '-c', required=True, type=str, help='Country code')
@click.option('--ngsw-bypass', '-ng', required=False, type=bool, help='NGSW Bypass')
def energy_savings(tado, month_date, country, ngsw_bypass=True):
  """Get the energy savings of your home."""

  energy_savings = tado.get_energy_savings(month_date, country, ngsw_bypass)

  click.echo('Energy savings for %s' % (energy_savings['yearMonth']))
  click.echo('')

  click.echo('Total savings (%s): %s' % (energy_savings['totalSavings']['unit'].lower(), energy_savings['totalSavings']['value']))
  click.echo('')

  click.echo('Sunshine duration (%s): %s' % (energy_savings['sunshineDuration']['unit'].lower(), energy_savings['sunshineDuration']['value']))
  click.echo('Manual control saving (%s): %s' % (energy_savings['manualControlSaving']['unit'].lower(), energy_savings['manualControlSaving']['value']))
  click.echo('Away duration (%s): %s' % (energy_savings['awayDuration']['unit'].lower(), energy_savings['awayDuration']['value']))
  click.echo('Setback schedule duration per day (%s): %s' % (energy_savings['setbackScheduleDurationPerDay']['unit'].lower(), energy_savings['setbackScheduleDurationPerDay']['value']))
  click.echo('Total savings in thermostatic mode (%s): %s' % (energy_savings['totalSavingsInThermostaticMode']['unit'].lower(), energy_savings['totalSavingsInThermostaticMode']['value']))
  click.echo('')

  click.echo('Auto-assit:')
  click.echo('  Auto-assist enabled: %s' % (energy_savings['hasAutoAssist']))
  click.echo('  Open window detection times: %s' % (energy_savings['withAutoAssist']['openWindowDetectionTimes']))
  click.echo('  Detected duration (%s): %s' % (energy_savings['withAutoAssist']['detectedAwayDuration']['unit'].lower(), energy_savings['withAutoAssist']['detectedAwayDuration']['value']))
  click.echo('')


@main.command()
@click.pass_obj
@click.option('--zone', '-z', required=True, type=int, help='Zone ID')
@click.option('--schedule', '-s', required=True, type=int, help='Schedule ID')
def schedule_blocks(tado, zone, schedule):
  """Get the schedule blocks of a zone."""
  schedule_blocks = tado.get_schedule_blocks(zone, schedule)

  click.echo('Schedule blocks for zone %s and schedule %s' % (zone, schedule))
  click.echo('')

  click.echo('Schedule blocks:')
  for sb in schedule_blocks:
    click.echo('  Day type: %s' % (sb['dayType']))
    click.echo('  Start: %s' % (sb['start']))
    click.echo('  End: %s' % (sb['end']))
    click.echo('  Setting:')
    click.echo('    Power: %s' % (sb['setting']['power']))
    click.echo('    Temperature (celsius): %s' % (sb['setting']['temperature']['celsius']))
    click.echo('')


@main.command()
@click.pass_obj
@click.option('--zone', '-z', required=True, type=int, help='Zone ID')
@click.option('--schedule', '-s', required=True, type=int, help='Schedule ID')
@click.option('--day-type', '-d', required=True, type=str, help='Day type')
def schedule_block_day_type(tado, zone, schedule, day_type):
  """Get the day type schedule block of a zone."""
  schedule_block_by_day_type = tado.get_schedule_block_by_day_type(zone, schedule, day_type)

  click.echo('Schedule blocks for zone %s and schedule %s' % (zone, schedule))
  click.echo('')

  click.echo('Day type: %s' % (schedule_block_by_day_type[0]['dayType']))
  click.echo('')

  click.echo('Schedule day type blocks:')
  for sb in schedule_block_by_day_type:
    click.echo('  Start: %s' % (sb['start']))
    click.echo('  End: %s' % (sb['end']))
    click.echo('  Setting:')
    click.echo('    Power: %s' % (sb['setting']['power']))
    click.echo('    Temperature (celsius): %s' % (sb['setting']['temperature']['celsius']))
    click.echo('')


@main.command()
@click.pass_obj
@click.option('--month-date', '-d', required=True, type=str, help='Month year (i.e. 2022-09)')
def consumption_details(tado, month_date):
  """Get the consumption details of your home."""
  consumption_details = tado.get_consumption_details(month_date)

  click.echo('Consumption for %s' % (month_date))
  click.echo('')

  click.echo('Summary:')
  click.echo('  Consumption (%s): %d' % (consumption_details['summary']['unit'], consumption_details['summary']['consumption']))
  click.echo('  Cost: %.2f' % (consumption_details['summary']['costInCents']/100))
  click.echo('')

  click.echo('Details:')
  for cd in consumption_details['graphConsumption']['monthlyAggregation']['requestedMonth']['consumptionPerDate']:
    click.echo('  %s\tConsumption (%s): %s\t\tCost: %.2f' % (cd['date'], consumption_details['graphConsumption']['unit'], cd['consumption'], cd['costInCents']/100))


if __name__ == "__main__":
  main()
