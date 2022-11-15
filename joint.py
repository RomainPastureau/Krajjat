import copy

class Joint(object):
    """Defines a joint pertaining to a pose."""

    def __init__(self, joint_type=None, x=None, y=None, z=None):

        self.joint_type = joint_type  # Label of the joint (e.g. "Head")
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.position = [self.x, self.y, self.z]  # List of the x, y and z coordinates of the joint

        self.velocity = None  # Velocity of the joint compared to the previous pose
        self.movement_over_threshold = False  # True if this joint has moved above threshold during correction
        self.corrected = False  # True if this joint has been corrected by the algorithm
        self.randomized = False  # True if this joint coordinates have been randomly generated

    # def read_json_data(self, data):
    #     """Reads the data from the json file and creates the corresponding attributes"""
    #     self.joint_type = data["JointType"]
    #     self.x = float(data["Position"]["X"])
    #     self.y = float(data["Position"]["Y"])
    #     self.z = float(data["Position"]["Z"])
    #     self.position = [self.x, self.y, self.z]

    def set_data(self, joint_type, x, y, z):
        self.joint_type = joint_type  # Label of the joint (e.g. "Head")
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.position = [self.x, self.y, self.z]  # List of the x, y and z coordinates of the joint

    def correct_joint(self, x, y, z):
        """Assigns new x, y and z coordinates to the joint and marks it as corrected"""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.position = [self.x, self.y, self.z]
        self.corrected = True

    def set_movement_over_threshold(self, movement_over_threshold):
        """Defines that the displacement of a joint compared to the previous pose is above or below threshold"""
        self.movement_over_threshold = movement_over_threshold

    def get_movement_over_threshold(self):
        """Returns True if the displacement of a joint compared to the previous pose is above threshold"""
        return self.movement_over_threshold

    def set_velocity(self, velocity):
        """Sets the velocity of the joint compared to the previous pose"""
        self.velocity = velocity

    def get_velocity(self):
        """Returns the velocity of the joint compared to the previous pose"""
        return self.velocity

    def get_copy(self):
        """Returns a copy of itself"""
        return copy.copy(self)

    def move_joint_randomized(self, origin, joint, verbose=0):
        """Changes the coordinates of a joint after randomization"""
        if verbose > 0:
            print("Before: "+str(self.x)+", "+str(self.y)+", "+str(self.z))
        self.x = joint.x + (self.x - origin.x)
        self.y = joint.y + (self.y - origin.y)
        self.z = joint.z + (self.z - origin.z)
        self.randomized = True
        if verbose > 0:
            print("After: "+str(self.x)+", "+str(self.y)+", "+str(self.z))

    def __repr__(self):
        """Returns a textual representation of the joint data"""
        txt = self.joint_type + ": (" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"
        txt += " - Shift: " + str(self.velocity)
        if self.movement_over_threshold:
            txt += " OVER THRESHOLD"
        if self.corrected:
            txt += " CORRECTED"
        return txt
