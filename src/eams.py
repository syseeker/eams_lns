import sys
import logging
from collections import Counter
from collections import namedtuple
from configobj import ConfigObj, ConfigObjError, flatten_errors
from copy import deepcopy
from datetime import datetime
from validate import Validator, ValidateError

from eams_error import EAMS_Error
from eams_meeting import Meeting
from eams_meeting_config import MeetingConfig
from eams_outdoor_temp import OutdoorTemperature
from eams_room_config import RoomConfig
from eams_room_thermal_config import RoomThermalCfg
from eams_timeslot import TimeSlot


class EAMS():
    def __init__(self, enableLog):

        self.err = EAMS_Error()        
        self.PROBLEM_CONFIG_SPEC = 'Data/ConfigSpecs/eams_prob_spec.cfg'
        
        if enableLog:
#           # activate log
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)
#             self.logger.setLevel(logging.DEBUG)
        
        self.Z = None
        #=======================================================================
        # Zone -> Room. Eg: {'1': {'Room1': {'ZoneID': '1', 'Width': 10.0, 'Length': 6.0 ...
        #=======================================================================               
        
        self.ZL = None
        #======================================================================
        # Zone -> Room Name. Eg: {'1': ['Room1'], '3': ['Room3'], '2': ['Room2']}
        #======================================================================
        
        self.RL = None
        #=======================================================================
        # Room list. Eg: ['Room1', 'Room3', 'Room2']
        #=======================================================================
        
        self.TS = None
        #=======================================================================
        #  Idx -> datetime. Eg: {0: datetime.datetime(2013, 1, 1, 8, 0), 1: datetime.datetime(2013, 1, 1, 8, 30), 2: datetime.datetime(2013, 1, 1, 9, 0), 3: datetime.datetime(2013, 1, 1, 9, 30), 4: datetime.datetime(2013, 1, 1, 10, 0),
        #=======================================================================
       
        self.ML = None
        #=======================================================================
        # List of namedtuple('Meeting_Desc', 'Key TimeWindows Duration Room Attendees')
        # [Meeting_Desc(Key='M110133', TimeWindows=[[datetime.datetime(2013, 1, 1, 9, 0), datetime.datetime(2013, 1, 1, 10, 30)], [datetime.datetime(2013, 1, 1, 12, 0), datetime.datetime(2013, 1, 1, 14, 0)], [datetime.datetime(2013, 1, 2, 14, 0), datetime.datetime(2013, 1, 2, 16, 0)]], Duration='3', Room='', Attendees=['1119', '2578', '3470', '4601', '6823', '7105', '7908', '12736', '12996', '20479']), Meeting_Desc(Key='M316335', TimeWindows=[[datetime.datetime(2013, 1, 1, 9, 0), datetime.datetime(2013, 1, 1, 18, 0)]], Duration='7', Room='', Attendees=['219', '246', '2852', '3304', '4095', '6845', '8495', '8811', '8927', '15695']), Meeting_Desc(Key='M325401', TimeWindows=[[datetime.datetime(2013, 1, 1, 9, 0), datetime.datetime(2013, 1, 1, 18, 0)]], Duration='7', Room='', Attendees=['264', '2165', '2528', '2890', '3167', '4273', '5258', '5363', '10719', '20204']), Meeting_Desc(Key='M433676', TimeWindows=[[datetime.datetime(2013, 1, 1, 9, 0), datetime.datetime(2013, 1, 1, 18, 0)]], Duration='7', Room='', Attendees=['413', '1104', '2192', '2674', '3201', '6866', '13958', '13998', '14601', '14607'])]
        #=======================================================================
                
        self.CALS = {}
        #=======================================================================
        # List of Conflicting Meetings follow the sequence of self.ML
        # eg. For ML[1] is conflict with ML[2] because of attendee['6153', '2425', '895']
        # 0 :  {}
        # 1 :  {2: ['6153', '2425', '895'], 3: ['6153']}
        # 2 :  {1: ['6153', '2425', '895'], 3: ['1068', '6153']}
        # 3 :  {1: ['6153'], 2: ['1068', '6153']}
        #=======================================================================
        
        self.MTYPE = []
        self.mtdesc = namedtuple('Meeting_Type', 'MTW MA MD MCA MLS')
        #=======================================================================   
        # List of Meeting Clique     
        # Meeting_Type(MTW=(66, 81, 162, 177), MA=15, MD=None, MCA=['6153', '2425', '895'], MLS=[1])
        # Meeting_Type(MTW=(66, 81, 162, 177), MA=15, MD=None, MCA=['6153', '2425', '895', '1068'], MLS=[2])
        # Meeting_Type(MTW=(66, 81, 162, 177), MA=15, MD=None, MCA=['6153', '1068'], MLS=[3])
        # Meeting_Type(MTW=(66, 81, 162, 177), MA=15, MD=None, MCA=[], MLS=[4, 9])
        # Meeting_Type(MTW=(66, 81), MA=15, MD=None, MCA=[], MLS=[6, 8])
        # Meeting_Type(MTW=(162, 177), MA=15, MD=None, MCA=[], MLS=[0, 5, 7])
        #=======================================================================
        
        self.CMT = {}
        #=======================================================================   
        # List of Conflicting Meeting Type because of an attendee
        # Key: Attendee ID, Value: Follow offset of Meeting Type in self.MTYPE
        # {'1068': [1, 2], '6153': [0, 1, 2], '2425': [0, 1], '895': [0, 1]}
        #=======================================================================
       
        self.OAT = None
        #=======================================================================
        # Sorted outdoor temperature. Eg: OrderedDict([(datetime.datetime(2013, 1, 1, 8, 0), '26.00'), (datetime.datetime(2013, 1, 1, 8, 30), '26.00'), (datetime.datetime(2013, 1, 1, 9, 0), '28.00')
        #=======================================================================
        
        self.SH = None
        #=======================================================================
        # A list follow the sequence of TS
        #=======================================================================
                
        self.MTW = None
        #=======================================================================
        # A Double array follow the sequence of self.ML
        # [
        #    [[18, 21], [24, 28], [76, 80]],   <- array of time windows [Start_Time, End_Time] 
        #    [[18, 36]], 
        #    [[18, 36]]
        # ]
        #=======================================================================
                
        self.MR = None
        #=======================================================================
        # A Double array follow the sequence of self.ML
        #
        #=======================================================================
        
        self.MOM = None
        #=======================================================================
        # A Double array follow the sequence of self.ML with list of meetings which has similar attendee(s)
        #  [
        #    [1, 2], 
        #    [2], 
        #    []
        #  ]
        #=======================================================================
        
        self.MODE_CONFIG = ""
        self.STANDBY_MODE = ""
        self.MEETINGS_CONFIG_DATA = ""      
        self.OUTDOOR_TEMP_DATA = ""
        self.ROOM_CONFIG_DATA = ""        
        self.SCHEDULING_START_DATETIME = "" 
        self.SCHEDULING_END_DATETIME = ""
        self.SCHEDULING_INTERVAL = -1
        self.DAILY_WORKING_HOUR_START = ""    
        self.DAILY_WORKING_HOUR_END = ""
        self.HVAC_NON_PEAK_OFF = -1
        self.HVAC_SHUT_DOWN = ""
        self.HVAC_TURN_ON = ""    
        self.SOLAR_GAIN_LOW = -1
        self.SOLAR_GAIN_MEDIUM = -1 
        self.SOLAR_GAIN_HIGH = -1        
        self.SOLAR_RADIATION_AM_START = ""
        self.SOLAR_RADIATION_NOON_START = ""
        self.SOLAR_RADIATION_PM_START = ""
        self.SOLAR_RADIATION_NIGHT_START = ""
        self.WALL_RESISTANCE_LOW = -1  
        self.WALL_RESISTANCE_HIGH = -1
        self.WALL_CAPACITANCE_LOW = -1
        self.WALL_CAPACITANCE_HIGH = -1        
        self.INITIAL_TEMPERATURE_MODE = -1        
        self.INITIAL_TEMPERATURE = -1      
        self.TEMPERATURE_UNOCC_MIN = -1               
        self.TEMPERATURE_UNOCC_RANGE_INCR = -1     
        self.TEMPERATURE_OCC_COMFORT_RANGE_INCR = -1                  
        self.TEMPERATURE_UNOCC_MAX = -1          
        self.TEMPERATURE_OCC_COMFORT_RANGE_DECR = -1      
        self.TEMPERATURE_CONDITIONED_AIR = -1            
        self.TEMPERATURE_SUPPLY_AIR_HIGH = -1         
        self.ALPHA_IAQ_FACTOR_OF_SAFETY = -1                 
        self.BETA_FAN_POWER_CONSTANT = -1        
        self.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE = -1 
        self.INITIAL_TEMPERATURE_SUPPLY_AIR_OCC = -1  
        self.INITIAL_TEMPERATURE_SUPPLY_AIR_UNOCC = -1
        self.INITIAL_MASS_AIR_FLOW_SUPPLY_AIR_OCC = -1  
        self.INITIAL_MASS_AIR_FLOW_SUPPLY_AIR_UNOCC = -1
        self.MASS_AIR_FLOW_SUPPLY_AIR_MIN = -1             
        self.MASS_AIR_FLOW_SUPPLY_AIR_MAX = -1             
        self.MASS_AIR_FLOW_SUPPLY_AIR_PER_PERSON = -1      
        self.MASS_AIR_FLOW_OUTSIDE_AIR_PER_PERSON = -1   
        self.MASS_AIR_FLOW_OUTSIDE_AIR_PER_METER_SQUARE = -1 
        self.MASS_AIR_FLOW_RETURN_AIR_RATIO = -1   
        self.OCCUPANT_SENSIBLE_HEAT_GAIN = -1  
        self.OCCUPANT_WATER_VAPOR_RATE = -1        
        self.PLOT_INTERVAL = -1
        self.PLOT_STEP = -1  
        self.ZOOMPLOT_START_DATETIME = "" 
        self.ZOOMPLOT_END_DATETIME = ""
        self.ZOOMPLOT_INTERVAL = -1
        self.ZOOMPLOT_STEP = -1
    
    def activateLogFile(self, f):        
        # remove old handler
        for old_handler in self.logger.handlers:
            self.logger.removeHandler(old_handler)
             
        # create a handler with the name defined by the variable f
        handler = logging.FileHandler(f)
        # add that handler to the logger
        self.logger.addHandler(handler)
    
    def _critical_err(self):
        sys.exit("Pop, Bang, Whooo, Boom... Fire Alarm! Evacuate! EAMS exit.")
    
    def _validateProblemConfig(self, config):        
        validator = Validator()
        results = config.validate(validator)
        logging.info("Validating problem configuration, result: %s" %results)
        
        if results != True:
            for (_, key, _) in flatten_errors(config, results):
                if key is not None:
                    logging.error('The "%s" key failed validation' % (key))
                else:
                    logging.error("Configuration error. Either some section was missing, duplicate key(s) etc..." )
            return self.err.eams_config_problem_err()
        return 0
    
    def _loadProblemConfig(self, config):
        #TODO: should cast these variables according to their type here, so you need not cast them later on!
        self.MODE_CONFIG = config['MODE_CONFIG']        
        self.STANDBY_MODE = config['STANDBY_MODE']
        self.MEETINGS_CONFIG_DATA = config['MEETINGS_CONFIG_DATA']
        self.OUTDOOR_TEMP_DATA = config['OUTDOOR_TEMP_DATA'] 
        self.ROOM_CONFIG_DATA = config['ROOM_CONFIG_DATA']        
        self.SCHEDULING_START_DATETIME = config['SCHEDULING_START_DATETIME']
        self.SCHEDULING_END_DATETIME = config['SCHEDULING_END_DATETIME']
        self.SCHEDULING_INTERVAL = int(config['SCHEDULING_INTERVAL'])
        self.DAILY_WORKING_HOUR_START = config['DAILY_WORKING_HOUR_START']
        self.DAILY_WORKING_HOUR_END = config['DAILY_WORKING_HOUR_END']         
        self.HVAC_NON_PEAK_OFF = config['HVAC_NON_PEAK_OFF']
        self.HVAC_SHUT_DOWN = config['HVAC_SHUT_DOWN']
        self.HVAC_TURN_ON = config['HVAC_TURN_ON'] 
        self.SOLAR_GAIN_LOW = config['SOLAR_GAIN_LOW']
        self.SOLAR_GAIN_MEDIUM = config['SOLAR_GAIN_MEDIUM']
        self.SOLAR_GAIN_HIGH =  config['SOLAR_GAIN_HIGH'] 
        self.SOLAR_RADIATION_AM_START = config['SOLAR_RADIATION_AM_START']
        self.SOLAR_RADIATION_NOON_START = config['SOLAR_RADIATION_NOON_START']
        self.SOLAR_RADIATION_PM_START = config['SOLAR_RADIATION_PM_START']
        self.SOLAR_RADIATION_NIGHT_START = config['SOLAR_RADIATION_NIGHT_START']       
        self.WALL_RESISTANCE_LOW =  config['WALL_RESISTANCE_LOW']
        self.WALL_RESISTANCE_HIGH = config['WALL_RESISTANCE_HIGH']
        self.WALL_CAPACITANCE_LOW = config['WALL_CAPACITANCE_LOW']
        self.WALL_CAPACITANCE_HIGH = config['WALL_CAPACITANCE_HIGH']    
        self.INITIAL_TEMPERATURE_MODE = config['INITIAL_TEMPERATURE_MODE']             
        self.INITIAL_TEMPERATURE = config['INITIAL_TEMPERATURE']
        self.TEMPERATURE_UNOCC_MIN = float(config['TEMPERATURE_UNOCC_MIN'])            
        self.TEMPERATURE_UNOCC_RANGE_INCR = float(config['TEMPERATURE_UNOCC_RANGE_INCR'])        
        self.TEMPERATURE_OCC_COMFORT_RANGE_INCR = float(config['TEMPERATURE_OCC_COMFORT_RANGE_INCR'])                    
        self.TEMPERATURE_UNOCC_MAX = float(config['TEMPERATURE_UNOCC_MAX'])             
        self.TEMPERATURE_OCC_COMFORT_RANGE_DECR = float(config['TEMPERATURE_OCC_COMFORT_RANGE_DECR'])      
        self.TEMPERATURE_CONDITIONED_AIR = float(config['TEMPERATURE_CONDITIONED_AIR'])                
        self.TEMPERATURE_SUPPLY_AIR_HIGH = float(config['TEMPERATURE_SUPPLY_AIR_HIGH'])   
        self.ALPHA_IAQ_FACTOR_OF_SAFETY = config['ALPHA_IAQ_FACTOR_OF_SAFETY']                   
        self.BETA_FAN_POWER_CONSTANT = config['BETA_FAN_POWER_CONSTANT']
        self.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE = float(config['AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE'])
        self.INITIAL_TEMPERATURE_SUPPLY_AIR_OCC = float(config['INITIAL_TEMPERATURE_SUPPLY_AIR_OCC'])  
        self.INITIAL_TEMPERATURE_SUPPLY_AIR_UNOCC = float(config['INITIAL_TEMPERATURE_SUPPLY_AIR_UNOCC'])
        self.INITIAL_MASS_AIR_FLOW_SUPPLY_AIR_OCC = float(config['INITIAL_MASS_AIR_FLOW_SUPPLY_AIR_OCC'])  
        self.INITIAL_MASS_AIR_FLOW_SUPPLY_AIR_UNOCC = float(config['INITIAL_MASS_AIR_FLOW_SUPPLY_AIR_UNOCC'])       
        self.MASS_AIR_FLOW_SUPPLY_AIR_MIN = float(config['MASS_AIR_FLOW_SUPPLY_AIR_MIN'])             
        self.MASS_AIR_FLOW_SUPPLY_AIR_MAX = float(config['MASS_AIR_FLOW_SUPPLY_AIR_MAX'])             
        self.MASS_AIR_FLOW_SUPPLY_AIR_PER_PERSON = float(config['MASS_AIR_FLOW_SUPPLY_AIR_PER_PERSON'])      
        self.MASS_AIR_FLOW_OUTSIDE_AIR_PER_PERSON = float(config['MASS_AIR_FLOW_OUTSIDE_AIR_PER_PERSON'])   
        self.MASS_AIR_FLOW_OUTSIDE_AIR_PER_METER_SQUARE = float(config['MASS_AIR_FLOW_OUTSIDE_AIR_PER_METER_SQUARE']) 
        self.MASS_AIR_FLOW_RETURN_AIR_RATIO = float(config['MASS_AIR_FLOW_RETURN_AIR_RATIO'])        
        self.OCCUPANT_SENSIBLE_HEAT_GAIN = float(config['OCCUPANT_SENSIBLE_HEAT_GAIN'])     
        self.OCCUPANT_WATER_VAPOR_RATE = float(config['OCCUPANT_WATER_VAPOR_RATE'])           
        self.PLOT_INTERVAL = config['PLOT_INTERVAL']
        self.PLOT_STEP = config['PLOT_STEP']        
        self.ZOOMPLOT_START_DATETIME = config['ZOOMPLOT_START_DATETIME'] 
        self.ZOOMPLOT_END_DATETIME = config['ZOOMPLOT_END_DATETIME']
        self.ZOOMPLOT_INTERVAL = config['ZOOMPLOT_INTERVAL'] 
        self.ZOOMPLOT_STEP = config['ZOOMPLOT_STEP']
        logging.info("Problem configuration initialized.")
        
    def _diagMode(self):   
        logging.info("===============================================================")  
        
        if self.MODE_CONFIG == 'TSRA':
            logging.info("EAMS for Room Allocation & Time Scheduling.")
        elif self.MODE_CONFIG == 'TS':
            logging.info("EAMS for Time Scheduling only.")        
        else:
            logging.critical("Unknown or Unsupported mode < %s >" %(self.MODE_CONFIG))            
            return self.err.eams_config_problem_err() 
        
        logging.info("===============================================================")
        
        return 0
        
    def _populateRoomConfig(self):
        self.RC = RoomConfig(self.WALL_RESISTANCE_LOW, self.WALL_RESISTANCE_HIGH, 
                   self.WALL_CAPACITANCE_LOW, self.WALL_CAPACITANCE_HIGH, 
                   self.SOLAR_GAIN_LOW, self.SOLAR_GAIN_MEDIUM, self.SOLAR_GAIN_HIGH)        
        ret = self.RC.loadRoomConfig(self.ROOM_CONFIG_DATA)
        if ret == 0:  
            self.RC.populateRoomByZone()
            self.Z = self.RC.getRoomsInfoByZone("All")
            self.ZL = self.RC.getZoneList()
            self.RL = self.RC.getRoomList()
            self.RCL = self.RC.getRoomCapaList()
            self.RNL = self.RC.getRoomNeighboursList()
            logging.debug("Get rooms: %s" %self.Z)
            logging.debug("Get zonelist: %s" %(self.ZL))
            logging.debug("Get roomlist: %s" %(self.RL))    
            logging.debug("Get room capa list: %s" %(self.RCL))
            logging.debug("Get room neighbours list: %s" %(self.RNL))       
    # DEBUG_ONLY
    #         self.Z = self.RC.getRoomsInfoByZone("1")
    # DEBUG_ONLY
          
        return ret

    def _populateOutdoorTemperature(self):
        self.OTC = OutdoorTemperature()
        ret = self.OTC.loadOutdoorTemperature(self.OUTDOOR_TEMP_DATA)    
        if ret == 0:
            # Populate outdoor temperature
            # option 1:
