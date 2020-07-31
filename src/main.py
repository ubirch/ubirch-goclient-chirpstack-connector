import os
import sys
import logging

import log
import config
import mqttReceiver
import devices
import messageProcessor
import goClientConnector
import fludiaAPIConnector


# get the config and log file path
CONFIGFILE = os.getenv("CONFIG_FILE", "../config.json")
CONFIG_FLAG = "--config"


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

    # initialise the go-client connector
    self.goClientConnector = goClientConnector.GoClientConnector(
      self.config.goClientUrl, self.devices, self.log
    )

    # initialise the fludia api connector
    self.fludiaApiConnector = fludiaAPIConnector.FludiaAPIConnector(
      self.config.fludiaUrl, self.config.fludiaUser, self.config.fludiaPass, self.devices, self.log
    )

    # initialise the MQTTReceiver
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
        self.log.error

      self.log.debug("Finished data packet: '%s'" % str(datapkt))

      # try to send it to the go client
      self.log.debug("Trying to send the measurement to the go-client ...")

      try:
        self.goClientConnector.sendData(datapkt)
      except Exception as e:
        self.log.error("Error sending a measurement to the go-client!")
        self.log.exception(e)

        return

      # try to send it to the fludia-api
      self.log.debug("Trying to send the measurement to the Fludia API")

      try:
        self.fludiaApiConnector.sendData(datapkt)
      except Exception as e:
        self.log.error("Error sending a measurement to the Fludia API!")
        self.log.exception(e)
    else:
      # ignore the message
      return

# initialise the main class
if __name__ == "__main__":
  Main()