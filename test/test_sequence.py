"""Tests the Sequence methods from the toolbox."""
import unittest

import numpy as np
from datetime import datetime as dt
import os.path as op

import pandas as pd

from krajjat.classes.audio import Audio
from krajjat.classes.exceptions import InvalidPathException, PoseAlreadyExistsException, \
    NoExistingJointListPresetException, InvalidJointLabelException, InvalidPoseIndexException, \
    VariableSamplingRateException
from krajjat.classes.joint import Joint
from krajjat.classes.pose import Pose
from krajjat.classes.sequence import Sequence
from krajjat.plot_functions import single_joint_movement_plotter


class TestsSequenceMethods(unittest.TestCase):

    def test_init(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412418
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 0.777046835
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 6
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == -2.819374393
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 2

        sequence = Sequence("test_sequences/test_sequence_4.tsv", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412419
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 2

        sequence = Sequence("test_sequences/test_sequence_5.tsv", verbosity=0)
        assert len(sequence.poses) == 5
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 0.307930071
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 2

        sequence = Sequence("test_sequences/test_sequence_6.tsv", verbosity=0)
        assert len(sequence.poses) == 1
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[0].joints["Head"].x == -2.819374393
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 1

        sequence = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        assert len(sequence.poses) == 16
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 1
        assert sequence.poses[1].joints["Head"].x == 1
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 16

        sequence = Sequence("test_sequences/test_sequence_8.tsv", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 0
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_1.json", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412418
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412418
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_1.pkl", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412418
        assert sequence.get_system() is None

        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_1.txt", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412418
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_1.xlsx", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412418
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_1.aaa", verbosity=0)
        assert len(sequence.poses) == 3
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["Head"].x == 1.769412418
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 4
        assert sequence.metadata["Number of poses"] == 3

        sequence = Sequence("test_sequences/test_sequence_qtm_1.tsv", verbosity=0)
        assert len(sequence.poses) == 3
        assert "HeadLeft" in sequence.joint_labels
        assert len(sequence.joint_labels) == 3
        assert sequence.poses[1].joints["HeadLeft"].x == 0.129903
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 12
        assert sequence.metadata["NO_OF_FRAMES"] == 3

        sequence = Sequence("test_sequences/test_sequence_individual/*.tsv", verbosity=0)
        assert len(sequence.poses) == 12
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 1
        assert sequence.poses[1].joints["Head"].x == 1
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 2

        sequence = Sequence("test_sequences/test_sequence_individual_no_other_file", verbosity=0)
        assert len(sequence.poses) == 12
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 1
        assert sequence.poses[1].joints["Head"].x == 1
        assert sequence.get_system() is None
        assert len(sequence.metadata) == 2

        sequence = Sequence("test_sequences/test_sequence_kinect", verbosity=0)
        assert len(sequence.poses) == 12
        assert "Head" in sequence.joint_labels
        assert len(sequence.joint_labels) == 21
        assert sequence.poses[1].joints["Head"].x == 0.0810945
        assert sequence.get_system() == "kinect"
        assert len(sequence.metadata) == 11

    def test_set_name(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.name == "test_sequence_1"
        sequence.set_name("test_sequence_2")
        assert sequence.name == "test_sequence_2"

    def test_set_condition(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.condition is None
        sequence.set_condition("English")
        assert sequence.condition == "English"

    def test_set_path_audio(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.path_audio is None
        sequence.set_path_audio("test_audios/test_audio_1.wav")
        assert sequence.path_audio == "test_audios/test_audio_1.wav"

    def test_set_first_timestamp(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=0)
        assert sequence.get_timestamps() == [0, 1, 2]
        sequence.set_first_timestamp(14)
        assert sequence.get_timestamps() == [14, 15, 16]
        sequence.set_first_timestamp(9.3)
        assert np.allclose(sequence.get_timestamps(), [9.3, 10.3, 11.3])

    def test_set_date_recording(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.date_recording is None
        date = dt(2000, 1, 1, 0, 0, 0)
        sequence.set_date_recording(date)
        assert sequence.date_recording == date

    def test_add_pose(self):
        sequence = Sequence(verbosity=0)
        assert sequence.get_number_of_poses() == 0

        joint1 = Joint("Head", 0, 0, 0)
        joint2 = Joint("HandRight", 1, 2, 3)
        joint3 = Joint("HandLeft", 4, 5, 6)
        pose1 = Pose(0.1)
        sequence.add_pose(pose1, verbosity=0)
        assert sequence.get_number_of_poses() == 1
        self.assertRaises(PoseAlreadyExistsException, sequence.add_pose, pose1, verbosity=0)

        pose2 = Pose(0.1)
        self.assertRaises(PoseAlreadyExistsException, sequence.add_pose, pose2, verbosity=0)
        sequence.add_pose(pose2, True, verbosity=0)
        assert sequence.get_number_of_poses() == 1

        pose = Pose(0.05)
        sequence.add_pose(pose, verbosity=0)
        assert sequence.get_number_of_poses() == 2
        assert sequence.poses[1].get_timestamp() == 0.1
        assert sequence.poses[1].get_relative_timestamp() == 0.05

        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=2)
        assert sequence.get_number_of_poses() == 3
        pose4 = Pose(0.5)
        pose4.add_joints(joint1, joint2, joint3)
        sequence.add_pose(pose4, verbosity=0)
        assert sequence.poses[1].get_timestamp() == 0.5
        assert sequence.get_number_of_poses() == 4

    def test_add_poses(self):
        sequence = Sequence(verbosity=0)
        assert sequence.get_number_of_poses() == 0

        joint1 = Joint("Head", 0, 0, 0)
        joint2 = Joint("HandRight", 1, 2, 3)
        joint3 = Joint("HandLeft", 4, 5, 6)
        pose1 = Pose(0.1)
        pose2 = Pose(0.2)
        pose3 = Pose(0.3)
        sequence.add_poses(pose1, pose2, pose3, verbosity=0)
        assert sequence.get_number_of_poses() == 3

        assert sequence.get_timestamps() == [0.1, 0.2, 0.3]

        sequence = Sequence(verbosity=0)
        assert sequence.get_number_of_poses() == 0
        sequence.add_poses(pose3, pose2, pose1, verbosity=0)
        assert sequence.get_number_of_poses() == 3
        assert sequence.get_timestamps() == [0.1, 0.2, 0.3]

        self.assertRaises(PoseAlreadyExistsException, sequence.add_poses, pose3, verbosity=0)

    def test_define_name_init(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", name="seq_1", verbosity=0)
        assert sequence.get_name() == "seq_1"
        sequence = Sequence("test_sequences/test_sequence_1.tsv", name=None, verbosity=0)
        assert sequence.get_name() == "test_sequence_1"
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_name() == "test_sequence_1"
        sequence = Sequence("test_sequences/test_sequence_1.tsv", name="test_sequence_1.tsv", verbosity=0)
        assert sequence.get_name() == "test_sequence_1.tsv"
        sequence = Sequence(verbosity=0)
        assert sequence.get_name() == "Unnamed sequence"
        sequence = Sequence(name="seq_1", verbosity=0)
        assert sequence.get_name() == "seq_1"
        sequence = Sequence("test_sequences/test_sequence_individual/*.tsv", verbosity=0)
        assert sequence.get_name() == "test_sequence_individual"
        sequence = Sequence("test_sequences/test_sequence_individual_no_other_file", verbosity=0)
        assert sequence.get_name() == "test_sequence_individual_no_other_file"
        sequence = Sequence("test_sequences/test_sequence_individual_no_other_file/", verbosity=0)
        assert sequence.get_name() == "test_sequence_individual_no_other_file"

    def test_set_time_unit(self):
        # Tests also _set_timestamp_time_unit
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.time_unit == "ms"
        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=0)
        assert sequence.time_unit == "s"
        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="sec", verbosity=0)
        assert sequence.time_unit == "sec"
        sequence = Sequence("test_sequences/test_sequence_9.tsv", verbosity=0)
        assert sequence.time_unit == "s"
        sequence = Sequence("test_sequences/test_sequence_10.tsv", time_unit="auto", verbosity=0)
        assert sequence.time_unit == "100ns"

    def test_load_from_path(self):
        sequence = Sequence("test_sequences/test_sequence_individual/*.tsv", verbosity=0)
        sequence = Sequence("test_sequences/test_sequence_individual_no_other_file", verbosity=0)
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        self.assertRaises(InvalidPathException, Sequence, "test_sequences/blabla")

    def test_load_poses(self):
        # See test_init
        pass

    def test_load_single_pose_files(self):
        # See test_init
        pass

    def test_load_sequence_file(self):
        # See test_init
        pass

    def test_create_pose_from_table_row(self):
        # See test_init
        pass

    def test_create_pose_from_json(self):
        # See test_init
        pass

    def test_set_timestamp_time_unit(self):
        # See test_init
        pass

    def test_load_json_metadata(self):
        sequence = Sequence("test_sequences/test_sequence_1.json", verbosity=0)
        assert sequence.metadata == {"Number of poses": 3, "Number of joints": 3, "processing_steps": [],
                                     "system": None}

    def test_load_date_recording(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_date_recording() is None

        sequence = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        assert sequence.get_date_recording() == dt(1985, 10, 26, 1, 21, 0)

        sequence = Sequence("test_sequences/test_sequence_qtm_1.tsv", verbosity=0)
        assert sequence.get_date_recording() == dt(2000, 1, 1, 12, 34, 56, 789000)

        sequence = Sequence("test_sequences/test_sequence_kinect", verbosity=0)
        assert sequence.get_date_recording() == dt(2021, 8, 10, 12, 5, 15, 295655)

    def test_set_joint_labels(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.joint_labels == ["Head", "HandRight", "HandLeft"]

        sequence = Sequence("test_sequences/test_sequence_kinect_missing_joints", verbosity=0)
        assert len(sequence.joint_labels) == 21
        assert len(sequence.poses[0].joints) == 21
        assert len(sequence.poses[2].joints) == 21
        assert sequence.poses[0].joints["Head"].x == 0.08329143
        assert sequence.poses[0].joints["SpineMid"].x == 0.07637808
        assert sequence.poses[0].joints["SpineBase"].x == 0.07009158
        assert sequence.poses[2].joints["Head"].x == 0.07885391
        assert sequence.poses[2].joints["SpineMid"].x is None  # Missing
        assert sequence.poses[2].joints["SpineBase"].x is None  # Missing

    def test_apply_joint_labels(self):
        # See test_set_joint_labels
        pass

    def test_set_system(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=0)
        assert sequence.get_system() is None

        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", system="kinect", verbosity=0)
        assert sequence.get_system() == "kinect"

        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        assert sequence.get_system() == "kinect"

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        assert sequence.get_system() == "kualisys"

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", system="qualisys", verbosity=0)
        assert sequence.get_system() == "qualisys"

    def test_calculate_relative_timestamps(self):
        sequence = Sequence("test_sequences/test_sequence_8.tsv", verbosity=0)
        assert sequence.get_timestamps() == [0.5, 0.6, 0.7]
        assert np.allclose(sequence.get_timestamps(True), [0.0, 0.1, 0.2])

        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=0)
        assert sequence.get_timestamps() == [0, 1, 2]
        assert sequence.get_timestamps(True) == [0, 1, 2]

    def test_get_path(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_path() == op.join("test_sequences", "test_sequence_1.tsv")

        sequence = Sequence("test_sequences/test_sequence_individual/*.tsv", verbosity=0)
        assert sequence.get_path() == op.join("test_sequences", "test_sequence_individual")

        sequence = Sequence("test_sequences/test_sequence_individual_no_other_file", verbosity=0)
        assert sequence.get_path() == op.join("test_sequences", "test_sequence_individual_no_other_file")

        sequence = Sequence("test_sequences/test_sequence_individual_no_other_file/", verbosity=0)
        assert sequence.get_path() == op.join("test_sequences", "test_sequence_individual_no_other_file")

        sequence = Sequence("test_sequences\\test_sequence_individual_no_other_file/", verbosity=0)
        assert sequence.get_path() == op.join("test_sequences", "test_sequence_individual_no_other_file")

        sequence = Sequence(op.join("test_sequences\\test_sequence_individual_no_other_file/"), verbosity=0)
        assert sequence.get_path() == op.join("test_sequences", "test_sequence_individual_no_other_file")

    def test_get_name(self):
        # See test_define_name_unit
        pass

    def test_get_condition(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_condition() is None

        sequence = Sequence("test_sequences/test_sequence_1.tsv", condition="English", verbosity=0)
        assert sequence.get_condition() == "English"

    def test_get_system(self):
        # See test_set_system
        pass

    def test_get_joint_labels(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_joint_labels() == ["Head", "HandRight", "HandLeft"]

        sequence = Sequence(verbosity=0)
        assert sequence.get_joint_labels() == []

        joint1 = Joint("Head", 0, 0, 0)
        joint2 = Joint("HandRight", 1, 2, 3)
        joint3 = Joint("HandLeft", 4, 5, 6)
        pose1 = Pose(0.1)
        pose1.add_joints(joint1, joint2, joint3)
        pose2 = Pose(0.2)
        pose2.add_joints(joint1, joint2, joint3)
        sequence.add_poses(pose1, pose2, verbosity=0)
        assert sequence.get_joint_labels() == ["Head", "HandRight", "HandLeft"]

        joint4 = Joint("HipRight", 7, 8, 9)
        pose3 = Pose(0.3)
        pose3.add_joint(joint4)
        sequence.add_pose(pose3, verbosity=0)
        assert sequence.get_joint_labels() == ["Head", "HandRight", "HandLeft", "HipRight"]

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        assert sequence.get_system() == "kualisys"
        assert sequence.get_joint_labels() == ['HeadLeft', 'HeadTop', 'HeadRight', 'HeadFront', 'ShoulderTopLeft',
        'ShoulderBackLeft', 'ArmLeft', 'ElbowLeft', 'WristOutLeft', 'WristInLeft', 'HandOutLeft', 'HandInLeft',
        'ShoulderTopRight', 'ShoulderBackRight', 'ArmRight', 'ElbowRight', 'WristOutRight', 'WristInRight',
        'HandOutRight', 'HandInRight', 'Chest', 'SpineTop', 'BackLeft', 'BackRight', 'WaistFrontLeft', 'WaistBackLeft',
        'WaistBackRight', 'WaistFrontRight', 'ThighLeft', 'KneeLeft', 'ShinLeft', 'AnkleLeft', 'HeelLeft',
        'ForefootOutLeft', 'ToetipLeft', 'ForefootInLeft', 'ThighRight', 'KneeRight', 'ShinRight', 'AnkleRight',
        'HeelRight', 'ForefootOutRight', 'ToetipRight', 'ForefootInRight']

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", system="qualisys", verbosity=0)
        assert sequence.get_system() == "qualisys"
        assert sequence.get_joint_labels() == ['HeadL', 'HeadTop', 'HeadR', 'HeadFront', 'LShoulderTop',
        'LShoulderBack', 'LArm', 'LElbowOut', 'LWristOut', 'LWristIn', 'LHandOut', 'LHandIn', 'RShoulderTop',
        'RShoulderBack', 'RArm', 'RElbowOut', 'RWristOut', 'RWristIn', 'RHandOut', 'RHandIn', 'Chest', 'SpineTop',
        'BackL', 'BackR', 'WaistLFront', 'WaistLBack', 'WaistRBack', 'WaistRFront', 'LThigh', 'LKneeOut', 'LShin',
        'LAnkleOut', 'LHeelBack', 'LForefootOut', 'LToeTip', 'LForefootIn', 'RThigh', 'RKneeOut', 'RShin', 'RAnkleOut',
        'RHeelBack', 'RForefootOut', 'RToeTip', 'RForefootIn']

    def test_get_number_of_joints(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_number_of_joints() == 3

        sequence = Sequence(verbosity=0)
        assert sequence.get_number_of_joints() == 0

        joint1 = Joint("Head", 0, 0, 0)
        joint2 = Joint("HandRight", 1, 2, 3)
        joint3 = Joint("HandLeft", 4, 5, 6)
        pose1 = Pose(0.1)
        pose1.add_joints(joint1, joint2, joint3)
        pose2 = Pose(0.2)
        pose2.add_joints(joint1, joint2, joint3)
        sequence.add_poses(pose1, pose2, verbosity=0)
        assert sequence.get_number_of_joints() == 3

        joint4 = Joint("HipRight", 7, 8, 9)
        pose3 = Pose(0.3)
        pose3.add_joint(joint4)
        sequence.add_pose(pose3, verbosity=0)
        assert sequence.get_number_of_joints() == 4

    def test_get_date_recording(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_date_recording() is None
        assert sequence.get_date_recording("str") == "No date found"

        sequence = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        assert sequence.get_date_recording() == dt(1985, 10, 26, 1, 21, 0)
        assert sequence.get_date_recording("str") == "Saturday 26 October 1985, 01:21:00"

        sequence = Sequence("test_sequences/test_sequence_qtm_1.tsv", verbosity=0)
        assert sequence.get_date_recording() == dt(2000, 1, 1, 12, 34, 56, 789000)
        assert sequence.get_date_recording("str") == "Saturday 1 January 2000, 12:34:56"

        sequence = Sequence("test_sequences/test_sequence_kinect", verbosity=0)
        assert sequence.get_date_recording() == dt(2021, 8, 10, 12, 5, 15, 295655)
        assert sequence.get_date_recording("str") == "Tuesday 10 August 2021, 12:05:15"

    def test_get_subject_height(self):
        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        assert np.isclose(sequence.get_subject_height(verbosity=0), 1.7669554145468716)

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", system="qualisys", verbosity=0)
        assert np.isclose(sequence.get_subject_height(verbosity=0), 1.7669554145468716)

        sequence = Sequence("test_sequences/test_sequence_kinect", verbosity=0)
        assert np.isclose(sequence.get_subject_height(verbosity=0), 1.8506318465979954)

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        self.assertRaises(NoExistingJointListPresetException, sequence.get_subject_height, verbosity=0)

        sequence = Sequence("test_sequences/test_sequence_1.tsv", system="kinect", verbosity=0)
        self.assertRaises(InvalidJointLabelException, sequence.get_subject_height, verbosity=0)

    def test_get_subject_arm_length(self):
        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        assert np.isclose(sequence.get_subject_arm_length("left", verbosity=0), 0.7321786536565029)
        assert np.isclose(sequence.get_subject_arm_length("right", verbosity=0), 0.7177157858720691)

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", system="qualisys", verbosity=0)
        assert np.isclose(sequence.get_subject_arm_length("left", verbosity=0), 0.7321786536565029)
        assert np.isclose(sequence.get_subject_arm_length("right", verbosity=0), 0.7177157858720691)

        sequence = Sequence("test_sequences/test_sequence_kinect", verbosity=0)
        assert np.isclose(sequence.get_subject_arm_length("left", verbosity=0), 0.5123874904069307)
        assert np.isclose(sequence.get_subject_arm_length("right", verbosity=0), 0.5159474697615221)

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        self.assertRaises(NoExistingJointListPresetException, sequence.get_subject_arm_length, "left", verbosity=0)
        self.assertRaises(NoExistingJointListPresetException, sequence.get_subject_arm_length, "right", verbosity=0)

    def test_get_stats(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        stats = sequence.get_info(verbosity=0)

        assert len(stats) == 15
        assert stats["Name"] == "test_sequence_1"
        assert stats["Condition"] is None
        assert stats["Path"] == op.join("test_sequences", "test_sequence_1.tsv")
        assert stats["Date of recording"] == "No date found"
        assert stats["Duration"] == 0.002
        assert stats["Number of poses"] == 3
        assert stats["Number of joint labels"] == 3
        assert stats["Stable sampling rate"] == True
        assert stats["Sampling rate"] == 1000.0
        assert stats["Fill level Head"] == 1.0
        assert stats["Fill level HandRight"] == 1.0
        assert stats["Fill level HandLeft"] == 1.0
        assert np.isclose(stats["Average velocity Head"], 1918.7854963305092)
        assert np.isclose(stats["Average velocity HandRight"], 2995.746241403909)
        assert np.isclose(stats["Average velocity HandLeft"], 2132.753610549076)

        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        stats = sequence.get_info(verbosity=0)
        assert len(stats) == 36
        assert stats["Name"] == "sequence_ainhoa"
        assert stats["Condition"] is None
        assert stats["Path"] == op.join("test_sequences", "sequence_ainhoa.json")
        assert stats["Date of recording"] == "Tuesday 10 August 2021, 15:08:40"
        assert stats["Duration"] == 79.0833823
        assert stats["Number of poses"] == 1269
        assert np.isclose(stats["Subject height"], 1.6200255058925102)
        assert np.isclose(stats["Left arm length"], 0.5076072070357612)
        assert np.isclose(stats["Right arm length"], 0.5080580501930614)
        assert stats["Stable sampling rate"] == False
        assert np.isclose(stats["Average sampling rate"], 16.345829847776503)
        assert np.isclose(stats["SD sampling rate"], 1.9394353845232761)
        assert np.isclose(stats["Min sampling rate"], 4.232300835329216)
        assert np.isclose(stats["Max sampling rate"], 21.118209175860837)
        assert stats["Fill level Head"] == 1.0
        assert stats["Fill level HandRight"] == 1.0
        assert stats["Fill level HandLeft"] == 1.0

        stats = sequence.get_info(return_type="list", verbosity=0)
        assert len(stats) == 2
        assert len(stats[0]) == 36
        assert len(stats[1]) == 36
        assert stats[0][2] == "Condition"
        assert stats[1][1] == op.join("test_sequences", "sequence_ainhoa.json")

        stats = sequence.get_info(return_type="str", verbosity=0)
        assert stats == ("Name: sequence_ainhoa\nPath: test_sequences\\sequence_ainhoa.json\nCondition: None\n" +
                         "Duration: 79.0833823 s\nNumber of poses: 1269\nNumber of joint labels: 21\n"+
                         "Date of recording: Tuesday 10 August 2021, 15:08:40\nSubject height: 1.62 m\n" +
                         "Left arm length: 0.508 m\nRight arm length: 0.508 m\nStable sampling rate: False\n" +
                         "Average sampling rate: 16.345829847776503\nSD sampling rate: 1.9394353845232761\n" +
                         "Min sampling rate: 4.232300835329216\nMax sampling rate: 21.118209175860837")

        stats = sequence.get_info(return_type="dict", full=False, verbosity=0)
        assert len(stats) == 5

        stats = sequence.get_info(return_type="str", full=False, verbosity=0)
        assert stats == "Name: sequence_ainhoa · Duration: 79.0833823 · Number of poses: 1269 · " +\
                        "Number of joint labels: 21 · Date of recording: Tuesday 10 August 2021, 15:08:40"

    def test_get_fill_level(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_fill_level("Head") == 1
        assert sequence.get_fill_level(["Head", "HandRight"]) == {"Head": 1, "HandRight": 1}
        assert sequence.get_fill_level() == {"Head": 1, "HandRight": 1, "HandLeft": 1}

        sequence = Sequence("test_sequences/test_sequence_8.tsv", verbosity=0)
        assert sequence.get_fill_level("Head") == 2/3
        assert sequence.get_fill_level(["Head", "HandRight"]) == {"Head": 2/3, "HandRight": 1}
        assert sequence.get_fill_level() == {"Head": 2/3, "HandRight": 1, "HandLeft": 1}

    def test_get_poses(self):
        joint1 = Joint("Head", 0, 0, 0)
        joint2 = Joint("HandRight", 1, 2, 3)
        joint3 = Joint("HandLeft", 4, 5, 6)
        pose1 = Pose(0.1)
        sequence = Sequence(verbosity=0)
        sequence.add_pose(pose1, verbosity=0)
        assert sequence.get_poses() == [pose1]
        assert len(sequence.get_poses()) == 1

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert len(sequence.get_poses()) == 3

    def test_get_pose(self):
        joint1 = Joint("Head", 0, 0, 0)
        joint2 = Joint("HandRight", 1, 2, 3)
        joint3 = Joint("HandLeft", 4, 5, 6)
        pose1 = Pose(0.1)
        sequence = Sequence(verbosity=0)
        sequence.add_pose(pose1, verbosity=0)
        assert sequence.get_pose(0) == pose1

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        pose = sequence.get_pose(1)
        assert pose.get_timestamp() == 0.001
        self.assertRaises(InvalidPoseIndexException, sequence.get_pose, "one")
        self.assertRaises(InvalidPoseIndexException, sequence.get_pose, -1)
        self.assertRaises(InvalidPoseIndexException, sequence.get_pose, 7)
        self.assertRaises(InvalidPoseIndexException, sequence.get_pose, 0.5)

    def test_get_pose_index_from_timestamp(self):
        sequence = Sequence("test_sequences/test_sequence_5.tsv", time_unit="s", verbosity=0)
        assert sequence.get_pose_index_from_timestamp(2) == 2
        assert sequence.get_pose_index_from_timestamp(2.2) == 2
        assert sequence.get_pose_index_from_timestamp(1.8) == 2
        assert sequence.get_pose_index_from_timestamp(1.5) == 1

        assert sequence.get_pose_index_from_timestamp(2, "closest") == 2
        assert sequence.get_pose_index_from_timestamp(2.2, "closest") == 2
        assert sequence.get_pose_index_from_timestamp(1.8, "closest") == 2
        assert sequence.get_pose_index_from_timestamp(1.5, "closest") == 1

        assert sequence.get_pose_index_from_timestamp(2, "lower") == 2
        assert sequence.get_pose_index_from_timestamp(2.2, "lower") == 2
        assert sequence.get_pose_index_from_timestamp(1.8, "lower") == 1
        assert sequence.get_pose_index_from_timestamp(1.5, "lower") == 1

        assert sequence.get_pose_index_from_timestamp(2, "higher") == 2
        assert sequence.get_pose_index_from_timestamp(2.2, "higher") == 3
        assert sequence.get_pose_index_from_timestamp(1.8, "higher") == 2
        assert sequence.get_pose_index_from_timestamp(1.5, "higher") == 2

    def test_get_pose_from_timestamp(self):
        sequence = Sequence("test_sequences/test_sequence_5.tsv", time_unit="s", verbosity=0)
        assert sequence.get_pose_from_timestamp(2) == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(2.2) == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(1.8) == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(1.5) == sequence.get_pose(1)

        assert sequence.get_pose_from_timestamp(2, "closest") == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(2.2, "closest") == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(1.8, "closest") == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(1.5, "closest") == sequence.get_pose(1)

        assert sequence.get_pose_from_timestamp(2, "lower") == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(2.2, "lower") == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(1.8, "lower") == sequence.get_pose(1)
        assert sequence.get_pose_from_timestamp(1.5, "lower") == sequence.get_pose(1)

        assert sequence.get_pose_from_timestamp(2, "higher") == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(2.2, "higher") == sequence.get_pose(3)
        assert sequence.get_pose_from_timestamp(1.8, "higher") == sequence.get_pose(2)
        assert sequence.get_pose_from_timestamp(1.5, "higher") == sequence.get_pose(2)

    def test_get_number_of_poses(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.get_number_of_poses() == 3
        sequence = Sequence(verbosity=0)
        assert sequence.get_number_of_poses() == 0
        sequence.add_pose(Pose(0.1), verbosity=0)
        assert sequence.get_number_of_poses() == 1

    def test_get_timestamps(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert np.array_equal(sequence.get_timestamps(), np.array([0.000, 0.001, 0.002]))

        sequence = Sequence("test_sequences/test_sequence_10.tsv", verbosity=0)
        assert np.allclose(sequence.get_timestamps(), np.array([481.5162342, 481.5172347, 481.5182352]))
        assert np.allclose(sequence.get_timestamps(True), np.array([0, 0.0010005, 0.002001]))
        assert np.allclose(sequence.get_timestamps(True, 0.001), np.array([0.0010005, 0.002001]))

        sequence = Sequence("test_sequences/test_sequence_7.tsv", time_unit="s", verbosity=0)
        assert np.allclose(sequence.get_timestamps(), np.linspace(0, 15, 16))
        assert np.allclose(sequence.get_timestamps(False, 3, 6), np.array([3, 4, 5, 6]))
        assert np.allclose(sequence.get_timestamps(False, 12), np.array([12, 13, 14, 15]))
        assert np.allclose(sequence.get_timestamps(False, None, 4), np.array([0, 1, 2, 3, 4]))

    def test_get_time_between_poses(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert np.isclose(sequence.get_time_between_poses(0, 1), 0.001)

        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=0)
        assert np.isclose(sequence.get_time_between_poses(0, 1), 1)

        sequence = Sequence("test_sequences/test_sequence_1.tsv", time_unit="d", verbosity=0)
        assert np.isclose(sequence.get_time_between_poses(0, 1), 86400)

    def test_get_duration(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert np.isclose(sequence.get_duration(), 0.002)

        sequence = Sequence("test_sequences/test_sequence_7.tsv", time_unit="s", verbosity=0)
        assert np.isclose(sequence.get_duration(), 15)

        sequence = Sequence("test_sequences/test_sequence_8.tsv", time_unit="s", verbosity=0)
        assert np.isclose(sequence.get_duration(), 0.2)

    def test_get_sampling_rate(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert np.isclose(sequence.get_sampling_rate(), 1000)

        sequence = Sequence("test_sequences/test_sequence_8.tsv", verbosity=0)
        assert np.isclose(sequence.get_sampling_rate(), 10)

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        assert np.isclose(sequence.get_sampling_rate(), 200)

        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        self.assertRaises(VariableSamplingRateException, sequence.get_sampling_rate)

    def test_get_sampling_rates(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert np.allclose(sequence.get_sampling_rates(), [1000, 1000])

        sequence = Sequence("test_sequences/test_sequence_8.tsv", verbosity=0)
        assert np.allclose(sequence.get_sampling_rates(), [10, 10])

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        assert np.allclose(sequence.get_sampling_rates(), np.ones(49) * 200)

        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        assert np.allclose(sequence.get_sampling_rates()[:3], [4.23230084, 13.36953804, 13.73194421])

    def test_has_stable_sampling_rate(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence.has_stable_sampling_rate() == True

        sequence = Sequence("test_sequences/test_sequence_8.tsv", verbosity=0)
        assert sequence.has_stable_sampling_rate() == True

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        assert sequence.has_stable_sampling_rate() == True

        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        assert sequence.has_stable_sampling_rate() == False

    def test_get_measure(self):
        # Coordinates
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        measure = sequence.get_measure("x", "Head")
        assert np.allclose(measure, np.array([0.160617024, 1.769412418, -1.678118013]))

        measure = sequence.get_measure("x", "Head", 0.000, 0.000, verbosity=0)
        assert np.allclose(measure, np.array([0.160617024]))

        measure = sequence.get_measure("y", ["Head", "HandRight"], verbosity=0)
        assert np.allclose(measure["Head"], np.array([0.494735048, 0.885312165, 0.85064505]))
        assert np.allclose(measure["HandRight"], np.array([0.873208589, 2.805260745, -0.059736892]))

        measure = sequence.get_measure("z", None, verbosity=0)
        assert type(measure) is dict
        assert len(measure) == 3
        assert np.allclose(measure["Head"], np.array([-0.453307693, -0.785718175, 1.37303521]))
        assert np.allclose(measure["HandRight"], np.array([0.408531847, 2.846927978, -1.456678185]))
        assert np.allclose(measure["HandLeft"], np.array([-0.483163821, 2.557279205, -0.221482265]))

        measure = sequence.get_measure("xyz", "Head", verbosity=0)
        assert np.allclose(measure, np.array([[0.160617024, 0.494735048, -0.453307693],
                                              [1.769412418, 0.885312165, -0.785718175],
                                              [-1.678118013, 0.85064505, 1.37303521]]))

        measure = sequence.get_measure("xyz", "Head", 0.001, verbosity=0)
        assert np.allclose(measure, np.array([[1.769412418, 0.885312165, -0.785718175],
                                              [-1.678118013, 0.85064505, 1.37303521]]))

        # Distances
        measure = sequence.get_measure("dx", "Head", verbosity=0)
        assert np.allclose(measure, np.array([1.60879539, 3.44753043]))

        measure = sequence.get_measure("dy", "Head", verbosity=0)
        assert np.allclose(measure, np.array([0.39057712, 0.03466711]))

        measure = sequence.get_measure("dz", "Head", verbosity=0)
        assert np.allclose(measure, np.array([0.33241048, 2.15875338]))

        measure = sequence.get_measure("d", "Head", verbosity=0)
        assert np.allclose(measure, np.array([1.68857035, 4.06778614]))

        sequence = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        measure = sequence.get_measure("dist", "Head", 0, 0.007)
        assert np.allclose(measure, np.array([1.73205081, 3.46410162, 5.19615242, 5.19615242,
                                              3.46410162, 1.73205081, 0.8660254, 0]))

        measure = sequence.get_measure("vel", "Head", 0, 0.007, verbosity=0)
        assert np.allclose(measure, np.array([98.52187564, 86.07295955, 73.32947175, 60.33673096,
                                              47.14005591, 33.78476532, 20.31617792, 6.77961243]))

        measure = sequence.get_measure("vel", "Head", 0.003, 0.007, verbosity=0)
        assert np.allclose(measure, np.array([60.33673096, 47.14005591, 33.78476532, 20.31617792, 6.77961243]))

        # Derivatives with close windows
        sequence = Sequence("test_sequences/test_sequence_11.tsv", verbosity=0)
        measure = sequence.get_measure("dist", "Head", verbosity=0)
        assert np.allclose(measure, [3.0, 6.0, 9.0, 3.0, 3.0, 6.0, 6.0, 6.0, 3.0, 3.0, 18.0, 9.0, 3.0, 9.0, 3.0])

        measure = sequence.get_measure("v", "Head", window_length=2, verbosity=0)
        assert np.allclose(measure, [ 30., 60., 90., 30., 30., 60., 60., 60., 30., 30., 180., 90., 30., 90., 30., 0.])

        measure = sequence.get_measure("a", "Head", window_length=3, verbosity=0)
        assert np.allclose(measure, [300.0, 300.0, 300.0, 600.0, 0.0, 300.0, 0.0, 0.0,
                                     900.0, 0.0, 1500.0, 900.0, 1200.0, 1200.0, 600.0, 300.0])

        measure = sequence.get_measure("j", "Head", window_length=4, verbosity=0)
        assert np.allclose(measure, [0.0, 0.0, 9000.0, 6000.0, 3000.0, 3000.0, 0.0, 9000.0,
                                     9000.0, 15000.0, 24000.0, 3000.0, 24000.0, 18000.0, 3000.0, 3000.0])

        # Derivatives with window 7
        measure = sequence.get_measure("v", "Head", 0, window_length=7, verbosity=0)
        assert np.allclose(measure, [ 15.11904762,  50.23809524,  69.4047619 ,  57.26190476,  40.83333333,
                                         39.76190476,  65.11904762,  54.4047619 ,  28.0952381 ,  43.33333333,
                                         115.11904762,  99.88095238,  67.5       ,  30.23809524,  35.83333333,
                                         30.95238095])

        measure = sequence.get_measure("a", "Head", 0, 0.5, window_length=7,
                                       verbosity=0)
        assert np.allclose(measure, [236.36363636, 418.18181818,  50., 311.36363636, 122.72727273, 231.81818182])

        measure = sequence.get_measure("j", "Head", 0, 0.5, window_length=7, verbosity=0)
        assert np.allclose(measure, [1875., 750., 6375., 2250., 7125., 750.])

        measure = sequence.get_measure("s", "Head", 0, 0.5, window_length=7, verbosity=0)
        assert np.allclose(measure, [ 45000.,  20000., 145000., 220000., 55000., 80000.])

        measure = sequence.get_measure("c", "Head", 0, 0.5, window_length=7, verbosity=0)
        assert np.allclose(measure, [150000.0, 300000.0, 750000.0, 300000.0, 1050000.0, 300000.0])

        measure = sequence.get_measure("p", "Head", 0, 0.5, window_length=7, verbosity=0)
        assert np.allclose(measure, [9000000.0, 12000000.0, 33000000.0, 42000000.0, 15000000.0, 12000000.0])

    def test_get_extremum_measure(self):
        # Coordinates
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        extrema = sequence.get_extremum_measure("x", "Head", verbosity=0)
        assert np.allclose(extrema, np.array([-1.678118013, 1.769412418]))

        extremum = sequence.get_extremum_measure("x", "Head", "max", verbosity=0)
        assert np.isclose(extremum, 1.769412418)

        extremum = sequence.get_extremum_measure("x", "Head", "min", verbosity=0)
        assert np.isclose(extremum, -1.678118013)

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        extrema = sequence.get_extremum_measure("x", None, "both", True, verbosity=0)
        assert np.allclose(extrema["Head"], np.array([-1.678118013, 1.769412418]))
        assert np.allclose(extrema["HandRight"], np.array([-1.612589342, 0.948776526]))
        assert np.allclose(extrema["HandLeft"], np.array([-1.418789803, -0.80645271]))

        extremum = sequence.get_extremum_measure("x", None, "max", verbosity=0)
        assert np.isclose(extremum["Head"], 1.769412418)
        assert np.isclose(extremum["HandRight"], 0.948776526)
        assert np.isclose(extremum["HandLeft"], -0.80645271)

        extremum = sequence.get_extremum_measure("x", None, "min", verbosity=0)
        assert np.isclose(extremum["Head"], -1.678118013)
        assert np.isclose(extremum["HandRight"], -1.612589342)
        assert np.isclose(extremum["HandLeft"], -1.418789803)

        extrema = sequence.get_extremum_measure("x", None, "both", False, verbosity=0)
        assert np.allclose(extrema, np.array([-1.678118013, 1.769412418]))

        extremum = sequence.get_extremum_measure("x", None, "max", False, verbosity=0)
        assert np.isclose(extremum, 1.769412418)

        extremum = sequence.get_extremum_measure("x", None, "min", False, verbosity=0)
        assert np.isclose(extremum, -1.678118013)

        # Derivatives with window 7
        sequence = Sequence("test_sequences/test_sequence_11.tsv", verbosity=0)
        measure = sequence.get_extremum_measure("v", "Head", "min", window_length=7, verbosity=0)
        assert np.isclose(measure, 15.119047619047619)

        measure = sequence.get_extremum_measure("a", "Head", "both", timestamp_end=0.5,
                                                window_length=7, verbosity=0)
        assert np.allclose(measure, [50.0, 418.181818181818])

        measure = sequence.get_extremum_measure("j", "Head", "max", True, 0,
                                                0.5, window_length=7, verbosity=0)
        assert np.isclose(measure, 7125.0)

    def test_get_sum_measure(self):
        # Coordinates
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sum_value = sequence.get_sum_measure("x", "Head")
        assert np.isclose(sum_value, 0.25191142899999996)

        sum_values = sequence.get_sum_measure("x", None)

        assert np.isclose(sum_values["Head"], 0.25191142899999996)
        assert np.isclose(sum_values["HandRight"], -0.5358494410000001)
        assert np.isclose(sum_values["HandLeft"], -3.6203082269999998)

        sum_value = sequence.get_sum_measure("x", None, False, verbosity=0)
        assert np.allclose(sum_value, -3.904246239)

        sum_value = sequence.get_sum_measure("x", None, False, absolute=True, verbosity=0)
        assert np.allclose(sum_value, 9.917784925)

        # Derivatives with window 7
        sequence = Sequence("test_sequences/test_sequence_11.tsv", verbosity=0)
        sum_value = sequence.get_sum_measure("v", "Head", window_length=7, absolute=True, verbosity=0)
        assert np.isclose(sum_value, 843.0952381)

        sum_value = sequence.get_sum_measure("a", "Head", timestamp_end=0.5, window_length=7,
                                             absolute=True, verbosity=0)
        assert np.isclose(sum_value, 1370.45454545)

        sum_value = sequence.get_sum_measure("j", "Head", True,
                                             0, 0.5, window_length=7, absolute=True, verbosity=0)
        assert np.isclose(sum_value, 19125.)

    def test_correct_jitter(self):
        # Jump: single joint out of pattern on linearly increasing data
        sequence = Sequence("test_sequences/test_sequence_12.tsv", name="ts12", verbosity=0)
        sequence_cj = sequence.correct_jitter(2, 3, "poses", "default", True, True, "ts12cj", verbosity=0)
        assert sequence_cj.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_cj.poses[4].joints["Head"].get_position() == (0.4, 0.4, 0.4)
        assert sequence_cj.poses[5].joints["Head"].get_position() == (0.5, 0.5, 0.5)  # Corrected
        assert sequence_cj.poses[6].joints["Head"].get_position() == (0.6, 0.6, 0.6)
        assert sequence_cj.poses[10].joints["Head"].get_position() == (1, 1, 1)
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "ts12cj"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter"

        # Classify it as a twitch
        sequence = Sequence("test_sequences/test_sequence_12.tsv", name="ts12", verbosity=0)
        sequence_cj = sequence.correct_jitter(10, 3, "poses", "default", True, True, "ts12cj", verbosity=0)
        assert sequence_cj.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_cj.poses[4].joints["Head"].get_position() == (0.4, 0.4, 0.4)
        assert sequence_cj.poses[5].joints["Head"].get_position() == (0.5, 0.5, 0.5)  # Corrected
        assert sequence_cj.poses[6].joints["Head"].get_position() == (0.6, 0.6, 0.6)
        assert sequence_cj.poses[10].joints["Head"].get_position() == (1, 1, 1)
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "ts12cj"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter"

        # Classify it as a twitch, using linear interpolation
        sequence = Sequence("test_sequences/test_sequence_12.tsv", name="ts12", verbosity=0)
        sequence_cj = sequence.correct_jitter(10, 3, "poses", "linear", True, True, "ts12cj", verbosity=0)
        assert sequence_cj.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_cj.poses[4].joints["Head"].get_position() == (0.4, 0.4, 0.4)
        assert sequence_cj.poses[5].joints["Head"].get_position() == (0.5, 0.5, 0.5)  # Corrected
        assert sequence_cj.poses[6].joints["Head"].get_position() == (0.6, 0.6, 0.6)
        assert sequence_cj.poses[10].joints["Head"].get_position() == (1, 1, 1)
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "ts12cj"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter"

        # Classify it as a twitch, using cubic interpolation
        sequence = Sequence("test_sequences/test_sequence_12.tsv", name="ts12", verbosity=0)
        sequence_cj = sequence.correct_jitter(10, 3, "poses", "cubic", True, True, "ts12cj", verbosity=0)
        assert sequence_cj.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_cj.poses[4].joints["Head"].get_position() == (0.4, 0.4, 0.4)
        assert sequence_cj.poses[5].joints["Head"].get_position() == (0.5, 0.5, 0.5)  # Corrected
        assert sequence_cj.poses[6].joints["Head"].get_position() == (0.6, 0.6, 0.6)
        assert sequence_cj.poses[10].joints["Head"].get_position() == (1, 1, 1)
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "ts12cj"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter"

        # Twitch: single joint out of pattern on linearly stagnating data
        sequence = Sequence("test_sequences/test_sequence_13.tsv", name="ts13", verbosity=0)
        sequence_cj = sequence.correct_jitter(2, 3, "poses", "default", True, True, verbosity=0)
        assert sequence_cj.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_cj.poses[4].joints["Head"].get_position() == (0.11, 0.11, 0.11)
        assert sequence_cj.poses[5].joints["Head"].get_position() == (0.11, 0.11, 0.11)  # Corrected
        assert sequence_cj.poses[6].joints["Head"].get_position() == (0.11, 0.11, 0.11)
        assert sequence_cj.poses[10].joints["Head"].get_position() == (0.1, 0.1, 0.1)
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "ts13 +CJ"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter"

        # Proper jump
        sequence = Sequence("test_sequences/test_sequence_14.tsv", verbosity=0)
        sequence_cj = sequence.correct_jitter(4, 5, "poses", "default", True, True, verbosity=0)
        assert sequence_cj.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_cj.poses[4].joints["Head"].get_position() == (0.11, 0.11, 0.11)
        assert sequence_cj.poses[5].joints["Head"].get_position() == (0.11, 0.11, 0.11)
        assert sequence_cj.poses[6].joints["Head"].get_position() == (0.11, 0.11, 0.11)
        assert sequence_cj.poses[10].joints["Head"].get_position() == (0.1, 0.1, 0.1)
        assert np.allclose(sequence_cj.poses[11].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_cj.poses[12].joints["Head"].get_position(), (0.3, 0.3, 0.3))
        assert np.allclose(sequence_cj.poses[13].joints["Head"].get_position(), (0.5, 0.5, 0.5))
        assert np.allclose(sequence_cj.poses[14].joints["Head"].get_position(), (0.7, 0.7, 0.7))
        assert np.allclose(sequence_cj.poses[15].joints["Head"].get_position(), (0.9, 0.9, 0.9))
        assert np.allclose(sequence_cj.poses[16].joints["Head"].get_position(), (1.1, 1.1, 1.1))
        assert np.allclose(sequence_cj.poses[17].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert sequence_cj.poses[20].joints["Head"].get_position() == (1.1, 1.1, 1.1)
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "test_sequence_14 +CJ"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter"

        # Proper jump
        sequence = Sequence("test_sequences/test_sequence_14.tsv", verbosity=0)
        sequence_cj = sequence.correct_jitter(4, 5, "poses", "cubic", True, True, verbosity=0)
        assert sequence_cj.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_cj.poses[4].joints["Head"].get_position() == (0.11, 0.11, 0.11)
        assert np.allclose(sequence_cj.poses[5].joints["Head"].get_position(), (0.112183, 0.112183, 0.112183))
        assert sequence_cj.poses[6].joints["Head"].get_position() == (0.11, 0.11, 0.11)
        assert sequence_cj.poses[10].joints["Head"].get_position() == (0.1, 0.1, 0.1)
        assert np.allclose(sequence_cj.poses[11].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_cj.poses[12].joints["Head"].get_position(), (0.228092, 0.228092, 0.228092))
        assert np.allclose(sequence_cj.poses[13].joints["Head"].get_position(), (0.459611, 0.459611, 0.459611))
        assert np.allclose(sequence_cj.poses[14].joints["Head"].get_position(), (0.727083, 0.727083, 0.727083))
        assert np.allclose(sequence_cj.poses[15].joints["Head"].get_position(), (0.963037, 0.963037, 0.963037))
        assert np.allclose(sequence_cj.poses[16].joints["Head"].get_position(), (1.1, 1.1, 1.1))
        assert np.allclose(sequence_cj.poses[17].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert sequence_cj.poses[20].joints["Head"].get_position() == (1.1, 1.1, 1.1)
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "test_sequence_14 +CJ"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter"
        assert sequence_cj.metadata["processing_steps"][0]["velocity_threshold"] == 4
        assert sequence_cj.metadata["processing_steps"][0]["window"] == 5
        assert sequence_cj.metadata["processing_steps"][0]["window_unit"] == "poses"
        assert sequence_cj.metadata["processing_steps"][0]["method"] == "cubic"
        assert sequence_cj.metadata["processing_steps"][0]["correct_twitches"] == True
        assert sequence_cj.metadata["processing_steps"][0]["correct_jumps"] == True

        # No processing test
        sequence_cj = sequence.correct_jitter(1000, 5, verbosity=0)
        assert sequence_cj == sequence

    def test_correct_jitter_window(self):
        # See test_correct_jitter
        pass

    def test_correct_jitter_single_joint(self):
        # See test_correct_jitter
        pass

    def test_correct_jitter_savgol(self):
        sequence = Sequence("test_sequences/test_sequence_12.tsv", name="ts12", verbosity=0)
        print(sequence.print_all())
        sequence_cj = sequence.correct_jitter_savgol(5, 3, "ts12cj", verbosity=0)
        print(sequence_cj.print_all())
        assert np.allclose(sequence_cj.poses[0].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_cj.poses[4].joints["Head"].get_position(), (0.88, 0.88, 0.88))
        assert np.allclose(sequence_cj.poses[5].joints["Head"].get_position(), (1.18, 1.18, 1.18))  # Corrected
        assert np.allclose(sequence_cj.poses[6].joints["Head"].get_position(), (1.08, 1.08, 1.08))
        assert np.allclose(sequence_cj.poses[10].joints["Head"].get_position(), (1, 1, 1))
        assert sequence_cj.get_path() == sequence.get_path()
        assert sequence_cj.get_date_recording() == sequence.get_date_recording()
        assert sequence_cj.get_condition() == sequence.get_condition()
        assert sequence_cj.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_cj.get_system() == sequence.get_system()
        assert sequence_cj.get_name() == "ts12cj"
        assert len(sequence_cj.metadata["processing_steps"]) == 1
        assert sequence_cj.metadata["processing_steps"][0]["processing_type"] == "correct_jitter_savgol"
        assert sequence_cj.metadata["processing_steps"][0]["window_length"] == 5
        assert sequence_cj.metadata["processing_steps"][0]["poly_order"] == 3

        # single_joint_movement_plotter([sequence, sequence_cj], "Head", ["x", "y", "z"])

    def test_re_reference(self):
        sequence = Sequence("test_sequences/test_sequence_9.tsv", verbosity=0)
        sequence_rr = sequence.re_reference("Head", verbosity=0)
        assert sequence_rr.get_path() == sequence.get_path()
        assert sequence_rr.get_date_recording() == sequence.get_date_recording()
        assert sequence_rr.get_condition() == sequence.get_condition()
        assert sequence_rr.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_rr.get_system() == sequence.get_system()
        assert sequence_rr.get_name() == "test_sequence_9 +RF"
        assert sequence_rr.poses[0].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_rr.poses[1].joints["Head"].get_position() == (0, 0, 0)
        assert sequence_rr.poses[2].joints["Head"].get_position() == (0, 0, 0)
        new_x = sequence.poses[0].joints["HandRight"].get_x() - sequence.poses[0].joints["Head"].get_x()
        assert sequence_rr.poses[0].joints["HandRight"].get_x() == new_x
        assert sequence_rr.metadata["processing_steps"][0]["processing_type"] == "re_reference"
        assert sequence_rr.metadata["processing_steps"][0]["reference_joint_label"] == "Head"
        assert sequence_rr.metadata["processing_steps"][0]["place_at_zero"] == True

    def test_trim(self):
        sequence = Sequence("test_sequences/test_sequence_7.tsv", time_unit="s", verbosity=0)
        sequence_t = sequence.trim(0, 10, verbosity=0)
        assert sequence_t.get_number_of_poses() == 11

        sequence = Sequence("test_sequences/test_sequence_7.tsv", time_unit="s", verbosity=0)
        sequence_t = sequence.trim(0, 10.5, verbosity=0)
        assert sequence_t.get_number_of_poses() == 11

        sequence = Sequence("test_sequences/test_sequence_7.tsv", time_unit="ms", verbosity=0)
        sequence_t = sequence.trim(0, 0.010, verbosity=0)
        assert sequence_t.get_number_of_poses() == 11

        sequence = Sequence("test_sequences/test_sequence_7.tsv", time_unit="s", verbosity=0)
        sequence_t = sequence.trim(-10, 100, verbosity=0)
        assert sequence_t.get_number_of_poses() == 16

        sequence = Sequence("test_sequences/test_sequence_8.tsv", time_unit="s", verbosity=0)
        sequence_t = sequence.trim(0, 0.1, True, verbosity=0)
        assert sequence_t.get_number_of_poses() == 2

        assert sequence_t.get_path() == sequence.get_path()
        assert sequence_t.get_date_recording() == sequence.get_date_recording()
        assert sequence_t.get_condition() == sequence.get_condition()
        assert sequence_t.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_t.get_system() == sequence.get_system()
        assert sequence_t.get_name() == "test_sequence_8 +TR"

        assert sequence_t.metadata["processing_steps"][0]["processing_type"] == "trim"
        assert sequence_t.metadata["processing_steps"][0]["start"] == 0
        assert sequence_t.metadata["processing_steps"][0]["end"] == 0.1
        assert sequence_t.metadata["processing_steps"][0]["use_relative_timestamps"] == True

        self.assertRaises(Exception, sequence.trim, 0.1, 0, verbosity=0)

        # No processing test
        sequence_t = sequence.trim(verbosity=0)
        assert sequence_t == sequence

    def test_trim_to_audio(self):
        sequence = Sequence("test_sequences/test_sequence_11.tsv", time_unit="s", verbosity=0)
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        sequence_ta = sequence.trim_to_audio(0, audio, verbosity=0)
        assert sequence_ta.get_number_of_poses() == 5
        assert sequence_ta.poses[0].joints["Head"].get_position() == (0, 0, 0)

        sequence_ta = sequence.trim_to_audio(0.5, audio, verbosity=0)
        assert sequence_ta.get_number_of_poses() == 5
        assert sequence_ta.poses[0].joints["Head"].get_position() == (16, 16, 8)

        sequence_ta = sequence.trim_to_audio(0.55, audio, verbosity=0)
        assert sequence_ta.get_number_of_poses() == 5
        assert sequence_ta.poses[0].joints["Head"].get_position() == (20, 20, 10)

        assert sequence_ta.get_path() == sequence.get_path()
        assert sequence_ta.get_date_recording() == sequence.get_date_recording()
        assert sequence_ta.get_condition() == sequence.get_condition()
        assert sequence_ta.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_ta.get_system() == sequence.get_system()
        assert sequence_ta.get_name() == "test_sequence_11 +TR"

        assert sequence_ta.metadata["processing_steps"][0]["processing_type"] == "trim"
        assert sequence_ta.metadata["processing_steps"][0]["start"] == 0.55
        assert np.isclose(sequence_ta.metadata["processing_steps"][0]["end"], 0.55 + 0.49997732426303854)
        assert sequence_ta.metadata["processing_steps"][0]["use_relative_timestamps"] == True

        self.assertRaises(Exception, sequence.trim_to_audio, 1.4, audio, verbosity=0)

    def test_filter_frequencies(self):
        sequence = Sequence("test_sequences/test_sequence_13.tsv", verbosity=0)
        sequence_ff = sequence.filter_frequencies(None, 4, verbosity=0)

        assert np.isclose(sequence_ff.poses[0].joints["Head"].get_x(), 0.01462934)
        assert np.isclose(sequence_ff.poses[1].joints["Head"].get_x(), 0.03923037)
        assert np.isclose(sequence_ff.poses[2].joints["Head"].get_x(), 0.24727853)
        assert np.isclose(sequence_ff.poses[3].joints["Head"].get_y(), -0.14039382)
        assert np.isclose(sequence_ff.poses[4].joints["Head"].get_z(), 0.45012674)

        assert sequence_ff.get_path() == sequence.get_path()
        assert sequence_ff.get_date_recording() == sequence.get_date_recording()
        assert sequence_ff.get_condition() == sequence.get_condition()
        assert sequence_ff.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_ff.get_system() == sequence.get_system()
        assert sequence_ff.get_name() == "test_sequence_13 +FF"

        assert sequence_ff.metadata["processing_steps"][0]["processing_type"] == "filter_frequencies"
        assert sequence_ff.metadata["processing_steps"][0]["filter_below"] is None
        assert sequence_ff.metadata["processing_steps"][0]["filter_over"] == 4

        self.assertRaises(ValueError, sequence.filter_frequencies, None, 10, verbosity=0)
        self.assertRaises(ValueError, sequence.filter_frequencies, -5, 1, verbosity=0)

        # No processing test
        sequence_ff = sequence.filter_frequencies(verbosity=0)
        assert sequence_ff == sequence

    def test_resample(self):
        sequence = Sequence("test_sequences/test_sequence_11.tsv", verbosity=0)
        sequence_r = sequence.resample(5, "linear", verbosity=0)
        assert sequence_r.get_number_of_poses() == 8
        assert np.allclose(sequence_r.poses[0].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_r.poses[1].joints["Head"].get_position(), (6, 6, 3))
        assert np.allclose(sequence_r.poses[2].joints["Head"].get_position(), (14, 14, 7))
        assert np.allclose(sequence_r.poses[3].joints["Head"].get_position(), (20, 20, 10))
        assert np.isclose(sequence_r.poses[0].timestamp, 0)
        assert np.isclose(sequence_r.poses[1].timestamp, 0.2)
        assert np.isclose(sequence_r.poses[2].timestamp, 0.4)
        assert np.isclose(sequence_r.poses[3].timestamp, 0.6)

        sequence_r = sequence.resample(7, "linear", verbosity=0)
        assert np.allclose(sequence_r.poses[0].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_r.poses[1].joints["Head"].get_position(), (3.7142857, 3.7142857, 1.8571428))
        assert np.allclose(sequence_r.poses[2].joints["Head"].get_position(), (11.1428571, 11.1428571, 5.5714285))
        assert np.allclose(sequence_r.poses[3].joints["Head"].get_position(), (14.5714285, 14.5714285, 7.2857142))

        sequence_r = sequence.resample(7, "cubic", verbosity=0)
        assert np.allclose(sequence_r.poses[0].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_r.poses[1].joints["Head"].get_position(), (3.3331357, 3.3331357, 1.6665678))
        assert np.allclose(sequence_r.poses[2].joints["Head"].get_position(), (11.3201626, 11.3201626, 5.6600813))
        assert np.allclose(sequence_r.poses[3].joints["Head"].get_position(), (14.3726822, 14.3726822, 7.1863411))

        sequence_r = sequence.resample(7, "pchip", verbosity=0)
        assert np.allclose(sequence_r.poses[0].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_r.poses[1].joints["Head"].get_position(), (3.4437317, 3.4437317, 1.7218658))
        assert np.allclose(sequence_r.poses[2].joints["Head"].get_position(), (11.4367346, 11.4367346, 5.7183673))
        assert np.allclose(sequence_r.poses[3].joints["Head"].get_position(), (14.5325558, 14.5325558, 7.2662779))

        assert sequence_r.get_path() == sequence.get_path()
        assert sequence_r.get_date_recording() == sequence.get_date_recording()
        assert sequence_r.get_condition() == sequence.get_condition()
        assert sequence_r.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_r.get_system() == sequence.get_system()
        assert sequence_r.get_name() == "test_sequence_11 +RS7"

        assert sequence_r.metadata["processing_steps"][0]["processing_type"] == "resample"
        assert sequence_r.metadata["processing_steps"][0]["frequency"] == 7
        assert sequence_r.metadata["processing_steps"][0]["method"] == "pchip"

        # No processing test
        sequence_r = sequence.resample(10, "linear", verbosity=0)
        assert sequence_r == sequence

    def test_interpolate_missing_data(self):
        sequence = Sequence("test_sequences/test_sequence_15.tsv", verbosity=0)
        sequence_im = sequence.interpolate_missing_data("linear", verbosity=0)
        assert sequence_im.get_number_of_poses() == 21
        assert np.allclose(sequence_im.poses[0].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[1].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[2].joints["Head"].get_position(), (0.11, 0.11, 0.11))
        assert np.allclose(sequence_im.poses[9].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[15].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[16].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[17].joints["Head"].get_position(), (1.11, 1.11, 1.11))

        sequence_im = sequence.interpolate_missing_data("cubic", verbosity=0)
        assert sequence_im.get_number_of_poses() == 21
        assert np.allclose(sequence_im.poses[0].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[1].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[2].joints["Head"].get_position(), (0.11, 0.11, 0.11))
        assert np.allclose(sequence_im.poses[9].joints["Head"].get_position(), (0.1233733, 0.1233733, 0.1233733))
        assert np.allclose(sequence_im.poses[15].joints["Head"].get_position(), (1.1573822, 1.1573822, 1.1573822))
        assert np.allclose(sequence_im.poses[16].joints["Head"].get_position(), (1.1550869, 1.1550869, 1.1550869))
        assert np.allclose(sequence_im.poses[17].joints["Head"].get_position(), (1.1302481, 1.1302481, 1.1302481))

        sequence_im = sequence.interpolate_missing_data("pchip", verbosity=0)
        assert sequence_im.get_number_of_poses() == 21
        assert np.allclose(sequence_im.poses[0].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[1].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[2].joints["Head"].get_position(), (0.11, 0.11, 0.11))
        assert np.allclose(sequence_im.poses[9].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[15].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[16].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[17].joints["Head"].get_position(), (1.11, 1.11, 1.11))

        sequence_im = sequence.interpolate_missing_data("pchip", which=0, verbosity=0)
        assert sequence_im.get_number_of_poses() == 21
        assert np.allclose(sequence_im.poses[0].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[1].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[2].joints["Head"].get_position(), (0.11, 0.11, 0.11))
        assert np.allclose(sequence_im.poses[9].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[15].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[16].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[17].joints["Head"].get_position(), (1.11, 1.11, 1.11))

        sequence.poses[10].joints["Head"].set_to_none()
        self.assertRaises(TypeError, sequence.interpolate_missing_data, "linear", which=0, verbosity=0)
        self.assertRaises(ValueError, sequence.interpolate_missing_data, "pchip", which=0, verbosity=0)

        sequence_im = sequence.interpolate_missing_data("linear", which=None, verbosity=0)
        assert sequence_im.get_number_of_poses() == 21
        assert np.allclose(sequence_im.poses[0].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_im.poses[1].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[2].joints["Head"].get_position(), (0.11, 0.11, 0.11))
        assert np.allclose(sequence_im.poses[9].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_im.poses[15].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_im.poses[16].joints["Head"].get_position(), (0, 0, 0))
        assert np.allclose(sequence_im.poses[17].joints["Head"].get_position(), (0, 0, 0))

        sequence_im = sequence.interpolate_missing_data("linear", which="both", verbosity=0)
        assert sequence_im.get_number_of_poses() == 21
        assert np.allclose(sequence_im.poses[0].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[1].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[2].joints["Head"].get_position(), (0.11, 0.11, 0.11))
        assert np.allclose(sequence_im.poses[9].joints["Head"].get_position(), (0.1, 0.1, 0.1))
        assert np.allclose(sequence_im.poses[15].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[16].joints["Head"].get_position(), (1.11, 1.11, 1.11))
        assert np.allclose(sequence_im.poses[17].joints["Head"].get_position(), (1.11, 1.11, 1.11))

        assert sequence_im.get_path() == sequence.get_path()
        assert sequence_im.get_date_recording() == sequence.get_date_recording()
        assert sequence_im.get_condition() == sequence.get_condition()
        assert sequence_im.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_im.get_system() == sequence.get_system()
        assert sequence_im.get_name() == "test_sequence_15 +IM"

        assert sequence_im.metadata["processing_steps"][0]["processing_type"] == "interpolate_missing_data"
        assert sequence_im.metadata["processing_steps"][0]["method"] == "linear"
        assert sequence_im.metadata["processing_steps"][0]["which"] == "both"

        # No processing test
        sequence = Sequence("test_sequences/test_sequence_10.tsv", verbosity=0)
        sequence_im = sequence.interpolate_missing_data(verbosity=0)
        assert sequence_im == sequence

    def test_randomize(self):
        sequence = Sequence("test_sequences/test_sequence_15.tsv", verbosity=0)
        sequence_rd = sequence.randomize(verbosity=0)

        old_diff_x = sequence.poses[1].joints["Head"].get_x() - sequence.poses[0].joints["Head"].get_x()
        new_diff_x = sequence_rd.poses[1].joints["Head"].get_x() - sequence_rd.poses[0].joints["Head"].get_x()
        assert np.isclose(old_diff_x, new_diff_x)

        assert sequence_rd.get_path() == sequence.get_path()
        assert sequence_rd.get_date_recording() == sequence.get_date_recording()
        assert sequence_rd.get_condition() == sequence.get_condition()
        assert sequence_rd.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_rd.get_system() == sequence.get_system()
        assert sequence_rd.get_name() == "test_sequence_15 +RD"

        assert sequence_rd.metadata["processing_steps"][0]["processing_type"] == "randomize"
        assert sequence_rd.metadata["processing_steps"][0]["x_scale"] == 0.2
        assert sequence_rd.metadata["processing_steps"][0]["y_scale"] == 0.3
        assert sequence_rd.metadata["processing_steps"][0]["z_scale"] == 0.5

    def test_create_new_sequence_with_timestamps(self):
        sequence = Sequence("test_sequences/test_sequence_15.tsv", verbosity=0)
        sequence_blank = sequence._create_new_sequence_with_timestamps(verbosity=0)

        assert sequence_blank.get_joint_labels() == sequence.get_joint_labels()

        assert sequence_blank.get_number_of_poses() == 21
        assert sequence_blank.poses[0].joints["Head"] is None
        assert sequence_blank.poses[20].joints["Head"] is None

    def test_set_attributes_from_other_sequence(self):
        sequence = Sequence("test_sequences/test_sequence_15.tsv", verbosity=0)
        sequence_blank = sequence._create_new_sequence_with_timestamps(verbosity=0)
        sequence_blank._set_attributes_from_other_sequence(sequence)

        assert sequence_blank.get_path() == sequence.get_path()
        assert sequence_blank.get_condition() == sequence.get_condition()
        assert sequence_blank.get_system() == sequence.get_system()
        assert sequence_blank.dimensions == sequence.dimensions
        assert sequence_blank.is_randomized == sequence.is_randomized
        assert sequence_blank.get_date_recording() == sequence.get_date_recording()
        assert sequence_blank.metadata == sequence.metadata
        assert sequence_blank.time_unit == sequence.time_unit
        assert sequence_blank.get_joint_labels() == sequence.get_joint_labels()
        assert sequence_blank.get_name() == "Unnamed sequence"

    def test_to_table(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        table = sequence.to_table()
        assert table == [['Timestamp',
                          'Head_X', 'Head_Y', 'Head_Z',
                          'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                          'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                         [0.0, 0.160617024, 0.494735048, -0.453307693, 0.127963375, 0.873208589,
                          0.408531847, -1.395065714, 2.653738732, -0.483163821],
                         [0.001, 1.769412418, 0.885312165, -0.785718175, 0.948776526, 2.805260745,
                          2.846927978, -0.80645271, 1.460889453, 2.557279205],
                         [0.002, -1.678118013, 0.85064505, 1.37303521, -1.612589342, -0.059736892,
                          -1.456678185, -1.418789803, 0.283037432, -0.221482265]]

    def test_to_json(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        json_data = sequence.to_json()
        assert json_data == {'Number of poses': 3, 'Number of joints': 3, 'system': None, 'processing_steps': [],
                             'Poses': [{'Bodies':
                                            [{'Joints':
                                                  [{'JointType': 'Head', 'Position':
                                                      {'X': 0.160617024, 'Y': 0.494735048, 'Z': -0.453307693}},
                                                   {'JointType': 'HandRight', 'Position':
                                                       {'X': 0.127963375, 'Y': 0.873208589, 'Z': 0.408531847}},
                                                   {'JointType': 'HandLeft', 'Position':
                                                       {'X': -1.395065714, 'Y': 2.653738732, 'Z': -0.483163821}}]}],
                                        'Timestamp': 0.0},
                                       {'Bodies':
                                            [{'Joints':
                                                  [{'JointType': 'Head', 'Position':
                                                      {'X': 1.769412418, 'Y': 0.885312165, 'Z': -0.785718175}},
                                                   {'JointType': 'HandRight', 'Position':
                                                       {'X': 0.948776526, 'Y': 2.805260745, 'Z': 2.846927978}},
                                                   {'JointType': 'HandLeft', 'Position':
                                                       {'X': -0.80645271, 'Y': 1.460889453, 'Z': 2.557279205}}]}],
                                        'Timestamp': 0.001},
                                       {'Bodies':
                                            [{'Joints':
                                                  [{'JointType': 'Head', 'Position':
                                                      {'X': -1.678118013, 'Y': 0.85064505, 'Z': 1.37303521}},
                                                   {'JointType': 'HandRight', 'Position':
                                                       {'X': -1.612589342, 'Y': -0.059736892, 'Z': -1.456678185}},
                                                   {'JointType': 'HandLeft', 'Position':
                                                       {'X': -1.418789803, 'Y': 0.283037432, 'Z': -0.221482265}}]}],
                                        'Timestamp': 0.002}]}

    def test_to_dict(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        dict_data = sequence.to_dict()
        assert np.allclose(dict_data['Timestamp'], [0.0, 0.001, 0.002])
        assert np.allclose(dict_data['Head_X'], np.array([ 0.16061702,  1.76941242, -1.67811801]))
        assert np.allclose(dict_data['Head_Y'], np.array([0.49473505, 0.88531216, 0.85064505]))
        assert np.allclose(dict_data['Head_Z'], np.array([-0.45330769, -0.78571817,  1.37303521]))
        assert np.allclose(dict_data['HandRight_X'], np.array([ 0.12796337,  0.94877653, -1.61258934]))
        assert np.allclose(dict_data['HandRight_Y'], np.array([ 0.87320859,  2.80526075, -0.05973689]))
        assert np.allclose(dict_data['HandRight_Z'], np.array([ 0.40853185,  2.84692798, -1.45667818]))
        assert np.allclose(dict_data['HandLeft_X'], np.array([-1.39506571, -0.80645271, -1.4187898 ]))
        assert np.allclose(dict_data['HandLeft_Y'], np.array([2.65373873, 1.46088945, 0.28303743]))
        assert np.allclose(dict_data['HandLeft_Z'], np.array([-0.48316382,  2.5572792 , -0.22148227]))

    def test_to_dataframe(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        df_data = sequence.to_dataframe()

        dict_data = {'Timestamp': [0.0, 0.001, 0.002],
                     'Head_X': np.array([ 0.16061702,  1.76941242, -1.67811801]),
                     'Head_Y': np.array([0.49473505, 0.88531216, 0.85064505]),
                     'Head_Z': np.array([-0.45330769, -0.78571817,  1.37303521]),
                     'HandRight_X': np.array([ 0.12796337,  0.94877653, -1.61258934]),
                     'HandRight_Y': np.array([ 0.87320859,  2.80526075, -0.05973689]),
                     'HandRight_Z': np.array([ 0.40853185,  2.84692798, -1.45667818]),
                     'HandLeft_X': np.array([-1.39506571, -0.80645271, -1.4187898 ]),
                     'HandLeft_Y': np.array([2.65373873, 1.46088945, 0.28303743]),
                     'HandLeft_Z': np.array([-0.48316382,  2.5572792 , -0.22148227])}
        dict_data_df = pd.DataFrame(dict_data)

        assert np.allclose(df_data, dict_data_df)

    def test_to_analysis_dataframe(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_df = sequence.to_analysis_dataframe()
        assert sequence_df.shape == (9, 9)
        assert sequence_df["subject"].unique().tolist() == [None]
        assert sequence_df["group"].unique().tolist() == [None]
        assert sequence_df["trial"].unique().tolist() == [None]
        assert sequence_df["condition"].unique().tolist() == [None]
        assert sequence_df["modality"].unique().tolist() == ["mocap"]
        assert sequence_df["label"].unique().tolist() == ["Head", "HandRight", "HandLeft"]
        assert sequence_df["measure"].unique().tolist() == ["velocity"]
        assert sequence_df.iloc[2]["timestamp"] == 0.002
        assert np.isclose(sequence_df.iloc[2]["value"], 72.945852)

        sequence = Sequence("test_sequences/test_sequence_2.tsv", condition="masked", verbosity=0)
        sequence.word = "first"
        sequence_df = sequence.to_analysis_dataframe(subject="S001")
        pd.set_option("display.max_columns", None)
        print(sequence_df)
        assert sequence_df.shape == (9, 9)
        assert sequence_df["subject"].unique().tolist() == ["S001"]
        assert sequence_df["group"].unique().tolist() == [None]
        assert sequence_df["trial"].unique().tolist() == [None]
        assert sequence_df["condition"].unique().tolist() == ["masked"]
        assert sequence_df["modality"].unique().tolist() == ["mocap"]
        assert sequence_df["label"].unique().tolist() == ["Head", "HandRight", "HandLeft"]
        assert sequence_df["measure"].unique().tolist() == ["velocity"]
        assert sequence_df.iloc[2]["timestamp"] == 0.002
        assert np.isclose(sequence_df.iloc[2]["value"], 103.038456)

    def test_average_qualisys_to_kinect(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        self.assertRaises(Exception, sequence.average_qualisys_to_kinect, verbosity=0)

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        sequence_avg = sequence.average_qualisys_to_kinect(verbosity=0)

        assert len(sequence_avg.joint_labels) == 59
        assert np.isclose(sequence_avg.poses[0].joints["HeadTop"].get_x(), -0.43288499999999996)
        assert np.isclose(sequence_avg.poses[0].joints["HeadFront"].get_x(), -0.42424)
        assert np.isclose(sequence_avg.poses[0].joints["HeadLeft"].get_x(), -0.36223099999999997)
        assert np.isclose(sequence_avg.poses[0].joints["HeadRight"].get_x(),-0.530575)
        assert np.isclose(sequence_avg.poses[0].joints["Head"].get_x(), -0.43748275)

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        sequence_avg = sequence.average_qualisys_to_kinect(remove_non_kinect_joints=True, verbosity=0)
        assert len(sequence_avg.joint_labels) == 21
        assert np.isclose(sequence_avg.poses[0].joints["Head"].get_x(), -0.43748275)

        sequence = Sequence("test_sequences/test_sequence_qtm_2.tsv", verbosity=0)
        sequence_avg = sequence.average_qualisys_to_kinect(joints_labels_to_exclude=["Neck"], verbosity=0)
        assert len(sequence_avg.joint_labels) == 58

    def test_average_joints(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert len(sequence.joint_labels) == 3
        sequence.average_joints(["HandRight", "HandLeft"], "HandAverage", False, 0)
        assert len(sequence.joint_labels) == 4
        assert np.isclose(sequence.poses[0].joints["HandRight"].x, 0.12796337)
        assert np.isclose(sequence.poses[0].joints["HandLeft"].x, -1.39506571)
        assert np.isclose(sequence.poses[0].joints["HandAverage"].x, (-1.39506571 + 0.12796337) / 2)

        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence.average_joints(["HandRight", "HandLeft"], "HandAverage", True, 0)
        assert len(sequence.joint_labels) == 2

    def test_concatenate(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=0)
        sequence_2 = Sequence("test_sequences/test_sequence_2.tsv", time_unit="s", verbosity=0)
        sequence_3 = sequence_1.concatenate(sequence_2)
        assert sequence_3.get_number_of_poses() == 6
        assert np.allclose(sequence_3.get_timestamps(), [0, 1, 2, 3, 4, 5])
        assert sequence_3.get_name() == "test_sequence_1 test_sequence_2"

    def test_copy(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        copy_sequence = sequence.copy()
        assert id(sequence) != id(copy_sequence)
        assert id(sequence.get_pose(0)) != id(copy_sequence.get_pose(0))
        assert id(sequence.get_pose(0).get_joint("Head")) != id(copy_sequence.get_pose(0).get_joint("Head"))
        assert sequence.get_pose(0) == copy_sequence.get_pose(0)
        assert sequence.get_pose(0).get_joint("Head") == copy_sequence.get_pose(0).get_joint("Head")

    def test_print_all(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence.print_all(True)

    def test_save(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_2 = Sequence("test_sequences/test_sequence_13.tsv", verbosity=0)

        # folder/name/file_format, include metadata
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "json", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "mat", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "xlsx", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "pkl", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "txt", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "csv", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "tsv", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/", "test_sequence_1", "aaa", verbosity=0)

        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "json", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "mat", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "xlsx", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "pkl", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "txt", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "csv", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "tsv", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/", "test_sequence_2", "aaa", verbosity=0)

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.pkl", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()
        
        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.json", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.mat", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.xlsx", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.pkl", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.txt", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.tsv", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.csv", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.aaa", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        # everything in folder, include metadata
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.pkl", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)

        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.json", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.mat", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.xlsx", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.pkl", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.txt", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.csv", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.tsv", verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.aaa", verbosity=0)

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.pkl", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.json", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.mat", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.xlsx", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.pkl", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.txt", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.tsv", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.csv", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.aaa", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()
        
        # everything in folder, omit metadata
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.json", include_metadata=False, verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.mat", include_metadata=False, verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.xlsx", include_metadata=False, verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.pkl", include_metadata=False, verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.txt", include_metadata=False, verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.csv", include_metadata=False, verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.tsv", include_metadata=False, verbosity=0)
        sequence_1.save("test_sequences/saved_sequences/test_sequence_1.aaa", include_metadata=False, verbosity=0)

        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.json", include_metadata=False, verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.mat", include_metadata=False, verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.xlsx", include_metadata=False, verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.pkl", include_metadata=False, verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.txt", include_metadata=False, verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.csv", include_metadata=False, verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.tsv", include_metadata=False, verbosity=0)
        sequence_2.save("test_sequences/saved_sequences/test_sequence_2.aaa", include_metadata=False, verbosity=0)

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.pkl", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.json", verbosity=0)
        assert sequence_2 == sequence_2s
        assert len(sequence_2s.metadata.keys()) == 2
        assert "system" in sequence_2s.metadata.keys()
        assert "processing_steps" in sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.mat", verbosity=0)
        assert sequence_2 == sequence_2s
        assert len(sequence_2s.metadata.keys()) == 2
        assert "system" in sequence_2s.metadata.keys()
        assert "processing_steps" in sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.xlsx", verbosity=0)
        assert sequence_2 == sequence_2s
        assert len(sequence_2s.metadata.keys()) == 2
        assert "system" in sequence_2s.metadata.keys()
        assert "processing_steps" in sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.pkl", verbosity=0)
        assert sequence_2 == sequence_2s
        assert sequence_2.metadata.keys() == sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.txt", verbosity=0)
        assert sequence_2 == sequence_2s
        assert len(sequence_2s.metadata.keys()) == 2
        assert "system" in sequence_2s.metadata.keys()
        assert "processing_steps" in sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.tsv", verbosity=0)
        assert sequence_2 == sequence_2s
        assert len(sequence_2s.metadata.keys()) == 2
        assert "system" in sequence_2s.metadata.keys()
        assert "processing_steps" in sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.csv", verbosity=0)
        assert sequence_2 == sequence_2s
        assert len(sequence_2s.metadata.keys()) == 2
        assert "system" in sequence_2s.metadata.keys()
        assert "processing_steps" in sequence_2s.metadata.keys()

        sequence_2s = Sequence("test_sequences/saved_sequences/test_sequence_2.aaa", verbosity=0)
        assert sequence_2 == sequence_2s
        assert len(sequence_2s.metadata.keys()) == 2
        assert "system" in sequence_2s.metadata.keys()
        assert "processing_steps" in sequence_2s.metadata.keys()

    def test_save_stats(self):
        sequence = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        sequence.save_info("test_sequences/test_saved_stats/test_stats_sequence_7.json", verbosity=0)
        sequence.save_info("test_sequences/test_saved_stats/test_stats_sequence_7.mat", verbosity=0)
        sequence.save_info("test_sequences/test_saved_stats/test_stats_sequence_7.xlsx", verbosity=0)
        sequence.save_info("test_sequences/test_saved_stats/test_stats_sequence_7.csv", verbosity=0)
        sequence.save_info("test_sequences/test_saved_stats/test_stats_sequence_7.txt", verbosity=0)
        sequence.save_info("test_sequences/test_saved_stats/test_stats_sequence_7.tsv", verbosity=0)
        sequence.save_info("test_sequences/test_saved_stats/test_stats_sequence_7.aaa", verbosity=0)

    def test_save_json(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)

        sequence_1.save_json("test_sequences/saved_sequences/", "test_sequence_1", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_json("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_json("test_sequences/saved_sequences/", "test_sequence_1", include_metadata=False,
                             verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.json", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

    def test_save_mat(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)

        sequence_1.save_mat("test_sequences/saved_sequences/", "test_sequence_1", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_mat("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_mat("test_sequences/saved_sequences/", "test_sequence_1", include_metadata=False,
                             verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.mat", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

    def test_save_excel(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)

        sequence_1.save_excel("test_sequences/saved_sequences/", "test_sequence_1", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_excel("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_excel("test_sequences/saved_sequences/", "test_sequence_1", include_metadata=False,
                             verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.xlsx", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

    def test_save_pickle(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)

        sequence_1.save_pickle("test_sequences/saved_sequences/", "test_sequence_1", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.pkl", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_pickle("test_sequences/saved_sequences/test_sequence_1.pkl", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.pkl", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

    def test_save_txt(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)

        # Text file
        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "txt", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "txt",
                            include_metadata=False, verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.txt", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        # TSV file
        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "tsv", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "tsv",
                            include_metadata=False, verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        # CSV file
        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "csv", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "csv",
                            include_metadata=False, verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.csv", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()

        # AAA file
        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "aaa", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)
        assert sequence_1 == sequence_1s
        assert sequence_1.metadata.keys() == sequence_1s.metadata.keys()

        sequence_1.save_txt("test_sequences/saved_sequences/", "test_sequence_1", "aaa",
                            include_metadata=False, verbosity=0)
        sequence_1s = Sequence("test_sequences/saved_sequences/test_sequence_1.aaa", verbosity=0)
        assert sequence_1 == sequence_1s
        assert len(sequence_1s.metadata.keys()) == 2
        assert "system" in sequence_1s.metadata.keys()
        assert "processing_steps" in sequence_1s.metadata.keys()
        
    def test_len(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert len(sequence) == 3

        sequence = Sequence(verbosity=0)
        assert len(sequence) == 0

    def test_getitem(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert sequence[0] == sequence.get_pose(0)
        assert sequence[0].joints == sequence.get_pose(0).joints

    def test_repr(self):
        sequence = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        assert repr(sequence) == sequence.name

        sequence = Sequence("test_sequences/test_sequence_1.tsv", name="seq22", verbosity=0)
        assert repr(sequence) == sequence.name
    
    def test_eq(self):
        sequence_1 = Sequence("test_sequences/test_sequence_6.tsv", verbosity=0)

        sequence_2 = Sequence()
        pose = Pose(0)
        pose.add_joint(Joint("Head", -2.819374393, -1.881188978, 0.412664491))
        pose.add_joint(Joint("HandRight", 1.445902298, 1.033955007, 2.049614771))
        pose.add_joint(Joint("HandLeft", 2.706231532, -0.22258201, -1.291594811))
        sequence_2.add_pose(pose, verbosity=0)

        assert sequence_1 == sequence_2