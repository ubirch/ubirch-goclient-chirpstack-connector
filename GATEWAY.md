# RAK7244C Gateway Setup
* This document explains how to set up a [RAK7244C](https://docs.rakwireless.com/Product-Categories/WisGate/RAK7244C/Quickstart) Gateway for usage with the [uBirch GoClient Chirpstack Connector](.) (UGCC).
It contains a step by step guide from setting up the OS itself over [Chirpstack](https://www.chirpstack.io/) configuration to installation and configuration of the UGCC.
***

## Contents
- [RAK7244C Gateway Setup](#rak7244c-gateway-setup)
  - [Contents](#contents)
  - [Gateway Preparation](#gateway-preparation)
  - [OS Setup](#os-setup)
    - [OS Installation](#os-installation)
    - [OS Configuration](#os-configuration)
      - [OS Update](#os-update)
      - [Firewall Setup](#firewall-setup)
  - [ChirpStack Configuration](#chirpstack-configuration)
    - [SSL Configuration](#ssl-configuration)
    - [Changing the JWT Secret + Port Configuration](#changing-the-jwt-secret--port-configuration)
    - [Configuration in the WebInterface](#configuration-in-the-webinterface)
    - [API Key generation](#api-key-generation)
  - [MQTT Configuration](#mqtt-configuration)
    - [Adjusting ChirpStack Configuration Files](#adjusting-chirpstack-configuration-files)
  - [UGCC Setup](#ugcc-setup)
    - [uBirch GoClient Installation](#ubirch-goclient-installation)
    - [uBirch GoClient Configuration](#ubirch-goclient-configuration)
    - [UGCC Installation](#ugcc-installation)
      - [Install Python 3.8](#install-python-38)
    - [UGCC Configuration](#ugcc-configuration)
    - [Fludia Sensor Setup](#fludia-sensor-setup)
      - [Generate a UUID](#generate-a-uuid)
      - [Device Registration at the uBirch Backend](#device-registration-at-the-ubirch-backend)
      - [Device Registration at the ChirpStack WebInterface](#device-registration-at-the-chirpstack-webinterface)
      - [Adjusting config files for the new device](#adjusting-config-files-for-the-new-device)
***

## Gateway Preparation
* The first thing to do is to connect all the antennas to the device. In the case of the [RAK7244C](https://docs.rakwireless.com/Product-Categories/WisGate/RAK7244C/Quickstart) there are four antennas. 1x GPS, 2x LTE and 1x LoRa. All the ports (USB, HDMI, Ethernet, Antennas, ...) are labeled in [here](https://docs.rakwireless.com/Product-Categories/WisGate/RAK7244/Datasheet/#rak7244c-2). The two LTE antennas have to be connected to hte lower two antenna ports. Now the LoRa antenna can only be connected to the upper left port, only leaving the upper right one for the GPS antenna. The Micro-SD card slot is located beneath the antenna ports. Remove the Micro-SD card if already inserted, it is needed for the next step.
***

## OS Setup
* RAK provides an own variation of [Raspbian](https://www.raspbian.org/) with ChirpStack and all drivers needed for the LoRa, GPS and LTE modules pre-installed. It is strongly recommended to use this image. It can be **[downloaded here](https://docs.rakwireless.com/Product-Categories/WisGate/RAK7244C/Overview/)**. **Note** that the image contained in the ZIP archive must match your gateway model. You won't notice that you chose the wrong image immediately but only after a while when things like GPS aren't working.

### OS Installation
* After unpacking the ZIP file, the contained `.img` file can be flashed onto the Micro-SD card. On Linux systems, the `.img` can be flashed like this:
```sh
sudo dd if=IMAGE_NAME.img status=progess of=/dev/mmcblk0
```
* Of course, `/dev/mmcblk0` is just the path to the Micro-SD card on my system. It may vary on yours; make sure you use the correct path, because you might accidentially overwrite data on other devices.

### OS Configuration
* Insert the Micro-SD card and power on the device. The first boot will take a while (...), you can check the progress by connecting the gateway to your monitor with a HDMI-microHDMI cable. Continue once it reaches the login prompt.
Now follow [the instructions provided in the official documentation of the RAK7244C](https://docs.rakwireless.com/Product-Categories/WisGate/RAK7244C/Quickstart/). You will need to SSH onto the gateway for the next step.

#### OS Update
* **This step is very important** because the image provided by RAK currently (as of December 2020) comes with an outdated version of ChirpStack.
* You should update your OS since the image provided by RAK might not be up to date.
```sh
sudo apt update && sudo apt upgrade
```
* Reboot afer the update completed.

#### Firewall Setup
* Services like the internal MQTT Server shouldn't be reachable from the outside when the gateway is run *in the wild*. Therefore a basic iptables setup is needed.
```sh
sudo iptables -A INPUT --src 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 8080 -j ACCEPT
sudo iptables -P INPUT DROP
```
* This will only allow incoming connections on port `22` (SSH) and `8080` (Web Interface). You can replace `8080` with the value of your choice if you plan to change the WebInterface port later when configuring it (see [ChirpStack Configuration](#chirpstack-configuration)).Connections on other ports originating from existing connections are also accepted (i.e.: client connects to the Web Interface and the HTTP server moves the connection to port 43421).
The new list of rules can be viewed with the following command:
```sh
sudo iptables -L -vn
```
```
Chain INPUT (policy DROP 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
   20  1268 ACCEPT     all  --  *      *       127.0.0.1            0.0.0.0/0           
   86  5752 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            ctstate RELATED,ESTABLISHED
    0     0 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:22
    0     0 ACCEPT     udp  --  *      *       0.0.0.0/0            0.0.0.0/0            udp dpt:22
    0     0 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:8080
    0     0 ACCEPT     udp  --  *      *       0.0.0.0/0            0.0.0.0/0            udp dpt:8080

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
```
* The same rules have to be applied for IPv6.
```sh
sudo ip6tables -A INPUT --src ::1 -j ACCEPT
sudo ip6tables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo ip6tables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo ip6tables -A INPUT -p udp --dport 22 -j ACCEPT
sudo ip6tables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo ip6tables -A INPUT -p udp --dport 8080 -j ACCEPT
sudo ip6tables -P INPUT DROP
```
* The `sudo ip6tables -L -vn` command will give almost the same output as above in the case of IPv4 with the only difference being the format of the IP addresses. These rules have to be made persistent. The propper way of doing this differs from distro to distro, but on Debian (which is the foundation of Raspbian, the system used in the image supplied by RAK) it can be done like this:
```sh
sudo apt update && sudo apt install iptables-persistent
```
* Now save the rules set above:
```sh
sudo su -c "iptables-save > /etc/iptables/rules.v4"
sudo su -c "ip6tables-save > /etc/iptables/rules.v6"
```
* Both of the files contents should now look like this:
```sh
cat /etc/iptables/rules.v4
```
```sh
# Generated by xtables-save v1.8.2 on Thu Dec 17 11:47:04 2020
*filter
:INPUT DROP [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -s 127.0.0.1/32 -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A INPUT -p udp -m udp --dport 22 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 8080 -j ACCEPT
-A INPUT -p udp -m udp --dport 8080 -j ACCEPT
COMMIT
# Completed on Thu Dec 17 11:47:04 2020
```
* Again, the IP address will vary in the IPv6 file, `/etc/iptables/rules.v6`.
***

## ChirpStack Configuration
### SSL Configuration
* Navigate to the ChirpStack Application Server config directory and generate a SSL certificate and the private key. **Note** that configuring SSL will cause the WebServer to not work without SSL anymore. Besides that, using a self-signed certificate will lead to a warning being shown in most browsers.
```sh
sudo -i
cd /etc/chirpstack-application-server
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout cs.key -out cs.crt
```
* These two files have to be readable by the ChirpStack Application Server user/group.
```sh
sudo chown appserver:appserver cs.key cs.crt
```
* Now open the configuration file.
```sh
sudo nano /etc/chirpstack-application-server/chirpstack-application-server.toml
```
* Search for `tls_cert` and `tls_key` in the `application_server.external_api` section and set these values as shown below.
```toml
tls_cert="/etc/chirpstack-application-server/cs.crt"
tls_key="/etc/chirpstack-application-server/cs.key"
```
* After restarting the Application Server and checking its status ...
```sh
sudo systemctl restart chirpstack-application-server.service
sudo systemctl status chirpstack-application-server.service
```
* ... you should be able to access the WebServer with a URL similar to this:
```
https://GATEWAY_IP:8080
```
* **Note** that it might be necessary to explicitly set the `https`. Using `http` instead should result in the following response (or a similar one):
```
Client sent an HTTP request to an HTTPS server.
```

### Changing the JWT Secret + Port Configuration
* The port on which the WebServer should listen can be changed in the same configuration file as used above (`/etc/chirpstack-application-server/chirpstack-application-server.toml`) by setting the `bind` option in the `application_server.external_api` section. The JWT secret is used for API authentication and it is strongly recommended to change it. The default value is `verysecret` and by definition a bad choice. The value can be set by changing the `jwt_secret` option in the `application_server.external_api` section. A good secret could be generated like this:
```sh
openssl rand -base64 32
```
* It could for example look like this:
```toml
jwt_secret="kxqExbs7wW6aGKkpKQF9batAyUu3Hy5XQuRYC3mzVZs="
```
***

### Configuration in the WebInterface
* Basic configuration is quite intuitive and you can edit/create users, organisations and so on.
* One thing that you might have to do to make Chirpstack work is delete the default gateway and create a new one
  * Go to Gateways and delete the default one
  * Create a new Gateway. You can chose everything as you will except for the GatewayID. You can get the ID by running the `gateway-version` command on the gateway.
* Further information on the WebInterface can be obtained via [ChirpStacks official documentation](https://www.chirpstack.io/application-server/).

### API Key generation
* If you plan to use the "automated" device registrator (currently not working, but the key can still be used to register the device at the Chirpstack API with the Chirpstack-Api-Tool), you will have to generate an API token. Log into your Chirpstack instance (default credentials: `admin`:`admin`), go to the API tab and create a new key. **Note** that the key will only be shown once and you won't be able to access it after leaving the page. Note it down somewhere.

## MQTT Configuration
* ChirpStack publishes most of its internal events on MQTT. This is used by the UGCC to get device messages and process them. The MQTT server used in this case is [Moquitto](https://mosquitto.org/). By default, it does not require any authentication which might not be optimal. Therefore, a user + password should be configured.
```sh
sudo mosquitto_passwd -c /etc/mosquitto/passwd user
```
* This command will create the moquitto password file `/etc/mosquitto/passwd` and the user `user`. It will prompt for a password for that user, you can generate it with the same command used to generate the JWT secret [above](#changing-the-jwt-secret--port-configuration).
```sh
openssl rand -base64 32
```
* Another option would be a password generator like [random.org](https://www.random.org/passwords/).
After generating the password file and user, Mosquitto needs to be configured to actually use it.
This can be done by creating the file `/etc/mosquitto/conf.d/auth.conf` with the following contents:
```
allow_anonymous false
password_file /etc/mosquitto/passwd
```

### Adjusting ChirpStack Configuration Files
* All ChirpStack components handle MQTT messaging themselves. That means, that all configuration files have to be updated to use the newly created credentials. These files are:
```
/etc/chirpstack-application-server/chirpstack-application-server.toml
/etc/chirpstack-application-server/chirpstack-gateway-bridge.toml
/etc/chirpstack-application-server/chirpstack-network-server.toml
/etc/chirpstack-application-server/chirpstack-network-server.eu_863_870.toml
```
* **Note** that the last file might differ in your case. It depends on your region/on the LoRa frequency you configured ChirpStack to use. In all of these files you will have to search for `mqtt server` and change the `username` and `password` variables nearby to the username and password you chose above.
After that, restart all the involved services and check if they are still running fine.
```sh
# Restart the services
sudo systemctl restart mosquitto
sudo systemctl restart chirpstack-application-server
sudo systemctl restart chirpstack-network-server
sudo systemctl restart chirpstack-gateway-bridge

# Check each status
sudo systemctl status mosquitto
sudo systemctl status chirpstack-application-server
sudo systemctl status chirpstack-network-server
sudo systemctl status chirpstack-gateway-bridge
```
* If you wan't to connect to the MQTT server for debug work, use the following command:
```sh
mosquitto_sub -h HOST -v -t "#" -u user -P PASS
```
* Where `HOST` can be replaced with `127.0.0.1` and `PASS` with the MQTT password you configured above.
After some time you should see messages appear.
***

## UGCC Setup
* The setup of the [uBirch-GoClient-ChirpStack-Connector](.) is divided into three parts.
These are:
  * the [installation](#ubirch-goclient-installation) and [configuration](#ubirch-goclient-configuration) of the [uBirch-GoClient](https://github.com/ubirch/ubirch-client-go)
  * the [installation](#ugcc-installation) and [configuration](#ugcc-configuration) of the [UGCC](.) itself
  * and the [setup](#fludia-sensor-setup) of a [Fludia](https://www.fludia.com/?lang=en) sensor

### uBirch GoClient Installation
* Before installing the [GoClient](https://github.com/ubirch/ubirch-client-go), you will have to install Golang.
```sh
sudo apt update && sudo apt install golang
```
* Now create a directory called `ubirch_client` in the home folder of the `pi` user and cd into it.
Download the latest stable release of the GoClient for Arm32: https://github.com/ubirch/ubirch-client-go/releases.
```sh
mkdir ~/ubirch_client && cd ~/ubirch_client
wget https://github.com/ubirch/ubirch-client-go/releases/download/v1.1.1/ubirch-client.linux_arm
```
* Make it executable:
```
chmod +x ubirch-client.linux_arm
```

### uBirch GoClient Configuration
* The GoClient can be configured by placing a file called `config.json` into the same directory as the executable. Details are described in the documentation of the GoClient. For this scenario, a config like the one below is suitable.
```json
{
  "devices": {
    "": ""
  },
  "secret": "16_BYTE_SECRET",
  "env": "prod",
  "TCP_addr": ":10000"
}
```
* The `devices` map will be filled with UUID:AUTH_TOKEN pairs as soon as they are known/after [registering a device at the uBirch backend](#device-registration-at-the-ubirch-backend). You can change the `env` field if you don't want to operate on the uBirch-`prod` environment. `secret` has to be replaced by a 16-Byte string which should be random. It can be obtained using the following command:
```sh
openssl rand -base64 16
```
* The port has to be specified manually since the default port is `8080`, which is already occupied by the ChirpStack WebInterface.
* Since the GoClient should start on boot, configuring a service for it is the next step. To achieve this, create the file `/etc/systemd/system/ubirch_client.service` with the following contents:
```
[Unit]
Description=uBirch go-client service
After=chirpstack-application-server.service
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=pi
WorkingDirectory=/home/pi/ubirch_client/
ExecStart=/home/pi/ubirch_client/ubirch-client.linux_arm

[Install]
WantedBy=multi-user.target
```
* Now you will have to reload the service file index. Start and enable the newly created service afterwards. **Note** that the service will fail to start as long as the `devices` map in the config file is empty.
```
sudo systemctl daemon-reload
sudo systemctl start ubirch_client
sudo systemctl enable ubirch_client
```

### UGCC Installation
#### Install Python 3.8
* The UGCC needs Python 3.8 which is not in the default repositories and therefore has to be installed manually.
```
sudo apt install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev tar wget vim

cd /tmp
sudo wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
sudo tar zxf Python-3.8.0.tgz
cd Python-3.8.0
sudo ./configure --enable-optimizations
sudo make -j 4
sudo make altinstall
cd /tmp
sudo rm -rf Python-3.8.0*
pip3.8 install --user --upgrade pip
```
* Clone [this](.) repository into the home directory of the user `pi`
```
cd && git clone https://github.com/UBOK19/ubirch-goclient-chirpstack-connector
```
* Install all needed Python modules
```
cd ubirch-goclient-chirpstack-connector
pip3.8 install -r requirements.txt
```

### UGCC Configuration
* An actual desciption of the different values in the configuration file (...) is given in the [main Readme](README.md).
* The `mqtt.user` and `mqtt.pass` fields have to be adapted to the values configured above during the [MQTT configuration](#mqtt-configuration)
* The same goes for `goClient.url` value, specifically the port, which is configured during the [GoClient configuration](#ubirch-goclient-configuration)
* As the UGCC should also be started on boot, it also needs a service file: `/etc/systemd/system/ugcc.service`
```
[Unit]
Description=uBirch UGCC service
After=chirpstack-application-server.service
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=pi
Environment=UGCC_CONFIG_FILE=/home/pi/ubirch-goclient-chirpstack-connector/config.json
ExecStart=python3.8 /home/pi/ubirch-goclient-chirpstack-connector/src/main.py

[Install]
WantedBy=multi-user.target
```
* Now you will have to reload the service file index. Start and enable the newly created service afterwards.
```
sudo systemctl daemon-reload
sudo systemctl start ugcc
sudo systemctl enable ugcc
```
* A special characteristic of the UGCC is that it will log to the normal Systemd log before loading the configuration file and then it will start logging to the specified log file

### Fludia Sensor Setup
* First, note down the LoRa EUI of the sensor.
* ~~The steps below only apply to manual device registration. For a more up-to-date guide take a look at [automatic device registration](AUTO-DEVREG.md).~~
* ~~**NOTE** that if you do not want to use the automatic device registrator you must disable it in the configuration file of the UGCC.~~

#### Generate a UUID
* A UUID is required to register a device at the uBirch backend, this UUID can be generated from its EUI using the `uuidgen.py` script contained in this repository. It can simply be executed with python and will ask for the device EUI, after that it will print out the UUID
```
python3.8 uuidgen.py
```
```
|===== UUID Generator =====|
Namespace: eon.uuid.trustservice -> ubirch / ee2a7eee-4ae4-577a-a647-07877df38198 -> e7ab97ca-20fd-597e-a0e4-3e0b41a1a664
DevEUI > aaaaaaaaaaaaaaaa
UUID: 5dfe791d-7289-5067-99c5-d6d0a1909a54
```
* **Note** that the EUI will be auto-lowercased

#### Device Registration at the uBirch Backend
* The UUID can be used to register the device. Mind the uBirch backend environment used during configuring the [GoClient](#ubirch-goclient-configuration) and the [UGCC](#ubirch-goclient-configuration). For the `prod` env, the console URL would be https://console.prod.ubirch.com

#### Device Registration at the ChirpStack WebInterface
* Detailed information about ChirpStack [applications](https://www.chirpstack.io/application-server/use/applications/) and [devices](https://www.chirpstack.io/application-server/use/devices/) can be found in the official documentation.
* To increase your rate of success, you can go to the `Device-profiles` tab, edit the default device profile, and set the `LoRaWAN MAC version` option in the `GENERAL` tab to `1.0.0`.
* Now you will have to create an application.
* You should now be in the `DEVICES` of the application. Click on the `+CREATE` button.
* Enter a name for the new device, as well as a describtion and the device EUI.
  * ~~If you intend to use the automatic device registrator you will have to provide extra informaiton using the description field, see [above](#use-the-automatic-device-registrator-recommended).~~
* Chose the default device profile and make sure that both the `Disable frame-counter validation` and the `Device is disabled` boxes are not checked.
* Press on the `CREATE DEVICE` button.
* You will now have to manually set the `Application key` for your device, since Fludia sensors have an application key "burned in". This hard-coded key must be obtained from Fludia. Go to the `KEYS (OTAA)` tab and paste the key into the `Application key` field. Press on `SET DEVICE-KEYS`.
* After switching to the `LORAWAN FRAMES` tab and reconnecting the Fludia sensor to the Lora-Link (**ATTENTION:** this will reset the calibration and you will have to re-calibrate the sensor. It is also possible to just wait for the sensor to send an measurement.) you should see something about a `Join Request` and `Join Accept`. Check the `ACTIVATION` tab, there should be some fields (`Device address`, `Network session key`, ...) with values that you can't edit.
* **Note** that the log of the UGCC may now contain errors like the following:
```
[2021-01-09 21:06:19,219]--[DEBUG   ]  Trying to process a message from 'application/2/device/xxxxxxxxxxxxxxxx/rx' ...
[2021-01-09 21:06:19,220]--[ERROR   ]  Can not process a message from a device with a unknown EUI: xxxxxxxxxxxxxxxx
```
* These are caused by the device not being existent in the configuration filed, which will be fixed in the [next step](#adjusting-config-files-for-the-new-device)
* Besides that there may also be other error related to the initial messages of the sensor not actually containing measurements but debug data, which the UGCC can not decode. This is expected behaviour.

#### Adjusting config files for the new device
* Given the UUID and backend authentication token which can be obtained from the uBirch console, the configuration files of the GoClient and UGCC can be completed. See [GoClient configuration](#ubirch-goclient-configuration) and [UGCC configuration](#ugcc-configuration).