"""Default class defining an experiment. An experiment object can contain multiple subjects, which themselves can
contain multiple trials."""
import os
from os import path as op
from collections import OrderedDict
from scipy.io import savemat

from krajjat.classes import Audio
from krajjat.tool_functions import get_system_csv_separator, show_progression

import pandas as pd
import numpy as np


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

    Example
    -------
    >>> experiment = Experiment("My experiment")
    >>> subject = Subject("Lambert")
    >>> experiment.add_subject(subject)
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

        Experiment
        ----------
        >>> experiment = Experiment("My experiment")
        >>> experiment.get_name()
        My experiment
        """
        return self.name

    def set_name(self, name):
        """Sets the attribute :attr:`Experiment.name` of the Experiment instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name of the experiment.

        Example
        -------
        >>> experiment = Experiment()
        >>> experiment.set_name("My experiment")
        """
        self.name = name

    # == Managing subjects =============================================================================================

    def add_subject(self, subject, replace_if_exists=False):
        """Adds a Subject instance to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        subject: Subject
            A Subject instance.
        replace_if_exists: bool, optional
            If set on `False`, the function will raise an exception if a subject with the same name already exists in
            the experiment instance.

        Note
        ----
        Subjects must have a name; adding a subject without a name will result in an error.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> experiment.add_subject(Subject("Carole-Anne"))
        """
        if not replace_if_exists and subject.name in self.subjects.keys():
            raise Exception(f"A subject with this name ({subject.name}) already exists in this experiment.")
        if subject.name is None:
            raise Exception("The subject must have a name.")
        self.subjects[subject.name] = subject

    def add_subjects(self, *subjects, replace_if_exists=False):
        """Adds multiple Subject instances to the experiment.

        .. versionadded:: 2.0

        Parameters
        ----------
        subjects: Subject
            One or many Subject instances.
        replace_if_exists: bool, optional
            If set on `False`, the function will raise an exception if a subject with the same name already exists in
            the experiment instance.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> subject1 = Subject("Maxime")
        >>> subject2 = Subject("Laurène")
        >>> subject3 = Subject("Margaux")
        >>> experiment.add_subjects(subject1, subject2, subject3)
        """
        for subject in subjects:
            self.add_subject(subject, replace_if_exists)

    def get_subject(self, name):
        """Returns the Subject instance corresponding to the given name.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name of the subject to retrieve.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> subject = Subject("Stéphane")
        >>> experiment.add_subject(subject)
        >>> experiment.get_subject("Stéphane")
        """
        return self.subjects[name]

    def get_subjects(self, names=None, group=None, return_type="dict", **kwargs):
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
        return_type: str, optional
            Defines if to return the subjects as a dictionary or a list. The default value is ``"dict"``, which returns
            the subjects as a dictionary with the subject names as keys. If set to ``"list"``, the function will return
            a list containing the subject in the same order as their names passed as parameter.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Subject instances.

        Returns
        -------
        list(Subject)
            A list of Subject instances.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> subject1 = Subject("Chloé", group="Control")
        >>> subject2 = Subject("Jérôme", group="Experimental")
        >>> subject3 = Subject("Étienne", group="Control")
        >>> experiment.add_subjects(subject1, subject2, subject3)
        >>> experiment.get_subjects()  # Returns all the subjects
        >>> experiment.get_subjects(group="Control")  # Returns all the subjects from the group "Control" (1 and 3)
        >>> experiment.get_subjects(["Chloé", "Jérôme"])  # Returns subjects 1 and 2
        """
        if type(names) in [str, int]:
            names = [names]

        subjects = []

        if names is None:
            names = self.subjects.keys()

        for name in names:
            add_subject = True

            if group is not None and self.subjects[name].group != group:
                add_subject = False

            for arg in kwargs.keys():
                if getattr(self.subjects[name], arg) != kwargs[arg]:
                    add_subject = False

            if add_subject:
                subjects.append(self.subjects[name])

        if return_type == "list":
            return subjects
        else:
            return {subject.get_name(): subject for subject in subjects}

    def get_subjects_names(self, group=None, **kwargs):
        """Returns a list containing the attributes :attr:`subject.Subject.name` for each subject.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of all the subjects names.
        group: str, int or None, optional
            If provided, the function will return the subjects having a :attr:`Subject.group` equal to the provided
            value. In the case were a list of subject names is also provided, the subjects in that list and belonging
            to that group will be returned.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Subject instances.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> subject1 = Subject("Tom")
        >>> subject2 = Subject("Floriane")
        >>> subject3 = Subject("Hélène")
        >>> experiment.add_subjects(subject1, subject2, subject3)
        >>> experiment.get_subjects_names()
        ["Tom", "Floriane", "Hélène"]
        """
        return list(self.get_subjects(None, group, "dict", **kwargs).keys())

    def remove_subject(self, name):
        """Removes a subject from the Experiment instance corresponding to the given name.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name of the subject to remove.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> subject1 = Subject("Arthur")
        >>> experiment.remove_subject("Arthur")
        """
        if name in self.subjects:
            del self.subjects[name]
        else:
            raise Exception(f"No subject with the name {name} was found in the experiment.")

    def get_number_of_subjects(self, group=None, **kwargs):
        """Returns the length of the :attr:`subjects` attribute, or the number of subjects in the experiment matching
        the group or other attributes.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The length of the :attr:`subjects` attribute.
        group: str, int or None, optional
            If provided, the function will return the subjects having a :attr:`Subject.group` equal to the provided
            value. In the case were a list of subject names is also provided, the subjects in that list and belonging
            to that group will be returned.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Subject instances.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> subject1 = Subject("Sacha")
        >>> subject2 = Subject("Tallulah")
        >>> subject3 = Subject("Mika")
        >>> experiment.add_subjects(subject1, subject2, subject3)
        >>> experiment.get_number_of_subjects()
        3
        """
        return len(self.get_subjects(None, group, "dict", **kwargs).keys())

    def get_joint_labels(self):
        """Returns the joint labels from the first sequence of the first subject of the experiment.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of joint labels.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> subject1 = Subject("Robin")
        >>> trial1 = Trial("R001", sequence=Sequence("Robin/sequence_001.txt"))  # Head
        >>> trial2 = Trial("R002", sequence=Sequence("Robin/sequence_002.txt"))  # Head, HandRight
        >>> subject1.add_trials(trial1, trial2)
        >>> subject2 = Subject("Alain")
        >>> trial1 = Trial("R001", sequence=Sequence("Alain/sequence_001.txt"))  # HandRight, HandLeft
        >>> trial2 = Trial("R002", sequence=Sequence("Alain/sequence_002.txt"))  # KneeRight
        >>> subject2.add_trials(trial1, trial2)
        >>> experiment.add_subjects(subject1, subject2)
        >>> experiment.get_joint_labels()
        ["Head", "HandRight", "HandLeft", "KneeRight"]
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
            • For any derivative of a higher order, set the corresponding integer.

        audio_measure: str, list(str) or None, optional
            The time series to be returned, can be one or a combination of the following:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant
            • ``"intensity"``

            This value can also be `None`: in that case, none of the data will be affected to audio measures.
            If the subjects' trials contain audio instances, and this parameter is set on an audio derivative,
            the audio derivative will be calculated, which can take some time. If the audio measure is set on an
            AudioDerivative and the subjects' trials contain the same AudioDerivative, the data will be taken as-is.
            Any other case will return an error.

        sampling_frequency: float, optional
            The frequency at which to resample the two measures before adding them to the dataframe. By default,
            no resampling is applied. If the sampling frequency of the Sequence and its corresponding Audio or
            AudioDerivative differ, the function will return an exception.

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
              ``"envelope"``)
            • ``"timestamp"``, containing the timestamps for each Trial.
            • ``"value"``, containing the measure value of the current modality label at the given timestamp.

        include_columns: list or None, optional
            A list of columns to include to the dataframe. The function will try to find attributes matching the given
            column names in the Subject and the Trial instances.

            .. note::
                The function first tries to find the attribute value in the Subject instance, then in the Trial
                instances. If there is a match in the Subject instance, the function will not try to find an attribute
                value in the Trial instances, so ensure that you have unique attribute names between Subject and Trial
                instances. Moreover, if a specific attribute cannot be found for a specific Subject or Trial, the
                function sets the values to numpy.nan.

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
        used to generate an envelope in the function :meth:`Audio.get_envelope`, such as ``"window_size"``
        or ``"filter_below"``; these will be directly used when generating the envelope. To know which parameters can be
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
            print("Number of trials: " + str(sum([len(t) for t in self.subjects])))

        # Default columns
        columns = ["subject", "group", "trial", "condition", "modality", "label", "measure", "timestamp", "value"]

        # Excluding the requested columns
        if exclude_columns is not None:
            for column in exclude_columns:
                columns.remove(column)

        # Including the requested columns
        if include_columns is not None:
            for column in include_columns:
                columns.append(column)

        # Define measures
        if type(sequence_measure) is not list:
            sequence_measure = [sequence_measure]
        if type(audio_measure) is not list:
            if audio_measure is not None:
                audio_measure = [audio_measure]
            else:
                audio_measure = []

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
            number_of_trials = self.subjects[subject].get_number_of_trials()
            number_of_seq_measures = len(joint_labels) * len(sequence_measure)
            number_of_aud_measures = len(audio_measure)
            number_of_iterations += number_of_trials * (number_of_seq_measures + number_of_aud_measures)
        #     print(f"{subject}: {number_of_trials} trials, {number_of_seq_measures} sequence measures, {number_of_aud_measures} audio measures.")
        # print("Number of iterations: " + str(number_of_iterations))
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

                if len(audio_measure) > 0 and not trial.has_audio():
                    raise Exception(f"An Audio is missing for Subject {subject_name}, Trial {trial_id}.")

                if sequence.get_sampling_rate() != sampling_frequency:
                    sequence = sequence.resample(sampling_frequency,
                                                 method=kwargs.get("method", "cubic"),
                                                 window_size=kwargs.get("window_size", 1e7),
                                                 overlap_ratio=kwargs.get("overlap_ratio", 0.5),
                                                 verbosity=verbosity)

                # For each measure (mocap)
                for measure in sequence_measure:

                    perc = show_progression(verbosity, i, number_of_iterations, perc)

                    if verbosity > 1:
                        print(f"\t\t\tMeasure {measure}")

                    sequence_values = sequence.get_measure(measure,
                                                           timestamp_start=timestamp_start,
                                                           timestamp_end=timestamp_end,
                                                           window_length=kwargs.get("window_length", 7),
                                                           poly_order=kwargs.get("poly_order", None),
                                                           verbosity=verbosity)

                    timestamps = sequence.get_timestamps(relative=True,
                                                         timestamp_start=timestamp_start,
                                                         timestamp_end=timestamp_end)

                    timestamps = timestamps[len(timestamps) - len(sequence_values[joint_labels[0]]):]

                    # For each joint
                    for joint_label in joint_labels:
                        values_to_append = {"subject": subject_name,
                                            "group": subject.group,
                                            "trial": trial_id,
                                            "condition": trial.condition,
                                            "modality": "mocap",
                                            "label": joint_label,
                                            "measure": measure}

                        for column in columns:

                            # Repeat the value for the first columns
                            if column in values_to_append.keys():
                                repeated_values = np.array([values_to_append[column] for _ in range(len(timestamps))])
                                data[column] = np.concatenate((data[column], repeated_values))

                            # Timestamps
                            elif column == "timestamp":
                                data[column] = np.concatenate((data[column], timestamps))

                            # Value
                            elif column == "value":
                                if joint_label not in sequence_values.keys():
                                    data[column] = np.concatenate((data[column], np.full(np.shape(timestamps), np.nan)))
                                else:
                                    data[column] = np.concatenate((data[column], sequence_values[joint_label]))

                            # Subject attribute
                            elif hasattr(subject, column):
                                repeated_values = [getattr(subject, column) for _ in range(len(timestamps))]
                                data[column] = np.concatenate((data[column], repeated_values))

                            # Trial attribute
                            elif hasattr(trial, column):
                                repeated_values = [getattr(trial, column) for _ in range(len(timestamps))]
                                data[column] = np.concatenate((data[column], repeated_values))

                            # Attribute not found (nan)
                            else:
                                data[column] = np.concatenate((data[column], np.full(np.shape(timestamps), np.nan)))

                        i += 1

                # For each measure (audio)
                for measure in audio_measure:

                    perc = show_progression(verbosity, i, number_of_iterations, perc)

                    if verbosity > 1:
                        print(f"\t\t\tMeasure {measure}")

                    audio = trial.audio

                    if type(audio) is Audio and measure != "audio":
                        audio = audio.get_derivative(measure,
                                                     filter_over=kwargs.get("filter_over", None),
                                                     filter_below=kwargs.get("filter_below", None),
                                                     timestamp_start=timestamp_start,
                                                     timestamp_end=timestamp_end,
                                                     verbosity=verbosity)
                    elif type(audio).__name__ != measure.title():
                        raise Exception(f"Impossible to derive the measure {measure} from a {type(audio).__name__} "
                                        f"object.")

                    if audio.frequency != sampling_frequency:
                        audio = audio.resample(sampling_frequency,
                                               method=kwargs.get("resampling_mode", "cubic"),
                                               window_size=kwargs.get("res_window_size", 1e7),
                                               overlap_ratio=kwargs.get("res_overlap_ratio", 0.5),
                                               verbosity=verbosity)

                    audio_values = audio.get_samples()
                    timestamps = audio.timestamps

                    values_to_append = {"subject": subject_name,
                                        "group": subject.group,
                                        "trial": trial_id,
                                        "condition": trial.condition,
                                        "modality": "audio",
                                        "label": "audio",
                                        "measure": measure}

                    for column in columns:

                        # Repeat the value for the first columns
                        if column in values_to_append.keys():
                            repeated_values = np.array([values_to_append[column] for _ in range(len(timestamps))])
                            data[column] = np.concatenate((data[column], repeated_values))

                        # Timestamps
                        elif column == "timestamp":
                            data[column] = np.concatenate((data[column], timestamps))

                        # Value
                        elif column == "value":
                            data[column] = np.concatenate((data[column], audio.samples))

                        # Subject attribute
                        elif hasattr(subject, column):
                            repeated_values = [getattr(subject, column) for _ in range(len(timestamps))]
                            data[column] = np.concatenate((data[column], repeated_values))

                        # Trial attribute
                        elif hasattr(trial, column):
                            repeated_values = [getattr(trial, column) for _ in range(len(timestamps))]
                            data[column] = np.concatenate((data[column], repeated_values))

                        # Attribute not found (nan)
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
            Defines the name of the file or files where to save the dataframe. By default, it is set on `"dataframe"`.

        file_format: str, optional
            The file format in which to save the sequence. The file format must be ``"pkl"`` (default), ``"gzip"``,
            ``"json"`` (default), ``"xlsx"``, ``"txt"``, ``"csv"``, ``"tsv"``, or, if you are a masochist,
            ``"mat"``. Notes:

            • ``"xls"`` will save the file with an ``.xlsx`` extension.
            • Excel files have a limited amount of rows, which may not be compatible with big datasets.
            • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
            • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
              on ``,``. By default, the function will detect which separator the system uses.
            • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
            • Any other string will not return an error, but rather be used as a custom extension. The data will
              be saved as in a text file (using tabulations as values separators).

        sequence_measure: str or list(str), optional
            The time series to be returned, can be one or a combination of the following:

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
            • For any derivative of a higher order, set the corresponding integer.

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

            • ``"subject"``, containing the subject :attr:`Subject.name`.
            • ``"group"``, containing the :attr:`Subject.group` attribute of the :class:`Subject` instances.
            • ``"trial"``, containing the :attr:`Trial.trial_id` attribute of each :class:`Trial` instance.
            • ``"condition"``, containing the :attr:`Trial.condition` attribute of each :class:`Trial` instance.
            • ``"joint_label"``, containing the name of each joint label for each sequence.
            • ``"timestamp"``, containing the timestamps for each Trial.
            • A column containing the selected sequence measure, which will be either ``"x"``, ``"y"``, ``"z"``,
              ``"distance_hands"``, ``"distance"``, ``"distance_x"``, ``"distance_y"``, ``"distance_z"``,
              ``"velocity"``, ``"acceleration"``, or ``"acceleration_abs"``.
            • A column containing the selected audio measure, either ``"audio"``, ``"envelope"``, ``"pitch"``,
              ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"``, or ``"intensity"``.

        include_columns: list or None, optional
            A list of columns to include to the dataframe. The function will try to find attributes matching the given
            column names in the Subject and the Trial instances.

            .. note::
                The function first tries to find the attribute value in the Subject instance, then in the Trial
                instances. If there is a match in the Subject instance, the function will not try to find an attribute
                value in the Trial instances, so ensure that you have unique attribute names between Subject and Trial
                instances. Moreover, if a specific attribute cannot be found for a specific Subject or Trial, the
                function sets the values to numpy.nan.

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
        used to generate an envelope in the function :meth:`Audio.get_envelope`, such as ``"window_size"``
        or ``"filter_below"``; these will be directly used when generating the envelope. To know which parameters can be
        used for each audio derivative, please refer to the corresponding methods in the :class:`Audio`:

            • :meth:`Audio.filter_and_resample`
            • :meth:`Audio.get_envelope`
            • :meth:`Audio.get_pitch`
            • :meth:`Audio.get_formant`
            • :meth:`Audio.get_intensity`
        """

        dataframe = self.get_dataframe(sequence_measure, audio_measure, sampling_frequency, exclude_columns,
                                       include_columns, verbosity, **kwargs)

        if folder_out == "":
            folder_out = os.getcwd()

        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0:
            if "." in subfolders[-1]:
                folder_out = op.split(folder_out)[0]
                name, file_format = op.splitext(subfolders[-1])

        file_format = file_format.strip(".")  # We remove the dot in the format
        if file_format in ["xlsx", "xl", "xls", "excel"]:
            file_format = "xlsx"

        os.makedirs(folder_out, exist_ok=True)

        path_out = op.join(folder_out, name + "." + file_format)

        if file_format == "json":
            dataframe.to_json(path_out)
        elif file_format in ["csv", "tsv", "txt"]:
            if file_format == "csv":
                sep = get_system_csv_separator()
            else:
                sep = "\t"
            dataframe.to_csv(path_out, sep=sep, index=False)
        elif file_format == "xlsx":
            dataframe.to_excel(path_out, index=False)
        elif file_format == "pkl":
            dataframe.to_pickle(path_out)
        elif file_format == "gzip":
            dataframe.to_parquet(path_out)
        elif file_format == "mat":
            savemat(path_out, {"data": {name: col.values for name, col in dataframe.items()}})

    def __len__(self):
        """Returns the total amount of subjects present in the Experiment instance.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The amount of subjects present in the Experiment instance.

        Example
        -------
        >>> experiment = Experiment("My experiment")
        >>> experiment.add_subject(Subject("Raphaël"))
        >>> experiment.add_subject(Subject("Chris"))
        >>> len(experiment)
        2
        """
        return len(self.subjects)

    def __getitem__(self, name):
        """Returns a subject, given a name.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str|int
            The name of the subject to retrieve.

        Returns
        -------
        Subject
            A Subject instance (if a Subject with the given name exists).

        Example
        -------
        >>> subject = Subject("Mathilde")
        >>> experiment = Experiment("My experiment")
        >>> experiment.add_subject(subject)
        >>> experiment["Mathilde"]
        """
        return self.subjects[name]