import os
import time
from libtado.api import Tado

import pytest

TADO_USERNAME = os.getenv("TADO_USERNAME")
TADO_PASSWORD = os.getenv("TADO_PASSWORD")
TADO_SECRET = os.getenv("TADO_SECRET")


global t

@pytest.fixture(scope='session', autouse=True)
def before_starting():
    global t
    t = Tado(TADO_USERNAME, TADO_PASSWORD, TADO_SECRET)

def test_auth():
    assert t.get_me()

def test_zones():
    r = t.get_home()
    assert r
    assert r['name'] == "Domicile"

def test_installations():
    r = t.get_installations()
    assert isinstance(r, list)

def test_invitations():
    r = t.get_invitations()
    assert r
    assert r[0]['inviter']['name'] == "Germain Lefebvre"

def test_me():
    r = t.get_me()
    assert r
    assert r['name'] == "Germain Lefebvre"

def test_mobile_devices():
    r = t.get_mobile_devices()
    assert r

def test_report():
    zone = t.get_zones()[0]['id']
    r = t.get_report(zone, "2020-10-04")
    assert r
    assert "interval" in r.keys()

def test_schedule():
    zone = t.get_zones()[0]['id']
    r = t.get_schedule(zone)
    assert r
    assert r['id'] == 0

def test_state():
    zone = t.get_zones()[0]['id']
    r = t.get_state(zone)
    assert r
    assert "tadoMode" in r.keys()

def test_users():
    r = t.get_users()
    assert len([x for x in r if x['name'] == "Germain Lefebvre"]) >  0

def test_weather():
    r = t.get_weather()
    assert r
    assert "solarIntensity" in r.keys()

def test_mobile_devices():
    r = t.get_mobile_devices()
    assert r
    assert len(r) > 0
    assert r[0]['name'] == "Germain"

def test_zones():
    r = t.get_zones()
    assert r
    assert len(r) > 0
    assert r[0]['id'] == 1
    assert r[0]['name'] == "Maison"