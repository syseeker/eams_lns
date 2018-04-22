
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

TSETS = ["eams_meeting_m20_07_011000_9", 
         "eams_meeting_m20_07_707000_2",
"eams_meeting_m20_07_838000_1",
"eams_meeting_m20_07_849000_9",
"eams_meeting_m20_07_716000_7",
"eams_meeting_m20_07_886000_4",
"eams_meeting_m50_07_738000_5",
"eams_meeting_m50_07_738000_9",
"eams_meeting_m50_07_807000_2",
"eams_meeting_m50_07_807000_8_m",
"eams_meeting_m50_07_514000_1_m",
"eams_meeting_m50_07_944000_7_m",
"eams_meeting_m100_27_249000_0",
"eams_meeting_m100_27_254000_6",
"eams_meeting_m100_27_125000_7",
"eams_meeting_m100_27_642000_2",
"eams_meeting_m100_27_642000_8",
"eams_meeting_m100_27_053000_6",
"eams_meeting_m200_27_301000_5",
"eams_meeting_m200_27_301000_6",
"eams_meeting_m200_28_580000_3",
"eams_meeting_m200_27_434000_2",
"eams_meeting_m200_29_523000_7",
"eams_meeting_m200_29_052000_9",
"eams_meeting_m50_07_738000_5_50R",
"eams_meeting_m50_07_738000_9_50R",
"eams_meeting_m50_07_807000_2_50R",
"eams_meeting_m50_07_807000_8_m_50R",
"eams_meeting_m50_07_514000_1_m_50R",
"eams_meeting_m50_07_944000_7_m_50R",
"eams_meeting_m100_27_249000_0_50R",
"eams_meeting_m100_27_254000_6_50R",
"eams_meeting_m100_27_125000_7_50R",
"eams_meeting_m100_27_642000_2_50R",
"eams_meeting_m100_27_642000_8_50R",
"eams_meeting_m100_27_053000_6_50R",
"eams_meeting_m200_27_301000_5_50R",
"eams_meeting_m200_27_301000_6_50R",
"eams_meeting_m200_28_580000_3_50R",
"eams_meeting_m200_27_434000_2_50R",
"eams_meeting_m200_29_523000_7_50R",
"eams_meeting_m200_29_052000_9_50R",
"eams_meeting_m500_29_352000_6_50R",
"eams_meeting_m500_29_427000_8_50R",
"eams_meeting_m500_29_699000_3_50R",
"eams_meeting_m500_30_050000_1_50R",
"eams_meeting_m500_30_643000_1_50R",
"eams_meeting_m500_30_053000_3_50R"]

# def analyse_case_performance(label, data):    
#     TESTCASE_ARR = []    
#     TESTCASE_COUNT = []
#     TESTCASE_FULLNAME_ARR = []
#     TESTCASE_LNS_ELEM = []
#     TESTCASE_MIP_ELEM = []
#     
#     LNSVSMIP_ELEM = []
#     
#     lines = data.split('\n')
#     for i in xrange(len(lines)-1):
#         line = lines[i]
#         parts = line.split(',')
#         caseid = parts[0][13:35]
#         if caseid not in TESTCASE_ARR:
#             TESTCASE_ARR.append(caseid)
#             TESTCASE_COUNT.append(1)
#             
#             TESTCASE_FULLNAME_ARR.append([parts[0]])
#             TESTCASE_LNS_ELEM.append([float(parts[2])])
#             TESTCASE_MIP_ELEM.append([float(parts[3])])
#             
#             lnsvsmip = (float(parts[3])-float(parts[2]))/float(parts[2])*100
#             LNSVSMIP_ELEM.append([lnsvsmip])
#             
#         else:
#             offset = TESTCASE_ARR.index(caseid)
#             TESTCASE_COUNT[offset] = TESTCASE_COUNT[offset] + 1
#             
#             TESTCASE_FULLNAME_ARR[offset].append(parts[0])
#             TESTCASE_LNS_ELEM[offset].append(float(parts[2]))
#             TESTCASE_MIP_ELEM[offset].append(float(parts[3]))
#             
#             lnsvsmip = (float(parts[3])-float(parts[2]))/float(parts[2])*100
#             LNSVSMIP_ELEM[offset].append(lnsvsmip)
#     
#     
#     print "| Testcase | LNS   | MIP   | Compare  | Filename"
#     for i in xrange(len(LNSVSMIP_ELEM)):
#         for j in xrange(len(LNSVSMIP_ELEM[i])):
#             print "|", TESTCASE_ARR[i], "|", round(TESTCASE_LNS_ELEM[i][j],2), "   |", round(TESTCASE_MIP_ELEM[i][j],2), "     | ", round(LNSVSMIP_ELEM[i][j],2), "   |", TESTCASE_FULLNAME_ARR[i][j] 
#     
#     # print to file
#     try:            
#         fstr = 'Output/' + label + '_indiv.txt'
#         f = open(fstr,'a')
#         f.write(",".join(map(str, ["Testcase", "LNS", "MIP", "Compare", "Filename"])))
#         f.write("\n")
#         for i in xrange(len(LNSVSMIP_ELEM)):
#             for j in xrange(len(LNSVSMIP_ELEM[i])):
#                 f.write(",".join(map(str, [TESTCASE_ARR[i], round(TESTCASE_LNS_ELEM[i][j],2), round(TESTCASE_MIP_ELEM[i][j],2), round(LNSVSMIP_ELEM[i][j],2), TESTCASE_FULLNAME_ARR[i][j]])))
#                 f.write("\n")
#         f.close()      
#         
#     except (ValueError), e:
#         print ('%s' % (e)) 

