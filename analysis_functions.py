"""These functions allow to find significant relationships between movements, or between movements and audio properties.
"""
from plot_functions import plot_silhouette


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

