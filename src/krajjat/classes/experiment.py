"""Default class defining an experiment. An experiment object can contain multiple subjects, which themselves can
contain multiple trials."""
import os
from collections import OrderedDict
from krajjat.tool_functions import get_system_csv_separator, show_progression


class Experiment(object):
    """Creates and return an Experiment object. An Experiment object can contain multiple Subject instances, which
    in turn contain Trial instances.

    .. versionadded:: 2.0

    Parameters
    ----------
    name: str, optional
        The name of the experiment.

    Attributes
    ----------
    name: str or None
        The name of the experiment.
    subjects: OrderedDict(subject)
        An ordered dictionary of Subject instances.
    """

    def __init__(self, name=None):
        self.name = name
        self.subjects = OrderedDict()

    # == Getter/Setter functions =======================================================================================

    def get_name(self):
        """Returns the attribute :attr:`name` of the Experiment instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The name of the experiment.
        """
        return self.name

    def set_name(self, name):
        """Sets the attribute :attr:`Experiment.name` of the Experiment instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name of the experiment.
        """
        self.name = name

    # == Managing subjects =============================================================================================

    def add_subject(self, subject):
        """Adds a Subject instance to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        subject: Subject
            A Subject instance.
        """
        if subject.name in self.subjects.keys():
            raise Exception(f"A subject with this name ({subject.name}) already exists in this experiment.")
        self.subjects[subject.name] = subject

    def get_subjects(self, names=None, group=None, **kwargs):
        """Returns the complete list or a sublist of subjects from the Experiment instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        names: list(str), optional
            A list of subject names. If provided, the returned Subject instances will be a sublist of the subjects
            from the experiment.
        group: str, int or None, optional
            If provided, the function will return the subjects having a :attr:`Subject.group` equal to the provided
            value. In the case were a list of subject names is also provided, the subjects in that list and belonging
            to that group will be returned.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Subject instances.

        Returns
        -------
        list(Subject)
            A list of Subject instances.
        """
        subjects = []

        if names is str:
            names = [names]

        for name in self.subjects.keys():
            add_subject = True

            if names is not None and name not in names:
                add_subject = False
            if group is not None and self.subjects[name].group != group:
                add_subject = False

            for arg in kwargs.keys():
                if getattr(self.subjects[name], arg) != kwargs[arg]:
                    add_subject = False

            if add_subject:
                subjects.append(self.subjects[name])

        return subjects

    def get_subjects_names(self):
        """Returns a list containing the attributes :attr:`subject.Subject.name` for each subject.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of all the subjects names.
        """
        return self.subjects.keys()

    def remove_subject(self, name):
        """Removes a subject from the Experiment instance corresponding to the given name.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name of the subject to remove.
        """
        if name in self.subjects.keys():
            del self.subjects[name]
        else:
            raise Exception(f"No subject with the name {name} was found in the experiment.")

    def get_number_of_subjects(self):
        """Returns the length of the :attr:`subjects` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The length of the :attr:`subjects` attribute.
        """
        return len(self.subjects)

    def get_joint_labels(self):
        """Returns the joint labels from the first sequence of the first subject of the experiment.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of joint labels.
        """
        joint_labels = []
        for subject in self.subjects.keys():
            joint_labels_subject = self.subjects[subject].get_joint_labels()
            for joint_label in joint_labels_subject:
                if joint_label not in joint_labels:
                    joint_labels.append(joint_label)

        return joint_labels

    def get_dataframe(self, sequence_measure="distance", audio_measure="envelope", sampling_frequency=None,
                      exclude_columns=None, include_columns=None, verbosity=1, **kwargs):
        """Returns the data from the experiment as a Pandas dataframe containing multiple columns.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence_measure: str or list(str), optional
            The time series to be returned, can be one or a combination of the following:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        audio_measure: str, list(str) or None, optional
            The time series to be returned, can be one or a combination of the following:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant
            • ``"intensity"``

            This value can also be `None`: in that case, none of the data will be affected to audio measures.

        sampling_frequency: float, optional
            The frequency at which to resample the two measures before adding them to the dataframe. By default,
            no resampling is applied. If the sampling frequency of the Sequence and its corresponding Audio differ,
            the function will return an exception.

        exclude_columns: list or None, optional
            A list of the columns to exclude from the dataframe. By default, the columns included are:

            • ``"subject"``, containing the subject :attr:`Subject.name`.
            • ``"group"``, containing the :attr:`Subject.group` attribute of the :class:`Subject` instances.
            • ``"trial"``, containing the :attr:`Trial.trial_id` attribute of each :class:`Trial` instance.
            • ``"condition"``, containing the :attr:`Trial.condition` attribute of each :class:`Trial` instance.
            • ``"modality"`, containing ``"mocap"`` for data from Sequence instances, ``"audio"`` for data from
              Audio instances, or ``"pca"`` or ``"ica"`` for data from PCA or ICA computations.
            • ``"label"``, containing the name of each feature: either the name of a joint label, ``"audio"``, or
              a PCA/ICA number.
            • ``"measure"``, indicating the selected sequence measure (e.g. ``"distance"``) or audio measure (e.g.
              ``"envelope"``
            • ``"timestamp"``, containing the timestamps for each Trial.
            • ``"value"``, containing the measure value of the current modality label at the given timestamp.

        include_columns: list or None, optional
            A list of columns to include to the dataframe. The function will try to find attributes matching the given
            column names in the Subject and the Trial instances.

            .. note::
            The function first tries to find the attribute value in the Subject instance, then in the Trial instances.
            If there is a match in the Subject instance, the function will not try to find an attribute value in the
            Trial instances, so ensure that you have unique attribute names between Subject and Trial instances.
            Moreover, if a specific attribute cannot be found for a specific Subject or Trial, the function sets the
            values to numpy.nan.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        **kwargs
            timestamp_start: float or None, optional
                If provided, the return values having a timestamp below the one provided will be ignored from the
                output.

            timestamp_end: float or None, optional
                If provided, the return values having a timestamp above the one provided will be ignored from the
                output.

        Note
        ----
        The function also allows to set a series af other attributes related to the generation of an Audio or
        AudioDerivative object. For example, if you choose `"envelope"` as an audio measure, you can add parameters
        used to generate an envelope in the function :meth:`Audio.get_envelope`, such as `"window_size"`
        or ``"filter_below"`; these will be directly used when generating the envelope. To know which parameters can be
        used for each audio derivative, please refer to the corresponding methods in the :class:`Audio`:
            • :meth:`Audio.filter_and_resample`
            • :meth:`Audio.get_envelope`
            • :meth:`Audio.get_pitch`
            • :meth:`Audio.get_formant`
            • :meth:`Audio.get_intensity`
        """

        if verbosity > 1:
            print("Creating a dataframe for the experiment.")
            print("Number of subjects: " + str(len(self.subjects)))
            print("Number of recordings: " + str(sum([len(s) for s in self.subjects])))

        # Import the modules
        try:
            import pandas as pd
        except ImportError:
            raise ModuleNotFoundError("pandas", "generating an experiment dataframe")

        try:
            import numpy as np
        except ImportError:
            raise ModuleNotFoundError("numpy", "generating an experiment dataframe")

        # Define the column headers
        columns = ["subject", "group", "trial", "condition", "modality", "label", "measure", "timestamp", "value"]
        if exclude_columns is not None:
            for column in exclude_columns:
                columns.remove(column)
        if include_columns is not None:
            for column in include_columns:
                columns.append(column)

        # Define measures
        if type(sequence_measure) is not list:
            sequence_measure = [sequence_measure]
        if audio_measure is not None and type(audio_measure) is not list:
            audio_measure = [audio_measure]

        # Define the joint labels
        joint_labels = self.get_joint_labels()

        # Create the dataframe skeleton
        data = {column: [] for column in columns}

        # Get timestamps if specified
        timestamp_start = kwargs.get("timestamp_start", None)
        timestamp_end = kwargs.get("timestamp_end", None)

        # Progression
        number_of_iterations = 0
        for subject in self.subjects:
            a = self.subjects[subject].get_number_of_trials()
            b = (len(joint_labels) + (audio_measure is not None))
            c = len(sequence_measure)
            d = 0
            if audio_measure is not None:
                d = len(audio_measure)
            number_of_iterations += a * b * (c + d)
        i = 0
        perc = 10

        if verbosity > 0:
            print("Creating the dataframe...")

        # For each subject
        for subject_name in self.subjects:

            if verbosity > 1:
                print(f"\tSubject {subject_name}")

            subject = self.subjects[subject_name]

            # For each trial
            for trial_id in subject.trials:

                if verbosity > 1:
                    print(f"\t\tTrial {trial_id}")

                trial = subject.trials[trial_id]

                if not trial.has_sequence():
                    raise Exception(f"A Sequence is missing for Subject {subject_name}, Trial {trial_id}.")
                sequence = trial.sequence

                if sequence.get_sampling_rate() != sampling_frequency:
                    sequence = sequence.resample(sampling_frequency, kwargs.get("mode", "pchip"), verbosity=verbosity)

                # For each measure (mocap)
                for measure in sequence_measure:

                    perc = show_progression(verbosity, i, number_of_iterations, perc)

                    if verbosity > 1:
                        print(f"\t\t\tMeasure {measure}")

                    sequence_values = sequence.get_time_series_as_list(measure, timestamp_start, timestamp_end,
                                                                       verbosity)
                    timestamps = sequence.get_timestamps_for_metric(measure, False, timestamp_start, timestamp_end)

                    # For each joint
                    for joint_label in joint_labels:
                        values_to_append = {"subject": subject_name, "group": subject.group, "trial": trial_id,
                                            "condition": trial.condition, "modality": "mocap", "label": joint_label,
                                            "measure": measure}
                        for column in columns:
                            if column in values_to_append.keys():
                                repeated_values = np.array([values_to_append[column] for _ in range(len(timestamps))])
                                data[column] = np.concatenate((data[column], repeated_values))
                            elif column == "timestamp":
                                data[column] = np.concatenate((data[column], timestamps))
                            elif column == "value":
                                if joint_label not in sequence_values.keys():
                                    data[column] = np.concatenate((data[column], np.full(np.shape(timestamps), np.nan)))
                                else:
                                    data[column] = np.concatenate((data[column], sequence_values[joint_label]))
                            elif hasattr(subject, column):
                                repeated_values = [getattr(subject, column) for _ in range(len(timestamps))]
                                data[column] = np.concatenate((data[column], repeated_values))
                            elif hasattr(trial, column):
                                repeated_values = [getattr(trial, column) for _ in range(len(timestamps))]
                                data[column] = np.concatenate((data[column], repeated_values))
                            else:
                                data[column] = np.concatenate((data[column], np.full(np.shape(timestamps), np.nan)))

                        i += 1

                # For each measure (audio)
                if audio_measure is not None:

                    perc = show_progression(verbosity, i, number_of_iterations, perc)

                    if not trial.has_audio():
                        raise Exception(f"An Audio is missing for Subject {subject_name}, Trial {trial_id}.")

                    for measure in audio_measure:

                        if verbosity > 1:
                            print(f"\t\t\tMeasure {measure}")

                        audio = trial.audio

                        audio = audio.get_derivative(measure, timestamp_start=timestamp_start,
                                                     timestamp_end=timestamp_end, verbosity=verbosity, **kwargs)

                        if audio.frequency != sampling_frequency:
                            audio = audio.resample(sampling_frequency, method=kwargs.get("resampling_mode", "pchip"),
                                                   window_size=kwargs.get("res_window_size", 1e7),
                                                   overlap_ratio=kwargs.get("res_overlap_ratio", 0.5),
                                                   verbosity=verbosity)

                        timestamps = audio.timestamps

                        values_to_append = {"subject": subject_name, "group": subject.group, "trial": trial_id,
                                            "condition": trial.condition, "modality": "audio", "label": "audio",
                                            "measure": measure}

                        for column in columns:
                            if column in values_to_append.keys():
                                repeated_values = np.array([values_to_append[column] for _ in range(len(timestamps))])
                                data[column] = np.concatenate((data[column], repeated_values))
                            elif column == "timestamp":
                                data[column] = np.concatenate((data[column], timestamps))
                            elif column == "value":
                                data[column] = np.concatenate((data[column], audio.samples))
                            elif hasattr(subject, column):
                                repeated_values = [getattr(subject, column) for _ in range(len(timestamps))]
                                data[column] = np.concatenate((data[column], repeated_values))
                            elif hasattr(trial, column):
                                repeated_values = [getattr(trial, column) for _ in range(len(timestamps))]
                                data[column] = np.concatenate((data[column], repeated_values))
                            else:
                                data[column] = np.concatenate((data[column], np.full(np.shape(timestamps), np.nan)))

                        i += 1

        return pd.DataFrame(data)

    def save_dataframe(self, folder_out="", name="dataframe", file_format="pkl", sequence_measure="distance",
                       audio_measure="envelope", sampling_frequency=None, exclude_columns=None, include_columns=None,
                       verbosity=1, **kwargs):
        """Saves a dataframe to disk.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str, optional
            The path to the folder where to save the dataframe. If one or more subfolders of the path do not exist,
            the function will create them. If the string provided is empty (by default), the sequence will be saved in
            the current working directory. If the string provided contains a file with an extension, the fields ``name``
            and ``file_format`` will be ignored.

        name: str,  optional
            Defines the name of the file or files where to save the dataframe. By default, it is set on `"dataframe`.

        file_format: str, optional
            The file format in which to save the sequence. The file format must be ``"pkl"`` (default), ``"gzip"``,
            ``"json"`` (default), ``"xlsx"``, ``"txt"``, ``"csv"``, ``"tsv"``, or, if you are a masochist,
            ``"mat"``. Notes:

                • ``"xls"`` will save the file with an ``.xlsx`` extension.
                · Excel files have a limited amount of rows, which may not be compatible with big datasets.
                • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
                • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
                  on ``,``. By default, the function will detect which separator the system uses.
                • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
                • Any other string will not return an error, but rather be used as a custom extension. The data will
                  be saved as in a text file (using tabulations as values separators).

        sequence_measure: str
            The time series to be returned, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        audio_measure: str
            The time series to be returned, can be either:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant
            • ``"intensity"``

        sampling_frequency: float, optional
            The frequency at which to resample the two measures before adding them to the dataframe. By default,
            no resampling is applied. If the sampling frequency of the Sequence and its corresponding Audio differ,
            the function will return an exception.

        exclude_columns: list or None, optional
            A list of the columns to exclude from the dataframe. By default, the columns included are:

            • `"subject"`, containing the subject :attr:`Subject.name`.
            • `"group"`, containing the :attr:`Subject.group` attribute of the :class:`Subject` instances.
            • `"trial"`, containing the :attr:`Trial.trial_id` attribute of each :class:`Trial` instance.
            • `"condition"`, containing the :attr:`Trial.condition` attribute of each :class:`Trial` instance.
            • `"joint_label"`, containing the name of each joint label for each sequence.
            • `"timestamp"`, containing the timestamps for each Trial.
            • A column containing the selected sequence measure, which will be either ``"x"``, ``"y"``, ``"z"``,
              ``"distance_hands"``, ``"distance"``, ``"distance_x"``, ``"distance_y"``, ``"distance_z"``,
              ``"velocity"``, ``"acceleration"``, or ``"acceleration_abs"``.
            • A column containing the selected audio measure, either ``"audio"``, ``"envelope"``, ``"pitch"``,
              `"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"``, or ``"intensity"``.

        include_columns: list or None, optional
            A list of columns to include to the dataframe. The function will try to find attributes matching the given
            column names in the Subject and the Trial instances.

            .. note::
            The function first tries to find the attribute value in the Subject instance, then in the Trial instances.
            If there is a match in the Subject instance, the function will not try to find an attribute value in the
            Trial instances, so ensure that you have unique attribute names between Subject and Trial instances.
            Moreover, if a specific attribute cannot be found for a specific Subject or Trial, the function sets the
            values to numpy.nan.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Note
        ----
        The function also allows to set a series af other attributes related to the generation of an Audio or
        AudioDerivative object. For example, if you choose `"envelope"` as an audio measure, you can add parameters
        used to generate an envelope in the function :meth:`Audio.get_envelope`, such as `"window_size"`
        or ``"filter_below"`; these will be directly used when generating the envelope. To know which parameters can be
        used for each audio derivative, please refer to the corresponding methods in the :class:`Audio`:
            • :meth:`Audio.filter_and_resample`
            • :meth:`Audio.get_envelope`
            • :meth:`Audio.get_pitch`
            • :meth:`Audio.get_formant`
            • :meth:`Audio.get_intensity`
        """

        dataframe = self.get_dataframe(sequence_measure, audio_measure, sampling_frequency, exclude_columns,
                                       include_columns, verbosity, **kwargs)

        if "." in folder_out.split("/")[-1]:
            path_out = folder_out
            folder_out = "/".join(folder_out.split("/")[:-1])
        else:
            path_out = folder_out + "/" + name + "." + file_format

        # Automatic creation of all the folders of the path if they don't exist
        os.makedirs(folder_out, exist_ok=True)
        extension = path_out.split(".")[-1]

        if extension == "json":
            dataframe.to_json(path_out)
        elif extension == "csv":
            sep = get_system_csv_separator()
            dataframe.to_csv(path_out, sep)
        elif extension in ["xls", "xlsx"]:
            dataframe.to_excel(path_out)
        elif extension == "pkl":
            dataframe.to_pickle(path_out)
        elif extension == "gzip":
            dataframe.to_parquet(path_out)
        elif extension == ".mat":
            try:
                import scipy.io.savemat as savemat
            except ImportError:
                raise ModuleNotFoundError("scipy", "saving a dataframe as a mat file")
            savemat(path_out, {"data": dataframe.to_dict()})
        else:
            with open(path_out) as f:
                f.write(dataframe.to_string())

    # == Print functions ==
    def print_subjects_details(self, include_trials=False, include_name=True, include_condition=True,
                               include_date_recording=True, include_number_of_poses=True, include_duration=True,
                               add_tabs=0):
        """Prints details on each Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_trials: bool, optional
            If set on `True`, the printed output will contain details from each trial contained in the subject.
        include_name: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`name` to the printed string.
        include_condition: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`condition` to the printed string.
        include_date_recording: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`date_of_recording` to the printed string.
        include_number_of_poses: bool, optional
            If set on ``True`` (default), adds the length of the attribute :attr:`poses` to the printed string.
        include_duration: bool, optional
            If set on ``True`` (default), adds the duration of the Sequence to the printed string.
        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.
        """

        t = add_tabs * "\t"
        # Header
        if len(self.subjects) == 1:
            title = t + f"==   Experiment {self.name}, with {len(self.subjects)} subject.   =="
        else:
            title = t + f"==   Experiment {self.name}, with {len(self.subjects)} subjects.   =="
        print(t + "=" * len(title))
        print(title)
        print(t + "=" * len(title) + str("\n"))

        # Subjects
        i = 0
        for subject_name in self.subjects.keys():
            subject = self.subjects[subject_name]
            # print(t + f"Subject {i + 1}/{len(self.subjects)}: {subject_name}")
            subject.print_sequences_details(include_trials, include_name, include_condition, include_date_recording,
                                            include_number_of_poses, include_duration, 1 + add_tabs)
            if i != len(self.subjects) - 1:
                print("")
            i += 1
