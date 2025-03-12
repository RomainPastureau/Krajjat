"""Tests the IO functions from the toolbox."""

import unittest
from krajjat.io_functions import *

class TestsIOFunctions(unittest.TestCase):

    def test_load_sequences(self):
        out = load_sequences("test_sequences", verbosity=0)
        number_of_files = len([file for file in os.listdir("test_sequences") if op.isfile(op.join("test_sequences", file))])
        assert len(out) == number_of_files

        out = load_sequences(op.join("test_sequences", "recursive"), False, "list", True,
                             False, verbosity=0)
        assert len(out) == 1

        out = load_sequences(op.join("test_sequences", "recursive"), True, "list", True,
                             False, verbosity=0)

        assert len(out) == 9

    def test_load_audios(self):
        out = load_audios("test_audios", verbosity=0)
        number_of_files = len([file for file in os.listdir("test_audios") if op.isfile(op.join("test_audios", file))])
        assert len(out) == number_of_files

        out = load_audios(op.join("test_audios", "recursive"), False, "list", True,
                          False, verbosity=0)
        assert len(out) == 1

        out = load_audios(op.join("test_audios", "recursive"), True, "list", True,
                          False, verbosity=0)

        assert len(out) == 6

    def test_save_sequences(self):
        sequences = [Sequence(op.join("test_sequences", "test_sequence_1.tsv"), verbosity=0),
                     Sequence(op.join("test_sequences", "test_sequence_2.tsv"), verbosity=0),
                     Sequence(op.join("test_sequences", "test_sequence_3.tsv"), verbosity=0)]
        save_sequences(sequences, op.join("test_sequences", "saved_sequences"), verbosity=0)

        new_sequences = [Sequence(op.join("test_sequences", "saved_sequences", "test_sequence_1.json"), verbosity=0),
                         Sequence(op.join("test_sequences", "saved_sequences", "test_sequence_2.json"), verbosity=0),
                         Sequence(op.join("test_sequences", "saved_sequences", "test_sequence_3.json"), verbosity=0)]

        for seq1, seq2 in zip(sequences, new_sequences):
            assert seq1 == seq2

        save_sequences(sequences, op.join("test_sequences", "saved_sequences"), file_format="tsv", verbosity=0)

        new_sequences = [Sequence(op.join("test_sequences", "saved_sequences", "test_sequence_1.tsv"), verbosity=0),
                         Sequence(op.join("test_sequences", "saved_sequences", "test_sequence_2.tsv"), verbosity=0),
                         Sequence(op.join("test_sequences", "saved_sequences", "test_sequence_3.tsv"), verbosity=0)]

        for seq1, seq2 in zip(sequences, new_sequences):
            assert seq1 == seq2

    def test_save_audios(self):
        audios = [Audio(op.join("test_audios", "test_audio_1.wav"), verbosity=0),
                  Audio(op.join("test_audios", "test_audio_2.wav"), verbosity=0),
                  Audio(op.join("test_audios", "test_audio_3.wav"), verbosity=0)]
        save_audios(audios, op.join("test_audios", "saved_audios"), verbosity=0)

        new_audios = [Audio(op.join("test_audios", "saved_audios", "test_audio_1.json"), verbosity=0),
                      Audio(op.join("test_audios", "saved_audios", "test_audio_2.json"), verbosity=0),
                      Audio(op.join("test_audios", "saved_audios", "test_audio_3.json"), verbosity=0)]

        for aud1, aud2 in zip(audios, new_audios):
            assert aud1 == aud2

        save_audios(audios, op.join("test_audios", "saved_audios"), file_format="wav", verbosity=0)

        new_audios = [Audio(op.join("test_audios", "saved_audios", "test_audio_1.wav"), verbosity=0),
                      Audio(op.join("test_audios", "saved_audios", "test_audio_2.wav"), verbosity=0),
                      Audio(op.join("test_audios", "saved_audios", "test_audio_3.wav"), verbosity=0)]

        for aud1, aud2 in zip(audios, new_audios):
            assert aud1 == aud2

    def test_save_stats(self):
        sequences = [Sequence(op.join("test_sequences", "test_sequence_1.tsv"), verbosity=0),
                     Sequence(op.join("test_sequences", "test_sequence_2.tsv"), verbosity=0),
                     Sequence(op.join("test_sequences", "test_sequence_3.tsv"), verbosity=0)]

        save_info(sequences, op.join("test_sequences", "stats"), verbosity=0)

        with open(op.join("test_sequences", "stats", "stats.json"), "r") as f:
            stats = json.loads(f.read())

        assert stats["test_sequence_1"]["Duration"] == 0.002
        assert stats["test_sequence_2"]["Fill level Head"] == 1.0
        assert stats["test_sequence_3"]["Number of poses"] == 3
