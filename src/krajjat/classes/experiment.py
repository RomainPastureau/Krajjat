"""Default class defining an experiment. An experiment object can contain multiple subjects, which themselves can
contain multiple sequences."""
import os

from krajjat.classes.exceptions import InvalidParameterValueException
from krajjat.tool_functions import get_system_csv_separator


class Experiment(object):
    """Creates and return an Experiment object. An Experiment object can contain multiple Subject instances, which
    in turn contain Sequence instances.

    .. versionadded:: 2.0

    Parameters
    ----------
    name: str, optional
        The name of the experiment.

    Attributes
    ----------
    name: str or None
        The name of the experiment.
    subjects: list(Subject)
        A list of Subject instances.
    """

    def __init__(self, name=None):
        self.name = name
        self.subjects = []

    def set_name(self, name):
        """Sets the attribute :attr:`Experiment.name` of the Experiment instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name of the experiment.
        """
        self.name = name

    def add_subject(self, subject):
        """Adds a Subject instance to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        subject: Subject
            A Subject instance.
        """
        self.subjects.append(subject)

    def get_subjects(self):
        """Returns the attribute :attr:`subjects` of the Experiment instance.

        .. versionadded:: 2.0

        Returns
        -------
        list(Subject)
            A list of Subject instances.
        """
        return self.subjects

    def get_subjects_names(self):
        """Returns a list containing the attributes :attr:`subject.Subject.name` for each subject.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of all the subjects names.
        """
        names = []
        for subject in self.subjects:
            names.append(subject.get_name())
        return names

    def get_subject_from_index(self, subject_index):
        """Returns the Subject instance matching the given index.

        .. versionadded:: 2.0

        Parameters
        ----------
        subject_index: int
            The index of the subject.

        Returns
        -------
        Subject
            A Subject instance corresponding to the provided index.
        """
        return self.subjects[subject_index]

    def get_subject_from_name(self, subject_name):
        """Returns the first Subject instance in :attr:`subjects` having the attribute
        :attr:`~krajjat.classes.subject.Subject.name` matching the name provided as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        subject_name: str
            The :attr:`~krajjat.classes.subject.Subject.name` attribute of a Subject instance.

        Returns
        -------
        Subject
            A Subject instance having the provided name as it attribute :attr:`~krajjat.classes.subject.Subject.name`.
        """
        for subject in self.subjects:
            if subject.get_name() == subject_name:
                return subject

    def remove_subject_from_index(self, subject_index):
        """Removes a subject from the Experiment instance corresponding to the given index.

        .. versionadded:: 2.0

        Parameters
        ----------
        subject_index: int
            The index of the subject to remove.
        """
        del self.subjects[subject_index]

    def remove_subject_from_name(self, subject_name):
        """Removes the first Subject instance in :attr:`subjects` having the attribute :attr:`subject.Subject.name`
        matching the name provided as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        subject_name: str
            The name attribute of a Subject instance.
        """
        for subject in self.subjects:
            if subject.get_name() == subject_name:
                self.subjects.remove(subject)
                break

    def get_subjects_from_group(self, group):
        """Returns a list of all the subjects that have an attribute :attr:`subject.Subject.group` equal to
        the condition provided.

        .. versionadded:: 2.0

        Parameters
        ----------
        group: str
            An subject group.

        Returns
        -------
        list(Subject)
            A list of Subject instances.
        """
        selected_subjects = []
        for subject in self.subjects:
            if subject.get_condition() == group:
                selected_subjects.append(subject)
        return selected_subjects

    def get_subjects_from_attribute(self, attribute, value):
        """Returns a list of all the subjects that have a provided attribute equal to a provided value.

        .. versionadded:: 2.0

        Parameters
        ----------
        attribute: str
            The name of the Subject attribute to compare to the value.
        value: any
            The value to match to each Subject's provided attribute.
        """
        selected_subjects = []
        for subject in self.subjects:
            if subject.get_attribute(attribute) == value:
                selected_subjects.append(subject)
        return selected_subjects

    def get_number_of_subjects(self):
        """Returns the length of the :attr:`subjects` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The length of the :attr:`subjects` attribute.
        """
        return len(self.subjects)

    def get_name(self):
        """Returns the attribute :attr:`name` of the Experiment instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The name of the experiment.
        """
        return self.name

    def get_joint_labels(self):
        """Returns the joint labels from the first sequence of the first subject of the experiment.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of joint labels.
        """
        return self.subjects[0].get_sequence_from_index(0).get_joint_labels()

    def get_dataframe(self, sequence_metric="distance", audio_metric="envelope", audio_filter_below=None,
                      audio_filter_above=None, audio_resampling_frequency=None):

        print(audio_metric)

        import pandas as pd
        sequence_metric_header = sequence_metric.title()
        audio_metric_header = audio_metric.title()
        data = {"Subject": [], "Group": [], "Trial": [], "Condition": [], "Joint label": [], "Timestamp": [],
                sequence_metric_header: [], audio_metric_header: []}

        for subject in self.subjects:

            for i in range(len(subject.get_sequences())):
                sequence = subject.get_sequence_from_index(i)
                sequence_values = sequence.get_time_series_as_list(sequence_metric)
                timestamps = sequence.get_timestamps_for_metric(sequence_metric)

                if i < subject.get_number_of_audios():
                    audio = subject.get_audio_from_index(i)
                else:
                    raise Exception("Discrepancy between the number of audios (" + str(subject.get_number_of_audios()) +
                                    " and the number of sequences (" + str(subject.get_number_of_sequences()))

                #audio_or_derivative = self._get_audio_values(audio, audio_metric, audio_filter_above, audio_filter_below,
                #                                      audio_resampling_frequency)
                audio_or_derivative = audio

                for joint_label in self.get_joint_labels():
                    sequence_values_joint = sequence_values[joint_label]
                    audio_start_index = len(sequence) - len(sequence_values_joint)
                    audio_end_index = len(sequence_values_joint) + audio_start_index
                    audio_values_trimmed = list(audio_or_derivative.get_samples())[audio_start_index:audio_end_index]

                    # if audio_or_derivative.get_frequency() != sequence.get_framerate():
                    #     raise Exception("The framerate of the sequence (" + str(sequence.get_framerate()) + ") is " +
                    #                     "different from the frequency of the " + str(type(audio_or_derivative)) + " (" +
                    #                     str(audio_or_derivative.get_frequency()) + "). Please be sure that the two " +
                    #                     "variables are sampled at the same rate before proceeding.")
                    #
                    # if audio_or_derivative.get_timestamps()[audio_start_index] != timestamps[0]:
                    #     raise Exception("The first timestamp of the sequence (" + timestamps[0] + ") is different " +
                    #                     "from the first timestamp of the " + str(type(audio_or_derivative)) + " (" +
                    #                     str(audio_or_derivative.get_timestamps()[audio_start_index]) + "). Please be " +
                    #                     "sure that the two variables are sampled at the same rate before proceeding.")

                    data["Subject"] += [subject.get_name() for _ in range(len(sequence_values_joint))]
                    data["Group"] += [subject.get_group() for _ in range(len(sequence_values_joint))]
                    data["Trial"] += [sequence.get_name() for _ in range(len(sequence_values_joint))]
                    data["Condition"] += [sequence.get_condition() for _ in range(len(sequence_values_joint))]
                    data["Joint label"] += [joint_label for _ in range(len(sequence_values_joint))]
                    data["Timestamp"] += timestamps
                    data[sequence_metric_header] += sequence_values_joint
                    data[audio_metric_header] += audio_values_trimmed

        return pd.DataFrame(data)

    def save_dataframe(self, path, sequence_metric="distance", audio_metric="envelope", audio_filter_below=None,
                      audio_filter_above=None, audio_resampling_frequency=None):

        dataframe = self.get_dataframe(sequence_metric, audio_metric, audio_filter_below, audio_filter_above,
                                       audio_resampling_frequency)

        os.makedirs(path, exist_ok=True)
        extension = path.split(".")[-1]

        if extension == "json":
            dataframe.to_json(path)
        elif extension == "csv":
            sep = get_system_csv_separator()
            dataframe.to_csv(path, sep)
        elif extension in ["xls", "xlsx"]:
            dataframe.to_excel(path)
        elif extension == ".mat":
            try:
                import scipy.io.savemat as savemat
            except ImportError:
                raise ModuleNotFoundError("scipy", "saving a dataframe as a mat file")
            savemat(path, {"data": dataframe.to_dict()})
        else:
            with open(path) as f:
                f.write(dataframe.to_string())

    def _get_audio_values(self, audio, audio_metric, audio_filter_below, audio_filter_above, audio_resampling_frequency):
        if audio_metric == "audio":
            return audio.filter_and_resample(audio_filter_below, audio_filter_above, audio_resampling_frequency)
        elif audio_metric == "envelope":
            return audio.get_envelope(audio_filter_below, audio_filter_above, audio_resampling_frequency)
        elif audio_metric == "intensity":
            return audio.get_intensity(audio_filter_below, audio_filter_above, audio_resampling_frequency)
        elif audio_metric == "pitch":
            return audio.get_pitch(audio_filter_below, audio_filter_above, audio_resampling_frequency)
        elif audio_metric.startswith("f") and len(audio_metric) == 2:
            return audio.get_formant(audio_filter_below, audio_filter_above, audio_resampling_frequency,
                                     formant_number=int(audio_metric[1]))
        else:
            raise InvalidParameterValueException("audio_metric", audio_metric)

    # == Print functions ==
    def print_subjects_details(self, include_name=True, include_condition=True, include_date_recording=True,
                                include_number_of_poses=True, include_duration=True):
        """Prints details on each Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
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
        """
        if len(self.subjects) == 1:
            title = "=   Experiment " + str(self.name) + ", with " + str(len(self.subjects)) + " subject.   ="
        else:
            title = "=   Experiment " + str(self.name) + ", with " + str(len(self.subjects)) + " subjects.   ="
        print("=" * len(title))
        print(title)
        print("=" * len(title) + str("\n"))

        for i in range(len(self.subjects)):
            subject = self.subjects[i]
            print("Subject " + str(i+1) + "/" + str(len(self.subjects)))
            subject.print_sequences_details(include_name, include_condition, include_date_recording,
                                            include_number_of_poses, include_duration)
            if i != len(self.subjects) - 1:
                print("")
