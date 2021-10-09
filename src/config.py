import os
import json
import shutil
import logging
from typing import Callable


class Config():
  def __init__(self, configFile: str, log: logging.Logger):
    """ init function of the Config class """
    # set default values (None means that is has to be set)
    self.configFile = configFile
    self.log = log
    self.config: dict = None
    self.configFD = None
    self.backupPath = self.configFile + ".backup"
    self.logLevel: int = 10
    self.logFile: str = "/dev/stdout"
    self.logFormat: str = "[%(asctime)s]--[%(levelname)-8s]  %(message)s"
    self.logMaxBytes: int = 2e7
    self.logBackupCount: int = 10
    self.devices: list = []
    self.ubPass: dict = None
    self.httpTimeout: int = 5
    self.httpAttempts: int = 3
    self.httpRetryDelay: int = 3
    self.mqttUser: str = None
    self.mqttPass: str = None
    self.mqttHost: str = "localhost"
    self.mqttPort: int = 1883
    self.goClientUrl: str = None
    self.dataClientUrl: str = None
    self.dataClientPass: str = None

  def readCfg(self) -> bool:
    """Read the configuration"""
    # try to open the config file
    self.log.debug("Trying to open config file '%s' ..." % self.configFile)

    try:
      self.configFD = open(self.configFile, "r")
    except Exception as e:
      self.log.error("Error opening config file '%s'!" % self.configFile)
      self.log.exception(e)

      return False

    # try to parse the config file
    self.log.debug("Trying to parse the config file '%s' ..." % self.configFile)

    try:
      self.config = json.loads(self.configFD.read())
    except Exception as e:
      self.log.error("Error pasing the config file '%s'!" % self.configFile)
      self.log.exception(e)

      return False

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
      self.logMaxBytes = self._getValueConfigOrEnv(["log", "maxBytes"], "UGCC_LOG_MAX_BYTES", self.logMaxBytes)
      self.log.debug("logMaxBytes => %d" % self.logMaxBytes)
      self.logBackupCount = self._getValueConfigOrEnv(["log", "backupCount"], "UGCC_LOG_BACKUP_COUNT", self.logBackupCount)
      self.log.debug("logBackupCount => %d" % self.logBackupCount)
      self.devices = self._getValueConfigOrEnv(["devices"], "UGCC_DEVICES", default=self.devices, convertFunc=json.loads)
      self.log.debug("devices => %s" % self.devices)
      self.ubPass = self._getValueConfigOrEnv(["ubpass"], "UGCC_UBPASS", default=self.ubPass, convertFunc=json.loads)
      self.log.debug("ubpass => len = %d" % len(self.ubPass))
      self.httpTimeout = self._getValueConfigOrEnv(["http", "timeout"], "UGCC_HTTP_TIMEOUT", default=self.httpTimeout, convertFunc=int)
      self.log.debug("httpTimeout => %d" % self.httpTimeout)
      self.httpAttempts = self._getValueConfigOrEnv(["http", "attempts"], "UGCC_HTTP_ATTEMPTS", default=self.httpAttempts, convertFunc=int)
      self.log.debug("httpAttempts => %d" % self.httpAttempts)
      self.httpRetryDelay = self._getValueConfigOrEnv(["http", "retryDelay"], "UGCC_HTTP_RETRY_DELAY", default=self.httpRetryDelay, convertFunc=int)
      self.log.debug("httpRetryDelay => %d" % self.httpRetryDelay)
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
      self.dataClientUrl = self._getValueConfigOrEnv(["dataClient", "url"], "UGCC_DATACLIENT_URL", default=self.dataClientUrl)
      self.log.debug("dataClientUrl => %s" % self.dataClientUrl)
      self.dataClientPass = self._getValueConfigOrEnv(["dataClient", "pass"], "UGCC_DATACLIENT_PASS", default=self.dataClientPass)
      self.log.debug("dataClientPass => len = %d" % len(self.dataClientPass))
    except:
      return False

    # got trough
    return True

  def save(self) -> bool:
    """ writes self.config back to the configuration file (creates a backup first) """
    self.log.info("Saving the current configuration to '%s' (placing backed up at: '%s')" %
      (self.configFile, self.backupPath)
    )

    # create the backup
    shutil.copyfile(self.configFile, self.backupPath)

    # write the current config
    with open(self.configFile, 'w') as fd:
      json.dump(self.config, fd, indent=2)

    return True

  def revert(self) -> bool:
    """ loads the backup and overwrites the current coniguration """
    if os.path.exists(self.backupPath):
      # overwrite the current config with the backup
      shutil.copyfile(self.backupPath, self.configFile)

      # re-read the configuration
      if self.readCfg() == False:
        self.log.error("Error reading the restored configuration! (%s)" % self.configFile)

      return True
    else:
      self.log.error("Cannot revert to backup configuration! (File '%s' not found)" % self.backupPath)

      return False

  def _getValueConfigOrEnv(self, keyPath: list, envName: str, default: object = None, convertFunc: Callable[[object], object] = None) -> object:
    """ get a config value from the config file or environment """
    # try to get the value from the config file
    val = self._getValueFromDict(keyPath, self.config)

    # if it is not in the config file, try env (or set the default)
    if val == None:
      val = os.getenv(envName, default)

      # check if this value should be converted before returning
      # this should only be applied to env-loaded values, since config-file-loaded values should already have the correct type
      if val and callable(convertFunc):
        try:
          val = convertFunc(val)
        except Exception as e:
          self.log.error("Error type-converting env-loaded value '%s' = '%s' with function '%s'" % (envName, val, convertFunc.__name__))
          self.log.exception(e)

          raise(Exception())

    # check if the value is still undefined
    if val == None:
      valName = "config"

      for namePart in keyPath:
        valName += "." + namePart

      self.log.error("Error value '%s'/'%s' couldn't be loaded from the config file or env and no default was set!" % (valName, envName))

      raise(Exception())

    return val

  def _getValueFromDict(self, keyPath: list, currentObj: dict) -> object:
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
