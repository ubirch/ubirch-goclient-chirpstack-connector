import uuid

EON_NAMESPACE_NAME = "eon.uuid.trustservice"
EON_NAMESPACE_UUID = uuid.uuid5(uuid.UUID("00000000-0000-0000-0000-000000000000"), EON_NAMESPACE_NAME)
UBIRCH_NAMESPACE_NAME = "ubirch"
UBIRCH_NAMESPACE_UUID = uuid.uuid5(EON_NAMESPACE_UUID, UBIRCH_NAMESPACE_NAME)


def getDevUUID(devEUI : str) -> uuid.UUID:
  return uuid.uuid5(UBIRCH_NAMESPACE_UUID, devEUI)

def main():
  print("|===== UUID Generator =====|")
  print("Namespace: %s -> %s / %s -> %s" % (EON_NAMESPACE_NAME, UBIRCH_NAMESPACE_NAME, str(EON_NAMESPACE_UUID), str(UBIRCH_NAMESPACE_UUID)))
  devEUI = input("DevEUI > ")
  print("UUID: %s" % str(getDevUUID(devEUI)))


if __name__ == "__main__":
  main()