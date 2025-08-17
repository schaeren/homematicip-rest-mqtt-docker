touch hmip_access.ini
chmod 660 hmip_access.ini
sudo chown 5678 hmip_access.ini  # 5678 is the user ID used by the container hmip2mqtt

docker run --rm -v ./hmip_access.ini:/app/config.ini -it ghcr.io/schaeren/homematicip-rest-mqtt-docker:latest hmip_generate_auth_token
