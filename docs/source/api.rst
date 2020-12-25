.. _api:

=====================
API Class Methods
=====================

Most of the functions receive JSON from the API and translate it to a Python dictionary or a list of Python dictionaries. So the return value will depend on the behaviour of the API.

******
Getter
******

-----------
Air comfort
-----------

.. autoclass:: libtado.api.Tado.get_air_comfort

------------------
Air comfort geoloc
------------------

.. autoclass:: libtado.api.Tado.get_air_comfort_geoloc

------------------
Away configuration
------------------

.. autoclass:: libtado.api.Tado.get_away_configuration

------------
Capabilities
------------

.. autoclass:: libtado.api.Tado.get_capabilities

---------------
Default overlay
---------------

.. autoclass:: libtado.api.Tado.get_default_overlay

------------
Device usage
------------

.. autoclass:: libtado.api.Tado.get_device_usage

-------
Devices
-------

.. autoclass:: libtado.api.Tado.get_devices

-----------
Early start
-----------

.. autoclass:: libtado.api.Tado.get_early_start

----------------
Heating circuits
----------------

.. autoclass:: libtado.api.Tado.get_heating_circuits

----
Home
----

.. autoclass:: libtado.api.Tado.get_home

----------
Home state
----------

.. autoclass:: libtado.api.Tado.get_home_state

---------
Incidents
---------

.. autoclass:: libtado.api.Tado.get_incidents

-------------
Installations
-------------

.. autoclass:: libtado.api.Tado.get_installations

-----------
Invitations
-----------

.. autoclass:: libtado.api.Tado.get_invitations

--
Me
--

.. autoclass:: libtado.api.Tado.get_me

----------------
Measuring device
----------------

.. autoclass:: libtado.api.Tado.get_measuring_device

--------------
Mobile devices
--------------

.. autoclass:: libtado.api.Tado.get_mobile_devices

---------------------
Open window detection
---------------------

.. autoclass:: libtado.api.Tado.set_open_window_detection

------
Report
------

.. autoclass:: libtado.api.Tado.get_report

-------------------
Schedule Timetables
-------------------

.. autoclass:: libtado.api.Tado.get_schedule_timetables

--------
Schedule
--------

.. autoclass:: libtado.api.Tado.get_schedule

---------------
Schedule blocks
---------------

.. autoclass:: libtado.api.Tado.get_schedule_blocks

-----
State
-----

.. autoclass:: libtado.api.Tado.get_state

------------------
Temperature offset
------------------

.. autoclass:: libtado.api.Tado.get_temperature_offset

-----
Users
-----

.. autoclass:: libtado.api.Tado.get_users

-------
Weather
-------

.. autoclass:: libtado.api.Tado.get_weather

-----
Zones
-----

.. autoclass:: libtado.api.Tado.get_zones


******
Setter
******

-----------
Early start
-----------

.. autoclass:: libtado.api.Tado.set_early_start

------------------
End manual control
------------------

.. autoclass:: libtado.api.Tado.end_manual_control

----------
Home state
----------

.. autoclass:: libtado.api.Tado.set_home_state

--------
Schedule
--------

.. autoclass:: libtado.api.Tado.set_schedule

---------------
Schedule blocks
---------------

.. autoclass:: libtado.api.Tado.set_schedule_blocks

-----------
Temperature
-----------

.. autoclass:: libtado.api.Tado.set_temperature

------------------
Temperature offset
------------------

.. autoclass:: libtado.api.Tado.set_temperature_offset

---------
Zone name
---------

.. autoclass:: libtado.api.Tado.set_zone_name
