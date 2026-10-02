import json

import pytest
import requests
import responses

API_BASE = "https://my.tado.com/api/v2"
ACME_BASE = "https://acme.tado.com/v1"
MINDER_BASE = "https://minder.tado.com/v1"
ENERGY_INSIGHTS_BASE = "https://energy-insights.tado.com/api"
ENERGY_BOB_BASE = "https://energy-bob.tado.com"

HOME_ID = 12345


def api_url(path):
    return f"{API_BASE}/{path}"


def acme_url(path):
    return f"{ACME_BASE}/{path}"


def minder_url(path):
    return f"{MINDER_BASE}/{path}"


def energy_insights_url(path):
    return f"{ENERGY_INSIGHTS_BASE}/{path}"


def energy_bob_url(path):
    return f"{ENERGY_BOB_BASE}/{path}"


# `_api_call` GET methods, per tasks.md 3.1.
GET_API_CALL_METHODS = [
    ("get_capabilities", (10,), f"homes/{HOME_ID}/zones/10/capabilities"),
    ("get_devices", (), f"homes/{HOME_ID}/devices"),
    ("get_device_usage", (), f"homes/{HOME_ID}/deviceList"),
    ("get_early_start", (10,), f"homes/{HOME_ID}/zones/10/earlyStart"),
    ("get_home", (), f"homes/{HOME_ID}"),
    ("get_home_state", (), f"homes/{HOME_ID}/state"),
    ("get_invitations", (), f"homes/{HOME_ID}/invitations"),
    ("get_me", (), "me"),
    ("get_mobile_devices", (), f"homes/{HOME_ID}/mobileDevices"),
    ("get_schedule_timetables", (10,), f"homes/{HOME_ID}/zones/10/schedule/timetables"),
    ("get_schedule", (10,), f"homes/{HOME_ID}/zones/10/schedule/activeTimetable"),
    ("get_schedule_blocks", (10, 1), f"homes/{HOME_ID}/zones/10/schedule/timetables/1/blocks"),
    (
        "get_schedule_block_by_day_type",
        (10, 1, "MONDAY"),
        f"homes/{HOME_ID}/zones/10/schedule/timetables/1/blocks/MONDAY",
    ),
    ("get_state", (10,), f"homes/{HOME_ID}/zones/10/state"),
    ("get_measuring_device", (10,), f"homes/{HOME_ID}/zones/10/measuringDevice"),
    ("get_default_overlay", (10,), f"homes/{HOME_ID}/zones/10/defaultOverlay"),
    ("get_users", (), f"homes/{HOME_ID}/users"),
    ("get_weather", (), f"homes/{HOME_ID}/weather"),
    ("get_zones", (), f"homes/{HOME_ID}/zones"),
    ("get_away_configuration", (10,), f"homes/{HOME_ID}/zones/10/awayConfiguration"),
    ("get_report", (10, "2024-01-01"), f"homes/{HOME_ID}/zones/10/dayReport?date=2024-01-01"),
    ("get_heating_circuits", (), f"homes/{HOME_ID}/heatingCircuits"),
    ("get_installations", (), f"homes/{HOME_ID}/installations"),
    ("get_temperature_offset", ("SERIAL123",), "devices/SERIAL123/temperatureOffset"),
]

# Remaining `_api_call` GET methods not covered by 3.1's explicit list, per tasks.md 4.5.
GET_API_CALL_METHODS_UNLISTED = [
    ("get_air_comfort", (), f"homes/{HOME_ID}/airComfort"),
    ("get_heating_system", (), f"homes/{HOME_ID}/heatingSystem"),
    ("get_zone_states", (), f"homes/{HOME_ID}/zoneStates"),
]


@pytest.mark.parametrize(
    "method_name, args, path", GET_API_CALL_METHODS + GET_API_CALL_METHODS_UNLISTED
)
def test_api_call_get_method(tado_unauthenticated, mocked_responses, method_name, args, path):
    payload = {"result": "ok"}
    mocked_responses.add(responses.GET, api_url(path), json=payload, status=200)

    result = getattr(tado_unauthenticated, method_name)(*args)

    assert result == payload
    assert mocked_responses.calls[0].request.url == api_url(path)


