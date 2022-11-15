from collections import OrderedDict


class Pose(object):
    """Defines a pose (frame) pertaining to a motion sequence."""

    def __init__(self, pose_number):
        self.pose_number = pose_number  # Index of the pose in the sequence
        self.joints = OrderedDict()  # Dictionary of joint objects
        self.timestamp = None  # Original timestamp of the pose
        self.relative_timestamp = None  # Timestamp relative to the first pose
        self.to_trim = False  # Defines if a pose is to trim or not for another sequence

    # def read_json_data(self, data):
    #     """Opens the file, reads the content and create the joints"""
    #     for joint in data:
    #         self.joints[joint["JointType"]] = Joint(joint)

    # def get_json_data(self):
    #     """Reads and returns the contents of one json file"""
    #     return tool_functions.open_json(self.file)

    def add_joint(self, name, joint):
        """Adds a joint to the pose"""
        self.joints[name] = joint

    def get_joint(self, name):
        """Returns a joint object from the name of the joint"""
        return self.joints[name]

    def set_timestamp(self, timestamp):
        """Sets the original json timestamp"""
        self.timestamp = float(timestamp)

    def get_timestamp(self):
        """Return the original json timestamp"""
        return self.timestamp

    def calculate_relative_timestamp(self, t, convert_to_seconds=True):
        """Sets the relative time compared to the time from the first pose (in sec)"""
        if convert_to_seconds:
            self.relative_timestamp = (self.timestamp - t) / 10000000
        else:
            self.relative_timestamp = (self.timestamp - t)

    def get_relative_timestamp(self):
        """Gets the relative time of this pose compared to the first one"""
        return self.relative_timestamp

    def get_table(self, include_relative_timestamp=False):
        """Returns the table version of the pose"""
        labels = ["Timestamp"]
        if include_relative_timestamp:
            values = [self.relative_timestamp]
        else:
            values = [self.timestamp]

        for joint in self.joints.keys():
            labels.append(self.joints[joint].joint_type + "_X")
            labels.append(self.joints[joint].joint_type + "_Y")
            labels.append(self.joints[joint].joint_type + "_Z")
            values.append(self.joints[joint].x)
            values.append(self.joints[joint].y)
            values.append(self.joints[joint].z)
        return [labels, values]

    def get_json_joint_list(self, include_relative_timestamp=False):

        data = {"Bodies": [{"Joints": []}]}

        if include_relative_timestamp:
            data["Timestamp"] = self.relative_timestamp
        else:
            data["Timestamp"] = self.timestamp

        joints = []
        for j in self.joints.keys():
            joint = {"JointType": j.joint_type, "Position": {"X": j.x, "Y": j.y, "Z": j.z}}
            joints.append(joint)

        data["Bodies"][0]["Joints"] = joints

        return data

    def __repr__(self):
        """Prints all the joints"""
        txt = ""
        if len(list(self.joints.keys())) == 0:
            txt = "Empty list of joints."
        for j in self.joints.keys():
            txt += str(self.joints[j]) + "\n"
        return txt

    # def get_clear_copy(self):
    #     """Creates a copy of the pose and returns it"""
    #     p = Pose(self.pose_number)
    #     p.joints = {}
    #     p.set_timestamp(self.timestamp)
    #     p.relative_timestamp = self.relative_timestamp
    #     return p
