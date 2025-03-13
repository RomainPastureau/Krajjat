"""Tests the Audio functions from the toolbox."""

import unittest
import numpy as np
import pandas as pd
from scipy.io import wavfile
import os.path as op

from krajjat.classes.audio import Audio
from krajjat.classes.exceptions import InvalidPathException

class TestsAudio(unittest.TestCase):

    def test_init(self):
        # WAV
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.wav")
        assert audio.files == ["test_audio_1.wav"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1/44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # JSON
        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.json")
        assert audio.files == ["test_audio_1.json"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1/44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # Excel
        audio = Audio("test_audios/test_audio_4.xlsx", verbosity=0)
        assert len(audio.samples) == 339
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_4.xlsx")
        assert audio.files == ["test_audio_4.xlsx"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_4"
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # MAT
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.mat")
        assert audio.files == ["test_audio_1.mat"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # Pickle
        audio = Audio("test_audios/test_audio_1.pkl", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.pkl")
        assert audio.files == ["test_audio_1.pkl"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # Text
        audio = Audio("test_audios/test_audio_1.txt", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.txt")
        assert audio.files == ["test_audio_1.txt"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # CSV
        audio = Audio("test_audios/test_audio_1.csv", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.csv")
        assert audio.files == ["test_audio_1.csv"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # TSV
        audio = Audio("test_audios/test_audio_1.tsv", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.tsv")
        assert audio.files == ["test_audio_1.tsv"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

        # Custom extension
        audio = Audio("test_audios/test_audio_1.aaa", verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.samples[42] == 18488
        assert audio.frequency == 44100
        assert audio.condition is None
        assert audio.path == op.join("test_audios", "test_audio_1.aaa")
        assert audio.files == ["test_audio_1.aaa"]
        assert audio.kind == "Audio"
        assert audio.name == "test_audio_1"
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert len(audio.metadata) == 1
        assert len(audio.metadata["processing_steps"]) == 0

    def test_set_name(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.name == "test_audio_1"
        audio.set_name("test_audio_2")
        assert audio.name == "test_audio_2"

    def test_set_condition(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.condition is None
        audio.set_condition("English")
        assert audio.condition == "English"

    def test_define_name_init(self):
        audio = Audio("test_audios/test_audio_1.wav", name="aud_1", verbosity=0)
        assert audio.get_name() == "aud_1"
        audio = Audio("test_audios/test_audio_1.wav", name=None, verbosity=0)
        assert audio.get_name() == "test_audio_1"
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.get_name() == "test_audio_1"
        audio = Audio("test_audios/test_audio_1.wav", name="test_audio_1.wav", verbosity=0)
        assert audio.get_name() == "test_audio_1.wav"
        freq, samples = wavfile.read("test_audios/test_audio_1.wav")
        audio = Audio(samples, freq, verbosity=0)
        assert audio.get_name() == "Unnamed audio"
        audio = Audio(samples, freq, name="seq_1", verbosity=0)
        assert audio.get_name() == "seq_1"

        audio = Audio("test_audios/test_audio_individual/*.tsv", verbosity=0)
        assert audio.get_name() == "test_audio_individual"

    def test_load_from_path(self):
        audio = Audio("test_audios/test_audio_individual/*.tsv", verbosity=0)
        audio = Audio("test_audios/test_audio_1.tsv", verbosity=0)
        self.assertRaises(InvalidPathException, Audio, "test_audios/blabla")

    def test_load_from_samples(self):
        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert len(audio.samples) == 8
        assert audio.frequency == 44100
        assert audio.timestamps[4] == 4 * 1 / 44100
        assert audio.samples[4] == 4

        freq, samples = wavfile.read("test_audios/test_audio_1.wav")
        audio = Audio(samples, freq, verbosity=0)
        assert len(audio.samples) == 22050
        assert audio.frequency == 44100
        assert audio.timestamps[42] == 42 * 1 / 44100
        assert audio.samples[42] == 18488

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
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.get_frequency() == 44100

        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        assert audio.get_frequency() == 44100

        audio = Audio("test_audios/test_audio_4.xlsx", verbosity=0)
        assert audio.get_frequency() == 44100

        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)
        assert audio.get_frequency() == 44100

        audio = Audio("test_audios/test_audio_1.txt", verbosity=0)
        assert audio.get_frequency() == 44100

        audio = Audio("test_audios/test_audio_1.csv", verbosity=0)
        assert audio.get_frequency() == 44100

        audio = Audio("test_audios/test_audio_1.tsv", verbosity=0)
        assert audio.get_frequency() == 44100

        audio = Audio("test_audios/test_audio_1.aaa", verbosity=0)
        assert audio.get_frequency() == 44100

    def test_calculate_timestamps(self):
        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert np.allclose(audio.timestamps, np.array([0, 1, 2, 3, 4, 5, 6, 7]) / freq)

        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        audio = Audio("test_audios/test_audio_4.xlsx", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        audio = Audio("test_audios/test_audio_1.txt", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        audio = Audio("test_audios/test_audio_1.csv", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        audio = Audio("test_audios/test_audio_1.tsv", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

        audio = Audio("test_audios/test_audio_1.aaa", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)

    def test_get_path(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.get_path() == op.join("test_audios", "test_audio_1.wav")

        audio = Audio("test_audios/test_audio_individual/*.tsv", verbosity=0)
        assert audio.get_path() == op.join("test_audios", "test_audio_individual")

        audio = Audio("test_audios/test_audio_individual", verbosity=0)
        assert audio.get_path() == op.join("test_audios", "test_audio_individual")

        audio = Audio("test_audios/test_audio_individual/", verbosity=0)
        assert audio.get_path() == op.join("test_audios", "test_audio_individual")

    def test_get_name(self):
        # See test_define_name_init
        pass

    def test_get_condition(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.get_condition() is None

        audio = Audio("test_audios/test_audio_1.wav", condition="test", verbosity=0)
        assert audio.get_condition() == "test"

    def test_get_samples(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert len(audio.get_samples()) == 22050

        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert np.allclose(audio.get_samples(), np.array([0, 1, 2, 3, 4, 5, 6, 7]))

    def test_get_sample(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.get_sample(42) == 18488

        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert audio.get_sample(4) == 4

    def test_get_number_of_samples(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert audio.get_number_of_samples() == 22050

        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert audio.get_number_of_samples() == 8

    def test_get_timestamps(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)
        assert len(audio.get_timestamps()) == 22050

        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert np.allclose(audio.get_timestamps(), np.array([0, 1, 2, 3, 4, 5, 6, 7]) / freq)
        assert len(audio.get_timestamps()) == 8

    def test_get_duration(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)
        assert len(audio.get_timestamps()) == 22050

        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert audio.get_duration() == 7/44100

    def test_get_frequency(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        assert np.allclose(audio.get_timestamps()[0:8], np.array([0, 1, 2, 3, 4, 5, 6, 7]) / 44100)
        assert audio.get_frequency() == 44100

        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        assert audio.get_frequency() == 44100

    def test_get_info(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        info = audio.get_info()
        assert len(info) == 5
        assert info["Name"] == "test_audio_1"
        assert info["Path"] == op.join("test_audios", "test_audio_1.wav")
        assert np.isclose(info["Duration"], 0.5 - 1/44100)
        assert info["Frequency"] == 44100
        assert info["Number of samples"] == 22050

        info = audio.get_info(include_path=False)
        assert len(info) == 4

        info = audio.get_info("list")
        assert info[0] == ['Name', 'Path', 'Duration', 'Frequency', 'Number of samples']
        assert info[1] == ['test_audio_1', 'test_audios\\test_audio_1.wav', 0.49997732426303854, 44100, 22050]

        freq = 44100
        samples = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        audio = Audio(samples, freq, verbosity=0)
        info = audio.get_info()
        assert info["Name"] == "Unnamed audio"
        assert info["Path"] is None
        assert np.isclose(info["Duration"], 7/44100)
        assert info["Frequency"] == 44100
        assert info["Number of samples"] == 8

    def test_get_envelope(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        envelope = audio.get_envelope(filter_over=50, verbosity=0)
        assert np.allclose(envelope[0:8], [0.06788517, 0.44120087, 1.38907701, 3.04069082,
                                              5.45514783, 8.67720331, 12.73744256, 17.66024739])
        assert len(envelope.samples) == len(audio.samples)
        assert envelope.get_name() == audio.get_name() + " (ENV)"

        assert envelope.metadata["processing_steps"][0]["processing_type"] == "get_envelope"
        assert envelope.metadata["processing_steps"][0]["original_audio"] == audio.get_name()
        assert envelope.metadata["processing_steps"][0]["original_path"] == audio.get_path()
        assert envelope.metadata["processing_steps"][0]["window_size"] == 1e6
        assert envelope.metadata["processing_steps"][0]["overlap_ratio"] == 0.5
        assert envelope.metadata["processing_steps"][0]["filter_below"] is None
        assert envelope.metadata["processing_steps"][0]["filter_over"] == 50
        assert envelope.metadata["processing_steps"][1]["processing_type"] == "filter_frequencies"
        assert envelope.metadata["processing_steps"][1]["filter_below"] is None
        assert envelope.metadata["processing_steps"][1]["filter_over"] == 50

    def test_get_pitch(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        pitch = audio.get_pitch(filter_over=50, verbosity=0)
        assert np.allclose(pitch[10000:10008], [197.7418498, 197.724117, 197.7064746, 197.6889226,
                                                197.6714611, 197.6540901,  197.6368094, 197.6196190])
        assert len(pitch.samples) == len(audio.samples)
        assert pitch.get_name() == audio.get_name() + " (PIT)"

        assert pitch.metadata["processing_steps"][0]["processing_type"] == "get_pitch"
        assert pitch.metadata["processing_steps"][0]["original_audio"] == audio.get_name()
        assert pitch.metadata["processing_steps"][0]["original_path"] == audio.get_path()
        assert pitch.metadata["processing_steps"][0]["method"] == "parselmouth"
        assert pitch.metadata["processing_steps"][0]["zeros_as_nan"] == False
        assert pitch.metadata["processing_steps"][0]["filter_below"] is None
        assert pitch.metadata["processing_steps"][0]["filter_over"] == 50
        assert pitch.metadata["processing_steps"][1]["processing_type"] == "filter_frequencies"
        assert pitch.metadata["processing_steps"][1]["filter_below"] is None
        assert pitch.metadata["processing_steps"][1]["filter_over"] == 50


    def test_get_intensity(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        intensity = audio.get_intensity(filter_over=50, verbosity=0)
        assert np.allclose(intensity[10000:10008], [179.34838814, 179.34837336, 179.34835867, 179.34834407,
                                                    179.34832957, 179.34831517, 179.34830087, 179.34828669])
        assert len(intensity.samples) == len(audio.samples)
        assert intensity.get_name() == audio.get_name() + " (INT)"

        assert intensity.metadata["processing_steps"][0]["processing_type"] == "get_intensity"
        assert intensity.metadata["processing_steps"][0]["original_audio"] == audio.get_name()
        assert intensity.metadata["processing_steps"][0]["original_path"] == audio.get_path()
        assert intensity.metadata["processing_steps"][0]["zeros_as_nan"] == False
        assert intensity.metadata["processing_steps"][0]["filter_below"] is None
        assert intensity.metadata["processing_steps"][0]["filter_over"] == 50
        assert intensity.metadata["processing_steps"][1]["processing_type"] == "filter_frequencies"
        assert intensity.metadata["processing_steps"][1]["filter_below"] is None
        assert intensity.metadata["processing_steps"][1]["filter_over"] == 50

    def test_get_formant(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        formant = audio.get_formant(filter_over=50, verbosity=0)
        assert np.allclose(formant[10000:10008], [179.15647516, 179.14794863, 179.13956819, 179.13133285,
                                                    179.12324156, 179.11529336, 179.10748729, 179.09982239])
        assert len(formant.samples) == len(audio.samples)
        assert formant.get_name() == audio.get_name() + " (F1)"

        formant = audio.get_formant(formant_number=1, filter_over=50, verbosity=0)
        assert np.allclose(formant[10000:10008], [179.15647516, 179.14794863, 179.13956819, 179.13133285,
                                                    179.12324156, 179.11529336, 179.10748729, 179.09982239])
        assert len(formant.samples) == len(audio.samples)
        assert formant.get_name() == audio.get_name() + " (F1)"

        formant = audio.get_formant(formant_number=2, filter_over=50, verbosity=0)
        assert np.allclose(formant[10000:10008], [282.36585267, 280.76513697, 279.17760047, 277.60319125,
                                                  276.04185723, 274.49354623, 272.95820598, 271.43578403])
        assert len(formant.samples) == len(audio.samples)
        assert formant.get_name() == audio.get_name() + " (F2)"

        assert formant.metadata["processing_steps"][0]["processing_type"] == "get_formant"
        assert formant.metadata["processing_steps"][0]["original_audio"] == audio.get_name()
        assert formant.metadata["processing_steps"][0]["original_path"] == audio.get_path()
        assert formant.metadata["processing_steps"][0]["formant_number"] == 2
        assert formant.metadata["processing_steps"][0]["zeros_as_nan"] == False
        assert formant.metadata["processing_steps"][0]["filter_below"] is None
        assert formant.metadata["processing_steps"][0]["filter_over"] == 50
        assert formant.metadata["processing_steps"][1]["processing_type"] == "filter_frequencies"
        assert formant.metadata["processing_steps"][1]["filter_below"] is None
        assert formant.metadata["processing_steps"][1]["filter_over"] == 50

    def test_get_derivative(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)

        envelope = audio.get_derivative("envelope", filter_over=50, verbosity=0)
        assert np.allclose(envelope[0:8], [0.06788517, 0.44120087, 1.38907701, 3.04069082,
                                              5.45514783, 8.67720331, 12.73744256, 17.66024739])
        assert len(envelope.samples) == len(audio.samples)
        assert envelope.get_name() == audio.get_name() + " (ENV)"

        pitch = audio.get_derivative("pitch", filter_over=50, verbosity=0)
        assert np.allclose(pitch[10000:10008], [197.7418498, 197.724117, 197.7064746, 197.6889226,
                                                197.6714611, 197.6540901,  197.6368094, 197.6196190])
        assert len(pitch.samples) == len(audio.samples)
        assert pitch.get_name() == audio.get_name() + " (PIT)"

        intensity = audio.get_derivative("intensity", filter_over=50, verbosity=0)
        assert np.allclose(intensity[10000:10008], [179.34838814, 179.34837336, 179.34835867, 179.34834407,
                                                    179.34832957, 179.34831517, 179.34830087, 179.34828669])
        assert len(intensity.samples) == len(audio.samples)
        assert intensity.get_name() == audio.get_name() + " (INT)"

        formant = audio.get_derivative("formant", formant_number=1, filter_over=50, verbosity=0)
        assert np.allclose(formant[10000:10008], [179.15647516, 179.14794863, 179.13956819, 179.13133285,
                                                    179.12324156, 179.11529336, 179.10748729, 179.09982239])
        assert len(formant.samples) == len(audio.samples)
        assert formant.get_name() == audio.get_name() + " (F1)"

        formant = audio.get_derivative("f2", filter_over=50, verbosity=0)
        assert np.allclose(formant[10000:10008], [282.36585267, 280.76513697, 279.17760047, 277.60319125,
                                                  276.04185723, 274.49354623, 272.95820598, 271.43578403])
        assert len(formant.samples) == len(audio.samples)
        assert formant.get_name() == audio.get_name() + " (F2)"

        assert formant.metadata["processing_steps"][0]["processing_type"] == "get_formant"
        assert formant.metadata["processing_steps"][0]["original_audio"] == audio.get_name()
        assert formant.metadata["processing_steps"][0]["original_path"] == audio.get_path()
        assert formant.metadata["processing_steps"][0]["formant_number"] == 2
        assert formant.metadata["processing_steps"][0]["zeros_as_nan"] == False
        assert formant.metadata["processing_steps"][0]["filter_below"] is None
        assert formant.metadata["processing_steps"][0]["filter_over"] == 50
        assert formant.metadata["processing_steps"][1]["processing_type"] == "filter_frequencies"
        assert formant.metadata["processing_steps"][1]["filter_below"] is None
        assert formant.metadata["processing_steps"][1]["filter_over"] == 50

    def test_filter_frequencies(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio_ff = audio.filter_frequencies(4000, 5000, "ff", verbosity=0)
        assert np.allclose(audio_ff[0:8], [ 0, 2.25135525, 11.36551573, 27.63221252,
                                            43.5740015, 48.28064242, 34.18843354, 2.40043875])
        assert len(audio_ff.samples) == len(audio.samples)
        assert audio_ff.get_name() == "ff"

        audio_ff = audio.filter_frequencies(4000, 5000, verbosity=0)
        assert np.allclose(audio_ff[0:8], [ 0, 2.25135525, 11.36551573, 27.63221252,
                                            43.5740015, 48.28064242, 34.18843354, 2.40043875])
        assert len(audio_ff.samples) == len(audio.samples)
        assert audio_ff.get_name() == "test_audio_1 +FF"

        assert audio_ff.metadata["processing_steps"][0]["processing_type"] == "filter_frequencies"
        assert audio_ff.metadata["processing_steps"][0]["filter_below"] == 4000
        assert audio_ff.metadata["processing_steps"][0]["filter_over"] == 5000

    def test_resample(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio_resampled = audio.resample(20000, name="res", verbosity=0)
        assert np.allclose(audio_resampled[0:8], [[0, 1076.38319137, 2151.37927296, 3222.89148491,
                                                   4289.24029694, 5345.03432549, 6395.4634669, 7436.25997244]])
        assert len(audio_resampled.samples) == 10000
        assert audio_resampled.get_name() == "res"

        audio_resampled = audio.resample(20000, verbosity=0)
        assert np.allclose(audio_resampled[0:8], [[0, 1076.38319137, 2151.37927296, 3222.89148491,
                                                   4289.24029694, 5345.03432549, 6395.4634669, 7436.25997244]])
        assert len(audio_resampled.samples) == 10000
        assert audio_resampled.get_name() == "test_audio_1 +RS 20000"

        assert audio_resampled.metadata["processing_steps"][0]["processing_type"] == "resample"
        assert audio_resampled.metadata["processing_steps"][0]["frequency"] == 20000
        assert audio_resampled.metadata["processing_steps"][0]["method"] == "cubic"
        assert audio_resampled.metadata["processing_steps"][0]["window_size"] == 1e7
        assert audio_resampled.metadata["processing_steps"][0]["overlap_ratio"] == 0.5

    def test_trim(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio_trimmed = audio.trim(0.2, 0.3, name="tr", verbosity=0)
        assert np.allclose(audio_trimmed[0:8], audio[8820:8828])
        assert len(audio_trimmed.samples) == 4411
        assert audio_trimmed.get_name() == "tr"

        audio_trimmed = audio.trim(0.2, 0.3, verbosity=0)
        assert np.allclose(audio_trimmed[0:8], audio[8820:8828])
        assert len(audio_trimmed.samples) == 4411
        assert audio_trimmed.get_name() == "test_audio_1 +TR"

        assert audio_trimmed.metadata["processing_steps"][0]["processing_type"] == "trim"
        assert audio_trimmed.metadata["processing_steps"][0]["start"] == 0.2
        assert audio_trimmed.metadata["processing_steps"][0]["end"] == 0.3

        audio_trimmed = audio.trim(-5, 5, verbosity=0)
        assert audio == audio_trimmed

        self.assertRaises(Exception, audio.trim, -5, 5, error_if_out_of_bounds=True, verbosity=0)

    def test_set_attributes_from_other_audio(self):
        audio = Audio("test_audios/test_audio_1.wav", condition="test", verbosity=0)
        new_audio = Audio([0, 1, 2], 1000)

        new_audio._set_attributes_from_other_object(audio)
        assert new_audio.get_path() == audio.get_path()
        assert new_audio.get_condition() == audio.get_condition()
        assert new_audio.metadata == audio.metadata

    def test_find_excerpt(self):
        audio = Audio("test_audios/audio_ainhoa.wav", verbosity=0)
        audio_excerpt = audio.trim(12, 18, verbosity=0)

        delay = audio.find_excerpt(audio_excerpt, return_delay_format="s", verbosity=0)
        assert delay == 12

    def test_find_excerpts(self):
        audio = Audio("test_audios/audio_ainhoa.wav", verbosity=0)
        audio_excerpt_1 = audio.trim(12, 18, verbosity=0)
        audio_excerpt_2 = audio.trim(15, 21, verbosity=0)
        audio_excerpt_3 = audio.trim(18, 24, verbosity=0)
        audio_excerpts = [audio_excerpt_1, audio_excerpt_2, audio_excerpt_3]

        delays = audio.find_excerpts(audio_excerpts, return_delay_format="s", verbosity=0)
        assert np.allclose(delays, [12, 15, 18])

    def test_to_table(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        table = audio.to_table()
        assert len(table) == len(audio.samples) + 1
        assert table[0] == ["Timestamp", "Sample"]
        assert np.isclose(table[1][1], 0)
        assert np.isclose(table[2][0], 2.2675736961451248e-05)

        audio = Audio([0, 1, 2, 3], 1000, verbosity=0)
        table = audio.to_table()
        assert len(table) == len(audio.samples) + 1
        assert table[0] == ["Timestamp", "Sample"]
        assert table[1] == [0.000, 0]
        assert table[2] == [0.001, 1]
        assert table[3] == [0.002, 2]
        assert table[4] == [0.003, 3]

    def test_to_json(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        json_data = audio.to_json()

        assert len(json_data) == 4
        assert len(json_data["processing_steps"]) == 0
        assert json_data["Sample"][1] == 489
        assert json_data["Timestamp"][441] == 0.01
        assert json_data["Frequency"] == 44100

        audio = Audio([0, 1, 2, 3], 1000, verbosity=0)
        json_data = audio.to_json()
        assert len(json_data) == 4
        assert len(json_data["processing_steps"]) == 0
        assert json_data["Sample"][1] == 1
        assert json_data["Timestamp"][1] == 0.001
        assert json_data["Frequency"] == 1000

    def test_to_dict(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio_dict = audio.to_dict()

        assert isinstance(audio_dict, dict)
        assert len(audio_dict) == 3
        assert audio_dict["Sample"][1] == 489
        assert audio_dict["Timestamp"][441] == 0.01
        assert audio_dict["Frequency"] == 44100

        audio = Audio([0, 1, 2, 3], 1000, verbosity=0)
        audio_dict = audio.to_dict()
        assert isinstance(audio_dict, dict)
        assert len(audio_dict) == 3
        assert audio_dict["Sample"][1] == 1
        assert audio_dict["Timestamp"][1] == 0.001
        assert audio_dict["Frequency"] == 1000

        audio_dict = audio.to_dict(False)
        assert isinstance(audio_dict, dict)
        assert len(audio_dict) == 2
        assert audio_dict["Sample"][1] == 1
        assert audio_dict["Timestamp"][1] == 0.001

    def test_to_dataframe(self):
        audio = Audio([0, 1, 2, 3], 1000, verbosity=0)
        audio_df = audio.to_dataframe()
        assert isinstance(audio_df, pd.DataFrame)

        dict_data = {'Timestamp': [0.000, 0.001, 0.002, 0.003],
                     'Samples': [0, 1, 2, 3]}

        dict_data_df = pd.DataFrame(dict_data)
        assert np.allclose(audio_df, dict_data_df)

    def test_save(self):
        audio = Audio([0, 1, 2, 3], 44100, verbosity=0)
        audio.metadata["Location"] = "France"

        # folder/name/file_format, include metadata
        audio.save("test_audios/saved_audios/", "test_audio_4", "json", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "mat", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "xlsx", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "pkl", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "txt", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "csv", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "tsv", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "aaa", verbosity=0)
        audio.save("test_audios/saved_audios/", "test_audio_4", "wav", verbosity=0)

        audio_s = Audio("test_audios/saved_audios/test_audio_4.json", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.mat", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.xlsx", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.pkl", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.txt", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.txt", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.csv", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.tsv", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.aaa", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.wav", verbosity=0)
        assert audio == audio_s
        keys_audio = [key.lower() for key in audio.metadata.keys()]
        keys_audio_s = [key.lower() for key in audio_s.metadata.keys()]
        assert set(keys_audio) == set(keys_audio_s)

        # everything in folder, omit metadata
        audio.save("test_audios/saved_audios/test_audio_4.json", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.mat", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.xlsx", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.pkl", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.txt", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.csv", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.tsv", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.aaa", include_metadata=False, verbosity=0)
        audio.save("test_audios/saved_audios/test_audio_4.wav", include_metadata=False, verbosity=0)

        audio_s = Audio("test_audios/saved_audios/test_audio_4.json", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.mat", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.xlsx", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.pkl", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 2
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.txt", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.txt", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.csv", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.tsv", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.aaa", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

        audio_s = Audio("test_audios/saved_audios/test_audio_4.wav", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

    def test_save_json(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio.metadata["Location"] = "France"

        audio.save_json("test_audios/saved_audios/", "test_audio_1", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.json", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_json("test_audios/saved_audios/test_audio_1.json", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.json", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_json("test_audios/saved_audios/", "test_audio_1", include_metadata=False, verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.json", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

    def test_save_mat(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio.metadata["Location"] = "France"

        audio.save_mat("test_audios/saved_audios/", "test_audio_1", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.mat", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_mat("test_audios/saved_audios/test_audio_1.mat", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.mat", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_mat("test_audios/saved_audios/", "test_audio_1", include_metadata=False, verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.mat", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()
        
    def test_save_excel(self):
        audio = Audio([0, 1, 2, 3], 44100, verbosity=0)
        audio.metadata["Location"] = "France"

        audio.save_excel("test_audios/saved_audios/", "test_audio_1", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.xlsx", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_excel("test_audios/saved_audios/test_audio_1.xlsx", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.xlsx", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_excel("test_audios/saved_audios/", "test_audio_1", include_metadata=False, verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.xlsx", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

    def test_save_pickle(self):
        audio = Audio("test_audios/test_audio_1.wav", verbosity=0)
        audio.metadata["Location"] = "France"

        audio.save_pickle("test_audios/saved_audios/", "test_audio_1", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.pkl", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_pickle("test_audios/saved_audios/test_audio_1.pkl", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.pkl", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

    def test_save_wav(self):
        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        audio.metadata["Location"] = "France"

        audio.save_wav("test_audios/saved_audios/", "test_audio_1", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.wav", verbosity=0)
        assert audio == audio_s
        keys_audio = [key.lower() for key in audio.metadata.keys()]
        keys_audio_s = [key.lower() for key in audio_s.metadata.keys()]
        assert set(keys_audio) == set(keys_audio_s)

        audio.save_wav("test_audios/saved_audios/test_audio_1.wav", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.wav", verbosity=0)
        assert audio == audio_s
        keys_audio = [key.lower() for key in audio.metadata.keys()]
        keys_audio_s = [key.lower() for key in audio_s.metadata.keys()]
        assert set(keys_audio) == set(keys_audio_s)

        audio.save_wav("test_audios/saved_audios/", "test_audio_1", include_metadata=False, verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.wav", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

    def test_save_txt(self):
        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        audio.metadata["Location"] = "France"

        # TXT
        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "txt", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.txt", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/test_audio_1.txt", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.txt", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "txt", include_metadata=False,
                       verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.txt", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()
        
        # TSV
        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "tsv", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.tsv", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/test_audio_1.tsv", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.tsv", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "tsv", include_metadata=False,
                       verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.tsv", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()
        
        # CSV
        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "csv", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.csv", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/test_audio_1.csv", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.csv", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "csv", include_metadata=False,
                       verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.csv", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()
        
        # AAA
        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "aaa", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.aaa", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/test_audio_1.aaa", verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.aaa", verbosity=0)
        assert audio == audio_s
        assert audio.metadata.keys() == audio_s.metadata.keys()

        audio.save_txt("test_audios/saved_audios/", "test_audio_1", "aaa", include_metadata=False,
                       verbosity=0)
        audio_s = Audio("test_audios/saved_audios/test_audio_1.aaa", verbosity=0)
        assert audio == audio_s
        assert len(audio_s.metadata.keys()) == 1
        assert "processing_steps" in audio_s.metadata.keys()

    def test_copy(self):
        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        copy_audio = audio.copy()
        assert id(audio) != id(copy_audio)
        assert id(audio.samples) != id(copy_audio.samples)
        assert id(audio.timestamps) != id(copy_audio.timestamps)

    def test_len(self):
        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        assert len(audio) == 22050

        audio = Audio([0, 1, 2, 3], 44100, verbosity=0)
        assert len(audio) == 4

    def test_get_item(self):
        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        assert np.allclose(audio[10000:10020], audio.samples[10000:10020])

        audio = Audio([0, 1, 2, 3], 44100, verbosity=0)
        assert np.allclose(audio[0:3], [0, 1, 2])

    def test_repr(self):
        audio = Audio("test_audios/test_audio_1.json", verbosity=0)
        assert repr(audio) == audio.name

        audio = Audio([0, 1, 2, 3], 44100, name="audio_1", verbosity=0)
        assert repr(audio) == audio.name

    def test_eq(self):
        audio_1 = Audio([0, 1, 2, 3], 44100, name="audio_1", verbosity=0)
        audio_2 = Audio([0, 1, 2, 3], 44100, name="audio_1", verbosity=0)
        assert audio_1 == audio_2