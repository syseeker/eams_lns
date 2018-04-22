import sys
import logging
from math import ceil
from time import time
from datetime import datetime
from random import randrange, sample, uniform
from configobj import ConfigObj, ConfigObjError

from eams import EAMS
from solver_milp_dr import Solver_MILP
from solver_error import SOLVER_LNS_Error

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
        self.MIP_DEFAULT_NOTIMELIMIT = 1e+100
        self.LOG_LNS_EAMS = 0  # turn this off to save more time for LNS operation!
        
        # variable
        self.INIT_SOLTYPE                       = -1
        self.LNS_TIMELIMIT_SEC                  = -1
        self.MIP_TIMELIMIT_SEC                  = -1
        self.MIP_LOG_CB                         = 0
        self.LNS_DESTROY_2_PCT                  = 0
        self.LNS_DESTROY_3_PCT                  = 0
                
        self.ACTIVATE_TABU                      = -1
        self.TABU_EXPIRED_TYPE                  = -1
        self.TABU_PERIOD_SEC                    = -1
        self.TABU_CYCLE                         = -1
        
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
        
    def _loadLNSConfig(self, runcfg, lnscount):
        
        ret = 0
        filename =  "Input/LNS_OPT/" + runcfg + "/lnsopt" + str(lnscount) + ".cfg"        
        try:
            logging.info("Loading LNS optimization config %s" %(filename))
            # Load LNS optimization configuration
            config = ConfigObj(filename, file_error=True)
            self.INIT_SOLTYPE = int(config['INIT_SOLTYPE'])
            self.LNS_TIMELIMIT_SEC = 60    #int(config['LNS_TIMELIMIT_SEC'])
            self.MIP_TIMELIMIT_SEC = float(config['MIP_TIMELIMIT_SEC'])
            self.MIP_LOG_CB = int(config['MIP_LOG_CB'])
            
            self.LNS_DESTROY_2_PCT = float(config['LNS_DESTROY_2_PCT'])
            self.LNS_DESTROY_3_PCT = float(config['LNS_DESTROY_3_PCT'])
            self.LNS_DESTROY_4_PCT = float(config['LNS_DESTROY_4_PCT'])
            self._calcRoomDestroyDist()
                    
            self.ACTIVATE_TABU = int(config['ACTIVATE_TABU'])
            self.TABU_EXPIRED_TYPE = int(config['TABU_EXPIRED_TYPE'])
            self.TABU_PERIOD_SEC = int(config['TABU_PERIOD_SEC']) 
            self.TABU_CYCLE = int(config['TABU_CYCLE'])
            
            self.LNS_DESTROY_MAX_ROOMS = int(config['LNS_DESTROY_MAX_ROOMS'])
            self.LNS_DESTROY_MAX_MEETINGS = int(config['LNS_DESTROY_MAX_MEETINGS'])
                        
            logging.info("=====================================================")
            logging.info("    Initialize LNS    ")
            logging.info("=====================================================")
            logging.info("Initial solution type: %d" %(self.INIT_SOLTYPE))
            logging.info("LNS time limit: %d" %(self.LNS_TIMELIMIT_SEC))
            logging.info("MIP time limit: %d" %(self.MIP_TIMELIMIT_SEC))
            logging.info("LNS Destroy 2 rooms probability: %f - %g" %(self.LNS_DESTROY_2_PCT, self.LNS_DESTROY_2_PCT_PRIME))
            logging.info("LNS Destroy 3 rooms probability: %f - %g" %(self.LNS_DESTROY_3_PCT, self.LNS_DESTROY_3_PCT_PRIME))
            logging.info("LNS Destroy 4 rooms probability: %f - %g" %(self.LNS_DESTROY_4_PCT, 1-(self.LNS_DESTROY_2_PCT_PRIME+self.LNS_DESTROY_3_PCT_PRIME)))
