import logging
from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from random import randint
# from eams_common import activateLog
from eams_meeting_generator import EAMS_MGEN

# ----------------------------------------------------
# [M534303]
# Attendees=1877, 1920, 2005, 2033, 2867, 2996, 3205, 4835, 6015, 7194, 7350, 7587, 8341, 8974, 9323
# Duration=2
#     [[W1]]
#     Start=2013-01-06 09:00
#     End=2013-01-06 17:00
# ----------------------------------------------------    

# EXAM_DAT_1 = "Data/01s1es.dat"
# STUDENT_EXAM_DAT_1 = "Data/01s1s.dat"

# search 10-25 to get attendee conflict and more exams to be scheduled
MIN_STUDENT1 = 2
MAX_STUDENT1 = 200
MIN_STUDENT2 = 201
MAX_STUDENT2 = 440
MIN_STUDENT3 = 441#24
MAX_STUDENT3 = 600#24

# EXAM_DURATION = 7  # 3.5hrs
# EXAM_START = '2013-01-01 09:00'
# EXAM_END = '2013-01-01 18:00'

# EXAM_START = '2013-01-01 09:30'
# EXAM_END = '2013-01-01 13:00'

# EXAM_START = '2013-01-01 14:00'
# EXAM_END = '2013-01-01 17:30'

class EAMS_MELBU():
    def __init__(self):
        self.EXAM_DAT = "Data/Patat/MelbU/01s1es.dat"
        self.STUDENT_EXAM_DAT = "Data/Patat/MelbU/01s1s.dat"
        
        self.smlist = []
        self.elist = []
        self.exam_attendee = {}
        self.edat = namedtuple('Exam_Desc', 'Key NumStudent')
        self.edesc = namedtuple('Exam_Sche_Desc', 'Key Start End Duration Room Attendees')
                 
#         activateLog()
        self._readStudentDat(self.STUDENT_EXAM_DAT)
        self._populateStudentDat()
        self._readExamDat(self.EXAM_DAT)
        self._populateExamDat()        
        self._populateExamSche()
        
    def getFilteredData(self):
        return self.elist
        
    def _readStudentDat(self, student_dat):
        studDataFile = open(student_dat, 'r')
        self.studentData = ''.join(studDataFile.readlines())        
        studDataFile.close()
        
    def _populateStudentDat(self):
        lines = self.studentData.split('\n')
        for i in xrange(len(lines)):
            line = lines[i]
            dat = line.split()
            if dat:
                student_id = int(dat[0])
                exam_id = int(dat[1])
                
                e = self.exam_attendee.get(exam_id)
                if not e:
                    self.exam_attendee[exam_id] = [student_id]
                else:
                    e.append(student_id)
                    
        logging.debug(self.exam_attendee)
                    
    def _readExamDat(self, exam_dat):
        examDataFile = open(exam_dat, 'r')
        self.examData = ''.join(examDataFile.readlines())        
        examDataFile.close()
        
    def _populateExamDat(self):
#         logging.debug(self.examData)
        lines = self.examData.split('\n')
#         logging.debug(len(lines))
        
        m = []
        for i in xrange(len(lines)):
            line = lines[i]
            dat = line.split()
            if dat:
                exam_id = int(dat[0])
                num_student = int(dat[1])
                if ((num_student >= MIN_STUDENT1 and num_student <= MAX_STUDENT1) 
                    or (num_student >= MIN_STUDENT2 and num_student <= MAX_STUDENT2)
                    or (num_student >= MIN_STUDENT3 and num_student <= MAX_STUDENT3)
                    ):
                    m.append(self.edat(exam_id, num_student))
        self.smlist = sorted(m , key=attrgetter('NumStudent'), reverse=False)
#         logging.debug(self.smlist)
#         logging.debug("Num Exam: %d" %(len(self.smlist)))
            
            
    def _populateExamSche(self):        
        m = []
        for i in xrange(len(self.smlist)):
#             Key Start End Duration Room Attendees
            exam_id = self.smlist[i].Key      
            
            alist = self.exam_attendee.get(exam_id)
            if len(alist) > 30:
                eid = randint(10, len(alist))
                alist = self.exam_attendee.get(exam_id)[eid-10:eid]
                print "i:", i, " sid:", eid-10, " eid:", eid
                
            # Option 1: no start/end time and duration      
            m.append(self.edesc(exam_id, 
                                None,
                                None, 
                                None, 
                                None, 
                                alist))
            
            # Option 2: with start/end time, duration
#             m.append(self.edesc(exam_id, 
#                                 datetime.strptime(EXAM_START, "%Y-%m-%d %H:%M"),
#                                 datetime.strptime(EXAM_END, "%Y-%m-%d %H:%M"), 
#                                 EXAM_DURATION, 
#                                 None, 
#                                 self.exam_attendee.get(exam_id)))
            
        logging.debug(m)
        self.elist = m
        
#         for i in xrange(len(self.smlist)):
#             logging.debug("%d %d" %(len(self.elist[i].Attendees), self.smlist[i].NumStudent))
#             
            
    def getExam(self):
        return self.elist
    
    
    def diagExam(self):        
        for i in xrange(len(self.elist)):            
            print self.elist[i].Key
            print self.elist[i].Attendees
#             print "Exam ID:", self.elist[i].Key
#             print "Atendee:", self.elist[i].Attendees
        print "NumExam:", len(self.elist)
        
    def diagAttendeeConflict(self):
        for i in xrange(len(self.elist)):
            if (self.elist[i].Attendees != None):
                for j in xrange(len(self.elist[i].Attendees)):
                    aid = self.elist[i].Attendees[j]
                    print "Attendee", aid, "sits in exam", self.elist[i].Key,
                    for ii in xrange(i+1, len(self.elist)):
                        for jj in xrange(len(self.elist[ii].Attendees)):
                            if self.elist[ii].Attendees[jj] == aid:
                                print " ", self.elist[ii].Key,
                    print ""
                            
                
                
    
melbu = EAMS_MELBU()
# melbu.diagExam()
# melbu.diagAttendeeConflict()

mgen = EAMS_MGEN(melbu.getFilteredData())

