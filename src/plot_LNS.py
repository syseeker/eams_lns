import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
from matplotlib.dates import WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY, rrulewrapper, RRuleLocator

from datetime import datetime, timedelta


def _getPlotRule(ptype):         
    if ptype == 0:
        return MINUTELY
    if ptype == 1:
        return HOURLY
    if ptype == 2:
        return DAILY
    if ptype == 3:
        return WEEKLY
    if ptype == 4:
        return SECONDLY
    else:
        print "Unknown Plot Type. Set to default MINUTELY"
        return MINUTELY
        

def getColor(ntlabel):     
    if ntlabel == 'RANDOM_RANGE_TIME_ONLY':
        return 'b'
    elif ntlabel == 'RANDOM_RANGE_LOCATION_ONLY':
        return 'r'
    elif ntlabel == 'RANDOM_RANGE_TIME_N_LOCATION':
        return 'y'
    elif ntlabel == 'ARBITRARY_MEETING':
        return 'c'
    else:
        return 'k'
    
def getMarker(ntlabel):     
    if ntlabel == 'RANDOM_RANGE_TIME_ONLY':
        return 's'
    elif ntlabel == 'RANDOM_RANGE_LOCATION_ONLY':
        return '^'
    elif ntlabel == 'RANDOM_RANGE_TIME_N_LOCATION':
        return 'o'
    elif ntlabel == 'ARBITRARY_MEETING':
        return 'd'
    else:
        return 'p'



def plot_LNS_graph(fdir, rfile, nt_label, pinterval, pstep):
    
#     fstr = 'Output\\' + rfile  
    fstr = fdir + rfile        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()

    objvalue = []
    period = []    
    # hardcoded
    nt1 = []
    nt2 = []
    nt3 = []
    nt4 = []
    nt5 = []
    nt6 = []
    nt1p = []
    nt2p = []
    nt3p = []
    nt4p = []
    nt5p = []
    nt6p = []
        
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
        
# Option 1: use timedelta
        if i == 0:
            delta_in_sec = 0
            period.append(0)
            start_time = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")            
        else:
            curr_time = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            delta = curr_time - start_time
            delta_in_sec = delta.total_seconds()
            period.append(delta_in_sec)            
        objvalue.append(float(parts[1]))
            
        if parts[2] == '-1':
            nt1.append(float(parts[1]))
            nt1p.append(delta_in_sec)
        elif parts[2] == '0':            
            nt2.append(float(parts[1]))
            nt2p.append(delta_in_sec)
        elif parts[2] == '1':            
            nt3.append(float(parts[1]))
            nt3p.append(delta_in_sec)
        elif parts[2] == '2':            
            nt4.append(float(parts[1]))
            nt4p.append(delta_in_sec)
        elif parts[2] == '3':            
            nt5.append(float(parts[1]))
            nt5p.append(delta_in_sec)
        else:            
            nt6.append(float(parts[1]))
            nt6p.append(delta_in_sec)
            
# # Option 2: use timestamp            
#         period.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
#         objvalue.append(float(parts[1]))
#         
#         if parts[2] == '-1':
#             nt1.append(float(parts[1]))
#             nt1p.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
#         elif parts[2] == '0':            
#             nt2.append(float(parts[1]))
#             nt2p.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
#         elif parts[2] == '1':            
#             nt3.append(float(parts[1]))
#             nt3p.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
#         elif parts[2] == '2':            
#             nt4.append(float(parts[1]))
#             nt4p.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
#         elif parts[2] == '3':            
#             nt5.append(float(parts[1]))
#             nt5p.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
#         else:            
#             nt6.append(float(parts[1]))
#             nt6p.append(datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
  
    fig = plt.figure()   
    lfig = fig.add_subplot(111)
           
    lfig.plot(period, objvalue, 'k-')
     
    lfig.scatter(nt1p, nt1, color='g', marker='*', s=30, label="Initial")
    if len(nt2) > 0:
        lfig.scatter(nt2p, nt2, color=getColor(nt_label[0]), marker=getMarker(nt_label[0]), s=30, label=nt_label[0], alpha=.5)
    if len(nt3) > 0:
        lfig.scatter(nt3p, nt3, color=getColor(nt_label[1]), marker=getMarker(nt_label[1]), s=30, label=nt_label[1], alpha=.5)
    if len(nt4) > 0:
        lfig.scatter(nt4p, nt4, color=getColor(nt_label[2]), marker=getMarker(nt_label[2]), s=30, label=nt_label[2], alpha=.5)
    if len(nt5) > 0:
        lfig.scatter(nt5p, nt5, color=getColor(nt_label[3]), marker=getMarker(nt_label[3]), s=30, label=nt_label[3], alpha=.5)
    if len(nt6) > 0:
        lfig.scatter(nt6p, nt6, color='k', marker='p', s=30, label="All-Tabued", alpha=.7)
              
    lfig.set_xlabel("Scheduling Period (s)",fontsize=10)
    lfig.set_ylabel("Power Consumption (kW)",fontsize=10)
    lfig.set_ylim(ymin=0, ymax=max(objvalue)+10)  
    lfig.set_xlim(xmin=-5, xmax=4500)        
    lfig_fontP = FontProperties()
    lfig_fontP.set_size(13)        
    lfig_handles, lfig_labels = lfig.get_legend_handles_labels()
    lfig.legend(lfig_handles, lfig_labels, loc='best', ncol=1, prop=lfig_fontP)

