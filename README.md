# Rituals Genie plugin for Domoticz

[Domoticz](https://www.domoticz.com) is free and open-source Home Automation system.

[Rituals](https://rituals.com) is a dutch company which has many fragrances and perfumes.

Plugin enables to control Rituals Genie from Domoticz via network. 

Currently, the following functions are implemented:

- Supports multiple devices, for those who have more than one Genie
- On / Off
- Set Perfume Amount
- Set Room Size
- Show Perfume
- Show Fill percentage

Supported Domoticz versions:

- Domoticz 2021.x
- Domoticz 2022.2

Supported Genie versions:
- Genie 1.0 (not tested)
- Genie 2.0

### Installation

- Connect to Domoticz via ssh 
- Go to Domoticz plugin folder: `cd domoticz/plugins`
- Download plugin: 
`git clone https://github.com/smitec11/Domoticz-Genie-Plugin`
- Restart Domoticz

### Configuration

From Domoticz web UI, go to _Setup -> Hardware_ and select _Rituals Genie_Plugin from drop-down menu.

Configure plugin:

- _Name_ - name of Genie hardware device in Domoticz (i.e. Genie)
- _EmailAddress_ - email address for rituals account
- _Password_ - password for rituals account
- click _Add_ button

###![image](https://user-images.githubusercontent.com/51033177/156994675-d5a94703-c397-42c7-8075-9dd1818e5866.png)

Plugin will create 5 devices per genie and shows them in related device tabs (Switches, Utilities):

- On/Off (Switch device)
- Amount (Selector Switch device)
- Room Size (Selector Switch device)
- Perfume (Text device)
- Fill (Text device)

##![image](https://user-images.githubusercontent.com/51033177/156995214-520f192f-b294-46e6-9bd5-108491ce26e6.png)


### Thanks to
this plugin is based on code of 
- Milan Meulemans
- Rolf Koenders

