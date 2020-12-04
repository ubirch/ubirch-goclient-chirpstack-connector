import logging
import requests
import json

import devices
import httpSend


class GoClientConnector():
  def __init__(self, url : str, devices : devices.Devices, http : httpSend.HttpSend, log : logging.Logger):
    """ init function of the GoClientConnector function """
    self.url = url
    self.devices = devices
    self.http = http
    self.log = log

    self.log.info("The go-client URL is '%s'" % self.url)

  def sendData(self, data : str, device : devices.Device):
    """ this function sends measurements to the go client """
    if not device.passwd:
      self.log.error("No password configured for the device with the UUID '%s'" % device.uuid)

      return

    status, reason, text = self.http.httpSend(
      self.url + device.uuid, 
      {"X-Auth-Token": device.passwd, "Content-Type": "application/json"},
      data
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
