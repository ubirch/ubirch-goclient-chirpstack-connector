# ubirch-goclient-chirpstack-connector
The main function of the uBirch-GoClient-Chirpstack-Connector is forwarding data extracted out LoRa messages published via. MQTT by ChirpStack to the uBirch-GoClient, but it also handles forwarding this data to other endpoints, namely [Fludia](https://fludia.com/?lang=en) and [re.alto](https://realto.io/).

## Run it
```
python src/main.py
```

## Requirements
0. Python 3.8+
1. A running instance of [ChirpStack](https://chirpstack.io)
2. A running instance of the [uBirch go-client](https://github.com/ubirch/ubirch-client-go)
3. Access data for the [Fludia](https://fludia.com/?lang=en) API
4. Access data for the [re.alto](https://realto.io/) API

## Configuration
All configuration values can be set via the environment or a configuration file. The default path for the configuration file if the folder above the `src` directory. This can be changed by setting the `UGCC_CONFIG_FILE` environment variable. `UGCC_` (UbirchGoclientChirpstackConnector) is a prefix for all environment variables. All configuration values that have no default value must be set manually.

### Logging Configuration
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
        The default value is "/dev/stdout".
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
      "roundsPkW": 70,
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
  # roundsPkW: Meter-specific
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
        The default value is 5.
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
        The default value is 3.
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
  "123.654.789.0"
```

#### `mqtt.port` / `UGCC_MQTT_PORT`
```
Descr:  The port to connect to on the MQTT host.
        The default value is 1883.
Type:   int
Examples:

  1883
  2000
  1234
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

  "http://localhost:8080/"
```

### re.alto Configuration
#### `realto.url` / `UGCC_REALTO_URL`
```
Descr:  The URL of the re.alto API.
        NOTE that the trailing '/' must be included.
Type:   str
Example:

  "https://reactor-poc.azure-api.net/collector/"
```

#### `realto.subKey` / `UGCC_REALTO_SUBKEY`
```
Descr:  The subscription key for the re.alto API.
Type:   str
Example:

  "SUBKEY"
```

### Fludia Configuration
#### `fludia.url` / `UGCC_FLUDIA_URL`
```
Descr:  The URL of the Fludia API.
        NOTE that the trailing '/' must be removed.
Type:   str
Example:

  "https://fm430-api.fludia.com/v1/callback"
```

#### `fludia.user` / `UGCC_FLUDIA_USER`
```
Descr:  The username to be used to authenticate to the Fludia API.
Type:   str
Example:

  "username"
```

#### `fludia.pass` / `UGCC_FLUDIA_PASS`
```
Descr:  The password to be used to authenticate to the Fludia API.
Type:   str
Example:

  "password123"
```