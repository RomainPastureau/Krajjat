"""Tests the Pose methods from the toolbox."""

import unittest

import numpy as np

from krajjat.classes.exceptions import InvalidJointLabelException, JointLabelAlreadyExistsException
from krajjat.classes.pose import Pose
from krajjat.classes.joint import Joint

class TestsPoseMethods(unittest.TestCase):

    def test_init(self):
        pose = Pose(1)
        assert len(pose.joints) == 0
        assert pose.timestamp == 1
        assert pose.relative_timestamp is None

    def test_set_timestamps(self):
        pose = Pose(1)
        pose.set_timestamp(2)
        assert pose.timestamp == 2

    def test_get_joint(self):
        pose = Pose(1)
        joint = Joint("Head", 1, 2, 3)
        pose.add_joint(joint)
        assert pose.get_joint("Head") == joint
        self.assertRaises(InvalidJointLabelException, pose.get_joint, "Hand")

    def test_get_joint_labels(self):
        pose = Pose(42)
        joint_1 = Joint("Head", 1, 2, 3)
        pose.add_joint(joint_1)
        joint_2 = Joint("HandRight", 4, 5, 6)
        pose.add_joint(joint_2)
        joint_3 = Joint("HandLeft", 7, 8, 9)
        pose.add_joint(joint_3)

        assert pose.get_joint_labels() == ["Head", "HandRight", "HandLeft"]

    def test_get_timestamp(self):
        pose = Pose(0)
        assert pose.get_timestamp() == 0

    def test_get_relative_timestamp(self):
        pose = Pose(0)
        assert pose.get_relative_timestamp() is None
        pose.relative_timestamp = 1
        assert pose.get_relative_timestamp() == 1

    def test_add_joint(self):
        pose = Pose(4)
        pose.add_joint(Joint("Head", 1, 2, 3))
        assert len(pose.joints) == 1
        assert pose.joints["Head"].joint_label == "Head"
        assert pose.joints["Head"].x == 1
        assert pose.joints["Head"].y == 2
        assert pose.joints["Head"].z == 3

        self.assertRaises(JointLabelAlreadyExistsException, pose.add_joint,
                          Joint("Head", 1, 2, 3), False)

        pose.add_joint(Joint("Head", 4, 5, 6), True)
        assert len(pose.joints) == 1
        assert pose.joints["Head"].joint_label == "Head"
        assert pose.joints["Head"].x == 4
        assert pose.joints["Head"].y == 5
        assert pose.joints["Head"].z == 6

    def test_add_joints(self):
        pose = Pose(8)
        j1 = Joint("Head", 1, 2, 3)
        j2 = Joint("HandRight", 4, 5, 6)
        j3 = Joint("HandLeft", 7, 8, 9)
        pose.add_joints(j1, j2, j3)

        assert pose.joints["Head"].joint_label == "Head"
        assert pose.joints["Head"].x == 1
        assert pose.joints["Head"].y == 2
        assert pose.joints["Head"].z == 3

        self.assertRaises(JointLabelAlreadyExistsException, pose.add_joints,
                          Joint("Head", 1, 2, 3), replace_if_exists=False)

    def test_generate_average_joint(self):
        pose = Pose(7)
        pose.add_joint(Joint("HeadFront", 0, 0, 0))
        pose.add_joint(Joint("HeadBack", 2, 4, 6))
        joint = pose.generate_average_joint(["HeadFront", "HeadBack"], "Head", True)
        assert joint.joint_label == "Head"
        assert joint.x == 1
        assert joint.y == 2
        assert joint.z == 3
        assert len(pose.joints) == 3

        pose.add_joint(Joint("A", 1, 2, 3))
        pose.add_joint(Joint("B", 4, 5, 10))
        pose.add_joint(Joint("C", 1, 5, 5))
        joint = pose.generate_average_joint(["A", "B", "C"], "D", False)
        assert joint.joint_label == "D"
        assert joint.x == 2
        assert joint.y == 4
        assert joint.z == 6
        assert len(pose.joints) == 6

        self.assertRaises(JointLabelAlreadyExistsException, pose.generate_average_joint, ["HeadFront", "HeadBack"],
                          "Head", True)

    def test_remove_joint(self):
        pose = Pose(2)
        pose.add_joint(Joint("HeadFront", 0, 0, 0))
        pose.add_joint(Joint("HeadBack", 2, 4, 6))
        pose.remove_joint("HeadFront")
        assert len(pose.joints) == 1

        self.assertRaises(InvalidJointLabelException, pose.remove_joint, "HandRight")

    def test_remove_joints(self):
        pose = Pose(2)
        pose.add_joint(Joint("HeadFront", 0, 0, 0))
        pose.add_joint(Joint("HeadBack", 2, 4, 6))
        pose.remove_joints(["HeadFront", "HeadBack"])
        assert len(pose.joints) == 0

        self.assertRaises(InvalidJointLabelException, pose.remove_joints, ["HandRight"])

    def test_convert_to_table(self):
        pose = Pose(0)
        pose.add_joint(Joint("HeadFront", 0, 0, 0))
        pose.add_joint(Joint("HeadBack", 2, 4, 6))

        labels, values = pose.to_table()
        assert labels == ['Timestamp', 'HeadFront_X', 'HeadFront_Y', 'HeadFront_Z',
                          'HeadBack_X', 'HeadBack_Y', 'HeadBack_Z']
        assert values == [0, 0, 0, 0, 2, 4, 6]

        pose.relative_timestamp = 1
        labels, values = pose.to_table(True)
        assert labels == ['Timestamp', 'HeadFront_X', 'HeadFront_Y', 'HeadFront_Z',
                          'HeadBack_X', 'HeadBack_Y', 'HeadBack_Z']

        assert values == [1, 0, 0, 0, 2, 4, 6]

    def test_convert_to_json(self):
        pose = Pose(0)
        pose.add_joint(Joint("HeadFront", 0, 0, 0))
        pose.add_joint(Joint("HeadBack", 2, 4, 6))

        data = pose.to_json()
        assert data == {'Bodies': [{'Joints': [{'JointType': 'HeadFront', 'Position': {'X': 0.0, 'Y': 0.0, 'Z': 0.0}},
                                               {'JointType': 'HeadBack', 'Position': {'X': 2.0, 'Y': 4.0, 'Z': 6.0}}]}],
                        'Timestamp': 0}

        pose.relative_timestamp = 1
        data = pose.to_json(True)
        assert data == {'Bodies': [{'Joints': [{'JointType': 'HeadFront', 'Position': {'X': 0.0, 'Y': 0.0, 'Z': 0.0}},
                                               {'JointType': 'HeadBack', 'Position': {'X': 2.0, 'Y': 4.0, 'Z': 6.0}}]}],
                        'Timestamp': 1}

    def test_copy(self):
        pose = Pose(0)
        pose.add_joint(Joint("HeadFront", 0, 0, 0))
        pose.add_joint(Joint("HeadBack", 2, 4, 6))

        new_pose = pose.copy()
        assert id(pose) != id(new_pose)
        assert pose.timestamp == new_pose.timestamp
        assert pose.relative_timestamp == new_pose.relative_timestamp
        assert len(pose.joints) == len(new_pose.joints)
        assert id(pose.joints["HeadFront"]) != id(new_pose.joints["HeadFront"])
        assert pose.joints["HeadFront"].x == new_pose.joints["HeadFront"].x

    def test_calculate_relative_timestamp(self):
        pose = Pose(17.42)
        pose._calculate_relative_timestamp(9.42)
        assert np.isclose(pose.relative_timestamp, 8.0)

        pose = Pose(9.42)
        pose._calculate_relative_timestamp(17.42)
        assert np.isclose(pose.relative_timestamp, -8.0)

    def test_get_copy_with_empty_joints(self):
        pose = Pose(0)
        pose.add_joint(Joint("HeadFront", 0, 0, 0))
        pose.add_joint(Joint("HeadBack", 2, 4, 6))

        new_pose = pose._get_copy_with_empty_joints()
        assert new_pose.timestamp == pose.timestamp
        assert new_pose.relative_timestamp == pose.relative_timestamp
        assert "HeadFront" in new_pose.joints
        assert "HeadBack" in new_pose.joints
        assert len(new_pose.joints) == 2
        assert new_pose.joints["HeadFront"] is None

    def test_repr(self):
        pose = Pose(0.5)
        pose.add_joint(Joint("Head", 0.2580389, 0.4354536, 2.449435))
        pose.add_joint(Joint("HandRight", 0.2747259, -0.3047626, 2.200738))
        assert pose.__repr__() == "Timestamp: 0.5\nRelative timestamp: None\nJoints (2):\n" +\
                                  "\tHead: (0.2580389, 0.4354536, 2.449435)\n" +\
                                  "\tHandRight: (0.2747259, -0.3047626, 2.200738)"

        pose.joints["Head"]._interpolated = True
        assert pose.__repr__() == "Timestamp: 0.5\nRelative timestamp: None\nJoints (2):\n" +\
                                  "\tHead: (0.2580389, 0.4354536, 2.449435) · Corrected (Interpolated)\n" +\
                                  "\tHandRight: (0.2747259, -0.3047626, 2.200738)"

        pose.remove_joints(["Head", "HandRight"])
        assert pose.__repr__() == "Timestamp: 0.5\nRelative timestamp: None\nEmpty list of joints."

    def test_eq(self):
        pose_1 = Pose(0.5)
        pose_1.add_joint(Joint("Head", 0.2580389, 0.4354536, 2.449435))
        pose_2 = Pose(0.5)
        pose_2.add_joint(Joint("Head", 0.2580389, 0.4354536, 2.449435))
        pose_3 = Pose(0)
        pose_3.add_joint(Joint("Head", 0.2580389, 0.4354536, 2.449435))
        pose_4 = Pose(0.5)
        pose_4.add_joint(Joint("Head", 0.2580389, 0.4354536, 3))
        pose_5 = Pose(0.5)
        pose_5.add_joint(Joint("HandRight", 0.2580389, 0.4354536, 2.449435))
        pose_6 = pose_1.copy()
        pose_7 = Pose(0.5)
        pose_7.add_joint(Joint("Head", 0.2580388, 0.4354536, 2.449435))

        assert pose_1 == pose_2
        assert pose_1 == pose_3
        assert pose_1 != pose_4
        assert pose_1 != pose_5
        assert pose_1 == pose_6
        assert pose_1 == pose_7

    def test_get_item(self):
        pose = Pose(0)
        joint = Joint("HeadFront", 0, 0, 0)
        pose.add_joint(joint)
        assert pose["HeadFront"] == joint
        assert pose["HeadFront"].x == 0