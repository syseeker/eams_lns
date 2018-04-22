import logging
from datetime import datetime
from time import time

from eams_log import cb_mipsol
from eams import EAMS
from solver_error import SOLVER_LNS_Error

from gurobipy import *
        
class Solver_MILP:
    def __init__(self, EAMS, fn, cfg_idx, timelimit, logcb, LNS_SEED):
        self.model = Model('EAMS')
        self.EAMS = EAMS
        self.GUROBI_LOGFILE = fn
        self.GUROBI_SEED = LNS_SEED
        self.err = SOLVER_LNS_Error()
        
        self.USE_REDUCED_MODEL = 1          # switch to HVAC reduced model (which remove all internal wall, ignore zone conduction within building, just consider enthalpy and external wall)
        logging.info("Use REDUCED HVAC Model? %s" %(self.USE_REDUCED_MODEL))
        self.LOG_LP = 0                     # turn on to write LP file
        self.LOG_MIP_EAMS = 0               # turn this off to save more time for LNS operation!
        
        self.solveTime = -1                 # TODO: in LNS, solveTime is calculated in solver_lns
        self.CASE_CFG = cfg_idx        
        self.TIME_LIMIT = float(timelimit)
        self.LOG_CB     = int(logcb)
        self.SOLUTION_LIMIT = -1            # do not impose limit
                
        self.SCHE_MODE = 0                  # 0: full schedule, 1: partial schedule
        self.MSTR_NUM_SLOT = len(self.EAMS.TS)-1
        self.MSTR_NUM_MEETING = len(self.EAMS.ML)
        self.MSTR_NUM_MEETING_TYPE = len(self.EAMS.MTYPE)
        self.MSTR_NUM_ROOM = len(self.EAMS.RL)
        logging.debug("******************* #k = %d #m = %d #r = %d  #mtype = %d" %(self.MSTR_NUM_SLOT, self.MSTR_NUM_MEETING, self.MSTR_NUM_ROOM, self.MSTR_NUM_MEETING_TYPE))
        
        self._initConstant()
        self._initMstrScheduleVar()
        self._initMstrHVACVar()
        
            
        
    #===========================================================================
    # Initialization & Create Model
    #===========================================================================
    def initModel(self):   
        logging.info("===============================================================")
        logging.info("Gurobi - Initialize Gurobi config & Callback ")
        logging.info("===============================================================")          
        self._initializeGurobiCfg() 
        
    def updateGurobiParam(self, TIME_LIMIT):
        """Set Gurobi param which apply to non-initial solution"""
                        
        if TIME_LIMIT > 0:
            self.TIME_LIMIT = TIME_LIMIT
            self.model.setParam(GRB.Param.TimeLimit, TIME_LIMIT) 
            logging.info("Update GRB.Param.TimeLimit to %f" %(self.TIME_LIMIT) )
        
                    
        self.model.update()
 
    def _resetGurobi(self, runidx):
        self.model = Model('EAMS_'+str(runidx))
        self.initModel()
        
    def _initializeGurobiCfg(self):
#         self.model.setParam(GRB.param.OutputFlag, 0)
        self.model.setParam(GRB.param.LogFile, self.GUROBI_LOGFILE)
#         self.model.setParam(GRB.param.LogToConsole, 0) #TODO: bug!! Never turn off!
                
        self.model.setParam(GRB.Param.Seed, self.GUROBI_SEED)        
        self.model.setParam(GRB.Param.Threads, 1)
        self.model.setParam(GRB.Param.FeasibilityTol, 1e-9)        
        self.model.setParam(GRB.Param.IntFeasTol, 1e-9)          
        self.model.setParam(GRB.Param.OptimalityTol, 1e-9)

        if self.TIME_LIMIT > 0:
            self.model.setParam(GRB.Param.TimeLimit, self.TIME_LIMIT) 
          
#         
#         self.model.setParam(GRB.Param.TuneTimeLimit, 180)  # 18000        
                
#        Limits the number of feasible MIP solutions found. 
#            Optimization returns with a SOLUTION_LIMIT status once the limit has been reached       
        if self.SOLUTION_LIMIT > 0: 
            self.model.setParam(GRB.Param.SolutionLimit, self.SOLUTION_LIMIT)
#        When querying attribute Xn to retrieve an alternate MIP solution, 
#            this parameter determines which alternate solution is retrieved. 
#            The value of this parameter should be less than the value of the SolCount attribute.
#         self.model.setParam(GRB.Param.SolutionNumber, 1)
                
#        Controls the branch variable selection strategy. 
#         The default -1 setting makes an automatic choice, depending on problem characteristics. 
#         Available alternatives are Pseudo Reduced Cost Branching (0), 
#                             Pseudo Shadow Price Branching (1), 
#                             Maximum Infeasibility Branching (2), 
#                             and Strong Branching (3).
#            Changing the value of this parameter rarely produces a significant benefit.
#         self.model.setParam(GRB.Param.VarBranch, 3)
        
#         Cope with out-of-memory error.
#         When the amount of memory used to store nodes (measured in GBytes) exceeds the specified parameter value, 
#         nodes are written to disk.  NodefileDir parameter can be used to choose a different location.
        self.model.setParam(GRB.Param.NodefileStart, 0.5)

#         The MIP solver can change parameter settings in the middle of the search in order to adopt a strategy 
#             that gives up on moving the best bound and instead devotes all of its effort towards finding better 
#             feasible solutions. 
#            
#            This parameter allows you to specify the node count at which the MIP solver switches
#             to a solution improvement strategy. For example, setting this parameter to 10 will cause the MIP solver
#             to switch strategies once the node count is larger than 10.
#         self.model.setParam(GRB.Param.ImproveStartNodes, 10.0)

#            This parameter allows you to specify an optimality gap at which the MIP solver switches 
#            to a solution improvement strategy. For example, setting this parameter to 0.1 will cause the MIP solver 
#            to switch strategies once the relative optimality gap is smaller than 0.1.
#         self.model.setParam(GRB.Param.ImproveStartGap, 0.1)
        
#         Controls the presolve level. A value of -1 corresponds to an automatic setting. 
#             Other options are off (0), conservative (1), or aggressive (2). 
#         self.model.setParam(GRB.param.Presolve,2)   

#        The PrePasses provides finer-grain control of presolve. 
#        It limits the number of passes presolve performs. Setting it to a small value (e.g., 3) can reduce presolve runtime.
#        Limits the number of passes performed by presolve. 
#            The default setting (-1) chooses the number of passes automatically. 
#            You should experiment with this parameter when you find that presolve is consuming 
#                a large fraction of total solve time.  
#         self.model.setParam(GRB.param.PrePasses,3)   
        
#         Controls the presolve sparsify reduction. 
#            This reduction can sometimes significantly reduce the number of nonzero values in the presolved model. 
#            Value 0 shuts off the reduction, while value 1 forces it on. The default value of -1 chooses automatically.              
#         self.model.setParam(GRB.param.PreSparsify,1)
        
#        The Symmetry parameter controls symmetry detection. 
#         The default value usually works well. 
#         The VarBranch parameter controls the branching variable selection strategy within the branch-and-bound process. 
#         Variable selection can have a significant impact on overall time to solution, 
#             but the default strategy is usually the best choice.
#
#        Controls MIP symmetry detection. A value of -1 corresponds to an automatic setting. Other options are off (0), conservative (1), or aggressive (2).
#            Changing the value of this parameter rarely produces a significant benefit.
#         self.model.setParam(GRB.Param.Symmetry, 2)
        
        # Algorithm used to solve continuous models or the root node of a MIP model.
            # Options are: -1=automatic, 0=primal simplex, 1=dual simplex, 2=barrier, 3=concurrent, 4=deterministic concurrent.
        # In the current release, the default Automatic (-1) setting will typically choose
            #---------------- non-deterministic concurrent (Method=3) for an LP,
            #--------------------------- barrier (Method=2) for a QP or QCP, and
            #---------------------------- dual (Method=1) for the MIP root node.
        # Only the simplex and barrier algorithms are available for continuous QP models.
        # Only primal and dual simplex are available for solving the root of an MIQP model.
        #------------------ Only barrier is available for continuous QCP models.
        # Concurrent optimizers run multiple solvers on multiple threads simultaneously, and
            #------------------------------- choose the one that finishes first.
        # Deterministic concurrent (Method=4) gives the exact same result each time,
            # while Method=3 is often faster but can produce different optimal bases when run multiple times.
        # The default setting is rarely significantly slower than the best possible setting,
            # so you generally won't see a big gain from changing this parameter.
        # There are classes of models where one particular algorithm is consistently fastest,
        # though, so you may want to experiment with different options when confronted with a particularly difficult model.
#         self.model.setParam(GRB.Param.Method, 2)


#         The MIP solver will terminate (with an optimal result) when the relative gap between the lower 
#             and upper objective bound is less than MIPGap times the upper bound. Default value:    1e-4
#         self.model.setParam(GRB.Param.MIPGap, 0.015)
        
#         If you are more interested in finding feasible solutions quickly, you can select MIPFocus=1. 
#         If you believe the solver is having no trouble finding good quality solutions, and wish to focus more attention on proving optimality, select MIPFocus=2. 
#         If the best objective bound is moving very slowly (or not at all), you may want to try MIPFocus=3 to focus on the bound.
#         self.model.setParam(GRB.Param.MIPFocus, 2)

#         Indicates that you aren't interested in solutions whose objective values are worse than the specified value. 
#         If the objective value for the optimal solution is better than the specified cutoff, 
#             the solver will return the optimal solution. Otherwise, it will terminate with a CUTOFF status
#         self.model.setParam(GRB.Param.Cutoff, double value)
        
        # Determines the amount of time spent in MIP heuristics. 
        # You can think of the value as the desired fraction of total MIP runtime devoted to heuristics 
        #     (so by default, we aim to spend 5% of runtime on heuristics). 
        # Larger values produce more and better feasible solutions, at a cost of slower progress in the best bound.
