"""Exceptions classes for handling error and displaying messages."""


class InvalidPathException(Exception):
    """Exception raised when a path provided does not point towards a valid Sequence or Audio. This error can be
    raised:

        * When multiple file extensions compatible with the toolbox are detected in the same folder.
        * When files are named sequentially (e.g. ``pose_1.txt``, ``pose_2.txt``, etc.), and at least one file of the
          sequence is missing.
        * When a provided file has an incompatible extension.
        * When the folder or file does not exist.

    .. versionadded:: 2.0

    Parameters
    ----------
    path: str
        The path to a file or folder.
    object_type: str
        The type of the element the path is supposed to point towards (``"sequence"`` or ``"audio clip"``).
    reason: str
        A short description of the reason the path is invalid.
    """

    def __init__(self, path, object_type, reason):
        self.path = path
        self.file_or_folder = object_type
        self.reason = reason
        self.message = "The path " + self.path + " does not point to a valid " + object_type + ": " + reason
        super().__init__(self.message)


class EmptySequenceException(Exception):
    """Exception raised when a Sequence does not have any pose.

    .. versionadded:: 2.0
    """

    def __init__(self):
        self.message = "The Sequence does not have any pose."
        super().__init__(self.message)


class EmptyAudioException(Exception):
    """Exception raised when an Audio object does not have any sample.

    .. versionadded:: 2.0
    """

    def __init__(self):
        self.message = "The Audio clip does not have any sample."
        super().__init__(self.message)


class ImpossibleTimeTravelException(Exception):
    """Exception raised if two consecutive timestamps are not in chronological order.

    .. versionadded:: 2.0

    Parameters
    ----------
    index1: int
        The index of a first pose or sample.
    index2: int
        The index of a second pose or sample, higher than the first.
    timestamp1: float
        The timestamp of the first pose or sample.
    timestamp2: float
        The timestamp of the second pose or sample.
    number_of_timestamps: int
        The number of timestamps in the original object.
    object_type: str
        The type of the element the path is supposed to point towards (``"sequence"`` or ``"audio clip"``).
    """

    def __init__(self, index1, index2, timestamp1, timestamp2, number_of_timestamps, object_type):
        self.index1 = index1
        self.index2 = index2
        self.timestamp1 = timestamp1
        self.timestamp2 = timestamp2
        self.number_of_timestamps = number_of_timestamps
        self.object_type = object_type
        self.message = "The timestamps aren't in chronological order: you can't travel back in time (yet). " + \
                       "Timestamp for " + str(object_type) + str(index1 + 1) + "/" + str(number_of_timestamps) + \
                       " is " + str(timestamp1) + " while the timestamp for pose " + \
                       str(index2 + 1) + " is " + str(timestamp2) + \
                       " (difference of " + str(timestamp1 - timestamp2) + ")."
        super().__init__(self.message)


class InvalidJointLabelException(Exception):
    """Exception raised when the provided joint name does not exist in the Sequence.

    .. versionadded:: 2.0

    Parameters
    ----------
    joint_label: str
        The label of the joint (e.g. ``"Head"``).
    """

    def __init__(self, joint_label):
        self.joint_label = joint_label
        self.message = "Invalid joint label: " + str(self.joint_label) + "."
        super().__init__(self.message)


class ModuleNotFoundException(Exception):
    """Exception raised when a specific Python module has not been found installed in the execution environment.

    .. versionadded:: 2.0

    Parameters
    ----------
    module_name: str
        The name of the Python module that failed to load.
    attempted_task: str
        A short description of the reason the module was necessary.
    """

    def __init__(self, module_name, attempted_task):
        self.module_name = module_name
        self.attempted_task = attempted_task
        self.message = "Module " + str(self.module_name) + " not found. Please install it in order to" + \
                       str(attempted_task) + "."
        super().__init__(self.message)


class InvalidPoseIndexException(Exception):
    """Exception raised when a pose index provided does not exist in the Sequence instance.

    .. versionadded:: 2.0

    Parameters
    ----------
    pose_index: int
        The invalid index of the pose that was provided.
    number_of_poses: int
        The number of poses in the Sequence instance.
    """

    def __init__(self, pose_index, number_of_poses):
        self.pose_index = pose_index
        self.number_of_poses = number_of_poses
        self.message = "The pose index must be between 0 and " + str(self.number_of_poses - 1) + ". "


class InvalidParameterValueException(Exception):
    """Exception raised when the value of a parameter is not one of the expected ones.

    .. versionadded:: 2.0

    Parameters
    ----------
    name: str
        The name of the parameter set at an invalid value.
    given_value
        The invalid value given to the parameter.
    expected_values: list, optional
        The expected value or values the parameter should have.
    """

    def __init__(self, name, given_value, expected_values=None):
        self.name = name
        self.given_value = given_value
        self.expected_values = expected_values
        self.message = "Invalid value for the parameter " + str(self.name) + ": " + str(self.given_value) + "."

        if self.expected_values is not None:
            self.message += "\nThe accepted values are: "
            for i in range(len(expected_values)-1):
                if type(expected_values[i]) is str:
                    self.message += '"' + str(expected_values[i]) + '" '
                else:
                    self.message += str(expected_values[i]) + " "

            if type(expected_values[-1]) is str:
                self.message += 'or "' + str(expected_values[-1]) + '".'
            else:
                self.message += "or " + str(expected_values[-1]) + "."


class JointLabelNotFoundException(Exception):
    """Exception raised when a joint label was not found in a sequence.

    .. versionadded:: 2.0

    Parameters
    ----------
    joint_label: str
        The joint label that was not found in the sequence.
    """

    def __init__(self, joint_label):
        self.message = f"The joint label {joint_label} could not be found in the sequence."
