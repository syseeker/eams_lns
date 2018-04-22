import sys

from solver_lns import Solver_LNS

def run_it(cfg_data, runcfg):
    
#    cfg_data   -->  number of test cases in line[0], follow by a list of test cases to run 
    cfg = cfg_data.split('\n')
    count = cfg[0].split()
    runCount = int(count[0])
    lnsOptTypeCount = int(count[1])
    
    lns_solver = Solver_LNS()
    
    for i in range(1, runCount+1):        
        if not cfg[i]:
            sys.exit("Invalid run... No config file exists.")
        
        for j in xrange(lnsOptTypeCount):  # For each optimization configuration, loop the same test config
            # as EAMS.ML is shuffled to randomize input sequence, only run EAMS once to ensure the same meeting list is used for all LNS config. 
            #    Also to reduce computational time by loading EAMS just once.
            if j==0: 
                reloadEAMS = 1   # load EAMS only on first LNS OPT config
                lns_solver.init_run(runcfg, cfg[i], j, reloadEAMS)
            else:
                reloadEAMS = 0
                lns_solver.init_run(runcfg, cfg[i], j, reloadEAMS)
                 
            lns_solver.run()        
#             lns_solver.log_schedule()   # Option 1: Note: call this for schedule only model.
#             lns_solver.log_hvac()       # Option 2: Note: call this only if HVAC model is run.
            lns_solver.log_all()        # Option 3: Note: call this only if schedule + HVAC model is run.
             

if __name__ == '__main__':    
          
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
        