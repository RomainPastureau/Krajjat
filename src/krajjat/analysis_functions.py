"""These functions allow to find significant relationships between movements, or between movements and audio properties.
"""
from krajjat.classes.exceptions import ModuleNotFoundException
from krajjat.classes.graph_element import Graph
from krajjat.plot_functions import plot_silhouette, plot_body_graphs
from krajjat.tool_functions import convert_colors


def correlation_with_audio(experiment, group=None, condition=None, subjects=None, sequence_metric="distance",
                           audio_metric="envelope", title=None, color_scheme="default", color_background="white",
                           color_silhouette="black", resolution=0.5, full_screen=False, path_save=None, verbosity=1):

    import pingouin as pg
    stats = {}

    for joint_label in experiment.get_joint_labels():
        dataframe = experiment.get_dataframe(sequence_metric, joint_label, audio_metric)

        if group is not None:
            dataframe = dataframe.loc[dataframe["Group"] == group]
        if condition is not None:
            dataframe = dataframe.loc[dataframe["Condition"] == condition]
        if subjects is not None:
            dataframe = dataframe.loc[dataframe["Subject"].isin(subjects)]

        try:
            output = pg.rm_corr(data=dataframe, x="SequenceMetric", y="AudioMetric", subject="Subject")
            stats[joint_label] = output.at["rm_corr", "r"]

        except AssertionError:
            stats[joint_label] = 0

    plot_silhouette(stats, title=title, color_scheme=color_scheme, color_background=color_background,
                    color_silhouette=color_silhouette, resolution=resolution, full_screen=full_screen,
                    path_save=path_save, verbosity=verbosity)

def coherence_with_audio(experiment, group=None, condition=None, subjects=None, sequence_metric="distance",
                         audio_metric="envelope", sampling_frequency=8, length_segment=32, specific_frequency=None,
                         title=None, width_line=1, color_line=None, verbosity=1):

    if color_line is None:
        color_line = ["b", "r"]

    try:
        from scipy.signal import coherence
    except ImportError:
        raise ModuleNotFoundException("scipy", "calculate the coherence")

    try:
        import numpy as np
    except ImportError:
        raise ModuleNotFoundException("numpy", "calculate the coherence")

    plot_dictionary = {}

    if verbosity > 1:
        print("Calculating the coherence for each joint label...")

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