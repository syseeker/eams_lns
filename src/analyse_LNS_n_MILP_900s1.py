
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

def analyse_performance(label, data, filter, maxset):    
    
    TESTCASE_LNS_ELEM = []
    TESTCASE_MIP_ELEM = []
    TESTCASE_COUNT = [0]*len(TSETS)
    TESTCASE_GRP_COUNT = [0]*8  #only 8 grps
    for i in xrange(len(TESTCASE_COUNT)):
        TESTCASE_LNS_ELEM.append([])
        TESTCASE_MIP_ELEM.append([])
    
    # extract data
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
        caseid = parts[0].split('_OPTCFG')[0]
        offset = TSETS.index(caseid)
         
        # extract data for group in "filter" only   
        group = TSETS_DICT.get(caseid) 
        if len(filter) > 0:
            if group not in filter:
                continue   
                               
        TESTCASE_GRP_COUNT[group-1] = TESTCASE_GRP_COUNT[group-1] + 1    
        # extract max number of data only, if indicate
        if maxset < 0 or TESTCASE_GRP_COUNT[group-1] <= maxset: #or TESTCASE_COUNT[offset] < maxset:
            TESTCASE_COUNT[offset] = TESTCASE_COUNT[offset] + 1
            TESTCASE_LNS_ELEM[offset].append(float(parts[2])* 30 * 60 * 0.000277777778)
            TESTCASE_MIP_ELEM[offset].append(float(parts[3])* 30 * 60 * 0.000277777778)
            
    LNSMEAN_ARR = []
    LNSSTD_ARR = []
    MIPMEAN_ARR = []
    MIPSTD_ARR = []
    LNSVSMIP_ARR = []
    NUM_TESTCASE = 0
    
    # calculate statistics
    print "|Testcase | #run | LNS mean  | LNS stddev   | MIP mean  | MIP stddev | LNS vs MIP|"    
    if PRINT:
        try:            
            fstr = 'Output/' + label + '_population.txt'
            f = open(fstr,'a')
            f.write(",".join(map(str, ["Testcase", "Count", "LNS Mean", "LNS Std Dev", "MIP Mean", "MIP Std Dev", "Compare"])))
            f.write("\n")
            f.close()  
        except (ValueError), e:
            print ('%s' % (e)) 
        
    for i in xrange(len(TESTCASE_COUNT)):        
        if TESTCASE_COUNT[i] > 0:
            lnsarr = np.array(TESTCASE_LNS_ELEM[i])
            lnsmean = np.mean(lnsarr, axis=0)
            lnsstd = np.std(lnsarr, axis=0)
            
            miparr = np.array(TESTCASE_MIP_ELEM[i])
            mipmean = np.mean(miparr, axis=0)
            mipstd = np.std(miparr, axis=0)
            
            NUM_TESTCASE = NUM_TESTCASE + len(TESTCASE_LNS_ELEM[i])
            
            lnsvsmip = (mipmean-lnsmean)/lnsmean*100
            
            print "|", TSETS[i], "|", TESTCASE_COUNT[i], "|", round(lnsmean,2), "   |", round(lnsstd,2), "     | ", round(mipmean,2), "   | ", round(mipstd,2), "|", round(lnsvsmip,1)
            
            LNSMEAN_ARR.append(lnsmean)
            LNSSTD_ARR.append(lnsstd)
            MIPMEAN_ARR.append(mipmean)
            MIPSTD_ARR.append(mipstd)
            LNSVSMIP_ARR.append(lnsvsmip)
        
            if PRINT:
                # print to file
                try:            
                    fstr = 'Output/' + label + '_population.txt'
                    f = open(fstr,'a')
                    f.write(",".join(map(str, [TSETS[i],  TESTCASE_COUNT[i], round(lnsmean,2), round(lnsstd,2), round(mipmean,2), round(mipstd,2), round(lnsvsmip,1)])))
                    f.write("\n")
                    f.close()     
                except (ValueError), e:
                    print ('%s' % (e)) 

    print label, ": #input=", NUM_TESTCASE, " lnsmean=", np.mean(LNSMEAN_ARR, axis=0), " mipmean=", np.mean(MIPMEAN_ARR, axis=0)
    return [np.mean(LNSMEAN_ARR, axis=0), np.mean(MIPMEAN_ARR, axis=0)]
  

def compare_LNS_MILP(prefix, label, fname, filter, maxset):
    fstr = prefix + fname        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    [lns, mip] = analyse_performance(label, data, filter, maxset)
    return [lns, mip]


def plotGraph():
    
#     [case, lnsbar, mipbar] = getLNSMIP_DuringTune()
#     fname = "lnsmip_900s_tuneprms"
    
#     [case, lnsbar, mipbar] = getLNSMIP_TL10()
#     fname = "lnsmip_tl10"
    
#     [case, lnsbar, mipbar] = getLNSMIP_TL60()
#     fname = "lnsmip_tl60"

    [case, lnsbar, mipbar] = getLNSMIP_BestParamMIP900()
    fname = "lnsmip_bestparam_mspec_mip900"
    