def analyse_performance(label, data):    
    
    TESTCASE_ARR = []
    TESTCASE_COUNT = []
    TESTCASE_LNS_ELEM = []
    TESTCASE_MIP_ELEM = []
    
    # extract data
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split(',')
#         caseid = parts[0][13:35]
        caseid = parts[0].split('_OPTCFG')
        if caseid not in TESTCASE_ARR:
            TESTCASE_ARR.append(caseid)
            TESTCASE_COUNT.append(1)
            
            TESTCASE_LNS_ELEM.append([float(parts[2])* 30 * 60 * 0.000277777778])
            TESTCASE_MIP_ELEM.append([float(parts[3])* 30 * 60 * 0.000277777778])
        else:
            offset = TESTCASE_ARR.index(caseid)
            TESTCASE_COUNT[offset] = TESTCASE_COUNT[offset] + 1
            
            TESTCASE_LNS_ELEM[offset].append(float(parts[2])* 30 * 60 * 0.000277777778)
            TESTCASE_MIP_ELEM[offset].append(float(parts[3])* 30 * 60 * 0.000277777778)
            
    LNSMEAN_ARR = []
    LNSSTD_ARR = []
    MIPMEAN_ARR = []
    MIPSTD_ARR = []
    LNSVSMIP_ARR = []
    # calculate statistics
    for i in xrange(len(TESTCASE_COUNT)):
        
        lnsarr = np.array(TESTCASE_LNS_ELEM[i])
        lnsmean = np.mean(lnsarr, axis=0)
        lnsstd = np.std(lnsarr, axis=0)
        
        miparr = np.array(TESTCASE_MIP_ELEM[i])
        mipmean = np.mean(miparr, axis=0)
        mipstd = np.std(miparr, axis=0)
        
        lnsvsmip = (mipmean-lnsmean)/lnsmean*100
        
#         print "|", TESTCASE_ARR[i], "|", TESTCASE_COUNT[i], "|", round(lnsmean,2), "   |", round(lnsstd,2), "     | ", round(mipmean,2), "   | ", round(mipstd,2), "|", round(lnsvsmip,1)
        
        LNSMEAN_ARR.append(lnsmean)
        LNSSTD_ARR.append(lnsstd)
        MIPMEAN_ARR.append(mipmean)
        MIPSTD_ARR.append(mipstd)
        LNSVSMIP_ARR.append(lnsvsmip)
        
        
    # sort testcase based on meeting number    
    SORTED_TESTCASE = {}   
    for i in xrange(len(TESTCASE_COUNT)):
        if TESTCASE_ARR[i][0:5] not in SORTED_TESTCASE:
            SORTED_TESTCASE[TESTCASE_ARR[i][0:5]] = [i]
        else:
            SORTED_TESTCASE.get(TESTCASE_ARR[i][0:5]).append(i)
            
            
    for k, v in SORTED_TESTCASE.iteritems():
        lnsval = 0
        mipval = 0
        num = 0
        for j in xrange(len(v)):
            i = v[j]
            lnsval = lnsval + LNSMEAN_ARR[i]
            mipval = mipval + MIPMEAN_ARR[i]
            num = num+1
        
        print k, " ", round(lnsval/num, 2), " ", round(mipval/num, 2)
            
    return [round(lnsval/num, 2), round(mipval/num, 2)]
            
