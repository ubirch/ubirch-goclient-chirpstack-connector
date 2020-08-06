import logging
import requests
import json
import base64

import httpSend


class FludiaAPIConnector():
  def __init__(self, url : str, user : str, flpass : str, http : httpSend.HttpSend, log : logging.Logger):
    """ init function of the FludiaAPIConnector class """
    self.url = url
    self.user = user
    self.flpass = flpass
    self.http = http
    self.log = log

    # get the authentication value
    self.b64pass = base64.encodebytes(
      bytes(self.user + ":" + self.flpass, "utf-8")
    ).decode("utf-8").rstrip("\n")

    # create the login header
    self.headers = {
      "Content-Type": "application/json",
      "Authorization": "Basic " + self.b64pass
    }

    self.log.info("The Fludia API URL is '%s'" % self.url)

  def sendData(self, data : str):
    """ this function sends measurements to the fludia api """
    status, reason = self.http.httpSend(self.url, self.headers, data)

    # check for success
    if status == requests.codes.OK:
      self.log.info("Successfully sent the measurement to the Fludia API")
    else:
      if status == -1:
        self.log.error("Error sending the measurement to the Fludia API")
      else:
        self.log.error("Error sending the measurement to the Fludia API (%d/%s)" % (status, reason))

    return