#             logging.info("LNS destroy up to max: %d rooms" %(self.LNS_DESTROY_MAX_ROOMS))
#             logging.info("LNS destroy up to max: %d meetings" %(self.LNS_DESTROY_MAX_MEETINGS))
                         
        except (ConfigObjError, IOError), e:        
            logging.critical('%s' % (e))
            return self.err.solver_lns_opt_config_not_found()
        except (ValueError), e:
            logging.critical('%s' % (e))            

        return ret        
        
        
    #===========================================================================
    # EAMS_LNS  Normal way
    #=========================================================================== 
    
    def init_run(self, runcfg, casecfg, lnscount, reloadEAMS, LNS_SEED):      
        """Re-initialize every time running new test case"""  
        
        print "\n\nRunning " + casecfg + " with LNS optimization configuration #" + str(lnscount) + "..."  
        
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
        self.milp_solver = Solver_MILP(self.eams, fn, self.casecfgid, -1, self.MIP_LOG_CB, LNS_SEED)   
        
    #===========================================================================
    # EAMS_LNS INIT SMAC
    #===========================================================================
    def init_run_smac(self, runcfg, casecfg, pMIP_TIMELIMIT_SEC, pLNS_DESTROY_2_PCT, pLNS_DESTROY_3_PCT, pLNS_DESTROY_4_PCT, LNS_SEED):
        
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
        self._activateLogFile(fn)
                        
        # Load LNS configuration from SMAC
        self.MIP_TIMELIMIT_SEC = float(pMIP_TIMELIMIT_SEC)        
        self.LNS_DESTROY_2_PCT = float(pLNS_DESTROY_2_PCT)
        self.LNS_DESTROY_3_PCT = float(pLNS_DESTROY_3_PCT)
        self.LNS_DESTROY_4_PCT = float(pLNS_DESTROY_4_PCT)        
        self._calcRoomDestroyDist()
                               
        # Constant for SMAC version
        self.LNS_TIMELIMIT_SEC = 900 #900 #900 #120 #int(pLNS_TIMELIMIT_SEC)
        self.INIT_SOLTYPE = 1        
        self.MIP_LOG_CB = 0
                # Below not used..        
        self.LNS_DESTROY_MAX_ROOMS = 2
        self.ACTIVATE_TABU = 0
        self.TABU_EXPIRED_TYPE = 1
        self.TABU_PERIOD_SEC = 15 
        self.TABU_CYCLE = 1
        self.LNS_DESTROY_MAX_MEETINGS = 10
                    
        logging.info("=====================================================")
        logging.info("    Initialize LNS    ")
        logging.info("=====================================================")
        logging.info("Initial solution type: %d" %(self.INIT_SOLTYPE))
        logging.info("LNS time limit: %d" %(self.LNS_TIMELIMIT_SEC))
        logging.info("MIP time limit: %d" %(self.MIP_TIMELIMIT_SEC))
        logging.info("LNS Destroy 2 rooms probability: %f - %g" %(self.LNS_DESTROY_2_PCT, self.LNS_DESTROY_2_PCT_PRIME))
        logging.info("LNS Destroy 3 rooms probability: %f - %g" %(self.LNS_DESTROY_3_PCT, self.LNS_DESTROY_3_PCT_PRIME))
        logging.info("LNS Destroy 4 rooms probability: %f - %g" %(self.LNS_DESTROY_4_PCT, 1-(self.LNS_DESTROY_2_PCT_PRIME+self.LNS_DESTROY_3_PCT_PRIME)))
