"""Tests the Analysis functions from the toolbox."""

import unittest

from krajjat import Experiment, Subject, Trial, Sequence, Audio, Envelope
from krajjat.analysis_functions import *
import os.path as op

from krajjat.display_functions import common_displayer


class TestsAnalysisFunctions(unittest.TestCase):

    def test_power_spectrum(self):

        # Create a test signal
        def make_test_signal(duration=60, sampling_rate=30, peak_freqs=(2.0, 5.0),
                             peak_amplitudes=None, noise_slope=-2.0, snr=5.0, seed=42):
            rng = np.random.default_rng(seed)
            n_samples = int(duration * sampling_rate)
            t = np.arange(n_samples) / sampling_rate

            # 1/f noise via spectral shaping
            freqs = np.fft.rfftfreq(n_samples, d=1 / sampling_rate)
            freqs[0] = 1  # avoid division by zero at DC
            power = freqs ** (noise_slope / 2)
            phases = rng.uniform(0, 2 * np.pi, len(freqs))
            spectrum = power * np.exp(1j * phases)
            noise = np.fft.irfft(spectrum, n=n_samples)
            noise /= np.std(noise)  # normalise

            # Add sinusoidal peaks
            signal = noise.copy()
            noise_std = np.std(noise)
            for i, freq in enumerate(peak_freqs):
                if peak_amplitudes is not None:
                    amp = peak_amplitudes[i]
                else:
                    amp = snr * noise_std
                signal += amp * np.sin(2 * np.pi * freq * t)

            return t, signal

        # Create an experiment
        duration = 60
        sampling_rate = 30
        subject = "S001"
        trial = "T001"

        t, signal_head = make_test_signal(duration, sampling_rate, [2.0, 5.5], noise_slope=-2.0, snr=5.0)
        t, signal_hand_right = make_test_signal(duration, sampling_rate, [3.0, 4.5], noise_slope=-2.0, snr=5.0)
        t, signal_hand_left = make_test_signal(duration, sampling_rate, [1, 2, 3], noise_slope=-2.0, snr=5.0)
        t, signal_envelope = make_test_signal(duration, sampling_rate, [2.0, 5.5], noise_slope=-2.0, snr=5.0)

        rows = []
        for mocap_label, signal in [("Head", signal_head), ("HandRight", signal_hand_right), ("HandLeft", signal_hand_left)]:
            for timestamp, value in zip(t, signal):
                rows.append({"subject": subject, "trial": trial, "modality": "mocap", "label": mocap_label,
                             "measure": "velocity", "timestamp": timestamp, "value": value})

        for timestamp, value in zip(t, signal_envelope):
            rows.append({"subject": subject, "trial": trial, "modality": "audio", "label": "Audio",
                         "measure": "envelope", "timestamp": timestamp, "value": value})

        df = pd.DataFrame(rows)

        out = power_spectrum(df, method="welch", sequence_measure="velocity", audio_measure="envelope",
                             fit_background=True, signif_style="markers", include_audio=True,
                             joint_layout=[["Head", "HandRight"], ["HandLeft", "Audio"]], show=False)

        fit_head = out.background_fits["power spectrum"]["velocity"]["Full dataset"]["Head"][0]
        assert len(fit_head["peak_freqs"]) > 0, "Expected peaks in Head signal"
        for peak in fit_head["peak_freqs"]:
            assert any(abs(peak - target) < 0.5 for target in [2.0, 5.5]), f"Unexpected peak at {peak:.2f} Hz"

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