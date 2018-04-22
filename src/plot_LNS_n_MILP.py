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

def getNeighbourhoodOrder(idxlist):
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

def plot_LNSnMILP_graph(setnum, lnsdir, lnsfile, milpdir, milpfile, nt, pinterval, pstep):
    
    # Read LNS
    fstr = lnsdir + lnsfile        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()

    lnsobjvalue = []
    lnsperiod = []    
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
    
    nt_label = getNeighbourhoodOrder(list(nt))
        
    lines = data.split('\n')
    for i in xrange(len(lines)-2):
        line = lines[i]
        parts = line.split(',')
        
# Option 1: use timedelta
        if i == 0:
            delta_in_sec = 0
            lnsperiod.append(0)
            start_time = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")            
        else:
            curr_time = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            delta = curr_time - start_time
            delta_in_sec = delta.total_seconds()
            lnsperiod.append(delta_in_sec)            
        lnsobjvalue.append(float(parts[1])* 30 * 60 * 0.000277777778)
#         lnsobjvalue.append(float(parts[1]))
        
            
        if parts[2] == '-1':
            nt1.append(float(parts[1])* 30 * 60 * 0.000277777778)
            nt1p.append(delta_in_sec)
        elif parts[2] == '0':            
            nt2.append(float(parts[1])* 30 * 60 * 0.000277777778)
            nt2p.append(delta_in_sec)
        elif parts[2] == '1':            
            nt3.append(float(parts[1])* 30 * 60 * 0.000277777778)
            nt3p.append(delta_in_sec)
        elif parts[2] == '2':            
            nt4.append(float(parts[1])* 30 * 60 * 0.000277777778)
            nt4p.append(delta_in_sec)
        elif parts[2] == '3':            
            nt5.append(float(parts[1])* 30 * 60 * 0.000277777778)
            nt5p.append(delta_in_sec)
        else:            
            nt6.append(float(parts[1])* 30 * 60 * 0.000277777778)
            nt6p.append(delta_in_sec)
        
        
    # Read MILP
    fstr = milpdir + milpfile        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    milpobjvalue = []
    milpperiod = []
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
        
        if i == 0:
            delta_in_sec = 0
            milpperiod.append(0)
            start_time = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S.%f")            
        else:
            curr_time = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S.%f")
            delta = curr_time - start_time
            delta_in_sec = delta.total_seconds()
            milpperiod.append(delta_in_sec)            
        milpobjvalue.append(float(parts[3])* 30 * 60 * 0.000277777778)
#         milpobjvalue.append(float(parts[3]))
        
        
    
    
    # Plot Graph
    fig = plt.figure()   
    lfig = fig.add_subplot(111)
           
    lfig.plot(lnsperiod, lnsobjvalue, 'k-', label="LNS")
    lfig.plot(milpperiod, milpobjvalue, 'k--', label="MIP")
     
#     lfig.scatter(nt1p, nt1, color='g', marker='*', s=30, label="Initial")
#     if len(nt2) > 0:
#         lfig.scatter(nt2p, nt2, color=getColor(nt_label[0]), marker=getMarker(nt_label[0]), s=30, label=nt_label[0], alpha=.5)
#     if len(nt3) > 0:
#         lfig.scatter(nt3p, nt3, color=getColor(nt_label[1]), marker=getMarker(nt_label[1]), s=30, label=nt_label[1], alpha=.5)
#     if len(nt4) > 0:
#         lfig.scatter(nt4p, nt4, color=getColor(nt_label[2]), marker=getMarker(nt_label[2]), s=30, label=nt_label[2], alpha=.5)
#     if len(nt5) > 0:
#         lfig.scatter(nt5p, nt5, color=getColor(nt_label[3]), marker=getMarker(nt_label[3]), s=30, label=nt_label[3], alpha=.5)
#     if len(nt6) > 0:
#         lfig.scatter(nt6p, nt6, color='k', marker='p', s=30, label="All-Tabued", alpha=.7)
              
    lfig.set_xlabel("Runtime (s)",fontsize=10)
#     lfig.set_ylabel("Power Consumption (kW)",fontsize=10)
    lfig.set_ylabel("Energy Consumption (kWh)",fontsize=10)
