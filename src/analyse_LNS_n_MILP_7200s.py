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

def read_milp(dm1, dm2, dm3):
    
    data_file = open(dm1, 'r')
    s1 = ''.join(data_file.readlines())
    data_file.close()
    data_file = open(dm2, 'r')
    s2 = ''.join(data_file.readlines())
    data_file.close()
    data_file = open(dm3, 'r')
    s3 = ''.join(data_file.readlines())
    data_file.close()
    
    dataset = [s1, s2, s3]
    
    TESTCASE_COUNT = [0]*len(TSETS)
    TESTCASE_VAL = np.zeros((len(TSETS), 3))
    TESTCASE_MEAN =  [0]*len(TSETS)
    TESTCASE_STDDEV =  [0]*len(TSETS)
    
    cnt = 0
    for s in dataset:    
        lines = s.split('\n')
        for i in xrange(len(lines)-1):
            line = lines[i]
            parts = line.split(' ')
#             if parts[0] in TSETS:
            offset = TSETS.index(parts[0])
            TESTCASE_COUNT[offset] = TESTCASE_COUNT[offset]+1
            TESTCASE_VAL[offset][cnt] = float(parts[2])
        cnt = cnt + 1        
                
    for i in xrange(len(TSETS)):
        TESTCASE_MEAN[i] = np.mean(TESTCASE_VAL[i], axis=0)
        TESTCASE_STDDEV[i] = np.std(TESTCASE_VAL[i], axis=0)
    
    for i in xrange(len(TSETS)):
        print TSETS[i], " ", TESTCASE_COUNT[i] , " ", TESTCASE_VAL[i], " ", TESTCASE_MEAN[i], " ", TESTCASE_STDDEV[i]
            
    
    # print to file
    try:            
        fstr = 'Output/milp7200.txt'
        f = open(fstr,'a')
        f.write(",".join(map(str, ["Testcase", "Count", "VAL1", "VAL2", "VAL3", "Mean", "StdDev"])))
        f.write("\n")
        for i in xrange(len(TSETS)):
            f.write(",".join(map(str, [TSETS[i], TESTCASE_COUNT[i], round(TESTCASE_VAL[i][0],2), round(TESTCASE_VAL[i][1],2), round(TESTCASE_VAL[i][2],2), TESTCASE_MEAN[i],TESTCASE_STDDEV[i]])))
            f.write("\n")
        f.close()      
        
    except (ValueError), e:
        print ('%s' % (e)) 
    
   
    
def plotGraph():
    
    case = ["m20_r20", "m50_r20", "m100_r20", "m200_r20", "m50_r50", "m100_r50", "m200_r50", "m500_r50"]    
    
    # 1run, intel only
    lnsbar_kW = [3948.101667, 4371.381667, 5789.181667, 9662.79, 9828.36, 10831.94333, 14071.05667, 24381.09167]
#     mipbar_kW = [3946.881667, 4115.863333, 5645.15, 10408.08833, 10138.17, 11509.17167, 18696.52, 22716.91]    
    # 3runs, with amd2, amd, intel
    mipbar_kW = [3944.575484, 4066.012468, 5504.697315, 10394.64071, 10207.54671, 11208.06007, 17804.40919, 22716.91]

    
    lnsbar = []
    mipbar = []
    for i in xrange(len(lnsbar_kW)):
        lnsbar.append(lnsbar_kW[i]* 30 * 60 * 0.000277777778)
        mipbar.append(mipbar_kW[i]* 30 * 60 * 0.000277777778)
    
    fig, ax = plt.subplots()    
    ind = np.arange(len(lnsbar))  
    width = 0.3       # the width of the bars

    rects1 = ax.bar(ind, lnsbar, width, color='#ededed', label='LNS') 
    rects2 = ax.bar(ind+width, mipbar, width, color='#666666', label='MIP', hatch="/")
    
    def autolabel(rects1, rects2):
        count1 = 0
        for recta in rects1:
            count2 = 0
            for rectb in rects2:
                if count1 == count2:         
                    height1 = recta.get_height()
                    height2 = rectb.get_height()                    
                    val = float((height2-height1))/height1*100
                    print height1, " ", height2, " ", val
                    ax.text(rectb.get_x()+rectb.get_width()/2., 1.02*height2, '%d%%'%int(val),
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
    
#     plt.savefig('Output\\lns900s_mip7200s.png', dpi=300)
    plt.show()
#     plt.close(fig)

    

# prefix1 = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140904_milp/EAMS_v11_140904_milp/src/Output/"
# prefix2 = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140904_milp/EAMS_v11_140904_milp1/src/Output/"
# prefix3 = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140904_milp/EAMS_v11_140904_milp2/src/Output/"
# read_milp(prefix1+"milp_stats", prefix2+"milp_stats", prefix3+"milp_stats")

plotGraph()

