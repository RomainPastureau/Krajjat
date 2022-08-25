import matplotlib.pyplot as plt
import math
from realigner import *

def get_movement(sequence):

    times = sequence.get_timestamps()
    linewidth = 1.0
    x = []
    y = []
    z = []
    dist = []
    speeds = []
    max_speed = 0
    
    for p in range(0, len(sequence.poses)) :

        #Joint
        joint = sequence.poses[p].joints["HandRight"]
        x.append(joint.x)
        y.append(joint.y)
        z.append(joint.z)

        if p > 0 :
            joint_bef = sequence.poses[p-1].joints["HandRight"]
            d = sequence.get_distance(joint_bef, joint)
            dist.append(d)
            
            spe = sequence.get_speed(sequence.poses[p-1], sequence.poses[p], "HandRight")
            if spe > max_speed :
                max_speed = spe
            speeds.append(spe)

    #plt.style.use('_mpl-gallery')

    plt.figure(facecolor="black")

    
    ax = plt.axes()
    ax.xaxis.label.set_color('red')
    

    plt.subplot(5, 1, 1)
    plt.plot(times, x, linewidth = linewidth, color = "#ffcc00")
    
    plt.subplot(5, 1, 2)
    plt.plot(times, y, linewidth = linewidth, color = "#ffcc00")

    plt.subplot(5, 1, 3)
    plt.plot(times, z, linewidth = linewidth, color = "#ffcc00")

    plt.subplot(5, 1, 4)
    plt.plot(times[1:], dist, linewidth = linewidth, color = "#ffcc00")

    plt.subplot(5, 1, 5)
    plt.plot(times[1:], speeds, linewidth = linewidth, color = "#ffcc00")



    
    #ax.set_facecolor("black")

    plt.show()

if __name__ == '__main__':
    #sequence1 = Sequence("F:/Body Tracking Recordings/Video/01_Original_videos/05_Larraitz/R028")
    sequence1 = Sequence("C:/Users/romai/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - 10, 3")
    get_movement(sequence1)
