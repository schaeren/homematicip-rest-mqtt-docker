## Preface to this fork

This fork is used to make a Docker image/container containing the original application.

### How to use

1. Add your `config.ini` to the current directory (see 'Instructions' below on how to generate it).
2. Download Doker image, create container and start it:<br/>
   `docker run --mount type=bind,source=./config.ini,target=/config.ini ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest --server {mqtt-broker} --debug`
3. Replace `{mqtt-broker}` with the hostname or IP address of your MQTT broker.
   If the MQTT broker requires any login credentials or/and other options you must add these to the command line (see `main.py` for supported command line arguments).

Prerequisites:

* Docker (or Docker Desktop)
* Git (if you want to start with the source code)
* Python
* MQTT broker (e.g. Mosquitto)

### How to build the Docker image/container

1. If you haven't already done so: Set up Git<br/
   `git config --global user.name "Your Name"`<br/
   `git config --global user.email "your.name@email.com"`
2. Clone the repo<br/
   `git clone git@github.com:schaeren/homematicip-rest-mqtt-docker.git`<br/
3. `cd homematicip-rest-mqtt-docker`
4. Add your `config.ini` to the current directory (see 'Instructions' below on how to generate it)
5. Execute the following commands to build the Docker image:<br/
   `docker build . -t homematicip-rest-mqtt-docker:latest`
6. To start the container execute:<br/
   `docker run --mount type=bind,source=./config.ini,target=/config.ini homematicip-rest-mqtt-docker:latest --server {mqtt-broker} --debug `
   
   Replace `{mqtt-broker}` with the hostname or IP address of your MQTT broker.
   If the MQTT broker requires any login credentials or/and other options you must add these to the command line (see `main.py` for supported command line arguments).

