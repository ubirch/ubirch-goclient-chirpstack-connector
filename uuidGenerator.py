"""
Generate a UUID v5, based on a Namespace and the input string, which should be the devEUI.
This script can be used to get the UUID of your device, which will be used at the ubirch backend.
"""

import uuid
import src.uuidgen

def main():
  print("|===== UUID Generator =====|")
  print("Namespace: %s -> %s / %s -> %s" % (src.uuidgen.NAMESPACE_NAME, src.uuidgen.UBIRCH_NAMESPACE_NAME, str(src.uuidgen.NAMESPACE_UUID), str(src.uuidgen.UBIRCH_NAMESPACE_UUID)))
  devEUI = input("DevEUI (will be auto-lowercased) > ")
  print("UUID: %s" % str(src.uuidgen.getDevUUID(devEUI, autoLower=True)))


if __name__ == "__main__":
  main()