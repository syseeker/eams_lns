import sys
import logging
from math import ceil
from time import time
from datetime import datetime
from random import randrange, sample
from configobj import ConfigObj, ConfigObjError, flatten_errors

from eams import EAMS
from solver_milp import Solver_MILP
from solver_error import SOLVER_LNS_Error
from plot_LNS import plot_LNS_graph

class Solver_LNS:
    def __init__(self):        
        self.runcfg = "unknown"
        self.casecfgid = "unknown"
        self.STATUS = ['', 'LOADED', 'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'CUTOFF', 'ITERATION_LIMIT', 'NODE_LIMIT', 'TIME_LIMIT', 'SOLUTION_LIMIT', 'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL']
        self.err = SOLVER_LNS_Error()
        
        # constant
        self.TABU_LOC_ONLY = 0
        self.TABU_TIME_ONLY = 1
        self.TABU_LOC_N_TIME = 2
        self.RANDOMIZE_ORDER = 1
        self.MIP_DEFAULT_NOTIMELIMIT = 1e+100
        
        # variable
        self.INIT_SOLTYPE                       = -1
        self.LNS_TIMELIMIT_SEC                  = -1
        self.LNS_EXPLORE_MAX_ITERATION          = -1     
        self.LNS_NEIGHOURHOOD_ORDER             = []   
        self.NUM_NEIGHBOURHOOD_TYPE             = -1
        self.ACTIVATE_ROLLBACK                  = -1
        self.ACTIVATE_TABU                      = -1
        self.TABU_EXPIRED_TYPE                  = -1
        self.TABU_PERIOD_SEC                    = -1
        self.TABU_CYCLE                         = -1
        
        self.MIP_TIMELIMIT_SEC                  = -1
        self.MIP_LOG_CB                         = 0
        self.MIP_SOLUTION_LIMIT                 = -1
        
        self.LNS_OBJVALUE_EPSILON = 1.0e-06
        
        self._initLogging()
        
    def _lns_critical_err(self, msg):
        logging.critical("===============================")
        logging.critical(msg)
        logging.critical("===============================")
        sys.exit("********************** Critical Error. %s. EAMS LNS exit." %msg)
        
    #===========================================================================
    # Initialization
    #===========================================================================  
    def _initLogging(self):
        # activate log
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
#         self.logger.setLevel(logging.DEBUG)

    def _activateLogFile(self, f):        
        # remove old handler
        for old_handler in self.logger.handlers:
            self.logger.removeHandler(old_handler)             
        # create a handler with the name defined by the variable f
        handler = logging.FileHandler(f)
        # add that handler to the logger
        self.logger.addHandler(handler)
        
    def _getNeighbourhoodOrder(self, idxlist):
        ns = []        
        for i in xrange(len(idxlist)):
            if idxlist[i] == '0':
                ns.append("RANDOM_RANGE_TIME_ONLY")
            elif idxlist[i] == '1':
                ns.append("RANDOM_RANGE_LOCATION_ONLY")
            elif idxlist[i] == '2':
                ns.append("RANDOM_RANGE_TIME_N_LOCATION")
            elif idxlist[i] == '3':
                ns.append("ARBITRARY_MEETING")
            else:
                ns.append("UNKNOWN")                
        return ns
                
    def _loadLNSConfig(self, runcfg, lnscount):
        
        ret = 0
        filename =  "Input/LNS_OPT/" + runcfg + "/lnsopt" + str(lnscount) + ".cfg"        
        try:
            logging.info("Loading LNS optimization config %s" %(filename))
            # Load LNS optimization configuration
            config = ConfigObj(filename, file_error=True)
            self.INIT_SOLTYPE = int(config['INIT_SOLTYPE'])
            self.LNS_TIMELIMIT_SEC = int(config['LNS_TIMELIMIT_SEC'])
            self.LNS_EXPLORE_MAX_ITERATION = int(config['LNS_EXPLORE_MAX_ITERATION'])
            self.LNS_NEIGHOURHOOD_ORDER = self._getNeighbourhoodOrder(list(config['LNS_NEIGHOURHOOD_ORDER']))                        
            self.NUM_NEIGHBOURHOOD_TYPE = len(self.LNS_NEIGHOURHOOD_ORDER)
            if self.NUM_NEIGHBOURHOOD_TYPE > 4:  #TODO: currently max 4 types of neighbourhood only
                raise ValueError("self.NUM_NEIGHBOURHOOD_TYPE=%d, self.LNS_NEIGHOURHOOD_ORDER=%s" %(self.NUM_NEIGHBOURHOOD_TYPE, self.LNS_NEIGHOURHOOD_ORDER))
            
            self.LNS_ORDER_RANDOMIZE = int(config['LNS_ORDER_RANDOMIZE'])
            
            self.ACTIVATE_ROLLBACK = int(config['ACTIVATE_ROLLBACK'])        
            self.ACTIVATE_TABU = int(config['ACTIVATE_TABU'])
            self.TABU_EXPIRED_TYPE = int(config['TABU_EXPIRED_TYPE'])
            self.TABU_PERIOD_SEC = int(config['TABU_PERIOD_SEC']) 
            self.TABU_CYCLE = int(config['TABU_CYCLE'])
            
            self.MIP_TIMELIMIT_SEC = float(config['MIP_TIMELIMIT_SEC'])
            self.MIP_LOG_CB = int(config['MIP_LOG_CB'])
            self.MIP_SOLUTION_LIMIT = -1 #int(config['MIP_SOLUTION_LIMIT'])
            
            self.LNS_MAX_K_DESTROY = float(config['LNS_MAX_K_DESTROY'])
            self.LNS_MAX_L_DESTROY = float(config['LNS_MAX_L_DESTROY'])
            self.LNS_MAX_M_DESTROY = float(config['LNS_MAX_M_DESTROY'])
                        
            logging.info("=====================================================")
            logging.info("    Initialize LNS    ")
            logging.info("=====================================================")
            logging.info("Initial solution type: %d" %(self.INIT_SOLTYPE))
            logging.info("LNS time limit: %d" %(self.LNS_TIMELIMIT_SEC))
            logging.info("MIP time limit: %d" %(self.MIP_TIMELIMIT_SEC))
            logging.info("MIP solution limit: %d" %(self.MIP_SOLUTION_LIMIT))
            logging.info("Neighbourhood order: %s" %(self.LNS_NEIGHOURHOOD_ORDER))
            logging.info("Number of neighbourhood type: %d" %(self.NUM_NEIGHBOURHOOD_TYPE))
            logging.info("Randomize neighbourhood change order?: %d" %(self.LNS_ORDER_RANDOMIZE))
            logging.info("LNS explore max iteration: %d" %(self.LNS_EXPLORE_MAX_ITERATION))
            logging.info("Percent of occupied slot to be destroyed: %g" %(self.LNS_MAX_K_DESTROY))
            logging.info("Percent of occupied location to be destroyed: %g" %(self.LNS_MAX_L_DESTROY))
            logging.info("Percent of occupied meeting to be destroyed: %g" %(self.LNS_MAX_M_DESTROY))
             
        except (ConfigObjError, IOError), e:        
            logging.critical('%s' % (e))
            return self.err.solver_lns_opt_config_not_found()
        except (ValueError), e:
            logging.critical('%s' % (e))            

        return ret        
        
                
                
    #===========================================================================
    # EAMS_LNS  Normal way
    #=========================================================================== 
    
    def init_run(self, runcfg, casecfg, lnscount, reloadEAMS):      
        """Re-initialize every time running new test case"""  
        
        print "\n\nRunning " + casecfg + " with LNS optimization configuration #" + str(lnscount) + "..."  
        
        # Given Input/eams_meeting_m10_04_227000_18_ws.cfg        
        #      caseid : ['Input', 'eams_meeting_m10_04_227000_18_ws', 'cfg']
        if '/' in casecfg:        
            casecfgid = casecfg.replace('/',' ').replace('.',' ').split()
        else:
            casecfgid = casecfg.replace('\\',' ').replace('.',' ').split()  
            
        self.casecfgid = casecfgid[1] + '_OPTCFG_' + str(lnscount)
        self.casecfgid_LNS_stats_only = casecfgid[1]  
        self.runcfg = runcfg
        
        # Activate log file
#         fn = 'Output\EAMS_LNS_' + self.casecfgid + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        fn = 'Output/EAMS_LNS_' + self.casecfgid + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        self._activateLogFile(fn)
                        
        # Load LNS configuration
        ret = self._loadLNSConfig(runcfg, lnscount)
        if ret < 0:
            self._lns_critical_err("Load LNS optimization config failed. %s" %ret)
         
        # Initialize & Read EAMS
        if reloadEAMS:
            enable_log = 0   # do not need to enable log from within EAMS, it has been done by solver_lns ... this param is for solver_milp which need to log eams w/o LNS
            self.eams = EAMS(enable_log)        
            self.eams.readProblemInstance(casecfg, enable_log)
        
        # Initialize MILP
        #     Note: self.MIP_TIMELIMIT_SEC = -1 for initial solution. For subsequent LNS-MIP, updateGurobiParam after getting initial solution
        self.milp_solver = Solver_MILP(self.eams, fn, self.casecfgid, self.MIP_SOLUTION_LIMIT, self.MIP_LOG_CB)   
        
    #===========================================================================
    # EAMS_LNS INIT SMAC
    #===========================================================================
    def init_run_smac(self, runcfg, casecfg, pMIP_TIMELIMIT_SEC, pLNS_TIMELIMIT_SEC, pTABU_PERIOD_SEC, 
           pMIP_SOLUTION_LIMIT, pLNS_NEIGHOURHOOD_ORDER, pLNS_ORDER_RANDOMIZE, pLNS_EXPLORE_MAX_ITERATION, 
           pINIT_SOLTYPE, pLNS_MAX_K_DESTROY, pLNS_MAX_L_DESTROY, pLNS_MAX_M_DESTROY):
        
        # Given Input/eams_meeting_m10_04_227000_18_ws.cfg        
        #      caseid : ['Input', 'eams_meeting_m10_04_227000_18_ws', 'cfg']
        if '/' in casecfg:        
            casecfgid = casecfg.replace('/',' ').replace('.',' ').split()
        else:
            casecfgid = casecfg.replace('\\',' ').replace('.',' ').split()  
            
        self.casecfgid = casecfgid[1] + '_OPTCFG_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        self.casecfgid_LNS_stats_only = casecfgid[1]  
        self.runcfg = runcfg
        
        # Activate log file
        fn = 'Output/EAMS_LNS_' + self.casecfgid
#         fn = 'Output/EAMS_LNS_' + self.casecfgid + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        self._activateLogFile(fn)
                        
        # Load LNS configuration
        self.INIT_SOLTYPE = int(pINIT_SOLTYPE)                       
        self.LNS_TIMELIMIT_SEC = int(pLNS_TIMELIMIT_SEC)                 
        self.LNS_EXPLORE_MAX_ITERATION = int(pLNS_EXPLORE_MAX_ITERATION)  
        print "\n\n\n" + str(pLNS_NEIGHOURHOOD_ORDER)                   
        self.LNS_NEIGHOURHOOD_ORDER = self._getNeighbourhoodOrder(list(pLNS_NEIGHOURHOOD_ORDER))
        self.LNS_ORDER_RANDOMIZE = int(pLNS_ORDER_RANDOMIZE)        
        self.TABU_PERIOD_SEC = int(pTABU_PERIOD_SEC)
        self.MIP_TIMELIMIT_SEC = float(pMIP_TIMELIMIT_SEC)
        self.MIP_SOLUTION_LIMIT = -1 #int(pMIP_SOLUTION_LIMIT)
        self.LNS_MAX_K_DESTROY = float(pLNS_MAX_K_DESTROY)
        self.LNS_MAX_L_DESTROY = float(pLNS_MAX_L_DESTROY)
        self.LNS_MAX_M_DESTROY = float(pLNS_MAX_M_DESTROY)
        
        self.NUM_NEIGHBOURHOOD_TYPE = len(self.LNS_NEIGHOURHOOD_ORDER)                  
        self.ACTIVATE_ROLLBACK = 1  # NOTE: not use.        
        self.ACTIVATE_TABU = 1    
        self.TABU_EXPIRED_TYPE = 0
        self.TABU_CYCLE = 1
        self.MIP_LOG_CB = 0       
                
        logging.info("=====================================================")
        logging.info("    Initialize LNS    ")
        logging.info("=====================================================")
        logging.info("Initial solution type: %d" %(self.INIT_SOLTYPE))
        logging.info("LNS time limit: %d" %(self.LNS_TIMELIMIT_SEC))        
        logging.info("MIP time limit: %d" %(self.MIP_TIMELIMIT_SEC))
        logging.info("MIP solution limit: %d" %(self.MIP_SOLUTION_LIMIT))
        logging.info("Neighbourhood order: %s" %(self.LNS_NEIGHOURHOOD_ORDER))
        logging.info("Number of neighbourhood type: %d" %(self.NUM_NEIGHBOURHOOD_TYPE))
        logging.info("Randomize neighbourhood change order?: %d" %(self.LNS_ORDER_RANDOMIZE))
        logging.info("LNS explore max iteration: %d" %(self.LNS_EXPLORE_MAX_ITERATION))
        logging.info("Percent of occupied slot to be destroyed: %g" %(self.LNS_MAX_K_DESTROY))
        logging.info("Percent of occupied location to be destroyed: %g" %(self.LNS_MAX_L_DESTROY))
        logging.info("Percent of occupied meeting to be destroyed: %g" %(self.LNS_MAX_M_DESTROY))
         
         
        # Initialize & Read EAMS
        enable_log = 0   # do not need to enable log from within EAMS, it has been done by solver_lns ... this param is for solver_milp which need to log eams w/o LNS
        self.eams = EAMS(enable_log)        
        self.eams.readProblemInstance(casecfg, enable_log) # casecfg is the eams config file
         
        # Initialize MILP
        #     Note: self.MIP_TIMELIMIT_SEC = -1 for initial solution. For subsequent LNS-MIP, updateGurobiParam after getting initial solution        
        self.milp_solver = Solver_MILP(self.eams, fn, self.casecfgid, -1, self.MIP_LOG_CB) 
     
        
    def run(self):
        
        # InitializeModel
        self.milp_solver.initModel()
        self.lns_run_count = 0
        self.curr_best_schedule = []
        self.curr_optval = -1
        self.tabulist = {}
        self.tabulist[self.TABU_LOC_ONLY] = {}
        self.tabulist[self.TABU_TIME_ONLY] = {}
        self.tabulist[self.TABU_LOC_N_TIME] = {}                
        # LNS Benchmark
        self.LNS_NS_TYPE = []
        self.LNS_NS_DESTROY = []
        self.LNS_NS_IMPACT = []
        self.LNS_NS_TYPE_POS_IMPACT = [0] * self.NUM_NEIGHBOURHOOD_TYPE
        self.LNS_NS_TYPE_TRIGGER = [0] * self.NUM_NEIGHBOURHOOD_TYPE
        
        # Get initial schedule without HVAC model
            #         self.SCHE_TYPE_ARBITRARY = 0
            #         self.SCHE_TYPE_MIN_ROOM_PER_DAY   = 1
        logging.info("\n\n==================================================================")
        logging.info("\t\t Initial Schedule")
        logging.info("==================================================================")
        
        # Limit the time for MIP to get an initial schedule.
#         self.milp_solver.updateGurobiParam(self.MIP_TIMELIMIT_SEC, self.MIP_SOLUTION_LIMIT)   
        timestart = time()
        logging.info("getInitialSchedule TimeStart: %s" %(timestart))
#         print "\n\n=================================================================="
#         print "\t\t Initial Schedule"
#         print "=================================================================="
        status = self.milp_solver.getInitialSchedule(self.INIT_SOLTYPE) 
        logging.info("getInitialSchedule TimeEnd after: %s s" %(time()-timestart))
        if status == self.STATUS.index('INFEASIBLE'):
            self._lns_critical_err("Failure to find an initial schedule.")
        else:
            logging.info("--------------------------- Initial Schedule ----------------------- ")
#             print "--------------------------- Initial Schedule -----------------------"
            self.log_schedule()
        # Remove MIP time limit to make sure we get a feasible solution with HVAC control.
#         self.milp_solver.updateGurobiParam(self.MIP_DEFAULT_NOTIMELIMIT, self.MIP_SOLUTION_LIMIT)
        
        # Initialize HVAC model & optimize HVAC control based on initial schedule
        timestart = time()
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule TimeStart: %s" %(timestart))        
        self.curr_optval = self.milp_solver.initHVACModelNEnergyObjBasedOnInitialSchedule()  
        self.initsol_schetime = time()-timestart    #TODO: var not used for TIME_LIMIT reset 
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule TimeEnd after: %s s" %(self.initsol_schetime))
        # NOTE: curr_optval returns either INFEASIBLE or initial energy consumption
        if self.curr_optval == self.STATUS.index('INFEASIBLE'):
            self._lns_critical_err("Failure to find HVAC control for the given initial schedule.")
        else:
            self._log_ObjValue_Neighbourhood(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), self.curr_optval, -1)
