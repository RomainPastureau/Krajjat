"""Tests the Analysis functions from the toolbox."""

import unittest

from krajjat import Experiment, Subject, Trial, Sequence, Audio, Envelope
from krajjat.analysis_functions import *
import os.path as op

from krajjat.display_functions import common_displayer


class TestsAnalysisFunctions(unittest.TestCase):

    def test_power_spectrum(self):
        experiment = Experiment("Test Experiment 1")
        subject = Subject("Ainhoa", None, "F", 42)
        trial = Trial("R001")
        sequence = Sequence("test_sequences/sequence_ainhoa_trimmed.tsv", verbosity=0)
        audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)
        sequence_cj = sequence.correct_jitter(1, 0.25, "s", verbosity=0)
        sequence_rs = sequence_cj.resample(20, "cubic", verbosity=0)
        sequence_t = sequence_rs.trim_to_audio(0, audio, verbosity=0)

        envelope = audio.get_envelope(filter_over=50, verbosity=0)
        envelope_rs = envelope.resample(20, "cubic", verbosity=0)

        path_audio = op.join("test_audios", "audio_ainhoa_trimmed.wav")
        path_video = op.join("test_videos", "video_ainhoa.mp4")

        # common_displayer(sequence_t, path_audio=path_audio, path_video=path_video)

        trial.set_sequence(sequence_t)
        trial.set_audio(envelope_rs)
        subject.add_trial(trial, verbosity=0)
        experiment.add_subject(subject)

        df = experiment.get_dataframe("velocity", "envelope")

        power_spectrum(df, method="fft", specific_frequency=[0.5, 1.5], freq_atol=1e2,
                       title_silhouette=["0.5 Hz", "1.5 Hz"],
                       color_background="black", color_silhouette="#303030", title="Power spectrum")

    def test_correlation(self):
        experiment = Experiment("Test Experiment 1")
        subject = Subject("Ainhoa", None, "F", 42)
        trial = Trial("R001")
        sequence = Sequence("test_sequences/sequence_ainhoa_trimmed.tsv", verbosity=0)
        audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)
        sequence_cj = sequence.correct_jitter(1, 0.25, "s", verbosity=0)
        sequence_rs = sequence_cj.resample(20, "cubic", verbosity=0)
        sequence_t = sequence_rs.trim_to_audio(0, audio, verbosity=0)

        envelope = audio.get_envelope(filter_over=50, verbosity=0)
        envelope_rs = envelope.resample(20, "cubic", verbosity=0)

        path_audio = op.join("test_audios", "audio_ainhoa_trimmed.wav")
        path_video = op.join("test_videos", "video_ainhoa.mp4")

        trial.set_sequence(sequence_t)
        trial.set_audio(envelope_rs)
        subject.add_trial(trial, verbosity=0)
        experiment.add_subject(subject)

        df = experiment.get_dataframe("velocity", "envelope")

        a, s, z, p = correlation(df, method="corr", include_randperm="whole", number_of_randperms=1000, random_seed=42,
                                 verbosity=2)
        print(z)
        print(p)