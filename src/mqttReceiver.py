import paho.mqtt.client as mqtt
from typing import Callable
import time
import logging
import sys

import config


class MQTTReceiver():
  def __init__(self, host : str, port : int, user : str, passwd : str, messageCb : Callable, log : logging.Logger):
    """ init function of the MQTTReceiver class """
    self.mqttClient : mqtt.Client = None
    self.log = log
    self.messageCB = messageCb

    # get the config valuess
    self.rhost = host
    self.rport = port
    self.user = user
    self.passwd = passwd

    # set up the connection
    self.setup()

    # enter the loop
    self.mqttClient.loop_forever()

    return

  def setup(self):
    """ this function sets up the MQTT client and connection """
    # check if the client is already initialised/if this is a reconnect
    if not self.mqttClient:
      self.mqttClient = mqtt.Client("goclient-chirpstack-connector" + str(int(time.time())))
      self.mqttClient.on_connect = self._onConnect
      self.mqttClient.on_message = self._onMessage
      self.mqttClient.on_disconnect = self._onDisconnect
      self.mqttClient.on_subscribe = self._onSubscribe

      # set the password
      self.mqttClient.username_pw_set(self.user, self.passwd)

    self.log.debug("Trying to connect to MQTT-Broker @ '%s:%d' ..." % (self.rhost, self.rport))

    # only connect; subscribing to a topic is done by _onConnect
    try:
      self.mqttClient.connect(self.rhost, port=self.rport)
    except Exception as e:
      self.log.error("Error connecting to the MQTT-Broker @ '%s:%d'!" % (self.rhost, self.rport))
      self.log.exception(e)

  def _onConnect(self, client : mqtt.Client, userdata, flags, status : int):
    """ function to be registered as 'on_connect' callback """
    if status == 0:
      self.log.info("Connected to MQTT-Broker @ '%s:%d'" % (self.rhost, self.rport))

      # subscribe to application/# (msg_id = (ret, msg_id))
      self.log.debug("Trying to subscribe to 'application/#' ...")
      msg_id = self.mqttClient.subscribe("application/#", 2)

      if msg_id[0] == 0:
        self.log.debug("Subscription ackknowledgement pending for request with mid=%s" % msg_id[1])
      else :
        self.log.error("Failed to subscribe to 'application/#'! (%d)" % msg_id[0])

        sys.exit(-1)
    else:
      self.log.error("Failed to connect to MQTT-Broker @ '%s:%d'!" % (self.rhost, self.rport))

      sys.exit(-1)

    return

  def _onMessage(self, client, userdata, msg : mqtt.MQTTMessage):
    """ function to be registered as 'on_message' callback """
    self.log.debug("Received a message on '%s'" % msg.topic)

    # call the registered callback
    self.messageCB(msg)

    return

  def _onDisconnect(self, client, userdata, status):
    """ function to be registered as 'on_disconnect' callback """
    if status == 0:
      self.log.info("Disconnected from MQTT-Broker @ '%s:%d'" % (self.rhost, self.rport))
    else:
      self.log.warning("Unexpectedly disconnected from MQTT-Broker @ '%s:%d'! Attempting to reconnect ..." % (self.rhost, self.rport))
      self.setup()

    return

  def _onSubscribe(self, client : mqtt.Client, userdata, msg_id, granted_qos):
    """ function to be registered as 'on_subscribe' callback """
    self.log.debug("The MQTT-Broker granted a QoS=%d for the subscription request with mid=%d" % (granted_qos[0], msg_id))

    return
