"""These functions allow finding significant relationships between movements, or between movements and audio properties.
"""

import pandas as pd
import numpy as np
from scipy import signal
from tqdm import tqdm
from datetime import datetime as dt
from numbers import Number
import itertools

from krajjat import Sequence, Trial, Subject
from krajjat.classes.exceptions import ModuleNotFoundException
from krajjat.classes.experiment import Experiment
from krajjat.classes.graph_element import Graph, GraphPlot
from krajjat.classes.results import Results
from krajjat.classes.analysis_parameters import AnalysisParameters
from krajjat.plot_functions import plot_silhouette, plot_body_graphs, _plot_components
from krajjat.tool_functions import read_pandas_dataframe, find_closest_value_index, set_nested_dict, \
    has_nested_key


def _common_analysis(**kwargs):
    """Common function to perform a multimodal analysis of the motion capture and audio signals. This function can
    perform power spectrum, correlation and coherence analyses, at the subject level or the trial level, before
    plotting a graph or a silhouette and returning the results.

    .. versionadded:: 2.0

    This internal function is designed to be called by specific analysis wrappers like `power_spectrum()`,
    `correlation()`, and `coherence()` and is not intended to be called directly.

    Returns
    -------
    Results
        A Results instance containing the analysis parameters and the results as attributes:

            • ``frequencies`` contains the frequencies corresponding to the results, if the analysis is in the
               frequency domain.
            • ``averages`` contains the results of the analysis, averaged across the specified level of averaging.
            • ``stds`` contains the standard deviations of the results.
            • ``averages_perm`` contains the averages of the random permutations, if they were computed.
            • ``stds`` contains the standard deviations of the random permutations.
            • ``z_scores`` contains the z-scores of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``p_values`` contains the p-values of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``plot_dictionary`` contains the plot dictionary that can be directly passed to ``plot_silhouette`` or
              ``plot_body_graphs``.
    """
    time_start = dt.now()

    params = AnalysisParameters(**kwargs)

    # Load pingouin for correlation
    pg = None
    if params.analysis == "correlation" and params.method == "pingouin":
        try:
            import pingouin as pg
        except ImportError:
            raise ModuleNotFoundException("pingouin", "calculate the correlation")

    if params.analysis == "mutual information":
        try:
            from sklearn.feature_selection import mutual_info_regression as mi
            sc = None
            if params.mi_scale == "standard":
                from sklearn.preprocessing import StandardScaler
                sc = StandardScaler()
            elif params.mi_scale == "minmax":
                from sklearn.preprocessing import MinMaxScaler
                sc = MinMaxScaler()
        except ImportError:
            raise ModuleNotFoundException("sklearn", "perform a mutual information regression")

    # Get the full dataframe
    dataframe = _prepare_dataframe(params)
    params._prepare_values(dataframe)
    params._validate_lags(dataframe)

    # Create the dictionaries that will contain the values
    plot_dictionary = {}
    analysis_values = {}
    randperm_values = {}
    frequencies = None

    if params.verbosity > 0:
        print(f"\nComputing the {params.analysis}...")

    # Precompute tqdm iterations
    progress_bar = tqdm(total=_count_tqdm_iterations(params, 1), desc=params.analysis.capitalize(), ncols=80,
                        disable=params.verbosity != 1, colour="#ffcc00",
                        bar_format="{l_bar}{bar} · {elapsed}<{remaining}")

    for target_measure in params.target_measures:

        # Print of the current analysis
        if params.verbosity > 1:
            message = f"\tComputing the {params.analysis}"
            if params.analysis != "power spectrum":
                message += f" to the "
                if target_measure[1] == "Audio":
                    message += f"{target_measure[1]} of the audio"
                else:
                    message += f"{target_measure[1]} of the {target_measure[0]} joint"
            print(message + "...")

        for measure in params.measures:

            if params.measure_to_modality[measure] == "audio" and not params.include_audio:
                continue

            if params.verbosity > 1:
                print("\t\t" + measure)

            # Filter the rows having the proper measures
            df_measure = dataframe[(dataframe["measure"] == measure)]
            keys_measure = df_measure[["subject", "trial", "timestamp"]].drop_duplicates()

            # Get the labels depending on the current modality of the measure
            if params.measure_to_modality[measure] == "audio":
                labels_modality = ["Audio"]
            else:
                labels_modality = params.labels_mocap

            # If the analysis is not power spectrum, we need a target
            if params.analysis != "power spectrum":
                df_target = dataframe[(dataframe["measure"] == target_measure[1]) & (dataframe["label"] == target_measure[0])]
                keys_target = df_target[["subject", "trial", "timestamp"]].drop_duplicates()

                rows_before = len(df_measure.index) + len(df_target.index)

                common_keys = pd.merge(keys_measure, keys_target, on=["subject", "trial", "timestamp"], how="inner")
                df_measure = pd.merge(df_measure, common_keys, on=["subject", "trial", "timestamp"], how="inner")
                df_target = pd.merge(df_target, common_keys, on=["subject", "trial", "timestamp"], how="inner")

                if params.verbosity > 1:
                    print(f"\t\tDropped {rows_before - len(df_measure.index) - len(df_target.index)} rows with " +
                          f"unmatched timestamps.")

            for series_value in params.series_values:
                if params.verbosity > 1:
                    print("\t\t\t" + series_value)

                # We get the corresponding dataframe
                if series_value == "Full dataset":
                    df_measure_series = df_measure
                    if params.analysis != "power spectrum":
                        df_measure_target = df_target
                else:
                    df_measure_series = df_measure.loc[df_measure[params.series] == series_value]
                    if params.analysis != "power spectrum":
                        df_measure_target = df_target.loc[df_target[params.series] == series_value]

                # For each subject/trial
                for individual in params.individuals:

                    # If the average is set on the same as series, we skip the individuals that are not the series value
                    if params.average == params.series and individual not in (series_value, "All"):
                        continue

                    if params.verbosity > 1:
                        print("\t\t\t\t" + individual)

                    # We select the rows with the subject if average is set the same as the series
                    if params.series == "subject" and params.average == "subject":
                        df_measure_ind = df_measure_series[df_measure_series["subject"] == individual]
                        if params.analysis != "power spectrum":
                            df_target_ind = df_measure_target[df_measure_target["subject"] == individual]
                    else:
                        if individual == "All":
                            df_measure_ind = df_measure_series
                        else:
                            df_measure_ind = df_measure_series[df_measure_series[params.average] == individual]
                        if params.analysis != "power spectrum":
                            if individual == "All":
                                df_target_ind = df_measure_target
                            else:
                                df_target_ind = df_measure_target[df_measure_target[params.average] == individual]

                    # Mappings for the label permutations
                    if params.compute_permutations and params.permutation_method == "label":
                        labels_mappings = []
                        for _ in range(params.number_of_randperms):
                            shuffled_labels = params.rng.permutation(labels_modality)  # e.g. ["HandLeft", "Head", "HandRight"]
                            labels_mappings.append(dict(zip(labels_modality, shuffled_labels)))

                    for label in labels_modality:
                        if params.verbosity > 1:
                            print("\t\t\t\t\t" + label)

                        measure_values = df_measure_ind[df_measure_ind["label"] == label]["value"].to_numpy()

                        if params.analysis != "power spectrum":
                            target_values = df_target_ind["value"].to_numpy()
                            if target_values.size == 0:
                                raise Exception("The target values are empty. Please ensure that the target measure "
                                                "is valid, and that all subjects have an entry for the each series.")
                            if target_values.size != measure_values.size:
                                raise ValueError(f"The length of the measure values {measure_values.size} is not "
                                                 f"equal to the length of the target values {target_values.size}. "
                                                 f"Please check the dataframe.")
                        else:
                            target_values = None

                        for lag in params.lags:

                            if params.verbosity > 1:
                                print("\t\t\t\t\t\tLag: " + str(lag) + " s")

                            sample = int(np.round(lag * params.sampling_rate))
                            n = measure_values.size

                            if sample > 0 :
                                measure_values_lag = measure_values[:n - sample]
                            elif sample == 0:
                                measure_values_lag = measure_values
                            else:
                                measure_values_lag = measure_values[-sample:]

                            if target_values is not None:
                                if sample > 0:
                                    target_values_lag = target_values[sample:]
                                elif sample == 0:
                                    target_values_lag = target_values
                                else:
                                    target_values_lag = target_values[:n + sample]

                            if params.analysis == "power spectrum":
                                frequencies, results = _compute_power_spectrum(params.method, measure_values_lag, frequencies,
                                                                               params.sampling_rate)

                            elif params.analysis == "correlation":
                                results = _compute_correlation(pg, params.method, measure_values_lag, target_values_lag)

                            elif params.analysis == "coherence":
                                frequencies, results = _compute_coherence(measure_values_lag, target_values_lag,
                                                                          frequencies, params.sampling_rate, params.nperseg)

                            elif params.analysis == "mutual information":
                                results = _compute_mutual_information(mi, sc, measure_values_lag, target_values_lag,
                                                                      params.random_seed, params.n_neighbors,
                                                                      params.mi_scale, params.mi_direction)

                            else:
                                raise Exception("Invalid value for the parameter analysis. Choose either 'power spectrum', "
                                                "'correlation', 'coherence' or 'mutual information'.")

                            # noinspection PyUnboundLocalVariable
                            set_nested_dict(analysis_values, [target_measure, measure, series_value, individual, label, lag],
                                            results)

                            if params.compute_permutations:
                                if not has_nested_key(randperm_values, [target_measure, measure, series_value, individual, label, lag]):
                                    set_nested_dict(randperm_values, [target_measure, measure, series_value, individual, label, lag], [], False)

                                for p in range(params.number_of_randperms):

                                    if params.permutation_method == "value":
                                        perm = params.rng.permutation(measure_values_lag)
                                    elif params.permutation_method == "label":
                                        random_label = labels_mappings[p][label]
                                        perm = df_measure_ind[df_measure_ind["label"] == random_label]["value"].to_numpy()
                                        if sample > 0:
                                            perm = perm[:n - sample]
                                        elif sample == 0:
                                            perm = perm
                                        else:
                                            perm = perm[-sample:]
                                    elif params.permutation_method == "shift":
                                        if len(measure_values_lag) <= 1:
                                            perm = measure_values_lag.copy()
                                        else:
                                            shift = params.rng.integers(1, len(measure_values_lag))
                                            perm = np.roll(measure_values_lag, shift)
                                    elif params.permutation_method == "phase":
                                        perm = _phase_randomize(measure_values_lag, params.rng)

                                    if params.analysis == "power spectrum":
                                        _, perm_values = _compute_power_spectrum(params.method, perm, frequencies,
                                                                                 params.sampling_rate)

                                    elif params.analysis == "correlation":
                                        perm_values = _compute_correlation(pg, params.method, perm, target_values_lag)

                                    elif params.analysis == "coherence":
                                        _, perm_values = _compute_coherence(perm, target_values_lag, frequencies,
                                                                            params.sampling_rate, params.nperseg)

                                    elif params.analysis == "mutual information":
                                        perm_values = _compute_mutual_information(mi, sc, perm, target_values_lag,
                                                                                  params.random_seed, params.n_neighbors,
                                                                                  params.mi_scale, params.mi_direction)

                                    set_nested_dict(randperm_values,
                                                    [target_measure, measure, series_value, individual, label, lag],
                                                    perm_values, True)

                            progress_bar.update(1)

    progress_bar.close()

    params._get_specific_frequencies(frequencies)
    params._generate_silhouette_titles(frequencies)

    if params.verbosity > 1:
        if params.result_type == "z-scores":
            print("\nCalculating the z-scores...")
        elif params.result_type == "average":
            print("\nCalculating the averages...")

    averages = {}
    stds = {}
    z_scores = {}
    p_values = {}
    averages_perm = {}
    stds_perm = {}
    max_value = 0

    tqdm_title = "Z-scores computation" if params.result_type == "z-scores" else "Averages computation"
    progress_bar = tqdm(total=_count_tqdm_iterations(params, 2), desc=tqdm_title, ncols=80,
                        disable=params.verbosity != 1, colour="#ff8800",
                        bar_format="{l_bar}{bar} · {elapsed}<{remaining}")

    for target_measure in params.target_measures:

        if params.verbosity > 1:
            message = f"\tComputing the {params.result_type}"
            if params.analysis != "power spectrum":
                message += f" to the "
                if target_measure[1] == "Audio":
                    message += f"{target_measure[0]} of the audio"
                else:
                    message += f"{target_measure[1]} of the {target_measure[0]} joint"
            print(message + "...")

        for measure in params.measures:

            if params.measure_to_modality[measure] == "audio" and not params.include_audio:
                continue

            if params.verbosity > 1:
                print("\t\t" + measure)

            # For each series
            for series_value in params.series_values:
                if params.verbosity > 1:
                    print("\t\t\t" + series_value)

                if params.measure_to_modality[measure] == "audio":
                    labels_modality = ["Audio"]
                else:
                    labels_modality = params.labels_mocap

                for label in labels_modality:
                    if params.verbosity > 1:
                        print("\t\t\t\t" + label)

                    for lag in params.lags:
                        if params.verbosity > 1:
                            print("\t\t\t\t\tLag: " + str(lag) + " s")

                        if params.specific_frequency is None and params.analysis not in ["correlation", "mutual information"] and label not in plot_dictionary.keys():
                            plot_dictionary[label] = Graph()

                        if params.average == params.series and params.average is not None:
                            vals = [analysis_values[target_measure][measure][series_value][series_value][label][lag]]
                        else:
                            vals = [analysis_values[target_measure][measure][series_value][ind][label][lag] for ind in params.individuals]

                        expected_length = None
                        for val in vals:
                            if expected_length is None:
                                if isinstance(val, Number):
                                    expected_length = 1
                                else:
                                    expected_length = len(val)
                            else:
                                if ((isinstance(val, Number) and expected_length != 1) or
                                        (not(isinstance(val, Number)) and len(val) != expected_length)):
                                    raise Exception("At least one element does not have the same length as the others.")

                        avg = np.nanmean(vals, axis=0)
                        std = np.nanstd(vals, axis=0)

                        if params.compute_permutations:
                            if params.analysis in ["correlation", "mutual information"]:
                                perms_stack = np.stack([np.asarray(randperm_values[target_measure][measure][series_value][ind][label][lag]) for ind in params.individuals], axis=0)
                                perms = np.nanmean(perms_stack, axis=0)
                            else:
                                perms_stack = np.stack([np.stack(randperm_values[target_measure][measure][series_value][ind][label][lag], axis=0) for ind in params.individuals], axis=0)
                                perms = np.nanmean(perms_stack, axis=0)
                                perms = perms[np.all(np.isfinite(perms), axis=1)]

                            if params.result_type == "z-scores":

                                if perms.size == 0:
                                    p = np.full_like(avg, np.nan)
                                    z = np.full_like(avg, np.nan)

                                else:
                                    avg_perms = np.nanmean(perms, axis=0)
                                    sd_perms = np.nanstd(perms, axis=0)
                                    sd_perms_safe = np.where(sd_perms == 0, np.inf, sd_perms)
                                    z = (avg - avg_perms) / sd_perms_safe
                                    p = (np.sum(np.abs(perms - avg_perms) >= np.abs(avg - avg_perms), axis=0) + 1) / (perms.shape[0] + 1)

                                set_nested_dict(z_scores, [target_measure, measure, series_value, label, lag], z)
                                set_nested_dict(p_values, [target_measure, measure, series_value, label, lag], p)

                            else:
                                set_nested_dict(averages_perm, [target_measure, measure, series_value, label, lag], np.nanmean(perms, axis=0))
                                set_nested_dict(stds_perm, [target_measure, measure, series_value, label, lag], np.nanstd(perms, axis=0))

                        else:
                            perms = []

                        set_nested_dict(averages, [target_measure, measure, series_value, label, lag], avg)
                        set_nested_dict(stds, [target_measure, measure, series_value, label, lag], std)

                        if params.plot_type == "silhouette":
                            key = label if params.measure_to_modality[measure] == "mocap" else "Audio"

                            if key != "Audio":
                                if key not in plot_dictionary.keys():
                                    plot_dictionary[key] = []
                                for i in range(params.nb_silhouettes_per_series):
                                    if params.specific_frequency is not None:
                                        if params.result_type == "z-scores":
                                            plot_dictionary[key].append(z_scores[target_measure][measure][series_value][label][lag][params.index_freqs[i]])
                                        else:
                                            plot_dictionary[key].append(averages[target_measure][measure][series_value][label][lag][params.index_freqs[i]])
                                    else:
                                        if params.result_type == "z-scores":
                                            plot_dictionary[key].append(z_scores[target_measure][measure][series_value][label][lag])
                                        else:
                                            plot_dictionary[key].append(averages[target_measure][measure][series_value][label][lag])

                        else:
                            graph_labels = []
                            if len(params.target_measures) > 1:
                                graph_labels.append(target_measure.title())
                            if len(params.measures) > 1:
                                graph_labels.append(measure.title())
                            graph_labels.append(series_value.title())

                            graph_label = " ".join(graph_labels)

                            if params.result_type == "z-scores":
                                graph_plot = GraphPlot(frequencies, z_scores[target_measure][measure][series_value][label][lag], line_width=params.width_line,
                                                       color=params.color_line_series[target_measure][measure][series_value][lag], label=graph_label)
                                plot_dictionary[label].add_graph_plot(graph_plot)
                            else:
                                graph_plot = GraphPlot(frequencies, averages[target_measure][measure][series_value][label][lag],
                                                       stds[target_measure][measure][series_value][label][lag], line_width=params.width_line,
                                                       color=params.color_line_series[target_measure][measure][series_value][lag],
                                                       label=graph_label)
                                plot_dictionary[label].add_graph_plot(graph_plot)

                                if params.compute_permutations:
                                    graph_plot = GraphPlot(frequencies, averages_perm[target_measure][measure][series_value][label][lag],
                                                           stds_perm[target_measure][measure][series_value][label][lag], line_width=params.width_line,
                                                           color=params.color_line_perm[target_measure][measure][series_value][lag],
                                                           label=graph_label + " (avg. perm.)")
                                    plot_dictionary[label].add_graph_plot(graph_plot)

                        progress_bar.update(1)

            for label in plot_dictionary.keys():
                if isinstance(plot_dictionary[label], Graph):
                    if params.label_to_modality[label] == "mocap":
                        for plot in plot_dictionary[label].plots:
                            if plot.sd is None:
                                max_value = max(max_value, np.nanmax(plot.y), np.nanmax(plot.y))
                            else:
                                max_value = max(max_value, np.nanmax(plot.y - plot.sd), np.nanmax(plot.y + plot.sd))
                else:
                    max_value = max(max_value, max(plot_dictionary[label]))

    progress_bar.close()

    series_p_values = {}
    series_z_scores = {}

    if params.signif_target == "series":
        series_a, series_b = params.series_values
        for target_measure in params.target_measures:
            for measure in params.measures:
                if params.measure_to_modality[measure] == "audio" and not params.include_audio:
                    continue
                labels_modality = ["Audio"] if params.measure_to_modality[measure] == "audio" else params.labels_mocap
                for label in labels_modality:
                    for lag in params.lags:
                        vals_series_a = []
                        vals_series_b = []
                        inds_series_a = []
                        inds_series_b = []
                        for ind in params.individuals:
                            if has_nested_key(analysis_values, [target_measure, measure, series_a, ind, label, lag]):
                                vals_series_a.append(analysis_values[target_measure][measure][series_a][ind][label][lag])
                                inds_series_a.append(ind)
                            if has_nested_key(analysis_values, [target_measure, measure, series_b, ind, label, lag]):
                                vals_series_b.append(analysis_values[target_measure][measure][series_b][ind][label][lag])
                                inds_series_b.append(ind)

                        # match pairing
                        common = [ind for ind in inds_series_a if ind in inds_series_b]
                        paired = len(common) > 0

                        # If some individuals are in common between the two series, it's a paired test
                        if paired:
                            vals_inds_series_a = np.stack([analysis_values[target_measure][measure][series_a][ind][label][lag] for ind in common])
                            vals_inds_series_b = np.stack([analysis_values[target_measure][measure][series_b][ind][label][lag] for ind in common])
                            ind_diffs = (vals_inds_series_a - vals_inds_series_b)
                            obs = np.nanmean(ind_diffs, axis=0)
                            perms = []
                            for _ in range(params.number_of_randperms):
                                flip = params.rng.integers(0, 2, size=ind_diffs.shape[0]) * 2 - 1
                                perms.append(
                                    np.nanmean(ind_diffs * flip[:, None] if hasattr(obs, "__len__") else ind_diffs * flip, axis=0))
                            perms = np.stack(perms, axis=0)

                        # Otherwise, unpaired test
                        else:
                            vals_inds_series_a = np.stack(vals_series_a) if len(vals_series_a) > 0 else np.empty((0,))
                            vals_inds_series_b = np.stack(vals_series_b) if len(vals_series_b) > 0 else np.empty((0,))
                            if vals_inds_series_a.size == 0 or vals_inds_series_b.size == 0: continue
                            obs = np.nanmean(vals_inds_series_a, axis=0) - np.nanmean(vals_inds_series_b, axis=0)
                            perms = []
                            n_inds_series_a = vals_inds_series_a.shape[0]
                            n_inds_series_b = vals_inds_series_b.shape[0]
                            pool = np.concatenate([vals_inds_series_a, vals_inds_series_b], axis=0)
                            for _ in range(params.number_of_randperms):
                                idx = params.rng.permutation(pool.shape[0])
                                series_a_idx, series_b_idx = idx[:n_inds_series_a], idx[n_inds_series_a:]
                                perms.append(np.nanmean(pool[series_a_idx], axis=0) - np.nanmean(pool[series_b_idx], axis=0))
                            perms = np.stack(perms, axis=0)

                        # p and z for difference
                        if perms.size == 0:
                            p = np.full_like(obs, np.nan)
                            z = np.full_like(obs, np.nan)
                        else:
                            avg_perms = np.nanmean(perms, axis=0)
                            sd_perms = np.nanstd(perms, axis=0)
                            sd_perms_safe = np.where(sd_perms == 0, np.inf, sd_perms)
                            z = (obs - avg_perms) / sd_perms_safe
                            p = (np.sum(np.abs(perms - avg_perms) >= np.abs(obs - avg_perms), axis=0) + 1) / (perms.shape[0] + 1)
                        set_nested_dict(series_p_values, [target_measure, measure, (series_a, series_b), label, lag], p)
                        set_nested_dict(series_z_scores, [target_measure, measure, (series_a, series_b), label, lag], z)

        # Build contrast_ticks for plotting
        if params.plot_type == "body":
            alpha = params.signif_alpha[0] if isinstance(params.signif_alpha, list) else float(params.signif_alpha)
            contrast_ticks = {}
            for label, g in plot_dictionary.items():
                # pick any available target/measure/lag to source the p mask (first one is fine for overlay)
                # you can refine later; minimal viable overlay
                tm = list(series_p_values.keys())[0]
                meas = list(series_p_values[tm].keys())[0]
                pair = list(series_p_values[tm][meas].keys())[0]
                for lag in params.lags:
                    p = series_p_values[tm][meas][pair][label][lag]
                    if isinstance(p, np.ndarray) and p.size > 1:
                        mask = p < alpha
                        contrast_ticks.setdefault(label, {"x": frequencies, "mask": mask, "height_frac": 0.97})
            params.kwargs["contrast_ticks"] = contrast_ticks

    params._set_signif_graph_params()

    analysis_parameters = {"analysis": params.analysis, "method": params.method, "groups": params.groups,
                           "conditions": params.conditions, "subjects": params.subjects, "trials": params.trials,
                           "sequence_measures": params.sequence_measures, "audio_measures": params.audio_measures,
                           "target_measures": params.target_measures, "series": params.series,
                           "average": params.average, "series_values": params.series_values, "lags": params.lags,
                           "individuals": params.individuals, "labels": params.labels,
                           "labels_mocap": params.labels_mocap, "result_type": params.result_type,
                           "permutation_method": params.permutation_method,
                           "number_of_randperms": params.number_of_randperms, "random_seed": params.random_seed,
                           "specific_frequency": params.specific_frequency, "freq_atol": params.freq_atol,
                           "include_audio": params.include_audio, "color_line_series": params.color_line_series,
                           "color_line_perm": params.color_line_perm, "title": params.title,
                           "width_line": params.width_line, "verbosity": params.verbosity, "kwargs": params.kwargs}

    if params.plot_type == "silhouette":
        if params.verbosity > 0:
            print("\nShowing the silhouette plot...")
        plot_silhouette(plot_dictionary, title=params.title, max_scale=max_value, verbosity=params.verbosity,
                        **params.kwargs)

    else:
        if params.verbosity > 0:
            print("\nShowing the body graph...")
        plot_body_graphs(plot_dictionary, title=params.title, max_scale=max_value, **params.kwargs)

    if params.result_type == "z-scores":
        analysis_results = {"frequencies": frequencies, "averages": averages, "stds": stds, "z_scores": z_scores,
                            "p_values": p_values}
    else:
        if params.permutation_method is not None:
            analysis_results = {"frequencies": frequencies, "averages": averages, "stds": stds, "averages_perm":
                                averages_perm, "stds_perm": stds_perm, "z_scores": z_scores, "p_values": p_values}
        else:
            analysis_results = {"frequencies": frequencies, "averages": averages, "stds": stds}

    if params.signif_target == "series":
        analysis_results.update({
            "series_p_values": series_p_values,
            "series_z_scores": series_z_scores
        })

    return Results(analysis_parameters, analysis_results, plot_dictionary, dt.now(), dt.now() - time_start)


