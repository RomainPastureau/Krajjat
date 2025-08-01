"""These functions allow finding significant relationships between movements, or between movements and audio properties.
"""

import pandas as pd
import numpy as np
from scipy import signal

from krajjat.classes.exceptions import ModuleNotFoundException
from krajjat.classes.experiment import Experiment
from krajjat.classes.graph_element import Graph, GraphPlot
from krajjat.plot_functions import plot_silhouette, plot_body_graphs, _plot_components
from krajjat.tool_functions import convert_colors, read_pandas_dataframe, find_closest_value_index

def _common_analysis(experiment_or_dataframe, analysis, method, group, condition, subjects, trials, series, average,
                     return_values, permutation_level, number_of_randperms, sequence_measure, audio_measure,
                     target_feature, sampling_frequency, specific_frequency=None, freq_atol=1e-8, include_audio=False,
                     random_seed=None, color_line_series=None, color_line_perm=None, title=None, width_line=1,
                     verbosity=1, **kwargs):
    """
    Performs a general-purpose analysis across multiple signal types, including power spectrum, correlation,
    and coherence, for a given dataset or Experiment. The function supports individual- and trial-level analyses,
    random permutations for significance estimation, and visualization via body or silhouette plots.

    .. versionadded:: 2.0

    This internal function is designed to be called by specific analysis wrappers like `power_spectrum()`,
    `correlation()`, and `coherence()` and is not intended to be called directly by end users.

    Parameters
    ----------
    experiment_or_dataframe : Experiment, pandas.DataFrame, str or list(any)
        The input data to analyse. This can be:
            • An :class:`Experiment` instance.
            • A pandas DataFrame (e.g., from :meth:`Experiment.get_dataframe()`).
            • A file path to a saved DataFrame (from :meth:`Experiment.save_dataframe()`).
            • A list combining any of the above types. All dataframes will be merged.

    analysis : str
        The type of analysis to perform. Must be one of: `"power spectrum"`, `"correlation"`, `"coherence"`.

    method : str
        For `"power spectrum"`: `"fft"` or `"welch"`.
        For `"correlation"`: `"corr"`, `"rm_corr"` or `"numpy"`.
        Ignored for `"coherence"`.

    group : str or None
        Filter the analysis to subjects with the specified group label.

    condition : str or None
        Filter the analysis to sequences with the specified condition label.

    subjects : list(str), str or None
        Restrict the analysis to the specified subjects. Can be a string or a list of strings. If `None`, all are used.

    trials : dict(str: list(str)), list(str), str or None
        Restrict the analysis to specific trials. See `power_spectrum()` or `correlation()` docstring for full format.

    series : str or None
        A column name from the dataframe to split data into subsets. E.g., `"group"`, `"condition"`.

    average : str or None
        Defines the level of averaging:
            • `"subject"`: average across subjects.
            • `"trial"`: average across trials.
            • `None`: no averaging; analyse full dataset.

    return_values : str
        Either `"raw"` or `"z-scores"`. Controls whether to return raw values or Z-scored results based on permutations.

    permutation_level : str
        This parameter determines how permutations are applied:
            • `"whole"`: permutations are done on the pooled data.
            • `"individual"`: permutations are done separately for each subject or trial (depending on the value of
              `average`).
            • ``None``: no permutations are calculated. This value is not allowed if `return_values == "z-scores"`.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_level` is set to ``"whole"`` or
        ``"individual"``. An average of the calculated random permutations is then calculated, in order to calculate
        a Z-score for the correlation.

    sequence_measure : str
        The column name of the sequence measure to analyse. See `power_spectrum()` or `correlation()` for options.

    audio_measure : str or None
        The audio feature to include (e.g., `"envelope"`, `"pitch"`). Ignored if `include_audio_in_labels` is `False`.

    target_feature : str
        The reference signal or label to compare against (for `"correlation"` and `"coherence"` analyses only).
        Can be either a joint label or an audio measure.

    sampling_frequency : int or float
        Sampling rate of the signals.

    specific_frequency : float or list of float or None
        Frequency (or list of frequencies) to extract from the result. If set, silhouette plots are generated.

    freq_atol : float or int
        Absolute tolerance for matching the specific frequency (default: 1e-8).

    include_audio : bool
        If `True`, includes audio signals in the set of labels to analyse.

    random_seed : int or None
        Fixes the seed for reproducible random permutations.

    color_line_series : list or str or None
        Color(s) to use when plotting time-frequency graphs. If this parameter is a list, a color will be
        attributed to each series.

    color_line_perm: str or None
        Color to use for the permutations when plotting time-frequency graphs.

    title: str or None
        If set, the title will be set to the plot. Otherwise, an automatic title will be generated.

    width_line : int or float
        Width of plotted lines (for spectral plots).

    verbosity : int
        Controls console output:
            • `0`: Silent mode.
            • `1`: Normal mode (default).
            • `2`: Chatty mode (prints every step and label).

    **kwargs
        Additional arguments passed to `plot_silhouette()` or `plot_body_graphs()`.

    Returns
    -------
    averages : dict
        Nested dictionary of average values per label and per series.
        Structure: {series_value: {label: average_value}}

    stds : dict
        Nested dictionary of standard deviations per label and series.
        Structure: {series_value: {label: std_value}}

    z_scores or averages_perms : dict
        Nested dictionary of Z-scores comparing real values to random permutations, or nested dictionary of the
        averages of the permutations.

    p_values or stds_perms : dict
        Nested dictionary of empirical p-values for each label and series, or nested dictionary of the standard
        deviations of the permutations.
    """

    # Load pingouin for correlation
    if analysis == "correlation" and method in ["corr", "rm_corr"]:
        try:
            import pingouin as pg
        except ImportError:
            raise ModuleNotFoundException("pingouin", "calculate the correlation")

    # Set the random seed for reproducibility on the randperm arrays
    if random_seed is not None:
        np.random.seed(random_seed)

    # Get the full dataframe
    if verbosity > 0:
        print("Preparing the dataframe...")
    dataframe = _make_dataframe(experiment_or_dataframe, sequence_measure, audio_measure, sampling_frequency,
                                verbosity)
    dataframe = _get_dataframe_from_requirements(dataframe, group, condition, subjects, trials)
    if verbosity > 0:
        print("Done.")

    if verbosity > 1:
        print("Showing the first few rows of the dataframe...")
        print(dataframe.head(10))
        print("Done.")

        print("Showing the last few rows of the dataframe...")
        print(dataframe.tail(10))
        print("Done.")

    # Get the series of interest
    if series is not None:
        series_values = list(dataframe[series].unique())
    else:
        series_values = ["Full dataset"]

    # Get the subjects/trials
    if average == "subject":
        if isinstance(subjects, str):
            individuals = [subjects]
        elif subjects is None:
            individuals =  dataframe["subject"].unique()
        else:
            individuals = subjects

    elif average == "trial":
        if isinstance(trials, str):
            individuals = [trials]
        elif trials is None:
            individuals = dataframe["trial"].unique()
        else:
            individuals = trials
    else:
        individuals = ["All"]

    # Get the unique labels (joint labels and audio measure)
    if include_audio:
        labels = dataframe["label"].unique()
    else:
        labels = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()

    # Handle the title
    if title is None:
        if analysis == "power spectrum":
            title = f"Power spectrum of the {sequence_measure}"
            if include_audio:
                title += f" and the {audio_measure}"
            if specific_frequency is not None:
                if type(specific_frequency) == list:
                    title += "at " + ", ".join(specific_frequency) + " Hz"
                else:
                    title += "at " + str(specific_frequency) + " Hz"
            settings = []
            if group is not None:
                if type(group) == str:
                    settings.append(f"group: {group}")
                elif len(group) < 4:
                    settings.append(f"groups: {', '.join(group)}")
                else:
                    settings.append(f"{len(group)} groups")
            if condition is not None:
                if type(condition) == str:
                    settings.append(f"condition: {condition}")
                elif len(condition) < 4:
                    settings.append(f"conditions: {', '.join(condition)}")
                else:
                    settings.append(f"{len(condition)} conditions")
            if subjects is not None:
                if type(subjects) == str:
                    settings.append(f"subject: {subjects}")
                elif len(subjects) < 4:
                    settings.append(f"subjects: {', '.join(subjects)}")
                else:
                    settings.append(f"{len(subjects)} subjects")
            if trials is not None:
                if type(trials) == str:
                    settings.append(f"trial: {trials}")
                elif type(trials) == dict:
                    settings.append(f"multiple trials")
                else:
                    settings.append(f"{len(trials)} trials")

            if len(settings) > 0:
                title += " (" + "; ".join(settings) + ")"
                    
    # Create the plot dictionary
    plot_dictionary = {}
    analysis_values = {}
    frequencies = None

    if return_values == "z-scores":
        if permutation_level is None or number_of_randperms <= 0:
            raise Exception("If the return_values parameter is set to 'z-scores', the permutation_level parameter "
                            "must be set, and number_of_randperms has to be more than 0.")
        else:
            randperm_values = {}

    if analysis == "coherence":
        nperseg = sampling_frequency / kwargs.get("step_segments", 0.25)

    if verbosity > 1:
        print(f"Calculating the {analysis}...")

    # For each series
    for series_value in series_values:
        if verbosity > 1:
            print("\t" + series_value)

        # We get the corresponding dataframe
        if series_value == "Full dataset":
            df_series = dataframe
        else:
            df_series = dataframe.loc[dataframe[series] == series_value]

        values_series = {}
        randperm_series = {ind: {label: [] for label in labels} for ind in individuals}

        # For each subject/trial
        for individual in individuals:

            if average == series and individual != series_value:
                continue

            if verbosity > 1:
                print("\t\t" + individual)

            if series == "subject" and average == "subject":
                df_ind = df_series[df_series["subject"] == individual]
            else:
                df_ind = df_series if individual == "All" else df_series[df_series[average] == individual]

            values_ind = {}

            for label in labels:
                if verbosity > 1:
                    print("\t\t\t" + label)

                df_label = df_ind[df_ind["label"] == label]
                label_values = df_label["value"]

                if analysis == "power spectrum":

                    if method not in ["fft", "welch"]:
                        raise Exception("""Method must be "fft" or "welch".""")

                    if frequencies is None:
                        frequencies, _ = signal.welch(np.zeros(1000), fs=sampling_frequency)

                    if label_values.empty:
                        values_ind[label] = np.empty(len(frequencies))
                        values_ind[label][:] = np.nan

                    else:
                        if method == "fft":
                            power_spectrum = np.abs(np.fft.fft(label_values)) ** 2
                            fft_freqs = np.fft.fftfreq(label_values.size, 1 / sampling_frequency)
                            fft_freqs = fft_freqs[:len(fft_freqs) // 2]
                            values_ind[label] = power_spectrum[:len(power_spectrum) // 2]

                            interpolated_spectrum = np.interp(frequencies, fft_freqs, values_ind[label])
                            values_ind[label] = interpolated_spectrum

                        elif method == "welch":
                            frequencies, values_ind[label] = signal.welch(label_values, fs=sampling_frequency)

                elif analysis in ["correlation", "coherence"]:
                    if target_feature in labels:
                        target_values = df_ind.loc[df_ind["label"] == target_feature]["value"].to_numpy()
                    else:
                        target_values = df_ind.loc[df_ind["measure"] == target_feature]["value"].to_numpy()

                    if target_values.size == 0:
                        raise Exception("Please select a correct value for the parameter target_feature.")

                    if analysis == "correlation":

                        if method == "corr":
                            try:
                                values_ind[label] = np.abs(pg.corr(x=label_values, y=target_values).values[0][1])
                            except (ValueError, AssertionError):
                                values_ind[label] = np.nan
                        elif method == "rm_corr":
                            df_temp = pd.DataFrame(
                                {"value": label_values, "correlation_with": target_values,
                                 "subject": [individual]})
                            try:
                                result = pg.rm_corr(data=df_temp, x="value", y="correlation_with", subject="subject")
                                values_ind[label] = np.abs(result["r"])
                            except (ValueError, AssertionError):
                                values_ind[label] = np.nan
                        elif method == "numpy":
                            label_values_mean = np.mean(label_values)
                            target_values_mean = np.mean(target_values)
                            num = np.sum((label_values - label_values_mean) * (target_values - target_values_mean))
                            denom = np.sqrt(np.sum((label_values - label_values_mean) ** 2) *
                                            np.sum((target_values - target_values_mean) ** 2))
                            if denom != 0:
                                values_ind[label] = num / denom
                            else:
                                values_ind[label] = np.nan
                        else:
                            raise ValueError("Invalid method. Choose either 'corr', 'rm_corr', or 'numpy'.")

                    elif analysis == "coherence":
                        freqs, coh = signal.coherence(label_values, target_values, fs=sampling_frequency,
                                                      nperseg=kwargs.get(nperseg))

                        if len(coh) == 0:
                            coh = np.tile(np.nan, int(nperseg // 2 + 1))

                        if frequencies is None:
                            frequencies = freqs

                        values_ind[label] = coh

                else:
                    raise Exception("Invalid value for the parameter analysis. Choose either 'power spectrum', "
                                    "'correlation', or 'coherence'.")

                if permutation_level is not None:
                    perm_targets = individuals if permutation_level == "individual" else ["whole"]
                    for _ in range(number_of_randperms):

                        if analysis == "power spectrum":
                            perm = np.random.permutation(label_values)

                            if method == "fft":
                                power_spectrum = np.abs(np.fft.fft(perm)) ** 2
                                fft_freqs = np.fft.fftfreq(perm.size, 1 / sampling_frequency)
                                fft_freqs = fft_freqs[:len(fft_freqs) // 2]
                                perm_values = power_spectrum[:len(power_spectrum) // 2]

                                interpolated_spectrum = np.interp(frequencies, fft_freqs, perm_values)
                                perm_values = interpolated_spectrum

                            elif method == "welch":
                                frequencies, perm_values = signal.welch(perm, fs=sampling_frequency)

                        elif analysis == "correlation":
                            perm = np.random.permutation(target_values)

                            if method == "corr":
                                try:
                                    perm_values = np.abs(pg.corr(x=label_values, y=perm).values[0][1])
                                except (ValueError, AssertionError):
                                    perm_values = np.nan
                            elif method == "rm_corr":
                                df_temp["correlation_with"] = perm
                                try:
                                    perm_values = np.abs(pg.rm_corr(data=df_temp, x="value", y="correlation_with",
                                                          subject="subject")["r"])
                                except (ValueError, AssertionError):
                                    perm_values = np.nan
                            elif method == "numpy":
                                label_values_mean = np.mean(label_values)
                                perm_mean = np.mean(perm)
                                num = np.sum((label_values - label_values_mean) * (perm - perm_mean))
                                denom = np.sqrt(np.sum((label_values - label_values_mean) ** 2) *
                                                np.sum((perm - perm_mean) ** 2))
                                if denom != 0:
                                    perm_values = num / denom
                                else:
                                    perm_values = np.nan

                        elif analysis == "coherence":
                            perm = np.random.permutation(target_values)
                            freqs, perm_values = signal.coherence(perm, target_values, fs=sampling_frequency,
                                                                  nperseg=nperseg)

                        for tgt in perm_targets:
                            if permutation_level == "individual":
                                randperm_values.setdefault(series_value, {}).setdefault(individual,
                                {}).setdefault(label, []).append(perm_values)
                            else:
                                randperm_values.setdefault(series_value, {}).setdefault("whole",
                                {}).setdefault(label, []).append(perm_values)

            values_series[individual] = values_ind

        analysis_values[series_value] = values_series

    color_series = {}

    if color_line_series is not None:
        if type(color_line_series) is not list:
            color_line_series = [color_line_series]
        color_line_series = convert_colors(color_line_series, "hex")
        for s in range(len(series_values)):
            if s < len(color_line_series):
                color_series[series_values[s]] = color_line_series[s]
            else:
                color_series[series_values[s]] = None

    else:
        color_line_series = {series_value: None for series_value in series_values}

    if color_line_perm is not None:
        color_line_perm = convert_colors(color_line_perm, "hex")

    if return_values == "z-scores":
        if verbosity > 1:
            print("Calculating the z-scores...")
    elif return_values == "raw":
        if verbosity > 1:
            print("Calculating the averages...")

    averages = {}
    stds = {}
    z_scores = {}
    p_values = {}
    averages_perm = {}
    stds_perm = {}
    max_value = 0

    index_freqs = []
    if specific_frequency is not None:
        for freq in specific_frequency:
            close_freq_index = int(find_closest_value_index(frequencies, freq, atol=freq_atol))
            if close_freq_index is not None:
                index_freqs.append(close_freq_index)
            else:
                raise Exception(f"The frequency {specific_frequency} was not found among the available "
                                f"frequencies. Please select a value among {frequencies}.")

        if len(specific_frequency) == 1:
            if verbosity > 0:
                print("Selected frequency: " + str(frequencies[index_freqs[0]]) + " Hz.")
        else:
            freqs = [str(np.round(frequencies[index_freqs[i]], 2)) for i in range(len(index_freqs))]
            if verbosity > 0:
                print("Selected frequencies: " + " Hz, ".join(freqs) + " Hz.")

    # For each series
    for series_value in series_values:
        if verbosity > 1:
            print("\t" + series_value)

        averages[series_value] = {}
        stds[series_value] = {}
        z_scores[series_value] = {}
        p_values[series_value] = {}
        averages_perm[series_value] = {}
        stds_perm[series_value] = {}

        # For each label
        for label in labels:
            if verbosity > 1:
                print("\t\t" + label)

            if specific_frequency is None and label not in plot_dictionary.keys():
                plot_dictionary[label] = Graph()

            if average == series:
                vals = [analysis_values[series_value][series_value][label]]
            else:
                vals = [analysis_values[series_value][ind][label] for ind in individuals]

            if analysis in ["power spectrum", "correlation"]:
                axis = 0
            else:
                axis = 1

            expected_length = None
            for val in vals:
                if expected_length is None:
                    expected_length = len(val)
                elif len(val) != expected_length:
                    raise Exception("At least one element does not have the same length as the others.")

            avg = np.nanmean(vals, axis=axis)
            std = np.nanstd(vals, axis=axis)
            p = np.nan

            if permutation_level is not None:
                perm_keys = individuals if permutation_level == "individual" else ["whole"]
                perms = [r for key in perm_keys for r in randperm_values.get(series_value, {}).get(key, {}).get(label, [])]
                perms = np.stack(perms)
                perms = perms[np.all(np.isfinite(perms), axis=1)]
                # perms = np.array(perms)
                # perms = perms[np.isfinite(perms)]

                if return_values == "z-scores":
                    # p-value: proportion of permuted correlations >= real average

                    if perms.size == 0:
                        p = np.full_like(avg, np.nan)
                        z = np.full_like(avg, np.nan)

                    else:
                        p = np.mean(perms >= avg, axis=0)
                        z = (avg - np.nanmean(perms, axis=0)) / np.nanstd(perms, axis=0)

                    # if len(perms) > 0:
                    #     p = np.mean(perms >= avg)
                    # else:
                    #     p = np.nan
                    #
                    # z = ((avg - np.nanmean(perms)) / np.nanstd(perms)) if np.nanstd(perms) > 0 else np.nan
                    z_scores[series_value][label] = z
                    p_values[series_value][label] = p
                    if np.any(np.isfinite(z)):
                        max_value = max(max_value, np.nanmax(z))

                else:
                    averages_perm[series_value][label] = np.nanmean(perms)
                    stds_perm[series_value][label] = np.nanstd(perms)

            else:
                perms = []
                max_value = max(max_value, np.max(avg), np.max(avg+std))

            averages[series_value][label] = avg
            stds[series_value][label] = std

            if specific_frequency is not None:
                if label not in plot_dictionary.keys():
                    plot_dictionary[label] = []
                for index_freq in index_freqs:
                    if return_values == "z-scores":
                        plot_dictionary[label].append(z_scores[series_value][label][index_freq])
                    else:
                        plot_dictionary[label].append(averages[series_value][label][index_freq])

            else:
                if return_values == "z-scores":
                    graph_plot = GraphPlot(frequencies, z_scores[series_value][label], line_width=width_line,
                                           color=color_line_series[series_value], label=series_value)
                    plot_dictionary[label].add_graph_plot(graph_plot)
                else:
                    graph_plot = GraphPlot(frequencies, averages[series_value][label],
                                           stds[series_value][label], line_width=width_line,
                                           color=color_line_series[series_value], label=series_value)
                    plot_dictionary[label].add_graph_plot(graph_plot)

                    if permutation_level is not None:
                        graph_plot = GraphPlot(frequencies, averages_perm[series_value][label],
                                               stds_perm[series_value][label], line_width=width_line,
                                               color=color_line_perm, label=series_value)
                        plot_dictionary[label].add_graph_plot(graph_plot)

    if specific_frequency is not None:
        plot_silhouette(plot_dictionary, title=title, max_scale=max_value, verbosity=verbosity, **kwargs)

    else:
        plot_body_graphs(plot_dictionary, title=title, max_scale=max_value, verbosity=verbosity, **kwargs)

    if return_values == "z-scores":
        return frequencies, averages, stds, z_scores, p_values
    else:
        if permutation_level is not None:
            return frequencies, averages, stds, averages_perm, stds_perm
        return frequencies, averages, stds


def power_spectrum(experiment_or_dataframe, method="welch", group=None, condition=None, subjects=None, trials=None,
                   series=None, average="subject", return_values="raw", permutation_level=None, number_of_randperms=0,
                   sequence_measure="distance", audio_measure="envelope",
                   sampling_frequency=50, specific_frequency=None, freq_atol=1e-8,
                   include_audio=False, width_line=1, color_line=None, verbosity=1, **kwargs):
    """Returns the power spectrum values for all the variables (joints and audio) of the given dataframe or experiment.
    The function also plots these power spectrum values.

    .. versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any)
        This parameter can be:

            • A :class:`Experiment` instance, containing the full dataset to be analyzed.
            • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
              generally generated from :meth:`Experiment.get_dataframe()`.
            • The path of a file containing a pandas DataFrame, generally generated from
              :class:`Experiment.save_dataframe()`.
            • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    method: str, optional
        The method to use to calculate the power spectrum. It can be either:
            • ``"fft"``: in that case, the power spectrum will be calculated using the Fast Fourier Transform algorithm
              from `numpy <https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html>`_.
            • ``"welch"`` (default): in that case, the power spectrum will be calculated using the Welch algorithm
              from `scipy <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html>`_. This method
              is more robust to noise than the FFT.

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

            • A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows discarding or select specific trials for individual subjects.
            • A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            • The name of a single trial. This will select the given trial for all subjects.
            • `None` (default). In that case, all trials will be considered.

        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and `trials` is set on `{"sub_001": ["trial_001",
            "trial_002"], "sub_004": ["trial_001"]}`, the analysis will run on the trials that intersect both
            requirements, i.e., trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    series: str, optional
        Defines the series that divide the data for comparison. This value can take any of the column names from the
        dataframe (apart from the values indicated in sequence_measure and audio_measure). For instance, if `group` is
        selected, the correlation will be calculated and plotted for each individual group of the dataframe.
        Alternatively, setting this parameter on `None` (default) or `"Full dataset"` will not perform any comparison,
        but rather run the analysis on all the data.

    average: str or None, optional
        Defines if an average power spectrum is computed. This parameter can be:
            • ``"subject"``: the power spectrum is calculated for each subject and averaged across all subjects.
            • ``"trial"``: the power spectrum is calculated for each trial and averaged across all trials.
            • ``None``: the power spectrum is calculated for the whole dataset.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    audio_measure: str|None, optional
        The audio measure, among:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``
            • ``None`` (default): in that case, the power spectrum of the audio will not be computed.

        .. note::
            In the case where the value is an audio value, this parameter will be used to generate a dataframe if the
            parameter `experiment_or_dataframe` is an Experiment instance.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, used to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance. If the parameter
        `experiment_or_dataframe` is a dataframe, this parameter is ignored.

    specific_frequency: float|list|None, optional
        If set, the function will return the power spectrum of the specified frequency, (or the specific frequencies,
        as a list) and plot a silhouette graph rather than a body graph.

    freq_atol: float|int, optional
        The absolute tolerance of the frequency set on ``specific_frequency`` (default: 1e-8). If set, the function
        will look for the closest matching frequency in the range ``[specific_frequency - freq_atol,
        specific_frequency + freq_atol]``.

    include_audio: bool, optional
        Whether to include the audio in the power spectrum calculation and plot. Default: `False`.

    width_line: int or float, optional
        Defines the width of the plotted lines (default: 1).

    color_line: list or None, optional
        A list containing the colors for the different variables of interest. If the number of colors is inferior to
        the plotted series, the colors loop through the list.

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
    frequencies : np.ndarray
        Frequency bins.

    averages : dict
        Average power per label and series.

    stds : dict
        Standard deviations of the power per label and series.
    """

    return _common_analysis(experiment_or_dataframe=experiment_or_dataframe, analysis="power spectrum", method=method,
                            group=group, condition=condition, subjects=subjects, trials=trials, series=series,
                            average=average, return_values=return_values, permutation_level=permutation_level,
                            number_of_randperms=number_of_randperms,
                            sequence_measure=sequence_measure, audio_measure=audio_measure, target_feature=None,
                            sampling_frequency=sampling_frequency, specific_frequency=specific_frequency,
                            freq_atol=freq_atol, include_audio=include_audio, random_seed=None,
                            color_line=color_line, width_line=width_line, verbosity=verbosity, **kwargs)

def correlation(experiment_or_dataframe, method="corr", group=None, condition=None, subjects=None, trials=None,
                series=None, average="subject", sequence_measure="distance", audio_measure="envelope",
                correlation_with="envelope", return_values="z-scores", permutation_level="whole",
                number_of_randperms=1000, sampling_frequency=50, include_audio=False, random_seed=None,
                verbosity=1, **kwargs):
    """Calculates and plots the correlation between one metric derived from the sequences, and the same metric from a
    given joint, or another metric derived from the corresponding audio clips.

    .. versionadded :: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any)
        This parameter can be:
        
            • A :class:`Experiment` instance, containing the full dataset to be analyzed.
            • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
              generally generated from :meth:`Experiment.get_dataframe()`.
            • The path of a file containing a pandas DataFrame, generally generated from
              :class:`Experiment.save_dataframe()`.
            • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    method: str, optional
        Can be either `"corr"` (default, uses
        `pingouin_corr <https://pingouin-stats.org/build/html/generated/pingouin.corr.html>`__), `"rm_corr"` (uses
        `pingouin_corr <https://pingouin-stats.org/build/html/generated/pingouin.rm_corr.html>`__), or ``"numpy"``
        (manual Pearson correlation).

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

            • A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows discarding or select specific trials for individual subjects.
            • A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            • The name of a single trial. This will select the given trial for all subjects.
            • `None` (default). In that case, all trials will be considered.

        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and `trials` is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]}`, the analysis will run on the trials that intersect both requirements, i.e..
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    series: str, optional
        Defines the series that divide the data for comparison. This value can take any of the column names from the
        dataframe (apart from the values indicated in sequence_measure and audio_measure). For instance, if `group` is
        selected, the correlation will be calculated and plotted for each individual group of the dataframe.

    average: str or None, optional
        Defines if an average correlation is returned. This parameter can be:
            • ``"subject"``: the correlation is calculated for each subject and averaged across all subjects.
            • ``"trial"``: the correlation is calculated for each trial and averaged across all trials.
            • ``None``: the correlation is calculated for the whole dataset.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    audio_measure: str, optional
        The measure of the audio, can be either:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the audio data in the dataframe.

    correlation_with : str
        The joint label or audio measure to correlate against (default: ``"envelope"``).

    return_values : str
        Defines which values are returned and plotted. This parameter can be:

            • ``"average"`` or ``"raw"``: the correlation is returned, averaged across subjects, trials or the whole
              dataset, depending on the value for the parameter ``average``.
            • ``"z-score"`` (default): z-scores are returned, calculated against an average of randomly permuted
              arrays.

    permutation_level : str
        This determines how permutations are applied:
            • `"whole"`: permutations are done on the pooled data.
            • `"individual"`: permutations are done separately for each subject or trial.
            • ``None``: no permutations are calculated. This value is not allowed if `return_values == "z-scores"`.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_level` is set to ``"whole"`` or
        ``"individual"``. An average of the calculated random permutations is then calculated, in order to calculate
        a Z-score for the correlation.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, used to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance, and to perform the correlation.

    include_audio: bool, optional
        Whether to include the audio in the power spectrum calculation and plot. Default: `False`.

    random_seed: int, optional
        Sets a fixed seed for the random number generator. Only used if random permutations are computed.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Returns
    -------
    dict
        A nested dictionary containing the average correlation values for each series and each joint.
        Structure: {series_value: {joint_label: average_correlation_value}}.

    dict
        A nested dictionary containing the standard deviation of correlation values for each series and joint.
        Structure: {series_value: {joint_label: std_deviation_value}}.

    dict, optional
        A nested dictionary containing the Z-scores of the correlation values, computed as:
        (average - mean of random permutations) / std of permutations.
        Structure: {series_value: {joint_label: z_score_value}}.

    dict, optional
        A nested dictionary containing the p-values of the z-scores.
    """

    return _common_analysis(experiment_or_dataframe=experiment_or_dataframe, analysis="correlation", method=method,
                            group=group, condition=condition, subjects=subjects, trials=trials, series=series,
                            average=average, return_values=return_values, permutation_level=permutation_level,
                            number_of_randperms=number_of_randperms, sequence_measure=sequence_measure,
                            audio_measure=audio_measure, target_feature=correlation_with,
                            sampling_frequency=sampling_frequency, include_audio=include_audio,
                            random_seed=random_seed, verbosity=verbosity, **kwargs)

def coherence(experiment_or_dataframe, group=None, condition=None, subjects=None, trials=None, series=None,
              average="subject", sequence_measure="distance", audio_measure="envelope", coherence_with="envelope",
              return_values="z-scores", permutation_level="whole", number_of_randperms=1000, sampling_frequency=50,
              specific_frequency=None, freq_atol=1e-8, step_segments=0.25, include_audio=False, random_seed=None,
              color_line=None, width_line=1, verbosity=1, **kwargs):
    """Calculates and plots the coherence between one metric derived from the sequences, and the same metric from a
    given joint, or another metric derived from the corresponding audio clips.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

            • A :class:`Experiment` instance, containing the full dataset to be analyzed.
            • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
              generally generated from :meth:`Experiment.get_dataframe()`.
            • The path of a file containing a pandas DataFrame, generally generated from
              :class:`Experiment.save_dataframe()`.
            • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

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

            • A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows discarding or select specific trials for individual subjects.
            • A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            • The name of a single trial. This will select the given trial for all subjects.
            • `None` (default). In that case, all trials will be considered.

        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and `trials` is set on `{"sub_001": ["trial_001",
            "trial_002"], "sub_004": ["trial_001"]}`, the analysis will run on the trials that intersect both
            requirements, i.e., trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    series: str, optional
        Defines the series that divide the data for comparison. This value can take any of the column names from the
        dataframe (apart from the values indicated in sequence_measure and audio_measure). For instance, if `group` is
        selected, the coherence will be calculated and plotted for each individual group of the dataframe.

    average: str or None, optional
        Defines if an average coherence is returned. This parameter can be:
            • ``"subject"``: the coherence is calculated for each subject and averaged across all subjects.
            • ``"trial"``: the coherence is calculated for each trial and averaged across all trials.
            • ``None``: the coherence is calculated for the whole dataset.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the sequence data in the dataframe.

    audio_measure: str, optional
        The measure of the audio, can be either:

            • ``"audio"``, for the original sample values.
            • ``"envelope"`` (default)
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``

        .. note::
            This parameter will be used to generate a dataframe if the parameter `experiment_or_dataframe` is an
            Experiment instance. In any other case, this parameter **has to be equal** to the title of the column
            containing the audio data in the dataframe.

    coherence_with : str
        The joint label or audio measure to correlate against (default: ``"envelope"``).

    return_values : str
        Defines which values are returned and plotted. This parameter can be:

            • ``"average"`` or ``"raw"``: the coherence is returned, averaged across subjects, trials or the whole
              dataset, depending on the value for the parameter ``average``.
            • ``"z-score"`` (default): z-scores are returned, calculated against an average of randomly permuted
              arrays.

    permutation_level : str
        This parameter determines how permutations are applied:
            • `"whole"`: permutations are done on the pooled data.
            • `"individual"`: permutations are done separately for each subject or trial.
            • ``None``: no permutations are calculated. This value is not allowed if `return_values == "z-scores"`.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_level` is set to ``"whole"`` or
        ``"individual"``. An average of the calculated random permutations is then calculated, in order to calculate
        a Z-score for the coherence.

    sampling_frequency: int or float, optional
        The sampling frequency of the sequence and audio measures, used to resample the data when generating the
        dataframe, if the parameter `experiment_or_dataframe` is an Experiment instance, and to perform the coherence.

    specific_frequency: int or float, optional
        If specified, the function will return the coherence values for the specified frequency alone, and will display
        a silhouette plot instead of a body graph.

    freq_atol: float|int, optional
        The absolute tolerance of the frequency set on ``specific_frequency`` (default: 1e-8). If set, the function
        will look for the closest matching frequency in the range ``[specific_frequency - freq_atol,
        specific_frequency + freq_atol]``.

    step_segments: int or float, optional
        Defines how large each frequency segment will be for the analysis. If set on 0.25 (default), the coherence
        will be calculated at intervals of 0.25 Hz.

    include_audio: bool, optional
        Whether to include the audio in the power spectrum calculation and plot. Default: `False`.

    random_seed: int, optional
        Sets a fixed seed for the random number generator. Only used if ``permutation_level`` is set.

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

    return _common_analysis(experiment_or_dataframe=experiment_or_dataframe, analysis="coherence", method=None,
                            group=group, condition=condition, subjects=subjects, trials=trials, series=series,
                            average=average, return_values=return_values, permutation_level=permutation_level,
                            number_of_randperms=number_of_randperms, sequence_measure=sequence_measure,
                            audio_measure=audio_measure, target_feature=coherence_with,
                            sampling_frequency=sampling_frequency, specific_frequency=specific_frequency,
                            freq_atol=freq_atol, include_audio=include_audio, random_seed=random_seed,
                            color_line=color_line, width_line=width_line, verbosity=verbosity,
                            step_segments=step_segments, **kwargs)


def pca(experiment_or_dataframe, n_components, group=None, condition=None, subjects=None, trials=None,
        sequence_measure="distance", audio_measure="envelope", include_audio=False, sampling_frequency=50,
        show_graph=True, selected_components=None, nan_behaviour="ignore", verbosity=1):
    """Performs a principal component analysis (PCA) on the measures from the experiment, reducing the dimensionality
    of the data. Each joint_label is used as a feature for the PCA, and, if specified, the audio measure too.
    Relies on the PCA function from
    `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`__.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        • A :class:`Experiment` instance, containing the full dataset to be analyzed.
        • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        • The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

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

            • A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows discarding or select specific trials for individual subjects.
            • A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            • The name of a single trial. This will select the given trial for all subjects.
            • `None` (default). In that case, all trials will be considered.

        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and `trials` is set on `{"sub_001": ["trial_001",
            "trial_002"], "sub_004": ["trial_001"]}`, the analysis will run on the trials that intersect both
            requirements, i.e., trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
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
    pca_ = PCA(n_components=n_components)
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
    pca_result = pca_.fit_transform(data_matrix)

    if show_graph:
        _plot_components(pca_result, pca_.components_, joint_labels, "PCA", selected_components)

    return pca_result


def ica(experiment_or_dataframe, n_components, group=None, condition=None, subjects=None, trials=None,
        sequence_measure="distance", audio_measure="envelope", include_audio=False, sampling_frequency=50,
        show_graph=True, selected_components=None, nan_behaviour="ignore", verbosity=1):
    """Performs an independent component analysis (ICA) on the measures from the experiment, trying to separate them
    into subcomponents. Relies on the fastICA function from
    `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html>`__.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        • A :class:`Experiment` instance, containing the full dataset to be analyzed.
        • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        • The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

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

            • A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows discarding or select specific trials for individual subjects.
            • A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            • The name of a single trial. This will select the given trial for all subjects.
            • `None` (default). In that case, all trials will be considered.

        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and `trials` is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]}`, the analysis will run on the trials that intersect both requirements, i.e.,
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
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
    ica_ = FastICA(n_components=n_components)
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
    ica_result = ica_.fit_transform(data_matrix)

    if show_graph:
        _plot_components(ica_result, ica_.components_, joint_labels, "ICA", selected_components)

    return ica_result


def mutual_information(experiment_or_dataframe, group=None, condition=None, subjects=None, trials=None,
                       series=None, average="subject", include_randperm="whole", sequence_measure="distance",
                       regression_with="envelope", sampling_frequency=50, nan_behaviour="ignore", verbosity=1,
                       **kwargs):
    """Performs a mutual information regression between the sequence measure and the audio. Relies on
    `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.mutual_info_regression.html>`__.

    ..versionadded:: 2.0

    Parameters
    ----------
    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any).
        This parameter can be:

        • A :class:`Experiment` instance, containing the full dataset to be analyzed.
        • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        • The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

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

            • A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows discarding or select specific trials for individual subjects.
            • A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            • The name of a single trial. This will select the given trial for all subjects.
            • `None` (default). In that case, all trials will be considered.

        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and `trials` is set on `{"sub_001": ["trial_001",
            "trial_002"], "sub_004": ["trial_001"]}`, the analysis will run on the trials that intersect both
            requirements, i.e., trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

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

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
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

        • A :class:`Experiment` instance, containing the full dataset to be analyzed.
        • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        • The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    sequence_measure: str, optional
        The measure used for each sequence instance, can be either:

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters, default)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
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


def _get_dataframe_from_requirements(dataframe, group=None, condition=None, subjects=None, trials=None, verbosity=1):
    """Returns a sub-dataframe containing only the data where the group, condition, subjects and trails match
    the given parameters.

    .. versionadded:: 2.0

    Parameters
    ----------
    dataframe: pandas.DataFrame
        A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
        generally generated from :meth:`Experiment.get_dataframe()`.

    group: list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.subject.Subject.group` attribute does not match the value or values provided for this
        parameter. Otherwise, if this parameter is set on `None` (default), subjects from all groups will be considered.

    condition: list(str), str or None
        If specified, the analysis will discard the trials whose
        :attr:`~krajjat.classes.trial.Trial.condition` attribute does not match the value or values provided for this
        parameter. Otherwise, if this parameter is set on `None` (default), all trials will be considered.

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

            • A dictionary where each key is a subject name, and each value is a list containing trial names. This
              allows discarding or select specific trials for individual subjects.
            • A list where each element is a trial name. This will select only the trials matching the given name,
              for each subject.
            • The name of a single trial. This will select the given trial for all subjects.
            • `None` (default). In that case, all trials will be considered.

        This parameter can be combined with the other parameters to select specific subjects or conditions.

        ..note ::
            In the case where at least two of the parameters `group`, `condition`, `subjects` or `trials` are set,
            the selected trials will be the ones that match all the selected categories. For example, if `subjects`
            is set on `["sub_001", "sub_002", "sub_003"]` and `trials` is set on `{"sub_001": ["trial_001", "trial_002"],
            "sub_004": ["trial_001"]}`, the analysis will run on the trials that intersect both requirements, i.e.,
            trials 1 and 2 for subject 1. Trials from subjects 2, 3 and 4 will be discarded.

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
        A dataframe, containing a subset from the original dataframe.
    """

    original_size = len(dataframe.index)
    removed = []

    if group is not None:
        if type(group) is list:
            dataframe = dataframe.loc[dataframe["group"].isin(group)]
            removed.append("groups")
        elif type(group) is str:
            dataframe = dataframe.loc[dataframe["group"] == group]
            removed.append("group")

    if condition is not None:
        if type(condition) is list:
            dataframe = dataframe.loc[dataframe["condition"].isin(condition)]
            removed.append("conditions")
        elif type(condition) is str:
            dataframe = dataframe.loc[dataframe["condition"] == condition]
            removed.append("condition")

    if subjects is not None:
        if type(subjects) is list:
            dataframe = dataframe.loc[dataframe["subject"].isin(subjects)]
            removed.append("subjects")
        elif type(subjects) is str:
            dataframe = dataframe.loc[dataframe["subject"] == subjects]
            removed.append("subject")

    if trials is not None:
        if type(trials) is dict:
            new_dataframe = []
            for subject in trials.keys():
                dataframe_subject = dataframe.loc[dataframe["subject"] == subject]
                if type(trials[subject]) is str:
                    trials[subject] = [trials[subject]]
                dataframe_trials = dataframe_subject[dataframe_subject["trial"].isin(trials[subject])]
                new_dataframe.append(dataframe_trials)
            dataframe = pd.concat(new_dataframe, ignore_index=True)
        elif type(trials) is list:
            dataframe = dataframe.loc[dataframe["trial"].isin(trials)]
        elif type(trials) is str:
            dataframe = dataframe.loc[dataframe["trial"] == trials]
        removed.append("trials")

    if verbosity > 0 and len(removed) > 0:
        print(f"\tThe dataframe was reduced to preserve the requested {','.join(removed)}.\n\tThe dataframe "
              f"originally had {original_size} rows, and now has {len(dataframe.index)} rows.")

    return dataframe