#         self.model.setParam(GRB.Param.Heuristics, 0)

    def _initConstant(self):
        
        self.USE_MEETING_TYPE = 1
        self.SCHE_TYPE_MIN_ROOM_PER_DAY   = 1        
        
        self.KJ_TO_KWh = 0.000277777778
        self.N_OUTDOOR = 1000
        self.N_NOT_EXIST = -1
        
        self.MIP_TIMELIMITREACHED_NOSOLUTION = 999999
        self.EPSILON = 1.0e-06
        self.STATUS = ['', 'LOADED', 'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'CUTOFF', 'ITERATION_LIMIT', 'NODE_LIMIT', 'TIME_LIMIT', 'SOLUTION_LIMIT', 'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL']

    def _initMstrScheduleVar(self):                
        self.MSTR_BDV_x_MLK = []                         # Binary Decision variable: The "Starting" slot of a meeting in Meeting x Location x Time        
        self.MSTR_BAV_z_LK = []                          # Binary Auxiliary variable: represent if location l is occupied at time k (do not care which meeting)        
        self.MSTR_DAV_Attendee_LK = []                   # Discrete Auxiliary variable: Number of attendee at room l at time k
        
        self.MSTR_BDV_x_MLK_Dict = {}                    # d[(m,l,k)] = offset of (m,l,k) in BDV_x_MLK. Record index of meeting x location x time periods
        self.MSTR_BDV_w_LK_Dict = {}                     # d[(l,k)] = offset of (l,k) in BDV_w_LK. Record index of location x time periods
        
        self._initMSTR_BDV_x_MLK_MT()
        self._initMSTR_BAV_z_LK()
        self._initMSTR_DAV_Attendee_LK()
        
         
    def _initMstrHVACVar(self):
        self.MSTR_CDV_T_SA_LK = []                       # Continuous Decision variable: Supply air temperature
        self.MSTR_CDV_A_SA_LK = []                       # Continuous Decision variable: air mass flow rate                
        self.MSTR_CAV_T_LK = []                          # Continuous Auxiliary variable: Room/Zone temperature        
        self.MSTR_CAV_E_FAN_LK = []                      # Auxiliary variable: Energy consumption of fan operation
        self.MSTR_CAV_E_CONDITIONING_LK = []             # Auxiliary variable: Energy consumption of conditioning operation
        self.MSTR_CAV_E_HEATING_LK = []                  # Auxiliary variable: Energy consumption of heating operation

        if self.EAMS.STANDBY_MODE == '1':            
            self.MSTR_BDV_w_LK = []                          # Binary Decision variable: represent if HVAC is activated from standby mode at location l at time k
            self._initMSTR_BDV_w_LK()
        
        self._initMSTR_CDV_T_SA_LK()
        self._initMSTR_CDV_A_SA_LK()
        self._initMSTR_CAV_T_LK()
        self._initMSTR_CAV_E_FAN_LK()
        self._initMSTR_CAV_E_CONDITIONING_LK()
        self._initMSTR_CAV_E_HEATING_LK()
        
                 
    def _initMSTR_BDV_x_MLK_MT(self):
        for m in xrange(self.MSTR_NUM_MEETING_TYPE):
            # Get feasible start time from any one meeting in MLS
            mid = self.EAMS.MTYPE[m].MLS[0]                
            self.MSTR_BDV_x_MLK.append([])
            ml = 0
            for l in xrange(self.MSTR_NUM_ROOM):
                if l in self.EAMS.MR[m]:    # TODO: assume all meetings of the same type can access the same room. Re-group required if not!
                    self.MSTR_BDV_x_MLK[m].append([])  
                    mk = 0                                      
                    for k in xrange(self.MSTR_NUM_SLOT):                        
                        if self.EAMS.isInTimeWindows(mid,k) > 0:
                            self.MSTR_BDV_x_MLK[m][ml].append(0)                            
                            self.MSTR_BDV_x_MLK_Dict[tuple([m,l,k])] = [m,ml,mk]                            
                            mk = mk+1
                    ml = ml+1
        logging.info("self.MSTR_BDV_x_MLK_Dict: %s" %(self.MSTR_BDV_x_MLK_Dict))
                    
    def _initMSTR_BDV_w_LK(self):                
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_BDV_w_LK.append([])
            mk = 0
            for k in xrange(self.MSTR_NUM_SLOT):
                if self.EAMS.SH[k] == 0:
                    self.MSTR_BDV_w_LK[l].append(0)
                    self.MSTR_BDV_w_LK_Dict[tuple([l,k])] = [l,mk]
                    mk = mk+1
                    
    def _initMSTR_BAV_z_LK(self):
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_BAV_z_LK.append([])
            self.MSTR_BAV_z_LK[l] = [0] * self.MSTR_NUM_SLOT
                         
    def _initMSTR_DAV_Attendee_LK(self): 
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_DAV_Attendee_LK.append([])
            self.MSTR_DAV_Attendee_LK[l] = [0] * self.MSTR_NUM_SLOT
                
    def _initMSTR_CDV_T_SA_LK(self):
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_CDV_T_SA_LK.append([])
            self.MSTR_CDV_T_SA_LK[l] = [0] * self.MSTR_NUM_SLOT
                
    def _initMSTR_CDV_A_SA_LK(self):
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_CDV_A_SA_LK.append([])
            self.MSTR_CDV_A_SA_LK[l] = [0] * self.MSTR_NUM_SLOT
          
    def _initMSTR_CAV_T_LK(self):
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_CAV_T_LK.append([])
            self.MSTR_CAV_T_LK[l] = [0] * self.MSTR_NUM_SLOT
            
    def _initMSTR_CAV_E_FAN_LK(self):
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_CAV_E_FAN_LK.append([])
            self.MSTR_CAV_E_FAN_LK[l] = [0] * self.MSTR_NUM_SLOT
                            
    def _initMSTR_CAV_E_CONDITIONING_LK(self):
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_CAV_E_CONDITIONING_LK.append([])
            self.MSTR_CAV_E_CONDITIONING_LK[l] = [0] * self.MSTR_NUM_SLOT
                
    def _initMSTR_CAV_E_HEATING_LK(self):
        for l in xrange(self.MSTR_NUM_ROOM):
            self.MSTR_CAV_E_HEATING_LK.append([])
            self.MSTR_CAV_E_HEATING_LK[l] = [0] * self.MSTR_NUM_SLOT
            
    def _createScheduleModel(self):                
        # Reset schedule and HVAC variables & constraints
        self._resetMILPVar()
        
        logging.info("Create Schedule Model *WITH* Meeting Type")
        self._createBDV_x_MLK_MT()
        self._createBAV_z_LK()
        self._createDAV_Attendee_LK()
        
        self._createCSTR_Schedule_Once_MT()
        self._createCSTR_LocationTimeOccupied_MT()
        self._createCSTR_NumAttendee_MT()
        self._createCSTR_AttendeeConflict_MT()     
        
    def _createHVACModel(self):
        self._createCDV_SupplyAirTemperature()
        self._createCDV_AirMassFlowRate()
        self._createCAV_RoomTemperature()
        self._createCAV_T_z1_l()
        self._createCAV_T_z2_l()  
        self._createCAV_T_z3_l()  
        self._createCAV_T_z4_l()  
        self._createCAV_T_l_z1()          
        self._createCAV_T_l_z2()
        self._createCAV_T_l_z3()
        self._createCAV_T_l_z4()
        self._createCAV_T_l_f()
        self._createCAV_T_l_c()
        self._createCAV_A_SA_T_z_LK()
        self._createCAV_A_SA_T_SA_LK()    
        
        self._createCSTR_RoomTemperature_LB()
        self._createCSTR_RoomTemperature_UB()
        self._createCSTR_RoomTemperature()
        self._createCSTR_T_z1_l()
        self._createCSTR_T_z2_l()  
        self._createCSTR_T_z3_l()  
        self._createCSTR_T_z4_l()  
        self._createCSTR_T_l_z1()          
        self._createCSTR_T_l_z2()
        self._createCSTR_T_l_z3()
        self._createCSTR_T_l_z4()
        self._createCSTR_T_l_f()
        self._createCSTR_T_l_c()
                
        if self.EAMS.STANDBY_MODE == '0':
            # HVAC mode - options - enable either 1 set
            # option 1: no standby mode. HVAC is OFF after standard working hours
            logging.info("HVAC running on non-standby mode... HVAC is off at night.")
            self._createHVAC_CSTR_noStandbyMode()
        else:
            # option 2: has standby mode. HVAC will be automatically turned on/off after standard working hours.
            logging.info("HVAC running on standby mode... HVAC can be turned on at night.")
            self._createHVAC_CSTR_hasStandbyMode()        
            
        self._createHVAC_CSTR_Energy()      
        
    def _createHVAC_CSTR_noStandbyMode(self):
        self._createCSTR_SupplyAirTemperature_LB_noStandbyMode()        
        self._createCSTR_SupplyAirFlowRate_LB_noStandbyMode()  
        self._createHVAC_CSTR_A_SA_T_SA_noStandbyMode()
        self._createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_noStandbyMode()
        
    def _createHVAC_CSTR_hasStandbyMode(self):
        self._createBDV_w_LK()
        self._createCSTR_SupplyAirTemperature_LB_hasStandbyMode()
        self._createCSTR_SupplyAirTemperature_UB_hasStandbyMode()
        self._createCSTR_SupplyAirFlowRate_LB_hasStandbyMode()
        self._createCSTR_SupplyAirFlowRate_UB_hasStandbyMode()   
        self._createHVAC_CSTR_A_SA_T_SA_hasStandbyMode()
        self._createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_hasStandbyMode()        
        
    def _get_A_SA_LB(self, l, k):        
        if self.EAMS.SH[k] == 1:
            [width, length, height] = self.EAMS.getRoomThermalConfig(l, "Dim")
            A_SA_LB = self.EAMS.ALPHA_IAQ_FACTOR_OF_SAFETY*(
                                                    (self.EAMS.MASS_AIR_FLOW_OUTSIDE_AIR_PER_METER_SQUARE * width * length * height) /
                                                    (1-self.EAMS.MASS_AIR_FLOW_RETURN_AIR_RATIO))
        else:
            A_SA_LB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MIN
        
        return float(A_SA_LB)
    
    def _get_T_SA_LB(self, l, k):
        if self.EAMS.SH[k] == 1:
            return float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)
        else:
            return float(self.EAMS.INITIAL_TEMPERATURE_SUPPLY_AIR_UNOCC)
        
    def _createHVAC_CSTR_A_SA_T_SA_hasStandbyMode(self):
        self._createCSTR_A_SA_T_SA_1_LK_hasStandbyMode()
        self._createCSTR_A_SA_T_SA_2_LK_hasStandbyMode()
        self._createCSTR_A_SA_T_SA_3_LK_hasStandbyMode()
        self._createCSTR_A_SA_T_SA_4_LK_hasStandbyMode()
        
    def _createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_hasStandbyMode(self):
        self._createCSTR_A_SA_T_z_1_LK_looseboundedT_hasStandbyMode()
        self._createCSTR_A_SA_T_z_2_LK_looseboundedT_hasStandbyMode()
        self._createCSTR_A_SA_T_z_3_LK_looseboundedT_hasStandbyMode()
        self._createCSTR_A_SA_T_z_4_LK_looseboundedT_hasStandbyMode()
                    
    def _createHVAC_CSTR_A_SA_T_SA_noStandbyMode(self):
        self._createCSTR_A_SA_T_SA_1_LK_noStandbyMode()
        self._createCSTR_A_SA_T_SA_2_LK_noStandbyMode()
        self._createCSTR_A_SA_T_SA_3_LK_noStandbyMode()
        self._createCSTR_A_SA_T_SA_4_LK_noStandbyMode()
        
    def _createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_noStandbyMode(self):
        self._createCSTR_A_SA_T_z_1_LK_looseboundedT_noStandbyMode()
        self._createCSTR_A_SA_T_z_2_LK_looseboundedT_noStandbyMode()
        self._createCSTR_A_SA_T_z_3_LK_looseboundedT_noStandbyMode()
        self._createCSTR_A_SA_T_z_4_LK_looseboundedT_noStandbyMode()
        
    def _createHVAC_CSTR_Energy(self):
        self._createCAV_EnergyConsumption_Fan()
        self._createCAV_EnergyConsumption_Conditioning()
        self._createCAV_EnergyConsumption_Heating()
        
        self._createCSTR_EnergyConsumption_Fan()
        self._createCSTR_EnergyConsumption_Conditioning()
        self._createCSTR_EnergyConsumption_Heating()
        
#---------------------------------------------------------------------------------        
        
    def _resetMILPVar(self):
        """Reset variable and constraint for new partial schedule generation every round."""
        
        logging.info("Reset NumSlot/Room/Meeting, ScheVar, HVAC Var.")
        self._resetScheduleVar()
        self._resetHVACVar()
        
        if self.SCHE_MODE == 0:  # Full schedule
            logging.info("Building *FULL* schedule")
            self.NUM_SLOT = len(self.EAMS.TS)-1
            self.NUM_MEETING = len(self.EAMS.ML)
            self.NUM_MEETING_TYPE = len(self.EAMS.MTYPE)
            self.NUM_ROOM = len(self.EAMS.RL)
            logging.info("******************* #k = %d #m = %d #r = %d  #mtype = %d" %(self.NUM_SLOT, self.NUM_MEETING, self.NUM_ROOM, self.NUM_MEETING_TYPE))
        else:
            logging.info("Building *PARTIAL* schedule")                       
            self.NUM_MEETING_TYPE = len(self.CURR_DESTROY_MTYPE)
            self.NUM_ROOM = len(self.CURR_DESTROY_LOCATION)
            logging.info("******************* #k = %d #r = %d  #mtype = %d" %(self.NUM_SLOT, self.NUM_ROOM, self.NUM_MEETING_TYPE))

        
    def _resetScheduleVar(self):                
        self.BDV_x_MLK = []                         # Binary Decision variable: The "Starting" slot of a meeting in Meeting x Location x Time
        self.BDV_w_LK = []                          # Binary Decision variable: represent if HVAC is activated from standby mode at location l at time k
        self.BAV_z_LK = []                          # Binary Auxiliary variable: represent if location l is occupied at time k (do not care which meeting)        
        self.DAV_Attendee_LK = []                   # Discrete Auxiliary variable: Number of attendee at room l at time k
        
        self.BDV_x_MLK_Dict = {}                    # d[(m,l,k)] = offset of (m,l,k) in BDV_x_MLK. Record index of meeting x location x time periods
        self.BDV_w_LK_Dict = {}                     # d[(l,k)] = offset of (l,k) in BDV_w_LK. Record index of location x time periods
        
        self.BAV_y_LD = []                          # Binary Decision variable: represent if location l is occupied at day D
        self.CSTR_MinRoom = []                      # Constraint: Force meeting allocation into minimum number of room per day
                
        self.CSTR_Schedule_Once_M = []              # Constraint: Every meeting must be scheduled to 1 room exactly at its starting time k
        self.CSTR_LocationTimeOccupied=[]           # Constraint:     set BAV_z_LK to 1 if at least 1 meeting is held at location l at time k
        self.CSTR_NumAttendee = []                  # Constraint: Number of attendee at room l at time k
        self.CSTR_AttendeeConflict = []             # Constraint: Meeting which has similar attendee should not be allocated at the same timeslot
       
    def _resetHVACVar(self):
        self.CDV_T_SA_LK = []                       # Continuous Decision variable: Supply air temperature
        self.CDV_A_SA_LK = []                       # Continuous Decision variable: air mass flow rate                
        self.CAV_T_LK = []                          # Continuous Auxiliary variable: Room/Zone temperature        
        self.CAV_A_SA_Room_L = []                   # Continuous Auxiliary variable: Minimum air mass flow rate per location
        self.CAV_A_SA_MaxPeople_L = []              # Continuous Auxiliary variable: Minimum air mass flow rate per occupant required
        self.CAV_A_SA_T_z_LK = []                   # Continuous Auxiliary variable:  aT(SA,z)
        self.CAV_A_SA_T_SA_LK = []                  # Continuous Auxiliary variable:  aT(SA,SA)        
        self.CAV_E_FAN_LK = []                      # Auxiliary variable: Energy consumption of fan operation
        self.CAV_E_CONDITIONING_LK = []             # Auxiliary variable: Energy consumption of conditioning operation
        self.CAV_E_HEATING_LK = []                  # Auxiliary variable: Energy consumption of heating operation        
        self.CAV_T_z1_l_LK = []                     # Continuous Auxiliary variable: wall temperature from zone zl to zone l                    
        self.CAV_T_z2_l_LK = []                     # Continuous Auxiliary variable: wall temperature from zone z2 to zone l
        self.CAV_T_z3_l_LK = []                     # Continuous Auxiliary variable: wall temperature from zone z3 to zone l
        self.CAV_T_z4_l_LK = []                     # Continuous Auxiliary variable: wall temperature from zone z4 to zone l
        self.CAV_T_l_z1_LK = []                     # Continuous Auxiliary variable: wall temperature from zone l to zone z1
        self.CAV_T_l_z2_LK = []                     # Continuous Auxiliary variable: wall temperature from zone l to zone z2
        self.CAV_T_l_z3_LK = []                     # Continuous Auxiliary variable: wall temperature from zone l to zone z3
        self.CAV_T_l_z4_LK = []                     # Continuous Auxiliary variable: wall temperature from zone l to zone z4
        self.CAV_T_l_f_LK  = []                     # Continuous Auxiliary variable: wall temperature from zone l to zone f
        self.CAV_T_l_c_LK  = []                     # Continuous Auxiliary variable: wall temperature from zone l to zone c   
        self.A_SA_LB = []
        
        self.CSTR_T_SA_LK = []                      # Constraint:     T_CA*BAV_L <= T_SA <= T_SA_HIGH
        self.CSTR_T_LK_lb = []                      # Constraint: lower bound of room temperature
        self.CSTR_T_LK_ub = []                      # Constraint: upper bound of room temperature
        self.CSTR_T_LK = []                         # Constraint: Equation of room/zone temperature
        self.CSTR_T_z1_l_LK = []                    # Constraint: Equation of wall temperature from z1 to l
        self.CSTR_T_z2_l_LK = []                    # Constraint: Equation of wall temperature from z2 to l
        self.CSTR_T_z3_l_LK = []                    # Constraint: Equation of wall temperature from z3 to l
        self.CSTR_T_z4_l_LK = []                    # Constraint: Equation of wall temperature from z4 to l
        self.CSTR_T_l_z1_LK = []                    # Constraint: Equation of wall temperature from l to z1  
        self.CSTR_T_l_z2_LK = []                    # Constraint: Equation of wall temperature from l to z2
        self.CSTR_T_l_z3_LK = []                    # Constraint: Equation of wall temperature from l to z3
        self.CSTR_T_l_z4_LK = []                    # Constraint: Equation of wall temperature from l to z4
        self.CSTR_T_l_f_LK = []                     # Constraint: Equation of wall temperature from l to f
        self.CSTR_T_l_c_LK = []                     # Constraint: Equation of wall temperature from l to c

        self.CSTR_A_SA_LB_LK = []                   # Constraint: lower bound of air mass flow rate
        self.CSTR_A_SA_UB_LK = []                   # Constraint: upper bound of air mass flow rate
        self.CSTR_T_SA_LB_LK = []                   # Constraint: lower bound of T_SA
        self.CSTR_T_SA_UB_LK = []                   # Constraint: upper bound of T_SA

        self.CSTR_A_SA_T_z_1_LK = []                # Constraint: MacCormick relaxation for A_SA x T
        self.CSTR_A_SA_T_z_2_LK = []                # Constraint: MacCormick relaxation for A_SA x T
        self.CSTR_A_SA_T_z_3_LK = []                # Constraint: MacCormick relaxation for A_SA x T
        self.CSTR_A_SA_T_z_4_LK = []                # Constraint: MacCormick relaxation for A_SA x T
                
        self.CSTR_A_SA_T_SA_1_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        self.CSTR_A_SA_T_SA_2_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        self.CSTR_A_SA_T_SA_3_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        self.CSTR_A_SA_T_SA_4_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        
        self.CSTR_E_FAN_LK = []                     # Constraint: Equation of energy consumption of fan operation
        self.CSTR_E_CONDITIONING_LK = []            # Constraint: Equation of energy consumption of air-conditioning operation
        self.CSTR_E_HEATING_LK = []                 # Constraint: Equation of energy consumption of heating operation
    

    #===========================================================================
    # MILP (solve MILP only)
    #===========================================================================
    def solveMILP(self, log_cb, time_limit, use_reduced_model):
        self.initModel()
        self.LOG_CB = int(log_cb)
        self.updateGurobiParam(float(time_limit))
                
        self.SCHE_MODE = 0
        self.USE_REDUCED_MODEL = use_reduced_model
        logging.info("Use REDUCED HVAC Model? %s" %(self.USE_REDUCED_MODEL))
        
        self._createScheduleModel()
        self._createHVACModel()        
        self._createObjective()
        
        if self.LOG_CB:
            self._initializeCallback()
            
        self.model.update()
        
        if self.LOG_CB == 1:
            self.model.optimize(cb_mipsol)
        else:                
            self.model.optimize()
        
        logging.info("ObjValue: %g" %(self.model.getAttr(GRB.attr.ObjVal)))    
        
    #===========================================================================
    # MILP (solve MILP given initial schedule)
    #===========================================================================
    def solveMILPWithInitialSchedule(self, fsche, log_cb, time_limit, use_reduced_model):
        
        self._readSchedule(fsche)
        
        self._resetGurobi(1)  
        self.LOG_CB = int(log_cb)
        self.updateGurobiParam(float(time_limit))
         
        self.SCHE_MODE = 0
        self.USE_REDUCED_MODEL = use_reduced_model
        logging.info("Use REDUCED HVAC Model? %s" %(self.USE_REDUCED_MODEL))
        
        self._createScheduleModel()
        self._createHVACModel()        
        self._createObjective()
         
        if self.LOG_CB:
            self.CASE_CFG = "MILP_" + self.CASE_CFG
            self._initializeCallback()

        for m in xrange(len(self.INIT_X)):
            [m,l,k] = self.INIT_X[m]
            self.BDV_x_MLK[int(m)][int(l)][int(k)].setAttr("LB", 1.0)
            
        for w in xrange(len(self.INIT_W)):
            [l,k] = self.INIT_W[w]
            self.BDV_w_LK[int(l)][int(k)].setAttr("LB", 1.0)

        self.model.update()
        