#         logging.info("LNS destroy up to max: %d rooms" %(self.LNS_DESTROY_MAX_ROOMS))
#         logging.info("LNS destroy up to max: %d meetings" %(self.LNS_DESTROY_MAX_MEETINGS))   
                
        # Initialize & Read EAMS
        enable_log = 0   # do not need to enable log from within EAMS, it has been done by solver_lns ... this param is for solver_milp which need to log eams w/o LNS
        self.eams = EAMS(enable_log)        
        self.eams.readProblemInstance(casecfg, enable_log) # casecfg is the eams config file
         
        # Initialize MILP
        #     Note: self.MIP_TIMELIMIT_SEC = -1 for initial solution. For subsequent LNS-MIP, updateGurobiParam after getting initial solution        
        self.milp_solver = Solver_MILP(self.eams, fn, self.casecfgid, -1, self.MIP_LOG_CB, LNS_SEED) 
        
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
           
        self.NUM_DESTROY_PER_ROOM = [0] * len(self.eams.RL)
        self.NUM_ROOM_DESTROYED_PER_ROUND = []
        self.NUM_MEETING_DESTROY_PER_ROUND = []
        
        # Get initial schedule without HVAC model
            #         self.SCHE_TYPE_ARBITRARY = 0
            #         self.SCHE_TYPE_MIN_ROOM_PER_DAY   = 1
        start = time()
        logging.info("\n\n==================================================================")
        logging.info("\t\t Initial Schedule")
        logging.info("==================================================================")
        # set different time limit for different size of meeting type
            # Limit IP to 10s to avoid wasteful B&B. Best data is received ard 10s. (self.MIP_TIMELIMIT_SEC which is <10s is too short)
        if len(self.eams.MTYPE) > 300:
            self.milp_solver.updateGurobiParam(40)
        elif len(self.eams.MTYPE) > 100:
            self.milp_solver.updateGurobiParam(20)
        else:
            self.milp_solver.updateGurobiParam(10)
              
        timestart = time()
        logging.info("getInitialSchedule TimeStart: %s" %(timestart))
        status = self.milp_solver.getInitialSchedule(self.INIT_SOLTYPE) 
        logging.info("getInitialSchedule TimeEnd after: %s s" %(time()-timestart))
        if status == self.STATUS.index('INFEASIBLE'):
            self._lns_critical_err("Failure to find an initial schedule.")
        else:
            self.log_schedule()   
            
        # Limit the time to get HVAC control 
        if len(self.eams.MTYPE) > 100:
            self.milp_solver.updateGurobiParam(300)
        else:
            self.milp_solver.updateGurobiParam(self.MIP_DEFAULT_NOTIMELIMIT)  # Reset MIP_TIMELIMIT_SEC to default
        
        # Initialize HVAC model & optimize HVAC control based on initial schedule
        logging.info("\n\n==================================================================")
        logging.info("\t\t HVAC Control for Initial Schedule")
        logging.info("==================================================================")
        timestart = time()
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule TimeStart: %s" %(timestart))        
        self.curr_optval = self.milp_solver.initHVACModelNEnergyObjBasedOnInitialSchedule()  
        self.initsol_schetime = time()-timestart     
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule TimeEnd after: %s s" %(self.initsol_schetime))        
        if self.curr_optval == self.STATUS.index('INFEASIBLE'):
            self._lns_critical_err("Failure to find HVAC control for the given initial schedule.")
        else:
#             self._log_ObjValue_Neighbourhood(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), self.curr_optval, -1)
            logging.info("++++++++ OBJVALUE ++++++++ Initial optimal value :  %g" %(self.curr_optval))
            self._log_ObjValue_Neighbourhood(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), self.curr_optval, -1)
            self.log_hvac()
            self.milp_solver.logXW(self.casecfgid)
        
