import sys
from eams import EAMS
from solver_milp_dr import Solver_MILP

def run_it(cfg_data, runcfg):
#    cfg_data   -->  number of test cases in line[0], follow by a list of test cases to run 
    cfg = cfg_data.split('\n')
    runCount = int(cfg[0])    
    STATUS = ['', 'LOADED', 'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'CUTOFF', 'ITERATION_LIMIT', 'NODE_LIMIT', 'TIME_LIMIT', 'SOLUTION_LIMIT', 'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL']
   
    prop = []
    for i in range(1, runCount+1):        
        if not cfg[i]:
            sys.exit("Invalid run... No config file exists.")
        
        if '/' in cfg[i]:        
            casecfgid = cfg[i].replace('/',' ').replace('.',' ').split()
        else:
            casecfgid = cfg[i].replace('\\',' ').replace('.',' ').split()  
        
        print "\n\nRunning " + cfg[i] + "..."        
        eams.readProblemInstance(cfg[i], enableLog)
            
        milp_solver = Solver_MILP(eams, eams.fn, casecfgid[1], -1, 0)  
        [NumVars, NumBinVars, NumNZs, NumConstrs] = milp_solver.getModelAttr()
        
        print NumVars, " ", NumBinVars, " ", NumNZs, " ", NumConstrs
            
#             NUM_ROOM = len(eams.RL)
#             NUM_SLOT = len(eams.TS)-1
#             NUM_MEETING = len(eams.ML)
#             NUM_MEETING_TYPE = len(eams.MTYPE)
#             DURATION = eams.ML[0].Duration
#                         
#             mdensity = calcDensity()
#             [mminTemp, mavgTemp, mmaxTemp] = calcTemperatureStats()
#             [lrlc, lrhc, hrlc, hrhc, brbc] = calcRoom()
#             
#             prop.append([])
#             prop[i-1].append(cfg[i])  # Instance name            
#             prop[i-1].append(NUM_MEETING) # total meeting
#             prop[i-1].append(NUM_MEETING_TYPE) # total meeting type            
#             prop[i-1].append(mdensity)  # constrainedness, meeting density
#             prop[i-1].append(DURATION)   # duration of meeting (all meetings have same duration in each problem set)
#             
#             prop[i-1].append(NUM_SLOT)   # scheduling period
#             prop[i-1].append(NUM_SLOT*NUM_ROOM)  # hvac horizon 
#             prop[i-1].append(mminTemp)   # min temperature difference between OAT and 21-23 during eligible time window
#             prop[i-1].append(mavgTemp)   # avg temperature difference between OAT and 21-23 during eligible time window
#             prop[i-1].append(mmaxTemp)   # max temperature difference between OAT and 21-23 during eligible time window
#             
#             prop[i-1].append(lrlc)   # NUM_ROOM_LRLC
#             prop[i-1].append(lrhc)
#             prop[i-1].append(hrlc)
#             prop[i-1].append(hrhc)
#             prop[i-1].append(brbc)
            
#     if RUNTYPE == 1:
#         logFeatures(runcfg, prop)
            
def logFeatures(runcfg, prop):
    try:            
        
        fstr = 'Output/' + runcfg + '_features'
        f = open(fstr,'a')   
        
        header = ["INST", "NUM_MEETING", "NUM_MTYPE", "SCHE_DENSITY", "MEETING_DURATION", "NUM_SLOT_PER_ROOM", "TOTAL_SLOT", "MIN_TEMP_DIFF", "AVG_TEMP_DIFF", "MAX_TEMP_DIFF", "NUM_LRLC", "NUM_LRHC", "NUM_HRLC", "NUM_HRHC", "NUM_BRBC"]
        f.write(str(','.join(str(e) for e in header)))
        f.write("\n")
        
        # log BDV_x_MLK which is 1
        for i in xrange(len(prop)):
            f.write(str(','.join(str(e) for e in prop[i])))
            f.write("\n")
        
        f.close()      
        
    except (ValueError), e:
        print e  
            
def calcRoom():
#     print eams.RL
    lrlc = 0
    lrhc = 0
    hrlc = 0
    hrhc = 0
    brbc = 0    
    for i in xrange(len(eams.RL)):
        if 'LRLC' in eams.RL[i]:
            lrlc = lrlc + 1
        elif 'LRHC' in eams.RL[i]:
            lrhc = lrhc + 1
        elif 'HRLC' in eams.RL[i]:
            hrlc = hrlc + 1
        elif 'HRHC' in eams.RL[i]:
            hrhc = hrhc + 1
        elif 'BRBC' in eams.RL[i]:
            brbc = brbc + 1
#                 
#     print lrlc
#     print lrhc
#     print hrlc
#     print hrhc
#     print brbc
    
    return [lrlc, lrhc, hrlc, hrhc, brbc]
    
    
def calcTemperatureStats():
    
    NUM_SLOT = len(eams.TS)-1
    NUM_MEETING = len(eams.ML)
    
    total_diff = 0
    min_diff = 999
    max_diff = -999 
    count = 0
    for k in xrange(NUM_SLOT):
        for m in xrange(NUM_MEETING):
            if eams.isInTimeWindows(m,k) > 0:
                oat = float(eams.OAT.values()[k])
                if  oat < float(21):
#                     print "OAT - :",oat
                    diff = 21 - oat
                elif oat > float(23):
#                     print "OAT + :",oat
                    diff = oat - 23
                
                total_diff = total_diff + diff
                    
                if diff < min_diff:
                    min_diff = diff
                if diff > max_diff:
                    max_diff = diff
                        
                count = count + 1
                    
#                 print "[", m, ",", k, "]:", diff           
                break
                
    avg_diff = float(total_diff/count)
#     print "min_diff:", min_diff
#     print "avg_diff:", avg_diff
#     print "max_diff:", max_diff
    
    return [min_diff, avg_diff, max_diff]
       
              
def calcDensity():
    NUM_SLOT = len(eams.TS)-1
    NUM_MEETING = len(eams.ML)
     
    avail_slot = [0] * NUM_SLOT
    required_slot = 0
     
    for m in xrange(NUM_MEETING):
        required_slot = required_slot + eams.ML[m].Duration
        for k in xrange(NUM_SLOT):    
            if eams.isInTimeWindows(m,k) > 0:
                avail_slot[k] = 1
                 
    eligible_slot = avail_slot.count(1) * len(eams.RL)
    density = (float(required_slot)/eligible_slot)*100
    print "eligible_slot: " + str(eligible_slot)
    print "required_slot: " + str(required_slot)
    print "density: " + str(density)
     
    return density
    

            
            

if __name__ == '__main__':    
    
    enableLog = 1
    eams = EAMS(enableLog)  # activate log within EAMS.
          
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        run_config_file = open(file_location, 'r')
        cfg_data = ''.join(run_config_file.readlines())
        run_config_file.close()        
        
        # Given eams_run_tests.cfg,
        #    cfg_data   -->  a list of test cases to run 
        #    cfg_idx[1] -->  "eams_run_tests"       
        if '/' in file_location:
            cfg_idx = file_location.replace('/',' ').replace('.',' ').split()
        else:
            cfg_idx = file_location.replace('\\',' ').replace('.',' ').split()  
        
        run_it(cfg_data, cfg_idx[1])      
        
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python run.py ./Input/eams.cfg)'
        