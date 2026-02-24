"""Tests the Analysis functions from the toolbox."""

import unittest

from krajjat import Experiment, Subject, Trial, Sequence, Audio, Envelope
from krajjat.analysis_functions import *
import os.path as op

from krajjat.display_functions import common_displayer


class TestsAnalysisFunctions(unittest.TestCase):

    def test_power_spectrum(self):
        pass
        # sequence = Sequence("test_sequences/sequence_ainhoa_trimmed.tsv", verbosity=0)
        # audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)
        # sequence_cj = sequence.correct_jitter(1, 0.25, "s", verbosity=0)
        # sequence_rs = sequence_cj.resample(20, "cubic", verbosity=0)
        # sequence_t = sequence_rs.trim_to_audio(0, audio, verbosity=0)
        #
        # envelope = audio.get_envelope(filter_over=50, verbosity=0)
        # envelope_rs = envelope.resample(20, "cubic", verbosity=0)
        #
        # experiment = Experiment("Test Experiment 1")
        # subject = Subject("Ainhoa", None, "F", 42)
        # trial = Trial("R001")
        # trial.set_sequence(sequence_t)
        # trial.set_audio(envelope_rs)
        # subject.add_trial(trial, verbosity=0)
        # experiment.add_subject(subject)
        #
        # df_ve = experiment.get_dataframe("velocity", "envelope")
        # df_ae = experiment.get_dataframe("acceleration", "envelope")
        #
        # sequence = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        # audio = Audio("test_audios/test_audio_1.tsv", verbosity=0)
        # sequence_cj = sequence.correct_jitter(1, 0.25, "s", verbosity=0)
        # sequence_rs = sequence_cj.resample(20, "cubic", verbosity=0)
        # sequence_t = sequence_rs.trim_to_audio(0, audio, verbosity=0)
        #
        # pitch = audio.get_pitch(filter_over=50, verbosity=0)
        # pitch_rs = pitch.resample(20, "cubic", verbosity=0)
        #
        # experiment = Experiment("Test Experiment 1")
        # subject = Subject("Ainhoa", None, "F", 42)
        # trial = Trial("R001")
        # trial.set_sequence(sequence_t)
        # trial.set_audio(pitch_rs)
        # subject.add_trial(trial, verbosity=0)
        # experiment.add_subject(subject)
        #
        # df_vp = experiment.get_dataframe("velocity", "pitch")
        # df_ap = experiment.get_dataframe("acceleration", "pitch")
        #
        # df = pd.concat([df_ve, df_ae, df_vp, df_ap], ignore_index=True)
        # df = df.drop_duplicates()
        #
        # # power_spectrum(df, method="fft", specific_frequency=[0.5, 1.5], freq_atol=1e2,
        # #                title_silhouette=["0.5 Hz", "1.5 Hz"],
        # #                color_background="black", color_silhouette="#303030", title="Power spectrum")
        # df.to_excel("dataframe_ps.xlsx")
        # power_spectrum(df, sequence_measure="velocity", audio_measure="envelope", method="welch", include_audio=True)
        # power_spectrum(df, sequence_measure="acceleration", audio_measure="envelope", method="welch", include_audio=True)
        # power_spectrum(df, sequence_measure="velocity", audio_measure="pitch", method="welch", include_audio=True)
        # power_spectrum(df, sequence_measure="acceleration", audio_measure="pitch", method="welch", include_audio=True)

    def test_correlation(self):
        pass
        # experiment = Experiment("Test Experiment 1")
        # subject = Subject("Ainhoa", None, "F", 42)
        # trial = Trial("R001")
        # sequence = Sequence("test_sequences/sequence_ainhoa_trimmed.tsv", verbosity=0)
        # audio = Audio("test_audios/audio_ainhoa_trimmed.wav", verbosity=0)
        # sequence_cj = sequence.correct_jitter(1, 0.25, "s", verbosity=0)
        # sequence_rs = sequence_cj.resample(20, "cubic", verbosity=0)
        # sequence_t = sequence_rs.trim_to_audio(0, audio, verbosity=0)
        #
        # envelope = audio.get_envelope(filter_over=50, verbosity=0)
        # envelope_rs = envelope.resample(20, "cubic", verbosity=0)
        #
        # path_audio = op.join("test_audios", "audio_ainhoa_trimmed.wav")
        # path_video = op.join("test_videos", "video_ainhoa.mp4")
        #
        # trial.set_sequence(sequence_t)
        # trial.set_audio(envelope_rs)
        # subject.add_trial(trial, verbosity=0)
        # experiment.add_subject(subject)
        #
        # df = experiment.get_dataframe("velocity", "envelope")
        #
        # a, s, z, p = correlation(df, method="corr", include_randperm="whole", number_of_randperms=1000, random_seed=42,
        #                          verbosity=2)
        # print(z)
        # print(p)