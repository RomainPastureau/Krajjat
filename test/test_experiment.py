"""Tests the Experiment methods from the toolbox."""
import unittest

from krajjat.classes import Experiment, Subject, Sequence, Trial, Envelope
from krajjat.tool_functions import read_pandas_dataframe


class TestsExperimentMethods(unittest.TestCase):

    def test_init(self):
        exp = Experiment("Test")
        assert exp.name == "Test"
        assert len(exp.subjects) == 0

    def test_get_name(self):
        exp = Experiment("Test")
        assert exp.get_name() == "Test"

        exp = Experiment()
        assert exp.get_name() is None

    def test_set_name(self):
        exp = Experiment()
        assert exp.get_name() is None
        exp.set_name("Test")
        assert exp.get_name() == "Test"

        exp = Experiment("Test")
        assert exp.get_name() == "Test"
        exp.set_name("Prueba")
        assert exp.get_name() == "Prueba"

    def test_add_subject(self):
        exp = Experiment()

        subject1 = Subject("Bob")
        exp.add_subject(subject1)
        assert len(exp.subjects) == 1

        subject2 = Subject("Alice")
        exp.add_subject(subject2)
        assert len(exp.subjects) == 2

        subject3 = Subject("Alice")
        self.assertRaises(Exception, exp.add_subject, subject3)
        exp.add_subject(subject3, True)
        assert len(exp.subjects) == 2

        subject4 = Subject()
        self.assertRaises(Exception, exp.add_subject, subject4)

    def test_add_subjects(self):
        exp = Experiment()

        subject1 = Subject("Alice")
        subject2 = Subject("Bob")
        subject3 = Subject("Charlie")
        exp.add_subjects(subject1, subject2, subject3)
        assert len(exp.subjects) == 3

        subject4 = Subject("Charlie")
        self.assertRaises(Exception, exp.add_subjects, subject4)
        exp.add_subjects(subject4, replace_if_exists=True)
        assert len(exp.subjects) == 3

    def test_get_subject(self):
        exp = Experiment()

        subject1 = Subject("Alice")
        exp.add_subject(subject1)
        assert exp.get_subject("Alice") == subject1
        self.assertRaises(KeyError, exp.get_subject, "Bob")
        
    def test_get_subjects(self):
        exp = Experiment()
        subject1 = Subject("Alice", "Control", "F", 23)
        subject1.language = "English"
        subject2 = Subject("Bob", "Experimental", "M", 99)
        subject2.language = "English"
        subject3 = Subject("Charlie", "Control", "M", 48)
        subject3.language = "Spanish"
        exp.add_subjects(subject1, subject2, subject3)

        subjects = exp.get_subjects()
        assert len(subjects) == 3
        assert subject1.name in subjects
        assert subject2.name in subjects
        assert subject3.name in subjects

        subjects = exp.get_subjects(["Alice", "Charlie"])
        assert len(subjects) == 2
        assert subject1.name in subjects
        assert subject3.name in subjects

        subjects = exp.get_subjects(None, "Control")
        assert len(subjects) == 2
        assert subject1.name in subjects
        assert subject3.name in subjects

        subjects = exp.get_subjects(return_type="list")
        assert len(subjects) == 3
        assert subject1 in subjects
        assert subject2 in subjects
        assert subject3 in subjects

        subjects = exp.get_subjects(language="English")
        assert len(subjects) == 2
        assert subject1.name in subjects
        assert subject2.name in subjects

    def test_get_subjects_name(self):
        exp = Experiment()
        subject1 = Subject("Alice", "Control", "F", 23)
        subject1.language = "English"
        subject2 = Subject("Bob", "Experimental", "M", 99)
        subject2.language = "English"
        subject3 = Subject("Charlie", "Control", "M", 48)
        subject3.language = "Spanish"
        exp.add_subjects(subject1, subject2, subject3)

        assert exp.get_subjects_names() == ["Alice", "Bob", "Charlie"]
        assert exp.get_subjects_names(group="Control") == ["Alice", "Charlie"]
        assert exp.get_subjects_names(language="English") == ["Alice", "Bob"]

    def test_remove_subject(self):
        exp = Experiment()
        subject1 = Subject("Alice", "Control", "F", 23)
        subject2 = Subject("Bob", "Experimental", "M", 99)
        subject3 = Subject("Charlie", "Control", "M", 48)
        exp.add_subjects(subject1, subject2, subject3)
        exp.remove_subject("Alice")
        assert len(exp.subjects) == 2
        assert "Bob" in exp.subjects
        assert "Charlie" in exp.subjects

    def test_get_number_of_subjects(self):
        exp = Experiment()
        subject1 = Subject("Alice", "Control", "F", 23)
        subject2 = Subject("Bob", "Experimental", "M", 99)
        subject3 = Subject("Charlie", "Control", "M", 48)
        exp.add_subjects(subject1, subject2, subject3)
        assert exp.get_number_of_subjects() == 3

    def test_get_joint_labels(self):
        subject = Subject("Bob", None, "M", 99)
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        trial1 = Trial(1, None, seq1)
        trial2 = Trial(2, None, seq2)
        trial3 = Trial(3, None, seq3)
        subject.add_trials(trial1, trial2, trial3, verbosity=0)
        experiment = Experiment()
        experiment.add_subject(subject)
        assert experiment.get_joint_labels() == ["Head", "HandRight", "HandLeft"]

        experiment = Experiment()
        subject = Subject("Charlie", None, "X", 97)
        seq7 = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        subject.add_trial(Trial(1, None, seq7), verbosity=0)
        experiment.add_subject(subject)
        assert experiment.get_joint_labels() == ["Head"]
        subject.add_trial(Trial(2, None, seq1), verbosity=0)
        assert experiment.get_joint_labels() == ["Head", "HandRight", "HandLeft"]

    def test_get_dataframe(self):
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        aud1 = Envelope([4, 8, 15], 1000, verbosity=0)
        trial1 = Trial(1, "English", seq1, aud1)
        trial1.visit = 1

        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        aud2 = Envelope([16, 23, 42], 1000, verbosity=0)
        trial2 = Trial(2, "Spanish", seq2, aud2)
        trial2.visit = 1

        subject1 = Subject("Alice", 1, "F", 20)
        subject1.add_trials(trial1, trial2, verbosity=0)

        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud3 = Envelope([1, 2, 3], 1000, verbosity=0)
        trial3 = Trial(1, "English", seq3, aud3)
        trial3.visit = 1

        seq4 = Sequence("test_sequences/test_sequence_4.tsv", verbosity=0)
        aud4 = Envelope([4, 5, 6], 1000, verbosity=0)
        trial4 = Trial(2, "Spanish", seq4, aud4)
        trial4.visit = 2

        subject2 = Subject("Bob", 2, "M", 99)
        subject2.add_trials(trial3, trial4, verbosity=0)

        experiment = Experiment("BodyLingual")
        experiment.add_subjects(subject1, subject2)

        df = experiment.get_dataframe("distance", "envelope", 1000,
                                      exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)

        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

    def test_save_dataframe(self):
        seq1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        aud1 = Envelope([4, 8, 15], 1000, verbosity=0)
        trial1 = Trial(1, "English", seq1, aud1)
        trial1.visit = 1

        seq2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        aud2 = Envelope([16, 23, 42], 1000, verbosity=0)
        trial2 = Trial(2, "Spanish", seq2, aud2)
        trial2.visit = 1

        subject1 = Subject("Alice", 1, "F", 20)
        subject1.add_trials(trial1, trial2, verbosity=0)

        seq3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        aud3 = Envelope([1, 2, 3], 1000, verbosity=0)
        trial3 = Trial(1, "English", seq3, aud3)
        trial3.visit = 1

        seq4 = Sequence("test_sequences/test_sequence_4.tsv", verbosity=0)
        aud4 = Envelope([4, 5, 6], 1000, verbosity=0)
        trial4 = Trial(2, "Spanish", seq4, aud4)
        trial4.visit = 2

        subject2 = Subject("Bob", 2, "M", 99)
        subject2.add_trials(trial3, trial4, verbosity=0)

        experiment = Experiment("BodyLingual")
        experiment.add_subjects(subject1, subject2)

        # TSV
        experiment.save_dataframe("test_dataframes/test_dataframe.tsv", sequence_measure="distance",
                                  audio_measure="envelope", sampling_frequency=1000,
                                  exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)
        df = read_pandas_dataframe("test_dataframes/test_dataframe.tsv")
        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

        # CSV
        experiment.save_dataframe("test_dataframes/test_dataframe.csv", sequence_measure="distance",
                                  audio_measure="envelope", sampling_frequency=1000,
                                  exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)
        df = read_pandas_dataframe("test_dataframes/test_dataframe.csv")
        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

        # Pickle
        experiment.save_dataframe("test_dataframes/test_dataframe.pkl", sequence_measure="distance",
                                  audio_measure="envelope", sampling_frequency=1000,
                                  exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)
        df = read_pandas_dataframe("test_dataframes/test_dataframe.pkl")
        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

        # MAT
        experiment.save_dataframe("test_dataframes/test_dataframe.mat", sequence_measure="distance",
                                  audio_measure="envelope", sampling_frequency=1000,
                                  exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)
        df = read_pandas_dataframe("test_dataframes/test_dataframe.mat")
        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

        # Excel
        experiment.save_dataframe("test_dataframes/test_dataframe.xlsx", sequence_measure="distance",
                                  audio_measure="envelope", sampling_frequency=1000,
                                  exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)
        df = read_pandas_dataframe("test_dataframes/test_dataframe.xlsx")
        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

        # JSON
        experiment.save_dataframe("test_dataframes/test_dataframe.json", sequence_measure="distance",
                                  audio_measure="envelope", sampling_frequency=1000,
                                  exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)
        df = read_pandas_dataframe("test_dataframes/test_dataframe.json")
        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

        # Parquet
        experiment.save_dataframe("test_dataframes/test_dataframe.gzip", sequence_measure="distance",
                                  audio_measure="envelope", sampling_frequency=1000,
                                  exclude_columns=["group", "condition"], include_columns=["visit"], verbosity=0)
        df = read_pandas_dataframe("test_dataframes/test_dataframe.gzip")
        assert df.shape == (36, 8)
        assert sorted(df["subject"].unique()) == ["Alice", "Bob"]

    def test_len(self):
        subject1 = Subject("Bob", None, "M", 99)
        subject2 = Subject("Charlie", None, "X", 97)
        experiment = Experiment()
        experiment.add_subjects(subject1, subject2)
        assert len(experiment) == 2

    def test_getitem(self):
        subject = Subject("Bob", None, "M", 99)
        experiment = Experiment()
        experiment.add_subject(subject)
        assert experiment["Bob"] == subject
        self.assertRaises(KeyError, experiment.__getitem__, "Alice")