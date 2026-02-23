"""Tests the subject functions from the toolbox."""

import unittest
from datetime import datetime, timedelta

import numpy as np

from krajjat.classes import Subject, Trial, Sequence, Audio

class TestSubject(unittest.TestCase):

    def test_init(self):
        subject = Subject()
        assert subject.name is None
        assert subject.group is None
        assert subject.gender is None
        assert subject.age is None
        assert len(subject.trials) == 0

        subject = Subject("Joe", "1", "M", 42)
        assert subject.name == "Joe"
        assert subject.group == "1"
        assert subject.gender == "M"
        assert subject.age == 42

    def test_set_name(self):
        subject = Subject()
        assert subject.get_name() is None
        subject.set_name("Joe")
        assert subject.get_name() == "Joe"

        subject = Subject("Harry")
        assert subject.get_name() == "Harry"
        subject.set_name("Joe")
        assert subject.get_name() == "Joe"

    def test_set_group(self):
        subject = Subject()
        assert subject.get_group() is None
        subject.set_group("1")
        assert subject.get_group() == "1"

        subject = Subject("Harry", "1")
        assert subject.get_group() == "1"
        subject.set_group(2)
        assert subject.get_group() == 2

    def test_set_gender(self):
        subject = Subject()
        assert subject.get_gender() is None
        subject.set_gender("M")
        assert subject.get_gender() == "M"

        subject = Subject("Harry", "1", "M")
        assert subject.get_gender() == "M"
        subject.set_gender("F")
        assert subject.get_gender() == "F"

    def test_set_age(self):
        subject = Subject()
        assert subject.get_age() is None
        subject.set_age(42)
        assert subject.get_age() == 42

        subject = Subject("Harry", "1", "M", 42)
        assert subject.get_age() == 42
        subject.set_age(21)
        assert subject.get_age() == 21

    def test_set_age_from_dob(self):
        subject = Subject()
        assert subject.get_age() is None
        subject.set_age_from_dob("1990-01-01")
        assert subject.get_age() == datetime.now().year - 1990
        subject.set_age_from_dob("2000-01-01", "01/01/2010")
        assert subject.get_age() == 10
        subject.set_age_from_dob("2000-01-01", "31/12/2009")
        assert subject.get_age() == 9
        subject.set_age_from_dob((2005, 1, 1), (2011, 12, 31))
        assert subject.get_age() == 6
        subject.set_age_from_dob(datetime(2009, 1, 1), datetime(2017, 12, 31))
        assert subject.get_age() == 8

    def test_get_name(self):
        # See test_set_name
        pass

    def test_get_group(self):
        # See test_set_group
        pass

    def test_get_gender(self):
        # See test_set_gender
        pass

    def test_get_age(self):
        # See test_set_age
        pass

    def test_get_joint_labels(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, None, seq1)
        trial2 = Trial(2, None, seq2)
        trial3 = Trial(3, None, seq3)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)
        assert subject.get_joint_labels() == ["Head", "HandRight", "HandLeft"]

        subject = Subject("Charlie", None, "X", 97)
        seq7 = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        subject.add_trial(Trial(1, None, seq7), verbosity=0)
        assert subject.get_joint_labels() == ["Head"]
        subject.add_trial(Trial(2, None, seq1), verbosity=0)
        assert subject.get_joint_labels() == ["Head", "HandRight", "HandLeft"]

    def test_get_trial(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, None, seq1)
        trial2 = Trial(2, None, seq2)
        trial3 = Trial(3, None, seq3)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.get_trial(1) == trial1
        assert subject.get_trial(2) == trial2
        assert subject.get_trial(3) == trial3
        self.assertRaises(KeyError, subject.get_trial, 4)

    def test_get_trials(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, "English", seq1)
        trial1.visit = 1
        trial2 = Trial(2, "Spanish", seq2)
        trial2.visit = 1
        trial3 = Trial(3, "English", seq3)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        trials = subject.get_trials()
        assert len(trials) == 3
        assert trial1.trial_id in trials
        assert trial2.trial_id in trials
        assert trial3.trial_id in trials

        trials = subject.get_trials([1, 3])
        assert len(trials) == 2
        assert trial1.trial_id in trials
        assert trial3.trial_id in trials

        trials = subject.get_trials(None, "English")
        assert len(trials) == 2
        assert trial1.trial_id in trials
        assert trial3.trial_id in trials

        trials = subject.get_trials(return_type="list")
        assert len(trials) == 3
        assert trial1 in trials
        assert trial2 in trials
        assert trial3 in trials

        trials = subject.get_trials(visit=1)
        assert len(trials) == 2
        assert trial1.trial_id in trials
        assert trial2.trial_id in trials

    def test_get_trials_id(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, "English", seq1)
        trial1.visit = 1
        trial2 = Trial(2, "Spanish", seq2)
        trial2.visit = 1
        trial3 = Trial(3, "English", seq3)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.get_trials_id() == [1, 2, 3]
        assert subject.get_trials_id(condition="English") == [1, 3]
        assert subject.get_trials_id(visit=2) == [3]

    def test_get_number_of_trials(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, "English", seq1)
        trial1.visit = 1
        trial2 = Trial(2, "Spanish", seq2)
        trial2.visit = 1
        trial3 = Trial(3, "English", seq3)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.get_number_of_trials() == 3
        assert subject.get_number_of_trials(condition="English") == 2
        assert subject.get_number_of_trials(condition="Spanish") == 1
        assert subject.get_number_of_trials(visit=1) == 2

    def test_get_sequence(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, None, seq1)
        trial2 = Trial(2, None, seq2)
        trial3 = Trial(3, None, seq3)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.get_sequence(3) == seq3

    def test_get_sequences(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, "English", seq1)
        trial1.visit = 1
        trial2 = Trial(2, "Spanish", seq2)
        trial2.visit = 1
        trial3 = Trial(3, "English", seq3)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert len(subject.get_sequences(1)) == 1
        assert subject.get_sequences(1)[1] == seq1
        assert len(subject.get_sequences(3)) == 1
        assert subject.get_sequences(3)[3] == seq3

        assert len(subject.get_sequences(1, return_type="list")) == 1
        assert subject.get_sequences(1, return_type="list")[0] == seq1
        assert len(subject.get_sequences(3, return_type="list")) == 1
        assert subject.get_sequences(3, return_type="list")[0] == seq3

        assert len(subject.get_sequences([1, 2, 3])) == 3
        assert subject.get_sequences([1, 2, 3])[1] == seq1

        assert len(subject.get_sequences(None, condition="English")) == 2
        assert 1 in subject.get_sequences(None, condition="English")
        assert 3 in subject.get_sequences(None, condition="English")

        assert len(subject.get_sequences(None, visit=2)) == 1
        assert 3 in subject.get_sequences(None, visit=2)

    def test_get_audio(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial3 = Trial("R003", "English", seq3, aud3)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.get_audio("R001") == aud1
        
    def test_get_audios(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial1.visit = 1
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial2.visit = 1
        trial3 = Trial("R003", "English", seq3, aud3)
        trial3.visit = 2       
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert len(subject.get_audios("R001")) == 1
        assert subject.get_audios("R001")["R001"] == aud1
        assert len(subject.get_audios("R003")) == 1
        assert subject.get_audios("R003")["R003"] == aud3

        assert len(subject.get_audios("R001", return_type="list")) == 1
        assert subject.get_audios("R001", return_type="list")[0] == aud1
        assert len(subject.get_audios("R003", return_type="list")) == 1
        assert subject.get_audios("R003", return_type="list")[0] == aud3

        assert len(subject.get_audios(["R001", "R002", "R003"])) == 3
        assert subject.get_audios(["R001", "R002", "R003"])["R001"] == aud1

        assert len(subject.get_audios(None, condition="English")) == 2
        assert "R001" in subject.get_audios(None, condition="English")
        assert "R003" in subject.get_audios(None, condition="English")

        assert len(subject.get_audios(None, visit=2)) == 1
        assert "R003" in subject.get_audios(None, visit=2)

    def test_get_recording_session_duration(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq1.set_date_recording(datetime(2020, 1, 1, 10, 0, 0))
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq2.set_date_recording(datetime(2020, 1, 1, 10, 3, 22))
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        seq3.set_date_recording(datetime(2020, 1, 1, 10, 7, 14))
        trial1 = Trial(1, None, seq1)
        trial2 = Trial(2, None, seq2)
        trial3 = Trial(3, None, seq3)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.get_recording_session_duration() == timedelta(minutes=7, seconds=14, microseconds=2000)

    def test_get_subject_height(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        seq2 = Sequence("test_sequences/sequence_ainhoa_trimmed.tsv", verbosity=0)
        trial1 = Trial(1, None, seq1)
        trial2 = Trial(2, None, seq2)
        subject.add_trials(trial1, trial2, verbosity=0)

        assert np.isclose(subject.get_height(verbosity=0), 1.6194760840231472)

    def test_get_subject_arm_length(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/sequence_ainhoa.json", verbosity=0)
        seq2 = Sequence("test_sequences/sequence_ainhoa_trimmed.tsv", verbosity=0)
        trial1 = Trial(1, None, seq1)
        trial2 = Trial(2, None, seq2)
        subject.add_trials(trial1, trial2, verbosity=0)

        assert np.isclose(subject.get_arm_length("left", verbosity=0), 0.5065866095454166)
        assert np.isclose(subject.get_arm_length("right", verbosity=0), 0.5068297391988286)

    def test_has_sequence_in_each_trial(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial1.visit = 1
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial2.visit = 1
        trial3 = Trial("R003", "English", None, None)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.has_sequence_in_each_trial() == False
        subject.trials["R003"].set_sequence(seq3)
        subject.trials["R003"].set_audio(aud3)
        assert subject.has_sequence_in_each_trial() == True

    def test_has_audio_in_each_trial(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial1.visit = 1
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial2.visit = 1
        trial3 = Trial("R003", "English", None, None)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert subject.has_audio_in_each_trial() == False
        subject.trials["R003"].set_sequence(seq3)
        subject.trials["R003"].set_audio(aud3)
        assert subject.has_audio_in_each_trial() == True

    def test_are_timestamps_equal_per_trial(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio([4, 8, 15], 1000, verbosity=0)
        aud2 = Audio([16, 23, 42], 1000, verbosity=0)
        aud3 = Audio([108, 109, 110, 111], 1000, verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial1.visit = 1
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial2.visit = 1
        trial3 = Trial("R003", "English", seq3, aud3)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, verbosity=0)
        assert subject.are_timestamps_equal_per_trial() == True
        subject.add_trial(trial3, verbosity=0)
        assert subject.are_timestamps_equal_per_trial() == False

    def test_are_frequencies_equal(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio([4, 8, 15], 1000, verbosity=0)
        aud2 = Audio([16, 23, 42], 1000, verbosity=0)
        aud3 = Audio([108, 109, 110], 500, verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial1.visit = 1
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial2.visit = 1
        trial3 = Trial("R003", "English", seq3, aud3)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, verbosity=0)
        assert subject.are_frequencies_equal() == True
        subject.add_trial(trial3, verbosity=0)
        assert subject.are_frequencies_equal() == False

    def test_add_trial(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        subject.add_trial(trial1, verbosity=0)
        assert len(subject.trials) == 1
        self.assertRaises(Exception, subject.add_trial, trial1, verbosity=0)
        subject.add_trial(trial1, True, verbosity=0)
        assert len(subject.trials) == 1
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        subject.add_trial(trial2, True, verbosity=0)
        assert len(subject.trials) == 2
        trial3 = Trial("R003", "English", seq1, aud1)
        subject.add_trial(trial3, True, verbosity=0)
        assert len(subject.trials) == 3

    def test_add_trials(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial1.visit = 1
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial2.visit = 1
        trial3 = Trial("R003", "English", None, None)
        trial3.visit = 2
        subject.add_trials(trial1, trial2, trial3, verbosity=0)
        assert len(subject.trials) == 3

        subject.add_trials(trial1, replace_if_exists=True, verbosity=0)
        assert len(subject.trials) == 3

        self.assertRaises(Exception, subject.add_trials, trial1, verbosity=0)

    def test_repr(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial3 = Trial("R003", "English", None, None)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)

        assert repr(subject) == "Subject Bob (M, 99) · None · 3 trials, 2 sequences, 2 audios"

    def test_len(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial3 = Trial("R003", "English", None, None)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)
        assert len(subject) == 3

    def test_getitem(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial3 = Trial("R003", "English", None, None)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)
        assert subject["R001"] == trial1
        self.assertRaises(KeyError, subject.__getitem__, "R004")

    def test_eq(self):
        subject_1 = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial3 = Trial("R003", "English", None, None)
        subject_1.add_trials(trial1, trial2, trial3, verbosity=0)

        subject_2 = Subject("Jane", "First", "F", 42)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud1 = Audio("test_audios/test_audio_1.wav", verbosity=0)
        aud2 = Audio("test_audios/test_audio_2.wav", verbosity=0)
        aud3 = Audio("test_audios/test_audio_3.wav", verbosity=0)
        trial1 = Trial("R001", "English", seq1, aud1)
        trial2 = Trial("R002", "Spanish", seq2, aud2)
        trial3 = Trial("R003", "English", None, None)
        subject_2.add_trials(trial2, trial3, trial1, verbosity=0)

        assert subject_1 == subject_2

        subject_3 = Subject("Bob", None, "M", 99)
        subject_3.add_trials(trial1, trial3, verbosity=0)
        assert subject_1 != subject_3