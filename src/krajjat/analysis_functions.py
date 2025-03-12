"""These functions allow to find significant relationships between movements, or between movements and audio properties.
"""
import numpy as np
import scipy
from matplotlib import pyplot as plt

from krajjat.classes.exceptions import ModuleNotFoundException
from krajjat.classes.experiment import Experiment
from krajjat.classes.graph_element import Graph, GraphPlot
from krajjat.plot_functions import plot_silhouette, plot_body_graphs, _plot_components
from krajjat.tool_functions import convert_colors, read_pandas_dataframe


def power_spectrum(experiment_or_dataframe, group=None, condition=None, subjects=None, trials=None, series=None,
                   average="subject", sequence_measure="distance", audio_measure="envelope", sampling_frequency=50,
                   method="fft", target="envelope", specific_frequency=None, width_line=1, color_line=None,
                   verbosity=1, **kwargs):

    try:
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundException("pandas", "calculate the correlation")

    # Get the full dataframe
    if verbosity > 0:
        print("Preparing the dataframe...")
    dataframe = _make_dataframe(experiment_or_dataframe, sequence_measure, audio_measure, sampling_frequency,
                                verbosity)
    dataframe = _get_dataframe_from_requirements(dataframe, group, condition, subjects, trials)
    if verbosity > 0:
        print("Done.")

    # Create the plot dictionary
    plot_dictionary = {}

    # Get the series of interest
    if series is not None:
        series_values = list(dataframe[series].unique())
    else:
        series_values = ["Full dataset"]

    # Get the subjects/trials
    if average == "subject":
        if type(subjects) == str:
            individuals = [subjects]
        elif subjects is None:
            individuals = dataframe["subject"].unique()
        else:
            individuals = subjects
    elif average == "trial":
        if type(trials) == str:
            individuals = [trials]
        elif subjects is None:
            individuals = dataframe["trial"].unique()
        else:
            individuals = trials
    else:
        individuals = ["All"]

    # Get the unique joint labels
    joint_labels = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()

    power_spectra = {}
    frequencies = []

    # For each series
    for series_value in series_values:

        # We get the corresponding dataframe
        if series_value == "Full dataset":
            dataframe_series_value = dataframe
        else:
            dataframe_series_value = dataframe.loc[dataframe[series] == series_value]

        if verbosity > 1:
            print("\t" + series_value)

        power_spectrum_series = {}

        # For each subject/trial
        for individual in individuals:
            if individual == "All":
                dataframe_individual = dataframe_series_value
            else:
                dataframe_individual = dataframe_series_value.loc[dataframe_series_value[average] == individual]

            if verbosity > 1:
                print("\t\t" + individual)

            power_spectrum_ind = {}

            for joint_label in joint_labels:

                if verbosity > 1:
                    print("\t\t\t" + joint_label)

                dataframe_joint = dataframe_individual.loc[dataframe_individual["label"] == joint_label]
                values = dataframe_joint["value"]

                if method == "fft":
                    power_spectrum = np.abs(np.fft.fft(values)) ** 2
                    frequencies = np.fft.fftfreq(values.size, 1/sampling_frequency)
                    # idx = np.argsort(frequencies)
                elif method == "welch":
                    frequencies, power_spectrum = scipy.signal.welch(values, fs=sampling_frequency)
                    # for i in range(len(frequencies)):
                    #     if i != 0:
                    #         power_spectrum[i] = power_spectrum[i]/(1/frequencies[i])
                    # power_spectrum = [power_spectrum[i]/(1/frequencies[i]) for i in range(len(power_spectrum))]
                else:
                    raise Exception("""Method must be "fft" or "welch".""")

                power_spectrum_ind[joint_label] = power_spectrum

            power_spectrum_series[individual] = power_spectrum_ind

        power_spectra[series_value] = power_spectrum_series

    print(power_spectra)

    if color_line is not None:
        if type(color_line) is not list:
            color_line = [color_line]
        color_line = convert_colors(color_line, "hex")

    # Calculate the averages
    average_power_spectra = {}
    sd_power_spectra = {}

    # For each series
    for series_value in series_values:
        print(series_value)

        average_power_spectra_series_value = {}
        sd_power_spectra_series_value = {}

        # For each joint
        for joint_label in joint_labels:
            print("\t"+joint_label)
            average_power_spectrum_joint = []
            sd_power_spectrum_joint = []

            # For each frequency
            for f in range(len(frequencies)):
                print("\t\t"+str(f))
                power_spectra_joint_frequency = []

                for individual in individuals:
                    print("\t\t\t"+individual)
                    if len(power_spectra[series_value][individual][joint_label]) > 0:
                        power_spectra_joint_frequency.append(power_spectra[series_value][individual][joint_label][f])
                    else:
                        power_spectra_joint_frequency.append(np.nan)

                average_power_spectrum_joint.append(np.mean(power_spectra_joint_frequency))
                sd_power_spectrum_joint.append(np.std(power_spectra_joint_frequency))

            average_power_spectra_series_value[joint_label] = average_power_spectrum_joint
            sd_power_spectra_series_value[joint_label] = sd_power_spectrum_joint

            if specific_frequency is not None:
                plot_dictionary[joint_label] = power_spectra[frequencies == specific_frequency]

            else:
                if color_line is not None:
                    color = color_line[0 % len(color_line)]
                else:
                    color = None
                graph_plot = GraphPlot(frequencies, average_power_spectra_series_value[joint_label],
                                       sd_power_spectra_series_value[joint_label],
                                       width_line, color, series_value)
                if joint_label not in plot_dictionary.keys():
                    plot_dictionary[joint_label] = Graph()
                plot_dictionary[joint_label].add_graph_plot(graph_plot)

        average_power_spectra[series_value] = average_power_spectra_series_value
        sd_power_spectra[series_value] = sd_power_spectra_series_value

    if specific_frequency is not None:
        plot_silhouette(plot_dictionary, **kwargs)

    else:
        plot_body_graphs(plot_dictionary, **kwargs)

    return frequencies, average_power_spectra, sd_power_spectra

