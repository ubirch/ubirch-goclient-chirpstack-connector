import logging
import requests
import json
import time

import devices
import httpSend


class GoClientConnector():
  def __init__(self, url: str, http: httpSend.HttpSend, log: logging.Logger, attempts : int = 3, retryDelay : int = 10):
    """ init function of the GoClientConnector function """
    self.url = url
    self.http = http
    self.log = log
    self.attempts = attempts
    self.retryDelay = retryDelay

    self.log.info("The go-client URL is '%s'" % self.url)

  def sendData(self, data: str, device: devices.Device):
    """ this function sends measurements to the go client """
    if not device.passwd:
      self.log.error("No password configured for the device with the UUID '%s'" % device.uuid)

      return

    # remove all fields that shouldn't be hashed
    oldDict = json.loads(data)
    newDict = {
      "device_properties": {
        "devuuid": oldDict["device_properties"]["devuuid"]
      },
      "payload_cleartext": oldDict["payload_cleartext"],
      "timestamp": oldDict["timestamp"]
    }

    dataStr = json.dumps(newDict, sort_keys=True, indent=None, separators=(",", ":"))

    self.log.info("Sending data to the GoClient: %s" % dataStr)

    
    #
    # the GoClient may fail to send UPPs because of a bad connection and then return internal server errors (500)
    # the http sender wont retry since technically the request has been sent; however this can lead to the data
    # api getting data for which no anchored UPP exists, which is a problem
    # therefore on internal server errors there will be retries according to the http retry settings
    #
    
    # set the amount of attempts left
    attemptsLeft = self.attempts

    while attemptsLeft > 0:
      # send it
      status, reason, text = self.http.httpSend(
        self.url + device.uuid, 
        {"X-Auth-Token": device.passwd, "Content-Type": "application/json"},
        dataStr
      )

      # decrease the number of attempts left
      attemptsLeft -= 1

      # check for success
      if status == requests.codes.OK:
        self.log.info("Successfully sent the measurement to the Go-Client")

        break
      else:
        if status == -1:
          self.log.error("Error sending the measurement to the Go-Client")

          break
        elif status == 500:
          self.log.error("Error sending the measurement to the Go-Client - 500 (trying again %d times)" % attemptsLeft)

          # sleep for the delay
          time.sleep(self.retryDelay)

          continue
        else:
          self.log.error("Error sending the measurement to the Go-Client (%d/%s): %s" % (status, reason, text))

          break

    return