#         self.LOG_LP = 1
#         if self.LOG_LP:
#             self.model.write('Output/EAMS_' + str(self.CASE_CFG) + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'wifBounds.lp')
#         self.LOG_LP = 0
         
        if self.LOG_CB == 1:
            self.model.optimize(cb_mipsol)
        else:                
            self.model.optimize()
         
        logging.info("ObjValue: %g" %(self.model.getAttr(GRB.attr.ObjVal)))    
        
        return self.model.getAttr(GRB.attr.ObjVal) 
           
        
    def solveByRemInitScheFixedAttrBounds(self):
        
        for m in xrange(len(self.INIT_X)):
            [m,l,k] = self.INIT_X[m]
            self.BDV_x_MLK[int(m)][int(l)][int(k)].setAttr("LB", 0.0)
            
        for w in xrange(len(self.INIT_W)):
            [l,k] = self.INIT_W[w]
            self.BDV_w_LK[int(l)][int(k)].setAttr("LB", 0.0)

        self.model.update()
        
#         self.LOG_LP = 1
#         if self.LOG_LP:
#             self.model.write('Output/EAMS_' + str(self.CASE_CFG) + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'remBounds.lp')
#         self.LOG_LP = 0
         
        if self.LOG_CB == 1:
            self.model.optimize(cb_mipsol)
        else:                
            self.model.optimize()
         
        logging.info("ObjValue: %g" %(self.model.getAttr(GRB.attr.ObjVal))) 
        
        return [self.model.getAttr(GRB.attr.ObjVal), self.model.getAttr(GRB.attr.MIPGap)]
        
        
    def _readSchedule(self, fsche):
        try:
            # Read schedule data
            if fsche:
                fsstr = 'Output/' + fsche
                sche_data_file = open(fsstr, 'r')
                sche_data = ''.join(sche_data_file.readlines())
                sche_data_file.close()
                
            if sche_data:
                sche_lines = sche_data.split('\n')                
                num_m = int(sche_lines[0])
                self.INIT_X = []
                self.INIT_W = []
                
                for i in xrange(1, num_m+1):
                    self.INIT_X.append(list(sche_lines[i].split(',')))
                
                num_w = int(sche_lines[num_m+1])
                for i in xrange(num_m+2, num_m+2+num_w):
                    self.INIT_W.append(list(sche_lines[i].split(',')))
                    
                logging.info("INIT_X = %s" %self.INIT_X)
                logging.info("INIT_W = %s" %self.INIT_W)    
                                
        except (ValueError), e:
            logging.critical('%s' % (e))  
            
    def _initializeCallback(self):        
        self.model._CASE_CFG = self.CASE_CFG        
        self.model._EAMS = self.EAMS
        self.model._NUM_ROOM = self.NUM_ROOM
        self.model._NUM_SLOT = self.NUM_SLOT        
        self.model._EPSILON = self.EPSILON        
        
        # NOTE: need to do the below after the data structure is assigned
        self.model._BDV_w_LK = self.BDV_w_LK
        self.model._BDV_w_LK_Dict = self.BDV_w_LK_Dict        
    
    def _updateCbLog(self, stage):
        self.model._CASE_CFG = self.CASE_CFG + "_" + stage
        self.model.update()
        
    #===========================================================================
    # MILP + LNS Solver
    #===========================================================================  

    def getInitialSchedule(self, INITIAL_SCHEDULE_TYPE):
        logging.info("Get initial schedule...")
        
        if self.LOG_CB:
            self._updateCbLog("1a_LNS_INITSCHE")
            
        # Step 1: Create schedule variables & constraints
        t_start = time()
        self._createScheduleModel()
        self.model.update()
        logging.info("getInitialSchedule _createScheduleModel takes %s s" %(time()-t_start))
        
        # Step 2: If objective is set for room schedule, create 
        if INITIAL_SCHEDULE_TYPE == self.SCHE_TYPE_MIN_ROOM_PER_DAY:
            t_start = time()
            self._createMinRoomPerDayObjective()
            self.model.update()
            logging.info("getInitialSchedule _createMinRoomPerDayObjective takes %s s" %(time()-t_start))
            
        # Step 3: Log room schedule LP model
        if self.LOG_LP:
            self.model.write('Output/EAMS_LNS_' + str(self.CASE_CFG) + '_1b_LNS_INITSCHE_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.lp')
            
        # Step 4: Optimize model        
        t_start = time()
        if INITIAL_SCHEDULE_TYPE == self.SCHE_TYPE_MIN_ROOM_PER_DAY:
            if self.LOG_CB == 1:
                # Option 1: With callback, log all solutions' schedules and temperatures
                # Only if an objective exists                 
                self.model.optimize(cb_mipsol)
            else:                
                self.model.optimize()
        else:
            # Option 2: No callback (because no objective function, just find a feasible solution)
            self.model.optimize()
        logging.info("getInitialSchedule optimize takes %s s" %(time()-t_start))
        
        # Step 5: Check model status
        if self.STATUS.index('INFEASIBLE') != self.model.getAttr(GRB.attr.Status):
            # TODO: log this to file
#             self.model.printStats()
#             self.model.printQuality()
            self.hasInitialSolution = 1
            self._updMSTR_Schedules()    
#             self.logSchedules(self.CASE_CFG + "_1c_LNS_INITSCHE")
#             self.logMSTR_Schedules(self.CASE_CFG + "_1c_LNS_INITSCHE_MASTER") # No need, since it is useless.. cant plot graph without temperature..
                    
        return self.model.getAttr(GRB.attr.Status)
    
    
    def initHVACModelNEnergyObjBasedOnInitialSchedule(self):
        logging.info("Initialize HVAC model and Energy Objective, enforce scheduling constraint, optimize based on initial schedule...")
        
        # Add scheduling constraint, for initial schedule, no destroy, just enforce initial schedule cstr.
        t_start = time()
        self._createLNS_ScheduleCstr([],[],[])
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule _createLNS_ScheduleCstr takes: %s s" %(time()-t_start))
        
        # Initialize HVAC model
        t_start = time()
        self._createHVACModel()
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule _createHVACModel takes: %s s" %(time()-t_start))

        # Add energy minimization objective  
        t_start = time()
        self._createObjective()        
        self.model.update()
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule _createObjective takes: %s s" %(time()-t_start))           
        
                     
        if self.LOG_LP:
            self.model.write('Output/EAMS_LNS_' + str(self.CASE_CFG) + '_2b_LNS_INITSCHEHVAC_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.lp')        
        
        t_start = time()
        self.model.optimize()
        logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule optimize takes %s s" %(time()-t_start))
             
        if self.model.getAttr(GRB.attr.Status) != self.STATUS.index('INFEASIBLE'):
            t_start = time()
            self._updMSTR_HVAC()
            logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule _updMSTR_HVAC takes: %s s" %(time()-t_start))
            
#             self.logSchedules(self.CASE_CFG + "_2c_LNS_INITSCHEHVAC")
#             self.logTemperatures(self.CASE_CFG + "_2c_LNS_INITSCHEHVAC")      
            t_start = time()      
            self.logMSTR_Schedules(self.CASE_CFG + "_2c_LNS_INITSCHE_MASTER")
            logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule logMSTR_Schedules takes: %s s" %(time()-t_start))
            
            t_start = time()
            self.logMSTR_Temperatures(self.CASE_CFG + "_2c_LNS_INITSCHEHVAC_MASTER")
            logging.info("initHVACModelNEnergyObjBasedOnInitialSchedule logMSTR_Temperatures takes: %s s" %(time()-t_start))
        else:            
            logging.error("Error! Infeasible HVAC model for the given initial schedule")
            return self.err.solver_lns_infeasible_hvac_ctrl()
         
        return self.model.getAttr(GRB.attr.ObjVal)
        
    def _createLNS_ScheduleCstr(self, locationls, slotls, mls):
        """Limit the upper bound and lower bound of x=1 which is NOT IN locationls and slotls"""
        
        self._getBDV_x_MLK_setToOne()
        for m in xrange(self.NUM_MEETING_TYPE):
            for l in xrange(len(self.BDV_x_MLK[m])):
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    [fm,fl,fk] = self._getBDV_x_MLK([m,l,k])
                        
#                     # Remove constraint on x=1 which has NOT been destroyed in the previous round, 
#                     #    but TO BE destroyed in the current round 
#                     if (self.BDV_x_MLK[m][l][k].getAttr("LB") == 1.0 and
#                         ((fl in locationls or
#                          fk in slotls or
#                          [fm, fl, fk] in mls))):
#                         self.BDV_x_MLK[m][l][k].setAttr("LB", 0.0)
#                         
                    # Add constraint on x=1 which is NOT TO BE destroyed in the current round
                    if (self.BDV_x_MLK[m][l][k].getAttr("LB") == 0.0 and
                        [fm,fl,fk] in self.milp_alloc and
                        fl not in locationls and
                        fk not in slotls and
                        [fm, fl,fk] not in mls):
                        self.BDV_x_MLK[m][l][k].setAttr("LB", 1.0)
                                
        self.model.update()
        
    def _getBDV_x_MLK_setToOne(self):
        logging.info("------------------- _getBDV_x_MLK_setToOne  Identify x=1")
        self.milp_alloc = []
        self.milp_alloc_sl = []
        self.milp_alloc_sk = []
        for m in xrange(self.NUM_MEETING_TYPE):
            for l in xrange(len(self.BDV_x_MLK[m])):
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    val = self.BDV_x_MLK[m][l][k].x                    
                    if val > self.EPSILON:
                        [fm,fl,fk] = self._getBDV_x_MLK([m,l,k]) 
                        self.milp_alloc.append([fm,fl,fk])
                        if fl not in self.milp_alloc_sl:
                            self.milp_alloc_sl.append(fl)
                        if fk not in self.milp_alloc_sk:
                            self.milp_alloc_sk.append(fk) 
        logging.info("[fm, fl, fk]: %s" %(self.milp_alloc))
        logging.info("[fl]: %s" %(self.milp_alloc_sl))
        logging.info("[fk]: %s" %(self.milp_alloc_sk))
            
    def rebuildNeighbourhood(self, runidx, locationls, slotls, mls):    
                
        self._getAllocMeetingsInLocation(locationls)
        
        if len(self.CURR_DESTROY_MTYPE) == 0:  # No meeting was scheduled in these rooms
            return self.err.solver_lns_no_meeting_destroy()
            
        self.SCHE_MODE = 1
        self._resetGurobi(runidx)            
        self._createScheduleModel()
        self._createHVACModel()
        self._createObjective()
        self.model.update()
        if self.LOG_LP:
            self.model.write('Output/EAMS_LNS_' + str(self.CASE_CFG) + '_3b_LNS_RUN_' + str(runidx) + '_'+ datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.lp')
        self.model.optimize()
         
        if self.model.getAttr(GRB.attr.Status) == self.STATUS.index('INFEASIBLE'):
            logging.error("Error! Infeasible HVAC model for the given initial schedule")
            return self.err.solver_lns_infeasible_hvac_ctrl()
        else:
            logging.info("Objective value: %g" %(self.model.getAttr(GRB.attr.ObjVal)))
            if self.LOG_MIP_EAMS:
                self.logSchedules(self.CASE_CFG + "_3c_LNS_RUN_"+ str(runidx))
                self.logTemperatures(self.CASE_CFG + "_3c_LNS_RUN_"+ str(runidx))    
            return self.model.getAttr(GRB.attr.ObjVal)
            
        
    def _getAllocMeetingsInLocation(self, locationls):  
        occls = []
        self.CURR_DESTROY_LOCATION = locationls
        for m in xrange(self.MSTR_NUM_MEETING_TYPE):
            for l in xrange(len(self.MSTR_BDV_x_MLK[m])):
                
                for dl in xrange(len(self.CURR_DESTROY_LOCATION)):
                    dr = self.CURR_DESTROY_LOCATION[dl]
                    if dr == l:
                        for k in xrange(len(self.MSTR_BDV_x_MLK[m][l])):
                            if self.MSTR_BDV_x_MLK[m][l][k] == 1:
                                occls.append([m,l,k])                                
        logging.info("Meetings to be rescheduled: %s. Total: %d" %(occls, len(occls)))
        self.CURR_DESTROY_MEETINGS = occls
        
        # Group to get MTYPE and number of MTYPE in partial schedule
        self._getMeetingType(occls)
        
    def _getMeetingType(self, occls):        
        self.CURR_DESTROY_MTYPE = []
        self.CURR_DESTROY_MTYPE_NUM = []
        
        for i in xrange(len(occls)):
            if occls[i][0] in self.CURR_DESTROY_MTYPE:
                idx = self.CURR_DESTROY_MTYPE.index(occls[i][0])
                self.CURR_DESTROY_MTYPE_NUM[idx] = self.CURR_DESTROY_MTYPE_NUM[idx] + 1
            else:
                self.CURR_DESTROY_MTYPE.append(occls[i][0])
                self.CURR_DESTROY_MTYPE_NUM.append(1)
        
        logging.info("self.CURR_DESTROY_MTYPE: %s. Total: %d" %(self.CURR_DESTROY_MTYPE, len(self.CURR_DESTROY_MTYPE)))
        logging.info("self.CURR_DESTROY_MTYPE_NUM: %s" %self.CURR_DESTROY_MTYPE_NUM)                          
        
    
    def updateNeighbourhood(self, runidx):
        self._updMSTR_Schedules()  
        self._updMSTR_HVAC()
        if self.LOG_MIP_EAMS:
            self.logMSTR_Schedules(self.CASE_CFG + "_3c_LNS_RUN_MASTER_"+ str(runidx))
            self.logMSTR_Temperatures(self.CASE_CFG + "_3c_LNS_RUN_MASTER_"+ str(runidx))
        
    
    #===========================================================================
    # Objective
    #===========================================================================    
    #===========================================================================
    # Room Usage Minimization (Scheduling) Objective
    #===========================================================================
    def _createMinRoomPerDayObjective(self):
        """Create a scheduling objective which allocate meeting into minimum number of room per day"""
        
        self._populateSlotIdxPerDay()
        logging.info("****** _createCSTR_MinRoom()  Daily Slot Index: %s" %self.k_m)
        
        start_time = time()
        self._createBAV_y_LD()        
        self._createCSTR_MinRoom()
        self._createLinearMinRoomObjective()
                    
    def _createBAV_y_LD(self):
        """For each location at day D, create an auxiliary variable"""
        
        for l in xrange(self.NUM_ROOM):
            self.BAV_y_LD.append([])
            for d in xrange(len(self.k_m)):   #TODO: hard-coded
                name = ['BAV_y_LD', str(l), str(d)]
                name = '_'.join(name)         
                self.BAV_y_LD[l].append(self.model.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=name))
             
        self.model.update()
        logging.debug("BAV_y_LD:\n %s" %self.BAV_y_LD)
        
    def _createLinearMinRoomObjective(self):
        """Create an objective to minimize number of room used """
        
        self.model.modelSense = GRB.MINIMIZE
        objective = 0     
        
        for l in xrange(self.NUM_ROOM):
            for d in xrange(len(self.k_m)):                    
                objective += self.BAV_y_LD[l][d]
                       
        self.model.setObjective(objective)
                        
    def _createCSTR_MinRoom(self):
        """Force meeting allocation into minimum number of room per day"""
        
        for m in xrange(self.NUM_MEETING_TYPE):
            # Get feasible start time from any one meeting in MLS
            mid = self.EAMS.MTYPE[m].MLS[0]                
            self.CSTR_MinRoom.append([])
            for l in xrange(self.NUM_ROOM):
                self.CSTR_MinRoom[m].append([])
                if l in self.EAMS.MR[m]:    # TODO: assume all meetings of the same type can access the same room. Re-group required if not!
                    for k in xrange(self.NUM_SLOT):                        
                        if self.EAMS.isInTimeWindows(mid,k) > 0:
                            day = self._getDayForSlotIdx(k) 
                            [om, ol, ok] = self.BDV_x_MLK_Dict[m, l, k]  
                            lcstr = self.BDV_x_MLK[om][ol][ok]
                            rcstr = self.BAV_y_LD[l][day] 
                            name = ['CSTR_MinRoom_MLK', str(m), str(l), str(k)]
                            name = '_'.join(name)
                            self.CSTR_MinRoom[m][l].append(self.model.addConstr(lcstr <= rcstr, name))
                           
        self.model.update()
        logging.debug("CSTR_MinRoom:\n %s" %self.CSTR_MinRoom)  
          
    
    def _populateSlotIdxPerDay(self):
        self.k_m = []
        d_start = -1
        d_end = -1        
        for k, v in self.EAMS.TS.iteritems():
            if (v.hour == 9 and v.minute == 0):
                if d_start == -1 and d_end == -1:
                    d_start = k 
                else:
#                     print "d_end or d_start != -1. Invalid start/end scheduling period"
                    logging.error("d_end or d_start != -1. Invalid start/end scheduling period")
                
            if (v.hour == 16 and v.minute == 30):
                if d_start != -1 and d_end == -1:
                    d_end = k
                    self.k_m.append([d_start, d_end])
                    d_start = -1
                    d_end = -1
                    
    def _getDayForSlotIdx(self, k):
        for i in xrange(len(self.k_m)):
            if k >= self.k_m[i][0] and k <= self.k_m[i][1]:
                return i
    #===========================================================================
    # Decision Variables
    #===========================================================================   
    def _createBDV_x_MLK_MT(self):
        """For each meeting type x feasible location x feasible time, create a decision variable  (M x L_m x K_m)"""
        
        for m in xrange(self.NUM_MEETING_TYPE):
            # Get feasible start time from any one meeting in MLS
            if self.SCHE_MODE == 1:
                dm = self.CURR_DESTROY_MTYPE[m]
                mid = self.EAMS.MTYPE[dm].MLS[0]
            else:
                mid = self.EAMS.MTYPE[m].MLS[0]
                
            self.BDV_x_MLK.append([])
            ml = 0
            for l in xrange(self.NUM_ROOM):
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l
                if dl in self.EAMS.MR[mid]:    # TODO: assume all meetings of the same type can access the same room. Re-group required if not!
                    self.BDV_x_MLK[m].append([])  
                    mk = 0                                      
                    for k in xrange(self.NUM_SLOT):                        
                        if self.EAMS.isInTimeWindows(mid,k) > 0:
                            logging.debug("M_L_K_%d_%d_%d = in array offset(%d, %d, %d)" %(m,l,k, m, ml, mk))
                            
                            name = ['BDV_x_MLK', str(m), str(l), str(k)]                            
                            name = '_'.join(name)         
                            self.BDV_x_MLK[m][ml].append(self.model.addVar(lb=0.0, ub=1.0, vtype=GRB.BINARY, name=name))                            
                            self.BDV_x_MLK_Dict[tuple([m,l,k])] = [m,ml,mk]                            
                            mk = mk+1
                    ml = ml+1
                
        self.model.update()                           
        logging.debug("BDV_x_MLK:\n %s" %self.BDV_x_MLK)
        logging.debug("BDV_x_MLK_Dict:\n %s" %self.BDV_x_MLK_Dict) 
    
    def _createBDV_w_LK(self):
        """For each time k, where k falls on non-standard working hour, create a decision variable  (L x K)"""
        
        for l in xrange(self.NUM_ROOM):
            self.BDV_w_LK.append([])
            mk = 0
            for k in xrange(self.NUM_SLOT):
                if self.EAMS.SH[k] == 0:
                    name = ['BDV_w_LK', str(l), str(k)]
                    name = '_'.join(name)         
                    self.BDV_w_LK[l].append(self.model.addVar(vtype=GRB.BINARY, name=name))
                    self.BDV_w_LK_Dict[tuple([l,k])] = [l,mk]
                    mk = mk+1
    
        self.model.update()
        logging.debug("BDV_w_LK:\n %s" %self.BDV_w_LK)
        logging.debug("BDV_w_LK_Dict:\n %s" %self.BDV_w_LK_Dict)
        
    def _createCDV_SupplyAirTemperature(self):
        """For each location at each timestep, create a decision variable of TSA, i.e. TSA(k,l)"""
        
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        for l in xrange(self.NUM_ROOM):
            self.CDV_T_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CDV_T_SA_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                self.CDV_T_SA_LK[l].append(self.model.addVar(lb=0, ub=T_SA_UB, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CDV_T_SA_LK:\n %s" %self.CDV_T_SA_LK)
        
    
    def _createCDV_AirMassFlowRate(self):
        """For each location at each timestep, create a decision variable of aSA, i.e. aSA(k,l)"""
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        for l in xrange(self.NUM_ROOM):
            self.CDV_A_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CDV_A_SA_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                self.CDV_A_SA_LK[l].append(self.model.addVar(lb=0, ub=A_SA_UB, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CDV_A_SA_LK:\n %s" %self.CDV_A_SA_LK)
        
    #===========================================================================
    # Energy Minimization Objective
    #===========================================================================
    def _createObjective(self):
        """Create an energy consumption minimization objective """
        
        self.model.modelSense = GRB.MINIMIZE
        objective = 0
        for l in xrange(self.NUM_ROOM):
            for k in xrange(self.NUM_SLOT):
                objective += self.CAV_E_FAN_LK[l][k] + self.CAV_E_CONDITIONING_LK[l][k] + self.CAV_E_HEATING_LK[l][k]
    
        self.model.setObjective(objective)
        
    #===========================================================================
    # Auxiliary Variables
    #===========================================================================
    
    #===========================================================================
    # Auxiliary Variables: Room Alloc
    #===========================================================================   
    def _createBAV_z_LK(self):
        """For each location at timeslot k, create an auxiliary variable"""
        
        for l in xrange(self.NUM_ROOM):
            self.BAV_z_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['BAV_z_LK', str(l), str(k)]
                name = '_'.join(name)         
#                self.BAV_z_LK[l].append(self.model.addVar(vtype=GRB.BINARY, name=name))
                self.BAV_z_LK[l].append(self.model.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=name))
             
        self.model.update()
        logging.debug("BAV_z_LK:\n %s" %self.BAV_z_LK)
         
    def _createDAV_Attendee_LK(self):
        """For each location at each timestamp, create an auxiliary variable representing number of attendee"""
         
        for l in xrange(self.NUM_ROOM):
            self.DAV_Attendee_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['DAV_Attendee_LK', str(l), str(k)]
                name = '_'.join(name)         
#                self.DAV_Attendee_LK[l].append(self.model.addVar(lb=0, vtype=GRB.INTEGER, name=name))
                self.DAV_Attendee_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))                 
        self.model.update()
        logging.debug("DAV_Attendee_LK:\n %s" %self.DAV_Attendee_LK)
        
    #===========================================================================
    # Auxiliary Variables: HVAC
    #===========================================================================
    def _createCAV_RoomTemperature(self):
        """For each location at each timestep, create an auxiliary variable of room temperature T(k, l)"""
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_LK:\n %s" %self.CAV_T_LK)
        
    def _createCAV_T_z1_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z1_l_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_NOT_EXIST)):
                                    
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_z1_l_LK', str(l), str(k)]                
                    name = '_'.join(name)   
                    self.CAV_T_z1_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z1_l_LK:\n %s" %self.CAV_T_z1_l_LK)
        
    def _createCAV_T_z2_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z2_l_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_NOT_EXIST)):
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_z2_l_LK', str(l), str(k)]
                    name = '_'.join(name)   
                    self.CAV_T_z2_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z2_l_LK:\n %s" %self.CAV_T_z2_l_LK)
        
    def _createCAV_T_z3_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z3_l_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_NOT_EXIST)):
            
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_z3_l_LK', str(l), str(k)]
                    name = '_'.join(name)                            
                    self.CAV_T_z3_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z3_l_LK:\n %s" %self.CAV_T_z3_l_LK)
        
    def _createCAV_T_z4_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z4_l_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_NOT_EXIST)):
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_z4_l_LK', str(l), str(k)]
                    name = '_'.join(name)  
                    self.CAV_T_z4_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z4_l_LK:\n %s" %self.CAV_T_z4_l_LK)
        
    def _createCAV_T_l_z1(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z1_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_NOT_EXIST)):
            
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_l_z1_LK', str(l), str(k)]                
                    name = '_'.join(name)       
                    self.CAV_T_l_z1_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z1_LK:\n %s" %self.CAV_T_l_z1_LK)
        
    def _createCAV_T_l_z2(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z2_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_NOT_EXIST)):
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_l_z2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    self.CAV_T_l_z2_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z2_LK:\n %s" %self.CAV_T_l_z2_LK)
        
    def _createCAV_T_l_z3(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z3_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_NOT_EXIST)):
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_l_z3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    self.CAV_T_l_z3_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z3_LK:\n %s" %self.CAV_T_l_z3_LK)
        
    def _createCAV_T_l_z4(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z4_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_NOT_EXIST)):
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_l_z4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    self.CAV_T_l_z4_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z4_LK:\n %s" %self.CAV_T_l_z4_LK)
        
    def _createCAV_T_l_f(self):
        
        if (self.USE_REDUCED_MODEL == 0):
            for l in xrange(self.NUM_ROOM):
                self.CAV_T_l_f_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_l_f_LK', str(l), str(k)]
                    name = '_'.join(name)         
                    
                    self.CAV_T_l_f_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                    
            self.model.update()
            logging.debug("CAV_T_l_f_LK:\n %s" %self.CAV_T_l_f_LK)
        
    def _createCAV_T_l_c(self):
        
        if (self.USE_REDUCED_MODEL == 0):
            for l in xrange(self.NUM_ROOM):
                self.CAV_T_l_c_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CAV_T_l_c_LK', str(l), str(k)]
                    name = '_'.join(name)         
                    
                    self.CAV_T_l_c_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                    
            self.model.update()
            logging.debug("CAV_T_l_c_LK:\n %s" %self.CAV_T_l_c_LK)
        
    def _createCAV_A_SA_T_z_LK(self):
        """For each location at each timestep, create an auxiliary variable of aT(SA, z)"""
        for l in xrange(self.NUM_ROOM):
            self.CAV_A_SA_T_z_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_A_SA_T_z_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_A_SA_T_z_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_A_SA_T_z_LK:\n %s" %self.CAV_A_SA_T_z_LK)
        
    def _createCAV_A_SA_T_SA_LK(self):
        """For each location at each timestep, create an auxiliary variable of aT(SA, SA)"""
        for l in xrange(self.NUM_ROOM):
            self.CAV_A_SA_T_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_A_SA_T_SA_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_A_SA_T_SA_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_A_SA_T_SA_LK:\n %s" %self.CAV_A_SA_T_SA_LK)
    
    #===========================================================================
    # Auxiliary Variables: Energy Consumption
    #===========================================================================
    def _createCAV_EnergyConsumption_Fan(self):
        """For each location at each timestep, create an auxiliary variable of e_fan(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CAV_E_FAN_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_E_FAN_LK', str(l), str(k)]
                name = '_'.join(name)         
                self.CAV_E_FAN_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_E_FAN_LK:\n %s" %self.CAV_E_FAN_LK)
        
    def _createCAV_EnergyConsumption_Conditioning(self):
        """For each location at each timestep, create an auxiliary variable of e_conditioning(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CAV_E_CONDITIONING_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_E_CONDITIONING_LK', str(l), str(k)]
                name = '_'.join(name)         
                self.CAV_E_CONDITIONING_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_E_CONDITIONING_LK:\n %s" %self.CAV_E_CONDITIONING_LK)
    
    def _createCAV_EnergyConsumption_Heating(self):
        """For each location at each timestep, create an auxiliary variable of e_heating(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CAV_E_HEATING_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_E_HEATING_LK', str(l), str(k)]
                name = '_'.join(name)         
                self.CAV_E_HEATING_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_E_HEATING_LK:\n %s" %self.CAV_E_HEATING_LK)
        
    #===========================================================================
    # Constraints
    #===========================================================================   
    
    #===========================================================================
    # Constraints: Room Alloc Based on Meeting Type
    #===========================================================================  
    def _createCSTR_Schedule_Once_MT(self):
        """Every meeting type must be scheduled to start at one feasible location exactly once within their respective time window."""
        
        for m in xrange(self.NUM_MEETING_TYPE):   
            if self.SCHE_MODE == 1:
                num_meeting = self.CURR_DESTROY_MTYPE_NUM[m]
            else:
                num_meeting = len(self.EAMS.MTYPE[m].MLS)
                
            self.CSTR_Schedule_Once_M.append([])                
            lcstr = 0
            for l in xrange(len(self.BDV_x_MLK[m])):                                    
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    lcstr += self.BDV_x_MLK[m][l][k] 
            
            name = ['CSTR_Schedule_Once_M', str(m)]
            name = '_'.join(name)
            self.CSTR_Schedule_Once_M[m].append(self.model.addConstr(lcstr == num_meeting, name))
                 
        self.model.update()
        logging.debug("CSTR_Schedule_Once_M:\n %s" %self.CSTR_Schedule_Once_M)  
        
    def _createCSTR_LocationTimeOccupied_MT(self):
        """Set BAV_z_LK=1 at all time periods k if meeting type m is allocated in room L"""
        
        for k in xrange(self.NUM_SLOT):             
            lcstr = []
            for l in xrange(self.NUM_ROOM):
                lcstr.append([])
                lcstr[l] = 0
                                     
            for m in xrange(self.NUM_MEETING_TYPE):
                # Get feasible start time from any one meeting in MLS
                if self.SCHE_MODE == 1:
                    dm = self.CURR_DESTROY_MTYPE[m]
                    mid = self.EAMS.MTYPE[dm].MLS[0]
                else:
                    mid = self.EAMS.MTYPE[m].MLS[0]
                   
                k_m = []
                k_m = self.EAMS.getFeasibleStartTime(mid, k)
                if k_m:
                    logging.debug("Meeting Type %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
                    for l in xrange(self.NUM_ROOM):
                        if self.SCHE_MODE == 1:
                            dl = self.CURR_DESTROY_LOCATION[l]
                        else:
                            dl = l
                        if dl in self.EAMS.MR[mid]:  #TODO: currently assume all meetings of the same type can use the same room! Need to re-group if not (_populateMeetingClique) !
                            for i in xrange(len(k_m)):
                                mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
#                                 logging.debug("MLK_%s" %mlk)                            
                                lcstr[l] += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                            
            self.CSTR_LocationTimeOccupied.append([])
            for l in xrange(self.NUM_ROOM):  
                if lcstr[l]:
                    rcstr = self.BAV_z_LK[l][k]
#                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
                    name = ['CSTR_LocationTimeOccupied_KL', str(k), str(l)]
                    name = '_'.join(name)
                    self.CSTR_LocationTimeOccupied[k].append(self.model.addConstr(lcstr[l] <= rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_LocationTimeOccupied:\n %s" %self.CSTR_LocationTimeOccupied)
           
    def _createCSTR_NumAttendee_MT(self):
        """For each meeting type, represent number of attendee as a unique constraint. Note: Number of attendee is grouped by 5, 15, 30 people."""
        
        for k in xrange(self.NUM_SLOT):             
            lcstr = []
            for l in xrange(self.NUM_ROOM):
                lcstr.append([])
                lcstr[l] = 0
                                     
            for m in xrange(self.NUM_MEETING_TYPE):   
                # Get feasible start time from any one meeting in MLS
                if self.SCHE_MODE == 1:
                    dm = self.CURR_DESTROY_MTYPE[m]
                    mid = self.EAMS.MTYPE[dm].MLS[0]
                else:
                    mid = self.EAMS.MTYPE[m].MLS[0]
                     
                k_m = []
                k_m = self.EAMS.getFeasibleStartTime(mid, k)
                if k_m:
#                     logging.debug("Meeting %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
                    for l in xrange(self.NUM_ROOM):
                        if self.SCHE_MODE == 1:
                            dl = self.CURR_DESTROY_LOCATION[l]
                        else:
                            dl = l
                        if dl in self.EAMS.MR[mid]:    #TODO: currently assume all meetings of the same type can use the same room! Need to re-group if not (_populateMeetingClique) !
                            for i in xrange(len(k_m)):
                                mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
#                                 logging.debug("MLK_%s" %mlk)                            
#                                 lcstr[l] += len(self.EAMS.ML[m].Attendees)*self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                                lcstr[l] += self.EAMS.MTYPE[m].MA*self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                            
            self.CSTR_NumAttendee.append([])
            for l in xrange(self.NUM_ROOM):
                rcstr = self.DAV_Attendee_LK[l][k]
#                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
                name = ['CSTR_NumAttendee_LK', str(l), str(k)]
                name = '_'.join(name)  
                if lcstr[l]:
                    self.CSTR_NumAttendee[k].append(self.model.addConstr(lcstr[l] == rcstr, name))
                else:
                    self.CSTR_NumAttendee[k].append(self.model.addConstr(0 == rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_NumAttendee:\n %s" %self.CSTR_NumAttendee)
        
    def _createCSTR_AttendeeConflict_MT(self):
        """Meetings Types which have the same attendee(s) should not be allocated into the same time period"""
        
        # CMT has duplicate MT set for different attendee, create a unique list.  
        #  {'1068': [1, 2], '6153': [0, 1, 2], '2425': [0, 1], '895': [0, 1]}
        #  -->  [1,2], [0,1,2], [0,1]   
        uniq_mtls = []
        mtls = self.EAMS.CMT.values() 
        for s in xrange(len(mtls)):
            if mtls[s] not in uniq_mtls:
                uniq_mtls.append(mtls[s]) 
        logging.debug("************************************** uniq_mtls:%s" %uniq_mtls)
        
        if self.SCHE_MODE == 1:
#             Given  uniq_mtls:[[1, 4], [10, 18, 27], [0, 4], [20, 29], [7, 27], [9, 19], [11, 30], [6, 13], [17, 33], [2, 33], [16, 25]]
#                    self.CURR_DESTROY_MTYPE: [1, 8, 12, 14, 17, 33]
#             Check if any combinations in uniq_mtls exists in CURR_DESTROY_MTYPE.
#             In this example:  uniq_mtls:[[17, 33]]
            
            logging.debug("self.CURR_DESTROY_MTYPE: %s" %(self.CURR_DESTROY_MTYPE))
            new_uniq_mtls = []
            for sublist in uniq_mtls:
                new_uniq_mtls.append(list(set(sublist).intersection(set(self.CURR_DESTROY_MTYPE))))            
            logging.debug("new_uniq_mtls: %s" %(new_uniq_mtls))
            uniq_mtls = new_uniq_mtls  # overwrite uniq_mtls
                
        for k in xrange(self.NUM_SLOT):
            self.CSTR_AttendeeConflict.append([])
            for s in xrange(len(uniq_mtls)):      #TODO: this loop can be improved!      
                mts = uniq_mtls[s]
#                 logging.debug("Conflict Meeting Types:%s" %mts)
                om = []
                for mt in xrange(len(mts)):
                    mtid = mts[mt]     
                    m = self.EAMS.MTYPE[mtid].MLS[0] # to get the time window of MTYPE, so simply get the first meeting in MLS
                    if self.EAMS.isInTimeWindows(m,k) > 0:   
                        logging.debug("++ k: %d" %k)    
                        logging.debug("----%s" %self.EAMS.getFeasibleStartTime(m, k))
                        
                        if self.SCHE_MODE == 1:
                            did = self.CURR_DESTROY_MTYPE.index(mtid)
                            om.append([did, self.EAMS.getFeasibleStartTime(m, k)])
                        else:
                            om.append([mtid, self.EAMS.getFeasibleStartTime(m, k)])
                            
                if len(om)>1: # has conflict
                        logging.debug("om: %s" %om)
                        lcstr = 0
                        for j in xrange(len(om)):    
                            logging.debug("om[%d]: %s" %(j,om[j]))    
                            logging.debug("om[%d][0]: %s" %(j, om[j][0]))
                            mk = om[j][1]
                            for p in xrange(len(mk)):
                                logging.debug("om[%d][1] [%d]: %s" %(j, p, mk[p]))      
                                         
                                for l in xrange(self.NUM_ROOM): #TODO: BUGGY!! need to map this for SCHE_MODE==1 
                                    mlk = self.BDV_x_MLK_Dict.get(tuple([om[j][0], l, mk[p]]))    
                                    logging.debug("MLK_%s" %mlk)
                                    if mlk:
                                        lcstr += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                        logging.debug(lcstr)
                        name = ['CSTR_AttendeeConflict_K_CM', str(k), str(m)]
                        name = '_'.join(name)
                        self.CSTR_AttendeeConflict[k].append(self.model.addConstr(lcstr <= 1, name))
                    
        self.model.update()
        logging.debug("CSTR_AttendeeConflict:\n %s" %self.CSTR_AttendeeConflict)

    #===========================================================================
    # Constraints: HVAC
    #===========================================================================
    def _createCSTR_SupplyAirTemperature_LB_noStandbyMode(self):
        for l in xrange(self.NUM_ROOM):        
            self.CSTR_T_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_SA_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                lcstr = self.CDV_T_SA_LK[l][k]

                if self.EAMS.SH[k] == 1:
                    rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)
                    self.CSTR_T_SA_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                else:
                    self.CSTR_T_SA_LK[l].append(self.model.addConstr(lcstr == 0, name))
             
        self.model.update()
        logging.debug("CSTR_T_SA_LK:\n %s" %self.CSTR_T_SA_LK)
                
    def _createCSTR_SupplyAirTemperature_LB_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):        
            self.CSTR_T_SA_LB_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_SA_LB_LK', str(l), str(k)]
                name = '_'.join(name)               
                 
                lcstr = self.CDV_T_SA_LK[l][k]
                if self.EAMS.SH[k] == 1:
                    rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)
                    self.CSTR_T_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                else:
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) * self.BDV_w_LK[lk[0]][lk[1]]
                    self.CSTR_T_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                             
        self.model.update()
        logging.debug("CSTR_T_SA_LB_LK:\n %s" %self.CSTR_T_SA_LB_LK)
        
    def _createCSTR_SupplyAirTemperature_UB_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):        
            self.CSTR_T_SA_UB_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_SA_UB_LK', str(l), str(k)]
                name = '_'.join(name)               
                 
                lcstr = self.CDV_T_SA_LK[l][k]
                # Not necessary to set the upper bound of SH==1, as it is the same as T_SA default UB
                if self.EAMS.SH[k] == 0: 
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = float(self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH) * self.BDV_w_LK[lk[0]][lk[1]]
                    self.CSTR_T_SA_UB_LK[l].append(self.model.addConstr(lcstr <= rcstr, name))
                             
        self.model.update()
        logging.debug("CSTR_T_SA_UB_LK:\n %s" %self.CSTR_T_SA_UB_LK)
        
#--------------------------------------    
    def _createCSTR_SupplyAirFlowRate_LB_noStandbyMode(self):
        """For each location at each timestep, create a constraint for lower bound of air mass flow rate"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_A_SA_LB_LK.append([])
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_A_SA_LB_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                lcstr = self.CDV_A_SA_LK[l][k]
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l                
                rcstr = self._get_A_SA_LB(dl,k)
                
                if self.EAMS.SH[k] == 1:                    
                    self.CSTR_A_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                else:
                    self.CSTR_A_SA_LB_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_A_SA_LB_LK:\n %s" %self.CSTR_A_SA_LB_LK)
        
    def _createCSTR_SupplyAirFlowRate_LB_hasStandbyMode(self):
        """For each location at each timestep, create a constraint for lower bound of air mass flow rate"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_A_SA_LB_LK.append([])
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_A_SA_LB_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                lcstr = self.CDV_A_SA_LK[l][k]
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l
                
                if self.EAMS.SH[k] == 1:
                    rcstr = self._get_A_SA_LB(dl,k)
                else: 
                    #TODO:  as long as ASA_LB for sh[k]=0 is set to 0, this cstr can be removed.
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = self._get_A_SA_LB(dl,k) * self.BDV_w_LK[lk[0]][lk[1]]
                self.CSTR_A_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_A_SA_LB_LK:\n %s" %self.CSTR_A_SA_LB_LK)
        
    def _createCSTR_SupplyAirFlowRate_UB_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_A_SA_UB_LK.append([])            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_A_SA_UB_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                lcstr = self.CDV_A_SA_LK[l][k]
                if self.EAMS.SH[k] == 0: # Not necessary to set the upper bound of SH==1, as it is the same as A_SA default UB
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX * self.BDV_w_LK[lk[0]][lk[1]]
                    self.CSTR_A_SA_UB_LK[l].append(self.model.addConstr(lcstr <= rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_A_SA_UB_LK:\n %s" %self.CSTR_A_SA_UB_LK)

#--------------------------------------             
    def _createCSTR_RoomTemperature_LB(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_LK_lb.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_LK_lb', str(l), str(k)]
                name = '_'.join(name)                
                 
                lcstr = self.CAV_T_LK[l][k]
                rcstr = float(self.EAMS.TEMPERATURE_UNOCC_MIN) + (float(self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_INCR) * self.BAV_z_LK[l][k])   
                self.CSTR_T_LK_lb[l].append(self.model.addConstr(lcstr >= rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_LK_lb:\n %s" %self.CSTR_T_LK_lb)
        
    def _createCSTR_RoomTemperature_UB(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_LK_ub.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_LK_ub', str(l), str(k)]
                name = '_'.join(name)                
                 
                lcstr = self.CAV_T_LK[l][k]
                rcstr = float(self.EAMS.TEMPERATURE_UNOCC_MAX) - (float(self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_DECR)*self.BAV_z_LK[l][k]) 
                self.CSTR_T_LK_ub[l].append(self.model.addConstr(lcstr <= rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_LK_ub:\n %s" %self.CSTR_T_LK_ub)
    
    def _createCSTR_RoomTemperature(self):
        """For each location at each timestep, create a constraint for room temperature T(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            A = self.EAMS.getRoomThermalConfig(dl, "C")
            B1 =  self.EAMS.getRoomThermalConfig(dl, "Rij")
            B2 =  self.EAMS.getRoomThermalConfig(dl, "Rik")
            B3 =  self.EAMS.getRoomThermalConfig(dl, "Ril")
            B4 =  self.EAMS.getRoomThermalConfig(dl, "Rio")
            B5 =  self.EAMS.getRoomThermalConfig(dl, "Rif")
            B6 =  self.EAMS.getRoomThermalConfig(dl, "Ric")            
            #TODO: For the moment, only 1 wall could have window. Test with more windows
            B7 = self.EAMS.getRoomThermalConfig(dl, "Rwij")            
            C = self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE            
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / A            
            E1 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B1)
            E2 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B2)
            E3 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B3)
            E4 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B4)
            E5 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B5)
            E6 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B6)
            E7 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B7)
            F = D * self.EAMS.OCCUPANT_SENSIBLE_HEAT_GAIN
                
            for k in xrange(self.NUM_SLOT):          
                name = ['CSTR_T_LK', str(l), str(k)]
                name = '_'.join(name)
                
                if k != 0:
                    
                    if self.USE_REDUCED_MODEL == 1:
                        BG = 0
                        EG = 0
                        if ((self.EAMS.RNL[dl][0] == self.N_OUTDOOR) or (self.EAMS.RNL[dl][0] == self.N_NOT_EXIST)):
                            BG += (self.CAV_T_LK[l][k-1] / B1)   
                            EG += (E1 * self.CAV_T_l_z1_LK[l][k-1])
                                        
                        if ((self.EAMS.RNL[dl][1] == self.N_OUTDOOR) or (self.EAMS.RNL[dl][1] == self.N_NOT_EXIST)):
                            BG += (self.CAV_T_LK[l][k-1] / B2)   
                            EG += (E2 * self.CAV_T_l_z2_LK[l][k-1])
                                                    
                        if ((self.EAMS.RNL[dl][2] == self.N_OUTDOOR) or (self.EAMS.RNL[dl][2] == self.N_NOT_EXIST)):
                            BG += (self.CAV_T_LK[l][k-1] / B3)     
                            EG += (E3 * self.CAV_T_l_z3_LK[l][k-1])
                                                
                        if ((self.EAMS.RNL[dl][3] == self.N_OUTDOOR) or (self.EAMS.RNL[dl][3] == self.N_NOT_EXIST)):
                            BG += (self.CAV_T_LK[l][k-1] / B4)
                            EG += (E4 * self.CAV_T_l_z4_LK[l][k-1])
                            
                        rcstr = (
                                 (self.CAV_T_LK[l][k-1] - 
                                 (D *
                                  (BG +                                
                                   (self.CAV_T_LK[l][k-1] / B7) +
                                  (C * self.CAV_A_SA_T_z_LK[l][k-1])
                                  )
                                 )
                                 ) + 
                                 EG +
                                 (E7 * float(self.EAMS.OAT.values()[k-1])) +                             
                                 (F * self.DAV_Attendee_LK[l][k-1]) + 
                                 (D * C * self.CAV_A_SA_T_SA_LK[l][k-1]))
                            
                    else:
                        rcstr = (
                                 (self.CAV_T_LK[l][k-1] - 
                                 (D *
                                  (
                                  (self.CAV_T_LK[l][k-1] / B1) +
                                (self.CAV_T_LK[l][k-1] / B2) +
                                (self.CAV_T_LK[l][k-1] / B3) +
                                (self.CAV_T_LK[l][k-1] / B4) +
                                (self.CAV_T_LK[l][k-1] / B5) +
                                (self.CAV_T_LK[l][k-1] / B6) +
                                (self.CAV_T_LK[l][k-1] / B7) +
                                  (C * self.CAV_A_SA_T_z_LK[l][k-1])
                                  )
                                 )
                                 ) + 
                                 (E1 * self.CAV_T_l_z1_LK[l][k-1]) +
                                (E2 * self.CAV_T_l_z2_LK[l][k-1]) +
                                (E3 * self.CAV_T_l_z3_LK[l][k-1]) +
                                (E4 * self.CAV_T_l_z4_LK[l][k-1]) +
                                (E5 * self.CAV_T_l_f_LK[l][k-1]) +
                                (E6 * self.CAV_T_l_c_LK[l][k-1]) +
                                (E7 * float(self.EAMS.OAT.values()[k-1])) +                             
                                 (F * self.DAV_Attendee_LK[l][k-1]) + 
                                 (D * C * self.CAV_A_SA_T_SA_LK[l][k-1]))
                    
                else: # no occupant at previous session (k=-1)
                    rcstr = self.EAMS.INITIAL_TEMPERATURE
                
                lcstr = self.CAV_T_LK[l][k]         
                self.CSTR_T_LK[l].append(self.model.addConstr(lcstr==rcstr, name))
                
        self.model.update()
        logging.debug("CSTR_T_LK:\n %s" %self.CSTR_T_LK)
        
   
    def _createCSTR_T_z1_l(self):        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z1_l_LK.append([])      
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l        
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_NOT_EXIST)):
                
                nz = self.EAMS.RNL[dl][0]
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cij")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rji")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rimj")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cij") * self.EAMS.getRoomThermalConfig(dl, "Rimj"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cij") * self.EAMS.getRoomThermalConfig(dl, "Rji"))
                H = 1-(A*(B+C)) 
                
                logging.debug("Cij = %s" %(self.EAMS.getRoomThermalConfig(dl, "Cij")))  
                logging.debug("A = %s" %(A))
                logging.debug("B = %s" %(B))
                logging.debug("C = %s" %(C))
                logging.debug("H = %s" %(H))
                                                     
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_z1_l_LK', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    if k != 0:
                        if nz == self.N_OUTDOOR:
                            F = float(self.EAMS.OAT.values()[k-1])
                        elif nz == self.N_NOT_EXIST:
                            F = self.CAV_T_LK[l][k-1]
                        else:
                            F = self.CAV_T_LK[nz][k-1]
                        
                        G = self.EAMS.getRoomSolarGain(k-1, dl, 0)
                            
                        rcstr = (
                                 (H * self.CAV_T_z1_l_LK[l][k-1]) +
                                 (D * self.CAV_T_l_z1_LK[l][k-1]) +
                                 (E * F) +
                                 (A * G)
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE
     
                    lcstr = self.CAV_T_z1_l_LK[l][k]                 
                    self.CSTR_T_z1_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                  
        self.model.update()
        logging.debug("CSTR_T_z1_l_LK:\n %s" %self.CSTR_T_z1_l_LK)
        
    def _createCSTR_T_l_z1(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z1_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l     
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][0] == self.N_NOT_EXIST)):
            
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cji")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rij")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rimj")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cji") * self.EAMS.getRoomThermalConfig(dl, "Rij"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cji") * self.EAMS.getRoomThermalConfig(dl, "Rimj"))
                
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_l_z1_LK', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    if k != 0:    
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_l_z1_LK[l][k-1]) +
                                 (D * self.CAV_T_LK[l][k-1]) +
                                 (E * self.CAV_T_z1_l_LK[l][k-1])
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE 
                    
                    lcstr = self.CAV_T_l_z1_LK[l][k]
                    self.CSTR_T_l_z1_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
        self.model.update()
        logging.debug("CSTR_T_l_z1_LK:\n %s" %self.CSTR_T_l_z1_LK)
        
    def _createCSTR_T_z2_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z2_l_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l     
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_NOT_EXIST)):
            
                nz = self.EAMS.RNL[dl][1]
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cik")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rki")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rimk")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cik") * self.EAMS.getRoomThermalConfig(dl, "Rimk"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cik") * self.EAMS.getRoomThermalConfig(dl, "Rki"))
                                         
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_z2_l_LK', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    if k != 0:
                        if nz == self.N_OUTDOOR:
                            F = float(self.EAMS.OAT.values()[k-1])
                        elif nz == self.N_NOT_EXIST:
                            F = self.CAV_T_LK[l][k-1]
                        else:
                            F = self.CAV_T_LK[nz][k-1]
                        
                        G = self.EAMS.getRoomSolarGain(k-1, dl, 1)
                            
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_z2_l_LK[l][k-1]) +
                                 (D * self.CAV_T_l_z2_LK[l][k-1]) +
                                 (E * F) +
                                 (A * G)
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE
                        
                    lcstr = self.CAV_T_z2_l_LK[l][k]
                    self.CSTR_T_z2_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
        self.model.update()
        logging.debug("CSTR_T_z2_l_LK:\n %s" %self.CSTR_T_z2_l_LK)
        
    def _createCSTR_T_l_z2(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z2_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l     
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][1] == self.N_NOT_EXIST)):
            
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cki")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rik")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rimk")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cki") * self.EAMS.getRoomThermalConfig(dl, "Rik"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cki") * self.EAMS.getRoomThermalConfig(dl, "Rimk"))
                
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_l_z2_LK', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    if k != 0:    
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_l_z2_LK[l][k-1]) +
                                 (D * self.CAV_T_LK[l][k-1]) +
                                 (E * self.CAV_T_z2_l_LK[l][k-1])
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE       
                     
                    lcstr = self.CAV_T_l_z2_LK[l][k]
                    self.CSTR_T_l_z2_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
        self.model.update()
        logging.debug("CSTR_T_l_z2_LK:\n %s" %self.CSTR_T_l_z2_LK)
        
    def _createCSTR_T_z3_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z3_l_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l     
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_NOT_EXIST)):
            
                nz = self.EAMS.RNL[dl][2]
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cil")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rli")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Riml")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cil") * self.EAMS.getRoomThermalConfig(dl, "Riml"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cil") * self.EAMS.getRoomThermalConfig(dl, "Rli"))
          
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_z3_l_LK', str(l), str(k)]
                    name = '_'.join(name)        
                    
                    if k != 0:
                        if nz == self.N_OUTDOOR:
                            F = float(self.EAMS.OAT.values()[k-1])
                        elif nz == self.N_NOT_EXIST:
                            F = self.CAV_T_LK[l][k-1]
                        else:
                            F = self.CAV_T_LK[nz][k-1]
                        
                        G = self.EAMS.getRoomSolarGain(k-1, dl, 2)
                            
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_z3_l_LK[l][k-1]) +
                                 (D * self.CAV_T_l_z3_LK[l][k-1]) +
                                 (E * F) +
                                 (A * G)
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE 
                     
                    lcstr = self.CAV_T_z3_l_LK[l][k]                
                    self.CSTR_T_z3_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
        self.model.update()
        logging.debug("CSTR_T_z3_l_LK:\n %s" %self.CSTR_T_z3_l_LK)
        
    def _createCSTR_T_l_z3(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z3_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l     
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][2] == self.N_NOT_EXIST)):
            
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cli")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Ril")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Riml")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cli") * self.EAMS.getRoomThermalConfig(dl, "Ril"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cli") * self.EAMS.getRoomThermalConfig(dl, "Riml"))
                
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_l_z3_LK', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    if k != 0:    
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_l_z3_LK[l][k-1]) +
                                 (D * self.CAV_T_LK[l][k-1]) +
                                 (E * self.CAV_T_z3_l_LK[l][k-1])
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE       
                     
                    lcstr = self.CAV_T_l_z3_LK[l][k]
                    self.CSTR_T_l_z3_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
        self.model.update()
        logging.debug("CSTR_T_l_z3_LK:\n %s" %self.CSTR_T_l_z3_LK)
             
    def _createCSTR_T_z4_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z4_l_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l     
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_NOT_EXIST)):
            
                nz = self.EAMS.RNL[dl][3]
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cio")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Roi")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rimo")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cio") * self.EAMS.getRoomThermalConfig(dl, "Rimo"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cio") * self.EAMS.getRoomThermalConfig(dl, "Roi"))
          
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_z4_l_LK', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    if k != 0:
                        if nz == self.N_OUTDOOR:
                            F = float(self.EAMS.OAT.values()[k-1])
                        elif nz == self.N_NOT_EXIST:
                            F = self.CAV_T_LK[l][k-1]
                        else:
                            F = self.CAV_T_LK[nz][k-1]
                        
                        G = self.EAMS.getRoomSolarGain(k-1, dl, 3)
                            
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_z4_l_LK[l][k-1]) +
                                 (D * self.CAV_T_l_z4_LK[l][k-1]) +
                                 (E * F) +
                                 (A * G)
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE 
                        
                    lcstr = self.CAV_T_z4_l_LK[l][k]                
                    self.CSTR_T_z4_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
        self.model.update()
        logging.debug("CSTR_T_z4_l_LK:\n %s" %self.CSTR_T_z4_l_LK)
        
    def _createCSTR_T_l_z4(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z4_LK.append([])
            
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l 
            
            if ((self.USE_REDUCED_MODEL == 0) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_OUTDOOR) or
                (self.USE_REDUCED_MODEL == 1 and self.EAMS.RNL[dl][3] == self.N_NOT_EXIST)):
            
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Coi")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rio")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rimo")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Coi") * self.EAMS.getRoomThermalConfig(dl, "Rio"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Coi") * self.EAMS.getRoomThermalConfig(dl, "Rimo"))
                
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_l_z4_LK', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    if k != 0:    
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_l_z4_LK[l][k-1]) +
                                 (D * self.CAV_T_LK[l][k-1]) +
                                 (E * self.CAV_T_z4_l_LK[l][k-1])
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE                    
                     
                    lcstr = self.CAV_T_l_z4_LK[l][k]                
                    self.CSTR_T_l_z4_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
        self.model.update()
        logging.debug("CSTR_T_l_z4_LK:\n %s" %self.CSTR_T_l_z4_LK)
        
    def _createCSTR_T_l_f(self):
        
        if (self.USE_REDUCED_MODEL == 0):
            for l in xrange(self.NUM_ROOM):
                self.CSTR_T_l_f_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
            
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cif")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rif")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rfi")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cif") * self.EAMS.getRoomThermalConfig(dl, "Rif"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cif") * self.EAMS.getRoomThermalConfig(dl, "Rfi"))
                F = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cfi")
           
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_l_f_LK', str(l), str(k)]
                    name = '_'.join(name)                
                    
                    G = self.EAMS.getRoomSolarGain(k-1, dl, 4)
                    
                    if k != 0:    
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_l_f_LK[l][k-1]) +
                                 (D * self.CAV_T_LK[l][k-1]) +
                                 (E * self.CAV_T_LK[l][k-1]) +
                                 (F * G)
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE     
                    
                    lcstr = self.CAV_T_l_f_LK[l][k]
                    self.CSTR_T_l_f_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
            self.model.update()
            logging.debug("CSTR_T_l_f_LK:\n %s" %self.CSTR_T_l_f_LK)
        
    def _createCSTR_T_l_c(self):
        
        if (self.USE_REDUCED_MODEL == 0):
            for l in xrange(self.NUM_ROOM):
                self.CSTR_T_l_c_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                
                A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(dl, "Cic")
                B = float(1)/self.EAMS.getRoomThermalConfig(dl, "Ric")
                C = float(1)/self.EAMS.getRoomThermalConfig(dl, "Rci")
                D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cic") * self.EAMS.getRoomThermalConfig(dl, "Ric"))
                E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(dl, "Cic") * self.EAMS.getRoomThermalConfig(dl, "Rci"))
                
                for k in xrange(self.NUM_SLOT):                
                    name = ['CSTR_T_l_c_LK', str(l), str(k)]
                    name = '_'.join(name)             
                    
                    if k != 0:    
                        rcstr = (
                                 ((1-A*(B+C))*self.CAV_T_l_c_LK[l][k-1]) +
                                 (D * self.CAV_T_LK[l][k-1]) +
                                 (E * self.CAV_T_LK[l][k-1])
                                 )
                    else:
                        rcstr = self.EAMS.INITIAL_TEMPERATURE      
                     
                    lcstr = self.CAV_T_l_c_LK[l][k]
                    self.CSTR_T_l_c_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                 
            self.model.update()
            logging.debug("CSTR_T_l_c_LK:\n %s" %self.CSTR_T_l_c_LK)        
        