#             if int(self.SCHEDULING_INTERVAL) >= 30:
#                 self.OAT = self.OTC.getSingleDayOutdoorTemperature(self.SCHEDULING_START_DATETIME, self.SCHEDULING_END_DATETIME, self.SCHEDULING_INTERVAL)
#             else:
#                 self.OAT = self.OTC.getSingleDayOutdoorTemperatureShortInterval(self.SCHEDULING_START_DATETIME, self.SCHEDULING_END_DATETIME, self.SCHEDULING_INTERVAL)            
            # option 2:      
            self.OAT = self.OTC.getOutdoorTemperature(self.SCHEDULING_START_DATETIME, self.SCHEDULING_END_DATETIME, self.SCHEDULING_INTERVAL)
            
            logging.debug("OAT: %s" %(self.OAT))
            
#             for k, v in self.OAT.iteritems():
#                 logging.debug("[%s]:[%s]" %(k,v))
                
            logging.debug("len: %s" %(len(self.OAT)))
            if len(self.OAT) == 0:
                return self.err.eams_no_outdoor_temp_in_scheduling_range()
          
            # Set initial temperature is set to outdoor temperature at first slot
#             option 1: override eams_probN.cfg INITIAL_TEMPERATURE
            if self.INITIAL_TEMPERATURE_MODE == '1':
                self.INITIAL_TEMPERATURE = float(self.OAT.get(datetime.strptime(self.SCHEDULING_START_DATETIME, "%Y-%m-%d %H:%M")))
                logging.debug("Initial OAT: %s" %(self.INITIAL_TEMPERATURE))
            # option 2:
#             self.INITIAL_TEMPERATURE = self.INITIAL_TEMPERATURE

            logging.debug("Set Initial Temperature : %.2f" %(self.INITIAL_TEMPERATURE))        
        return ret    
        
    def _populateMeetingConfig(self):
        self.MC = MeetingConfig()               
        ret = self.MC.loadMeetings(self.MEETINGS_CONFIG_DATA)
        if ret == 0:
            mr = self.MC.getMeetings() 
            
            self.M = Meeting()            
            ret = self.M.populateMeetingsForRoomAllocNSchedule(mr)
            if ret < 0:
                return ret
                
            self.ML = self.M.getMeetingsList() 
            logging.debug("Total number of meetings: %d" %(len(self.ML)))
            logging.debug(self.ML)
            
        return ret  
    
    def _populateSchedulingTimeSlot(self):
        """Form timeslot based on given work week and time slot interval"""
        self.TSC = TimeSlot(self.SCHEDULING_START_DATETIME, self.SCHEDULING_END_DATETIME, (int)(self.SCHEDULING_INTERVAL))
        self.TS = self.TSC.getTimeSlots()
        logging.debug("Timeslot: %s" %self.TS) 
        logging.debug("Total number of timeslot: %d" %len(self.TS))
            
    def _populateHVACStdTimeslot(self):
        """Populate binary indicator list which denotes if the timeslot is in standard operating hour of HVAC (i.e. always on) """  
        self.SH = []
        if self.HVAC_NON_PEAK_OFF ==  '1':
            s = datetime.strptime(self.HVAC_SHUT_DOWN, "%H:%M")
            e = datetime.strptime(self.HVAC_TURN_ON, "%H:%M")
         
            for _, v in self.TS.iteritems():
                if (v.time() >= s.time() or v.time() < e.time()):
                    self.SH.append(0)  #off HVAC
                else:
                    self.SH.append(1)
        else:
            for _, v in self.TS.iteritems():
                self.SH.append(1)
                
        logging.debug("HVAC Standard Hours:\n%s" %(self.SH))
                
    def _populateMeetingRequestTimeslot(self):       
        """Populate slot index of meetings' time windows """         
        self.MTW = []
        for i in xrange(len(self.ML)):
            self.MTW.append([])
            for j in xrange(len(self.ML[i].TimeWindows)):
                s = self.ML[i].TimeWindows[j][0]
                e = self.ML[i].TimeWindows[j][1]
                sidx = self.TSC.getTimeSlotIdxByDatetime(s)
                eidx = self.TSC.getTimeSlotIdxByDatetime(e)        

                if sidx is None:
                    logging.error("Meeting request falls outside of timeslot range. HALT.")
                    return self.err.eams_meeting_out_of_timeslot_range()  
                if eidx is None:
                    logging.error("Meeting ends outside of timeslot range. ")
                    return self.err.eams_meeting_out_of_timeslot_range()
                
                logging.debug("Meeting %s start at %s [slot %d], deadline at %s[slot %d], duration of %s slot(s)" %(self.ML[i].Key, s, sidx, e, eidx-1, self.ML[i].Duration))
                