class TestApiCallMutations:
    """`_api_call` set_*/delete_* methods, per tasks.md 3.2."""

    def test_set_home_state_home(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.PUT, api_url(f"homes/{HOME_ID}/presenceLock"), status=204)

        tado_unauthenticated.set_home_state(True)

        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"homePresence": "HOME"}

    def test_set_home_state_away(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.PUT, api_url(f"homes/{HOME_ID}/presenceLock"), status=204)

        tado_unauthenticated.set_home_state(False)

        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"homePresence": "AWAY"}

    def test_set_invitation(self, tado_unauthenticated, mocked_responses):
        response_payload = {"token": "abc", "email": "a@b.com"}
        mocked_responses.add(
            responses.POST, api_url(f"homes/{HOME_ID}/invitations"), json=response_payload, status=200
        )

        result = tado_unauthenticated.set_invitation("a@b.com")

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"email": "a@b.com"}

    def test_delete_invitation_204(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(
            responses.DELETE, api_url(f"homes/{HOME_ID}/invitations/TOKEN123"), status=204
        )

        result = tado_unauthenticated.delete_invitation("TOKEN123")

        assert result is None

    def test_delete_invitation_200(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(
            responses.DELETE,
            api_url(f"homes/{HOME_ID}/invitations/TOKEN123"),
            json={"deleted": True},
            status=200,
        )

        result = tado_unauthenticated.delete_invitation("TOKEN123")

        assert result == {"deleted": True}

    def test_set_schedule(self, tado_unauthenticated, mocked_responses):
        response_payload = {"id": 1, "type": "THREE_DAY"}
        mocked_responses.add(
            responses.PUT,
            api_url(f"homes/{HOME_ID}/zones/10/schedule/activeTimetable"),
            json=response_payload,
            status=200,
        )

        result = tado_unauthenticated.set_schedule(10, 1)

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"id": 1}

    def test_set_schedule_blocks(self, tado_unauthenticated, mocked_responses):
        blocks = [{"dayType": "MONDAY_TO_SUNDAY", "start": "00:00", "end": "24:00"}]
        response_payload = {"acknowledged": True}
        mocked_responses.add(
            responses.PUT,
            api_url(f"homes/{HOME_ID}/zones/10/schedule/timetables/0/blocks/MONDAY_TO_SUNDAY"),
            json=response_payload,
            status=200,
        )

        result = tado_unauthenticated.set_schedule_blocks(10, 0, blocks)

        assert result == [response_payload]
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == blocks

    def test_set_schedule_blocks_invalid_schedule(self, tado_unauthenticated, mocked_responses, capsys):
        result = tado_unauthenticated.set_schedule_blocks(10, 99, [])

        assert result is None
        assert len(mocked_responses.calls) == 0

    def test_set_schedule_block_by_day_type_delegates(self, tado_unauthenticated, mocked_responses):
        blocks = [{"dayType": "MONDAY_TO_SUNDAY", "start": "00:00", "end": "24:00"}]
        response_payload = {"acknowledged": True}
        mocked_responses.add(
            responses.PUT,
            api_url(f"homes/{HOME_ID}/zones/10/schedule/timetables/0/blocks/MONDAY_TO_SUNDAY"),
            json=response_payload,
            status=200,
        )

        result = tado_unauthenticated.set_schedule_block_by_day_type(10, 0, "MONDAY_TO_SUNDAY", blocks)

        assert result == [response_payload]

    def test_set_zone_name(self, tado_unauthenticated, mocked_responses):
        response_payload = {"name": "Kitchen"}
        mocked_responses.add(
            responses.PUT, api_url(f"homes/{HOME_ID}/zones/10/details"), json=response_payload, status=200
        )

        result = tado_unauthenticated.set_zone_name(10, "Kitchen")

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"name": "Kitchen"}

    def test_set_early_start_enabled(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(
            responses.PUT, api_url(f"homes/{HOME_ID}/zones/10/earlyStart"), json={"enabled": True}, status=200
        )

        result = tado_unauthenticated.set_early_start(10, True)

        assert result == {"enabled": True}
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"enabled": "true"}

    def test_set_early_start_disabled(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(
            responses.PUT, api_url(f"homes/{HOME_ID}/zones/10/earlyStart"), json={"enabled": False}, status=200
        )

        tado_unauthenticated.set_early_start(10, False)

        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"enabled": "false"}

    def test_set_temperature(self, tado_unauthenticated, mocked_responses):
        response_payload = {"setting": {"power": "ON"}}
        mocked_responses.add(
            responses.PUT, api_url(f"homes/{HOME_ID}/zones/10/overlay"), json=response_payload, status=200
        )

        result = tado_unauthenticated.set_temperature(10, 21.0)

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {
            "setting": {"type": "HEATING", "power": "ON", "temperature": {"celsius": 21.0}},
            "termination": {"type": "MANUAL"},
        }

    def test_set_temperature_below_min_turns_off(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.PUT, api_url(f"homes/{HOME_ID}/zones/10/overlay"), json={}, status=200)

        tado_unauthenticated.set_temperature(10, 3, termination="AUTO")

        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {
            "setting": {"type": "HEATING", "power": "OFF"},
            "termination": {"type": "TADO_MODE"},
        }

    def test_set_temperature_timer_termination(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.PUT, api_url(f"homes/{HOME_ID}/zones/10/overlay"), json={}, status=200)

        tado_unauthenticated.set_temperature(10, 19.5, termination=600)

        body = json.loads(mocked_responses.calls[0].request.body)
        assert body["termination"] == {"type": "TIMER", "durationInSeconds": 600}

    def test_end_manual_control(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.DELETE, api_url(f"homes/{HOME_ID}/zones/10/overlay"), status=204)

        result = tado_unauthenticated.end_manual_control(10)

        assert result is None

    def test_set_away_configuration(self, tado_unauthenticated, mocked_responses):
        response_payload = {"type": "HEATING"}
        mocked_responses.add(
            responses.PUT,
            api_url(f"homes/{HOME_ID}/zones/10/awayConfiguration"),
            json=response_payload,
            status=200,
        )

        result = tado_unauthenticated.set_away_configuration(10, "HEATING", "ECO", 16.0)

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {
            "type": "HEATING",
            "preheatingLevel": "ECO",
            "minimumAwayTemperature": {"celsius": 16.0},
        }

    def test_set_open_window_detection(self, tado_unauthenticated, mocked_responses):
        response_payload = {"enabled": True}
        mocked_responses.add(
            responses.PUT,
            api_url(f"homes/{HOME_ID}/zones/10/openWindowDetection"),
            json=response_payload,
            status=200,
        )

        result = tado_unauthenticated.set_open_window_detection(10, True, 600)

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"enabled": True, "timeoutInSeconds": 600}

    def test_set_incident_detection(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.PUT, api_url(f"homes/{HOME_ID}/incidentDetection"), status=204)

        result = tado_unauthenticated.set_incident_detection(True)

        assert result is None
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"enabled": True}

    def test_set_temperature_offset(self, tado_unauthenticated, mocked_responses):
        response_payload = {"celsius": 0.5}
        mocked_responses.add(
            responses.PUT, api_url("devices/SERIAL123/temperatureOffset"), json=response_payload, status=200
        )

        result = tado_unauthenticated.set_temperature_offset("SERIAL123", 0.5)

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == {"celsius": 0.5}

    def test_set_heating_system_boiler(self, tado_unauthenticated, mocked_responses):
        payload = {"present": True, "found": True, "id": "17830"}
        mocked_responses.add(responses.PUT, api_url(f"homes/{HOME_ID}/heatingSystem/boiler"), status=204)

        result = tado_unauthenticated.set_heating_system_boiler(payload)

        assert result is None
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == payload

    def test_set_zone_order(self, tado_unauthenticated, mocked_responses):
        payload = [{"id": 1}, {"id": 6}]
        mocked_responses.add(
            responses.PUT, api_url(f"homes/{HOME_ID}/zoneOrder?ngsw-bypass=True"), json=payload, status=200
        )

        result = tado_unauthenticated.set_zone_order(payload)

        assert result == payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == payload


