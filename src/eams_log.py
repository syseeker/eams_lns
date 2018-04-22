import datetime
import logging
from gurobipy import *


def cb_mipsol(model, where):
    if where == GRB.callback.MIPSOL:
        currtime = datetime.datetime.now()        
        obj     = model.cbGet(GRB.callback.MIPSOL_OBJ)
        objbnd  = model.cbGet(GRB.callback.MIPSOL_OBJBND)
        nodecnt = int(model.cbGet(GRB.callback.MIPSOL_NODCNT))
        solcnt  = int(model.cbGet(GRB.callback.MIPSOL_SOLCNT))
        gap = (obj - objbnd)/ obj * 100
        print('*** Found New solution #%d at node %g objective %g bound %g gap %g' % (solcnt, nodecnt, obj, objbnd, gap))
        
#         caseid = model._CASE_CFG + "_" + str(solcnt)
        _cb_logSolutionsStat(model._CASE_CFG, currtime, obj, objbnd, nodecnt, solcnt, gap)
#         _cb_logSchedules(caseid, model)
#         _cb_logTemperatures(caseid, model)
        
def _cb_logSolutionsStat(logcase, currtime, obj, objbnd, nodecnt, solcnt, gap):
    try:            
#         fstr = 'Output\\' + logcase + '_solstats'
        fstr = 'Output/' + logcase + '_solstats'
        f = open(fstr,'a')
        f.write(",".join(map(str, [solcnt, currtime, nodecnt, obj, objbnd, gap])))
        f.write("\n")
        f.close()      
        
    except (ValueError), e:
        logging.critical('%s' % (e)) 

def _cb_logSchedules(logcase, model):
    try:
                    
#         fstr = 'Output\\' + logcase + '_schedules'
        fstr = 'Output/' + logcase + '_schedules'
        f = open(fstr,'a')   
        
        # Log timeslot
        f.write(",".join(map(str,model._EAMS.TS.values())))            
        f.write("\n")
        
        # Log number of rooms
        f.write(str(model._NUM_ROOM))
        f.write("\n")
        
        # Log room allocation & standby mode        
        for l in xrange(model._NUM_ROOM):
            vz = []                      
            for k in xrange(model._NUM_SLOT):  
                vname = "BAV_z_LK" + "_" + str(l) + "_" + str(k)  
                val = model.cbGetSolution(model.getVarByName(vname))
                if val > model._EPSILON:   
                    vz.append(1)
                else:
                    vz.append(0)
                                                                                    
            vw = []                    
            if model._EAMS.STANDBY_MODE != '0':
                for k in xrange(model._NUM_SLOT):
                    if (l, k) in model._BDV_w_LK_Dict.keys(): 
                        vname = "BDV_w_LK" + "_" + str(l) + "_" + str(k)  
                        val = model.cbGetSolution(model.getVarByName(vname))
                        if val > model._EPSILON:
                            vw.extend(str(1))
                                        
                        else:
                            vw.extend(str(0))
                    else:
                        vw.extend(str(0))
                    
            f.write(",".join(map(str,vz)))
            f.write("\n")
            f.write(",".join(map(str,vw)))
            f.write("\n")
            
        f.close()      
        
    except (ValueError), e:
        logging.critical('%s' % (e))  
    
def _cb_logTemperatures(logcase, model):
    try:
#         fstr = 'Output\\' + logcase + '_temperatures'
        fstr = 'Output/' + logcase + '_temperatures'
        f = open(fstr,'a')   
         
        # Log timeslot
        f.write(",".join(map(str,model._EAMS.TS.values())))            
        f.write("\n")
         
        # Log outdoor temperature
        f.write(",".join(map(str,model._EAMS.OAT.values())))  
        f.write("\n")
         
        # Log number of rooms
        f.write(str(model._NUM_ROOM))
        f.write("\n")
           
        # Log room temperature, TSA, ASA            
        for l in xrange(model._NUM_ROOM):
            T = []
            TSA = []
            ASA = []
            for k in xrange(model._NUM_SLOT):
                vname = "CAV_T_LK" + "_" + str(l) + "_" + str(k)  
                val = model.cbGetSolution(model.getVarByName(vname))   
                T.append(val)
                
                vname = "CDV_T_SA_LK" + "_" + str(l) + "_" + str(k)  
                val = model.cbGetSolution(model.getVarByName(vname))   
                TSA.append(val)
                
                vname = "CDV_A_SA_LK" + "_" + str(l) + "_" + str(k)  
                val = model.cbGetSolution(model.getVarByName(vname))   
                ASA.append(val)
                                 
            f.write(",".join(map(str,T)))
            f.write("\n")
            f.write(",".join(map(str,TSA)))
            f.write("\n")
            f.write(",".join(map(str,ASA)))
            f.write("\n")
         
        f.close()      
     
    except (ValueError), e:
        logging.critical('%s' % (e))  
     
     
    