def power_spectrum(experiment_or_dataframe, method="welch", sampling_rate="auto", groups=None, conditions=None,
                   subjects=None, trials=None, sequence_measure="auto", audio_measure="auto", series=None, average=None,
                   lags=None, result_type="average", permutation_method=None, number_of_randperms=0, random_seed=None,
                   specific_frequency=None, freq_atol=0.1, include_audio=False, signif_style="threshold",
                   signif_alpha=0.05, signif_tail="1", signif_direction="up", color_line_series=None,
                   color_line_perm=None, title=None, width_line=1, verbosity=1, **kwargs):
    """Returns the power spectrum values for all the variables (joints and audio) of the given dataframe or experiment.
    The function also plots these power spectrum values.

    .. versionadded:: 2.0

    Parameters
    ----------

    General parameters
    ~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any)
        The input data to analyse. This parameter can be:

            • A :class:`Experiment` instance, containing the full dataset to be analysed.
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

    sampling_rate : int|str|float, optional
        Sampling rate of the signals. By default, this value is set on ``"auto"``: in that case, the sampling rate
        is inferred from the dataframes. Otherwise, this value must be equal to the one of the dataframe or the
        experiment object.

    Dataframe filtering
    ~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    groups : list(str)|str|None, optional
        Restricts the analysis to subjects with the specified groups. This parameter can be:

            • A single group.
            • A list of groups.
            • ``None`` (default): the dataframe will not be filtered by group.

    conditions : list(str)|str|None, optional
        Restricts the analysis to trials with the specified conditions. This parameter can be:

            • A single condition.
            • A list of conditions.
            • ``None`` (default): the dataframe will not be filtered by condition.

    subjects : list(str)|str|None, optional
        Restricts the analysis to the specified subjects. This parameter can be:

            • A single subject.
            • A list of subjects.
            • ``None`` (default): all subjects will be considered.

    trials : dict(str: list(str))|list(str)|str|None, optional
        Restricts the analysis to the specified trials. This parameter can be:

            • A single trial.
            • A list of trials.
            • A dictionary mapping subjects or groups to a list of trials.
            • ``None`` (default): all trials will be considered.

    Targets
    ~~~~~~~
    .. rubric:: Parameters

    sequence_measure : list(str)|str, optional
        The sequence measure(s) from the mocap modalities to include in the analysis (e.g., ``"velocity"``,
        ``"acceleration"``). If experiment_or_dataframe is or contains a dataframe, the specified measures must appear
        in its measure column. When provided as a list, each sequence measure is paired with each audio_measure to
        generate separate entries in both the results and the plot dictionary. By default, the value of this parameter
        is ``"auto"``: the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"mocap"``. This parameter can also take the following values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"``, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"``, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"``, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.

    audio_measure : list(str)|str, optional
        The audio measure(s) from the audio modality to include in the analysis (e.g., "envelope", "pitch"). If
        experiment_or_dataframe is or contains a dataframe, the specified measures must appear in its measure column.
        When provided as a list, each sequence measure is paired with each sequence_measure to generate separate
        entries in both the results and the plot dictionary. By default, the value of this parameter is ``"auto"``:
        the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"audio"``. The parameter can also be set on ``None`` if your Experiment does not
        have AudioDerivatives, or if you wish to ignore them. This parameter can also take the following values:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``.
            • ``"pitch"``.
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``.

    series : str|None, optional
        A column name from the dataframe to split data into subsets (e.g., `"group"`, `"condition"`, `"trial"`). Each
        subset will create a new entry in the results and the plot dictionary.

    average : str|None, optional
        Defines the level of averaging:

            • ``"subject"``: average across subjects.
            • ``"trial"``: average across trials.
            • ``None``: no averaging; the full dataset is used.

    lags: int|float|list(int|float)|None, optional
        Defines one or more lags (in seconds) to apply to the target feature in the analysis. A lag can be positive or
        negative. Provided lags are rounded to the closest timestamp value given the sampling rate (e.g., specifying
        a lag of 0.11 for a sampling rate of 10 Hz will result in the lag being rounded to 0.1).

    Result format
    ~~~~~~~~~~~~~
    .. rubric:: Parameters

    result_type : str, optional
        The type of the results computed and returned by the function. This parameter can be:

            • ``"average"`` (alternatives: ``"raw"``, ``"avg"``, default): in that case, the values plotted and
              returned will be the values computed during the analysis, averaged if ``"average"`` is set.
            • ``"z-scores"` (alternatives: ``"z"``, ``"zscores"``, ``"z-score"``, ``"zscore"``, ``"zeta"``): in that
              case, the values plotted will be the z-scores computed against the randomly permuted values. The
              parameters ``permutation_method`` and ``number_of_randperms`` must be set. Note that the returned Result
              instance will contain both the raw/average results and the z-scores.

    permutation_method: str|None, optional
        This parameter determines how permutations are applied:

            • `"value"`: the values of each time series are permuted, allowing to compare the signal against random
              noise.
            • `"label"`: permutations are done by randomly selecting values matching a label, to compare the labels
              between each other.
            • `"shift"`: permutations are done by shifting the time series values (rolling the last values to the
              beginning), allowing to preserve the phase spectrum but without the temporal alignment.
            • `"phase"`: permutations are done by randomizing each Fourier coefficient's phase, which keeps the
              amplitude spectrum but destroys the phase relationships.
            • ``None`` (default): no permutations are calculated. This value is not allowed if ``return_values ==
              "z-scores"``.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_method` is set. An average of the
        calculated random permutations is then calculated, in order to calculate a z-score.

    random_seed : int|None, optional
        Fixes the seed for reproducible random permutations. Default: ``None``: the random permutations will change
        on each execution.

    specific_frequency : float|list(float)|None, optional
        Frequency (or list of frequencies) to extract from the result. If set, silhouette plots are generated.

    freq_atol : float|int, optional
        Absolute tolerance for matching the specific frequency (default: 0.1).

    include_audio : bool, optional
        If ``True``, includes audio signals in the set of labels to analyse.

    Significance parameters
    ~~~~~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    signif_style: list(str) | str | None, optional
        The style of significance to show on the plot. This parameter can be one or more of the following:

            • ``"threshold"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show horizontal lines
              matching the significance threshold.
            • ``"shade"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show shades
              matching the significance threshold.
            • ``"markers"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show markers on the
              frequencies showing significance. This option is compatible with silhouette plots.
            • ``None`` (default): the significant values aren't shown.

    signif_alpha: list(float) | float, optional
        Significance threshold(s). Can be a single value (default: 0.05) or a list of values. If multiple thresholds
        are provided, each level is shown with a different marker according to ``signif_marker``.

    signif_tail: str | int, optional
        Whether the z-score test is one-tailed or two-tailed. This affects the significance threshold. Default: "1".

    signif_direction: str, optional
        The direction of the significance, if signif_tail is 1. By default, this value is set on ``"up"``, but it also
        can be set on ``"down"``.

    Plot parameters
    ~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    color_line_series : list|str|None, optional
        Color(s) to use when plotting time-frequency graphs. If this parameter is a list, a color will be
        attributed to each series. If this parameter is a string, the same color is attributed to all series. Each
        color can take a number of forms:

            • The `HTML/CSS name of a color <https://en.wikipedia.org/wiki/X11_color_names>`_ (e.g. ``"red"`` or
              ``"blanched almond"``),
            • The hexadecimal code of a color, starting with a number sign (``#``, e.g. ``"#ffcc00"`` or ``"#c0ffee"``).
            • The RGB or RGBA tuple of a color (e.g. ``(153, 204, 0)`` or ``(77, 77, 77, 255)``).

    color_line_perm: list|str|None, optional
        Color to use for the permutations when plotting time-frequency graphs. If this parameter is a list, a color
        will be attributed to each series. If this parameter is a string, the same color is attributed to all series.

    title: str|None, optional
        If set, the title of the plot. Otherwise, an automatic title will be generated.

    width_line : int|float
        Width of plotted lines.

    Other parameters
    ~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: optional
        Additional arguments passed to :func:`plot_functions.plot_silhouette` or
        :func:`plot_functions.plot_body_graphs`.

    Returns
    -------
    Results
        A Results instance containing the analysis parameters and the results as attributes:

            • ``frequencies`` contains the frequencies corresponding to the results, if the analysis is in the
               frequency domain.
            • ``averages`` contains the results of the analysis, averaged across the specified level of averaging.
            • ``stds`` contains the standard deviations of the results.
            • ``averages_perm`` contains the averages of the random permutations, if they were computed.
            • ``stds`` contains the standard deviations of the random permutations.
            • ``z_scores`` contains the z-scores of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``p_values`` contains the p-values of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``plot_dictionary`` contains the plot dictionary that can be directly passed to ``plot_silhouette`` or
              ``plot_body_graphs``.
    """

    return _common_analysis(experiment_or_dataframe=experiment_or_dataframe, analysis="power spectrum", method=method,
                            sampling_rate=sampling_rate, groups=groups, conditions=conditions, subjects=subjects,
                            trials=trials, sequence_measure=sequence_measure, audio_measure=audio_measure,
                            series=series, average=average, lags=lags, result_type=result_type,
                            permutation_method=permutation_method, number_of_randperms=number_of_randperms,
                            random_seed=random_seed, specific_frequency=specific_frequency, freq_atol=freq_atol,
                            include_audio=include_audio,  signif_style=signif_style,
                            signif_alpha=signif_alpha, signif_tail=signif_tail, signif_direction=signif_direction, color_line_series=color_line_series,
                            color_line_perm=color_line_perm, title=title, width_line=width_line, verbosity=verbosity,
                            **kwargs)

