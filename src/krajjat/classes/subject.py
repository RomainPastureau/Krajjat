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

    Example
    -------
    >>> subject = Subject("Trisha", 30, "F", "Control")
    >>> trial1 = Trial("R001", sequence=Sequence("Trisha/sequence_01.csv"), audio=Audio("Trisha/audio_01.wav"))
    >>> trial2 = Trial("R002", sequence=Sequence("Trisha/sequence_02.csv"), audio=Audio("Trisha/audio_02.wav"))
    >>> trial3 = Trial("R003", sequence=Sequence("Trisha/sequence_03.csv"), audio=Audio("Trisha/audio_03.wav"))
    >>> subject.add_trials(trial1, trial2, trial3)
    """

    def __init__(self, name: str = None, group: str | int = None, gender: str = None, age: int = None):
        self.name = name
        self.group = group
        self.gender = gender
        self.age = age
        self.trials = OrderedDict()

    # == Getter/Setter functions =======================================================================================

    def set_name(self, name):
        """Sets the attribute :attr:`Subject.name` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name or identifier of the subject.

        Example
        -------
        >>> subject = Subject("Nicola")
        >>> subject.set_name("Mikel")
        """
        assert isinstance(name, str)
        self.name = name

    def set_group(self, group):
        """Sets the attribute :attr:`Subject.group` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        group: str
            The experimental group the subject belongs to.

        Example
        -------
        >>> subject = Subject("Manolo")
        >>> subject.set_group("Control")
        """
        assert isinstance(group, (str, int))
        self.group = group

    def set_gender(self, gender):
        """Sets the attribute :attr:`Subject.gender` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        gender: str
            The gender of the subject (e.g. ``"F"```or ``"Female"``).

        Example
        -------
        >>> subject = Subject("Manuela")
        >>> subject.set_gender("F")
        """
        self.gender = gender

    def set_age(self, age):
        """Sets the attribute :attr:`Subject.age` of the Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        age: int or None
            The age of the subject, in years.

        Example
        -------
        >>> subject = Subject("Marta")
        >>> subject.set_age(7)
        """
        self.age = age

    def set_age_from_dob(self, birth_date, session_date=None):
        """Sets the attribute :attr:`Subject.age` of the Subject instance, based on a date of birth and the date of the
        session. If no session date is provided, the current date is used to calculate the age of the subject. Dates
        must be provided in the gregorian calendar.

        .. versionadded:: 2.0

        Parameters
        ----------
        birth_date: str|tuple|datetime
            The date of birth of the subject. This parameter can be a string in the format ``DD/MM/YYYY`` or
            ``YYYY-MM-DD``, a tuple of three integers (``YYYY``, ``MM``, ``DD``), or a datetime object.

        session_date: str|tuple|datetime|None, optional
            The date of the recording session. If not provided, the current date is used. This parameter can be a string
            in the format ``DD/MM/YYYY`` or ``YYYY-MM-DD``, a tuple of three integers (``YYYY``, ``MM``, ``DD``), or a
            datetime object.

        Example
        -------
        >>> subject = Subject("Vincenzo")
        >>> subject.set_age_from_dob("01/01/1995")
        >>> subject.set_age_from_dob(("1995", "01", "01"), "2025-01-01")
        >>> subject.set_age_from_dob(datetime.datetime(1995, 1, 1))
        """

        if type(birth_date) is str:
            if "/" in birth_date:
                birth_date = datetime.datetime.strptime(birth_date, '%d/%m/%Y').date()
            else:
                birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
        elif type(birth_date) is tuple:
            birth_date = datetime.date(birth_date[0], birth_date[1], birth_date[2])
        elif not type(birth_date) is datetime.datetime:
            raise TypeError("The date of birth must be provided as a string, a tuple or a datetime object.")

        if type(session_date) is str:
            if "/" in session_date:
                session_date = datetime.datetime.strptime(session_date, '%d/%m/%Y').date()
            else:
                session_date = datetime.datetime.strptime(session_date, '%Y-%m-%d').date()
        elif type(session_date) is tuple:
            session_date = datetime.date(session_date[0], session_date[1], session_date[2])
        elif session_date is None:
            session_date = datetime.date.today()
        elif not type(session_date) is datetime.datetime:
            raise TypeError("The date of birth must be provided as a string, a tuple or a datetime object.")

        if session_date < birth_date:
            raise Exception("Unless you own a DeLorean, the subject cannot be born in the future.")
        else:
            self.age = int((session_date - birth_date).days / 365.2425)

    def get_name(self):
        """Returns the attribute :attr:`name` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The name or identifier of the subject.

        Example
        -------
        >>> subject = Subject("José")
        >>> subject.get_name()
        José
        """
        return self.name

    def get_group(self):
        """Returns the attribute :attr:`group` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The experimental group the subject belongs to.

        Example
        -------
        >>> subject = Subject("Giada", "Control")
        >>> subject.get_group()
        Control
        """
        return self.group

    def get_gender(self):
        """Returns the attribute :attr:`gender` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The gender of the subject (e.g. ``"F"```or ``"Female"``).

        Example
        -------
        >>> subject = Subject("Noemi", "Experimental", "F")
        >>> subject.get_gender()
        F
        """
        return self.gender

    def get_age(self):
        """Returns the attribute :attr:`age` of the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The age of the subject, in years.

        Example
        -------
        >>> subject = Subject("Hadeel", "Group A", "F", 20)
        >>> subject.get_age()
        20
        """
        return self.age

    def get_joint_labels(self):
        """Returns a list of all the unique joint labels contained in the trials sequences.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            A list of joint labels.

        Example
        -------
        >>> subject = Subject("David")
        >>> subject.add_trial(Trial(1, sequence=Sequence("David/sequence_01.tsv"))  # Contains Head
        >>> subject.add_trial(Trial(2, sequence=Sequence("David/sequence_02.tsv"))  # Contains HandRight and HandLeft
        >>> subject.get_joint_labels()
        ["Head", "HandRight", "HandLeft"]
        """
        joint_labels = []

        for trial_id in self.trials.keys():
            if self.trials[trial_id].has_sequence():
                for joint_label in self.trials[trial_id].sequence.get_joint_labels():
                    if joint_label not in joint_labels:
                        joint_labels.append(joint_label)

        return joint_labels

    def get_trial(self, trial_id):
        """Returns a Trial instance from the subject that matches the specified trial ID, if it exists.

        .. versionadded:: 2.0

        Parameters
        ----------
        trial_id: str|int
            The ID of the trial to retrieve.

        Returns
        -------
        Trial
            The corresponding Trial, if it exists.

        Example
        -------
        >>> subject = Subject("Li-Chuan")
        >>> subject.add_trial(Trial("R001", sequence=Sequence("Li-Chuan/sequence_01.tsv"))
        >>> subject.get_trial("R001")
        """
        return self.trials[trial_id]

    def get_trials(self, trial_ids=None, condition=None, return_type="dict", **kwargs):
        """Returns a dictionary or a list containing all or a subset of the subject's trials.

        .. versionadded:: 2.0

        Parameters
        ----------
        trial_ids: list(str|int)|str|int|None, optional
            Defines a list of trial IDs to gather specifically; if set, the returned dictionary will only contain
            the trials matching the given IDs. The function will return an error if an ID does not match any ID
            present in the subject.
        condition: str or int, optional
            If set, the function will return the trials that have an attribute :attr:`Trial.condition` matching the
            given value. This parameter can be used in conjunction with `trial_ids` to select only the trials in the
            list that also match the given condition.
        return_type: str, optional
            Defines if to return the trials as a dictionary or a list. The default value is ``"dict"``, which returns
            the trials as a dictionary with the trial IDs as keys. If set to ``"list"``, the function will return a
            list containing the trials in the same order as their IDs passed as parameter.

        Note
        ----
        The function also allows for other arguments, as long as each argument is a custom attribute set to the
        Trial instances.

        Returns
        -------
        Dict(Trial)|List(Trial)
            A dictionary or a list of Trial instances.

        Example
        -------
        >>> subject = Subject("Ana")
        >>> trial1 = Trial("R001", sequence=Sequence("Ana/sequence_01.tsv"), condition="Spanish")
        >>> trial2 = Trial("R002", sequence=Sequence("Ana/sequence_02.tsv"), condition="English")
        >>> trial3 = Trial("R003", sequence=Sequence("Ana/sequence_03.tsv"), condition="English")
        >>> subject.add_trials(trial1, trial2, trial3)
        >>> subject.get_trials()  # Returns all the trials
        >>> subject.get_trials(condition="English")  # Returns all the trials with condition "English" (2 and 3)
        >>> subject.get_trials(trial_ids=["R001", "R002"])  # Returns the trials with IDs "R001" and "R002"
        """
        if type(trial_ids) in [str, int]:
            trial_ids = [trial_ids]

        trials = []

        if trial_ids is None:
            trial_ids = self.trials.keys()

        for trial_id in trial_ids:
            add_trial = True

            if condition is not None and self.trials[trial_id].condition != condition:
                add_trial = False

            for arg in kwargs.keys():
                if getattr(self.trials[trial_id], arg) != kwargs[arg]:
                    add_trial = False

            if add_trial:
                trials.append(self.trials[trial_id])

        if return_type == "list":
            return trials
        else:
            return {trial.get_trial_id(): trial for trial in trials}

    def get_trials_id(self, condition=None, **kwargs):
        """Returns a list of the trial IDs, in the order the trials were added to the subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str|None, optional
            If specified, returns the IDs of the trials matching the given condition.
        **kwargs: any, optional
            If specified, returns the IDs of the trials matching the given attributes.

        Returns
        -------
        list(str|int)
            A list of the trial IDs.

        Example
        -------
        >>> subject = Subject("Sandra")
        >>> trial1 = Trial("R001", sequence=Sequence("Sandra/sequence_01.tsv"))
        >>> trial2 = Trial("R002", sequence=Sequence("Sandra/sequence_02.tsv"))
        >>> trial3 = Trial("R003", sequence=Sequence("Sandra/sequence_03.tsv"))
        >>> subject.add_trials(trial1, trial2, trial3)
        >>> subject.get_trials_id()
        ["R001", "R002", "R003"]
        """
        return list(self.get_trials(None, condition, "dict", **kwargs).keys())

    def get_number_of_trials(self, condition=None, **kwargs):
        """Returns the total amount of Trial elements present in the Subject instance, or the amount of Trial elements
        matching the condition or other attributes.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str|None, optional
            If specified, returns the amount of trials matching the given condition.
        **kwargs: any, optional
            If specified, returns the amount of trials matching the given attributes.

        Returns
        -------
        int
            The number of Trial elements matching the given attributes in the Subject instance.

        Example
        -------
        >>> subject = Subject("Tiger")
        >>> trial1 = Trial("R001", sequence=Sequence("Tiger/sequence_01.tsv"))
        >>> trial2 = Trial("R002", sequence=Sequence("Tiger/sequence_02.tsv"))
        >>> trial3 = Trial("R003", sequence=Sequence("Tiger/sequence_03.tsv"))
        >>> subject.add_trials(trial1, trial2, trial3)
        >>> subject.get_number_of_trials()
        3
        """
        trials = self.get_trials(None, condition, "list", **kwargs)
        return len(trials)

    def get_sequence(self, trial_id):
        """Returns the sequence matching the given trial ID.

        .. versionadded:: 2.0

        Returns
        -------
        Sequence
            A Sequence instance included in the Trial instance matching the given trial ID.

        Example
        -------
        >>> subject = Subject("Catherine")
        >>> trial = Trial("R001", sequence=Sequence("Catherine/sequence_01.tsv"))
        >>> subject.add_trial(trial)
        >>> sequence = subject.get_sequence("R001")
        """
        return self.trials[trial_id].get_sequence()

    def get_sequences(self, trial_ids=None, condition=None, return_type="dict", **kwargs):
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
        return_type: str, optional
            Defines if to return the sequences as a dictionary or a list. The default value is ``"dict"``, which returns
            the sequences as a dictionary with the trial IDs as keys. If set to ``"list"``, the function will return a
            list containing the sequences in the same order as their trial IDs passed as parameter.

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
        dict(Sequence)|list(Sequence)
            A dictionary or a list of Sequence instances.

        Examples
        --------
        >>> subject = Subject("Irene")
        >>> trial1 = Trial("R001", sequence=Sequence("Irene/sequence_01.tsv", condition="English"))
        >>> trial1.session = 1
        >>> trial2 = Trial("R002", sequence=Sequence("Irene/sequence_02.tsv", condition="Spanish"))
        >>> trial2.session = 1
        >>> trial3 = Trial("R003", sequence=Sequence("Irene/sequence_03.tsv", condition="Spanish"))
        >>> trial3.session = 2
        >>> subject.add_trials(trial1, trial2, trial3)
        >>> sequences = subject.get_sequences(["ROO1", "R003"])
        >>> sequences = subject.get_sequences(condition="Spanish", return_type="list")  # Returns R002 and R003
        >>> sequences = subject.get_sequences(session=1)  # Returns R001 and R002
        """

        trials = self.get_trials(trial_ids, condition, return_type, **kwargs)
        if return_type == "list":
            return [trial.get_sequence() for trial in trials]
        else:
            return {trials[trial].get_trial_id(): trials[trial].get_sequence() for trial in trials}

    def get_audio(self, trial_id):
        """Returns the audio matching the given trial ID.

        .. versionadded:: 2.0

        Returns
        -------
        Audio
            An Audio instance included in the Trial instance matching the given trial ID.

        Examples
        --------
        >>> subject = Subject("Maialen")
        >>> trial1 = Trial("R001", audio=Audio("Maialen/recording_01.wav", condition="English"))
        >>> subject.add_trial(trial1)
        >>> audio = subject.get_audio("ROO1")
        """
        return self.trials[trial_id].get_audio()

    def get_audios(self, trial_ids=None, condition=None, return_type="dict", **kwargs):
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
        return_type: str, optional
            Defines if to return the audios as a dictionary or a list. The default value is ``"dict"``, which returns
            the audios as a dictionary with the trial IDs as keys. If set to ``"list"``, the function will return a
            list containing the audios in the same order as their trial IDs passed as parameter.

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
        list(Audio|AudioDerivative)
            A list of Audio instances.

        Examples
        --------
        >>> subject = Subject("Clara")
        >>> trial1 = Trial("R001", audio=Audio("Clara/recording_01.wav", condition="English"))
        >>> trial1.session = 1
        >>> trial2 = Trial("R002", audio=Audio("Clara/recording_02.wav", condition="Spanish"))
        >>> trial2.session = 1
        >>> trial3 = Trial("R003", audio=Audio("Clara/recording_03.wav", condition="Spanish"))
        >>> trial3.session = 2
        >>> subject.add_trials(trial1, trial2, trial3)
        >>> audios = subject.get_audios(["ROO1", "R003"])
        >>> audios = subject.get_audios(condition="Spanish", return_type="list")  # Returns R002 and R003
        >>> audios = subject.get_audios(session=1)  # Returns R001 and R002
        """
        trials = self.get_trials(trial_ids, condition, return_type, **kwargs)
        if return_type == "list":
            return [trial.get_audio() for trial in trials]
        else:
            return {trials[trial].get_trial_id(): trials[trial].get_audio() for trial in trials}

    def get_recording_session_duration(self):
        """Returns an estimation of the duration of the recording session by calculating the time between the recording
        date of the sequence with the earliest recording date, and the recording date plus duration of the sequence
        with the latest recording date.

        .. versionadded:: 2.0

        Returns
        -------
        datetime.timedelta
            The duration between the beginning of the first and the end of the last sequence.

        Example
        -------
        >>> subject = Subject("Manex")
        >>> trial1 = Trial("R001", sequence=Sequence("Manex/sequence_01.txt"))  # Recorded 2025-01-01 10:00:00
        >>> trial2 = Trial("R002", sequence=Sequence("Manex/sequence_02.txt"))  # Recorded 10:03:00, duration 00:01:00
        >>> subject.add_trials(trial1, trial2)
        >>> subject.get_recording_session_duration()
        datetime.timedelta(seconds=240)
        """
        sequences = self.get_sequences(return_type="list")
        sequences_in_order = sort_sequences_by_date(*sequences)
        duration = sequences_in_order[-1].get_date_recording() - sequences_in_order[0].get_date_recording()
        duration += datetime.timedelta(seconds=sequences_in_order[-1].get_duration())
        return duration

    def get_height(self, joints_list=None, verbosity=1):
        """Returns an estimation of the height of the subject, in meters, based on the successive distances between a
        series of joints. The height is calculated across all poses for each Sequence present in each Trial
        (see :meth:`sequence.Sequence.get_subject_height`), and the resulting heights are averaged across all sequences.

        .. versionadded:: 2.0

        Parameters
        ----------
        joints_list: list, optional
            A list of joint labels, of which the successive distances will be calculated. If set on `None` (default),
            this parameter is ignored and the height is estimated by using the pre-set joints listed above. If set,
            the joints used in this parameter replace the presets.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Raises
        ------
        NoExistingJointListPresetException
            If the recording system is not set for a Sequence instance.
        InvalidJointLabelException
            If at least one joint in a preset is missing from a Sequence instance.

        Returns
        -------
        float
            The estimated height of the subject, in meters.

        Example
        -------
        >>> subject = Subject("Maite")
        >>> trial1 = Trial("R001", sequence=Sequence("Maite/sequence_01.csv"))
        >>> trial2 = Trial("R002", sequence=Sequence("Maite/sequence_02.csv"))
        >>> subject.add_trials(trial1, trial2)
        >>> subject.get_subject_height()
        1.68123456879
        """
        heights = []
        for trial_id in self.trials.keys():
            if self.trials[trial_id].has_sequence():
                heights.append(self.trials[trial_id].get_sequence().get_subject_height(joints_list, verbosity))

        return sum(heights)/len(heights)

    def get_arm_length(self, side="left", verbosity=1):
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

        Example
        -------
        >>> subject = Subject("Janire")
        >>> trial1 = Trial("R001", sequence=Sequence("Janire/sequence_01.csv"))
        >>> trial2 = Trial("R002", sequence=Sequence("Janire/sequence_02.csv"))
        >>> subject.add_trials(trial1, trial2)
        >>> subject.get_arm_length(side="left")
        0.754815162342
        """
        arm_lengths = []
        for trial_id in self.trials.keys():
            if self.trials[trial_id].has_sequence():
                arm_lengths.append(self.trials[trial_id].get_sequence().get_subject_arm_length(side, verbosity))

        return sum(arm_lengths) / len(arm_lengths)

    def has_sequence_in_each_trial(self):
        """Returns `True` if each Trial element present in the Subject instance contains a Sequence.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            Whether the Subject instance contains a Sequence in each Trial element.

        Example
        -------
        >>> subject = Subject("Larraitz")
        >>> trial1 = Trial("R001", sequence=Sequence("Larraitz/sequence_01.csv"))
        >>> trial2 = Trial("R002", sequence=None)
        >>> subject.add_trials(trial1, trial2)
        >>> subject.has_sequence_in_each_trial()
        False
        >>> subject.trials["R002"].add_sequence(Sequence("Larraitz/sequence_02.csv"))
        >>> subject.has_sequence_in_each_trial()
        True
        """
        for trial_id in self.trials.keys():
            if not self.trials[trial_id].has_sequence():
                return False
        return True

    def has_audio_in_each_trial(self):
        """Returns `True` if each Trial element present in the Subject instance contains an Audio or AudioDerivative.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            Whether the Subject instance contains an Audio or an AudioDerivative in each Trial element.
            
        Example
        -------
        >>> subject = Subject("Eider")
        >>> trial1 = Trial("R001", audio=Audio("Eider/audio_01.wav"))
        >>> trial2 = Trial("R002", audio=None)
        >>> subject.add_trials(trial1, trial2)
        >>> subject.has_audio_in_each_trial()
        False
        >>> subject.trials["R002"].add_audio(Audio("Eider/audio_02.wav"))
        >>> subject.has_audio_in_each_trial()
        True
        """
        for trial_id in self.trials.keys():
            if not self.trials[trial_id].has_audio():
                return False
        return True

    def are_timestamps_equal_per_trial(self):
        """Returns `True` if, for each trial in the Subject instance, the timestamps of the Sequence and the Audio or
        AudioDerivative are equal. The function will return an error if a sequence or an audio/audio derivative is
        missing.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            Whether the timestamps of the Sequence and the Audio or AudioDerivative are equal for all trials.

        Example
        -------
        >>> subject = Subject("Ihintza")
        >>> trial1 = Trial("R001", sequence=Sequence("Ihintza/sequence_01.mat"), audio=Audio("Ihintza/audio_01.wav"))
        >>> trial2 = Trial("R002", sequence=Sequence("Ihintza/sequence_02.mat"), audio=Audio("Ihintza/audio_02.wav"))
        >>> subject.add_trials(trial1, trial2)
        >>> subject.are_timestamps_equal_per_trial()
        True
        """
        for trial_id in self.trials:
            if not self.trials[trial_id].are_timestamps_equal():
                return False
        return True

    def are_frequencies_equal(self):
        """Returns `True` if the frequencies for all the sequences and audio/audio derivatives are equal across all
        trials. The function will return an error if a sequence or an audio/audio derivative is missing.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            Whether the frequencies for all the sequences and audio/audio derivatives are equal across all trials.

        Example
        -------
        >>> subject = Subject("Mo")
        >>> trial1 = Trial("R001", sequence=Sequence("Mo/sequence_01.mat"), audio=Audio("Mo/audio_01.wav"))  # 20 Hz
        >>> trial2 = Trial("R002", sequence=Sequence("Mo/sequence_02.mat"), audio=Audio("Mo/audio_02.wav"))  # 25 Hz
        >>> subject.add_trials(trial1, trial2)
        >>> subject.are_frequencies_equal()
        False
        """
        for trial_id in self.trials:
            if (self.trials[trial_id].get_sequence().get_sampling_rate() !=
                    self.trials[trial_id].get_audio().get_frequency()):
                return False
        return True

    # == Adding functions ==============================================================================================
    def add_trial(self, trial, replace_if_exists=False, verbosity=1):
        """Adds a Trial instance to the current subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        trial: Trial
            A Trial instance.
        replace_if_exists: bool, optional
            If `False` (default), returns an error if a trial with the same ID already exists for the subject. If
            `True`, the existing trial with the same ID will be replaced by the new trial.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> subject = Subject("Macarena")
        >>> trial1 = Trial("R001", sequence=Sequence("Macarena/sequence_01.csv"), audio=Audio("Macarena/audio_01.wav"))
        >>> subject.add_trial(trial1)
        """
        if trial.trial_id in self.trials.keys() and not replace_if_exists:
            raise Exception(f"A trial with this ID {trial.trial_id} already exists for subject {self.name}.")
        else:
            self.trials[trial.trial_id] = trial
            if verbosity > 0:
                print(f"Trial {trial.trial_id} added to subject {self.name}.")

    def add_trials(self, *trials, replace_if_exists=False, verbosity=1):
        """Adds one or more Trial instances to the current subject.

        .. versionadded:: 2.0

        Parameters
        ----------
        trials: Trial
            One or many Trial instances.
        replace_if_exists: bool, optional
            If `False` (default), returns an error if a trial with the same ID already exists for the subject. If
            `True`, the existing trial with the same ID will be replaced by the new trial.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> subject = Subject("Martin")
        >>> trial1 = Trial("R001", sequence=Sequence("Martin/sequence_01.csv"), audio=Audio("Martin/audio_01.wav"))
        >>> trial2 = Trial("R002", sequence=Sequence("Martin/sequence_02.csv"), audio=Audio("Martin/audio_02.wav"))
        >>> trial3 = Trial("R003", sequence=Sequence("Martin/sequence_03.csv"), audio=Audio("Martin/audio_03.wav"))
        >>> subject.add_trials(trial1, trial2, trial3)
        """
        for trial in trials:
            self.add_trial(trial, replace_if_exists, verbosity)

    # == Print function ================================================================================================
    def __repr__(self):
        """Returns a string representation of the Subject instance, containing basic information about the subject,
        and the amount of trials present.

        .. versionadded:: 2.0

        Returns
        -------
        str
            A string containing the subject name, age, gender, group, and the amount of trials, sequences and audios
            attached to it.

        Example
        -------
        >>> subject = Subject("Itziar", 40, "F", "Basque")
        >>> trial1 = Trial("R001", sequence=Sequence("Itziar/sequence_01.csv"))
        >>> trial2 = Trial("R002", sequence=Sequence("Itziar/sequence_02.csv"), audio=Audio("Itziar/audio_02.wav"))
        >>> subject.add_trials(trial1, trial2)
        >>> print(subject)
        Subject Itziar (F, 40) · Basque · 2 trials, 2 sequences, 1 audio.
        """
        no_sequences = sum([1 for trial in self.trials.values() if trial.has_sequence()])
        no_audios = sum([1 for trial in self.trials.values() if trial.has_audio()])

        trial_text = "trials"
        if len(self.trials) == 1:
            trial_text = "trial"

        seq_text = "sequences"
        if no_sequences == 1:
            seq_text = "sequence"

        aud_text = "audios"
        if no_audios == 1:
            aud_text = "audio"

        return (f"Subject {self.name} ({self.gender}, {self.age}) · {self.group} · "
                f"{self.get_number_of_trials()} {trial_text}, {no_sequences} {seq_text}, {no_audios} {aud_text}")

    def __len__(self):
        """Returns the total amount of trials present in the Subject instance.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The amount of trials present in the Subject instance.

        Example
        -------
        >>> subject = Subject("Amets", 30, "F", "Basque")
        >>> trial1 = Trial("R001", sequence=Sequence("Amets/sequence_01.csv"))
        >>> trial2 = Trial("R002", sequence=Sequence("Amets/sequence_02.csv"), audio=Audio("Amets/audio_02.wav"))
        >>> subject.add_trials(trial1, trial2)
        >>> len(subject)
        2
        """
        return len(self.trials)

    def __getitem__(self, trial_id):
        """Returns a trial, given a trial ID.

        .. versionadded:: 2.0

        Parameters
        ----------
        trial_id: str|int
            The ID of the trial to retrieve.

        Returns
        -------
        Trial
            A Trial instance (if a Trial with the given ID exists).

        Example
        -------
        >>> subject = Subject("Leire", 30, "F", "Basque")
        >>> trial1 = Trial("R001", sequence=Sequence("Leire/sequence_01.csv"))
        >>> subject.add_trial(trial1)
        >>> subject["R001"]  # Equivalent to subject.get_trial("R001")
        """
        return self.trials[trial_id]

    def __eq__(self, other):
        """Returns ``True`` if the subject trials are the same as the ones from another instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Subject
            Another Subject instance.

        Returns
        -------
        bool
            ``True`` if the subject trials are the same as the ones from another instance.

        Example
        -------
        >>> subject1 = Subject("Svetlana", 30, "F", "French")
        >>> trial1 = Trial("R001", sequence=Sequence("Svetlana/sequence_01.csv"))
        >>> subject1.add_trial(trial1)
        >>> subject2 = Subject("Brendan", 40, "M", "English")
        >>> trial2 = Trial("R001", sequence=Sequence("Brendan/sequence_01.csv"))
        >>> subject2.add_trial(trial2)
        >>> subject1 == subject2
        False
        >>> subject3 = Subject()
        >>> subject3.add_trial(trial1)
        >>> subject1 == subject3
        True
        """
        if len(self.trials) != len(other.trials):
            return False
        for trial in self.trials:
            if self.trials[trial] != other.trials[trial]:
                return False
        return True