#             print "+++++++++++++++++++++++++++ Initial optimal value :  ", self.curr_optval
            logging.info("+++++++++++++++++++++++++++ Initial optimal value :  %g" %(self.curr_optval))
            
        # Run LNS
        self.start_t = time()
        curr_t = self.start_t
        self._storeCurrentBestSchedule(self.curr_optval, 1)                                        # TODO: this must be called only if initial FEASIBLE SOLUTION is available
        self.milp_solver.updateGurobiParam(self.MIP_TIMELIMIT_SEC, self.MIP_SOLUTION_LIMIT)     # Update this after initial solution (because we don't want to limit initial solution)
           
        # Run until system time limit is reached
        while curr_t - self.start_t < self.LNS_TIMELIMIT_SEC:            
            # Restart from the first neighbourhood type everytime
            curr_nt = 0
            # Loop until all neighbourhood type is explored
            while curr_nt < self.NUM_NEIGHBOURHOOD_TYPE:                 
                # ExploreNeighbourhood
                new_optval = self.exploreNeighbourhood(self.curr_optval, curr_nt)  
                                              
                # ChangeNeighbourhood (if necessary)
                curr_nt = self.changeNeighbourhood(new_optval, self.curr_optval, curr_nt)
                                                   
                # Prevent infinite loop. 
                # Current implementation of changeNeighbourhood() might lead to infinite loop
                #    when better solution is always found.
                if (time() - self.start_t) > self.LNS_TIMELIMIT_SEC:
                    break
               
            curr_t = time()
