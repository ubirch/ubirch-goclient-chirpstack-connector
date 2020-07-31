import os
import sys
import json
import logging
from typing import Callable


class Config():
  """ init function of the Config class """
  def __init__(self, configFile : str, log : logging.Logger):
    self.configFile = configFile
    self.log = log
    self.config : dict = None
    self.configFD = None

    # used to signalise init success/failure to the caller
    self.initSuccess = False

    # set default values
    self.logLevel : int = 10
    self.logFile : str = "/dev/stdout"
    self.logFormat : str = "[%(asctime)s]--[%(levelname)-8s]  %(message)s"
    self.devices : list = []
    self.ubPass : dict = None
    self.mqttUser : str = None
    self.mqttPass : str = None
    self.mqttHost : str = "localhost"
    self.mqttPort : int = 1883
    self.goClientUrl : str = None
    self.realToUrl : str = None
    self.realToSubKey : str = None
    self.fludiaUrl : str = None
    self.fludiaUser : str = None
    self.fludiaPass : str = None

    # try to open the config file
    self.log.debug("Trying to open config file '%s' ..." % self.configFile)

    try:
      self.configFD = open(self.configFile, "r")
    except Exception as e:
      self.log.error("Error opening config file '%s'!" % self.configFile)
      self.log.exception(e)

      return

    # try to parse the config file
    self.log.debug("Trying to parse the config file '%s' ..." % self.configFile)

    try:
      self.config = json.loads(self.configFD.read())
    except Exception as e:
      self.log.error("Error pasing the config file '%s'!" % self.configFile)
      self.log.exception(e)

      return

    # close the fd
    self.configFD.close()

    # get values from the loaded config
    try:
      self.logLevel = self._getValueConfigOrEnv(["log", "level"], "UGCC_LOG_LEVEL", default=self.logLevel, convertFunc=int)
      self.log.debug("logLevel => %d" % self.logLevel)
      self.logFile = self._getValueConfigOrEnv(["log", "file"], "UGCC_LOG_FILE", default=self.logFile)
      self.log.debug("logFile => %s" % self.logFile)
      self.logFormat = self._getValueConfigOrEnv(["log", "format"], "UGCC_LOG_FORMAT", self.logFormat)
      self.log.debug("logFormat => %s" % self.logFormat)
      self.devices = self._getValueConfigOrEnv(["devices"], "UGCC_DEVICES", default=self.devices, convertFunc=json.loads)
      self.log.debug("devices => %s" % self.devices)
      self.ubPass = self._getValueConfigOrEnv(["ubpass"], "UGCC_UBPASS", default=self.ubPass, convertFunc=json.loads)
      self.log.debug("ubpass => len = %d" % len(self.ubPass))
      self.mqttUser = self._getValueConfigOrEnv(["mqtt", "user"], "UGCC_MQTT_USER", default=self.mqttUser)
      self.log.debug("mqttUser => %s" % self.mqttUser)
      self.mqttPass = self._getValueConfigOrEnv(["mqtt", "pass"], "UGCC_MQTT_PASS", default=self.mqttPass)
      self.log.debug("mqttPass => len = %d" % len(self.mqttPass))
      self.mqttHost = self._getValueConfigOrEnv(["mqtt", "host"], "UGCC_MQTT_HOST", default=self.mqttHost)
      self.log.debug("mqttHost => %s" % self.mqttHost)
      self.mqttPort = self._getValueConfigOrEnv(["mqtt", "port"], "UGCC_MQTT_PORT", default=self.mqttPort, convertFunc=int)
      self.log.debug("mqttPort => %d" % self.mqttPort)
      self.goClientUrl = self._getValueConfigOrEnv(["goClient", "url"], "UGCC_GOCLIENT_URL", default=self.goClientUrl)
      self.log.debug("goClientUrl => %s" % self.goClientUrl)
      self.realToUrl = self._getValueConfigOrEnv(["realto", "url"], "UGCC_REALTO_URL", default=self.realToUrl)
      self.log.debug("realToUrl => %s" % self.realToUrl)
      self.realToSubKey = self._getValueConfigOrEnv(["realto", "subKey"], "UGCC_REALTO_SUBKEY", default=self.realToSubKey)
      self.log.debug("realToSubKey => len = %d" % len(self.realToSubKey))
      self.fludiaUrl = self._getValueConfigOrEnv(["fludia", "url"], "UGCC_FLUDIA_URL", default=self.fludiaUrl)
      self.log.debug("fludiaUrl => %s" % self.fludiaUrl)
      self.fludiaUser = self._getValueConfigOrEnv(["fludia", "user"], "UGCC_FLUDIA_USER", default=self.fludiaUser)
      self.log.debug("fludiaUser => %s" % self.fludiaUser)
      self.fludiaPass = self._getValueConfigOrEnv(["fludia", "pass"], "UGCC_FLUDIA_PASS", default=self.fludiaPass)
      self.log.debug("fludiaPass => %s" % self.fludiaPass)
      
    except:
      return

    # got trough
    self.initSuccess = True

  def _getValueConfigOrEnv(self, keyPath : list, envName : str, default : object = None, convertFunc : Callable[[object], object] = None) -> object:
    """ get a config value from the config file or environment """
    # try to get the value from the config file
    val = self._getValueFromDict(keyPath, self.config)

    # if it is not in the config file, try env (or set the default)
    if not val:
      val = os.getenv(envName, default)

      # check if this value should be converted before returning
      # this should only be applied to env-loaded values, since config-file-loaded values should already have the correct type
      if val and callable(convertFunc):
        try:
          val = convertFunc(val)
        except Exception as e:
          self.log.error("Error type-converting env-loaded value '%s' = '%s' with function '%s'" % (envName, val, convertFunc.__name__))
          self.log.exception(e)

          raise()

    # check if the value is still undefined
    if not val:
      valName = "config"

      for namePart in keyPath:
        valName += "." + namePart

      self.log.error("Error value '%s'/'%s' couldn't be loaded from the config file or env and no default was set!" % (valName, envName))

      raise()

    return val

  def _getValueFromDict(self, keyPath : list, currentObj : dict) -> object:
    """ this function gets an object from the config object: config[path[0]][path[1]][path[n]] """
    if len(keyPath) == 0 or not currentObj:
      return currentObj
    elif type(currentObj) == list and type(keyPath[0]) == int:
      return self._getValueFromDict(keyPath[1:], currentObj[keyPath[0]])
    elif type(currentObj) != dict:
      return None
    else:
      return self._getValueFromDict(keyPath[1:], currentObj.get(keyPath[0]))

  def getConfig(self) -> dict:
    """ function to get the config object """
    return self.config
