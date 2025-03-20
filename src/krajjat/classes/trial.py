"""Default class defining a trial, that can contain one motion sequence and one audio clip."""
import numpy as np

from krajjat.classes import Sequence, AudioDerivative


class Trial(object):
    """Creates a Trial instance, which can contain a motion sequence and an audio clip.

    .. versionadded:: 2.0

    Parameters
    ----------
    trial_id: str|int|None, optional
        The identifier for the trial, which can be a string, an integer or None. If set on `None`, the initialisation
        function will try to set the trial ID on the name on the name of the Sequence instance or the name of the Audio
        instance, in that order. If no sequence nor audio attribute are set, the function will return an Exception, as
        a trial must have an ID.
    condition: str|int|None, optional
        The condition for the Trial instance.
    sequence: Sequence|None, optional
        The motion sequence from this trial.
    audio: Audio|AudioDerivative|None, optional
        The audio clip (or an AudioDerivative) from this trial.

    Attributes
    ----------
    trial_id: str|int
        The identifier of the trial.
    condition: str|int|None
        The condition of the trial.
    sequence: Sequence|None
        The motion sequence of the trial.
    audio: Audio|AudioDerivative|None
        The audio (or an AudioDerivative) of the trial.

    Examples
    --------
    >>> trial = Trial()
    >>> sequence = Sequence("sequence_01.xlsx")
    >>> audio = Audio("audio_01.wav")
    >>> trial = Trial("001", sequence=sequence, audio=audio)
    """

    def __init__(self, trial_id=None, condition=None, sequence=None, audio=None):
        self.trial_id = trial_id
        self.condition = condition

        self.sequence = sequence
        if self.trial_id is None and self.sequence is not None and self.sequence.get_name() is not None:
            self.trial_id = self.sequence.get_name()

        self.audio = audio
        if self.trial_id is None and self.audio is not None and self.audio.get_name() is not None:
            self.trial_id = self.audio.get_name()

        if self.trial_id is None:
            raise Exception("The ID of the trial has to be set or inferred from the name of the Sequence or Audio " +
                            "object. Please set the trial ID.")

    # == Getters/Setter functions ======================================================================================

    def set_trial_id(self, trial_id):
        """Ses the identifier of the trial.

        .. versionadded:: 2.0

        Parameter
        ---------
        trial_id: int|str
            A code to identify the trial.

        Example
        -------
        >>> trial = Trial()
        >>> trial.set_trial_id("R001")
        """
        self.trial_id = trial_id

    def set_condition(self, condition):
        """Sets the condition of the trial.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str or int
            The condition of the trial.

        Example
        -------
        >>> trial = Trial()
        >>> trial.set_condition("English")
        """
        self.condition = condition

    def set_sequence(self, sequence):
        """Sets a Sequence instance in the trial.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence: Sequence
            A Sequence instance.

        Example
        -------
        >>> trial = Trial()
        >>> trial.set_sequence(Sequence("sequence_01.mat"))
        """
        assert type(sequence) is Sequence
        self.sequence = sequence

    def set_audio(self, audio):
        """Sets an Audio instance in the trial.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio: Audio|AudioDerivative
            An Audio or AudioDerivative instance.

        Example
        -------
        >>> trial = Trial()
        >>> trial.set_audio(Audio("audio_01.wav"))
        """
        assert issubclass(type(audio), AudioDerivative)
        self.audio = audio

    def get_trial_id(self):
        """Returns the identifier of the trial.

        .. versionadded:: 2.0

        Returns
        -------
        str or int
           The value of the :attr:`trial_id` of the Trial instance.

        Examples
        --------
        >>> trial = Trial(42)
        >>> trial.get_trial_id()
        42
        >>> sequence = Sequence(name="trial_01")
        >>> trial = Trial(sequence=sequence)
        >>> trial.get_trial_id()
        trial_01
        """
        return self.trial_id

    def get_condition(self):
        """Returns the condition of the trial.

        .. versionadded:: 2.0

        Returns
        -------
        str, int or None
            The condition of the trial

        Examples
        --------
        >>> trial = Trial()
        >>> trial.get_condition()
        None
        >>> trial = Trial(1, condition="Swedish")
        >>> trial.get_condition()
        Swedish
        """
        return self.condition

    def get_sequence(self):
        """Returns the Sequence instance from the trial.

        .. versionadded:: 2.0

        Returns
        -------
        Sequence
           The sequence of the trial.

        Example
        -------
        >>> trial = Trial("108", None, Sequence("sequence_01.xlsx"))
        >>> trial.get_sequence()
        """
        return self.sequence

    def get_audio(self):
        """Returns the Audio instance from the trial.

        .. versionadded:: 2.0

        Returns
        -------
        Audio|AudioDerivative
            The audio of the trial.

        Example
        -------
        >>> trial = Trial(audio=Audio("audio_01.wav"))
        >>> trial.get_audio()
        """
        return self.audio

    def get_audio_kind(self):
        """Returns the attribute :attr:`AudioDerivative.kind` of the :attr:`audio` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        str|None
            The kind of the AudioDerivative, either ``"Audio"``, ``"Envelope"``, ``"Pitch"``, ``"Intensity"``,
            or ``"Formant"`` - or ``None`` if no audio is set.

        Examples
        --------
        >>> trial = Trial(audio=Envelope("envelope.tsv"))
        >>> trial.get_audio_kind()
        Envelope
        >>> trial.set_audio(Intensity("intensity.csv"))
        >>> trial.get_audio_kind()
        Intensity
        """
        if self.audio is not None:
            return self.audio.kind
        else:
            return None

    # == Predicates ============================================================================================

    def has_sequence(self):
        """Returns `True` if a Sequence has been set for the Trial instance.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            `False` if :attr:`Trial.sequence` is set on `None`, `True` otherwise.

        Examples
        --------
        >>> trial = Trial(1)
        >>> trial.has_sequence()
        False
        >>> trial.set_sequence(Sequence("sequence_01.json"))
        >>> trial.has_sequence()
        True
        """
        return self.sequence is not None

    def has_audio(self):
        """Returns `True` if an Audio has been set for the Trial instance.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            `False` if :attr:`Trial.audio` is set on `None`, `True` otherwise.

        Examples
        --------
        >>> trial = Trial(1)
        >>> trial.has_audio()
        False
        >>> trial.set_audio(audio("audio_01.json"))
        >>> trial.has_audio()
        True
        """
        return self.audio is not None

    def are_timestamps_equal(self):
        """Returns `True` if there are as many data points between the Sequence and the Audio objects, and if their
        timestamps are the same.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            `True` if the timestamps are the same for the Sequence and the Audio objects.

        Example
        -------
        >>> sequence = Sequence("sequence_01.mat")
        >>> audio = Audio("audio_01.wav")
        >>> trial = Trial(1, sequence=sequence, audio=audio)
        >>> trial.are_timestamps_equal()
        True
        """
        if self.sequence is None:
            raise Exception("The sequence is not set. Please set the sequence before checking the timestamps.")
        if self.audio is None:
            raise Exception("The audio is not set. Please set the audio before checking the timestamps.")

        if self.sequence.get_sampling_rate() != self.audio.get_frequency():
            return False
        if self.sequence.get_number_of_poses() != self.audio.get_number_of_samples():
            return False
        if not np.allclose(self.sequence.get_timestamps(), self.audio.get_timestamps()):
            return False

        return True

    def __eq__(self, other):
        """Returns `True` if the trial IDs, sequence and audio attributes are the same.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Trial
            Another Trial instance.

        Returns
        -------
        bool
            Whether the Trial instances are equal.

        Example
        -------
        >>> trial_1 = Trial(1, "English", Sequence("sequence_01.mat"), Audio("audio_01.wav"))
        >>> trial_2 = Trial(1, "English", Sequence("sequence_01.mat"), Audio("audio_01.wav"))
        >>> trial_1 == trial_2
        True
        >>> trial_3 = Trial(1, "Spanish", Sequence("sequence_01.mat"), Audio("audio_01.wav"))
        >>> trial_1 == trial_3
        True
        >>> trial_4 = Trial(2, "English", Sequence("sequence_01.mat"), Audio("audio_01.wav"))
        >>> trial_1 == trial_4
        False
        """
        if self.trial_id == other.trial_id and self.sequence == other.sequence and self.audio == other.audio:
            return True
        return False