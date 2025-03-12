"""Tests the Joint methods from the toolbox."""

import unittest

from krajjat.classes.exceptions import InvalidParameterValueException
from krajjat.classes.joint import Joint
from krajjat.classes.sequence import Sequence
from krajjat.tool_functions import generate_random_joints
import numpy as np


class TestsJointMethods(unittest.TestCase):

    def test_init(self):
        joint = Joint("Head", 0, 0, 0)
        assert joint.joint_label == "Head"
        assert joint.x == 0
        assert joint.y == 0
        assert joint.z == 0
        assert joint.get_position() == (0, 0, 0)
        assert joint._velocity_over_threshold == False
        assert joint._interpolated == False
        assert joint._dejittered == False
        assert joint._rereferenced == False
        assert joint._randomized == False

        joint = Joint()
        assert joint.joint_label is None
        assert joint.x is None
        assert joint.y is None
        assert joint.z is None
        assert joint.get_position() == (None, None, None)
        assert joint._velocity_over_threshold == False
        assert joint._interpolated == False
        assert joint._dejittered == False
        assert joint._rereferenced == False
        assert joint._randomized == False

    def test_set_joint_label(self):
        joint = Joint("Head", 0, 0, 0)
        joint.set_joint_label("Hand")
        assert joint.joint_label == "Hand"

        joint = Joint()
        joint.set_joint_label("Hand")
        assert joint.joint_label == "Hand"

    def test_set_x(self):
        joint = Joint("Head", 0, 0, 0)
        joint.set_x(4)
        assert joint.x == 4
        assert joint.get_position() == (4, 0, 0)

        joint = Joint()
        joint.set_x(8)
        assert joint.x == 8
        assert joint.get_position() == (8, None, None)

    def test_set_y(self):
        joint = Joint("Head", 0, 0, 0)
        joint.set_y(15)
        assert joint.y == 15
        assert joint.get_position() == (0, 15, 0)

        joint = Joint()
        joint.set_y(16)
        assert joint.y == 16
        assert joint.get_position() == (None, 16, None)

    def test_set_z(self):
        joint = Joint("Head", 0, 0, 0)
        joint.set_z(23)
        assert joint.z == 23
        assert joint.get_position() == (0, 0, 23)

        joint = Joint()
        joint.set_z(42)
        assert joint.z == 42
        assert joint.get_position() == (None, None, 42)

    def test_set_coordinate(self):
        joint = Joint("Head", 0, 0, 0)
        joint.set_coordinate("x", 1)
        assert joint.x == 1
        joint.set_coordinate("y", 2)
        assert joint.y == 2
        joint.set_coordinate("z", 3)
        assert joint.z == 3

    def test_set_position(self):
        joint = Joint("Head", 0, 0, 0)
        joint.set_position(4, 8, 15)
        assert joint.x == 4
        assert joint.y == 8
        assert joint.z == 15
        assert joint.get_position() == (4, 8, 15)

        joint = Joint()
        joint.set_position(16, 23, 42)
        assert joint.x == 16
        assert joint.y == 23
        assert joint.z == 42
        assert joint.get_position() == (16, 23, 42)

    def test_set_zero(self):
        joint = Joint("Head", 1, 1, 1)
        joint.set_to_zero()
        assert joint.x == 0
        assert joint.y == 0
        assert joint.z == 0
        assert joint.get_position() == (0, 0, 0)

        joint = Joint()
        joint.set_to_zero()
        assert joint.x == 0
        assert joint.y == 0
        assert joint.z == 0
        assert joint.get_position() == (0, 0, 0)

    def test_set_to_none(self):
        joint = Joint("Head", 1, 1, 1)
        joint.set_to_none()
        assert joint.x is None
        assert joint.y is None
        assert joint.z is None
        assert joint.get_position() == (None, None, None)

    def test_get_joint_label(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.get_joint_label() == "Head"

        joint = Joint()
        assert joint.get_joint_label() is None

    def test_get_x(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.get_x() == 1

        joint = Joint()
        assert joint.get_x() is None

    def test_get_y(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.get_y() == 2

        joint = Joint()
        assert joint.get_y() is None

    def test_get_z(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.get_z() == 3

        joint = Joint()
        assert joint.get_z() is None

    def test_get_coordinate(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.get_coordinate("x") == 1
        assert joint.get_coordinate("y") == 2
        assert joint.get_coordinate("z") == 3

        joint = Joint()
        assert joint.get_coordinate("x") is None
        assert joint.get_coordinate("y") is None
        assert joint.get_coordinate("z") is None

    def test_get_position(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.get_position() == (1, 2, 3)

        joint = Joint()
        assert joint.get_position() == (None, None, None)

    def test_has_velocity_over_threshold(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.has_velocity_over_threshold() == False

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_cj = sequence.correct_jitter(1, 2, "poses", verbosity=0)
        assert sequence_cj.poses[1].joints["Head"].has_velocity_over_threshold() == True

    def test_is_corrected(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.is_corrected() == False

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_cj = sequence.correct_jitter(1, 2, "poses", verbosity=0)
        assert sequence_cj.poses[1].joints["Head"].is_corrected() == True
        assert sequence_cj.poses[1].joints["Head"]._dejittered == True
        assert sequence_cj.poses[1].joints["Head"]._rereferenced == False
        assert sequence_cj.poses[1].joints["Head"]._interpolated == False

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_cj = sequence.correct_jitter(1, 2, "poses", verbosity=0)
        assert sequence_cj.poses[1].joints["Head"].is_corrected() == True
        assert sequence_cj.poses[1].joints["Head"]._dejittered == True
        assert sequence_cj.poses[1].joints["Head"]._rereferenced == False
        assert sequence_cj.poses[1].joints["Head"]._interpolated == False

        sequence = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        sequence_rf = sequence.re_reference("Head", verbosity=0)
        assert sequence_rf.poses[1].joints["Head"].is_corrected() == True
        assert sequence_rf.poses[1].joints["Head"]._dejittered == False
        assert sequence_rf.poses[1].joints["Head"]._rereferenced == True
        assert sequence_rf.poses[1].joints["Head"]._interpolated == False

        sequence = Sequence("test_sequences/test_sequence_8.tsv", verbosity=0)
        sequence_cz = sequence.interpolate_missing_data("cubic", verbosity=0)
        assert sequence_cz.poses[1].joints["Head"].is_corrected() == True
        assert sequence_cz.poses[1].joints["Head"]._dejittered == False
        assert sequence_cz.poses[1].joints["Head"]._rereferenced == False
        assert sequence_cz.poses[1].joints["Head"]._interpolated == True

    def test_is_randomized(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_rn = sequence.randomize(verbosity=0)
        assert sequence_rn.poses[1].joints["Head"].is_randomized() == True

    def test_is_zero(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.is_zero() == False

        joint = Joint("Head", 0, 0, 0)
        assert joint.is_zero() == True

        joint = Joint()
        assert joint.is_zero() == False

    def test_is_none(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.is_none() == False

        joint = Joint("Head", 0, 0, 0)
        assert joint.is_none() == False

        joint = Joint()
        assert joint.is_none() == True

    def test_copy(self):
        joint = Joint("Head", 1, 2, 3)
        joint_copy = joint.copy()
        assert id(joint) != id(joint_copy)
        assert joint.joint_label == joint_copy.joint_label
        assert joint.x == joint_copy.x
        assert joint.y == joint_copy.y
        assert joint.z == joint_copy.z
        assert joint.get_position() == joint_copy.get_position()
        assert joint.has_velocity_over_threshold() == joint_copy.has_velocity_over_threshold()
        assert joint.is_corrected() == joint_copy.is_corrected()
        assert joint.is_randomized() == joint_copy.is_randomized()
        assert joint._dejittered == joint_copy._dejittered
        assert joint._rereferenced == joint_copy._rereferenced
        assert joint._interpolated == joint_copy._interpolated

    def test_rotate(self):
        joint = Joint("Head", 1, 2, 0)

        x, y, z = joint.rotate(90, 0, 0)
        assert np.allclose((x, y, z), (-2, 1, 0))

        x, y, z = joint.rotate(180, 0, 0)
        assert np.allclose((x, y, z), (-1, -2, 0))

        x, y, z = joint.rotate(270, 0, 0)
        assert np.allclose((x, y, z), (2, -1, 0))

        x, y, z = joint.rotate(0, 90, 0)
        assert np.allclose((x, y, z), (0, 2, -1))

        x, y, z = joint.rotate(0, 180, 0)
        assert np.allclose((x, y, z), (-1, 2, 0))

        x, y, z = joint.rotate(0, 270, 0)
        assert np.allclose((x, y, z), (0, 2, 1))

        x, y, z = joint.rotate(0, 0, 90)
        assert np.allclose((x, y, z), (1, 0, 2))

        x, y, z = joint.rotate(0, 0, 180)
        assert np.allclose((x, y, z), (1, -2, 0))

        x, y, z = joint.rotate(0, 0, 270)
        assert np.allclose((x, y, z), (1, 0, -2))

        x, y, z = joint.rotate(90, 180, 270)
        assert np.allclose((x, y, z), (0, -1, 2))

    def test_randomize_coordinates_keep_movement(self):
        joint_0 = Joint("Head", 1, 2, 3)
        joint_1 = Joint("Head", 4, 5, 6)
        joint_random = generate_random_joints(1)[0]
        joint_r = joint_1._randomize_coordinates_keep_movement(joint_0, joint_random, 0)

        assert joint_r.x == joint_random.x + (joint_1.x - joint_0.x)
        assert joint_r.y == joint_random.y + (joint_1.y - joint_0.y)
        assert joint_r.z == joint_random.z + (joint_1.z - joint_0.z)

    def test_repr(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint.__repr__() == "Head: (1.0, 2.0, 3.0)"
        joint._rereferenced = True
        assert joint.__repr__() == "Head: (1.0, 2.0, 3.0) · Corrected (Rereferenced)"
        joint._interpolated = True
        assert joint.__repr__() == "Head: (1.0, 2.0, 3.0) · Corrected (Interpolated, Rereferenced)"
        joint._velocity_over_threshold = True
        assert joint.__repr__() == "Head: (1.0, 2.0, 3.0) · Over threshold · Corrected (Interpolated, Rereferenced)"

    def test_eq(self):
        joint_1 = Joint("Head", 1, 2, 3)
        joint_2 = Joint("Head", 1, 2, 3)
        joint_3 = Joint("Neck", 1, 2, 3)
        joint_4 = Joint("Head", 1, 2, 4)
        joint_5 = joint_1.copy()
        joint_6 = Joint("Head", 1.00001, 2, 3)

        assert joint_1 == joint_2
        assert joint_1 != joint_3
        assert joint_1 != joint_4
        assert joint_1 == joint_5
        assert joint_1 == joint_6

        assert Joint("Head", None, None, None) == Joint("Head", None, None, None)

    def test_get_item(self):
        joint = Joint("Head", 1, 2, 3)
        assert joint["x"] == 1
        assert joint["y"] == 2
        assert joint["z"] == 3
        self.assertRaises(InvalidParameterValueException, joint.__getitem__, "w")

    def test_set_item(self):
        joint = Joint("Head", 1, 2, 3)
        joint["x"] = 5
        assert joint.get_x() == 5
        joint["y"] = 6
        assert joint.get_y() == 6
        joint["z"] = 7
        assert joint.get_z() == 7
        self.assertRaises(InvalidParameterValueException, joint.__setitem__, "w", 4)

if __name__ == "__main__":
    unittest.main()