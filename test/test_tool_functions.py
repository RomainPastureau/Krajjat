"""Tests the tool functions from the toolbox."""

import unittest
from datetime import datetime as dt

# from matplotlib import pyplot as plt

from krajjat.classes.sequence import Sequence
from krajjat.tool_functions import *


class TestsToolFunctions(unittest.TestCase):

    def test_compute_subpath(self):
        path_1 = "A:/b/c/d/e/f/g/h/i/j"
        path_2 = "A:/b/c/d/e/f"
        path_3 = "A:/b/c/d/e/f/g/h/i/j/"
        path_4 = "A:/b/c/d/e/f/"
        path_5 = "B:/c/d/e/f/"

        path_1b = "A:\\b\\c\\d\\e\\f\\g\\h\\i\\j"
        path_2b = "A:\\b\\c\\d\\e\\f"

        assert compute_subpath(path_1, path_2) == "g\\h\\i\\j"
        assert compute_subpath(path_3, path_2) == "g\\h\\i\\j"
        assert compute_subpath(path_3, path_1) == ""
        assert compute_subpath(path_4, path_1) == "g\\h\\i\\j"
        self.assertRaises(NotASubPathException, compute_subpath, path_5, path_1)

        assert compute_subpath(path_3, path_2, remove_ending_separators=False) == "g\\h\\i\\j"
        assert compute_subpath(path_2, path_3, remove_leading_separators=False) == "\\g\\h\\i\\j"

        assert compute_subpath(path_2, path_1) == "g\\h\\i\\j"
        assert compute_subpath(path_2, path_3) == "g\\h\\i\\j"
        assert compute_subpath(path_1, path_3) == ""
        assert compute_subpath(path_1, path_4) == "g\\h\\i\\j"
        self.assertRaises(NotASubPathException, compute_subpath, path_1, path_5)

        assert compute_subpath(path_1b, path_2b, separator="\\") == "g\\h\\i\\j"
        assert compute_subpath(path_2b, path_1b, separator="\\") == "g\\h\\i\\j"

        assert compute_subpath(path_1, path_3) == ""

    def test_get_difference_paths(self):
        path_1 = "A:/b/c/d/e/f/g/h/i/j"
        path_2 = "A:/b/c/d/e/f/k/h/i/j"
        path_3 = "A:/b/c/d/e"
        path_4 = "A:/b/c/d/e/k"

        path_1b = "A:\\b\\c\\d\\e\\f\\g\\h\\i\\j"
        path_2b = "A:\\b\\c\\d\\e\\f\\k\\h\\i\\j"

        assert get_difference_paths(path_1, path_1) == [[], []]
        assert get_difference_paths(path_1, path_2) == [["g"], ["k"]]
        assert get_difference_paths(path_1, path_3) == [["f", "g", "h", "i", "j"], []]
        assert get_difference_paths(path_1, path_4) == [["f", "g", "h", "i", "j"], ["k"]]
        assert get_difference_paths(path_4, path_1) == [["k"], ["f", "g", "h", "i", "j"]]

        assert get_difference_paths(path_1b, path_2b, separator="\\") == [["g"], ["k"]]

    def test_get_objects_paths(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        sequence_3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)

        assert get_objects_paths(sequence_1, sequence_2, sequence_3) == \
               [op.join("test_sequences", "test_sequence_1.tsv"), op.join("test_sequences", "test_sequence_2.tsv"),
                op.join("test_sequences", "test_sequence_3.tsv")]

    def test_sort_files_trailing_index(self):
        path = "test_sequences/test_sequence_individual"

        ordered_files = sort_files_trailing_index(path, "tsv", verbosity=0)
        assert ordered_files == ["test_sequence_ind_" + str(i).zfill(2) + ".tsv" for i in range(12)]

        ordered_files = sort_files_trailing_index(path, None, "", True, True, False,
                                                  verbosity=0)
        assert ordered_files == ["test_sequence_ind_" + str(i).zfill(2) + ".tsv" for i in range(12)]

    # Name functions
    def test_get_objects_names(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", name="seq1", verbosity=0)
        sequence_2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        sequence_3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)

        assert get_objects_names(sequence_1, sequence_2, sequence_3) == ['seq1', 'test_sequence_2',
                                                                                'test_sequence_3']

    # Sequence comparison functions
    def test_compute_different_joints(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        sequence_4 = Sequence("test_sequences/test_sequence_4.tsv", verbosity=0)
        sequence_5 = Sequence("test_sequences/test_sequence_5.tsv", verbosity=0)

        assert compute_different_joints(sequence_1, sequence_2, 5, 0) == (9, 9)
        assert compute_different_joints(sequence_1, sequence_4, 5, 0) == (1, 9)
        self.assertRaises(DifferentSequencesLengthsException, compute_different_joints, sequence_1, sequence_5)

    def test_align_two_sequences(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", time_unit ="s", verbosity=0)
        sequence_4 = Sequence("test_sequences/test_sequence_4.tsv", time_unit ="s", verbosity=0)
        sequence_5 = Sequence("test_sequences/test_sequence_5.tsv", time_unit ="s", verbosity=0)

        assert align_two_sequences(sequence_5, sequence_4, verbosity=0) == (2, 0)
        assert align_two_sequences(sequence_4, sequence_5, verbosity=0) == (0, 2)
        assert align_two_sequences(sequence_1, sequence_4, verbosity=0) is None
        assert align_two_sequences(sequence_1, sequence_5, verbosity=0) is None

    def test_align_multiple_sequences(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", time_unit ="s", verbosity=0)
        sequence_4 = Sequence("test_sequences/test_sequence_4.tsv", time_unit ="s", verbosity=0)
        sequence_5 = Sequence("test_sequences/test_sequence_5.tsv", time_unit ="s", verbosity=0)

        expected_timestamps = [[2.0, 3.0, 4.0], [0.0, 1.0, 2.0, 3.0, 4.0]]
        for i in range(len(expected_timestamps)):
            assert np.allclose(align_multiple_sequences(sequence_4, sequence_5, verbosity=0)[i], expected_timestamps[i])
        expected_timestamps = [[0.0, 1.0, 2.0], [2.0, 3.0, 4.0], [0.0, 1.0, 2.0, 3.0, 4.0]]
        for i in range(len(expected_timestamps)):
            assert np.allclose(align_multiple_sequences(sequence_1, sequence_4, sequence_5, verbosity=0)[i],
                               expected_timestamps[i])

    def test_sort_sequences_by_date(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        sequence_2 = Sequence("test_sequences/test_sequence_2.tsv", verbosity=0)
        sequence_3 = Sequence("test_sequences/test_sequence_3.tsv", verbosity=0)
        sequence_4 = Sequence("test_sequences/test_sequence_4.tsv", verbosity=0)

        sequence_1.set_date_recording(dt(1999, 12, 31, 23, 59, 59))
        sequence_2.set_date_recording(dt(2015, 8, 4, 16, 23, 42))
        sequence_3.set_date_recording(dt(2015, 8, 4, 16, 23, 41))

        assert sort_sequences_by_date(sequence_1, sequence_2, sequence_3) == [sequence_1, sequence_3,
                                                                                         sequence_2]
        self.assertRaises(MissingRecordingDateException, sort_sequences_by_date, sequence_1, sequence_2, sequence_3, sequence_4)

    # File reading functions
    def test_get_system_csv_separator(self):
        assert get_system_csv_separator() in [";", ","]

    def test_get_filetype_separator(self):
        assert get_filetype_separator("csv") in [";", ","]
        assert get_filetype_separator("tsv") == "\t"
        assert get_filetype_separator("txt") == "\t"

    def test_read_json(self):
        assert read_json("test_files/test_json_ansi.json") == {"test": [1, 2, 3, "é&*ç"]}
        assert read_json("test_files/test_json_utf8.json") == {"test": [1, 2, 3, "é&*ç"]}
        assert read_json("test_files/test_json_utf16.json") == {"test": [1, 2, 3, "é&*ç"]}

    def test_read_text_table(self):
        data, metadata = read_text_table("test_sequences/test_sequence_6.tsv", convert_strings=False, verbosity=0)
        assert data == [['Timestamp', 'Head_X', 'Head_Y', 'Head_Z', 'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                         'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                        ['0', '-2.819374393', '-1.881188978', '0.412664491', '1.445902298', '1.033955007',
                         '2.049614771', '2.706231532', '-0.22258201', '-1.291594811']]
        assert metadata == {"Number of poses": "1", "Number of joints": "3"}

        data, metadata = read_text_table("test_sequences/test_sequence_6.tsv", convert_strings=True, verbosity=0)
        assert data == [['Timestamp', 'Head_X', 'Head_Y', 'Head_Z', 'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                         'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                        [0, -2.819374393, -1.881188978, 0.412664491, 1.445902298, 1.033955007,
                         2.049614771, 2.706231532, -0.22258201, -1.291594811]]
        assert metadata == {"Number of poses": 1, "Number of joints": 3}

    def test_read_xlsx(self):
        data, metadata = read_xlsx("test_sequences/test_sequence_1.xlsx", metadata_sheet=1, verbosity=0)
        assert data == [['Timestamp', 'Head_X', 'Head_Y', 'Head_Z', 'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                         'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                        [0, 0.160617024, 0.494735048, -0.453307693, 0.127963375, 0.873208589, 0.408531847,
                         -1.395065714, 2.653738732, -0.483163821],
                        [0.001, 1.769412418, 0.885312165, -0.785718175, 0.948776526, 2.805260745, 2.846927978,
                         -0.80645271, 1.460889453, 2.557279205],
                        [0.002, -1.678118013, 0.85064505, 1.37303521, -1.612589342, -0.059736892, -1.456678185,
                         -1.418789803, 0.283037432, -0.221482265]]
        assert metadata == {"Number of poses": 3, "Number of joints": 3}

        data, metadata = read_xlsx("test_sequences/test_sequence_1.xlsx", read_metadata=False, verbosity=0)
        assert data == [['Timestamp', 'Head_X', 'Head_Y', 'Head_Z', 'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                         'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                        [0, 0.160617024, 0.494735048, -0.453307693, 0.127963375, 0.873208589, 0.408531847,
                         -1.395065714, 2.653738732, -0.483163821],
                        [0.001, 1.769412418, 0.885312165, -0.785718175, 0.948776526, 2.805260745, 2.846927978,
                         -0.80645271, 1.460889453, 2.557279205],
                        [0.002, -1.678118013, 0.85064505, 1.37303521, -1.612589342, -0.059736892, -1.456678185,
                         -1.418789803, 0.283037432, -0.221482265]]
        assert metadata == {}

        data, metadata = read_xlsx("test_sequences/test_sequence_2.xlsx", metadata_sheet="Meta", verbosity=0)
        assert data == [['Timestamp', 'Head_X', 'Head_Y', 'Head_Z', 'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                         'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                        [0, 0.525427568, 2.262117574, 2.732305305, 0.655765136, 0.936800881, 1.239729805,
                         0.777198055, -2.715098339, 0.372867851],
                        [0.001, 0.777046835, -2.710884656, -2.406077931, 2.107607901, -2.836958025, 1.428118596,
                         -0.583576978, -1.515003002, 1.939965554],
                        [0.002, 0.854490334, -0.95024563, 0.889712865, 2.480004585, 0.299735764, -2.328024041,
                         0.738588473, 2.577813565, -0.432393549]]
        assert metadata == {"Number of poses": 3, "Number of joints": 3, 'Joints': ['Head', 'HandRight', 'HandLeft']}

        data, metadata = read_xlsx("test_sequences/test_sequence_3.xlsx", verbosity=0)
        assert data == [['Timestamp', 'Head_X', 'Head_Y', 'Head_Z', 'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                         'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                        [0, 2.675293565, 1.604723176, 2.376943581, -0.57230126, -0.956047805, -0.549442091,
                         -0.986938147, 0.841414942, -1.1938083],
                        [0.001, -2.819374393, -1.881188978, 0.412664491, 1.445902298, 1.033955007, 2.049614771,
                         2.706231532, -0.22258201, -1.291594811],
                        [0.002, 0.307930071, 0.169326298, 0.810794239, 2.489205899, -2.249246333, 1.541833369,
                         0.265601278, -0.027851166, 2.830655356]]
        assert metadata == {}

    def test_read_pandas_dataframe(self):
        data = read_pandas_dataframe("test_files/dataframe_1.csv", verbosity=0)
        assert data["Timestamp"][0] == 0.0
        assert round(data["HandRight_X"][1], 9) == 0.948776526
        assert data["HandLeft_Z"][2] == (-0.221482265)

        data = read_pandas_dataframe("test_files/dataframe_1.gzip", verbosity=0)
        assert data["Timestamp"][0] == 0.0
        assert round(data["HandRight_X"][1], 9) == 0.948776526
        assert data["HandLeft_Z"][2] == (-0.221482265)

        data = read_pandas_dataframe("test_files/dataframe_1.json", verbosity=0)
        assert data["Timestamp"][0] == 0.0
        assert round(data["HandRight_X"][1], 9) == 0.948776526
        assert data["HandLeft_Z"][2] == (-0.221482265)

        data = read_pandas_dataframe("test_files/dataframe_1.pkl", verbosity=0)
        assert data["Timestamp"][0] == 0.0
        assert data["HandRight_X"][1] == 0.948776526
        assert data["HandLeft_Z"][2] == -0.221482265

        data = read_pandas_dataframe("test_sequences/test_sequence_1.xlsx", verbosity=0)
        assert data["Timestamp"][0] == 0.0
        assert data["HandRight_X"][1] == 0.948776526
        assert data["HandLeft_Z"][2] == -0.221482265

    def test_convert_data_from_qtm(self):
        with open("test_sequences/test_sequence_qtm_1.tsv", "r") as f:
            data = f.read().split("\n")
        data, metadata = convert_data_from_qtm(data, verbosity=0)
        assert data == [['Timestamp', 'HeadLeft_X', 'HeadLeft_Y', 'HeadLeft_Z', 'HandInLeft_X', 'HandInLeft_Y',
                         'HandInLeft_Z', 'HandInRight_X', 'HandInRight_Y', 'HandInRight_Z'],
                        [0.0, 0.129864, 0.235617, 1.179573, 0.041594, 0.27970999999999996, 1.2715329999999998,
                         -0.046029, 0.292576, 1.168298],
                        [0.005, 0.129903, 0.235608, 1.17951, 0.041575, 0.279719, 1.271504,
                         -0.046052, 0.292684, 1.168268],
                        [0.01, 0.12981, 0.235604, 1.1795170000000001, 0.041526, 0.279714, 1.271444,
                         -0.04598, 0.292673, 1.168123]]
        assert metadata == {'ORIGIN': 'Qualisys', 'NO_OF_FRAMES': 3, 'NO_OF_CAMERAS': 14, 'NO_OF_MARKERS': 3,
                            'FREQUENCY': 200, 'NO_OF_ANALOG': 0, 'ANALOG_FREQUENCY': 0, 'DESCRIPTION': '--',
                            'TIME_STAMP': ['2000-01-01, 12:34:56.789', '0.123456789'], 'DATA_INCLUDED': '3D'}

        with open("test_sequences/test_sequence_qtm_1.tsv", "r") as f:
            data = f.read().split("\n")
        data, metadata = convert_data_from_qtm(data, standardize_labels=False, verbosity=0)
        assert data == [['Timestamp', 'HeadL_X', 'HeadL_Y', 'HeadL_Z', 'LHandIn_X', 'LHandIn_Y',
                         'LHandIn_Z', 'RHandIn_X', 'RHandIn_Y', 'RHandIn_Z'],
                        [0.0, 0.129864, 0.235617, 1.179573, 0.041594, 0.27970999999999996, 1.2715329999999998,
                         -0.046029, 0.292576, 1.168298],
                        [0.005, 0.129903, 0.235608, 1.17951, 0.041575, 0.279719, 1.271504,
                         -0.046052, 0.292684, 1.168268],
                        [0.01, 0.12981, 0.235604, 1.1795170000000001, 0.041526, 0.279714, 1.271444,
                         -0.04598, 0.292673, 1.168123]]
        assert metadata == {'ORIGIN': 'Qualisys', 'NO_OF_FRAMES': 3, 'NO_OF_CAMERAS': 14, 'NO_OF_MARKERS': 3,
                            'FREQUENCY': 200, 'NO_OF_ANALOG': 0, 'ANALOG_FREQUENCY': 0, 'DESCRIPTION': '--',
                            'TIME_STAMP': ['2000-01-01, 12:34:56.789', '0.123456789'], 'DATA_INCLUDED': '3D'}

    def test_write_text_table(self):
        table = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
        write_text_table(table, "\t", "test_files/test_tsv.tsv", None, None,
                         "utf-8", verbosity=0)
        new_table, _ = read_text_table("test_files/test_tsv.tsv", read_metadata=False)
        assert table == new_table

        metadata = {"a": "b", "c": "d"}
        write_text_table(table, "\t", "test_files/test_tsv.tsv", metadata, "\n",
                         "utf-8", verbosity=0)
        new_table, new_metadata = read_text_table("test_files/test_tsv.tsv", read_metadata=True,
                                                  keyword_data_start="\n", keyword_data_in_table=False)
        assert table == new_table
        assert metadata == new_metadata

        metadata = {"Number of poses": 3, "Number of joints": 3}
        table = [['Timestamp', 'Head_X', 'Head_Y', 'Head_Z', 'HandRight_X', 'HandRight_Y', 'HandRight_Z',
                  'HandLeft_X', 'HandLeft_Y', 'HandLeft_Z'],
                 [0, 0.160617024, 0.494735048, -0.453307693, 0.127963375, 0.873208589, 0.408531847,
                  -1.395065714, 2.653738732, -0.483163821],
                 [0.001, 1.769412418, 0.885312165, -0.785718175, 0.948776526, 2.805260745, 2.846927978,
                  -0.80645271, 1.460889453, 2.557279205],
                 [0.002, -1.678118013, 0.85064505, 1.37303521, -1.612589342, -0.059736892, -1.456678185,
                  -1.418789803, 0.283037432, -0.221482265]]
        write_text_table(table, "\t", "test_files/test_table.tsv", metadata=metadata, verbosity=0)
        new_table, new_metadata = read_text_table("test_files/test_table.tsv")
        assert table == new_table
        assert metadata == new_metadata

    def test_write_xlsx(self):
        table = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
        write_xlsx(table, "test_files/test_xlsx.xlsx", verbosity=0)
        new_table, _ = read_xlsx("test_files/test_xlsx.xlsx", read_metadata=False, verbosity=0)
        assert table == new_table

        table = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
        metadata = {"Number of poses": 3, "Number of joints": 3, 'Joints': ['Head', 'HandRight', 'HandLeft']}
        write_xlsx(table, "test_files/test_xlsx.xlsx", "Data", metadata, "Metadata",
                   verbosity=0)
        new_table, new_metadata = read_xlsx("test_files/test_xlsx.xlsx", read_metadata=True, verbosity=0)
        assert table == new_table
        assert metadata == new_metadata

    def test_find_closest_value_index(self):
        a = np.array([1, 2, 3, 4, 5])
        assert find_closest_value_index(a, 3) == 2
        assert find_closest_value_index(a, 3.1) is None
        assert find_closest_value_index(a, 3.5) is None
        assert find_closest_value_index(a, 3.1, rtol=0.1) == 2

        b = np.array([3, 5, 1, 4, 2])
        assert find_closest_value_index(b, 3) == 0

    def test_resample_data(self):
        # Linear resampling
        array = np.linspace(1, 0, 11)
        original_timestamps = np.linspace(0, 2, 11)
        resampling_frequency = 4

        resampled_array, resampled_timestamps = resample_data(array, original_timestamps, resampling_frequency,
                                                              method="linear", verbosity=0)
        assert np.array_equal(resampled_array, np.array([1, 0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0]))
        assert np.array_equal(resampled_timestamps, np.array([0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]))

        # Cubic resampling
        original_timestamps = np.linspace(0, 3.14, 1000)
        array = np.sin(original_timestamps)
        resampling_frequency = 5

        resampled_array, resampled_timestamps = resample_data(array, original_timestamps, resampling_frequency,
                                                              method="cubic", verbosity=0)

        assert np.allclose(resampled_array, np.array([0., 0.19866933, 0.38941834, 0.56464247, 0.71735609,
                                                         0.84147098, 0.93203909, 0.98544973, 0.9995736, 0.97384763,
                                                         0.90929743, 0.8084964, 0.67546318, 0.51550137, 0.33498815,
                                                         0.14112001]))
        assert np.allclose(resampled_timestamps, np.linspace(0, 3, 16))

    def test_resample_window(self):

        # Linear resampling
        array = np.linspace(1, 0, 11)
        original_timestamps = np.linspace(0, 2, 11)
        resampled_timestamps = np.linspace(0, 2, 9)

        resampled_array = resample_window(array, original_timestamps, resampled_timestamps, 0,
                                          10, 0, 8,
                                          "linear", verbosity=0)

        assert np.array_equal(resampled_array, np.array([1, 0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0]))

    def test_interpolate_data(self):

        # Linear interpolation
        array = np.linspace(1, 0, 11)
        original_timestamps = np.linspace(0, 1, 11)
        interpolation_timestamps = np.linspace(0.05, 0.95, 10)

        new_data, new_timestamps = interpolate_data(array, original_timestamps, interpolation_timestamps, "linear")
        expected_output = np.linspace(0.95, 0.05, 10)

        assert np.allclose(new_data, expected_output)

    def test_pad(self):

        # First test
        data = [5, 4, 3, 2, 1]
        time_points_data = [1, 2, 3, 4, 5]
        time_points_padding = [0, 1, 2, 3, 4, 5, 6, 7]
        padded_data, time_points_padding = pad(data, time_points_data, time_points_padding, 0, verbosity=0)
        assert np.array_equal(padded_data, np.array([0, 5, 4, 3, 2, 1, 0, 0]))

        # Second test: inconsistent values
        data = [5, 4, 3, 2, 1]
        time_points_data = [1, 2, 3.7, 4, 5]
        time_points_padding = [0, 1, 2, 3, 4, 5, 6, 7]
        self.assertRaises(Exception, pad, data, time_points_data, time_points_padding, 0, verbosity=0)

        # Third test: using edges
        data = [5, 4, 3, 2, 1]
        time_points_data = [1, 2, 3, 4, 5]
        time_points_padding = [0, 1, 2, 3, 4, 5, 6, 7]
        padded_data, time_points_padding = pad(data, time_points_data, time_points_padding, "edge", verbosity=0)
        assert np.array_equal(padded_data, np.array([5, 5, 4, 3, 2, 1, 1, 1]))

        # Fourth test: lacking values
        data = [5, 4, 3, 2, 1]
        time_points_data = [1, 2, 3, 5, 6]
        time_points_padding = [0, 1, 2, 3, 4, 5, 6, 7]
        self.assertRaises(Exception, pad, data, time_points_data, time_points_padding, 0, verbosity=0)

    def test_add_delay(self):
        timestamps = [1, 2, 3, 4, 5]
        delayed_timestamps = add_delay(timestamps, 5)
        assert np.array_equal(delayed_timestamps, np.array([6, 7, 8, 9, 10]))

        timestamps = np.array([1, 2, 3, 4, 5])
        delayed_timestamps = add_delay(timestamps, 5)
        assert np.array_equal(delayed_timestamps, np.array([6, 7, 8, 9, 10]))

    def test_calculate_distance(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", verbosity=0)
        joint_1 = sequence_1.poses[0].joints["Head"]
        joint_2 = sequence_1.poses[1].joints["Head"]

        distance = calculate_distance(joint_1, joint_2)
        assert distance == 1.6885703516949238

        distance = calculate_distance(joint_2, joint_1)
        assert distance == 1.6885703516949238

        distance = calculate_distance(joint_1, joint_2, "x")
        assert distance == 1.608795394

        sequence_7 = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        joint_1 = sequence_7.poses[0].joints["Head"]
        joint_2 = sequence_7.poses[1].joints["Head"]

        distance = calculate_distance(joint_1, joint_2)
        assert distance == 1.7320508075688772

        distance = calculate_distance(joint_2, joint_1)
        assert distance == 1.7320508075688772

        distance = calculate_distance(joint_1, joint_2, "x")
        assert distance == 1

    def test_calculate_consecutive_distances(self):
        sequence = Sequence("test_sequences/test_sequence_7.tsv", time_unit="s", verbosity=0)
        x_array = sequence.get_measure("x", "Head")
        x_distances = calculate_consecutive_distances(list(x_array))
        assert np.array_equal(x_distances, [1, 2, 3, 3, 2, 1, 0.5, 0, 0.5, 1, 2, 3, 3, 2, 1])

        x_array = sequence.get_measure("x", "Head",5, 10)
        x_distances = calculate_consecutive_distances(x_array)
        assert np.array_equal(x_distances, [1, 0.5, 0, 0.5, 1])

        distances = calculate_consecutive_distances([4, 8, 15, 16, 23, 42])
        assert np.array_equal(distances, [4, 7, 1, 7, 19])

    def test_calculate_euclidian_distances(self):
        sequence = Sequence("test_sequences/test_sequence_7.tsv", verbosity=0)
        x_array = sequence.get_measure("x", "Head")
        y_array = sequence.get_measure("y", "Head")
        z_array = sequence.get_measure("z", "Head")
        distances = calculate_euclidian_distances(x_array, y_array, z_array)
        expected_distances = [1.7320508075688772, 3.4641016151377544, 5.196152422706632, 5.196152422706632,
                              3.4641016151377544, 1.7320508075688772, 0.8660254037844386, 0.0,
                              0.8660254037844386, 1.7320508075688772, 3.4641016151377544, 5.196152422706632,
                              5.196152422706632, 3.4641016151377544, 1.7320508075688772]
        assert np.array_equal(distances, expected_distances)

        distances = calculate_euclidian_distances([3, 4, 5], [5, 12, 13], [8, 15, 17])
        assert np.array_equal(distances, np.array([9.9498743710662, 2.449489742783178]))

        distances = calculate_euclidian_distances([1, 2, 3], [2, 4, 6], [2, 4, 6])
        assert np.array_equal(distances, [3, 3])

    def test_calculate_derivative(self):

        # Test with trigonometric functions
        nb_points = 10000
        timestamps = np.linspace(0, 4*np.pi, nb_points)
        sin = np.sin(timestamps)
        sin_v = calculate_derivative(sin, 1, 7, 2, freq=1/timestamps[1], mode="interp")
        sin_a = calculate_derivative(sin, 2, 7, 3, freq=1/timestamps[1], mode="interp")
        sin_j = calculate_derivative(sin, 3, 7, 4, freq=1/timestamps[1], mode="interp")
        sin_s = calculate_derivative(sin, 4, 7, 5, freq=1/timestamps[1], mode="interp")

        # import matplotlib.pyplot as plt
        # fig = plt.figure()
        # ax = plt.subplot(5, 1, 1)
        # ax.plot(np.linspace(0, np.pi, nb_points), sin)
        # ax = plt.subplot(5, 1, 2)
        # ax.plot(np.linspace(0, np.pi, nb_points), sin_v)
        # ax = plt.subplot(5, 1, 3)
        # ax.plot(np.linspace(0, np.pi, nb_points), sin_a)
        # ax = plt.subplot(5, 1, 4)
        # ax.plot(np.linspace(0, np.pi, nb_points), sin_j)
        # ax = plt.subplot(5, 1, 5)
        # ax.plot(np.linspace(0, np.pi, nb_points), sin_s)
        # plt.show()

        assert np.allclose(sin_v, np.cos(timestamps), atol=0.005)
        assert np.allclose(sin_a, -np.sin(timestamps), atol=0.005)
        assert np.allclose(sin_j, -np.cos(timestamps), atol=0.005)
        assert np.allclose(sin_s, np.sin(timestamps), atol=0.005)

        # Test with sequence
        path = "test_sequences/sequence_ainhoa.json"
        sequence = Sequence(path, name="seq1", verbosity=0)
        sequence = sequence.resample(100)
        x_array = sequence.get_measure("x", "HandRight")
        y_array = sequence.get_measure("y", "HandRight")
        z_array = sequence.get_measure("z", "HandRight")
        distances = np.sqrt(np.diff(x_array) ** 2 + np.diff(y_array) ** 2 + np.diff(z_array) ** 2)

        freq = sequence.get_sampling_rate()

        # fig = plt.figure()
        # ax = plt.subplot(4, 2, 1)
        # ax.plot(sequence.get_timestamps(), sequence.get_measure("x", "HandRight"))
        # ax.set_title("x")
        # ax = plt.subplot(4, 2, 3)
        # ax.plot(sequence.get_timestamps(), sequence.get_measure("y", "HandRight"))
        # ax.set_title("y")
        # ax = plt.subplot(4, 2, 5)
        # ax.plot(sequence.get_timestamps(), sequence.get_measure("z", "HandRight"))
        # ax.set_title("z")
        # ax = plt.subplot(4, 2, 7)
        # ax.plot(sequence.get_timestamps()[1:], sequence.get_measure("distance", "HandRight"))
        # ax.set_title("distance")
        # ax = plt.subplot(4, 2, 2)
        # ax.plot(sequence.get_timestamps(), sequence.get_measure("velocity", "HandRight"))
        # ax.set_title("velocity")
        # ax = plt.subplot(4, 2, 4)
        # ax.plot(sequence.get_timestamps(), sequence.get_measure("acceleration", "HandRight"))
        # ax.set_title("acceleration")
        # ax = plt.subplot(4, 2, 6)
        # ax.plot(sequence.get_timestamps(), sequence.get_measure("jerk", "HandRight"))
        # ax.set_title("jerk")
        # ax = plt.subplot(4, 2, 8)
        # ax.plot(sequence.get_timestamps(), sequence.get_measure("snap", "HandRight"))
        # ax.set_title("snap")
        # plt.tight_layout()
        # plt.show()

    def test_calculate_delay(self):
        sequence_1 = Sequence("test_sequences/test_sequence_1.tsv", time_unit="s", verbosity=0)
        pose_1 = sequence_1.poses[0]
        pose_2 = sequence_1.poses[1]
        pose_3 = sequence_1.poses[2]

        delay = calculate_delay(pose_1, pose_2)
        assert delay == 1

        delay = calculate_delay(pose_2, pose_1)
        assert delay == -1

        delay = calculate_delay(pose_2, pose_1, True)
        assert delay == 1

        delay = calculate_delay(pose_3, pose_1, True)
        assert delay == 2

    def test_generate_random_joints(self):
        random_joints = generate_random_joints(100, 1, 2, 3)
        assert len(random_joints) == 100
        x_values = [joint.x for joint in random_joints]
        y_values = [joint.y for joint in random_joints]
        z_values = [joint.z for joint in random_joints]
        assert(np.max(np.abs(x_values)) < np.max(np.abs(y_values)) < np.max(np.abs(z_values)))

    def test_get_number_of_windows(self):
        windows = get_number_of_windows(100, 10, 0, True)
        assert windows == 10

        windows = get_number_of_windows(100, 10, 0.5, True)
        assert windows == 19

        windows = get_number_of_windows(100, 10, 0.5, False)
        assert windows == 19

        windows = get_number_of_windows(10, 3, 0.5, False)
        assert windows == 8

    def test_get_window_length(self):
        window_length = get_window_length(100, 10, 0)
        assert window_length == 10

        window_length = get_window_length(100, 19, 0.5)
        assert window_length == 10

        window_length = get_window_length(10, 8, 0.5)
        assert window_length == 3

        window_length = get_window_length(10, 8, 0.5, False)
        assert np.round(window_length, 6) == 2.222222

    def test_divide_in_windows(self):
        array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        divided_array = divide_in_windows(array, 5, 0)
        assert np.array_equal(divided_array, [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10],
                                              [11, 12, 13, 14, 15], [16, 17, 18, 19, 20]])

        divided_array = divide_in_windows(array, 5, 2)
        expected_array = [[1, 2, 3, 4, 5], [4, 5, 6, 7, 8], [7, 8, 9, 10, 11], [10, 11, 12, 13, 14],
                          [13, 14, 15, 16, 17], [16, 17, 18, 19, 20], [19, 20]]
        for i in range(len(divided_array)):
            assert np.array_equal(divided_array[i], expected_array[i])

        divided_array = divide_in_windows(array, 5, 2, False)
        assert np.array_equal(divided_array, [[1, 2, 3, 4, 5], [4, 5, 6, 7, 8], [7, 8, 9, 10, 11],
                                              [10, 11, 12, 13, 14], [13, 14, 15, 16, 17], [16, 17, 18, 19, 20]])

    def test_load_color_names(self):
        colors_dict = load_color_names()

        assert colors_dict["red"] == (255, 0, 0, 255)
        assert colors_dict["r"] == (255, 0, 0, 255)
        assert colors_dict["xkcd:red"] == (229, 0, 0, 255)
        assert colors_dict["matlab:red"] == (162, 20, 47, 255)
        assert colors_dict["mr"] == (162, 20, 47, 255)

    def test_load_color_schemes(self):
        color_schemes = load_color_schemes()

        assert color_schemes["default"] == [(154, 205, 50, 255), (255, 0, 0, 255)]
        assert color_schemes["celsius"] == [(64, 224, 208, 255), (153, 204, 0, 255), (255, 204, 0, 255),
                                            (255, 165, 0, 255), (255, 0, 0, 255)]

    # noinspection SpellCheckingInspection
    def test_hex_color_to_rgb(self):
        assert hex_color_to_rgb("#c0ffee") == (192, 255, 238)
        assert hex_color_to_rgb("#C0FFEE") == (192, 255, 238)
        assert hex_color_to_rgb("c0ffee") == (192, 255, 238)
        assert hex_color_to_rgb("#c0ffee", True) == (192, 255, 238, 255)
        assert hex_color_to_rgb("#f0ccac1a", False) == (240, 204, 172)
        assert hex_color_to_rgb("#f0ccac1a", True) == (240, 204, 172, 26)
        assert hex_color_to_rgb("#f0ccac1a", None) == (240, 204, 172, 26)
        assert hex_color_to_rgb("#f0ccac1a") == (240, 204, 172, 26)
        self.assertRaises(Exception, hex_color_to_rgb, "krajjat")
        self.assertRaises(Exception, hex_color_to_rgb, "#zzzzzz")

    # noinspection SpellCheckingInspection
    def test_rgb_color_to_hex(self):
        assert rgb_color_to_hex((192, 255, 238)) == "#c0ffee"
        assert rgb_color_to_hex((192, 255, 238), True) == "#c0ffeeff"

        assert rgb_color_to_hex((240, 204, 172, 26), False) == "#f0ccac"
        assert rgb_color_to_hex((240, 204, 172, 26), True) == "#f0ccac1a"
        assert rgb_color_to_hex((240, 204, 172, 26), None) == "#f0ccac1a"
        assert rgb_color_to_hex((240, 204, 172, 26)) == "#f0ccac1a"

        self.assertRaises(Exception, hex_color_to_rgb, (0, 0, 0, 0, 0))
        self.assertRaises(Exception, hex_color_to_rgb, (0, 256, 256, 0, 0))

    def test_convert_color(self):
        assert convert_color("red", "RGB") == (255, 0, 0, 255)
        assert convert_color("red", "RGB", False) == (255, 0, 0)
        assert convert_color((255, 0, 0), "RGB") == (255, 0, 0, 255)
        assert convert_color((255, 0, 0, 255), "RGB", False) == (255, 0, 0)
        assert convert_color("#ff0000", "RGB") == (255, 0, 0, 255)
        assert convert_color("#ff0000", "RGB", False) == (255, 0, 0)
        assert convert_color("#ff0000ff", "RGB") == (255, 0, 0, 255)
        assert convert_color("#ff0000ff", "RGB", False) == (255, 0, 0)
        assert convert_color("red", "HEX") == "#ff0000ff"
        assert convert_color("red", "HEX", False) == "#ff0000"
        assert convert_color((255, 0, 0), "HEX") == "#ff0000ff"
        assert convert_color((255, 0, 0, 255), "HEX", False) == "#ff0000"
        assert convert_color("#ff0000", "HEX") == "#ff0000ff"
        assert convert_color("#ff0000", "HEX", False) == "#ff0000"
        assert convert_color("#ff0000ff", "HEX") == "#ff0000ff"
        assert convert_color("#ff0000ff", "HEX", False) == "#ff0000"

    # noinspection SpellCheckingInspection
    def test_convert_colors(self):
        colors = ["red", "lime", "blue"]
        converted_colors = convert_colors(colors, "RGB")
        assert converted_colors == [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)]

        converted_colors = convert_colors(colors, "RGB", False)
        assert converted_colors == [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

        converted_colors = convert_colors(colors, "HEX")
        assert converted_colors == ["#ff0000ff", "#00ff00ff", "#0000ffff"]

        converted_colors = convert_colors(colors, "HEX", False)
        assert converted_colors == ["#ff0000", "#00ff00", "#0000ff"]

        colors = ["#ff0000", (255, 0, 0), "red", (255, 0, 0, 255)]
        converted_colors = convert_colors(colors, "RGB")
        assert converted_colors == [(255, 0, 0, 255)] * 4

        converted_colors = convert_colors(colors, "RGB", False)
        assert converted_colors == [(255, 0, 0)] * 4

        converted_colors = convert_colors(colors, "HEX")
        assert converted_colors == ["#ff0000ff"] * 4

        converted_colors = convert_colors(colors, "HEX", False)
        assert converted_colors == ["#ff0000"] * 4

        assert convert_colors("default", "HEX", False) == ['#9acd32', '#ff0000']

    def test_calculate_color_points_on_gradient(self):
        color_scheme = ["red", "orange", "yellow"]
        color_points = calculate_color_points_on_gradient(color_scheme, 9)
        assert color_points == [(255, 0, 0, 255), (255, 41, 0, 255), (255, 82, 0, 255),
                                (255, 123, 0, 255), (255, 165, 0, 255), (255, 187, 0, 255),
                                (255, 210, 0, 255), (255, 232, 0, 255), (255, 255, 0, 255)]

        color_points = calculate_color_points_on_gradient("viridis", 7)
        assert color_points == [(66, 1, 86, 255), (60, 58, 122, 255), (48, 106, 140, 255),
                                (32, 146, 140, 255), (74, 183, 110, 255), (148, 212, 83, 255),
                                (252, 233, 59, 255)]

    def test_calculate_color_ratio(self):
        colors = [(0, 0, 0, 255), (255, 255, 255, 255)]
        assert calculate_color_ratio(colors, 0, "RGB", True) == (0, 0, 0, 255)
        assert calculate_color_ratio(colors, 0.2, "RGB", True) == (51, 51, 51, 255)
        assert calculate_color_ratio(colors, 0.4, "RGB", True) == (102, 102, 102, 255)
        assert calculate_color_ratio(colors, 0.6, "RGB", True) == (153, 153, 153, 255)
        assert calculate_color_ratio(colors, 0.8, "RGB", True) == (204, 204, 204, 255)
        assert calculate_color_ratio(colors, 1, "RGB", True) == (255, 255, 255, 255)

        colors = [(255, 0, 0, 255), (255, 165, 0, 255), (255, 255, 0, 255)]
        assert calculate_color_ratio(colors, 0, "RGB", True) == (255, 0, 0, 255)
        assert calculate_color_ratio(colors, 0.2, "RGB", True) == (255, 66, 0, 255)
        assert calculate_color_ratio(colors, 0.4, "RGB", True) == (255, 132, 0, 255)
        assert calculate_color_ratio(colors, 0.6, "RGB", True) == (255, 183, 0, 255)
        assert calculate_color_ratio(colors, 0.8, "RGB", True) == (255, 219, 0, 255)
        assert calculate_color_ratio(colors, 1, "RGB", True) == (255, 255, 0, 255)

        colors = [(0, 0, 0, 255), (255, 255, 255, 255)]
        assert calculate_color_ratio(colors, 0, "HEX", False) == "#000000"
        assert calculate_color_ratio(colors, 0.2, "HEX", False) == "#333333"
        assert calculate_color_ratio(colors, 0.4, "HEX", False) == "#666666"
        assert calculate_color_ratio(colors, 0.6, "HEX", False) == "#999999"
        assert calculate_color_ratio(colors, 0.8, "HEX", False) == "#cccccc"
        assert calculate_color_ratio(colors, 1, "HEX", False) == "#ffffff"

        colors = [(255, 0, 0, 255), (255, 165, 0, 255), (255, 255, 0, 255)]
        assert calculate_color_ratio(colors, 0, "HEX", False) == "#ff0000"
        assert calculate_color_ratio(colors, 0.2, "HEX", False) == "#ff4200"
        assert calculate_color_ratio(colors, 0.4, "HEX", False) == "#ff8400"
        assert calculate_color_ratio(colors, 0.6, "HEX", False) == "#ffb700"
        assert calculate_color_ratio(colors, 0.8, "HEX", False) == "#ffdb00"
        assert calculate_color_ratio(colors, 1, "HEX", False) == "#ffff00"

    def test_calculate_colors_by_values(self):
        values = {"Head": 0.2, "Hand": 0.59, "Knee": 0.47, "Shoulder": 0.745}
        colors = calculate_colors_by_values(values, "celsius")
        assert colors["Head"] == (64, 224, 208, 255)
        assert colors["Hand"] == (255, 170, 0, 255)
        assert colors["Knee"] == (253, 204, 0, 255)
        assert colors["Shoulder"] == (255, 0, 0, 255)

        colors = calculate_colors_by_values(values, ["black", "white"], min_value=0)
        assert colors["Head"] == (68, 68, 68, 255)
        assert colors["Hand"] == (201, 201, 201, 255)
        assert colors["Knee"] == (160, 160, 160, 255)
        assert colors["Shoulder"] == (255, 255, 255, 255)

        colors = calculate_colors_by_values(values, ["black", "white"], max_value=10, type_return="HEX")
        assert colors["Head"] == '#000000ff'
        assert colors["Hand"] == '#0a0a0aff'
        assert colors["Knee"] == '#070707ff'
        assert colors["Shoulder"] == '#0e0e0eff'

    def test_generate_random_color(self):
        color = generate_random_color()
        assert 0 <= color[0] <= 255
        assert 0 <= color[1] <= 255
        assert 0 <= color[2] <= 255
        assert color[3] == 255

        color = generate_random_color(True)
        assert 0 <= color[0] <= 255
        assert 0 <= color[1] <= 255
        assert 0 <= color[2] <= 255
        assert 0 <= color[3] <= 255

        color = generate_random_color(True, "HEX")
        assert color.startswith("#")
        assert len(color) == 9

        color = generate_random_color(True, "HEX", False)
        assert color.startswith("#")
        assert len(color) == 7

    def test_scale_audio(self):
        audio_array = [1, 2, 3, 4, 5]
        new_audio_array = scale_audio(audio_array, 1, verbosity=0)
        assert np.array_equal(new_audio_array, [0.2, 0.4, 0.6, 0.8, 1])

        new_audio_array = scale_audio(audio_array, 1, set_lowest_at_zero=True, verbosity=0)
        assert np.array_equal(new_audio_array, [0, 0.25, 0.5, 0.75, 1])

        audio_array = [-1, 2, -3, 4, -5]
        new_audio_array = scale_audio(audio_array, 1, verbosity=0)
        assert np.array_equal(new_audio_array, [-0.2, 0.4, -0.6, 0.8, -1])

        new_audio_array = scale_audio(audio_array, 1, True, verbosity=0)
        assert np.array_equal(new_audio_array, [0.2, 0.4, 0.6, 0.8, 1])

    def test_stereo_to_mono(self):
        stereo_data = np.array([[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]).transpose()
        mono_data = stereo_to_mono(stereo_data, verbosity=0)
        assert np.array_equal(mono_data, [1, 2, 3, 4, 5, 6])

        mono_data = stereo_to_mono(stereo_data, mono_channel=1, verbosity=0)
        assert np.array_equal(mono_data, [7, 8, 9, 10, 11, 12])

        mono_data = stereo_to_mono(stereo_data, mono_channel="average", verbosity=0)
        assert np.array_equal(mono_data, [4, 5, 6, 7, 8, 9])

    def test_remove_average(self):
        array = [1, 2, 3, 4, 5]
        new_array = remove_average(array)
        assert np.array_equal(new_array, [-2, -1, 0, 1, 2])

    def test_load_joint_labels(self):
        joint_labels = load_joint_labels("kinect", "all")
        assert "Head" in joint_labels
        assert "ElbowLeft" in joint_labels
        assert "AnkleRight" in joint_labels

        joint_labels = load_joint_labels("qualisys", "all", "original")
        assert "HeadR" in joint_labels
        assert "LElbowOut" in joint_labels
        assert "RAnkleOut" in joint_labels

        joint_labels = load_joint_labels("qualisys", "all", "new")
        assert "HeadRight" in joint_labels
        assert "ElbowLeft" in joint_labels
        assert "AnkleRight" in joint_labels

        joint_labels = load_joint_labels("kualisys", "top", "new")
        assert "HeadRight" in joint_labels
        assert "WaistFrontLeft" in joint_labels
        assert "ThighRight" not in joint_labels

        joint_labels = load_joint_labels("kualisys", "bottom", "new")
        assert "HeadRight" not in joint_labels
        assert "WaistFrontLeft" not in joint_labels
        assert "ThighRight" in joint_labels

        joint_labels = load_joint_labels("../src/krajjat/res/kualisys_joint_labels.txt", "all", "new")
        assert "HeadRight" in joint_labels
        assert "WaistFrontLeft" in joint_labels
        assert "ThighRight" in joint_labels

    def test_load_qualisys_joint_label_conversion(self):
        joints_conversions = load_qualisys_joint_label_conversion()
        assert joints_conversions["HeadR"] == "HeadRight"
        assert joints_conversions["LElbowOut"] == "ElbowLeft"
        assert joints_conversions["RAnkleOut"] == "AnkleRight"

    def test_load_joint_connections(self):
        joints_connections = load_joint_connections("kinect", "all")
        assert ("Head", "Neck") in joints_connections
        assert ("WristLeft", "HandLeft") in joints_connections
        assert ("SpineBase", "HipRight") in joints_connections

        joints_connections = load_joint_connections("kinect", "top")
        assert ("Head", "Neck") in joints_connections
        assert ("WristLeft", "HandLeft") in joints_connections
        assert ("SpineBase", "HipRight") not in joints_connections

        joints_connections = load_joint_connections("kinect", "bottom")
        assert ("Head", "Neck") not in joints_connections
        assert ("WristLeft", "HandLeft") not in joints_connections
        assert ("SpineBase", "HipRight") in joints_connections

        joints_connections = load_joint_connections("qualisys", "all")
        assert ("HeadTop", "HeadRight") in joints_connections
        assert ("WaistFrontLeft", "WaistFrontRight") in joints_connections
        assert ("WaistFrontRight", "ThighRight") in joints_connections

        joints_connections = load_joint_connections("qualisys", "top")
        assert ("HeadTop", "HeadRight") in joints_connections
        assert ("WaistFrontLeft", "WaistFrontRight") in joints_connections
        assert ("WaistFrontRight", "ThighRight") not in joints_connections

        joints_connections = load_joint_connections("qualisys", "bottom")
        assert ("HeadTop", "HeadRight") not in joints_connections
        assert ("WaistFrontLeft", "WaistFrontRight") not in joints_connections
        assert ("WaistFrontRight", "ThighRight") in joints_connections

    def test_load_qualisys_to_kinect(self):
        conversions = load_qualisys_to_kinect()
        assert conversions["Head"] == ("HeadTop", "HeadFront", "HeadRight", "HeadLeft")
        assert conversions["SpineMid"] == ("Chest", "BackRight", "BackLeft")
        assert conversions["FootRight"] == ("ForefootOutRight", "ForefootInRight", "ToetipRight", "HeelRight")

    def test_load_joints_subplot_layout(self):
        layout = load_joints_subplot_layout("kinect")
        assert layout["Head"] == 3
        assert layout["SpineMid"] == 18
        assert layout["FootLeft"] == 35

        layout = load_joints_subplot_layout("qualisys")
        assert layout["HeadTop"] == 4
        assert layout["SpineTop"] == 18
        assert layout["ForefootOutLeft"] == 83

    def test_load_joints_silhouette_layout(self):
        positions, layout = load_joints_silhouette_layout("kinect")
        assert positions["Head"] == (233, 60, 120)
        assert positions["SpineMid"] == (233, 355, 150)
        assert positions["FootLeft"] == (173, 1040, 150)
        assert layout[19] == "Head"
        assert layout[1] == "SpineMid"
        assert layout[18] == "FootLeft"

        positions, layout = load_joints_silhouette_layout("qualisys")
        assert positions["HeadTop"] == (233, 10, 50)
        assert positions["SpineTop"] == (233, 160, 100)
        assert positions["ForefootOutLeft"] == (318, 1030, 50)
        assert layout[0] == "HeadTop"
        assert layout[4] == "SpineTop"
        assert layout[41] == "ForefootOutLeft"

    def test_load_default_steps_gui(self):
        default_steps_gui = load_default_steps_gui()
        assert default_steps_gui["size_joint_default"] == 5
        assert default_steps_gui["speed"] == 0.25
        assert default_steps_gui["shift_y"] == 1

    def test_convert_timestamp_to_seconds(self):
        assert convert_timestamp_to_seconds(5, "ms") == 0.005
        assert convert_timestamp_to_seconds(1, "day") == 86400
        assert convert_timestamp_to_seconds(1, "h") == 3600
        assert convert_timestamp_to_seconds(1000000, "ns") == 0.001

    def test_format_time(self):
        assert format_time(1, "s", "hh:mm:ss") == "00:00:01"
        assert format_time(1000, "s", "hh:mm:ss") == "00:16:40"
        assert format_time(1000, "s", "hh:mm:ss.ms") == "00:16:40.000"
        assert format_time(1000, "s", "mm:ss") == "16:40"
        assert format_time(1000, "s", "mm:ss.ms") == "16:40.000"

    def test_time_unit_to_datetime(self):
        t_dt = datetime.datetime(1, 1, 1, 0, 0, 1)
        assert time_unit_to_datetime(1, "s") == t_dt

        t_dt = datetime.datetime(1, 1, 1, 0, 16, 40)
        assert time_unit_to_datetime(1000000, "ms") == t_dt

    def test_time_unit_to_timedelta(self):
        t_dt = datetime.timedelta(0, 1, 0)
        assert time_unit_to_timedelta(1, "s") == t_dt

        t_dt = datetime.timedelta(0, 1000, 0)
        assert time_unit_to_timedelta(1000000, "ms") == t_dt

    def test_show_progression(self):
        assert show_progression(1, 50, 500, 10) == 10
        assert show_progression(1, 51, 500, 10) == 20

    def test_get_min_max_values_from_plot_dictionary(self):
        # plot_dictionary = {"Head": [0, 1, 2, 3, 4], "Hand": [5, 6, 7, 8, 9]}
        # assert get_min_max_values_from_plot_dictionary(plot_dictionary) == (0, 9)

        g1 = Graph()
        g1.add_plot([0, 1, 2, 3], [0, 1, 2, 3])
        g1.add_plot([0, 1, 2, 3], [4, 5, 6, 7])
        g2 = Graph()
        g2.add_plot([0, 1, 2, 3], [8, 9, 10, 11])
        g2.add_plot([0, 1, 2, 3], [12, 13, 14, 15])

        plot_dictionary = {"Head": g1, "Hand": g2}
        assert get_min_max_values_from_plot_dictionary(plot_dictionary) == (0, 15)

        plot_dictionary = {"Head": 1, "Hand": 2}
        assert get_min_max_values_from_plot_dictionary(plot_dictionary) == (1, 2)

    def test_kwargs_parser(self):
        kwargs = {"size": 2, "size_hand": 3, "color_hand": "red"}
        parsed_kwargs = kwargs_parser(kwargs, "_hand")

        assert parsed_kwargs["size"] == 2
        assert parsed_kwargs["color"] == "red"

    def test_set_nested_dict(self):
        a = {}
        set_nested_dict(a, ["A", "AA", "AAA"], 1)
        print(a)
        assert a["A"]["AA"]["AAA"] == 1

        set_nested_dict(a, ["B", "BA"], 2)
        assert a["A"]["AA"]["AAA"] == 1
        assert a["B"]["BA"] == 2

        set_nested_dict(a, ["A", "AA", "AAB"], 3)
        assert a["A"]["AA"]["AAA"] == 1
        assert a["B"]["BA"] == 2
        assert a["A"]["AA"]["AAB"] == 3

        set_nested_dict(a, ["A", "AA", "AAB"], 4)
        assert a["A"]["AA"]["AAA"] == 1
        assert a["B"]["BA"] == 2
        assert a["A"]["AA"]["AAB"] == 4

    def test_has_nested_key(self):
        a = {}
        set_nested_dict(a, ["A", "AA", "AAA"], 1)
        assert has_nested_key(a, ["A", "AA", "AAA"])
        assert not has_nested_key(a, ["A", "AA", "AAB"])