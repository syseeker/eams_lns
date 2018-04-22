import logging
from datetime import datetime
from datetime import timedelta

#TODO: form working hour timeslot only

class TimeSlot:    
    def __init__(self, start, end, interval):   
#         self.half_hourly = 30
#         self.hourly = 60     
        self.start = datetime.strptime(start, "%Y-%m-%d %H:%M")  
        self.end = datetime.strptime(end, "%Y-%m-%d %H:%M")
        self.interval = interval  
        
        #TODO: check start time must have tm_min=00, else invalid
        self.timeslots = {}
        self._createTimeSlot()
#         if interval == self.hourly:
#             self._createTimeSlot(self.hourly)
#         else:
#             self._createTimeSlot(self.half_hourly)
    
    def _createTimeSlot(self):
        logging.info("Populate timeslot between %s and %s for %s mins interval" %(self.start, self.end, self.interval))
        curr_time = self.start
        self.timeslots[0] = curr_time
        idx = 1         
        while curr_time < self.end:          
            curr_time = curr_time + timedelta(minutes=self.interval)
            self.timeslots[idx] = curr_time
            idx = idx+1
            
    def getTimeSlots(self):
        return self.timeslots
        
    def getTimeSlotIdxByString(self, dts):        
        for k, v in self.timeslots.iteritems():
            if v == datetime.strptime(dts, "%Y-%m-%d %H:%M:%S"):
                return k 
        return None
    
    def getTimeSlotIdxByDatetime(self, dt):        
        for k, v in self.timeslots.iteritems():
#             logging.debug("%s ,   %s " %(v, dt))
            if v == dt:
                return k 
        return None
            
        