#                 logging.debug("sidx=%s eidx=%s d=%d" %(sidx, eidx-1, int(self.ML[i].Duration)))
                if (eidx - sidx) < int(self.ML[i].Duration):
                    logging.error("Meeting duration longer than Earliest-Start-Time to Latest-Finished-Time timeslot. HALT.")
                    return self.err.eams_meeting_invalid_duration()
                
                self.MTW[i].append([sidx, eidx-1]) #Note: Meeting end at the slot before 'End' time, hence -1
        
        logging.debug("Meetings' time windows:")
        logging.debug(self.MTW)                    
        return 0
        
    def _populateFeasibleRoomsForMeeting(self):
        """Does location l has the capacity to accommodate meeting midx? """   
        
        logging.info("Populate feasible rooms for meeting(s)...")
        
        self.MR = []
        for i in xrange(len(self.ML)):
            self.MR.append([])
            
            a = len(self.ML[i].Attendees)
            
            if not self.ML[i].Room:  # no preferred room            
                for j in xrange(len(self.RCL)):
                    if a <= self.RCL[j]:
                        self.MR[i].append(j)
                        
                if not self.MR[i]:
                    logging.error("No feasible room for meeting [%d]" %i) 
                    return self.err.eams_meeting_no_feasible_room()
            else: # has preferred room
                if self.ML[i].Room not in self.RL:
                    logging.critical("Mode Config: %s. Preferred room [%s] for meeting [%s] does not exist in room list." %(self.MODE_CONFIG, self.ML[i].Room, self.ML[i].Key))
                    return self.err.eams_config_meeting_err()
                
                ridx = self.RL.index(self.ML[i].Room)
                if len(self.ML[i].Attendees) > self.RCL[ridx]:
                    logging.critical("Mode Config: %s. Preferred room [%s] for meeting [%s] has smaller capacity (only for %d people) than the number of attendee." %(self.MODE_CONFIG, self.ML[i].Room, self.ML[i].Key, self.RCL[ridx]))
                    return self.err.eams_config_meeting_err()
                
                self.MR[i].append(ridx)  # limit feasible room to preferred room
                
        logging.debug("Feasible rooms based on meetings' attendees and room capacity:")
        logging.debug(self.MR)    
        return 0
            
    
    def _populateMeetingsWithSimilarAttendees(self):
        """Does meeting m has similar attendee(s) as meeting om"""
        
        self.MOM = []        
        for mx in xrange(len(self.ML)):
            self.MOM.append([])
            # TODO: use set.intersection instead! See _populateMeetingConflicts()
            mx_multiset = Counter(self.ML[mx].Attendees)
            for my in xrange(mx+1, len(self.ML)):
