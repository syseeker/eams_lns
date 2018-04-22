import os
import random
from datetime import datetime
from math import factorial

NUM_MSET = 5
NUM_M_PER_SET = 500 #10
# NUM_DURATION_SET = 4
MAX_TIMEWINDOW = 1
# NUM_TIMEWINDOW_SET = 5

class EAMS_MGEN():    
    def __init__(self, mdata):
        self.num_meeting = 0
        self.slotlist = []
        self.twlist = []
        self.mset = {}
        self.mset_conflict = {}
        
        self.initSlot()
        self.initSlotTimeWindow()
        
        self.mlist = mdata
        self.diagData()
        
        self.genMeetingSet()
        self.diagnose(-1)
        self.writeMeetingSet()
          
            
    def diagnose(self, mset_idx):
        self.diagMSet(mset_idx)  # -1 to print all, [0 to NUM_M_PER_SET-1] to print specific meeting        
        if mset_idx != -1:
            self.diagAttendeeConflict(mset_idx, self.mset[mset_idx][0])
        else:
            for i in xrange(len(self.mset)):
                self.diagAttendeeConflict(i, self.mset[i][0])
        
                
    def initSlot(self):
        """Duration of meetings. [2] means only 2 slots, [2,3] means either 2 or 3"""
#         self.slotlist = [2,3,4,6]
#         self.slotlist = [4,6]
#         self.slotlist = [6]
#         self.slotlist = [3]
        self.slotlist = [2]   
        self.NUM_DURATION_SET = len(self.slotlist)    
    
    def initSlotTimeWindow(self):
#         self.twlist.append(["2013-01-07 09:00", "2013-01-07 17:00"])        
        self.twlist.append(["2013-01-08 09:00", "2013-01-08 17:00"])
        self.twlist.append(["2013-01-09 09:00", "2013-01-09 17:00"])
#         self.twlist.append(["2013-01-10 09:00", "2013-01-10 17:00"])
        self.twlist.append(["2013-01-11 09:00", "2013-01-11 17:00"])

#         self.twlist.append(["2013-01-07 09:00", "2013-01-07 13:00"])        
#         self.twlist.append(["2013-01-08 09:00", "2013-01-08 13:00"])
#         self.twlist.append(["2013-01-09 09:00", "2013-01-09 13:00"])
#         self.twlist.append(["2013-01-10 09:00", "2013-01-10 13:00"])
#         self.twlist.append(["2013-01-11 09:00", "2013-01-11 13:00"])

#         self.twlist.append(["2013-01-07 09:00", "2013-01-07 11:00"])        
#         self.twlist.append(["2013-01-08 09:00", "2013-01-08 11:00"])
#         self.twlist.append(["2013-01-09 09:00", "2013-01-09 11:00"])
#         self.twlist.append(["2013-01-10 09:00", "2013-01-10 11:00"])
#         self.twlist.append(["2013-01-11 09:00", "2013-01-11 11:00"])

#         self.twlist.append(["2013-01-07 11:00", "2013-01-07 15:00"])        
#         self.twlist.append(["2013-01-08 11:00", "2013-01-08 15:00"])
#         self.twlist.append(["2013-01-09 11:00", "2013-01-09 15:00"])
#         self.twlist.append(["2013-01-10 11:00", "2013-01-10 15:00"])
#         self.twlist.append(["2013-01-11 11:00", "2013-01-11 15:00"])

#         self.twlist.append(["2013-01-07 13:00", "2013-01-07 17:00"])        
#         self.twlist.append(["2013-01-08 13:00", "2013-01-08 17:00"])
#         self.twlist.append(["2013-01-09 13:00", "2013-01-09 17:00"])
#         self.twlist.append(["2013-01-10 13:00", "2013-01-10 17:00"])
#         self.twlist.append(["2013-01-11 13:00", "2013-01-11 17:00"])

#         self.twlist.append(["2013-01-07 15:00", "2013-01-07 17:00"])        
#         self.twlist.append(["2013-01-08 15:00", "2013-01-08 17:00"])
#         self.twlist.append(["2013-01-09 15:00", "2013-01-09 17:00"])
#         self.twlist.append(["2013-01-10 15:00", "2013-01-10 17:00"])
#         self.twlist.append(["2013-01-11 15:00", "2013-01-11 17:00"])


        self.NUM_TIMEWINDOW_SET = len(self.twlist)   
         
        
    def diagData(self):
        self.num_meeting = len(self.mlist)
        for i in xrange(len(self.mlist)):            
            print i, ":", self.mlist[i].Key
            print i, ":", self.mlist[i].Start
            print i, ":", self.mlist[i].End
            print i, ":", self.mlist[i].Room
            print i, ":", self.mlist[i].Attendees
            print ""
            
    def genMeetingSet(self):
        #[0]: Offset of selected meeting
        #[1]: Index of  self.slotlist ---> Duration of meeting
        #[2]: Number of Time Window for the meeting
        #[3]: Index of self.twlist --->  Time Window for the meeting
        for i in xrange(NUM_MSET):
            self.mset[i] = [random.sample(range(self.num_meeting), NUM_M_PER_SET)]
            self.mset[i].append([random.randrange(self.NUM_DURATION_SET) for _ in range(NUM_M_PER_SET)])
            
            num_tw = [random.randrange(1, MAX_TIMEWINDOW+1) for _ in range(NUM_M_PER_SET)]
            self.mset[i].append(num_tw)
                        
            tw = []
            for j in xrange(len(num_tw)):
                tw.append(random.sample(range(self.NUM_TIMEWINDOW_SET), num_tw[j]))
            self.mset[i].append(tw)    
            
    def diagMSet(self, idx):
        if idx == -1:
            for i in xrange(len(self.mset)):
                print self.mset[i]                
        elif idx <= len(self.mset):
            print self.mset[idx]            
        else:
            print "Invalid mset offset"
            
    def diagAttendeeConflict(self, idx, meetings):
        num_meeting = len(meetings)        
        conflictls = []
        num_conflict_pair = 0
        for m in xrange(num_meeting):
            i = meetings[m]            
            for j in xrange(len(self.mlist[i].Attendees)):  # For every attendee in mlist[i]
                aid = self.mlist[i].Attendees[j]
