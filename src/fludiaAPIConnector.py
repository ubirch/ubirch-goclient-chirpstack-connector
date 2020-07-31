import logging
import requests
import json
import base64

import devices


class FludiaAPIConnector():
  def __init__(self, url : str, user : str, flpass : str, devices : devices.Devices, log : logging.Logger):
    """ init function of the FludiaAPIConnector class """
    self.url = url
    self.user = user
    self.flpass = flpass
    self.devices = devices
    self.log = log

    # get the authentication value
    self.b64pass = base64.encodebytes(
      bytes(self.user + ":" + self.flpass, "utf-8")
    ).decode("utf-8").rstrip("\n")

    # create the login header
    self.header = {
      "Authorization": "Basic " + self.b64pass
    }

    self.log.info("The fludia API URL is '%s'" % self.url)

  def sendData(self, data : dict):
    """ this function sends measurements to the fludia api """

    # send the measurement
    self.log.info("Sending a measurement to %s" % self.url)

    r = requests.post(
      self.url,
      headers=self.header,
      data=json.dumps(data),
      verify=True
    )

    # check for success
    if r.status_code == requests.codes.OK:
      self.log.debug("Successfully sent the measurement to the Fludia API")
    else:
      self.log.error("Error sending the measurement to the Fludia API (%d/%s)" % (r.status_code, r.reason))

    return
