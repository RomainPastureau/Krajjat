"""These functions allow to find significant connections between movements, or between movements and audio properties.
"""

import copy
from krajjat.plot_functions import *
import statsmodels.api as sm

def correlation_sequence_with_audio(experiment, group=None, condition=None, subject=None, metric_sequence="distance",
                                    metric_audio="envelope"):
    pass

def correlation_sequence_with_joint(experiment, group=None, condition=None, subject=None, metric_sequence="distance",
                                    joint_label="Head"):
    pass


def global_correlating(trials, signals, time_vector, concat_series=False, cross_correlation=False, lag=None, window=1,
                       line_width=1.0, color_scheme="default", min_scale="auto", max_scale="auto", verbose=1):
    # The two variables must have the same number of observations
    if len(trials) != len(signals):
        raise Exception("Non-matching number of sequences (" + str(len(trials)) +
                        ") and signals (" + str(len(signals)) + ").")

    # Concatenate the series if asked to
    if concat_series:
        trials, signals, time_vector = concatenate_series(trials, signals, time_vector, verbose)

    # Variables
    perc = 10  # Progression marker
    time_window = []  # Time window array for the cross-correlation
    max_correlation = 0  # Max correlation to scale the plot
    joints_correlations = {}  # Dictionary to save the correlations

    for t in range(len(trials)):

        trial = trials[t]
        signal = signals[t]

        if verbose == 1:
            perc = show_progression(verbose, t, len(trials), perc, step=10)
        elif verbose > 1:
            print("Calculating correlation for sequence " + str(t + 1) + "/" + str(len(trials)) + "...")

        # Calculate the correlations
        if cross_correlation:
            joints_correlations, time_window = compute_cross_correlations(trial, signal, time_vector[t], window,
                                                                          joints_correlations)
        else:
            joints_correlations = compute_correlations(trial, signal, joints_correlations)

    # Averaging correlations
    average_correlations = {}
    if cross_correlation:
        average_correlations, max_correlation = average_cross_correlations(joints_correlations)
    else:
        for joint in joints_correlations.keys():
            if len(trials) == 1:
                average_correlations[joint] = joints_correlations[joint][0]
            else:
                average_correlations[joint] = sum(joints_correlations[joint]) / len(joints_correlations[joint])
            if abs(average_correlations[joint]) > max_correlation:
                max_correlation = abs(average_correlations[joint])

    # Printing the correlations
    if not cross_correlation:
        print_correlations(average_correlations, verbose)

    # Plotting the body graphs (cross-correlation)
    if cross_correlation and lag is None:
        plot_dictionary = {}
        for joint in average_correlations.keys():
            graph = Graph()
            graph.add_plot(time_window, average_correlations[joint], line_width, "#aa0000")
            plot_dictionary[joint] = graph
        plot_body_graphs(plot_dictionary, name="Cross-correlation")

    else:
        if cross_correlation:
            for joint in average_correlations.keys():
                if lag not in time_window:
                    raise Exception("Invalid lag input.")
                else:
                    average_correlations[joint] = average_correlations[joint][time_window.index(lag)]
        plot_silhouette(average_correlations, min_scale=min_scale, max_scale=max_scale, color_scheme=color_scheme,
                        name="Correlation")


def correlation_with_audio(sequence_or_sequences, audio_or_audios, concat_series=False, color_scheme="default",
                           min_scale="auto", max_scale="auto", verbose=1):
    """Calculates the correlation """

    # If there is one sequence only, we turn it into a list
    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]
    if type(audio_or_audios) is Audio:
        audio_or_audios = [audio_or_audios]

    trials = []
    time_vector = []
    for sequence in sequence_or_sequences:
        trials.append(sequence.get_velocities())
        time_vector.append(sequence.get_timestamps())

    signal = []
    for audio in audio_or_audios:
        signal.append(audio.envelope[1:])

    global_correlating(trials, signal, time_vector, concat_series, color_scheme=color_scheme, min_scale=min_scale,
                       max_scale=max_scale, verbose=verbose)


