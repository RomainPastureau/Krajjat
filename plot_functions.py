"""These various functions allow to plot the data from the Sequence and Audio instances on graphs, or to plot
statistics calculated using the stats_functions."""

import pygame
from pygame.locals import *

import tool_functions
from lib import gradients
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.dates as mdates
import seaborn as sns
import sys
from classes.sequence import *


def single_joint_movement_plotter(sequence_or_sequences, joint_label="HandRight", metrics="all", align=True,
                                  timestamp_start=None, timestamp_end=None, ylim=None, time_format=True,
                                  figure_background_color=None, graph_background_color=None, line_color=None,
                                  line_width=1.0, verbosity=1):
    """Plots the x, y, z positions across time of the joint of one or more sequences, along with the distance travelled,
    velocity and absolute variations of acceleration.

    Note
    ----
    The values for distance travelled and velocity are, by definition, calculated between two timestamps. The
    acceleration is calculated between three timestamps. For simplification purposes, in these graphs, the values are
    plotted at the ending timestamp. In other words, the plotting of the distance and velocity values starts at the
    second timestamp, while the plotting for the acceleration starts at the third timestamp.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence_or_sequences: Sequence or list(Sequence)
        One or multiple sequence instances.

    joint_label: str, optional
        The label of the joint from which to use the values to plot (default: ``"HandRight"``).

    metrics: str or list(str)
        The name of a metric, or a list containing the name of multiple metrics, among ``"x"``, ``"y"``, ``"z"``,
        ``"distance"``, ``"velocity"`` and ``"acceleration"``. This value can also be ``"all"`` (default) and will
        in that case display all the aforementioned metrics.

    align: bool, optional
        If this parameter is set on ``"True"`` (default), and if the parameter ``sequence_or_sequences`` is a list
        containing more than one sequence instance, the function will try to check if one or more of the sequences
        provided is or are sub-sequences of others. If it is the case, the function will align the timestamps of the
        sequences for the plot. If only one sequence is provided, this parameter is ignored.

    timestamp_start: float or None, optional
        If defined, indicates at what timestamp the plot starts.

    timestamp_end: float or None, optional
        If defined, indicates at what timestamp the plot ends.

    ylim: list(int or float), optional
        If defined, sets the lower and upper limits of the y axis for all sub-graphs (e.g. `[0, 1]`)

    time_format: bool, optional
        Defines if the time on the x axis should be shown in raw seconds (``False``) or in a formatted ``mm:ss:ms.``
        format (``True``, default). The format turns automatically to ``hh:mm:ss`` if more than 60 minutes of recording
        are plotted.

    figure_background_color: tuple or string or list, optional
        The color of the background of the whole figure. See :ref:`color_codes` for the color name guidelines.
        If more than one sequence is provided, this parameter should be a list with the color for each line.

    graph_background_color: tuple or string or list, optional
        The color of the background of each graph. See :ref:`color_codes` for the color name guidelines.
        If more than one sequence is provided, this parameter should be a list with the color for each line.

    line_color: tuple or string or list, optional
        The color of the line(s) in the graph. See :ref:`color_codes` for the color name guidelines.
        If more than one sequence is provided, this parameter should be a list with the color for each line.

    line_width: float, optional
        The width of the plotted lines, in pixels (default: 1.0).

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    if type(sequence_or_sequences) is not list:
        sequence_or_sequences = [sequence_or_sequences]

    # Aligning sequences
    if align:
        if verbosity > 0:
            print("Trying to align sequences...", end=" ")
        timestamps = tool_functions.align_multiple_sequences(sequence_or_sequences)
        if verbosity > 0:
            print(" - Done.")
    else:
        timestamps = []
        for sequence in sequence_or_sequences:
            timestamps.append(sequence.get_timestamps())

    for sequence in timestamps:
        print(sequence)

    # Handling timestamp_start and timestamp_end
    if timestamp_start is None:
        for timestamps_sequence in timestamps:
            if timestamp_start is None or timestamp_start > min(timestamps_sequence):
                timestamp_start = min(timestamps_sequence)
    if timestamp_end is None:
        for timestamps_sequence in timestamps:
            if timestamp_end is None or timestamp_end < max(timestamps_sequence):
                timestamp_end = max(timestamps_sequence)

    # Getting the epoch timestamps for each aligned sequence
    epoch_timestamps = []
    for i in range(len(timestamps)):
        sequence_epoch_timestamps = []
        for t in timestamps[i]:
            if timestamp_start <= t <= timestamp_end:
                sequence_epoch_timestamps.append(t)
        epoch_timestamps.append(sequence_epoch_timestamps)
    timestamps = epoch_timestamps

    # Create empty lists for the arrays
    values = {"x": [], "y": [], "z": [],  "distance": [], "velocity": [], "acceleration": []}
    plot_timestamps = {"x": [], "y": [], "z": [],  "distance": [], "velocity": [], "acceleration": []}

    # For all poses
    for i in range(len(sequence_or_sequences)):
        sequence = sequence_or_sequences[i]

        values["x"].append(sequence.get_joint_coordinate_as_list(joint_label, "x", timestamps[i][0], timestamps[i][-1]))
        values["y"].append(sequence.get_joint_coordinate_as_list(joint_label, "y", timestamps[i][0], timestamps[i][-1]))
        values["z"].append(sequence.get_joint_coordinate_as_list(joint_label, "z", timestamps[i][0], timestamps[i][-1]))
        values["distance"].append(sequence.get_joint_distance_as_list(joint_label, None, timestamps[i][0],
                                                                      timestamps[i][-1]))
        values["velocity"].append(sequence.get_joint_velocity_as_list(joint_label, timestamps[i][0], timestamps[i][-1]))
        values["acceleration"].append(sequence.get_joint_acceleration_as_list(joint_label, True, timestamps[i][0],
                                                                              timestamps[i][-1]))

        for key in plot_timestamps.keys():
            plot_timestamps[key].append(sequence.get_timestamps_for_metric(key, False, timestamps[i][0],
                                                                           timestamps[i][-1]))

    if type(metrics) is str and metrics.lower() == "all":
        metrics = ["x", "y", "z", "distance", "velocity", "acceleration"]

    if time_format:
        for key in plot_timestamps:
            for i in range(len(plot_timestamps[key])):
                for j in range(len(plot_timestamps[key][i])):
                    plot_timestamps[key][i][j] = time_unit_to_datetime(plot_timestamps[key][i][j])
        timestamp_start = time_unit_to_datetime(timestamp_start)
        timestamp_end = time_unit_to_datetime(timestamp_end)

    sns.set()
    plt.rcParams["figure.figsize"] = (12, 9)

    fig = plt.figure()
    if figure_background_color is not None:
        fig.patch.set_facecolor(tool_functions.convert_color(figure_background_color, "hex", False))
    fig.subplots(6, 1)  # figsize=(12, 9))
    fig.subplots_adjust(left=0.15, bottom=0.1, right=0.97, top=0.9, wspace=0.3, hspace=0.6)

    # Plot x, y, z, distance travelled and velocities
    parameters = {"rotation": "horizontal", "horizontalalignment": "right", "verticalalignment": "center",
                  "font": {"weight": "bold"}}

    labels_units = {"x": "m", "y": "m", "z": "m", "distance": "m", "velocity": "m/s", "acceleration": "m/s²"}

    # Get colors
    colors = []
    if type(line_color) is list:
        for color in line_color:
            colors.append(convert_color(color, "hex", False))
    elif type(line_color) is str:
        colors.append(convert_color(line_color, "hex", False))
    else:
        colors = [None]

    for i in range(len(metrics)):
        ax = plt.subplot(len(metrics), 1, i + 1)
        if graph_background_color is not None:
            ax.set_facecolor(convert_color(graph_background_color, "hex", False))

        if time_format:
            if (timestamp_end - timestamp_start).seconds >= 3600:
                formatter = mdates.AutoDateFormatter(mdates.AutoDateLocator(), defaultfmt='%H:%M:%S')
            else:
                formatter = mdates.AutoDateFormatter(mdates.AutoDateLocator(), defaultfmt='%M:%S')
            plt.gcf().axes[i].xaxis.set_major_formatter(formatter)

        for j in range(len(sequence_or_sequences)):
            plt.xlim([timestamp_start, timestamp_end])
            if ylim is not None:
                plt.ylim(ylim)
            if i == 0:
                label = sequence_or_sequences[j].get_name()
            else:
                label = None

            plt.plot(plot_timestamps[metrics[i]][j], values[metrics[i]][j], linewidth=line_width,
                     color=colors[j % len(colors)], label=label)

            if i == 0:
                plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand",
                           ncol=len(sequence_or_sequences))

        if (timestamp_end - timestamp_start).seconds >= 3600:
            plt.xlabel("Time (hh:mm:ss.ms)")
        else:
            plt.xlabel("Time (mm:ss.ms)")

        plt.ylabel(metrics[i] + " (" + labels_units[metrics[i]] + ")", **parameters)

    plt.show()


def joints_movement_plotter(sequence, time_series="velocity", audio_or_derivative=None, overlay_audio=False,
                            line_width=1.0, color_scheme="default", show_scale=False, verbosity=1):
    """Plots the distance or velocity across time of the joints, in separate sub-graphs whose localisation roughly
    follows the original body position of the joints.

    .. versionadded:: 2.0

    Parameters
    ----------

    sequence: Sequence
        A Sequence instance.

    time_series: str, optional
        Defines which time series to display in the graphs, either ``"x"``, ``"y"`` or ``"z"`` for the distance
        travelled between poses on one single axis, ``"distance"`` for the euclidian 3D distance travelled between
        poses, ``"velocity"`` (default) for the velocity between poses, or ``"acceleration"`` for the changes of
        velocity between pairs of poses.

    audio_or_derivative: Audio, AudioDerivative or None, optional
        An Audio instance, or any of the AudioDerivative child classes (:class:`Envelope`, :class:`Pitch`,
        :class:`Intensity` or :class:`Formant`). If provided, the samples of the object will be plotted in the top-left
        corner.

    overlay_audio: bool, optional
        If set on ``True``, and if audio_or_derivative is not None, the samples of the ``audio_or_derivative`` object
        will be shown on overlay of the different joint velocities.

    line_width: float, optional
        The width of the plotted lines, in pixels (default: 1.0).

    color_scheme: string or list, optional
        The name of a color scheme or a list of colors to create a gradient. The resulting color gradient will be used
        to color the joints plots depending on their quantity of movement. If set on ``"default"``, the default
        :doc:`color scheme <color_schemes>` will be used, with the joints having the highest quantity of movement
        colored red. If a list of colors is set as parameter, the colors can be specified in RGB, RGBA, hexadecimal
        or standard `HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_.

    show_scale: bool, optional
        If set on ``True``, shows a colored scale on the left side of the graph.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    if verbosity > 0:
        print("Plotting the data skeleton for the sequence " + str(sequence.get_name()) + "...")
        print("\tGetting data...", end=" ")

    timestamps = sequence.get_timestamps()[1:]

    # Compute velocities of the joints
    if time_series in ["x", "y", "z"]:
        joints_time_series = sequence.get_distances(time_series)
        total_time_series_per_joint = sequence.get_total_distance_per_joint(time_series)
        max_value_whole_sequence = sequence.get_max_distance_whole_sequence(time_series)
        title_scale = "Sum of the distances travelled on the " + time_series + " coordinate"
        title = "Distance travelled on the " + time_series + " coordinate between poses for each joint of the sequence"

    elif time_series == "distance":
        joints_time_series = sequence.get_distances()
        total_time_series_per_joint = sequence.get_total_distance_per_joint()
        max_value_whole_sequence = sequence.get_max_distance_whole_sequence()
        title_scale = "Sum of the distances travelled"
        title = "Distance travelled between poses for each joint of the sequence"

    elif time_series == "velocity":
        joints_time_series = sequence.get_velocities()
        total_time_series_per_joint = sequence.get_total_velocity_per_joint()
        max_value_whole_sequence = sequence.get_max_velocity_whole_sequence()
        title_scale = "Sum of the velocities"
        title = "Velocity between poses for each joint of the sequence"

    elif time_series == "acceleration":
        joints_time_series = sequence.get_accelerations(absolute=True)
        total_time_series_per_joint = sequence.get_total_acceleration_per_joint()
        max_value_whole_sequence = sequence.get_max_acceleration_whole_sequence(absolute=True)
        timestamps = sequence.get_timestamps()[2:]
        title_scale = "Sum of the absolute accelerations"
        title = "Variations of acceleration between pairs of poses for each joint of the sequence"

    else:
        raise InvalidParameterValueException("time_series", time_series, ["x", "y", "z", "distance", "velocity",
                                                                          "acceleration"])

    # We define the plot dictionary
    plot_dictionary = {}

    if verbosity > 0:
        print("Done.")
        print("\tCalculating colors...", end=" ")

    # Determine color depending on global velocity
    joints_colors = calculate_colors_by_values(total_time_series_per_joint, color_scheme, "hex", False)

    if verbosity > 0:
        print("Done.")
        print("\tScaling the audio...", end=" ")

    # Scale the audio
    scaled_audio_or_derivative = []
    if audio_or_derivative is not None and overlay_audio:
        scaled_audio_or_derivative = scale_audio(audio_or_derivative.get_samples(), max_value_whole_sequence,
                                                 True, True, 0)

    if verbosity > 0:
        print("Done.")
        print("\tCreating the sub-graphs...", end=" ")

    for joint in joints_time_series.keys():
        graph = Graph()
        if overlay_audio:
            graph.add_plot(audio_or_derivative.get_timestamps(), scaled_audio_or_derivative, line_width, "#d5cdd8")
        graph.add_plot(timestamps, joints_time_series[joint], line_width, joints_colors[joint])
        plot_dictionary[joint] = graph

    title_audio = None
    if audio_or_derivative is not None:
        graph = Graph()
        graph.add_plot(audio_or_derivative.get_timestamps(), audio_or_derivative.get_samples(), line_width, "#a102db")
        plot_dictionary["Audio"] = graph
        title_audio = audio_or_derivative.kind

    if verbosity > 0:
        print("Done.")

    plot_body_graphs(plot_dictionary, min_scale=0, max_scale=max_value_whole_sequence, show_scale=show_scale,
                     title_scale=title_scale, color_scheme=color_scheme, title=title, title_audio=title_audio)


def framerate_plotter(sequence_or_sequences, line_width=1.0, line_color="#000000"):
    """Plots the framerates across time for one or multiple sequences. The framerate is calculated by getting the
    inverse of the time between consecutive poses.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence_or_sequences: Sequence or list(Sequence)
        One or multiple sequence instances.

    line_width: float, optional
        The width of the plotted lines, in pixels (default: 1.0).

    line_color: tuple(int, int, int) or tuple(int, int, int, int) or string
        The color of the line in the graph. This parameter can be:

        • A `HTML/CSS name <https://en.wikipedia.org/wiki/X11_color_names>`_ (e.g. ``"red"`` or
          ``"blanched almond"``),
        • An hexadecimal code, starting with a number sign (``#``, e.g. ``"#ffcc00"`` or ``"#c0ffee"``).
        • A RGB or RGBA tuple (e.g. ``(153, 204, 0)`` or ``(77, 77, 77, 255)``).
    """

    # If only one sequence has been provided, we turn it into a list
    if type(sequence_or_sequences) is not list:
        sequence_or_sequences = [sequence_or_sequences]

    # Figure parameters
    sns.set()
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.9, wspace=0.3, hspace=0.7)
    labels = get_difference_paths(get_objects_names(sequence_or_sequences))
    print(labels)
    for i in range(len(labels)):
        if len(labels[i]) == 1:
            labels[i] = labels[i][0]
        else:
            labels[i] = " · ".join(labels[i])

    # Values and lists for calculating the framerates
    max_framerate = 0
    framerates_list = []
    timestamps_list = []
    averages_list = []

    # Getting the framerate vectors
    for seq in range(len(sequence_or_sequences)):

        sequence = sequence_or_sequences[seq]
        framerates, timestamps = sequence.get_framerates()
        average = sequence.get_average_framerate()
        averages = [average for _ in range(len(framerates))]

        framerates_list.append(framerates)
        timestamps_list.append(timestamps)
        averages_list.append(averages)

        if max(framerates) > max_framerate:
            max_framerate = max(framerates)

    # Size of the plot area
    i = math.ceil(math.sqrt(len(sequence_or_sequences)))
    j = i - 1 * (len(sequence_or_sequences) <= i * (i - 1))

    # Plot the framerates
    for seq in range(len(sequence_or_sequences)):
        plt.subplot(i, j, seq + 1)
        plt.ylim([0, max_framerate + 1])
        plt.plot(timestamps_list[seq], framerates_list[seq], linewidth=line_width, color=line_color, label="Framerate")
        plt.plot(timestamps_list[seq], averages_list[seq], linewidth=line_width, color="#ff0000", label="Average")
        if seq == 0:
            plt.legend(bbox_to_anchor=(0, 1 + i * 0.15), loc="upper left", ncol=2)
        plt.title(labels[seq] + " [Avg: " + format(averages_list[seq][0], '.2f') + "]")

    plt.show()


# noinspection PyArgumentList
def audio_plotter(audio, threshold_low_pass_envelope=10, number_of_formants=3):
    """Given an audio instance, plots the samples, filtered envelope, pitch, intensity, formants and spectrogram.

    .. versionadded:: 2.0

    Parameters
    ----------
    audio: Audio
        An Audio instance.
    threshold_low_pass_envelope: int or None, optional
        Defines the threshold frequency over which the envelope will be filtered (default: 10). If set on ``None``, the
        envelope will not be filtered.
    number_of_formants: int, optional
        The number of formants to plot (default: 3).

    Warning
    -------
    With non-resampled audio files, this function can take several minutes to compute before being able to plot the
    graphs. It is recommended to perform a downsampling of the audio object before running this function.
    """

    try:
        from parselmouth import Sound
    except ImportError:
        raise ModuleNotFoundException("parselmouth", "get the pitch, intensity and formants of an audio clip.")

    try:
        import numpy as np
    except ImportError:
        raise ModuleNotFoundException("numpy", "get the pitch, intensity and formants of an audio clip.")

    # Creating a Parselmouth object
    audio_samples = np.array(audio.get_samples(), dtype=np.float64)
    parselmouth_sound = Sound(np.ndarray(np.shape(audio_samples), np.float64, audio_samples), audio.frequency)

    # Envelope
    envelope = audio.get_envelope(filter_over=10, verbosity=0)

    # Intensity
    intensity = parselmouth_sound.to_intensity(time_step=1 / audio.frequency)
    temp_timestamps = add_delay(intensity.xs(), -1 / (2 * audio.frequency))
    intensity_samples, intensity_timestamps = pad(intensity.values.T, temp_timestamps, audio.timestamps, 100)

    # Pitch
    pitch = parselmouth_sound.to_pitch(time_step=1 / audio.frequency)
    pitch_samples, pitch_timestamps = pad(pitch.selected_array["frequency"], pitch.xs(), audio.timestamps)

    # Formants
    formants = parselmouth_sound.to_formant_burg(time_step=1 / audio.frequency)
    temp_timestamps = add_delay(formants.xs(), -1 / (2 * audio.frequency))
    number_of_points = formants.get_number_of_frames()
    formants_samples = [[] for _ in range(number_of_formants)]
    formants_timestamps = [[] for _ in range(number_of_formants)]
    for i in range(1, number_of_points + 1):
        t = formants.get_time_from_frame_number(i)
        for j in range(number_of_formants):
            formants_samples[j].append(formants.get_value_at_time(formant_number=j + 1, time=t))
    for j in range(number_of_formants):
        formants_samples[j], formants_timestamps[j] = pad(formants_samples[j], temp_timestamps, audio.timestamps)

    import seaborn as sns
    sns.set()

    plt.subplot(3, 2, 1)
    plt.plot(audio.timestamps, audio.samples)
    plt.title("Original audio")

    plt.subplot(3, 2, 2)
    plt.plot(envelope.timestamps, envelope.samples)
    title = "Envelope"
    if threshold_low_pass_envelope is not None:
        title += " (low-pass: " + str(threshold_low_pass_envelope) + " Hz)"
    plt.title("Envelope")

    plt.subplot(3, 2, 3)
    plt.plot(intensity_timestamps, intensity_samples)
    plt.title("Intensity")

    plt.subplot(3, 2, 4)
    plt.plot(pitch_timestamps, pitch_samples)
    plt.title("Pitch")

    plt.subplot(3, 2, 5)
    for i in range(len(formants_samples)):
        plt.plot(formants_timestamps[i], formants_samples[i], label="f" + str(i + 1))
    plt.legend()
    plt.title("Formants")

    plt.subplot(3, 2, 6)
    spectrogram = parselmouth_sound.to_spectrogram()
    x, y = spectrogram.x_grid(), spectrogram.y_grid()
    sg_db = 10 * np.log10(spectrogram.values)
    plt.pcolormesh(x, y, sg_db, vmin=sg_db.max() - 70, cmap='afmhot')
    plt.ylim([spectrogram.ymin, spectrogram.ymax])
    plt.xlabel("time [s]")
    plt.ylabel("frequency [Hz]")

    plt.show()


def plot_body_graphs(plot_dictionary, joint_layout="auto", title=None, min_scale=None, max_scale=None, show_scale=False,
                     title_scale=None, color_scheme="default", title_audio="Audio"):
    """Creates multiple sub-plots placed so that each joint is roughly placed where it is located on the body. The
    values of each subplot are taken from the parameter ``plot_dictionary``, and the positions from the layout
    differ between Kinect and Kualisys systems.

    .. versionadded:: 2.0

    Parameters
    ----------
    plot_dictionary: dict(str: Graph)
        A dictionary containing the title of the sub-graphs as keys, and Graph objects as elements.

    joint_layout: str, optional
        Defines the layout to use for the sub-plots of the joints: ``"kinect"`` or ``"qualisys"``/``"kualisys"``. If
        set on ``"auto"`` (default), the function will automatically assign the layout depending on if the joint label
        ``"Chest"`` is among the keys of the ``plot_dictionary``.

        The joint layouts are a grid of 7 × 5 sub-plots for Kinect, and 13 × 7 subplots for Qualisys. The corresponding
        spot for each joint are loaded from ``"res/kinect_joints_subplot_layout.txt"`` and
        ``"res/kualisys_joints_subplot_layout.txt"``.

    title: str or None, optional
        The title to display on top of the plot.

    min_scale: float or None, optional
        The minimum value to set on the y axis, for all the elements in the ``plot_dictionary`` that match joint keys
        (i.e., except from the sub-plot under the ``"Audio"`` key). If set on None (default), the minimum value will be
        the overall minimum value from the ``plot_dictionary``, with the sub-graph ``"Audio"`` excluded.

    max_scale: float or None, optional
        The maximum value to set on the y axis, for all the elements in the ``plot_dictionary`` that match joint keys
        (i.e., except from the sub-plot under the ``"Audio"`` key). If set on None (default), the maximum value will be
        the overall minimum value from the ``plot_dictionary``, with the sub-graph ``"Audio"`` excluded.

    show_scale: bool, optional
        If set on ``True``, shows a colored scale on the right side of the graph.

    title_scale: str or None, optional
        Defines a title to give to the scale, if ``show_scale`` is set on ``True``.

    color_scheme: str or list, optional
        The color scheme to use for the color scale. This color scheme should be coherent with the colors defined in
        the ``plot_dictionary``.

    title_audio: str or None, optional
        The title to give to the sub-plot that matches the key ``"Audio"`` from the ``plot_dictionary``. This sub-plot
        is located in the top-left corner of the plot, and is not scaled the same way as the other plots. By default,
        the title of this sub-plot is ``"Audio"``, but this parameter allows to change the title to put the name of an
        AudioDerivative type, such as ``"Envelope"`` or ``"Pitch"``, for example.
    """

    # Getting the joint layout
    if joint_layout == "auto":
        if "Chest" in plot_dictionary.keys():
            joint_layout = "qualisys"
        else:
            joint_layout = "kinect"
    joints_positions, joint_layout = load_joints_subplot_layout(joint_layout)

    # Figure parameters
    sns.set()
    plt.rcParams["figure.figsize"] = (12, 9)
    if joint_layout == "kinect":
        rows, cols = 7, 5
    else:
        rows, cols = 13, 7
    fig, axes = plt.subplots(nrows=rows, ncols=cols)
    if title is not None:
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.93, wspace=0.3, hspace=0.6)
        fig.suptitle(title, fontsize="x-large", fontweight="bold")
    else:
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0.3, hspace=0.6)

    # Get min and max values
    min_value, max_value = get_min_max_values_from_plot_dictionary(plot_dictionary, keys_to_exclude=["Audio"])
    if max_scale == "auto":
        max_scale = max_value

    # Plot the subplots
    for key in plot_dictionary.keys():
        plt.subplot(rows, cols, joints_positions[key])
        if key != "Audio":  # We want to scale everything apart from the audio
            plt.ylim([min_value, max_value])
            plt.title(key)
        else:
            plt.title(title_audio)
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
    color_list = calculate_color_points_on_gradient(color_scheme, 100)
    print(convert_colors(color_list, "hex", include_alpha=False))
    color_list = convert_colors(color_list, "hex", include_alpha=False)

    # Show the scale if max_scale is not None
    if show_scale:
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.9, top=0.97, wspace=0.3, hspace=0.6)
        cmap = colors.ListedColormap(color_list)
        norm = colors.Normalize(vmin=min_scale, vmax=max_scale)
        cbax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbax, orientation='vertical', label=title_scale)
    plt.show()


def plot_silhouette(plot_dictionary, joint_layout="auto", title=None, min_scale="auto", max_scale="auto",
                    show_scale=True, title_scale=None, color_scheme="default", color_background="white",
                    color_silhouette="black", resolution=0.5, full_screen=False, path_save=None, verbosity=1):
    """Plots a silhouette with circles representing the different joints, colored according to their values in the
    ``plot_dictionary``. Passing the mouse on the different joints shows, in the bottom right corner, the value
    associated to the joint the mouse is on.

    .. versionadded:: 2.0

    Parameters
    ----------
    plot_dictionary: dict(str: float)
        A dictionary containing the title of the sub-graphs as keys, and values as elements.

    joint_layout: str, optional
        Defines the layout to use for the sub-plots of the joints: ``"kinect"`` or ``"qualisys"``/``"kualisys"``. If
        set on ``"auto"`` (default), the function will automatically assign the layout depending on if the joint label
        ``"Chest"`` is among the keys of the ``plot_dictionary``. In order to create a personalized layout, it is
        possible to click on the figure to print in the console a specific position. Pressing the CTRL key at the same
        time allows to display a test circle where the mouse is located, to give an idea of the render.

        The joint layouts are a grid of 7 × 5 sub-plots for Kinect, and 13 × 7 subplots for Qualisys. The corresponding
        spot for each joint are loaded from ``"res/kinect_joints_subplot_layout.txt"`` and
        ``"res/kualisys_joints_subplot_layout.txt"``.

    title: str or None, optional
        The title to display on top of the plot.

    min_scale: str or float, optional
        If set on ``"auto"`` (default), the lowest value of the scale will be set on the lowest value in the
        ``plot_dictionary``. If set on a number, all the values below that number will be colored will the color
        matching this parameter on the scale.

    max_scale: str or float, optional
        If set on ``"auto"`` (default), the highest value of the scale will be set on the highest value in the
        ``plot_dictionary``. If set on a number, all the values above that number will be colored will the color
        matching this parameter on the scale.

    show_scale: bool, optional
        If set on ``True``, shows a colored scale on the left side of the graph.

    title_scale: str or None, optional
        Defines a title to give to the scale, if ``show_scale`` is set on ``True``.

    color_scheme: str or list, optional
        The color scheme of the scale.
        This parameter can take a number of forms:

        • **The name of a color scheme:** a string matching one of the color gradients available in
          :doc:`color_schemes` (default: ``"default"``).
        • **A list of colors:** a list containing colors, either using:

            • Their `HTML/CSS names <https://en.wikipedia.org/wiki/X11_color_names>`_ (e.g. ``"red"`` or
              ``"blanched almond"``),
            • Their hexadecimal code, starting with a number sign (``#``, e.g. ``"#ffcc00"`` or ``"#c0ffee"``).
            • Their RGB or RGBA tuples (e.g. ``(153, 204, 0)`` or ``(77, 77, 77, 255)``).

          These different codes can be used concurrently, e.g. ``["red", (14, 18, 32), "#a1b2c3"]``.

    color_background: str, tuple(int, int, int) or tuple(int, int, int, int), optional
        The color of the background (default: ``"white"``). This parameter can be a tuple with RGB or RGBA values,
        a string with a hexadecimal value (starting with a leading ``#``) or one of the standard
        `HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_.

    color_silhouette: str, tuple(int, int, int) or tuple(int, int, int, int), optional
        The color of the silhouette (default: ``"black"``). This parameter can be a tuple with RGB or RGBA values,
        a string with a hexadecimal value (starting with a leading ``#``) or one of the standard
        `HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_.

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the silhouette. This parameter can be:

        • A tuple with two integers, representing the width and height of the window in pixels.
        • A float, representing the ratio of the total screen width and height; for example, setting
          this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
          Note: if a video is provided and set on the side of the sequence, or if two sequences are provided,
          side by side, the horizontal resolution will be set to be twice the size. A parameter of 0.5 on a screen
          that is 1920 × 1080 pixels will, in that case, create a window of 1920 × 540 pixels.
        • None: in that case, the window will be the size of the screen.

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``) or not (``False``, default).

    path_save: str or None optional
        If provided, the function will save the silhouette as a picture. The path should contain the folder, the name
        file, and one of the following extensions: ``".png"``, ``".jpeg"`` or ``".bmp"``.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    pygame.init()

    # Setting up the resolution
    info = pygame.display.Info()
    if resolution is None:
        resolution = (info.current_w, info.current_h)
    elif isinstance(resolution, float):
        resolution = (int(info.current_w * resolution), int(info.current_h * resolution))

    if verbosity > 0:
        print("Window resolution: " + str(resolution))

    # Setting up the full screen mode
    if full_screen:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode(resolution)

    # Scale variables to the resolution
    ratio_w = resolution[0] / 1920
    ratio_h = resolution[1] / 1080

    # Load silhouette picture, color it and resize it
    silhouette = pygame.image.load("res/silhouette.png")
    silhouette.get_size()
    color_background = convert_color(color_background, "rgb", False)
    if color_background != (255, 255, 255):
        for x in range(silhouette.get_width()):
            for y in range(silhouette.get_height()):
                alpha = silhouette.get_at((x, y))[3]
                silhouette.set_at((x, y), pygame.Color(color_background[0], color_background[1],
                                                       color_background[2], alpha))
    silhouette = pygame.transform.scale(silhouette, (resolution[1] * (16 / 9), resolution[1]))
    silhouette_x = resolution[0] // 2 - silhouette.get_width() // 2

    # Font and colors
    colors = convert_colors(color_scheme, "rgb", True)  # Color scheme
    color_silhouette = convert_color(color_silhouette, "rgb", False)
    luminance = color_background[0] * 0.2126 + color_background[1] * 0.7152 + color_background[2] * 0.0722
    font = pygame.font.Font("res/junction_bold.otf", int(resolution[1] * 0.04))
    if luminance > 0.5:
        font_color = convert_color("black", "rgb", False)
    else:
        font_color = convert_color("white", "rgb", False)

    # If the scale is on auto, we scale it the max value
    min_value, max_value = get_min_max_values_from_plot_dictionary(plot_dictionary)
    if min_scale == "auto":
        min_scale = min_value
    if max_scale == "auto":
        max_scale = max_value

    # Getting the joint layout
    if joint_layout == "auto":
        if "Chest" in plot_dictionary.keys():
            joint_layout = "qualisys"
        else:
            joint_layout = "kinect"

    joints_positions, order_joints = load_joints_silhouette_layout(joint_layout)

    # Calculating the color of the circles and applying a gradient
    circles = {}
    values_to_plot = {}

    for joint in plot_dictionary.keys():
        ratio = (plot_dictionary[joint] - min_scale) / (max_scale - min_scale)  # Get the ratio of the max value
        color_in = calculate_color_ratio(colors, ratio)  # Turn that into a color
        color_edge = (color_in[0], color_in[1], color_in[2], 0)  # Transparent color of the circle edge for the gradient
        circles[joint] = gradients.radial(int(joints_positions[joint][2] * ratio_h), color_in, color_edge)
        values_to_plot[joint] = font.render(str(joint) + ": " + str(round(plot_dictionary[joint], 2)), True, font_color)

    # Color scale on the side of the graph
    scale_height = 500
    scale_width = 50
    start_scale_x = 50
    start_scale_y = 540 - scale_height // 2
    sep = scale_height // (len(colors) - 1)

    # Side backgrounds
    side_background = None
    if resolution[0] / resolution[1] > 16 / 9:
        side_background = pygame.Surface((silhouette_x, resolution[1] + 5))
        side_background.fill(color_background)

    grad = []
    for i in range(len(colors) - 1):
        grad.append(gradients.vertical((int(scale_width * ratio_w),
                                        int(((scale_height // (len(colors) - 1)) + 1) * ratio_h)),
                                       colors[len(colors) - i - 1], colors[len(colors) - i - 2]))

    scale_top = font.render(str(round(max_scale, 2)), True, font_color)
    scale_bottom = font.render(str(round(min_scale, 2)), True, font_color)
    if title_scale is None:
        title_scale = ""
    scale_title = font.render(str(title_scale), True, font_color)
    scale_title = pygame.transform.rotate(scale_title, 90)

    # Title
    title_plot = None
    if title is not None:
        title_plot = font.render(str(title), True, font_color)

    # Mouse
    pygame.mouse.set_visible(True)  # Allows the mouse to be visible
    mouse_sensitivity = 50  # Radius around the center in which the mouse position will be detected as inside

    place_circle = False
    circle_position = None
    color_in = calculate_color_ratio(colors, 1)  # Turn that into a color
    color_edge = (color_in[0], color_in[1], color_in[2], 0)  # Transparent color of the circle edge for the gradient
    circle = gradients.radial(int(150 * ratio_w), color_in, color_edge)
    run = True  # Loop variable

    # Program loop
    while run:

        window.fill(color_silhouette)  # Set background to black

        if resolution[0] / resolution[1] > 16 / 9:
            window.blit(side_background, (0, 0))
            window.blit(side_background, (window.get_width() - side_background.get_width(), 0))

        mouse_coord = pygame.mouse.get_pos()

        for event in pygame.event.get():

            # Leave the program
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = False
                break

            elif event.type == KEYDOWN and event.key in [K_LCTRL, K_RCTRL]:
                place_circle = True
            elif event.type == KEYUP and event.key in [K_LCTRL, K_RCTRL]:
                place_circle = False

            # Click in the figure
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                print((mouse_coord[0] / ratio_w, mouse_coord[1] / ratio_h))
                print(mouse_coord)
                if place_circle:
                    circle_position = (mouse_coord[0] * ratio_w, mouse_coord[1] * ratio_h)

        for joint in order_joints:
            if joint in plot_dictionary.keys():
                window.blit(circles[joint], (((joints_positions[joint][0] - joints_positions[joint][2]) * ratio_h +
                                              silhouette_x),
                                             (joints_positions[joint][1] - joints_positions[joint][2]) * ratio_h))

        if circle_position is not None:
            window.blit(circle, circle_position)

        if title is not None:
            window.blit(title_plot, ((window.get_width() - title_plot.get_width()) // 2, 5 * ratio_h))

        window.blit(silhouette, (silhouette_x, 0))

        to_blit = []
        for joint in order_joints:
            if joint in plot_dictionary.keys():
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

        if path_save is not None:
            pygame.image.save(window, path_save)
            path_save = None

    pygame.quit()
    sys.exit()
