import logging
import requests

import devices
import httpSend


class ExampleConnector():
  def __init__(self, url : str, epass : str, http : httpSend.HttpSend, log : logging.Logger):
    """ init function of the ExampleConnector class """
    self.url = url
    self.epass = epass
    self.http = http
    self.log = log

    # create the login header
    self.headers = {
      "Content-Type": "application/json",
      "Cache-Control": "no-cache",
      "X-Auth-Token": self.epass
    }

    self.log.info("The example API URL is '%s'" % self.url)

  def sendData(self, data : str, device : devices.Device):
    """ this function sends measurements to the example api """
    status, reason, text = self.http.httpSend(self.url + device.uuid, self.headers, data)

    # check for success (201 is required to be accepted as success)
    if status == requests.codes.OK or status == 201:
      self.log.info("Successfully sent the measurement to the example API")
    else:
      if status == -1:
        self.log.error("Error sending the measurement to the example API")
      else:
        self.log.error("Error sending the measurement to the example API (%d/%s): %s" % (status, reason, text))

    return
