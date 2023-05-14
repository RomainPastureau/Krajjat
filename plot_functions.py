import pygame
from pygame.locals import *

from lib import gradients
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import sys
from classes.sequence import *


def joint_temporal_plotter(sequence_or_sequences, joint_label="HandRight", align=True):
    """Plots the x, y, z positions across time of the joint of one or more sequences, along with the distance
    and velocity."""

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
                d = calculate_distance(joint_before, joint)
                dist[i].append(d)

                # Get velocity
                vel = calculate_velocity(sequence.poses[p - 1], sequence.poses[p], joint_label)
                if vel > max_velocity:
                    max_velocity = vel
                velocities[i].append(vel)

    plt.rcParams["figure.figsize"] = (12, 9)
    line_width = 1.0
    plt.subplots(5, 1, figsize=(12, 9))
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
    plt.ylabel("Velocity", **parameters)

    plt.show()


def velocity_plotter(folder_or_sequence, audio=None, overlay=False, line_width=1.0, color_scheme="default"):
    """Plots the velocity across time of the joints"""

    # If folderOrSequence is a folder, we load the sequence; otherwise, we just attribute the sequence
    if folder_or_sequence is str:
        sequence = Sequence(folder_or_sequence)
    else:
        sequence = folder_or_sequence

    # Compute velocities of the joints
    joints_velocity = sequence.get_velocities()
    joints_qty_movement = sequence.get_total_velocity_per_joint()
    max_velocity = sequence.get_max_velocity_whole_sequence()
    timestamps = sequence.get_timestamps()

    # We define the plot dictionary
    plot_dictionary = {}

    # Determine color depending on global velocity
    joints_colors = get_joints_colors_qty_movement(joints_qty_movement, color_scheme)

    # Scale the audio
    new_audio_envelope = []
    if audio is not None and overlay:
        new_audio_envelope = get_scaled_audio(audio.get_envelope(), max_velocity)

    for joint in joints_velocity.keys():
        graph = Graph()
        if overlay:
            graph.add_plot(timestamps, new_audio_envelope, line_width, "#aa0000")
        graph.add_plot(timestamps[1:], joints_velocity[joint], line_width, joints_colors[joint])
        plot_dictionary[joint] = graph

    if overlay:
        graph = Graph()
        graph.add_plot(timestamps, audio.envelope, line_width, "#d5cdd8")
        plot_dictionary["Audio"] = graph

    plot_body_graphs(plot_dictionary, max_velocity)


def framerate_plotter(sequence_or_sequences, line_width=1.0, color="#000000"):
    """Plots the framerates across time of one or many sequences."""

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
    timestamps_list = []
    averages_list = []

    for seq in range(len(sequence_or_sequences)):

        sequence = sequence_or_sequences[seq]
        framerates, timestamps = sequence.get_frequencies()
        avg = sum(framerates) / len(framerates)
        averages = [avg for _ in range(len(framerates))]

        framerates_list.append(framerates)
        timestamps_list.append(timestamps)
        averages_list.append(averages)

        if max(framerates) > max_framerate:
            max_framerate = max(framerates)

    for seq in range(len(sequence_or_sequences)):
        plt.subplot(i, j, seq + 1)
        plt.ylim([0, max_framerate + 1])
        plt.plot(timestamps_list[seq], framerates_list[seq], linewidth=line_width, color=color, label="Framerate")
        plt.plot(timestamps_list[seq], averages_list[seq], linewidth=line_width, color="#ff0000", label="Average")
        if seq == 0:
            plt.legend(bbox_to_anchor=(0, 1.3 + 0.1 * i, 1, 0), loc="upper left", ncol=2)
        plt.title(labels[seq] + " [Avg: " + format(averages_list[seq][0], '.2f') + "]")

    plt.show()


