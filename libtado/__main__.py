#! /usr/bin/env python3

import click
import libtado.api

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--username', '-u', required=True, envvar='TADO_USERNAME', help='Tado username')
@click.option('--password', '-p', required=True, envvar='TADO_PASSWORD', help='Tado password')
@click.option('--client-secret', '-c', required=True, envvar='TADO_CLIENT_SECRET', help='Tado client secret')
@click.pass_context
def main(ctx, username, password, client_secret):
  """
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
  click.echo(tado.get_home())


@main.command()
@click.pass_obj
def mobile(tado):
  """Display all mobile devices."""
  click.echo(tado.get_mobile_devices())


@main.command()
@click.pass_obj
def users(tado):
  """Display all users of your home."""
  click.echo(tado.get_users())


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
