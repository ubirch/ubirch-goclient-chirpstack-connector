import json
import base64
import struct
import datetime

import devices
import log
import mqttReceiver



class MessageProcessor():
  def __init__(self, devices : devices.Devices, log : log.logging.Logger):
    """ init function of the MessageProcessor class """
    self.devices = devices
    self.log = log

    return

  def mkDataPacket(self, message : mqttReceiver.mqtt.MQTTMessage) -> dict:
    """ this function creates a data packet (json) out of a message received via mqtt """
    # parse the mqtt payload (json)
    self.log.debug("Trying to parse the Json payload ...")
    payload = self.getMessagePayload(message)

    if not payload:
      return None

    # get the uplink id
    uplinkID = self._getValueFromDict(["rxInfo", 0, "uplinkID"], payload)

    self.log.info("Processing a message with uplinkID='%s'" % uplinkID)
    
    # take the base64 encoded data, decode it and put it into json format
    self.log.debug("Trying to decode the application data ...")
    data = self.decodeData(payload["data"])

    if not data:
      return None

    self.log.debug("Data for uplinkID='%s': '%s'" % (uplinkID, str(data)))

    # get the device that sent this uplink
    self.log.debug("Trying to find a matching device for EUI: '%s'" % payload["devEUI"])
    device = self.devices.getDeviceByEUI(payload["devEUI"])

    # check if a matching device was found
    if not device:
      self.log.error("Error finding a matching device for EUI: '%s'" % payload["devEUI"])

      return None

    self.log.debug("Found a matching device for EUI '%s' with UUID '%s', ID '%s' and kWh/Rot=%d" % (device.eui, device.uuid, device.id, device.roundsPkW))

    # get the total amount of Wh
    totalWh = self.roundsToWh(data["totalRot"], device.roundsPkW)
    totalWh_1 = self.roundsToWh(data["lastDiff1"], device.roundsPkW)
    totalWh_2 = self.roundsToWh(data["lastDiff2"], device.roundsPkW)
    totalWh_3 = self.roundsToWh(data["lastDiff3"], device.roundsPkW)

    # get the time in rfc3339 format
    time = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()

    # assemble the packet
    dpkt = {
      "device_properties": {
        "deveui": device.eui
      },
      "meterId": device.id,
      "reading": totalWh,
      "r_diff-5": totalWh_1,
      "r_diff-10": totalWh_2,
      "r_diff-15": totalWh_3,
      "timestamp": time,
      "payload_cleartext": data["rawBytes"],
      "type":"uplink"
    }

    return dpkt

  def getMessagePayload(self, message : mqttReceiver.mqtt.MQTTMessage) -> dict:
    """ this function extracts the json payload out of the mqtt message """
    try:
      return json.loads(message.payload)
    except Exception as e:
      self.log.error("Error parsing Json-Payload of message: '%s'" % str(message.payload))
      self.log.exception(e)
      return None

  def decodeData(self, data : str) -> dict:
    """ this function decodes the data and puts it into a json object """
    # remove base64 coding
    try:
      dataBytes = base64.decodestring(bytes(data, "utf8"))
    except Exception as e:
      self.log.error("Error decoding base64 encoded application data: '%s'" % data)
      self.log.exception(e)

      return None

    self.log.debug("Data bytes: '%s'" % str(dataBytes))

    totalRot = 0
    lastDiff1 = 0 # the difference from the last measurement to the current one
    lastDiff2 = 0 # the difference from the measurement before the last one to the last one
    lastDiff3 = 0 # the difference from the measurement before before the last one to the one before the last one

    #           DATA LAYOUT
    #
    # b[0:0] -> MsgType
    # b[1:3] -> Total value
    # b[4:5] -> Difference between 10min ago and 15min ago
    # b[6:7] -> Difference between 5min ago and 10min ago
    # b[8:0] -> Difference between 0min ago and 5min ago
    #
    # If the message is 10 bytes long, it will look like above.
    # If the message is 08 bytes long, the difference between 10 and 15 minutes ago will miss.
    # If the message is 06 bytes long, ...
    # ...
    #

    # there are four valid data lens
    dataLen = len(dataBytes)

    try:
      if 4 <= dataLen <= 10:
        # totalWh is a three byte integer
        totalRot = dataBytes[1] << 16 | dataBytes[2] << 8 | dataBytes[3]

        if dataLen > 4:
          # lastDiff1 is a two byte integer
          lastDiff1 = dataBytes[4] << 8 | dataBytes[5]

          if dataLen > 6:
            # lastDiff2 is a two byte integer
            lastDiff2 = lastDiff1
            lastDiff1 = dataBytes[6] << 8 | dataBytes[7]

            if dataLen > 8:
              # lastDiff3 is a two byte integer
              lastDiff3 = lastDiff2
              lastDiff2 = lastDiff1
              lastDiff1 = dataBytes[8] << 8 | dataBytes[9] 
      else:
        self.log.error("Error invalid application data length: '%d'" % dataLen)
        
        return None
    except IndexError as e:
        self.log.error("Error invalid application data length: '%d'" % dataLen)
        self.log.exception(e)

        return None

    return {
      "rawBytes": "".join(format(x, "02x") for x in dataBytes), 
      "totalRot": totalRot,
      "lastDiff1": lastDiff1,
      "lastDiff2": lastDiff2,
      "lastDiff3": lastDiff3
    }

  def roundsToWh(self, rounds, roundsPkWh) -> int:
    return int(rounds / (roundsPkWh / 1000))

  def _getValueFromDict(self, keyPath : list, currentObj : dict) -> object:
    """ this function gets an object from the config object: config[path[0]][path[1]][path[n]] """
    if len(keyPath) == 0 or not currentObj:
      return currentObj
    elif type(currentObj) == list and type(keyPath[0]) == int:
      return self._getValueFromDict(keyPath[1:], currentObj[keyPath[0]])
    elif type(currentObj) != dict:
      return None
    else:
      return self._getValueFromDict(keyPath[1:], currentObj.get(keyPath[0]))