
<span style="color: red;">Remark: This documentation is still in work!</span>


## Preface to this fork

This repository [homematicip-rest-mqtt-docker](https://github.com/schaeren/homematicip-rest-mqtt-docker) started as a fork of [homematicip-rest-mqtt](https://github.com/cyraxx/homematicip-rest-mqtt). It wraps the original application into a Docker container for easier installation in Docker environments.

Apart from dockerisation, this solution offers the following improvements:
- Optional support for TLS (Transport Layer Security) to encrypt/secure communication with the MQTT broker.
- Optional support for client certificate authentication with the MQTT broker. 
- Flexible configuration of logger using the configuration file `logging.json`.


### Prerequisites

- Linux system with Docker installed. I use a Raspberry Pi 5 with Raspberry Pi OS and the [official Docker installation script](https://get.docker.com).
- MQTT Broker. I use [Eclipse Mosquitto](https://mosquitto.org/) as a [separate Docker container](https://hub.docker.com/_/eclipse-mosquitto). With a basic configuration it can be accessed without authentication (use this only in a protected / isolated environment)
- Basic knowledge of Docker and Docker Compose.

Optional:
- In a production environment or if the MQTT broker is accessible via the Internet, you should protect access to it with at least a username/password or client certificate authentication. If you operate your own MQTT broker, you may also need to generate self-signed certificates for TLS and, if necessary, client certificate authentication. This works perfectly with self-signed certificates.
- Optional: [MQTT Explorer](https://mqtt-explorer.com/) is a very handy tool for displaying MQTT messages during installation and for debugging.

### Installation

Steps to be taken:
1. [Create access token](#CreateAccessToken) used to access the HomematicIP cloud.
2. [Prepare external files](#PrepareExternalFiles) as necessary (those located outside the container, for configuration, logging, certificates)
3. [Create the file `compose.yaml`](#CreateComposeYaml), which is used to set up the containers and start it.
4. [Start the container](#StartContainer)

<a id="CreateAccessToken"></a>
#### 1. Create access token
In order to have access to the HomemaitcIP Cloud the container needs a file with an access token and the SGTIN of the Access Point. To create theis file you must execute the `hmip_generate_auth_token` command inside th container:
```
mkdir ~/docker/hmip2mqtt  # Change this path according to your needs
cd ~/docker/hmip2mqtt
mkdir secrets
touch secrets/hmip_access.ini
chmod 770 secrets
chmod 660 secrets/hmip_access.ini
sudo chown -R 5678 secrets  # 5678 is the user ID used by the container
```
The following command finally starts the container and executes the script `hmip_generate_auth_token` contained therein. The script writes the access token and the SGTIN to the file `/app/config.ini` in the container. This file is in turn mapped to the external file `./secerts/hmip_access.ini`.
```
docker run --rm -v ./secrets/hmip_access.ini:/app/config.ini -it ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest hmip_generate_auth_token 
```
The script prompts you to enter the SGINT of the access point. You will find this printed on the underside of the access point.
You can also enter a client/device/user name, which will be displayed in the Homematic IP app in the user management section (default: homemaitcip-python).
You must also enter the administrator PIN, if you have defined one in the Homematic IP app.
You will then be prompted to press the blue button on the access point.

Example screenshot of the generation of an access token:
```
peter@raspi:~ $ cd ~/docker/hmip2mqtt
peter@raspi:~/docker/hmip2mqtt $ docker run --rm -v ./secrets/hmip_access.ini:/app/config.ini -it ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest hmip_generate_auth_token

If you are about to connect to a HomematicIP HCU1 you have to press the button on top of the device, before you continue.
From now, you have 5 Minutes to complete the registration process.
Press Enter to continue...
Please enter the accesspoint id (SGTIN): ****-****-****-****-****-****
Please enter the client/devicename (leave blank to use default): hmip2mqtt-user
Please enter the PIN (leave Blank if there is none):
Connection Request successful!
Please press the blue button on the access point
Please press the blue button on the access point
...
Please press the blue button on the access point
-----------------------------------------------------------------------------
Token successfully registered!
AUTH_TOKEN:     *************************************************************
ACCESS_POINT:   ************************
Client ID:      ********-****-****-****-************
saving configuration to ./config.ini

peter@raspi:~/docker/hmip2mqtt $ ls -l secrets

insgesamt 12
-rw-rw---- 1 peter  5678  162 16. Aug 16:22 hmip_access.ini
```

<a id="PrepareExternalFiles"></a>
#### 2. Prepare external files
The external files are located outside the container and must be mapped into it (bind mount). Depending on your configuration you need the following external files:

The paths and file names used here are only examples; you can adapt them to suit your needs.

External file required for container `hmip2mqtt`:
- `~/docker/hmip2mqtt/secrets/hmip_access.ini`: File with access token (see above on how to create it).
- [`~/docker/hmip2mqtt/config/logging.json`](doc/logging.json.md): Optional file with logging configuraion. You only need this file if you want to overwrite the default configuration defined in the container.
- `~/docker/hmip2mqtt/secrets/ca.crt`: Optional file with the certificate of the CA (certificate authority). You mainly need this file if you are using TLS with self-signed certificates.
- `~/docker/hmip2mqtt/secrets/client.crt` and `~/docker/hmip2mqtt/secrets/client.key`: Optional files with the client certificate (including the public key) and the private key. These external files must be provided if client certificate authentication is used. 

External file required for container `mqtt_broker`:
- `~/docker/mqtt_broker/config/mosquitto.conf`: Configuration file for Mosquitto MQTT broker:
```
per_listener_settings true

listener 1883
allow_anonymous true
```

<a id="CreateComposeYaml"></a>
#### 3. Create the Docker Compose file `~/docker/compose.yaml`
The `compose.yaml` defines how to start the container. The following example creates a simple setup with two containers: `hmip2mqtt` and `mqtt_broker`:

`nano ~/docker/compose.yaml`
```
services:

  hmip2mqtt:
    container_name: hmip2mqtt
    image: ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest
    environment:
      - HMIP_CONFIG_FILE=/config/hmip_access.ini
      - MQTT_SERVER=mqtt_broker
    volumes:
      - ./hmip2mqtt/secrets/hmip_access.ini:/config/hmip_access.ini:ro
    networks:
      - mqtt_network
    restart: unless-stopped
    depends_on:
      - mqtt_broker

  mqtt_broker:
    container_name: mqtt_broker
    image: eclipse-mosquitto
    volumes:
      - ./mqtt_broker/config/mosquitto.conf:/mosquitto/config/mosquitto.conf
    networks:
      - mqtt_network
    ports:
      - 1883:1883
    restart: unless-stopped

networks:
  mqtt_network:
    driver: bridge
```
Remark: File and directory paths in `compose.yaml` can be absolute paths or relative to the directory containing `compose.yaml`, in our case relative to `~/docker`.

To use your own `~/docker/hmip2mqtt/config/logging.json` an a external directory `~/docker/hmip2mqtt/log` for the logfiles, add the following settings (see also [`logging.json`](doc/logging.json.md)):

```
services:
  hmip2mqtt:
    ...
    volumes:
      ...
      - ./hmip2mqtt/log:/log:rw
      - ./hmip2mqtt/config/logging.json:/config/logging.json:ro
```
Remark: The directory `~/docker/hmip2mqtt/log` must exist before starting the container.

To use TLS and client certificates, add something like the following settings:
```
services:
  hmip2mqtt:
    ...
    environment:
      - ...
      - MQTT_PORT=8883
      - MQTT_USERNAME=mqtt_user
      - MQTT_PASSWORD=********
#       - MQTT_PASSWORD_FILE=/run/secrets/mqtt_broker_password
      - MQTT_CA_CERT_FILE=/certs/ca.crt
      - MQTT_CLIENT_CERT_FILE=/certs/client.crt
      - MQTT_CLIENT_KEY_FILE=/certs/client.key
      - MQTT_USE_TLS=true
    volumes:
      ...
      - /hmip2mqtt/certs:/certs:ro    
    ...
  
# secrets:
#   mqtt_broker_password:
#     file: ./secrets/mqtt_broker_password.txt  
```
Remarks: 
1. You can use the `MQTT_PASSWORD=` or the out-commented version with `MQTT_PASSWORD_FILE=` including the `secrets:` section (for more information [see here](https://docs.docker.com/compose/how-tos/use-secrets/)).
2. You may use secrets for the `hmip_access.ini`, too: 
```
services:
  hmip2mqtt:
    ...
    environment:
      ...
      - HMIP_CONFIG_FILE=/run/secrets/hmip_access
      ...

secrets:
  hmip_access:
    file: ./hmip2mqtt/hmip_access.ini
```

<a id="StartContainer"></a>
#### 4. Start the container

Command to start all containers defined in `compose.yaml`:
```
cd ~/docker
docker compose up -d
```
Remark: the current user should be member of the `docker`group.

Command to stop all containers defined in `compose.yaml`:
```
cd ~/docker
docker compose down -d
```

### Configuration 

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

----------------------------------------------------------------------------------------------------

<span style="color: red;">***** The following is a copy of the ORIGINAL DOCUMENTATION from [homematicip-rest-mqtt](https://github.com/cyraxx/homematicip-rest-mqtt) *****</span>

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

