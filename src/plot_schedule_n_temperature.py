from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
from matplotlib.dates import WEEKLY, DAILY, HOURLY, MINUTELY, rrulewrapper, RRuleLocator

def _getPlotRule(ptype):         
        if ptype == 0:
            return MINUTELY
        if ptype == 1:
            return HOURLY
        if ptype == 2:
            return DAILY
        if ptype == 3:
            return WEEKLY
        else:
            print "Unknown Plot Type. Set to default DAILY"
            return DAILY
        
        
def plot_airflow_roomsche_twingraph(fdir, logfile, hvac_sche, t, pinterval, pstep, room_asa):
    
    fig = plt.figure()   
    afig = fig.add_subplot(211)
    hfig = fig.add_subplot(212)        
        
    ind = t    
    width = 0.02
    # For 4 rooms
    colors = ('r', 'g', 'b', 'y')
    t_labels = ('R1', 'R2', 'R3', 'R4')
    labels = ('R1', 'R2', 'R3', 'R4')
# #     t_labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
# #     labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
    
    # For 20 rooms
#     colors = ('#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc')
#     t_labels = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8','R9', 'R10', 'R11', 'R12','R13', 'R14', 'R15', 'R16','R17', 'R18', 'R19', 'R20')
#     labels = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8','R9', 'R10', 'R11', 'R12','R13', 'R14', 'R15', 'R16','R17', 'R18', 'R19', 'R20')
#     
    for i in xrange(len(room_asa)):   
        afig.plot(ind, room_asa[i], colors[i], label=t_labels[i])
    afig.grid(True)
    afig.set_ylabel("Air Flow Rate (kg/s)")
    handles, labels = afig.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    afig.legend(handles, labels, loc='best', prop=fontP)  # TODO: for 20 rooms, cant show this..
    afig.set_title('[' + fdir + '\n' + logfile +']\n', fontsize=12)
    
    
    inputd = []
    for i in xrange(len(hvac_sche)):
        inputd.append(hvac_sche[i])
         
    data = np.array(inputd)     
    bottom = np.vstack((np.zeros((data.shape[1],), dtype=data.dtype),
                        np.cumsum(data, axis=0)[:-1]))
    
    for dat, col, lab, bot in zip(data, colors, labels, bottom):
        hfig.bar(ind, dat, width, color=col, label=lab, bottom=bot)
    hfig.grid(True)
    hfig.set_xlabel("Scheduling Periods")
    hfig.set_ylabel("HVAC Activation")
    handles, labels = hfig.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    hfig.legend(handles, labels, loc='best', prop=fontP)  # TODO: for 20 rooms, cant show this..
    
           
    ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    rule_1 = rrulewrapper(_getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
    loc_1 = RRuleLocator(rule_1)
    hfig.xaxis.set_major_locator(loc_1)    
    hfig.xaxis.set_major_formatter(ymdhFmt)
    datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
    datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
    hfig.set_xlim(datemin, datemax)  
     
    fig.autofmt_xdate()
     
    plt.savefig('Output/'+ logfile +'_hvac_asa.png')
#     plt.show()
    plt.close(fig)
    print "Done!"
    
def plot_temperature_roomsche_twingraph_ws(fdir, logfile, hvac_standby_sche, room_sche, t, pinterval, pstep, oat, room_zt, room_tsa):
    
    #TODO: room_tsa is not used!
#     print hvac_standby_sche
#     print room_sche
    
    fig = plt.figure()   
    rsfig = fig.add_subplot(111)
    tfig = rsfig.twinx()
        
    ind = t     
    width = 0.02
    # For 4 rooms
#     colors = ('r', 'g', 'b', '#ffff00')
#     ws_colors = ('#ff0000', '#00ff00', '#0000ff', '#ffff00')
#     h_labels = ('$S^{R1}$', '$S^{R2}$', '$S^{R3}$', '$S^{R4}$')
#     t_labels = ('R1', 'R2', 'R3', 'R4')
#     labels = ('R1', 'R2', 'R3', 'R4')
#     t_labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
#     labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
    
    # For 20 rooms
#     colors = ('#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc')
#     ws_colors = ('#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc','#cccccc', '#cccccc', '#cccccc', '#cccccc')
#     h_labels = ('$S^{R1}$', '$S^{R2}$', '$S^{R3}$', '$S^{R4}$', '$S^{R5}$', '$S^{R6}$', '$S^{R7}$', '$S^{R8}$','$S^{R9}$', '$S^{R10}$', '$S^{R11}$', '$S^{R12}$','$S^{R13}$', '$S^{R14}$', '$S^{R15}$', '$S^{R16}$','$S^{R17}$', '$S^{R18}$', '$S^{R19}$', '$S^{R20}$')
#     t_labels = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8','R9', 'R10', 'R11', 'R12','R13', 'R14', 'R15', 'R16','R17', 'R18', 'R19', 'R20')
#     labels = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8','R9', 'R10', 'R11', 'R12','R13', 'R14', 'R15', 'R16','R17', 'R18', 'R19', 'R20')

    colors = ['#cccccc'] * 50
    labels = [''] * 50
    t_labels = [''] * 50
    
    # plot room schedule
    inputd = []
    for i in xrange(len(room_sche)):        
        inputd.append(room_sche[i])   
             
    data = np.array(inputd)     
    bottom = np.vstack((np.zeros((data.shape[1],), dtype=data.dtype),
                        np.cumsum(data, axis=0)[:-1]))
    
    for dat, col, lab, bot in zip(data, colors, labels, bottom):
        plt.bar(ind, dat, width, color=col, label=lab, bottom=bot)
        
#     # plot hvac standby mode
#     hinputd = []
#     for i in xrange(len(hvac_standby_sche)):        
#         newlist = [x*3 for x in hvac_standby_sche[i]]
#         hinputd.append(newlist)   
#              
#     hdata = np.array(hinputd)     
#     hbottom = np.vstack((np.zeros((hdata.shape[1],), dtype=hdata.dtype),
#                         np.cumsum(hdata, axis=0)[:-1]))
#     
#     for hdat, col, hlab, hbot in zip(hdata, ws_colors, h_labels, hbottom):
#         plt.bar(ind, hdat, width, color=col, label=hlab, bottom=hbot, hatch="//")
    
    tfig.plot(ind, oat, 'k', label='Outdoor')
    tfig.plot(ind, [21]*len(ind), 'k--', label='Comfort Bounds')
    tfig.plot(ind, [23]*len(ind), 'k--')
    for i in xrange(len(room_zt)):   
        tfig.plot(ind, room_zt[i], colors[i], label=t_labels[i])        
    
    tfig.grid(True)
    tfig.set_ylabel("Temperature (Celcius)")
#     tfig.set_ylim(ymin=0, ymax=60)
    tfig.set_title('[' + fdir + '\n' + logfile +']\n', fontsize=12)    
    
    rsfig.axes.set_yticks([])
    rsfig.set_xlabel("Scheduling Periods")
    rsfig.set_ylabel("# of Meetings")
    plt.setp(rsfig.get_xticklabels(), rotation='vertical', fontsize=8)
    
#     handles, labels = tfig.get_legend_handles_labels()
#     fontP = FontProperties()
#     fontP.set_size('small')
#     tfig.legend(handles, labels, ncol=5, loc='best', prop=fontP)  # TODO: for 20 rooms, cant show this..
           
    ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    rule_1 = rrulewrapper(_getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
    loc_1 = RRuleLocator(rule_1)
    rsfig.xaxis.set_major_locator(loc_1)    
    rsfig.xaxis.set_major_formatter(ymdhFmt)
    datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
    datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
    rsfig.set_xlim(datemin, datemax)  
     
    fig.autofmt_xdate()
     
#     plt.savefig('Output/'+ logfile +'_temperature_ralloc.png', dpi=400)
    plt.show()
#     plt.close(fig)
    print "Done!"
    
def plot_temperature_roomsche_twingraph_ns(logfile, room_sche, t, pinterval, pstep, oat, room_zt, room_tsa):
    
    fig = plt.figure()   
    rsfig = fig.add_subplot(111)
    tfig = rsfig.twinx()
        
    ind = t # np.arange(len(room_sche[0]))    
    width = 0.02
#     num_room = len(room_sche)
    colors = ('r', 'g', 'b', 'y')
    t_labels = ('R1', 'R2', 'R3', 'R4')
    labels = ('R1', 'R2', 'R3', 'R4')
#     t_labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
#     labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')

    inputd = []
    for i in xrange(len(room_sche)):        
        inputd.append(room_sche[i])        
    data = np.array(inputd)     
    bottom = np.vstack((np.zeros((data.shape[1],), dtype=data.dtype),
                        np.cumsum(data, axis=0)[:-1]))
    
    for dat, col, lab, bot in zip(data, colors, labels, bottom):
        plt.bar(ind, dat, width, color=col, label=lab, bottom=bot)
    
    tfig.plot(ind, oat, 'k', label='Outdoor')
    for i in xrange(len(room_zt)):   
        tfig.plot(ind, room_zt[i], colors[i], label=t_labels[i])        
    tfig.plot(ind, [21]*len(ind), 'k--', label='Comfort Bounds')
    tfig.plot(ind, [23]*len(ind), 'k--')
    tfig.grid(True)
    tfig.set_ylabel("Temperature (Celcius)")
     
    rsfig.axes.set_yticks([])
    rsfig.set_xlabel("Scheduling Periods")
    rsfig.set_ylabel("# of Meetings")
    
    handles, labels = tfig.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    rsfig.legend(handles, labels, ncol=2, loc='best', prop=fontP)
           
    ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    rule_1 = rrulewrapper(_getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
    loc_1 = RRuleLocator(rule_1)
    rsfig.xaxis.set_major_locator(loc_1)    
    rsfig.xaxis.set_major_formatter(ymdhFmt)
    datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
    datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
    rsfig.set_xlim(datemin, datemax)  
     
    fig.autofmt_xdate()
     
    plt.savefig('Output/'+ logfile +'_temperature_ralloc.png')
#     plt.show()
    plt.close(fig)
    print "Done!"
        
def plotScheduleNTemp(isws, fdir, fs, ft, start, end, pinterval, pstep):
            
    # Read schedule data
    if fs:
        fsstr = fdir + 'Output/' + fs
        sche_data_file = open(fsstr, 'r')
        sche_data = ''.join(sche_data_file.readlines())
        sche_data_file.close()
        
    # Read temperature data
    if ft:
        ftstr = fdir + 'Output/' + ft
        temperature_data_file = open(ftstr, 'r')
        temperature_data = ''.join(temperature_data_file.readlines())
        temperature_data_file.close()
    
    # Get timeslot information        
    if sche_data:
        sche_lines = sche_data.split('\n')
        slot_parts = sche_lines[0].split(",")
#         num_room = sche_lines[1] 
               
    if temperature_data:
        temperature_lines = temperature_data.split('\n')   
#         slot_parts = temperature_lines[0].split(",")
        oat_parts = temperature_lines[1].split(",")
    
    t = []    
    for i in xrange(len(slot_parts)):
        t.append(datetime.strptime(slot_parts[i], "%Y-%m-%d %H:%M:%S"))
        
    oat = []
    for i in xrange(len(oat_parts)):
        oat.append(float(oat_parts[i]))
        
    sidx = -1
    eidx = -1
    s = datetime.strptime(start, "%Y-%m-%d %H:%M")
    e = datetime.strptime(end, "%Y-%m-%d %H:%M")    
    for ridx, x in enumerate(t):
        if x == s:
            sidx = ridx
        if x == e:
            eidx = ridx
             
    if sidx == -1 or eidx == -1:
        print "Error, start and end out of range!"
           
    room_vz = []    
    if isws:
        room_vw = []
            
    for i in xrange(2, len(sche_lines)-1, 2):
        #Options: select either one
#         tmp_vz = [int(x) for x in sche_lines[i].split(",")]
        tmp_vz = [int(x)*3 for x in sche_lines[i].split(",")]
        room_vz.append(tmp_vz[sidx:eidx])
        
        if isws:
#             tmp_vw = [int(x) for x in sche_lines[i+1].split(",")]
            tmp_vw = [int(x) for x in sche_lines[i+1].split(",")]      
            room_vw.append(tmp_vw[sidx:eidx])
         
    room_zt = []
    room_tsa = []
    room_asa = []
    for i in xrange(3, len(temperature_lines)-1, 3):        
        tmp_zt = [float(x) for x in temperature_lines[i].split(",")]
        tmp_tsa = [float(x) for x in temperature_lines[i+1].split(",")]
        tmp_asa = [float(x) for x in temperature_lines[i+2].split(",")]         
        room_zt.append(tmp_zt[sidx:eidx])
        room_tsa.append(tmp_tsa[sidx:eidx])  
        room_asa.append(tmp_asa[sidx:eidx])
    
    if isws:
        plot_temperature_roomsche_twingraph_ws(fdir, fs, room_vw, room_vz, t[sidx:eidx], pinterval, pstep, oat[sidx:eidx], room_zt, room_tsa)
        plot_airflow_roomsche_twingraph(fdir, fs, room_vw, t[sidx:eidx], pinterval, pstep, room_asa)
    else:
        plot_temperature_roomsche_twingraph_ns(fs, room_vz, t[sidx:eidx], pinterval, pstep, oat[sidx:eidx], room_zt, room_tsa)
                
isws = 1
notws = 0



# prefix = "C:/Users/bplim/My PhD/Code/EAMS_experiments/140908_temperatures/EAMS_v11_140905_mspec_50r/src/"
prefix = "C:/Users/bplim/My PhD/Code/EAMS_v11/src/"
plotScheduleNTemp(isws, prefix, "eams_meeting_test1_OPTCFG_2014_09_29_16_14_17_793000_schedules", "eams_meeting_test1_OPTCFG_2014_09_29_16_14_17_793000_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 1, 4)