#             print "***************************************** Last round solve time from the start time: ", curr_t - self.start_t," sec"
            logging.info("***************************************** Last round solve time from the start time: %g sec" %(curr_t - self.start_t))
                  
        self._log_LNS_stats()
#         plot_LNS_graph(self.casecfgid + '_LNS_trace', self.LNS_NEIGHOURHOOD_ORDER, 0, 2) #4,5

        return self.curr_optval
         
        
    def exploreNeighbourhood(self, optval, nt):
#         print "***************************************** ExploreNeighbourhood nt = ", self.LNS_NEIGHOURHOOD_ORDER[nt]
#         logging.info("***************************************** ExploreNeighbourhood nt =  %s" %(self.LNS_NEIGHOURHOOD_ORDER[nt]))
        
        i = 0
        retval = optval         
        while (retval >= optval) and (i < self.LNS_EXPLORE_MAX_ITERATION):  
            
            logging.info("\n\n==================================================================")
            logging.info("\t\t Explore Neighbourhood Run #%d [%s], ExploreCount %d" %(self.lns_run_count, self.LNS_NEIGHOURHOOD_ORDER[nt], i))
            logging.info("==================================================================")
            
            [locls, timels, mls] = self.shakeNeighbourhood(nt)
            # If all options are tabu-ed, then return to see if we can change neighbourhood type.
            if len(locls) == 0 and len(timels) == 0 and len(mls) == 0:
                # Benchmark LNS impact
                self.LNS_NS_TYPE.append(nt+10)
                self.LNS_NS_DESTROY.append(0)
                self.LNS_NS_IMPACT.append(0)  
                self.LNS_NS_TYPE_TRIGGER[nt] = self.LNS_NS_TYPE_TRIGGER[nt] + 1              
                logging.info("************************* All options are tabued. Stop exploreNeighbourhood.")
                logging.info("+++++++++++++++++++++++++++ Current optimal :  %s" %retval)
                self._log_ObjValue_Neighbourhood(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), retval, nt+10) 
                self.lns_run_count = self.lns_run_count+1               
                break
            
            timestart = time()
            logging.info("solveLNSConstrainedMILP TimeStart: %s" %(timestart))
            newval = self.milp_solver.solveLNSConstrainedMILP(self.lns_run_count, locls, timels, mls)
            logging.info("solveLNSConstrainedMILP TimeEnd after: %s s" %(time()-timestart))            
            if (newval == self.milp_solver.MIP_TIMELIMITREACHED_NOSOLUTION):
                logging.critical("********************************* solveLNSConstrainedMILP() return %g. Time Limit reached without finding a feasible solution." %newval)
                
            
            # checking only...
            logging.info("+++++++++++++++++++++++++++ newval= %g, optval=%g" %(newval, optval))            
            # Benchmark LNS impact
            self.LNS_NS_TYPE.append(nt)
            self.LNS_NS_TYPE_TRIGGER[nt] = self.LNS_NS_TYPE_TRIGGER[nt] + 1
            self.LNS_NS_DESTROY.append(self.milp_solver.NUMVAR_BDV_x_MLK_DESTROY)
            
            if (newval + self.LNS_OBJVALUE_EPSILON) < optval:  
                self.LNS_NS_IMPACT.append(1)                 
                self.LNS_NS_TYPE_POS_IMPACT[nt] = self.LNS_NS_TYPE_POS_IMPACT[nt] + 1
            else:  
                # NOTE: when (newval + self.LNS_OBJVALUE_EPSILON) > optval, no impact, LNS rollback to previous best solution
                #   The retval, that is logged below, is generated by the previous best schedule.
                #   So there is a little inconsistent between Destroy_trace vs. impact graphs 
                self.LNS_NS_IMPACT.append(0)
            
            # TODO: maybe the rollbackPreviousBestSchedule should not be called here, it should be called in in changeNeighbourhood()? 
            #        But the logics in the next few lines need to be changed...
            # only accept newval if ((newval + self.LNS_OBJVALUE_EPSILON) <= optval)
            #    newval |---  LNS_OBJVALUE_EPSILON ----| optval
            logging.info("((newval + self.LNS_OBJVALUE_EPSILON) - optval) %g - %g = %g" %(newval + self.LNS_OBJVALUE_EPSILON, optval, (newval + self.LNS_OBJVALUE_EPSILON - optval)))
            if (newval + self.LNS_OBJVALUE_EPSILON)  <= optval:                
                retval = newval
            else:  
                if (newval == self.milp_solver.MIP_TIMELIMITREACHED_NOSOLUTION):
                    logging.info("TimeLimit reached without getting a solution this round. Rollback.")
                    
                else:             
                    logging.info(" WELL! a (slightly) worse solution is found......expecting newval+eps == optval, or newval+eps <= optval ")
                    logging.info("***************************************** Below is the *worse* schedule")
                    logging.info("worse_schedule = %s" %self.milp_solver.getOccupiedLocationNSlot())
                    
                # As initial HVAC solution is generated without time limit, therefore the rollback should be done w/o too. Otherwise will result in getting infeasible solution.
                if self.is_bestsche_initsol == 1:
                        self.milp_solver.updateGurobiParam(self.MIP_DEFAULT_NOTIMELIMIT, self.MIP_SOLUTION_LIMIT)
                retval = self.milp_solver.rollbackPreviousBestSchedule(self.lns_run_count, self.curr_best_schedule)  # self.initsol_schetime
                # After rollback to initial HVAC solution, reset the MIP time limit.
                if self.is_bestsche_initsol == 1:
                        self.milp_solver.updateGurobiParam(self.MIP_TIMELIMIT_SEC, self.MIP_SOLUTION_LIMIT)

            logging.info("+++++++++++++++++++++++++++ Current optimal :  %s" %retval)
            # Log LNS trace
            self._log_ObjValue_Neighbourhood(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), retval, nt)
                                   
            i = i+1
            self.lns_run_count = self.lns_run_count+1
                        
            #TODO:  also add a time check in this loop??? change start_t to self.start_t
            
        return retval 
    
    def shakeNeighbourhood(self, nt):
        