# # # #         self.milp_solver.updateGurobiParam(self.MIP_TIMELIMIT_SEC)    # Update this after initial solution (because we don't want to limit initial solution)
# # # #         self.start_t = time()
# # # #         curr_t = self.start_t
# # # #         # Run until system time limit is reached
# # # #         while curr_t - self.start_t < self.LNS_TIMELIMIT_SEC:  
# # # #             logging.info("\n\n==================================================================")
# # # #             logging.info("\t\t Destroy Neighbourhood Run #%d" %(self.lns_run_count))
# # # #             logging.info("==================================================================")
# # # #             timestart = time()
# # # #             [locls, timels, mls] = self._destroyNeighbourhood()
# # # #               
# # # #             logging.info("\n\n==================================================================")
# # # #             logging.info("\t\t Rebuild Neighbourhood")
# # # #             logging.info("==================================================================")
# # # #             objval_partial = self.milp_solver.rebuildNeighbourhood(self.lns_run_count, locls, timels, mls)
# # # #             self.NUM_MEETING_DESTROY_PER_ROUND.append(len(self.milp_solver.CURR_DESTROY_MEETINGS))
# # # #             if (objval_partial < 0):  # NOTE: no destroy made or no feasible result for this round...
# # # #                 self.lns_run_count = self.lns_run_count+1   
# # # #                 continue
# # # #      
# # # #             logging.info("\n\n==================================================================")
# # # #             logging.info("\t\t Evaluate Neighbourhood")
# # # #             logging.info("==================================================================")
# # # #             status = self._evaluateNeighbourhood(locls, objval_partial)
# # # #             self._log_ObjValue_Neighbourhood(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), self.curr_optval, 0)
# # # #             if status > 0:
# # # #                 logging.info("\n\n==================================================================")
# # # #                 logging.info("\t\t Update Neighbourhood")
# # # #                 logging.info("==================================================================")
# # # #                 self._updateNeighbourhood(self.lns_run_count)
# # # #               
# # # #             if (time() - self.start_t) > self.LNS_TIMELIMIT_SEC:
# # # #                 break
# # # #              
# # # #             curr_t = time()
# # # #             logging.info("Last round solve time from the start time: %g sec" %(curr_t - self.start_t))
# # # #                
# # # #             self.lns_run_count = self.lns_run_count+1    
# # # #               
# # # #         end = time()-start
# # # #         logging.info("\n\n==================================================================")
# # # #         logging.info("\t\t Summary")
# # # #         logging.info("==================================================================")
# # # #         logging.info("Total LNS runtime: %g s" %end)
# # # #         logging.info("Statistics of destroy per room: %s" %(self.NUM_DESTROY_PER_ROOM))
# # # #         logging.info("Number of room destroyed per round: %s" %(self.NUM_ROOM_DESTROYED_PER_ROUND))
# # # #         logging.info("Number of meeting destroyed per round: %s" %(self.NUM_MEETING_DESTROY_PER_ROUND))
# # # #         self.log_DRStats()
# # # #         self.log_all()
        
        return self.curr_optval
                  
    #===========================================================================
    # LNS Evaluate
    #===========================================================================
    def _evaluateNeighbourhood(self, locls, newobj):
        rooms = set(range(0, len(self.eams.RL))).difference(locls) 
        e_nodr = self.milp_solver.getEnergyConsumption(rooms)
#         e_dr = self.milp_solver.getEnergyConsumption(locls) # TODO: this one no need, just use self.curr_optval
#         e_dr_new = self.milp_solver.getEnergyConsumption_DRonly() #TODO: no need, just get from partial_objval
#         logging.info("e_nodr=%g, e_dr=%g, old:%g, self.curr_optval:%g; e_dr_new=%g, new:%g" %(e_nodr, self.curr_optval, e_nodr+self.curr_optval, self.curr_optval, newobj, e_nodr+newobj))
        
        if (e_nodr + newobj) < (self.curr_optval): # found a better solution
            self.curr_optval = e_nodr + newobj
            logging.info("++++++++ OBJVALUE ++++++++ New optimal value with (%g + %g) :  %g. Accept" %(e_nodr, newobj, self.curr_optval))
#             print "++++++++ OBJVALUE ++++++++ New optimal value : "+ str(self.curr_optval) +". Accept"
            return 1
        else:
            logging.info("++++++++ OBJVALUE ++++++++ No better solution found with (%g + %g) =    %g (>= %g). Reject." %(e_nodr, newobj, e_nodr + newobj, self.curr_optval))