def correlation(experiment_or_dataframe, method="pingouin", sampling_rate="auto", groups=None, conditions=None,
                subjects=None, trials=None, sequence_measure="auto", audio_measure="auto", correlation_with="envelope",
                series=None, average=None, lags=None, result_type="average", permutation_method=None,
                number_of_randperms=0, random_seed=None, include_audio=False, signif_style="threshold",
                signif_alpha=0.05, signif_tail="1", signif_direction="up", verbosity=1, **kwargs):
    """Calculates and plots the correlation between one metric derived from the sequences, and the same metric from a
    given joint, or another metric derived from the corresponding audio clips.

    .. versionadded :: 2.0

    Parameters
    ----------

    General parameters
    ~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any)
        The input data to analyse. This parameter can be:

            • A :class:`Experiment` instance, containing the full dataset to be analysed.
            • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
              generally generated from :meth:`Experiment.get_dataframe()`.
            • The path of a file containing a pandas DataFrame, generally generated from
              :class:`Experiment.save_dataframe()`.
            • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    method: str, optional
        The method to use to calculate the correlation. Can be either:
            • ``"pingouin"`` (default, alternative: ``"pg"``), uses
              `pingouin_corr <https://pingouin-stats.org/build/html/generated/pingouin.corr.html>`_
            • ``"numpy"``, uses a Pearson correlation calculated with numpy.

    sampling_rate : int|str|float, optional
        Sampling rate of the signals. By default, this value is set on ``"auto"``: in that case, the sampling rate
        is inferred from the dataframes. Otherwise, this value must be equal to the one of the dataframe or the
        experiment object.

    Dataframe filtering
    ~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    groups : list(str)|str|None, optional
        Restricts the analysis to subjects with the specified groups. This parameter can be:

            • A single group.
            • A list of groups.
            • ``None`` (default): the dataframe will not be filtered by group.

    conditions : list(str)|str|None, optional
        Restricts the analysis to trials with the specified conditions. This parameter can be:

            • A single condition.
            • A list of conditions.
            • ``None`` (default): the dataframe will not be filtered by condition.

    subjects : list(str)|str|None, optional
        Restricts the analysis to the specified subjects. This parameter can be:

            • A single subject.
            • A list of subjects.
            • ``None`` (default): all subjects will be considered.

    trials : dict(str: list(str))|list(str)|str|None, optional
        Restricts the analysis to the specified trials. This parameter can be:

            • A single trial.
            • A list of trials.
            • A dictionary mapping subjects or groups to a list of trials.
            • ``None`` (default): all trials will be considered.

    Targets
    ~~~~~~~
    .. rubric:: Parameters

    sequence_measure : list(str)|str, optional
        The sequence measure(s) from the mocap modalities to include in the analysis (e.g., ``"velocity"``,
        ``"acceleration"``). If experiment_or_dataframe is or contains a dataframe, the specified measures must appear
        in its measure column. When provided as a list, each sequence measure is paired with each audio_measure to
        generate separate entries in both the results and the plot dictionary. By default, the value of this parameter
        is ``"auto"``: the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"mocap"``. This parameter can also take the following values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"``, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"``, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"``, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.

    audio_measure : list(str)|str|None, optional
        The audio measure(s) from the audio modality to include in the analysis (e.g., "envelope", "pitch"). If
        experiment_or_dataframe is or contains a dataframe, the specified measures must appear in its measure column.
        When provided as a list, each sequence measure is paired with each sequence_measure to generate separate
        entries in both the results and the plot dictionary. By default, the value of this parameter is ``"auto"``:
        the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"audio"``. The parameter can also be set on ``None`` if your Experiment does not
        have AudioDerivatives, or if you wish to ignore them. This parameter can also take the following values:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``.
            • ``"pitch"``.
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``.

    correlation_with : str|tuple, optional
        The reference signal or label to correlate against. This value can be:

            • A joint label (if only one `sequence_measure` is specified)
            • A tuple containing a sequence measure and a joint label
            • An audio measure
            • A list containing any of the above types.

    series : str|None, optional
        A column name from the dataframe to split data into subsets (e.g., `"group"`, `"condition"`, `"trial"`). Each
        subset will create a new entry in the results and the plot dictionary.

    average : str|None, optional
        Defines the level of averaging:

            • ``"subject"``: average across subjects.
            • ``"trial"``: average across trials.
            • ``None``: no averaging; the full dataset is used.

    lags: int|float|list(int|float)|None, optional
        Defines one or more lags (in seconds) to apply to the target feature in the analysis. A lag can be positive or
        negative. Provided lags are rounded to the closest timestamp value given the sampling rate (e.g., specifying
        a lag of 0.11 for a sampling rate of 10 Hz will result in the lag being rounded to 0.1).

    Result format
    ~~~~~~~~~~~~~
    .. rubric:: Parameters

    result_type : str, optional
        The type of the results computed and returned by the function. This parameter can be:

            • ``"average"`` (alternatives: ``"raw"``, ``"avg"``, default): in that case, the values plotted and
              returned will be the values computed during the analysis, averaged if ``"average"`` is set.
            • ``"z-scores"` (alternatives: ``"z"``, ``"zscores"``, ``"z-score"``, ``"zscore"``, ``"zeta"``): in that
              case, the values plotted will be the z-scores computed against the randomly permuted values. The
              parameters ``permutation_method`` and ``number_of_randperms`` must be set. Note that the returned Result
              instance will contain both the raw/average results and the z-scores.

    permutation_method: str|None, optional
        This parameter determines how permutations are applied:

            • `"value"`: the values of each time series are permuted, allowing to compare the signal against random
              noise.
            • `"label"`: permutations are done by randomly selecting values matching a label, to compare the labels
              between each other.
            • `"shift"`: permutations are done by shifting the time series values (rolling the last values to the
              beginning), allowing to preserve the phase spectrum but without the temporal alignment.
            • `"phase"`: permutations are done by randomizing each Fourier coefficient's phase, which keeps the
              amplitude spectrum but destroys the phase relationships.
            • ``None`` (default): no permutations are calculated. This value is not allowed if ``return_values ==
              "z-scores"``.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_method` is set. An average of the
        calculated random permutations is then calculated, in order to calculate a z-score.

    random_seed : int|None, optional
        Fixes the seed for reproducible random permutations. Default: ``None``: the random permutations will change
        on each execution.

    include_audio : bool, optional
        If ``True``, includes audio signals in the set of labels to analyse.

    Significance parameters
    ~~~~~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    signif_style: list(str) | str | None, optional
        The style of significance to show on the plot. This parameter can be one or more of the following:

            • ``"threshold"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show horizontal lines
              matching the significance threshold.
            • ``"shade"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show shades
              matching the significance threshold.
            • ``None`` (default): the significant values aren't shown.

    signif_alpha: float, optional
        The alpha value for the significance (default: 0.05).

    signif_tail: str | int, optional
        Whether the z-score test is one-tailed or two-tailed. This affects the significance threshold. Default: "1".

    signif_direction: str, optional
        The direction of the significance, if signif_tail is 1. By default, this value is set on ``"up"``, but it also
        can be set on ``"down"``.

    Other parameters
    ~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: optional
        Additional arguments passed to :func:`plot_functions.plot_silhouette` or
        :func:`plot_functions.plot_body_graphs`.

    Returns
    -------
    Results
        A Results instance containing the correlation parameters and the results as attributes:

            • ``averages`` contains the results of the correlation, averaged across the specified level of averaging.
            • ``stds`` contains the standard deviations of the correlation.
            • ``averages_perm`` contains the averages of the random permutations, if they were computed.
            • ``stds`` contains the standard deviations of the random permutations.
            • ``z_scores`` contains the z-scores of the correlation, if ``return_type`` was set on ``z-scores``.
            • ``p_values`` contains the p-values of the correlation, if ``return_type`` was set on ``z-scores``.
            • ``plot_dictionary`` contains the plot dictionary that can be directly passed to ``plot_silhouette`` or
              ``plot_body_graphs``.
    """

    return _common_analysis(experiment_or_dataframe=experiment_or_dataframe, analysis="correlation", method=method,
                            sampling_rate=sampling_rate, groups=groups, conditions=conditions, subjects=subjects,
                            trials=trials, sequence_measure=sequence_measure, audio_measure=audio_measure,
                            target_measure=correlation_with, series=series, average=average, result_type=result_type,
                            permutation_method=permutation_method, number_of_randperms=number_of_randperms,
                            random_seed=random_seed, include_audio=include_audio, verbosity=verbosity, **kwargs)

