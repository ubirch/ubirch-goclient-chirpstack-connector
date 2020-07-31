import uuid

NAMESPACE_NAME = "eon-community"
NAMESPACE_UUID = uuid.uuid5(uuid.UUID("00000000-0000-0000-0000-000000000000"), NAMESPACE_NAME)

print("|===== UUID Generator =====|")
print("Namespace: %s/%s" % (NAMESPACE_NAME, str(NAMESPACE_UUID)))
devEUI = input("DevEUI > ")
uuid = uuid.uuid5(NAMESPACE_UUID, devEUI)
print("UUID: %s" % str(uuid))