#             print "++++++++ OBJVALUE ++++++++ No better solution found with ("+str(e_nodr)+"+"+str(newobj)+")="+str(e_nodr + newobj)+" (>= "+str(self.curr_optval)+"). Reject."
            return -1
        
    def _updateNeighbourhood(self, runidx):
        self.milp_solver.updateNeighbourhood(runidx)
        
        if self.LOG_LNS_EAMS:
            self.log_schedule() 
            self.log_hvac()  
        
    #===========================================================================
    # LNS Destroy
    #===========================================================================
    def _destroyNeighbourhood(self):
        
        locls = []
        timels = []
        mls = []
        
        self.LNS_DESTROY_MAX_ROOMS = self._getNumRoomToDestroy()
        locls = self._selectArbitraryRoom()
        
        if len(locls) == 0:
            logging.info("All options are tabued. Reset tabu list?")
        else:
            for i in xrange(len(locls)):
                rid = locls[i]
                self.NUM_DESTROY_PER_ROOM[rid] = self.NUM_DESTROY_PER_ROOM[rid] + 1 
        
        return [locls, timels, mls]
        

    def _calcRoomDestroyDist(self):    
        self.LNS_DESTROY_2_PCT_PRIME = self.LNS_DESTROY_2_PCT / (self.LNS_DESTROY_2_PCT + self.LNS_DESTROY_3_PCT + self.LNS_DESTROY_4_PCT)
        self.LNS_DESTROY_3_PCT_PRIME = self.LNS_DESTROY_3_PCT / (self.LNS_DESTROY_2_PCT + self.LNS_DESTROY_3_PCT + self.LNS_DESTROY_4_PCT)
        
    def _getNumRoomToDestroy(self):
        
        num_rooms = 0
        a = uniform(0,1)  # generate random floating number from uniform distribution
        
        if a <= self.LNS_DESTROY_2_PCT_PRIME:
            num_rooms = 2
        elif a <= (self.LNS_DESTROY_2_PCT_PRIME + self.LNS_DESTROY_3_PCT_PRIME):
            num_rooms = 3
        else:
            num_rooms = 4
        logging.info("Randomly generated %g, destroy %d rooms" %(a, num_rooms))
        
        self.NUM_ROOM_DESTROYED_PER_ROUND.append(num_rooms) 
        return num_rooms
        
    def _selectArbitraryRoom(self):
        
        empty_ls = []
        
        if self.ACTIVATE_TABU:
            self._remExpiredTabuList()
            
        NUM_ROOM = len(self.eams.RL)
        
        if self.ACTIVATE_TABU:
            locls = self._remTabuedOption(self.TABU_LOC_ONLY, range(0, NUM_ROOM))
            if len(locls) == 0: # all options tabu-ed
                logging.info("all LOCATION option tabued")
                return empty_ls
        else:
            locls = xrange(0, NUM_ROOM)
        
        locls = sample(locls, self.LNS_DESTROY_MAX_ROOMS)        
        num_l = len(locls) 
                    
        if self.ACTIVATE_TABU:
            self._addTabuList(self.TABU_LOC_ONLY, locls)
            
        logging.info("Destroying meeting schedule in ( <%d> locations %s )" %(num_l, locls))
        
        return locls
        
        
    #===========================================================================
    # Tabu
    #===========================================================================   
    def _remTabuedOption(self, lstype, candidatels):

        logging.info("******* TABU ************ candidatels = %s" %(candidatels))     
           
        tabuls = self._getTabuList(lstype)
        logging.info("******* TABU ************ tabuls=%s" %tabuls)
        ls = [x for x in candidatels if x not in tabuls]
        logging.info("******* TABU ************ candidatels after removing tabu-ed option = %s" %(ls))
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
       
        logging.info("******* TABU ************ updated  tabulist: %s" %(self.tabulist))
        
        
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
    
        logging.info("******* TABU ************ expls: %s" %(expls))
        
        for i in xrange(len(expls)):
            [k,tk] = expls[i]
            del self.tabulist[k][tk]
            
        logging.info("******* TABU ************ after removing expired tabulist: %s" %(self.tabulist))
            
    #===========================================================================
    # Diagnose
    #=========================================================================== 
    def _log_ObjValue_Neighbourhood(self, logtime, objvalue, nt):
        data = [logtime, objvalue, nt]
        try:
            fstr = 'Output/' + self.casecfgid + '_LNS_trace'
            f = open(fstr,'a')
            f.write(",".join(map(str, data)))            
            f.write("\n")
            f.close()    
        except (ValueError), e:
            logging.critical('%s' % (e))    
    
    def log_schedule(self):        
        self.milp_solver.logSchedulingResults()
        self.milp_solver.logMSTR_SchedulingResults()    
        
    def log_hvac(self):
        self.milp_solver.logHVACResults()
        self.milp_solver.logMSTR_HVACResults()
        
    def log_all(self):
        self.milp_solver.logMSTR_SchedulingResults()
        self.milp_solver.logMSTR_HVACResults()
        self.milp_solver.logMSTR_Schedules(self.casecfgid)
        self.milp_solver.logMSTR_Temperatures(self.casecfgid)
