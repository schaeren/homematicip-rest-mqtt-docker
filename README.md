## Preface to this fork

This fork is used to make a Docker image/container containing the original application.

### Prerequisites

- Linux system with Docker installed. I use a Raspberry Pi 5 with Raspberry Pi OS and the [official Docker installation script](https://get.docker.com). 
- Basic knowledge about docker, some knowledge of Docker Compose would be beneficial, too.
- MQTT broker. I use [Eclipse Mosquitto](https://mosquitto.org/) as a [separate Docker container](https://hub.docker.com/_/eclipse-mosquitto). With a basic configuration it can be accessed without authentication (use this only in a protected environment)
- In a production environment or if the MQTT broker can be accessed from the Internet you should protect the access to it with at least username/password or client certificate authentication. If you operate your own MQTT broker, you may also need to generate the self-signed certificates for SSL/TLS and client certificate authentication. It works fine with self-signed certificates.
- Optional: [MQTT Explorer](https://mqtt-explorer.com/) is a very handy tool for displaying MQTT messages.

### Installation

Steps to be taken:
1. Create access token used to access the HomematicIP cloud.
2. Prepare external files.
3. Create the compose.yaml.

#### 1. Create access token
Create the file containing the access token according to [this instructions](https://github.com/hahn-th/homematicip-rest-api?tab=readme-ov-file#generate-token). The file created will contain the access token used to access your HomematicIP devices through the HomematicIP Cloud. Move it to a secure place! Later it must be bind mounted into the container.

#### 2. Prepare external files
The external files are located outside the container and must be mapped into it (bind mount). Depending on your configuration you need the following external files:
- [`hmip_access.ini`](doc/hmip_access.ini.md): File with access token for the HomematicIP cloud.
- [`logging.json`](doc/logging.json.md): Optional file with logging configuraion. The container contains a config file for the logger but you can overwrite it with a external file.
- `ca.crt`: Optional file with the certificate of the CA (certificate authority). This external file should be provided if SSL/TLS is used to access the MQTT broker.
- `client.crt` and `client.key`: Optional files with the client certificate (including the public key) and the private key. These external files must be provided if client certificate authentication is used. 

#### Create the compose.yaml
The following `compose.yaml` defines a minimal setup with two containers: `hmip2mqtt` and `mqtt_broker`:


```
services:
  hmip2mqtt:
    container_name: hmip2mgtt
    hostname: hmip2mgtt
    image: ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest
    environment:
      - HMIP_CONFIG_FILE=/run/secrets/hmip_access
      - MQTT_SERVER=mqtt-broker
    volumes:
      - /volumes/hmip2mqtt/log:/log:rw
    networks:
      - internal_network
    secrets:
      - hmip_access
      - mqtt_broker_password
    restart: unless-stopped
    depends_on:
      - mqtt_broker

  container_name: mqtt_broker
    image: eclipse-mosquitto
    hostname: mqtt-broker
    environment:
      - TZ=Europe/Zurich
      - PUID=2000
      - PGID=2000
    volumes:
      - /volumes/mqtt_broker/config:/mosquitto/config:rw # :ro -> creates messages in log
      - /volumes/mqtt_broker/data:/mosquitto/data:rw
      - /volumes/mqtt_broker/log:/mosquitto/log:rw
      - /secrets/certs/mqtt_broker:/mosquitto/certs:rw # :ro -> creates messages in log
    networks:
      - internal_network
    ports:
      - 8883:8883
    restart: unless-stopped
    
secrets:
  hmip_access:
    file: /secrets/hmip_access.ini
  mqtt_broker_password:
    file: /secrets/mqtt_broker_password.txt
    
```
To use your own logging.json an the extzernal logfile, add the following setting:

```
services:
  hmip2mqtt:
    ...
    volumes:
      ...
      - /volumes/hmip2mqtt/log:/log:rw
      - /volumes/hmip2mqtt/config/logging.json:/config/logging.json:ro
```

To use SSL/TLS and client certificates, add the following settings:

```
services:
  hmip2mqtt:
    ...
    environment:
      - ...
      - MQTT_PORT=18883
      - MQTT_USERNAME=mqtt_user
      - MQTT_PASSWORD_FILE=/run/secrets/mqtt_broker_password
      - MQTT_CA_CERT_FILE=/certs/ca.crt
      - MQTT_CLIENT_CERT_FILE=/certs/client.crt
      - MQTT_CLIENT_KEY_FILE=/certs/client.key
      - MQTT_USE_TLS=true
    volumes:
      ...
      - /secrets/certs/mqtt_client:/certs:ro    
```
----------------------------------------------------------------------------------------------------

ORIGINAL DOCUMENTATION FROM [homematicip-rest-mqtt](https://github.com/cyraxx/homematicip-rest-mqtt)

----------------------------------------------------------------------------------------------------

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

