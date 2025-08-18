# Demo configurations

This directory shows how to use the `homematicip-rest-mqtt-docker` image as `hmip2mqtt` container together with the [Mosquitto MQTT](https://mosquitto.org/) broker also in a docker container.

This directory contains all files for three different demo configurations:
- [Minimal configuration](#MinimalConfiguration) without scurity concerns and minimal configuration.
- [Extended configuration with username/password](#ExtendedConfiguration1) with support for TLS (Transport Layer Security), user/password authentication and logfile.
- [Extended configuration with client certificate](#ExtendedConfiguration2) with the same functionallity as the previous version, but with additional support for client certificate authentication.

Any of these configurations can be started directly from the cloned directory tree of this repository.

For all configurations you must first [create the access token](#CreateAccessToken) used by the `hmip2mqtt` container to access your HomematicIP devices via the HomematicIP Cloud.

<a id="CreateAccessToken"></a>
## Create access token

In order to have access to the HomemaitcIP Cloud the container `hmip2mqtt` needs a file with an access token and the SGTIN of your Access Point. The script [`create_hmip_access_ini.bash`](secrets/create_hmip_access_ini.bash) starts temporarily the `homematicip-rest-mqtt-docker` image in a container and executes the Python script `hmip_generate_auth_token` contained therein. This script writes the access token and the SGTIN to the file `/app/config.ini` in the container. This file is in turn mapped to the external file `./hmip_access.ini`.
- The Python script prompts you to enter the SGINT of the access point. You will find this printed on the underside of the access point.
- You can also enter a client/device/user name, which will be displayed in the Homematic IP app in the user management section (default if left empty: homematicip-python).
- You must also enter the administrator PIN, if you have defined one in the Homematic IP app.
- You will then be prompted to press the blue button on the access point.
```
cd .../demo/secrets
./create_hmip_access_ini.bash

If you are about to connect to a HomematicIP HCU1 you have to press the button on top of the device, before you continue.
From now, you have 5 Minutes to complete the registration process.
Press Enter to continue...
Please enter the accesspoint id (SGTIN): 3014-F711-A000-03DF-29A5-36E3
Please enter the client/devicename (leave blank to use default):hmip2mqtt-test-user
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

ls -l hmip_access.ini
-rw-rw---- 1  5678 peter  162 17. Aug 12:15 hmip_access.ini
```
Important:<br/>
Keep the file `hmip_access.ini` in a safe place. Anyone how has this file may gain access to yout HomematicIP devices.

<a id="MinimalConfiguration"></a>
## Minimal configuration

- Container `hmip2mqtt`<br/>
Executes `homematicip-rest-mqtt-docker` which establishes a connection to the HomemaicIP Cloud on one side and to the MQTT broker on the other side. Status changes on one side are forwarded to the other side.<br/>
External Files (mapped files)
  - [`.../demo/secrets/hmip_access.ini`](../doc/hmip_access.ini.md) (see the previous chapter for how to create it)
- Container `mqtt_broker`<br/>
Default configuration, except that anonymous access is allowed for non-localhost mqtt clients. As the two Docker containers `hmip2mqtt` and `mqtt_broker` receive different IP addresses, this non-localhost access must be granted.
External Files (mapped files)
  - [`.../demo/mqtt_broker/config/mosquitto.conf`](./mqtt_broker/config/mosquitto.conf)

[`.../demo/compose.yaml`](./compose.yaml)
```
services:

  hmip2mqtt:
    container_name: hmip2mqtt
    image: ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest
    environment:
      - HMIP_CONFIG_FILE=/config/hmip_access.ini
      - MQTT_SERVER=mqtt_broker
    volumes:
      - ./secrets/hmip_access.ini:/config/hmip_access.ini:ro
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

Command to start the containers defined in `compose.yaml`:<br/>
Remark:<br/>
The current user should be member of the `docker`group.
```
cd .../demo
docker compose up -d
```

Command to stop the containers defined in `compose.yaml`:
```
cd ~/docker
docker compose down -d
```

<a id="ExtendedConfiguration1"></a>
## Extended configuration with username/password

The extended configuration expands on the [minimal configuration](#MinimalConfiguration).

- Container `hmip2mqtt`
  - Use TLS with self-signed certificates for communication<br/>
    `.../demo/secrets/certs/ca/ca.crt`<br/>
    See [.../demo/secrets/certs/ca/create_ca_certificate.bash](./secrets/certs/ca/create_ca_certificate.bash) and [.../demo/secrets/certs/ca/ca.cnf](./secrets/certs/ca/ca.cnf) to find out how to create the CA certificate. Remark: Some keyUsage extensions are important when using the current Python version (3.13.5).
  - Use username/password authentication
  - Use Docker Secret for `mqtt_broker_password`
  - Use own logging configuration and external logfile<br/>
    See [`.../demo/hmip2mqtt/config/logging.json`](./hmip2mqtt/config/logging.json) and directory `.../demo/hmip2mqtt/log/`.

- Container `mqtt_broker`
  - Use extended configuration for MQTT broker.<br/>
    See [`.../demo/mqtt_broker/config/mosquitto_2.conf`](./mqtt_broker/config/mosquitto_2.conf).
  - Use TLS with self-signed certificates for communication<br/>
    `.../demo/secrets/certs/ca/ca.crt`, `secrets/certs/mqtt_broker/server.crt` and `.../server.key`<br/>
    See [.../demo/secrets/certs/mqtt_broker/create_server_certificate.bash](./secrets/certs/mqtt_broker/create_server_certificate.bash) and [.../secrets/certs/mqtt_broker/server.cnf](./secrets/certs/mqtt_broker/server.cnf) to find out how to create the server certificate.
  - Use external logfile in directory `.../demo/mqtt_broker/log/`.

[`.../demo/compose_2.yaml`](./compose_2.yaml)
```
services:

  hmip2mqtt:
    container_name: hmip2mqtt
    image: ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest
    environment:
      - HMIP_CONFIG_FILE=/config/hmip_access.ini
      - MQTT_SERVER=mqtt_broker
      - MQTT_PORT=18883
      - MQTT_USERNAME=mqtt_user  # or MQTT_USERNAME=hmip2mqtt 
      - MQTT_PASSWORD_FILE=/run/secrets/mqtt_broker_password  # or MQTT_PASSWORD=${env-variable-with-password}
      - MQTT_CA_CERT_FILE=/certs/ca.crt
      - MQTT_USE_TLS=true
      - MQTT_NO_PUBLISH=false
    volumes:
      - ./hmip2mqtt/config/logging.json:/config/logging.json:ro
      - ./hmip2mqtt/log:/log:rw
      - ./secrets/hmip_access.ini:/config/hmip_access.ini:ro
      - ./secrets/certs/ca/ca.crt:/certs/ca.crt:ro
    networks:
      - mqtt_network
    secrets:
      - mqtt_broker_password
    restart: unless-stopped
    depends_on:
      - mqtt_broker

  mqtt_broker:
    container_name: mqtt_broker
    image: eclipse-mosquitto
    volumes:
      # Remark: :ro -> creates messages in log, so we don't use it here
      - ./mqtt_broker/config/mosquitto_2.conf:/mosquitto/config/mosquitto.conf
      - ./mqtt_broker/data:/mosquitto/data
      - ./mqtt_broker/log:/mosquitto/log
      - ./secrets/certs/ca/ca.crt:/mosquitto/certs/ca.crt
      - ./secrets/certs/mqtt_broker/server.crt:/mosquitto/certs/server.crt
      - ./secrets/certs/mqtt_broker/server.key:/mosquitto/certs/server.key
    networks:
      - mqtt_network
    ports:
      - 1883:1883    # anonymous access without username/password
      - 18883:18883  # requires username/password authentication
    restart: unless-stopped

networks:
  mqtt_network:
    driver: bridge

secrets:
  mqtt_broker_password:
    file: ./secrets/mqtt_broker_password.txt

```
Command to start the containers defined in `compose_2.yaml`:<br/>
```
docker compose -f compose_2.yaml up -d
```

<a id="ExtendedConfiguration2"></a>
## Extended configuration with client certificate

The following configuration uses client certificate authentication instead of username/password authentication.

- Container `hmip2mqtt`
  -  Use (self-signed) client certificate for authentication. The MQTT broker gets the username from the subject (CN=...) in the client certificate. I.e. no username or password is required.<br/>
  The MQTT broker assumes that only authenticated clients have valid certificates.<br/>
  Client certificate: `.../demo/secrets/certs/ca/ca.crt`, `secrets/certs/hmip2mqtt/client.crt` abd `.../client.key`.<br/>
  See [.../secrets/certs/hmip2mqtt/create_client_certificate.bash](./secrets/certs/hmip2mqtt/create_client_certificate.bash) and [.../demo/secrets/certs/hmip2mqtt/client.cnf](./secrets/certs/hmip2mqtt/client.cnf) to find out how to create the client certificate.

- Container `mqtt_broker`
  - Disabled external access using port 1888, i.e. anonymous access is only allowed from other containers using the same Docker network `mqtt_network`.


[`.../demo/compose_3.yaml`](./compose_3.yaml)
```
services:

  hmip2mqtt:
    container_name: hmip2mqtt
    image: ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest
    environment:
      - HMIP_CONFIG_FILE=/config/hmip_access.ini
      - MQTT_SERVER=mqtt_broker
      - MQTT_PORT=8883  # this port requires client certificate but no username/password
      - MQTT_CA_CERT_FILE=/certs/ca.crt
      - MQTT_CLIENT_CERT_FILE=/certs/client.crt
      - MQTT_CLIENT_KEY_FILE=/certs/client.key
      - MQTT_USE_TLS=true
      - MQTT_NO_PUBLISH=false
    volumes:
      - ./hmip2mqtt/config/logging.json:/config/logging.json:ro
      - ./hmip2mqtt/log:/log:rw
      - ./secrets/hmip_access.ini:/config/hmip_access.ini:ro
      - ./secrets/certs/ca/ca.crt:/certs/ca.crt:ro
      - ./secrets/certs/hmip2mqtt/client.crt:/certs/client.crt
      - ./secrets/certs/hmip2mqtt/client.key:/certs/client.key
    networks:
      - mqtt_network
    secrets:
      - mqtt_broker_password
    restart: unless-stopped
    depends_on:
      - mqtt_broker

  mqtt_broker:
    container_name: mqtt_broker
    image: eclipse-mosquitto
    volumes:
      # Remark: :ro -> creates messages in log, so we don't use it here
      - ./mqtt_broker/config/mosquitto_2.conf:/mosquitto/config/mosquitto.conf
      - ./mqtt_broker/data:/mosquitto/data
      - ./mqtt_broker/log:/mosquitto/log
      - ./secrets/certs/ca/ca.crt:/mosquitto/certs/ca.crt
      - ./secrets/certs/mqtt_broker/server.crt:/mosquitto/certs/server.crt
      - ./secrets/certs/mqtt_broker/server.key:/mosquitto/certs/server.key
    networks:
      - mqtt_network
    ports:
      # See ./mqtt_broker/config/mosquitto_2.conf to see which port allows which authentication.
      # Do not map port 1883, i.e. anonymous access is allowed only Docker internally, i.e from network mqtt_network.
      # - 1883:1883
      - 18883:18883  # requires username/password authentication
      - 8883:8883    # requires client certificate authentication
    restart: unless-stopped

networks:
  mqtt_network:
    driver: bridge

secrets:
  mqtt_broker_password:
    file: ./secrets/mqtt_broker_password.txt
```

Command to start the containers defined in `compose_3.yaml`:<br/>

```
docker compose -f compose_3.yaml up -d
```