def plot_body_graphs(plot_dictionary, min_scale=None, max_scale=None, show_scale=False, name=None,
                     color_scheme="default", joint_layout="auto"):
    # Places the positions of the different joints in the graph to look like a body

    joints_positions, joint_layout = load_joints_positions(plot_dictionary, joint_layout)

    # Figure parameters
    plt.rcParams["figure.figsize"] = (12, 9)
    if joint_layout == "kinect":
        rows = 7
        cols = 5
    else:
        rows = 13
        cols = 7
    fig, axes = plt.subplots(nrows=rows, ncols=cols)
    plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0.3, hspace=0.6)

    # Get min and max values
    min_value, max_value = get_min_max_values(plot_dictionary)
    if max_scale == "auto":
        max_scale = max_value

    # Plot the subplots
    for key in plot_dictionary.keys():
        plt.subplot(rows, cols, joints_positions[key])
        if key != "Audio":  # We want to scale everything apart from the audio
            plt.ylim([min_value, max_value])
        plt.title(key)
        for subplot in plot_dictionary[key].plots:
            plt.plot(subplot.x, subplot.y, linewidth=subplot.line_width, color=subplot.color)

    # Delete unused axes
    if "Audio" not in plot_dictionary.keys():
        fig.delaxes(axes[0][0])
    if joint_layout == "kinect":
        axes_to_delete = [(0, 1), (0, 3), (0, 4), (1, 0), (1, 1), (1, 3), (1, 4), (3, 1), (3, 3), (5, 0), (5, 2),
                          (5, 4), (6, 2)]
    else:
        axes_to_delete = [(0, 1), (0, 2), (0, 4), (0, 5), (0, 6), (1, 0), (1, 1), (1, 5), (1, 6), (3, 1), (3, 5),
                          (4, 1), (4, 3), (4, 5), (5, 1), (5, 3), (5, 5), (6, 1), (6, 3), (6, 5), (7, 0), (7, 1),
                          (7, 3), (7, 5), (7, 6), (8, 0), (8, 1), (8, 3), (8, 5), (8, 6), (9, 0), (9, 1), (9, 3),
                          (9, 5), (9, 6), (10, 0), (10, 1), (10, 3), (10, 5), (10, 6), (11, 0), (11, 3), (11, 6),
                          (12, 0), (12, 3), (12, 6)]
    for axis_to_delete in axes_to_delete:
        fig.delaxes(axes[axis_to_delete[0]][axis_to_delete[1]])

    # Get colors
    color_list = get_color_points_on_gradient(color_scheme, 100)

    # Show the scale if max_scale is not None
    if show_scale:
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.9, top=0.97, wspace=0.3, hspace=0.6)
        cmap = colors.ListedColormap(color_list)
        norm = colors.Normalize(vmin=min_scale, vmax=max_scale)
        cbax: object = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbax, orientation='vertical', label=name)
    plt.show()


