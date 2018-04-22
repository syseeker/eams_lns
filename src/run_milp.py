import sys
from eams import EAMS
from solver_milp import Solver_MILP


def run_it(cfg_data, runcfg):
    
#    cfg_data   -->  number of test cases in line[0], follow by a list of test cases to run 
    cfg = cfg_data.split('\n')
    runCount = int(cfg[0])    
    
    #TODO: Configure this....... everytime...
    MIP_TIMELIMIT_SEC = 259200
    MIP_LOG_CB = 1
    
           
    for i in range(1, runCount+1):        
        if not cfg[i]:
            sys.exit("Invalid run... No config file exists.")
        
        if '/' in cfg[i]:        
            casecfgid = cfg[i].replace('/',' ').replace('.',' ').split()
        else:
            casecfgid = cfg[i].replace('\\',' ').replace('.',' ').split()  
        
        print "\n\nRunning " + cfg[i] + "..."        
        eams.readProblemInstance(cfg[i], enableLog)
                
        milp_solver = Solver_MILP(eams, eams.fn, casecfgid[1], MIP_TIMELIMIT_SEC, MIP_LOG_CB)  # param 2 : sneaky step...
        milp_solver.solve()
         
        milp_solver.logSchedulingResults()    
        milp_solver.logHVACResults()
        milp_solver.logStatistics(runcfg, casecfgid[1])        
        milp_solver.logEnergy(runcfg, casecfgid[1])
        milp_solver.logSchedules(casecfgid[1])
        milp_solver.logTemperatures(casecfgid[1])
            

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
        