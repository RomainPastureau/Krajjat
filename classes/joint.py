import copy


class Joint(object):
    """Defines a joint pertaining to a pose."""

    def __init__(self, joint_type=None, x=None, y=None, z=None):

        self.joint_type = joint_type  # Label of the joint (e.g. "Head")
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.position = [self.x, self.y, self.z]  # List of the x, y and z coordinates of the joint

        self.movement_over_threshold = False  # True if this joint has moved above threshold during correction
        self.corrected = False  # True if this joint has been corrected by the algorithm
        self.randomized = False  # True if this joint coordinates have been randomly generated

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

    def set_to_zero(self):
        """Sets the joints coordinates to (0, 0, 0)."""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.position = [self.x, self.y, self.z]

    def set_movement_over_threshold(self, movement_over_threshold):
        """Defines that the displacement of a joint compared to the previous pose is above or below threshold"""
        self.movement_over_threshold = movement_over_threshold

    def get_movement_over_threshold(self):
        """Returns True if the displacement of a joint compared to the previous pose is above threshold"""
        return self.movement_over_threshold

    def get_copy(self):
        """Returns a copy of itself"""
        return copy.deepcopy(self)

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
        if self.movement_over_threshold:
            txt += " OVER THRESHOLD"
        if self.corrected:
            txt += " CORRECTED"
        return txt
