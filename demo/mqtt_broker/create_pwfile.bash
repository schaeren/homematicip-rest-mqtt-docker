touch ./data/pwfile
chmod 770 ./data
chmod 660 ./data/pwfile
sudo chgrp -R 2000 ./data
docker run --rm -v ./data:/mosquitto/data --user 2000:2000 eclipse-mosquitto /bin/sh -c \
    "mosquitto_passwd -c -b /mosquitto/data/pwfile hmip2mqtt changeThisPassword && \
     mosquitto_passwd    -b /mosquitto/data/pwfile mqtt_user changeThisPassword"
