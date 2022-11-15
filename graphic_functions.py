#!/usr/bin/env python
"""Krajjat 1.10
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
__version__ = "1.10"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"


def common_displayer(folder_or_sequence1, folder_or_sequence2=None, show_lines=True, ignore_bottom=False,
                     resolution=(1600, 900), full_screen=False, manual=False, show_image=False, path_images=None,
                     start_pose=0, realign=False, folder_save=None, velocity_threshold=10, w=3):
    # If folderOrSequence is a folder, we load the sequence; otherwise, we just attribute the sequence
    if folder_or_sequence1 is str:
        sequence1 = Sequence(folder_or_sequence1)
    else:
        sequence1 = folder_or_sequence1

    # Realignment and saving of the realignment
    if realign:
        sequence2 = sequence1.realign(velocity_threshold, w, verbose=False)
        if folder_save:
            save_sequence(sequence1, sequence2, folder_save)
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
    disp = GraphicDisplay(window)  # Contains the window and resizing info

    # Generates a graphic sequence from the sequence
    animation1 = GraphicSequence(sequence1, show_lines, ignore_bottom, start_pose, path_images, disp)
    animation2 = None
    if sequence2 is not None:
        animation2 = GraphicSequence(sequence2, show_lines, ignore_bottom, start_pose, path_images, disp)

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
                if ev.type == KEYDOWN and ev.key == K_RIGHT:
                    animation1.next_pose()
                elif ev.type == KEYDOWN and ev.key == K_LEFT:
                    animation1.previous_pose()

        if manual:
            animation1.show_pose(window, show_lines, show_image)
        elif sequence2 is None:
            animation1.show(window, show_lines, shift_x=0)
        else:
            animation1.show(window, show_lines, shift_x=-300)
            animation2.show(window, show_lines, shift_x=300)

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

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen, realign=True,
                     folder_save=folder_save, velocity_threshold=velocity_threshold, w=w)


def sequence_comparer(folder_or_sequence1, folder_or_sequence2, show_lines=True, ignore_bottom=False,
                      resolution=(1600, 900), full_screen=False):
    """Compares two sequences side by side."""

    common_displayer(folder_or_sequence1, folder_or_sequence2, show_lines, ignore_bottom, resolution, full_screen)


def pose_reader(folder_or_sequence, start_pose=0, show_lines=True, show_image=True, ignore_bottom=False,
                resolution=(1600, 900), full_screen=False, path_images=None):
    """Reads a sequence and offers a manuel control over the poses (with the arrows of the keyboard)."""

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen, True,
                     show_image, start_pose=start_pose, path_images=path_images)


def velocity_plotter(folder_or_sequence, audio=None, overlay=False):
    """Plots the velocity across time of the joints"""

    # If folderOrSequence is a folder, we load the sequence; otherwise, we just attribute the sequence
    if folder_or_sequence is str:
        sequence = Sequence(folder_or_sequence)
    else:
        sequence = folder_or_sequence

    # Compute velocities of the joints
    joints_velocity, joints_qty_movement, max_velocity, times, audio_array, \
    audio_times = get_velocities_joints(sequence, audio)
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

    if len(audio_array) != 0:
        print("Plotting the audio... ")
        plt.subplot(7, 5, 1)
        plt.title("Audio")
        plt.plot(audio_times, audio_array, linewidth=line_width, color="#8e3faa")

        if overlay:
            max_audio_array = max(audio_array)
            j = 10
            for i in range(len(audio_array)):
                if i / len(audio_array) > j / 100:
                    print(str(j) + "%", end=" ")
                    j += 10
                new_audio_array.append(audio_array[i] / max_audio_array * max_velocity)

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


def joint_temporal_plotter(sequence_or_sequences, joint_label="HandRight", align=True):
    # Get the time array
    times = []
    if type(sequence_or_sequences) is list:
        for seq in range(len(sequence_or_sequences)):
            sequence = sequence_or_sequences[seq]

            # If we already had sequences, and align is True, we try to align the sequences
            if seq != 0 and align:

                aligned = False
                # We compare the sequence to every other sequence already in the list
                for seq2 in range(seq):
                    prior_sequence = sequence_or_sequences[seq2]
                    alignment = align_two_sequences(sequence, prior_sequence)
                    if alignment:
                        if alignment[0] == 0:
                            print("Aligning sequence " + str(seq + 1) + " to sequence " + str(seq2 + 1) + ".")
                            times.append(times[seq2][alignment[1]:alignment[1] + len(sequence)])
                            aligned = True
                            break
                        else:
                            print("Aligning sequence " + str(seq2 + 1) + " to sequence " + str(seq + 1) + ".")
                            times.append(sequence.get_timestamps())
                            times[seq2] = times[seq][alignment[0]:alignment[0] + len(prior_sequence)]
                            aligned = True
                            break

                if not aligned:
                    times.append(sequence.get_timestamps())

            else:
                times.append(sequence.get_timestamps())

    else:
        times.append(sequence_or_sequences.get_timestamps())
        sequence_or_sequences = [sequence_or_sequences]

    # Create empty lists for the arrays
    x = []
    y = []
    z = []
    dist = []
    velocities = []

    # Define a "max_velocity" to get the upper limit of the y-axis
    max_velocity = 0

    # For all poses
    for i in range(len(sequence_or_sequences)):

        sequence = sequence_or_sequences[i]

        x.append([])
        y.append([])
        z.append([])
        dist.append([])
        velocities.append([])

        for p in range(0, len(sequence.poses)):

            # Get the joint x, y and z info
            joint = sequence.poses[p].joints[joint_label]
            x[i].append(joint.x)
            y[i].append(joint.y)
            z[i].append(joint.z)

            # For all poses after the first one
            if p > 0:

                # Get distance travelled
                joint_before = sequence.poses[p - 1].joints[joint_label]
                d = sequence.get_distance(joint_before, joint)
                dist[i].append(d)

                # Get velocity
                vel = sequence.get_velocity(sequence.poses[p - 1], sequence.poses[p], joint_label)
                if vel > max_velocity:
                    max_velocity = vel
                velocities[i].append(vel)

    plt.rcParams["figure.figsize"] = (12, 9)
    line_width = 1.0
    fig = plt.subplots(5, 1, figsize=(12, 9))
    plt.subplots_adjust(left=0.15, bottom=0.1, right=0.97, top=0.9, wspace=0.3, hspace=0.5)

    # Define colors to show
    colors = ["#0066ff", "#ff6600", "#009900", "#ff0000", "#009999", "#cc0099"]

    # Plot x, y, z, distance travelled and velocities
    parameters = {"rotation": "horizontal", "horizontalalignment": "right", "verticalalignment": "center",
                  "font": {'size': 16, "weight": "bold"}}

    plt.subplot(5, 1, 1)
    for i in range(len(sequence_or_sequences)):
        lab = sequence_or_sequences[i].name
        print(lab)
        plt.plot(times[i], x[i], linewidth=line_width, color=colors[i % 5], label=lab)
    plt.ylabel("x", **parameters)
    plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=len(sequence_or_sequences))

    plt.subplot(5, 1, 2)
    for i in range(len(sequence_or_sequences)):
        plt.plot(times[i], y[i], linewidth=line_width, color=colors[i % 5])
    plt.ylabel("y", **parameters)

    plt.subplot(5, 1, 3)
    for i in range(len(sequence_or_sequences)):
        plt.plot(times[i], z[i], linewidth=line_width, color=colors[i % 5])
    plt.ylabel("z", **parameters)

    plt.subplot(5, 1, 4)
    for i in range(len(sequence_or_sequences)):
        plt.plot(times[i][1:], dist[i], linewidth=line_width, color=colors[i % 5])
    plt.ylabel("Distance", **parameters)

    plt.subplot(5, 1, 5)
    for i in range(len(sequence_or_sequences)):
        plt.plot(times[i][1:], velocities[i], linewidth=line_width, color=colors[i % 5])
    plt.ylabel("Speed", **parameters)

    plt.show()


def framerate_plotter(sequence_or_sequences):
    if type(sequence_or_sequences) is not list:
        sequence_or_sequences = [sequence_or_sequences]

    i = 1
    while i ** 2 < len(sequence_or_sequences):
        i += 1
    if len(sequence_or_sequences) <= i * (i - 1):
        j = i - 1
    else:
        j = i
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.9, wspace=0.3, hspace=0.7)
    labels = get_names(sequence_or_sequences)
    max_framerate = 0

    framerates_list = []
    time_stamps_list = []
    averages_list = []

    for seq in range(len(sequence_or_sequences)):

        sequence = sequence_or_sequences[seq]
        framerates, time_stamps = sequence.get_framerate()
        avg = sum(framerates) / len(framerates)
        averages = [avg for _ in range(len(framerates))]

        framerates_list.append(framerates)
        time_stamps_list.append(time_stamps)
        averages_list.append(averages)

        if max(framerates) > max_framerate:
            max_framerate = max(framerates)

    for seq in range(len(sequence_or_sequences)):
        plt.subplot(i, j, seq + 1)
        plt.ylim([0, max_framerate + 1])
        plt.plot(time_stamps_list[seq], framerates_list[seq], linewidth=1.0, color="#000000", label="Framerate")
        plt.plot(time_stamps_list[seq], averages_list[seq], linewidth=1.0, color="#ff0000", label="Average")
        if seq == 0:
            plt.legend(bbox_to_anchor=(0, 1.3 + 0.1 * i, 1, 0), loc="upper left", ncol=2)
        plt.title(labels[seq] + " [Avg: " + format(averages_list[seq][0], '.2f') + "]")

    plt.show()
