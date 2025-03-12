"""Default class defining a subject, that can contain trials, each of which can contain a sequence and an audio clips.
This class can be used in the stats functions to calculate variances across participants."""
from __future__ import annotations

import datetime
from collections import OrderedDict

from krajjat.classes.audio import Audio
from krajjat.classes.sequence import Sequence
from krajjat.classes.trial import Trial
from krajjat.tool_functions import sort_sequences_by_date


class Subject(object):
    """Creates an instance from the class Subject, and returns a Subject object, which matches one individual that
    performed one or multiple recordings. Upon creation, a Subject instance contains no Trial instances. They can
    be directly added with the method :meth:`Subject.add_trial`.

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
    name: str
        The name or identifier of the subject.
    group: str, int or None
        The experimental group the subject belongs to.
    gender: str or None
        The gender of the subject (e.g. ``"F"`` or ``"Female"``).
    age: int or None
        The age of the subject, in years.
    trials: OrderedDict(str or int: Trial)
        An ordered dictionary of Trial instances.

    Note
    ----
    It is possible to define personalized attributes for subjects if more than one set of conditions is involved. To do
    so, see :meth:`Subject.set_trial_attribute`.
    """

    def __init__(self, name: str, group: str | int = None, gender: str = None, age: int = None):
        self.name = name
        self.group = group
        self.gender = gender
        self.age = age
        self.trials = OrderedDict()

    # == Getter/Setter functions =======================================================================================

    def get_name(self):
        """Returns the attribute :attr:`name` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The name or identifier of the subject.
        """
        return self.name

    def set_name(self, name):
        """Sets the attribute :attr:`Subject.name` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name or identifier of the subject.
        """
        assert isinstance(name, str)
        self.name = name

    def get_group(self):
        """Returns the attribute :attr:`group` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The experimental group the subject belongs to.
        """
        return self.group

    def set_group(self, group):
        """Sets the attribute :attr:`Subject.group` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        group: str
            The experimental group the subject belongs to.
        """
        assert isinstance(group, (str, int))
        self.group = group

    def get_gender(self):
        """Returns the attribute :attr:`gender` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The gender of the subject (e.g. ``"F"```or ``"Female"``).
        """
        return self.gender

    def set_gender(self, gender):
        """Sets the attribute :attr:`Subject.gender` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        gender: str
            The gender of the subject (e.g. ``"F"```or ``"Female"``).
        """
        self.gender = gender

    def get_age(self):
        """Returns the attribute :attr:`age` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The age of the subject, in years.
        """
        return self.age

    def set_age(self, age):
        """Sets the attribute :attr:`Subject.age` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        age: int or None
            The age of the subject, in years.
        """
        self.age = age

    # == Special getters ===============================================================================================

    def get_trials(self, trial_ids=None, condition=None, **kwargs):
        """Returns a dictionary containing the trials, where each key is the trial ID and each value is a Trial
        instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        trial_ids: list(str) or None, optional
            Defines a list of trial IDs to gather specifically; if set, the returned dictionary will only contain
            the trials matching the given IDs. The function will return an error if an ID does not match any ID
            present in the subject.
        condition: str or int, optional
            If set, the function will return the trials that have an attribute :attr:`Trial.condition` matching the
            given value. This parameter can be used in conjunction with `trial_ids` to select only the trials in the
            list that also match the given condition.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Trial instances.

        Returns
        -------
        List(Trial)
            A list of Trial instances.
        """
        if trial_ids is str:
            trial_ids = [trial_ids]

        trials = []

        for trial_id in self.trials.keys():
            add_trial = True

            if trial_ids is not None and trial_id not in trial_ids:
                add_trial = False

            if condition is not None and self.trials[trial_id].condition != condition:
                add_trial = False

            for arg in kwargs.keys():
                if getattr(self.trials[trial_id], arg) != kwargs[arg]:
                    add_trial = False

            if add_trial:
                trials.append(self.trials[trial_id])

        return trials

    def get_trials_id(self):
        """Returns a list of the trial IDs, in the order the trials were added to the subject.

        .. versionadded:: 2.0

        Returns
        -------
        list(str or int)
        """
        return self.trials.keys()

    def get_sequences(self, trial_ids=None, condition=None, **kwargs):
        """Returns a list containing the sequences of the Trial instances of the subject.

        Parameters
        ----------
        trial_ids: list(str) or None, optional
            Defines a list of trial IDs to gather specifically; if set, the returned list will only contain
            the sequences included in the trials matching the given IDs. The function will return an error if an ID does
            not match any ID present in the subject.
        condition: str or int, optional
            If set, the function will return the sequences included in the trials having an attribute
            :attr:`Trial.condition` matching the given value. This parameter can be used in conjunction with
            `trial_ids` to select only the trials in the list that also match the given condition.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Trial instances.

        Note
        ----
        As the trials are in an OrderedDict, the returned sequences will be sorted in the order the trials were added.
        If some trials do not contain sequences, the corresponding list entries will be `None`.

        .. versionadded:: 2.0

        Returns
        -------
        list(Sequence)
            A list of Sequence instances.
        """
        trials = self.get_trials(trial_ids, condition, **kwargs)

        sequences = []
        for trial_id in trials.keys():
            sequences.append(trials[trial_id].get_sequence())
        return sequences

    def get_audios(self, trial_ids=None, condition=None, **kwargs):
        """Returns a list containing the audios of the Trial instances of the subject.

        Parameters
        ----------
        trial_ids: list(str) or None, optional
            Defines a list of trial IDs to gather specifically; if set, the returned list will only contain
            the audios included in the trials matching the given IDs. The function will return an error if an ID does
            not match any ID present in the subject.
        condition: str or int, optional
            If set, the function will return the audios included in the trials having an attribute
            :attr:`Trial.condition` matching the given value. This parameter can be used in conjunction with
            `trial_ids` to select only the trials in the list that also match the given condition.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Trial instances.

        Note
        ----
        As the trials are in an OrderedDict, the returned audios will be sorted in the order the trials were added.
        If some trials do not contain audios, the corresponding list entries will be `None`.

        .. versionadded:: 2.0

        Returns
        -------
        list(Audio)
            A list of Audio instances.
        """
        trials = self.get_trials(trial_ids, condition, **kwargs)

        audios = []
        for trial_id in trials.keys():
            audios.append(trials[trial_id].get_sequence())
        return audios

    def get_sequence(self, trial_id):
        """Returns the sequence matching the given trial ID.

        .. versionadded:: 2.0

        Returns
        -------
        Sequence
            A Sequence instance included in the Trial instance matching the given trial ID.
        """
        return self.trials[trial_id].get_sequence()

    def get_audio(self, trial_id):
        """Returns the audio matching the given trial ID.

        .. versionadded:: 2.0

        Returns
        -------
        Audio
            An Audio instance included in the Trial instance matching the given trial ID.
        """
        return self.trials[trial_id].get_audio()

    def get_number_of_trials(self):
        """Returns the number of Trial elements present in the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of Trial elements in the Subject instance.
        """
        return len(self.trials)

    def get_number_of_trials_condition(self, condition):
        """Returns the number of Trial elements that have an attribute :attr:`Trial.condition` equal to the value set
        as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: int or str
            A condition value.

        Returns
        -------
        int
            The amount of trials having their attribute :attr:`Trial.condition` equal to the value set as parameter.
        """
        number_of_trials = 0

        for trial_id in self.trials.keys():
            if self.trials[trial_id].condition == condition:
                number_of_trials += 1

        return number_of_trials

    def get_number_of_trials_attribute(self, attribute, value):
        """Returns the number of Trial elements that have a customized attribute equal to the value set as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        attribute: str
            The name of an attribute shared by all trials of the Subject instance.
        value: any
            The value to count for this attribute.

        Returns
        -------
        int
            The amount of trials having their attribute `attribute` equal to the value set as parameter.
        """
        number_of_trials = 0

        for trial_id in self.trials.keys():
            if getattr(self.trials[trial_id], attribute) == value:
                number_of_trials += 1

        return number_of_trials

    def get_subject_height(self, verbosity=1):
        """Returns an estimation of the height of the subject, in meters, based on the successive distances between a
        series of joints. The height is calculated across all poses for each Sequence present in each Trial
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
        for trial_id in self.trials.keys():
            if self.trials[trial_id].has_sequence():
                heights.append(self.trials[trial_id].get_sequence().get_subject_height(verbosity))

        return sum(heights)/len(heights)

    def get_subject_arm_length(self, side="left", verbosity=1):
        """Returns an estimation of the length of the left or right arm of the subject, in meters. The length of the arm
        is calculated across all poses for each Sequence present in each Trial
        (see :meth:`sequence.Sequence.get_subject_arm_length`).

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
        for trial_id in self.trials.keys():
            if self.trials[trial_id].has_sequence():
                arm_lengths.append(self.trials[trial_id].get_sequence().get_subject_arm_length(side, verbosity))

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
        sequences = self.get_sequences()
        sequences_in_order = sort_sequences_by_date(*sequences)
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

        for sequence in self.get_sequences():
            distance += sequence.get_total_velocity_single_joint(joint_label)
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
        joint_labels = self.get_sequences()[0].get_joint_labels()
        average_velocities = {}

        for joint_label in joint_labels:
            average_velocities[joint_label] = self.get_average_velocity_single_joint(joint_label)

        return average_velocities

    def get_joint_labels(self):
        """Returns a list of all the unique joint labels contained in the trials sequences.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of joint labels.
        """
        joint_labels = []

        for trial_id in self.trials.keys():
            if self.trials[trial_id].has_sequence():
                for joint_label in self.trials[trial_id].sequence.get_joint_labels():
                    if joint_label not in joint_labels:
                        joint_labels.append(joint_label)

        return joint_labels

    # == Special setter ================================================================================================

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
                self._age = year_session - year_birth - 1
            else:
                self._age = year_session - year_birth

    # == Adding functions ==============================================================================================

    def add_trial(self, trial_id=None, condition=None, sequence=None, audio=None, **kwargs):
        """Adds a Trial instance to the current subject. If a trial with the given ID already exists, the function
        returns an exception, to avoid to rewrite an existing trial.

        .. versionadded:: 2.0

        Parameters
        ----------
        trial_id: str, int, or None, optional
            The identifier for the trial, which can be a string, an integer or None. If set on `None`, the
            initialisation function will try to set the trial ID on the name on the name of the Sequence instance or the
            name of the Audio instance, in that order. If no sequence nor audio attribute are set, the function will
            return an Exception, as a trial must have an ID.
        condition: str, int or None, optional
            The condition for the Trial instance.
        sequence: Sequence or None, optional
            The motion sequence from this trial.
        audio: Audio or None, optional
            The audio clip from this trial.

        Note
        ----
        The function allows for keyword arguments; all the arguments that are passed will be defined as attributes
        for the added trial.
        """
        if trial_id is not None:
            pass
        elif sequence is not None and sequence.name is not None:
            trial_id = sequence.name
        elif audio is not None and audio.name is not None:
            trial_id = audio.name
        else:
            raise Exception(f"Please specify an ID for the trial.")

        trial = Trial(trial_id, condition, sequence, audio)

        for keyword in kwargs.keys():
            setattr(trial, keyword, kwargs[keyword])

        if trial.trial_id in self.trials.keys():
            raise Exception(f"A trial with this ID {trial.trial_id} already exists for subject {self.name}.")
        else:
            self.trials[trial.trial_id] = trial

    def add_attribute(self, name, value):
        """Adds an attribute to the Trial instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name of the attribute.
        value: any
            The value of the attribute.
        """
        setattr(self, name, value)

    def add_sequence(self, sequence, trial_id=None, condition=None):
        """Adds a Sequence instance to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence: Sequence
            A Sequence instance.
        trial_id: str, int or None, optional
            The identifier for the trial, which can be a string, an integer or None. If set on `None`, the
            initialisation function will try to set the trial ID on the name on the name of the Sequence instance. If no
            sequence nor audio attribute are set, the function will return an Exception, as a trial must have an ID.
        condition: str, int or None, optional
            The condition for the Trial instance.
        """
        if trial_id in self.trials.keys():
            self.trials[trial_id].sequence = sequence
        else:
            self.add_trial(trial_id, condition, sequence)

    def add_audio(self, audio, trial_id=None, condition=None):
        """Adds an Audio instance to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio: Audio
            An Audio instance.
        condition: str, int or None, optional
            The condition for the Trial instance.
        trial_id: str, int or None
            The identifier for the trial, which can be a string, an integer or None. If set on `None`, the
            initialisation function will try to set the trial ID on the name on the name of the Audio instance. If no
            sequence nor audio attribute are set, the function will return an Exception, as a trial must have an ID.
        """
        if trial_id in self.trials.keys():
            self.trials[trial_id].audio = audio
        else:
            self.add_trial(trial_id, condition, audio=audio)

    # == Checking functions ============================================================================================

    def has_sequence_in_each_trial(self):
        """Returns `True` if each Trial element present in the Subject instance has a Sequence as an attribute,
        `False` otherwise.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            `True` if each Trial has a Sequence instance, `False` otherwise.
        """
        for trial_id in self.trials.keys():
            if not self.trials[trial_id].has_sequence():
                return False
        return True

    def has_audio_in_each_trial(self):
        """Returns `True` if each Trial element present in the Subject instance has an Audio as an attribute,
        `False` otherwise.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            `True` if each Trial has an Audio instance, `False` otherwise.
        """
        for trial_id in self.trials.keys():
            if not self.trials[trial_id].has_audio():
                return False
        return True

    # == Print function ================================================================================================

    def print_sequences_details(self, include_trials=False, include_name=True, include_condition=True,
                                include_date_recording=True, include_number_of_poses=True, include_duration=True,
                                add_tabs=0):
        """Prints details on each Sequence instance, one Sequence per line.

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

        header = f"Subject {self.name}: {self.get_number_of_trials()} trials · Group: {self.group} · Gender: " + \
                 f"{self.gender} · Age: {self.age}"
        print(t + header)
        print(t + "-" * len(header))

        if include_trials:
            for trial_id in self.trials.keys():
                trial = self.trials[trial_id]
                print(t + f"\tTrial {trial_id} · Condition {trial.condition}")
                if self.trials[trial_id].has_sequence():
                    trial.sequence.print_details(include_name, include_condition, include_date_recording,
                                                 include_number_of_poses, include_duration, add_tabs + 1)
                else:
                    print(t + "\t\tNo sequence in this trial.")
                if self.trials[trial_id].has_audio():
                    trial.audio.print_details(include_name, include_condition, include_number_of_poses,
                                              include_duration, add_tabs + 1)
                else:
                    print(t + "\t\tNo audio in this trial.")

    def __len__(self):
        return len(self.trials)
