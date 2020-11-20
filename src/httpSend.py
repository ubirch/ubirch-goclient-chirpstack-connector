import requests
import logging
import time

import config


class HttpSend():
  def __init__(self, timeout : int, attempts : int, retryDelay : int, log : logging.Logger):
    """ the init function of the HTTP class """
    self.timeout = timeout
    self.attempts = attempts
    self.retryDelay = retryDelay
    self.log = log

  def httpSend(self, url : str, headers : dict, data : object) -> (int, str, str):
    """ sends a http request to a given url """
    # set the amount of attempts left
    attemptsLeft = self.attempts

    self.log.info("Sending data to %s" % url)

    # try to send it
    while True:
      try:
        r = requests.post(
          url, headers=headers, data=data, timeout=self.timeout
        )
      except Exception as e:
        self.log.exception(e)
      else:
        # success -> exit the loop
        break

      # decrement the amount of attempts left
      attemptsLeft -= 1

      # check if there are attempts left and delay before retry
      if attemptsLeft > 0:
        self.log.error("Error sending data to %s! Trying again %d more times in %d seconds" % (
          url, attemptsLeft, self.retryDelay
        ))

        time.sleep(self.retryDelay)
      else:
        self.log.error("Finally failed send data to %s!" % url)

        return (-1, None, None)

    # return the status code and reason sent from the HTTP server
    return (r.status_code, r.reason, r.text)