def correlation_with_joint(sequence_or_sequences, joint_to_correlate, concat_series=False, color_scheme="default",
                           min_scale="auto", max_scale="auto", verbose=1):
    # If there is one sequence only, we turn it into a list
    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]

    trials = []
    signal = []
    time_vector = []
    for sequence in sequence_or_sequences:
        joints_velocities = sequence.get_velocities()
        trials.append(joints_velocities)
        signal.append(joints_velocities[joint_to_correlate])
        time_vector.append(sequence.get_timestamps())

    global_correlating(trials, signal, time_vector, concat_series, color_scheme=color_scheme, min_scale=min_scale,
                       max_scale=max_scale, verbose=verbose)


def cross_correlation_with_audio(sequence_or_sequences, audio_or_audios, concat_series=False, lag=None, window=1,
                                 verbose=1):
    # If there is one sequence only, we turn it into a list
    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]
    if type(audio_or_audios) is Audio:
        audio_or_audios = [audio_or_audios]

    trials = []
    time_vector = []
    for sequence in sequence_or_sequences:
        trials.append(sequence.get_velocities())
        time_vector.append(sequence.get_timestamps())

    signal = []
    for audio in audio_or_audios:
        signal.append(audio.envelope[1:])

    global_correlating(trials, signal, time_vector, concat_series, cross_correlation=True, lag=lag, window=window,
                       verbose=verbose)


def cross_correlation_with_joint(sequence_or_sequences, joint_to_correlate, concat_series=False, lag=None, window=1,
                                 verbose=1):
    # If there is one sequence only, we turn it into a list
    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]

    trials = []
    signal = []
    time_vector = []
    for sequence in sequence_or_sequences:
        joints_velocities = sequence.get_velocities()
        trials.append(joints_velocities)
        signal.append(joints_velocities[joint_to_correlate])
        time_vector.append(sequence.get_timestamps())

    global_correlating(trials, signal, time_vector, concat_series, cross_correlation=True, lag=lag, window=window,
                       verbose=verbose)


def compute_correlations(trial, signal, correlations_dict=None, absolute_values=True):
    """Returns a dictionary with the correlation of all the elements of the dictionary time_series_dict to the
    target_time_series. If absolute_values is false, returns the raw value of the correlation."""

    if correlations_dict is None:
        correlations_dict = {}

    for key in trial.keys():
        # If the time series is 0 for the whole time series, we set the correlation on 0
        # (typically, the re-referenced joint):
        if trial[key] == [0.0 for _ in range(len(trial[key]))]:
            correlation = 0.0
        else:
            correlation = np.corrcoef(trial[key], signal)[0][1]
        if absolute_values:
            correlation = abs(correlation)

        # We add the correlation to the dictionary
        if key not in correlations_dict.keys():
            correlations_dict[key] = [correlation]
        else:
            correlations_dict[key].append(correlation)

    return correlations_dict


def compute_cross_correlations(trial, signal, time_vector, window, correlations_dict=None):
    if correlations_dict is None:
        correlations_dict = {}

    time, no_offsets = get_time_window(time_vector, window)
    print(time)

    for key in trial.keys():

        # Calculate correlations with offsets:
        # Highest peak positive: signal predicts the trial
        # Highest peak negative: signal is predicted by the trial
        correlations_forward = list(sm.tsa.stattools.ccf(signal[:len(trial[key])], trial[key], adjusted=False))
        correlations_backward = list(sm.tsa.stattools.ccf(trial[key], signal[:len(trial[key])], adjusted=False))

        # Get only the values of the time window
        correlations_forward = correlations_forward[:no_offsets]
        correlations_backward = correlations_backward[:no_offsets]
        correlations_backward.reverse()

        # Merging correlations in a single array
        correlations = correlations_backward[:-1] + correlations_forward
        print(correlations)

        # If the time series is NaN for the whole time series, we set the correlation on 0
        # (typically, the re-referenced joint):
        for cor in correlations:
            if np.isnan(cor):
                correlations = [0.0 for _ in range(len(correlations))]
                break

        # We add the correlation to the dictionary
        if key not in correlations_dict.keys():
            correlations_dict[key] = [correlations]
        else:
            correlations_dict[key].append(correlations)

    return correlations_dict, time


