import logging
import requests
import json

import devices
import httpSend


class GoClientConnector():
  def __init__(self, url: str, http: httpSend.HttpSend, log: logging.Logger):
    """ init function of the GoClientConnector function """
    self.url = url
    self.http = http
    self.log = log

    self.log.info("The go-client URL is '%s'" % self.url)

  def sendData(self, data: str, device: devices.Device):
    """ this function sends measurements to the go client """
    if not device.passwd:
      self.log.error("No password configured for the device with the UUID '%s'" % device.uuid)

      return

    # remove all fields that shouldn't be hashed
    oldDict = json.loads(str)
    newDict = {
      "device_properties": {
        "devuuid": oldDict["device_properties"]["devuuid"]
      },
      "payload_cleartext": oldDict["payload_cleartext"],
      "timestamp": oldDict["timestamp"]
    }

    dataStr = json.dumps(newDict, sort_keys=True, indent=None, separators=(",", ":"))

    self.log.info("Sending data to the GoClient: %s" % dataStr)

    status, reason, text = self.http.httpSend(
      self.url + device.uuid, 
      {"X-Auth-Token": device.passwd, "Content-Type": "application/json"},
      dataStr
    )

    # check for success
    if status == requests.codes.OK:
      self.log.info("Successfully sent the measurement to the Go-Client")
    else:
      if status == -1:
        self.log.error("Error sending the measurement to the Go-Client")
      else:
        self.log.error("Error sending the measurement to the Go-Client (%d/%s): %s" % (status, reason, text))

    return