#                 logging.debug("checking m[%d, %d]" %(mx, my))
                my_multiset = Counter(self.ML[my].Attendees)
                if (list((mx_multiset & my_multiset).elements())):
                    logging.debug("Meeting %d and %d have similar attendees" %(mx,my))    
                    self.MOM[mx].append(my)
        
        logging.debug("Meetings which has similar attendee(s)") 
        logging.debug(self.MOM)
        
    def _populateRoomThermalCfg(self):
        """Populate individual room config to be used by Gurobi"""        
        self.RTC = RoomThermalCfg(self.Z, self.TS, 
                                  self.SOLAR_RADIATION_AM_START,
                                  self.SOLAR_RADIATION_NOON_START,
                                  self.SOLAR_RADIATION_PM_START,
                                  self.SOLAR_RADIATION_NIGHT_START)
            
    def _populateMeetingConflicts(self):
        """Which meeting is conflict with m, and who are the attendee that cause the conflict"""
         
        self.CALS = {}
        for mx in xrange(len(self.ML)):
            for my in xrange(mx+1, len(self.ML)):  
                oa = set(self.ML[mx].Attendees) & set(self.ML[my].Attendees)
                if oa:
                    if mx in self.CALS.keys():
                        self.CALS.get(mx).update({my:list(oa)})
                    else:
                        self.CALS[mx]={my:list(oa)}
                        
                    if my in self.CALS.keys():
                        self.CALS.get(my).update({mx:list(oa)})
                    else:
                        self.CALS[my]={mx:list(oa)}

