import uuid
import src.uuidgen

def main():
  print("|===== UUID Generator =====|")
  print("Namespace: %s -> %s / %s -> %s" % (src.uuidgen.EON_NAMESPACE_NAME, src.uuidgen.UBIRCH_NAMESPACE_NAME, str(src.uuidgen.EON_NAMESPACE_UUID), str(src.uuidgen.UBIRCH_NAMESPACE_UUID)))
  devEUI = input("DevEUI > ")
  print("UUID: %s" % str(src.uuidgen.getDevUUID(devEUI)))


if __name__ == "__main__":
  main()