def coherence(experiment_or_dataframe, sampling_rate="auto", groups=None, conditions=None,
              subjects=None, trials=None, sequence_measure="distance", audio_measure="envelope",
              coherence_with="envelope", series=None, average=None, lags=None, result_type="z-scores",
              permutation_method="value", number_of_randperms=1000, specific_frequency=None, freq_atol=1e-8,
              freq_resolution_hz=0.25, include_audio=False, random_seed=None,
              signif_style="threshold", signif_alpha=0.05, signif_tail="1", signif_direction="up",
              color_line_series=None, color_line_perm=None, title=None, width_line=1, verbosity=1, **kwargs):
    """Calculates and plots the coherence between measures.

    ..versionadded:: 2.0

    Parameters
    ----------

    General parameters
    ~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any)
        The input data to analyse. This parameter can be:

            • A :class:`Experiment` instance, containing the full dataset to be analysed.
            • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
              generally generated from :meth:`Experiment.get_dataframe()`.
            • The path of a file containing a pandas DataFrame, generally generated from
              :class:`Experiment.save_dataframe()`.
            • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    sampling_rate : int|str|float, optional
        Sampling rate of the signals. By default, this value is set on ``"auto"``: in that case, the sampling rate
        is inferred from the dataframes. Otherwise, this value must be equal to the one of the dataframe or the
        experiment object.

    Dataframe filtering
    ~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    groups : list(str)|str|None, optional
        Restricts the analysis to subjects with the specified groups. This parameter can be:

            • A single group.
            • A list of groups.
            • ``None`` (default): the dataframe will not be filtered by group.

    conditions : list(str)|str|None, optional
        Restricts the analysis to trials with the specified conditions. This parameter can be:

            • A single condition.
            • A list of conditions.
            • ``None`` (default): the dataframe will not be filtered by condition.

    subjects : list(str)|str|None, optional
        Restricts the analysis to the specified subjects. This parameter can be:

            • A single subject.
            • A list of subjects.
            • ``None`` (default): all subjects will be considered.

    trials : dict(str: list(str))|list(str)|str|None, optional
        Restricts the analysis to the specified trials. This parameter can be:

            • A single trial.
            • A list of trials.
            • A dictionary mapping subjects or groups to a list of trials.
            • ``None`` (default): all trials will be considered.

    Targets
    ~~~~~~~
    .. rubric:: Parameters

    sequence_measure : list(str)|str, optional
        The sequence measure(s) from the mocap modalities to include in the analysis (e.g., ``"velocity"``,
        ``"acceleration"``). If experiment_or_dataframe is or contains a dataframe, the specified measures must appear
        in its measure column. When provided as a list, each sequence measure is paired with each audio_measure to
        generate separate entries in both the results and the plot dictionary. By default, the value of this parameter
        is ``"auto"``: the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"mocap"``. This parameter can also take the following values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"``, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"``, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"``, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.

    audio_measure : list(str)|str, optional
        The audio measure(s) from the audio modality to include in the analysis (e.g., "envelope", "pitch"). If
        experiment_or_dataframe is or contains a dataframe, the specified measures must appear in its measure column.
        When provided as a list, each sequence measure is paired with each sequence_measure to generate separate
        entries in both the results and the plot dictionary. By default, the value of this parameter is ``"auto"``:
        the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"audio"``. The parameter can also be set on ``None`` if your Experiment does not
        have AudioDerivatives, or if you wish to ignore them. This parameter can also take the following values:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``.
            • ``"pitch"``.
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``.

    coherence_with : str|tuple, optional
        The reference signal or label to calculate the correlation against. This value can be:

            • A joint label (if only one `sequence_measure` is specified)
            • A tuple containing a sequence measure and a joint label
            • An audio measure
            • A list containing any of the above types.

    series : str|None, optional
        A column name from the dataframe to split data into subsets (e.g., `"group"`, `"condition"`, `"trial"`). Each
        subset will create a new entry in the results and the plot dictionary.

    average : str|None, optional
        Defines the level of averaging:

            • ``"subject"``: average across subjects.
            • ``"trial"``: average across trials.
            • ``None``: no averaging; the full dataset is used.

    lags: int|float|list(int|float)|None, optional
        Defines one or more lags (in seconds) to apply to the target feature in the analysis. A lag can be positive or
        negative. Provided lags are rounded to the closest timestamp value given the sampling rate (e.g., specifying
        a lag of 0.11 for a sampling rate of 10 Hz will result in the lag being rounded to 0.1).

    Result format
    ~~~~~~~~~~~~~
    .. rubric:: Parameters

    result_type : str, optional
        The type of the results computed and returned by the function. This parameter can be:

            • ``"average"`` (alternatives: ``"raw"``, ``"avg"``, default): in that case, the values plotted and
              returned will be the values computed during the analysis, averaged if ``"average"`` is set.
            • ``"z-scores"` (alternatives: ``"z"``, ``"zscores"``, ``"z-score"``, ``"zscore"``, ``"zeta"``): in that
              case, the values plotted will be the z-scores computed against the randomly permuted values. The
              parameters ``permutation_method`` and ``number_of_randperms`` must be set. Note that the returned Result
              instance will contain both the raw/average results and the z-scores.

    permutation_method: str|None, optional
        This parameter determines how permutations are applied:

            • `"value"`: the values of each time series are permuted, allowing to compare the signal against random
              noise.
            • `"label"`: permutations are done by randomly selecting values matching a label, to compare the labels
              between each other.
            • `"shift"`: permutations are done by shifting the time series values (rolling the last values to the
              beginning), allowing to preserve the phase spectrum but without the temporal alignment.
            • `"phase"`: permutations are done by randomizing each Fourier coefficient's phase, which keeps the
              amplitude spectrum but destroys the phase relationships.
            • ``None`` (default): no permutations are calculated. This value is not allowed if ``return_values ==
              "z-scores"``.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_method` is set. An average of the
        calculated random permutations is then calculated, in order to calculate a z-score.

    random_seed : int|None, optional
        Fixes the seed for reproducible random permutations. Default: ``None``: the random permutations will change
        on each execution.

    specific_frequency : float|list(float)|None, optional
        Frequency (or list of frequencies) to extract from the result. If set, silhouette plots are generated. This
        parameter is ignored if ``analysis == "correlation"``.

    freq_atol : float|int, optional
        Absolute tolerance for matching the specific frequency (default: 0.1).

    freq_resolution_hz: int or float, optional
        Defines how large each frequency segment will be for the analysis. If set on 0.25 (default), the coherence
        will be calculated at intervals of 0.25 Hz.

    include_audio : bool, optional
        If ``True``, includes audio signals in the set of labels to analyse.

    Significance parameters
    ~~~~~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    signif_style: list(str) | str | None, optional
        The style of significance to show on the plot. This parameter can be one or more of the following:

            • ``"threshold"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show horizontal lines
              matching the significance threshold.
            • ``"shade"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show shades
              matching the significance threshold.
            • ``None`` (default): the significant values aren't shown.

    signif_alpha: float, optional
        The alpha value for the significance (default: 0.05).

    signif_tail: str | int, optional
        Whether the z-score test is one-tailed or two-tailed. This affects the significance threshold. Default: "1".

    signif_direction: str, optional
        The direction of the significance, if signif_tail is 1. By default, this value is set on ``"up"``, but it also
        can be set on ``"down"``.

    Plot parameters
    ~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    color_line_series : list|str|None, optional
        Color(s) to use when plotting time-frequency graphs. If this parameter is a list, a color will be
        attributed to each series. If this parameter is a string, the same color is attributed to all series. Each
        color can take a number of forms:

            • The `HTML/CSS name of a color <https://en.wikipedia.org/wiki/X11_color_names>`_ (e.g. ``"red"`` or
              ``"blanched almond"``),
            • The hexadecimal code of a color, starting with a number sign (``#``, e.g. ``"#ffcc00"`` or ``"#c0ffee"``).
            • The RGB or RGBA tuple of a color (e.g. ``(153, 204, 0)`` or ``(77, 77, 77, 255)``).

    color_line_perm: list|str|None, optional
        Color to use for the permutations when plotting time-frequency graphs. If this parameter is a list, a color
        will be attributed to each series. If this parameter is a string, the same color is attributed to all series.

    title: str|None, optional
        If set, the title of the plot. Otherwise, an automatic title will be generated.

    width_line : int|float
        Width of plotted lines.

    Other parameters
    ~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: optional
        Additional arguments passed to :func:`plot_functions.plot_silhouette` or
        :func:`plot_functions.plot_body_graphs`.

    Returns
    -------
    Results
        A Results instance containing the analysis parameters and the results as attributes:

            • ``frequencies`` contains the frequencies corresponding to the results, if the analysis is in the
               frequency domain.
            • ``averages`` contains the results of the analysis, averaged across the specified level of averaging.
            • ``stds`` contains the standard deviations of the results.
            • ``averages_perm`` contains the averages of the random permutations, if they were computed.
            • ``stds`` contains the standard deviations of the random permutations.
            • ``z_scores`` contains the z-scores of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``p_values`` contains the p-values of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``plot_dictionary`` contains the plot dictionary that can be directly passed to ``plot_silhouette`` or
              ``plot_body_graphs``.
    """

    return _common_analysis(experiment_or_dataframe=experiment_or_dataframe, analysis="coherence",
                            sampling_rate=sampling_rate, groups=groups, conditions=conditions, subjects=subjects,
                            trials=trials, sequence_measure=sequence_measure, audio_measure=audio_measure,
                            target_measure=coherence_with, series=series, average=average, result_type=result_type,
                            permutation_method=permutation_method, number_of_randperms=number_of_randperms,
                            specific_frequency=specific_frequency, freq_atol=freq_atol, freq_resolution_hz=freq_resolution_hz,
                            include_audio=include_audio, random_seed=random_seed, signif_style=signif_style,
                            signif_alpha=signif_alpha, signif_tail=signif_tail, signif_direction=signif_direction,
                            color_line_series=color_line_series, color_line_perm=color_line_perm, title=title,
                            width_line=width_line, verbosity=verbosity, **kwargs)

