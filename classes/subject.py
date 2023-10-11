"""Default class defining a subject, that can contain multiple sequences and audio clips. This class can be used in the
stats functions to calculate variances across participants."""

import datetime
import math

from classes.audio import Audio
from classes.sequence import Sequence
from tool_functions import order_sequences_by_date


class Subject(object):
    """Creates an instance from the class Subject, and returns a Subject object, which matches one individual that
    performed one or multiple recordings. Upon creation, a Subject instance contains no Sequence instances. They can
    be added with the methods :meth:`Subject.add_sequence` or :meth:`Subject.load_sequence`.

    .. versionadded:: 2.0

    Parameters
    ----------
    name: str or None, optional
        The name or identifier of the subject.
    group: str or None, optional
        The experimental group the subject belongs to.
    gender: str or None, optional
        The gender of the subject (e.g. ``"F"```or ``"Female"``).
    age: int or None, optional
        The age of the subject, in years.

    Attributes
    ----------
    name: str or None
        The name or identifier of the subject.
    group: str or None
        The experimental group the subject belongs to.
    gender: str or None
        The gender of the subject (e.g. ``"F"`` or ``"Female"``).
    age: int or None
        The age of the subject, in years.
    sequences: list(Sequence)
        A list of Sequence instances.
    audios: list(Audio)
        A list of Audio instances.

    Note
    ----
    It is possible to define personalized attributes for subjects if more than one set of conditions is involved. To do
    so, see :meth:`Subject.add_attribute`.
    """

    def __init__(self, name=None, group=None, gender=None, age=None):
        self.name = name
        self.group = group
        self.gender = gender
        self.age = age
        self.sequences = []
        self.audios = []

    # == Setter functions ==

    def set_name(self, name):
        """Sets the attribute :attr:`Subject.name` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name or identifier of the subject.
        """
        self.name = name

    def set_group(self, group):
        """Sets the attribute :attr:`Subject.group` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        group: str
            The experimental group the subject belongs to.
        """
        self.group = group

    def set_gender(self, gender):
        """Sets the attribute :attr:`Subject.gender` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        gender: str
            The gender of the subject (e.g. ``"F"```or ``"Female"``).
        """
        self.gender = gender

    def set_age(self, age):
        """Sets the attribute :attr:`Subject.age` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        age: int or None
            The age of the subject, in years.
        """
        self.age = age

    def set_age_from_dob(self, day_birth, month_birth, year_birth, day_session=None, month_session=None,
                         year_session=None):
        """Sets the attribute :attr:`Subject.age` of the Subject instance, based on a date of birth and the date of the
        session. If no session date is provided, the current date is used to calculate the age of the subject. Dates
        must be provided in the gregorian calendar.

        .. versionadded:: 2.0

        Parameters
        ----------
        day_birth: int
            The day of birth of the subject, between 1 and 31.

        month_birth: int
            The month of birth of the subject, between 1 and 12.

        year_birth: int
            The year of birth of the subject.

        day_session: int or None
            The day of the session. If not provided, the current day will be used.

        month_session: int or None
            The month of the session. If not provided, the current month will be used.

        year_session: int or None
            The year of the session. If not provided, the current year will be used.
        """

        if year_session is None:
            year_session = datetime.datetime.now().date().year
        if month_session is None:
            month_session = datetime.datetime.now().date().month
        if day_session is None:
            day_session = datetime.datetime.now().date().day

        if datetime.datetime(year_birth, month_birth, day_birth) > datetime.datetime(year_session, month_session,
                                                                                     day_session):
            raise Exception("Unless you own a DeLorean, the subject cannot be born in the future.")
        else:
            if month_birth > month_session or (month_birth == month_session and day_birth > day_session):
                self.age = year_session - year_birth - 1
            else:
                self.age = year_session - year_birth

    # == Sequences ==

    def add_sequence(self, sequence):
        """Adds a Sequence instance to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence: Sequence
            A Sequence instance.
        """
        self.sequences.append(sequence)

    def add_sequences(self, *args):
        """Adds Sequence instances to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        *args: Sequence or list(Sequence)
            Sequence instances separated by a comma, or list of Sequence instances.
        """
        for element in args:
            if type(element) is list:
                for sequence in element:
                    self.sequences.append(sequence)
            else:
                self.sequences.append(element)

    def load_sequence(self, path, path_audio=None, name=None, condition=None, time_unit="auto",
                      start_timestamps_at_zero=False, verbosity=1):
        """Loads a sequence from a path, and adds it to the :attr:`Subject.sequences` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        path: str
            Absolute path to the motion sequence (starting from the root of the drive, e.g.
            ``C:/Users/Hiro/Documents/Recordings``). The path may point to a folder or a single file.
            For the acceptable file types, see :doc:`input`. If the path is ``None``, an empty sequence will be created.

        path_audio: str or None, optional
            Absolute path to an audio file corresponding to the sequence. The path should point to a .wav
            file. This path will be stored as an attribute of the Sequence object, and may be used automatically by
            functions using an audio file (typically, :py:meth:`Sequence.synchronize()` and
            :py:func:`sequence_reader()`). This parameter is however far from vital in the definition of a Sequence
            instance, and can be skipped safely.

        name: str or None, optional
            Defines a name for the Sequence instance. If a string is provided, the attribute :attr:`name` will take
            its value. If not, see :meth:`Sequence._define_name_init()`.

        condition: str or None, optional
            Optional field to represent in which experimental condition the sequence was recorded.

        time_unit: str or None, optional
            The unit of time of the timestamps in the original file. Depending on the value put as parameter, the
            timestamps will be converted to seconds.

                • If set on ``"auto"``, the function :meth:`Sequence._calculate_relative_timestamps()` will try to
                  automatically detect the unit of the timestamps based on the difference of time between the two first
                  frames, and will divide the timestamps by 10 000 000 (if it detects the timestamps to be in 100 ns),
                  by 1 000 (if the timestamps are in ms), or won't divide them (if the timestamps are already in s).
                • If set on ``"100ns"``, divides the timestamps from the file by 10 000 000. Typically, this is due to
                  the output timestamps from Kinect being in tenth of microsecond (C# system time).
                • If set on ``"ms"``, divides the timestamps from the file by 1 000.
                • If set on ``"s"``, the function will preserve the timestamps as they are in the file.

            The parameter also allows other units: ``"ns"``, ``"1ns"``, ``"10ns"``, ``"100ns"``, ``"µs"``, ``"1µs"``,
            ``"10µs"``, ``"100µs"``, ``"ms"``, ``"1ms"``, ``"10ms"``, ``"100ms"``, ``"s"``, ``"sec"``, ``"1s"``,
            ``"min"``, ``"mn"``, ``"h"``, ``"hr"``, ``"d"``, ``"day"``. See the documentation for the function
            :meth:`Sequence._calculate_relative_timestamps()`.

        start_timestamps_at_zero: bool, optional
            If set on ``True``, the timestamp of the first pose of the sequence will be
            set at 0, and the timestamps of the other poses will be reassigned to keep the same delay from the first
            pose. As such, the attributes timestamp and relative_timestamp from every pose will be equal.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.sequences.append(Sequence(path, path_audio, name, condition, time_unit, start_timestamps_at_zero,
                                       verbosity))
        if verbosity > 0:
            print("Sequence added to the subject " + str(self.name) + " with the index " + str(len(self.sequences) - 1))

    def get_sequences(self):
        """Returns the attribute :attr:`sequences` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        list(Sequence)
            A list of Sequence instances.
        """
        return self.sequences

    def get_sequence_from_index(self, sequence_index):
        """Returns the sequence instance matching the given index.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence_index: int
            The index of the sequence.

        Returns
        -------
        Sequence
            A Sequence instance corresponding to the provided index.
        """
        return self.sequences[sequence_index]

    def get_sequence_from_name(self, sequence_name):
        """Returns the first Sequence instance in :attr:`sequences` having the attribute :attr:`sequence.Sequence.name`
        matching the name provided as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence_name: str
            The name attribute of a Sequence instance.

        Returns
        -------
        Sequence
            A Sequence instance having the provided name as its attribute :attr:`sequence.Sequence.name`.
        """
        for sequence in self.sequences:
            if sequence.get_name() == sequence_name:
                return sequence

    def remove_sequence_from_index(self, sequence_index):
        """Removes a sequence from the Subject instance corresponding to the given index.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence_index: int
            The index of the sequence to remove.
        """
        del self.sequences[sequence_index]

    def remove_sequence_from_name(self, sequence_name):
        """Removes the first Sequence instance in :attr:`sequences` having the attribute :attr:`sequence.Sequence.name`
        matching the name provided as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence_name: str
            The name attribute of a Sequence instance.
        """
        for sequence in self.sequences:
            if sequence.get_name() == sequence_name:
                self.sequences.remove(sequence)
                break

    def get_sequences_from_condition(self, condition):
        """Returns a list of all the sequences that have an attribute :attr:`sequence.Sequence.condition` equal to
        the condition provided.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str
            An experimental condition.

        Returns
        -------
        list(Sequence)
            A list of Sequence instances.
        """
        selected_sequences = []
        for sequence in self.sequences:
            if sequence.get_condition() == condition:
                selected_sequences.append(sequence)
        return selected_sequences

    def get_sequences_from_attribute(self, attribute, value):
        """Returns a list of all the sequences that have a provided attribute equal to a provided value.

        .. versionadded:: 2.0

        Parameters
        ----------
        attribute: str
            The name of the Sequence attribute to compare to the value.
        value: any
            The value to match to each Sequence's provided attribute.
        """
        selected_sequences = []
        for sequence in self.sequences:
            if sequence.getattribute(attribute) == value:
                selected_sequences.append(sequence)
        return selected_sequences

    def get_number_of_sequences(self):
        """Returns the length of the :attr:`sequences` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The length of the :attr:`sequences` attribute.
        """
        return len(self.sequences)

    # == Audio ==
    def add_audio(self, audio):
        """Adds an Audio instance to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio: Audio
            An Audio instance.
        """
        self.audios.append(audio)

    def add_audios(self, *args):
        """Adds Audio instances to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        *args: Audio or list(Audio)
            Audio instances separated by a comma, or list of Audio instances.
        """
        for element in args:
            if type(element) is list:
                for audio in element:
                    self.audios.append(audio)
            else:
                self.audios.append(element)

    def load_audio(self, path_or_samples, frequency=None, name=None, verbosity=1):
        """Loads an audio clip from a path, and adds it to the :attr:`Subject.audios` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        path_or_samples: str or list(int)
            The path to the audio file, or a list containing the samples of an audio file. If the file is a path, it
            should either point to a `.wav` file, or to a file containing the timestamps and samples in a text form
            (`.json`, `.csv`, `.tsv`, `.txt` or `.mat`). It is also possible to point to a folder containing one file
            per sample. See :ref:`Audio formats <wav_example>` for the acceptable file types.

        frequency: int or float, optional
            The frequency, in Hz (or samples per sec) at which the parameter `path_or_samples` is set. This parameter
            will be ignored if ``path_or_samples`` is a path, but will be used to define the :attr:`timestamps` of the
            Audio object if ``path_or_samples`` is a list of samples.

        name: str, optional
            Defines a name for the Audio instance. If a string is provided, the attribute :attr:`name` will take
            its value. If not, see :meth:`Audio._define_name_init()`.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.audios.append(Audio(path_or_samples, frequency, name, verbosity))
        if verbosity > 0:
            print("Audio added to the subject " + str(self.name) + " with the index " + str(len(self.audios) - 1))

    def get_audios(self):
        """Returns the attribute :attr:`audios` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        list(Audio)
            A list of Audio instances.
        """
        return self.audios

    def get_audio_from_index(self, audio_index):
        """Returns the Audio instance matching the given index.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio_index : int
            The index of the audio clip.

        Returns
        -------
        Audio
            An Audio instance corresponding to the provided index.
        """
        return self.audios[audio_index]

    def get_audio_from_name(self, audio_name):
        """Returns the first Audio instance in :attr:`audios` having the attribute :attr:`audio.Audio.name` matching
        the name provided as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio_name: str
            The name attribute of an Audio instance.

        Returns
        -------
        Audio
            An Audio instance having the provided name as its attribute :attr:`audio.Audio.name`.
        """
        for audio in self.audios:
            if audio.get_name() == audio_name:
                return audio

    def remove_audio_from_index(self, audio_index):
        """Removes an Audio instance from the Subject instance corresponding to the given index.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio_index: int
            The index of the Audio instance to remove.
        """
        del self.sequences[audio_index]

    def remove_audio_from_name(self, audio_name):
        """Removes the first Audio instance in :attr:`audios having the attribute :attr:`audio.Audio.name` matching the
        name provided as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio_name: str
            The name attribute of an Audio instance.
        """
        for audio in self.audios:
            if audio.get_name() == audio_name:
                self.audios.remove(audio)
                break

    def remove_all_audios(self):
        """Clears the :attr:`Subject.audios` attribute.

        .. versionadded:: 2.0
        """
        self.audios = []

    def get_audios_from_condition(self, condition):
        """Returns a list of all the Audio instances that have an attribute :attr:`audio.Audio.condition` equal to
        the condition provided.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str
            An experimental condition.

        Returns
        -------
        list(Sequence)
            A list of Sequence instances.
        """
        selected_audios = []
        for audio in self.audios:
            if audio.get_condition() == condition:
                selected_audios.append(audio)
        return selected_audios

    def get_audios_from_attribute(self, attribute, value):
        """Returns a list of all the Audio instances that have a provided attribute equal to a provided value.

        .. versionadded:: 2.0

        Parameters
        ----------
        attribute: str
            The name of the Audio attribute to compare to the value.
        value: any
            The value to match to each Audio instance's provided attribute.
        """
        selected_audios = []
        for audio in self.audios:
            if audio.getattribute(attribute) == value:
                selected_audios.append(audio)
        return selected_audios

    def get_number_of_audios(self):
        """Returns the length of the :attr:`audios` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The length of the :attr:`audios` attribute.
        """
        return len(self.audios)

    # == Getter functions ==

    def get_name(self):
        """Returns the attribute :attr:`name` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The name or identifier of the subject.
        """
        return self.name

    def get_group(self):
        """Returns the attribute :attr:`group` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The experimental group the subject belongs to.
        """
        return self.group

    def get_gender(self):
        """Returns the attribute :attr:`gender` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The gender of the subject (e.g. ``"F"```or ``"Female"``).
        """
        return self.gender

    def get_age(self):
        """Returns the attribute :attr:`age` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The age of the subject, in years.
        """
        return self.age

    def get_subject_height(self, verbosity=1):
        """Returns an estimation of the height of the subject, in meters, based on the successive distances between a
        series of joints. The height is calculated across all poses for each Sequence
        (see :meth:`sequence.Sequence.get_subject_height`), and the resulting heights are averaged across all sequences.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        float
            The estimated height of the subject, in meters.
        """
        heights = []
        for sequence in self.sequences:
            heights.append(sequence.get_subject_height(verbosity))

        return sum(heights)/len(heights)

    def get_subject_arm_length(self, side="left", verbosity=1):
        """Returns an estimation of the length of the left or right arm of the subject, in meters. The length of the arm
        is calculated across all poses for each Sequence (see :meth:`sequence.Sequence.get_subject_arm_length`.

        .. versionadded:: 2.0

        Parameters
        ----------
        side: str
            The side of the arm you want to measure, either ``"left"`` or ``"right"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        float
            The estimated arm length of the subject, in meters.
        """
        arm_lengths = []
        for sequence in self.sequences:
            arm_lengths.append(sequence.get_subject_arm_length(side, verbosity))

        return sum(arm_lengths) / len(arm_lengths)

    def get_recording_session_duration(self):
        """Returns an estimation of the duration of the recording session by calculating the time between the recording
        date of the sequence with the earliest recording date, and the recording date plus duration of the sequence
        with the latest recording date.

        .. versionadded:: 2.0

        Returns
        -------
        datetime.timedelta
            The duration between the beginning of the first and the end of the last sequence.
        """
        sequences_in_order = order_sequences_by_date(self.sequences)
        duration = sequences_in_order[-1].get_date_recording() - sequences_in_order[0].get_date_recording()
        duration += datetime.timedelta(seconds=sequences_in_order[-1].get_duration())
        return duration

    def get_average_velocity_single_joint(self, joint_label):
        """Returns the average velocity of a specific joint for the subject, across all sequences.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        -------
        float
            The average velocity of the joint, in meters per second.
        """
        distance = 0
        duration = 0

        for sequence in self.sequences:
            distance += sequence.get_total_distance_single_joint(joint_label)
            duration += sequence.get_duration()

        return distance / duration

    def get_average_velocities(self):
        """Returns a dictionary containing the average velocity for each joint, across all sequences of the subject.

        .. versionadded:: 2.0

        Returns
        -------
        dict(str: float)
            A dictionary with the joint labels as keys, and their average velocity as values.
        """
        joint_labels = self.sequences[0].get_joint_labels()
        average_velocities = {}

        for joint_label in joint_labels:
            average_velocities[joint_label] = self.get_average_velocity_single_joint(joint_label)

    def print_sequences_details(self, include_name=True, include_condition=True, include_date_recording=True,
                                include_number_of_poses=True, include_duration=True):
        """Prints details on each Sequence instance, one Sequence per line.

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
        header = "Subject " + str(self.name) + ": " + str(self.get_number_of_sequences()) + " sequences · "
        header += "Group: " + str(self.group) + " · Gender: " + str(self.gender) + " · Age: " + str(self.age)
        print(header)
        print("-" * len(header))
        for seq in range(len(self.sequences)):
            print("\tSequence #" + str(seq+1).zfill(int(math.log10(len(self.sequences)))) + " |", end=" ")
            self.sequences[seq].print_details(include_name, include_condition, include_date_recording,
                                              include_number_of_poses, include_duration)
            if seq < len(self.audios):
                print("\tAudio #" + str(seq+1).zfill(int(math.log10(len(self.sequences)))) + " |", end=" ")
                self.audios[seq].print_details(include_name, include_condition, include_number_of_poses,
                                               include_duration)