def concatenate_series(trials, signals, time_vector, verbose=1):

    if verbose > 0:
        print("Concatenating the series...", end=" ")

    meta_trials = copy.deepcopy(trials[0])
    meta_signals = signals[0]
    meta_time_series = time_vector[0]
    end_time = meta_time_series[-1]
    gap = meta_time_series[-1] - meta_time_series[-2]

    if len(trials) > 1:

        for seq in range(1, len(trials)):

            for key in trials[seq].keys():
                meta_trials[key] += trials[seq][key]

            key = trials[seq].keys()[0]
            meta_signals += signals[seq][:len(trials[seq][key])]

            for t in time_vector[seq]:
                meta_time_series.append(t + end_time + gap)

            end_time = meta_time_series[-1]
            gap = meta_time_series[-1] - meta_time_series[-2]

    print("100% - Done.")

    return meta_trials, meta_signals, meta_time_series


def get_time_window(time_vector, window):
    time = []
    time_forward = time_vector
    time_backward = [-i for i in time_vector]

    for i in range(len(time_backward)):
        if abs(time_backward[i]) <= window:
            time.append(time_backward[i])
        else:
            break

    no_offsets = len(time)
    time.reverse()
    time = time[:-1]

    for i in range(len(time_forward)):
        if abs(time_forward[i]) <= window:
            time.append(time_forward[i])
        else:
            break

    return time, no_offsets


def average_cross_correlations(correlations):
    average_correlations = {}
    max_correlation = 0

    for key in correlations.keys():
        average_correlations[key] = []

        for time_point in range(len(correlations[key][0])):
            time_point_cor = []

            for cor in correlations[key]:
                time_point_cor.append(cor[time_point])

            average_correlations[key].append(sum(time_point_cor) / len(time_point_cor))

            if abs(average_correlations[key][time_point]) > max_correlation:
                max_correlation = abs(average_correlations[key][time_point])

    return average_correlations, max_correlation


def print_correlations(correlations_dict, verbose=1):
    if verbose >= 1:
        print("\n== CORRELATIONS ==")
        ordered_correlations = sorted(correlations_dict.items(), key=lambda x: x[1])
        ordered_correlations.reverse()
        for cor in range(len(ordered_correlations)):
            print(str(cor + 1) + ".\t" + str(ordered_correlations[cor][0]) + "\t" + str(ordered_correlations[cor][1]))


def get_colors_correlations(correlations_dict, max_value, color_scheme="default"):
    """Returns a color for every value according to a gradient and a max value."""

    if type(color_scheme) == "string":
        color_scheme = convert_colors(color_scheme, "RGB", True)

    colors = {}

    for key in correlations_dict.keys():
        ratio = abs(correlations_dict[key]) / max_value
        colors[key] = calculate_color_ratio(color_scheme, ratio)

    return colors


# def correlate_with_audio_plot_frequencies(sequence, audio, color_scheme="default", line_width=1.0, verbose=1):
#     """
#     """
#
#     # Compute velocities of the joints
#     joints_velocity = sequence.get_velocities()  # Get the dictionary of the velocity for all joints
#     max_velocity = sequence.get_max_velocity()  # Get the max value for the velocity across all joints for scale
#     timestamps = sequence.get_timestamps()
#
#     # Define the dictionary of the subplots
#     plot_dictionary = {}  # Create a dictionary that will contain what to plot
#
#     # Calculate the correlations
#     joints_correlations = get_correlations(joints_velocity, audio.envelope[1:])
#     max_correlation = max(joints_correlations.values())  # Get the max value of the correlations for scale
#
#     # Determine color depending on global velocity
#     joints_colors = get_colors_correlations(joints_correlations, max_correlation, color_scheme)
#
#     # Scale the audio envelope for overlay
#     new_audio_envelope = get_scaled_audio(audio.get_envelope(), max_velocity)
#
#     # Create the plot dictionary
#     for joint in joints_velocity.keys():
#         graph = Graph()
#         graph.add_plot(timestamps, new_audio_envelope, line_width, "#d5cdd8")
#         graph.add_plot(timestamps[1:], joints_velocity[joint], line_width, joints_colors[joint])
#         plot_dictionary[joint] = graph
#     graph = Graph()
#     graph.add_plot(timestamps, list(audio.envelope), line_width, "#8e3faa")
#     plot_dictionary["Audio"] = graph
#
#     print_correlations(joints_correlations, verbose)
#
#     plot_body_graphs(plot_dictionary, max_correlation, "Correlation")


