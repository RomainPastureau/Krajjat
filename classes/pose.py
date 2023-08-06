"""Default class for poses, i.e. group of joints at a specific timestamp. A pose, in the motion sequence, is the
equivalent of a frame in a video. The methods in this class are mainly handled by the methods in the class Sequence,
but some of them can be directly accessed."""

from collections import OrderedDict
from classes.joint import Joint
from tool_functions import UNITS


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
    """

    def __init__(self, timestamp=None):
        self.joints = OrderedDict()  # Dictionary of joint objects
        self.timestamp = timestamp  # Original timestamp of the pose
        self.relative_timestamp = None  # Timestamp relative to the first pose

    # === Joints functions ===

    def add_joint(self, joint_label, joint, replace_if_exists=False):
        """Adds a Joint object to the pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        joint: Joint
            A joint object.
        replace_if_exists: bool
            If ``False`` (default), the function will return an error if there is already a key with the name
            ``joint_label`` in the :attr:`joints` parameter. If ``True``, the function will replace the existing
            value if it exists, without any warning message.
        """
        if not replace_if_exists and joint_label in self.joints.keys():
            raise Exception("The joint "+str(joint_label)+" already exists in this pose.")
        else:
            self.joints[joint_label] = joint

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
        """
        if joint_label not in self.joints.keys():
            raise Exception("Invalid joint label: " + joint_label + ".")
        return self.joints[joint_label]

    def get_joint_labels(self):
        """Returns the labels of the joints in the :attr:`joints` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        list(str)
            The list of joint labels.
        """
        return self.joints.keys()

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
        """
        try:
            self.joints.pop(joint_label)
        except KeyError:
            raise Exception("No joint label with the name "+str(joint_label)+" in this pose.")

    def remove_joints(self, list_of_joint_labels):
        """Removes the specified joints from the pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        list_of_joint_labels: list(str)
            A list of labels of joints to remove.
        """
        for joint_label in list_of_joint_labels:
            try:
                self.joints.pop(joint_label)
            except KeyError:
                raise Exception("No joint label with the name " + str(joint_label) + " in this pose.")

    # === Timestamp functions ===

    def set_timestamp(self, timestamp):
        """Sets the attribute :attr:`timestamp` of the pose (in seconds).

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp
            The timestamp of the pose (in seconds).
        """
        self.timestamp = float(timestamp)

    def get_timestamp(self):
        """Returns the attribute :attr:`timestamp` of the pose (in seconds).

        .. versionadded:: 2.0

        Returns
        -------
        float
            The timestamp of the pose (in seconds).
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

    def _calculate_relative_timestamp(self, timestamp_first_pose, time_unit="s"):
        """Calculates the timestamp relative to the first pose of the sequence. This function is typically called at the
        end of the initialisation of a new sequence (either by opening a file or performing a processing on an
        existing sequence), and sets a value to the attribute :attr:`relative_timestamp`.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp_first_pose: float
            The timestamp of the first pose of the sequence, in its original time unit.
        time_unit: str, optional
            The time unit of the timestamps of the sequence. This parameter can take the following values: among the
            following values: "ns", "1ns", "10ns", "100ns", "µs", "1µs", "10µs", "100µs", "ms", "1ms", "10ms", "100ms",
            "s", "sec", "1s", "min", "mn", "h", "hr", "d", "day".

        """
        self.relative_timestamp = (self.timestamp - timestamp_first_pose) / UNITS[time_unit]

    # === Conversion functions ===

    def convert_to_table(self, use_relative_timestamp=False):
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

    def convert_to_json(self, use_relative_timestamp=False):
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
            A list containing the data of the sequence, ready to be exported in JSON."""

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

    # === Miscellaneous functions ===

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

    def get_copy(self):
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
            p.joints[key] = self.joints[key].get_copy()

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
        >>> sequence = Sequence("C:/Users/Hadeel/Sequences/seq1/")
        >>> pose = sequence.get_pose(4)
        >>> print(pose)
        Timestamp: 0.7673687
        Relative timestamp: 0.7673687
        Joints (21):
            Head: (0.2580389, 0.4354536, 2.449435)
            Neck: (0.2200405, 0.2870165, 2.452467)
            SpineShoulder: (0.2213234, 0.2103061, 2.444264)
            SpineMid: (0.224096, -0.02492883, 2.409717)
            SpineBase: (0.2265415, -0.3467222, 2.352579)
            ShoulderLeft: (0.08861267, 0.1529641, 2.387205)
            ElbowLeft: (0.05989294, -0.05652162, 2.338059)
            WristLeft: (0.1408673, -0.2341767, 2.213683)
            HandLeft: (0.1808563, -0.2797168, 2.203833)
            ShoulderRight: (0.3932458, 0.1480468, 2.420666)
            ElbowRight: (0.410402, -0.09375393, 2.338974)
            WristRight: (0.3219678, -0.2662066, 2.203344)
            HandRight: (0.2747259, -0.3047626, 2.200738)
            HipLeft: (0.1522616, -0.3320134, 2.309463)
            KneeLeft: (0.1468181, -0.8557156, 2.233713)
            AnkleLeft: (0.08108322, -1.155779, 2.15636)
            FootLeft: (0.1320685, -1.193715, 2.080927)
            HipRight: (0.2934242, -0.3502887, 2.319931)
            KneeRight: (0.2045003, -0.8930826, 2.275977)
            AnkleRight: (0.2089309, -1.175371, 2.194727)
            FootRight: (0.2288543, -1.20977, 2.095591)
        """

        txt = "\nTimestamp: "+str(self.timestamp)
        txt += "\nRelative timestamp: " + str(self.relative_timestamp)
        txt += "\nJoints ("+str(len(self.joints))+"): \n"
        if len(list(self.joints.keys())) == 0:
            txt = "Empty list of joints."
        for joint_label in self.joints.keys():
            txt += "\t" + str(self.joints[joint_label]) + "\n"
        return txt