class TestApiCallErrorHandlingAndRateLimit:
    """`_api_call` error handling and rate-limit propagation, per tasks.md 3.3."""

    def test_get_error_4xx(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.GET, api_url(f"homes/{HOME_ID}/zones"), status=404)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_zones()

    def test_get_error_5xx(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.GET, api_url(f"homes/{HOME_ID}/zones"), status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_zones()

    def test_put_error(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.PUT, api_url(f"homes/{HOME_ID}/zones/10/details"), status=400)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.set_zone_name(10, "Kitchen")

    def test_post_error(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.POST, api_url(f"homes/{HOME_ID}/invitations"), status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.set_invitation("a@b.com")

    def test_delete_error(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.DELETE, api_url(f"homes/{HOME_ID}/invitations/TOKEN123"), status=404)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.delete_invitation("TOKEN123")

    def test_rate_limit_header_propagation(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(
            responses.GET,
            api_url(f"homes/{HOME_ID}/zones"),
            json=[],
            status=200,
            headers={
                "ratelimit-policy": '"perday";q=20000;w=86400',
                "ratelimit": '"perday";r=15500;t=123',
            },
        )

        tado_unauthenticated.get_zones()

        info = tado_unauthenticated.get_rate_limit_info()
        assert info.granted_calls == 20000
        assert info.remaining_calls == 15500


class TestApiAcmeCall:
    """`_api_acme_call`, per tasks.md 4.1."""

    def test_get_air_comfort_geoloc_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"roomMessages": []}
        url = acme_url(f"homes/{HOME_ID}/airComfort?latitude=50.631201&longitude=2.907079")
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_air_comfort_geoloc(50.6312013, 2.9070787)

        assert result == response_payload

    def test_get_air_comfort_geoloc_error(self, tado_unauthenticated, mocked_responses):
        url = acme_url(f"homes/{HOME_ID}/airComfort?latitude=50.631201&longitude=2.907079")
        mocked_responses.add(responses.GET, url, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_air_comfort_geoloc(50.6312013, 2.9070787)


class TestApiMinderCall:
    """`_api_minder_call`, per tasks.md 4.2."""

    def test_get_incidents_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"incidents": []}
        mocked_responses.add(responses.GET, minder_url(f"homes/{HOME_ID}/incidents"), json=response_payload, status=200)

        result = tado_unauthenticated.get_incidents()

        assert result == response_payload

    def test_get_incidents_error(self, tado_unauthenticated, mocked_responses):
        mocked_responses.add(responses.GET, minder_url(f"homes/{HOME_ID}/incidents"), status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_incidents()

    def test_get_running_times_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"runningTimes": []}
        url = minder_url(f"homes/{HOME_ID}/runningTimes?from=2024-01-01")
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_running_times("2024-01-01")

        assert result == response_payload

    def test_get_running_times_error(self, tado_unauthenticated, mocked_responses):
        url = minder_url(f"homes/{HOME_ID}/runningTimes?from=2024-01-01")
        mocked_responses.add(responses.GET, url, status=404)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_running_times("2024-01-01")


class TestApiEnergyInsightsCall:
    """`_api_energy_insights_call`, per tasks.md 4.3."""

    def test_get_energy_consumption_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"unit": "m3"}
        url = energy_insights_url(
            f"homes/{HOME_ID}/consumption?startDate=2024-01-01&endDate=2024-01-31&country=FRA&ngsw-bypass=True"
        )
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_energy_consumption("2024-01-01", "2024-01-31", "FRA")

        assert result == response_payload

    def test_get_energy_consumption_error(self, tado_unauthenticated, mocked_responses):
        url = energy_insights_url(
            f"homes/{HOME_ID}/consumption?startDate=2024-01-01&endDate=2024-01-31&country=FRA&ngsw-bypass=True"
        )
        mocked_responses.add(responses.GET, url, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_energy_consumption("2024-01-01", "2024-01-31", "FRA")

    def test_set_cost_simulation_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"consumptionUnit": "m3"}
        url = energy_insights_url(f"homes/{HOME_ID}/costSimulator?country=FRA&ngsw-bypass=True")
        mocked_responses.add(responses.POST, url, json=response_payload, status=200)
        payload = {"temperatureDeltaPerZone": [{"zone": 1, "setTemperatureDelta": -1}]}

        result = tado_unauthenticated.set_cost_simulation("FRA", payload=payload)

        assert result == response_payload
        body = json.loads(mocked_responses.calls[0].request.body)
        assert body == payload

    def test_set_cost_simulation_error(self, tado_unauthenticated, mocked_responses):
        url = energy_insights_url(f"homes/{HOME_ID}/costSimulator?country=FRA&ngsw-bypass=True")
        mocked_responses.add(responses.POST, url, status=400)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.set_cost_simulation("FRA", payload={"temperatureDeltaPerZone": []})

    def test_get_consumption_overview_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"unit": "m3"}
        url = energy_insights_url(f"homes/{HOME_ID}/consumptionOverview?month=2024-01&country=FRA&ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_consumption_overview("2024-01", "FRA")

        assert result == response_payload

    def test_get_consumption_overview_error(self, tado_unauthenticated, mocked_responses):
        url = energy_insights_url(f"homes/{HOME_ID}/consumptionOverview?month=2024-01&country=FRA&ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_consumption_overview("2024-01", "FRA")

    def test_get_consumption_details_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"isInPreferredUnit": True}
        url = energy_insights_url(f"homes/{HOME_ID}/consumptionDetails?month=2024-01&ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_consumption_details("2024-01")

        assert result == response_payload

    def test_get_consumption_details_error(self, tado_unauthenticated, mocked_responses):
        url = energy_insights_url(f"homes/{HOME_ID}/consumptionDetails?month=2024-01&ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_consumption_details("2024-01")

    def test_get_energy_settings_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"homeId": HOME_ID}
        url = energy_insights_url(f"homes/{HOME_ID}/settings?ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_energy_settings()

        assert result == response_payload

    def test_get_energy_settings_error(self, tado_unauthenticated, mocked_responses):
        url = energy_insights_url(f"homes/{HOME_ID}/settings?ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_energy_settings()

    def test_get_energy_insights_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"costForecast": {}}
        url = energy_insights_url(
            f"homes/{HOME_ID}/insights?startDate=2024-01-01&endDate=2024-01-31&country=FRA&ngsw-bypass=True"
        )
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_energy_insights("2024-01-01", "2024-01-31", "FRA")

        assert result == response_payload

    def test_get_energy_insights_error(self, tado_unauthenticated, mocked_responses):
        url = energy_insights_url(
            f"homes/{HOME_ID}/insights?startDate=2024-01-01&endDate=2024-01-31&country=FRA&ngsw-bypass=True"
        )
        mocked_responses.add(responses.GET, url, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_energy_insights("2024-01-01", "2024-01-31", "FRA")


class TestApiEnergyBobCall:
    """`_api_energy_bob_call`, per tasks.md 4.4."""

    def test_get_energy_savings_success(self, tado_unauthenticated, mocked_responses):
        response_payload = {"totalSavingsAvailable": True}
        url = energy_bob_url(f"{HOME_ID}/2024-01?country=FRA&ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, json=response_payload, status=200)

        result = tado_unauthenticated.get_energy_savings("2024-01", "FRA")

        assert result == response_payload

    def test_get_energy_savings_error(self, tado_unauthenticated, mocked_responses):
        url = energy_bob_url(f"{HOME_ID}/2024-01?country=FRA&ngsw-bypass=True")
        mocked_responses.add(responses.GET, url, status=500)

        with pytest.raises(requests.exceptions.HTTPError):
            tado_unauthenticated.get_energy_savings("2024-01", "FRA")


class TestGetBoilerState:
    BRIDGE_SERIAL = "IB0123456789"
    AUTH_KEY = "ABCDEF1234"

    def _devices_url(self):
        return api_url(f"homes/{HOME_ID}/devices")

    def _boiler_url(self):
        return api_url(
            f"homeByBridge/{self.BRIDGE_SERIAL}/boilerWiringInstallationState"
            f"?authKey={self.AUTH_KEY}"
        )

    def test_get_boiler_state_success(self, tado_unauthenticated, mocked_responses):
        devices = [
            {"deviceType": "GW03", "serialNo": "GW0000"},
            {"deviceType": "IB01", "serialNo": self.BRIDGE_SERIAL},
        ]
        state = {
            "state": "INSTALLATION_COMPLETED",
            "deviceWiredToBoiler": {"type": "BR02", "thermInterfaceType": "OPENTHERM"},
            "hotWaterZonePresent": False,
            "boiler": {"outputTemperature": {"celsius": 50.01}},
        }
        mocked_responses.add(responses.GET, self._devices_url(), json=devices, status=200)
        mocked_responses.add(responses.GET, self._boiler_url(), json=state, status=200)

        result = tado_unauthenticated.get_boiler_state(self.AUTH_KEY)

        assert result == state

    def test_get_boiler_state_no_bridge_returns_none(self, tado_unauthenticated, mocked_responses):
        devices = [{"deviceType": "GW03", "serialNo": "GW0000"}]
        mocked_responses.add(responses.GET, self._devices_url(), json=devices, status=200)

        assert tado_unauthenticated.get_boiler_state(self.AUTH_KEY) is None