#         self.milp_solver.logStatistics(self.runcfg, self.casecfgid)        
#         self.milp_solver.logEnergy(self.runcfg, self.casecfgid)
        

    #===========================================================================
    # EAMS_LNS Compare with MILP given LNS Initial Schedule 
    #===========================================================================
    def run_milp_withLNSinitSche(self, timelim):  
        logging.info("\n\n\n\n\n=====================================================")
        logging.info("    Solving MILP only with Given LNS initial schedule    ")
        logging.info("=====================================================")   
        if timelim < 0:       
            self.milp_solver.solveMILPWithInitialSchedule(self.casecfgid + "_XW", 1, self.LNS_TIMELIMIT_SEC, 1)
        else:
            self.milp_solver.solveMILPWithInitialSchedule(self.casecfgid + "_XW", 1, timelim, 1)
        [objval, gap] = self.milp_solver.solveByRemInitScheFixedAttrBounds()   # This API must run after running solveMILPWithInitialSchedule()
        self.milp_solver.logSchedulingResults()    
        self.milp_solver.logHVACResults()
        self.milp_solver.logSchedules(self.casecfgid + "_MILP")
        self.milp_solver.logTemperatures(self.casecfgid + "_MILP")       
         
        self.log_MILPGap(gap)
         
        return [objval]
    
    def log_MILPGap(self, gap):
        data = [self.casecfgid, gap]
        try:
            fstr = 'Output/' + self.runcfg + '_milp_gap'
            f = open(fstr,'a')
            f.write(",".join(map(str, data)))            
            f.write("\n")
            f.close()    
        except (ValueError), e:
            logging.critical('%s' % (e))    
        

    def log_AlgoStats(self, lns_obj, mip_obj, seed, mip, d2, d3, d4):
        data = [self.casecfgid, seed, lns_obj, mip_obj, mip, d2, d3, d4]
        try:
            fstr = 'Output/' + self.runcfg + '_stats'
            f = open(fstr,'a')
            f.write(",".join(map(str, data)))            
            f.write("\n")
            f.close()    
        except (ValueError), e:
            logging.critical('%s' % (e))    
        
    def log_DRStats(self):
        
        dr_per_room = " ".join(map(str, self.NUM_DESTROY_PER_ROOM))
        dr_per_round = " ".join(map(str, self.NUM_ROOM_DESTROYED_PER_ROUND))
        drm_per_round = " ".join(map(str, self.NUM_MEETING_DESTROY_PER_ROUND))
        data = [dr_per_room, len(self.NUM_ROOM_DESTROYED_PER_ROUND), dr_per_round, drm_per_round]
        
        try:
            fstr = 'Output/' + self.runcfg + '_drstats'
            f = open(fstr,'a')
            f.write(",".join(map(str, data)))            
            f.write("\n")
            f.close()    
        except (ValueError), e:
            logging.critical('%s' % (e)) 
            
        
        
    
        