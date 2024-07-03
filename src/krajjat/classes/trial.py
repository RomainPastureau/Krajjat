"""Default class defining a trial, that can contain one motion sequence and one audio clip."""
import numpy as np


class Trial(object):
    """Creates a Trial instance, which can contain a motion sequence and an audio clip.

    .. versionadded:: 2.0

    Parameters
    ----------
    trial_id: str, int, or None, optional
        The identifier for the trial, which can be a string, an integer or None. If set on `None`, the initialisation
        function will try to set the trial ID on the name on the name of the Sequence instance or the name of the Audio
        instance, in that order. If no sequence nor audio attribute are set, the function will return an Exception, as
        a trial must have an ID.
    condition: str, int or None, optional
        The condition for the Trial instance.
    sequence: Sequence or None, optional
        The motion sequence from this trial.
    audio: Audio or None, optional
        The audio clip from this trial.

    Attributes
    ----------
    trial_id: str, int or None
        The identifier of the trial.
    condition: str, int or None
        The condition of the trial.
    sequence: Sequence or None
        The motion sequence of the trial.
    audio: Audio or None
        The audio of the trial.
    """

    def __init__(self, trial_id=None, condition=None, sequence=None, audio=None):
        self._trial_id = trial_id
        self._condition = condition

        self._sequence = sequence
        if self._trial_id is None and self.sequence is not None and self.sequence.get_name() is not None:
            self._trial_id = self.sequence.get_name()

        self._audio = audio
        if self._trial_id is None and self.audio is not None and self.audio.get_name() is not None:
            self._trial_id = self.audio.get_name()

        if self._trial_id is None:
            raise Exception("The ID of the trial has to be set or inferred from the name of the Sequence or Audio " +
                            "object. Please set the trial ID.")

    # == Getters/Setter functions ======================================================================================

    @property
    def trial_id(self):
        """Returns the identifier of the trial.

        .. versionadded:: 2.0

        Returns
        -------
        str or int
           The value of the :attr:`trial_id` of the Trial instance.
        """
        return self._trial_id

    @trial_id.setter
    def trial_id(self, trial_id):
        """Raises an Exception if the trial_ID is set outside of initialisation.

        .. versionadded:: 2.0
        """
        raise Exception("Cannot rename the trial ID after initialisation.")

    @property
    def condition(self):
        """Returns the condition of the trial.

        .. versionadded:: 2.0

        Returns
        -------
        str, int or None
            The condition of the trial
        """
        return self._condition

    @condition.setter
    def condition(self, condition):
        """Sets the condition of the trial.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str or int
            The condition of the trial.
        """
        self._condition = condition

    @property
    def sequence(self):
        """Returns the Sequence instance from the trial.

        .. versionadded:: 2.0

        Returns
        -------
        Sequence
           The sequence of the trial.
        """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence):
        """Sets a Sequence instance in the trial.

        Note
        ----
        The function will return an exception if the sequence has already been set for this trial.

        .. versionadded:: 2.0

        Parameters
        ----------
        sequence: Sequence
            A Sequence instance.
        """
        if self._sequence is None:
            self._sequence = sequence
        else:
            raise Exception("A Sequence has already been set for this trial.")

    @property
    def audio(self):
        """Returns the Audio instance from the trial.

        .. versionadded:: 2.0

        Returns
        -------
        Audio
            The audio of the trial.
        """
        return self._audio

    @audio.setter
    def audio(self, audio):
        """Sets an Audio instance in the trial.

        Note
        ----
        The function will return an exception if the audio has already been set for this trial.

        .. versionadded:: 2.0

        Parameters
        ----------
        audio: Audio
            An Audio instance.
        """
        if self._audio is None:
            self._audio = audio
        else:
            raise Exception("An Audio instance has already been set for this trial.")

    # == Checking functions ============================================================================================

    def has_sequence(self):
        """Returns `True` if a Sequence has been set for the Trial instance.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            `False` if :attr:`Trial.sequence` is set on `None`, `True` otherwise.
        """
        return self.sequence is not None

    def has_audio(self):
        """Returns `True` if an Audio has been set for the Trial instance.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            `False` if :attr:`Trial.audio` is set on `None`, `True` otherwise.
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
        """
        if self.sequence.framerate != self.audio.frequency:
            return False
        if len(self.sequence.poses) != len(self.audio.poses):
            return False
        if not np.equal(self.sequence.timestamps, self.audio.timestamps):
            return False

        return True
