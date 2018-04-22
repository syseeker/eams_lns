from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


def plot_MILP(fdir, rfile):
    fstr = fdir + rfile        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    objvalue = []
    objbound = []
    period = []    
    
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
        
        if i == 0:
            delta_in_sec = 0
            period.append(0)
            start_time = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S.%f")            
        else:
            curr_time = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S.%f")
            delta = curr_time - start_time
            delta_in_sec = delta.total_seconds()
            period.append(delta_in_sec)            
        objvalue.append(float(parts[3]))
        objbound.append(float(parts[4]))
            
    fig = plt.figure()   
    lfig = fig.add_subplot(111)           
    lfig.plot(period, objvalue, marker='+', label="ObjValue")
    lfig.plot(period, objbound, marker='o', label="ObjBound" )
    lfig.set_xlabel("Scheduling Period (s)",fontsize=10)
    lfig.set_ylabel("Power Consumption (kW)",fontsize=10)
#     lfig.set_ylim(ymin=600, ymax=2600)  
#     lfig.set_xlim(xmin=-5, xmax=4500)
    lfig.set_title('[' + fdir + '\n' + rfile +']\n', fontsize=8)        
    lfig_fontP = FontProperties()
    lfig_fontP.set_size(13)        
    lfig_handles, lfig_labels = lfig.get_legend_handles_labels()
    lfig.legend(lfig_handles, lfig_labels, loc='best', ncol=1, prop=lfig_fontP)
    fig.autofmt_xdate()
     
#     plt.savefig('Output\\'+ rfile +'_LNS_trace.png', dpi=400)
    plt.savefig(prefix + rfile +'_MILP_trace.png', dpi=400)
#     plt.show()
    plt.close(fig)
    print "Done!"
    
# 
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140823_MILP_reduced_full_study/4LRHC/EAMS_v10_140818_reduced_4R/src/Output/"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140823_MILP_reduced_full_study/4LRHC/EAMS_v10_140818_full_4R/src/Output/"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140823_MILP_reduced_full_study/4DiffRoom/EAMS_v10_140818_reduced_4R/src/Output/"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140823_MILP_reduced_full_study/4DiffRoom/EAMS_v10_140818_full_4R/src/Output/"
# plot_MILP(prefix, "eams_meeting_m20_07_707000_9_ws_solstats")
# plot_MILP(prefix, "eams_meeting_m20_07_011000_9_ws_solstats")
# plot_MILP(prefix, "eams_meeting_m10_04_227000_2_ws_solstats")
# plot_MILP(prefix, "eams_meeting_m10_04_694000_1_ws_solstats")
# plot_MILP(prefix, "eams_meeting_m50_07_944000_7_m_ws_solstats")


prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140825_LNS_MILP/EAMS_v11_140823_MILP/src/Output/"
plot_MILP(prefix, "eams_meeting_m50_07_944000_7_m_ws_20R_solstats")    
plot_MILP(prefix, "eams_meeting_m50_07_807000_3_ws_20R_solstats")
plot_MILP(prefix, "eams_meeting_m100_07_151000_0_ws_20R_solstats")


    