#                 for k, v in self.CALS.iteritems():
#                     print k, ": ", v
#                 print ""
                
        # Add empty set for meetings w/o conflicts!
        no_conflict = list(set(list(xrange(len(self.ML)))).difference(set(self.CALS.keys())))
        for i in xrange(len(no_conflict)):
            self.CALS[no_conflict[i]] = {}
        
        # debug_only----------------------------------------
#         for k, v in self.CALS.iteritems():
#             print k, ": ", v
#         print ""
#         
#         for mx in xrange(len(self.ML)):             
#             for my in xrange(mx+1, len(self.ML)):  
#                 print "[", mx, "," , my, "] =", self._hasSameConflictProperties(mx, my)
#         print ""
#             
#         for m in xrange(len(self.ML)):
#             print 'Meeting', m
#             print 'Attendees with multiple meetings:', self._getConflictAttendees(m)
#             print 'Meetings with same attendee:', self._getConflictMeetings(m)
#             print ""    
        # debug_only----------------------------------------
            
    # debug_only----------------------------------------
#     def _hasSameConflictProperties(self, m1, m2):
#         # True:  if both meeting has the same conflict attendees and conflict meetings.
#         if (self.CALS[m1].values() != self.CALS[m2].values()):
#             return False
#         
#         if m2 in self.CALS[m1].keys() and m1 in self.CALS[m2].keys():
#             k1 = deepcopy(self.CALS[m1].keys())#.remove(m2)
#             k2 = deepcopy(self.CALS[m2].keys())#.remove(m1)
#             k1.remove(m2)
#             k2.remove(m1)
#             if k1 == k2:
#                 return True
#         else:
#             return False 
    # debug_only----------------------------------------
        
    def _getConflictAttendees(self, m):
        return self.CALS[m].values()
     
    def _getConflictMeetings(self, m):
        return self.CALS[m].keys()

    # TODO: move this to new file which compute meeting clique!
    # TODO: For simplicity, we do not classify meeting further based on duration and room.
    def _populateMeetingClique(self):        
        
        self.MTYPE = []        
        # Group based on time window
        logging.debug("Group based on time window... ")
        dg_mtw = {}
        for i in xrange(len(self.ML)):
