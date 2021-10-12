import logging
import requests
import json

import devices
import httpSend


class DataConnector():
  def __init__(self, url: str, dpass: str, http: httpSend.HttpSend, log: logging.Logger):
    """ init function of the DataConnector class """
    self.url = url
    self.dpass = dpass
    self.http = http
    self.log = log

    # create the login header
    self.headers = {
      "Content-Type": "application/json",
      "Cache-Control": "no-cache",
      "Ocp-Apim-Subscription-Key": self.dpass
    }

    self.log.info("The data API URL is '%s'" % self.url)

  def sendData(self, data: str, device: devices.Device):
    """ this function sends measurements to the example api """
    status, reason, text = self.http.httpSend(self.url + device.uuid, self.headers, data)

    # check for success (201 is required to be accepted as success)
    if status == requests.codes.OK or status == 201:
      self.log.info("Successfully sent the measurement to the data API")
    else:
      if status == -1:
        self.log.error("Error sending the measurement to the data API")
      else:
        self.log.error("Error sending the measurement to the data API (%d/%s): %s" % (status, reason, text))

    return