#         print "***************************************** ShakeNeighbourhood nt = ", self.LNS_NEIGHOURHOOD_ORDER[nt]
#         logging.info("***************************************** ShakeNeighbourhood nt =  %s" %(self.LNS_NEIGHOURHOOD_ORDER[nt]))
#         
        max_l = -1
        max_k = -1
        max_m = -1
        locls = []
        timels = []
        mls = []
        shakels = []  # [locls, timels, mls] contains x=1 to destroyed
        empty_ls = [[], [], []]
        
        # TODO: identify how long it takes to construct optimal solution for max_k, max_l, and tailor max_k, max_l
        # TODO: more method to shake...
        
        if self.ACTIVATE_TABU:
            self._remExpiredTabuList()
        
        if ('RANDOM_RANGE_TIME_ONLY' in self.LNS_NEIGHOURHOOD_ORDER) and (nt == self.LNS_NEIGHOURHOOD_ORDER.index('RANDOM_RANGE_TIME_ONLY')):  
#             print "Shaking based on [RANDOM_RANGE_TIME_ONLY]"
            logging.info("Shaking based on [RANDOM_RANGE_TIME_ONLY]")
              
            occ_k = self.milp_solver.getOccupiedSlot()
            if self.ACTIVATE_TABU:
                occ_k = self._remTabuedOption(self.TABU_TIME_ONLY, occ_k)
                if len(occ_k) == 0: # all options tabu-ed
