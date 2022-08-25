import matplotlib.pyplot as plt
import math
from realigner import *

def get_movement(sequence):

    joints_movement = {}
    joints_speed = {}
    times = sequence.get_timestamps()[1:]
    max_speed = 0
    joints_qty_movement = {}
    
    for j in sequence.poses[0].joints :
        movement = []
        speed = []
        
        for p in range(1, len(sequence.poses)) :

            #Distance
            j1 = sequence.poses[p-1].joints[j]
            j2 = sequence.poses[p].joints[j]
            dist = sequence.get_distance(j1, j2)
            movement.append(dist)

            #Speed
            spe = sequence.get_speed(sequence.poses[p-1], sequence.poses[p], j)
            if spe > max_speed :
                max_speed = spe
            speed.append(spe)

        joints_movement[j] = movement
        joints_speed[j] = speed
        joints_qty_movement[j] = sum(speed)

    plot_sequence(joints_speed, joints_qty_movement, max_speed, times)

def plot_sequence(joints_speed, joints_qty_movement, max_speed, times):
    #plt.style.use('_mpl-gallery')

    positions = [3, 8, 11, 12, 13, 14, 15,
                 16, 18, 20, 21, 22, 23, 24,
                 25, 27, 29, 31, 32, 34, 35]

    joints = ["Head",
              "Neck",
              "ElbowRight", "ShoulderRight", "SpineShoulder", "ShoulderLeft", "ElbowLeft",
              "WristRight", "SpineMid", "WristLeft",
              "HandRight", "HipRight", "SpineBase", "HipLeft", "HandLeft",
              "KneeRight", "KneeLeft",
              "FootRight", "AnkleRight", "AnkleLeft", "FootLeft"]

    ##Determine color
    joints_color = {}
    
    qty_mov = []
    for j in joints :
        qty_mov.append(joints_qty_movement[j])
    min_qty = min(qty_mov)
    max_qty = max(qty_mov)

    col_max = (204, 0, 0)
    col_min = (153, 204, 0)
    diff = (col_max[0]-col_min[0], col_max[1]-col_min[1], col_max[2]-col_min[2])

    for j in joints :
        ratio = (joints_qty_movement[j] - min_qty)/(max_qty - min_qty)
        colR = int(col_min[0] + ratio*diff[0])
        colG = int(col_min[1] + ratio*diff[1])
        colB = int(col_min[2] + ratio*diff[2])
        col = (colR, colG, colB)
        joints_color[j] = '#%02x%02x%02x' % col
        
    linewidth = 1.0

    plt.rcParams["figure.figsize"] = (12,9)
    plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0.3, hspace=0.5)

    for j in range(len(positions)) :

        plt.subplot(7, 5, positions[j])
        plt.ylim([0, max_speed])
        plt.title(joints[j])
        plt.plot(times, joints_speed[joints[j]], linewidth = linewidth, color = joints_color[joints[j]])

    plt.show()

if __name__ == '__main__':
    #sequence1 = Sequence("F:/Body Tracking Recordings/Video/01_Original_videos/05_Larraitz/R028")
    sequence1 = Sequence("C:/Users/romai/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - 10, 3")
    get_movement(sequence1)
