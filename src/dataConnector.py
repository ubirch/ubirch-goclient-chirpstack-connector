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
      "X-Auth-Token": self.dpass
    }

    self.log.info("The data API URL is '%s'" % self.url)

  def addHashlist(self, data: str):
    """ add the list of values to hash to the data object """
    dataDict : dict = json.loads(data)
    hashLink = []

    # add all keys from data to hashLink
    for o in dataDict:
      hashLink.append(o)

    # add hashLink to data
    dataDict.update({
      "hashLink": hashLink
    })

    return dataDict

  def sendData(self, data: str, device: devices.Device):
    """ this function sends measurements to the example api """
    datawhashlist = self.addHashlist(data)

    self.log.info("Added hashLink to data: %s" % str(datawhashlist))

    status, reason, text = self.http.httpSend(self.url + device.uuid, self.headers, datawhashlist)

    # check for success (201 is required to be accepted as success)
    if status == requests.codes.OK or status == 201:
      self.log.info("Successfully sent the measurement to the data API")
    else:
      if status == -1:
        self.log.error("Error sending the measurement to the data API")
      else:
        self.log.error("Error sending the measurement to the data API (%d/%s): %s" % (status, reason, text))

    return
