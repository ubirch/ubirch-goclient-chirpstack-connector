import os
import logging

import config


class Device():
  def __init__(self, eui : str, uuid : str, passwd : str, roundsPkW : int, deviceID : str):
    """ init function of the device class """
    self.eui = eui
    self.uuid = uuid
    self.passwd = passwd
    self.roundsPkW = roundsPkW
    self.id = deviceID

    return


class Devices():
  def __init__(self, config : config.Config, log : logging.Logger):
    """ init function of the devices class """
    self.devices : [Device] = []
    self.config = config
    self.log = log

    # initialise the single devices
    for rawDevice in config.devices:
      # get the matching password for the device
      ubPass = self.config.ubPass.get(rawDevice.get("deviceUUID"))

      # check if a password was found
      if not ubPass:
        self.log.warning("No password for device with UUID '%s', EUI '%s' and ID '%s' found!" %
          (rawDevice.get("deviceUUID"), rawDevice.get("deviceEUI"), rawDevice.get("deviceID"))
        )

      self.devices.append(Device(
        rawDevice.get("deviceEUI"),
        rawDevice.get("deviceUUID"),
        ubPass,
        rawDevice.get("roundsPkW"),
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
