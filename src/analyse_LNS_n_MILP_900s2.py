
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

TSETS = ["eams_meeting_m20_07_011000_9", 
         "eams_meeting_m20_07_707000_2",
"eams_meeting_m20_07_838000_1",
"eams_meeting_m20_07_849000_9",
"eams_meeting_m20_07_716000_7",
"eams_meeting_m20_07_886000_4",
"eams_meeting_m20_07_011000_5",
"eams_meeting_m20_07_707000_1",
"eams_meeting_m20_07_838000_8",
"eams_meeting_m20_07_716000_5",
"eams_meeting_m50_07_738000_5",
"eams_meeting_m50_07_738000_9",
"eams_meeting_m50_07_807000_2",
"eams_meeting_m50_07_807000_8_m",
"eams_meeting_m50_07_514000_1_m",
"eams_meeting_m50_07_944000_7_m",
"eams_meeting_m50_07_738000_0",
"eams_meeting_m50_07_807000_3",
"eams_meeting_m50_07_807000_3_m",
"eams_meeting_m50_07_944000_1_m",
"eams_meeting_m100_27_249000_0",
"eams_meeting_m100_27_254000_6",
"eams_meeting_m100_27_125000_7",
"eams_meeting_m100_27_642000_2",
"eams_meeting_m100_27_642000_8",
"eams_meeting_m100_27_053000_6",
"eams_meeting_m100_27_249000_9",
"eams_meeting_m100_27_254000_2",
"eams_meeting_m100_27_642000_4",
"eams_meeting_m100_27_053000_3",
"eams_meeting_m200_27_301000_5",
"eams_meeting_m200_27_301000_6",
"eams_meeting_m200_28_580000_3",
"eams_meeting_m200_27_434000_2",
"eams_meeting_m200_29_523000_7",
"eams_meeting_m200_29_052000_9",
"eams_meeting_m200_27_301000_4",
"eams_meeting_m200_28_580000_1",
"eams_meeting_m200_27_434000_9",
"eams_meeting_m200_29_523000_9",
"eams_meeting_m50_07_738000_5_50R",
"eams_meeting_m50_07_738000_9_50R",
"eams_meeting_m50_07_807000_2_50R",
"eams_meeting_m50_07_807000_8_m_50R",
"eams_meeting_m50_07_514000_1_m_50R",
"eams_meeting_m50_07_944000_7_m_50R",
"eams_meeting_m50_07_738000_0_50R",
"eams_meeting_m50_07_807000_3_50R",
"eams_meeting_m50_07_807000_3_m_50R",
"eams_meeting_m50_07_944000_1_m_50R",
"eams_meeting_m100_27_249000_0_50R",
"eams_meeting_m100_27_254000_6_50R",
"eams_meeting_m100_27_125000_7_50R",
"eams_meeting_m100_27_642000_2_50R",
"eams_meeting_m100_27_642000_8_50R",
"eams_meeting_m100_27_053000_6_50R",
"eams_meeting_m100_27_249000_9_50R",
"eams_meeting_m100_27_254000_2_50R",
"eams_meeting_m100_27_642000_4_50R",
"eams_meeting_m100_27_053000_3_50R",
"eams_meeting_m200_27_301000_5_50R",
"eams_meeting_m200_27_301000_6_50R",
"eams_meeting_m200_28_580000_3_50R",
"eams_meeting_m200_27_434000_2_50R",
"eams_meeting_m200_29_523000_7_50R",
"eams_meeting_m200_29_052000_9_50R",
"eams_meeting_m200_27_301000_4_50R",
"eams_meeting_m200_28_580000_1_50R",
"eams_meeting_m200_27_434000_9_50R",
"eams_meeting_m200_29_523000_9_50R",
"eams_meeting_m500_29_352000_6_50R",
"eams_meeting_m500_29_427000_8_50R",
"eams_meeting_m500_29_699000_3_50R",
"eams_meeting_m500_30_050000_1_50R",
"eams_meeting_m500_30_643000_1_50R",
"eams_meeting_m500_30_053000_3_50R",
"eams_meeting_m500_29_427000_5_50R",
"eams_meeting_m500_29_699000_4_50R",
"eams_meeting_m500_30_643000_4_50R",
"eams_meeting_m500_30_053000_1_50R"]


