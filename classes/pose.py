from collections import OrderedDict
from classes.joint import Joint
from tool_functions import UNITS


class Pose(object):
    """Default class for poses, i.e. series of joints at a specific timestamp in time. A pose, in the motion sequence,
    is the equivalent of a frame in a video. The methods in this class are mainly handled by the methods in the class
    Sequence, but some of them can be directly accessed."""

    def __init__(self, pose_number, timestamp):
        self.pose_number = pose_number  # Index of the pose in the sequence
        self.joints = OrderedDict()  # Dictionary of joint objects
        self.timestamp = timestamp  # Original timestamp of the pose
        self.relative_timestamp = None  # Timestamp relative to the first pose

    # === Joints functions ===

    def add_joint(self, joint_label, joint):
        """Adds a joint to the pose."""
        self.joints[joint_label] = joint

    def get_joint(self, joint_label):
        """Returns a joint object from the pose."""
        if joint_label not in self.joints.keys():
            raise Exception("Invalid joint label: " + joint_label + ".")
        return self.joints[joint_label]

    def generate_average_joint(self, list_joints_to_average, new_joint_label, add_joint=True):
        """Generates and returns a joint that is located at the average position of the other joints."""
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
        """Removes the specified joint from the pose."""
        self.joints.pop(joint_label)

    def remove_joints(self, list_of_joint_labels):
        """Removes the specified joints from the pose."""
        for joint in list_of_joint_labels:
            self.joints.pop(joint)

    # === Timestamp functions ===

    def set_timestamp(self, timestamp):
        """Sets the timestamp of the pose (in seconds)."""
        self.timestamp = float(timestamp)

    def get_timestamp(self):
        """Returns the timestamp of the pose (in seconds)."""
        return self.timestamp

    def get_relative_timestamp(self):
        """Returns the timestamp of the pose, relative to the first pose of the sequence (in seconds)."""
        return self.relative_timestamp

    def _calculate_relative_timestamp(self, t, time_unit="s"):
        """Sets the relative time compared to the time from the first pose (in sec)"""
        self.relative_timestamp = (self.timestamp - t) / UNITS[time_unit]

    # === Conversion functions ===

    def convert_to_table(self, use_relative_timestamp=False):
        """Returns the table version of the pose"""
        labels = ["Timestamp"]
        if use_relative_timestamp:
            values = [self.relative_timestamp]
        else:
            values = [self.timestamp]

        for joint_label in self.joints.keys():
            labels.append(self.joints[joint_label].joint_type + "_X")
            labels.append(self.joints[joint_label].joint_type + "_Y")
            labels.append(self.joints[joint_label].joint_type + "_Z")
            values.append(self.joints[joint_label].x)
            values.append(self.joints[joint_label].y)
            values.append(self.joints[joint_label].z)
        return [labels, values]

    def convert_to_json(self, use_relative_timestamp=False):

        data = {"Bodies": [{"Joints": []}]}

        if use_relative_timestamp:
            data["Timestamp"] = self.relative_timestamp
        else:
            data["Timestamp"] = self.timestamp

        joints = []
        for j in self.joints:
            joint = {"JointType": j.joint_type, "Position": {"X": j.x, "Y": j.y, "Z": j.z}}
            joints.append(joint)

        data["Bodies"][0]["Joints"] = joints

        return data

    def get_copy_with_empty_joints(self, use_relative_timestamp=False):
        """Creates a copy of the pose and returns it"""

        if use_relative_timestamp:
            p = Pose(self.pose_number, self.relative_timestamp)
        else:
            p = Pose(self.pose_number, self.timestamp)

        p.joints = OrderedDict()
        for key in self.joints.keys():
            p.joints[key] = None

        p.relative_timestamp = self.relative_timestamp
        return p

    def __repr__(self):
        """Prints all the joints"""
        txt = "Pose with index "+str(self.pose_number)
        txt += "\nTimestamp: "+str(self.relative_timestamp)
        txt += "\nJoints ("+str(len(self.joints))+"): \n"
        if len(list(self.joints.keys())) == 0:
            txt = "Empty list of joints."
        for joint_label in self.joints.keys():
            txt += "\t" + str(self.joints[joint_label]) + "\n"
        return txt
