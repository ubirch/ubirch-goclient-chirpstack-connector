import os
import sys
import logging
import json
import traceback

import log
import config
import mqttReceiver
import devices
import messageProcessor
import httpSend
import goClientConnector
import dataConnector

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
    self.log = log.setupLog(initialLogger=True)

    # register the unhandled exception handler
    sys.excepthook = self._unhandledExceptionHandler

    # check for success
    if not self.log:
      sys.exit(-1)

    # load the config
    self.config = config.Config(CONFIGFILE, self.log)

    # check if the config was loaded successfully and get it
    if self.config.readCfg() == False:
      sys.exit(-1)

    self.log.info("Transitioning to the final logger")

    # load the final logger (post-config)
    self.log = log.setupLog(self.config, initialLogger=False)

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
      self.config.goClientUrl, self.http, self.log
    )

    # initialize dataConnector
    self.dataConnector = dataConnector.DataConnector(
      self.config.dataClientUrl, self.config.dataClientPass, self.http, self.log
    )

    # create an array of endpoints
    self.endpoints = [
      ["uBirch go-client", self.goClientConnector.sendData],
      ["data client", self.dataConnector.sendData]
    ]

    # initialise/run the MQTTReceiver (BLOCKING)
    self.mqttReceiver = mqttReceiver.MQTTReceiver(
      self.config.mqttHost, self.config.mqttPort, self.config.mqttUser,
      self.config.mqttPass, self.messageCB, self.log
    )

    # inform about the MQTTReceiver having terminated and exit
    self.log.info("The MQTTReceiver terminated - Exiting!")

    return


  def _unhandledExceptionHandler(self, eType, eVal, eTrace):
    msg = "".join(traceback.format_exception(eType, eVal, eTrace))

    self.log.critical("Unhandled exception: %s", msg)

  def messageCB(self, message : mqttReceiver.mqtt.MQTTMessage):
    """ function to be registered as message callback (MQTT) """

    try:
      # check if it is a device message
      if mqttReceiver.mqtt.topic_matches_sub("application/+/device/+/rx", message.topic):
        # process the message
        self.log.debug("Trying to process a message from '%s' ..." % message.topic)

        # check if the message comes from a known device
        eui = self.getDevEUIFromTopic(message.topic)

        device = self.devices.getDeviceByEUI(eui)

        if not device:
          self.log.warning("Unknown device EUI ('%s')!" % eui)

          return

        # try to create the data packet
        try:
          datapkt = self.messageProcessor.mkDataPacket(message)
        except Exception as e:
          self.log.error("Error creating a data packet out of a message!")
          self.log.exception(e)

          return

        if not datapkt:
          self.log.error("Error creating a data packet out of a message!")

          return

        # sort the json object and string-ify it
        data = json.dumps(datapkt, sort_keys=True, indent=None, separators=(",", ":"))

        self.log.debug("Finished data packet: '%s'" % data)

        try:
          # try to send it to all the endpoints
          for endpoint in self.endpoints:
            self.log.debug("Trying to send the measurement to the %s" % endpoint[0])

            try:
              endpoint[1](data, device)
            except Exception as e:
              self.log.error("Error sending a measurement to the %s!" % endpoint[0])
              self.log.exception(e)
        except Exception as e:
          return
      else:
        # ignore the message
        return
    except Exception as e:
      self.log.error("Error processing a message on topic %s!" % message.topic)
      self.log.exception(e)

  def getDevEUIFromTopic(self, topic : str):
    """ get the device ID from the topic string of a message """

    #
    # The topic-structure of a message:
    #   "application/APPLICATION_NAME/device/DEVICE_ID/rx"
    #

    topicList = topic.split("/")

    if len(topicList) != 5:
      return None
    else:
      return topicList[3]


# initialise the main class
if __name__ == "__main__":
  Main()