def mutual_information(experiment_or_dataframe, sampling_rate="auto", groups=None, conditions=None, subjects=None,
                       trials=None, sequence_measure="distance", audio_measure="envelope", regression_with="envelope",
                       series=None, average=None, lags=None, result_type="z-scores", permutation_method="value",
                       number_of_randperms=1000, scale="standard", n_neighbors=3, direction="target",
                       include_audio=False, random_seed=None, signif_style="threshold", signif_alpha=0.05,
                       signif_tail="1", signif_direction="up", color_line_series=None, color_line_perm=None, title=None,
                       width_line=1, verbosity=1, **kwargs):
    """Calculates and plots the mutual information between measures.

    ..versionadded:: 2.0

    Parameters
    ----------

    General parameters
    ~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any)
        The input data to analyse. This parameter can be:

            • A :class:`Experiment` instance, containing the full dataset to be analysed.
            • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
              generally generated from :meth:`Experiment.get_dataframe()`.
            • The path of a file containing a pandas DataFrame, generally generated from
              :class:`Experiment.save_dataframe()`.
            • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    sampling_rate : int|str|float, optional
        Sampling rate of the signals. By default, this value is set on ``"auto"``: in that case, the sampling rate
        is inferred from the dataframes. Otherwise, this value must be equal to the one of the dataframe or the
        experiment object.

    Dataframe filtering
    ~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    groups : list(str)|str|None, optional
        Restricts the analysis to subjects with the specified groups. This parameter can be:

            • A single group.
            • A list of groups.
            • ``None`` (default): the dataframe will not be filtered by group.

    conditions : list(str)|str|None, optional
        Restricts the analysis to trials with the specified conditions. This parameter can be:

            • A single condition.
            • A list of conditions.
            • ``None`` (default): the dataframe will not be filtered by condition.

    subjects : list(str)|str|None, optional
        Restricts the analysis to the specified subjects. This parameter can be:

            • A single subject.
            • A list of subjects.
            • ``None`` (default): all subjects will be considered.

    trials : dict(str: list(str))|list(str)|str|None, optional
        Restricts the analysis to the specified trials. This parameter can be:

            • A single trial.
            • A list of trials.
            • A dictionary mapping subjects or groups to a list of trials.
            • ``None`` (default): all trials will be considered.

    Targets
    ~~~~~~~
    .. rubric:: Parameters

    sequence_measure : list(str)|str, optional
        The sequence measure(s) from the mocap modalities to include in the analysis (e.g., ``"velocity"``,
        ``"acceleration"``). If experiment_or_dataframe is or contains a dataframe, the specified measures must appear
        in its measure column. When provided as a list, each sequence measure is paired with each audio_measure to
        generate separate entries in both the results and the plot dictionary. By default, the value of this parameter
        is ``"auto"``: the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"mocap"``. This parameter can also take the following values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"``, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"``, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"``, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.

    audio_measure : list(str)|str, optional
        The audio measure(s) from the audio modality to include in the analysis (e.g., "envelope", "pitch"). If
        experiment_or_dataframe is or contains a dataframe, the specified measures must appear in its measure column.
        When provided as a list, each sequence measure is paired with each sequence_measure to generate separate
        entries in both the results and the plot dictionary. By default, the value of this parameter is ``"auto"``:
        the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"audio"``. The parameter can also be set on ``None`` if your Experiment does not
        have AudioDerivatives, or if you wish to ignore them. This parameter can also take the following values:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``.
            • ``"pitch"``.
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``.

    regression_with : str|tuple, optional
        The target signal or label to calculate the mutual information with the predictors. This value can be:

            • A joint label (if only one `sequence_measure` is specified)
            • A tuple containing a sequence measure and a joint label
            • An audio measure
            • A list containing any of the above types.

    series : str|None, optional
        A column name from the dataframe to split data into subsets (e.g., `"group"`, `"condition"`, `"trial"`). Each
        subset will create a new entry in the results and the plot dictionary.

    average : str|None, optional
        Defines the level of averaging:

            • ``"subject"``: average across subjects.
            • ``"trial"``: average across trials.
            • ``None``: no averaging; the full dataset is used.

    lags: int|float|list(int|float)|None, optional
        Defines one or more lags (in seconds) to apply to the target feature in the analysis. A lag can be positive or
        negative. Provided lags are rounded to the closest timestamp value given the sampling rate (e.g., specifying
        a lag of 0.11 for a sampling rate of 10 Hz will result in the lag being rounded to 0.1).

    Result format
    ~~~~~~~~~~~~~
    .. rubric:: Parameters

    result_type : str, optional
        The type of the results computed and returned by the function. This parameter can be:

            • ``"average"`` (alternatives: ``"raw"``, ``"avg"``, default): in that case, the values plotted and
              returned will be the values computed during the analysis, averaged if ``"average"`` is set.
            • ``"z-scores"` (alternatives: ``"z"``, ``"zscores"``, ``"z-score"``, ``"zscore"``, ``"zeta"``): in that
              case, the values plotted will be the z-scores computed against the randomly permuted values. The
              parameters ``permutation_method`` and ``number_of_randperms`` must be set. Note that the returned Result
              instance will contain both the raw/average results and the z-scores.

    permutation_method: str|None, optional
        This parameter determines how permutations are applied:

            • `"value"`: the values of each time series are permuted, allowing to compare the signal against random
              noise.
            • `"label"`: permutations are done by randomly selecting values matching a label, to compare the labels
              between each other.
            • `"shift"`: permutations are done by shifting the time series values (rolling the last values to the
              beginning), allowing to preserve the phase spectrum but without the temporal alignment.
            • `"phase"`: permutations are done by randomizing each Fourier coefficient's phase, which keeps the
              amplitude spectrum but destroys the phase relationships.
            • ``None`` (default): no permutations are calculated. This value is not allowed if ``return_values ==
              "z-scores"``.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_method` is set. An average of the
        calculated random permutations is then calculated, in order to calculate a z-score.

    n_neighbors: int, optional
        Number of neighbors to use for mutual information estimation. This parameter is directly passed to
        `sklearn <https://scikit-learn.org/1.5/modules/generated/sklearn.feature_selection.mutual_info_regression.html>`_.

    scale: str | None, optional
        The scale to apply to the data before estimating the distances, or None. This value can be:
            • `"standard"`: the values are scaled using `StandardScaler <https://sklearn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_
            • `"minmax"`:  the values are scaled using `MinMaxScaler <https://sklearn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html>`_
            • ``None``: the values are not scaled.

    direction: str, optional
        How to consider the target variable ``regression_with`` in the calculation:
            • `"target"`: all the other variables are considered as predictors
            • `"predictor"`: all the other variables are considered as targets
            • ``symmetric``: the average of the two previous calculations is returned.

    random_seed : int|None, optional
        Fixes the seed for reproducible random permutations. Default: ``None``: the random permutations will change
        on each execution.

    include_audio : bool, optional
        If ``True``, includes audio signals in the set of labels to analyse.

    Significance parameters
    ~~~~~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    signif_style: list(str) | str | None, optional
        The style of significance to show on the plot. This parameter can be one or more of the following:

            • ``"threshold"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show horizontal lines
              matching the significance threshold.
            • ``"shade"``: if ``result_type`` is equal to ``"z-scores"``, the plot will show shades
              matching the significance threshold.
            • ``None`` (default): the significant values aren't shown.

    signif_alpha: float, optional
        The alpha value for the significance (default: 0.05).

    signif_tail: str | int, optional
        Whether the z-score test is one-tailed or two-tailed. This affects the significance threshold. Default: "1".

    signif_direction: str, optional
        The direction of the significance, if signif_tail is 1. By default, this value is set on ``"up"``, but it also
        can be set on ``"down"``.

    Plot parameters
    ~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    color_line_series : list|str|None, optional
        Color(s) to use when plotting time-frequency graphs. If this parameter is a list, a color will be
        attributed to each series. If this parameter is a string, the same color is attributed to all series. Each
        color can take a number of forms:

            • The `HTML/CSS name of a color <https://en.wikipedia.org/wiki/X11_color_names>`_ (e.g. ``"red"`` or
              ``"blanched almond"``),
            • The hexadecimal code of a color, starting with a number sign (``#``, e.g. ``"#ffcc00"`` or ``"#c0ffee"``).
            • The RGB or RGBA tuple of a color (e.g. ``(153, 204, 0)`` or ``(77, 77, 77, 255)``).

    color_line_perm: list|str|None, optional
        Color to use for the permutations when plotting time-frequency graphs. If this parameter is a list, a color
        will be attributed to each series. If this parameter is a string, the same color is attributed to all series.

    title: str|None, optional
        If set, the title of the plot. Otherwise, an automatic title will be generated.

    width_line : int|float
        Width of plotted lines.

    Other parameters
    ~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: optional
        Additional arguments passed to :func:`plot_functions.plot_silhouette` or
        :func:`plot_functions.plot_body_graphs`.

    Returns
    -------
    Results
        A Results instance containing the analysis parameters and the results as attributes:

            • ``frequencies`` contains the frequencies corresponding to the results, if the analysis is in the
               frequency domain.
            • ``averages`` contains the results of the analysis, averaged across the specified level of averaging.
            • ``stds`` contains the standard deviations of the results.
            • ``averages_perm`` contains the averages of the random permutations, if they were computed.
            • ``stds`` contains the standard deviations of the random permutations.
            • ``z_scores`` contains the z-scores of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``p_values`` contains the p-values of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``plot_dictionary`` contains the plot dictionary that can be directly passed to ``plot_silhouette`` or
              ``plot_body_graphs``.
    """
    return _common_analysis(experiment_or_dataframe=experiment_or_dataframe, analysis="mutual information",
                            sampling_rate=sampling_rate, groups=groups, conditions=conditions, subjects=subjects,
                            trials=trials, sequence_measure=sequence_measure, audio_measure=audio_measure,
                            target_measure=regression_with, series=series, average=average, result_type=result_type,
                            permutation_method=permutation_method, number_of_randperms=number_of_randperms,
                            n_neighbors=n_neighbors, mi_scale=scale, mi_direction=direction,
                            include_audio=include_audio, random_seed=random_seed, color_line_series=color_line_series,
                            color_line_perm=color_line_perm, title=title, width_line=width_line, verbosity=verbosity,
                            **kwargs)

