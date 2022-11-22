"""
<plugin key="RitualsGenie" name="Rituals Genie plugin" author="Chris Smit" version="0.1.0"
    wikilink="https://github.com/smitec/Domoticz-Genie-Plugin" externallink="https://rituals.sense-company.com">
    <description>
       <h2>Rituals Genie Plugin</h2><br/>
       Connects to Rituals Genie Diffuser devices found in network.<br/><br/>
       This plugin has been tested with a Genie 2.0 diffuser.<br/><br/>
       <h3> Configuration</h3><br/>
       Configuration of the plugin is done by providing the following information:
       <ul style="list-style-type:square">
            <li>enter the email address used for the Rituals Account under "Cloud account email address"</li>
            <li>enter the password used for the Rituals Account under "Cloud account password"</li>
       </ul>
    </description>
    <params>
        <param field="Mode1" label="Cloud account Email" width="300px" required="false" default=""/>
        <param field="Mode2" label="Cloud account password" width="200px" required="false" default="" password="true"/>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="True" value="Debug" />
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>        
    </params>    
</plugin>
"""

import Domoticz
from commands import Account, Diffuser

idxtable = dict()

class BasePlugin:
    def __init__(self):
        self.my_account = ()
        self.my_devices = ()
        self.DevName = None

    def onStart(self):
        Domoticz.Debug("onStart called")

        #read out parameters for connection
        self.account_email = Parameters['Mode1']
        self.account_password = Parameters['Mode2']

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()

        self.my_account= Account(self.account_email, self.account_password)       
        self.my_account.authenticate()
        self.my_devices = self.my_account.get_devices()

        devcount=0
        idxtable.clear()
        for diffuser in self.my_devices:
            diffuser.update_data()
            idxtable[devcount] = diffuser.hash
            devcount+=1

        if 'genie' not in Images:
            Domoticz.Image('genie_icons.zip').Create()
            icon_id = Images["genie"].ID
            Domoticz.Log("Icon ID: " + str(icon_id))    

        if (len(Devices) == 0):
            devcount=0
            idxtable.clear()
            for diffuser in self.my_devices:
                diffuser.update_data()
                devname = diffuser.name
                idxtable[devcount] = diffuser.hash

                Domoticz.Device(Name=devname, Unit=(devcount*5)+1, TypeName="Switch", Image=icon_id, Used=1).Create()
                Domoticz.Device(Name=devname + " Perfume", Unit=(devcount*5)+2, Type=243, Subtype=19, Image=icon_id, Used=1).Create()
                Domoticz.Device(Name=devname + " Fill", Unit=(devcount*5)+3, Type=243, Subtype=19, Image=icon_id, Used=1).Create()
                amount_opts = {"LevelActions": "0|10|20|30|40",
                               "LevelNames": "Off|Mild|Medium|Strong",
                               "LevelOffHidden": "true",
                               "SelectorStyle": "0"}
                Domoticz.Device(Name=devname + " Amount", Unit=(devcount*5)+4, TypeName="Selector Switch",
                                Options=amount_opts,
                                Image=icon_id, Used=1).Create()
                roomsize_opts = {"LevelActions": "0|10|20|30|40",
                                 "LevelNames": "Off|15|30|60|100",
                                 "LevelOffHidden": "true",
                                 "SelectorStyle": "0"}
                Domoticz.Device(Name=devname + " Room Size in m2", Unit=(devcount*5)+5, TypeName="Selector Switch",
                                Options=roomsize_opts,
                                Image=icon_id, Used=1).Create()
                devcount +=1
            Domoticz.Debug("Genie Device(s) created.")

        #Set heartbeat for polling interval, do not exceed max, account will than block temporary
        Domoticz.Heartbeat(30)   #seconds
        self._updateDevices()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        DumpHTTPResponseToLog(Data)
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("Genie plugin: onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        # determine index from device
        # 1,2,3,4,5 = idx 0 , 6,7,8,9,10 = idx 1, etc
        # use hash from table to reach correct diffuser
        idx = ((Unit-1) // 5)
        tUnit = Unit - ((int((Unit - 1) / 5)) * 5)

        for diffuser in self.my_devices:
            if (diffuser.hash == idxtable[idx]): # hash matches
                if (tUnit == 1):     # On Off Control
                    if (Command == "On"):
                        diffuser.turn_on()
                    elif (Command == "Off"):
                        diffuser.turn_off()
                elif (tUnit == 4):       # Amount
                    diffuser.set_perfume_amount(int(Level/10))
                elif (tUnit == 5):       # Room Size
                    diffuser.set_room_size(int(Level/10))

                diffuser.update_data()
        self._updateDevices()

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Genie plugin: onNotification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self._updateDevices()

    def _updateDevices(self):
        for diffuser in self.my_devices:
            diffuser.update_data()
            devcount = get_key(diffuser.hash)

            if (diffuser.is_on == True):
                ntemp = 1
                stemp = "On"
            else:
                ntemp = 0
                stemp = "Off"

            if (len(Devices) > 0):
                UpdateDevice(Unit=devcount*5+1, nValue=ntemp, sValue=stemp)
                UpdateDevice(devcount*5+2, 0, diffuser.perfume)
                UpdateDevice(devcount*5+3, 0, diffuser.fill)
                temp = int(diffuser.perfume_amount*10)
                UpdateDevice(devcount*5+4,temp,str(temp))
                temp = int(diffuser.room_size*10)
                UpdateDevice(devcount*5+5,temp,str(temp))

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onDeviceRemoved(self, Units):
        Domoticz.Debug("onDeviceRemoved called")


    def onStop(self):
        Domoticz.Debug("onStop called")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onDeviceRemoved(Unit):
    global _plugin
    _plugin.onDeviceRemoved(Unit)

# Generic helper functions

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "Parameter '" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))        
    return
    
def DumpHTTPResponseToLog(httpResp, level=0):
    if (level==0): Domoticz.Debug("HTTP Details ("+str(len(httpResp))+"):")
    indentStr = ""
    for x in range(level):
        indentStr += "----"
    if isinstance(httpResp, dict):
        for x in httpResp:
            if not isinstance(httpResp[x], dict) and not isinstance(httpResp[x], list):
                Domoticz.Debug(indentStr + ">'" + x + "':'" + str(httpResp[x]) + "'")
            else:
                Domoticz.Debug(indentStr + ">'" + x + "':")
                DumpHTTPResponseToLog(httpResp[x], level+1)
    elif isinstance(httpResp, list):
        for x in httpResp:
            Domoticz.Debug(indentStr + "['" + x + "']")
    else:
        Domoticz.Debug(indentStr + ">'" + x + "':'" + str(httpResp[x]) + "'")

def get_key(val):
    for key, value in idxtable.items():
        if val == value:
            return key
    return "key doesn't exist"

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return