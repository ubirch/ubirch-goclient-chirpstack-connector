import os
import sys
import logging

import log
import config
import mqttReceiver
import devices
import messageProcessor
import httpSend
import goClientConnector
import fludiaAPIConnector
import realtoConnector


# get the config and log file path
CONFIGFILE = os.getenv("UGCC_CONFIG_FILE", "../config.json")


class Main():
  def __init__(self):
    """ init function of the main class """
    self.mqttReceiver = None
    self.config : config.Config = None
    self.log : logging.Logger = None
    self.devices : devices.Devices = None
    self.messageProcessor : messageProcessor.MessageProcessor = None
    
    # set up the inital logger (pre-config)
    self.log = log.setupLog(initialLogger=True, default_logfile="/dev/stdout")

    # check for success
    if not self.log:
      sys.exit(-1)

    # load the config
    self.config = config.Config(CONFIGFILE, self.log)

    # check if the config was loaded successfully and get it
    if not self.config.initSuccess:
      sys.exit(-1)

    # load the final logger (post-config)
    self.log = log.setupLog(self.config, initialLogger=False, default_logfile="/dev/stdout")

    # check for success
    if not self.log:
      sys.exit(-1)

    # load configured devices
    self.devices = devices.Devices(self.config, self.log)

    if self.devices.getDevlistLen() < 1:
      self.log.warning("No devices were found in the configuration file!")
    else:
      self.log.debug("Found and added %d device(s) to the device list" % self.devices.getDevlistLen())

    # initialise the message processor
    self.messageProcessor = messageProcessor.MessageProcessor(self.devices, self.log)

    # initalise the http class
    self.http = httpSend.HttpSend(
      self.config.httpTimeout, self.config.httpAttempts, self.config.httpRetryDelay, self.log
    )

    # initialise the go-client connector
    self.goClientConnector = goClientConnector.GoClientConnector(
      self.config.goClientUrl, self.devices, self.http, self.log
    )

    # initialise the fludia api connector
    self.fludiaApiConnector = fludiaAPIConnector.FludiaAPIConnector(
      self.config.fludiaUrl, self.config.fludiaUser, self.config.fludiaPass, self.http, self.log
    )

    # initalise the realto api connector
    self.realtoApiConnector = realtoConnector.RealtoConnector(
      self.config.realToUrl, self.config.realToSubKey, self.http, self.log
    )

    # create a array of endpoints
    self.endpoints = [
      ["uBirch go-client", self.goClientConnector.sendData],
      ["Fludia API", self.fludiaApiConnector.sendData],
      ["re.alto API", self.realtoApiConnector.sendData]
    ]

    # initialise the MQTTReceiver (BLOCKING)
    self.mqttReceiver = mqttReceiver.MQTTReceiver(
      self.config.mqttHost, self.config.mqttPort, self.config.mqttUser,
      self.config.mqttPass, self.messageCB, self.log
    )

    return

  def messageCB(self, message : mqttReceiver.mqtt.MQTTMessage):
    """ function to be registered as message callback (MQTT) """

    # check if it is a device message
    if mqttReceiver.mqtt.topic_matches_sub("application/+/device/+/rx", message.topic):
      # process the message
      self.log.debug("Trying to process a message from '%s' ..." % message.topic)

      try:
        datapkt = self.messageProcessor.mkDataPacket(message)
      except Exception as e:
        self.log.error("Error creating a data packet out of a message!")
        self.log.exception(e)

        return

      if not datapkt:
        self.log.error("Error creating a data packet out of a message!")

        return

      self.log.debug("Finished data packet: '%s'" % str(datapkt))

      try:
        # try to send it to all the endpoints
        for endpoint in self.endpoints:
          self.log.debug("Trying to send the measurement to the %s" % endpoint[0])

          try:
            endpoint[1](datapkt)
          except Exception as e:
            self.log.error("Error sending a measurement to the %s!" % endpoint[0])
            self.log.exception(e)
      except Exception as e:
        return
    else:
      # ignore the message
      return

# initialise the main class
if __name__ == "__main__":
  Main()