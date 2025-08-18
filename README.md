
# Preface to this fork

This repository [homematicip-rest-mqtt-docker](https://github.com/schaeren/homematicip-rest-mqtt-docker) started as a fork of [homematicip-rest-mqtt](https://github.com/cyraxx/homematicip-rest-mqtt). It wraps the original application into a Docker container for easier installation in Docker environments.

in addition to dockerization, this solution offers the following improvements:
- Optional support for TLS (Transport Layer Security) to encrypt/secure communication with the MQTT broker.
- Optional support for client certificate authentication with the MQTT broker. 
- Flexible configuration of logger using the configuration file `logging.json`.


# Prerequisites

- Your Homematic IP devices have been configured in the Homematic IP app (Android or iOS).
- Linux system with Docker installed. I use a Raspberry Pi 5 with Raspberry Pi OS and the [official Docker installation script](https://get.docker.com).
- MQTT Broker, e.g. [Eclipse Mosquitto](https://mosquitto.org/). I use the [official Docker image](https://hub.docker.com/_/eclipse-mosquitto). With a basic configuration it can be accessed without authentication (use this only in a protected / isolated environment).
- Basic knowledge of MQTT, Docker and Docker Compose.

Optional:
- In a production environment or if the MQTT broker is accessible via the Internet, you should protect access to it with at least a username/password or client certificate authentication. If you operate your own MQTT broker, you may also need to generate self-signed certificates for TLS and, if necessary, client certificate authentication.
- [MQTT Explorer](https://mqtt-explorer.com/) is a very handy tool for displaying MQTT messages during installation and for debugging.

# Installation

Even if an installation with the `docker run` command is possible, I recommend using `docker compose` with a `compose.yaml` configuration file.

Various configurations with detailed descriptions and all necessary files can be found in the demo folder: [`./demo/README.md`](./demo/README.md).


# Configuration 

`homematicip-rest-mqtt-docker` supports the following configuration options for the container:

Remark: Command line options take precedence over environment variables.

| Command line option | Environment variable | Default |  |
|--|--|--|--|
| --hmip_config_file | HMIP_CONFIG_FILE | - | Path to the hmip_access.ini with the access token for the HomematicIP Cloud.<br/>For backward compatibility it accepts also --config.
| --server | MQTT_SERVER | localhost | Hostname or IP-Address of the MQTT broker. |
| --port | MQTT_PORT | 1883 | Port number of the MQTT broker. |
| --username | MQTT_USERNAME | - | Username for the MQTT broker. |
| --password | MQTT_PASSWORD | - | Password for the MQTT broker. |
| --ca_cert_file | MQTT_CA_CERT_FILE | - | Absolute or relative path to the CA certificate file. Required if the MQTT broker uses a self-signed certificate. |
| --client_cert_file | MQTT_CLIENT_CERT_FILE | - | Abolute or relative path to the client certificate file. Abolute or relative path to the client private key file. Required for client certificate authentication. |
| --client_key_file | MQTT_CLIENT_KEY_FILE | - | Required for client certificate authentication. |
| --use_tls | MQTT_USE_TLS | true if port != 1883 | Use TSL for the MQTT connection, true/false. |
| --disable_server_cert | MQTT_DISABLE_SERVER_CERT | false | Disable server certificate verification (if TLS is enabled), true/false.<br/> **Important: Should be disabled only in a isolated / secure environment and only for debugging, if at all.** |
| --no_publish | MQTT_NO_PUBLISH | false | Don't actually publish messages (log only), true/false- |

<br/>

----------------------------------------------------------------------------------------------------

<span style="color: red;">***** The following is a copy of the ORIGINAL DOCUMENTATION from [homematicip-rest-mqtt](https://github.com/cyraxx/homematicip-rest-mqtt) *****</span>

----------------------------------------------------------------------------------------------------

<br/>

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

