"""These functions allow to find significant relationships between movements, or between movements and audio properties.
"""
from classes.exceptions import ModuleNotFoundException
from classes.graph_element import Graph
from plot_functions import plot_silhouette, plot_body_graphs


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
                         title=None, width_line=1, color_line="blue", verbosity=1):

    try:
        from scipy.signal import coherence
    except ImportError:
        raise ModuleNotFoundException("scipy", "calculate the coherence")

    try:
        import numpy as np
    except ImportError:
        raise ModuleNotFoundException("numpy", "calculate the coherence")

    plot_dictionary = {}

    for joint_label in experiment.get_joint_labels():
        dataframe = experiment.get_dataframe(sequence_metric, joint_label, audio_metric)

        if group is not None:
            dataframe = dataframe.loc[dataframe["Group"] == group]
        if condition is not None:
            dataframe = dataframe.loc[dataframe["Condition"] == condition]
        if subjects is not None:
            dataframe = dataframe.loc[dataframe["Subject"].isin(subjects)]

        frequencies, coherence_values = coherence(dataframe["SequenceMetric"], dataframe["AudioMetric"],
                                                  fs=sampling_frequency, nperseg=length_segment)

        if specific_frequency is not None:
            plot_dictionary[joint_label] = coherence_values[frequencies == specific_frequency]
        else:
            graph = Graph()
            graph.add_plot(frequencies, coherence_values, width_line, color_line)
            plot_dictionary[joint_label] = graph

    plot_body_graphs(plot_dictionary, title=title)