import uuid

EON_NAMESPACE_NAME = "eon.uuid.trustservice"
EON_NAMESPACE_UUID = uuid.uuid5(uuid.UUID("00000000-0000-0000-0000-000000000000"), EON_NAMESPACE_NAME)
UBIRCH_NAMESPACE_NAME = "ubirch"
UBIRCH_NAMESPACE_UUID = uuid.uuid5(EON_NAMESPACE_UUID, UBIRCH_NAMESPACE_NAME)


def getDevUUID(devEUI : str, autoLower : bool = True) -> uuid.UUID:
  return uuid.uuid5(UBIRCH_NAMESPACE_UUID, devEUI if autoLower == False else devEUI.lower())
