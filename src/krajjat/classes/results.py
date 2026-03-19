"""Default class for analysis results."""
import json
import os
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path


class Results(object):

    def __init__(self, analysis_parameters, analysis_results, plot_dictionary, timestamp, duration):

        # Parse analysis parameters
        self.analysis = analysis_parameters.get("analysis", None)
        self.method = analysis_parameters.get("method", None)

        self.groups = analysis_parameters.get("groups", None)
        self.conditions = analysis_parameters.get("conditions", None)
        self.subjects = analysis_parameters.get("subjects", None)
        self.trials = analysis_parameters.get("trials", None)

        self.individuals = analysis_parameters.get("individuals", [])
        self.labels = analysis_parameters.get("labels", [])
        self.series_values = analysis_parameters.get("series_values", [])

        self.sequence_measures = analysis_parameters.get("sequence_measures", [])
        self.audio_measures = analysis_parameters.get("audio_measures", [])
        self.target_measures = analysis_parameters.get("target_measures", None)
        self.series = analysis_parameters.get("series", None)
        self.average = analysis_parameters.get("average", None)
        self.lags = analysis_parameters.get("lags", [0])
        self.labels_mocap = analysis_parameters.get("labels_mocap", [])

        self.result_type = analysis_parameters.get("result_type", None)
        self.permutation_method = analysis_parameters.get("permutation_method", None)
        self.number_of_randperms = analysis_parameters.get("number_of_randperms", None)
        self.random_seed = analysis_parameters.get("random_seed", None)
        self.specific_frequency = analysis_parameters.get("specific_frequency", None)
        self.freq_atol = analysis_parameters.get("freq_atol", None)
        self.include_audio = analysis_parameters.get("include_audio", None)

        self.color_line_series = analysis_parameters.get("color_line_series", None)
        self.color_line_perm = analysis_parameters.get("color_line_perm", None)
        self.title = analysis_parameters.get("title", None)
        self.width_line = analysis_parameters.get("width_line", None)
        self.verbosity = analysis_parameters.get("verbosity", None)
        self.kwargs = analysis_parameters.get("kwargs", {})

        # Parameters needed to fully reproduce the plot after loading
        self.sampling_rate = analysis_parameters.get("sampling_rate", None)
        self.freq_resolution_hz = analysis_parameters.get("freq_resolution_hz", None)
        self.fit_background = analysis_parameters.get("fit_background", False)
        self.background_lower_freq = analysis_parameters.get("background_lower_freq", None)
        self.signif_alpha = analysis_parameters.get("signif_alpha", 0.05)
        self.signif_tail = analysis_parameters.get("signif_tail", "1")
        self.signif_direction = analysis_parameters.get("signif_direction", "up")
        self.signif_style = analysis_parameters.get("signif_style", None)
        self.signif_target = analysis_parameters.get("signif_target", "z-scores")

        self.frequencies = analysis_results.get("frequencies", [])
        self.averages = analysis_results.get("averages", {})
        self.stds = analysis_results.get("stds", {})
        self.averages_perm = analysis_results.get("averages_perm", {})
        self.stds_perm = analysis_results.get("stds_perm", {})
        self.z_scores = analysis_results.get("z_scores", {})
        self.p_values = analysis_results.get("p_values", {})
        self.background_fits = analysis_results.get("background_fits", {})

        self.plot_dictionary = plot_dictionary

        self.timestamp = timestamp
        self.duration = duration

    # ── Serialization helpers ─────────────────────────────────────────────────

    @staticmethod
    def _encode(obj):
        """Recursively convert an object to a JSON-serialisable structure.

        Handles: numpy arrays/scalars, tuples (including as dict keys), datetime,
        timedelta, and Graph/GraphPlot objects.
        """
        if isinstance(obj, np.ndarray):
            return {"__type__": "ndarray", "data": obj.tolist(), "dtype": str(obj.dtype)}
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, datetime):
            return {"__type__": "datetime", "data": obj.isoformat()}
        elif isinstance(obj, timedelta):
            return {"__type__": "timedelta", "seconds": obj.total_seconds()}
        elif isinstance(obj, tuple):
            return {"__type__": "tuple", "data": [Results._encode(v) for v in obj]}
        elif isinstance(obj, dict):
            return {
                "__type__": "dict",
                "items": [[Results._encode(k), Results._encode(v)] for k, v in obj.items()]
            }
        elif isinstance(obj, list):
            return [Results._encode(v) for v in obj]
        elif hasattr(obj, "__dict__"):
            # Graph and GraphPlot — serialise by class name + attributes
            return {
                "__type__": "object",
                "class": type(obj).__name__,
                "attrs": Results._encode(obj.__dict__)
            }
        return obj

    @staticmethod
    def _decode(obj):
        """Recursively restore a JSON-decoded structure to its original Python types."""
        if isinstance(obj, list):
            return [Results._decode(v) for v in obj]
        if not isinstance(obj, dict):
            return obj

        t = obj.get("__type__")

        if t == "ndarray":
            return np.array(obj["data"], dtype=obj["dtype"])
        elif t == "datetime":
            return datetime.fromisoformat(obj["data"])
        elif t == "timedelta":
            return timedelta(seconds=obj["seconds"])
        elif t == "tuple":
            return tuple(Results._decode(v) for v in obj["data"])
        elif t == "dict":
            return {Results._decode(k): Results._decode(v) for k, v in obj["items"]}
        elif t == "object":
            return Results._restore_object(obj["class"], Results._decode(obj["attrs"]))

        # Plain JSON dict with no __type__ tag (e.g. from older saves) — decode values
        return {k: Results._decode(v) for k, v in obj.items()}

    @staticmethod
    def _restore_object(class_name, attrs):
        """Reconstruct a Graph or GraphPlot from its serialised attributes."""
        try:
            from krajjat.classes.graph_element import Graph, GraphPlot
        except ImportError:
            # Return a plain namespace if krajjat is unavailable
            obj = type(class_name, (), {})()
            obj.__dict__.update(attrs)
            return obj

        if class_name == "Graph":
            obj = Graph.__new__(Graph)
        elif class_name == "GraphPlot":
            obj = GraphPlot.__new__(GraphPlot)
        else:
            # Unknown class — keep as plain dict rather than silently losing data
            return attrs
        obj.__dict__.update(attrs)
        return obj

    def _build_payload(self):
        """Assemble the full serialisable payload from self."""
        analysis_parameters = {
            "analysis":             self.analysis,
            "method":               self.method,
            "groups":               self.groups,
            "conditions":           self.conditions,
            "subjects":             self.subjects,
            "trials":               self.trials,
            "individuals":          list(self.individuals),
            "labels":               list(self.labels),
            "series_values":        list(self.series_values),
            "sequence_measures":    list(self.sequence_measures),
            "audio_measures":       list(self.audio_measures),
            "target_measures":      self.target_measures,
            "series":               self.series,
            "average":              self.average,
            "lags":                 list(self.lags),
            "labels_mocap":         list(self.labels_mocap),
            "result_type":          self.result_type,
            "permutation_method":   self.permutation_method,
            "number_of_randperms":  self.number_of_randperms,
            "random_seed":          self.random_seed,
            "specific_frequency":   self.specific_frequency,
            "freq_atol":            self.freq_atol,
            "include_audio":        self.include_audio,
            "color_line_series":    self.color_line_series,
            "color_line_perm":      self.color_line_perm,
            "title":                self.title,
            "width_line":           self.width_line,
            "verbosity":            self.verbosity,
            "kwargs":               self.kwargs,
            "sampling_rate":        self.sampling_rate,
            "freq_resolution_hz":   self.freq_resolution_hz,
            "fit_background":       self.fit_background,
            "background_lower_freq": self.background_lower_freq,
            "signif_alpha":         self.signif_alpha,
            "signif_tail":          self.signif_tail,
            "signif_direction":     self.signif_direction,
            "signif_style":         self.signif_style,
            "signif_target":        self.signif_target,
        }
        analysis_results = {
            "frequencies":      self.frequencies,
            "averages":         self.averages,
            "stds":             self.stds,
            "averages_perm":    self.averages_perm,
            "stds_perm":        self.stds_perm,
            "z_scores":         self.z_scores,
            "p_values":         self.p_values,
            "background_fits":  self.background_fits,
        }
        return {
            "krajjat_results_version": 1,
            "analysis_parameters": Results._encode(analysis_parameters),
            "analysis_results":    Results._encode(analysis_results),
            "plot_dictionary":     Results._encode(self.plot_dictionary),
            "timestamp":           Results._encode(self.timestamp),
            "duration":            Results._encode(self.duration),
        }

    def save(self, path):
        """Save the Results object to a JSON file.

        Parameters
        ----------
        path : str or Path
            Destination file path. The appropriate extension is added automatically
            if not already present.

        Examples
        --------
        >>> out.save("results/coherence_velocity.json")           # JSON, lossless
        """
        path = Path(path)
        if path.suffix != ".json":
            path = path.with_suffix(".json")
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._build_payload(), f, indent=2, ensure_ascii=False)
        print(f"Results saved to {path}")

    @classmethod
    def load(cls, path):
        """Load a Results object previously saved with :meth:`Results.save`.
        The loaded object includes the full plot dictionary and can be passed directly to :func:`plot_body_graphs`.

        Parameters
        ----------
        path : str or Path
            Path to the ``.json`` file.

        Returns
        -------
        Results

        Examples
        --------
        >>> out = Results.load("results/coherence_velocity.json")
        >>> print(out)
        >>> plot_body_graphs(out.plot_dictionary, ...)
        """
        path = Path(path)
        if path.suffix != ".json":
            path = path.with_suffix(".json")

        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        version = raw.get("krajjat_results_version", 1)
        if version != 1:
            raise ValueError(f"Unsupported results file version: {version}")

        analysis_parameters = cls._decode(raw["analysis_parameters"])
        analysis_results    = cls._decode(raw["analysis_results"])
        plot_dictionary     = cls._decode(raw["plot_dictionary"])
        timestamp           = cls._decode(raw["timestamp"])
        duration            = cls._decode(raw["duration"])

        return cls(analysis_parameters, analysis_results, plot_dictionary, timestamp, duration)

    def __repr__(self):
        out = []

        title = f"Results for the {self.analysis}"
        out.append(title)
        out.append("=" * len(title))
        out.append("Analysis finished on " + self.timestamp.strftime("%A %d %B %Y, %H:%M:%S"))
        out.append("Duration: " + str(self.duration))
        out.append("")

        title = "Parameters"
        out.append(title)
        out.append("-" * len(title))
        out.append(f"Method: {self.method}")

        if self.analysis == "power spectrum":
            tms = ["Power spectrum"]
        else:
            tms = [tm[1].title() if tm[1] not in self.labels_mocap else tm[1].title() + " " + tm[0].title() for tm in self.target_measures]
        if self.analysis == "correlation":
            out.append(f"Correlation with: {', '.join(tms)}")
        elif self.analysis == "coherence":
            out.append(f"Coherence with: {', '.join(tms)}")
        if len(self.sequence_measures) == 1:
            out.append(f"Sequence measure: {self.sequence_measures[0].title()}")
        else:
            out.append(f"Sequence measures: {', '.join([sm.title() for sm in self.sequence_measures])}")
        if len(self.audio_measures) == 1:
            out.append(f"Audio measure: {self.audio_measures[0].title()}")
        else:
            out.append(f"Audio measures: {', '.join([am.title() for am in self.audio_measures])}")
        if self.series is not None:
            out.append(f"Series: {self.series.title()}")
        else:
            out.append(f"Series: Whole dataset")
        if self.average is not None:
            out.append(f"Average: {self.average.title()}")
        else:
            out.append(f"Average: Whole dataset")
        if self.lags == [0]:
            out.append(f"No lag specified")
        else:
            out.append(f"Specified lags: {', '.join([str(lag) for lag in self.lags])}")
        out.append("")

        title = "Dataframe filters"
        out.append(title)
        out.append("-" * len(title))

        if isinstance(self.groups, (tuple, list)):
            if len(self.groups) == 1:
                out.append(f"Group: {self.groups[0]}")
            elif len(self.groups) > 1:
                out.append(f"Groups: {', '.join(self.groups)}")
        elif isinstance(self.groups, str):
            out.append(f"Group: {self.groups}")

        if isinstance(self.conditions, (tuple, list)):
            if len(self.conditions) == 1:
                out.append(f"Condition: {self.conditions[0]}")
            elif len(self.conditions) > 1:
                out.append(f"Conditions: {', '.join(self.conditions)}")
        elif isinstance(self.conditions, str):
            out.append(f"Condition: {self.conditions}")

        if isinstance(self.subjects, (tuple, list)):
            if len(self.subjects) == 1:
                out.append(f"Subject: {self.subjects[0]}")
            elif len(self.subjects) > 1:
                out.append(f"Subjects: {', '.join(self.subjects)}")
        elif isinstance(self.subjects, str):
            out.append(f"Subject: {self.subjects}")

        if isinstance(self.trials, dict):
            if len(self.trials) == 1 and len(self.trials[list(self.trials.keys())[0]]) == 1:
                out.append(f"Trial:")
            else:
                out.append(f"Trials:")
            for subject in self.trials:
                out.append(f"\t{subject}: {', '.join(self.trials[subject])}")
        if isinstance(self.trials, (tuple, list)):
            if len(self.trials) == 1:
                out.append(f"Trial: {self.subjects[0]}")
            elif len(self.trials) > 1:
                out.append(f"Trials: {', '.join(self.trials)}")
        elif isinstance(self.trials, str):
            out.append(f"Trial: {self.trials}")
        out.append("")

        title = "Results"
        out.append(title)
        out.append("-" * len(title))
        out.append("")

        if len(self.averages) > 0:
            title = "Averages"
            out.append("\t" + title)
            out.append("\t" + "~" * len(title))
            out.append("")

            for target_measure in self.averages:
                if target_measure == "power spectrum":
                    title = "Power spectrum"
                else:
                    if target_measure[1] in self.labels_mocap:
                        title = f"{target_measure[1].title()} {target_measure[0]}"
                    else:
                        title = f"{target_measure[1].title()}"
                out.append("\t\t" + title)
                out.append("\t\t" + "~" * len(title))
                out.append("")

                for series_value in self.series_values:
                    title = series_value
                    out.append(f"\t\t\t{title}")
                    out.append("\t\t\t" + "~" * len(title))
                    out.append("")

                    for measure in self.averages[target_measure]:
                        for label in self.averages[target_measure][measure][series_value]:
                            if len(self.lags) > 1:
                                out.append(f"\t\t\t\t {measure.title()} {label}: ")
                                for lag in self.averages[target_measure][measure][series_value][label]:
                                    if self.averages[target_measure][measure][series_value][label][lag].size < 3:
                                        out.append(f"\t\t\t\t\tLag {lag} s: {self.averages[target_measure][measure][series_value][label][lag]} (SD: "
                                               f"{self.stds[target_measure][measure][series_value][label][lag]})")
                                    else:
                                        out.append(f"\t\t\t\t\tLag {lag} s: {self.averages[target_measure][measure][series_value][label][lag].size} values")
                            else:
                                if self.averages[target_measure][measure][series_value][label][self.lags[0]].size < 3:
                                    out.append(f"\t\t\t\t {measure.title()} {label}: "
                                               f"{self.averages[target_measure][measure][series_value][label][self.lags[0]]} (SD: "
                                               f"{self.stds[target_measure][measure][series_value][label][self.lags[0]]})")
                                else:
                                    out.append(f"\t\t\t\t {measure.title()} {label}: "
                                               f"{self.averages[target_measure][measure][series_value][label][self.lags[0]].size} values")

                    out.append("")

        if len(self.z_scores) > 0:
            title = "Z-scores"
            out.append("\t" + title)
            out.append("\t" + "~" * len(title))
            out.append("")

            for target_measure in self.z_scores:
                if target_measure == "power spectrum":
                    title = "Power spectrum"
                else:
                    if target_measure[1] in self.labels_mocap:
                        title = f"{target_measure[1].title()} {target_measure[0]}"
                    else:
                        title = f"{target_measure[1].title()}"
                out.append("\t\t" + title)
                out.append("\t\t" + "~" * len(title))
                out.append("")

                for series_value in self.series_values:
                    title = series_value
                    out.append(f"\t\t\t{title}")
                    out.append("\t\t\t" + "~" * len(title))
                    out.append("")

                    for measure in self.z_scores[target_measure]:
                        for label in self.z_scores[target_measure][measure][series_value]:
                            if len(self.lags) > 1:
                                out.append(f"\t\t\t\t {measure.title()} {label}: ")
                                for lag in self.z_scores[target_measure][measure][series_value][label]:
                                    if self.z_scores[target_measure][measure][series_value][label][lag].size < 3:
                                        out.append(f"\t\t\t\t\tLag {lag} s: {self.z_scores[target_measure][measure][series_value][label][lag]} (p-value: "
                                               f"{self.p_values[target_measure][measure][series_value][label][lag]})")
                                        if isinstance(self.p_values[target_measure][measure][series_value][label][lag],
                                                      (int, float)):
                                            val = self.p_values[target_measure][measure][series_value][label][lag]
                                        else:
                                            val = np.min(self.p_values[target_measure][measure][series_value][label][lag])
                                        if val <= 0.001:
                                            out[-1] += "***"
                                        elif val <= 0.01:
                                            out[-1] += "**"
                                        elif val <= 0.05:
                                            out[-1] += "*"
                                    else:
                                        out.append(f"\t\t\t\t\tLag {lag} s: {self.z_scores[target_measure][measure][series_value][label][lag].size} values")
                            else:
                                if self.z_scores[target_measure][measure][series_value][label][self.lags[0]].size < 3:
                                    out.append(f"\t\t\t\t {measure.title()} {label}: "
                                               f"{self.z_scores[target_measure][measure][series_value][label][self.lags[0]]} (p-value: "
                                               f"{self.p_values[target_measure][measure][series_value][label][self.lags[0]]})")
                                    if isinstance(self.p_values[target_measure][measure][series_value][label][self.lags[0]], (int, float)):
                                        val = self.p_values[target_measure][measure][series_value][label][self.lags[0]]
                                    else:
                                        val = np.min(self.p_values[target_measure][measure][series_value][label][self.lags[0]])
                                    if val <= 0.001:
                                        out[-1] += "***"
                                    elif val <= 0.01:
                                        out[-1] += "**"
                                    elif val <= 0.05:
                                        out[-1] += "*"
                                else:
                                    out.append(f"\t\t\t\t {measure.title()} {label}: "
                                               f"{self.z_scores[target_measure][measure][series_value][label][self.lags[0]].size} values")

                    out.append("")

        if len(self.background_fits) > 0:
            title = "Background fits"
            out.append("\t" + title)
            out.append("\t" + "~" * len(title))
            out.append("")

            for target_measure in self.background_fits:
                for measure in self.background_fits[target_measure]:
                    for series_value in self.series_values:
                        for label in self.background_fits[target_measure][measure][series_value]:
                            for lag in self.background_fits[target_measure][measure][series_value][label]:
                                fit = self.background_fits[target_measure][measure][series_value][label][lag]
                                n_peaks = len(fit["peak_indices"])
                                peak_str = (f"{n_peaks} peak(s) at "
                                            f"{', '.join([f'{f:.3f} Hz' for f in fit['peak_freqs']])}"
                                            if n_peaks > 0 else "no significant peaks")
                                out.append(f"\t\t\t\t {measure.title()} {label}: "
                                           f"slope={fit['slope']:.2f}, "
                                           f"R²={fit['r_squared']:.3f}, "
                                           f"lower bound={fit['lower_freq_used']:.3f} Hz, "
                                           f"{peak_str}")
            out.append("")

        return "\n".join(out)