def plot_silhouette(plot_dictionary, min_scale="auto", max_scale="auto", show_scale=True, name=None,
                    color_scheme="default", resolution=(1600, 900), full_screen=False):
    pygame.init()

    # If the resolution is None, we just create a window the size of the screen
    if resolution is None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)

    # We set to full screen
    if full_screen:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode(resolution)

    # Scale variables to the resolution
    ratio_w = resolution[0] / 1920
    ratio_h = resolution[1] / 1080

    # Load silhouette picture and resize it
    silhouette = pygame.image.load("res/silhouette.png")
    silhouette = pygame.transform.scale(silhouette, (resolution[0], resolution[1]))

    pygame.mouse.set_visible(True)  # Allows the mouse to be visible
    mouse_sensitivity = 50  # Radius around the center in which the mouse position will be detected as inside
    program = True  # Loop variable
    colors = get_color_scheme(color_scheme)  # Color scheme
    font = pygame.font.SysFont("Corbel", int(30 * ratio_h), True)  # Define font

    # If the scale is on auto, we scale it the max value
    min_value, max_value = get_min_max_values(plot_dictionary)
    if min_scale == "auto":
        min_scale = min_value
    if max_scale == "auto":
        max_scale = max_value

    # Position of the center of the circles of color for the joints (for a 1920x1080 screen)
    joints_positions = {"Head": (960, 60), "Neck": (960, 160), "SpineShoulder": (960, 205), "SpineMid": (960, 355),
                        "ShoulderRight": (860, 230), "ElbowRight": (825, 375), "WristRight": (795, 510),
                        "HandRight": (770, 570), "ShoulderLeft": (1060, 230), "ElbowLeft": (1095, 375),
                        "WristLeft": (1125, 510), "HandLeft": (1150, 570), "SpineBase": (960, 500),
                        "HipLeft": (900, 550), "KneeLeft": (900, 730), "AnkleLeft": (900, 980), "FootLeft": (900, 1040),
                        "HipRight": (1020, 550), "KneeRight": (1020, 730), "AnkleRight": (1020, 980),
                        "FootRight": (1020, 1040)}

    # Order in which the joints should be plotted, in order to avoid covering
    order_for_joints_plotting = ["SpineShoulder", "SpineMid", "SpineBase", "ShoulderRight", "ShoulderLeft",
                                 "ElbowRight", "ElbowLeft", "WristRight", "WristLeft", "HandRight", "HandLeft",
                                 "HipRight", "HipLeft", "KneeRight", "KneeLeft", "AnkleRight", "AnkleLeft",
                                 "FootRight", "FootLeft", "Head", "Neck"]

    # Radii of the circles, smaller for the joints close to each other
    radius_default = 150
    circles_radii = {"Head": 120, "Neck": 100, "SpineShoulder": radius_default, "SpineMid": radius_default,
                     "ShoulderRight": radius_default, "ElbowRight": radius_default, "WristRight": 120,
                     "HandRight": 100, "ShoulderLeft": radius_default, "ElbowLeft": radius_default,
                     "WristLeft": 120, "HandLeft": 100, "SpineBase": radius_default,
                     "HipLeft": radius_default, "KneeLeft": radius_default, "AnkleLeft": radius_default,
                     "FootLeft": radius_default, "HipRight": radius_default, "KneeRight": radius_default,
                     "AnkleRight": radius_default, "FootRight": radius_default}

    # Calculating the color of the circles and applying a gradient
    circles = {}
    values_to_plot = {}
    for joint in joints_positions.keys():
        ratio = (plot_dictionary[joint] - min_scale) / (max_scale - min_scale)  # Get the ratio of the max value
        color_in = get_color_ratio(colors, ratio)  # Turn that into a color
        color_edge = (color_in[0], color_in[1], color_in[2], 0)  # Transparent color of the circle edge for the gradient
        circles[joint] = gradients.radial(int(circles_radii[joint] * ratio_w), color_in, color_edge)
        values_to_plot[joint] = font.render(str(joint) + ": " + str(round(plot_dictionary[joint], 2)), True, (0, 0, 0))

    # Color scale on the side of the graph
    scale_height = 500
    scale_width = 50
    start_scale_x = 50
    start_scale_y = 540 - scale_height // 2
    sep = scale_height // (len(colors) - 1)

    grad = []
    for i in range(len(colors) - 1):
        grad.append(
            gradients.vertical((int(scale_width * ratio_w),
                                int(((scale_height // (len(colors) - 1)) + 1) * ratio_h)),
                               colors[len(colors) - i - 1], colors[len(colors) - i - 2]))

    scale_top = font.render(str(round(max_scale, 2)), True, (0, 0, 0))
    scale_bottom = font.render(str(round(min_scale, 2)), True, (0, 0, 0))
    scale_title = font.render(str(name), True, (0, 0, 0))
    scale_title = pygame.transform.rotate(scale_title, 90)

    # Program loop
    while program:

        window.fill((0, 0, 0))  # Set background to black

        mouse_coord = pygame.mouse.get_pos()

        for ev in pygame.event.get():

            # Leave the program
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                program = False
                break

        for joint in order_for_joints_plotting:
            window.blit(circles[joint], ((joints_positions[joint][0] - circles_radii[joint]) * ratio_w,
                                         (joints_positions[joint][1] - circles_radii[joint]) * ratio_h))

        window.blit(silhouette, (0, 0))

        to_blit = []
        for joint in order_for_joints_plotting:
            if (joints_positions[joint][0] - mouse_sensitivity) * ratio_w < mouse_coord[0] < (
                    joints_positions[joint][0] + mouse_sensitivity) * ratio_w and (
                    joints_positions[joint][1] - mouse_sensitivity) * ratio_h < mouse_coord[1] < (
                    joints_positions[joint][1] + mouse_sensitivity) * ratio_h:
                to_blit.append(joint)

        height = 0
        for joint in to_blit:
            window.blit(values_to_plot[joint], (resolution[0] - values_to_plot[joint].get_width() - 5,
                                                resolution[1] - values_to_plot[joint].get_height() - 5 - height))
            height += values_to_plot[joint].get_height() + 5

        if show_scale:
            for i in range(len(colors) - 1):
                window.blit(grad[i], (start_scale_x * ratio_w, (start_scale_y + (i * sep)) * ratio_h))
            window.blit(scale_top, (int((start_scale_x + scale_width + 10) * ratio_w),
                                    int((start_scale_y * ratio_h) - scale_top.get_height() // 2)))
            window.blit(scale_bottom, (int((start_scale_x + scale_width + 10) * ratio_w),
                                       int((start_scale_y + scale_height) * ratio_h - scale_bottom.get_height() // 2)))
            window.blit(scale_title, (int((start_scale_x + scale_width + 10) * ratio_w),
                                      int(resolution[1] // 2 - scale_title.get_height() // 2)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()