#                     print "all RANDOM_RANGE_TIME_ONLY option tabued"
                    logging.info("all RANDOM_RANGE_TIME_ONLY option tabued")
                    return empty_ls
            
#             occ_k.sort()
            if self.LNS_MAX_K_DESTROY > 0:                
                idxls = sample(range(len(occ_k)), int(ceil(self.LNS_MAX_K_DESTROY*len(occ_k))))
                logging.info("LNS_MAX_K_DESTROY idxls: %s" %(idxls))
                for i in xrange(len(idxls)):
                    timels.append(occ_k[idxls[i]])
            else:
                start_k = randrange(0, len(occ_k))            
                end_k   = randrange(start_k, len(occ_k))
                timels = occ_k[start_k:end_k+1]
            max_k = len(timels) 
            shakels = [[], timels, []]
            
            if self.ACTIVATE_TABU:
                self._addTabuList(self.TABU_TIME_ONLY, timels)
            
        elif ('RANDOM_RANGE_LOCATION_ONLY' in self.LNS_NEIGHOURHOOD_ORDER) and (nt == self.LNS_NEIGHOURHOOD_ORDER.index('RANDOM_RANGE_LOCATION_ONLY')):   
#             print "Shaking based on [RANDOM_RANGE_LOCATION_ONLY]"
            logging.info("Shaking based on [RANDOM_RANGE_LOCATION_ONLY]")
             
            occ_l = self.milp_solver.getOccupiedLocation()            
            if self.ACTIVATE_TABU:
                occ_l = self._remTabuedOption(self.TABU_LOC_ONLY, occ_l)
                if len(occ_l) == 0: # all options tabu-ed
