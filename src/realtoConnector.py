import logging
import requests
import json
import base64

import httpSend


class RealtoConnector():
  def __init__(self, url : str, rpass : str, http : httpSend.HttpSend, log : logging.Logger):
    """ init function of the realtoConnector class """
    self.url = url
    self.rpass = rpass
    self.http = http
    self.log = log

    # create the login header
    self.headers = {
      "Content-Type": "application/json",
      "Cache-Control": "no-cache",
      "Ocp-Apim-Subscription-Key": self.rpass
    }

    self.log.info("The re.alto API URL is '%s'" % self.url)

  def sendData(self, data : dict):
    """ this function sends measurements to the fludia api """
    status, reason = self.http.httpSend(self.url, self.headers, json.dumps(data))

    # check for success
    if status == requests.codes.OK:
      self.log.debug("Successfully sent the measurement to the re.alto API")
    else:
      if status == -1:
        self.log.error("Error sending the measurement to the re.alto API")
      else:
        self.log.error("Error sending the measurement to the re.alto API (%d/%s)" % (status, reason))

    return
