import sys
import logging
from random import seed
from solver_lns_dr import Solver_LNS

def run_it(runcfg, casecfg, MIP_TIMELIMIT_SEC, LNS_DESTROY_2_PCT, LNS_DESTROY_3_PCT, LNS_DESTROY_4_PCT, LNS_SEED):
    
    seed(LNS_SEED)    
    lns_solver = Solver_LNS()    
    lns_solver.init_run_smac(runcfg, casecfg, MIP_TIMELIMIT_SEC, LNS_DESTROY_2_PCT, LNS_DESTROY_3_PCT, LNS_DESTROY_4_PCT, LNS_SEED)
    logging.info("Note: random seed is set to %d" %LNS_SEED)    
       
    lns_obj = lns_solver.run()  
    # Run MILP for comparison
    mip_obj = lns_solver.run_milp_withLNSinitSche(7200)      
    lns_solver.log_AlgoStats(lns_obj, mip_obj, LNS_SEED, MIP_TIMELIMIT_SEC, LNS_DESTROY_2_PCT, LNS_DESTROY_3_PCT, LNS_DESTROY_4_PCT)
    
    # SMAC has a few different output fields; here, we only need the 4th output:    
    print "Result of algorithm run: SUCCESS, 0, 0, %f, 0" % lns_obj
    

if __name__ == '__main__':    

     
    runcfg = sys.argv[1]
    casecfg = sys.argv[2]
#     cutoff = int(float(sys.argv[?]) + 1)
#     runlength = int(sys.argv[5])
    LNS_SEED = int(sys.argv[6])
    
    for i in range(len(sys.argv)-1):  
#         print str(i) + " " + str(sys.argv[i])
        if (sys.argv[i] == '-MIP_TIMELIMIT_SEC'):
            MIP_TIMELIMIT_SEC = float(sys.argv[i+1])
            
#         elif(sys.argv[i] == '-LNS_TIMELIMIT_SEC'):
#             LNS_TIMELIMIT_SEC = int(float(sys.argv[i+1])) 
#               
#         elif(sys.argv[i] == '-LNS_DESTROY_MAX_ROOMS'):
#             LNS_DESTROY_MAX_ROOMS = int(sys.argv[i+1])
            
        elif(sys.argv[i] == '-LNS_DESTROY_2_PCT'):
            LNS_DESTROY_2_PCT = float(sys.argv[i+1])
            
        elif(sys.argv[i] == '-LNS_DESTROY_3_PCT'):
            LNS_DESTROY_3_PCT = float(sys.argv[i+1])
            
        elif(sys.argv[i] == '-LNS_DESTROY_4_PCT'):
            LNS_DESTROY_4_PCT = float(sys.argv[i+1])
                    
    run_it(runcfg, casecfg, MIP_TIMELIMIT_SEC, LNS_DESTROY_2_PCT, LNS_DESTROY_3_PCT, LNS_DESTROY_4_PCT, LNS_SEED)      
        
    