#                     print "all RANDOM_RANGE_LOCATION_ONLY option tabued"
                    logging.info("all RANDOM_RANGE_LOCATION_ONLY option tabued")
                    return empty_ls            
            
#             occ_l.sort()
            if self.LNS_MAX_L_DESTROY > 0:                
                idxls = sample(range(len(occ_l)), int(ceil(self.LNS_MAX_L_DESTROY*len(occ_l))))
                logging.info("LNS_MAX_L_DESTROY idxls: %s" %(idxls))
                for i in xrange(len(idxls)):
                    locls.append(occ_l[idxls[i]])
            else:     
                start_l = randrange(0, len(occ_l))
                end_l   = randrange(start_l, len(occ_l))
                locls = occ_l[start_l:end_l+1]
            max_l = len(locls) 
            shakels = [locls, [], []]
            
            if self.ACTIVATE_TABU:
                self._addTabuList(self.TABU_LOC_ONLY, locls)
                         
        elif ('RANDOM_RANGE_TIME_N_LOCATION' in self.LNS_NEIGHOURHOOD_ORDER) and (nt == self.LNS_NEIGHOURHOOD_ORDER.index('RANDOM_RANGE_TIME_N_LOCATION')): 
#             print "Shaking based on [RANDOM_RANGE_TIME_N_LOCATION]"
            logging.info("Shaking based on [RANDOM_RANGE_TIME_N_LOCATION]")
              
            occ_k = self.milp_solver.getOccupiedSlot()
            if self.ACTIVATE_TABU:
                occ_k = self._remTabuedOption(self.TABU_TIME_ONLY, occ_k)
            if len(occ_k) != 0:  
#                 occ_k.sort()     
                if self.LNS_MAX_K_DESTROY > 0:                
                    idxls = sample(range(len(occ_k)), int(ceil(self.LNS_MAX_K_DESTROY*len(occ_k))))
                    logging.info("LNS_MAX_K_DESTROY idxls: %s" %(idxls))
                    for i in xrange(len(idxls)):
                        timels.append(occ_k[idxls[i]])
                else:       
                    start_k = randrange(0, len(occ_k))
                    end_k   = randrange(start_k, len(occ_k))
                    timels = occ_k[start_k:end_k+1]
                max_k = len(timels) 
                self._addTabuList(self.TABU_TIME_ONLY, timels)
            
            occ_l = self.milp_solver.getOccupiedLocation()
            if self.ACTIVATE_TABU:
                occ_l = self._remTabuedOption(self.TABU_LOC_ONLY, occ_l)
            if len(occ_l) != 0:
#                 occ_l.sort()  
                if self.LNS_MAX_L_DESTROY > 0:                
                    idxls = sample(range(len(occ_l)), int(ceil(self.LNS_MAX_L_DESTROY*len(occ_l))))
                    logging.info("LNS_MAX_L_DESTROY idxls: %s" %(idxls))
                    for i in xrange(len(idxls)):
                        locls.append(occ_l[idxls[i]])
                else:             
                    start_l = randrange(0, len(occ_l))
                    end_l   = randrange(start_l, len(occ_l))
                    locls = occ_l[start_l:end_l+1]
                max_l = len(locls)
                self._addTabuList(self.TABU_LOC_ONLY, locls) # a little bit delayed for expiration time in time-based tabu list
        
            if self.ACTIVATE_TABU:
                if len(occ_l) == 0 and len(occ_k) == 0:
#                     print "all RANDOM_RANGE_TIME_N_LOCATION option tabued"
                    logging.info("all RANDOM_RANGE_TIME_N_LOCATION option tabued")
                    return empty_ls
            
            shakels = [locls, timels, []]
            
        elif ('ARBITRARY_MEETING' in self.LNS_NEIGHOURHOOD_ORDER) and (nt == self.LNS_NEIGHOURHOOD_ORDER.index('ARBITRARY_MEETING')):   
#             print "Shaking based on [ARBITRARY_MEETING]"
            logging.info("Shaking based on [ARBITRARY_MEETING]")            
            
            occ_m = self.milp_solver.getOccupiedLocationNSlot()
            if self.ACTIVATE_TABU:
                occ_m = self._remTabuedOption(self.TABU_LOC_N_TIME, occ_m)
                if len(occ_m) == 0: # all options tabu-ed
