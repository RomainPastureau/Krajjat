from __future__ import annotations

import itertools
from typing import Any, Sequence
from numbers import Number

import numpy as np
import scipy
from pandas import DataFrame
from krajjat.classes.experiment import Experiment
from krajjat.tool_functions import CLEAN_DERIV_NAMES, convert_color, find_closest_value_index
from dataclasses import dataclass, field

StringOrSequence = str | Sequence[str]
OptionalStringOrSequence = StringOrSequence | None
TupleOrString = tuple[str, str] | str

@dataclass
class AnalysisParameters:
    # Required parameters
    analysis: str
    experiment_or_dataframe: Experiment | DataFrame | str | list[Experiment | DataFrame | str]

    # Core analysis parameters
    method: str | None = None
    sampling_rate: Number | str = "auto"

    # Filtering parameters
    groups: OptionalStringOrSequence = None
    conditions: OptionalStringOrSequence = None
    subjects: OptionalStringOrSequence = None
    trials: dict[str, StringOrSequence] | OptionalStringOrSequence = None

    # Measure parameters
    sequence_measure: OptionalStringOrSequence = None
    audio_measure: OptionalStringOrSequence = None
    target_measure: Sequence[TupleOrString] | TupleOrString | None = None

    # Analysis configuration
    series: str | None = None
    average: str | None = None
    result_type: str | None = "average"
    lags: Number | list[Number] | tuple[Number, ...] | None = None

    # Specific analyses parameters
    freq_resolution_hz: Number = 0.25
    n_neighbors: Number = 3
    mi_scale: str | None = "standard"
    mi_direction: str = "target"

    # Permutation parameters
    permutation_method: str | None = None
    number_of_randperms: int = 0
    random_seed: int | None = None

    # Specific frequency parameters
    specific_frequency: Number | list[Number] | tuple[Number, ...] | None = None
    freq_atol: Number = 0.1

    # Display parameters
    include_audio: bool = False
    color_line_series: OptionalStringOrSequence = None
    color_line_perm: OptionalStringOrSequence = None
    title: str | None = None
    width_line: Number = 1

    # Significance parameters
    signif_style: OptionalStringOrSequence = None
    signif_alpha: list[Number] | Number = 0.05
    signif_tail: str | int = 2
    signif_direction: str = "up"
    signif_target: str = "z-scores"

    # Internal parameters
    compute_permutations: bool = False

    # Misc. parameters
    verbosity: int = 1
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __init__(self, **init_kwargs):
        # Extract known args
        known_fields = {f.name for f in self.__dataclass_fields__.values()}
        fixed_args = {k: v for k, v in init_kwargs.items() if k in known_fields}
        extra_args = {k: v for k, v in init_kwargs.items() if k not in known_fields}

        # Assign known ones
        for k, v in fixed_args.items():
            setattr(self, k, v)

        # Fill defaults for missing fields
        for f in self.__dataclass_fields__.values():
            if not hasattr(self, f.name):
                setattr(self, f.name, f.default_factory() if callable(f.default_factory) else f.default)

        # Store unknown ones in kwargs
        self.kwargs = extra_args
        self.__post_init__()

    def __post_init__(self):

        # Analysis
        if self.analysis not in ("power spectrum", "correlation", "coherence", "mutual information"):
            raise ValueError(f"Invalid value for the parameter analysis: {self.analysis}.")

        # Method
        if self.method == "welsh":
            self.method = "welch"
        elif self.method == "pg":
            self.method = "pingouin"
        elif self.method in ["cross", "cross-spectrum"]:
            self.method = "cross_spectrum"
        elif self.method == "coherency":
            self.method = "complex"

        if self.analysis == "power spectrum" and self.method not in ("fft", "welch"):
            raise ValueError(f"Invalid value for the parameter method: {self.method}, must be fft or welch.")
        elif self.analysis == "correlation" and self.method not in ("pingouin", "numpy"):
            raise ValueError(f"Invalid value for the parameter method: {self.method}, must be pingouin or numpy.")

        # Sequence measures and audio measures
        if self.sequence_measure is not None:
            self.sequence_measure = self._to_list(self.sequence_measure)
        if self.audio_measure is not None:
            self.audio_measure = self._to_list(self.audio_measure)

        # Result type
        if self.result_type in ("avg", "average", "averages", "raw"):
            self.result_type = "average"
        elif self.result_type in ("z", "zscore", "zscores", "z-score", "zeta", "z-scores"):
            self.result_type = "z-scores"
        else:
            raise ValueError(f"Invalid value for the parameter result_type: {self.result_type} must be \"average\" "
                             f"or \"z-scores\".")

        # Significance target
        if self.signif_target is not None:
            if self.signif_target in ("z", "zscore", "zscores", "z-score", "zeta", "z-scores"):
                self.signif_target = "z-scores"
            elif self.signif_target in ("series", "condition"):
                self.signif_target = "series"
            else:
                raise ValueError(f"Invalid value for the parameter signif_target: {self.signif_target}, must be "
                                 f"\"z-scores\" or \"series\".")


        if isinstance(self.sampling_rate, (int, float)) and self.sampling_rate <= 0:
            raise ValueError("The parameter sampling_rate must be > 0.")

        # Permutations
        if self.permutation_method not in (None, "value", "label", "shift", "phase"):
            raise ValueError(f"Invalid value for the parameter permutation_method: {self.permutation_method}, "
                             f"must be value, label, shift or phase or None.")
        if self.permutation_method is not None and self.number_of_randperms > 0:
            self.compute_permutations = True
        else:
            self.compute_permutations = False

        if self.result_type == "z-scores" and not self.compute_permutations:
            raise Exception("If the return_values parameter is set to 'z-scores', the permutation_method parameter "
                            "must be set, and number_of_randperms has to be more than 0.")

        if self.number_of_randperms < 0:
            raise ValueError("The parameter number_of_randperms must be >= 0.")

        if self.freq_atol <= 0:
            raise ValueError("The parameter freq_atol must be > 0.")

        # Specific frequency
        if self.analysis == "correlation":
            self.specific_frequency = None

        if self.lags is None:
            self.lags = [0]
        else:
            if isinstance(self.lags, Number):
                self.lags = [self.lags]

    def _prepare_values(self, dataframe):
        if self.verbosity > 0:
            print(f"\nPreparing the variables for the analysis...")

        # Set the random seed for reproducibility on the randperm arrays
        self.rng = np.random.default_rng(self.random_seed)

        # Set the series of interest
        if self.series is not None:
            self.series_values = list(dataframe[self.series].unique())
        else:
            self.series_values = ["Full dataset"]

        if self.signif_target == "series":
            if self.series is None:
                raise ValueError("The parameter signif_target is set to 'series', but the parameter series is not "
                                 "defined.")
            elif len(self.series_values) != 2:
                raise ValueError("The parameter signif_target is set to 'series', but the parameter series does not "
                                 "separate the dataframe into exactly two series. For now, the toolbox only supports "
                                 "statistical analyses between exactly two series.")
            elif self.series == self.average:
                raise ValueError("The parameter signif_target is set to 'series', but the parameter series is set to "
                                 "the same value as the parameter average. For statistical comparisons, you cannot "
                                 f"average across {self.series}.")

        # Set the subjects/trials
        if self.average == "subject":
            if isinstance(self.subjects, str):
                self.individuals = [self.subjects]
            elif self.subjects is None:
                self.individuals = dataframe["subject"].unique()
            else:
                self.individuals = self.subjects

        elif self.average == "trial":
            if isinstance(self.trials, str):
                self.individuals = [self.trials]
            elif self.trials is None:
                self.individuals = dataframe["trial"].unique()
            else:
                self.individuals = self.trials
        else:
            self.individuals = ["All"]

        # Set the sequence and audio measures
        if self.sequence_measure is None:
            self.sequence_measure = []
        elif self.sequence_measure == ["auto"]:
            self.sequence_measure = list(dataframe.loc[dataframe["modality"] == "mocap"]["measure"].unique())
        self.sequence_measures = [CLEAN_DERIV_NAMES[sm] for sm in self.sequence_measure]

        if self.audio_measure is None:
            self.audio_measure = []
        elif self.audio_measure == ["auto"]:
            self.audio_measure = list(dataframe.loc[dataframe["modality"] == "audio"]["measure"].unique())
        self.audio_measures = [audio_measure for audio_measure in self.audio_measure]
        self.measures = self.sequence_measures + self.audio_measures

        # Get the unique labels (joint labels and audio measure)
        if self.include_audio:
            self.labels = dataframe["label"].unique()
        else:
            self.labels = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()
        self.measure_to_modality = self._infer_modalities(dataframe, "measure")
        self.label_to_modality = self._infer_modalities(dataframe, "label")

        self.labels_mocap = dataframe.loc[dataframe["modality"] == "mocap"]["label"].unique()
        self.labels_audio = ["Audio"]

        # Target measures
        self.target_measures = []
        if self.target_measure is not None:
            if isinstance(self.target_measure, str):
                self.target_measure = [self.target_measure]
            if isinstance(self.target_measure, list):
                for measure in self.target_measure:
                    if isinstance(measure, str):
                        if measure in self.labels_mocap:
                            for sequence_measure in self.sequence_measures:
                                self.target_measures.append((measure, sequence_measure))
                        else:
                            self.target_measures.append(("Audio", measure))
            if isinstance(self.target_measure, tuple):
                self.target_measures = [self.target_measure]
        elif self.analysis == "power spectrum":
            self.target_measures = ["power spectrum"]
        else:
            raise ValueError(f"The target measure has to be defined for a {self.analysis} analysis.")

        self._infer_sampling_rate(dataframe)

        # Default nperseg
        if self.analysis == "coherence":
            self.nperseg = self.sampling_rate / self.freq_resolution_hz

        if self.verbosity > 0:
            print("\tDone.")

        self._prepare_plot_variables()

        if isinstance(self.signif_style, str):
            self.signif_style = [self.signif_style]
        elif self.signif_style is None:
            self.signif_style = [None]

        for signif_style in self.signif_style:
            if signif_style is not None and signif_style not in ("threshold", "shade", "markers"):
                raise ValueError(f"Invalid value for the parameter signif_style: {signif_style}, must be "
                                 f"threshold, shade, markers or None.")

        if str(self.signif_tail).replace("-", "") in ("onetailed", "onetail", "1tailed", "1tail", "one",
                                                      "1"):
            self.signif_tail = "1"
        elif str(self.signif_tail).replace("-", "") in ("twotailed", "twotails", "twotail", "2tailed",
                                                        "2tails", "2tail", "two", "2"):
            self.signif_tail = "2"
        else:
            raise ValueError(f"Invalid value for the parameter signif_tail: {self.signif_tail}, must be one or two.")

    def _validate_lags(self, dataframe):
        # Validate that lags are in the correct time range
        trials_max = dataframe.groupby(["subject", "trial"])["timestamp"].max().to_numpy()
        min_of_max = np.min(trials_max)
        for lag in self.lags:
            if abs(lag) > min_of_max:
                raise ValueError(f"The provided lag {lag} is too large for the provided data. The maximum possible "
                                 f"lag is {min_of_max}.")

        # Get closest lags
        dt = 1 / self.sampling_rate
        snapped_lags = []
        for lag in self.lags:
            sample = lag / dt
            snapped_sample = np.round(sample)
            snapped_lags.append(snapped_sample * dt)
        self.lags = snapped_lags

    @staticmethod
    def _infer_modalities(dataframe, column):
        """Infers the modality ('mocap' or 'audio') associated with each measure and each label from the dataframe.

        versionadded:: 2.0

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Input dataframe containing 'label' and 'modality' columns.

        column: str
            A column from the dataframe.

        Returns
        -------
        dict
            A dictionary mapping each value in the column to its inferred modality.

        Raises
        ------
        ValueError
            If a label is found with more than one associated modality.
        """
        column_modality_map = dataframe.drop_duplicates(subset=[column, 'modality'])
        column_counts = column_modality_map.groupby(column)['modality'].nunique()

        ambiguous = column_counts[column_counts > 1].index.tolist()
        if ambiguous:
            raise ValueError(f"The following {column}s are associated with multiple modalities: {ambiguous}")

        return dict(zip(column_modality_map[column], column_modality_map['modality']))

    def _infer_sampling_rate(self, dataframe, tolerance=1e-3):
        """Infers the sampling rate from the time column, if possible."""

        if self.verbosity > 0:
            print("\nInferring the sampling rate from the dataframe to compare it with the provided sampling rate...")

        time_diffs = dataframe["timestamp"].diff().dropna()
        median_diff = time_diffs.median()
        if median_diff <= 0:
            raise ValueError("Invalid or non-monotonic time values found in the dataframe.")
        inferred_rate = 1.0 / median_diff

        if self.sampling_rate == "auto":
            self.sampling_rate = inferred_rate

        # Compare with provided value
        if not np.isclose(inferred_rate, self.sampling_rate, atol=1e-2):
            raise ValueError(f"The provided sampling_rate ({self.sampling_rate} Hz) does not match "
                             f"inferred rate from dataframe ({inferred_rate:.2f} Hz).")
        else:
            if self.verbosity > 0:
                print(f"\tThe provided sampling_rate ({self.sampling_rate} Hz) matches the inferred rate from the "
                      f"dataframe ({inferred_rate:.2f} Hz).")

    def _prepare_plot_variables(self):
        # Plot
        self.plot_type = "silhouette" if (self.specific_frequency is not None or
                                          self.analysis in ["correlation", "mutual information"]) else "body"

        # Create the plot title
        if self.title is None:
            self._create_plot_title()

        self.title_silhouette_auto = False
        if self.kwargs.get("title_silhouette", None) is None:
            self.title_silhouette_auto = True
            if self.plot_type == "silhouette":
                self.kwargs["title_silhouette"] = []

        if (self.kwargs.get("title_audio", None) is None and len(self.audio_measures) > 0 and
                self.audio_measures[0] is not None and self.plot_type == "body"):
            self.kwargs["title_audio"] = self.audio_measures[0].title() if len(self.audio_measures) == 1 else "Audio"

        self.color_line_series = self._define_color_series(self.color_line_series)
        self.color_line_perm = self._define_color_series(self.color_line_perm)

    def _create_plot_title(self):

        if self.analysis == "power spectrum":
            self.title = "Power spectrum"
        elif self.analysis == "correlation":
            self.title = "Correlation"
        elif self.analysis == "coherence":
            self.title = "Coherence"
        elif self.analysis == "mutual information":
            self.title = "Mutual information"

        if len(self.sequence_measures) == 1:
            self.title += f" of the {self.sequence_measures[0]}"
        else:
            self.title += f" of {len(self.sequence_measures)} sequence measures"

        if self.include_audio and self.specific_frequency is None and self.audio_measures[0] is not None:
            if len(self.audio_measures) == 1:
                self.title += f" and the {self.audio_measures[0]}"
            else:
                self.title += f" and {len(self.audio_measures)} audio measures"

        if self.analysis in ["correlation", "coherence", "mutual information"]:
            if len(self.target_measures) == 1:
                if isinstance(self.target_measures[0], tuple):
                    self.title += f" to the {self.target_measures[0][1]} of the {self.target_measures[0][0]}"
            else:
                self.title += f" to {len(self.target_measures)} measures"

        if self.specific_frequency is not None:
            if type(self.specific_frequency) == list:
                self.title += " at " + ", ".join([str(freq) for freq in self.specific_frequency]) + " Hz"
            else:
                self.title += " at " + str(self.specific_frequency) + " Hz"

        if len(self.lags) > 1:
            self.title += f" with {len(self.lags)} lags"

        settings = []
        if self.groups is not None:
            if type(self.groups) == str:
                settings.append(f"group: {self.groups}")
            elif len(self.groups) < 4:
                settings.append(f"groups: {', '.join(self.groups)}")
            else:
                settings.append(f"{len(self.groups)} groups")
        if self.conditions is not None:
            if type(self.conditions) == str:
                settings.append(f"condition: {self.conditions}")
            elif len(self.conditions) < 4:
                settings.append(f"conditions: {', '.join(self.conditions)}")
            else:
                settings.append(f"{len(self.conditions)} conditions")
        if self.subjects is not None:
            if type(self.subjects) == str:
                settings.append(f"subject: {self.subjects}")
            elif len(self.subjects) < 4:
                settings.append(f"subjects: {', '.join(self.subjects)}")
            else:
                settings.append(f"{len(self.subjects)} subjects")
        if self.trials is not None:
            if type(self.trials) == str:
                settings.append(f"trial: {self.trials}")
            elif type(self.trials) == dict:
                settings.append(f"multiple trials")
            else:
                settings.append(f"{len(self.trials)} trials")

        if len(settings) > 0:
            self.title += " (" + "; ".join(settings) + ")"

    def _define_color_series(self, color_line_series):
        color_series = {}

        if isinstance(color_line_series, str) or color_line_series is None:
            color_line_series = [color_line_series] * len(self.target_measures) * len(self.series_values) * len(self.lags)
        if not isinstance(color_line_series, list):
            color_line_series = [color_line_series]

        index = 0

        for target_measure in self.target_measures:

            color_series[target_measure] = {measure:
                                                {series_value:
                                                     {lag: None for lag in self.lags}
                                                 for series_value in self.series_values}
                                            for measure in self.measures}

            for measure in self.measures:

                for series_value in self.series_values:
                    for lag in self.lags:
                        if index < len(color_line_series):
                            if color_line_series[index] is not None:
                                color_line_series[index] = convert_color(color_line_series[index], "hex")
                            color_series[target_measure][measure][series_value][lag] = color_line_series[index]
                        index += 1

        return color_series
    
    def _get_specific_frequencies(self, frequencies):
        self.index_freqs = []
        self.nb_silhouettes_per_series = 1
        if self.specific_frequency is not None:
            if isinstance(self.specific_frequency, (int, float)):
                self.specific_frequency = [self.specific_frequency]
            for freq in self.specific_frequency:
                close_freq_index = find_closest_value_index(frequencies, freq, atol=self.freq_atol)
                if close_freq_index is not None:
                    self.index_freqs.append(int(close_freq_index))
                else:
                    raise Exception(f"The frequency {self.specific_frequency} was not found among the available "
                                    f"frequencies. Please select a value among {frequencies}.")

            if self.verbosity > 0:
                if len(self.index_freqs) == 1:
                    print("\tSelected frequency: " + str(frequencies[self.index_freqs[0]]) + " Hz.")
                else:
                    freqs = [str(np.round(frequencies[self.index_freqs[i]], 2)) for i in range(len(self.index_freqs))]
                    print("\tSelected frequencies: " + " Hz, ".join(freqs) + " Hz.")
                self.nb_silhouettes_per_series = len(self.index_freqs)
    
    def _generate_silhouette_titles(self, frequencies):
        # Silhouette title
        if self.plot_type == "silhouette" and self.title_silhouette_auto:
            for sequence_measure, target_measure, series_value, lag in itertools.product(self.sequence_measures,
                                                                                         self.target_measures,
                                                                                         self.series_values,
                                                                                         self.lags):
                t = []
                if len(self.sequence_measures) > 1:
                    t.append(sequence_measure.title())
                if len(self.sequence_measures) > 1 and len(self.target_measures) > 1:
                    t.append("to")
                if len(self.target_measures) > 1:
                    t.append(target_measure[1].title())
                    if target_measure[0] in self.labels_mocap:
                        t.append(target_measure[0].title())
                if len(self.series_values) > 1:
                    t.append(series_value.title())
                if len(self.lags) > 1 :
                    t.append(f"Lag {lag} s")
                if self.specific_frequency is not None and len(self.specific_frequency) > 1:
                    for i in range(len(self.specific_frequency)):
                        self.kwargs["title_silhouette"].append(
                            " ".join(t + [str(frequencies[self.index_freqs[i]]) + " Hz"]))
                else:
                    self.kwargs["title_silhouette"].append(" ".join(t))

    def _set_signif_graph_params(self):

        if isinstance(self.signif_alpha, (int, float)):
            self.signif_alpha = [self.signif_alpha]
        else:
            self.signif_alpha = [float(a) for a in self.signif_alpha]
        self.signif_alpha.sort()

        if self.plot_type == "body" and self.result_type == "z-scores":

            if "threshold" in self.signif_style:
                self.kwargs["horizontal_lines"] = []
            if "shade" in self.signif_style:
                self.kwargs["horizontal_shades"] = []
            if "markers" in self.signif_style:
                self.kwargs["signif_marker_values"] = []
                if "signif_marker" not in self.kwargs:
                    self.kwargs["signif_marker"] = "*"

            thresholds = []
            for alpha in self.signif_alpha:
                if self.signif_tail == "1":
                    thresholds.append(scipy.stats.norm.ppf(1 - alpha))
                else:
                    thresholds.append(scipy.stats.norm.ppf(1 - alpha / 2))

            bands = []
            if self.signif_tail == "1":
                if self.signif_direction == "up":
                    for i in range(len(thresholds) - 1):
                        bands.append((thresholds[i], thresholds[i + 1]))
                    bands.append((thresholds[-1], np.inf))
                else:
                    bands.append((-np.inf, -thresholds[-1]))
                    for i in range(len(thresholds) - 1, 0, -1):
                        bands.append((-thresholds[i], -thresholds[i - 1]))
            else:
                bands.append((-np.inf, -thresholds[-1]))
                for i in range(len(thresholds) - 1, 0, -1):
                    bands.append((-thresholds[i], -thresholds[i - 1]))
                for i in range(0, len(thresholds) - 1):
                    bands.append((thresholds[i], thresholds[i + 1]))
                bands.append((thresholds[-1], np.inf))

            if "threshold" in self.signif_style:
                if self.signif_tail == "1":
                    if self.signif_direction == "up":
                        self.kwargs["horizontal_lines"] = thresholds
                    else:
                        self.kwargs["horizontal_lines"] = [-threshold for threshold in thresholds]
                else:
                    self.kwargs["horizontal_lines"] = thresholds
                    self.kwargs["horizontal_lines"] += [-threshold for threshold in thresholds]

            if "shade" in self.signif_style:
                self.kwargs["horizontal_shades"] = bands

            if "markers" in self.signif_style:
                if self.signif_tail == "1":
                    if self.signif_direction == "up":
                        self.kwargs["signif_marker_values"] = [(threshold, np.inf) for threshold in thresholds]
                    elif self.signif_direction == "down":
                        self.kwargs["signif_marker_values"] = [(-np.inf, -threshold) for threshold in thresholds]
                else:
                    self.kwargs["signif_marker_values"] = [(-threshold, threshold) for threshold in thresholds]

    @staticmethod
    def _to_list(x: str | list[str] | tuple[str]) -> list[str]:
        return [x] if isinstance(x, str) else list(x)