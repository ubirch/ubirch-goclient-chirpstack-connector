import shutil
import subprocess
import logging
import config
import httpSend
import json
from multiprocessing import Lock

#
# TODO The registrator is currently not working. Do not use it.
#

DEVICE_GET_URL="/devices/%s"  # has to be completed with the device EUI


class DeviceRegistrator:
  def __init__(self, config : config.Config, http : httpSend.HttpSend, log : logging.Logger):
    """ init function of the DeviceRegistrator class """
    self.config = config
    self.goClientConfig = self.config.registratorGoClientConfig
    self.goClientService = self.config.registratorGoClientService
    self.registrationURL = self.config.registratorRegistrationURL
    self.uBirchToken = self.config.registratorRegistrationURL
    self.chirpstackApiURL = self.config.registratorChirpstackApiURL
    self.chirpstackApiToken = self.config.registratorChirpstackApiToken
    self.http = http
    self.log = log
    self.lock = Lock()

  def registerDevice(self, devEUI : str):
    """ controls the device registration process """
    self.log.info("Starting the registration process for a new device with the EUI '%s'" % devEUI)

    # get some device information from chirpstack (description-payload)
    devDescr = self.getDeviceDescr(devEUI)

    if devDescr == None:
      self.log.error("Error getting device information from Chirpstack!")

      return

    self.log.info("Configuration of the new device: EUI=%s; UUID=%s; CR=%d; ID=%s" %
      (devEUI, devDescr["uuid"], devDescr["cr"], devDescr["id"])
    )

    # register the device and get the AuthToken
    authToken = self.registerAtBackend(devEUI, devDescr)

    if authToken == None:
      self.log.error("Failed to register the new device ('%s'/'%s') at the uBirch backend!" % (devEUI, devDescr["uuid"]))

      return

    # modify the configuration files
    if self.modifyConfigs(devEUI, authToken, devDescr) == False:
      self.log.error("Failed to update the configuration files for the new device ('%s'/'%s')!" % (devEUI, devDescr["uuid"]))

      return

    return

  def getDeviceDescr(self, devEUI : str) -> dict:
    """ gets the device description from chirpstack """
    
    # request information from chirpstack
    statusCode, reason, text = self.http.httpSend(self.chirpstackApiURL + DEVICE_GET_URL % devEUI, {
      "Grpc-Metadata-Authorization": "Bearer " + self.chirpstackApiToken
    }, None, operation="get", verify=False)

    if statusCode != 200:
      self.log.error("HTTP request to the Chirpstack API failed! Code: '%d', Status: '%s', Message: '%s'" % 
        (statusCode, reason, text)
      )

      return None
    
    # try to extract the device description
    try:
      textDict = json.loads(text)
      descr = textDict["device"]["description"]
    except Exception as e:
      self.log.error("Error parsing device information from Chirpstack! Data: '%s'" % text)
      self.log.exception(e)

      return None

    # try to convert the string into a dict
    try:
      descrDict = json.loads(descr)
    except Exception as e:
      self.log.error("Error the Chirpstack device dscription (Inavlid Json)! Data: '%s'" % descrDict)
      self.log.exception(e)

      return None

    return descrDict

  def registerAtBackend(self, devEUI : str, devDescr : dict) -> str:
    """ performs the actual device registration at the uBirch backend """
    return "abc"

  def modifyConfigs(self, devEUI : str, devUbToken : str, devDescr : dict) -> bool:
    """ modifies the configurations files of the UGCC and the GoClient """
    # modify the ugcc configuration
    if self._modifyUgccConfig(devEUI, devUbToken, devDescr) == False:
      return False

    # modify the go-client configuration
    if self._modifyGoClientConfig(devDescr["uuid"], devUbToken) == False:
      self.log.error("Reverting UGCC configuration changes!")

      # the ugcc configuration has to be reverted so that it is synced to the go-client config
      if self.config.revert() == False:
        self.log.error("Failed to revert the UGCC configuration!")

      return False

    # restart the go-client
    self._restartGoClient()      

    return True

  def _modifyUgccConfig(self, devEUI : str, devUbToken : str, devDescr : dict) -> bool:
    """ modifies the ugcc configuration """
    self.log.debug("Adding the new device to the UGCC configuration ...")

    try:
      # update the in-memory configuration
      self.config.config["devices"].append({
        "deviceEUI": devEUI,
        "deviceUUID": devDescr["uuid"],
        "roundsPkW": devDescr["cr"],
        "deviceID": devDescr["id"]
      })

      self.config.config["ubpass"][devDescr["uuid"]] = devUbToken

      # write configuration changes
      self.config.save()
    except Exception as e:
      self.log.error("Error adding a new device ('%s'/'%s') to the UGCC configuration!" % (devEUI, devDescr["uuid"]))
      self.log.exception(e)

      return False

    return True

  def _modifyGoClientConfig(self, devUUID : str, devUbToken : str) -> bool:
    self.log.debug("Adding the new device to the Go-Client configuration ...")

    try:
      # make a backup of the original goclient configuration file
      shutil.copyfile(self.config.registratorGoClientConfig, self.config.registratorGoClientConfig + ".backup")

      with open(self.config.registratorGoClientConfig, "r+") as fd:
        # load the config as dict
        cfgJ = json.load(fd)

        cfgJ["devices"][devUUID] = devUbToken

        # jump back to the beginning of the file and delete its contents
        fd.seek(0)
        fd.truncate()

        # write the config 
        json.dump(cfgJ, fd, indent=2)
    except Exception as e:
      self.log.error("Error modifying the Go-Client configuration file! (%s)" % self.config.registratorGoClientConfig)
      self.log.exception(e)

      return False

    return True

  def _restartGoClient(self) -> bool:
    """ restarts the GoClient so that the config changes will come into effect """
    self.log.debug("Trying to restart the Go-Client ('%s') ..." % self.goClientService)

    # restart the service; output will be ignored
    p = subprocess.Popen(["systemctl", "restart", self.goClientService], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

    if p.returncode != 0:
      self.log.error("Error restarting the Go-Client! Return Code = '%d'" % p.returncode)

      return False

    return True