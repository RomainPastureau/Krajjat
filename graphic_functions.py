#!/usr/bin/env python
"""Krajjat 1.6
Kinect Realignment Algorithm for Joint Jumps And Twitches
Author: Romain Pastureau
This file contains the main graphic functions. This is the
file to run to use any of the graphic functions.
"""

from core_functions import *
from graphic_classes import *
import matplotlib.pyplot as plt
import sys

__author__ = "Romain Pastureau"
__version__ = "1.6"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"


def common_displayer(folder_or_sequence1, folder_or_sequence2=None, show_lines=True, ignore_bottom=False,
                     resolution=(1600, 900), full_screen=False, manual=False, show_image=False, start_pose=0,
                     realign=True, folder_save=None, velocity_threshold=10, w=3):
    # If folderOrSequence is a folder, we load the sequence; otherwise, we just attribute the sequence
    if folder_or_sequence1 is str:
        sequence1 = Sequence(folder_or_sequence1)
    else:
        sequence1 = folder_or_sequence1

    # Realignment and saving of the realignment
    if realign:
        sequence2 = sequence1.realign(velocity_threshold, w, verbose=False)
        if folder_save:
            save_json(sequence1, sequence2, folder_save)
    else:
        if folder_or_sequence2 is str:
            sequence2 = Sequence(folder_or_sequence2)
        else:
            sequence2 = folder_or_sequence2

    # If the resolution is None, we just create a window the size of the screen
    if resolution is None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)

    # We set to full screen
    if full_screen:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode(resolution)

    pygame.mouse.set_visible(True)  # Allows the mouse to be visible
    disp = Display(window)  # Contains the window and resizing info

    # Generates a graphic sequence from the sequence
    animation1 = GraphicSequence(sequence1, show_lines, ignore_bottom, start_pose, disp)
    animation2 = None
    if sequence2 is not None:
        animation2 = GraphicSequence(sequence2, show_lines, ignore_bottom, start_pose, disp)

    program = True

    # Program loop
    while program:

        window.fill((0, 0, 0))  # Set background to black

        for ev in pygame.event.get():

            # Leave the program
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                program = False
                break

        if manual:
            animation1.show_pose(window, show_lines, show_image)
        if sequence2 is None:
            animation1.show(window, show_lines, 0)
        else:
            animation1.show(window, show_lines, -300)
            animation2.show(window, show_lines, 300)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def sequence_reader(folder_or_sequence, show_lines=True, ignore_bottom=False, resolution=(1600, 900),
                    full_screen=False):
    """Displays the joints of the sequence in real time and loops back to the beginning when over."""

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen)


def sequence_realigner(folder_or_sequence, velocity_threshold, w, folder_save=None, show_lines=True,
                       ignore_bottom=False, resolution=(1600, 900), full_screen=False):
    """Realigns a sequence, then displays the original and the realigned sequence side by side."""

    common_displayer(folder_or_sequence, show_lines, ignore_bottom, resolution, full_screen, realign=True,
                     folder_save=folder_save, velocity_threshold=velocity_threshold, w=w)


def sequence_comparer(folder_or_sequence1, folder_or_sequence2, show_lines=True, ignore_bottom=False,
                      resolution=(1600, 900), full_screen=False):
    """Compares two sequences side by side."""

    common_displayer(folder_or_sequence1, folder_or_sequence2, show_lines, ignore_bottom, resolution, full_screen)


def pose_reader(folder_or_sequence, start_pose=0, show_lines=True, show_image=True, ignore_bottom=False,
                resolution=(1600, 900), full_screen=False):
    """Reads a sequence and offers a manuel control over the poses (with the arrows of the keyboard)."""

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen, True,
                     show_image, start_pose)


def velocity_plotter(folder_or_sequence1, audio=None, overlay=False):
    """Plots the velocity across time of the joints"""

    # If folderOrSequence is a folder, we load the sequence; otherwise, we just attribute the sequence
    if folder_or_sequence1 is str:
        sequence = Sequence(folder_or_sequence1)
    else:
        sequence = folder_or_sequence1

    # Compute velocities of the joints
    joints_velocity, joints_qty_movement, max_velocity, times, audio_array, \
    audio_times = get_velocities_joints(sequence, audio, overlay)
    new_audio_array = []

    # Places the positions of the different joints in the graph to look like a body
    positions = [3,
                 8,
                 11, 12, 13, 14, 15,
                 16, 18, 20,
                 21, 22, 23, 24, 25,
                 27, 29,
                 31, 32, 34, 35]

    # Labels of the joints
    joints = ["Head",
              "Neck",
              "ElbowRight", "ShoulderRight", "SpineShoulder", "ShoulderLeft", "ElbowLeft",
              "WristRight", "SpineMid", "WristLeft",
              "HandRight", "HipRight", "SpineBase", "HipLeft", "HandLeft",
              "KneeRight", "KneeLeft",
              "FootRight", "AnkleRight", "AnkleLeft", "FootLeft"]

    # Determine color depending on global velocity
    joints_color = {}

    qty_mov = []
    for j in joints:
        qty_mov.append(joints_qty_movement[j])
    min_qty = min(qty_mov)  # Determines min global velocity (green)
    max_qty = max(qty_mov)  # Determines max global velocity (red)

    col_max = (204, 0, 0)
    col_min = (153, 204, 0)
    diff = (col_max[0] - col_min[0], col_max[1] - col_min[1], col_max[2] - col_min[2])

    # Apply the colors to all joints
    for j in joints:
        ratio = (joints_qty_movement[j] - min_qty) / (max_qty - min_qty)
        col_r = int(col_min[0] + ratio * diff[0])
        col_g = int(col_min[1] + ratio * diff[1])
        col_b = int(col_min[2] + ratio * diff[2])
        col = (col_r, col_g, col_b)
        joints_color[j] = '#%02x%02x%02x' % col

    line_width = 1.0

    plt.rcParams["figure.figsize"] = (12, 9)
    plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0.3, hspace=0.5)

    if len(audio_array) != 0 :
        print("Plotting the audio... ")
        plt.subplot(7, 5, 1)
        plt.title("Audio")
        plt.plot(audio_times, audio_array, linewidth=line_width, color="#8e3faa")

        if overlay:
            max_audio_array = max(audio_array)
            j = 10
            for i in range(len(audio_array)) :
                if i/len(audio_array) > j/100 :
                    print(str(j)+"%", end=" ")
                    j += 10
                new_audio_array.append(audio_array[i]/max_audio_array * max_velocity)

            print("100% - Done.\n")

    print("Joint", end=" ")

    # Plot everything
    for j in range(len(positions)):
        print(j + 1, end=" ")

        plt.subplot(7, 5, positions[j])
        plt.ylim([0, max_velocity])
        plt.title(joints[j])
        if overlay:
            plt.plot(audio_times, new_audio_array, linewidth=line_width, color="#d5cdd8")
        plt.plot(times, joints_velocity[joints[j]], linewidth=line_width, color=joints_color[joints[j]])

    plt.show()