#             print "ML[", i, "]=", self.ML[i].Key
#             print "MTW[", i, "]:", self.MTW[i]
#             print "MOM[", i, "]:", self.MOM[i]
#             print "MA:", len(self.ML[i].Attendees)
#             print "MD:", self.ML[i].Duration
#             print "MR:", self.MR[i]
 
            mtw_tup = ()                                # create tuple for MTW object [[66, 81], [114, 129]] --> (66, 81, 114, 129)
            for j in xrange(len(self.MTW[i])):
                mtw_tup = mtw_tup + tuple(self.MTW[i][j])       

            if mtw_tup in dg_mtw.keys():                # use tuple as key, store index of ML which has that MTW properties 
                dg_mtw.get(mtw_tup).append(i)           #  (66, 81, 114, 129): [4]  --> ML[4] has  [[66, 81], [114, 129]
            else:
                dg_mtw[mtw_tup] = [i]                
                                 
        logging.debug("Num MTW group:%d" %len(dg_mtw))
        logging.debug("%s" %dg_mtw)
        
        # Re-group based on number of attendee
        logging.debug("\nWithin group of same time window, re-group based on number of attendee... ")
        logging.debug("For simplicity, meetings are grouped based on 2-5, 6-15, 16-30 ppl")
        for k, v in dg_mtw.iteritems():
            logging.debug("k=%s, ---v=%s" %(k,v))
            numals = {5:[],15:[],30:[], 100:[]}  # a dict of based on number of attendee (num attendee less than 'key')            
            for m in xrange(len(v)):
                mid = v[m]
                numa = len(self.ML[mid].Attendees)
                if numa <= 5:
                    numals.get(5).append(mid)
                elif numa <= 15:
                    numals.get(15).append(mid)
                elif numa <= 30:
                    numals.get(30).append(mid)
                else:
                    numals.get(100).append(mid)
            
            for nk,nv in numals.iteritems():
                if len(nv):
                    self.MTYPE.append(self.mtdesc(k, nk, None, None, nv))
         
        logging.debug("%s" %(self.MTYPE))
        logging.debug("Num meeting type:%d" %len(self.MTYPE))
        
        # Re-group based on attendee conflict
        logging.debug("\nWithin group of same time window & same num attendee group, Re-group based on attendee conflict... ")
        new_mtype = []     
        for i in xrange(len(self.MTYPE)):
            mls = self.MTYPE[i].MLS 
            logging.debug("Evaluating MTYPE %d: %s" %(i, mls))
            tmp_mtype = []   
            for x in xrange(len(mls)):
                stat = False
                m = mls[x]
                mca = self._getConflictAttendees(m)
                # Get a unique list of mca
                uniq_mca = []
                for a in xrange(len(mca)):
                    for b in xrange(len(mca[a])):
                        if mca[a][b] not in uniq_mca:
                            uniq_mca.append(mca[a][b])
                logging.debug(uniq_mca)
                
                for y in xrange(len(tmp_mtype)):  
#                     print "tmp_mtype[y].MCA:", tmp_mtype[y].MCA
#                     print "uniq_mca:", uniq_mca
#                     print tmp_mtype[y].MCA == uniq_mca
                    if tmp_mtype[y].MCA == uniq_mca:
                        tmp_mtype[y].MLS.append(m)
                        stat = True
                        break
                if stat == False:
                    tmp_mtype.append(self.mtdesc(self.MTYPE[i].MTW, self.MTYPE[i].MA, None, uniq_mca, [m]))
                
            for j in xrange(len(tmp_mtype)):
                new_mtype.append(tmp_mtype[j]) 
        
        logging.info("%s" %new_mtype)   
        logging.info("Number of new MTYPE:%d" %len(new_mtype))
#         # debug only -------------
#         for i in xrange(len(new_mtype)):
#             print new_mtype[i]
#         print "Num MTYPE:" + str(len(new_mtype))
#         # debug only -------------
        for i in xrange(len(new_mtype)):
            logging.info("MTYPE[%d]:%s" %(i, str(new_mtype[i])))
                
        # Overwrite MTYPE
        self.MTYPE = new_mtype
        
        
    def _populateConflictMeetingTypesBasedOnAttendee(self):
        self.CMT = {}        
        for i in xrange(len(self.MTYPE)): 
            for j in xrange(len(self.MTYPE[i].MCA)):
                aid = self.MTYPE[i].MCA[j]
                if aid not in self.CMT.keys():
                    self.CMT[aid] = [i]
                else:
                    self.CMT.get(aid).append(i)
                    
        logging.debug("ConflictMeetingTypes: %s" %self.CMT)
        
            
    def _populateProbData(self, filename):            
        ret = 0
        try:
            # Load problem configuration
            config = ConfigObj(filename,  configspec=self.PROBLEM_CONFIG_SPEC, file_error=True)   
            ret = self._validateProblemConfig(config)
            if ret < 0:                 
                raise ValidateError()
            self._loadProblemConfig(config)
            ret = self._diagMode()
            if ret < 0:
                raise ValueError("Invalid problem configuration.")
                        
            # Initialize & load room, meeting, timeslot, outdoor temperature etc information
            ret = self._populateRoomConfig()
            if ret < 0:
                raise ValueError("Invalid room configuration.")
            
            ret = self._populateMeetingConfig()
            if ret < 0:
                raise ValueError("Invalid meeting configuration.")
            
            ret = self._populateOutdoorTemperature()
            if ret < 0:
                raise ValueError("Invalid outdoor temperature configuration.")
             
            self._populateSchedulingTimeSlot()
             
            ret = self._populateMeetingRequestTimeslot()
            if ret < 0:
                raise ValueError("Meeting request out of timeslot range.")
             
            ret = self._populateFeasibleRoomsForMeeting()
            if ret < 0:
                raise ValueError("Invalid room configuration for a meeting.")
             
            self._populateHVACStdTimeslot()
            self._populateMeetingsWithSimilarAttendees()
            
            self._populateMeetingConflicts()
            self._populateMeetingClique()
            self._populateConflictMeetingTypesBasedOnAttendee()
                         
            self._populateRoomThermalCfg()            
            
        except (ConfigObjError, IOError), e:        
            logging.critical('%s' % (e))
            return self.err.eams_config_problem_err() 
        except (ValidateError), e:        
            logging.critical("%s validation error. %d" %(filename, ret))            
        except (ValueError), e:
            logging.critical('%s' % (e))            
        
        return ret
    
