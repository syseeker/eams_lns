import sys
from solver_lns import Solver_LNS
import math


def run_it(runcfg, casecfg, MIP_TIMELIMIT_SEC, LNS_TIMELIMIT_SEC, TABU_PERIOD_SEC, 
           MIP_SOLUTION_LIMIT, LNS_NEIGHOURHOOD_ORDER, LNS_ORDER_RANDOMIZE, LNS_EXPLORE_MAX_ITERATION, 
           INIT_SOLTYPE, LNS_MAX_K_DESTROY, LNS_MAX_L_DESTROY, LNS_MAX_M_DESTROY):
    
    lns_solver = Solver_LNS()
    
    lns_solver.init_run_smac(runcfg, casecfg, MIP_TIMELIMIT_SEC, LNS_TIMELIMIT_SEC, TABU_PERIOD_SEC, 
           MIP_SOLUTION_LIMIT, LNS_NEIGHOURHOOD_ORDER, LNS_ORDER_RANDOMIZE, LNS_EXPLORE_MAX_ITERATION, 
           INIT_SOLTYPE, LNS_MAX_K_DESTROY, LNS_MAX_L_DESTROY, LNS_MAX_M_DESTROY)
    
    val = lns_solver.run()      
    lns_solver.log_all()

    # SMAC has a few different output fields; here, we only need the 4th output:    
    print "Result of algorithm run: SUCCESS, 0, 0, %f, 0" % val
    
    

if __name__ == '__main__':    

     
    runcfg = sys.argv[1]
    casecfg = sys.argv[2]
#     cutoff = int(float(sys.argv[3]) + 1)
#     runlength = int(sys.argv[4])
#     seed = int(sys.argv[5])
    
    for i in range(len(sys.argv)-1):  
#         print str(i) + " " + str(sys.argv[i])
        if (sys.argv[i] == '-MIP_TIMELIMIT_SEC'):
            MIP_TIMELIMIT_SEC = float(sys.argv[i+1])
            
        elif(sys.argv[i] == '-LNS_TIMELIMIT_SEC'):
            LNS_TIMELIMIT_SEC = int(float(sys.argv[i+1])) 
              
        elif(sys.argv[i] == '-TABU_PERIOD_SEC'):
            TABU_PERIOD_SEC = int(float(sys.argv[i+1]))  
            
#         elif(sys.argv[i] == '-MIP_SOLUTION_LIMIT'):
            MIP_SOLUTION_LIMIT = -1 #int(float(sys.argv[i+1]))  
            
        elif(sys.argv[i] == '-LNS_NEIGHOURHOOD_ORDER'):
            LNS_NEIGHOURHOOD_ORDER = (sys.argv[i+1]) 
             
        elif(sys.argv[i] == '-LNS_ORDER_RANDOMIZE'):
            LNS_ORDER_RANDOMIZE = int(float(sys.argv[i+1]))  
            
        elif(sys.argv[i] == '-LNS_EXPLORE_MAX_ITERATION'):
            LNS_EXPLORE_MAX_ITERATION = int(float(sys.argv[i+1]))  
            
        elif(sys.argv[i] == '-INIT_SOLTYPE'):
            INIT_SOLTYPE = int(float(sys.argv[i+1]))  
            
        elif(sys.argv[i] == '-LNS_MAX_K_DESTROY'):
            LNS_MAX_K_DESTROY = float(sys.argv[i+1])  
            
        elif(sys.argv[i] == '-LNS_MAX_L_DESTROY'):
            LNS_MAX_L_DESTROY = float(sys.argv[i+1])  
            
        elif(sys.argv[i] == '-LNS_MAX_M_DESTROY'):
            LNS_MAX_M_DESTROY = float(sys.argv[i+1])  
                    
    run_it(runcfg, casecfg, MIP_TIMELIMIT_SEC, LNS_TIMELIMIT_SEC, TABU_PERIOD_SEC, 
           MIP_SOLUTION_LIMIT, LNS_NEIGHOURHOOD_ORDER, LNS_ORDER_RANDOMIZE, LNS_EXPLORE_MAX_ITERATION, 
           INIT_SOLTYPE, LNS_MAX_K_DESTROY, LNS_MAX_L_DESTROY, LNS_MAX_M_DESTROY)      
        
    