#     print SORTED_TESTCASE
#     for _, v in SORTED_TESTCASE.iteritems():
#         for j in xrange(len(v)):
#             i = v[j]
#             print "|", TESTCASE_ARR[i], "|", TESTCASE_COUNT[i], "|", round(LNSMEAN_ARR[i],2), "   |", round(LNSSTD_ARR[i],2), "     | ", round(MIPMEAN_ARR[i],2), "   | ", round(MIPSTD_ARR[i],2), "|", round(LNSVSMIP_ARR[i],1)
    
        
    # print to file
#     try:            
#         fstr = 'Output/' + label + '_population.txt'
#         f = open(fstr,'a')
#         f.write(",".join(map(str, ["Testcase", "Count", "LNS Mean", "LNS Std Dev", "MIP Mean", "MIP Std Dev", "Compare"])))
#         f.write("\n")
#         for _, v in SORTED_TESTCASE.iteritems():
#             for j in xrange(len(v)):
#                 i = v[j]
#                 print "|", TESTCASE_ARR[i], "|", TESTCASE_COUNT[i], "|", round(LNSMEAN_ARR[i],2), "   |", round(LNSSTD_ARR[i],2), "     | ", round(MIPMEAN_ARR[i],2), "   | ", round(MIPSTD_ARR[i],2), "|", round(LNSVSMIP_ARR[i],1)
#                 f.write(",".join(map(str, [TESTCASE_ARR[i],  TESTCASE_COUNT[i], round(LNSMEAN_ARR[i],2), round(LNSSTD_ARR[i],2), round(MIPMEAN_ARR[i],2), round(MIPSTD_ARR[i],2), round(LNSVSMIP_ARR[i],1)])))
#                 f.write("\n")
#         
#         f.close()      
#         
#     except (ValueError), e:
#         print ('%s' % (e)) 
#        

def compare_LNS_MILP(prefix, label, fname):
    fstr = prefix + fname        
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
#     analyse_case_performance(label, data)
    [lns, mip] = analyse_performance(label, data)
    return [lns, mip]


def plotGraph():
    
    lnsbar = []
    mipbar = []
    
    case = ["All M, All R", "All M, 20R", "All M, 50R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
    
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mall/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall", "mall_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
    
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mall_20R/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall_20r", "mall_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
      
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mall_50R/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "mall_50r", "mall_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
    
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mspec_20r/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "m20_20r", "m20_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
      
    [lns, mip] = compare_LNS_MILP(prefix, "m50_20r", "m50_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
          
    [lns, mip] = compare_LNS_MILP(prefix, "m100_20r", "m100_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
          
    [lns, mip] = compare_LNS_MILP(prefix, "m200_20r", "m200_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
    
    prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140907_results/EAMS_v11_140830_mspec_50r/src/Output/"
    [lns, mip] = compare_LNS_MILP(prefix, "m50_50r", "m50_50r_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
          
    [lns, mip] = compare_LNS_MILP(prefix, "m100_50r", "m100_50r_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
          
    [lns, mip] = compare_LNS_MILP(prefix, "m200_50r", "m200_50r_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
          
    [lns, mip] = compare_LNS_MILP(prefix, "m500_50r", "m500_50r_lns_stats")
    lnsbar.append(lns)
    mipbar.append(mip)
        
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
    ax.legend(handles, labels, loc='best', prop=fontP)   
      
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(case) 
    ax.set_ylabel("Energy Consumption (kWh)") 
    ax.set_ylim([0,18000])
    
    fig.autofmt_xdate()
    
#     plt.savefig('Output\\lnsmip_900s.png', dpi=300)
    plt.show()
#     plt.close(fig)
    
plotGraph()

# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140903_result/EAMS_v11_140830_mall/src/Output/"
# compare_LNS_MILP("mall", "mall_lns_stats")
# 
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140903_result/EAMS_v11_140830_mall_20R/src/Output/"
# compare_LNS_MILP("mall_20r", "mall_lns_stats")
# 
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140903_result/EAMS_v11_140830_mall_50R/src/Output/"
# compare_LNS_MILP("mall_50r", "mall_lns_stats")