#==================================================================
#     API
#==================================================================    
    
    def readProblemInstance(self, filename, enableLog):    
        if enableLog:
            # Configure log file
            if '/' in filename:
                fn = filename.replace('/',' ').replace('.',' ').split()
            else:
                fn = filename.replace('\\',' ').replace('.',' ').split()  
#             fn = 'Output\EAMS_' + fn[1] + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
            self.fn = 'Output/EAMS_' + fn[1] + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
            self.activateLogFile(self.fn)
                    
        logging.info("===============================================================")
        logging.info("Loading problem instance from %s ..." %filename)
        logging.info("===============================================================")        
        ret = self._populateProbData(filename)
        self.PROB_CFG = filename
        if ret < 0:
            self._critical_err()
                
    def getRoomThermalConfig(self, ridx, param):
        """API to retrieve room thermal resistance and capacitance"""
        
        if param == "C":
            return self.RTC.getRoomC(self.RL[ridx])
        
        if param == "Rij":
            return self.RTC.getRoomRij(self.RL[ridx])
        if param == "Rimj":
            return self.RTC.getRoomRimj(self.RL[ridx])
        if param == "Rji":
            return self.RTC.getRoomRji(self.RL[ridx])
        if param == "Cij":
            return self.RTC.getRoomCij(self.RL[ridx])
        if param == "Cji":
            return self.RTC.getRoomCji(self.RL[ridx])
        
        if param == "Rik":
            return self.RTC.getRoomRik(self.RL[ridx])
        if param == "Rimk":
            return self.RTC.getRoomRimk(self.RL[ridx])
        if param == "Rki":
            return self.RTC.getRoomRki(self.RL[ridx])
        if param == "Cik":
            return self.RTC.getRoomCik(self.RL[ridx])
        if param == "Cki":
            return self.RTC.getRoomCki(self.RL[ridx])
        
        if param == "Ril":
            return self.RTC.getRoomRil(self.RL[ridx])
        if param == "Riml":
            return self.RTC.getRoomRiml(self.RL[ridx])
        if param == "Rli":
            return self.RTC.getRoomRli(self.RL[ridx])
        if param == "Cil":
            return self.RTC.getRoomCil(self.RL[ridx])
        if param == "Cli":
            return self.RTC.getRoomCli(self.RL[ridx])
        
        if param == "Rio":
            return self.RTC.getRoomRio(self.RL[ridx])
        if param == "Rimo":
            return self.RTC.getRoomRimo(self.RL[ridx])
        if param == "Roi":
            return self.RTC.getRoomRoi(self.RL[ridx])
        if param == "Cio":
            return self.RTC.getRoomCio(self.RL[ridx])
        if param == "Coi":
            return self.RTC.getRoomCoi(self.RL[ridx])
        
        if param == "Rif":
            return self.RTC.getRoomRif(self.RL[ridx])
        if param == "Rfi":
            return self.RTC.getRoomRfi(self.RL[ridx])
        if param == "Cif":
            return self.RTC.getRoomCif(self.RL[ridx])
        if param == "Cfi":
            return self.RTC.getRoomCfi(self.RL[ridx])
        
        if param == "Ric":
            return self.RTC.getRoomRic(self.RL[ridx])
        if param == "Rci":
            return self.RTC.getRoomRci(self.RL[ridx])
        if param == "Cic":
            return self.RTC.getRoomCic(self.RL[ridx])
        if param == "Cci":
            return self.RTC.getRoomCci(self.RL[ridx])
        
        if param == "Rwij":
            return self.RTC.getRoomRwij(self.RL[ridx])
        if param == "Rwik":
            return self.RTC.getRoomRwik(self.RL[ridx])
        if param == "Rwil":
            return self.RTC.getRoomRwil(self.RL[ridx])
        if param == "Rwio":
            return self.RTC.getRoomRwio(self.RL[ridx])
                
        if param == "Dim":
            return self.RTC.getRoomDim(self.RL[ridx])
             
    def getRoomSolarGain(self, slot, ridx, wall):
        """API to retrieve room solar gain"""
        return self.RTC.getRoomSolarGainByTime(slot, self.RL[ridx], wall) 
    
    def isInTimeWindows(self, midx, k):
        """Is k within feasible timeslot between earliest-start-time and latest-start-time? """
        d = self.ML[midx].Duration        
        for i in xrange(len(self.MTW[midx])):            
            tw = self.MTW[midx][i]
            if k >= tw[0] and  k <= (tw[1]-d+1): 
                return 1            
        return -1       
    
    def getFeasibleStartTime(self, midx, k):
        """If meeting m starts at kp, is it still on-going at time period k?"""
        ls = []        
        d = self.ML[midx].Duration
        for i in xrange(len(self.MTW[midx])):
            tw = self.MTW[midx][i]
            if tw[0] <= k and tw[1] >= k:
                kp = tw[0]
                while kp <= tw[1]-d+1:
                    if kp not in ls and kp <= k and kp+d-1 >= k:
                        ls.append(kp)
                    kp = kp+1                
        return ls
    

    
            
          
 
                
                
                