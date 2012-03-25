
import ConfigParser
import os

from utils import Data

def createOrGetConfiguration(cfgFilepath):
    config = ConfigParser.RawConfigParser()
    sec = 'TraktCalendarExporter'
    if not os.path.exists(cfgFilepath):
        print "One time configuration. Can change it later in %s." % cfgFilepath 
        traktUser = raw_input("Trakt Username:").strip()
        traktApiKey = raw_input("Trakt API Key:").strip()
        userTimezone = raw_input("User Timezone:").strip()
        exportFile = raw_input("Export File Path:").strip()
        descFormatInput = raw_input("Event Description Format (default empty):").strip()
        eventDescFormat = descFormatInput if descFormatInput else ""
        
        config.add_section(sec)
        config.set(sec, "TraktUser", traktUser)
        config.set(sec, "TraktApiKey", traktApiKey)
        config.set(sec, "UserTimezone", userTimezone)
        config.set(sec, "ShowsTimezone", "US/Central")
        config.set(sec, "ExportFilePath", exportFile)
        config.set(sec, "EventDescriptionFormat", eventDescFormat)

        with open(cfgFilepath, 'wb') as configfile:
            config.write(configfile)
    else:
        config.read(cfgFilepath)
    
    result = {}
    for k in [ "TraktUser", "TraktApiKey", "UserTimezone", "ShowsTimezone", "ExportFilePath", "EventDescriptionFormat" ]:
        result[k] = config.get(sec, k)

    return Data(result)