#-----------------------------------
        
    def _createCSTR_A_SA_T_SA_1_LK_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_1_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    T_SA_LB = self._get_T_SA_LB(dl,k)
                    A_SA    = self.CDV_A_SA_LK[l][k]      
                    A_SA_LB = self._get_A_SA_LB(dl,k)
                                  
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    rcstr = (A_SA_LB * T_SA) + (T_SA_LB * A_SA) - (A_SA_LB * T_SA_LB)
                    self.CSTR_A_SA_T_SA_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                    
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_1_LK:\n %s" %self.CSTR_A_SA_T_SA_1_LK)
        
    def _createCSTR_A_SA_T_SA_2_LK_hasStandbyMode(self):        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]   
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                                        
                    rcstr = (A_SA_UB * T_SA) + (T_SA_UB * A_SA) - (A_SA_UB * T_SA_UB)
                    self.CSTR_A_SA_T_SA_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_2_LK:\n %s" %self.CSTR_A_SA_T_SA_2_LK)
        
        
    def _createCSTR_A_SA_T_SA_3_LK_hasStandbyMode(self):
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_3_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._get_A_SA_LB(dl,k)
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                                        
                    rcstr = (A_SA_LB * T_SA) + (T_SA_UB * A_SA) - (A_SA_LB * T_SA_UB)
                    self.CSTR_A_SA_T_SA_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_3_LK:\n %s" %self.CSTR_A_SA_T_SA_3_LK)
        
    def _createCSTR_A_SA_T_SA_4_LK_hasStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_4_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]    
                    T_SA_LB = self._get_T_SA_LB(dl,k)                   
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    rcstr = (A_SA_UB * T_SA) + (T_SA_LB * A_SA) - (A_SA_UB * T_SA_LB)
                    self.CSTR_A_SA_T_SA_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_4_LK:\n %s" %self.CSTR_A_SA_T_SA_4_LK)   