TSETS_DICT = {}
TSETS_DICT["eams_meeting_m20_07_011000_9"] = 1 
TSETS_DICT["eams_meeting_m20_07_707000_2"] = 1 
TSETS_DICT["eams_meeting_m20_07_838000_1"] = 1 
TSETS_DICT["eams_meeting_m20_07_849000_9"] = 1 
TSETS_DICT["eams_meeting_m20_07_716000_7"] = 1 
TSETS_DICT["eams_meeting_m20_07_886000_4"] = 1 
TSETS_DICT["eams_meeting_m20_07_011000_5"] = 1
TSETS_DICT["eams_meeting_m20_07_707000_1"] = 1
TSETS_DICT["eams_meeting_m20_07_838000_8"] = 1
TSETS_DICT["eams_meeting_m20_07_716000_5"] = 1

TSETS_DICT["eams_meeting_m50_07_738000_5"] = 2
TSETS_DICT["eams_meeting_m50_07_738000_9"] = 2
TSETS_DICT["eams_meeting_m50_07_807000_2"] = 2
TSETS_DICT["eams_meeting_m50_07_807000_8_m"] = 2
TSETS_DICT["eams_meeting_m50_07_514000_1_m"] = 2
TSETS_DICT["eams_meeting_m50_07_944000_7_m"] = 2
TSETS_DICT["eams_meeting_m50_07_738000_0"] = 2
TSETS_DICT["eams_meeting_m50_07_807000_3"] = 2
TSETS_DICT["eams_meeting_m50_07_807000_3_m"] = 2
TSETS_DICT["eams_meeting_m50_07_944000_1_m"] = 2

TSETS_DICT["eams_meeting_m100_27_249000_0"] = 3
TSETS_DICT["eams_meeting_m100_27_254000_6"] = 3
TSETS_DICT["eams_meeting_m100_27_125000_7"] = 3
TSETS_DICT["eams_meeting_m100_27_642000_2"] = 3
TSETS_DICT["eams_meeting_m100_27_642000_8"] = 3
TSETS_DICT["eams_meeting_m100_27_053000_6"] = 3
TSETS_DICT["eams_meeting_m100_27_249000_9"] = 3
TSETS_DICT["eams_meeting_m100_27_254000_2"] = 3
TSETS_DICT["eams_meeting_m100_27_642000_4"] = 3
TSETS_DICT["eams_meeting_m100_27_053000_3"] = 3

TSETS_DICT["eams_meeting_m200_27_301000_5"] = 4
TSETS_DICT["eams_meeting_m200_27_301000_6"] = 4
TSETS_DICT["eams_meeting_m200_28_580000_3"] = 4
TSETS_DICT["eams_meeting_m200_27_434000_2"] = 4
TSETS_DICT["eams_meeting_m200_29_523000_7"] = 4
TSETS_DICT["eams_meeting_m200_29_052000_9"] = 4
TSETS_DICT["eams_meeting_m200_27_301000_4"] = 4
TSETS_DICT["eams_meeting_m200_28_580000_1"] = 4
TSETS_DICT["eams_meeting_m200_27_434000_9"] = 4
TSETS_DICT["eams_meeting_m200_29_523000_9"] = 4

TSETS_DICT["eams_meeting_m50_07_738000_5_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_738000_9_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_807000_2_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_807000_8_m_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_514000_1_m_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_944000_7_m_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_738000_0_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_807000_3_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_807000_3_m_50R"] = 5
TSETS_DICT["eams_meeting_m50_07_944000_1_m_50R"] = 5

TSETS_DICT["eams_meeting_m100_27_249000_0_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_254000_6_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_125000_7_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_642000_2_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_642000_8_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_053000_6_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_249000_9_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_254000_2_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_642000_4_50R"] = 6
TSETS_DICT["eams_meeting_m100_27_053000_3_50R"] = 6

TSETS_DICT["eams_meeting_m200_27_301000_5_50R"] = 7
TSETS_DICT["eams_meeting_m200_27_301000_6_50R"] = 7
TSETS_DICT["eams_meeting_m200_28_580000_3_50R"] = 7
TSETS_DICT["eams_meeting_m200_27_434000_2_50R"] = 7
TSETS_DICT["eams_meeting_m200_29_523000_7_50R"] = 7
TSETS_DICT["eams_meeting_m200_29_052000_9_50R"] = 7
TSETS_DICT["eams_meeting_m200_27_301000_4_50R"] = 7
TSETS_DICT["eams_meeting_m200_28_580000_1_50R"] = 7
TSETS_DICT["eams_meeting_m200_27_434000_9_50R"] = 7
TSETS_DICT["eams_meeting_m200_29_523000_9_50R"] = 7

