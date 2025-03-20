"""Tests the trial functions from the toolbox."""

import unittest

from krajjat.classes import Trial, Sequence, Audio, Envelope, Pose, Joint


class TestTrial(unittest.TestCase):

    def test_init(self):
        self.assertRaises(Exception, Trial)

        trial = Trial(1)
        assert trial.trial_id == 1
        assert trial.condition is None
        assert trial.sequence is None
        assert trial.audio is None

        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)

        trial = Trial(1, "English", sequence, audio)
        assert trial.trial_id == 1
        assert trial.condition == "English"
        assert trial.sequence == sequence
        assert trial.audio == audio

        trial = Trial(sequence=sequence, audio=audio)
        assert trial.trial_id == "test_sequence_1"
        assert trial.condition is None
        assert trial.sequence == sequence
        assert trial.audio == audio

    def test_set_trial_id(self):
        # See test_get_trial_id
        pass

    def test_set_condition(self):
        # See test_get_condition
        pass
    
    def test_set_sequence(self):
        # See test_set_sequence
        pass
    
    def test_set_audio(self):
        # See test_set_audio
        pass

    def test_get_trial_id(self):
        trial = Trial(1, "English")
        assert trial.get_trial_id() == 1
        trial.set_trial_id(2)
        assert trial.get_trial_id() == 2

        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)

        trial = Trial(sequence=sequence, audio=audio)
        assert trial.get_trial_id() == "test_sequence_1"
        trial.set_trial_id(2)
        assert trial.get_trial_id() == 2

        trial = Trial(42, sequence=sequence, audio=audio)
        assert trial.get_trial_id() == 42
        trial.set_trial_id(2)
        assert trial.get_trial_id() == 2

        trial = Trial(audio=audio)
        assert trial.get_trial_id() == "test_audio_1"
        trial.set_trial_id(2)
        assert trial.get_trial_id() == 2

    def test_get_condition(self):
        trial = Trial(1, "English")
        assert trial.get_condition() == "English"
        trial.set_condition("German")
        assert trial.get_condition() == "German"

        trial = Trial(2)
        assert trial.get_condition() is None
        
    def test_get_sequence(self):
        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)
        
        trial = Trial(1, "English")
        assert trial.get_sequence() is None
        trial.set_sequence(sequence)
        assert trial.get_sequence() == sequence
        assert id(trial.get_sequence()) == id(sequence)
        
        trial = Trial(2, "Spanish", sequence)
        assert trial.get_sequence() == sequence
        assert id(trial.get_sequence()) == id(sequence)
        
        trial = Trial(3, "German", audio=audio)
        assert trial.get_sequence() is None
        
        trial = Trial(4, "French", sequence, audio)
        assert trial.get_sequence() == sequence
        assert id(trial.get_sequence()) == id(sequence)
        
    def test_get_audio(self):
        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)

        trial = Trial(1, "English")
        assert trial.get_audio() is None
        trial.set_audio(audio)
        assert trial.get_audio() == audio
        assert id(trial.get_audio()) == id(audio)

        trial = Trial(2, "Spanish", sequence)
        assert trial.get_audio() is None

        trial = Trial(3, "German", audio=audio)
        assert trial.get_audio() == audio
        assert id(trial.get_audio()) == id(audio)

        trial = Trial(4, "French", sequence, audio)
        assert trial.get_audio() == audio
        assert id(trial.get_audio()) == id(audio)

    def test_get_audio_kind(self):
        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)
        envelope = Envelope("test_envelopes/test_audio_1_envelope.mat", verbosity=0)

        trial = Trial(1, "Polish", sequence, audio)
        assert trial.get_audio_kind() == "Audio"
        trial = Trial(2, "Danish", sequence, envelope)
        assert trial.get_audio_kind() == "Envelope"
        trial.set_audio(audio)
        assert trial.get_audio_kind() == "Audio"
        trial = Trial(3)
        assert trial.get_audio_kind() is None

    def test_has_sequence(self):
        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        trial = Trial(1)
        assert trial.has_sequence() == False
        trial.set_sequence(sequence)
        assert trial.has_sequence() == True
        trial = Trial(2, sequence=sequence)
        assert trial.has_sequence() == True
        
    def test_has_audio(self):
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)
        trial = Trial(1)
        assert trial.has_audio() == False
        trial.set_audio(audio)
        assert trial.has_audio() == True
        trial = Trial(2, audio=audio)
        assert trial.has_audio() == True

    def test_are_timestamps_equal(self):
        sequence = Sequence("test_sequences/test_sequence_1.mat", verbosity=0)
        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)
        trial = Trial(1, "Norwegian", sequence, audio)
        assert trial.are_timestamps_equal() == False

        audio = Audio([4, 8, 15], 1000)
        trial = Trial(2, "Finnish", sequence, audio)
        assert trial.are_timestamps_equal() == True

    def test_eq(self):
        sequence_1 = Sequence("test_sequences/test_sequence_6.tsv", verbosity=0)

        sequence_2 = Sequence()
        pose = Pose(0)
        pose.add_joint(Joint("Head", -2.819374393, -1.881188978, 0.412664491))
        pose.add_joint(Joint("HandRight", 1.445902298, 1.033955007, 2.049614771))
        pose.add_joint(Joint("HandLeft", 2.706231532, -0.22258201, -1.291594811))
        sequence_2.add_pose(pose, verbosity=0)

        audio = Audio("test_audios/test_audio_1.mat", verbosity=0)

        trial_1 = Trial(1, "Dutch", sequence_1, audio)
        trial_2 = Trial(1, "Italian", sequence_2, audio)
        assert trial_1 == trial_2

        trial_1.set_trial_id(2)
        assert trial_1 != trial_2