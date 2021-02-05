# Automatic device registration
THE AUTOMATIC DEVICE REGISTRATOR IS CURRENTLY NOT WORKING. DO NOT USE IT.
The automatic device registration works by putting some extra information into the description field when registering the device at Chirpstack which enables the UGCC to use that extra information to register the device at the uBirch backend and modify its own configuration file and the one of the GoClient. The registration at Chirpstack can either be done using the WebInterace or by using the Chirpstack Api Tool as shown [below](#registering-the-device-at-chirpstack---chirpstack-api-tool). The UGCC will become aware of the new device as soon as the first measurement arrives. A couple moments after you should be able to see it in the uBirch console, there you should also see the public key for the device which was registered by the GoClient.
## Description Format
* The contents of the description field (Chirpstack) will have to be of the following structure:
```
{
  "eui": "xxxxxxxxxxxxxxxx",
  "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "cr": 75,
  "id": "someID"
}
```
wheere the fields of the following meanings:
```
eui

  The EUI of the device

uuid

  The UUID that should be assigned to the device. It should be derived from the EUI using the uuidGenerator.py

cr

  The conversion ration between counting wheel rotations and energy usage

id

  The ID to be assigned to the device
```
## Registering the device at Chirpstack - Chirpstack-Api-Tool
* First of all, read the README of the Chirpstack Api Tool.
* Below is a example of the device registration process
  * The example assumes that the application the device shall be registered to already exists
  * It does not contain the complete output of each command but only the relevant parts
```sh
# The operation to add a device is 'put_device'
# Run the help command for it to get an overview of the required parameters
> python3.8 src/chirpstackApiTool.py help put_device

Usage: python3.8 src/chirpstackApiTool.py --config config.json put_device applicationID devName devDescr devEUI devProfileID

   applicationID   The application to which the device should belong
   devName         A name for the device
   devDescr        A description for the device
   devEUI          The EUI of the device
   devProfileID    The profile to be used for the device

# The applicationID as well as the devProfileID have to be obtained from chirpstack
# This can be archieved using the get_applications and get_device-profiles operations
# Both of these need a limit parameter, specifying how many entries are to be returned at most
> python3.8 src/chirpstackApiTool.py --config config.json get_applications 10

{'id': '2', 'name': 'testApp', 'description': 'testApp', 'organizationID': '2', 'serviceProfileID': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'serviceProfileName': 'Default Service Profile'}

> python3.8 src/chirpstackApiTool.py --config config.json get_device-profiles 10

{'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', 'name': 'TestDeviceProfile', 'organizationID': '2', 'networkServerID': '1', 'createdAt': '2000-00-20T11:11:11.111111Z', 'updatedAt': '2000-00-20T11:11:11.111112', 'networkServerName': 'TestNetworkServer'}

# Both needed IDs are now kown and can be used to register the device
# The format of the description is described above
> python3.8 src/chirpstackApiTool.py --config config.json put_device 2 TestDevice '{"eui": "xxxxxxxxxxxxxxxx", "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "cr": 75, "id": "someID"}' xxxxxxxxxxxxxxxx xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```
* The last command should give you a 200 response
* If your device has fixed application keys into it you will have to set these so that Chirpstack uses them
```
> python3.8 src/chirpstackApiTool.py help put_device_keys

Usage: python3.8 src/chirpstackApiTool.py put_device_keys devEUI appKey nwkKey genAppKey

   devEUI      The EUI of the device
   appKey      Application key
   nwkKey      Network key
   genAppKey   ---

# You can just set all three values to your application key and it should work
# The key should be a 32 byte hex string representing 16 bytes
```
* Whether a device has been activated or not can be checked using the `get_activation_status` operation
```
> python3.8 src/chirpstackApiTool.py help get_activation_status

Usage: python3.8 src/chirpstackApiTool.py get_activation_status deviceEUI

   deviceEUI   The EUI (hex) of the device to get the activation status from

Note that the return code 404 means that there is no activation information for the device.
If you are sure that the device exists, you can conclude that the device is not activated.
```