If you want to publish the Docker image into your own GitHub Container Repository (ghcr.io) see the video [Push Docker Images to GitHub Container Registry](https://www.youtube.com/watch?v=RgZyX-e6W9E).

** JUST IN WORK ** (Docker compose.yaml may follow)

# Homematic IP REST API to MQTT bridge (Docker Container)

Bridges between Homematic IP components using the REST API (i.e. using an Homematic IP Access Point, not a CCU)
and an MQTT broker so you can use your home automation software of choice to interact with Homematic IP.

In its current state, it offers Homematic IP to MQTT functionality for a number of devices (see below) and
MQTT to Homematic IP functionality for a very limited number of devices and values. Additional devices are
pretty trivial to implement so feel free to open a PR.

![Example screenshot from MQTT explorer](example.png)

# Instructions

Install the module requirements using `pip install -r requirements.txt`.

Before first use, you need to follow the instructions for
[homematicip-rest-api](https://github.com/hahn-th/homematicip-rest-api#usage) to generate the config file
containing your auth token.

Then simply run `main.py --server <ip of your MQTT server>`, add `--debug` if you want to see what's going on.

To run as a daemon using systemd, see `homematicip-rest-mqtt.service` for a starting point.

# Supported devices

## Home (alarm state)

| Property                                                     | MQTT topic (read)                        | MQTT topic (write)                           |
| -------------------------------------------------------------- | ------------------------------------------ | ---------------------------------------------- |
| Current alarm state (`OFF`, `ABSENCE_MODE`, `PRESENCE_MODE`) | `homematicip/home/alarm//state` | `cmd/homematicip/home/alarm//state` |

## Heating group (aka room)

| Property                                            | MQTT topic (read)                                   | MQTT topic (write)                              |
| ----------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------- |
| Group (room) name                                   | `homematicip/groups/heating//label`       |                                                 |
| Set point temperature                               | `homematicip/groups/heating//set`         | `cmd/homematicip/groups/heating//set` |
| Current temperature                                 | `homematicip/groups/heating//temperature` |                                                 |
| Current humidity                                    | `homematicip/groups/heating//humidity`    |                                                 |
| Current valve position (0..1)                       | `homematicip/groups/heating//valve`       |                                                 |
| Current window state (`OPEN`,`CLOSED`,`TILTED`)     | `homematicip/groups/heating//window`      |                                                 |
| Current control mode (`AUTOMATIC`, `MANUAL`, `ECO`) | `homematicip/groups/heating//mode`        |                                                 |

## Heating thermostat (valve)

Homematic IP product codes: HMIP-eTRV, HMIP-eTRV-C

| Property                      | MQTT topic (read)                                        | MQTT topic (write) |
| ------------------------------- | ---------------------------------------------------------- | -------------------- |
| Low battery state             | `homematicip/devices/thermostat//low_battery` |                    |
| Set point temperature         | `homematicip/devices/thermostat//set`         |                    |
| Current temperature           | `homematicip/devices/thermostat//temperature` |                    |
| Current valve position (0..1) | `homematicip/devices/thermostat//valve`       |                    |

## Wall mounted thermostat

Homematic IP product codes: HMIP-WTH, HMIP-WTH-2, HMIP-BWTH

| Property              | MQTT topic (read)                                             | MQTT topic (write) |
| ----------------------- | --------------------------------------------------------------- | -------------------- |
| Low battery state     | `homematicip/devices/wall_thermostat//low_battery` |                    |
| Set point temperature | `homematicip/devices/wall_thermostat//set`         |                    |
| Current temperature   | `homematicip/devices/wall_thermostat//temperature` |                    |
| Current humidity      | `homematicip/devices/wall_thermostat//humidity`    |                    |

## Window/contact sensor

Homematic IP product codes: HMIP-SWDO, HMIP-SWDO-I, HMIP-SWDM, HMIP-SWDM-B2, HMIP-SCI, HMIP-SRH

| Property                                        | MQTT topic (read)                                    | MQTT topic (write) |
| ------------------------------------------------- | ------------------------------------------------------ | -------------------- |
| Low battery state                               | `homematicip/devices/window//low_battery` |                    |
| Current window state (`OPEN`,`CLOSED`,`TILTED`) | `homematicip/devices/window//state`       |                    |

## Motion detector indoor

Homematic IP product code: HMIP-SMI

| Property             | MQTT topic (read)                                                    | MQTT topic (write) |
| ---------------------- | ---------------------------------------------------------------------- | -------------------- |
| Low battery state    | `homematicip/devices/motion_detector//low_battery`        |                    |
| Current illumination | `homematicip/devices/motion_dector//current_illumination` |                    |
| Illumination         | `homematicip/devices/motion_detector//illumination`       |                    |
| Motion detected      | `homematicip/devices/motion_detector//motion_detected`    |                    |

## Smoke detector

Homematic IP product code: HMIP-SWSD

| Property          | MQTT topic (read)                                            | MQTT topic (write) |
| ------------------- | -------------------------------------------------------------- | -------------------- |
| Low battery state | `homematicip/devices/smoke_detector//low_battery` |                    |

## Alarm siren indoor

Homematic IP product code: HMIP-ASIR-2

| Property          | MQTT topic (read)                                         | MQTT topic (write) |
| ------------------- | ----------------------------------------------------------- | -------------------- |
| Low battery state | `homematicip/devices/alarm_siren//low_battery` |                    |

## Weather sensor (basic)

Homematic IP product code: HmIP-SWO-B

| Property                        | MQTT topic (read)                                                         | MQTT topic (write) |
| --------------------------------- | --------------------------------------------------------------------------- | -------------------- |
| Low battery state               | `homematicip/devices/weather//low_battery`                     |                    |
| Current temperature             | `homematicip/devices/weather//temperature`                     |                    |
| Current humidity                | `homematicip/devices/weather//humidity`                        |                    |
| Current illumination            | `homematicip/devices/weather//illumination`                    |                    |
| Illumination threshold sunshine | `homematicip/devices/weather//illumination_threshold_sunshine` |                    |
| Storm                           | `homematicip/devices/weather//storm`                           |                    |
| Sunshine                        | `homematicip/devices/weather//sunshine`                        |                    |
| Today sunshine duration         | `homematicip/devices/weather//today_sunshine_duration`         |                    |
| Total sunshine duration         | `homematicip/devices/weather//total_sunshine_duration`         |                    |
| Wind value type                 | `homematicip/devices/weather//wind_value_type`                 |                    |
| Wind speed                      | `homematicip/devices/weather//wind_speed`                      |                    |
| Yesterday sunshine duration     | `homematicip/devices/weather//yesterday_sunshine_duration`     |                    |
| Vapor amount                    | `homematicip/devices/weather//vapor_amount`                    |                    |

## Hoermann Gate Drive

Homematic IP product code: HmIP-MOD-HO

| Property                                                      | MQTT topic (read)                                      | MQTT topic (write)                                         |
| --------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------ |
| Current door state (`CLOSED`, `OPEN`, `STOP`, `PARTIAL_OPEN`) | `homematicip/devices/hoermann_drive//state` | `cmd/homematicip/devices/hoermann_drive//state` |

## Light sensor

Homematic IP product code: HMIP-SLO

MQTT topics:

- `homematicip/devices/light_sensor/current`: Current illumination
- `homematicip/devices/light_sensor/average`: Average illumination
- `homematicip/devices/light_sensor/highest`: Highest illumination
- `homematicip/devices/light_sensor/lowest`: Lowest illumination

