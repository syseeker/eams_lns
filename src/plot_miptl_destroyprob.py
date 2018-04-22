import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
    
def plot_miptl_destroyprob():
    
    
#     case = ["All M, All R", "All M, 20R", "All M, 50R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
    # result on 0903
#     d2 = [0.56, 0.50, 0.53, 0.59, 0.84, 0.81, 0.32, 0.74, 0.58, 0.74, 0.50]
#     d3 = [0.24, 0.48, 0.38, 0.18, 0.05, 0.09, 0.43, 0.24, 0.37, 0.22, 0.24]
#     d4 = [0.20, 0.01, 0.09, 0.23, 0.11, 0.09, 0.26, 0.02, 0.05, 0.03, 0.26]
#     mip = [9.18, 9.69, 9.75, 8.23, 8.47, 9.88, 8.74, 7.29, 9.75, 9.82, 6.31]
    
    # result on 0907
#     d2 = [0.583156495, 0.923781248, 0.914548852, 0.695830966, 0.837416369, 0.931255747, 0.754797288, 0.478054087, 0.623827407, 0.839514995, 0.665576521]
#     d3 = [0.253277419, 0.06477578, 0.073791125, 0.192152803, 0.059642367, 0.009361944, 0.149414832, 0.518762195, 0.321898865, 0.124818165, 0.195738318]
#     d4 = [0.163566086, 0.011442972, 0.011660023, 0.112016231, 0.102941263, 0.059382309, 0.09578788, 0.003183718, 0.054273728, 0.03566684, 0.138685161]
#     mip = [9.395361254, 9.898791227, 9.869192802, 8.648753256, 9.172406085, 9.866495724, 7.187791227, 9.497094045, 9.749388035, 9.747512601, 7.997733907]
    case = ["All M, All R", "20M, 20R", "50M, 20R", "100M, 20R", "200M, 20R", "50M, 50R", "100M, 50R", "200M, 50R", "500M, 50R"]
    d2 = [0.583156495, 0.695830966, 0.837416369, 0.931255747, 0.754797288, 0.478054087, 0.623827407, 0.839514995, 0.665576521]
    d3 = [0.253277419, 0.192152803, 0.059642367, 0.009361944, 0.149414832, 0.518762195, 0.321898865, 0.124818165, 0.195738318]
    d4 = [0.163566086, 0.112016231, 0.102941263, 0.059382309, 0.09578788, 0.003183718, 0.054273728, 0.03566684, 0.138685161]
    mip = [9.395361254, 8.648753256, 9.172406085, 9.866495724, 7.187791227, 9.497094045, 9.749388035, 9.747512601, 7.997733907]

            
    colors = ['#ededed', '#d6d6d6', '#666666']
    labels = ['2 rooms', '3 rooms', '4 rooms']
        
    fig = plt.figure()   
    rsfig = fig.add_subplot(111)
    tfig = rsfig.twinx()
        
    ind = np.arange(len(case))
    width = 0.3
           
    rsfig.bar(ind, d2, width, color=colors[0], label=labels[0]) 
    rsfig.bar(ind+width, d3, width, color=colors[1], label=labels[1], hatch=".")
    rsfig.bar(ind+(2*width), d4, width, color=colors[2], label=labels[2], hatch="/")
          
    tfig.plot(ind, mip, 'k*-', label='MIP Time Limit')
    tfig.grid(True)
    tfig.set_ylabel("MIP Time Limit")
    tfig.set_ylim(ymin=1, ymax=12)
    
    rsfig.set_xticks(ind+(width*2))  
    rsfig.set_xticklabels(case)
    rsfig.set_ylim(ymax=1.2) 
    rsfig.set_xlabel("Instances Group")
    rsfig.set_ylabel("Rescheduling Probability")
    plt.setp(rsfig.get_xticklabels(), rotation='vertical', fontsize=10)
     
    fontP = FontProperties()
    fontP.set_size('medium')     
    h1, l1 = rsfig.get_legend_handles_labels()
    h2, l2 = tfig.get_legend_handles_labels()
    rsfig.legend(h1+h2, l1+l2, loc='upper left', ncol=2, prop=fontP)
    
    fig.autofmt_xdate()
     
    plt.savefig('Output/mipdestroy_0907_9grps.png', dpi=400)
#     plt.show()
    plt.close(fig)
    print "Done!"
    


plot_miptl_destroyprob()
        
        
                
