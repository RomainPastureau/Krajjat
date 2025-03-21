"""Tests the plot functions from the toolbox."""

import unittest

from krajjat.classes.audio import Audio
from krajjat.classes.sequence import Sequence
from krajjat.plot_functions import *


class TestsPlotFunctions(unittest.TestCase):

    def test_single_joint_movement_plotter(self):
        # pass
        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        print(sequence.get_timestamps())
        # sequence_trimmed = sequence.trim(11.1284139, verbosity=0)
        sequence_r = sequence.resample(20)
        single_joint_movement_plotter(sequence_r, joint_label="HandRight", measures=["v", "a", "j"], verbosity=0)

        sequence_rs = sequence.resample(20, "cubic", verbosity=0)
        sequence_cj = sequence.correct_jitter(1, 5, "poses", verbosity=0)
        sequence_rs_cj = sequence_cj.resample(20, "cubic", verbosity=0)

        single_joint_movement_plotter(sequence_rs, joint_label="HandRight", measures="default", verbosity=0)

        single_joint_movement_plotter(sequence_rs, joint_label="HandRight", measures=["x", "y", "z"], verbosity=0)

        single_joint_movement_plotter(sequence_rs, joint_label="HandRight", measures=["velocity_abs"], verbosity=0)

        single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                      measures=["d", "v", "a", "j"], verbosity=0)

        single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                      measures=["d", "v", "a", "j"], verbosity=0)

        single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                      measures=["d", "v", "a", "j"], domain="frequency", verbosity=0)

        single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                      measures=["d", "v", "a", "j"], domain="frequency", timestamp_start=1,
                                      timestamp_end=2, ylim=[[0, 4e-5], [0, 0.003], [0, 0.35], [0, 50]], line_width=2,
                                      line_color=["bcbl blue", "bcbl dark blue"], verbosity=0)

    def test_joint_movement_plotter(self):
        pass
        # sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        # sequence_rs = sequence.resample(20, "cubic", verbosity=0)
        # sequence_t = sequence_rs.trim(11.1284139, verbosity=0)
        # sequence_t.set_first_timestamp(0)
        # sequence_cj = sequence.correct_jitter(1, 5, "poses", verbosity=0)
        # sequence_rs_cj = sequence_cj.resample(20, "cubic", verbosity=0)
        # audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)
        #
        #
        # joints_movement_plotter(sequence_rs, measure="velocity", domain="time", verbosity=0)
        # joints_movement_plotter(sequence_rs, measure="velocity_abs", domain="time", verbosity=0)
        # joints_movement_plotter([sequence_rs, sequence_rs_cj], measure="velocity_abs", domain="time", verbosity=0)
        # joints_movement_plotter(sequence_rs, measure="velocity", domain="frequency", xlim=[1, 3], ylim=[0, 0.004],
        #                         verbosity=0)
        # joints_movement_plotter(sequence_rs, measure="velocity_abs", domain="frequency", verbosity=0)
        # joints_movement_plotter(sequence_t, measure="velocity", domain="time", audio_or_derivative=audio,
        #                         overlay_audio=True, verbosity=0)
        # joints_movement_plotter(sequence_t, measure="velocity_abs", domain="time", audio_or_derivative=audio,
        #                         overlay_audio=True, verbosity=0)

    def test_framerate_plotter(self):
        pass
        # sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        # framerate_plotter(sequence)
        # sequence_rs = sequence.resample(20, "cubic", verbosity=0)
        # framerate_plotter(sequence_rs)
        # framerate_plotter([sequence, sequence_rs])

    def test_audio_plotter(self):
        pass
        # audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)
        # audio_plotter(audio, filter_over=50, verbosity=1)

    def test_plot_body_graphs(self):
        pass
        # plot_dictionary = {}
        # plot_dictionary["Head"] = Graph()
        # plot_dictionary["Head"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "red", "x=y")
        # plot_dictionary["HandRight"] = Graph()
        # plot_dictionary["HandRight"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "green", "x=y")
        # plot_dictionary["HandLeft"] = Graph()
        # plot_dictionary["HandLeft"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "blue", "x=y")
        # plot_dictionary["HandLeft"].add_plot(np.linspace(0, 10, 11), np.linspace(10, 0, 11), None, 2, "orange", "y=x")
        #
        # plot_body_graphs(plot_dictionary, joint_layout="auto")
        #
        # plot_body_graphs(plot_dictionary, joint_layout="auto", title="Graph", min_scale=-10, max_scale=7,
        #                  show_scale=True, title_scale="Scale", x_lim=[-1, 15])

    def test_plot_silhouette(self):
        pass
        # plot_dictionary = {"Head": 0.1, "HandRight": 0.48, "HandLeft": 0.88}
        # plot_silhouette(plot_dictionary, joint_layout="auto", title="Coherence", min_scale=0, max_scale=1,
        #                 show_scale=True, title_scale="Coherence scale (A.U.)", color_scheme="horizon",
        #                 color_background="black", color_silhouette="#303030", verbosity=0)

    def test_plot_components(self):
        pass

    def test_prepare_plot_timestamps(self):
        pass

    def test_calculate_plot_limits(self):
        pass