def pca(data, n_components=0.95, groups=None, conditions=None, subjects=None, trials=None, labels="all",
        sequence_measure="auto", audio_measure="auto", selected_components=None, random_seed=None, nan_behaviour=0.1,
        verbosity=1, **kwargs):
    """Performs a principal component analysis (PCA) on the measures from the experiment, reducing the dimensionality
    of the data. Each joint_label is used as a feature for the PCA, and, if specified, the audio measure too.
    Relies on the PCA function from
    `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`_.

    ..versionadded:: 2.0

    Parameters
    ----------

    General parameters
    ~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    data: Experiment|pandas.DataFrame|str|list(any)|Subject|Trial|Sequence
        The data to include in the PCA. The sequences and audio measures will be included, if present. This parameter
        can be:
        • A :class:`Experiment` instance, containing the full dataset to be analyzed.
        • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
          generally generated from :meth:`Experiment.get_dataframe()`.
        • The path of a file containing a pandas DataFrame, generally generated from
          :class:`Experiment.save_dataframe()`.
        • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.
        • A Subject instance, containing the data for a single subject.
        • A Trial instance, containing both Sequence and Audio data.
        • A Sequence instance, containing the data for a single sequence.

    n_components: int|float|str|None, optional
        This parameter is passed to `scikit <https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`_.
        As such, the same rules apply:
        • If set on an integer, the parameter represents the number of components to generate from the PCA. This value
          must be at least 1, but lower than the number of samples of the data, and lower than the number of channels
          (joint labels + audio measures).
        • If set on a string, the parameter must be equal to `"mle"`. In that case, Thomas P. Minka's method for
          automatically choosing the dimensionality of the PCA is applied.
        • If set on a float between 0 and 1, the parameter represents the proportion of variance explained by the PCA.
          By default, this value is set on **0.95**.
        • `None` sets the parameter on ``min(n_samples, n_features) - 1``.

    Dataframe filtering
    ~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    groups : list(str)|str|None, optional
        Restricts the analysis to subjects with the specified groups. This parameter can be:

            • A single group.
            • A list of groups.
            • ``None`` (default): the dataframe will not be filtered by group.

    conditions : list(str)|str|None, optional
        Restricts the analysis to trials with the specified conditions. This parameter can be:

            • A single condition.
            • A list of conditions.
            • ``None`` (default): the dataframe will not be filtered by condition.

    subjects : list(str)|str|None, optional
        Restricts the analysis to the specified subjects. This parameter can be:

            • A single subject.
            • A list of subjects.
            • ``None`` (default): all subjects will be considered.

    trials : dict(str: list(str))|list(str)|str|None, optional
        Restricts the analysis to the specified trials. This parameter can be:

            • A single trial.
            • A list of trials.
            • A dictionary mapping subjects or groups to a list of trials.
            • ``None`` (default): all trials will be considered.

    Measures
    ~~~~~~~~
    .. rubric:: Parameters

    labels: str | list(str), optional
        Which labels to include in the PCA. This parameter can be ``"all"`` (default), or a list of labels.

    sequence_measure : list(str)|str, optional
        The sequence measure(s) from the mocap modalities to include in the analysis (e.g., ``"velocity"``,
        ``"acceleration"``). If experiment_or_dataframe is or contains a dataframe, the specified measures must appear
        in its measure column. When provided as a list, each sequence measure is paired with each audio_measure to
        generate separate entries in both the results and the plot dictionary. By default, the value of this parameter
        is ``"auto"``: the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"mocap"``. This parameter can also take the following values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"``, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"``, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"``, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.

    audio_measure : list(str)|str|None, optional
        The audio measure(s) from the audio modality to include in the analysis (e.g., "envelope", "pitch"). If
        experiment_or_dataframe is or contains a dataframe, the specified measures must appear in its measure column.
        When provided as a list, each sequence measure is paired with each sequence_measure to generate separate
        entries in both the results and the plot dictionary. By default, the value of this parameter is ``"auto"``:
        the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"audio"``. The parameter can also be set on ``None`` if your Experiment does not
        have AudioDerivatives, or if you wish to ignore them. This parameter can also take the following values:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``.
            • ``"pitch"``.
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``.

    Analysis parameters
    ~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    selected_components: list, int or None, optional
        Defines the components to plot. It can be a single component (e.g. `2`) or a list of components
        (e.g. [0, 2, 5]). If set on `None` (default), all the components are plotted.

    random_seed : int|None, optional
        Fixes the seed for reproducible PCA. Default: ``None``: the PCA will change on each execution.

    nan_behaviour: str|int|float|None, optional
        This parameter sets the behaviour to adopt if NaN values are encountered in the dataframe:

            • ``"drop_timestamps"`` or ``drop_rows`` : the rows of the dataframe containing NaN values are removed.
              This can result in a loss of data for the labels that contain values, and render the sampling rate non-
              constant. Use this option if you are using data that is not perfectly the same length (e.g. velocity
              mocap doesn't have a value at timestamp 0, while audio samples do).
            • ``"drop_labels"`` or ``drop_columns``: the labels containing NaN values are removed. This can result in
              the loss of a lot of channels if each contains at least one NaN value. Use this option if you know that
              a few channels contain NaN values.
            • A float 0 < x <= 1: the labels containing more than a certain percentage of NaN values are removed.
              For instance, if the parameter is set on 0.1 (default value), the labels containing more than 10% of NaN
              values are removed. Then, the timestamps where NaNs occur are dropped (similarly to ``drop_timestamps``).
            • ``"zero"``: the NaN values are replaced with 0.
            • ``None``: nothing is done. This will result in an error if NaN values are encountered.

    Other parameters
    ~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: optional
        Additional arguments passed to :func:`_plot_components`.
    """
    if isinstance(data, Sequence):
        df = data.to_analysis_dataframe(measure=sequence_measure)
    elif isinstance(data, Trial):
        df = pd.DataFrame()
        if data.has_sequence():
            df = data.sequence.to_analysis_dataframe(measure=sequence_measure, trial=data.trial_id)
        if data.has_audio():
            if type(data.audio).__name__.lower() != audio_measure.lower():
                raise Exception(f"The selected audio measure {audio_measure} does not match with the audio measure "
                                f"present in the Trial instance ({type(data.audio)}.")
            df = pd.concat([df, data.audio.to_analysis_dataframe(measure=audio_measure, trial=data.trial_id)],
                           axis=0, ignore_index=True)
    elif isinstance(data, Subject):
        df = pd.DataFrame()
        for trial in data.trials:
            if trial.has_sequence():
                df_seq = trial.sequence.to_analysis_dataframe(measure=sequence_measure, subject=data.name,
                                                              trial=trial.trial_id)
                df = pd.concat([df, df_seq], axis=0, ignore_index=True)
            if trial.has_audio():
                if type(trial.audio).__name__.lower() != audio_measure.lower():
                    raise Exception(f"The selected audio measure {audio_measure} does not match with the audio measure "
                                    f"present in the Trial instance ({type(trial.audio)}.")
                df = pd.concat([df, trial.audio.to_analysis_dataframe(measure=audio_measure,
                                                                      trial=trial.trial_id)], axis=0, ignore_index=True)
    else:
        df = pd.DataFrame()

    params = AnalysisParameters(analysis="pca", experiment_or_dataframe=df, groups=groups, conditions=conditions,
                                trials = trials, sequence_measure=sequence_measure, audio_measure=audio_measure,
                                result_type="pca", random_seed=random_seed, nan_behaviour=nan_behaviour,
                                selected_components=selected_components, verbosity=verbosity, **kwargs)

    try:
        from sklearn.decomposition import PCA
    except ImportError:
        raise ModuleNotFoundException("sklearn", "calculate a PCA")

    dataframe = _prepare_dataframe(params)
    if labels == "all":
        labels = list(dataframe["label"].unique())

    # Keep only the labels of interest
    dataframe_filtered = dataframe[dataframe["label"].isin(labels)].copy()

    pca_model = PCA(n_components=n_components, random_state=params.random_seed)

    # Single subject/trial: fill the default columns
    for col, default in [("subject", "_single_subject"), ("trial", "_single_trial")]:
        if col not in dataframe_filtered.columns:
            dataframe_filtered[col] = default
        else:
            if dataframe_filtered[col].isna().all():
                dataframe_filtered[col] = default
            else:
                dataframe_filtered[col] = dataframe_filtered[col].fillna(default)

    data_matrix = dataframe_filtered.pivot_table(index=["subject", "trial", "timestamp"],
                                                columns="label",
                                                values="value",
                                                aggfunc="mean").sort_index()

    # NaN handling
    if isinstance(nan_behaviour, str):
        if nan_behaviour in ["drop_timestamps", "drop_rows"]:
            n_rows_before = len(data_matrix)
            data_matrix = data_matrix.dropna(axis=0, how="any")
            n_rows_after = len(data_matrix)
            if verbosity > 0 and n_rows_before != n_rows_after:
                print(f"Dropped {n_rows_before - n_rows_after} row(s) containing NaNs (drop_timestamps).")
            elif verbosity > 0:
                print(f"No NaNs found (drop_timestamps).")
        elif nan_behaviour in ["drop_labels", "drop_columns"]:
            keep_cols = ~data_matrix.isna().any(axis=0)
            dropped_cols = data_matrix.columns[~keep_cols].to_list()
            data_matrix = data_matrix.loc[:, keep_cols]
            if verbosity > 0 and dropped_cols:
                print(f"Dropped {len(dropped_cols)} label(s) containing NaNs (drop_labels): {', '.join(dropped_cols[:10])}"
                      f"{'...' if len(dropped_cols) > 10 else ''}")
            elif verbosity > 0:
                print(f"No NaNs found (drop_labels).")
        elif nan_behaviour in ["zero", "0"]:
            n_nans = int(data_matrix.isna().sum().sum())
            data_matrix = data_matrix.fillna(0)
            if verbosity > 0:
                print(f"Replacing {n_nans} NaN value(s) with 0 (nan_behaviour='zero').")
        else:
            raise ValueError(f"Invalid value for nan_behaviour: {nan_behaviour}.")

    elif isinstance(nan_behaviour, (int, float)):
        if not (0 < nan_behaviour <= 1):
            raise ValueError("nan_behaviour as a number must satisfy 0 < x <= 1.")

        # Drop labels with more than x proportion of NaNs
        nan_ratio = data_matrix.isna().mean(axis=0)
        keep_cols = nan_ratio <= nan_behaviour
        dropped_cols = data_matrix.columns[~keep_cols].to_list()
        data_matrix = data_matrix.loc[:, keep_cols]

        # Then drop timestamps where NaNs remain
        n_rows_before = len(data_matrix)
        data_matrix = data_matrix.dropna(axis=0, how="any")
        n_rows_after = len(data_matrix)

        if verbosity > 0:
            if dropped_cols:
                print(f"Dropped {len(dropped_cols)} label(s) with NaN ratio > {nan_behaviour}: {', '.join(dropped_cols[:10])}"
                      f"{'...' if len(dropped_cols) > 10 else ''}")
            else:
                print(f"No labels dropped.")
            if n_rows_before != n_rows_after:
                print(f"Dropped {n_rows_before - n_rows_after} row(s) containing NaNs after label filtering.")
            else:
                print("No timestamps dropped.")

    pca_result = pca_model.fit_transform(data_matrix)

    _plot_components(pca_result, pca_model.components_, labels, "PCA", selected_components, verbosity=verbosity, **kwargs)

    pca_comps = [{l: c for l, c in zip(labels, comp)} for comp in pca_model.components_]
    return pca_result, pca_comps

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
    dataframe = _filter_dataframe(dataframe, group, condition, subjects, trials)
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


