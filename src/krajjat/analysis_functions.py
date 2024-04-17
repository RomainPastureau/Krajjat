"""These functions allow to find significant relationships between movements, or between movements and audio properties.
"""
import numpy as np

from krajjat.classes.exceptions import ModuleNotFoundException
from krajjat.classes.graph_element import Graph
from krajjat.plot_functions import plot_silhouette, plot_body_graphs
from krajjat.tool_functions import convert_colors


def correlation_with_audio(experiment, group=None, condition=None, subjects=None, sequence_metric="distance",
                           audio_metric="envelope", title=None, color_scheme="default", color_background="white",
                           color_silhouette="black", resolution=0.5, full_screen=False, path_save=None, verbosity=1):

    import pingouin as pg
    stats = {}

    dataframe = experiment.get_dataframe(sequence_metric, audio_metric)

    if group is not None:
        dataframe = dataframe.loc[dataframe["Group"] == group]
    if condition is not None:
        dataframe = dataframe.loc[dataframe["Condition"] == condition]
    if subjects is not None:
        dataframe = dataframe.loc[dataframe["Subject"].isin(subjects)]

    for joint_label in experiment.get_joint_labels():

        dataframe_joint_label = dataframe.loc[dataframe["Joint label"] == joint_label]

        #print(dataframe_joint_label)

        #try:
        #output = pg.rm_corr(data=dataframe_joint_label, x=sequence_metric.capitalize(), y=audio_metric.capitalize(),
        #                    subject="Subject")
        output = pg.corr(x = dataframe_joint_label["Velocity"], y = dataframe_joint_label["Envelope"])

        print(output)
        print(joint_label, output.values[0][1])
        stats[joint_label] = np.abs(output.values[0][1])

        #except AssertionError:
        #    stats[joint_label] = 0

    plot_silhouette(stats, title=title, color_scheme=color_scheme, color_background=color_background,
                    color_silhouette=color_silhouette, resolution=resolution, full_screen=full_screen,
                    path_save=path_save, verbosity=verbosity)

def coherence_with_audio(experiment, group=None, condition=None, subjects=None, sequence_metric="distance",
                         audio_metric="envelope", sampling_frequency=8, length_segment=32, specific_frequency=None,
                         title=None, width_line=1, color_line=None, verbosity=1):
    """Calculates and plots the coherence between one metric derived from the sequences, and one metric derived from
    the corresponding audio clips.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment: Experiment
        An Experiment instance, containing the full dataset to be analyzed.

    group: str or None
        If specified, the analysis will focus exclusively on subjects whose
        :attr:`~krajjat.classes.subject.Subject.group` attribute matches the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), subjects from all groups will be considered.

    condition: str or None
        If specified, the analysis will focus exclusively on sequences whose
        :attr:`~krajjat.classes.sequence.Sequence.condition` attribute matches the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), all sequences will be considered.

    subjects: list(str), str or None
        If specified, the analysis will focus exclusively on subjects whose
        :attr:`~krajjat.classes.subject.Subject.name` attribute matches the value(s) provided for this parameter.
        This parameter can be a string (for one subject), or a list of strings (for multiple subjects).
        Otherwise, if this parameter is set on `None`, all subjects will be considered. This parameter can be combined
        with the parameter ``group`` (default), to perform the analysis on certain subjects from a certain group.

    sequence_metric: str
        The sequence


    """

    # Define the colors of the lines if they are not defined in the parameters
    if color_line is None:
        color_line = ["b", "r"]

    # Import scipy and numpy
    try:
        from scipy.signal import coherence
    except ImportError:
        raise ModuleNotFoundException("scipy", "calculate the coherence")

    try:
        import numpy as np
    except ImportError:
        raise ModuleNotFoundException("numpy", "calculate the coherence")

    # Create the plot dictionary
    plot_dictionary = {}

    if verbosity > 1:
        print("Calculating the coherence for each joint label...")

    # Get the full dataframe
    dataframe = experiment.get_dataframe(sequence_metric, audio_metric, audio_filter_above=sampling_frequency,
                                         audio_resampling_frequency=sampling_frequency)

    for joint_label in experiment.get_joint_labels():

        if verbosity > 1:
            print("\t"+joint_label)

        dataframe_joint = dataframe.loc[dataframe["Joint label"] == joint_label]

        if group is not None:
            dataframe_joint = dataframe_joint.loc[dataframe["Group"] == group]
        if condition is not None:
            dataframe_joint = dataframe_joint.loc[dataframe["Condition"] == condition]
        if subjects is not None:
            dataframe_joint = dataframe_joint.loc[dataframe["Subject"].isin(subjects)]

        values_audio = dataframe_joint[audio_metric.title()]
        values_audio_randperm = np.random.permutation(values_audio)

        frequencies, coherence_values = coherence(dataframe_joint[sequence_metric.title()], values_audio,
                                                  fs=sampling_frequency, nperseg=length_segment)

        frequencies_randperm, coherence_values_randperm = coherence(dataframe_joint[sequence_metric.title()],
                                                                    values_audio_randperm, fs=sampling_frequency,
                                                                    nperseg=length_segment)

        if type(color_line) is not list:
            color_line = [color_line]
        color_line = convert_colors(color_line, "hex")

        if specific_frequency is not None:
            plot_dictionary[joint_label] = coherence_values[frequencies == specific_frequency]

        else:
            graph = Graph()
            graph.add_plot(frequencies, coherence_values, width_line, color_line[0%len(color_line)])
            graph.add_plot(frequencies_randperm, coherence_values_randperm, width_line, color_line[1%len(color_line)])
            plot_dictionary[joint_label] = graph

    if specific_frequency is not None:
        plot_silhouette(plot_dictionary)

    else:
        plot_body_graphs(plot_dictionary, title=title)