#     lfig.set_ylim(ymin=0, ymax=max(lnsobjvalue)+10)  
#     lfig.set_xlim(xmin=-5, xmax=4500)        
    lfig_fontP = FontProperties()
    lfig_fontP.set_size(13)        
    lfig_handles, lfig_labels = lfig.get_legend_handles_labels()
    lfig.legend(lfig_handles, lfig_labels, loc='best', ncol=1, prop=lfig_fontP)
#     lfig.set_title('[' + lnsdir + '\n' + lnsfile +']\n', fontsize=8)
    fig.autofmt_xdate()
     
    plt.savefig('Output\\'+ lnsfile +'_LNSnMILP7200_trace.png', dpi=400)
#     plt.show()
    plt.close(fig)
    print "Done!"




nt = '1'
prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140910_lnsvsmip7200/EAMS_v11_140908_mspec_mspecparam7200/src/Output/"

case = []
# # case.append("eams_meeting_m100_27_125000_7_OPTCFG_2014_09_09_18_06_25_588115")
# # case.append("eams_meeting_m100_27_642000_8_OPTCFG_2014_09_09_02_10_37_767234")
# case.append("eams_meeting_m100_27_125000_7_OPTCFG_2014_09_08_14_32_44_818690")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_08_14_32_45_048773")
# case.append("eams_meeting_m100_27_249000_0_OPTCFG_2014_09_08_16_49_50_185601")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_08_16_49_35_772159")
# case.append("eams_meeting_m100_27_249000_0_OPTCFG_2014_09_08_19_07_14_128364")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_08_19_10_38_673525")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_08_21_24_33_840466")
# case.append("eams_meeting_m100_27_642000_8_OPTCFG_2014_09_08_21_31_43_279130")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_08_23_41_54_646645")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_08_23_51_13_702880")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_09_02_01_24_144941")
# case.append("eams_meeting_m100_27_642000_8_OPTCFG_2014_09_09_02_10_37_767234")
# case.append("eams_meeting_m100_27_249000_0_OPTCFG_2014_09_09_04_20_49_358516")
# case.append("eams_meeting_m100_27_125000_7_OPTCFG_2014_09_09_04_29_51_551014")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_09_06_38_25_558526")
# case.append("eams_meeting_m100_27_249000_0_OPTCFG_2014_09_09_06_46_58_532245")
# case.append("eams_meeting_m100_27_125000_7_OPTCFG_2014_09_09_08_55_34_748319")
# case.append("eams_meeting_m100_27_125000_7_OPTCFG_2014_09_09_09_04_37_010458")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_09_11_12_32_186292")
# case.append("eams_meeting_m100_27_642000_8_OPTCFG_2014_09_09_11_21_51_645047")
# case.append("eams_meeting_m100_27_249000_0_OPTCFG_2014_09_09_13_29_44_727117")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_09_13_41_08_045292")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_09_15_46_55_871666")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_09_16_00_47_955019")
# case.append("eams_meeting_m100_27_125000_7_OPTCFG_2014_09_09_18_06_25_588115")
# case.append("eams_meeting_m100_27_125000_7_OPTCFG_2014_09_09_18_18_14_788935")
# case.append("eams_meeting_m100_27_642000_8_OPTCFG_2014_09_09_20_23_29_097674")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_09_20_35_18_538619")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_09_22_44_05_825949")
# case.append("eams_meeting_m100_27_249000_0_OPTCFG_2014_09_09_22_52_46_033179")
# case.append("eams_meeting_m100_27_053000_6_OPTCFG_2014_09_10_01_04_16_658850")
# case.append("eams_meeting_m100_27_642000_8_OPTCFG_2014_09_10_01_10_22_981547")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_10_03_22_05_910601")
# case.append("eams_meeting_m100_27_642000_2_OPTCFG_2014_09_10_03_30_07_297680")
# case.append("eams_meeting_m100_27_249000_0_OPTCFG_2014_09_10_05_39_36_607457")
# case.append("eams_meeting_m100_27_053000_6_OPTCFG_2014_09_10_05_50_35_458570")
# case.append("eams_meeting_m100_27_053000_6_OPTCFG_2014_09_10_07_57_27_065336")
# case.append("eams_meeting_m100_27_254000_6_OPTCFG_2014_09_10_08_08_14_252924")