def correlation(experiment_or_dataframe, group=None, condition=None, subjects=None, trials=None, series=None,
                correlation_type="corr", average="subject", include_randperm="whole", sequence_measure="distance",
                correlation_with="envelope", sampling_frequency=50, verbosity=1, **kwargs):
    """Calculates and plots the correlation between one metric derived from the sequences, and the same metric from a
    given joint, or another metric derived from the corresponding audio clips.

    .. versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        · A :class:`Experiment` instance, containing the full dataset to be analyzed.
        · A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        · The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        · A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

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

    trials: dict(str: list(str)), list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be:
            · A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows to discard or select specific trials for individual subjects.
            · A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            · The name of a single trial. This will select the given trial for all subjects.
            · `None` (default). In that case, all trials will be considered.
        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and trials is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]`, the analysis will run on the trials that intersect both requirements, i.e.
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    series: str, optional
        Defines the series that divide the data for comparison. This value can take any of the column names from the
        dataframe (apart from the values indicated in sequence_measure and audio_measure). For instance, if `group` is
        selected, the correlation will be calculated and plotted for each individual group of the dataframe.

    correlation_type: str, optional
        Can be either `"corr"` (default, uses
        `pingouin_corr <https://pingouin-stats.org/build/html/generated/pingouin.corr.html>`_) or `"rm_corr"` (uses
        `pingouin_corr <https://pingouin-stats.org/build/html/generated/pingouin.rm_corr.html>`_).

    average: str or None, optional
        Defines if an average correlation is returned. This parameter can be:
            • ``"subject"``: the correlation is calculated for each subject and averaged across all subjects.
            • ``"trial"``: the correlation is calculated for each trial and averaged across all trials.
            • ``None``: the correlation is calculated for the whole dataset.

    include_randperm: bool or str, optional
        Defines if to include the calculation of the correlation for the randomly permuted data. This parameter can be:
            • ``False``: in that case, no correlation on a random permutation of the data will be calculated.
            • ``"whole"``: calculates a random permutation on the whole data.
            • ``"individual"``: calculates a random permutation for each series.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    correlation_with: str, optional
        The measure used for the correlation. It can be either a joint label (in that case, the coherence uses the
        sequence measure of that joint), or an audio measure, among:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            In the case where the value is an audio value, this parameter will be used to generate a dataframe if the
            parameter `experiment_or_dataframe` is an Experiment instance.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, used to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance, and to perform the coherence.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    try:
        import pingouin as pg
    except ImportError:
        raise ModuleNotFoundException("pingouin", "calculate the correlation")

    try:
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundException("pandas", "calculate the correlation")

    # Get the full dataframe
    if verbosity > 0:
        print("Preparing the dataframe...")

    dataframe = _make_dataframe(experiment_or_dataframe, sequence_measure, correlation_with, sampling_frequency,
                                verbosity)
    dataframe = _get_dataframe_from_requirements(dataframe, group, condition, subjects, trials)

    if verbosity > 0:
        print("Done.")

    # Create the plot dictionary
    plot_dictionary = {}

    # Get the series of interest
    if series is not None:
        series_values = list(dataframe[series].unique())
    else:
        series_values = ["Full dataset"]

    # Get if to calculate the random permutation
    if include_randperm == "whole":
        series_values.append("Full dataset (randomly permuted)")
    elif include_randperm == "individual":
        for s in range(len(series_values)):
            series_values.append(series_values[s] + "(randomly permuted)")

    # Get the subjects/trials
    if average == "subject":
        if type(subjects) == str:
            individuals = [subjects]
        elif subjects is None:
            individuals = dataframe["subject"].unique()
        else:
            individuals = subjects
    elif average == "trial":
        if type(trials) == str:
            individuals = [trials]
        elif subjects is None:
            individuals = dataframe["trial"].unique()
        else:
            individuals = trials
    else:
        individuals = ["All"]

    # Get the unique joint labels
    joint_labels = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()

    correlation_values = {}

    if verbosity > 1:
        print("Calculating the correlation...")

    # For each series
    for series_value in series_values:

        # We get the corresponding dataframe
        value = series_value
        if series_value.endswith(" (randomly permuted)"):
            value = series_value.replace(" (randomly permuted)", "")

        if value == "Full dataset":
            dataframe_series_value = dataframe
        else:
            dataframe_series_value = dataframe.loc[dataframe[series] == value]

        if verbosity > 1:
            print("\t" + series_value)

        correlation_values_series = {}

        if correlation_type == "corr":

            # For each subject/trial
            for individual in individuals:
                if individual == "All":
                    dataframe_individual = dataframe_series_value
                else:
                    dataframe_individual = dataframe_series_value.loc[dataframe_series_value[average] == individual]

                if verbosity > 1:
                    print("\t\t" + individual)

                correlation_values_ind = {}

                for joint_label in joint_labels:

                    if verbosity > 1:
                        print("\t\t\t" + joint_label)

                    dataframe_joint = dataframe_individual.loc[dataframe_individual["label"] == joint_label]
                    dataframe_joint = dataframe_joint.copy()

                    if correlation_with in ["audio", "envelope", "intensity", "pitch", "f1", "f2", "f3", "f4", "f5"]:
                        values_to_correlate = dataframe_individual.loc[dataframe_individual["measure"] ==
                                                                       correlation_with]
                        values_to_correlate = pd.merge(values_to_correlate, dataframe_joint[["subject", "trial",
                                                                                             "timestamp"]],
                                                    on=["subject", "trial", "timestamp"], how="inner")["value"]

                        if series_value.endswith(" (randomly permuted)"):
                            values_to_correlate = np.random.permutation(values_to_correlate)

                        dataframe_joint["correlation_with"] = values_to_correlate

                    elif correlation_with in joint_labels:
                        values_to_correlate = dataframe_individual.loc[dataframe_individual["label"] ==
                                                                    correlation_with]["value"]
                        if series_value.endswith(" (randomly permuted)"):
                            values_to_correlate = np.random.permutation(values_to_correlate)

                        dataframe_joint["correlation_with"] = values_to_correlate

                    else:
                        raise Exception("Please select a correct value for the parameter correlation_with.")

                    try:
                        output = pg.corr(x=dataframe_joint["value"], y=dataframe_joint["correlation_with"])
                        correlation_values_joint = np.abs(output.values[0][1])
                    except (ValueError, AssertionError):
                        correlation_values_joint = np.nan

                    correlation_values_ind[joint_label] = correlation_values_joint

                correlation_values_series[individual] = correlation_values_ind

            correlation_values[series_value] = correlation_values_series

        elif correlation_type == "rm_corr":

            for joint_label in joint_labels:

                if verbosity > 1:
                    print("\t\t" + joint_label)

                dataframe_joint = dataframe_series_value.loc[dataframe_series_value["label"] == joint_label]
                dataframe_joint = dataframe_joint.copy()

                if correlation_with in ["audio", "envelope", "intensity", "pitch", "f1", "f2", "f3", "f4", "f5"]:
                    values_to_correlate = dataframe_series_value.loc[dataframe_series_value["measure"] ==
                                                                     correlation_with]
                    values_to_correlate = pd.merge(values_to_correlate,
                                                   dataframe_joint[["subject", "trial", "timestamp"]],
                                                   on=["subject", "trial", "timestamp"], how="inner")["value"]

                    if series_value.endswith(" (randomly permuted)"):
                        values_to_correlate = np.random.permutation(values_to_correlate)

                    dataframe_joint["correlation_with"] = values_to_correlate

                elif correlation_with in joint_labels:
                    values_to_correlate = dataframe_series_value.loc[dataframe_series_value["label"] ==
                                                                correlation_with]["value"]
                    if series_value.endswith(" (randomly permuted)"):
                        values_to_correlate = np.random.permutation(values_to_correlate)

                    dataframe_joint["correlation_with"] = values_to_correlate

                else:
                    raise Exception("Please select a correct value for the parameter correlation_with.")

                try:
                    output = pg.rm_corr(data=dataframe_joint, x="value", y="correlation_with", subject="subject")
                    correlation_values_joint = np.abs(output.r)
                except (ValueError, AssertionError):
                    correlation_values_joint = np.nan

                correlation_values_series[joint_label] = correlation_values_joint

            correlation_values[series_value] = correlation_values_series

    # Calculate the averages
    average_correlation = {}
    sd_correlation = {}

    max_value = 0

    # For each series
    for series_value in series_values:

        average_correlation_series_value = {}
        sd_correlation_series_value = {}

        # For each joint
        for joint_label in joint_labels:

            correlation_values_joint = []

            if correlation_type == "corr":
                for individual in individuals:
                    correlation_values_joint.append(correlation_values[series_value][individual][joint_label])
            elif correlation_type == "rm_corr":
                correlation_values_joint.append(correlation_values[series_value][joint_label])

            average_correlation_series_value[joint_label] = np.mean(correlation_values_joint)
            sd_correlation_series_value[joint_label] = np.std(correlation_values_joint)

            plot_dictionary[joint_label] = average_correlation_series_value[joint_label]
            if average_correlation_series_value[joint_label] > max_value:
                max_value = average_correlation_series_value[joint_label]

        average_correlation[series_value] = average_correlation_series_value
        sd_correlation[series_value] = sd_correlation_series_value

        plot_silhouette(plot_dictionary, title=series_value, max_scale=max_value, verbosity=verbosity, **kwargs)

    return average_correlation, sd_correlation


def coherence(experiment_or_dataframe, group=None, condition=None, subjects=None, trials=None, series=None,
              average="subject", include_randperm="whole", sequence_measure="distance", coherence_with="envelope",
              sampling_frequency=10, step_segments=0.25, specific_frequency=None, width_line=1, color_line=None,
              random_seed=42, verbosity=1, **kwargs):
    """Calculates and plots the coherence between one metric derived from the sequences, and the same metric from a
    given joint, or another metric derived from the corresponding audio clips.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        · A :class:`Experiment` instance, containing the full dataset to be analyzed.
        · A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        · The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        · A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

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

    trials: dict(str: list(str)), list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be:
            · A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows to discard or select specific trials for individual subjects.
            · A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            · The name of a single trial. This will select the given trial for all subjects.
            · `None` (default). In that case, all trials will be considered.
        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and trials is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]`, the analysis will run on the trials that intersect both requirements, i.e.
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    series: str, optional
        Defines the series that divide the data for comparison. This value can take any of the column names from the
        dataframe (apart from the values indicated in sequence_measure and audio_measure). For instance, if `group` is
        selected, the coherence will be calculated and plotted for each individual group of the dataframe.

    average: str or None, optional
        Defines if an average coherence is returned. This parameter can be:
            • ``"subject"``: the coherence is calculated for each subject and averaged across all subjects.
            • ``"trial"``: the coherence is calculated for each trial and averaged across all trials.
            • ``None``: the coherence is calculated for the whole dataset.

    include_randperm: bool or str, optional
        Defines if to include the calculation of the coherence for the randomly permuted data. This parameter can be:
            • ``False``: in that case, no coherence on a random permutation of the data will be calculated.
            • ``"whole"``: calculates a random permutation on the whole data.
            • ``"individual"``: calculates a random permutation for each series.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    coherence_with: str, optional
        The measure used for the coherence. It can be either a joint label (in that case, the coherence uses the
        sequence measure of that joint), or an audio measure, among:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            In the case where the value is an audio value, this parameter will be used to generate a dataframe if the
            parameter `experiment_or_dataframe` is an Experiment instance.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, used to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance, and to perform the coherence.

    step_segments: int or float, optional
        Defines how large each frequency segment will be for the analysis. If set on 0.25 (default), the coherence
        will be calculated at intervals of 0.25 Hz.

    specific_frequency: int or float, optional
        If specified, the function will return the coherence values for the specified frequency alone, and will display
        a silhouette plot instead of a body graph.

    random_seed: int or None, optional
        Defines a random seed (default: 42) for Numpy, in order to get reproducible results when generating a randomly
        permuted array.

    color_line: list or None, optional
        A list containing the colors for the different variables of interest. If the number of colors is inferior to
        the plotted series, the colors loop through the list.

    width_line: int or float, optional
        Defines the width of the plotted lines (default: 1).

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: optional
        Any parameter accepted by either :func:`plot_functions.plot_silhouette` or
        :func:`plot_functions.plot_body_graphs`.

    Returns
    -------
    np.ndarray(float)
        A list of all the frequencies at which the coherence was computed.
    dict(str: np.ndarray(float))
        A dictionary containing joint labels as keys, and coherence averages (or raw coherence, if no average was
        requested) as values.
    dict(str: np.ndarray(float))
        A dictionary containing the standard deviations matching the averages from the previous one. If no average was
        requested, this dictionary will only contain zeros.
    """

    # Import scipy, numpy and pandas
    try:
        from scipy import signal
    except ImportError:
        raise ModuleNotFoundException("scipy", "calculate the coherence")

    try:
        import numpy as np
    except ImportError:
        raise ModuleNotFoundException("numpy", "calculate the coherence")

    try:
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundException("pandas", "calculate the coherence")

    # Set the random seed
    if random_seed is not None:
        np.random.seed(random_seed)

    # Get the full dataframe
    if verbosity > 0:
        print("Preparing the dataframe...")
    dataframe = _make_dataframe(experiment_or_dataframe, sequence_measure, coherence_with, sampling_frequency,
                                verbosity)
    dataframe = _get_dataframe_from_requirements(dataframe, group, condition, subjects, trials)
    if verbosity > 0:
        print("Done.")

    # Create the plot dictionary
    plot_dictionary = {}

    # Get the series of interest
    if series is not None:
        series_values = list(dataframe[series].unique())
    else:
        series_values = ["Full dataset"]

    # Get if to calculate the random permutation
    if include_randperm == "whole":
        series_values.append("Full dataset (randomly permuted)")
    elif include_randperm == "individual":
        for s in range(len(series_values)):
            series_values.append(series_values[s] + "(randomly permuted)")

    # Get the subjects/trials
    if average == "subject":
        if type(subjects) == str:
            individuals = [subjects]
        elif subjects is None:
            individuals = dataframe["subject"].unique()
        else:
            individuals = subjects
    elif average == "trial":
        if type(trials) == str:
            individuals = [trials]
        elif subjects is None:
            individuals = dataframe["trial"].unique()
        else:
            individuals = trials
    else:
        individuals = ["All"]

    # Get the unique joint labels
    joint_labels = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()

    frequencies = None
    coherence_values = {}
    nperseg = sampling_frequency / step_segments

    if verbosity > 1:
        print("Calculating the coherence...")

    # For each series
    for series_value in series_values:

        # We get the corresponding dataframe
        value = series_value
        if series_value.endswith(" (randomly permuted)"):
            value = series_value.replace(" (randomly permuted)", "")

        if value == "Full dataset":
            dataframe_series_value = dataframe
        else:
            dataframe_series_value = dataframe.loc[dataframe[series] == value]

        if verbosity > 1:
            print("\t" + series_value)

        coherence_values_series = {}

        # For each subject/trial
        for individual in individuals:
            if individual == "All":
                dataframe_individual = dataframe_series_value
            else:
                dataframe_individual = dataframe_series_value.loc[dataframe_series_value[average] == individual]

            if verbosity > 1:
                print("\t\t" + individual)

            coherence_values_ind = {}

            for joint_label in joint_labels:

                if verbosity > 1:
                    print("\t\t\t" + joint_label)

                dataframe_joint = dataframe_individual.loc[dataframe_individual["label"] == joint_label]

                if coherence_with in ["audio", "envelope", "intensity", "pitch", "f1", "f2", "f3", "f4", "f5"]:
                    values_to_cohere = dataframe_individual.loc[dataframe_individual["measure"] == coherence_with]
                    values_to_cohere = pd.merge(values_to_cohere, dataframe_joint[["subject", "trial", "timestamp"]],
                                                on=["subject", "trial", "timestamp"], how="inner")["value"]

                    if series_value.endswith(" (randomly permuted)"):
                        values_to_cohere = np.random.permutation(values_to_cohere)
                elif coherence_with in joint_labels:
                    values_to_cohere = dataframe_individual.loc[dataframe_individual["label"] ==
                                                                coherence_with]["value"]
                    if series_value.endswith(" (randomly permuted)"):
                        values_to_cohere = np.random.permutation(values_to_cohere)
                else:
                    raise Exception("Please select a correct value for the parameter coherence_with.")

                if values_to_cohere.shape[0] == 0 and dataframe_joint["value"].shape[0] != 0:
                    raise Exception(f"No value with the requested measure ({coherence_with}) has been found in the "
                                    f"dataframe")

                # print(dataframe_joint["value"])
                # print(values_to_cohere)

                frequencies_joint, coherence_values_joint = signal.coherence(dataframe_joint["value"],
                                                                             values_to_cohere,
                                                                             fs=sampling_frequency,
                                                                             nperseg=nperseg)

                if len(coherence_values_joint) == 0:
                    coherence_values_joint = np.tile(np.nan, int(nperseg // 2 + 1))

                if frequencies is None:
                    frequencies = frequencies_joint

                coherence_values_ind[joint_label] = coherence_values_joint

            coherence_values_series[individual] = coherence_values_ind

        coherence_values[series_value] = coherence_values_series

    # print(coherence_values)

    if color_line is not None:
        if type(color_line) is not list:
            color_line = [color_line]
        color_line = convert_colors(color_line, "hex")

    # Calculate the averages
    average_coherence = {}
    sd_coherence = {}

    # For each series
    for series_value in series_values:

        average_coherence_series_value = {}
        sd_coherence_series_value = {}

        # For each joint
        for joint_label in joint_labels:
            average_coherence_joint = []
            sd_coherence_joint = []

            # For each frequency
            for f in range(len(frequencies)):
                coherence_values_joint_frequency = []

                for individual in individuals:
                    coherence_values_joint_frequency.append(coherence_values[series_value][individual][joint_label][f])

                average_coherence_joint.append(np.mean(coherence_values_joint_frequency))
                sd_coherence_joint.append(np.std(coherence_values_joint_frequency))

            average_coherence_series_value[joint_label] = average_coherence_joint
            sd_coherence_series_value[joint_label] = sd_coherence_joint

            if specific_frequency is not None:
                plot_dictionary[joint_label] = coherence_values[frequencies == specific_frequency]

            else:
                if color_line is not None:
                    color = color_line[0 % len(color_line)]
                else:
                    color = None
                graph_plot = GraphPlot(frequencies, average_coherence_series_value[joint_label],
                                       sd_coherence_series_value[joint_label],
                                       width_line, color, series_value)
                if joint_label not in plot_dictionary.keys():
                    plot_dictionary[joint_label] = Graph()
                plot_dictionary[joint_label].add_graph_plot(graph_plot)

        average_coherence[series_value] = average_coherence_series_value
        sd_coherence[series_value] = sd_coherence_series_value

    if specific_frequency is not None:
        plot_silhouette(plot_dictionary, **kwargs)

    else:
        plot_body_graphs(plot_dictionary, **kwargs)

    return frequencies, average_coherence, sd_coherence


def pca(experiment_or_dataframe, n_components, group=None, condition=None, subjects=None, trials=None,
        sequence_measure="distance", audio_measure="envelope", include_audio=False, sampling_frequency=50,
        show_graph=True, selected_components=None, nan_behaviour="ignore", verbosity=1):
    """Performs a principal component analysis (PCA) on the measures from the experiment, reducing the dimensionality
    of the data. Each joint_label is used as a feature for the PCA, and, if specified, the audio measure too.
    Relies on the PCA function from
    `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`_.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        · A :class:`Experiment` instance, containing the full dataset to be analyzed.
        · A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        · The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        · A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    n_components: int, optional
        The number of components to generate from the PCA.

    group: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.subject.Subject.group` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), subjects from all groups will be considered.

    condition: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.condition` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), all trials will be considered.

    subjects: list(str), str or None
        If specified, the analysis will discard the subjects whose
        :attr:`~krajjat.classes.subject.Subject.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be a string (for one subject), or a list of strings (for multiple subjects).
        Otherwise, if this parameter is set on `None`, all subjects will be considered. This parameter can be combined
        with the parameter ``group`` (default), to perform the analysis on certain subjects from a certain group.

    trials: dict(str: list(str)), list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be:
            · A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows to discard or select specific trials for individual subjects.
            · A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            · The name of a single trial. This will select the given trial for all subjects.
            · `None` (default). In that case, all trials will be considered.
        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and trials is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]`, the analysis will run on the trials that intersect both requirements, i.e.
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    audio_measure: str, optional
        The measure used for each audio instance, can be either:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the audio data in the dataframe.

    include_audio: bool, optional
        If set on `True`, includes the audio channel as one of the features for the PCA. By default, this parameter
        is set on `False`.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, use to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance (otherwise, the parameter
        `sampling_frequency` is unused).

    show_graph: bool, optional
        If set on `True` (default), shows the selected components (see next parameter) and the contribution of each
        joint to the components.

        .. note::
            Even if `include_audio` is set on True, the audio will not appear on the contribution silhouette
            on the left of each graph.

    selected_components: list, int or None, optional
        Defines the components to plot. It can be a single component (e.g. `2`) or a list of components
        (e.g. [0, 2, 5]). If set on `None` (default), all the components are plotted.

    nan_behaviour: str
        If `"ignore"` (default), the labels containing values equal to numpy.NaN will be removed from the PCA. If
        `"zero"`, all the numpy.NaN will be turned to zero.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    # Import sklearn and pandas
    try:
        from sklearn.decomposition import PCA
    except ImportError:
        raise ModuleNotFoundException("sklearn", "calculate a PCA")

    try:
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundException("pandas", "calculate a PCA")

    # Get the full dataframe
    if verbosity > 0:
        print("Preparing the dataframe...")
    dataframe = _make_dataframe(experiment_or_dataframe, sequence_measure, audio_measure, sampling_frequency)
    dataframe = _get_dataframe_from_requirements(dataframe, group, condition, subjects, trials)
    if verbosity > 0:
        print("Done.")

    # Get the unique joint labels
    joint_labels = list(dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique())

    ignored = []
    pca = PCA(n_components=n_components)
    i = 0

    data_matrix = {}

    for joint_label in joint_labels:

        if verbosity > 1:
            print("\t"+joint_label)

        dataframe_joint = dataframe.loc[dataframe["label"] == joint_label]

        if i == 0 and include_audio:
            dataframe_audio = dataframe.loc[dataframe["measure"] == audio_measure]
            data_matrix[audio_measure] = pd.merge(dataframe_audio, dataframe_joint[["subject", "trial", "timestamp"]],
                                         on=["subject", "trial", "timestamp"], how="inner")["value"]

        if dataframe_joint["value"].hasnans and nan_behaviour == "ignore":
            if verbosity > 0:
                print(f"Ignoring {joint_label} as it contains nan values.")
            ignored.append(i)

        elif dataframe_joint["value"].hasnans and nan_behaviour == "zero":
            if verbosity > 0:
                print(f"Replacing some nan values from joint label {joint_label} by 0.")
            data_matrix[joint_label] = dataframe_joint["value"].mask(dataframe_joint["value"] == np.nan, 0)

        else:
            data_matrix[joint_label] = np.array(dataframe_joint["value"])

        i += 1

    joint_labels = np.delete(joint_labels, ignored)

    data_matrix = pd.DataFrame(data_matrix)
    pca_result = pca.fit_transform(data_matrix)

    if show_graph:
        _plot_components(pca_result, pca.components_, joint_labels, "PCA", selected_components)

    return pca_result


def ica(experiment_or_dataframe, n_components, group=None, condition=None, subjects=None, trials=None,
        sequence_measure="distance", audio_measure="envelope", include_audio=False, sampling_frequency=50,
        show_graph=True, selected_components=None, nan_behaviour="ignore", verbosity=1):
    """Performs an independent component analysis (ICA) on the measures from the experiment, trying to separate them
    into subcomponents. Relies on the fastICA function from
    `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html>`_.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        · A :class:`Experiment` instance, containing the full dataset to be analyzed.
        · A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        · The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        · A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    n_components: int, optional
        The number of components to generate from the ICA.

    group: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.subject.Subject.group` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), subjects from all groups will be considered.

    condition: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.condition` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), all trials will be considered.

    subjects: list(str), str or None
        If specified, the analysis will discard the subjects whose
        :attr:`~krajjat.classes.subject.Subject.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be a string (for one subject), or a list of strings (for multiple subjects).
        Otherwise, if this parameter is set on `None`, all subjects will be considered. This parameter can be combined
        with the parameter ``group`` (default), to perform the analysis on certain subjects from a certain group.

    trials: dict(str: list(str)), list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be:
            · A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows to discard or select specific trials for individual subjects.
            · A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            · The name of a single trial. This will select the given trial for all subjects.
            · `None` (default). In that case, all trials will be considered.
        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and trials is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]`, the analysis will run on the trials that intersect both requirements, i.e.
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    audio_measure: str, optional
        The measure used for each audio instance, can be either:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the audio data in the dataframe.

    include_audio: bool, optional
        If set on `True`, includes the audio channel as one of the features for the PCA. By default, this parameter
        is set on `False`.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, use to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance (otherwise, the parameter
        `sampling_frequency` is unused).

    show_graph: bool, optional
        If set on `True` (default), shows the selected components (see next parameter) and the contribution of each
        joint to the components.

        .. note::
            Even if `include_audio` is set on True, the audio will not appear on the contribution silhouette
            on the left of each graph.

    selected_components: list, int or None, optional
        Defines the components to plot. It can be a single component (e.g. `2`) or a list of components
        (e.g. [0, 2, 5]). If set on `None` (default), all the components are plotted.

    nan_behaviour: str
        If `"ignore"` (default), the labels containing values equal to numpy.NaN will be removed from the ICA. If
        `"zero"`, all the numpy.NaN will be turned to zero.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    # Import sklearn and pandas
    try:
        from sklearn.decomposition import FastICA
    except ImportError:
        raise ModuleNotFoundException("sklearn", "calculate an ICA")

    try:
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundException("pandas", "calculate an ICA")

    # Get the full dataframe
    if verbosity > 0:
        print("Preparing the dataframe...")
    dataframe = _make_dataframe(experiment_or_dataframe, sequence_measure, audio_measure, sampling_frequency)
    dataframe = _get_dataframe_from_requirements(dataframe, group, condition, subjects, trials)
    if verbosity > 0:
        print("Done.")

    # Get the unique joint labels
    joint_labels = list(dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique())

    ignored = []
    ica = FastICA(n_components=n_components)
    i = 0

    data_matrix = {}

    for joint_label in joint_labels:

        if verbosity > 1:
            print("\t"+joint_label)

        dataframe_joint = dataframe.loc[dataframe["label"] == joint_label]

        if i == 0 and include_audio:
            dataframe_audio = dataframe.loc[dataframe["measure"] == audio_measure]
            data_matrix[audio_measure] = pd.merge(dataframe_audio, dataframe_joint[["subject", "trial", "timestamp"]],
                                         on=["subject", "trial", "timestamp"], how="inner")["value"]

        if dataframe_joint["value"].hasnans and nan_behaviour == "ignore":
            if verbosity > 0:
                print(f"Ignoring {joint_label} as it contains nan values.")
            ignored.append(i)

        else:
            if dataframe_joint["value"].hasnans and nan_behaviour == "zero":
                if verbosity > 0:
                    print(f"Replacing some nan values from joint label {joint_label} by 0.")
                data_matrix[joint_label] = dataframe_joint["value"].mask(dataframe_joint["value"] == np.nan, 0)

            else:
                data_matrix[joint_label] = np.array(dataframe_joint["value"])

        i += 1

    joint_labels = np.delete(joint_labels, ignored)

    data_matrix = pd.DataFrame(data_matrix)
    ica_result = ica.fit_transform(data_matrix)

    if show_graph:
        _plot_components(ica_result, ica.components_, joint_labels, "ICA", selected_components)

    return ica_result


def mutual_information(experiment_or_dataframe, group=None, condition=None, subjects=None, trials=None,
                       series=None, average="subject", include_randperm="whole", sequence_measure="distance",
                       regression_with="envelope", sampling_frequency=50, nan_behaviour="ignore", verbosity=1,
                       **kwargs):
    """Performs a mutual information regression between the sequence measure and the audio. Relies on
    `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.mutual_info_regression.html>`_.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        · A :class:`Experiment` instance, containing the full dataset to be analyzed.
        · A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        · The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        · A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    group: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.subject.Subject.group` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), subjects from all groups will be considered.

    condition: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.condition` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), all trials will be considered.

    subjects: list(str), str or None
        If specified, the analysis will discard the subjects whose
        :attr:`~krajjat.classes.subject.Subject.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be a string (for one subject), or a list of strings (for multiple subjects).
        Otherwise, if this parameter is set on `None`, all subjects will be considered. This parameter can be combined
        with the parameter ``group`` (default), to perform the analysis on certain subjects from a certain group.

    trials: dict(str: list(str)), list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be:
            · A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows to discard or select specific trials for individual subjects.
            · A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            · The name of a single trial. This will select the given trial for all subjects.
            · `None` (default). In that case, all trials will be considered.
        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and trials is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]`, the analysis will run on the trials that intersect both requirements, i.e.
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    series: str, optional
        Defines the series that divide the data for comparison. This value can take any of the column names from the
        dataframe (apart from the values indicated in sequence_measure and audio_measure). For instance, if `group` is
        selected, the correlation will be calculated and plotted for each individual group of the dataframe.

    average: str or None, optional
        Defines if an average regression is returned. This parameter can be:
            • ``"subject"``: the regression is calculated for each subject and averaged across all subjects.
            • ``"trial"``: the regression is calculated for each trial and averaged across all trials.
            • ``None``: the regression is calculated for the whole dataset.

    include_randperm: bool or str, optional
        Defines if to include the calculation of the regression for the randomly permuted data. This parameter can be:
            • ``False``: in that case, no regression on a random permutation of the data will be calculated.
            • ``"whole"``: calculates a random permutation on the whole data.
            • ``"individual"``: calculates a random permutation for each series.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    regression_with: str, optional
        The measure used for the coherence. It can be either a joint label (in that case, the coherence uses the
        sequence measure of that joint), or an audio measure, among:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            In the case where the value is an audio value, this parameter will be used to generate a dataframe if the
            parameter `experiment_or_dataframe` is an Experiment instance.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, use to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance (otherwise, the parameter
        `sampling_frequency` is unused).

    nan_behaviour: str
        If `"ignore"` (default), the labels containing values equal to numpy.NaN will be removed from the ICA. If
        `"zero"`, all the numpy.NaN will be turned to zero.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    try:
        from sklearn.feature_selection import mutual_info_regression
    except ImportError:
        raise ModuleNotFoundException("sklearn", "perform a mutual information regression")

    try:
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundException("pandas", "perform a mutual information regression")

    # Get the full dataframe
    if verbosity > 0:
        print("Preparing the dataframe...")

    dataframe = _make_dataframe(experiment_or_dataframe, sequence_measure, regression_with, sampling_frequency,
                                verbosity)
    dataframe = _get_dataframe_from_requirements(dataframe, group, condition, subjects, trials)

    if verbosity > 0:
        print("Done.")

    # Get the series of interest
    if series is not None:
        series_values = list(dataframe[series].unique())
    else:
        series_values = ["Full dataset"]

    # Get if to calculate the random permutation
    if include_randperm == "whole":
        series_values.append("Full dataset (randomly permuted)")
    elif include_randperm == "individual":
        for s in range(len(series_values)):
            series_values.append(series_values[s] + "(randomly permuted)")

    # Get the subjects/trials
    if average == "subject":
        if type(subjects) == str:
            individuals = [subjects]
        elif subjects is None:
            individuals = dataframe["subject"].unique()
        else:
            individuals = subjects
    elif average == "trial":
        if type(trials) == str:
            individuals = [trials]
        elif subjects is None:
            individuals = dataframe["trial"].unique()
        else:
            individuals = trials
    else:
        individuals = ["All"]

    plot_dictionary = {}

    # Get the unique joint labels
    joint_labels = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()

    regression_values = {}

    if verbosity > 1:
        print("Calculating the regression...")

    for series_value in series_values:

        # We get the corresponding dataframe
        value = series_value
        if series_value.endswith(" (randomly permuted)"):
            value = series_value.replace(" (randomly permuted)", "")

        if value == "Full dataset":
            dataframe_series_value = dataframe
        else:
            dataframe_series_value = dataframe.loc[dataframe[series] == value]

        if verbosity > 1:
            print("\t" + series_value)

        regression_values_series = {}

        # For each subject/trial
        for individual in individuals:
            if individual == "All":
                dataframe_individual = dataframe_series_value
            else:
                dataframe_individual = dataframe_series_value.loc[dataframe_series_value[average] == individual]

            if verbosity > 1:
                print("\t\t" + individual)

            data_matrix = {}
            regression_values_ind = {}
            values_to_correlate_joints = {}

            joint_labels = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()
            ignored = []
            i = 0

            for joint_label in joint_labels:

                if verbosity > 1:
                    print("\t\t\t" + joint_label)

                dataframe_joint = dataframe_individual.loc[dataframe_individual["label"] == joint_label]
                dataframe_joint = dataframe_joint.copy()

                if dataframe_joint["value"].shape[0] == 0:
                    print(f"\t\t\t\tIgnoring {joint_label} as it doesn't contain any value for {individual}.")
                    ignored.append(i)

                else:

                    if dataframe_joint["value"].hasnans and nan_behaviour == "ignore":
                        if verbosity > 0:
                            print(f"\t\t\t\tIgnoring {joint_label} as it contains nan values.")
                        ignored.append(i)

                    elif dataframe_joint["value"].hasnans and nan_behaviour == "zero":
                        if verbosity > 0:
                            print(f"\t\t\t\tReplacing some nan values from joint label {joint_label} by 0.")
                        data_matrix[joint_label] = dataframe_joint["value"].mask(dataframe_joint["value"] == np.nan, 0)

                    else:
                        data_matrix[joint_label] = np.array(dataframe_joint["value"])

                if regression_with in ["audio", "envelope", "intensity", "pitch", "f1", "f2", "f3", "f4", "f5"]:
                    values_to_correlate = dataframe_individual.loc[dataframe_individual["measure"] == regression_with]
                    values_to_correlate = pd.merge(values_to_correlate,
                                                   dataframe_joint[["subject", "trial", "timestamp"]],
                                                   on=["subject", "trial", "timestamp"], how="inner")["value"]

                    if series_value.endswith(" (randomly permuted)"):
                        values_to_correlate = np.random.permutation(values_to_correlate)
                    values_to_correlate_joints[joint_label] = values_to_correlate

                elif regression_with in joint_labels:
                    values_to_correlate = dataframe_individual.loc[dataframe_individual["label"] ==
                                                                   regression_with]["value"]
                    if series_value.endswith(" (randomly permuted)"):
                        values_to_correlate = np.random.permutation(values_to_correlate)
                    values_to_correlate_joints[joint_label] = values_to_correlate

                else:
                    raise Exception("Please select a correct value for the parameter regression_with.")

                i += 1

            data_matrix = pd.DataFrame(data_matrix)
            joint_labels = np.delete(joint_labels, ignored)

            # values_to_correlate_matrix = pd.DataFrame(values_to_correlate_joints)
            # np.delete(values_to_correlate_joints, ignored)

            selected_joint_label = None
            for joint_label in values_to_correlate_joints:
                if joint_label in joint_labels:
                    #print(joint_label)
                    if selected_joint_label is None:
                        selected_joint_label = joint_label
                    elif values_to_correlate_joints[joint_label].shape != \
                            values_to_correlate_joints[selected_joint_label].shape:
                        raise Exception("The joint labels do not all have the same amount of values in the dataframe.")

            values_to_correlate = values_to_correlate_joints[selected_joint_label]

            #print(data_matrix.shape)
            #print(values_to_correlate.shape)

            results_regression = mutual_info_regression(data_matrix, values_to_correlate, discrete_features=False)

            for i in range(len(joint_labels)):
                regression_values_ind[joint_labels[i]] = results_regression[i]

            regression_values_series[individual] = regression_values_ind

        regression_values[series_value] = regression_values_series

    # Calculate the averages
    average_regression = {}
    sd_regression = {}

    max_value = 0

    # For each series
    for series_value in series_values:

        average_regression_series_value = {}
        sd_regression_series_value= {}

        # For each joint
        for joint_label in joint_labels:

            regression_values_joint = []

            # For each individual
            for individual in individuals:
                if joint_label in regression_values[series_value][individual].keys():
                    regression_values_joint.append(regression_values[series_value][individual][joint_label])

            average_regression_series_value[joint_label] = np.mean(regression_values_joint)
            sd_regression_series_value[joint_label] = np.std(regression_values_joint)

            plot_dictionary[joint_label] = average_regression_series_value[joint_label]

            if average_regression_series_value[joint_label] > max_value:
                max_value = average_regression_series_value[joint_label]

        average_regression[series_value] = average_regression_series_value
        sd_regression[series_value] = sd_regression_series_value

        plot_silhouette(plot_dictionary, title=series_value, max_scale=max_value, verbosity=verbosity, **kwargs)

    return average_regression, sd_regression


def _make_dataframe(experiment_or_dataframe, sequence_measure, audio_measure, sampling_frequency, verbosity=1):
    """Loads a dataframe from a variety of inputs.

    .. versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        · A :class:`Experiment` instance, containing the full dataset to be analyzed.
        · A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        · The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        · A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    audio_measure: str, optional
        The measure used for each audio instance, can be either:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the audio data in the dataframe.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, used to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance, and to perform the coherence.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Returns
    -------
    dataframe: pandas.DataFrame
        A dataframe containing the loaded data.
    """
    dataframe = None

    try:
        import pandas as pd
    except ImportError:
        raise ModuleNotFoundException("pandas", "generate a DataFrame")

    # Get the full dataframe
    if type(experiment_or_dataframe) is not list:
        experiment_or_dataframe = [experiment_or_dataframe]

    if verbosity > 1:
        print(f"\tFound {len(experiment_or_dataframe)} input element(s).")

    i = 1

    for item in experiment_or_dataframe:
        if type(item) is Experiment:
            if audio_measure not in ["audio", "envelope", "intensity", "pitch", "f1", "f2", "f3", "f4", "f5"]:
                audio_measure = None
            dataframe_item = item.get_dataframe(sequence_measure, audio_measure,
                                                audio_resampling_frequency=sampling_frequency)
        elif type(item) is str:
            dataframe_item = read_pandas_dataframe(item)
        elif type(item) is pd.DataFrame:
            dataframe_item = item
        else:
            raise Exception("One item in experiment_or_dataframe is neither an Experiment, a Pandas Dataframe or a "
                            "path to a Pandas Dataframe.")

        if verbosity > 1:
            print(f"\t\tDataframe {i} with {dataframe_item.shape[1]} columns and {dataframe_item.shape[0]} rows.")

        if dataframe is None:
            dataframe = dataframe_item
        else:
            dataframe = pd.concat([dataframe, dataframe_item])

        i += 1

    if verbosity > 1:
        print(f"\tGlobal dataframe generated with {dataframe.shape[1]} columns and {dataframe.shape[0]} rows.")

    return dataframe


def _get_dataframe_from_requirements(dataframe, group=None, condition=None, subjects=None, trials=None):
    """Returns a sub-dataframe containing only the data where the group, condition, subjects and trails match
    the given parameters.

    .. versionadded:: 2.0

    Parameters
    ----------
    dataframe: pandas.DataFrame
        A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
        generally generated from :meth:`Experiment.get_dataframe()`.

    group: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.subject.Subject.group` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), subjects from all groups will be considered.

    condition: str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.condition` attribute does not match the value provided for this parameter.
        Otherwise, if this parameter is set on `None` (default), all trials will be considered.

    subjects: list(str), str or None
        If specified, the analysis will discard the subjects whose
        :attr:`~krajjat.classes.subject.Subject.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be a string (for one subject), or a list of strings (for multiple subjects).
        Otherwise, if this parameter is set on `None`, all subjects will be considered. This parameter can be combined
        with the parameter ``group`` (default), to perform the analysis on certain subjects from a certain group.

    trials: dict(str: list(str)), list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.name` attribute does not match the value(s) provided for this parameter.
        This parameter can be:
            · A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows to discard or select specific trials for individual subjects.
            · A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            · The name of a single trial. This will select the given trial for all subjects.
            · `None` (default). In that case, all trials will be considered.
        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and trials is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]`, the analysis will run on the trials that intersect both requirements, i.e.
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    Returns
    -------
    dataframe: pandas.DataFrame
        A dataframe, containing a subset from the original dataframe.
    """

    if group is not None:
        dataframe = dataframe.loc[dataframe["group"] == group]
    if condition is not None:
        dataframe = dataframe.loc[dataframe["condition"] == condition]
    if subjects is not None:
        if type(subjects) is list:
            dataframe = dataframe.loc[dataframe["subject"].isin(subjects)]
        elif type(subjects) is str:
            dataframe = dataframe.loc[dataframe["subject"] == subjects]
    if trials is not None:
        if type(trials) is dict:
            new_dataframe = None
            for subject in trials.keys():
                dataframe_subject = dataframe.loc[dataframe["subject"] == subject]
                if type(trials[subject]) is str:
                    trials[subject] = [trials[subject]]
                for trial in trials[subject]:
                    dataframe_trial = dataframe_subject.loc[dataframe["trial"] == trial]
                    if new_dataframe is None:
                        new_dataframe = dataframe_trial
                    else:
                        new_dataframe.merge(dataframe_trial)
            dataframe = new_dataframe
        elif type(trials) is list:
            dataframe = dataframe.loc[dataframe["trial"].isin(trials)]
        elif type(trials) is str:
            dataframe = dataframe.loc[dataframe["trial"] == trials]

    return dataframe
