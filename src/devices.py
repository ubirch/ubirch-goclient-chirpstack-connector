import os
import logging

import config


class Device():
  def __init__(self, eui : str, uuid : str, passwd : str, deviceID : str):
    """ init function of the device class """
    self.eui = eui
    self.uuid = uuid
    self.passwd = passwd
    self.id = deviceID

    return


class Devices():
  def __init__(self, config : config.Config, log : logging.Logger):
    """ init function of the devices class """
    self.devices : [Device] = []
    self.config = config
    self.log = log

    # start the device initialisation
    self.initialiseDevices()

  def initialiseDevices(self):
    # initialise the single devices
    for rawDevice in self.config.devices:
      # get the matching password for the device
      ubPass = self.config.ubPass.get(rawDevice.get("deviceUUID"))

      # check if a password was found
      if not ubPass:
        self.log.warning("No password for device with UUID '%s', EUI '%s' and ID '%s' found!" %
          (rawDevice.get("deviceUUID"), rawDevice.get("deviceEUI"), rawDevice.get("deviceID"))
        )

      # check if the device is already known
      devices = list(filter(lambda x: x.eui == rawDevice.get("deviceEUI"), self.devices))
      if len(devices) != 0:
        self.log.debug("Updating a device with EUI '%s' ..." % rawDevice.get("deviceEUI"))

        # there can only be one device with the EUI; index 0 can be assumed
        devices[0].uuid = rawDevice.get("deviceUUID")
        devices[0].passwd = ubPass
        devices[0].id = rawDevice.get("deviceID")
      else:
        self.log.debug("Adding a new device with EUI='%s' ..." % rawDevice.get("deviceEUI"))

        self.devices.append(Device(
          rawDevice.get("deviceEUI"),
          rawDevice.get("deviceUUID"),
          ubPass,
          rawDevice.get("deviceID")
        ))

  def getDeviceByEUI(self, eui : str) -> Device:
    """ this function gets a device from self.devices by its eui """
    for device in self.devices:
      if device.eui.lower() == eui.lower():
        return device

    return None

  def getDeviceByUUID(self, uuid : str) -> Device:
    """ this function gets a device from self.devices by its uuid """
    for device in self.devices:
      if device.uuid.lower() == uuid.lower():
        return device

    return None

  def getDevlistLen(self) -> int:
    return len(self.devices)