# # 
case.append("eams_meeting_m200_29_523000_7_50R_OPTCFG_2014_09_08_14_33_14_440295")
case.append("eams_meeting_m200_27_301000_6_50R_OPTCFG_2014_09_10_01_54_21_447275")
# case.append("eams_meeting_m200_29_523000_7_50R_OPTCFG_2014_09_08_14_33_14_440295")
# case.append("eams_meeting_m200_29_052000_9_50R_OPTCFG_2014_09_08_14_33_13_980119")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_08_17_01_38_164128")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_08_17_05_36_849535")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_08_19_46_10_654188")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_08_19_54_14_663749")
# case.append("eams_meeting_m200_29_052000_9_50R_OPTCFG_2014_09_08_22_31_04_089904")
# case.append("eams_meeting_m200_28_580000_3_50R_OPTCFG_2014_09_08_22_42_48_957334")
# case.append("eams_meeting_m200_29_052000_9_50R_OPTCFG_2014_09_09_01_02_26_022252")
# case.append("eams_meeting_m200_29_052000_9_50R_OPTCFG_2014_09_09_01_22_54_262661")
# case.append("eams_meeting_m200_28_580000_3_50R_OPTCFG_2014_09_09_03_32_44_074680")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_09_03_55_16_743535")
# case.append("eams_meeting_m200_29_052000_9_50R_OPTCFG_2014_09_09_06_10_04_688921")
# case.append("eams_meeting_m200_28_580000_3_50R_OPTCFG_2014_09_09_06_41_10_140834")
# case.append("eams_meeting_m200_29_523000_7_50R_OPTCFG_2014_09_09_08_41_19_205269")
# case.append("eams_meeting_m200_27_434000_2_50R_OPTCFG_2014_09_09_09_20_54_815735")
# case.append("eams_meeting_m200_28_580000_3_50R_OPTCFG_2014_09_09_11_11_17_285413")
# case.append("eams_meeting_m200_28_580000_3_50R_OPTCFG_2014_09_09_12_04_51_618671")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_09_13_48_58_071794")
# case.append("eams_meeting_m200_29_523000_7_50R_OPTCFG_2014_09_09_14_44_39_369626")
# case.append("eams_meeting_m200_27_301000_6_50R_OPTCFG_2014_09_09_16_31_51_951486")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_09_17_15_40_448907")
# case.append("eams_meeting_m200_29_523000_7_50R_OPTCFG_2014_09_09_19_31_26_564037")
# case.append("eams_meeting_m200_27_301000_6_50R_OPTCFG_2014_09_09_20_04_02_022216")
# case.append("eams_meeting_m200_27_301000_5_50R_OPTCFG_2014_09_09_22_03_25_329893")
# case.append("eams_meeting_m200_29_052000_9_50R_OPTCFG_2014_09_09_23_19_07_642350")
# case.append("eams_meeting_m200_27_301000_6_50R_OPTCFG_2014_09_10_00_54_24_232741")
# case.append("eams_meeting_m200_27_301000_6_50R_OPTCFG_2014_09_10_01_54_21_447275")
# case.append("eams_meeting_m200_27_434000_2_50R_OPTCFG_2014_09_10_04_01_33_859421")
# case.append("eams_meeting_m200_27_301000_6_50R_OPTCFG_2014_09_10_05_02_53_532838")
# case.append("eams_meeting_m200_29_523000_7_50R_OPTCFG_2014_09_10_06_40_45_823844")
# case.append("eams_meeting_m200_28_580000_3_50R_OPTCFG_2014_09_10_08_09_50_538318")

# # case.append("eams_meeting_m500_30_050000_1_50R_OPTCFG_2014_09_08_20_35_55_330023")
# # case.append("eams_meeting_m500_30_050000_1_50R_OPTCFG_2014_09_09_01_22_21_793326")
# # case.append("eams_meeting_m500_30_050000_1_50R_OPTCFG_2014_09_09_12_24_21_628075")
# # case.append("eams_meeting_m500_29_352000_6_50R_OPTCFG_2014_09_09_10_20_59_625076")
# # case.append("eams_meeting_m500_30_050000_1_50R_OPTCFG_2014_09_10_00_30_18_705612")
# # case.append("eams_meeting_m500_30_050000_1_50R_OPTCFG_2014_09_10_02_28_54_287774")





for i in xrange(len(case)):
    plot_LNSnMILP_graph(1, prefix, case[i]+"_LNS_trace", prefix, "MILP_"+case[i]+"_solstats", nt, 0, 2)