#-----------------------------------
        
    def _createCSTR_A_SA_T_SA_1_LK_noStandbyMode(self):
        
        T_SA_LB = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)     
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_1_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._get_A_SA_LB(dl,k)
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T_SA) + (T_SA_LB * A_SA) - (A_SA_LB * T_SA_LB)
                        self.CSTR_A_SA_T_SA_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                    else:
                        self.CSTR_A_SA_T_SA_1_LK[l].append(self.model.addQConstr(lcstr == 0, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_1_LK:\n %s" %self.CSTR_A_SA_T_SA_1_LK)
        
    def _createCSTR_A_SA_T_SA_2_LK_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]   
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T_SA) + (T_SA_UB * A_SA) - (A_SA_UB * T_SA_UB)
                        self.CSTR_A_SA_T_SA_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_2_LK:\n %s" %self.CSTR_A_SA_T_SA_2_LK)
        
        
    def _createCSTR_A_SA_T_SA_3_LK_noStandbyMode(self):
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_3_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._get_A_SA_LB(dl,k)
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T_SA) + (T_SA_UB * A_SA) - (A_SA_LB * T_SA_UB)
                        self.CSTR_A_SA_T_SA_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_3_LK:\n %s" %self.CSTR_A_SA_T_SA_3_LK)
        
    def _createCSTR_A_SA_T_SA_4_LK_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_SA_LB = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) 
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_4_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]                       
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T_SA) + (T_SA_LB * A_SA) - (A_SA_UB * T_SA_LB)
                        self.CSTR_A_SA_T_SA_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_4_LK:\n %s" %self.CSTR_A_SA_T_SA_4_LK)    
        
