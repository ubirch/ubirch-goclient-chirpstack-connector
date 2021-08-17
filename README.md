# ubirch-goclient-chirpstack-connector
The main function of the uBirch-GoClient-Chirpstack-Connector is forwarding data extracted out of LoRa messages published via. MQTT by ChirpStack to the uBirch-GoClient, but it also handles forwarding this data to other endpoints, which have to be configured by making some slight modifications to the code.

## Run it
```
python3.8 src/main.py
```

## Requirements
0. Python 3.8+
1. A running instance of [ChirpStack](https://chirpstack.io)
2. A running instance of the [uBirch go-client](https://github.com/ubirch/ubirch-client-go)
3. Access data for the [Fludia](https://fludia.com/?lang=en) API
4. Access data for the [re.alto](https://realto.io/) API

* If you are using a RAK7244C gateway to set up the UGCC, you can follow [this](GATEWAY.md) guide

## Configuration
All configuration values can be set via the environment or a configuration file which you will have to create. The default path for the configuration file is the folder above the current directory (the UGCC will look for it in the directory above the one it is started from). This can be changed by setting the `UGCC_CONFIG_FILE` environment variable. It is recommended to use absolute paths. `UGCC_` is a prefix for all environment variables used by the UGCC. It generally is *not* recommended to use environment variables and values from the configuration file have a higher priority. Injecting the following values via the environment might even cause the program to crash:
```
config.devices (UGCC_DEVICES)
config.ubpass (UGCC_UBPASS)
```
This is caused by the ability to add and update devices while running, see [Adding New Devices](#adding-new-devices). An example path for the configuration file might be `/home/pi/ubirch-goclient-chirpstack-connector/config.json` (you will have to pass this path the the UGCC using the env) and its contents should look like this:
```json
{
  "log": {
    "level": 10,
    "file": "/home/pi/ugcc.log",
    "format": "[%(asctime)s]--[%(levelname)-8s]  %(message)s",
    "maxBytes": 2000000.0,
    "backupCount": 3
  },
  "devices": [
    {
      "deviceEUI": "SOME-EUI",
      "deviceUUID": "UUID",
      "deviceID": "someid"
    }
  ],
  "ubpass": {
    "UUID": "AUTH-TOKEN"
  },
  "http": {
    "timeout": 10,
    "attempts": 3,
    "retryDelay": 3
  },
  "mqtt": {
    "user": "USER",
    "pass": "PASSWORD",
    "host": "127.0.0.1",
    "port": 1883
  },
  "goClient": {
    "url": "http://127.0.0.1:10000/"
  },
  "exampleClient": {
    "url": "https://example.client.com",
    "pass": "myPa5s"
  }
}
```
### Logging Configuration
Note that before the configuration file is loaded, logs will be written to `"/dev/stdout"`
#### 'UGCC_DEFAULT_LOG_FILE'
```
Descr:  Sets the log file to be used for post-config logging.
        The default value is "/dev/stdout".
Type:   str
Examples:

  "/dev/stdout"   # Standard Output
  "/log/ugcc.log"
```
#### `log.level` / `UGCC_LOG_LEVEL`
```
Descr:  Sets the log level to be used for the python logging module.
        (https://docs.python.org/3/library/logging.html#levels)
        The default value is 10 (Debug).
Type:   int
Values:

  50    # Critical
  40    # Error
  30    # Warning
  20    # Info
  10    # Debug
  0     # Not-Set
```

#### `log.file` / `UGCC_LOG_FILE`
```
Descr:  Sets the file to which the log should be written to.
        The default value is "/dev/stdout". Note that "/dev/stdout" will disable log rotation.
Type:   str
Examples:

  "/dev/stdout"   # Log to standard output
  "/dev/null"     # Log to the null-device/don't log
  "/var/log/ugcc.log"   # Log to /var/log/ugcc.log
```

#### `log.format` / `UGCC_LOG_FORMAT`
```
Descr:  Sets the log format to be used for the python logging module.
        (https://docs.python.org/3/library/logging.html#logging.Formatter)
        The default value is the one shown in the example below.
Type:   str
Example:

  "[%(asctime)s]--[%(levelname)-8s]  %(message)s"   # -> [2020-08-01 9:19:01,683]--[WARNING]  log message ...
```

#### `log.maxBytes` / `UGCC_LOG_MAX_BYTES`
```
Descr:  Sets the maximum amount of bytes to be logged into a log file before rotating
Type:   int
Example:

  20000000  # Rotate after 20mb
  10000000  # Rotate after 10mb
  5000000   # Rotate after 5mb
```

#### `log.backupCount` / `UGCC_LOG_BACKUP_COUNT`
```
Descr:  Sets the amount of log files to keep. If a rotation is triggered and this limit was already 
        reached, the oldest log file will be deleted.
Type:   int
Example:

  10  #   Keep ten files
  5   #   Keep five filed
  1   #   Keep only one file
```

### Device Configuration
#### `devices` / `UGCC_DEVICES`
```
Descr:  Stores information about known devices. Only messages from configured devices can be processed and forwarded.
Type:   list
Example:

  [
    {
      "deviceEUI": "xxxxxxxxxxxxxxxx",
      "deviceUUID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "deviceID": "xxxxxxxx"
    },
    {
      ...
    },
    ...
  ]

  #
  # deviceEUI: The LoRa EUI of the device.
  # deviceUUID: The UUID of the device.
  # deviceID: ID of the meter
  #
```

### uBirch Password Configuration
#### `ubpass` / `UGCC_UBPASS`
```
Descr:  Stores UUID:PASSWORD pairs for different devices.
Type:   Json-Object (json.loads())
Example:

  {
    "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }

  # UUID:PASSWORD
```

### HTTP Configuration
#### `http.timeout` / `UGCC_HTTP_TIMEOUT`
```
Descr:  Timeout for HTTP-Post request attempts.
        The default value is 10.
Type:   int
Examples:

  5
  10
  20
```

#### `http.attempts` / `UGCC_HTTP_ATTEMPTS`
```
Descr:  Amount of attempts for sending a HTTP-Post request.
        The default value is 3.
Type:   int
Examples:

  1
  2
  3
```

#### `http.retryDelay` / `UGCC_HTTP_RETRY_DELAY`
```
Descr:  The amount of seconds between HTTP-Post request attempts.
        The default value is 5.
Type:   int
Examples:

  3
  4
  5
```

### MQTT Configuration
#### `mqtt.host` / `UGCC_MQTT_HOST`
```
Descr:  The MQTT host to connect to.
        The default value is "localhost".
Type:   str
Examples:

  "127.0.0.1"
  "localhost"
  "192.168.178.1"
```

#### `mqtt.port` / `UGCC_MQTT_PORT`
```
Descr:  The port to connect to on the MQTT host.
        The default value is 1883.
Type:   int
Examples:

  1883
  1884
  8883
```

#### `mqtt.user` / `UGCC_MQTT_USER`
```
Descr:  The user to be used for MQTT authentication.
Type:   str
Example:

  "user"
```

#### `mqtt.pass` / `UGCC_MQTT_PASS`
```
Descr:  The password to be used for MQTT authentication.
Type:   str
Example:

  "password123"
```

### Go-Client Configuration
#### `goClient.url` / `UGCC_GOCLIENT_URL`
```
Descr:  The URL of the uBirch Go-Client.
        NOTE that the trailing '/' must be included.
Type:   str
Example:

  "http://localhost:10000/"
```

## Adding new devices
This can be done by directly modifying the `devices` and `ubpass` values in the configuration file and **restarting** the UGCC afterwards.
Besides that, you will also have to modify the configuration file of the uBirch GoClient and **restart it**.

## Adding new data backends
To add a new data backend, a few additions and alterations have to done:

### [config.py](src/config.py) 
Define variables needed to work with your backend, i.e.: `exampleClientUrl`, `exampleClientPass` 

```python
# defining variables
self.exampleClientUrl : str = None
self.exampleClientPass : str = None
```
Load the variables from the config or env:
```python
self.exampleClientUrl = self._getValueConfigOrEnv(["exampleClient", "url"], "UGCC_EXAMPLECLIENT_URL", default=self.exampleClientUrl)
self.log.debug("exampleClientUrl => %s" % self.exampleClientUrl)
self.exampleClientPass = self._getValueConfigOrEnv(["exampleClient", "pass"], "UGCC_EXAMPLECLIENT_PASS", default=self.exampleClientPass)
self.log.debug("exampleClientPass => len = %d" % len(self.exampleClientPass))
```
### [config.json](src/config.json)
Add new configuration values for the backend, i.e.:
```json
{
  ...
  "exampleClient": {
    "url": "https://example.client.com",
    "pass": "myPa5s"
  },
  ...
}
```
### [exampleConnector.py](src/exampleConnector.py)
Adapt the example connector to fit your needs. This will mainly consist of changing the file name, the class name, log messages and adapting other details like how the URL is assembled. Alterations to the data itself should be kept minimal, since the connector should only handle sending. One thing that cannot be modified is that the connector class needs a function called `sendData` with the following signature:
```
def sendData(self, data : str, device : devices.Device)
```
The `data` parameter contains the JSON object created by the message processor (see `mkDataPacket()` in [messageProcessor.py](src/messageProcessor.py)) dumped into a string. The `device` parameter is the device object of the device that sent the message to which the data corresponds. See [devices.py](src/devices.py) for its members. If the send functions needs more information than can be delivered by the two parameters, consider passing those information to the class when initializing it.
### [main.py](src/main.py)
Import the new conncetor:
```python
import exampleConnector
```
Initialize the connector:
```python
self.exampleConnector = exampleConnector.ExampleConnector(
    self.config.exampleClientUrl, self.config.exampleClientPass, self.http, self.log
)
```
Add the new connector to the endpoint list:
```python
self.endpoints = [
    ["uBirch go-client", self.goClientConnector.sendData],
    ["example client", self.exampleConnector.sendData]
]
```

## Verification
To verify the data, got to [ubirch console](https://console.prod.ubirch.com/verification/json) and enter the base64 encoded hash of the data.

### Create a hash for verification
To create a hash for verification, you can use the following python script:
```
>>> import json, hashlib, base64
>>> msgjson = {"device_properties":{"deveui":"70b3d54a00000aac"},"meterId":"SomeID","payload_cleartext":"46000007000000000000","r_diff-10":0,"r_diff-15":0,"r_diff-5":0,"reading":93,"timestamp":"2020-08-06T12:44:02.083157+02:00","type":"uplink"}
>>> msgstr = json.dumps(msgjson, sort_keys=True, indent=None, separators=(",", ":"))
>>> hash = hashlib.sha256(bytes(msgstr, "utf8"))
>>> base64.b64encode(hash.digest())
b'irjr79EU//D3ex0SZI+r9G8chBiEPefk62u+DCzOLlE='
>>> 
```
Now copy the output from the last line (e.g: `irjr79EU//D3ex0SZI+r9G8chBiEPefk62u+DCzOLlE=`) and paste it to the verification field.
If you do not have an account at ubirch, set one up, or use curl:
```
curl -d 'juujpm23LNbltrKqRtRH+0V9pMnbZ2HABGUNgFrM/KY=' https://verify.demo.ubirch.com/api/upp/verify
```