def _prepare_dataframe(params):
    """Prepares the dataframe by creating it if necessary, and filtering it.

    .. versionadded:: 2.0
    """
    if params.verbosity > 0:
        print("Preparing the dataframe...")
    dataframe = _make_dataframe(params.experiment_or_dataframe, params.sequence_measure, params.audio_measure,
                                params.sampling_rate, params.verbosity, 1)
    dataframe = _filter_dataframe(dataframe, params.groups, params.conditions, params.subjects,
                                  params.trials, params.verbosity, 1)
    if dataframe.empty:
        raise ValueError("The provided dataframe is empty, or the dataframe after applying the required filters ("
                         "group, condition, subjects, trials) is empty. Please check your input parameters.")
    if params.verbosity > 0:
        print("Dataframe ready.")

    # Showing the first and last 10 rows of the dataframe
    if params.verbosity > 1:
        print("\nShowing the first few rows of the dataframe...")
        print(dataframe.head(10))
        print("\nShowing the last few rows of the dataframe...")
        print(dataframe.tail(10))

    return dataframe


def _make_dataframe(experiment_or_dataframe, sequence_measure, audio_measure, sampling_frequency, verbosity=1,
                    add_tabs=1):
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

    add_tabs: int, optional
        Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
        functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
        by the user.

    Returns
    -------
    dataframe: pandas.DataFrame
        A dataframe containing the loaded data.
    """
    t = add_tabs * "\t"
    dataframe = None

    # Get the full dataframe
    if type(experiment_or_dataframe) is not list:
        experiment_or_dataframe = [experiment_or_dataframe]

    if verbosity > 0:
        print(t+f"Loading {len(experiment_or_dataframe)} input dataframe(s) or experiment(s)...")

    i = 1

    for item in experiment_or_dataframe:
        if type(item) is Experiment:
            if audio_measure not in ["audio", "envelope", "intensity", "pitch", "f1", "f2", "f3", "f4", "f5"]:
                audio_measure = None
            if sequence_measure == "auto":
                raise ValueError("The parameter sequence_measure cannot be set to 'auto' when one of the elements "
                                 "in experiment_or_dataframe is an Experiment instance.")
            dataframe_item = item.get_dataframe(sequence_measure, audio_measure,
                                                audio_resampling_frequency=sampling_frequency)
        elif type(item) is str:
            dataframe_item = read_pandas_dataframe(item, verbosity, add_tabs + 1)
        elif type(item) is pd.DataFrame:
            dataframe_item = item
        else:
            raise Exception("One item in experiment_or_dataframe is neither an Experiment, a Pandas Dataframe or a "
                            "path to a Pandas Dataframe.")

        if verbosity > 1:
            print(t+f"\tDataframe {i} with {dataframe_item.shape[1]} columns and {dataframe_item.shape[0]} rows.")

        if dataframe is None:
            dataframe = dataframe_item
        else:
            dataframe = pd.concat([dataframe, dataframe_item])

        i += 1

    if verbosity > 0:
        print(t+f"\tGlobal dataframe generated with {dataframe.shape[1]} columns and {dataframe.shape[0]} rows.")

    return dataframe


def _filter_dataframe(dataframe, group=None, condition=None, subjects=None, trials=None, verbosity=1,
                      add_tabs=1):
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

    add_tabs: int, optional
        Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
        functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
        by the user.

    Returns
    -------
    dataframe: pandas.DataFrame
        A dataframe, containing a subset from the original dataframe.
    """
    t = add_tabs * "\t"

    original_size = len(dataframe.index)
    removed = []

    if verbosity > 0:
        print(t + "Reducing the dataframe to discard the unused rows...")

    if group is not None:
        if isinstance(group, (tuple, list)):
            dataframe = dataframe.loc[dataframe["group"].isin(group)]
            removed.append("groups")
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a group that is not part of {', '.join(group)}.")
        elif isinstance(group, str):
            dataframe = dataframe.loc[dataframe["group"] == group]
            removed.append("group")
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a group that is not {group}.")
        else:
            raise ValueError("The parameter group must be either a string or a list of strings.")

    if condition is not None:
        if isinstance(condition, (tuple, list)):
            dataframe = dataframe.loc[dataframe["condition"].isin(condition)]
            removed.append("conditions")
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a condition that is not part of {', '.join(condition)}.")
        elif isinstance(condition, str):
            dataframe = dataframe.loc[dataframe["condition"] == condition]
            removed.append("condition")
            removed.append("conditions")
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a condition that is not {condition}.")
        else:
            raise ValueError("The parameter condition must be a string or a list of strings.")

    if subjects is not None:
        if isinstance(subjects, (tuple, list)):
            dataframe = dataframe.loc[dataframe["subject"].isin(subjects)]
            removed.append("subjects")
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a subject that is not part of {', '.join(subjects)}.")
        elif isinstance(subjects, str):
            dataframe = dataframe.loc[dataframe["subject"] == subjects]
            removed.append("subject")
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a condition that is not {subjects}.")
        else:
            raise ValueError("The parameter subjects must be a string or a list of strings.")

    if trials is not None:
        if isinstance(trials, dict):
            new_dataframe = []
            for key, trial_list in trials.items():
                if isinstance(trial_list, str):
                    trial_list = [trial_list]
                if key in dataframe["subject"].values:
                    dataframe_subject = dataframe.loc[dataframe["subject"] == key]
                    dataframe_trials = dataframe_subject[dataframe_subject["trial"].isin(trial_list)]
                    level = "subject"
                elif key in dataframe["group"].values:
                    dataframe_group = dataframe.loc[dataframe["group"] == key]
                    dataframe_trials = dataframe_group[dataframe_group["trial"].isin(trial_list)]
                    level = "group"
                else:
                    raise ValueError(f"In the specified trials, '{key}' is neither a subject nor a group in the "
                                     f"dataframe.")
                new_dataframe.append(dataframe_trials)
                if verbosity > 1:
                    if len(trial_list) == 1:
                        print(t + f"\tRemoved the rows for {level} {key} with a trial that is not {trial_list[0]}")
                    else:
                        print(t + f"\tRemoved the rows for {level} {key} with a trial that is not part of"
                                  f" {', '.join(trial_list)}.")
            dataframe = pd.concat(new_dataframe, ignore_index=True)
        elif isinstance(trials, (tuple, list)):
            dataframe = dataframe.loc[dataframe["trial"].isin(trials)]
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a trial that is not part of {', '.join(trials)}.")
        elif isinstance(trials, str):
            dataframe = dataframe.loc[dataframe["trial"] == trials]
            if verbosity > 1:
                print(t + f"\tRemoved the rows with a trial that is not {trials}.")
        else:
            raise ValueError("The parameter trials must be either a dictionary, a list or a string.")
        removed.append("trials")

    if dataframe.empty:
        raise Exception("The requested filtering options reduced the dataframe to an empty one.")

    if verbosity > 0 and len(removed) > 0:
        print(t+f"\tThe dataframe was reduced to preserve the requested {', '.join(removed)}.\n\t\tThe dataframe "
              f"originally had {original_size} rows, and now has {len(dataframe.index)} rows ("
              f"{np.round(len(dataframe.index)/original_size * 100, 2)} %).")

    return dataframe

