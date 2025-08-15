
...

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

1. If you haven't already done so: Set up Git<br/>
   `git config --global user.name "Your Name"`<br/>
   `git config --global user.email "your.name@email.com"`
2. Clone the repo<br/>
   `git clone git@github.com:schaeren/homematicip-rest-mqtt-docker.git`<br/>
3. `cd homematicip-rest-mqtt-docker`
4. Add your `config.ini` to the current directory (see 'Instructions' below on how to generate it)
5. Execute the following commands to build the Docker image:<br/>
   `docker build . -t homematicip-rest-mqtt-docker:latest`
6. To start the container execute:<br/>
   `docker run --mount type=bind,source=./config.ini,target=/config.ini homematicip-rest-mqtt-docker:latest --server {mqtt-broker} --debug `
   
   Replace `{mqtt-broker}` with the hostname or IP address of your MQTT broker.
   If the MQTT broker requires any login credentials or/and other options you must add these to the command line (see `main.py` for supported command line arguments).

If you want to publish the Docker image into your own GitHub Container Repository (ghcr.io) see the video [Push Docker Images to GitHub Container Registry](https://www.youtube.com/watch?v=RgZyX-e6W9E).

** JUST IN WORK ** (Docker compose.yaml may follow)