#                     print "all ARBITRARY_MEETING option tabued"
                    logging.info("all ARBITRARY_MEETING option tabued")
                    return empty_ls
            
#             occ_m.sort()    
            if self.LNS_MAX_M_DESTROY > 0:                
                idxls = sample(range(len(occ_m)), int(ceil(self.LNS_MAX_M_DESTROY*len(occ_m))))
                logging.info("LNS_MAX_M_DESTROY idxls: %s" %(idxls))
                for i in xrange(len(idxls)):
                    mls.append(occ_m[idxls[i]])
            else:           
                start_m = randrange(0, len(occ_m))
                end_m   = randrange(start_m, len(occ_m))
                mls = occ_m[start_m:end_m+1]
            max_m = len(mls) 
            shakels = [[], [], mls]    
            
            if self.ACTIVATE_TABU:   
                self._addTabuList(self.TABU_LOC_N_TIME, mls)
            
        else:
            logging.error("Unknown neighbourhood type %d" %nt)
        
        logging.info("Destroying meeting schedule based on [%s] in ([%d] location %s  and  [%d] time %s) or in [%d] meeting %s" %(self.LNS_NEIGHOURHOOD_ORDER[nt], max_l, locls, max_k, timels, max_m, mls))
#         print "******************************** Destroying meeting schedule based on [", self.LNS_NEIGHOURHOOD_ORDER[nt], "] in (", max_l, " location:", locls,  " and ", max_k, " time:", timels, ") or (", max_m, " meeting:", mls
        
        return shakels
        
        
    def changeNeighbourhood(self, new_optval, curr_optval, curr_nt):

        logging.info("***************************************** ChangeNeighbourhood")
        logging.info("new_optval + LNS_OBJVALUE_EPSILON - curr_optval, %g + %g - %g = %g" %(new_optval, self.LNS_OBJVALUE_EPSILON, curr_optval, new_optval+self.LNS_OBJVALUE_EPSILON-curr_optval))
        
        
        if (new_optval + self.LNS_OBJVALUE_EPSILON)  <= curr_optval:    # new neighbourhood performs better than (or as good as) old neighbourhood
            logging.info("***************************************** new_optval+self.LNS_OBJVALUE_EPSILON <= curr_optval, better or equal solution found. _storeCurrentBestSchedule.")
            # store latest best schedule (which achieve new_optval)            
            self._storeCurrentBestSchedule(new_optval, 0)
        else:
            logging.info("***************************************** new_optval+self.LNS_OBJVALUE_EPSILON > curr_optval, no better solution found. No update for CurrentBestSchedule.")   
            
            
        if self.LNS_ORDER_RANDOMIZE == self.RANDOMIZE_ORDER:
            nt = randrange(0, self.NUM_NEIGHBOURHOOD_TYPE)
            logging.info("********* Randomly changeNeighbourhood to = %s" %(self.LNS_NEIGHOURHOOD_ORDER[nt]))
            return nt
        else:
            if (new_optval + self.LNS_OBJVALUE_EPSILON)  <= curr_optval:
                # restart from first neighbourhood
                # TODO: really?  Or do not change neighbourhood??? return curr_nt ??
                logging.info("***************************************** changeNeighbourhood to %s" %(self.LNS_NEIGHOURHOOD_ORDER[0]))
                return 0       
            else: # TODO: since you rollback to previousBestSolution in exploreNeighbourhood, this will never happen
                logging.info("***************************************** new_optval > curr_optval, no better solution found. ")   
                # try with next structure
                # TODO: what about s+step?
                return curr_nt + 1    
        
    #===========================================================================
    # Log & Tabu
    #===========================================================================     
                                      
    def _storeCurrentBestSchedule(self, optval, isinitsol):        
        self.curr_best_from_start_t = time() - self.start_t
        self.curr_optval = optval
        self.is_bestsche_initsol = isinitsol
                        
        logging.info("***************************************** Below is the latest schedule")
        self.curr_best_schedule = self.milp_solver.getOccupiedLocationNSlot()
        
#         print "***************************************** storeCurrentBestSchedule - objval:",  self.curr_optval, " - found at ", self.curr_best_from_start_t, "s"
        logging.info("***************************************** storeCurrentBestSchedule - objval: %g - found at %g s" %(self.curr_optval, self.curr_best_from_start_t))
        logging.info("curr_best_schedule = %s" %self.curr_best_schedule)
        
    def _remTabuedOption(self, lstype, candidatels):
#         print "******************* candidatels =", candidatels
        logging.info("******************* candidatels = %s" %(candidatels))     
           
        tabuls = self._getTabuList(lstype)
#         print "tabuls=", tabuls
        logging.info("tabuls=%s" %tabuls)
        ls = [x for x in candidatels if x not in tabuls]
#         print "******************* candidatels after removing tabu-ed option =", ls
        logging.info("******************* candidatels after removing tabu-ed option = %s" %(ls))
        return ls
    
    def _getTabuList(self, lstype):
        tabu = []
        val = self.tabulist[lstype]
        for v in val.itervalues():
            if v not in tabu:
                tabu.extend(v)                
        return tabu    
    
    def _addTabuList(self, lstype, tabuls):
        
        if self.TABU_EXPIRED_TYPE == 0:    # 0: time-based, 1: cycle-based
            tabu_key = time()
        else:
            tabu_key = self.lns_run_count
                        
        # add new tabu list
        if not self.tabulist.get(lstype):
            self.tabulist[lstype] = {tabu_key:tabuls}
        elif self.tabulist[lstype].get(tabu_key):
            self.tabulist[lstype].get(tabu_key).extend(tabuls)
        else:
            self.tabulist[lstype].update({tabu_key: tabuls})
       