#     [case, lnsbar, mipbar] = getLNSMIP_BestParamMIP7200()
#     fname = "lnsmip_bestparam_mip7200"
        
    fig, ax = plt.subplots()    
    ind = np.arange(len(lnsbar))  
    width = 0.4       # the width of the bars

    rects1 = ax.bar(ind, mipbar, width, color='#666666', label='MIP', hatch="/") 
    rects2 = ax.bar(ind+width, lnsbar, width, color='#ededed', label='LNS')
    
    def autolabel(rects1, rects2):
        count1 = 0
        for recta in rects1:
            count2 = 0
            for rectb in rects2:
                if count1 == count2:         
                    height1 = recta.get_height()
                    height2 = rectb.get_height()                    
                    val = float((height1-height2))/height2*100
                    print height1, " ", height2, " ", val
                    ax.text(recta.get_x()+recta.get_width()/2., 1.02*height1, '%d%%'%int(val),
                        ha='center', va='bottom')
                    break
                count2 = count2+1
            count1 = count1+1
    
    autolabel(rects1, rects2)
    
    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('large')
    ax.legend(handles, labels, loc='upper left', prop=fontP)   
      
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(case) 
    ax.set_ylabel("Energy Consumption (kWh)") 
    ax.set_ylim([0,18000])
    
    fig.autofmt_xdate()
    
#     plt.savefig("Output/"+fname, dpi=300)
    plt.show()
#     plt.close(fig)


def getLNSMIP_TL10():    
    
    maxdata = -1
    lnsbar = []
    mipbar = []
    case = ["All M, All R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140908_sneakpeak/EAMS_v11_140907_mall_fixedMIPTimeLimit/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)    
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [1], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)   
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [2], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [3], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [4], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [5], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [6], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [7], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl10_stats", [8], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    return [case, lnsbar, mipbar]
    
    
def getLNSMIP_TL60():    
    
    maxdata = -1
    lnsbar = []
    mipbar = []
    case = ["All M, All R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140908_sneakpeak/EAMS_v11_140907_mall_fixedMIPTimeLimit/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)    
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [1], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)   
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [2], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [3], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [4], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [5], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [6], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [7], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_tl60_stats", [8], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)  
    
    return [case, lnsbar, mipbar]

    
def getLNSMIP_DuringTune():  
    
    maxdata = -1   
    lnsbar = []
    mipbar = []
    case = ["All M, All R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
        
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mall/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
      
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mspec_20r/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "m20_20r", "m20_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
        
    [lns, mip] = compare_LNS_MILP(prefix, "m50_20r", "m50_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m100_20r", "m100_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m200_20r", "m200_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
      
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mspec_50r/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "m50_50r", "m50_50r_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m100_50r", "m100_50r_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m200_50r", "m200_50r_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m500_50r", "m500_50r_lns_stats", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
    
    return [case, lnsbar, mipbar]
    

def getLNSMIP_BestParamMIP7200(): 
    
    maxdata = 5    
    lnsbar = []
    mipbar = []
    case = ["All M, All R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
        
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140908_sneakpeak/EAMS_v11_140907_mspec_bestparam7200/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_stats.txt", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
    
    [lns, mip] = compare_LNS_MILP(prefix, "m20_20r", "m20_lns_stats", [1], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
        
    [lns, mip] = compare_LNS_MILP(prefix, "m50_20r", "m50_lns_stats", [2], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m100_20r", "m100_lns_stats", [3], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m200_20r", "m200_lns_stats", [4], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
    
    [lns, mip] = compare_LNS_MILP(prefix, "m50_50r", "m50_50r_lns_stats", [5], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m100_50r", "m100_50r_lns_stats", [6], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m200_50r", "m200_50r_lns_stats", [7], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m500_50r", "m500_50r_lns_stats", [8], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
    
    return [case, lnsbar, mipbar]
    
    
def getLNSMIP_BestParamMIP900():     
    
    maxdata = 100
    lnsbar = []
    mipbar = []
    case = ["All M, All R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
    
#     prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mspecparam900/src/Output/"
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mallparam900/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_stats.txt", [], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
     
    [lns, mip] = compare_LNS_MILP(prefix, "m20_20r", "m20_lns_stats", [1], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
         
    [lns, mip] = compare_LNS_MILP(prefix, "m50_20r", "m50_lns_stats", [2], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
             
    [lns, mip] = compare_LNS_MILP(prefix, "m100_20r", "m100_lns_stats", [3], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
             
    [lns, mip] = compare_LNS_MILP(prefix, "m200_20r", "m200_lns_stats", [4], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
    
    [lns, mip] = compare_LNS_MILP(prefix, "m50_50r", "m50_50r_lns_stats", [5], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
            
    [lns, mip] = compare_LNS_MILP(prefix, "m100_50r", "m100_50r_lns_stats", [6], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
             
    [lns, mip] = compare_LNS_MILP(prefix, "m200_50r", "m200_50r_lns_stats", [7], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
             
    [lns, mip] = compare_LNS_MILP(prefix, "m500_50r", "m500_50r_lns_stats", [8], maxdata)
    lnsbar.append(lns)
    mipbar.append(mip)
    
    return [case, lnsbar, mipbar]

def mergeInitData():
#     prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mallparam900/src/Output/"
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mspecparam900/src/Output/"
    testcase_db = "mall_stats.txt"
    
    fstr = prefix + testcase_db        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    TESTCASES = []
    # extract data
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
        TESTCASES.append(parts[0])
        
    print TESTCASES
    print "total:", len(TESTCASES)
        
    
    
PRINT = 0

# plotGraph()
mergeInitData()