TSETS_DICT["eams_meeting_m500_29_352000_6_50R"] = 8
TSETS_DICT["eams_meeting_m500_29_427000_8_50R"] = 8
TSETS_DICT["eams_meeting_m500_29_699000_3_50R"] = 8
TSETS_DICT["eams_meeting_m500_30_050000_1_50R"] = 8
TSETS_DICT["eams_meeting_m500_30_643000_1_50R"] = 8
TSETS_DICT["eams_meeting_m500_30_053000_3_50R"] = 8
TSETS_DICT["eams_meeting_m500_29_427000_5_50R"] = 8
TSETS_DICT["eams_meeting_m500_29_699000_4_50R"] = 8
TSETS_DICT["eams_meeting_m500_30_643000_4_50R"] = 8
TSETS_DICT["eams_meeting_m500_30_053000_1_50R"] = 8
  
def getInitSolValue(prefix, fname, maxdata, isall):    
    
    TESTCASE_GRP_COUNT = [0]*8  #only 8 grps
    
    testcase_db = fname  #"mall_stats.txt"    
    fstr = prefix + testcase_db        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()      
    # extract data
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
        
        caseid = parts[0].split('_OPTCFG')[0]   
        group = TSETS_DICT.get(caseid)-1      # group in TSETS_DICT (1-8, so -1)
        if isall:
            if maxdata < 0 or TESTCASE_GRP_COUNT[group] < (maxdata/8):
                TESTCASES.append(parts[0])
                TESTCASE_GRP_COUNT[group] = TESTCASE_GRP_COUNT[group] + 1
        else:
            if (maxdata < 0 or i < maxdata):
                TESTCASES.append(parts[0])
                TESTCASE_GRP_COUNT[group] = TESTCASE_GRP_COUNT[group] + 1
            else:
                break        
        
    # extract init solution
    for i in xrange(len(TESTCASES)):
        fstr = prefix + "MILP_" + TESTCASES[i] + "_solstats"
        data_file = open(fstr, 'r')
        data = ''.join(data_file.readlines())
        data_file.close()
        
        lines = data.split('\n')        
        if maxdata < 0 or i < maxdata:
            parts = lines[0].split(',')
            TESTCASES_INITSOL.append(float(parts[3])* 30 * 60 * 0.000277777778)
        else:
            break
        
    #     print TESTCASES
    print "total:", len(TESTCASES)
    print TESTCASE_GRP_COUNT

def getMIPLNSSolValue(prefix, fname, maxdata):     
    TESTCASES_LNSSOL = [0] * len(TESTCASES)
    TESTCASES_MIPSOL = [0] * len(TESTCASES)
    
    fstr = prefix + fname        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
        if parts[0] in TESTCASES:
            offset = TESTCASES.index(parts[0])  # offset in TESTCASES        
            TESTCASES_LNSSOL[offset] = float(parts[2])* 30 * 60 * 0.000277777778
            TESTCASES_MIPSOL[offset] = float(parts[3])* 30 * 60 * 0.000277777778
         
        
    TESTCASES_INIT_LNS_DIFF = [0] * len(TESTCASES)
    TESTCASES_MIP_LNS_DIFF = [0] * len(TESTCASES)    
#     print len(TESTCASES)
#     print len(TESTCASES_INITSOL)
#     print len(TESTCASES_LNSSOL)
#     print len(TESTCASES_MIPSOL)
#     print len(TESTCASES_INIT_LNS_DIFF)
#     print len(TESTCASES_MIP_LNS_DIFF)
    
    for i in xrange(len(TESTCASES)):
        TESTCASES_INIT_LNS_DIFF[i] = (TESTCASES_INITSOL[i]-TESTCASES_LNSSOL[i])/TESTCASES_LNSSOL[i]
        TESTCASES_MIP_LNS_DIFF[i] = (TESTCASES_MIPSOL[i]-TESTCASES_LNSSOL[i])/TESTCASES_LNSSOL[i]

            
    print np.mean(TESTCASES_INITSOL, axis=0), " ", np.mean(TESTCASES_MIPSOL, axis=0), " ",np.mean(TESTCASES_LNSSOL, axis=0), " ", np.mean(TESTCASES_INIT_LNS_DIFF, axis=0), " ", np.mean(TESTCASES_MIP_LNS_DIFF, axis=0)
    return [np.mean(TESTCASES_INITSOL, axis=0), np.mean(TESTCASES_MIPSOL, axis=0), np.mean(TESTCASES_LNSSOL, axis=0), np.mean(TESTCASES_INIT_LNS_DIFF, axis=0)*100, np.mean(TESTCASES_MIP_LNS_DIFF, axis=0)*100]
    
    
