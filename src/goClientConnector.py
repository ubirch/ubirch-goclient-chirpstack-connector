import logging
import requests
import json

import devices


class GoClientConnector():
  def __init__(self, url : str, devices : devices.Devices, log : logging.Logger):
    """ init function of the GoClientConnector function """
    self.url = url
    self.devices = devices
    self.log = log

    self.log.info("The go-client URL is '%s'" % self.url)

  def sendData(self, data : dict):
    """ this function sends measurements to the go client """
    eui = data.get("device_properties").get("deveui")

    # get the device
    device = self.devices.getDeviceByEUI(eui)
    
    if not device:
      self.log.error("No device found for EUI '%s'" % eui)

      return

    if not device.passwd:
      self.log.error("No password configured for the device with the UUID '%s'" % device.uuid)

      return

    # send the measurement
    self.log.info("Sending a measurement to %s" % (self.url + device.uuid))

    r = requests.post(
      self.url + device.uuid,
      headers={"X-Auth-Token": device.passwd, "Content-Type": "application/json"},
      data=json.dumps(data)
    )

    # check for success
    if r.status_code == requests.codes.OK:
      self.log.debug("Successfully sent the measurement to the go-client")
    else:
      self.log.error("Error sending the measurement to the go-client (%d/%s)" % (r.status_code, r.reason))

    return