#                 print "Attendee", aid, "sits in exam", self.mlist[i].Key,                                                
                for nm in xrange(m+1, num_meeting):
                    ii = meetings[nm]
                    for jj in xrange(len(self.mlist[ii].Attendees)):
                        if self.mlist[ii].Attendees[jj] == aid:
                            if [self.mlist[i].Key, self.mlist[ii].Key] not in conflictls:
                                conflictls.append([self.mlist[i].Key, self.mlist[ii].Key])
                                num_conflict_pair = num_conflict_pair + 1 
                                           
        num_comb_wo_repeat = factorial(num_meeting) / (factorial(num_meeting-2) * factorial(2))
        print "List of meeting pairs with conflict attendee:", conflictls 
        print "% of conflict:", str(num_conflict_pair), "/", str(num_comb_wo_repeat), "=", str(float(num_conflict_pair)/float(str(num_comb_wo_repeat))*100), "%\n"
        self.mset_conflict[idx] = [conflictls, str(float(num_conflict_pair)/float(str(num_comb_wo_repeat))*100)]  
        
    def writeMeetingSet(self):        
        # create directory
#         folder_name = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'))
#         directory = "Output\\" + folder_name         

        set_idx = str(datetime.now().strftime('%d_%f'))
        directory = "Data\\NewMeetings\\"  

        if not os.path.exists(directory):
            os.makedirs(directory)
            
        self.writeCompleteMeetingSet(directory, set_idx)
        self.writeMeetingConfig(directory, set_idx)       
        

    def writeCompleteMeetingSet(self, directory, set_idx):        
        fname = directory + "eams_meeting_m" + str(NUM_M_PER_SET) + "_" + str(set_idx) + "_readme"        
        f = open(fname,'w')
        
        f.write('Num_Meeting: ' + str(self.num_meeting) + "\n\n")
        f.write('Conflict: ' + str(self.mset_conflict) + "\n\n")
        
        for i in xrange(len(self.mlist)):            
            f.write(str(i) + ":" + str(self.mlist[i].Key) + "\n")
            f.write(str(i) + ":" + str(self.mlist[i].Start) + "\n")
            f.write(str(i) + ":" + str(self.mlist[i].End) + "\n")
            f.write(str(i) + ":" + str(self.mlist[i].Room) + "\n")
            f.write(str(i) + ":" + str(self.mlist[i].Attendees) + "\n")
            f.write("\n")
        f.close() 
        
  
    def writeMeetingConfig(self, directory, set_idx):
        for k in xrange(len(self.mset)):
            fname = directory + "\\eams_meeting_m" + str(NUM_M_PER_SET) + "_" + str(set_idx) + "_" + str(k) + ".cfg"         
            f = open(fname,'w')            
                        
            f.write("# Set Config: " + str(self.mset[k]) + "\n")
            f.write("# Slot List: " + ", ".join( repr(e) for e in self.slotlist)  + "\n")
            f.write("# TimeWindow List: " + ", ".join( repr(e) for e in self.twlist)  + "\n\n")
            f.write("# List of meeting with conflict attendee: " + ", ".join( repr(e) for e in self.mset_conflict.get(k)[0])  + "\n")
            f.write("# % of conflict: " + str(self.mset_conflict.get(k)[1]) + "\n\n")
            
            #[0]: Offset of selected meeting
            #[1]: Index of  self.slotlist ---> Duration of meeting
            #[2]: Number of Time Window for the meeting
            #[3]: Index of self.twlist --->  Time Window for the meeting
            for m in xrange(len(self.mset[k][0])):
                i = self.mset[k][0][m]
                d = self.mset[k][1][m]
                tw = self.mset[k][2][m]
                
                f.write('[M' + str(self.mlist[i].Key) + ']\n')
                f.write('Attendees=' + ", ".join( repr(e) for e in self.mlist[i].Attendees) + "\n")
                f.write('Duration=' + str(self.slotlist[d]) + "\n")
                
                for w in xrange(tw):                    
                    t = self.mset[k][3][m][w]
                    f.write("\t[[W" + str(w) + "]]\n")
                    f.write("\tStart="+ self.twlist[t][0] + "\n")
                    f.write("\tEnd="+ self.twlist[t][1] + "\n")
                    
                f.write("\n")
                    
                
            
            
            
            
                
        
            
            
            
            
            