def global_coherence(trials, signals, time_vector, concat_series=False, frequency="auto", bands=128,
                     specific_band="all", line_width=1.0, show_scale=False, min_scale="auto", max_scale="auto",
                     color_scheme="default", verbose=1):

    # The two variables must have the same number of observations
    if len(trials) != len(signals):
        raise Exception("Non-matching number of sequences (" + str(len(trials)) +
                        ") and signals (" + str(len(signals)) + ").")

    # Concatenate the series if asked to
    if concat_series:
        trials, signals, time_vector = concatenate_series(trials, signals, time_vector, verbose)

    if frequency == "auto":
        frequency = int(1 / (time_vector[1] - time_vector[0]))
        if verbose > 1:
            print("Frequency detected automatically: " + str(frequency) + " Hz.")

    perc = 10  # Progression marker
    freq = [i * frequency / bands for i in range((bands // 2) + 1)]  # Frequencies for plotting
    max_coherence = 0  # Max coherence to scale the plot
    joints_coherences = {}  # Dictionary to save the coherences
    plot_dictionary = {}  # Dictionary to save the plots
    band = None  # Band for the silhouette plot

    # We get the index of the specific band if we want to plot a silhouette
    if specific_band != "all":
        if type(specific_band) in [int, float]:
            band = freq.index(specific_band)
        else:
            raise Exception("Invalid frequency band.")

    # Calculate the coherences
    for t in range(len(trials)):

        if verbose == 1:
            perc = show_progression(verbose, t, len(trials), perc, step=10)
        elif verbose > 1:
            print("Calculating coherence for sequence " + str(t+1) + "/" + str(len(trials)) + "...")

        trial = trials[t]
        signal = signals[t]

        # Compute coherences of the joints
        joints_coherences = compute_coherences(trial, signal, frequency, bands, joints_coherences)

    for joint in joints_coherences.keys():

        # We create a list of 0 coherence for every joint in all bands
        coherences = [0 for _ in range((bands // 2) + 1)]

        # For every sequence involved, we add the value of the coherence
        for seq in joints_coherences[joint]:
            for i in range(len(seq)):
                coherences[i] += seq[i]

        # We average the coherences
        if specific_band != "all":
            coherence = coherences[band] / len(joints_coherences[joint])
            plot_dictionary[joint] = coherence

        else:
            average_coherence = []

            for i in range(len(coherences)):
                average_coherence.append(coherences[i] / len(joints_coherences[joint]))
                if average_coherence[i] >= max_coherence:
                    max_coherence = average_coherence[i]

            graph = Graph()
            graph.add_plot(list(freq), list(average_coherence), line_width, "#000000")
            plot_dictionary[joint] = graph

    if specific_band != "all":
        plot_silhouette(plot_dictionary, min_scale=min_scale, max_scale=max_scale, color_scheme=color_scheme,
                        name="Coherence", show_scale=show_scale)
    else:
        plot_body_graphs(plot_dictionary, max_coherence, name="Coherence")


def coherence_with_audio(sequence_or_sequences, audio_or_audios, concat_series=False, frequency="auto", bands=128,
                         specific_band="all", line_width=1.0, show_scale=True, min_scale="auto", max_scale="auto",
                         color_scheme="default", verbose=1):

    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]
    if type(audio_or_audios) is Audio:
        audio_or_audios = [audio_or_audios]

    trials = []
    time_vector = []
    for sequence in sequence_or_sequences:
        trials.append(sequence.get_velocities())
        time_vector.append(sequence.get_timestamps())

    signal = []
    for audio in audio_or_audios:
        signal.append(audio.envelope[1:])

    global_coherence(trials, signal, time_vector, concat_series, frequency, bands, specific_band, line_width,
                     show_scale, min_scale, max_scale, color_scheme, verbose)


def coherence_with_joint(sequence_or_sequences, joint_to_cohere, concat_series=False, frequency="auto", bands=128,
                         specific_band="all", line_width=1.0, show_scale=True, min_scale="auto", max_scale="auto",
                         color_scheme="default", verbose=1):

    # If there is one sequence only, we turn it into a list
    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]

    trials = []
    signal = []
    time_vector = []
    for sequence in sequence_or_sequences:
        joints_velocities = sequence.get_velocities()
        trials.append(joints_velocities)
        signal.append(joints_velocities[joint_to_cohere])
        time_vector.append(sequence.get_timestamps())

    global_coherence(trials, signal, time_vector, concat_series, frequency, bands, specific_band, line_width,
                     show_scale, min_scale, max_scale, color_scheme, verbose)


def compute_coherences(trial, signal, frequency, bands, coherence_dict=None):
    """Returns a dictionary with the coherences of all the elements of the dictionary time_series_dict to the
    target_time_series. Does it for all the number of bands specified, in the limit of the max_frequency."""

    if coherence_dict is None:
        coherence_dict = {}

    for key in trial.keys():
        # If the time series is 0 for the whole time series, we set the coherence on 0
        # (typically, the re-referenced joint):
        if trial[key] == [0 for _ in range(len(trial[key]))]:
            coh = [0 for _ in range((bands // 2) + 1)]
        else:
            # coh, freq = plt.cohere(time_series_dict[key], target_time_series[1:len(time_series_dict[key]) + 1],
            #                       bands, max_frequency)
            coh, freq = plt.cohere(trial[key], signal, bands, frequency)

        if key not in coherence_dict.keys():
            coherence_dict[key] = []
        coherence_dict[key].append(coh)

    return coherence_dict


# def coherence_with_audio_meta(sequence_or_sequences, audio_or_audios, bands=128, max_frequency=8):
#     if type(sequence_or_sequences) is Sequence:
#         sequence_or_sequences = [sequence_or_sequences]
#     if type(audio_or_audios) is Audio:
#         audio_or_audios = [audio_or_audios]
#
#     plot_dictionary = {}
#
#     # Determine line width
#     line_width = 1.0
#
#     meta_sequence = {}
#     meta_audio = []
#
#     # Calculate the coherences
#     for seq in range(len(sequence_or_sequences)):
#
#         print("=== " + sequence_or_sequences[seq].name + " ===")
#
#         audio = audio_or_audios[seq]
#         sequence = sequence_or_sequences[seq]
#
#         # Compute velocities of the joints
#         joints_velocity = sequence.get_velocities()
#
#         for joint in joints_velocity.keys():
#             if joint not in meta_sequence.keys():
#                 meta_sequence[joint] = joints_velocity[joint]
#             else:
#                 meta_sequence[joint] += joints_velocity[joint]
#
#             meta_audio += audio.envelope[1:len(joints_velocity[joint]) + 1]
#
#         coh, freq = plt.cohere(joints_velocity[joint], audio.envelope[1:len(joints_velocity[joint]) + 1],
#                                bands, max_frequency)
#
#         if joint not in plot_dictionary.keys():
#             plot_dictionary[joint] = []
#         plot_dictionary[joint].append(coh)
#
#     max_coherence = 0
#
#     freq = [i * max_frequency / bands for i in range((bands // 2) + 1)]
#
#     for joint in plot_dictionary.keys():
#
#         # We create a list of 0 coherence for every joint in all bands
#         coherences = [0 for _ in range((bands // 2) + 1)]
#
#         # For every sequence involved, we add the value of the coherence
#         for seq in plot_dictionary[joint]:
#             for i in range(len(seq)):
#                 coherences[i] += seq[i]
#
#         average_coherence = [0 for _ in range((bands // 2) + 1)]
#
#         # We average the coherences
#         for i in range(len(coherences)):
#             average_coherence[i] = coherences[i] / len(plot_dictionary[joint])
#             if average_coherence[i] >= max_coherence:
#                 max_coherence = average_coherence[i]
#         plot_dictionary[joint] = [{"x": list(freq), "y": list(average_coherence),
#                                    "line_width": line_width, "color": "#000000"}]
#
#     plot_body_graphs(plot_dictionary, max_coherence, name="Coherence")
