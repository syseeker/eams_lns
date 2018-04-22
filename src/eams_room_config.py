import logging
import collections
from eams_error import EAMS_Error 
from validate import Validator, ValidateError
from configobj import ConfigObj, ConfigObjError, flatten_errors

#TODO: (a) Add checking to make sure all adjacent rooms must exist.

class RoomConfig:    
    def __init__(self, rl, rh, cl, ch, sl, sm, sh):
        """Initialization"""
        self.err = EAMS_Error()
        
        self.ROOM_CONFIG = None        
        self.WALL_RESISTANCE_LOW = rl
        self.WALL_RESISTANCE_HIGH = rh
        self.WALL_CAPACITANCE_LOW = cl
        self.WALL_CAPACITANCE_HIGH = ch
        self.SOLAR_GAIN_LOW = sl        
        self.SOLAR_GAIN_MEDIUM = sm
        self.SOLAR_GAIN_HIGH = sh
#         self.ROOM_CONFIG_SPEC = 'Data/eams_room_spec.cfg'
        self.ROOM_CONFIG_SPEC = 'Data/ConfigSpecs/eams_room_spec.cfg'
        self.rooms = {}
        self.zones = {}
        self.zonelist = {}
        self.roomlist = []
        self.roomcapa = []
        self.room_neighbours = []
        
    
    def _getRoomAdjacentWalls(self, room):
        """Get adjacent room of a given room's ID"""           
        aw = []    
        aw.append(room['Wall1']['AdjRoom'])
        aw.append(room['Wall2']['AdjRoom'])
        aw.append(room['Wall3']['AdjRoom'])
        aw.append(room['Wall4']['AdjRoom'])      
        return aw
        
    def _validateAdjacentWallConfig(self, rooms):
        """Validate consistency of adjacent wall(s) configurations in ROOM_CONFIG """
        logging.info("Validating adjacent walls configuration...")        
        awls = {}
        for k, v in rooms.iteritems():
            awls[k] = self._getRoomAdjacentWalls(v)
            logging.debug("Room [%s]'s adjacent rooms [%s]" %(k, ','.join(awls[k])))
        logging.debug("Rooms' adjacent wall's: %s" %awls)
    
        for k, v in awls.iteritems(): #range(len(awls)):  
            #k = awls.keys()[i]              # In room awls{'k'}
            nls = v #awls.get(k)               #    get awls{'k'} neighbors               
            
            # Check duplicate adjacent wall
            dls = collections.Counter(nls)
            if len([j for j in dls if j!='Outdoor' and dls[j]>1]) != 0:
                logging.error("Duplicate adjacent wall for the room[%s]: %s. HALT." %(k, dls))
                return self.err.eams_config_room_duplicate_wall_err()
            
            # Check if neighbor rooms has also set room{'k'}'s wall as adjacent wall.
            for j in range(len(nls)):
                nnls = awls.get(nls[j])     #    get awls{'k'} neighbors[j]'s neighbors
    #             logging.debug("neighbor of %s: [%s]" %(nls[j], nnls))
                
                # (nnls is None) : Some adjacent room has no configuration in ROOM_CONFIG. It's OK to ignore.    
                if nnls is not None and k not in nnls:              
                    logging.error("[%s] is not adjacent to [%s]. HALT." %(k, nls[j]))
                    return self.err.eams_config_room_invalid_wall_err()
            
        logging.info("Adjacent wall configurations, result: True.")    
        return 0
    
    def _validateRoomConfig(self, rooms):
        """Validate ROOM_CONFIG input value based on specification in ROOM_CONFIG_SPEC"""
        validator = Validator()
        results = rooms.validate(validator)
        logging.info("Validating room configuration, result: %s" %results)
        
        if results != True:
            for (section_list, key, _) in flatten_errors(rooms, results):
                if key is not None:
                    logging.error('The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)))
                else:
                    logging.error("Configuration error in %s. Either some section was missing, duplicate key(s) etc..." %self.ROOM_CONFIG)
            return self.err.eams_config_room_err()
        return 0
        
    
    def loadRoomConfig(self, rfile):
        """Load room configuration from ROOM_CONFIG"""
        self.ROOM_CONFIG = rfile
        logging.info("Loading room configuration from %s" %self.ROOM_CONFIG)
        ret = 0
        
        try:
            if self.ROOM_CONFIG == "":
                raise IOError("ROOM_CONFIG is not configured. Error.")
            
            rooms = ConfigObj(self.ROOM_CONFIG,  configspec=self.ROOM_CONFIG_SPEC, file_error=True)
        
            for _, v in rooms.iteritems():           
                for sk, sv in v.iteritems():
                    if sk == 'Wall1' or sk == 'Wall2' or sk == 'Wall3' or sk == 'Wall4' or sk == 'Ceiling' or sk == 'Floor':
                        for wk, wv in sv.iteritems():
                            if (wk == 'R1' or wk == 'R2' or wk == 'R3' or wk == 'RW') and (wv == 'LR'): sv[wk] = self.WALL_RESISTANCE_LOW
                            if (wk == 'R1' or wk == 'R2' or wk == 'R3' or wk == 'RW') and (wv == 'HR'): sv[wk] = self.WALL_RESISTANCE_HIGH
                            if (wk == 'C1' or wk == 'C2') and (wv == 'LC'): sv[wk] = self.WALL_CAPACITANCE_LOW
                            if (wk == 'C1' or wk == 'C2') and (wv == 'HC'): sv[wk] = self.WALL_CAPACITANCE_HIGH                        
                            if (wk == 'QS_AM' or wk == 'QS_NOON' or wk == 'QS_PM') and (wv == 'HG'): sv[wk] = self.SOLAR_GAIN_HIGH
                            if (wk == 'QS_AM' or wk == 'QS_NOON' or wk == 'QS_PM') and (wv == 'MG'): sv[wk] = self.SOLAR_GAIN_MEDIUM
                            if (wk == 'QS_AM' or wk == 'QS_NOON' or wk == 'QS_PM') and (wv == 'LG'): sv[wk] = self.SOLAR_GAIN_LOW
                    elif sk == 'CR':
                        if sv == 'LC':
                            v[sk] = self.WALL_CAPACITANCE_LOW
                        elif sv == 'HC':
                            v[sk] = self.WALL_CAPACITANCE_HIGH
                                
                                            
            logging.debug("Room properties: %s" %rooms)
            logging.debug("Total number of room: %d [%s]" %(len(rooms), ', '.join(rooms.keys())))
            
            ret = self._validateRoomConfig(rooms)
            if ret < 0: 
                raise ValidateError()
            
            ret = self._validateAdjacentWallConfig(rooms)      
            if ret < 0: 
                raise ValidateError()
            
            self.rooms = rooms
        
        except (ConfigObjError, IOError), e:        
            logging.critical('%s' % (e))
            ret = self.err.eams_config_room_err()
        except (ValidateError), e:        
            logging.critical("%s validation error. %d" %(self.ROOM_CONFIG, ret))
            
        return ret
        
    def populateRoomByZone(self):
        logging.info("Populate rooms into zone")        
#         logging.debug(self.CR)
        
        try:
            zr = {}
            zone = {}
            for k, v in self.rooms.iteritems():
                z = zr.get(v['ZoneID'])            
                if z is None:
                    zr[v['ZoneID']] = [k]
                    zone[v['ZoneID']] = {k:v}
                else:
                    z.append(k)        
                    zone[v['ZoneID']].update({k:v})
            logging.debug("Room by zone: %s" %zr)
            logging.debug("Room Info by zone: %s" %zone)        
            self.zonelist = zr # contain Room Name for rooms in each zone
            self.zones = zone  # contain full room information for rooms in each zone
            
            self._populateRoomList()
            self._populateRoomCapa()
            self._populateRoomNeighbourList()
        except (UnboundLocalError), e:
            logging.error('%s' % (e))
            
    def _populateRoomCapa(self):
        logging.info("Populate room capacity")
        try:
            for i in xrange(len(self.roomlist)):
                self.roomcapa.append(self.rooms.get(self.roomlist[i])['MaxCapa'])
        except(UnboundLocalError), e:
            logging.error('%s' % (e))
            
    def _populateRoomList(self):
        logging.info("Populate a list of rooms from all zones")
        for _,v in self.zonelist.iteritems():
            for i in range(len(v)):
                self.roomlist.append(v[i])                
        logging.debug("List of rooms: %s" %self.roomlist)
        
#     def countZoneNumRoom(self):
#         for k, v in self.zonelist.iteritems():
#             logging.debug("zone [%s]: %d" %(k,len(v)))
#             self.nzr[k] = len(v)
#             self.nr += len(v)
#         logging.debug("Total number of room: %d" %(self.nr))

    def _populateRoomNeighbourList(self):
        logging.info("Populate a list of room neighbours")
        
        nls = []
        ridx = -1
        for _, v in self.rooms.iteritems():
            nls = self._getRoomAdjacentWalls(v)
            logging.debug(nls)
            self.room_neighbours.append([])
            ridx = ridx + 1
            for n in xrange(len(nls)):
                if nls[n] == 'Outdoor':
                    self.room_neighbours[ridx].append(1000)
                elif nls[n] in self.roomlist:
                    self.room_neighbours[ridx].append(self.roomlist.index(nls[n]))                    
                else:
                    self.room_neighbours[ridx].append(-1)
#         logging.debug("Neighbor List:%s" %self.room_neighbours)
            
        
    def getRoomsInfoByZone(self, zone_key):     
        if self.zones is None:
            logging.error("Empty zone. Call populateRoomByZone() first.")
            return None   
        if zone_key == "All":
            return self.zones
        else:
            return self.zones.get(zone_key)
        
    def getZoneList(self):
        return self.zonelist
        
    def getRoomList(self):
        return self.roomlist
    
    def getRoomCapaList(self):
        return self.roomcapa
    
    def getRoomNeighboursList(self):
        return self.room_neighbours
    