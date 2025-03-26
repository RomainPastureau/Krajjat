"""Tests the display functions from the toolbox."""

import unittest
from krajjat.display_functions import *


class TestsDisplayFunctions(unittest.TestCase):

    def test_common_displayer(self):
        pass
        sequence_kinect = Sequence(op.join("test_sequences", "sequence_ainhoa.json"))
        sequence_kinect_t = sequence_kinect.trim(11.1284139)
        path_audio = op.join("test_audios", "audio_ainhoa_trimmed.wav")
        path_video = op.join("test_videos", "video_ainhoa.mp4")
        common_displayer(sequence_kinect_t, path_audio=path_audio, path_video=path_video)
        common_displayer(sequence_kinect_t, path_audio=path_audio, path_video=path_video)
        # find_delay(op.join("test_sequences", "audio_ainhoa.wav"), op.join("test_sequences", "audio_ainhoa_trimmed.wav"))

    def test_sequence_reader(self):
        pass
        # sequence_kinect = Sequence(op.join("test_sequences", "sequence_ainhoa.json"))
        # sequence_kinect_t = sequence_kinect.trim(11.1284139)
        # path_audio = op.join("test_sequences", "audio_ainhoa_trimmed.wav")
        # path_video = op.join("test_sequences", "video_ainhoa.mp4")
        # sequence_reader(sequence_kinect_t, path_audio=path_audio, path_video=path_video, position_video="side",
        #                 ignore_bottom=True, show_lines=True, color_background="dark blue", color_joint="yellow",
        #                 width_line=2, size_joint_default=10, size_joint_hand=15, size_joint_head=15, font_color="black")

    def test_sequence_comparer(self):
        pass
        # sequence_kinect = Sequence(op.join("test_sequences", "sequence_ainhoa.json"))
        # sequence_kinect_t = sequence_kinect.trim(11.1284139)

        # print(sequence_kinect_t.get_pose(122).get_timestamp())
        # print(sequence_kinect_t.get_pose(123).get_timestamp())
        # print(sequence_kinect_t.get_pose(124).get_timestamp())
        # print(sequence_kinect_t.get_pose(125).get_timestamp())
        # print(sequence_kinect_t.get_pose(126).get_timestamp())
        # print(sequence_kinect_t.get_pose(127).get_timestamp())
        #
        # print(sequence_kinect_t.get_pose(122).joints["WristLeft"].get_position())
        # print(sequence_kinect_t.get_pose(123).joints["WristLeft"].get_position())
        # print(sequence_kinect_t.get_pose(124).joints["WristLeft"].get_position())
        # print(sequence_kinect_t.get_pose(125).joints["WristLeft"].get_position())
        # print(sequence_kinect_t.get_pose(126).joints["WristLeft"].get_position())
        # print(sequence_kinect_t.get_pose(127).joints["WristLeft"].get_position())
        #
        # print(calculate_distance(sequence_kinect_t.get_pose(122)["WristLeft"], sequence_kinect_t.get_pose(123)["WristLeft"]) / calculate_delay(sequence_kinect_t.get_pose(122), sequence_kinect_t.get_pose(123)))
        # print(calculate_distance(sequence_kinect_t.get_pose(123)["WristLeft"], sequence_kinect_t.get_pose(124)["WristLeft"]) / calculate_delay(sequence_kinect_t.get_pose(123), sequence_kinect_t.get_pose(124)))
        # print(calculate_distance(sequence_kinect_t.get_pose(124)["WristLeft"], sequence_kinect_t.get_pose(125)["WristLeft"]) / calculate_delay(sequence_kinect_t.get_pose(124), sequence_kinect_t.get_pose(125)))
        # print(calculate_distance(sequence_kinect_t.get_pose(125)["WristLeft"], sequence_kinect_t.get_pose(126)["WristLeft"]) / calculate_delay(sequence_kinect_t.get_pose(125), sequence_kinect_t.get_pose(126)))
        # print(calculate_distance(sequence_kinect_t.get_pose(126)["WristLeft"], sequence_kinect_t.get_pose(127)["WristLeft"]) / calculate_delay(sequence_kinect_t.get_pose(126), sequence_kinect_t.get_pose(127)))

        # sequence_kinect_cj = sequence_kinect_t.correct_jitter(1, 0.25, "s")
        # sequence_kinect_rs = sequence_kinect_cj.resample(20, "cubic")
        #
        # path_audio = op.join("test_sequences", "audio_ainhoa_trimmed.wav")
        # path_video = op.join("test_sequences", "video_ainhoa.mp4")
        # sequence_comparer(sequence_kinect_t, sequence_kinect_rs, path_audio=path_audio, path_video=path_video,
        #                   font_color="black")

    def test_pose_reader(self):
        pass
        # sequence_kinect = Sequence(op.join("test_sequences", "sequence_ainhoa.json"))
        # sequence_kinect_t = sequence_kinect.trim(11.1284139)
        #
        # path_audio = op.join("test_sequences", "audio_ainhoa_trimmed.wav")
        # path_video = op.join("test_sequences", "video_ainhoa.mp4")
        # pose_reader(sequence_kinect_t, 124, path_audio=path_audio, path_video=path_video, font_color="black",
        # zoom_level=1.4, shift=(-195, -107))

    def test_process_events(self):
        # See the other test functions
        pass

    def test_save_video_sequence(self):
        pass
        # sequence_kinect = Sequence(op.join("test_sequences", "sequence_ainhoa.json"))
        # sequence_kinect_t = sequence_kinect.trim(11.1284139)
        #
        # path_audio = op.join("test_sequences", "audio_ainhoa_trimmed.wav")
        # path_video = op.join("test_sequences", "video_ainhoa.mp4")
        # save_video_sequence(sequence_kinect_t, "test_videos/test_video_ainhoa.mp4", path_audio=path_audio,
        #                     path_video=path_video, font_color="black", zoom_level=1.4, shift=(-195, -107),
        #                     verbosity=2)