#--------------------------------------------------
    def _createCSTR_A_SA_T_z_1_LK_looseboundedT_hasStandbyMode(self):
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_1_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._get_A_SA_LB(dl,k)                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_LB * T) + (T_LB * A_SA) - (A_SA_LB * T_LB)
                    self.CSTR_A_SA_T_z_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                        
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_1_LK:\n %s" %self.CSTR_A_SA_T_z_1_LK)
        
    def _createCSTR_A_SA_T_z_2_LK_looseboundedT_hasStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T = self.CAV_T_LK[l][k]                    
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_UB * T) + (T_UB * A_SA) - (A_SA_UB * T_UB)
                    self.CSTR_A_SA_T_z_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_2_LK:\n %s" %self.CSTR_A_SA_T_z_2_LK)
        
        
    def _createCSTR_A_SA_T_z_3_LK_looseboundedT_hasStandbyMode(self):
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_3_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._get_A_SA_LB(dl,k)
                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_LB * T) + (T_UB * A_SA) - (A_SA_LB * T_UB)
                    self.CSTR_A_SA_T_z_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_3_LK:\n %s" %self.CSTR_A_SA_T_z_3_LK)
        
    def _createCSTR_A_SA_T_z_4_LK_looseboundedT_hasStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_4_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_UB * T) + (T_LB * A_SA) - (A_SA_UB * T_LB)
                    self.CSTR_A_SA_T_z_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                    
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_4_LK:\n %s" %self.CSTR_A_SA_T_z_4_LK)
        
        
#---------------------------------------
    def _createCSTR_A_SA_T_z_1_LK_looseboundedT_noStandbyMode(self):
   
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_1_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]     
                    A_SA_LB = self._get_A_SA_LB(dl,k)     
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T) + (T_LB * A_SA) - (A_SA_LB * T_LB)
                        self.CSTR_A_SA_T_z_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                    else:
                        self.CSTR_A_SA_T_z_1_LK[l].append(self.model.addQConstr(lcstr == 0, name=name))
                        
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_1_LK:\n %s" %self.CSTR_A_SA_T_z_1_LK)
        
    def _createCSTR_A_SA_T_z_2_LK_looseboundedT_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T = self.CAV_T_LK[l][k]                    
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T) + (T_UB * A_SA) - (A_SA_UB * T_UB)
                        self.CSTR_A_SA_T_z_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_2_LK:\n %s" %self.CSTR_A_SA_T_z_2_LK)
        
        
    def _createCSTR_A_SA_T_z_3_LK_looseboundedT_noStandbyMode(self):
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_3_LK.append([])
                
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l 
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._get_A_SA_LB(dl,k)
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T) + (T_UB * A_SA) - (A_SA_LB * T_UB)
                        self.CSTR_A_SA_T_z_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_3_LK:\n %s" %self.CSTR_A_SA_T_z_3_LK)
        
    def _createCSTR_A_SA_T_z_4_LK_looseboundedT_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_4_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T) + (T_LB * A_SA) - (A_SA_UB * T_LB)
                        self.CSTR_A_SA_T_z_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                    
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_4_LK:\n %s" %self.CSTR_A_SA_T_z_4_LK)
        
    #===========================================================================
    # Constraints: Energy Consumption
    #===========================================================================
    def _createCSTR_EnergyConsumption_Fan(self):
        """For each location at each timestep, create a constraint for e_fan(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_E_FAN_LK.append([])
            for k in xrange(self.NUM_SLOT):
                
                name = ['CSTR_E_FAN_LK', str(l), str(k)]
                name = '_'.join(name)      
                
                cstr = self.EAMS.BETA_FAN_POWER_CONSTANT * self.CDV_A_SA_LK[l][k]
                
                e_fan = self.CAV_E_FAN_LK[l][k]
                self.CSTR_E_FAN_LK[l].append(self.model.addConstr(e_fan==cstr, name))
                
        self.model.update()
        logging.debug("CSTR_E_FAN_LK:\n %s" %self.CSTR_E_FAN_LK)
        
    def _createCSTR_EnergyConsumption_Conditioning(self):
        """For each location at each timestep, create a constraint for e_conditioning(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_E_CONDITIONING_LK.append([])            
            for k in xrange(self.NUM_SLOT):               
                name = ['CSTR_E_CONDITIONING_LK', str(l), str(k)]
                name = '_'.join(name)    
                
                cstr = 0
                # NOTE: only when OAT > T_CA!!
                if (float(self.EAMS.OAT.values()[k]) > float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)):            
                    cstr += self.CDV_A_SA_LK[l][k] * (
                                   ((float)(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) * (float)(self.EAMS.OAT.values()[k])) -
                                   ((float)(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) * (float)(self.EAMS.TEMPERATURE_CONDITIONED_AIR))
                                   )

                e_conditioning = self.CAV_E_CONDITIONING_LK[l][k]
                self.CSTR_E_CONDITIONING_LK[l].append(self.model.addConstr(e_conditioning==cstr, name))
                
        self.model.update()
        logging.debug("CSTR_E_CONDITIONING_LK:\n %s" %self.CSTR_E_CONDITIONING_LK)
        
    def _createCSTR_EnergyConsumption_Heating(self):
        """For each location at each timestep, create a constraint for e_heating(k, l)"""
                
        for l in xrange(self.NUM_ROOM):
            self.CSTR_E_HEATING_LK.append([])
            for k in xrange(self.NUM_SLOT):
                
                name = ['CSTR_E_HEATING_LK', str(l), str(k)]
                name = '_'.join(name) 
                e_heating = self.CAV_E_HEATING_LK[l][k]
                
                cstr = (
                         (float(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) *
                         self.CAV_A_SA_T_SA_LK[l][k]
                         ) - 
                         (float(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) *
                         float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) *
                         self.CDV_A_SA_LK[l][k]
                         )
                        )
   
                self.CSTR_E_HEATING_LK[l].append(self.model.addConstr(e_heating==cstr, name)) 
                    
        self.model.update()
        logging.debug("CSTR_E_HEATING_LK:\n %s" %self.CSTR_E_HEATING_LK)
                    
        
    #===========================================================================
    # Master Schedule
    #=========================================================================== 
    def _getMSTR_BDV_x_MLK(self, idx):
        for k,v in self.MSTR_BDV_x_MLK_Dict.iteritems():
            if v == idx:
                return k  
                  
            
    def _getMSTR_BDV_w_LK(self, idx):
        
        for k,v in self.MSTR_BDV_w_LK_Dict.iteritems():
            if v == idx:
                return k   

    def _updMSTR_Schedules(self):
        self._updMSTR_BDV_x_MLK_MT()
        self._updMSTR_BAV_z_LK()        
        self._updMSTR_DAV_Attendee_LK()
        
    def _updMSTR_HVAC(self):
        if self.SCHE_MODE == 0:
            self._updMSTR_BAV_z_LK()  # SCHE_MODE=1 will call both _updMSTR_Schedules & _updMSTR_HVAC
        self._updMSTR_BDV_w_LK()
        self._updMSTR_CDV_T_SA_LK()
        self._updMSTR_CDV_A_SA_LK()
        self._updMSTR_CAV_T_LK()
        self._updMSTR_CAV_E_FAN_LK()
        self._updMSTR_CAV_E_CONDITIONING_LK()
        self._updMSTR_CAV_E_HEATING_LK()
        
                 
    def _updMSTR_BDV_x_MLK_MT(self):
        for m in xrange(self.NUM_MEETING_TYPE):
            if self.SCHE_MODE == 1:
                dm = self.CURR_DESTROY_MTYPE[m]
            else:
                dm = m
            
            for l in xrange(len(self.BDV_x_MLK[m])):
                if self.SCHE_MODE == 1:
                    dl = self.CURR_DESTROY_LOCATION[l]
                else:
                    dl = l
                
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    val = self.BDV_x_MLK[m][l][k].x
                    if val > self.EPSILON:                         
                        self.MSTR_BDV_x_MLK[dm][dl][k] = 1
                    else:
                        self.MSTR_BDV_x_MLK[dm][dl][k] = 0
            
        
    def _updMSTR_BAV_z_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            for k in xrange(self.NUM_SLOT):
                val = self.BAV_z_LK[l][k].x
                if val > self.EPSILON:
                    self.MSTR_BAV_z_LK[dl][k] = 1
                else:
                    self.MSTR_BAV_z_LK[dl][k] = 0
                        
    def _updMSTR_DAV_Attendee_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            for k in xrange(self.NUM_SLOT):
                val = self.DAV_Attendee_LK[l][k].x
                if val > self.EPSILON:
                    self.MSTR_DAV_Attendee_LK[dl][k] = self.DAV_Attendee_LK[l][k].x
                else:
                    self.MSTR_DAV_Attendee_LK[dl][k] = 0
                        
    def _updMSTR_BDV_w_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
            
            for k in xrange(len(self.BDV_w_LK[l])):    
                val = self.BDV_w_LK[l][k].x
                if val > self.EPSILON:
                    self.MSTR_BDV_w_LK[dl][k] = 1
                else:
                    self.MSTR_BDV_w_LK[dl][k] = 0
            
    def _updMSTR_CDV_T_SA_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
                
            for k in xrange(self.NUM_SLOT):                
                self.MSTR_CDV_T_SA_LK[dl][k] = self.CDV_T_SA_LK[l][k].x
                
    def _updMSTR_CDV_A_SA_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
                
            for k in xrange(self.NUM_SLOT):                
                self.MSTR_CDV_A_SA_LK[dl][k] = self.CDV_A_SA_LK[l][k].x
          
    def _updMSTR_CAV_T_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
                
            for k in xrange(self.NUM_SLOT):                
                self.MSTR_CAV_T_LK[dl][k] = self.CAV_T_LK[l][k].x
            
    def _updMSTR_CAV_E_FAN_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
                
            for k in xrange(self.NUM_SLOT):                
                self.MSTR_CAV_E_FAN_LK[dl][k] = self.CAV_E_FAN_LK[l][k].x
                            
    def _updMSTR_CAV_E_CONDITIONING_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
                
            for k in xrange(self.NUM_SLOT):                
                self.MSTR_CAV_E_CONDITIONING_LK[dl][k] = self.CAV_E_CONDITIONING_LK[l][k].x
                
    def _updMSTR_CAV_E_HEATING_LK(self):
        for l in xrange(self.NUM_ROOM):
            if self.SCHE_MODE == 1:
                dl = self.CURR_DESTROY_LOCATION[l]
            else:
                dl = l
                
            for k in xrange(self.NUM_SLOT):                
                self.MSTR_CAV_E_HEATING_LK[dl][k] = self.CAV_E_HEATING_LK[l][k].x
                
                
    def getEnergyConsumption(self, locls):
        """Get the energy consumption of the location in locls from the Master Schedule"""
        e = 0
        for l in xrange(self.MSTR_NUM_ROOM):
            if l in locls:
                e = e + sum(self.MSTR_CAV_E_HEATING_LK[l]) + sum(self.MSTR_CAV_E_CONDITIONING_LK[l]) + sum(self.MSTR_CAV_E_FAN_LK[l])
        return e
                
    def getEnergyConsumption_DRonly(self):
        
        e = 0
        self.total_power_kJs = []
        self.total_fan_power_kJs = []
        self.total_cond_power_kJs = []
        self.total_heat_power_kJs = []
          
        for l in xrange(self.NUM_ROOM):
            loc_fan_power_kJs = 0
            loc_cond_power_kJs = 0
            loc_heat_power_kJs = 0
            
            self.total_power_kJs.append([])
            self.total_fan_power_kJs.append([])
            self.total_cond_power_kJs.append([])
            self.total_heat_power_kJs.append([])
            
            for k in xrange(self.NUM_SLOT):
                loc_fan_power_kJs = loc_fan_power_kJs + self.CAV_E_FAN_LK[l][k].x
                loc_cond_power_kJs = loc_cond_power_kJs + self.CAV_E_CONDITIONING_LK[l][k].x
                loc_heat_power_kJs = loc_heat_power_kJs + self.CAV_E_HEATING_LK[l][k].x
                
            self.total_fan_power_kJs[l] = loc_fan_power_kJs
            self.total_cond_power_kJs[l] = loc_cond_power_kJs
            self.total_heat_power_kJs[l] = loc_heat_power_kJs
            self.total_power_kJs[l] = self.total_fan_power_kJs[l] + self.total_cond_power_kJs[l] + self.total_heat_power_kJs[l]
     
            e = e + self.total_power_kJs[l]
            
        return e
     
                
                
    
    #===========================================================================
    # Diagnose Full Schedule
    #===========================================================================
    def _printMSTR_Var_DAV_Attendee_LK(self):        
        logging.info("MSTR DAV_Attendee")        
        for l in xrange(self.MSTR_NUM_ROOM):
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.MSTR_NUM_SLOT):
                res.append(str(self.MSTR_DAV_Attendee_LK[l][k]))
            s = ' '.join(res)
            logging.info(s)
 
    def _printMSTR_Var_BDV_x_MLK_MT_Summary(self):        
        logging.info ("Summary MSTR BDV_x_MLK_MT:")          
        for m in xrange(self.MSTR_NUM_MEETING_TYPE):
            for l in xrange(len(self.MSTR_BDV_x_MLK[m])):
                for k in xrange(len(self.MSTR_BDV_x_MLK[m][l])):
                    if self.MSTR_BDV_x_MLK[m][l][k] == 1:
                        [_,fl,fk] = self._getMSTR_BDV_x_MLK([m,l,k])
                        logging.info("Meeting %d | Location %d [%s] | Start Slot %s [%s]" %(m, fl, self.EAMS.RL[fl], fk, self.EAMS.TS.get(fk)))
                             
    def _printMSTR_Var_BDV_w_LK_Summary(self):
        if self.MSTR_BDV_w_LK: 
            logging.info ("Summary BDV_w_LK:")          
                
            for l in xrange(len(self.MSTR_BDV_w_LK)):
                for k in xrange(len(self.MSTR_BDV_w_LK[l])):
                    if self.MSTR_BDV_w_LK[l][k] == 1:
                        [fl,fk] = self._getMSTR_BDV_w_LK([l,k])  
                        logging.info("Location %d [%s] | Start Slot %s [%s]" %(l, self.EAMS.RL[fl], fk, self.EAMS.TS.get(fk)))                               

    def _printMSTR_Var_BAV_z_LK(self):
        logging.info("BAV_z_LK")
        for l in xrange(self.MSTR_NUM_ROOM):
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.MSTR_NUM_SLOT):
                if self.MSTR_BAV_z_LK[l][k] == 1:
                    res.append(str(1))
                else:
                    res.append(str(0))
            s = ' '.join(res)
            logging.info(s)


    def _printMSTR_Var_Occupied_RoomTemperature_Summary(self):
        logging.info("Room Temperature when BAV_z_LK=1:")     
        for l in xrange(self.MSTR_NUM_ROOM):
            logging.info("Location %s" %l)
            res = []
            for k in xrange(self.MSTR_NUM_SLOT):            
                if self.MSTR_BAV_z_LK[l][k] == 1:
                    res.append(str(self.MSTR_CAV_T_LK[l][k]))
            s = ' '.join(res)
            logging.info(s)
                                 
    def logMSTR_SchedulingResults(self):      
        try:
            logging.info ("=============================================================")
            logging.info ("Master Schedule")              
            logging.info ("=============================================================")
            self._printMSTR_Var_DAV_Attendee_LK()
            self._printMSTR_Var_BDV_x_MLK_MT_Summary()
            logging.info ("=============================================================")
        except (ValueError), e:
            logging.critical('%s' % (e)) 
            
    def logMSTR_HVACResults(self):
        try:
            logging.info ("=============================================================")
            logging.info ("Master HVAC Control")              
            logging.info ("=============================================================")
            self._printMSTR_Var_BAV_z_LK() 
            self._printMSTR_Var_BDV_w_LK_Summary()
            self._printMSTR_Var_Occupied_RoomTemperature_Summary()
            logging.info ("=============================================================")
            
        except (ValueError), e:
            logging.critical('%s' % (e)) 

            
    def logMSTR_Schedules(self, logcase):
        try:
            fstr = 'Output/' + logcase + '_schedules'
            f = open(fstr,'a')   
            
            # Log timeslot
            f.write(",".join(map(str,self.EAMS.TS.values())))            
            f.write("\n")
            
            # Log number of rooms
            f.write(str(self.MSTR_NUM_ROOM))
            f.write("\n")
              
            # Log room allocation          
            # TODO: maybe no need loop, just print????  
            for r in xrange(self.MSTR_NUM_ROOM):
                vz = []                      
                for k in xrange(self.MSTR_NUM_SLOT):
                    vz.append(self.MSTR_BAV_z_LK[r][k])
                                                                  
                vw = []                    
                if self.EAMS.STANDBY_MODE != '0' and len(self.MSTR_BDV_w_LK) != 0:
                    vwidx = 0      
                    for k in xrange(len(self.MSTR_BDV_w_LK[r])):
                        [_,fk] = self._getMSTR_BDV_w_LK([r,k])                    
                        if fk > vwidx:
                            vw.extend([str(0)] * (fk-vwidx))
                            
                        vw.append(self.MSTR_BDV_w_LK[r][k])
                        vwidx = len(vw)
                                            
                f.write(",".join(map(str,vz)))
                f.write("\n")
                f.write(",".join(map(str,vw)))
                f.write("\n")
                
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
        
                            
    def logMSTR_Temperatures(self, logcase):
        try:
            fstr = 'Output/' + logcase + '_temperatures'
            f = open(fstr,'a')   
            
            # Log timeslot
            f.write(",".join(map(str,self.EAMS.TS.values())))            
            f.write("\n")
            
            # Log outdoor temperature
            f.write(",".join(map(str,self.EAMS.OAT.values())))  
            f.write("\n")
            
            # Log number of rooms
            f.write(str(self.NUM_ROOM))
            f.write("\n")
              
            # Log room temperature, TSA, ASA            
            for r in xrange(self.NUM_ROOM):
                T = []
                TSA = []
                ASA = []
                for k in xrange(self.NUM_SLOT):   
                    T.append(self.MSTR_CAV_T_LK[r][k])
                    TSA.append(self.MSTR_CDV_T_SA_LK[r][k])
                    ASA.append(self.MSTR_CDV_A_SA_LK[r][k])
                                    
                f.write(",".join(map(str,T)))
                f.write("\n")
                f.write(",".join(map(str,TSA)))
                f.write("\n")
                f.write(",".join(map(str,ASA)))
                f.write("\n")
            
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
        
        
    #===========================================================================
    # Diagnose Current Partial Schedule
    #=========================================================================== 
    def _getBDV_x_MLK(self, idx):
        for k,v in self.BDV_x_MLK_Dict.iteritems():
            if v == idx:
                return k        
            
    def _getBDV_w_LK(self, idx):
        for k,v in self.BDV_w_LK_Dict.iteritems():
            if v == idx:
                return k   
            
    def _printVar_DAV_Attendee_LK(self):        
        logging.info("DAV_Attendee")
        
        for l in xrange(self.NUM_ROOM):
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                val = self.DAV_Attendee_LK[l][k].x
                if val > self.EPSILON:
                    res.append(str(self.DAV_Attendee_LK[l][k].x))                   
                else:
                    res.append(str(0))
            s = ' '.join(res)
            logging.info(s)
 
    def _printVar_BDV_x_MLK_MT_Summary(self):        
        logging.info ("Summary BDV_x_MLK_MT:")          
        for m in xrange(self.NUM_MEETING_TYPE):
            for l in xrange(len(self.BDV_x_MLK[m])):
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    val = self.BDV_x_MLK[m][l][k].x                    
                    if val > self.EPSILON:
                        [_,fl,fk] = self._getBDV_x_MLK([m,l,k])
                        logging.info("Meeting %d | Location %d [%s] | Start Slot %s [%s]" %(m, fl, self.EAMS.RL[fl], fk, self.EAMS.TS.get(fk)))
                                 
    def _printVar_BAV_z_LK(self):
        logging.info("BAV_z_LK")
        
        for l in xrange(self.NUM_ROOM):
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                val = self.BAV_z_LK[l][k].x
                if val > self.EPSILON:
                    res.append(str(self.BAV_z_LK[l][k].x))
                else:
                    res.append(str(0))
            s = ' '.join(res)
            logging.info(s)
            
    def _printVar_BDV_w_LK_Summary(self):
        if self.BDV_w_LK: 
            logging.info ("Summary BDV_w_LK:")          
                
            for l in xrange(len(self.BDV_w_LK)):
                for k in xrange(len(self.BDV_w_LK[l])):
                    val = self.BDV_w_LK[l][k].x
                    if val > self.EPSILON:
                        [fl,fk] = self._getBDV_w_LK([l,k])  
                        logging.info("Location %d [%s] | Start Slot %s [%s]" %(l, self.EAMS.RL[fl], fk, self.EAMS.TS.get(fk)))                               
        
    def _printVar_Occupied_RoomTemperature_Summary(self):
        logging.info("Room Temperature when BAV_z_LK=1:")     
        for l in xrange(self.NUM_ROOM):
            logging.info("Location %s" %l)
            res = []
            for k in xrange(self.NUM_SLOT):            
                val = self.BAV_z_LK[l][k].x
                if val > self.EPSILON:                    
                    res.append(str(self.CAV_T_LK[l][k].x))
            s = ' '.join(res)
            logging.info(s)
    
    def logSchedulingResults(self):      
        try:
            logging.info ("=============================================================")
            logging.info ("Partial Schedule")              
            logging.info ("=============================================================")
            if (self.model.getAttr(GRB.attr.SolCount) == 0):
                    raise ValueError("logSchedulingResults skipped. MIP failed to produce a solution.")                
            self._printVar_DAV_Attendee_LK()
            self._printVar_BDV_x_MLK_MT_Summary()
            logging.info ("=============================================================")
        except (ValueError), e:
            logging.critical('%s' % (e)) 
            
    def logHVACResults(self):
        try:
            logging.info ("=============================================================")
            logging.info ("Partial HVAC Control")              
            logging.info ("=============================================================")
            if (self.model.getAttr(GRB.attr.SolCount) == 0):
                    raise ValueError("logHVACResults skipped. MIP failed to produce a solution.")
            
            self._printVar_BAV_z_LK() 
            self._printVar_BDV_w_LK_Summary()
            self._printVar_Occupied_RoomTemperature_Summary()
            logging.info ("=============================================================")
        except (ValueError), e:
            logging.critical('%s' % (e)) 
            
    def logXW(self, logcase):
        try:            
            if (self.model.getAttr(GRB.attr.SolCount) == 0):
                raise ValueError("logSchedules skipped. MIP failed to produce a solution.")
            
            fstr = 'Output/' + logcase + '_XW'
            f = open(fstr,'a')   
            
            occ_x = []
            num_x = 0
            for m in xrange(self.NUM_MEETING_TYPE):
                for l in xrange(len(self.BDV_x_MLK[m])):
                    for k in xrange(len(self.BDV_x_MLK[m][l])):
                        val = self.BDV_x_MLK[m][l][k].x                    
                        if val > self.EPSILON:
                            occ_x.append([m,l,k])
                            num_x = num_x + 1
                        
            occ_w = []
            num_w = 0    
            for l in xrange(len(self.BDV_w_LK)):
                for k in xrange(len(self.BDV_w_LK[l])):
                    val = self.BDV_w_LK[l][k].x
                    if val > self.EPSILON:
                        occ_w.append([l,k])
                        num_w = num_w + 1
                                   
            
            # log number of meetings
            f.write(str(num_x))
            f.write("\n")
            
            # log BDV_x_MLK which is 1
            for i in xrange(len(occ_x)):
                f.write(str(','.join(str(e) for e in occ_x[i])))
                f.write("\n")
            
            # log standby mode
            f.write(str(num_w))
            f.write("\n")
            
            # log BDV_w_MLK which is 1
            for i in xrange(len(occ_w)):
                f.write(str(', '.join(str(e) for e in occ_w[i])))
                f.write("\n")
            
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
        
            
    def logSchedules(self, logcase):
        try:            
            if (self.model.getAttr(GRB.attr.SolCount) == 0):
                raise ValueError("logSchedules skipped. MIP failed to produce a solution.")
            