# # Option 2: use timestamp  
#     ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
#     lfig_rule = rrulewrapper(_getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
#     lfig_loc = RRuleLocator(lfig_rule)
#     lfig.xaxis.set_major_locator(lfig_loc)
#     lfig.xaxis.set_major_formatter(ymdhFmt)    
#     lfig_datemin = period[0] - timedelta(seconds=2) #datetime(min(period).year, min(period).month, min(period).day, min(period).hour, min(period).minute, min(period).second) 
#     lfig_datemax = period[len(period)-1] + timedelta(seconds=2) #datetime(max(period).year, max(period).month, max(period).day, max(period).hour, max(period).minute, max(period).second)        
#     lfig.set_xlim(lfig_datemin, lfig_datemax)     
    fig.autofmt_xdate()
     
    plt.savefig('Output\\'+ rfile +'_LNS_trace.png', dpi=400)
#     plt.show()
    plt.close(fig)
    print "Done!"

# 
# # 
# # nt_label = ['RANDOM_RANGE_TIME_ONLY', 'RANDOM_RANGE_LOCATION_ONLY', 'RANDOM_RANGE_TIME_N_LOCATION', 'ARBITRARY_MEETING']
# # # plot_LNS_graph("eams_meeting_test_OPTCFG_1_LNS_trace", nt_label, 4, 5)
# # plot_LNS_graph("eams_meeting_m10_04_227000_2_ws_OPTCFG_0_LNS_trace", nt_label, 0, 2)
# 
# 
# 
# nt0 = ["RANDOM_RANGE_TIME_ONLY", "RANDOM_RANGE_LOCATION_ONLY", "RANDOM_RANGE_TIME_N_LOCATION", "ARBITRARY_MEETING"]                
# nt1 = ["RANDOM_RANGE_LOCATION_ONLY", "RANDOM_RANGE_TIME_ONLY", "RANDOM_RANGE_TIME_N_LOCATION", "ARBITRARY_MEETING"]                
# nt2 = ["RANDOM_RANGE_TIME_N_LOCATION", "RANDOM_RANGE_TIME_ONLY", "RANDOM_RANGE_LOCATION_ONLY", "ARBITRARY_MEETING"]               
# nt3 = ["RANDOM_RANGE_TIME_N_LOCATION", "RANDOM_RANGE_LOCATION_ONLY", "RANDOM_RANGE_TIME_ONLY", "ARBITRARY_MEETING"]                
# nt4 = ["RANDOM_RANGE_TIME_ONLY", "RANDOM_RANGE_TIME_N_LOCATION"]          
# nt5 = ["RANDOM_RANGE_LOCATION_ONLY", "RANDOM_RANGE_TIME_N_LOCATION"]                
# 
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/Output_LNS_set1_4DiffRoom/Output_LNS_set1_4DiffRoom/EAMS_v10_set1_4DiffRoom/src/Output/"
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/Output_LNS_set2_4DiffRoom/Output_LNS_set2_4DiffRoom/EAMS_v10_set2_4DiffRoom/src/Output/"
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/Output_LNS_set1_4LRHC/Output_LNS_set1_4LRHC/EAMS_v10_set1_4LRHC/src/Output/"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/Output_LNS_set2_4LRHC/Output_LNS_set2_4LRHC/EAMS_v10_set2_4LRHC/src/Output/"
# 
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m20_07_011000_9_ws_set_1/"
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m20_07_011000_9_ws_set_2/"
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_0_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_1_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_2_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_3_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_4_LNS_trace", nt4, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_5_LNS_trace", nt5, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_6_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_7_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_8_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_9_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_10_LNS_trace", nt4, 0, 2)
# # # plot_LNS_graph(prefix, "eams_meeting_m20_07_011000_9_ws_OPTCFG_11_LNS_trace", nt5, 0, 2)
# 
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m20_07_707000_9_ws_set_1/"
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m20_07_707000_9_ws_set_2/"
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_0_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_1_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_2_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_3_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_4_LNS_trace", nt4, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_5_LNS_trace", nt5, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_6_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_7_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_8_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_9_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_10_LNS_trace", nt4, 0, 2)
# # plot_LNS_graph(prefix, "eams_meeting_m20_07_707000_9_ws_OPTCFG_11_LNS_trace", nt5, 0, 2)
# 
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m50_07_807000_3_ws_set_1/"
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m50_07_807000_3_ws_set_2/"
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_0_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_1_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_2_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_3_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_4_LNS_trace", nt4, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_5_LNS_trace", nt5, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_6_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_7_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_8_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_9_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_10_LNS_trace", nt4, 0, 2)
# # plot_LNS_graph(prefix, "eams_meeting_m50_07_807000_3_ws_OPTCFG_11_LNS_trace", nt5, 0, 2)
# 
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m50_07_944000_7_m_ws_set_1/"
# # prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/v10/Exp0727/LNS_ArbitrarySche_4LRHC/m50_07_944000_7_m_ws_set_2/"
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_0_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_1_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_2_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_3_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_4_LNS_trace", nt4, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_5_LNS_trace", nt5, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_6_LNS_trace", nt0, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_7_LNS_trace", nt1, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_8_LNS_trace", nt2, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_9_LNS_trace", nt3, 0, 2)
# plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_10_LNS_trace", nt4, 0, 2)
# # plot_LNS_graph(prefix, "eams_meeting_m50_07_944000_7_m_ws_OPTCFG_11_LNS_trace", nt5, 0, 2)
# 




