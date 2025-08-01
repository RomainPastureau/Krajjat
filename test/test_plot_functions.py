"""Tests the plot functions from the toolbox."""

import unittest

from krajjat.classes.audio import Audio
from krajjat.classes.sequence import Sequence
from krajjat.plot_functions import *


class TestsPlotFunctions(unittest.TestCase):

    def test_single_joint_movement_plotter(self):
        show = False
        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        sequence_trimmed = sequence.trim(11.1284139, verbosity=0)
        figure = single_joint_movement_plotter([sequence, sequence_trimmed], joint_label="HandRight",
                                               measures=["x", "y", "z", "d"], show=show, verbosity=0)
        assert len(figure.axes) == 4
        assert np.allclose(figure.axes[0].get_xlim(), (0, 0.0009153169212962963))
        assert np.allclose(figure.axes[0].get_ylim(), (-0.10709512899999998, 0.587753949))
        figure.close()

        sequence_rs = sequence.resample(20, "cubic", verbosity=0)
        sequence_cj = sequence.correct_jitter(1, 5, "poses", verbosity=0)
        sequence_rs_cj = sequence_cj.resample(20, "cubic", verbosity=0)

        figure = single_joint_movement_plotter(sequence_rs, joint_label="HandRight", measures="default", show=show,
                                               verbosity=0)
        assert len(figure.axes) == 6
        figure.close()

        figure = single_joint_movement_plotter(sequence_rs, joint_label="HandRight", measures=["x", "y", "z"],
                                               show=show, verbosity=0)
        figure.close()

        figure = single_joint_movement_plotter(sequence_rs, joint_label="HandRight", measures=["velocity_abs"],
                                               show=show, verbosity=0)
        figure.close()

        figure = single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                               measures=["d", "v", "a", "j"], show=show, verbosity=0)
        figure.close()

        figure = single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                               measures=["d", "v", "a", "j"], show=show, verbosity=0)
        figure.close()

        figure = single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                               measures=["d", "v", "a", "j"], domain="frequency", nperseg=256,
                                               show=show, verbosity=0)
        figure.close()

        figure = single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                               measures=["d", "v", "a", "j"], domain="frequency", nperseg=256,
                                               welch_window="flattop", show=show, verbosity=0)
        figure.close()

        figure = single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                               measures=["d", "v", "a", "j"], domain="frequency", timestamp_start=1,
                                               timestamp_end=2, ylim=[[0, 4e-5], [0, 0.003], [0, 0.35], [0, 250]],
                                               line_width=2,
                                               line_color=["bcbl blue", "bcbl dark blue"], show=show, verbosity=0)

        assert len(figure.axes) == 4
        assert np.allclose(figure.axes[0].get_xlim(), (0, 10))
        assert np.allclose(figure.axes[0].get_ylim(), (0, 4e-5))
        figure.close()

        figure = single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                               measures=["d", "v", "a", "j"], domain="frequency", timestamp_start=1,
                                               timestamp_end=2, xlim=[0, 5], ylim=[0, 1], line_width=2,
                                               line_color=["bcbl blue", "bcbl dark blue"], show=show, verbosity=0)

        assert len(figure.axes) == 4
        assert np.allclose(figure.axes[0].get_xlim(), (0, 5))
        assert np.allclose(figure.axes[0].get_ylim(), (0, 1))
        figure.close()

        figure = single_joint_movement_plotter([sequence_rs, sequence_rs_cj], joint_label="HandRight",
                                               measures=["d", "v", "a", "j"], domain="time", timestamp_start=1,
                                               timestamp_end=2, line_width=2,
                                               line_color=["bcbl blue", "bcbl dark blue"],
                                               show=show, verbosity=0)

        assert len(figure.axes) == 4
        assert np.allclose(figure.axes[0].get_xlim(),
                           (1.1574074074074073e-05, 2.3148148148148147e-05))
        assert np.allclose(figure.axes[0].get_ylim(),
                           (-0.0002892237800528336, 0.016544788669802486))
        figure.close()

    def test_joint_movement_plotter(self):
        show = False
        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        sequence_rs = sequence.resample(20, "cubic", verbosity=0)
        sequence_t = sequence_rs.trim(11.1284139, verbosity=0)
        sequence_t.set_first_timestamp(0)
        sequence_cj = sequence.correct_jitter(1, 5, "poses", verbosity=0)
        sequence_rs_cj = sequence_cj.resample(20, "cubic", verbosity=0)
        audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)

        figure = joints_movement_plotter(sequence_rs, measure="velocity", domain="time", show=show, verbosity=0)
        assert len(figure.axes) == 21
        assert np.allclose(figure.axes[0].get_xlim(), (0, 79.05))
        assert np.allclose(figure.axes[0].get_ylim(), (-0.728253488317679, 0.7217512296715232))
        figure.close()

        figure = joints_movement_plotter(sequence_rs, measure="velocity", domain="time", timestamp_start=10,
                                         timestamp_end=20, ylim=[-1, 1], show=show, verbosity=0)
        assert len(figure.axes) == 21
        assert np.allclose(figure.axes[0].get_xlim(), (10, 20))
        assert np.allclose(figure.axes[0].get_ylim(), (-1, 1))
        figure.close()

        figure = joints_movement_plotter(sequence_rs, measure="velocity_abs", domain="time", show=show, verbosity=0)
        figure.close()

        figure = joints_movement_plotter([sequence_rs, sequence_rs_cj], measure="velocity_abs",
                                         domain="time", show=show, verbosity=0)
        figure.close()

        figure = joints_movement_plotter(sequence_rs, measure="velocity", domain="frequency", xlim=[1, 3],
                                         ylim=[0, 0.004], show=show, verbosity=0)
        figure.close()

        figure = joints_movement_plotter(sequence_rs, measure="velocity_abs", domain="frequency", show=show,
                                         verbosity=0)
        figure.close()

        figure = joints_movement_plotter(sequence_t, measure="velocity", domain="time", audio_or_derivative=audio,
                                         overlay_audio=True, show=show, verbosity=0)
        figure.close()

        figure = joints_movement_plotter(sequence_t, measure="velocity_abs", domain="time", audio_or_derivative=audio,
                                         overlay_audio=True, show=show, verbosity=0)
        figure.close()

    def test_framerate_plotter(self):
        show = False
        sequence = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        figure = framerate_plotter(sequence, show=False)
        figure.close()
        sequence_rs = sequence.resample(20, "cubic", verbosity=0)
        figure = framerate_plotter(sequence_rs, show=show)
        figure.close()
        figure = framerate_plotter([sequence, sequence_rs], show=show)
        figure.close()

    def test_audio_plotter(self):
        show = False
        # audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)
        # audio_plotter(audio, filter_over=50, show=show, verbosity=1)

    def test_plot_body_graphs(self):
        show = False
        plot_dictionary = {}
        plot_dictionary["Head"] = Graph()
        plot_dictionary["Head"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "red", "x=y")
        plot_dictionary["HandRight"] = Graph()
        plot_dictionary["HandRight"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "green", "x=y")
        plot_dictionary["HandLeft"] = Graph()
        plot_dictionary["HandLeft"].add_plot(np.linspace(0, 10, 11), np.linspace(0, 10, 11), None, 1, "blue", "x=y")
        plot_dictionary["HandLeft"].add_plot(np.linspace(0, 10, 11), np.linspace(10, 0, 11), None, 2, "orange", "y=x")

        figure = plot_body_graphs(plot_dictionary, joint_layout="auto", show=show, verbosity=0)
        figure.close()

        figure = plot_body_graphs(plot_dictionary, joint_layout="auto", title="Graph", min_scale=-10, max_scale=7,
                                  show_scale=True, title_scale="Scale", x_lim=[-1, 15], show=show, verbosity=0)
        figure.close()

    def test_plot_silhouette(self):
        show = True
        plot_dictionary = {"Head": 0.1, "HandRight": 0.48, "HandLeft": 0.88, "SpineShoulder": 0.28, "SpineMid": 0.54,
                           "SpineBase": 0.75, "ShoulderRight": 0.44, "ShoulderLeft": 0.23, "ElbowRight": 0.35,
                           "ElbowLeft": 0.65, "WristRight": 0.54, "WristLeft": 0.75, "HipRight": 0.65,
                           "HipLeft": 0.04, "KneeRight": 0.54, "KneeLeft": 0.75, "AnkleRight": 0.65, "AnkleLeft": 0.88,
                           "FootRight": 0.75, "FootLeft": 0.98, "Neck": 0.5}
        plot_silhouette(plot_dictionary, resolution=0.5, joint_layout="auto", title="Coherence", min_scale=0,
                        max_scale=1, title_silhouette="2 Hz", font_size=1, scale_silhouette=0.8,
                        show_scale=True, title_scale="Coherence scale (A.U.)", color_scheme="horizon",
                        color_background="black", color_silhouette="#303030", show=show, verbosity=0)

        plot_dictionary = {"Head": [0.1, 0.2], "HandRight": [0.48, 0.35], "HandLeft": [0.88, 0.75], "SpineMid": [
            np.nan, 0.5]}
        plot_silhouette(plot_dictionary, joint_layout="auto", title="Coherence", min_scale=0, max_scale=1,
                        title_silhouette=["Alpha", "Beta"], font_size=(1, 0.8, 0.5),
                        show_scale=True, title_scale="Coherence scale (A.U.)", color_scheme="horizon",
                        color_background="black", color_silhouette="#303030", show=show, verbosity=0)

        plot_dictionary = {"Head": [0.1, 0.2, 0.3], "HandRight": [0.48, 0.35, 0.54], "HandLeft": [0.88, 0.75, 0.2]}
        plot_silhouette(plot_dictionary, joint_layout="auto", title="Coherence", min_scale=0, max_scale=1,
                        title_silhouette=["0.5 Hz", "2.5 Hz", "4.5 Hz"],
                        show_scale=True, title_scale="Coherence scale (A.U.)", color_scheme="horizon",
                        color_background="black", color_silhouette="#303030", show=show, verbosity=0,
                        pixels_between_silhouettes=20)