#             fstr = 'Output\\' + logcase + '_schedules'
            fstr = 'Output/' + logcase + '_schedules'
            f = open(fstr,'a')   
            
            # Log timeslot
            f.write(",".join(map(str,self.EAMS.TS.values())))            
            f.write("\n")
            
            # Log number of rooms
            f.write(str(self.NUM_ROOM))
            f.write("\n")
              
            # Log room allocation            
            for r in xrange(self.NUM_ROOM):
                vz = []                      
                for k in xrange(self.NUM_SLOT):    
                    if self.BAV_z_LK[r][k].x > self.EPSILON:   
                        vz.append(1)
                    else:
                        vz.append(0)
                                                                  
                vw = []                    
                if self.EAMS.STANDBY_MODE != '0' and len(self.BDV_w_LK) != 0: #len(self.BDV_w_LK[r])==0 -> HVAC control not running, for initial schedule only     
                    vwidx = 0      
                    for k in xrange(len(self.BDV_w_LK[r])):
                        [_,fk] = self._getBDV_w_LK([r,k])                    
                        if fk > vwidx:
                            vw.extend([str(0)] * (fk-vwidx))
                            
                        if self.BDV_w_LK[r][k].x > self.EPSILON:
                            vw.extend(str(1))
                        else:
                            vw.extend(str(0))
                                                    
                        vwidx = len(vw)
                    
                f.write(",".join(map(str,vz)))
                f.write("\n")
                f.write(",".join(map(str,vw)))
                f.write("\n")
                
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
            
            
    def logTemperatures(self, logcase):
        try:
            if (self.model.getAttr(GRB.attr.SolCount) == 0):
                raise ValueError("logTemperatures skipped. MIP failed to produce a solution.")

            fstr = 'Output/' + logcase + '_temperatures'
            f = open(fstr,'a')   
            
            # Log timeslot
            f.write(",".join(map(str,self.EAMS.TS.values())))            
            f.write("\n")
            
            # Log outdoor temperature
            f.write(",".join(map(str,self.EAMS.OAT.values())))  
            f.write("\n")
            
            # Log number of rooms
            f.write(str(self.NUM_ROOM))
            f.write("\n")
              
            # Log room temperature, TSA, ASA            
            for r in xrange(self.NUM_ROOM):
                T = []
                TSA = []
                ASA = []
                for k in xrange(self.NUM_SLOT):   
                    T.append(self.CAV_T_LK[r][k].x)
                    TSA.append(self.CDV_T_SA_LK[r][k].x)
                    ASA.append(self.CDV_A_SA_LK[r][k].x)
                                    
                f.write(",".join(map(str,T)))
                f.write("\n")
                f.write(",".join(map(str,TSA)))
                f.write("\n")
                f.write(",".join(map(str,ASA)))
                f.write("\n")
            
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
    
    