#         print "updated tabulist:", self.tabulist
        logging.info("updated  tabulist: %s" %(self.tabulist))
        
        
    def _remExpiredTabuList(self):
        
        if self.TABU_EXPIRED_TYPE == 0:    # 0: time-based, 1: cycle-based
            tabu_key = time() 
            expire_limit = self.TABU_PERIOD_SEC 
        else:
            tabu_key = self.lns_run_count
            expire_limit = self.TABU_CYCLE
        
        # remove expired tabu list
        expls = []
        for k, v in self.tabulist.iteritems():        
            for tk, _ in v.iteritems():            
                if (tabu_key - tk) > expire_limit:
                    expls.append([k, tk])
    
#         print "expls:", expls
        logging.info("expls: %s" %(expls))
        
        for i in xrange(len(expls)):
            [k,tk] = expls[i]
            del self.tabulist[k][tk]
            
#         print "after removing expired tabulist: ", self.tabulist
        logging.info("after removing expired tabulist: %s" %(self.tabulist))
        
   
        
    #===========================================================================
    # Diagnose
    #=========================================================================== 
    def _log_ObjValue_Neighbourhood(self, logtime, objvalue, nt):
        data = [logtime, objvalue, nt]
        try:
#             fstr = 'Output\\' + self.casecfgid + '_LNS_trace'
            fstr = 'Output/' + self.casecfgid + '_LNS_trace'
            f = open(fstr,'a')
            f.write(",".join(map(str, data)))            
            f.write("\n")
            f.close()    
        except (ValueError), e:
            logging.critical('%s' % (e))    
    
    def _log_LNS_stats(self):      
        
        # Number of time a neighbourhood is being triggered vs. effectively reduce energy consumption
        # Offset of neighbourhood follows their NEIGHBOURHOOD ORDER
        logging.info("LNS_NS_TYPE_TRIGGER: %s" %self.LNS_NS_TYPE_TRIGGER)
        logging.info("LNS_NS_TYPE_POS_IMPACT: %s" %self.LNS_NS_TYPE_POS_IMPACT)
        
        # Total number of BDV_x_MLK vs number of this variable is being destroyed in each round
        #  Offset of LNS_NS_DESTROY represents each round of LNS
        logging.info("Total BDV_x_MLK : %d" %(self.milp_solver.NUMVAR_BDV_x_MLK))
        logging.info("LNS_NS_DESTROY: %s" %self.LNS_NS_DESTROY)
        
        # Neighbourhood triggered in each round vs. their impact (0: optval equal or more, 1: better solution found)
        logging.info("LNS_NS_TYPE: %s" %self.LNS_NS_TYPE)        
        logging.info("LNS_NS_IMPACT: %s" %self.LNS_NS_IMPACT)  
        
#         header = ["LNS_NEIGHOURHOOD_ORDER", "LNS_NS_TYPE_TRIGGER", "LNS_NS_TYPE_POS_IMPACT", "NUMVAR_BDV_x_MLK", "LNS_NS_DESTROY", "LNS_NS_TYPE", "LNS_NS_IMPACT", "curr_optval", "curr_best_from_start_t"]
        data = [self.casecfgid, self.LNS_NEIGHOURHOOD_ORDER, self.LNS_NS_TYPE_TRIGGER, self.LNS_NS_TYPE_POS_IMPACT, self.milp_solver.NUMVAR_BDV_x_MLK, self.LNS_NS_DESTROY, self.LNS_NS_TYPE, self.LNS_NS_IMPACT, self.curr_optval, self.curr_best_from_start_t]        
#         data = [self.LNS_NEIGHOURHOOD_ORDER, self.curr_optval, self.curr_best_from_start_t]        
        try:            
            # Write to stats file
#             fstr = 'Output\\' + self.casecfgid_LNS_stats_only + '_LNS_stats'
            fstr = 'Output/' + self.casecfgid_LNS_stats_only + '_LNS_stats'
            f = open(fstr,'a')
#             f.write(" # ".join(map(str, header)))
            f.write(" # ".join(map(str, data)))            
            f.write("\n")
            f.close()    
            
            # For simplicity, also write to trace file
            fstr = 'Output/' + self.casecfgid + '_LNS_trace'
            f = open(fstr,'a')
            f.write(" # ".join(map(str, data)))            
            f.write("\n")
            f.close()    
            
        except (ValueError), e:
            logging.critical('%s' % (e))    
    
    def log_schedule(self):
        logging.info("------------------------- Scheduling -----------------------")
        self.milp_solver.logSchedulingResults()    
        
    def log_hvac(self):
        logging.info("------------------------- HVAC Control -----------------------")
        self.milp_solver.logHVACResults()
        
    def log_all(self):        
        logging.info("------------------------- Scheduling & HVAC Results -----------------------")
        self.milp_solver.logSchedulingResults()    
        self.milp_solver.logHVACResults()
        self.milp_solver.logStatistics(self.runcfg, self.casecfgid)        
        self.milp_solver.logEnergy(self.runcfg, self.casecfgid)
        self.milp_solver.logSchedules(self.casecfgid)
        self.milp_solver.logTemperatures(self.casecfgid)
        
    
        