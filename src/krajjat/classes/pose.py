"""Default class for poses, i.e. group of joints at a specific timestamp. A pose, in the motion sequence, is the
equivalent of a frame in a video. The methods in this class are mainly handled by the methods in the class Sequence,
but some of them can be directly accessed."""

from collections import OrderedDict

from krajjat.classes.exceptions import InvalidJointLabelException, JointLabelAlreadyExistsException
from krajjat.classes.joint import Joint


class Pose(object):
    """Creates an instance from the class Pose and returns a Pose object, which stores :class:`Joint` objects and
    a timestamp.

    .. versionadded:: 2.0

    Parameters
    ----------
    timestamp: float, optional
        The timestamp of the pose (in seconds).

    Attributes
    ----------
    joints: OrderedDict(str: Joint)
        A dictionary of joints, where the keys are the joint labels and the values are Joint instances.
    timestamp: float
        The timestamp of the pose (in seconds).
    relative_timestamp: float
        The timestamp of the pose, relative to the first pose of the sequence (in seconds).

    Example
    -------
    >>> p = Pose(1)
    """

    def __init__(self, timestamp=None):
        self.joints = OrderedDict()  # Dictionary of joint objects
        self.timestamp = timestamp  # Original timestamp of the pose
        self.relative_timestamp = None  # Timestamp relative to the first pose

    # === Setter functions ===
    def set_timestamp(self, timestamp):
        """Sets the attribute :attr:`timestamp` of the pose (in seconds).

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp
            The timestamp of the pose (in seconds).

        Example
        -------
        >>> p = Pose(1)
        >>> p.set_timestamp(2)
        >>> p.get_timestamp()
        2
        """
        self.timestamp = float(timestamp)

    # === Getter functions ===
    def get_joint(self, joint_label):
        """Returns a joint object from the pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        -------
        Joint
            An instance of the class :class:`Joint`.

        Raises
        ------
        InvalidJointLabelException
            If the joint label is not in the keys of the :attr:`joints` attribute.

        Example
        -------
        >>> p = Pose(0)
        >>> j = Joint("Head", 1, 2, 3)
        >>> p.add_joint(j)
        >>> p.get_joint("Head")
        Head: (1, 2, 3)
        """
        if joint_label not in self.joints.keys():
            raise InvalidJointLabelException(joint_label)
        return self.joints[joint_label]

    def get_joint_labels(self):
        """Returns the labels of the joints in the :attr:`joints` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            The list of joint labels.

        Example
        -------
        >>> pose = Pose(42)
        >>> joint_1 = Joint("Head", 1, 2, 3)
        >>> pose.add_joint(joint_1)
        >>> joint_2 = Joint("HandRight", 4, 5, 6)
        >>> pose.add_joint(joint_2)
        >>> joint_3 = Joint("HandLeft", 7, 8, 9)
        >>> pose.add_joint(joint_3)
        >>> pose.get_joint_labels()
        ["Head", "HandRight", "HandLeft"]
        """
        return list(self.joints.keys())

    def get_timestamp(self):
        """Returns the attribute :attr:`timestamp` of the pose (in seconds).

        .. versionadded:: 2.0

        Returns
        -------
        float
            The timestamp of the pose (in seconds).

        Example
        -------
        >>> p = Pose(108)
        >>> p.get_timestamp()
        108
        """
        return self.timestamp

    def get_relative_timestamp(self):
        """Returns the attribute :attr:`relative_timestamp` of the pose, which is the timestamp relative to the first
        pose of the sequence (in seconds).

        .. versionadded:: 2.0

        Returns
        -------
        float
            The timestamp of the pose relative to the first timestamp of the sequence, in seconds.
        """
        return self.relative_timestamp

    # === Joints functions ===
    def add_joint(self, joint, replace_if_exists=False):
        """Adds a Joint object to the pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint: Joint
            A joint object.
        replace_if_exists: bool
            If ``False`` (default), the function will return an error if there is already a key with the name
            ``joint_label`` in the :attr:`joints` parameter. If ``True``, the function will replace the existing
            value if it exists, without any warning message.

        Raises
        ------
        JointLabelAlreadyExistsException
            If the parameter ``replace_if_exists`` is set on `False` and there is already a joint with the same label
            in the pose.

        Example
        -------
        >>> p = Pose(23.4268)
        >>> p.add_joint(Joint("Head", 1, 2, 3))
        """

        joint_label = joint.joint_label
        if not replace_if_exists and joint_label in self.joints.keys():
            raise JointLabelAlreadyExistsException(joint_label)
        else:
            self.joints[joint_label] = joint

    def add_joints(self, *joints, replace_if_exists=False):
        """Adds Joint objects to the pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        joints: Joint
            One or multiple Joint objects.
        replace_if_exists: bool
            If ``False`` (default), the function will return an error if there is already a key with the name
            ``joint_label`` in the :attr:`joints` parameter. If ``True``, the function will replace the existing
            value if it exists, without any warning message.

        Raises
        ------
        JointLabelAlreadyExistsException
            If the parameter ``replace_if_exists`` is set on `False` and there is already a joint with the same label
            in the pose.

        Example
        -------
        >>> p = Pose(23.4268)
        >>> j1 = Joint("Head", 1, 2, 3)
        >>> j2 = Joint("HandRight", 4, 5, 6)
        >>> j3 = Joint("HandLeft", 7, 8, 9)
        >>> p.add_joints(j1, j2, j3)
        """

        for joint in joints:
            self.add_joint(joint, replace_if_exists)

    def generate_average_joint(self, list_joints_to_average, new_joint_label, add_joint=True):
        """Generates and returns a joint that is located at the average position of the other joints.

        .. versionadded:: 2.0

        Parameters
        ----------
        list_joints_to_average: list(Joint)
            A list containing the strings of the joints to average.
        new_joint_label: str
            The label of the joint (e.g. ``"Head"``).
        add_joint: bool, optional
            If set on `True`, the joint created is also added to the parameter joints of the current Pose instance. If
            set on `False`, the joint is only generated and returned.

        Returns
        -------
        Joint
            The average joint.

        Raises
        ------
        JointLabelAlreadyExistsException
            If the label ``new_joint_label`` is already in the :attr:`joints` attribute and ``add_joint`` is set on
            `True`.

        Example
        -------
        >>> pose = Pose(7)
        >>> pose.add_joint(Joint("HeadFront", 0, 0, 0))
        >>> pose.add_joint(Joint("HeadBack", 2, 4, 6))
        >>> joint = pose.generate_average_joint(["HeadFront", "HeadBack"], "Head", True)
        Head: (1, 2, 3)
        """
        x = 0
        y = 0
        z = 0
        no_joints = len(list_joints_to_average)

        for joint_label in list_joints_to_average:
            x += self.joints[joint_label].x
            y += self.joints[joint_label].y
            z += self.joints[joint_label].z

        x /= no_joints
        y /= no_joints
        z /= no_joints

        new_joint = Joint(new_joint_label, x, y, z)

        if add_joint and new_joint_label in self.joints.keys():
            raise JointLabelAlreadyExistsException(new_joint_label)

        if add_joint:
            self.joints[new_joint_label] = new_joint

        return new_joint

    def remove_joint(self, joint_label):
        """Removes the specified joint from the pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Raises
        ------
        InvalidJointLabelException
            If the joint label is not present in the keys of the :attr:`joints` attribute.

        Example
        -------
        >>> pose = Pose()
        >>> pose.add_joint(Joint("HeadFront", 0, 0, 0))
        >>> pose.remove_joint("HeadFront")
        """
        try:
            self.joints.pop(joint_label)
        except KeyError:
            raise InvalidJointLabelException(joint_label)

    def remove_joints(self, list_of_joint_labels):
        """Removes the specified joints from the pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        list_of_joint_labels: list(str)
            A list of labels of joints to remove.

        Raises
        ------
        InvalidJointLabelException
            If a joint label is not present in the keys of the :attr:`joints` attribute.

        Example
        -------
        >>> pose = Pose()
        >>> pose.add_joint(Joint("HeadFront", 0, 0, 0))
        >>> pose.add_joint(Joint("HeadBack", 2, 4, 6))
        >>> pose.remove_joints(["HeadFront", "HeadBack"])
        """
        for joint_label in list_of_joint_labels:
            try:
                self.joints.pop(joint_label)
            except KeyError:
                raise InvalidJointLabelException(joint_label)

    # === Conversion functions ===
    def to_table(self, use_relative_timestamp=False):
        """Returns a table (a list of lists) where the first row is the header, and the second row contains the
        values. The first column of the table contains the timestamps, while the subsequent columns, by sets of three,
        contain the coordinates of a joint on the x, y and z axes respectively. The output then resembles the table
        found in :ref:`Tabled formats <table_example>`.

        .. versionadded:: 2.0

        Parameters
        ----------
        use_relative_timestamp: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        list(list)
            A list of lists that can be interpreted as a table, containing headers and the values of the timestamps and
            the coordinates of the joints from the pose.

        Example
        -------
        >>> pose = Pose(0)
        >>> pose.add_joint(Joint("HeadFront", 0, 0, 0))
        >>> pose.add_joint(Joint("HeadBack", 2, 4, 6))
        >>> pose.to_table()
        [['Timestamp', 'HeadFront_X', 'HeadFront_Y', 'HeadFront_Z', 'HeadBack_X', 'HeadBack_Y', 'HeadBack_Z'],
        [0, 0, 0, 0, 2, 4, 6]]
        """
        labels = ["Timestamp"]
        if use_relative_timestamp:
            values = [self.relative_timestamp]
        else:
            values = [self.timestamp]

        for joint_label in self.joints.keys():
            labels.append(self.joints[joint_label].joint_label + "_X")
            labels.append(self.joints[joint_label].joint_label + "_Y")
            labels.append(self.joints[joint_label].joint_label + "_Z")
            values.append(self.joints[joint_label].x)
            values.append(self.joints[joint_label].y)
            values.append(self.joints[joint_label].z)
        return [labels, values]

    def to_json(self, use_relative_timestamp=False):
        """Returns a list ready to be exported in JSON. The structure followed by the dictionary is the same as the
        output dictionary from Kinect, for compatibility purposes. The output then resembles the table found in
        :ref:`JSON formats <json_example>`.

        .. versionadded:: 2.0

        Parameters
        ----------
        use_relative_timestamp: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        list
            A list containing the data of the sequence, ready to be exported in JSON.

        Example
        -------
        >>> pose = Pose(0)
        >>> pose.add_joint(Joint("HeadFront", 0, 0, 0))
        >>> pose.add_joint(Joint("HeadBack", 2, 4, 6))
        >>> pose.to_json()
        {'Bodies': [{'Joints': [{'JointType': 'HeadFront', 'Position': {'X': 0.0, 'Y': 0.0, 'Z': 0.0}},
                                {'JointType': 'HeadBack', 'Position': {'X': 2.0, 'Y': 4.0, 'Z': 6.0}}]}],
         'Timestamp': 0}
        """

        data = {"Bodies": [{"Joints": []}]}

        if use_relative_timestamp:
            data["Timestamp"] = self.relative_timestamp
        else:
            data["Timestamp"] = self.timestamp

        joints = []
        for j in self.joints:
            joint = {"JointType": j, "Position": {"X": self.joints[j].x, "Y": self.joints[j].y, "Z": self.joints[j].z}}
            joints.append(joint)

        data["Bodies"][0]["Joints"] = joints

        return data

    # === Copy function ===
    def copy(self):
        """Returns a deep copy of itself, containing deep copies of all the joints.

        .. versionadded:: 2.0

        Returns
        -------
        Pose
            A deep copy of the Pose instance.
        """

        p = Pose(self.timestamp)
        p.relative_timestamp = self.relative_timestamp

        p.joints = OrderedDict()
        for key in self.joints.keys():
            p.joints[key] = self.joints[key].copy()

        return p

    # === Private methods ===
    def _calculate_relative_timestamp(self, timestamp_first_pose):
        """Calculates the timestamp relative to the first pose of the sequence. This function is typically called at the
        end of the initialisation of a new sequence (either by opening a file or performing a processing on an
        existing sequence), and sets a value to the attribute :attr:`relative_timestamp`.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp_first_pose: float
            The timestamp of the first pose of the sequence, in its original time unit.
        """
        self.relative_timestamp = (self.timestamp - timestamp_first_pose)

    def _get_copy_with_empty_joints(self, use_relative_timestamp=False):
        """Creates a deep copy of the pose with a timestamp, and a :attr:`joints` with the same label joints as the
        original, but with the values set on `None`. The function then returns the copy.

        .. versionadded:: 2.0

        Parameters
        ----------
        use_relative_timestamp: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        Pose
            A Pose instance that is the deep copy of the original, but with all the values of the :attr:`joints`
            dictionary set on `None`.
        """

        if use_relative_timestamp:
            p = Pose(self.relative_timestamp)
        else:
            p = Pose(self.timestamp)

        p.joints = OrderedDict()
        for key in self.joints.keys():
            p.joints[key] = None

        p.relative_timestamp = self.relative_timestamp
        return p

    def __repr__(self):
        """Returns a string containing the timestamp, the relative timestamp and all the joints labels and coordinates
        from the Pose instance.

        Returns
        -------
        str
            A formatted string of the information contained in :attr:`timestamp`, :attr:`relative_timestamp` and
            :attr:`joints`.

        Example
        -------
        >>> pose = Pose(0.5)
        >>> pose.add_joint(Joint("Head", 0.2580389, 0.4354536, 2.449435))
        >>> pose.add_joint(Joint("HandRight", 0.2747259, -0.3047626, 2.200738))
        >>> print(pose)
        Timestamp: 0.5
        Relative timestamp: None
        Joints (2):
            Head: (0.2580389, 0.4354536, 2.449435)
            HandRight: (0.2747259, -0.3047626, 2.200738)
        """

        txt = "Timestamp: "+str(self.timestamp)
        txt += "\nRelative timestamp: " + str(self.relative_timestamp)
        if len(list(self.joints.keys())) == 0:
            txt += "\nEmpty list of joints.\n"
        else:
            txt += "\nJoints (" + str(len(self.joints)) + "):\n"
        for joint_label in self.joints.keys():
            txt += "\t" + str(self.joints[joint_label]) + "\n"
        return txt[:-1]

    def __eq__(self, other):
        """Returns `True` if all the joints in the attribute :attr:`joints` are identical between the two
        :class:`Pose` objects. If the joints are equal, the function will return `True` regardless of the timestamps.
        Each joint is compared using the function :meth:`Joint.__eq__`.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Pose
            Another :class:`Pose` object.

        Examples
        --------
        >>> pose_1 = Pose(0.5)
        >>> pose_1.add_joint(Joint("Head", 1, 2, 3))
        >>> pose_2 = Pose(0.5)
        >>> pose_2.add_joint(Joint("Head", 1, 2, 3))
        >>> pose_1 == pose_2
        True
        >>> pose_3 = Pose(0)
        >>> pose_3.add_joint(Joint("Head", 1, 2, 3))
        >>> pose_1 == pose_3
        True
        >>> pose_4 = Pose(0.5)
        >>> pose_4.add_joint(Joint("Head", 1, 2, 4))
        >>> pose_1 == pose_4
        False
        >>> pose_5 = Pose(0.5)
        >>> pose_5.add_joint(Joint("HandRight", 1, 2, 3))
        >>> pose_1 == pose_5
        False
        >>> pose_6 = pose_1.copy()
        >>> pose_1 == pose_6
        True
        >>> pose_7 = Pose(0.5)
        >>> pose_7.add_joint(Joint("Head", 1.00001, 2, 3))
        >>> pose_1 == pose_7
        True
        """
        if len(self.joints) != len(other.joints):
            return False

        for joint_label in self.joints:
            if joint_label in other.joints:
                if self.joints[joint_label] != other.joints[joint_label]:
                    return False
            else:
                return False

        return True

    def __getitem__(self, key):
        """Allows to get a joint directly from its label.

        .. versionadded:: 2.0

        Parameters
        ----------
        key: str
            A joint label.

        Returns
        -------
        Joint
            A Joint, if the joint label was present in the :attr:`joints` attribute.

        Example
        -------
        >>> pose = Pose(0)
        >>> pose.add_joint(Joint("HeadFront", 0, 0, 0))
        >>> pose["HeadFront"]
        HeadFront: (0, 0, 0)
        """
        if key in self.joints:
            return self.joints[key]
        else:
            raise InvalidJointLabelException(key)
