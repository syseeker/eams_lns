import logging
from eams_error import EAMS_Error 
from configobj import ConfigObj, ConfigObjError

class MeetingConfig:
    def __init__(self):        
        self.err = EAMS_Error()
        self.MEETINGS_CONFIG = None
        self.meetings = {}

    def loadMeetings(self, mfile):
        """Load meeting requests from MEETINGS_CONFIG"""
        self.MEETINGS_CONFIG = mfile
        logging.info("Loading meeting requests from %s" %self.MEETINGS_CONFIG)
        
        try:
            meetings = ConfigObj(self.MEETINGS_CONFIG,  file_error=True)
              
            #TODO: any validation required? Eg. Faulty datetime (end time earlier than start time etc), non-exists room, same people at same meeting time etc...
            self.meetings = meetings    
        except (ConfigObjError, IOError), e:        
            logging.error('%s' % (e))
            return self.err.eams_config_meeting_err()
        
        return 0
            
    def getMeetings(self):
        return self.meetings