def joint_temporal_plotter(sequence, joint_label="HandRight"):
    # Get the time array
    times = sequence.get_timestamps()

    # Create empty lists for the arrays
    x = []
    y = []
    z = []
    dist = []
    velocities = []

    # Define a "max_velocity" to get the upper limit of the y-axis
    max_velocity = 0

    # For all poses
    for p in range(0, len(sequence.poses)):

        # Get the joint x, y and z info
        joint = sequence.poses[p].joints[joint_label]
        x.append(joint.x)
        y.append(joint.y)
        z.append(joint.z)

        # For all poses after the first one
        if p > 0:

            # Get distance travelled
            joint_before = sequence.poses[p - 1].joints[joint_label]
            d = sequence.get_distance(joint_before, joint)
            dist.append(d)

            # Get velocity
            vel = sequence.get_velocity(sequence.poses[p - 1], sequence.poses[p], joint_label)
            if vel > max_velocity:
                max_velocity = vel
            velocities.append(vel)

    plt.figure(facecolor="white")
    ax = plt.axes()
    ax.xaxis.label.set_color('red')
    line_width = 1.0

    # Plot x, y, z, distance travelled and velocities
    plt.subplot(5, 1, 1)
    plt.plot(times, x, linewidth=line_width, color="#ffcc00")

    plt.subplot(5, 1, 2)
    plt.plot(times, y, linewidth=line_width, color="#ffcc00")

    plt.subplot(5, 1, 3)
    plt.plot(times, z, linewidth=line_width, color="#ffcc00")

    plt.subplot(5, 1, 4)
    plt.plot(times[1:], dist, linewidth=line_width, color="#ffcc00")

    plt.subplot(5, 1, 5)
    plt.plot(times[1:], velocities, linewidth=line_width, color="#ffcc00")

    plt.show()


if __name__ == '__main__':
    # Enter the path to the folder containing the first sequence
    folder1 = ""

    # (Facultative) Enter the path to the folder containing the second sequence
    folder2 = ""

    # Load the sequences
    sequence1 = Sequence(folder1)
    sequence2 = Sequence(folder2)

    # Randomize the second sequence
    sequence2.randomize()

    # Parameters for the following functions
    # Sequence: you can enter either a Sequence object or a path to a folder
    # Show lines: show the lines connecting the joints
    # Ignore bottom: ignore the joints below the hip (feet, ankles and knees)
    # Velocity threshold: for the realignment, velocity over which we do a realignment
    # W: window of frames over which we consider a jump, below (or at) which we consider a twitch
    # Folder save: defines a folder to save the realigned sequence. Does NOT save the sequence if None
    # Start pose: pose index at which the visualization starts
    # Show image: shows the video image below the skeleton
    # Resolution: in pixels, default 1600 x 900
    # Full screen: shows the animation in full screen (it is recommended to set your screen resolution)
    # Joint label: joint of which you want to see the temporal components

    # Reads one sequence and loops through it
    sequence_reader(sequence1, show_lines=True, ignore_bottom=True, resolution=(1600, 900), full_screen=False)

    # Realign a sequence and compare them side by side (saves the realigned sequence only if folder_save is not None)
    sequence_realigner(sequence1, velocity_threshold=10, w=3, folder_save=None, show_lines=True, ignore_bottom=False,
                       resolution=(1600, 900), full_screen=False)

    # Compare two sequences side by side
    sequence_comparer(sequence1, sequence2, show_lines=True, ignore_bottom=False, resolution=(1600, 900),
                      full_screen=False)

    # Compares two sequences side by side
    pose_reader(sequence1, start_pose=100, show_lines=True, show_image=True, ignore_bottom=False,
                resolution=(1600, 900), full_screen=False)

    # Plots the velocity of the joints across time
    velocity_plotter(sequence1)

    # Plots the time components (x, y, z, distance travelled and velocity) of a joint from a sequence
    joint_temporal_plotter(sequence1, joint_label="HandRight")