def plotGraph(INITVAL, MIPVAL, LNSVAL, INITVSLNS, MIPVSLNS, fname):
        
    fig, ax = plt.subplots()    
    ind = np.arange(len(LNSVAL))  
    width = 0.2       # the width of the bars
    case = ["All M, All R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
    
    rects1 = ax.bar(ind, INITVAL, width, color='#d6d6d6', label='HS', hatch=".") 
    rects2 = ax.bar(ind+width, MIPVAL, width, color='#666666', label='MILP', hatch="/") 
    rects3 = ax.bar(ind+(width*2), LNSVAL, width, color='#ededed', label='LNS')
    
    def autolabel(rects1, rects2, rects3):
        count1 = 0
        for recta in rects1:
            count2 = 0
            for rectc in rects3:
                if count1 == count2:         
                    height1 = recta.get_height()
                    height3 = rectc.get_height()                    
                    val = float((height1-height3))/height3*100
                    print height1, " ", height3, " ", val
                    if count2 == 0:
                        ax.text(recta.get_x()+recta.get_width()+0.1, 1.04*height1, '%d%%'%int(val),
                        ha='center', va='bottom')
                    elif count2 == 8:
                        ax.text(recta.get_x()+recta.get_width()-0.25, 1.01*height1, '%d%%'%int(val),
                        ha='center', va='bottom')
                    else:
                        ax.text(recta.get_x()+recta.get_width()-0.1, 1.04*height1, '%d%%'%int(val),
                        ha='center', va='bottom')
                    break
                count2 = count2+1
            count1 = count1+1
        
        count1 = 0
        for rectb in rects2:
            count2 = 0
            for rectc in rects3:
                if count1 == count2:         
                    height2 = rectb.get_height()
                    height3 = rectc.get_height()                    
                    val = float((height2-height3))/height3*100
                    print height2, " ", height3, " ", val
                    ax.text(rectb.get_x()+rectb.get_width()+0.15, 1.01*height2, '%d%%'%int(val),
                        ha='center', va='bottom')
                    break
                count2 = count2+1
            count1 = count1+1
            
    autolabel(rects1, rects2, rects3)
    
    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('large')
    ax.legend(handles, labels, loc='best', prop=fontP)   
      
    ax.set_title('['+fname+']', fontsize=8)
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(case) 
    ax.set_ylabel("Avg. Energy Consumption (kWh)") 
    ax.set_ylim([0,17000])
    
    fig.autofmt_xdate()
    
    plt.savefig("Output/"+fname, dpi=300)
#     plt.show()
    plt.close(fig)
#-----------------------------------------


def plotHorizGraph(INITVAL, MIPVAL, LNSVAL, INITVSLNS, MIPVSLNS, fname):
        
    fig, ax = plt.subplots()    
    ind = np.arange(len(LNSVAL))  
    width = 0.25       # the width of the bars
    case = ["All M-All R", "20M-20R", "50M-20R", "100M-20R", "200M-20R", "50M-50R", "100M-50R", "200M-50R", "500M-50R"]
     
    rects1 = ax.barh(ind+(width*2), INITVAL, width, color='#d6d6d6', label='HS', hatch=".")
    rects2 = ax.barh(ind+width, MIPVAL, width, color='#666666', label='MILP', hatch="/")
    rects3 = ax.barh(ind, LNSVAL, width, color='#ededed', label='LNS')
    
    def autolabel(rects1, rects2, rects3):
# ------------------ based on rects3
        count1 = 0
        for rectb in rects1:
            count2 = 0
            for recta in rects3:
                if count1 == count2:         
                    height2 = rectb.get_width()
                    height1 = recta.get_width()                    
                    val = float((height2-height1))/height1*100
                    print height1, " ", height2, " ", val
                    ax.text(1*height2+1000, rectb.get_y()-0.1, '%d%%'%int(val), ha='center', va='bottom', size='10')
                    break
                count2 = count2+1
            count1 = count1+1
              
        count1 = 0
        for recta in rects3:
            count2 = 0
            for rectc in rects2:
                if count1 == count2:         
                    height1 = recta.get_width()
                    height3 = rectc.get_width()                    
                    val = float((height3-height1))/height1*100
                    print height1, " ", height3, " ", val
                    ax.text(1*height3+1000, rectc.get_y()-0.15, '%d%%'%int(val),
                        ha='center', va='bottom', size='10')
                    break
                count2 = count2+1
            count1 = count1+1
            
    autolabel(rects1, rects2, rects3)
    
    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('large')
    ax.legend(handles, labels, loc='best', prop=fontP)   
      
#     ax.set_title('['+fname+']', fontsize=8)
    ax.set_yticks(ind+width)  
    ax.set_yticklabels(case) 
    ax.set_ylim(-0.2, len(ind))
    ax.set_xlabel("Avg. Energy Consumption (kWh)") 
    ax.set_xlim([0,18000])
    
    fig.autofmt_xdate()
    
    plt.savefig("Output/"+fname, dpi=300)
#     plt.show()
#     plt.close(fig)

#---------------------------------
# Never delete this!
prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mspecparam900/src/Output/"  # AAAI!
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mallparam900/src/Output/"
fname = "lnsmip_mspec_mspec900"
maxdata = 100
maxalldata = maxdata*8
#---------------------------------

# maxdata = 100
# maxdata = 200
# maxdata = 500
# fname = "lnsmip_mspec_mspec7200"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140908_mspec_mspecparam7200/src/Output/"
# fname = "lnsmip_mspec_mspec7200_0908"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140908_mspec_mspecparam7200/src/Output/"
# fname = "lnsmip_mspec_mspec7200_0910"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140910_mspec_mspecparam7200/src/Output/"

# fname = "lnsmip_mspec_mall7200"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140908_mspec_mallparam7200/src/Output/"
# fname = "lnsmip_mspec_mall7200_0908"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140908_mspec_mallparam7200/src/Output/"
# fname = "lnsmip_mspec_mall7200_0910"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140910_mspec_mallparam7200/src/Output/"


# maxdata = 100
# maxdata = 500
# fname = "lnsmip_mall_mspec900"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140908_mspec_mallparam900/src/Output/"
# fname = "lnsmip_mspec_mspec900"
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/141002_lns/EAMS_v11_140908_mspec_mspecparam900/src/Output/"


# maxalldata = maxdata*8

INITVAL = []
MIPVAL  = []
LNSVAL  = []
INITVSLNS   = []
MIPVSLNS    = []

TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "mall_stats.txt", maxalldata, 1)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "mall_stats.txt", maxalldata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)

TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m20_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m20_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)
 
TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m50_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m50_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)
 
TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m100_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m100_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)
 
TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m200_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m200_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)
 
TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m50_50r_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m50_50r_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)
 
TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m100_50r_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m100_50r_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)
 
TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m200_50r_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m200_50r_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)
 
TESTCASES = []
TESTCASES_INITSOL = []
TESTCASES_LNSSOL = []
TESTCASES_MIPSOL = []
TESTCASES_INIT_LNS_DIFF = []
TESTCASES_MIP_LNS_DIFF = []
getInitSolValue(prefix, "m500_50r_lns_stats", maxdata, 0)
[init, mip, lns, initvslns, mipvslns] = getMIPLNSSolValue(prefix, "m500_50r_lns_stats", maxdata)
INITVAL.append(init)
MIPVAL.append(mip)
LNSVAL.append(lns)
INITVSLNS.append(initvslns)
MIPVSLNS.append(mipvslns)


# plotGraph(INITVAL, MIPVAL, LNSVAL, INITVSLNS, MIPVSLNS, fname+"_maxdata"+str(maxdata))
plotHorizGraph(INITVAL, MIPVAL, LNSVAL, INITVSLNS, MIPVSLNS, fname+"_maxdata"+str(maxdata)+"_horiz")

