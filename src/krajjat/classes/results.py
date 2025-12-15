"""Default class for analysis results."""
import numpy as np


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

        self.frequencies = analysis_results.get("frequencies",[])
        self.averages = analysis_results.get("averages", {})
        self.stds = analysis_results.get("stds", {})
        self.averages_perm = analysis_results.get("averages_perm", {})
        self.stds_perm = analysis_results.get("stds_perm", {})
        self.z_scores = analysis_results.get("z_scores", {})
        self.p_values = analysis_results.get("p_values", {})

        self.plot_dictionary = plot_dictionary

        self.timestamp = timestamp
        self.duration = duration

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
            out.append(f"Specified lags: {", ".join([str(lag) for lag in self.lags])}")
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
            if len(self.trials) == 1 and len(self.trials[list(self.trials.keys())[0]] == 1):
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

        return "\n".join(out)