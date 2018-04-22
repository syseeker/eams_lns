
import logging
import collections
from datetime import datetime
from datetime import timedelta
from eams_error import EAMS_Error 
    
class OutdoorTemperature:
    def __init__(self):        
        self.err = EAMS_Error()
        self.half_hourly = 30
        self.hourly = 60
        self.OUTDOOR_TEMP_DATA = None
        self.temperature = {}      
        
    def loadOutdoorTemperature(self, tfile):
        """Load outdoor temperature from OUTDOOR_TEMP_DATA"""
        logging.info("Loading outdoor temperature data from %s" %tfile)
        
        try:
            df = open(tfile, 'r')
            data = ''.join(df.readlines())
            df.close()
            
            self._parseOutdoorTemperature(data)            
        except (IOError), e:        
            logging.error('%s' % (e))
            return self.err.eams_config_otc_err()
        
        return 0  
            
    def _parseOutdoorTemperature(self, data):
        """Parse the temperature input data"""
        
        #TODO: Adjust temperature to GMT+8, GMT+11 or GMT+10!!!   
        GMT = 8     
        temperature = {}
        lines = data.split('\n')    
        count = int(lines[0])
        for i in range(1, count+1):
            line = lines[i]
            parts = line.split()
            dtstr = ' '.join((parts[1], parts[2]))
            #NOTE: As dict type is used, duplicate entries with the same date/time is filtered.
            temperature[datetime.strptime(dtstr, "%Y-%m-%d %H:%M") - timedelta(hours=GMT)] = parts[3]
            
        #NOTE: Python dictionary is unordered by default. Use OrderedDict to make sure temperature is recorded in date/time order.
        self.temperature = collections.OrderedDict(sorted(temperature.items()))        
        
#         for k,v in self.temperature.iteritems():
#             logging.debug("[%s]: %s" %(k,v))
            
    
    def getOutdoorTemperature(self, start, end, interval):
        """Get outdoor temperature between specific timeframe"""
        s = datetime.strptime(start, "%Y-%m-%d %H:%M")
        e = datetime.strptime(end, "%Y-%m-%d %H:%M")
        logging.info("Extracting temperature data between %s and %s" %(start, end))
        
        temperature = {}   
        for k, v in self.temperature.iteritems():
            if (k >= s and k < e):
                if int(interval) == self.half_hourly: 
                    if (k.minute == 0 or k.minute == 30):                
                        temperature[k]=v                    
                elif int(interval) == self.hourly:
                    if (k.minute == 0):                
                        temperature[k]=v                   
                else:
                    temperature[k]=v           
        
        #TODO: double check if assigning dict to OrderedDict always returns the correct order!
        dtm = collections.OrderedDict(sorted(temperature.items()))        
        return dtm
    
    #NOTE: This is only for experiment - START
    def getSingleDayOutdoorTemperature(self, start, end, interval):
        """Get outdoor temperature between specific timeframe"""
        s = datetime.strptime(start, "%Y-%m-%d %H:%M")
        e = datetime.strptime(end, "%Y-%m-%d %H:%M")
        logging.info("Extracting temperature data between %s and %s" %(start, end))
        
        de = (s + timedelta(hours=24))
        
        i=0
        oneday_temp = []
        for k, v in self.temperature.iteritems():
            if (k >= s and k < de):
                if int(interval) == self.half_hourly: 
                    if (k.minute == 0 or k.minute == 30):
                        oneday_temp.append(v)      
                        i = i+1            
                elif int(interval) == self.hourly:
                    if (k.minute == 0):
                        oneday_temp.append(v)                        
                        i = i+1              
                else:
                    oneday_temp.append(v)
                    i = i+1
        
        total_i = i
                              
        # TODO: a bit stupid way
        ii=0
        temperature = {}
        for k, v in self.temperature.iteritems():
#             if (k >= de and k <= e):
#             if (k >= s and k <= e):
            if (k >= s and k < e):
                if int(interval) == self.half_hourly: 
                    if (k.minute == 0 or k.minute == 30):                                                
                        temperature[k] = oneday_temp[ii]      
                        ii = ii+1                     
                elif int(interval) == self.hourly:
                    if (k.minute == 0):  
                        temperature[k] = oneday_temp[ii]
                        ii = ii+1                                 
                else:
                    temperature[k] = oneday_temp[ii]
                    ii = ii+1    
                    
                if ii == total_i: ii=0                   
                
                    
#         #TODO: double check if assigning dict to OrderedDict always returns the correct order!
        dtm = collections.OrderedDict(sorted(temperature.items()))        
        return dtm
    
    def getSingleDayOutdoorTemperatureShortInterval(self, start, end, interval):
        """Get outdoor temperature between specific timeframe"""
        s = datetime.strptime(start, "%Y-%m-%d %H:%M")
        e = datetime.strptime(end, "%Y-%m-%d %H:%M")
        logging.info("Extracting temperature data between %s and %s for %s mins interval" %(start, end, interval))
        
        if interval >= self.half_hourly:
            # TODO: this is quick fix, silly way. Error code should be return to halt the app.
            logging.critical("Scheduling interval is longer than %d, you SHOULD NOT call this function." %self.half_hourly)
             
        de = (s + timedelta(hours=24))
        
        i=0
        oneday_temp = []
        for k, v in self.temperature.iteritems():
            if (k >= s and k < de):
                if (k.minute == 0 or k.minute == 30):
                    oneday_temp.append(v)      
                    logging.debug("Time [%s]: %s" %(k,v))
                    i = i+1    
        total_i = i
        
#         logging.debug("total_i: %d, len: %d, One day temp: %s" %(total_i, len(oneday_temp), oneday_temp))
                
        ii=0
        temperature = {}
        for k, v in self.temperature.iteritems():
            if (k >= s and k < e):
#                 logging.debug("For time period t=%s" %(k))    
                if (k.minute == 0 or k.minute == 30):
                    curr_t = k
                    next_t = (curr_t + timedelta(minutes=30))
#                     logging.debug("curr_t: %s, next_t: %s" %(curr_t, next_t))
                    t = curr_t
                    
                    curr_rec = float(oneday_temp[ii])
                    if ii < total_i-1:
                        next_rec = float(oneday_temp[ii+1])                    
                    else:
                        next_rec = float(oneday_temp[0])
#                     logging.debug("current temp record [%s], next [%s]" %(curr_rec, next_rec))
                        
                    if interval==1:
                        delta_rec = float(next_rec - curr_rec)/10
                    else:
                        delta_rec = float((next_rec - curr_rec)/float(interval))
                        
                    j = 0
                    while t < next_t:
#                         logging.debug("interpolate at t=%s, +%.3f" %(t, delta_rec * j))
                        temperature[t] = curr_rec + (delta_rec * j)
                        
                        t =  t + timedelta(minutes=int(interval))
                        j = j+1
                
                    ii = ii + 1
                    if ii == total_i: ii=0  
                    
        dtm = collections.OrderedDict(sorted(temperature.items()))
                
        return dtm
        #NOTE: This is only for experiment - END

