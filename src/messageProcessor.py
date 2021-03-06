import json
import base64
import datetime

import devices
import log
import mqttReceiver


class MessageProcessor():
  def __init__(self, devices: devices.Devices, log: log.logging.Logger):
    """ init function of the MessageProcessor class """
    self.devices = devices
    self.log = log

    return

  def mkDataPacket(self, message: mqttReceiver.mqtt.MQTTMessage) -> dict:
    """ this function creates a data packet (json) out of a message received via mqtt """
    # parse the mqtt payload (json)
    self.log.debug("Trying to parse the Json payload ...")
    payload = self.getMessagePayload(message)

    if not payload:
      self.log.error("Error getting payload from the message!")

      return None

    # get the uplink id
    uplinkID = self._getValueFromDict(["rxInfo", 0, "uplinkID"], payload)

    self.log.info("Processing a message with uplinkID='%s'" % uplinkID)
    
    # take the base64 encoded data, decode it and put it into json format
    self.log.debug("Trying to decode the application data ...")
    data = self.decodeData(payload["data"])

    if not data:
      self.log.error("Error decoding application data!")

      return None

    self.log.debug("Data for uplinkID='%s': '%s'" % (uplinkID, str(data)))

    # get the device that sent this uplink
    self.log.debug("Trying to find a matching device for EUI: '%s'" % payload["devEUI"])
    device = self.devices.getDeviceByEUI(payload["devEUI"])

    # check if a matching device was found
    if not device:
      self.log.error("Error finding a matching device for EUI: '%s'" % payload["devEUI"])

      return None

    self.log.debug("Found a matching device for EUI '%s' with UUID '%s'" % (device.eui, device.uuid))

    # get the time in rfc3339 format
    time = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()

    # assemble the packet
    dpkt = {
      "deveui": device.eui,
      "deviceId": device.id,
      "timestamp": time,
      "data": data
    }

    return dpkt

  def getMessagePayload(self, message: mqttReceiver.mqtt.MQTTMessage) -> dict:
    """ this function extracts the json payload out of the mqtt message """
    try:
      return json.loads(message.payload)
    except Exception as e:
      self.log.error("Error parsing Json-Payload of message: '%s'" % str(message.payload))
      self.log.exception(e)
      return None

  def decodeData(self, data: str) -> dict:
    """ this function decodes the data and puts it into a json object """
    # remove base64 coding
    try:
      dataBytes = base64.decodebytes(bytes(data, "utf8"))
    except Exception as e:
      self.log.error("Error decoding base64 encoded application data: '%s'" % data)
      self.log.exception(e)

      return None

    self.log.debug("Data bytes: '%s'" % str(dataBytes))

    '''
    ADD HERE: custom data parsing.
    '''
    byte1 = dataBytes[0]
    byte2 = dataBytes[1]
    byte3 = dataBytes[2]
    byte4 = dataBytes[3]
    
    return {
      "rawBytes": "".join(format(x, "02x") for x in dataBytes), 
      "val1": byte1,
      "val2": byte2,
      "val3": byte3,
      "val4": byte4
    }


  def _getValueFromDict(self, keyPath: list, currentObj: dict) -> object:
    """ this function gets an object from the config object: config[path[0]][path[1]][path[n]] """
    if len(keyPath) == 0 or not currentObj:
      return currentObj
    elif type(currentObj) == list and type(keyPath[0]) == int:
      return self._getValueFromDict(keyPath[1:], currentObj[keyPath[0]])
    elif type(currentObj) != dict:
      return None
    else:
      return self._getValueFromDict(keyPath[1:], currentObj.get(keyPath[0]))