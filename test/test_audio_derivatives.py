"""Tests the Audio functions from the toolbox."""

import unittest
import os.path as op
import random

import numpy as np
from scipy.io import wavfile

from krajjat.classes.audio import Audio
from krajjat.classes.audio_derivatives import Envelope, Pitch, Intensity, Formant
from krajjat.classes.exceptions import InvalidPathException


class TestsAudioDerivatives(unittest.TestCase):

    def test_init(self):

        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]

        # Envelope
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        envelope = audio.get_envelope(filter_over=50, verbosity=0)
        envelope.save_pickle("test_envelopes/test_audio_1_envelope.pkl", verbosity=0)

        for ext in extensions:
            envelope = Envelope("test_envelopes/test_audio_1_envelope." + ext, verbosity=0)
            assert len(envelope.samples) == 22050
            assert np.isclose(envelope.samples[42], 767.4754693763366)
            assert envelope.frequency == 44100
            assert envelope.condition is None
            assert envelope.path == op.join("test_envelopes", "test_audio_1_envelope." + ext)
            assert envelope.files == ["test_audio_1_envelope." + ext]
            assert envelope.kind == "Envelope"
            assert envelope.name == "test_audio_1_envelope"
            assert envelope.timestamps[42] == 42 * 1/44100
            assert len(envelope.metadata) == 1
            assert len(envelope.metadata["processing_steps"]) == 2

        envelope = Envelope("test_envelopes/test_audio_4_envelope.xlsx", verbosity=0)
        assert len(envelope.samples) == 339
        assert np.isclose(envelope.samples[42], 1022.252396644028)
        assert envelope.frequency == 44100
        assert envelope.condition is None
        assert envelope.path == op.join("test_envelopes", "test_audio_4_envelope.xlsx")
        assert envelope.files == ["test_audio_4_envelope.xlsx"]
        assert envelope.kind == "Envelope"
        assert envelope.name == "test_audio_4_envelope"
        assert envelope.timestamps[42] == 42 * 1/44100
        assert len(envelope.metadata) == 1
        assert len(envelope.metadata["processing_steps"]) == 2

        # Pitch
        for ext in extensions:
            pitch = Pitch("test_pitches/test_audio_1_pitch." + ext, verbosity=0)
            assert len(pitch.samples) == 22050
            assert np.isclose(pitch.samples[10025], 197.32558113945146)
            assert pitch.frequency == 44100
            assert pitch.condition is None
            assert pitch.path == op.join("test_pitches", "test_audio_1_pitch." + ext)
            assert pitch.files == ["test_audio_1_pitch." + ext]
            assert pitch.kind == "Pitch"
            assert pitch.name == "test_audio_1_pitch"
            assert pitch.timestamps[42] == 42 * 1/44100
            assert len(pitch.metadata) == 1
            assert len(pitch.metadata["processing_steps"]) == 2

        pitch = Pitch("test_pitches/test_audio_4_pitch.xlsx", verbosity=0)
        assert len(pitch.samples) == 2206
        assert np.isclose(pitch.samples[1103], 73.47269061225556)
        assert pitch.frequency == 44100
        assert pitch.condition is None
        assert pitch.path == op.join("test_pitches", "test_audio_4_pitch.xlsx")
        assert pitch.files == ["test_audio_4_pitch.xlsx"]
        assert pitch.kind == "Pitch"
        assert pitch.name == "test_audio_4_pitch"
        assert pitch.timestamps[42] == 42 * 1/44100
        assert len(pitch.metadata) == 1
        assert len(pitch.metadata["processing_steps"]) == 3

        # Intensity
        for ext in extensions:
            intensity = Intensity("test_intensities/test_audio_1_intensity." + ext, verbosity=0)
            assert len(intensity.samples) == 22050
            assert np.isclose(intensity.samples[10025], 179.3480545298692)
            assert intensity.frequency == 44100
            assert intensity.condition is None
            assert intensity.path == op.join("test_intensities", "test_audio_1_intensity." + ext)
            assert intensity.files == ["test_audio_1_intensity." + ext]
            assert intensity.kind == "Intensity"
            assert intensity.name == "test_audio_1_intensity"
            assert intensity.timestamps[42] == 42 * 1/44100
            assert len(intensity.metadata) == 1
            assert len(intensity.metadata["processing_steps"]) == 2

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert len(intensity.samples) == 4411
        assert np.isclose(intensity.samples[2206], 183.9678676679894)
        assert intensity.frequency == 44100
        assert intensity.condition is None
        assert intensity.path == op.join("test_intensities", "test_audio_4_intensity.xlsx")
        assert intensity.files == ["test_audio_4_intensity.xlsx"]
        assert intensity.kind == "Intensity"
        assert intensity.name == "test_audio_4_intensity"
        assert intensity.timestamps[42] == 42 * 1/44100
        assert len(intensity.metadata) == 1
        assert len(intensity.metadata["processing_steps"]) == 3
        
        # F1
        for ext in extensions:
            formant = Formant("test_formants/test_audio_1_formant." + ext, verbosity=0)
            assert len(formant.samples) == 22050
            assert formant.formant_number == 1
            assert np.isclose(formant.samples[10025], 178.98487908)
            assert formant.frequency == 44100
            assert formant.condition is None
            assert formant.path == op.join("test_formants", "test_audio_1_formant." + ext)
            assert formant.files == ["test_audio_1_formant." + ext]
            assert formant.kind == "Formant"
            assert formant.name == "test_audio_1_formant"
            assert formant.timestamps[42] == 42 * 1/44100
            assert len(formant.metadata) == 2
            assert formant.metadata["formant_number"] == 1
            assert len(formant.metadata["processing_steps"]) == 2

        formant = Formant("test_formants/test_audio_4_formant.xlsx", verbosity=0)
        assert len(formant.samples) == 4411
        assert formant.formant_number == 1
        assert np.isclose(formant.samples[2206], 114.2607274528348)
        assert formant.frequency == 44100
        assert formant.condition is None
        assert formant.path == op.join("test_formants", "test_audio_4_formant.xlsx")
        assert formant.files == ["test_audio_4_formant.xlsx"]
        assert formant.kind == "Formant"
        assert formant.name == "test_audio_4_formant"
        assert formant.timestamps[42] == 42 * 1/44100
        assert len(formant.metadata) == 2
        assert formant.metadata["formant_number"] == 1
        assert len(formant.metadata["processing_steps"]) == 3

        # F2
        for ext in extensions:
            formant = Formant("test_formants/test_audio_1_f2." + ext, verbosity=0)
            assert len(formant.samples) == 22050
            assert formant.formant_number == 2
            assert np.isclose(formant.samples[10025], 246.1807372781575)
            assert formant.frequency == 44100
            assert formant.condition is None
            assert formant.path == op.join("test_formants", "test_audio_1_f2." + ext)
            assert formant.files == ["test_audio_1_f2." + ext]
            assert formant.kind == "Formant"
            assert formant.name == "test_audio_1_f2"
            assert formant.timestamps[42] == 42 * 1/44100
            assert len(formant.metadata) == 2
            assert formant.metadata["formant_number"] == 2
            assert len(formant.metadata["processing_steps"]) == 2

        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio_t = audio.trim(0, 0.1, verbosity=0)
        formant = audio_t.get_formant(formant_number=2, filter_over=50, verbosity=0)
        formant.save("test_formants/test_audio_4_f2.xlsx", verbosity=0)
        formant = Formant("test_formants/test_audio_4_f2.xlsx", verbosity=0)
        assert len(formant.samples) == 4411
        assert formant.formant_number == 2
        assert np.isclose(formant.samples[2206], 158.0678093872848)
        assert formant.frequency == 44100
        assert formant.condition is None
        assert formant.path == op.join("test_formants", "test_audio_4_f2.xlsx")
        assert formant.files == ["test_audio_4_f2.xlsx"]
        assert formant.kind == "Formant"
        assert formant.name == "test_audio_4_f2"
        assert formant.timestamps[42] == 42 * 1/44100
        assert len(formant.metadata) == 2
        assert formant.metadata["formant_number"] == 2
        assert len(formant.metadata["processing_steps"]) == 3

    def test_set_name(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.json", verbosity=0)
        pitch = Pitch("test_pitches/test_audio_1_pitch.txt", verbosity=0)
        intensity = Intensity("test_intensities/test_audio_1_intensity.mat", verbosity=0)
        formant = Formant("test_formants/test_audio_1_formant.pkl", verbosity=0)

        envelope.set_name("env_1")
        assert envelope.name == "env_1"
        pitch.set_name("pitch_1")
        assert pitch.name == "pitch_1"
        intensity.set_name("intensity_1")
        assert intensity.name == "intensity_1"
        formant.set_name("formant_1")
        assert formant.name == "formant_1"

        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        envelope = audio.get_envelope(filter_over=50, verbosity=0)
        envelope.set_name("env_2")
        assert envelope.name == "env_2"
        pitch = audio.get_pitch(filter_over=50, verbosity=0)
        pitch.set_name("pitch_2")
        assert pitch.name == "pitch_2"
        intensity = audio.get_intensity(filter_over=50, verbosity=0)
        intensity.set_name("intensity_2")
        assert intensity.name == "intensity_2"
        formant = audio.get_formant(formant_number=1, filter_over=50, verbosity=0)
        formant.set_name("formant_2")

    def test_set_condition(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.json", verbosity=0)
        pitch = Pitch("test_pitches/test_audio_1_pitch.txt", verbosity=0)
        intensity = Intensity("test_intensities/test_audio_1_intensity.mat", verbosity=0)
        formant = Formant("test_formants/test_audio_1_formant.pkl", verbosity=0)

        envelope.set_condition("cond_1")
        assert envelope.condition == "cond_1"
        pitch.set_condition("cond_1")
        assert pitch.condition == "cond_1"
        intensity.set_condition("cond_1")
        assert intensity.condition == "cond_1"
        formant.set_condition("cond_1")
        assert formant.condition == "cond_1"

        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        envelope = audio.get_envelope(filter_over=50, verbosity=0)
        envelope.set_condition("cond_2")
        assert envelope.condition == "cond_2"
        pitch = audio.get_pitch(filter_over=50, verbosity=0)
        pitch.set_condition("cond_2")
        assert pitch.condition == "cond_2"
        intensity = audio.get_intensity(filter_over=50, verbosity=0)
        intensity.set_condition("cond_2")
        assert intensity.condition == "cond_2"
        formant = audio.get_formant(formant_number=1, filter_over=50, verbosity=0)
        formant.set_condition("cond_2")

    def test_define_name_init(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.wav", name="env_1", verbosity=0)
        assert envelope.get_name() == "env_1"
        pitch = Pitch("test_pitches/test_audio_1_pitch.wav", name=None, verbosity=0)
        assert pitch.get_name() == "test_audio_1_pitch"
        intensity = Intensity("test_intensities/test_audio_1_intensity.wav", verbosity=0)
        assert intensity.get_name() == "test_audio_1_intensity"
        formant = Formant("test_formants/test_audio_1_formant.wav", name="test_audio_1_formant.wav", verbosity=0)
        assert formant.get_name() == "test_audio_1_formant.wav"
        freq, samples = wavfile.read("test_envelopes/test_audio_1_envelope.wav")
        envelope = Envelope(samples, freq, verbosity=0)
        assert envelope.get_name() == "Unnamed envelope"
        pitch = Pitch(samples, freq, name="seq_1", verbosity=0)
        assert pitch.get_name() == "seq_1"

    def test_load_from_path(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.tsv", verbosity=0)
        self.assertRaises(InvalidPathException, Envelope, "test_envelopes/blabla")

    def test_load_from_samples(self):
        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        envelope = Envelope(samples, freq, verbosity=0)
        assert len(envelope.samples) == 8
        assert envelope.frequency == 44100
        assert envelope.timestamps[4] == 4 * 1 / 44100
        assert envelope.samples[4] == 4

        freq, samples = wavfile.read("test_pitches/test_audio_1_pitch.wav")
        pitch = Pitch(samples, freq, verbosity=0)
        assert len(pitch.samples) == 22050
        assert pitch.frequency == 44100
        assert pitch.timestamps[42] == 42 * 1 / 44100
        assert np.isclose(pitch.samples[10025], 197.32558113945146)

    def test_load_samples(self):
        # See test_load_from_samples
        pass

    def test_load_single_sample_file(self):
        # See test_init
        pass

    def test_load_audio_file(self):
        # See test_init
        pass

    def test_load_json_metadata(self):
        # See test_init
        pass

    def test_calculate_frequency(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.wav", verbosity=0)
        assert envelope.get_frequency() == 44100

        pitch = Pitch("test_pitches/test_audio_1_pitch.json", verbosity=0)
        assert pitch.get_frequency() == 44100

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert intensity.get_frequency() == 44100

        formant = Formant("test_formants/test_audio_1_formant.mat", verbosity=0)
        assert formant.get_frequency() == 44100

        envelope = Envelope("test_envelopes/test_audio_1_envelope.txt", verbosity=0)
        assert envelope.get_frequency() == 44100

        pitch = Pitch("test_pitches/test_audio_1_pitch.csv", verbosity=0)
        assert pitch.get_frequency() == 44100

        intensity = Intensity("test_intensities/test_audio_1_intensity.tsv", verbosity=0)
        assert intensity.get_frequency() == 44100

        formant = Formant("test_formants/test_audio_1_formant.aaa", verbosity=0)
        assert formant.get_frequency() == 44100

    def test_calculate_timestamps(self):
        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        envelope = Envelope(samples, freq, verbosity=0)
        assert np.allclose(envelope.timestamps, np.array([0, 1, 2, 3, 4, 5, 6, 7]) / freq)

        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert np.allclose(obj.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert np.allclose(intensity.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

    def test_get_path(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert obj.get_path() == op.join(f"test_{folder}", f"test_audio_1_{kind}.{ext}")

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert intensity.get_path() == op.join("test_intensities", "test_audio_4_intensity.xlsx")

    def test_get_name(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert obj.get_name() == f"test_audio_1_{kind}"

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert intensity.get_name() == "test_audio_4_intensity"

    def test_get_conditions(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert obj.get_condition() is None

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert intensity.get_condition() is None

    def test_get_samples(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert len(obj.get_samples()) == 22050

            freq = 44100
            samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
            obj = typ(samples, freq, verbosity=0)
            assert np.allclose(obj.get_samples(), np.array([0, 1, 2, 3, 4, 5, 6, 7]))

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert len(intensity.get_samples()) == 4411

    def test_get_sample(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.wav", verbosity=0)
        assert np.isclose(envelope.get_sample(42), 767.4754693763366)

        pitch = Pitch("test_pitches/test_audio_1_pitch.json", verbosity=0)
        assert np.isclose(pitch.get_sample(10025), 197.32558113945146)

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert np.isclose(intensity.get_sample(2206), 183.9678676679894)

        formant = Formant("test_formants/test_audio_1_formant.mat", verbosity=0)
        assert np.isclose(formant.get_sample(2206), 114.27552422725371)

        envelope = Envelope("test_envelopes/test_audio_1_envelope.txt", verbosity=0)
        assert np.isclose(envelope.get_sample(42), 767.4754693763366)

        pitch = Pitch("test_pitches/test_audio_1_pitch.csv", verbosity=0)
        assert np.isclose(pitch.get_sample(10025), 197.32558113945146)

        intensity = Intensity("test_intensities/test_audio_1_intensity.tsv", verbosity=0)
        assert np.isclose(intensity.get_sample(2206), 183.9678676679894)

        formant = Formant("test_formants/test_audio_1_formant.aaa", verbosity=0)
        assert np.isclose(formant.get_sample(2206), 114.27552422725371)

    def test_get_number_of_samples(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert obj.get_number_of_samples() == 22050

            freq = 44100
            samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
            obj = typ(samples, freq, verbosity=0)
            assert np.allclose(obj.get_number_of_samples(), 8)

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert intensity.get_number_of_samples() == 4411

    def test_get_timestamps(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert np.allclose(obj.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

            freq = 44100
            samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
            obj = typ(samples, freq, verbosity=0)
            assert np.allclose(obj.get_timestamps(), np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert np.allclose(intensity.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

    def test_get_duration(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert np.isclose(obj.get_duration(), 0.5 - 1/obj.frequency)

            freq = 44100
            samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
            obj = typ(samples, freq, verbosity=0)
            assert np.isclose(obj.get_duration(), (len(samples) - 1) / freq)

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert np.isclose(intensity.get_duration(), 0.1)

    def test_get_frequency(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            obj = typ(f"test_{folder}/test_audio_1_{kind}.{ext}", verbosity=0)
            assert np.isclose(obj.get_frequency(), 44100)

            freq = 44100
            samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
            obj = typ(samples, freq, verbosity=0)
            assert np.isclose(obj.get_frequency(), freq)

        intensity = Intensity("test_intensities/test_audio_4_intensity.xlsx", verbosity=0)
        assert np.isclose(intensity.get_frequency(), 44100)

    def test_get_info(self):
        extensions = ["wav", "json", "mat", "pkl", "txt", "csv", "tsv", "aaa"]
        random.shuffle(extensions)
        types = [Envelope, Pitch, Intensity, Formant, Envelope, Pitch, Intensity, Formant]
        folders = ["envelopes", "pitches", "intensities", "formants", "envelopes", "pitches", "intensities", "formants"]
        kinds = ["envelope", "pitch", "intensity", "formant", "envelope", "pitch", "intensity", "formant"]

        for ext, typ, folder, kind in zip(extensions, types, folders, kinds):
            path = op.join(f"test_{folder}", f"test_audio_1_{kind}.{ext}")
            obj = typ(path, verbosity=0)
            assert obj.get_info("str") == (f"Name: test_audio_1_{kind} · Path: {path} · Duration: {obj.get_duration()} "
                                           f"· Frequency: {obj.get_frequency()} · Number of samples: 22050")

            freq = 44100
            samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
            obj = typ(samples, freq, verbosity=0)
            assert obj.get_info("str") == (f"Name: Unnamed {kind} · Path: None · Duration: {7 / 44100} "
                                           f"· Frequency: {freq} · Number of samples: {8}")

    def test_filter_frequencies(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.wav", verbosity=0)
        envelope_ff = envelope.filter_frequencies(filter_below=10, filter_over=3000, name="ff", verbosity=0)
        assert np.allclose(envelope_ff.samples[0:8], [2.34764269e-03, 2.32594720e-02, 1.12372390e-01, 3.62002009e-01,
                                                         8.95240420e-01, 1.84493845e+00, 3.33689272e+00, 5.47989149e+00])
        assert len(envelope_ff.samples) == len(envelope.samples)
        assert envelope_ff.get_name() == "ff"

        pitch = Pitch("test_pitches/test_audio_1_pitch.wav", verbosity=0)
        pitch_ff = pitch.filter_frequencies(filter_below=10, filter_over=3000)
        assert np.allclose(pitch_ff.samples[10000:10008], [35.90719797, 35.7800959, 35.65326703, 35.52671107,
                                                           35.40042771, 35.27441667, 35.14867763, 35.02321028])
        assert len(pitch_ff.samples) == len(pitch.samples)
        assert pitch_ff.get_name() == "test_audio_1_pitch +FF"

        assert pitch_ff.metadata["processing_steps"][-1]["processing_type"] == "filter_frequencies"
        assert pitch_ff.metadata["processing_steps"][-1]["filter_below"] == 10
        assert pitch_ff.metadata["processing_steps"][-1]["filter_over"] == 3000

    def test_resample(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.wav", verbosity=0)
        envelope_rs = envelope.resample(1000, name="rs", verbosity=0)
        assert np.allclose(envelope_rs.samples[100:108], [26095.57947678, 25578.82067011, 25205.70429134,
                                                          25061.02902818, 25073.08554854, 25173.3233327,
                                                          25322.26627459, 25495.1196532])
        assert len(envelope_rs.samples) == 500
        assert envelope_rs.get_name() == "rs"

        intensity = Intensity("test_intensities/test_audio_1_intensity.wav", verbosity=0)
        intensity_rs = intensity.resample(1000, verbosity=0)
        print(intensity_rs.samples[100:108])
        assert np.allclose(intensity_rs.samples[100:108], [179.23876828, 179.23088875, 179.22505774, 179.2209274,
                                                           179.21837787, 179.21813704, 179.22018497, 179.2239262])
        assert len(intensity_rs.samples) == 500
        assert intensity_rs.get_name() == "test_audio_1_intensity +RS 1000"

        assert intensity_rs.metadata["processing_steps"][-1]["processing_type"] == "resample"
        assert intensity_rs.metadata["processing_steps"][-1]["frequency"] == 1000
        assert intensity_rs.metadata["processing_steps"][-1]["method"] == "cubic"
        assert intensity_rs.metadata["processing_steps"][-1]["window_size"] == 1e7
        assert intensity_rs.metadata["processing_steps"][-1]["overlap_ratio"] == 0.5

    def test_trim(self):
        envelope = Envelope("test_envelopes/test_audio_1_envelope.wav", verbosity=0)
        envelope_tr = envelope.trim(0.2, 0.3, name="tr", verbosity=0)
        assert np.allclose(envelope_tr.samples[100:108], [24752.44167911, 24746.92042137, 24741.79038621,
                                                          24737.04770754, 24732.68833988, 24728.70812428,
                                                          24725.10277104, 24721.86785002])
        assert len(envelope_tr.samples) == 4411
        assert envelope_tr.get_name() == "tr"

        formant = Formant("test_formants/test_audio_1_formant.wav", verbosity=0)
        formant_tr = formant.trim(0.2, 0.3, verbosity=0)
        assert np.allclose(formant_tr.samples[100:108], [222.64964362, 222.8200719,  222.98974076, 223.15864185,
                                                         223.32675951, 223.49408571, 223.66061993, 223.82635406])
        assert len(formant_tr.samples) == 4411
        assert formant_tr.get_name() == "test_audio_1_formant +TR"

        assert formant_tr.metadata["processing_steps"][-1]["processing_type"] == "trim"
        assert formant_tr.metadata["processing_steps"][-1]["start"] == 0.2
        assert formant_tr.metadata["processing_steps"][-1]["end"] == 0.3

        formant_tr = formant.trim(-5, 5, verbosity=0)
        assert formant == formant_tr

        self.assertRaises(Exception, formant.trim, -5, 5, error_if_out_of_bounds=True, verbosity=0)

    def test_to_table(self):
        pass

    def test_to_json(self):
        pass

    def test_to_dict(self):
        pass

    def test_to_dataframe(self):
        pass

    def test_save(self):
        pass

    def test_save_json(self):
        pass

    def test_save_mat(self):
        pass

    def test_save_excel(self):
        pass

    def test_save_pickle(self):
        pass

    def test_save_wav(self):
        pass

    def test_save_txt(self):
        pass

    def test_len(self):
        pass

    def test_getitem(self):
        pass

    def test_repr(self):
        pass

    def test_eq(self):
        pass

    def test_init_envelope(self):
        # See test_init
        pass

    def test_init_pitch(self):
        # See test_init
        pass

    def test_init_intensity(self):
        # See test_init
        pass

    def test_init_formant(self):
        # See test_init
        pass

    def test_load_formant_number(self):
        # See test_init
        pass