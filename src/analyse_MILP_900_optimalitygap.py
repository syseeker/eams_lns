
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
  
def getMIPGAP(prefix, fname, maxdata, isall):    
    
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
            dl = len(lines)-2
            parts = lines[dl].split(',')
            MIPGAP.append(float(parts[5]))
        else:
            break
        
    #     print TESTCASES
#     print "total:", len(TESTCASES)
    print fname
    print TESTCASE_GRP_COUNT    
    print sum(MIPGAP)/len(TESTCASES)
    print max(MIPGAP)
    print min(MIPGAP)
    print " "
    




#---------------------------------
# Never delete this!
prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mspecparam900/src/Output/"  # AAAI!
# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140911_sneakpeak/EAMS_v11_140908_mspec_mallparam900/src/Output/"
maxdata = 100
maxalldata = maxdata*8
#---------------------------------

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "mall_stats.txt", maxalldata, 1)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m20_lns_stats", maxdata, 0)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m50_lns_stats", maxdata, 0)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m100_lns_stats", maxdata, 0)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m200_lns_stats", maxdata, 0)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m50_50r_lns_stats", maxdata, 0)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m100_50r_lns_stats", maxdata, 0)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m200_50r_lns_stats", maxdata, 0)

MIPGAP  = []
TESTCASES = []
getMIPGAP(prefix, "m500_50r_lns_stats", maxdata, 0)