def _compute_power_spectrum(method, measure_values, frequencies, sampling_rate):

    if frequencies is None:
        frequencies, _ = signal.welch(np.zeros(1000), fs=sampling_rate)

    if measure_values.size == 0:
        results = np.empty(len(frequencies))
        results[:] = np.nan

    else:
        if method == "fft":
            power_spectrum = np.abs(np.fft.fft(measure_values)) ** 2
            fft_freqs = np.fft.fftfreq(measure_values.size, 1 / sampling_rate)
            fft_freqs = fft_freqs[:len(fft_freqs) // 2]
            results = power_spectrum[:len(power_spectrum) // 2]

            interpolated_spectrum = np.interp(frequencies, fft_freqs, results)
            results = interpolated_spectrum

        elif method == "welch":
            frequencies, results = signal.welch(measure_values, fs=sampling_rate)

        else:
            raise ValueError(f"""When computing the power spectrum, the parameter method (current value: {method} must 
                             be "fft" or "welch".""")

    return frequencies, results

def _compute_correlation(pg, method, measure_values, target_values):
    if method == "pingouin":
        try:
            results = np.abs(pg.corr(x=measure_values, y=target_values).values[0][1])
        except (ValueError, AssertionError):
            results = np.nan
    elif method == "numpy":
        measure_values_mean = np.mean(measure_values)
        target_values_mean = np.mean(target_values)
        num = np.sum((measure_values - measure_values_mean) * (target_values - target_values_mean))
        denom = np.sqrt(np.sum((measure_values - measure_values_mean) ** 2) *
                        np.sum((measure_values - target_values_mean) ** 2))
        if denom != 0:
            results = num / denom
        else:
            results = np.nan
    else:
        raise ValueError(f"""When computing a correlation, the parameter method (current value: {method} must 
                         be "pingouin" or "numpy".""")

    return results

def _compute_coherence(measure_values, target_values, frequencies, sampling_rate, nperseg):
    freqs, coh = signal.coherence(measure_values, target_values, fs=sampling_rate,
                                  nperseg=int(nperseg))

    if len(coh) == 0:
        coh = np.tile(np.nan, int(nperseg // 2 + 1))

    if frequencies is None:
        frequencies = freqs

    results = coh

    return frequencies, results

def _compute_mutual_information(mi, sc, measure_values, target_values, random_state, n_neighbors, scale, direction):

    if scale:
        x = sc.fit_transform(measure_values.reshape(-1, 1)).reshape(-1)
        y = sc.fit_transform(target_values.reshape(-1, 1)).reshape(-1)

    else:
        x = measure_values
        y = target_values

    x_pred = x.reshape(-1, 1)
    y_pred = y.reshape(-1, 1)
    x_targ = x
    y_targ = y

    if direction == "target":
        result = mi(x_pred, y_targ, random_state=random_state, n_neighbors=n_neighbors)[0]
    elif direction == "predictor":
        result = mi(y_pred, x_targ, random_state=random_state, n_neighbors=n_neighbors)[0]
    else:
        result_target = mi(x_pred, y_targ, random_state=random_state, n_neighbors=n_neighbors)[0]
        result_predictor = mi(y_pred, x_targ, random_state=random_state, n_neighbors=n_neighbors)[0]
        result = (result_target + result_predictor) / 2

    return result

def _phase_randomize(array, rng):
    """Return a phase-randomized surrogate of a real-valued signal."""
    # FFT
    fft_vals = np.fft.rfft(array)           # one-sided spectrum
    amplitudes = np.abs(fft_vals)
    phases = np.angle(fft_vals)

    # Generate random phases for the non-DC, non-Nyquist bins
    n_freqs = len(phases)
    random_phases = rng.uniform(0, 2*np.pi, n_freqs)
    # keep DC (0 Hz) and Nyquist (if present) unchanged
    random_phases[0] = phases[0]
    if len(array) % 2 == 0:  # Nyquist exists only for even length
        random_phases[-1] = phases[-1]

    # Construct new spectrum
    new_fft = amplitudes * np.exp(1j * random_phases)

    # Back to time domain
    surrogate = np.fft.irfft(new_fft, n=len(array))
    return surrogate


def _count_tqdm_iterations(params, loop_number):
    total = 0
    for target_measure in params.target_measures:
        for measure in params.measures:
            if params.measure_to_modality[measure] == "audio" and not params.include_audio:
                continue
            labels_modality = ["Audio"] if params.measure_to_modality[measure] == "audio" else params.labels_mocap

            for series_value in params.series_values:

                if loop_number == 1:
                    for individual in params.individuals:
                        if params.average == params.series and individual != series_value and individual != "All":
                            continue
                        total += len(labels_modality) * len(params.lags)
                else:
                    total += len(labels_modality) * len(params.lags)

    return total