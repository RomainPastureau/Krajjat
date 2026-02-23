"""These various functions allow to plot the data from the Sequence and Audio instances on graphs, or to plot
statistics calculated using the analysis_functions."""
import pygame
from parselmouth import Sound
from pygame.locals import *
from scipy import signal

from krajjat.tool_functions import *
from krajjat.lib import gradients
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.dates as mdates
import seaborn as sns


def single_joint_movement_plotter(sequence_or_sequences, joint_label="HandRight", measures="default", domain="time",
                                  window_length=7, poly_order=None, nperseg=None, welch_window="hann", align=True,
                                  timestamp_start=None, timestamp_end=None, xlim=None, ylim=None, time_format=True,
                                  figure_background_color=None, graph_background_color=None, line_color=None,
                                  line_width=1.0, show=True, path_save=None, verbosity=1, **kwargs):
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

    measures: str or list(str)
        The name of a metric, or a list containing the name of multiple metrics, among:

        • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
        • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
        • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
        • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
        • For the consecutive distances on the x-axis: ``"dx"`, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
          or ``"x_dist"``.
        • For the consecutive distances on the y-axis: ``"dy"`, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
          or ``"y_dist"``.
        • For the consecutive distances on the z-axis: ``"dz"`, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
          or ``"z_dist"``.
        • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
        • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
        • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
        • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
        • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
        • For the pop: ``"p"``, ``"pop"``, or ``6``.
        • For any derivative of a higher order, set the corresponding integer.

        This value can also be ``"default"`` (default) and will in that case display a sub-selection made of the x, y
        and z coordinates, the consecutive distances, the velocity, and the acceleration.

        It is also possible to add the suffix ``"_abs"`` after a specific measure to plot the absolute values of the
        measure.

    domain: str, optional
        Defines if to plot the movement in the time domain (`"time"`, default) or in the frequency domain
        (`"frequency"`).

    window_length: int, optional
        The length of the window for the Savitzky–Golay filter when calculating a derivative (default: 7). See
        `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
        for more info.

    poly_order: int|None, optional
        The order of the polynomial for the Savitzky–Golay filter. If set on `None`, the polynomial will be set to
        one over the derivative rank. See
        `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
        for more info.

    nperseg: int|None, optional
        Number of samples per segment for the power spectrum density calculation (in case `domain` is set to
        ``"frequency"``). This parameter is passed to `scipy.signal.welch
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html>`_.

    welch_window: str, optional
        The window to use when calculating the power spectrum density (in case `domain` is set to ``"frequency"``).
        This parameter is passed to `scipy.signal.welch
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html>`_.

    align: bool, optional
        If this parameter is set on ``"True"`` (default), and if the parameter ``sequence_or_sequences`` is a list
        containing more than one sequence instance, the function will try to check if one or more of the sequences
        provided is or are sub-sequences of others. If it is the case, the function will align the timestamps of the
        sequences for the plot. If only one sequence is provided, this parameter is ignored.

    timestamp_start: float or None, optional
        If defined, indicates at what timestamp to start to calculate the measure.

    timestamp_end: float or None, optional
        If defined, indicates at what timestamp to finish to calculate the measure.

    xlim: list(int|float)|None, optional
        If defined, indicates the timestamp range of frequency range on the x-axis for all subplots. If not defined,
        the values of xlim will take the values of `timestamp_start` and `timestamp_end` in the time domain,
        or ``0`` and the half of the highest sequence frequency in the frequency domain.

    ylim: list(float) or list(list(float)) optional
        If defined, sets the lower and upper limits of the y-axis for all sub-graphs (e.g. `[0, 1]`). If this parameter
        is a list of lists, each sublist sets the limits for each sub-graph.

    time_format: bool, optional
        Defines if the time on the x-axis should be shown in raw seconds (``False``) or in a formatted ``mm:ss:ms.``
        format (``True``, default). The format turns automatically to ``hh:mm:ss`` if more than 60 minutes of recording
        are plotted.

    figure_background_color: tuple or string or list, optional
        The color of the background of the whole figure. See :doc:`../appendix/color_codes` for the color name
        guidelines. If more than one sequence is provided, this parameter should be a list with the color for each
        line.

    graph_background_color: tuple or string or list, optional
        The color of the background of each graph. See :doc:`../appendix/color_codes` for the color name guidelines.
        If more than one sequence is provided, this parameter should be a list with the color for each line.

    line_color: tuple or string or list, optional
        The color of the line(s) in the graph. See :doc:`../appendix/color_codes` for the color name guidelines.
        If more than one sequence is provided, this parameter should be a list with the color for each line.

    line_width: float, optional
        The width of the plotted lines, in pixels (default: 1.0).

    show: bool, optional
        If set on `False`, the function does not show the graph. This parameter can be set if the purpose of the
        function is to save the graph in a file, without having to halt the execution of the code when opening a window.

    path_save: str or None optional
        If provided, the function will save the plot as a picture. The path should contain the folder, the name
        file, and one of the following extensions: ``".png"``, ``".jpeg"`` or ``".bmp"``.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict
        Any of the parameters accepted by
        `matplotlib.pyplot.plot <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html>`_.

    Examples
    --------
    >>> sequence = Sequence("Sequences/Auge/sequence_01.tsv")
    >>> single_joint_movement_plotter(sequence, joint_label="HandRight", measures="default")
    >>> sequence_cj = sequence.correct_jitter(1, 5)
    >>> single_joint_movement_plotter([sequence, sequence_cj], joint_label="HandRight", measures=["d", "v", "a", "j"])
    >>> single_joint_movement_plotter([sequence, sequence_cj], joint_label="HandRight",
    ...                               measures=["d", "v", "a", "j"], domain="frequency", x_start=1, x_end=2,
    ...                               ylim=[[0, 4e-5], [0, 0.003], [0, 0.35], [0, 50]], line_width=2,
    ...                               line_color=["bcbl blue", "bcbl dark blue"], verbosity=1)
    """

    if verbosity > 0:
        if len(sequence_or_sequences) > 1:
            print(f"Plotting the movement for {len(sequence_or_sequences)} sequences...")
            print("\tGetting data...", end=" ")
        else:
            print(f"Plotting the movement for the sequence {sequence_or_sequences[0].get_name()}...")
            print("\tGetting data...", end=" ")

    sequences, timestamps = _prepare_plot_timestamps(sequence_or_sequences, align, verbosity)
    timestamp_start, timestamp_end, xlim = _calculate_plot_limits(sequences, timestamps, domain,
                                                                  timestamp_start, timestamp_end, xlim, verbosity)

    if verbosity > 0:
        print(f"Getting the timestamps between {timestamp_start} s and {timestamp_end} s for each sequence...", end=" ")
        timestamps = [np.array(seq_timestamps)[np.where(np.logical_and(seq_timestamps >= timestamp_start,
                                                                       seq_timestamps <= timestamp_end))]
                      for seq_timestamps in timestamps]
        print("Done.")

    if verbosity > 0:
        print("Checking the validity of the requested measures...", end=" ")

    # Setting the measures on their values
    if measures == "default":
        measures = ["x", "y", "z", "distance", "velocity", "acceleration"]
    elif type(measures) is str:
        measures = list(measures)

    # Create empty lists for the arrays
    absolute_measures = {}

    for m in range(len(measures)):
        abs_measure = False
        if measures[m].endswith("_abs"):
            measures[m] = measures[m][:-4]
            abs_measure = True

        if measures[m] not in CLEAN_DERIV_NAMES:
            raise InvalidParameterValueException("measures", measures[m], ["x", "y", "z",
                                                                           "distance_x", "distance_y", "distance_z",
                                                                           "distance", "velocity", "acceleration",
                                                                           "jerk", "snap", "crackle", "pop"])

        measures[m] = CLEAN_DERIV_NAMES[measures[m]]
        absolute_measures[measures[m]] = abs_measure

    values = {measure: [] for measure in measures}
    plot_timestamps = {measure: [] for measure in measures}

    if verbosity > 0:
        print("Done.")

    if verbosity > 0:
        print("Getting the measures for each sequence...", end=" ")

    # For all sequences
    for i in range(len(sequences)):
        sequence = sequences[i]

        if domain == "time":

            for measure in measures:
                values[measure].append(sequence.get_measure(measure, joint_label, timestamp_start, timestamp_end,
                                                            window_length, poly_order, absolute_measures[measure],
                                                            verbosity))

            for measure in plot_timestamps.keys():
                timestamps[i] = np.array(timestamps[i])
                plot_timestamps[measure].append(
                    timestamps[i][np.where((timestamps[i] >= xlim[0]) & (timestamps[i] <= xlim[1]))])

        elif domain == "frequency":

            for measure in measures:
                values[measure].append(sequence.get_measure(measure, joint_label, timestamp_start, timestamp_end,
                                                            window_length, poly_order, absolute_measures[measure],
                                                            verbosity))

                t, values[measure][i] = signal.welch(np.array(values[measure][i]),
                                                     sequence.get_sampling_rate(), welch_window, nperseg,
                                                     scaling="spectrum")
                plot_timestamps[measure].append(t)

    if verbosity > 0:
        print("Done.")

    if time_format and domain != "frequency":
        if verbosity > 0:
            print("Setting the timestamps to seconds...", end=" ")
        for measure in plot_timestamps:
            for i in range(len(sequences)):
                plot_timestamps[measure][i] = np.array(plot_timestamps[measure][i] * 1000000, dtype="datetime64[us]")
        timestamp_start = np.datetime64(int(timestamp_start * 1000000), "us")
        timestamp_end = np.datetime64(int(timestamp_end * 1000000), "us")
        xlim[0] = np.datetime64(int(xlim[0] * 1000000), "us")
        xlim[1] = np.datetime64(int(xlim[1] * 1000000), "us")
        if verbosity > 0:
            print("Done.")

    sns.set_theme()
    plt.rcParams["figure.figsize"] = (12, 9)

    fig = plt.figure()
    if figure_background_color is not None:
        fig.patch.set_facecolor(convert_color(figure_background_color, "hex", False))
    fig.subplots(len(measures), 1)  # figsize=(12, 9))
    fig.subplots_adjust(left=0.15, bottom=0.1, right=0.97, top=0.9, wspace=0.3, hspace=0.6)

    # Plot x, y, z, distance travelled and velocities
    parameters = {"rotation": "horizontal", "horizontalalignment": "right", "verticalalignment": "center",
                  "font": {"weight": "bold"}}

    if domain == "time":
        labels_units = {"x": "m", "y": "m", "z": "m", "distance": "m", "distance x": "m", "distance y": "m",
                        "distance z": "m", "velocity": "m/s", "acceleration": "m/s²", "jerk": "m/s³", "snap": "m/s⁴",
                        "crackle": "m/s⁵", "pop": "m/s⁶"}
    else:
        labels_units = {"x": "A.U.", "y": "A.U.", "z": "A.U.", "distance": "A.U.", "distance x": "A.U.",
                        "distance y": "A.U.", "distance z": "A.U.", "velocity": "A.U.", "acceleration": "A.U.",
                        "jerk": "A.U.", "snap": "A.U.", "crackle": "A.U.", "pop": "A.U."}

    # Get colors
    colors = []
    if type(line_color) is list:
        for color in line_color:
            colors.append(convert_color(color, "hex", False))
    elif type(line_color) is str:
        colors.append(convert_color(line_color, "hex", False))
    else:
        colors = [None]

    # Formatting functions for the x-axis (MM:SS and HH:MM:SS)
    def get_label(value, include_hour=True, include_us=True):
        """Returns a label value depending on the selected parameters."""

        neg = False
        # If negative, put positive
        if value < 0:
            neg = True
            value = abs(value)

        # If zero, set zero
        elif value == 0:
            if include_hour:
                return "00:00:00"
            else:
                return "00:00"

        # Turn to timedelta
        td_value = mdates.num2timedelta(value)

        seconds = td_value.total_seconds()
        hh = str(int(seconds // 3600)).zfill(2)
        mm = str(int((seconds // 60) % 60)).zfill(2)
        ss = str(int(seconds % 60)).zfill(2)

        us = str(int((seconds % 1) * 1000000)).rstrip("0")

        label = ""
        if neg:
            label += "-"
        if include_hour:
            label += hh + ":"
        label += mm + ":" + ss
        if include_us and us != "":
            label += "." + us

        return label

    def get_label_hh_mm_ss_no_ms(value, pos=None):
        """Returns a label value as HH:MM:SS, without any ms value."""
        return get_label(value, True, False)

    def get_label_hh_mm_ss(value, pos=None):
        """Returns a label value as HH:MM:SS.ms, without any trailing zero."""
        return get_label(value, True, True)

    def set_label_time_figure(ax):
        """Sets the time formatted labels on the x axes."""
        formatter = mdates.AutoDateFormatter(ax.xaxis.get_major_locator())
        formatter.scaled[1 / mdates.MUSECONDS_PER_DAY] = get_label_hh_mm_ss
        formatter.scaled[1 / mdates.SEC_PER_DAY] = get_label_hh_mm_ss
        formatter.scaled[1 / mdates.MINUTES_PER_DAY] = get_label_hh_mm_ss_no_ms
        formatter.scaled[1 / mdates.HOURS_PER_DAY] = get_label_hh_mm_ss_no_ms
        formatter.scaled[1] = get_label_hh_mm_ss_no_ms
        formatter.scaled[mdates.DAYS_PER_MONTH] = get_label_hh_mm_ss_no_ms
        formatter.scaled[mdates.DAYS_PER_YEAR] = get_label_hh_mm_ss_no_ms
        ax.xaxis.set_major_formatter(formatter)
        return ax

    for i in range(len(measures)):
        ax = plt.subplot(len(measures), 1, i + 1)
        if graph_background_color is not None:
            ax.set_facecolor(convert_color(graph_background_color, "hex", False))

            if domain == "time":
                ax = set_label_time_figure(ax)

                # plt.gcf().axes[i].xaxis.set_major_formatter(formatter)
                if (xlim[1] - xlim[0]).seconds >= 3600:
                    plt.xlabel("Time (hh:mm:ss.ms)")
                else:
                    plt.xlabel("Time (mm:ss.ms)")

            else:
                plt.xlabel("Frequency (Hz)")

        for j in range(len(sequences)):
            plt.xlim(xlim)
            if ylim is not None:
                if type(ylim[0]) is list:
                    plt.ylim(ylim[i])
                else:
                    plt.ylim(ylim)
            if i == 0:
                label = sequences[j].get_name()
            else:
                label = None

            start_timestamps = len(plot_timestamps[measures[i]][j]) - len(values[measures[i]][j])
            if start_timestamps not in [0, 1]:
                raise Exception("The number of timestamps and the number of values must be equal for plotting.")
            plt.plot(plot_timestamps[measures[i]][j][start_timestamps:], values[measures[i]][j],
                     linewidth=line_width, color=colors[j % len(colors)], label=label, **kwargs)

            if i == 0:
                plt.legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand",
                           ncol=len(sequences))

        plt.ylabel(measures[i] + " (" + labels_units[measures[i]] + ")", **parameters)

    if show:
        plt.show()

    if path_save is not None:
        os.makedirs(op.split(path_save)[0], exist_ok=True)
        plt.savefig(path_save)

    plt.close()

    return fig


def joints_movement_plotter(sequence_or_sequences, measure="velocity", domain="time", window_length=7, poly_order=None,
                            nperseg=None, welch_window="hann", audio_or_derivative=None, overlay_audio=False,
                            audio_color="#a102db", align=True, timestamp_start=None, timestamp_end=None, xlim=None,
                            ylim=None, line_width=1.0, color_scheme="default", show_scale=False, show=True,
                            path_save=None, verbosity=1, **kwargs):
    """Plots the distance or velocity across time of the joints, in separate sub-graphs whose localisation roughly
    follows the original body position of the joints.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence_or_sequences: Sequence or list(Sequence)
        One or multiple sequence instances.

    measure: str, optional
        This parameter can take the following values:

        • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
        • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
        • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
        • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
        • For the consecutive distances on the x-axis: ``"dx"`, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
          or ``"x_dist"``.
        • For the consecutive distances on the y-axis: ``"dy"`, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
          or ``"y_dist"``.
        • For the consecutive distances on the z-axis: ``"dz"`, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
          or ``"z_dist"``.
        • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
        • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
        • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
        • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
        • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
        • For the pop: ``"p"``, ``"pop"``, or ``6``.
        • For any derivative of a higher order, set the corresponding integer.

        This value can also be ``"default"`` (default) and will in that case display a sub-selection made of the x, y
        and z coordinates, the consecutive distances, the velocity, and the acceleration.

        It is also possible to add the suffix ``"_abs"`` after a specific measure to plot the absolute values of the
        measure.

    domain: str, optional
        Defines if to plot the movement in the time domain (`"time"`, default) or in the frequency domain
        (`"frequency"`).

    window_length: int, optional
        The length of the window for the Savitzky–Golay filter when calculating a derivative (default: 7). See
        `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
        for more info.

    poly_order: int|None, optional
        The order of the polynomial for the Savitzky–Golay filter. If set on `None`, the polynomial will be set to
        one over the derivative rank. See
        `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
        for more info.

    nperseg: int|None, optional
        Number of samples per segment for the power spectrum density calculation (in case `domain` is set to
        ``"frequency"``). This parameter is passed to `scipy.signal.welch
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html>`_.

    welch_window: str, optional
        The window to use when calculating the power spectrum density (in case `domain` is set to ``"frequency"``).
        This parameter is passed to `scipy.signal.welch
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html>`_.

    audio_or_derivative: Audio, AudioDerivative or None, optional
        An Audio instance, or any of the AudioDerivative child classes (:class:`Envelope`, :class:`Pitch`,
        :class:`Intensity` or :class:`Formant`). If provided, the samples of the object will be plotted in the top-left
        corner.

    overlay_audio: bool, optional
        If set on ``True``, and if audio_or_derivative is not None, the samples of the ``audio_or_derivative`` object
        will be shown on overlay of the different joint velocities.

    audio_color: str, optional
        The color of the audio samples if ``overlay_audio`` is set on ``True`` (default: "#a102db").

    align: bool, optional
        If this parameter is set on ``"True"`` (default), and if the parameter ``sequence_or_sequences`` is a list
        containing more than one sequence instance, the function will try to check if one or more of the sequences
        provided is or are sub-sequences of others. If it is the case, the function will align the timestamps of the
        sequences for the plot. If only one sequence is provided, this parameter is ignored.
        
    timestamp_start: float or None, optional
        If defined, indicates at what timestamp to start to calculate the measure.

    timestamp_end: float or None, optional
        If defined, indicates at what timestamp to finish to calculate the measure.

    xlim: list(int|float)|None, optional
        If defined, indicates the timestamp range of frequency range on the x-axis for all subplots. If not defined,
        the values of xlim will take the values of `timestamp_start` and `timestamp_end` in the time domain,
        or ``0`` and the half of the highest sequence frequency in the frequency domain.

    ylim: list(int|float)|None, optional
        If defined, sets the lower and upper limits of the y-axis for all sub-graphs (e.g. `[0, 1]`). If this parameter
        is a list of lists, each sublist sets the limits for each sub-graph.

    line_width: float, optional
        The width of the plotted lines, in pixels (default: 1.0).

    color_scheme: string or list, optional
        The name of a color scheme or a list of colors to create a gradient. The resulting color gradient will be used
        to color the joints plots depending on their quantity of movement. If set on ``"default"``, the default
        :doc:`color scheme <../appendix/color_schemes>` will be used, with the joints having the highest quantity of
        movement colored red. If a list of colors is set as parameter, the colors can be specified in RGB, RGBA,
        hexadecimal or standard `HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_.
        In the case where multiple sequences are passed as parameter, this parameter should contain a list of colors,
        for each sequence.

    show_scale: bool, optional
        If set on ``True``, shows a colored scale on the left side of the graph.

    show: bool, optional
        If set on `False`, the function does not show the graph. This parameter can be set if the purpose of the
        function is to save the graph in a file, without having to halt the execution of the code when opening a window.

    path_save: str or None optional
        If provided, the function will save the plot as a picture. The path should contain the folder, the name
        file, and one of the following extensions: ``".png"``, ``".jpeg"`` or ``".bmp"``.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict
        Any of the parameters accepted by
        `matplotlib.pyplot.plot <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html>`_.

    Examples
    --------
    >>> sequence = Sequence("Sequences/Anatolê/sequence_02.tsv")
    >>> joints_movement_plotter(sequence, measure="velocity", domain="time", verbosity=0)
    >>> sequence_cj = sequence.correct_jitter(1, 5)
    >>> joints_movement_plotter([sequence, sequence_cj], measure="velocity_abs", domain="time", verbosity=0)
    >>> audio = Audio("Sequences/Anatolê/sequence_02.wav", verbosity=0)
    >>> joints_movement_plotter(sequence_cj, measure="velocity", domain="time", audio_or_derivative=audio,
    ...                         overlay_audio=True, verbosity=0)
    """

    if verbosity > 0:
        if len(sequence_or_sequences) > 1:
            print(f"Plotting the data skeleton for {len(sequence_or_sequences)} sequences...")
            print("\tGetting data...", end=" ")
        else:
            print(f"Plotting the data skeleton for the sequence {sequence_or_sequences[0].get_name()}...")
            print("\tGetting data...", end=" ")

    sequences, timestamps = _prepare_plot_timestamps(sequence_or_sequences, align, verbosity)
    timestamp_start, timestamp_end, xlim = _calculate_plot_limits(sequences, timestamps, domain,
                                                                  timestamp_start, timestamp_end, xlim, verbosity)

    if verbosity > 0:
        print(f"Getting the timestamps between {timestamp_start} s and {timestamp_end} s for each sequence...", end=" ")
        timestamps = [np.array(seq_timestamps)[
                          np.where(np.logical_and(seq_timestamps >= timestamp_start, seq_timestamps <= timestamp_end))]
                      for seq_timestamps in timestamps]
        print("Done.")

    if verbosity > 0:
        print("Checking the validity of the requested measure...", end=" ")

    abs_measure = False
    if measure.endswith("_abs"):
        measure = measure[:-4]
        abs_measure = True

    # Setting the measures on their values
    if measure not in CLEAN_DERIV_NAMES:
        raise InvalidParameterValueException("measures", measure, ["x", "y", "z", "distance_x", "distance_y",
                                                                   "distance_z", "distance", "velocity",
                                                                   "acceleration", "jerk", "snap", "crackle", "pop"])

    measure = CLEAN_DERIV_NAMES[measure]

    if verbosity > 0:
        print("Done.")

    if verbosity > 0:
        print(f"Getting the {measure} for each sequence...", end=" ")

    values = []
    totals = []
    maxima = []
    plot_timestamps = []

    min_value = 0
    max_value = 0

    # For all sequences
    for i in range(len(sequences)):
        sequence = sequences[i]

        if domain == "time":
            values.append(sequence.get_measure(measure, None, timestamp_start, timestamp_end, window_length, poly_order,
                                               abs_measure, verbosity))
            totals.append(
                sequence.get_sum_measure(measure, None, True, timestamp_start, timestamp_end, window_length, poly_order,
                                         True, verbosity))
            min_seq, max_seq = sequence.get_extremum_measure(measure, None, "both", False, timestamp_start,
                                                             timestamp_end, window_length,
                                                             poly_order, abs_measure, verbosity)
            if min_seq < min_value:
                min_value = min_seq
            if max_seq > max_value:
                max_value = max_seq

            plot_timestamps.append(timestamps[i][np.where((timestamps[i] >= xlim[0]) & (timestamps[i] <= xlim[1]))])

        elif domain == "frequency":
            values.append(sequence.get_measure(measure, None, None, None, window_length, poly_order,
                                               abs_measure, verbosity))

            t = []
            for joint_label in values[i]:

                t, values[i][joint_label] = signal.welch(values[i][joint_label], sequence.get_sampling_rate(),
                                                         welch_window, nperseg, scaling="spectrum")

                if np.min(values[i][joint_label]) < min_value:
                    min_value = np.min(values[i][joint_label])
                if np.max(values[i][joint_label]) > max_value:
                    max_value = np.max(values[i][joint_label])

            plot_timestamps.append(t)

    if verbosity > 0:
        print("Done.")
        print("Getting the titles...")

    # Titles
    title_scale = "Sum of the variations"
    if measure in ["x", "y", "z"]:
        title = f"Position on the {measure} coordinate for each joint of the sequence"

    elif measure in ["distance x", "distance y", "distance z"]:
        title = f"Distance travelled on the {measure[-1]} coordinate between poses for each joint of the sequence"

    elif measure == "distance":
        title = f"Distance travelled for each joint of the sequence"

    elif measure in ["velocity", "acceleration", "jerk", "snap", "crackle", "pop"]:
        if abs_measure:
            title = f"Absolute {measure} for each joint of the sequence"
        else:
            title = f"{measure.title()} for each joint of the sequence"

    else:
        raise InvalidParameterValueException("measure", measure, ["x", "y", "z", "distance_x", "distance_y",
                                                                  "distance_z", "distance", "velocity", "acceleration",
                                                                  "jerk", "snap", "crackle", "pop"])

    if len(sequences) > 1:
        title += f" ({len(sequences)} sequences)"
    elif len(sequences) == 1 and sequences[0].get_name() is not None:
        title += " " + str(sequences[0].get_name())

    # We define the plot dictionary
    plot_dictionary = {}

    if verbosity > 0:
        print("Done.")
        print("\tCalculating colors...", end=" ")

    # Determine color depending on global sum
    joints_colors = []
    if domain == "time":
        if len(sequences) == 1:
            joints_colors.append(calculate_colors_by_values(totals[0], color_scheme, type_return="hex",
                                                            include_alpha=False))
        else:
            for s in range(len(sequences)):
                if type(color_scheme) is list:
                    joints_colors.append({joint_label: color_scheme[s % len(color_scheme)]
                                          for joint_label in sequences[s].get_joint_labels()})
                else:
                    joints_colors.append({joint_label: "C" + str(s) for joint_label in
                                          sequences[s].get_joint_labels()})

    else:
        for s in range(len(sequences)):
            joints_colors.append({joint_label: "C" + str(s)
                                  for joint_label in sequences[s].get_joint_labels()})

    if verbosity > 0:
        print("Done.")
        print("\tScaling the audio...", end=" ")

    # Scale the audio
    scaled_audio_or_derivative = []
    if audio_or_derivative is not None and overlay_audio:
        if abs_measure:
            scaled_audio_or_derivative = scale_audio(audio_or_derivative.get_samples(), max_value,
                                                     abs_measure, True, 0)
        else:
            scaled_audio_or_derivative = scale_audio(audio_or_derivative.get_samples(), max_value,
                                                     abs_measure, False, 0)

    if verbosity > 0:
        print("Done.")
        print("\tCreating the sub-graphs...", end=" ")

    for joint_label in sequences[0].get_joint_labels():
        graph = Graph()
        if overlay_audio:
            graph.add_plot(audio_or_derivative.get_timestamps(), scaled_audio_or_derivative, None, line_width,
                           convert_color(audio_color, "hex", False) + "60")

        for s in range(len(sequences)):
            if (len(sequences)) > 1:
                label = sequences[s].get_name()
            else:
                label = None
            start_timestamps = len(plot_timestamps[s]) - len(values[s][joint_label])
            if start_timestamps not in [0, 1]:
                raise Exception("The number of timestamps and the number of values must be equal for plotting.")
            graph.add_plot(plot_timestamps[s][start_timestamps:], values[s][joint_label], None, line_width,
                           joints_colors[s][joint_label], label)
        plot_dictionary[joint_label] = graph

    title_audio = None
    if audio_or_derivative is not None:
        graph = Graph()
        graph.add_plot(audio_or_derivative.get_timestamps(), audio_or_derivative.get_samples(), None, line_width,
                       convert_color(audio_color, "hex", True))
        plot_dictionary["Audio"] = graph
        title_audio = audio_or_derivative.kind

    if verbosity > 0:
        print("Done.")

    return plot_body_graphs(plot_dictionary, min_scale=min_value, max_scale=max_value, show_scale=show_scale,
                            title_scale=title_scale, color_scheme=color_scheme, xlim=xlim, ylim=ylim,
                            title=title, title_audio=title_audio, show=show, path_save=path_save, **kwargs)


def framerate_plotter(sequence_or_sequences, line_width=1.0, line_color="black", show=True, path_save=None, **kwargs):
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

    show: bool, optional
        If set on `False`, the function does not show the graph. This parameter can be set if the purpose of the
        function is to save the graph in a file, without having to halt the execution of the code when opening a window.

    path_save: str or None optional
        If provided, the function will save the plot as a picture. The path should contain the folder, the name
        file, and one of the following extensions: ``".png"``, ``".jpeg"`` or ``".bmp"``.

    **kwargs: dict
        Any of the parameters accepted by
        `matplotlib.pyplot.plot <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html>`_.

    Examples
    --------
    >>> sequence = Sequence("Sequences/Musica/sequence_02.csv", verbosity=0)
    >>> framerate_plotter(sequence)
    >>> sequence_rs = sequence.resample(20, "cubic", verbosity=0)
    >>> framerate_plotter([sequence, sequence_rs])
    """

    # If only one sequence has been provided, we turn it into a list
    if type(sequence_or_sequences) is not list:
        sequence_or_sequences = [sequence_or_sequences]

    # Figure parameters
    sns.set_theme()
    fig = plt.figure()
    plt.rcParams["figure.figsize"] = (12, 6)
    labels = get_difference_paths(*get_objects_names(*sequence_or_sequences))
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
        framerates = sequence.get_sampling_rates()
        timestamps = sequence.get_timestamps()[1:]
        average = np.average(framerates)
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
        plt.plot(timestamps_list[seq], framerates_list[seq], linewidth=line_width, color=line_color, label="Framerate",
                 **kwargs)
        plt.plot(timestamps_list[seq], averages_list[seq], linewidth=line_width, color="#ff0000", label="Average",
                 **kwargs)
        if seq == 0:
            plt.legend(bbox_to_anchor=(0, 1 + i * 0.15), loc="upper left", ncol=2)
        plt.title(labels[seq] + " [Avg: " + format(averages_list[seq][0], '.2f') + "]")

    plt.tight_layout()

    if show:
        plt.show()

    if path_save is not None:
        os.makedirs(op.split(path_save)[0], exist_ok=True)
        plt.savefig(path_save)

    plt.close()

    return fig


# noinspection PyArgumentList
def audio_plotter(audio, filter_below=None, filter_over=None, number_of_formants=3, show=True, path_save=None,
                  verbosity=1):
    """Given an audio instance, plots the samples, filtered envelope, pitch, intensity, formants and spectrogram.

    .. versionadded:: 2.0

    Parameters
    ----------
    audio: Audio
        An Audio instance.

    filter_below: int, float or None, optional
        If not ``None`` nor 0, this value will be provided as the lowest frequency of the band-pass filter.

    filter_over: int, float or None, optional
        If not ``None`` nor 0, this value will be provided as the highest frequency of the band-pass filter.

    number_of_formants: int, optional
        The number of formants to plot (default: 3).

    show: bool, optional
        If set on `False`, the function does not show the graph. This parameter can be set if the purpose of the
        function is to save the graph in a file, without having to halt the execution of the code when opening a window.

    path_save: str or None optional
        If provided, the function will save the plot as a picture. The path should contain the folder, the name
        file, and one of the following extensions: ``".png"``, ``".jpeg"`` or ``".bmp"``.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Warning
    -------
    With non-resampled audio files, this function can take several minutes to compute before being able to plot the
    graphs. It is recommended to perform a downsampling of the audio object before running this function.

    Example
    -------
    >>> audio = Audio("Sequences/Gymnastica/recording_gymnastica.wav", verbosity=0)
    >>> audio_plotter(audio, filter_over=50, verbosity=0)
    """

    if verbosity > 0:
        print("Getting the envelope...", end=" ")
    envelope = audio.get_envelope(filter_over=filter_over, filter_below=filter_below, verbosity=verbosity - 1)
    if verbosity > 0:
        print("Done.")

    if verbosity > 0:
        print("Getting the pitch...", end=" ")
    pitch = audio.get_pitch(filter_over=filter_over, filter_below=filter_below, zeros_as_nan=False,
                            verbosity=verbosity - 1)
    if verbosity > 0:
        print("Done.")

    if verbosity > 0:
        print("Getting the intensity...", end=" ")
    intensity = audio.get_intensity(filter_over=filter_over, filter_below=filter_below, zeros_as_nan=False,
                                    verbosity=verbosity - 1)
    if verbosity > 0:
        print("Done.")

    formants = []
    for f in range(1, number_of_formants + 1):
        if verbosity > 0:
            print(f"Getting the formant f{f}...", end=" ")
        formant = audio.get_formant(f, filter_over=filter_over, filter_below=filter_below, zeros_as_nan=False,
                                    verbosity=verbosity - 1)
        formants.append(formant)
        if verbosity > 0:
            print("Done.")

    if verbosity > 0:
        print("Getting the spectrogram...", end=" ")
    audio_samples = np.array(audio.get_samples(), dtype=np.float64)
    parselmouth_sound = Sound(np.ndarray(np.shape(audio_samples), np.float64, audio_samples), audio.frequency)
    spectrogram = parselmouth_sound.to_spectrogram()
    x, y = spectrogram.x_grid(), spectrogram.y_grid()
    sg_db = 10 * np.log10(spectrogram.values)
    if verbosity > 0:
        print("Done.")

    sns.set_theme()
    fig = plt.figure()

    plt.subplot(3, 2, 1)
    plt.plot(audio.timestamps, audio.samples)
    plt.title("Original audio")

    plt.subplot(3, 2, 2)
    plt.plot(envelope.timestamps, envelope.samples)
    plt.title("Envelope")

    plt.subplot(3, 2, 3)
    plt.plot(pitch.timestamps, pitch.samples)
    plt.title("Pitch")

    plt.subplot(3, 2, 4)
    plt.plot(intensity.timestamps, intensity.samples)
    plt.title("Intensity")

    plt.subplot(3, 2, 5)
    for i in range(len(formants)):
        plt.plot(formants[i].timestamps, formants[i].samples, label="f" + str(i + 1))

    plt.legend()
    plt.title("Formants")

    plt.subplot(3, 2, 6)
    plt.pcolormesh(x, y, sg_db, vmin=sg_db.max() - 70, cmap='afmhot')
    plt.ylim([spectrogram.ymin, spectrogram.ymax])
    plt.xlabel("time [s]")
    plt.ylabel("frequency [Hz]")
    plt.title("Spectrogram")

    if show:
        plt.show()

    if path_save is not None:
        os.makedirs(op.split(path_save)[0], exist_ok=True)
        plt.savefig(path_save)

    plt.close()

    return fig

def plot_body_graphs(plot_dictionary, joint_layout="auto", title=None, min_scale=None, max_scale=None, show_scale=False,
                     title_scale=None, xlim=None, ylim=None, shaded_error_bars=True, horizontal_lines=None,
                     horizontal_lines_colors="red", horizontal_lines_styles="--", horizontal_shades=None,
                     horizontal_shades_colors="red", horizontal_shades_alphas=0.3, alpha_shade=0.4,
                     signif_marker=None, signif_marker_values=None, signif_marker_size=10, signif_marker_color="black",
                     signif_marker_offset=0.02, color_scheme="default", title_audio="Audio", full_screen=False,
                     show=True, path_save=None):
    """Creates multiple subplots placed so that each joint is roughly placed where it is located on the body. The
    values of each subplot are taken from the parameter ``plot_dictionary``, and the positions from the layout
    differ between Kinect and Kualisys systems.

    .. versionadded:: 2.0

    Parameters
    ----------
    plot_dictionary: dict(str: Graph)
        A dictionary containing the title of the subgraphs as keys, and Graph objects as elements.

    joint_layout: str, optional
        Defines the layout to use for the subplots of the joints: ``"kinect"``, ``"qualisys"``/``"kualisys"``, or the
        path to a file containing a custom layout.  If set on ``"auto"`` (default), the function will automatically
        assign the layout depending on if the joint label ``"Chest"`` is among the keys of the ``plot_dictionary``.

        The joint layouts are a grid of 7 × 5 subplots for Kinect, and 13 × 7 subplots for Qualisys. The corresponding
        spots for each joint are loaded from ``"res/kinect_joints_subplot_layout.txt"`` and
        ``"res/kualisys_joints_subplot_layout.txt"``.

    title: str or None, optional
        The title to display on top of the plot.

    min_scale: float or None, optional
        The minimum value to set on the y-axis, for all the elements in the ``plot_dictionary`` that match joint keys
        (i.e., except from the subplot under the ``"Audio"`` key). If set on None (default), the minimum value will be
        the overall minimum value from the ``plot_dictionary``, with the subgraph ``"Audio"`` excluded.

    max_scale: float or None, optional
        The maximum value to set on the y-axis, for all the elements in the ``plot_dictionary`` that match joint keys
        (i.e., except from the subplot under the ``"Audio"`` key). If set on None (default), the maximum value will be
        the overall minimum value from the ``plot_dictionary``, with the subgraph ``"Audio"`` excluded.

    show_scale: bool, optional
        If set on ``True``, shows a colored scale on the right side of the graph.

    title_scale: str or None, optional
        Defines a title to give to the scale, if ``show_scale`` is set on ``True``.

    xlim: list(float, float)|None, optional
        If set, defines the lower and upper limits of the x-axis of the sub-graphs (default: None).

    ylim: list(float, float)|None, optional
        If set, defines the lower and upper limits of the y-axis of the sub-graphs (default: None).

    shaded_error_bars: bool, optional
        Shows shaded error bars for each plot if the standard deviation is part of the plot_dictionary. Default: True.

    horizontal_lines: list(float) | float | None, optional
        If set, adds one or more horizontal lines to the plot (e.g. to signify significance). Default: None.

    horizontal_lines_colors: list(color) | color, optional
        The color or colors to apply to each horizontal line. If a list is provided, the length of the list must be
        equal to the length of ``horizontal_lines``. If a single color is provided, it will be applied to all lines.

    horizontal_lines_styles: list(str) | str, optional
        The line style to apply to each horizontal line. If a list is provided, the length of the list must be equal
        to the length of ``horizontal_lines``. If a single line style is provided, it will be applied to all lines.
        See `linestyles <https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html>`_ for more info.

    horizontal_shades: list(tuple(float, float)) | (float, float) | None, optional
        If set, adds one or more horizontal shades to the plot (e.g. to signify significance). Each shade must be two
        values, starting from the lowest. Setting ``"inf"`` or ``"-inf"`` will change set the color until the
        corresponding vertical limit of the graph. Default: None.

    horizontal_shades_colors: list(color) | color, optional
        The color or colors to apply to each horizontal shade. If a list is provided, the length of the list must be
        equal to the length of ``horizontal_shades``. If a single color is provided, it will be applied to all shades.

    horizontal_shades_alphas: list(str) | str, optional
        The alpha value to apply to each horizontal shade. If a list is provided, the length of the list must be equal
        to the length of ``horizontal_shades``. If a single alpha value is provided, it will be applied to all shades.

    alpha_shade: float, optional
        The alpha value for the color of the shaded error bars. Default: 0.4.

    signif_marker: str, optional
        Marker(s) to display for significant values. If a single character is given (default: ``"*"``), it will be
        repeated according to the number of thresholds in ``signif_alpha`` (e.g., ``"*"``, ``"**"``, ``"***"``
        for three levels). Alternatively, a list of symbols can be provided, in which case its length must match the
        number of alpha values.
        
    signif_marker_values: tuple(float, float) | list(tuple(float, float)) | None, optional
        A list of tuples containing the lower and upper bounds of the thresholds for the ``signif_marker`` parameter.
        If a value is strictly over or below a bound, set numpy.inf or -numpy.inf as the other bound. This parameter
        must be set if ``signif_marker`` is set on ``True``.

    signif_marker_size: float|int, optional
        The size of the significance marker(s). Default: 10.

    signif_marker_color: str|list(str), optional
        The color(s) of the significance marker(s). Default: ``"black"``.

    signif_marker_offset: float, optional
        The vertical offset of the significance marker(s), as a fraction of the height of the plot. Default: 0.02.

    color_scheme: str or list, optional
        The color scheme to use for the color scale. This color scheme should be coherent with the colors defined in
        the ``plot_dictionary``.

    title_audio: str or None, optional
        The title to give to the sub-plot that matches the key ``"Audio"`` from the ``plot_dictionary``. This sub-plot
        is located in the top-left corner of the plot, and is not scaled the same way as the other plots. By default,
        the title of this sub-plot is ``"Audio"``, but this parameter allows to change the title to put the name of an
        AudioDerivative type, such as ``"Envelope"`` or ``"Pitch"``, for example.

    full_screen: bool, optional
        If set on `True`, shows the figure in full screen. By default, set on `False`.

    show: bool, optional
        If set on `False`, the function does not show the graph. This parameter can be set if the purpose of the
        function is to save the graph in a file, without having to halt the execution of the code when opening a window.

    path_save: str or None
        If not `None`, the function saves the obtained graph at the given path.

    Example
    -------
    >>> plot_dictionary = {}
    >>> plot_dictionary["Head"] = Graph()
    >>> plot_dictionary["Head"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "red", "x=y")
    >>> plot_dictionary["HandRight"] = Graph()
    >>> plot_dictionary["HandRight"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "green", "x=y")
    >>> plot_dictionary["HandLeft"] = Graph()
    >>> plot_dictionary["HandLeft"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "blue", "x=y")
    >>> plot_dictionary["HandLeft"].add_plot(np.linspace(0, 10, 11), np.linspace(10, 0, 11), None, 2, "orange", "y=x")
    >>> plot_body_graphs(plot_dictionary, joint_layout="auto")
    """

    # Getting the joint layout
    if joint_layout == "auto":
        if "Chest" in plot_dictionary.keys():
            joint_layout = "qualisys"
        else:
            joint_layout = "kinect"
    joints_positions = load_joints_subplot_layout(joint_layout)

    # Figure parameters
    sns.set_theme(font_scale=0.8)
    plt.rcParams["figure.figsize"] = (12, 9)

    # plt.rcParams["font.size"] = 7
    if joint_layout == "kinect":
        rows, cols = 7, 5
    else:
        rows, cols = 13, 7
    fig, axes = plt.subplots(nrows=rows, ncols=cols)  # constrained_layout=True)
    if title is not None:
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.93, wspace=0.3, hspace=0.8)
        fig.suptitle(title, fontsize="x-large", fontweight="bold")
    else:
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.97, top=0.97, wspace=0.3, hspace=0.8)

    if full_screen:
        manager = plt.get_current_fig_manager()
        manager.full_screen_toggle()

    # Get min and max values
    min_value, max_value = get_min_max_values_from_plot_dictionary(plot_dictionary, keys_to_exclude=["Audio"],
                                                                   xlim=xlim)

    if min_scale is not None:
        min_value = min_scale
    if isinstance(max_scale, (int, float)):
        max_value = max_scale

    # Horizontal lines
    if horizontal_lines is not None:
        if not isinstance(horizontal_lines, (tuple, list)):
            horizontal_lines = (horizontal_lines,)
        if min_scale is None and min(horizontal_lines) < min_value:
            min_value = min(horizontal_lines)
        if max_scale is None and max(horizontal_lines) > max_value:
            max_value = max(horizontal_lines)

        if horizontal_lines_colors is None or isinstance(horizontal_lines_colors, str):
            horizontal_lines_colors = [horizontal_lines_colors] * len(horizontal_lines)
        if len(horizontal_lines_colors) != len(horizontal_lines):
            raise ValueError(f"The length of the horizontal_lines_colors list ({horizontal_lines_colors}) must be equal "
                             f"to the length of horizontal_lines ({horizontal_lines}).")
        horizontal_lines_colors = convert_colors(horizontal_lines_colors, "HEX")

        if horizontal_lines_styles is None or isinstance(horizontal_lines_styles, str):
            horizontal_lines_styles = [horizontal_lines_styles] * len(horizontal_lines)
        if len(horizontal_lines_styles) != len(horizontal_lines):
            raise ValueError(f"The length of the horizontal_lines_styles list ({horizontal_lines_styles}) must be equal "
                             f"to the length of horizontal_lines ({horizontal_lines}).")

    # Horizontal shades
    if horizontal_shades is not None:
        if not isinstance(horizontal_shades, list):
            horizontal_shades = [horizontal_shades]
        for s in range(len(horizontal_shades)):
            if not isinstance(horizontal_shades[s], (tuple, list)):
                raise ValueError("Error: each value in horizontal_shades must be a list or a tuple.")
            if horizontal_shades[s][0] == -np.inf:
                horizontal_shades[s] = (min_value, horizontal_shades[s][1])
            if horizontal_shades[s][1] == np.inf:
                horizontal_shades[s] = (horizontal_shades[s][0], max_value)

        if horizontal_shades_colors is None or isinstance(horizontal_shades_colors, str):
            horizontal_shades_colors = [horizontal_shades_colors] * len(horizontal_shades)
        if len(horizontal_shades_colors) != len(horizontal_shades):
            raise ValueError(f"The length of the horizontal_shades_colors list ({horizontal_shades_colors}) must be equal "
                             f"to the length of horizontal_shades ({horizontal_shades}).")

        if horizontal_shades_alphas is None or isinstance(horizontal_shades_alphas, (int, float)):
            horizontal_shades_alphas = [horizontal_shades_alphas] * len(horizontal_shades)
        if len(horizontal_shades_alphas) != len(horizontal_shades):
            raise ValueError(f"The length of the horizontal_shades_alphas list ({horizontal_shades_alphas}) must be equal "
                             f"to the length of horizontal_shades ({horizontal_shades}).")

        horizontal_shades_colors = convert_colors(horizontal_shades_colors, "HEX", False)

    # Markers
    if signif_marker is not None:
        if isinstance(signif_marker, str):
            signif_marker = [signif_marker]
        if not isinstance(signif_marker_color, list):
            signif_marker_color = [signif_marker_color]
        signif_marker_color = convert_colors(signif_marker_color, "HEX", False)

        if len(signif_marker_values) != len(signif_marker):
            if len(signif_marker) == 1:
                signif_marker = [signif_marker[0] * i for i in range(len(signif_marker_values), 0, -1)]
            else:
                raise ValueError(f"The length of the parameter signif_marker_value ({len(signif_marker_values)}) must "
                                 f"be equal to the length of signif_marker ({len(signif_marker)}).")

        if len(signif_marker) != 1 and len(signif_marker_color) == 1:
            signif_marker_color = signif_marker_color * len(signif_marker)
        elif len(signif_marker) != len(signif_marker_color):
            raise ValueError(f"The length of the signif_marker list ({len(signif_marker)}) must be equal to the "
                             f"length of signif_marker_color ({len(signif_marker_color)}).")

        if signif_marker_values is None:
            raise ValueError("The parameter signif_marker_value must be set if signif_marker is set.")
        elif isinstance(signif_marker_values, tuple):
            signif_marker_values = [signif_marker_values]
        elif not isinstance(signif_marker_values, list):
            raise ValueError("The parameter signif_marker_values must be a tuple or a list.")

    # print(signif_marker, signif_marker_values, signif_marker_color)

    # Plot the subplots
    for key in plot_dictionary.keys():
        plt.subplot(rows, cols, joints_positions[key])
        if key != "Audio":  # We want to scale everything apart from the audio
            plt.ylim([min_value, max_value])
            plt.title(key)
        else:
            plt.title(title_audio)
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)

        if key != "Audio":
            if horizontal_shades is not None:
                for line, color, alpha in zip(horizontal_shades, horizontal_shades_colors, horizontal_shades_alphas):
                    plt.axhspan(line[0], line[1], color=color, alpha=alpha)

            if horizontal_lines is not None:
                for line, color, linestyle in zip(horizontal_lines, horizontal_lines_colors, horizontal_lines_styles):
                    plt.axhline(y=line, color=color, linestyle=linestyle)

        for subplot in plot_dictionary[key].plots:
            line, = plt.plot(subplot.x, subplot.y, linewidth=subplot.line_width, color=subplot.color, label=subplot.label)
            if signif_marker is not None and key != "Audio":
                for x, y in zip(subplot.x, subplot.y):
                    for marker, v, color in zip(signif_marker, signif_marker_values, signif_marker_color):
                        if v[0] < y < v[1]:
                            plt.text(x, y + signif_marker_offset, marker, fontsize=signif_marker_size, color=color,
                                     ha="center", va="bottom")
                            break

            if subplot.sd is not None and shaded_error_bars:
                plt.fill_between(subplot.x, subplot.y - subplot.sd, subplot.y + subplot.sd,
                                 alpha=alpha_shade, facecolor=line.get_color())

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
    color_list = convert_colors(color_list, "hex", include_alpha=False)

    # Show the scale if max_scale is not None
    if show_scale:
        plt.subplots_adjust(left=0.03, bottom=0.03, right=0.9, top=0.97, wspace=0.3, hspace=0.6)
        cmap = colors.ListedColormap(color_list)
        norm = colors.Normalize(vmin=min_scale, vmax=max_scale)
        cbax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbax, orientation='vertical', label=title_scale)

    # Build a figure-level legend from ALL subplots
    all_handles = []
    all_labels = []
    for ax in fig.get_axes():
        h, l = ax.get_legend_handles_labels()
        if h:  # skip axes with nothing labeled (e.g., empty slots or colorbar)
            all_handles.extend(h)
            all_labels.extend(l)

    # Deduplicate while preserving order
    seen = set()
    uniq_handles, uniq_labels = [], []
    for h, l in zip(all_handles, all_labels):
        if l and l not in seen:
            seen.add(l)
            uniq_handles.append(h)
            uniq_labels.append(l)

    # Unified legend
    fig.legend(uniq_handles, uniq_labels, loc="upper right", bbox_to_anchor=(0.98, 0.98), frameon=True, ncol=1)

    if path_save is not None:
        os.makedirs(op.split(path_save)[0], exist_ok=True)
        plt.savefig(path_save)

    if show:
        plt.show()

    plt.close()

    return fig


def plot_silhouette(plot_dictionary, joint_layout="auto", title=None, title_silhouette=None,
                    scale_silhouette=0.9, min_scale="auto", max_scale="auto", show_scale=True, title_scale=None,
                    color_scheme="default", color_background="white", color_silhouette="black",
                    pixels_between_silhouettes=100, path_font=None, font_size=1, resolution=0.5,
                    full_screen=False, show=True, path_save=None, verbosity=1):
    """Plots one or multiple silhouettes with circles representing the different joints, colored according to their
    values in the ``plot_dictionary``. Passing the mouse on the different joints shows, in the bottom right corner, the
    value associated with the joint the mouse is on.

    .. versionadded:: 2.0

    Parameters
    ----------
    plot_dictionary: dict(str: float|np.array)
        A dictionary containing the title of the subgraphs as keys, and values as elements. The number of silhouettes
        displayed will depend on the number of values in each value of the plot dictionary: if there is only one value,
        one silhouette is displayed; if the value is an array, the function will display as many silhouettes as the
        size of the arrays.

    joint_layout: str, optional
        Defines the layout to use for the subplots of the joints: ``"kinect"`` or ``"qualisys"``/``"kualisys"``. If
        set on ``"auto"`` (default), the function will automatically assign the layout depending on if the joint label
        ``"Chest"`` is among the keys of the ``plot_dictionary``. In order to create a personalized layout, it is
        possible to click on the figure to print in the console a specific position. Pressing the CTRL key at the same
        time allows to display a test circle where the mouse is located, to give an idea of the render.

        The joint layouts are a grid of 7 × 5 sub-plots for Kinect, and 13 × 7 subplots for Qualisys. The corresponding
        spot for each joint are loaded from ``"res/kinect_joints_subplot_layout.txt"`` and
        ``"res/kualisys_joints_subplot_layout.txt"``.

    title: str or None, optional
        The title to display on top of the plot.

    title_silhouette: str | list | None (optional)
        The title to set for each silhouette. If a list is provided, the length must be equal to the number of
        elements in each value of the ``plot_dictionary``.

    scale_silhouette: float (optional)
        The scale of each silhouette in the window. If set on 1, the silhouette will take the total height of the
        window. The default value is 0.9, in order to leave place for titles.

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
          :doc:`../appendix/color_schemes` (default: ``"default"``).
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

    pixels_between_silhouettes: int, optional
        The amount of pixels separating two silhouettes, if more than one silhouette is shown (default: 100).

    path_font: str or None, optional
        If set, defines the path to any TTF or OTF font. This font will be used for the title, the silhouette titles
        and the scale titles and values. If set on `None` (default), the built-in font junction-bold.otf will be
        used.

    font_size: int | tuple, optional
        The size of the font for the title, the silhouette titles and the scale. The default value is 1, which is an
        arbitrary value that is equal to 4% of the height of the window. This parameter can be set on a tuple of three
        values ``(a, b, c)`` where ``α`` is the size of the title, ``b`` the size of the silhouette titles, and ``c``
        the size of the scale titles and values.

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

    show: bool, optional
        If set on `False`, the function does not show the graph. This parameter can be set if the purpose of the
        function is to save the graph in a file, without having to halt the execution of the code when opening a window.

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

    Example
    -------
    >>> plot_dictionary = {"Head": 0.1, "HandRight": 0.48, "HandLeft": 0.88}
    >>> plot_silhouette(plot_dictionary, joint_layout="auto", title="Coherence", min_scale=0, max_scale=1,
    ...                 show_scale=True, title_scale="Coherence scale (A.U.)", color_scheme="horizon",
    ...                 color_background="black", color_silhouette="#303030", verbosity=0)
    """

    pygame.init()

    if verbosity > 0:
        print("Setting up the resolution...", end=" ")

    # Setting up the resolution
    info = pygame.display.Info()
    if resolution is None:
        resolution = (info.current_w, info.current_h)
    elif isinstance(resolution, numbers.Number):
        resolution = (int(info.current_w * resolution), int(info.current_h * resolution))

    # Setting up the fullscreen mode
    if not show:
        pygame.display.set_mode((1, 1))
        window = pygame.Surface(resolution)
    else:
        if full_screen:
            window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        else:
            window = pygame.display.set_mode(resolution)

    # Scale variables to the resolution
    ratio_w = resolution[0] / 1920
    ratio_h = resolution[1] / 1080

    if verbosity > 0:
        print("Window resolution: " + str(resolution))
        print("Load the silhouette...", end=" ")

    # Determine how many silhouettes
    number_of_silhouettes = 1
    for key in plot_dictionary:
        if isinstance(plot_dictionary[key], numbers.Number) and key != "Audio":
            plot_dictionary[key] = np.array([plot_dictionary[key]])
        if key != "Audio":
            number_of_silhouettes = len(plot_dictionary[key])

    # Load silhouette picture, color it and resize it
    silhouette = pygame.image.load(SILHOUETTE_PATH)
    color_background = convert_color(color_background, "rgb", False)

    if color_background != (255, 255, 255):
        silhouette.fill(color_background, special_flags=pygame.BLEND_RGBA_MIN)

    # Calculate silhouette size using `size_silhouette` ratio of vertical resolution
    silhouette_ratio = silhouette.get_width() / silhouette.get_height()
    silhouette_height = int(resolution[1] * scale_silhouette)
    silhouette_width = int(silhouette_height * silhouette_ratio)
    silhouette = pygame.transform.scale(silhouette, (silhouette_width, silhouette_height))

    # Compute x and y offset to center it horizontally and vertically
    silhouette_x = (resolution[0] // 2 - (silhouette_width * number_of_silhouettes +
                                          (pixels_between_silhouettes * (number_of_silhouettes - 1))) // 2)
    silhouette_y = (resolution[1] - silhouette_height) // 2

    # Create the surfaces around the silhouette
    width_surface_side = (resolution[0] - (silhouette.get_width() * number_of_silhouettes) -
                          (pixels_between_silhouettes * (number_of_silhouettes - 1))) / 2
    surface_horizontal = pygame.Surface((resolution[0], resolution[1] * (1 - scale_silhouette) / 2 + 1))

    surface_left = pygame.Surface((max(0, width_surface_side + 1), resolution[1]))
    surface_between = pygame.Surface((pixels_between_silhouettes + 1, resolution[1]))
    surface_right = pygame.Surface((max(0, width_surface_side), resolution[1]))
    surface_horizontal.fill(color_background)
    surface_left.fill(color_background)
    surface_between.fill(color_background)
    surface_right.fill(color_background)

    if verbosity > 0:
        print("Done.")
        print("Load the fonts and colors...", end=" ")

    # Font and colors
    colors = convert_colors(color_scheme, "rgb", True)  # Color scheme
    color_silhouette = convert_color(color_silhouette, "rgb", False)
    luminance = color_background[0] * 0.2126 + color_background[1] * 0.7152 + color_background[2] * 0.0722

    if isinstance(font_size, numbers.Number):
        font_size = (font_size, font_size, font_size)

    if path_font is not None:
        font_title = pygame.font.Font(path_font, int(resolution[1] * 0.04 * font_size[0]))
        font_silhouette_title = pygame.font.Font(path_font, int(resolution[1] * 0.04 * font_size[1]))
        font_scale = pygame.font.Font(path_font, int(resolution[1] * 0.04 * font_size[2]))
    else:
        font_title = pygame.font.Font(DEFAULT_FONT_PATH, int(resolution[1] * 0.04 * font_size[0]))
        font_silhouette_title = pygame.font.Font(DEFAULT_FONT_PATH, int(resolution[1] * 0.04 * font_size[1]))
        font_scale = pygame.font.Font(DEFAULT_FONT_PATH, int(resolution[1] * 0.04 * font_size[2]))

    if luminance > 0.5:
        font_color = convert_color("black", "rgb", False)
    else:
        font_color = convert_color("white", "rgb", False)

    if verbosity > 0:
        print("Done.")

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
    circle_positions = {}

    for joint in plot_dictionary.keys():
        if joint in joints_positions.keys():
            circles[joint] = []
            values_to_plot[joint] = []
            circle_positions[joint] = []
            for value in plot_dictionary[joint]:
                ratio = (value - min_scale) / (max_scale - min_scale)  # Get the ratio of the max value
                color_in = calculate_color_ratio(colors, ratio)  # Turn that into a color
                # Transparent color of the circle edge for the gradient
                color_edge = (color_in[0], color_in[1], color_in[2], 0)
                values_to_plot[joint].append(font_silhouette_title.render(str(joint) + ": " + str(round(value, 2)),
                                                         True, font_color))

                radius = joints_positions[joint][2] * ratio_h * scale_silhouette
                pos_x = joints_positions[joint][0] * ratio_h * scale_silhouette
                pos_y = joints_positions[joint][1] * ratio_h * scale_silhouette
                absolute_pos_y = pos_y + silhouette_y - radius

                for i in range(number_of_silhouettes):
                    absolute_pos_x = pos_x + silhouette_x + i * (silhouette_width + pixels_between_silhouettes) - radius
                    circle_positions[joint].append((absolute_pos_x, absolute_pos_y))

                circles[joint].append(gradients.radial(int(radius), color_in, color_edge))

    # Color scale on the side of the graph
    scale_height = 500
    scale_width = 50
    start_scale_x = 50
    start_scale_y = 540 - scale_height // 2
    sep = scale_height // (len(colors) - 1)

    grad = []
    for i in range(len(colors) - 1):
        grad.append(gradients.vertical((int(scale_width * ratio_w),
                                        int(((scale_height // (len(colors) - 1)) + 1) * ratio_h)),
                                       colors[len(colors) - i - 1], colors[len(colors) - i - 2]))

    scale_top = font_scale.render(str(round(max_scale, 2)), True, font_color)
    scale_bottom = font_scale.render(str(round(min_scale, 2)), True, font_color)
    if title_scale is None:
        title_scale = ""
    scale_title = font_scale.render(str(title_scale), True, font_color)
    scale_title = pygame.transform.rotate(scale_title, 90)

    # Title
    title_plot = None
    if title is not None:
        title_plot = font_title.render(str(title), True, font_color)
        title_pos = (resolution[0] // 2 - title_plot.get_width() // 2,
                     (resolution[1] * ((1 - scale_silhouette) / 2)) / 2 - (title_plot.get_height() / 2))

    # Silhouette titles
    silhouette_titles = []
    silhouette_titles_positions = []

    if title_silhouette is not None:
        if type(title_silhouette) is str:
            title_silhouette = [title_silhouette]
        if len(title_silhouette) != number_of_silhouettes:
            raise ValueError(f"The number of silhouette titles ({len(title_silhouette)}) must be equal to the number "
                             f"of silhouettes ({number_of_silhouettes}).")
        for i in range(len(title_silhouette)):
            silhouette_titles.append(font_silhouette_title.render(str(title_silhouette[i]), True, font_color))
            pos_x = (silhouette_x + silhouette_width // 2 - silhouette_titles[i].get_width() // 2 +
                     i * (silhouette_width + pixels_between_silhouettes))
            pos_y = resolution[1] * (1 - (1 - scale_silhouette) / 4) - silhouette_titles[i].get_height() / 2
            silhouette_titles_positions.append((pos_x, pos_y))

    # Mouse
    pygame.mouse.set_visible(True)  # Allows the mouse to be visible
    mouse_sensitivity = 50 * ratio_h * scale_silhouette # Radius around the center in which the mouse position will be detected as inside

    place_circle = False
    circle_position = None
    color_in = calculate_color_ratio(colors, 1)  # Turn that into a color
    color_edge = (color_in[0], color_in[1], color_in[2], 0)  # Transparent color of the circle edge for the gradient
    circle_radius = int(150 * ratio_w)
    circle = gradients.radial(circle_radius, color_in, color_edge)
    run = True  # Loop variable
    img = None

    # Program loop
    while run:

        window.fill(color_silhouette)  # Set background to black

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
                print("Click position: " + str(mouse_coord))
                mouse_x = 0
                for i in range(number_of_silhouettes):
                    start_x = silhouette_x + (i * (silhouette.get_width() + pixels_between_silhouettes))
                    end_x = start_x + silhouette.get_width()
                    if start_x < mouse_coord[0] < end_x:
                        print(f"Click in silhouette {i + 1}")
                        mouse_x = mouse_coord[0] - start_x
                        print("Scaled position in the figure: " + str((mouse_x / ratio_w, mouse_coord[1] / ratio_h)))
                if place_circle:
                    circle_position = (mouse_x / ratio_w, mouse_coord[1] / ratio_h)

        for joint in order_joints:
            if joint in plot_dictionary.keys():
                for i in range(number_of_silhouettes):
                    if not np.isnan(plot_dictionary[joint][i]):
                        window.blit(circles[joint][i], circle_positions[joint][i])

        if circle_position is not None:
            for i in range(number_of_silhouettes):
                circle_x = silhouette_x + circle_position[0] * ratio_w + (i * (silhouette.get_width() +
                                                                     pixels_between_silhouettes)) - circle_radius
                window.blit(circle, (circle_x, circle_position[1] * ratio_h - circle_radius))

        for i in range(number_of_silhouettes):
            window.blit(silhouette, (silhouette_x + i * (silhouette_width + pixels_between_silhouettes), silhouette_y))

        window.blit(surface_horizontal, (0, 0))
        window.blit(surface_horizontal, (0, resolution[1] * (1 - ((1 - scale_silhouette) / 2)) - 1))
        window.blit(surface_left, (0, 0))
        window.blit(surface_right, (resolution[0] - width_surface_side, 0))

        for i in range(number_of_silhouettes - 1):
            window.blit(surface_between, (width_surface_side + ((i + 1) * silhouette.get_width()) + (i *
                                          pixels_between_silhouettes), 0))

        if title is not None:
            window.blit(title_plot, title_pos)

        if title_silhouette is not None:
            for i in range(number_of_silhouettes):
                window.blit(silhouette_titles[i], silhouette_titles_positions[i])

        to_blit = []
        for joint in order_joints:
            if joint in plot_dictionary.keys():
                for i in range(number_of_silhouettes):
                    pos_x = circle_positions[joint][i][0] + joints_positions[joint][2] * ratio_h
                    pos_y = circle_positions[joint][i][1] + joints_positions[joint][2] * ratio_h

                    if (pos_x - mouse_sensitivity < mouse_coord[0] < pos_x + mouse_sensitivity and
                        pos_y - mouse_sensitivity < mouse_coord[1] < pos_y + mouse_sensitivity):
                        to_blit.append((joint, i))

        height = 0
        for joint, i in to_blit:
            window.blit(values_to_plot[joint][i], (resolution[0] - values_to_plot[joint][i].get_width() - 5,
                                                resolution[1] - values_to_plot[joint][i].get_height() - 5 - height))
            height += values_to_plot[joint][i].get_height() + 5

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

        if show is False:
            run = False
            img = pygame.surfarray.array3d(window)

    pygame.quit()

    return img


def _plot_components(pca_or_ica, components, joint_labels, title, selected_components=None, show=True, path_save=None,
                     verbosity=1, **kwargs):
    """Plots the components of a PCA or an ICA.

    .. versionadded:: 2.0

    Parameters
    ----------
    pca_or_ica: numpy.ndarray
        The components returned by a Principal Component Analysis.

    components: numpy.ndarray
        The components attribute of the PCA, containing the directions of maximum variance in the data for each feature
        (the joint labels).

    joint_labels: list(str)
        The labels of each feature.

    title: str
        The title of the figure.

    selected_components: int, list(int) or None
        If set, plots only the selected component(s). The components start at index 0.

    show: bool, optional
        If set on `False`, the function does not show the graph. This parameter can be set if the purpose of the
        function is to save the graph in a file, without having to halt the execution of the code when opening a window.

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
    n_components = np.shape(components)[0]
    max_components = np.max(components)

    if selected_components is None:
        selected_components = [i for i in range(n_components)]
    elif type(selected_components) == int:
        selected_components = [selected_components]

    fig, ax = plt.subplots(len(selected_components), 2, width_ratios=[1, 4], constrained_layout=True)
    fig.suptitle(title)

    for i in range(len(selected_components)):
        dict_plot = {joint_labels[j]: components[selected_components[i]][j] for j in range(len(joint_labels))}
        img = plot_silhouette(dict_plot, show=False, max_scale=max_components, resolution=(300, 300),
                              verbosity=verbosity, **kwargs)
        img = np.transpose(img, (1, 0, 2))
        ax[i][0].imshow(img)
        ax[i][0].xaxis.set_visible(False)
        plt.setp(ax[i][0].get_yticklabels(), visible=False)
        ax[i][0].set_yticks([])
        ax[i][0].set_ylabel(f"Component {selected_components[i]}")
        ax[i][1].plot(pca_or_ica[:, i])

    if path_save is not None:
        os.makedirs(op.split(path_save)[0], exist_ok=True)
        plt.savefig(path_save)

    if show:
        plt.show()

    plt.close()
    return fig


def _prepare_plot_timestamps(sequence_or_sequences, align, verbosity):
    """
    Returns the timestamps, aligned or not, from one or multiple Sequence instances.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence_or_sequences: Sequence or list(Sequence)
        One or multiple sequence instances.

    align: bool, optional
        If this parameter is set on ``"True"`` (default), and if the parameter ``sequence_or_sequences`` is a list
        containing more than one sequence instance, the function will try to check if one or more of the sequences
        provided is or are sub-sequences of others. If it is the case, the function will align the timestamps of the
        sequences for the plot. If only one sequence is provided, this parameter is ignored.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Returns
    -------
    list(Sequence)
        A list containing the Sequence instances passed as parameter. If only one Sequence was passed, a list
        containing only this Sequence is returned.
    list(numpy.array(float))
        A list of timestamps from each of the Sequence instances (in the same order as they were passed as parameters).
    """

    # Turn to list
    if type(sequence_or_sequences) is not list:
        sequence_or_sequences = [sequence_or_sequences]

    # Aligning sequences
    if align and len(sequence_or_sequences) > 1:
        if verbosity > 0:
            print("Trying to align sequences...", end=" ")
        timestamps = align_multiple_sequences(*sequence_or_sequences, verbosity=verbosity)
        if verbosity > 0:
            print("Done.")
    else:
        if verbosity > 0:
            print("Getting the timestamps...", end=" ")
        timestamps = []
        for sequence in sequence_or_sequences:
            timestamps.append(np.array(sequence.get_timestamps()))
        if verbosity > 0:
            print("Done.")

    return sequence_or_sequences, timestamps


def _calculate_plot_limits(sequences, timestamps, domain, timestamp_start, timestamp_end, xlim, verbosity):
    """Given a list of sequences and their timestamps, sets:

        * The starting and ending timestamps for the measure calculations, if they weren't defined.
        * The limit on the x-axis, if it wasn't manually defined.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequences: list(Sequence)
        A list of Sequence instances.

    timestamps: list(np.ndarray)
        A list of timestamps from the Sequence instances.

    domain: str, optional
        Defines if to plot the movement in the time domain (`"time"`, default) or in the frequency domain
        (`"frequency"`).

    timestamp_start: float or None, optional
        If defined, indicates at what timestamp to start to calculate the measure.

    timestamp_end: float or None, optional
        If defined, indicates at what timestamp to finish to calculate the measure.

    xlim: list(float|None, float|None)
        The limits of the plot on the x-axis. If set, this parameter will be returned as is. Otherwise, the calculation
        of the limit of the x-axis depends on the domain:

        • If domain is set on ``"time"``, the limits are set on the timestamp_start and timestamp_end values.
        • If domain is set on ``"frequency"``, the limits are set on 0 and half of the highest Sequence frequency.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    # Handling timestamp_start and timestamp_end
    if timestamp_start is None:
        if verbosity > 0:
            print("Defining timestamp_start...", end=" ")
        for timestamps_sequence in timestamps:
            if timestamp_start is None or np.min(timestamps_sequence) < timestamp_start:
                timestamp_start = np.min(timestamps_sequence)
    if verbosity > 0:
        print(f"timestamp_start set on {timestamp_start}.")

    if timestamp_end is None:
        if verbosity > 0:
            print("Defining timestamp_end...", end=" ")
        for timestamps_sequence in timestamps:
            if timestamp_end is None or np.max(timestamps_sequence) > timestamp_end:
                timestamp_end = np.max(timestamps_sequence)
    if verbosity > 0:
        print(f"timestamp_end set on {timestamp_end}.")

    # Handling xlim
    if xlim is None:
        xlim = [None, None]

    if xlim[0] is None:
        if domain == "frequency":
            xlim[0] = 0
        else:
            xlim[0] = timestamp_start
    if verbosity > 0:
        print(f"Lower limit of the x-axis set on {xlim[0]}.")

    if xlim[1] is None:
        if domain == "frequency":
            xlim[1] = 0
            for sequence in sequences:
                if sequence.get_sampling_rate() / 2 > xlim[1]:
                    xlim[1] = sequence.get_sampling_rate() / 2
        else:
            xlim[1] = timestamp_end
    if verbosity > 1:
        print(f"Upper limit of the x-axis set on {xlim[1]}.")

    return timestamp_start, timestamp_end, xlim
