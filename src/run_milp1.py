import sys
from eams import EAMS
from solver_milp import Solver_MILP


def run_it(cfg_data):

    #TODO: Configure this....... everytime...
    MIP_TIMELIMIT_SEC = 7200
    MIP_LOG_CB = 1
               
    if '/' in cfg_data:        
        casecfgid = cfg_data.replace('/',' ').replace('.',' ').split()
    else:
        casecfgid = cfg_data.replace('\\',' ').replace('.',' ').split()  
            
    print "\n\nRunning " + cfg_data + "..."        
    eams.readProblemInstance(cfg_data, enableLog)
            
    milp_solver = Solver_MILP(eams, eams.fn, casecfgid[1], MIP_TIMELIMIT_SEC, MIP_LOG_CB)  # param 2 : sneaky step...
    milp_solver.solve()
     
    milp_solver.logSchedulingResults()    
    milp_solver.logHVACResults()
    milp_solver.logStatistics("milp", casecfgid[1])        
    milp_solver.logEnergy("milp", casecfgid[1])
    milp_solver.logSchedules(casecfgid[1])
    milp_solver.logTemperatures(casecfgid[1])
            

if __name__ == '__main__':    
    
    enableLog = 1
    eams = EAMS(enableLog)  # activate log within EAMS.
          
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        run_it(file_location)      
        
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python run.py ./Input/eams.cfg)'
        