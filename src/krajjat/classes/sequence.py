"""Default class for motion sequences in the toolbox. An instance of this class will be
one motion sequence. The class contains several methods to perform **pre-processing** or
**displaying summarized data** in text form (see public methods)."""

import copy
import pickle
from collections import OrderedDict
from bisect import bisect

from scipy.signal import butter, lfilter
from scipy.io import savemat

from krajjat.classes.pose import Pose
from krajjat.classes.audio import Audio
from krajjat.classes.exceptions import *
from krajjat.classes.time_series import TimeSeries
from krajjat.tool_functions import *

from statistics import stdev
from datetime import datetime
import os
import os.path as op


class Sequence(TimeSeries):
    """Creates an instance from the class Sequence and returns a Sequence object, allowing to be manipulated for
    processing or displaying. Upon creation, the function tries to assign a name to it based on the provided
    name parameter or path parameter. It then proceeds to load the sequence if a path has been provided.

    .. versionadded:: 2.0

    Parameters
    ----------
    path: str or None, optional
        Absolute path to the motion sequence (starting from the root of the drive, e.g.
        ``C:/Users/Elliot/Documents/Recordings``). The path may point to a folder or a single file.
        For the acceptable file types, see :doc:`../general/input`. If the path is ``None``, an empty sequence will be
        created.

    path_audio: str or None, optional
        Absolute path to an audio file corresponding to the sequence. The path should point to a .wav
        file. This path will be stored as an attribute of the Sequence object, and may be used automatically by
        functions using an audio file (typically, :py:meth:`~Sequence.synchronize()` and :py:func:`sequence_reader()`).
        This parameter is however far from vital in the definition of a Sequence instance, and can be skipped safely.

    name: str or None, optional
        Defines a name for the Sequence instance. If a string is provided, the attribute :attr:`name` will take
        its value. If not, see :meth:`~Sequence._define_name_init()`.

    condition: str or None, optional
        Optional field to represent in which experimental condition the sequence was recorded.

    time_unit: str or None, optional
        The unit of time of the timestamps in the original file. Depending on the value put as parameter, the timestamps
        will be converted to seconds.

            • If set on ``"auto"``, the function :meth:`Sequence._calculate_relative_timestamps()` will try to
              automatically detect the unit of the timestamps based on the difference of time between the two first
              frames, and will divide the timestamps by 10 000 000 (if it detects the timestamps to be in 100 ns), by
              1 000 (if the timestamps are in ms), or won't divide them (if the timestamps are already in s).
            • If set on ``"100ns"``, divides the timestamps from the file by 10 000 000. Typically, this is due to
              the output timestamps from Kinect being in tenth of microsecond (C# system time).
            • If set on ``"ms"``, divides the timestamps from the file by 1 000.
            • If set on ``"s"``, the function will preserve the timestamps as they are in the file.

        The parameter also allows other units: ``"ns"``, ``"1ns"``, ``"10ns"``, ``"100ns"``, ``"µs"``, ``"1µs"``,
        ``"10µs"``, ``"100µs"``, ``"ms"``, ``"1ms"``, ``"10ms"``, ``"100ms"``, ``"s"``, ``"sec"``, ``"1s"``, ``"min"``,
        ``"mn"``, ``"h"``, ``"hr"``, ``"d"``, ``"day"``. See the documentation for the function
        :meth:`Sequence._calculate_relative_timestamps()`.

    system: str or None, optional
        Defines the type of system used to record the sequence. Can be manually set on ``"kinect"``, ``"qualisys"``,
        ``"kualisys"``, or ``"auto"`` (default). If set on ``"auto"``, the function will try to detect the type of
        system based on the joint labels present in the recording. This parameter can also be set on ``None``. In that
        case, the functions using pre-sets for the aforementioned systems might not work properly.

    start_timestamps_at_zero: bool, optional
        If set on ``True``, the timestamp of the first pose of the sequence will be
        set at 0, and the timestamps of the other poses will be reassigned to keep the same delay from the first pose.
        As such, the attributes timestamp and relative_timestamp from every pose will be equal.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Attributes
    ----------
    path: str
        Path to the sequence passed as a parameter upon creation.
    path_audio: str
        Path to the audio file corresponding to the sequence.
    name: str
        Custom name given to the sequence. If no name has been provided upon initialisation, it will be defined by
        :meth:`Sequence._define_name_init()`.
    condition: str
        Defines in which experimental condition the sequence was recorded.
    files: list(str)
        List of files contained in the path. The list will be of size 1 if the path points to a single file.
    poses: list(Pose)
        List of all the :class:`Pose` objects of the :class:`Sequence`.
    is_randomized: bool
        Testifies if the starting position of the joints have been randomized by the function
        :meth:`Sequence.randomize()`. Is ``False`` upon initialisation.
    date_recording: datetime
        The date at which the recording was performed, extracted from the file.
    metadata: dict
        A dictionary containing metadata about the recording, extracted from the file.
    time_unit: str
        The time unit of the timestamps.
    joint_labels: list(str)
        A list containing the joint labels present in each pose of the sequence.

    Examples
    --------
    >>> seq1 = Sequence("sequences/John/seq_001.tsv")
    >>> seq2 = Sequence("sequences/Paul/seq_001.xlsx", name="Paul_001")
    >>> seq3 = Sequence(name="George_001")
    >>> seq4 = Sequence("sequences/Ringo/seq_001.json", name="Ringo_001", condition="English", time_unit="ms", system="Kinect", verbosity=0)
    >>> seq5 = Sequence()
    """

    def __init__(self, path=None, path_audio=None, name=None, condition=None, time_unit="auto", system="auto",
                 start_timestamps_at_zero=False, verbosity=1):

        super().__init__("Sequence", path, name, condition, verbosity)

        # self._define_name_init(verbosity)  # Defines the name of the sequence

        self.path_audio = path_audio  # Path to the audio file matched with this series of gestures

        self.poses = []  # List of the poses in the sequence, ordered
        self.joint_labels = []  # Name of the joint labels contained in the sequence
        self.system = system.lower()  # Placeholder for Kinect, Qualisys, OpenPose, etc.
        self.dimensions = 0  # Dimensionality of the data (2D, 3D) - unused as of v2.0.

        self.is_randomized = False  # True if the joints positions are randomized
        self.date_recording = None  # Placeholder for the date of the recording.

        self.timestamps = []  # List containing the timestamps of the poses.
        self.time_unit = time_unit  # Time unit of the timestamps.

        if path is not None:
            self._load_from_path(verbosity)

        if self.time_unit == "auto":
            self._set_time_unit()

        self._set_timestamps_time_unit()  # Sets the timestamps according to the defined time unit
        self._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

        if start_timestamps_at_zero:
            self.set_first_timestamp(0)

        self._set_joint_labels(verbosity)
        self._apply_joint_labels(None, True, verbosity)
        self._set_system(verbosity)

    # === Name and setter functions ===
    def set_name(self, name):
        """Sets the :py:attr:`name` attribute of the Sequence instance. This name can be used as display functions or as
        a means to identify the sequence (typically, :func:`plot_functions.joint_temporal_plotter()`).

        .. versionadded:: 2.0

        Parameters
        ----------
        name : str
            The name you want to give to the sequence.

        Example
        -------
        >>> seq7 = Sequence("C:/Users/Mario/Sequences/seq7/seq7.tsv")
        >>> seq7.name
        seq7
        >>> seq7.set_name("Sequence story telling 7")
        >>> seq7.name
        Sequence story telling 7
        """
        super().set_name(name)

    def set_condition(self, condition):
        """Sets the :py:attr:`condition` attribute of the Sequence instance. This attribute can be used to save the
        experimental condition in which the Sequence instance was recorded.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str
            The experimental condition in which the sequence was recorded.

        Examples
        --------
        >>> seq8 = Sequence("C:/Users/Harold/Sequences/English/seq8.xlsx")
        >>> seq8.set_condition("English")
        >>> seq9 = Sequence("C:/Users/Harold/Sequences/Spanish/seq9.xlsx")
        >>> seq9.set_condition("Spanish")
        """
        self.condition = condition

    def set_path_audio(self, path_audio):
        """Sets the :py:attr:`path_audio` attribute of the Sequence instance. This path may be used automatically by
        functions using an audio file (typically, :func:`Sequence.trim_to_audio()` and
        :func:`graphic_functions.sequence_reader`).

        .. versionadded:: 2.0

        Parameters
        ----------
        path_audio : str
            The absolute path to the .wav file corresponding to the sequence.

        Example
        -------
        >>> seq10 = Sequence("C:/Users/Link/Sequences/seq_10.xlsx")
        >>> seq10.set_path_audio("C:/Users/Link/Audios/audio_10.wav")
        """

        self.path_audio = path_audio

    def set_first_timestamp(self, first_timestamp, time_unit="s"):
        """Attributes a new timestamp to the first pose of the sequence and delays the timestamps of the other poses
        accordingly.

        .. versionadded:: 2.0

        Parameters
        ----------
        first_timestamp: float|int
            The new timestamp of the first pose of the sequence.
        time_unit: str, optional
            The unit of time of first_timestamp (default: ``"s"``). The parameter also allows other units: ``"ns"``,
            ``"1ns"``, ``"10ns"``, ``"100ns"``, ``"µs"``, ``"1µs"``, ``"10µs"``, ``"100µs"``, ``"ms"``, ``"1ms"``,
            ``"10ms"``, ``"100ms"``, ``"s"``, ``"sec"``, ``"1s"``, ``"min"``, ``"mn"``, ``"h"``, ``"hr"``, ``"d"``,
            ``"day"``.

        Note
        ----
        If 0 is passed as a parameter, the absolute timestamps of the sequence will be equal to its relative timestamps.

        Example
        -------
        >>> seq11 = Sequence("C:/Users/MarkS/Sequences/seq_11.xlsx")
        >>> seq11.get_timestamps()
        [0, 0.1, 0.2]
        >>> seq11.set_first_timestamp(4.8)
        >>> seq11.get_timestamps()
        [4.8, 4.9, 5.0]
        """
        original_starting_timestamp = self.poses[0].get_timestamp()
        time_difference = convert_timestamp_to_seconds(first_timestamp, time_unit) - original_starting_timestamp

        for p in range(len(self.poses)):
            self.poses[p].set_timestamp(self.poses[p].timestamp + time_difference)

    def set_date_recording(self, date):
        """Sets the :attr:`date_recording` attribute of the Sequence instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        date: datetime
            A datetime object representing the date of the recording.

        Example
        -------

        """
        self.date_recording = date

    # === Pose handling ===
    def add_pose(self, pose, replace_if_exists=False, verbosity=1):
        """Adds a pose to the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose: Pose
            A Pose instance.
        replace_if_exists: bool, optional
            If `True`, replaces the pose if it already exists in the sequence. If `False` (default), returns an error
            if the Sequence object contains a Pose with the same timestamp as the one being added.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Raises
        ------
        PoseAlreadyExistsException
            If a pose with the same timestamp already exists in the sequence.

        Example
        -------
        >>> joint = Joint("Head", 1, 2, 3)
        >>> pose = Pose(1)
        >>> pose.add_joint(joint)
        >>> seq = Sequence()
        >>> seq.add_pose(pose)
        """
        if verbosity > 1:
            print(f"Adding the following pose to the sequence {self.name}:\n{pose}")

        bisect_index = bisect(self.get_timestamps(), pose.get_timestamp())
        if bisect_index != 0 and np.isclose(self.poses[bisect_index - 1].get_timestamp(), pose.get_timestamp()):
            if replace_if_exists:
                if verbosity > 0:
                    print(f"Replacing pose with index {bisect_index - 1} at timestamp {pose.get_timestamp()}.")
                idx = bisect_index - 1
                self.poses[idx] = pose
            else:
                raise PoseAlreadyExistsException(self.name, pose.get_timestamp())
        else:
            if verbosity > 0:
                print(f"Inserting the pose at index {bisect_index}.")
            idx = bisect_index
            self.poses.insert(idx, pose)

        # Relative timestamps
        if bisect_index == 0:
            self._calculate_relative_timestamps()
        else:
            self.poses[idx]._calculate_relative_timestamp(self.poses[0].timestamp)

        # Joint labels
        new_joint_labels = False
        for joint_label in pose.get_joint_labels():
            if joint_label not in self.joint_labels:
                self.joint_labels.append(joint_label)
                new_joint_labels = True

        if new_joint_labels:
            if verbosity > 1:
                print("New joint labels detected in the added pose. Adding them to the other poses...")
            self._apply_joint_labels(None, True, verbosity)

    def add_poses(self, *poses, replace_if_exists=False, verbosity=1):
        """Adds poses to the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        poses: Pose
            One or multiple Pose instances.
        replace_if_exists: bool, optional
            If `True`, replaces the pose if it already exists in the sequence. If `False` (default), returns an error
            if the Sequence object contains a Pose with the same timestamp as the one being added.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Raises
        ------
        PoseAlreadyExistsException
            If a pose with the same timestamp already exists in the sequence.

        Example
        -------
        >>> pose1 = Pose(1)
        >>> pose2 = Pose(2)
        >>> pose3 = Pose(3)
        >>> seq = Sequence()
        >>> seq.add_poses(pose1, pose2, pose3)
        """
        for pose in poses:
            self.add_pose(pose, replace_if_exists, verbosity)

    # === Loading functions ===
    def _set_time_unit(self):
        """Defines the unit if the attribute :attr:`time_unit` is set on ``"auto"``. To do so, it checks
        if the difference between the timestamps of the two first poses of the sequence:

            • If it is over 1000, the function presumes that the unit is in hundreds of ns (C# precision unit,
              Kinect output unit).
            • If it is between 1 and 1000, it presumes that the unit is in milliseconds (Qualisys output unit).
            • If it is below that threshold, or if there is only one pose in the sequence, it presumes that the unit
              is in seconds.

        Otherwise, it is possible to manually define the unit, among the following values: ``"ns"``, ``"1ns"``,
        ``"10ns"``, ``"100ns"``, ``"µs"``, ``"1µs"``, ``"10µs"``, ``"100µs"``, ``"ms"``, ``"1ms"``, ``"10ms"``,
        ``"100ms"``, ``"s"``, ``"sec"``, ``"1s"``, ``"min"``, ``"mn"``, ``"h"``, ``"hr"``, ``"d"``, ``"day"``."""
        if self.time_unit == "auto":
            if len(self.poses) > 1:
                if self.poses[1].get_timestamp() - self.poses[0].get_timestamp() >= 1000:
                    self.time_unit = "100ns"
                elif self.poses[1].get_timestamp() - self.poses[0].get_timestamp() >= 1:
                    self.time_unit = "ms"
                else:
                    self.time_unit = "s"
            else:
                self.time_unit = "s"

    def _load_from_path(self, verbosity=1):
        """Loads the sequence data from the :attr:`path` provided during the initialization, and calculates the relative
        timestamps from the first pose for each pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        super()._load_from_path(verbosity)

        self._load_poses(verbosity)  # Loads the files into poses

        if len(self.poses) == 0:
            raise EmptyInstanceException("Sequence")

        self._load_date_recording(verbosity)

    def _load_poses(self, verbosity=1):
        """Loads the single pose files or the global file containing all the poses. Depending on the input, this
        function calls either :meth:`Sequence._load_single_pose_file` or :meth:`Sequence._load_sequence_file`.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        """

        if verbosity == 1:
            print(f"Opening sequence from {self.path}...", end=" ")
        elif verbosity > 1:
            print(f"Opening sequence from {self.path}...")
        perc = 10  # Used for the progression percentage

        # If the path is a folder, we load every single file
        if op.isdir(self.path):

            for i in range(len(self.files)):

                if verbosity > 1:
                    print(f"Loading file {i + 1} of {len(self.files)}: {self.files[i]}...", end=" ")

                # Show percentage if verbosity
                perc = show_progression(verbosity, i, len(self.files), perc)

                # Create the Pose object, passes as parameter the index and the file path
                self._load_single_pose_file(i, op.join(self.path, self.files[i]), verbosity)

                if verbosity > 1:
                    print("OK.")

            if verbosity > 0:
                print("100% - Done.")

        # Otherwise, we load the one file
        else:
            self._load_sequence_file(verbosity)

    def _load_single_pose_file(self, pose_index, path, verbosity=1):
        """Loads the content of a single pose file into a Pose object. Depending on the file type, this function
        handles the content differently (see :doc:`../general/input`).

        Parameters
        ----------
        pose_index: int
            The index of the pose.

        path: str
            The path of a file containing a single pose.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        """

        file_extension = op.splitext(path)[-1]

        # JSON file
        if file_extension == ".json":
            data = read_json(path)
            if pose_index == 0:
                self._load_json_metadata(data, verbosity)
            self._create_pose_from_json(data, verbosity)

        # Excel file
        elif file_extension == ".xlsx":
            data = read_xlsx(path, verbosity=verbosity)
            self._create_pose_from_table_row(data)

        elif file_extension == ".pkl":
            with open(path, "rb") as f:
                pose = pickle.load(f)
            self.poses.append(pose)

        else:
            if os.path.splitext(self.path)[-1] not in [".csv", ".tsv", ".txt"]:
                if verbosity > 0:
                    print(f"Loading from non-standard extension {os.path.splitext(self.path)[-1]} as text...")

            # Open the file and read the data
            if self.system == "qualisys":
                data, metadata = read_text_table(path, standardize_labels=False, verbosity=verbosity)
                self.metadata.update(metadata)
            else:
                data, metadata = read_text_table(path, standardize_labels=True, verbosity=verbosity)
                self.metadata.update(metadata)
            self._create_pose_from_table_row(data)

    def _load_sequence_file(self, verbosity=1):
        """Loads the content of a global sequence file containing individual poses into Pose objects.
        Depending on the file type, this function handles the content differently (see :doc:`../general/input`).

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        """

        perc = 10  # Used for the progression percentage

        file_extension = op.splitext(self.path)[-1]

        # JSON file
        if file_extension == ".json":

            # Open the file and read the data
            data = read_json(self.path)

            if len(data) == 0:
                raise EmptyInstanceException("Sequence")

            self._load_json_metadata(data, verbosity)

            for p in range(len(data["Poses"])):
                if verbosity > 1:
                    print("Loading pose " + str(p) + " of " + str(len(data["Poses"])) + "...", end=" ")

                # Show percentage if verbosity
                perc = show_progression(verbosity, p, len(data["Poses"]), perc)

                # Create the Pose object, passes as parameter the index and the data
                self._create_pose_from_json(data["Poses"][p])

                if verbosity > 1:
                    print("OK.")

        # Excel file
        elif file_extension == ".xlsx":
            data, metadata = read_xlsx(self.path, verbosity=verbosity)
            if "processing_steps" in metadata.keys():
                metadata["processing_steps"] = json.loads(metadata["processing_steps"])
            self.metadata.update(metadata)

            # For each pose
            for p in range(len(data) - 1):

                if verbosity > 1:
                    print("Loading pose " + str(p) + " of " + str(len(data)) + "...", end=" ")

                self._create_pose_from_table_row(data, p + 1)

                if verbosity > 1:
                    print("OK.")

        # Pickle file
        elif file_extension == ".pkl":
            with open(self.path, "rb") as f:
                audio = pickle.load(f)
            for attr in audio.__dict__:
                if attr == "metadata":
                    self.metadata.update(audio.metadata)
                elif attr not in ["name", "path", "files"]:
                    self.__setattr__(attr, audio.__dict__[attr])

        # Mat file
        elif file_extension == ".mat":
            with open(self.path, "rb") as f:
                data = loadmat(f, simplify_cells=True)

            for key in data["data"]:
                if key == "Poses":
                    values = pd.DataFrame(data["data"]["Poses"]).values.tolist()
                    table = [[key for key in data["data"]["Poses"]]] + [row for row in values]

                    for p in range(len(values)):

                        if verbosity > 1:
                            print("Loading pose " + str(p) + " of " + str(len(data) - 1) + "...", end=" ")

                        self._create_pose_from_table_row(table, p + 1)

                        if verbosity > 1:
                            print("OK.")

                else:
                    self.metadata[key] = data["data"][key]

        # Text file (csv or txt)
        else:
            if file_extension not in [".csv", ".tsv", ".txt"]:
                if verbosity > 0:
                    print(f"Loading from non-standard extension {file_extension} as text...")

            if self.system == "qualisys":
                data, metadata = read_text_table(self.path, standardize_labels=False, verbosity=verbosity)
                self.metadata.update(metadata)
            else:
                data, metadata = read_text_table(self.path, standardize_labels=True, verbosity=verbosity)
                self.metadata.update(metadata)

            # For each pose
            for p in range(len(data) - 1):

                if verbosity > 1:
                    print(f"Loading pose {p} of {len(data) - 1}...", end=" ")

                self._create_pose_from_table_row(data, p + 1)

                if verbosity > 1:
                    print("OK.")

        if verbosity:
            print("100% - Done.")

    def _create_pose_from_table_row(self, table, row=1):
        """Reads the content of a table, considering the first row as containing headers, and converts the content of a
        specific row into a pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        table: list(list)
            A table, where the first elements are the headers.
        row: int, optional
            The row containing the data of the pose. 0 being the header row, row should be 1 or more.
        """

        headers = table[0]
        values = table[row]

        data = OrderedDict()
        for i in range(len(headers)):
            data[headers[i]] = values[i]

        pose = Pose(float(data["Timestamp"]))

        for value in headers:
            if value[-2:] == "_X":
                label = value[:-2]
                joint = Joint(label, float(data[label + "_X"]), float(data[label + "_Y"]), float(data[label + "_Z"]))
                pose.add_joint(joint)

        self.poses.append(pose)

    def _create_pose_from_json(self, data, verbosity=1):
        """Reads the content of a json file containing a single pose, and converts the content of a specified pose index
        into a pose object.

        .. versionadded:: 2.0

        Parameters
        ----------
        data: list or dict
            The content of a json file.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        # If there is at least a body found
        if len(data["Bodies"]) != 0:
            joints = data["Bodies"][0]["Joints"]
            if verbosity > 1:
                print(str(len(joints)) + " joints were found.")

        # Otherwise, no mocap data
        else:
            joints = {}
            if verbosity > 1:
                print("No mocap data found.")
        timestamp = data["Timestamp"]

        # We create a pose and create all the joint elements there
        pose = Pose(timestamp)
        for j in joints:
            joint = Joint(j["JointType"], j["Position"]["X"], j["Position"]["Y"], j["Position"]["Z"])
            pose.add_joint(joint)

        self.poses.append(pose)

    def _set_timestamps_time_unit(self):
        """Sets the timestamps for each pose according to the attribute :attr:`time_unit`.

        .. versionadded:: 2.0
        """

        for pose in self.poses:
            pose.timestamp = pose.timestamp / UNITS[self.time_unit]

    def _load_json_metadata(self, data, verbosity=1):
        """Loads the data from the file apart from the joint positions, and saves it in the attribute :attr:`metadata`.
        For Kinect data, this function will load all the elements from the JSON file apart from `"Bodies"`.

        .. versionadded:: 2.0

        Parameters
        ----------
        data: dict
            The data from the file containing the full recording, or containing the first pose of the recording.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        if verbosity > 1:
            print("Trying to find metadata...", end=" ")

        for key in data:
            if key not in ["Poses", "Bodies"]:
                if key == "Timestamp":
                    self.metadata["Date recording"] = data[key]
                else:
                    self.metadata[key] = data[key]

        if verbosity > 1:
            if len(self.metadata) == 0:
                print("Found no metadata entries.")
            elif len(self.metadata) == 1:
                print("Found 1 metadata entry.")
            else:
                print("Found " + str(len(self.metadata)) + " metadata entries.")

            for key in self.metadata:
                print("\t" + str(key) + ": " + str(self.metadata[key]))

            if "system" in self.metadata:
                self.system = self.metadata["system"]

    def _load_date_recording(self, verbosity=1):
        """Loads the date of a recording from the information contained in the recording metadata.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        if verbosity > 1:
            print("Trying to find recording date...", end=" ")

        possible_keys = ["DATE_RECORDING", "Recording date", "Date of recording"]

        if "Date recording" in self.metadata.keys():
            if type(self.metadata["Date recording"]) == str:
                self.metadata["Date recording"] = datetime.fromisoformat(self.metadata["Date recording"])
            elif str(type(self.metadata["Date recording"])) == "<class 'datetime.datetime'>":
                pass
            elif self.metadata["Date recording"] > 2147483647:
                self.metadata["Date recording"] = datetime.fromtimestamp((self.metadata["Date recording"] - 621355968000000000) / 10000000)
            else:
                self.metadata["Date recording"] = datetime.fromtimestamp(self.metadata["Date recording"])
            self.date_recording = self.metadata["Date recording"]

        elif "TIME_STAMP" in self.metadata.keys():
            self.date_recording = datetime.fromisoformat(self.metadata["TIME_STAMP"][0].replace(",", ""))

        else:
            for possible_key in possible_keys:
                if possible_key in self.metadata.keys():
                    self.date_recording = datetime.fromisoformat(self.metadata[possible_key])

        if verbosity > 1:
            if self.date_recording is not None:
                print("found: " + self.get_date_recording("str"))
            else:
                print("not found.")

    def _set_joint_labels(self, verbosity=1, add_tabs=0):
        """Scans through all the poses of the Sequence instance, and sets the parameter :attr:`Sequence.joint_labels`
        with the joint labels appearing at least once.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.
        """
        t = add_tabs * "\t"

        if verbosity > 1:
            print(f"{t}Scanning the joint labels...")

        joint_labels = {}

        for p in range(len(self.poses)):

            if verbosity > 1:
                if len(self.poses[p].joints) == 1:
                    print(f"{t}\t{len(self.poses[p].joints)} joint found in pose {p + 1}.")
                else:
                    print(f"{t}\t{len(self.poses[p].joints)} joints found in pose {p + 1}.")

            for joint in self.poses[p].get_joint_labels():
                joint_labels[joint] = None

        self.joint_labels = list(joint_labels.keys())

    def _apply_joint_labels(self, default_value=None, check_length_only=True, verbosity=1, add_tabs=0):
        """Verifies if each pose of the Sequence instance contains a Joint object for each of the joint labels present
        in :attr:`Sequence.joint_labels`. If some Joint objects are missing (typically, if the skeleton was not detected
        for one frame), the function creates Joint objects with all the coordinates equal to `default_value`.

        .. versionadded:: 2.0

        Parameters
        ----------
        default_value: None, numpy.nan, int or float (optional)
            The default value to set to all the coordinates for the missing joint labels. By default, it is equal to
            `None`, but it can be set on 0 (in that case, missing joints will have a coordinate of (0, 0, 0)), numpy.nan
            or any other numerical value.

        check_length_only: bool, optional
            If set on `True` (default), the function only checks if the number of joint labels in the pose is equal
            to the number of labels in the attribute :attr:`joint_labels` of the Sequence instance. If you want to check
            thoroughly that the name of the joint labels is exactly the same, set this parameter on `False` - the
            computation time may be impacted.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.
        """
        t = add_tabs * "\t"

        if verbosity > 1:
            print(f"{t}Adding joint labels to the poses missing them...")

        for p in range(len(self.poses)):
            joint_labels_pose = self.poses[p].get_joint_labels()

            if verbosity > 1:
                print(f"{t}\tChecking pose {p + 1}...", end=" ")

            if check_length_only:
                if not len(joint_labels_pose) == len(self.joint_labels):

                    if verbosity > 1:
                        if len(joint_labels_pose) == 1:
                            print(f"{t}\t\t{len(joint_labels_pose)} joint out of {len(self.joint_labels)} found.")
                        else:
                            print(f"{t}\t\t{len(joint_labels_pose)} joints out of {len(self.joint_labels)} found.")

                    for joint_label in self.joint_labels:
                        if joint_label not in joint_labels_pose:

                            if verbosity > 1:
                                print(f"{t}\t\tAdding joint label {joint_label}...", end=" ")

                            self.poses[p].add_joint(Joint(joint_label, default_value, default_value, default_value))

                            if verbosity > 1:
                                print("OK.")

                else:

                    if verbosity > 1:
                        print("OK.")

            else:

                for joint_label in self.joint_labels:
                    if joint_label not in joint_labels_pose:

                        if verbosity > 1:
                            print(f"{t}\t\tAdding joint label {joint_label}...", end=" ")

                        self.poses[p].add_joint(Joint(joint_label, default_value, default_value, default_value))

                        if verbosity > 1:
                            print("OK.")

                    else:

                        if verbosity > 1:
                            print(f"{t}\t\tJoint label {joint_label} found.")

    def _set_system(self, verbosity=1):
        """Sets the recording system of the Sequence, based on its joint labels.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        if verbosity > 1:
            print("Setting the system of the recording...")

        if type(self.system) is str and self.system.lower() in ["kinect", "qualisys", "kualisys"]:

            if verbosity > 1:
                print(f"\tSystem set manually on {self.system.lower()}.")

        elif self.system == "auto":

            if verbosity > 1:
                print(f"\tSystem set on \"auto\". Trying to detect the system...")

            if "system" in self.metadata:
                self.system = self.metadata["system"]

                if verbosity > 1:
                    print(f"\tSystem set on {self.system} from metadata.")

            else:

                standard_joints = []
                possible_system = None

                if "Head" in self.joint_labels:
                    standard_joints = load_joint_labels("kinect")
                    possible_system = "kinect"
                elif "RShoulderTop" in self.joint_labels:
                    standard_joints = load_joint_labels("kinect", "all", "original")
                    possible_system = "qualisys"
                elif "ShoulderTopRight" in self.joint_labels:
                    standard_joints = load_joint_labels("qualisys", "all", "krajjat")
                    possible_system = "kualisys"
                else:
                    possible_system = None
                    self.system = None

                if possible_system is not None:
                    if set(standard_joints).issubset(set(self.joint_labels)):
                        self.system = possible_system
                    else:
                        self.system = None

                if verbosity > 1:
                    print(f"\tSystem set on {self.system} from matching joint labels.")

        else:
            self.system = None

            if verbosity > 1:
                print(f"\tSystem set on {self.system}.")

        self.metadata["system"] = self.system

    # === Calculation functions ===
    def _calculate_relative_timestamps(self):
        """For all the poses of the sequence, sets and converts the relative_timestamp attribute taking the first pose
        of the sequence as reference. This function is called internally any time a sequence is created.

        .. versionadded:: 2.0
        """

        # Validity check
        self.time_unit = self.time_unit.lower().replace(" ", "")  # Removes spaces
        units = ["ns", "1ns", "10ns", "100ns", "µs", "1µs", "10µs", "100µs", "ms", "1ms", "10ms", "100ms",
                 "s", "sec", "1s", "min", "mn", "h", "hr", "d", "day"]
        if self.time_unit not in units:
            raise Exception("Invalid time unit. Should be ns, µs, ms or s.")

        if len(self.poses) > 0:
            t = self.poses[0].get_timestamp()
            for p in range(len(self.poses)):
                if self.poses[p].timestamp - t < 0:
                    raise ImpossibleTimeTravelException(p, 0, self.poses[p].timestamp, t, len(self.poses), "pose")
                elif p > 0:
                    if self.poses[p].timestamp - self.poses[p - 1].timestamp < 0:
                        raise ImpossibleTimeTravelException(p, p - 1, self.poses[p].timestamp, self.poses[p - 1].timestamp,
                                                            len(self.poses), "pose")
                self.poses[p]._calculate_relative_timestamp(t)

    # === Getter functions ===
    def get_path(self):
        """Returns the attribute :attr:`path` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The path of the sequence.

        Examples
        --------
        >>> sequence = Sequence("recordings/sequence_12.tsv")
        >>> sequence.get_path()
        recordings\\sequence_12.tsv
        >>> sequence = Sequence("test_sequences/test_sequence_individual/*.tsv")
        >>> sequence.get_path()
        test_sequences\\test_sequence_individual
        """
        return self.path

    def get_name(self):
        """Returns the attribute :attr:`name` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The name of the sequence.

        Examples
        --------
        >>> sequence = Sequence("test_sequence_13.tsv")
        >>> sequence.get_name()
        test_sequence_13.tsv
        >>> sequence = Sequence("test_sequence_14.tsv", name="seq_14")
        >>> sequence.get_name()
        seq_15
        >>> sequence = Sequence("test_sequence_individual/*.tsv", name="seq_15")
        >>> sequence.get_name()
        test_sequence_indiviual
        >>> sequence = Sequence()
        >>> sequence.get_name()
        Unnamed sequence
        """
        return self.name

    def get_condition(self):
        """Returns the attribute :attr:`condition` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The experimental condition in which the recording of the sequence was performed.

        Examples
        --------
        >>> sequence = Sequence("test_sequence_16.tsv")
        >>> sequence.get_condition()
        None
        >>> sequence = Sequence("test_sequence_17.tsv", condition="English")
        >>> sequence.get_condition()
        English
        """
        return self.condition

    def get_system(self):
        """Returns the attribute :attr:`system` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The recording system used to perform the recording.

        Examples
        --------
        >>> sequence = Sequence("sequences/kinect/sequence_18.json")
        >>> sequence.get_system()
        kinect
        >>> sequence = Sequence("sequences/qualisys/sequence_19.tsv")
        >>> sequence.get_system()
        qualisys
        """
        return self.system

    def get_joint_labels(self):
        """Returns the joint labels present in each pose of the Sequence.

        .. versionadded:: 2.0

        Returns
        -------
        list
            The list of the joint labels present in each pose of the Sequence.

        Example
        -------
        >>> sequence = Sequence("Sequences/Fiona/sequence_20.tsv")
        >>> sequence.get_joint_labels()
        ["Head", "HandRight", "HandLeft"]
        """
        return self.joint_labels

    def get_number_of_joints(self):
        """Returns the number of joints in each pose of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of joints in each pose of the sequence.

        Example
        -------
        >>> sequence = Sequence("Sequences/Kinect/sequence_21.json")
        >>> sequence.get_number_of_joints()
        21
        """
        return len(self.joint_labels)

    def get_date_recording(self, return_type="datetime"):
        """Returns the date and time of the recording as a datetime object, if it exists. If the date of the recording
        was not specified in the original file, the value will be None.

        .. versionadded:: 2.0

        Parameters
        ----------
        return_type: str, optional
            The format of the date to return. By default, `"datetime"` is used. If set on `"str"`, a string containing
            the weekday, day, month (in letters), year, hour (24-hour format), minutes and seconds will be returned
            (e.g. ``"Wednesday 21 October 2015, 07:28:00"``).

        Returns
        -------
        datetime|str
            The date and time of the first frame of the recording.

        Example
        -------
        >>> sequence = Sequence("Sequences/Arthur/sequence_22.json")
        >>> sequence.get_date_recording()
        datetime.datetime(2015, 10, 21, 7, 28, 0)
        >>> sequence.get_date_recording("str")
        Wednesday 21 October 2015, 07:28:00
        """
        if return_type == "datetime":
            return self.date_recording

        elif return_type == "str":
            days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
            months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                      7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

            if self.date_recording is not None:
                day = days[self.date_recording.weekday()] + " "
                month = months[self.date_recording.month] + " "
                date = day + str(self.date_recording.day) + " " + month + str(self.date_recording.year) + ", " + \
                       str(self.date_recording.hour).zfill(2) + ":" + str(self.date_recording.minute).zfill(2) + ":" + \
                       str(self.date_recording.second).zfill(2)
            else:
                date = "No date found"

            return date

        else:
            raise InvalidParameterValueException("return_type", return_type, ["datetime", "str"])

    def get_subject_height(self, joints_list=None, verbosity=1):
        """Returns an estimation of the height of the subject, in meters, based on the successive distances between a
        series of joints. The successive distances are calculated for each pose, and averaged across all poses. Some
        joints are imaginary, based on the average of the position of two or four joints.

        .. versionadded:: 2.0

        • For the Kinect system, the joints used are ``"Head"``, ``"Neck"``, ``"SpineShoulder"``, ``"SpineMid"``,
          ``"SpineBase"``, the average between ``"KneeRight"`` and ``"KneeLeft"``, the average between
          ``"AnkleRight"`` and ``"AnkleLeft"``, and the average between ``"FootRight"`` and ``"FootLeft"``.
        • For the Qualisys system, the joints used are ``"Head Top"``, the average between ``"ShoulderTopRight"``
          and ``"ShoulderTopLeft"``, ``"Chest"``, the average between ``"WaistBackRight"``, ``"WaistBackLeft"``,
          ``"WaistFrontRight"`` and ``"WaistFrontLeft"``, the average between ``"KneeRight"`` and ``"KneeLeft"``,
          the average between ``"AnkleRight"`` and ``"AnkleLeft"``, and the average between ``"ForefootOutRight"``
          and ``"ForefootOutLeft"``.

        Note
        ----
        This method is based on estimations and might not reflect the true height of the subjects - which depends also
        on the quality of the data.

        Parameters
        ----------
        joints_list: list, optional
            A list of joint labels, of which the successive distances will be calculated. If set on `None` (default),
            this parameter is ignored and the height is estimated by using the pre-set joints listed above. If set,
            the joints used in this parameter replace the presets.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        float
            The estimated height of the subject, in meters.

        Raises
        ------
        NoExistingJointListPresetException
            If the recording system is not set for a Sequence instance.
        InvalidJointLabelException
            If at least one joint in a preset is missing from the Sequence instance.

        Example
        -------
        >>> sequence = Sequence("Sequences/Nora/sequence_23.json")
        >>> sequence.get_subject_height()
        1.7356669872340
        """

        kinect_joints = ["Head", "Neck", "SpineShoulder", "SpineMid", "SpineBase", ["KneeRight", "KneeLeft"],
                         ["AnkleRight", "AnkleLeft"], ["FootRight", "FootLeft"]]
        qualisys_joints = ["HeadTop", ["RShoulderTop", "LShoulderTop"], "Chest",
                           ["WaistRBack", "WaistLBack", "WaistRFront", "WaistLFront"],
                           ["RKneeOut", "LKneeOut"], ["RAnkleOut", "LAnkleOut"], ["RForefootOut", "LForefootOut"]]
        kualisys_joints = ["HeadTop", ["ShoulderTopRight", "ShoulderTopLeft"], "Chest",
                           ["WaistBackRight", "WaistBackLeft", "WaistFrontRight", "WaistFrontLeft"],
                           ["KneeRight", "KneeLeft"], ["AnkleRight", "AnkleLeft"],
                           ["ForefootOutRight", "ForefootOutLeft"]]

        if joints_list is None:
            if self.system == "kinect":
                joints_list = kinect_joints
            elif self.system == "qualisys":
                joints_list = qualisys_joints
            elif self.system == "kualisys":
                joints_list = kualisys_joints
            else:
                raise NoExistingJointListPresetException("the subject height", self.system)

        height_sum = 0  # Summing the heights through all poses to average

        if verbosity > 1:
            print("Calculating the height of the subject based on the poses...")

        for p in range(len(self.poses)):

            pose = self.poses[p]  # Current pose
            dist = 0  # Height for the current pose
            joints = []  # Joints and average joints

            # Getting the average joints
            for i in range(len(joints_list)):

                if type(joints_list[i]) is list:
                    for joint_label in joints_list[i]:
                        if joint_label not in self.joint_labels:
                            raise InvalidJointLabelException(joints_list[i])
                else:
                    if joints_list[i] not in self.joint_labels:
                        raise InvalidJointLabelException(joints_list[i])

                if type(joints_list[i]) is list:
                    joint = pose.generate_average_joint(joints_list[i], "Average", False)
                else:
                    joint = pose.joints[joints_list[i]]

                joints.append(joint)

            # Calculating the distance
            for i in range(len(joints) - 1):
                dist += calculate_distance(joints[i], joints[i + 1])

            if verbosity > 1:
                print(
                    "\tHeight on frame " + str(p + 1) + "/" + str(len(self.poses)) + ": " + str(round(dist, 3)) + " m.")
            height_sum += dist

        height = height_sum / len(self.poses)

        if verbosity == 1:
            print("Average height estimated at " + str(round(height, 3)) + " m.")

        return height

    def get_subject_arm_length(self, side="left", verbosity=1):
        """Returns an estimation of the length of the left or right arm of the subject, in meters. The length of the arm
        is calculated for each pose, and averaged across all poses.

        .. versionadded:: 2.0

        • For the Kinect system, the joints used to get the length of the left arm are ``"ShoulderLeft"``,
          ``"ElbowLeft"``, ``"WristLeft"`` and ``"HandLeft"``. For the right arm, the joints are their equivalent on the
          right side.
        • For the Qualisys system, the joints used to get the length of the left arm are ``"ShoulderTopLeft"``,
          ``"ArmLeft"``, ``"ElbowLeft"``, ``"WristOutLeft"`` and ``"HandOutLeft"``. For the right arm, the joints are
          their equivalent on the right side.

        Parameters
        ----------
        side: str
            The side of the arm you want to measure, either ``"left"`` or ``"right"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        float
            The estimated arm length of the subject, in meters.

        Raises
        ------
        NoExistingJointListPresetException
            If the recording system is not set for a Sequence instance.
        InvalidJointLabelException
            If at least one joint in a preset is missing from the Sequence instance.

        Example
        -------
        >>> sequence = Sequence("Sequences/Nora/sequence_23.json")
        >>> sequence.get_subject_arm_length("left")
        0.7321786536565029
        """

        kinect_joints = ["Shoulder", "Elbow", "Wrist", "Hand"]
        qualisys_joints = ["ShoulderTop", "Arm", "ElbowOut", "WristOut", "HandOut"]
        kualisys_joints = ["ShoulderTop", "Arm", "Elbow", "WristOut", "HandOut"]

        if self.system == "kinect":
            list_joints = kinect_joints
        elif self.system == "qualisys":
            list_joints = qualisys_joints
        elif self.system == "kualisys":
            list_joints = kualisys_joints
        else:
            raise NoExistingJointListPresetException("the subject arm length", self.system)

        if side.lower() == "left":
            if self.system == "qualisys":
                list_joints = ["L" + joint_label for joint_label in list_joints]
            else:
                list_joints = [joint_label + "Left" for joint_label in list_joints]
        elif side.lower() == "right":
            if self.system == "qualisys":
                list_joints = ["R" + joint_label for joint_label in list_joints]
            else:
                list_joints = [joint_label + "Right" for joint_label in list_joints]
        else:
            raise InvalidParameterValueException("side", side, ["left", "right"])

        for i in range(len(list_joints)):

            if type(list_joints[i]) is list:
                for joint_label in list_joints[i]:
                    if joint_label not in self.joint_labels:
                        raise InvalidJointLabelException(list_joints[i])
            else:
                if list_joints[i] not in self.joint_labels:
                    raise InvalidJointLabelException(list_joints[i])

        arm_length_sum = 0  # Summing the arm_lengths through all poses to average

        if verbosity > 1:
            print("Calculating the " + side.lower() + " arm length of the subject based on the poses...")

        for p in range(len(self.poses)):

            pose = self.poses[p]  # Current pose
            dist = 0  # Arm length for the current pose

            # Calculating the distance
            for i in range(len(list_joints) - 1):
                dist += calculate_distance(pose.joints[list_joints[i]], pose.joints[list_joints[i + 1]])

            if verbosity > 1:
                print("\t" + side + " arm length on frame " + str(p + 1) + "/" + str(len(self.poses)) + ": " + str(
                    round(dist, 3)) + " m.")
            arm_length_sum += dist

        arm_length = arm_length_sum / len(self.poses)

        if verbosity == 1:
            print("Average " + side.lower() + " arm length estimated at " + str(round(arm_length, 3)) + " m.")

        return arm_length

    def get_info(self, return_type="dict", full=True, verbosity=1):
        """Returns information and statistics regarding the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        return_type: bool, optional
            If set on ``"dict"`` (default), the info is returned as an OrderedDict. If set on ``"table"``, the info
            is returned as a two-dimensional list, ready to be exported as a table. If set on ``"str"``, a printable
            string is returned.

        full: bool, optional
            If set on ``True`` (default), the method returns all the elements mentioned below. If set on
            ``False``, a subset of these elements is returned (name, condition (if set), date of recording, duration,
            number of poses, and number of joint labels). If `return_type` is set on ``"str"``, the elements are printed on
            different lines if `full` is set on ``True``, and on one line if set on ``False``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        OrderedDict|list(list)|str
            If the returned object is an OrderedDict, the keys are the title of a statistic, and the values are their
            matching value. If the returned object is a two-dimensional list, each sublist contains the title as the
            first element, and the value as the second element.
            The data included contains:

            • ``"Name"``: The :attr:`name` attribute of the sequence.
            • ``"Path"``: The :attr:`path` attribute of the sequence.
            • ``"Condition"``: The :attr:`condition` attribute of the sequence (if set).
            • ``"Duration"``: Output of :meth:`Sequence.get_duration` (seconds).
            • ``"Number of poses"``: Output of :meth:`Sequence.get_number_of_poses`.
            • ``"Number of joint labels"``: The length of :attr:`joint_labels` attribute of the sequence.
            • ``"Date of recording"``: Output of :meth:`Sequence.get_printable_date_recording`.
            • ``"Subject height"``: Output of :meth:`Sequence.get_subject_height` (meters).
            • ``"Left arm length"``: Output of :meth:`Sequence.get_subject_arm_length` for the left arm (meters).
            • ``"Right arm length"``: Output of :meth:`Sequence.get_subject_arm_length` for the right arm (meters).
            • ``"Average framerate"``: Output of :meth:`Sequence.get_average_framerate`.
            • ``"SD framerate"``: Standard deviation of the framerate of the sequence.
            • ``"Min framerate"``: Output of :meth:`Sequence.get_min_framerate`.
            • ``"Max framerate"``: Output of :meth:`Sequence.get_max_framerate`.
            • ``"Fill level X"``: Output of :meth:`Sequence.get_fill_level_per_joint`.
            • ``"Average velocity X"``: Output of :meth:`Sequence.get_total_velocity_single_joint` divided by the
              total number of poses. This key has one entry per joint label.

        Example
        -------
        >>> sequence = Sequence("Sequences/Jacob/sequence_24.json")
        >>> sequence.get_info()
        OrderedDict({'Name': 'sequence_24', 'Condition': None, Path': 'Sequences\\Jacob\\sequence_24.json',
        'Date of recording': 'Tuesday 10 August 2021, 15:08:40', 'Duration': 79.0833823, 'Number of poses': 1269,
        'Number of joint labels': 21, 'Subject height': 1.6200255058925102, ...})
        """
        stats = OrderedDict()
        stats["Name"] = self.name
        if full:
            stats["Path"] = self.path
        if full or self.condition is not None:
            stats["Condition"] = self.condition
        stats["Duration"] = self.get_duration()
        stats["Number of poses"] = self.get_number_of_poses()
        stats["Number of joint labels"] = len(self.joint_labels)
        stats["Date of recording"] = self.get_date_recording("str")

        if full:
            # Height and distances stats
            try:
                stats["Subject height"] = self.get_subject_height(verbosity=0)
            except NoExistingJointListPresetException:
                if verbosity > 0:
                    print(f"Could not calculate the subject height as no preset exists for the system ({self.system})")
            except InvalidJointLabelException:
                if verbosity > 0:
                    print("Could not calculate the subject height because of missing joints.")
                stats["Subject height"] = None

            try:
                stats["Left arm length"] = self.get_subject_arm_length("left", 0)
            except NoExistingJointListPresetException:
                if verbosity > 0:
                    print(f"Could not calculate the length of the left arm as no preset exists for the system " +
                          f"({self.system})")
            except InvalidJointLabelException:
                if verbosity > 0:
                    print("Could not calculate the length of the left arm because of missing joints.")
                stats["Left arm length"] = None

            try:
                stats["Right arm length"] = self.get_subject_arm_length("right", 0)
            except NoExistingJointListPresetException:
                if verbosity > 0:
                    print(f"Could not calculate the length of the right arm as no preset exists for the system " +
                          f"({self.system})")
            except InvalidJointLabelException:
                if verbosity > 0:
                    print("Could not calculate the length of the right arm because of missing joints.")
                stats["Right arm length"] = None

            # Framerate stats
            frequencies = self.get_sampling_rates()

            if self.has_stable_sampling_rate():
                stats["Stable sampling rate"] = True
                stats["Sampling rate"] = self.get_sampling_rate()

            else:
                stats["Stable sampling rate"] = False
                sampling_rates = self.get_sampling_rates()
                stats["Average sampling rate"] = np.mean(sampling_rates)
                if frequencies.size < 2:
                    stats["SD sampling rate"] = None
                else:
                    stats["SD sampling rate"] = stdev(frequencies)
                stats["Min sampling rate"] = np.min(sampling_rates)
                stats["Max sampling rate"] = np.max(sampling_rates)

            # Fill level stats
            for joint_label in self.joint_labels:
                stats["Fill level " + joint_label] = self.get_fill_level(joint_label)

            # Movement stats
            if self.has_stable_sampling_rate() and len(self.poses) >= 2:
                for joint_label in self.poses[0].joints.keys():
                    stats["Average velocity " + joint_label] = (self.get_sum_measure("velocity", joint_label,
                                                                                     window_length=min(len(self.poses)
                                                                                                       - 1, 7),
                                                                                     absolute=True) / len(self.poses))
        else:
            if verbosity > 0:
                print("Could not calculate the average velocity for each joint as the sampling rate is variable.")

        if return_type.lower() in ["list", "table"]:
            table = [[], []]
            for key in stats.keys():
                table[0].append(key)
                table[1].append(stats[key])
            return table

        elif return_type.lower() == "str":
            if full:
                string = ""
                for key in stats.keys():
                    if key == "Duration":
                        string += f"{key}: {stats[key]} s\n"
                    elif key in ["Subject height", "Left arm length", "Right arm length"]:
                        if stats[key] is None:
                            string += f"{key}: Not available\n"
                        else:
                            string += f"{key}: {round(stats[key], 3)} m\n"
                    elif "Fill level" in key:
                        f"{key}: {round(stats[key] * 100, 2)} %\n"
                    elif "Average velocity" in key:
                        f"{key}: {round(stats[key] * 1000, 1)} mm/s\n"
                    else:
                        string += f"{key}: {stats[key]}\n"

                if string[-1] == "\n":
                    string = string[:-1]

                return string
            else:
                return " · ".join([f"{key}: {stats[key]}" for key in stats.keys()])

        return stats

    def get_fill_level(self, joint_label=None):
        """Returns the ratio of poses for which a coordinates of one or multiple joints are not equal to ``(0, 0, 0)``,
        or ``(None, None, None)``. If  the ratio is 1, the joint was tracked correctly for the whole duration of the
        sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: list(str)|str|None
            A joint label (e.g. ``"Head"``), a list of joint labels (e.g. ``["Head", "HandRight"]``), or ``None``
            (default - in that case, the fill level will be calculated for all the joints).

        Returns
        --------
        dict(str: float)|float
            A dictionary with the joint labels as keys, and the ratio (between 0 and 1) of poses where the coordinates
            of the joint are present - if a single joint has been passed as parameter, the ratio is returned directly.

        Examples
        --------
        >>> sequence = Sequence("Walt/sequence_39.json")
        >>> sequence.get_fill_level()
        {"Head": 1.0, "HandRight": 0.998}
        >>> sequence.get_fill_level("Head")
        1.0
        """

        if type(joint_label) is list:
            joint_labels = joint_label
        elif type(joint_label) is str:
            joint_labels = [joint_label]
        elif joint_label is None:
            joint_labels = self.joint_labels
        else:
            raise InvalidParameterValueException("joint_label", joint_label, ["None", "str", "list"])

        fill_levels = {}

        for joint_label in joint_labels:
            i = 0
            for p in range(len(self.poses)):
                if not self.poses[p].joints[joint_label].is_zero() and not self.poses[p].joints[joint_label].is_none():
                    i += 1

            fill_levels[joint_label] = i / len(self.poses)

        if len(fill_levels) == 1:
            return fill_levels[joint_label]
        else:
            return fill_levels

    def get_poses(self):
        """Returns the attribute :attr:`poses` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        list(Pose)
            A list containing all the Pose objects in the sequence, in chronological order.

        Example
        -------
        >>> sequence = Sequence("Barney/sequence_25.json")
        >>> sequence.get_poses()
        """
        return self.poses

    def get_pose(self, pose_index):
        """Returns the pose instance corresponding to the index passed as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose.

        Returns
        -------
        Pose
            A pose from the sequence.

        Raises
        ------
        InvalidPoseIndexException
            If the index is not an integer, below 0, or over the length of the Sequence.

        Example
        -------
        >>> sequence = Sequence("Jack/sequence_26.json")
        >>> sequence.get_pose(42)
        """
        if len(self.poses) == 0:
            raise EmptyInstanceException("Sequence")
        elif not type(pose_index) is int or not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))

        return self.poses[pose_index]

    def get_pose_index_from_timestamp(self, timestamp, method="closest", use_relative_timestamps=True):
        """Returns the closest pose index from the provided timestamp.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp: float
            A relative timestamp, in seconds.
        method: str, optional
            This parameter can take multiple values:

            • If set on ``"closest"`` (default) or ``"nearest"``, returns the closest pose index from the timestamp.
            • If set on ``"below"``, ``"lower"`` or ``"under"``, returns the closest pose index below the timestamp.
            • If set on ``"above"``, ``"higher"`` or ``"over"``, returns the closest pose index above the timestamp.

        use_relative_timestamps: bool, optional
            Defines if the timestamps ``start`` and ``end`` refer to the original timestamps or the relative timestamps.

        Note
        ----
        If the provided timestamp matches exactly the timestamp of a pose from the sequence, the pose index is returned,
        and the parameter ``method`` is ignored.

        Examples
        --------
        >>> sequence = Sequence("Kate/sequence_27.json", time_unit="s")  # Timestamps: 0, 1, 2, 3, 4
        >>> sequence.get_pose_index_from_timestamp(2)
        2
        >>> sequence.get_pose_index_from_timestamp(2.2)
        2
        >>> sequence.get_pose_index_from_timestamp(1.8)
        2
        >>> sequence.get_pose_index_from_timestamp(1.5)
        1
        >>> sequence.get_pose_index_from_timestamp(1.8, "lower")
        1
        >>> sequence.get_pose_index_from_timestamp(2.2, "higher")
        3
        """

        timestamps = np.array(self.get_timestamps(use_relative_timestamps))
        if method.lower() in ["closest", "nearest"]:
            timestamps_dist = timestamps - timestamp
            return np.argmin(np.abs(timestamps_dist))
        elif method.lower() in ["below", "lower", "under"]:
            mask = timestamps <= timestamp
            timestamp_below_indices = np.where(mask)[0]
            timestamps_below = timestamps[timestamp_below_indices]
            return timestamp_below_indices[np.argmax(timestamps_below)]
        elif method.lower() in ["above", "higher", "over"]:
            mask = timestamps >= timestamp
            timestamp_above_indices = np.where(mask)[0]
            timestamps_above = timestamps[timestamp_above_indices]
            return timestamp_above_indices[np.argmin(timestamps_above)]
        else:
            raise InvalidParameterValueException("method", method, ["closest", "nearest", "below", "lower", "under",
                                                                     "above", "higher", "over"])

    def get_pose_from_timestamp(self, timestamp, method="closest"):
        """Returns the closest pose from the provided timestamp.

        .. versionadded:: 2.0

        Note
        ----
        This function is a wrapper for the function :meth:`get_pose_index_from_timestamp`.

        Parameters
        ----------
        timestamp: float
            A relative timestamp.
        method: str, optional
            This parameter can take multiple values:

            • If set on ``"closest"`` (default) or ``"nearest"``, returns the closest pose index from the timestamp.
            • If set on ``"below"``, ``"lower"`` or ``"under"``, returns the closest pose index below the timestamp.
            • If set on ``"above"``, ``"higher"`` or ``"over"``, returns the closest pose index above the timestamp.

        Examples
        --------
        >>> sequence = Sequence("Charlie/sequence_28.json", time_unit="s")  # Timestamps: 0, 1, 2, 3, 4
        >>> sequence.get_pose_from_timestamp(2)  # Returns Pose with index 2
        >>> sequence.get_pose_from_timestamp(2.2)  # Returns Pose with index 2
        >>> sequence.get_pose_from_timestamp(1.8)  # Returns Pose with index 2
        >>> sequence.get_pose_from_timestamp(1.5)  # Returns Pose with index 1
        >>> sequence.get_pose_from_timestamp(1.8, "lower")  # Returns Pose with index 1
        >>> sequence.get_pose_from_timestamp(2.2, "higher")  # Returns Pose with index 3
        """
        return self.poses[self.get_pose_index_from_timestamp(timestamp, method)]

    def get_number_of_poses(self):
        """Returns the number of poses in the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of poses in the sequence.

        Example
        -------
        >>> sequence = Sequence("Sayid/sequence_29.json", time_unit="s")
        >>> sequence.get_number_of_poses()
        108
        """
        return len(self.poses)

    def get_timestamps(self, relative=False, timestamp_start=None, timestamp_end=None):
        """Returns a list of the timestamps for every pose, in seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        relative: boolean
            Defines if the returned timestamps are relative to the first pose (in that case, the timestamp of the first
            pose will be 0), or the original timestamps.
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
            This timestamp is inclusive.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.
            This timestamp is inclusive.

        Returns
        -------
        list(float)
            List of the timestamps of all the poses of the sequence, in seconds.

        Examples
        --------
        >>> sequence = Sequence("Shannon/sequence_30.json", time_unit="s")
        >>> sequence.get_timestamps()
        [14.23, 14.235, 14.24, 14.245, 14.25]
        >>> sequence.get_timestamps(relative=True)
        [0, 0.005, 0.01, 0.015, 0.02]
        >>> sequence.get_timestamps(relative=True, timestamp_start=0.01, timestamp_end=0.5)
        [0.01, 0.015, 0.02]
        """

        if len(self.poses) == 0:
            return []

        if timestamp_start is None:
            if relative:
                timestamp_start = self.poses[0].get_relative_timestamp()
            else:
                timestamp_start = self.poses[0].get_timestamp()

        if timestamp_end is None:
            if relative:
                timestamp_end = self.poses[-1].get_relative_timestamp()
            else:
                timestamp_end = self.poses[-1].get_timestamp()

        timestamps = []
        for pose in self.poses:
            if relative:
                t = pose.get_relative_timestamp()
            else:
                t = pose.get_timestamp()
            if timestamp_start <= t <= timestamp_end:
                timestamps.append(t)

        return timestamps

    def get_time_between_poses(self, index_pose_1, index_pose_2):
        """Returns the difference between the timestamps of two poses, in seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        index_pose_1: int
            The index of the first pose.
        index_pose_2: int
            The index of the second pose.

        Returns
        -------
        float
            The time difference (in seconds) between the two poses.

        Note
        ----
        If the index of the second pose is inferior to the index of the first pose, the difference will be negative.

        Example
        -------
        >>> sequence = Sequence("Boone/sequence_31.json")
        >>> sequence.get_timestamps()
        [0, 0.5, 1, 1.5, 2, 2.5, 3]
        >>> sequence.get_time_between_poses(2, 5)
        1.5
        """
        timestamp1 = self.poses[index_pose_1].relative_timestamp
        timestamp2 = self.poses[index_pose_2].relative_timestamp
        return timestamp2 - timestamp1

    def get_duration(self):
        """Returns the duration of the sequence, in seconds.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The duration of the sequence, in seconds.

        Example
        -------
        >>> sequence = Sequence("John/sequence_32.json")
        >>> sequence.get_duration()
        38.72
        """
        return self.poses[-1].relative_timestamp

    def get_sampling_rate(self):
        """Returns the number of poses per second of the sequence, only if this one is stable. If the frequency is
        variable, the function returns an error message.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The number of poses per second (or Hertz) for the sequence, if this number is stable.

        Raises
        ------
        VariableSamplingRateException
            If the sampling rate of the sequence is not constant across all poses.

        Example
        -------
        >>> sequence = Sequence("Claire/sequence_33.json")
        >>> sequence.get_sampling_rate()
        200
        """
        framerates = self.get_sampling_rates()
        if self.has_stable_sampling_rate():
            return framerates[0]
        else:
            raise VariableSamplingRateException(self.name)

    def get_sampling_rates(self):
        """Returns a list of the frequencies of poses per second and a list of the matching timestamps. This function
        calculates, for each pose, the inverse of the time elapsed since the previous pose (in seconds), in order to
        obtain a list of framerates across time.

        .. versionadded:: 2.0

        Returns
        -------
        list(float)
            Framerates for all the poses of the sequence, starting on the second pose.

        Note
        ----
        Because the framerates are calculated by consecutive pairs of poses, the returned list has a length of
        :math:`n-1`, with :math:`n` being the number of poses of the sequence.

        Example
        -------
        >>> sequence = Sequence("Claire/sequence_33.json")
        >>> sequence.get_sampling_rates()
        [100, 102.32, 99.48, 101.9, 103.5]
        """
        return 1 / (np.array(self.get_timestamps(relative=True)[1:]) - np.array(self.get_timestamps(relative=True)[:-1]))

    def has_stable_sampling_rate(self):
        """Returns a boolean indicating if the sequence has a stable sampling rate.

        .. versionadded:: 2.0

        Returns
        -------
        bool
            A boolean indicating if the sequence has a stable sampling rate.

        Examples
        --------
        >>> sequence = Sequence("Nikki/sequence_34.json")  # Timestamps [0, 0.1, 0.2]
        >>> sequence.has_stable_sampling_rate()
        True
        >>> sequence = Sequence("Paulo/sequence_35.json")  # Timestamps [0, 0.09, 0.21]
        >>> sequence.has_stable_sampling_rate()
        False
        """
        framerates = self.get_sampling_rates()
        return np.allclose(framerates, np.ones(framerates.size) * framerates[0])

    def get_measure(self, measure, joint_label=None, timestamp_start=None, timestamp_end=None, window_length=7,
                    poly_order=None, absolute=False, use_relative_timestamps=True, verbosity=1):
        """Returns an array of coordinates, distances, or derivatives of the distance for one or multiple joints
        from the Sequence instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        measure: str|int
            The measure to return for each of the joints. This parameter can take multiple values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"``, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"``, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"``, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.
            • For any derivative of a higher order, set the corresponding integer.

            The measure can be suffixed by ``_abs`` to obtain its absolute values. In that case, the parameter
            ``absolute`` is ignored.

        joint_label: str|list(str)|None, optional
            The joint labels or joint labels you want to return the measures from. If set on ``None`` (default),
            a dictionary containing all the joints as keys will be returned. If set on a string, an array matching
            the requested measure for the specified joint label will be returned. Finally, if set on a list of joint
            labels, a dictionary containing the specified subset of joint labels will be returned.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
            This parameter is inclusive: if a timestamp is equal to this value, the corresponding pose will be included.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.
            This parameter is inclusive: if a timestamp is equal to this value, the corresponding pose will be included.

        window_length: int, optional
            The length of the window for the Savitzky–Golay filter when calculating a derivative (default: 7). See
            `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
            for more info.

        poly_order: int|None, optional
            The order of the polynomial for the Savitzky–Golay filter. If set on `None`, the polynomial will be set to
            one over the derivative rank. See
            `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
            for more info.

        absolute: bool, optional
            If set on ``True``, the returned values will be absolute. By default, the parameter is set on ``False``.

        use_relative_timestamps: bool, optional
            Defines if the timestamps ``timestamp_start`` and ``timestamp_end`` refer to the original timestamps or
            the relative timestamps, and if the returned timestamps should be original or relative.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Note
        ----
        When selecting single coordinates, for each joint, the array will be of dimension :math:`1̀×p`, with :math:`p`
        being the number of poses in the sequence (or a subset if ``timestamp_start`` or ``timestamp_end`` have been
        specified). When selecting all the coordinates, the array will be of dimension :math:`3×p`. For every other
        measure, because the distances are calculated on consecutive poses, the array will be of dimension
        :math:`1×(p-1)`.

        Note
        ----
        The derivatives can only be calculated if the sampling rate of the sequence is constant. If it is not,
        the function will raise an exception.

        Important
        ---------
        If using single letters for the parameter ``measure``, beware that ``"s"`` stands for ``"snap"`` (4th
        derivative of the distance) and not for ``"speed"`` - use ``"v"`` for ``"velocity"`` instead.

        Returns
        -------
        np.ndarray|dict(str: np.ndarray)
            An array containing the requested measure if a single joint has been requested, or a dictionary
            where an array of the measure is associated to each joint label.

        Examples
        --------
        >>> sequence = Sequence("Bernard/sequence_36.json")
        >>> sequence.get_measure("x", "Head")
        [0.95845, 0.94222, 0.89631]
        >>> sequence.get_measure("velocity", "Head")
        [1.32268, 1.48962]
        >>> sequence.get_measure("acceleration")
        {"Head": [14.32589, 98.74512], "HandRight": [-48.15162, -3.42108]}
        """

        # Joint labels
        if joint_label is None:
            joint_labels = self.joint_labels
        elif type(joint_label) is str:
            joint_labels = [joint_label]
        elif type(joint_label) is list:
            joint_labels = joint_label
        else:
            raise InvalidParameterValueException("joint_label", joint_label, ["None", "str", "list"])

        for joint_label in joint_labels:
            if joint_label not in self.joint_labels:
                raise InvalidJointLabelException(joint_label)

        # Timestamps
        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        if timestamp_start > timestamp_end:
            raise Exception(f"The parameter timestamp_start ({timestamp_start}) must be lower than timestamp_end "
                            f"({timestamp_end}).")

        # Measures
        if type(measure) is str:
            measure = measure.lower()
            if measure.endswith("_abs"):
                measure = measure[:-4]
                absolute = True
        if not type(measure) is int and measure in CLEAN_DERIV_NAMES:
            measure = CLEAN_DERIV_NAMES[measure]
        else:
            raise InvalidParameterValueException("measure", measure, ["x", "y", "z", "coordinates",
                                                 "distance", "velocity", "acceleration", "jerk", "snap", "crackle",
                                                 "pop"])

        if verbosity > 1:
            if measure in ["x", "y", "z"]:
                print(f"Getting the {measure} coordinate for {len(joint_labels)} joint label(s): " +
                      f"{', '.join(joint_labels)}.")
            else:
                print(f"Getting the {measure} for {len(joint_labels)} joint label(s): {', '.join(joint_labels)}.")

        measures = {}

        # Get the measures
        for joint_label in joint_labels:

            if verbosity > 1:
                print(f"\t{joint_label}")

            # Placeholder arrays
            if measure == "coordinates":
                measures[joint_label] = np.zeros((len(self.poses), 3))
            else:
                measures[joint_label] = np.zeros(len(self.poses))

            start = None
            end = None

            for p in range(len(self.poses)):

                if p == 0 and measure not in ["x", "y", "z", "coordinates"]:
                    if verbosity > 1:
                        print(f"\t\tPose with index {p} · Ignoring this pose as a distance or derivative is " +
                              f"calculated.")
                    continue

                pose = self.poses[p]

                if verbosity > 1:
                    print(f"\t\tPose with index {p}", end=" ")

                if use_relative_timestamps:
                    timestamp = pose.get_relative_timestamp()
                else:
                    timestamp = pose.get_timestamp()

                if timestamp_start <= timestamp <= timestamp_end:

                    if start is None:
                        if verbosity > 1:
                            print(f"· Defining as starting pose", end=" ")
                        start = p

                    if measure in ["x", "y", "z"]:
                        measures[joint_label][p] = pose.joints[joint_label].get_coordinate(measure)
                        if verbosity > 1:
                            print(f"· Value: {measures[joint_label][p]}")

                    elif measure in ["coordinates"]:
                        measures[joint_label][p] = pose.joints[joint_label].get_position()
                        if verbosity > 1:
                            print(f"· Value: {measures[joint_label][p]}")

                    elif measure in ["distance x", "distance y", "distance z"]:
                        measures[joint_label][p] = calculate_distance(self.poses[p - 1].joints[joint_label],
                                                                      self.poses[p].joints[joint_label],
                                                                      measure[-1])
                        if verbosity > 1:
                            print(f"· Value: {measures[joint_label][p]}")

                else:
                    if start is not None and end is None:
                        if verbosity > 1:
                            print(f"· Defining as ending pose", end=" ")
                        end = p

                if measure not in ["x", "y", "z", "coordinates", "distance x", "distance y", "distance z"]:
                    measures[joint_label][p] = calculate_distance(self.poses[p - 1].joints[joint_label],
                                                                  self.poses[p].joints[joint_label])
                    if verbosity > 1:
                        print(f"· Distance value: {measures[joint_label][p]}")

                else:

                    if verbosity > 1:
                        print(f"· No value")

            if start is None:
                raise Exception(f"There are no poses between the provided timestamps ({timestamp_start} and " +
                                f"{timestamp_end}) is zero. If you are trying to get a distance or a derivative, "
                                f"consider that no value will be attributed to the first pose of the sequence.")

            if measure not in ["x", "y", "z", "coordinates", "distance", "distance x", "distance y", "distance z"]:
                if verbosity > 1:
                    print(f"\t\tDistances calculated. Now getting the derivative...")
                measures[joint_label] = calculate_derivative(measures[joint_label][1:], measure, window_length,
                                                             poly_order, freq=self.get_sampling_rate())
                start -= 1
                if end is not None:
                    end -= 1

            measures[joint_label] = measures[joint_label][start:end]

            if absolute:
                measures[joint_label] = np.abs(measures[joint_label])

        if len(measures.keys()) == 1:
            return measures[joint_labels[0]]
        else:
            return measures

    def get_extremum_measure(self, measure, joint_label=None, value="both", per_joint=True, timestamp_start=None,
                             timestamp_end=None, window_length=7, poly_order=None, absolute=False,
                             verbosity=1):
        """Returns the minimum, maximum or both values of the measure for one or multiple joints from the Sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        measure: str|int
            The measure to return for each of the joints. This parameter can take multiple values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"`, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"`, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"`, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.
            • For any derivative of a higher order, set the corresponding integer.

        joint_label: str|list(str)|None, optional
            The joint labels or joint labels you want to return the measures from. If set on ``None`` (default),
            a dictionary containing all the joints as keys will be returned. If set on a string, an array matching
            the requested measure for the specified joint label will be returned. Finally, if set on a list of joint
            labels, a dictionary containing the specified subset of joint labels will be returned.

        value: str, optional
            Defines the value to return. Can be either ``"min"``, ``"max"``, or ``"both"`` (default). In that last case,
            a tuple will be returned for each joint, with the min and the max values, respectively.

        per_joint: bool, optional
            If set on `True` (default), returns the value(s) for each joint in a dictionary (or directly if only one
            joint is specified). If set on `False`, the extreme value(s) across all provided joints will be returned.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
            This parameter is inclusive: if a timestamp is equal to this value, the corresponding pose will be included.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.
            This parameter is inclusive: if a timestamp is equal to this value, the corresponding pose will be included.

        window_length: int, optional
            The length of the window for the Savitzky–Golay filter when calculating a derivative (default: 7). See
            `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
            for more info.

        poly_order: int|None, optional
            The order of the polynomial for the Savitzky–Golay filter. If set on `None`, the polynomial will be set to
            one over the derivative rank. See
            `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
            for more info.

        absolute: bool, optional
            If set on ``True``, the returned values will be absolute. By default, the parameter is set on ``False``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        dict(str: float)|dict(str: (float, float)|(float, float)|float
            A dictionary with joint labels as keys, and an extreme value or a tuple of extreme values as values; if
            only one joint_label has been provided, the returned value will be a single extreme value or a tuple of the
            extreme value(s).

        Examples
        --------
        >>> sequence = Sequence("Rose/sequence_37.json")
        >>> sequence.get_extremum_measure("x", "Head", "min")
        0.12345
        >>> sequence.get_extremum_measure("x", "Head", "min")
        1.42369
        >>> sequence.get_extremum_measure("x", "Head", "both")
        (0.12345, 1.42369)
        >>> sequence.get_extremum_measure("distance")
        {"Head": (14.23695, 89.23647), "HandRight": (1.42367, 8.69511)}
        """

        measures = self.get_measure(measure, joint_label, timestamp_start, timestamp_end, window_length, poly_order,
                                    absolute, verbosity)

        if type(measures) is dict:
            values = {}

            if value == "min":
                for key in measures.keys():
                    values[key] = np.min(measures[key])
            elif value == "max":
                for key in measures.keys():
                    values[key] = np.max(measures[key])
            elif value == "both":
                for key in measures.keys():
                    values[key] = (np.min(measures[key]), np.max(measures[key]))
            else:
                raise InvalidParameterValueException("value", value, ["min", "max", "both"])

        else:
            if value == "min":
                values = np.min(measures)
            elif value == "max":
                values = np.max(measures)
            elif value == "both":
                values = (np.min(measures), np.max(measures))
            else:
                raise InvalidParameterValueException("value", value, ["min", "max", "both"])

        if per_joint:
            return values
        else:
            if value == "min":
                if type(values) is dict:
                    return np.min(list(values.values()))
                else:
                    return np.min(values)

            elif value == "max":
                if type(values) is dict:
                    return np.max(list(values.values()))
                else:
                    return np.max(values)

            elif value == "both":
                if type(values) is dict:
                    return np.min(list(values.values())), np.max(list(values.values()))
                else:
                    return np.min(values), np.max(values)

    def get_sum_measure(self, measure, joint_label=None, per_joint=True, timestamp_start=None, timestamp_end=None,
                        window_length=7, poly_order=None, absolute=False, verbosity=1):
        """Returns the sum of the values of the measure for one or multiple joints from the Sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        measure: str|int
            The measure to return for each of the joints. This parameter can take multiple values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"`, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"`, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"`, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.
            • For any derivative of a higher order, set the corresponding integer.

        joint_label: str|list(str)|None, optional
            The joint labels or joint labels you want to return the measures from. If set on ``None`` (default),
            a dictionary containing all the joints as keys will be returned. If set on a string, an array matching
            the requested measure for the specified joint label will be returned. Finally, if set on a list of joint
            labels, a dictionary containing the specified subset of joint labels will be returned.

        per_joint: bool, optional
            If set on `True` (default), returns the value for each joint in a dictionary (or directly if only one
            joint is specified). If set on `False`, the sum across all provided joints will be returned.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
            This parameter is inclusive: if a timestamp is equal to this value, the corresponding pose will be included.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.
            This parameter is inclusive: if a timestamp is equal to this value, the corresponding pose will be included.

        window_length: int, optional
            The length of the window for the Savitzky–Golay filter when calculating a derivative (default: 7). See
            `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
            for more info.

        poly_order: int|None, optional
            The order of the polynomial for the Savitzky–Golay filter. If set on `None`, the polynomial will be set to
            one over the derivative rank. See
            `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_
            for more info.

        absolute: bool, optional
            If set on ``True``, the returned values will be absolute. By default, the parameter is set on ``False``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        dict(str: float)|float
            A dictionary with joint labels as keys, and the sum of the measure for each joint label as values; if
            only one joint_label has been provided, or if the sum of all the joints have been requested, the returned
            value will be a single sum value.

        Examples
        --------
        >>> sequence = Sequence("Michael/sequence_38.json")
        >>> sequence.get_sum_measure("x", "Head")
        19.65475
        >>> sequence.get_sum_measure("distance")
        {"Head": 586.36524, "HandRight": 10.00001}
        >>> sequence.get_sum_measure("distance", per_joint=False)
        596.36525
        """
        measures = self.get_measure(measure, joint_label, timestamp_start, timestamp_end, window_length, poly_order,
                                    absolute, verbosity)

        if type(measures) is dict:
            values = {}
            for key in measures.keys():
                values[key] = np.sum(measures[key])

        else:
            values = np.sum(measures)

        if per_joint:
            return values
        else:
            if type(values) is dict:
                return np.sum(list(values.values()))
            else:
                return np.sum(values)

    # === Correction functions ===
    def correct_jitter(self, velocity_threshold, window, window_unit="poses", method="default", correct_twitches=True,
                       correct_jumps=True, name=None, verbosity=1):
        """Detects and corrects rapid twitches and jumps in a motion sequence. These rapid movements, typically due to
        poor automatic detection of a joint in space, result in aberrant, unrealistic displacements from the joints.
        Though originally developed to handle Kinect data, the algorithm can be used for any 3D-tracked biological
        movement data having timestamps and X, Y and Z coordinates for each pose. The ``velocity_threshold``
        parameter defines the threshold of velocity, in meters per second, over which a movement is considered as
        aberrant; the ``window parameter``, defined in individual poses or in milliseconds (via the parameter
        ``window_unit``), defines the maximum duration of an aberrant movement – if the duration exceeds the
        window, the joint is corrected and smoothed out for all the poses of the window, using the defined
        ``method`` (linear by default).

        .. versionadded:: 2.0

        Parameters
        ----------
        velocity_threshold: float
            The threshold of velocity over which a movement is considered as abnormal, hence to correct. It is defined
            in meters per second. A good threshold must correct jumps and twitches without correcting valid, biological
            movement (e.g. between 0.1 and 1 m/s).

        window: float or int
            The amount of poses (by default) or time allowed for a joint to come back below threshold. If the parameter
            ``window_unit`` is set on poses, the window should be adjusted depending on the framerate of the
            recording. A window of 3 to 5 poses for a Kinect recording between 10 and 15 poses per second has been
            shown to give good results.

        window_unit: str, optional
            The unit for the parameter window.

                • If set on ``"pose"``, the parameter ``window`` will be interpreted as a number of poses.
                  Recommended for recordings with variable framerate.
                • If set on ``"s"`` or ``"ms"``, the parameter ``window`` will be interpreted as being an amount of
                  seconds or milliseconds, respectively. The algorithm will then, on every iteration, calculate the
                  amount of poses that has a duration the closes to the provided window value.

        method: str, optional
            The method as to how smoothen out the data of the joints detected has being part of a twitch or a jump.

                • If set on ``"default"``, the movement is corrected linearly by taking as reference the last pose
                  before the aberrant movement, and the first pose below threshold (in case of a twitch) or the last
                  pose of the window (in case of a jump).
                • This parameter also allows for all the values accepted for the ``kind`` parameter in the function
                  :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
                  ``"slinear"``, ``"quadratic"``, ``"cubic"``, ``"previous"``, and ``"next"``. See the `documentation
                  for this Python module
                  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.
                  In case one of these values is used, all the corrected joints are first set to (0, 0, 0) by the
                  function, before calling the :meth:`Sequence.correct_zeros()` function to interpolate the missing
                  values.

        correct_twitches: bool, optional
            If set on `True` (default), corrects the abnormal movements where the joints come back below threshold
            within the specified window. If set on `False`, the jitter correction will not correct the twitches.

        correct_jumps: bool, optional
            If set on `True` (default), corrects the abnormal movements where the joints do not come back below
            threshold within the specified window. If set on `False`, the jitter correction will not correct the jumps.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+CJ"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            A new sequence having the same amount of poses and timestamps as the original, but with corrected joints
            coordinates.

        Example
        -------
        >>> sequence = Sequence("Walt/sequence_39.xlsx")
        >>> sequence_cj = sequence.correct_jitter(1, 5)
        """

        dict_joints_to_correct = {}
        for key in self.joint_labels:
            dict_joints_to_correct[key] = []

        if verbosity > 0:
            print("Correcting jitter...", end=" ")

        # Create an empty sequence, the same length in poses as the original, just keeping the timestamp information
        # for each pose.
        new_sequence = self._create_new_sequence_with_timestamps(verbosity, add_tabs=1)

        # Defining the name
        if name is None:
            new_sequence.name = self.name + " +CJ"
        else:
            new_sequence.name = name

        if verbosity > 0:
            print("\tDetecting jitter...", end=" ")

        # If the window unit is defined in ms, we convert it to s
        if window_unit != "poses":
            window = convert_timestamp_to_seconds(window, window_unit)
            window_unit = "s"

        # Define the counters
        realigned_points = 0
        jumps = 0
        twitches = 0
        perc = 10

        # We keep the joint positions for the first pose
        new_sequence.poses[0] = self.poses[0].copy()

        # For every pose starting on the second one
        for p in range(1, len(self.poses)):

            if verbosity > 1:
                print(f"\n\t\tPose number {p + 1}")
                print(f"\t\t{'-' * len(f'Pose number {p + 1}')}")

            perc = show_progression(verbosity, p, len(self.poses), perc)

            # If the window unit is defined in seconds, we calculate how many poses that is.
            if window_unit == "s":
                if verbosity > 1:
                    print("\t\t\tCalculating number of poses in the window...", end=" ")

                window_effective = 0
                time_diff = 0
                previous_time_diff = 0

                # Get window length in poses
                for i in range(p, len(self.poses)):
                    window_effective = i - p
                    time_diff = self.get_time_between_poses(p, i)
                    if time_diff >= window:
                        break
                    previous_time_diff = time_diff

                # We get the closest window from the target
                if p + window_effective != len(self.poses) - 1:
                    if abs(window - previous_time_diff) < abs(window - time_diff):
                        window_effective -= 1

                if verbosity > 1:
                    print(f"Window size: {window_effective} ({time_diff} s).")

            else:
                window_effective = window

            # For every joint
            for joint_label in self.poses[0].joints.keys():

                # We get the m/s travelled by the joint between this pose and the previous
                if new_sequence.poses[p].joints[joint_label] is not None:
                    dist_before = calculate_distance(new_sequence.poses[p - 1].joints[joint_label],
                                                     new_sequence.poses[p].joints[joint_label])
                else:
                    dist_before = calculate_distance(new_sequence.poses[p - 1].joints[joint_label],
                                                     self.poses[p].joints[joint_label])
                delay_before = calculate_delay(self.poses[p - 1], self.poses[p])
                velocity_before = dist_before/delay_before

                if verbosity > 1:
                    print(f"\t\t{joint_label}: {velocity_before}")

                # If we already corrected this joint, we ignore it to avoid overcorrection
                if new_sequence.poses[p].joints[joint_label] is not None:

                    if verbosity > 1:
                        print("\t\t\tAlready corrected.")

                # If the velocity is over threshold, we check if it is a jump or a twitch
                elif velocity_before > velocity_threshold and p != len(self.poses) - 1:

                    if verbosity > 1:
                        print(f"\t\t\tVelocity over threshold between poses {p} and {p + 1}.", end=" ")

                    self.poses[p].joints[joint_label]._velocity_over_threshold = True

                    if window_effective < 2:
                        if verbosity > 1:
                            print("Window size inferior to 2, copying joint...")
                        new_sequence, realigned_points = \
                            self._correct_jitter_window(new_sequence, p - 1, p, joint_label, realigned_points,
                                                        verbosity)

                    else:
                        if verbosity > 1:
                            print("Checking in subsequent poses...")

                        # We check the next poses (defined by the window) if the position of the joint comes back below
                        # threshold
                        for k in range(p + 1, min(p + window_effective, len(self.poses))):

                            if verbosity > 1:
                                print("\t\t\t\tPose " + str(k + 1) + ":", end=" ")

                            dist = calculate_distance(new_sequence.poses[p - 1].joints[joint_label],
                                                      self.poses[k].joints[joint_label])
                            delay = calculate_delay(new_sequence.poses[p - 1], new_sequence.poses[p])
                            velocity = dist / delay

                            # Twitch case: One of the poses of the window is below threshold compared to previous pose.
                            if velocity < velocity_threshold:

                                if verbosity > 1:
                                    print(f"velocity ({velocity}) back under threshold defined by pose {p}.")

                                if correct_twitches:
                                    if verbosity > 1:
                                        print("\t\t\t\t\tCorrecting for twitch...")

                                    new_sequence, realigned_points = \
                                        self._correct_jitter_window(new_sequence, p - 1, k, joint_label,
                                                                    realigned_points, verbosity)

                                    if method != "default":
                                        for i in range(p, k):
                                            dict_joints_to_correct[joint_label].append(i)

                                    twitches += 1

                                    break

                                else:
                                    if verbosity > 1:
                                        print("\t\t\t\t\tNot correcting for the twitch as the parameter "
                                              "correct_twitches is set on False.")

                            # Jump case: No pose of the window is below threshold.
                            if k == p + window_effective - 1 or k == len(self.poses) - 1:

                                if verbosity > 1:
                                    print(f"velocity ({velocity}) still over threshold at the end of the window.")

                                if correct_jumps:

                                    if verbosity > 1:
                                        print("\t\t\t\t\tCorrecting for jump...")

                                    new_sequence, realigned_points = \
                                        self._correct_jitter_window(new_sequence, p - 1, k, joint_label,
                                                                    realigned_points, verbosity)

                                    if method not in ["old", "default"]:
                                        for i in range(p, k):
                                            dict_joints_to_correct[joint_label].append(i)

                                    jumps += 1

                                    break

                                else:
                                    if verbosity > 1:
                                        print("\t\t\t\t\tNot correcting for the jump as the parameter correct_jumps" +
                                              "is set on False.")

                            # Wait: if there are still poses in the window, we continue.
                            else:

                                if verbosity > 1:
                                    print("still over threshold.")

                    if verbosity > 1:
                        print("")

                # If we're still in threshold, there is no correction, we copy the joint
                else:

                    joint = self.poses[p].joints[joint_label].copy()
                    new_sequence.poses[p].add_joint(joint, replace_if_exists=True)
                    new_sequence.poses[p].joints[joint_label]._dejittered = False

        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

        if verbosity == 1:
            print("100% - Done.")
        elif verbosity > 1:
            print("\n\t100% - Done.")

        # If we use one of the interpolation methods, we call the correct_zeros function
        if method != "default":

            if verbosity > 0:
                print("\t" + str(realigned_points) + " point(s) with twitches and jumps detected.")
                print("\tSetting faulty joints to (None, None, None)...", end=" ")

            for joint_label in dict_joints_to_correct:
                for p in dict_joints_to_correct[joint_label]:
                    new_sequence.poses[p].joints[joint_label].set_to_none()

            if verbosity > 0:
                print("100% - Done.")
                print("\tInterpolation of the data of the joints set to (None, None, None)...")

            new_sequence = new_sequence.interpolate_missing_data(method=method, which=None, name=new_sequence.name,
                                                                 verbosity=verbosity, add_tabs=2)

        if verbosity > 0:
            percentage = round((realigned_points / (len(self.poses) * len(list(self.poses[0].joints.keys())))) * 100, 1)
            print("De-jittering over. " + str(realigned_points) + " point(s) corrected over " + str(
                len(self.poses) * len(list(self.poses[0].joints.keys()))) + " (" + str(percentage) + "%).")
            print(str(jumps) + " jump(s) and " + str(twitches) + " twitch(es) corrected.\n")

        new_sequence._set_attributes_from_other_sequence(self)
        new_sequence.metadata["processing_steps"].append({"processing_type": "correct_jitter",
                                                          "velocity_threshold": velocity_threshold,
                                                          "window": window,
                                                          "window_unit": window_unit,
                                                          "method": method,
                                                          "correct_twitches": correct_twitches,
                                                          "correct_jumps": correct_jumps})

        return new_sequence

    def _correct_jitter_window(self, new_sequence, start_pose_index, end_pose_index, joint_label,
                               number_of_realigned_points, verbosity=1):
        """Corrects linearly the jumps and twitches of the positions of a joint, between two given time points. This
        is a sub-function of :meth:`Sequence.correct_jitter`.

        For a given ``joint_label``, and two time points ``start_pose_number`` and ``end_pose_number`` between which a
        movement has been detected as being over threshold by the function :meth:`Sequence.correct_jitter()`, this
        function corrects the position of the joint between the two time points, by calling the function
        :meth:`Sequence._correct_jitter_single_joint()` for each individual time point. This function does not perform
        the correction if the size of the window is of size 0 or 1.

        .. versionadded:: 2.0

        Parameters
        ----------
        new_sequence: Sequence
            Corrected sequence that is used by and will be returned by :meth:`Sequence.correct_jitter()`.
        start_pose_index: int
            Last pose index before the jump or twitch.
        end_pose_index: int
            First pose index after the jump or twitch.
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        number_of_realigned_points: int
            The number of time points corrected since the beginning of the execution of
            :meth:`Sequence.correct_jitter()`.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            Sequence provided in input with corrected window.
        int
            Number of time points corrected, provided in input, incremented by the number of corrections performed.
        """
        t = "\t" * 6

        # We extract the data from the joints at the beginning and at the end of the partial sequence to correct
        joint_before = new_sequence.poses[start_pose_index].joints[joint_label]
        joint_after = self.poses[end_pose_index].joints[joint_label]

        # If the starting and ending joint are the same, we don't correct, it means it is the last pose of the sequence
        if start_pose_index == end_pose_index:
            joint = self.poses[start_pose_index].joints[joint_label].copy()
            new_sequence.poses[start_pose_index + 1].add_joint(joint, replace_if_exists=True)

            if verbosity > 1:
                print(f"{t}Did not correct joint {start_pose_index + 1} as the window is of size 0 or the joint is " +
                      f"the last pose of the sequence.")

        elif start_pose_index == end_pose_index - 1:
            joint = self.poses[start_pose_index].joints[joint_label].copy()
            new_sequence.poses[start_pose_index + 1].add_joint(joint, replace_if_exists=True)

            if verbosity > 1:
                print(f"{t}Did not correct joint {start_pose_index + 1} as the window is of size 1.")

        # Otherwise we correct for all the intermediate joints
        for pose_number in range(start_pose_index + 1, end_pose_index):

            # If a joint was already corrected we don't correct it to avoid overcorrection
            if self.poses[pose_number].joints[joint_label]._dejittered:

                if verbosity > 1:
                    print(f"{t}Did not correct joint {pose_number + 1} as it was already corrected.")

            # Otherwise we correct it
            else:

                x, y, z = self._correct_jitter_single_joint(joint_before, joint_after, start_pose_index, pose_number,
                                                            end_pose_index, verbosity)

                # We copy the original joint, apply the new coordinates and add it to the new sequence
                joint = self.poses[pose_number].joints[joint_label].copy()
                joint.set_position(x, y, z)
                joint._dejittered = True
                new_sequence.poses[pose_number].add_joint(joint, replace_if_exists=True)

                if verbosity > 1:
                    print(f"{t}Correcting joint {joint_label} from pose {pose_number + 1}.")
                    print(f"{t}Previous joint (pose {start_pose_index + 1}): " +
                          f"{new_sequence.poses[start_pose_index].joints[joint_label].get_position()}.")
                    print(f"{t}Original coordinates (pose {pose_number + 1}): " +
                          f"{self.poses[pose_number].joints[joint_label].get_position()}.")
                    print(f"{t}Next joint: (pose {str(end_pose_index + 1)}): "
                          f"{self.poses[end_pose_index].joints[joint_label].get_position()}.")
                    print(f"{t}New coordinates of corrected joint (pose {pose_number + 1}): "
                          f"{joint.get_position()}.")

                # To count the number of joints that were realigned overall
                number_of_realigned_points += 1

        return new_sequence, number_of_realigned_points

    def _correct_jitter_single_joint(self, joint_before, joint_after, pose_index_before, pose_index_current,
                                     pose_index_after, verbosity=1):
        """Corrects linearly a Joint object following the algorithm in :meth:`Sequence.correct_jitter()`. Given a
        ``joint_before`` on pose ``pose_index_before`` (last pose before the jump or twitch) and ``joint_after`` on pose
        ``pose_index_after`` (first pose after the jump on twitch), this function calculates the percentage of time
        elapsed at ``pose_index_current`` and uses this percentage as a ratio to calculate and return the new position
        of the x, y and z coordinates.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_before: Joint
            Last joint before the detected jump or twitch.
        joint_after: Joint
            First joint after the detected jump or twitch.
        pose_index_before: int
            Pose index of ``joint_before``.
        pose_index_current: int
            Pose index of the joint being corrected.
        pose_index_after: int
            Pose index of ``joint_after``.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        int
            Corrected x coordinate.
        int
            Corrected y coordinate.
        int
            Corrected z coordinate.
        """

        # We calculate the percentage of time elapsed between the pose at the beginning of the partial sequence to
        # correct and the pose at the end
        percentage_time = (self.poses[pose_index_current].timestamp - self.poses[pose_index_before].timestamp) / (
                self.poses[pose_index_after].timestamp - self.poses[pose_index_before].timestamp)

        if verbosity > 1:
            print(f"\t\t\t\t\t\tPose {pose_index_current + 1} positioned at " +
                  f"{np.round(percentage_time * 100, 2)} % between poses {pose_index_before + 1} and " +
                  f"{pose_index_after + 1}.")

        # We correct linearly every joint. See the documentation for precisions.
        x = joint_before.x - percentage_time * (joint_before.x - joint_after.x)
        y = joint_before.y - percentage_time * (joint_before.y - joint_after.y)
        z = joint_before.z - percentage_time * (joint_before.z - joint_after.z)

        return x, y, z

    def re_reference(self, reference_joint_label="auto", place_at_zero=True, name=None, verbosity=1):
        """Changes the position of all the joints of a sequence to be relative to the position of a reference joint,
        across all poses.

        .. versionadded:: 2.0

        Parameters
        ----------
        reference_joint_label: str, optional
            The label of the joint to take as reference. If set on ``"auto"``, the function will try to detect the
            presence of ``"SpineMid"`` (Kinect data), or ``"Chest"`` (Qualisys data) and assign it as the reference
            joint.

        place_at_zero: boolean, optional
            If set on ``True``, the positions of the joint with the label ``reference_joint`` will be set at coordinate
            (0, 0, 0). If set on ``False``, the positions of the joint with the label reference_joint will be set at the
            position from the first pose of the sequence.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+RF"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            A new sequence having the same amount of poses and timestamps as the original, but with re-referenced
            coordinates.

        Example
        -------
        >>> sequence = Sequence("Sawyer/sequence_40.xlsx")
        >>> sequence_rf = sequence.re_reference("SpineMid", True)
        """

        if reference_joint_label == "auto":
            if "SpineMid" in self.joint_labels:
                reference_joint_label = "SpineMid"
            elif "Chest" in self.joint_labels:
                reference_joint_label = "Chest"
            else:
                raise Exception("Automatic reference joint finder failed. Please enter a valid joint label as a " +
                                "reference joint.")

        if verbosity > 0:
            print("Re-referencing to " + str(reference_joint_label) + "...")

        # Create an empty sequence, the same length in poses as the original, just keeping the timestamp information
        # for each pose.
        new_sequence = self._create_new_sequence_with_timestamps(verbosity)
        if name is None:
            new_sequence.name = self.name + " +RF"
        else:
            new_sequence.name = name

        # If verbosity, show all the information. Else, show only the progress in percentage.
        if verbosity > 0:
            print("\tPerforming re-referencing...", end=" ")

        # Get reference : position of the reference joint at time 0
        if place_at_zero:
            start_ref_x = 0
            start_ref_y = 0
            start_ref_z = 0
        else:
            start_ref_x = self.poses[0].joints[reference_joint_label].x
            start_ref_y = self.poses[0].joints[reference_joint_label].y
            start_ref_z = self.poses[0].joints[reference_joint_label].z

        # Define the percentage counter
        perc = 10

        # For every pose starting on the second one
        for p in range(len(self.poses)):

            if verbosity > 1:
                print("\n== POSE NUMBER " + str(p + 1) + " ==")

            perc = show_progression(verbosity, p, len(self.poses), perc)

            # Get movement from the reference point
            curr_ref_x = self.poses[p].joints[reference_joint_label].x
            curr_ref_y = self.poses[p].joints[reference_joint_label].y
            curr_ref_z = self.poses[p].joints[reference_joint_label].z

            # Compute the differences
            diff_ref_x = curr_ref_x - start_ref_x
            diff_ref_y = curr_ref_y - start_ref_y
            diff_ref_z = curr_ref_z - start_ref_z

            if verbosity > 1:
                print("Removing " + str(diff_ref_x) + " to every joint in x;")
                print("Removing " + str(diff_ref_y) + " to every joint in y;")
                print("Removing " + str(diff_ref_z) + " to every joint in z.")

            # For every joint
            for joint_label in self.poses[0].joints.keys():

                # Compute new joint position
                if joint_label == reference_joint_label:
                    new_x = 0
                    new_y = 0
                    new_z = 0
                else:
                    new_x = self.poses[p].joints[joint_label].x - diff_ref_x
                    new_y = self.poses[p].joints[joint_label].y - diff_ref_y
                    new_z = self.poses[p].joints[joint_label].z - diff_ref_z

                # Add to the sequence
                joint = self.poses[p].joints[joint_label].copy()
                joint.set_position(new_x, new_y, new_z)
                joint._rereferenced = True
                new_sequence.poses[p].add_joint(joint, replace_if_exists=True)

                if verbosity > 1:
                    print(joint_label + ": ")
                    print("X: " + str(self.poses[p].joints[joint_label].x) + " -> " + str(new_x))
                    print("Y: " + str(self.poses[p].joints[joint_label].y) + " -> " + str(new_y))
                    print("Z: " + str(self.poses[p].joints[joint_label].z) + " -> " + str(new_z))

        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

        if verbosity > 0:
            print("100% - Done.")
            print("Re-referencing over.\n")

        new_sequence._set_attributes_from_other_sequence(self)
        new_sequence.metadata["processing_steps"].append({"processing_type": "re_reference",
                                                          "reference_joint_label": reference_joint_label,
                                                          "place_at_zero": place_at_zero})
        return new_sequence

    def trim(self, start=None, end=None, use_relative_timestamps=False, name=None, error_if_out_of_bounds=False,
             verbosity=1, add_tabs=0):
        """Trims a sequence according to a starting timestamp (by default the beginning of the original sequence) and
        an ending timestamp (by default the end of the original sequence). Timestamps must be provided in seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        start: int or None, optional
            The timestamp after which the poses will be preserved (inclusive). If set on ``None``, or if set on a value
            lower than the first timestamp, the beginning of the sequence will be set as the timestamp of the
            first pose.

        end: int or None, optional
            The timestamp before which the poses will be preserved (inclusive). If set on ``None``, or if set on a value
            higher than the last timestamp, the end of the sequence will be set as the timestamp of the last pose.

        use_relative_timestamps: bool, optional
            Defines if the timestamps ``start`` and ``end`` refer to the original timestamps or the relative timestamps.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+TR"``.

        error_if_out_of_bounds: bool, optional
            Defines if to return an error if the timestamps are out of bounds. If set on ``True``, the function will
            raise an Exception if `start` is below 0, or if `end` is above the length of the audio.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.

        Returns
        -------
        Sequence
            A new sequence containing a subset of the poses of the original sequence.

        Example
        -------
        >>> sequence = Sequence("Hurley/sequence_41.tsv")  # Sequence with 100 poses at 10 Hz.
        >>> sequence_t = sequence.trim(0, 5)
        >>> sequence_t.get_number_of_poses()
        51  # Remember: the last pose is inclusive. If you wish not to include it, set the end to 4.999
        """

        tabs = add_tabs * "\t"

        if start is None:
            if use_relative_timestamps:
                start = 0
            else:
                start = self.poses[0].timestamp

        if end is None:
            if use_relative_timestamps:
                end = self.get_duration()
            else:
                end = self.poses[-1].timestamp

        if end < start:
            raise Exception("End timestamp should be inferior to beginning timestamp.")

        if error_if_out_of_bounds:
            if use_relative_timestamps:
                if not self.poses[0].get_relative_timestamp() <= start <= self.poses[-1].get_relative_timestamp():
                    raise Exception(f"The start timestamp should be between {self.poses[0].get_relative_timestamp()} " +
                                    f"and {self.poses[-1].get_relative_timestamp()}.")
                elif not self.poses[0].get_relative_timestamp() <= end <= self.poses[-1].get_relative_timestamp():
                    raise Exception(f"The end timestamp should be between {self.poses[0].get_relative_timestamp()} " +
                                    f"and {self.poses[-1].get_relative_timestamp()}.")
            else:
                if not self.poses[0].get_timestamp() <= start <= self.poses[-1].get_timestamp():
                    raise Exception(f"The start timestamp should be between {self.poses[0].get_timestamp()} " +
                                    f"and {self.poses[-1].get_timestamp()}.")
                elif not self.poses[0].get_timestamp() <= end <= self.poses[-1].get_timestamp():
                    raise Exception(f"The end timestamp should be between {self.poses[0].get_timestamp()} " +
                                    f"and {self.poses[-1].get_timestamp()}.")

        if verbosity > 0:
            print(tabs + "Trimming the sequence:")
            print(tabs + "\tStarting timestamp: " + str(start) + " seconds")
            print(tabs + "\tEnding timestamp: " + str(end) + " seconds")
            print(tabs + "\tOriginal duration: " + str(self.get_duration()) + " seconds")
            print(tabs + "\tDuration after trimming: " + str(end - start) + " seconds")
        if verbosity == 1:
            print(tabs + "Starting the trimming...", end=" ")

        # Create an empty sequence
        new_sequence = Sequence(None)
        if name is None:
            new_sequence.name = self.name + " +TR"
        else:
            new_sequence.name = name

        # Define the percentage counter
        perc = 10

        for p in range(len(self.poses)):

            if verbosity == 1:
                perc = show_progression(verbosity, p, len(self.poses), perc)

            if use_relative_timestamps:
                t = self.poses[p].relative_timestamp
            else:
                t = self.poses[p].timestamp

            if verbosity > 1:
                print(tabs + "\t\tPose " + str(p + 1) + " of " + str(len(self.poses)) + ": " + str(t), end=" ")

            if start <= t <= end:
                pose = self.poses[p].copy()
                new_sequence.poses.append(pose)
                if verbosity > 1:
                    print("Preserved.")
            elif verbosity > 1:
                print("Trimmed.")

        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

        if verbosity > 0:
            if verbosity == 1:
                print("100% - Done.")
            print(tabs + "\tNew sequence duration: " + str(new_sequence.get_duration()) + " s.")
            print(tabs + "\tOriginal number of poses: " + str(len(self.poses)), end=" · ")
            print("New number of poses: " + str(len(new_sequence.poses)))
            print(tabs + "Trimming over.\n")

        new_sequence._set_attributes_from_other_sequence(self)
        new_sequence.joint_labels = self.joint_labels
        new_sequence.metadata["processing_steps"].append({"processing_type": "trim",
                                                          "start": start,
                                                          "end": end,
                                                          "use_relative_timestamps": use_relative_timestamps})
        return new_sequence

    def trim_to_audio(self, delay=0, audio=None, name=None, error_if_out_of_bounds=False, verbosity=1):
        """Synchronizes the timestamps to the duration of an audio file.

        .. versionadded:: 2.0

        Parameters
        ----------
        delay: float, optional
            The relative timestamp after which the poses will be preserved. If set on 0, the first pose will be included
            in the returned subsequence.

        audio: str or Audio or None, optional
            An instance of the Audio class, a string containing the path of the audio file, or ``None``. In the case of
            a string, the function will internally create an instance of the Audio class. In the case where the value
            is set on ``None``, the function will check for a path to the audio file in the :attr:`path_audio`
            attribute (created upon initialization or via the :meth:`Sequence.set_path_audio` method). If this
            attribute is also ``None``, the function will raise an error.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+TR"``.

        error_if_out_of_bounds: bool, optional
            Defines if to return an error if the timestamps are out of bounds. If set on ``True``, the function will
            raise an Exception if `start` is below 0, or if `end` is above the length of the audio.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            A new sequence containing a subset of the poses of the original sequence.

        Note
        ----
        This function is a wrapper for :meth:`Sequence.trim`, with ``delay`` set as ``start``, and the duration of
        ``audio`` + ``delay`` set as ``end``.

        Important
        ---------
        The function will trim the Sequence to the pose that has the closest time above the one provided for the
        parameter ``delay``. This means that the difference between the delay entered and the actual timestamp might be
        significant. This difference will be printed if verbosity is set to 1 or more.

        Example
        -------
        >>> sequence = Sequence("Jin/sequence_42.tsv")  # Sequence with 100 poses at 10 Hz.
        >>> audio = Audio("Jin/audio_42.wav")  # Audio duration of 5 s.
        >>> sequence_ta = sequence.trim(2, audio)
        >>> sequence_ta.get_number_of_poses()
        51
        """

        if audio is None:
            if self.path_audio is None:
                raise Exception("No audio path defined in the sequence, please specify one.")
            audio = Audio(self.path_audio, name=self.path_audio)

        if type(audio) is str:
            audio = Audio(audio, name=audio)

        audio_duration = audio.get_duration()

        if verbosity > 0:
            print("Trimming the sequence according to the duration of an audio file...")
            print("\tParameters:")
            print("\t\tSequence duration: " + str(self.get_duration()) + " s.")
            print("\t\tAudio duration: " + str(audio_duration) + " s.")

        if delay < 0:
            raise InvalidParameterValueException("delay", delay, "any integer >= 0.")

        if audio_duration > self.get_duration():
            print("\n\tSequence duration: " + str(self.get_duration()))
            print("\tAudio duration: " + str(audio_duration))
            raise Exception("Error: The duration of the audio exceeds the duration of the sequence.")
        elif audio_duration + delay > self.get_duration():
            raise Exception("Error: The duration of the audio plus the delay exceeds the duration of the sequence.")
        elif verbosity > 0:
            print("\t\tMoving the beginning by a delay of " + str(delay) + " s.")
            print("\t\tIgnoring " + str(round(self.get_duration() - audio_duration - delay, 2)) +
                  " s at the end of the sequence.")

        new_sequence = self.trim(delay, audio_duration + delay, True, name, error_if_out_of_bounds,
                                 verbosity)

        if abs(audio_duration - new_sequence.get_duration()) > 1:
            raise Exception("The duration of the audio is different of more than one second with the duration of the " +
                            "new sequence.")

        if verbosity > 0:
            print(f"\tDelay requested: {delay} · " +
                  f"First timestamp of the trimmed sequence: {new_sequence.poses[0].timestamp} · " +
                  f"Losing precision of {round(new_sequence.poses[0].timestamp - delay, 2)} s.\n")

        return new_sequence

    # noinspection PyTupleAssignmentBalance
    def filter_frequencies(self, filter_below=None, filter_over=None, name=None, verbosity=1):
        """Applies a low-pass, high-pass or band-pass filter to the positions of the joints.

        .. versionadded: 2.0

        Parameters
        ----------
        filter_below: float or None, optional
            The value below which you want to filter the data. If set on None or 0, this parameter will be ignored.
            If this parameter is the only one provided, a high-pass filter will be applied to the data; if
            ``filter_over`` is also provided, a band-pass filter will be applied to the data.

        filter_over: float or None, optional
            The value over which you want to filter the data. If set on None or 0, this parameter will be ignored.
            If this parameter is the only one provided, a low-pass filter will be applied to the data; if
            ``filter_below`` is also provided, a band-pass filter will be applied to the data.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the
            original sequence, with the suffix ``"+FF"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            The Sequence instance, with filtered values.

        Raises
        ------
        ValueError
            If filter_below is below 0, or filter_above is superior or equal to the frequency of the Sequence divided
            by two.

        VariableSamplingRateException
            If the sampling rate of the Sequence is not fixed.

        Example
        -------
        >>> sequence = Sequence("Sun/sequence_43.tsv")  # Sequence with 100 poses at 10 Hz.
        >>> audio = Audio("Sun/audio_43.wav")
        >>> sequence_ta = sequence.trim(2, audio)
        >>> sequence_ta.get_number_of_poses()
        """

        new_sequence = self._create_new_sequence_with_timestamps(verbosity)

        if verbosity > 0:
            if filter_below not in [None, 0] and filter_over not in [None, 0]:
                print(f"Applying a band-pass filter for frequencies between {filter_below} and {filter_over} Hz...",
                      end=" ")
            elif filter_below not in [None, 0]:
                print(f"Applying a high-pass filter for frequencies over {filter_below} Hz...", end=" ")
            elif filter_over not in [None, 0]:
                print(f"Applying a low-pass filter for frequencies below {filter_over} Hz...", end=" ")

        for joint_label in self.joint_labels:

            if verbosity > 1:
                print(f"\t{joint_label}")

            x_positions = self.get_measure("x", joint_label)
            y_positions = self.get_measure("y", joint_label)
            z_positions = self.get_measure("z", joint_label)

            a, b = None, None
            # Band-pass filter
            if filter_below not in [None, 0] and filter_over not in [None, 0]:
                b, a = butter(2, [filter_below, filter_over], "band", fs=self.get_sampling_rate())

            # High-pass filter
            elif filter_below not in [None, 0]:
                b, a = butter(2, filter_below, "high", fs=self.get_sampling_rate())

            # Low-pass filter
            elif filter_over not in [None, 0]:
                b, a = butter(2, filter_over, "low", fs=self.get_sampling_rate())

            if a is None and b is None:
                filtered_x_positions = x_positions
                filtered_y_positions = y_positions
                filtered_z_positions = z_positions

            else:
                filtered_x_positions = lfilter(b, a, x_positions)
                filtered_y_positions = lfilter(b, a, y_positions)
                filtered_z_positions = lfilter(b, a, z_positions)

            for p in range(len(new_sequence.poses)):
                new_sequence.poses[p].joints[joint_label] = Joint(joint_label, filtered_x_positions[p],
                                                                  filtered_y_positions[p], filtered_z_positions[p])

        if verbosity > 0:
            print("Done.")

        if name is None:
            name = self.name + " +FF"

        new_sequence.set_name(name)
        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose
        new_sequence._set_attributes_from_other_sequence(self)

        new_sequence.metadata["processing_steps"].append({"processing_type": "filter_frequencies",
                                                         "filter_below": filter_below, "filter_over": filter_over})
        return new_sequence

    def resample(self, frequency, method="cubic", window_size=1e7, overlap_ratio=0.5, name=None, verbosity=1):
        """Resamples a sequence with a constant or variable framerate to the `frequency` parameter. It first creates
        a new set of timestamps at the desired frequency, and then interpolates the original data to the new timestamps.

        .. versionadded:: 2.0

        Parameters
        ----------
        frequency: float
            The frequency, in hertz, at which you want to resample the sequence. A frequency of 4 will return resample
            joints at 0.25 s intervals.

        method: str, optional
            This parameter also allows for all the values accepted for the ``kind`` parameter in the function
            :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
            ``"slinear"``, ``"quadratic"``, ``"cubic"``, ``"previous"``, and ``"next"``. See the `documentation
            for this Python module
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.

        window_size: int, optional
            The size of the windows in which to cut the points to perform the resampling. Cutting long arrays
            in windows allows to speed up the computation. If this parameter is set on `None`, the window size will be
            set on the number of samples. A good value for this parameter is generally 10 million (1e7). If this
            parameter is set on 0, on None or on a number of samples bigger than the amount of samples in the Sequence
            instance, the window size is set on the length of the samples.

        overlap_ratio: float, optional
            The ratio of points overlapping between each window. If this parameter is not `None`, each window will
            overlap with the previous (and, logically, the next) for an amount of samples equal to the number of samples
            in a window times the overlap ratio. Then, only the central values of each window will be preserved and
            concatenated; this allows to discard any "edge" effect due to the windowing. If the parameter is set on
            `None` or 0, the windows will not overlap. By default, this parameter is set on 0.5, meaning that each
            window will overlap for half of their values with the previous, and half of their values with the next.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+RS"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            A new sequence containing resampled timestamps and joints coordinates.

        Warning
        -------
        This function allows both the **upsampling** and the **downsampling** of sequences, along with stabilizing a
        recording to a constant framerate. However, during any of these operations, the algorithm only **estimates**
        the real coordinates of the joints. You should then consider the upsampling (and the downsampling, to a
        lesser extent) with care.
        You can control the frequency of your original sequence with :meth:`Sequence.get_average_frequency()`,
        :meth:`Sequence.get_min_frequency()` and :meth:`Sequence.get_max_frequency()`.

        Example
        -------
        >>> sequence = Sequence("Ben/sequence_44.tsv")  # Sequence with 100 poses at 10 Hz.
        >>> sequence_rs = sequence.resample(5)
        >>> sequence_rs.get_number_of_poses()
        50
        """

        if verbosity > 0:
            print("Resampling the sequence at " + str(frequency) + " Hz (method: " + str(method) + ")...")
            print("\tOriginal framerate: ")
            sampling_rates = self.get_sampling_rates()
            print("\t\tAverage: " + str(round(np.mean(self.get_sampling_rates()), 2)), end=" · ")
            print("Min: " + str(round(np.min(self.get_sampling_rates()), 2)), end=" · ")
            print("Max: " + str(round(np.max(self.get_sampling_rates()), 2)))
            print("\tCreating vectors...", end=" ")

        # Create an empty sequence
        new_sequence = Sequence(None)
        if name is None:
            new_sequence.name = self.name + " +RS" + str(frequency)
        else:
            new_sequence.name = name

        # Define the percentage counter
        perc = 10

        # Define positions lists
        x_points = OrderedDict()
        y_points = OrderedDict()
        z_points = OrderedDict()
        time_points = self.get_timestamps(relative=True)

        # Turn timestamps into microsecond accuracy
        time_points = np.round(np.array(time_points), 6)
        number_of_poses = len(self.poses)

        # Create vectors of position and time
        for p in range(number_of_poses):

            perc = show_progression(verbosity, p, len(self.poses), perc)

            for joint_label in self.poses[p].joints.keys():
                if p == 0:
                    x_points[joint_label] = np.zeros(number_of_poses)
                    y_points[joint_label] = np.zeros(number_of_poses)
                    z_points[joint_label] = np.zeros(number_of_poses)
                x_points[joint_label][p] = self.poses[p].joints[joint_label].x
                y_points[joint_label][p] = self.poses[p].joints[joint_label].y
                z_points[joint_label][p] = self.poses[p].joints[joint_label].z

        if verbosity > 0:
            print("100% - Done.")

        if verbosity == 1:
            print("\tPerforming the resampling...", end=" ")
        if verbosity > 1:
            print("\tPerforming the resampling...")

        # Define the percentage counter
        perc = 10

        # Resample
        new_x_points = OrderedDict()
        new_y_points = OrderedDict()
        new_z_points = OrderedDict()
        new_time_points = []

        no_joints = len(x_points.keys())
        i = 0

        if window_size == 0 or window_size is None:
            window_size = len(self.poses)

        for joint_label in x_points.keys():
            if verbosity > 1:
                print("\n\tJoint label: " + str(joint_label))
            perc = show_progression(verbosity, i, no_joints, perc)
            new_x_points[joint_label], new_time_points = resample_data(x_points[joint_label], time_points, frequency,
                                                                       window_size, overlap_ratio, method=method,
                                                                       time_unit=self.time_unit, verbosity=verbosity)
            new_y_points[joint_label], new_time_points = resample_data(y_points[joint_label], time_points, frequency,
                                                                       window_size, overlap_ratio, method=method,
                                                                       time_unit=self.time_unit, verbosity=verbosity)
            new_z_points[joint_label], new_time_points = resample_data(z_points[joint_label], time_points, frequency,
                                                                       window_size, overlap_ratio, method=method,
                                                                       time_unit=self.time_unit, verbosity=verbosity)
            i += 1

        # Define the percentage counter
        if verbosity > 0:
            print("100% - Done.")
            print("\tSaving the new sequence...", end=" ")
        perc = 10

        # Save data
        for p in range(len(new_time_points)):
            perc = show_progression(verbosity, i, no_joints, perc)
            pose = Pose(new_time_points[p])
            for joint_label in new_x_points.keys():
                x = new_x_points[joint_label][p]
                y = new_y_points[joint_label][p]
                z = new_z_points[joint_label][p]
                j = Joint(joint_label, x, y, z)
                j.joint_label = joint_label
                pose.add_joint(j)
            new_sequence.poses.append(pose)

        if verbosity > 0:
            print("100% - Done.")
            print("\tOriginal sequence had " + str(len(self.poses)) + " poses.")
            print("\tNew sequence has " + str(len(new_sequence.poses)) + " poses.\n")

        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose
        new_sequence._set_attributes_from_other_sequence(self)
        new_sequence.joint_labels = self.joint_labels

        new_sequence.metadata["processing_steps"].append({"processing_type": "resample",
                                                          "frequency": frequency,
                                                          "method": method,
                                                          "window_size": window_size,
                                                          "overlap_ratio": overlap_ratio})
        return new_sequence

    def interpolate_missing_data(self, method="cubic", which="both", name=None, min_duration_warning=0.1, verbosity=1,
                                 add_tabs=0):
        """Detects the joints set at (0, 0, 0) and/or (None, None, None), considers them as missing, and correct their
        coordinates by interpolating the data from the neighbouring temporal points. Typically, this function is used
        to correct the zeros set by the Qualisys system when a specific joint is not tracked. In the case where an edge
        pose (first or last pose of the sequence) has missing coordinates, the closest non-zero coordinate is assigned
        to the pose. The missing coordinates are then considered as missing and are new values are interpolated using
        `tool_functions.interpolate_data()`.

        .. versionadded:: 2.0

        Parameters
        ----------
        method: str, optional
            This parameter also allows for all the values accepted for the ``kind`` parameter in the function
            :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
            ``"slinear"``, ``"quadratic"``, ``"cubic"``, ``"previous"``, and ``"next"``. See the `documentation
            for this Python module
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.

        which: str|int|None, optional
            Whether to correct for zeros (``"zero"``, ``"zeros"``, ``0``, ``(0, 0, 0)``), for None (``None``,
            ``"none"``, ``(None, None, None)``) or both (default, ``"both"``).

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+IM"``.

        min_duration_warning: float, optional
            Defines the time over which an uninterrupted series of (0, 0, 0) coordinates will trigger a warning if
            the parameter `verbosity` is 1 or more.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.

        Returns
        -------
        Sequence
            A new sequence having the same amount of poses and timestamps as the original, but with re-referenced
            coordinates.

        Warning
        -------
        Please note that for long series of 0 coordinates, the interpolation of the data may not be accurate. When
        running this function with a verbosity of 1 or more, the longest duration of a 0 coordinate will be displayed.

        Example
        -------
        >>> sequence = Sequence("Juliet/sequence_45.tsv")
        >>> sequence_im = sequence.resample("linear", "both")
        """

        to_correct = []

        if which in ["zero", "zeros", "Zero", "Zeros", 0, (0, 0, 0)]:
            to_correct = [0]
        elif which in ["none", "None", None, (None, None, None)]:
            to_correct = [None]
        elif which in ["both", "Both"]:
            to_correct = [0, None]
        else:
            raise InvalidParameterValueException("which", which, ["zero", "none", "both"])

        t = add_tabs * "\t"

        if verbosity > 0:
            print(t + "Interpolating missing data (mode: " + str(method) + ")...")
            print(t + "\tCreating vectors and finding missing data...", end=" ")

        # Create an empty sequence
        new_sequence = Sequence(None, verbosity)
        if name is None:
            new_sequence.name = self.name + " +IM"
        else:
            new_sequence.name = name

        # Define the percentage counter
        perc = 10

        # Define positions lists
        x_points = OrderedDict()
        y_points = OrderedDict()
        z_points = OrderedDict()
        time_points = OrderedDict()
        zero_points_detected = 0
        total_joints = 0
        longest_zero = 0

        # Define the zero counter
        counter_zeros = {}
        last_index = {}
        for joint_label in self.poses[0].joints.keys():
            counter_zeros[joint_label] = 0
            last_index[joint_label] = None

        # Create vectors of position and time
        for p in range(len(self.poses)):

            perc = show_progression(verbosity, p, len(self.poses), perc)
            if verbosity > 1:
                if p == 0:
                    print("")
                print(t + "\t\tChecking pose " + str(p + 1) + " out of " + str(len(self.poses)))

            faulty_joints = []

            for joint_label in self.poses[p].joints.keys():

                # First iteration, we create the vectors for this joint
                if p == 0:
                    x_points[joint_label] = []
                    y_points[joint_label] = []
                    z_points[joint_label] = []
                    time_points[joint_label] = []

                # If coordinates are non-zero
                if (self.poses[p].joints[joint_label].x not in to_correct and
                        self.poses[p].joints[joint_label].y not in to_correct and
                        self.poses[p].joints[joint_label].z not in to_correct):

                    time_zeros = self.get_time_between_poses(p - counter_zeros[joint_label], p)
                    if time_zeros >= min_duration_warning:
                        if verbosity > 0:
                            print(t + "\t\t\tWarning: sequence of missing coordinates of " +
                                  str(round(time_zeros, 3)) + " s for the joint " + str(joint_label) + ".")
                    if time_zeros > longest_zero:
                        longest_zero = time_zeros
                    counter_zeros[joint_label] = 0

                    # If these are the first non-zero coordinates, we create a non-zero coordinate
                    if p != 0 and len(x_points[joint_label]) == 0:
                        if verbosity > 1:
                            print(t + "\t\t\tThis is the first pose for the joint " + str(joint_label) + " having " +
                                  "non-zero coordinates. Creating a pose at all the previous timestamps with these " +
                                  "coordinates.")
                        for q in range(p):
                            x_points[joint_label].append(self.poses[p].joints[joint_label].x)
                            y_points[joint_label].append(self.poses[p].joints[joint_label].y)
                            z_points[joint_label].append(self.poses[p].joints[joint_label].z)
                            time_points[joint_label].append(self.poses[q].timestamp)
                            last_index[joint_label] = q

                    # We add the coordinates and timestamps
                    x_points[joint_label].append(self.poses[p].joints[joint_label].x)
                    y_points[joint_label].append(self.poses[p].joints[joint_label].y)
                    z_points[joint_label].append(self.poses[p].joints[joint_label].z)
                    time_points[joint_label].append(self.poses[p].timestamp)
                    last_index[joint_label] = p

                # If coordinate is missing
                else:

                    counter_zeros[joint_label] += 1
                    self.poses[p].joints[joint_label]._interpolated = True

                    # If it's the last pose of the sequence
                    if p == len(self.poses) - 1:

                        time_zeros = self.get_time_between_poses(p - counter_zeros[joint_label], p)
                        if time_zeros >= min_duration_warning:
                            if verbosity > 0:
                                print(t + "\t\t\tWarning: sequence of missing coordinates of " +
                                      str(round(time_zeros, 3)) + " s for the joint " + str(joint_label) + ".")

                        # If the vector is still empty, we add a first coordinate
                        if len(x_points[joint_label]) == 0:
                            if verbosity > 1:
                                print(t + "\t\t\tAll the coordinates for the joint " + str(joint_label) + " were " +
                                      "missing. Creating a pose at timestamp 0 with (0, 0, 0) coordinates.")
                            x_points[joint_label][0] = self.poses[p].joints[joint_label].x
                            y_points[joint_label][0] = self.poses[p].joints[joint_label].y
                            z_points[joint_label][0] = self.poses[p].joints[joint_label].z
                            time_points[joint_label][0] = self.poses[0].timestamp
                            last_index[joint_label] = 0

                        # We copy the last coordinate we added to the vector as an ending point
                        if verbosity > 1:
                            print(
                                t + "\t\t\tThis is the last pose for the joint " + str(joint_label) + ", and it has " +
                                "missing coordinates. Copying the last pose having non-zero coordinates to put at " +
                                "all the following timestamps at the end of the series.")

                        s = len(x_points[joint_label]) - 1
                        for q in range(last_index[joint_label] + 1, p + 1):
                            x_points[joint_label].append(x_points[joint_label][s])
                            y_points[joint_label].append(y_points[joint_label][s])
                            z_points[joint_label].append(z_points[joint_label][s])
                            time_points[joint_label].append(self.poses[q].timestamp)

                    zero_points_detected += 1

                    if joint_label not in faulty_joints:
                        faulty_joints.append(joint_label)

                    # if len(time_points[joint_label]) > 1:
                    #     t_diff = time_points[joint_label][-1] - time_points[joint_label][-2]
                    #     if t_diff > longest_zero:
                    #         longest_zero = t_diff

                total_joints += 1

            if verbosity > 1:
                if len(faulty_joints) == 0:
                    print(t + "\t\t\tNo joints found with missing coordinates.")
                else:
                    to_print = ""
                    if len(faulty_joints) == 1:
                        print(t + "\t\t\t 1 joint with missing coordinate detected: ", end="")
                    else:
                        print(t + "\t\t\t" + str(len(faulty_joints)) + " joints with missing coordinate detected: ",
                              end="")
                    for joint_label in faulty_joints:
                        to_print += joint_label + ", "
                    print(to_print[:-2])

        if verbosity == 1:
            print("100% - Done.")
        if verbosity > 0:
            print(t + "\t\t" + str(zero_points_detected) + " points with missing coordinates detected over " +
                  str(total_joints) + " (" + str(round(zero_points_detected / total_joints * 100, 2)) + "%).")
            print(t + f"\t\tLongest chain of missing data detected: {np.round(longest_zero, 2)} s. ")

        if zero_points_detected != 0:
            if verbosity > 0:
                print(t + "\tPerforming the correction...", end=" ")

            # Define the percentage counter
            perc = 10

            # Resample
            new_x_points = OrderedDict()
            new_y_points = OrderedDict()
            new_z_points = OrderedDict()
            new_time_points = []

            no_joints = len(x_points.keys())
            i = 0

            for joint_label in x_points.keys():
                perc = show_progression(verbosity, i, no_joints, perc)
                if verbosity > 1:
                    if i == 0:
                        print("")
                    print(t + "\t\tCorrecting the time series for the joint " + joint_label + "...", end=" ")

                    print("="*100)
                    print(x_points[joint_label])
                    print(time_points[joint_label])

                new_x_points[joint_label], new_time_points = interpolate_data(x_points[joint_label],
                                                                              time_points[joint_label],
                                                                              self.get_timestamps(relative=False),
                                                                              method)
                new_y_points[joint_label], new_time_points = interpolate_data(y_points[joint_label],
                                                                              time_points[joint_label],
                                                                              self.get_timestamps(relative=False),
                                                                              method)
                new_z_points[joint_label], new_time_points = interpolate_data(z_points[joint_label],
                                                                              time_points[joint_label],
                                                                              self.get_timestamps(relative=False),
                                                                              method)

                if verbosity > 1:
                    print("OK")
                i += 1

            # Define the percentage counter
            if verbosity == 1:
                print("100% - Done.")
            if verbosity > 0:
                print(t + "\tSaving the new sequence...", end=" ")
            perc = 10

            # Save data
            for p in range(len(new_time_points)):
                perc = show_progression(verbosity, i, no_joints, perc)
                if verbosity > 1:
                    if p == 0:
                        print("")
                    print(t + "\t\tCreating pose " + str(p + 1) + " out of " + str(len(self.poses)) + "... ", end="")
                pose = Pose(new_time_points[p])
                for joint_label in new_x_points.keys():
                    joint = self.poses[p].joints[joint_label].copy()
                    self.poses[p].joints[joint_label]._interpolated = False
                    joint.set_x(new_x_points[joint_label][p])
                    joint.set_y(new_y_points[joint_label][p])
                    joint.set_z(new_z_points[joint_label][p])
                    pose.add_joint(joint)
                new_sequence.poses.append(pose)
                if verbosity > 1:
                    print("OK")

            if verbosity == 1:
                print("100% - Done.")
            if verbosity > 1:
                print(t + "\tOriginal sequence had " + str(len(self.poses)) + " poses.")
                print(t + "\tNew sequence has " + str(len(new_sequence.poses)) + " poses.")
                print(t + "\t\t" + str(zero_points_detected) + " out of " + str(total_joints) + " joints have been " +
                      "corrected (" + str(round(zero_points_detected / total_joints * 100, 2)) + "%).")

            new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose
            new_sequence._set_attributes_from_other_sequence(self)
            new_sequence.joint_labels = self.joint_labels

            new_sequence.metadata["processing_steps"].append({"processing_type": "interpolate_missing_data",
                                                              "method": method, "which": which})

            return new_sequence

        else:
            if verbosity != 0:
                print(t + "No missing coordinate found, returning the original sequence.")
            return self

    def randomize(self, x_scale=0.2, y_scale=0.3, z_scale=0.5, name=None, verbosity=1):
        """Returns a sequence that randomizes the starting position of all the joints of the original sequence. The
        randomization follows a uniform distribution:

            •	x coordinate randomized between -0.2 and 0.2 (default)
            •	y coordinate randomized between -0.3 and 0.3 (default)
            •	z coordinate randomized between -0.5 and 0.5 (default)

        The randomization preserves the direction of movement, timestamps and all the other metrics of the sequence;
        the starting position only of the joints is randomized, and the coordinates of the joints of the subsequent
        poses are adapted using the new starting position as reference.

        .. versionadded:: 2.0

        Parameters
        ----------
        x_scale: float
            The absolute maximum value of the random uniform distribution on the x-axis.
        y_scale: float
            The absolute maximum value of the random uniform distribution on the y-axis.
        z_scale: float
            The absolute maximum value of the random uniform distribution on the z axis.
        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+RD"``.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            A new sequence having the same amount of poses and timestamps as the original, but with randomized starting
            coordinates. The attribute :attr:`randomized` of this new Sequence will be set on `True`.

        Example
        -------
        >>> sequence = Sequence("Desmond/sequence_46.tsv")
        >>> sequence_rd = sequence.randomize()
        """

        if verbosity > 0:
            print("Randomizing the starting points of the joints...")
            print("\tCreating a new sequence...", end=" ")

        new_sequence = Sequence(None)
        if name is None:
            new_sequence.name = self.name + " +RD"
        else:
            new_sequence.name = name

        for p in range(len(self.poses)):
            new_sequence.poses.append(self.poses[p].copy())

        if verbosity > 0:
            print("OK. \n\tRandomizing starting positions...", end=" ")

        # Get the starting positions of all joints
        starting_positions = []
        for joint_label in new_sequence.poses[0].joints.keys():
            starting_positions.append(new_sequence.poses[0].joints[joint_label].copy())

        # Randomize new starting positions for joints
        randomized_positions = generate_random_joints(len(new_sequence.poses[0].joints), x_scale, y_scale, z_scale)
        # random.shuffle(randomized_positions)

        if verbosity > 0:
            print("OK. \n\tMoving the joints...", end=" ")

        # Assign these new starting positions to the joints and moves the joints in every subsequent pose
        # in relation to the new starting positions
        joints_labels = list(new_sequence.poses[0].joints.keys())
        for p in new_sequence.poses:
            for j in range(len(joints_labels)):
                p.joints[joints_labels[j]] = p.joints[joints_labels[j]]._randomize_coordinates_keep_movement(
                                                                        starting_positions[j], randomized_positions[j])

        if verbosity > 0:
            print("OK.")

        new_sequence.is_randomized = True
        new_sequence._calculate_relative_timestamps()
        new_sequence._set_attributes_from_other_sequence(self)
        new_sequence.joint_labels = self.joint_labels
        new_sequence.metadata["processing_steps"].append({"processing_type": "randomize",
                                                          "x_scale": x_scale,
                                                          "y_scale": y_scale,
                                                          "z_scale": z_scale})
        return new_sequence

    # === Copy and blank sequence creation functions ===
    def _create_new_sequence_with_timestamps(self, verbosity=1, add_tabs=1):
        """Creates a sequence with the same number of poses as in the original, but only containing timestamps.
        This function is used by :meth:`Sequence.correct_jitter()` and :meth:`Sequence.re_reference()` to obtain
        placeholder poses. The sequence created has the same number of Pose objects as the original sequence in the
        :attr:`poses` attribute; however, for every Pose object, the attribute ``joints`` is an OrderedDict that has
        the joint labels as keys, but ``None`` as values, apart from the first pose, that preserves the coordinates for
        all the joints; the attributes ``pose_number`` and ``timestamp`` are preserved from the original sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.

        Returns
        -------
        Sequence
            A :class:`Sequence` instance that has the same number of Pose objects as the original sequence in the
            :attr:`poses` attribute; however, for every Pose object, the attribute ``joints`` is an OrderedDict that has
            the joint labels as keys, but ``None`` as values, apart from the first pose, that preserves the coordinates
            for all the joints; the attributes ``pose_number`` and ``timestamp`` are preserved from the original
            sequence.
        """
        t = add_tabs * "\t"

        if verbosity > 0:
            print(f"\n{t}Creating an empty sequence...", end=" ")
        new_sequence = Sequence(None)

        # Used for the progression percentage
        perc = 10
        for p in range(len(self.poses)):
            perc = show_progression(verbosity, p, len(self.poses), perc)
            # Creates an empty pose with the same timestamp as the original
            pose = self.poses[p]._get_copy_with_empty_joints(False)
            new_sequence.poses.append(pose)  # Add to the sequence

        # Copy the joints from the first pose
        for joint_label in self.poses[0].joints.keys():  # For every joint

            # If this joint doesn't already exist in the new sequence, we copy it
            if joint_label not in new_sequence.poses[0].joints.keys():
                new_sequence.poses[0].joints[joint_label] = joint = self.poses[0].joints[joint_label].copy()

        if verbosity > 0:
            print("100% - Done.")

        new_sequence.joint_labels = self.joint_labels.copy()

        return new_sequence

    def _set_attributes_from_other_sequence(self, other):
        """Sets the attributes `condition`, `system`, `dimensions`, `is_randomized`, `date_recording`, `metadata` and
        `time_unit` of the Sequence from another instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Sequence
            Another Sequence instance, from which to copy some of the parameters.
        """
        self.path = other.path
        self.condition = other.condition
        self.system = other.system
        self.dimensions = other.dimensions
        self.is_randomized = other.is_randomized
        self.date_recording = other.date_recording
        self.metadata = copy.deepcopy(other.metadata)
        self.time_unit = other.time_unit

    # === Conversion functions ===
    def to_table(self, use_relative_timestamps=False):
        """Returns a list of lists where each sublist contains a timestamp and the coordinates for each joint. The
        coordinates are grouped by sets of three, with the values on the x, y and z axes respectively. The first sublist
        contains the headers of the table. The output then resembles the table found in
        :ref:`Tabled formats <table_example>`.

        .. versionadded:: 2.0

        Parameters
        ----------
        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        list(list)
            A list of lists that can be interpreted as a table, containing headers, and with the timestamps and the
            coordinates of the joints from the sequence on each row.

        Example
        -------
        >>> sequence = Sequence("Ana-Lucia/sequence_47.tsv")
        >>> sequence.to_table()
        [["Timestamp", "Head_X", "Head_Y", "Head_Z"],
        [0, 4, 8, 15],
        [0.01, 16, 23, 42],
        [0.02, 108, 316, 815]]
        """

        table = []

        # For each pose
        for p in range(len(self.poses)):
            if p == 0:
                table = self.poses[0].to_table(use_relative_timestamps)
            else:
                table.append(self.poses[p].to_table(use_relative_timestamps)[1])

        return table

    def to_json(self, include_metadata=True, use_relative_timestamps=False):
        """Returns a list ready to be exported in JSON. The structure followed by the dictionary is the same as the
        output dictionary from Kinect, for compatibility purposes. The output then resembles the table found in
        :ref:`JSON formats <json_example>`.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_metadata: bool, optional
            Whether to include the metadata in the output dictionary.
        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        dict
            A dictionary containing the data of the sequence, ready to be exported in JSON.

        Example
        -------
        >>> sequence = Sequence("Miles/sequence_48.tsv")
        >>> sequence.to_json()
        ['Poses':
            [{'Bodies':
                [{'Joints':
                    [{'JointType':
                        'Head',
                      'Position':
                          {'X': 0.160617024, 'Y': 0.494735048, 'Z': -0.453307693},
                      'Timestamp': 0.0}]}]}]
        """

        if include_metadata:
            data = self.metadata.copy()
            for key in data:
                if str(type(data[key])) == "<class 'datetime.datetime'>":
                    data[key] = str(data[key])
        else:
            data = {}
        data["Poses"] = []

        # For each pose
        for p in range(len(self.poses)):
            data["Poses"].append(self.poses[p].to_json(use_relative_timestamps))

        return data

    def to_dict(self, use_relative_timestamps=False):
        """Returns a dictionary containing the data of the sequence. The coordinates are grouped by sets of three,
        with the values on the x, y and z axes respectively. The first sublist contains the headers of the table. The
        output then resembles the table found in :ref:`Tabled formats <table_example>`.

        .. versionadded:: 2.0

        Parameters
        ----------
        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        dict
            A dataframe containing the timestamps and coordinates of the sequence.

        Example
        -------
        >>> sequence = Sequence("Daniel/sequence_49.tsv")
        >>> sequence.to_dict()
        {"Timestamp": [0, 0.001, 0.002], "Head_X": [1, 2, 3], "Head_Y": [4, 5, 6], "Head_Z": [7, 8, 9]}
        """
        data_dict = {"Timestamp": self.get_timestamps(use_relative_timestamps)}

        for joint_label in self.joint_labels:
            data_dict[joint_label + "_X"] = self.get_measure("x", joint_label)
            data_dict[joint_label + "_Y"] = self.get_measure("y", joint_label)
            data_dict[joint_label + "_Z"] = self.get_measure("z", joint_label)

        return data_dict

    def to_dataframe(self, use_relative_timestamps=False):
        """Returns a Pandas dataframe containing the data of the sequence. The coordinates are grouped by sets of three,
        with the values on the x, y and z axes respectively. The first sublist contains the headers of the table. The
        output then resembles the table found in :ref:`Tabled formats <table_example>`.

        .. versionadded:: 2.0

        Parameters
        ----------
        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        Pandas.dataframe
            A dataframe containing the timestamps and coordinates of the sequence.

        Example
        -------
        >>> sequence = Sequence("Charlotte/sequence_50.tsv")
        >>> sequence.to_dataframe()
            Timestamp    Head_X    Head_Y  ...  HandLeft_X  HandLeft_Y  HandLeft_Z
        0      0.000  0.160617  0.494735  ...   -1.395066    2.653739   -0.483164
        1      0.001  1.769412  0.885312  ...   -0.806453    1.460889    2.557279
        2      0.002 -1.678118  0.850645  ...   -1.418790    0.283037   -0.221482
        """
        data_dict = self.to_dict(use_relative_timestamps)
        return pd.DataFrame(data_dict)

    # === Miscellaneous functions ===
    def average_qualisys_to_kinect(self, joints_labels_to_exclude=None, remove_non_kinect_joints=False, verbosity=1):
        """Creates missing Kinect joints from the Qualisys labelling system by averaging the distance between Qualisys
        joints, and returns the resulting sequence. The new joints are located at the midpoint of the arithmetic
        distance between two or more joints. The list of averaged joints is set from the ``res/kualisys_to_kinect.txt``
        file:

        +---------------+------------------+-------------------+-------------+-----------+
        |   New joint   | Averaged joints                                                |
        +===============+==================+===================+=============+===========+
        | Head          | HeadTop          | HeadFront         | HeadRight   | HeadLeft  |
        +---------------+------------------+-------------------+-------------+-----------+
        | Neck          | Head             | SpineShoulder     |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | ShoulderLeft  | ShoulderTopLeft  | ShoulderTopRight  |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | ShoulderRight | ShoulderTopRight | ShoulderBackRight |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | SpineMid      | Chest            | BackRight         | BackLeft    |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | HipLeft       | WaistBackLeft    | WaistFrontLeft    |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | HipRight      | WaistBackRight   | WaistFrontRight   |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | SpineBase     | HipLeft          | HipRight          |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | WristLeft     | WristOutLeft     | WristInLeft       |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | WristRight    | WristOutRight    | WristInRight      |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | HandLeft      | HandOutLeft      | HandInLeft        |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | HandRight     | HandOutRight     | HandInRight       |             |           |
        +---------------+------------------+-------------------+-------------+-----------+
        | FootLeft      | ForefootOutLeft  | ForefootInLeft    | ToetipLeft  | HeelLeft  |
        +---------------+------------------+-------------------+-------------+-----------+
        | FootRight     | ForefootOutRight | ForefootInRight   | ToetipRight | HeelRight |
        +---------------+------------------+-------------------+-------------+-----------+

        .. versionadded:: 2.0

        Parameters
        ----------
        joints_labels_to_exclude: list(str) or None, optional
            List of joint labels that will **not** be created from the function.
        remove_non_kinect_joints: bool, optional
            If ``True``, removes the joints from Qualisys that are not found in the Kinect labelling system.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            A Sequence instance with the averaged joints.

        Example
        -------
        >>> sequence = Sequence("Frank/sequence_51.tsv")  # Qualisys sequence, 44 joints
        >>> sequence.average_qualisys_to_kinect(remove_non_kinect_joints=True)  # Kinect converted sequence, 21 joints
        """

        new_sequence = self.copy()

        joints_to_average = load_qualisys_to_kinect()
        list_kinect_joints = load_joint_labels("kinect")
        joints_to_remove = [] #["ArmRight", "ArmLeft", "ThighRight", "ThighLeft", "ShinRight", "ShinLeft"]

        if remove_non_kinect_joints:
            for joint_label in new_sequence.joint_labels:
                if joint_label not in list_kinect_joints:
                    joints_to_remove.append(joint_label)

        if joints_labels_to_exclude is None:
            joints_labels_to_exclude = []

        for p in range(len(new_sequence.poses)):

            for joint_label in joints_to_average.keys():

                if joint_label not in joints_labels_to_exclude:
                    new_sequence.poses[p].generate_average_joint(joints_to_average[joint_label], joint_label)

            if remove_non_kinect_joints:
                new_sequence.poses[p].remove_joints(joints_to_remove)

        new_sequence._set_joint_labels(verbosity)
        new_sequence._apply_joint_labels(verbosity)

        return new_sequence

    def average_joints(self, joints_labels_to_average, new_joint_label, remove_averaged_joints=False, verbosity=0):
        """Create a joint located at the average arithmetic distance of specified joint labels.

        .. versionadded:: 2.0

        Parameters
        ----------
        joints_labels_to_average: list(str)
            A list of the labels of the joints to average.
        new_joint_label: str
            The label of the newly created joint.
        remove_averaged_joints: bool, optional
            If ``True``, removes the joints that are part of an averaging from every pose of the sequence.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Note
        ----
        Compared to :func:`Sequence.average_qualisys_to_kinect()`, this function modifies the Sequence instance
        in-place.

        Example
        -------
        >>> sequence = Sequence("Jacob/sequence_52.tsv")
        >>> sequence.poses[0].joints["HeadFront"].get_position()
        (0, 0, 0)
        >>> sequence.poses[0].joints["HeadBack"].get_position()
        (2, 2, 2)
        >>> sequence.average_joints(["HeadFront", "HeadBack"], "Head", False)
        >>> sequence.poses[0].joints["Head"].get_position()
        (1, 1, 1)
        """

        for pose in self.poses:
            pose.generate_average_joint(joints_labels_to_average, new_joint_label)

            if remove_averaged_joints:
                pose.remove_joints(joints_labels_to_average)

        self._set_joint_labels(verbosity)
        self._apply_joint_labels(verbosity)

    def concatenate(self, other, delay=None, name=None, verbosity=0):
        """Returns a new Sequence, result of the concatenation of another sequence to the end of the current instance,
        with a delay.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: :class:`Sequence`
            The sequence to concatenate.
        delay: float, optional
            The delay to apply, in seconds, between the last pose of the original sequence and the first pose of the
            new sequence. If set on None, the applied delay will be the 1 over the sampling rate of the current
            instance.
        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the concatenation of the
            name of both sequences, separated by a space.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Sequence
            A new Sequence instance concatenating the poses of the two Sequences, separated by a delay. The preserved
            metadata in the new instance is the same as the current instance.

        Example
        -------
        >>> sequence_1 = Sequence("Richard/sequence_53_part1.tsv")  # 3 poses at 10 Hz
        >>> sequence_2 = Sequence("Richard/sequence_53_part2.tsv")  # 3 poses at 10 Hz
        >>> sequence_3 = sequence_1.concatenate(sequence_2, "sequence_53_full")
        >>> sequence_3.get_timestamps()
        [0, 0.1, 0.2, 0.3, 0.4, 0.5]
        """
        new_sequence = self.copy()

        if name is None:
            new_sequence.set_name(self.name + " " + other.name)
        else:
            new_sequence.set_name(name)

        last_pose_timestamp = new_sequence.poses[-1].timestamp

        if delay is None:
            delay = self.get_sampling_rate()

        for p in range(len(other.poses)):
            new_sequence.poses.append(other.poses[p])
            new_sequence.poses[-1].timestamp = last_pose_timestamp + delay + new_sequence.poses[-1].relative_timestamp

        new_sequence._calculate_relative_timestamps()
        new_sequence._set_joint_labels(verbosity)
        new_sequence._apply_joint_labels(verbosity)

        return new_sequence

    def copy(self):
        """Returns a deep copy of the Sequence object.

        .. versionadded:: 2.0

        Returns
        -------
        Sequence
            A new Sequence object, copy of the original.

        Example
        -------
        >>> sequence = Sequence("Libby/sequence_54.tsv")
        >>> sequence_copy = sequence.copy()
        """
        return super().copy()

    def print_all(self, include_metadata=False):
        """Successively prints the poses, their timestamps and the coordinates of each of the joints. If specified,
        also prints the metadata of the sequence.

        .. versionadded:: 2.0

        Important
        ---------
        For long sequences, the output can be quite long, so use this function with care, or on a subset of the
        sequence (by using the :func:`Sequence.trim` function first).

        Parameters
        ----------
        include_metadata: bool, optional
            If set on ``True``, the output will be led the metadata of the sequence. Default: ``False``.

        Example
        -------
        >>> sequence = Sequence("Penny/sequence_55.tsv")
        >>> sequence.print_all()
        #################
        ## sequence_55 ##
        #################

        Poses
        #####

        Pose 1/3
        Timestamp: 0.0
        Relative timestamp: 0.0
        Joints (3):
        Head: (0.160617024, 0.494735048, -0.453307693)
        HandRight: (0.127963375, 0.873208589, 0.408531847)
        HandLeft: (-1.395065714, 2.653738732, -0.483163821)

        Pose 2/3
        Timestamp: 0.001
        Relative timestamp: 0.001
        Joints (3):
        Head: (1.769412418, 0.885312165, -0.785718175)
        HandRight: (0.948776526, 2.805260745, 2.846927978)
        HandLeft: (-0.80645271, 1.460889453, 2.557279205)

        Pose 3/3
        Timestamp: 0.002
        Relative timestamp: 0.002
        Joints (3):
        Head: (-1.678118013, 0.85064505, 1.37303521)
        HandRight: (-1.612589342, -0.059736892, -1.456678185)
        HandLeft: (-1.418789803, 0.283037432, -0.221482265)
        """

        print("#" * (len(self.name) + 6))
        print("## " + self.name + " ##")
        print("#" * (len(self.name) + 6) + "\n")

        if include_metadata:
            print("Metadata")
            print("########\n")
            for key in self.metadata:
                print(f"{key}: {self.metadata[key]}")
            print()

        print("Poses")
        print("#####\n")

        for p in range(len(self.poses)):
            print(f"Pose {p + 1}/{len(self.poses)}")
            print(str(self.poses[p]) + "\n")

    # === Saving functions ===

    def save(self, folder_out="", name=None, file_format="json", encoding="utf-8", individual=False,
             include_metadata=True, use_relative_timestamps=True, verbosity=1):
        """Saves a sequence in a file or a folder. The function saves the sequence under
        ``folder_out/name.file_format``. All the non-existent subfolders present in the ``folder_out`` path will be
        created by the function. The function also updates the :attr:`path` attribute of the Sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str, optional
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them. If the string provided is empty (by default), the sequence will be saved in
            the current working directory. If the string provided contains a file with an extension, the fields ``name``
            and ``file_format`` will be ignored.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on the attribute :attr:`name` of the sequence; if that attribute is also set on ``None``, the name will be
            set on ``"out"``. If ``individual`` is set on ``True``, each pose will be saved as a different file, having
            the index of the pose as a suffix after the name (e.g. if the name is ``"pose"`` and the file format is
            ``"txt"``, the poses will be saved as ``pose_0.txt``, ``pose_1.txt``, ``pose_2.txt``, etc.).

        file_format: str or None, optional
            The file format in which to save the sequence. The file format must be ``"json"`` (default), ``"xlsx"``,
            ``"txt"``, ``"csv"``, ``"tsv"``, ``"pkl"``, or, if you are a masochist, ``"mat"``. Notes:

                • ``"xls"`` will save the file with an ``.xlsx`` extension.
                • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
                • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
                  on ``,``. By default, the function will detect which separator the system uses.
                • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
                • ``"pkl"`` or ``"pickle"`` will save the sequence using pickling.
                • Any other string will not return an error, but rather be used as a custom extension. The data will
                  be saved as in a text file (using tabulations as values separators).

            .. warning::
                While it is possible to save sequences as ``.mat`` or custom extensions, the toolbox will not recognize
                these files upon opening. The support for ``.mat`` and custom extensions as input may come in a future
                release, but for now these are just offered as output options.

        encoding: str, optional
            The encoding of the file to save. By default, the file is saved in UTF-8 encoding. This input can take any
            of the
            `official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`). This parameter does not apply to individually
            saved files.

                • For ``json`` files, the metadata is saved at the top level. Metadata keys will be saved next to the
                  ``"Poses"`` key.
                • For ``mat`` files, the metadata is saved at the top level of the structure.
                • For ``xlsx`` files, the metadata is saved in a second sheet.
                • For ``pkl`` files, the metadata will always be saved as the object is saved as-is - this parameter
                  is thus ignored.
                • For all the other formats, the metadata is saved at the beginning of the file.

        use_relative_timestamps: bool, optional
            Defines if the timestamps that will be saved are absolute (``False``) or relative to the first pose
            (``True``).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Examples
        --------
        >>> sequence_1 = Sequence("MarkS/sequence_1.json")
        >>> sequence_1.save("MarkS/sequence_1.tsv")
        >>> sequence_1.save("MarkS/sequence_1.mat", include_metadata=False)
        """

        if folder_out == "":
            folder_out = os.getcwd()

        if not individual:
            subfolders = op.normpath(folder_out).split(os.sep)
            if len(subfolders) != 0:
                if "." in subfolders[-1]:
                    folder_out = op.split(folder_out)[0]
                    name, file_format = op.splitext(subfolders[-1])

        # Automatic creation of all the folders of the path if they don't exist
        os.makedirs(folder_out, exist_ok=True)

        if name is None and self.name is not None:
            name = self.name
        elif name is None:
            name = "out"

        file_format = file_format.strip(".")  # We remove the dot in the format
        if file_format in ["xl", "xls", "excel"]:
            file_format = "xlsx"

        if verbosity > 0:
            if individual:
                print(f"Saving {file_format.upper()} individual files...")
            else:
                folder_without_slash = folder_out.strip('/')
                print(f"Saving {file_format.upper()} global file: {folder_without_slash}/{name}.{file_format}...")

        if file_format == "json":
            self.save_json(folder_out, name, individual, include_metadata, encoding, use_relative_timestamps, verbosity)

        elif file_format == "mat":
            self.save_mat(folder_out, name, individual, include_metadata, use_relative_timestamps, verbosity)

        elif file_format == "xlsx":
            self.save_excel(folder_out, name, individual, include_metadata=include_metadata,
                            use_relative_timestamps=use_relative_timestamps, verbosity=verbosity)

        elif file_format in ["pickle", "pkl"]:
            self.save_pickle(folder_out, name, individual, verbosity)

        else:
            self.save_txt(folder_out, name, file_format, encoding, individual, include_metadata,
                          use_relative_timestamps, verbosity)

        if individual:
            self.path = op.join(folder_out, name)
        else:
            self.path = op.join(folder_out, name + "." + file_format)

        if verbosity > 0:
            print("100% - Done.")

    def save_info(self, folder_out="", name=None, file_format="json", encoding="utf-8", keys_to_exclude=None,
                  keys_to_include=None, verbosity=1):
        """Saves the statistics provided by :meth:``Sequence.get_stats`` on the disk.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str, optional
            The path to the folder where to save the file containing the stats. If one or more subfolders of the path do
            not exist, the function will create them. If the string provided is empty (by default), the sequence will be
            saved in the current working directory. If the string provided contains a file with an extension, the fields
            ``name`` and ``file_format`` will be ignored.

        name: str, optional
            Defines the name of the file or files where to save the stats. If set on ``None``, the name will be set
            on ``"stats_"`` plus the attribute :attr:`name` of the sequence; if that attribute is also set on ``None``,
            the name will be set on ``"stats"``.

        file_format: str, optional
            The file format in which to save the stats. The file format must be ``"json"`` (default), ``"xlsx"``,
            ``"txt"``, ``"csv"``, ``"tsv"``, or, if you are a masochist, ``"mat"``. Notes:

                • ``"xls"`` will save the files with an ``.xlsx`` extension.
                • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
                • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
                  on ``,``. By default, the function will detect which separator the system uses.
                • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
                • Any other string will not return an error, but rather be used as a custom extension. The data will
                  be saved as in a text file (using tabulations as values separators).

        encoding: str, optional
            The encoding of the file to save. By default, the file is saved in UTF-8 encoding. This input can take any
            of the
            `official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        keys_to_exclude: list(str) or None, optional
            A list of the stats that you do not wish to save. Each string must be a valid entry among the keys saved by
            the function :meth:`Sequence.get_stats`. If set on ``None``, all the stats will be saved, unless some keys
            are specified in ``keys_to_include``.

        keys_to_include: list(str) or None, optional
            A list of the stats that you wish to save. Each string must be a valid entry among the keys saved by the
            function :meth:`Sequence.get_stats`. If set on ``None``, all the stats will be saved, unless some keys are
            specified in ``keys_to_exclude``. If at least one key is entered, all the absent keys will not be saved.
            This parameter will only be considered if ``keys_to_exclude`` is None.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> sequence = Sequence("HellyR/sequence_2.json")
        >>> sequence.save_info("HellyR/stats.csv")
        """

        if folder_out == "":
            folder_out = os.getcwd()

        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0:
            if "." in subfolders[-1]:
                folder_out = op.split(folder_out)[0]
                name, file_format = op.splitext(subfolders[-1])

        # Automatic creation of all the folders of the path if they don't exist
        os.makedirs(folder_out, exist_ok=True)

        # Handling file format
        file_format = file_format.strip(".")  # We remove the dot in the format
        if file_format == "xls":
            file_format = "xlsx"

        stats = self.get_info(verbosity=verbosity)
        if keys_to_exclude is not None:
            for key in keys_to_exclude:
                del stats[key]

        if keys_to_exclude is None and keys_to_include is not None:
            selected_stats = {}
            for key in keys_to_include:
                selected_stats[key] = stats[key]
            stats = selected_stats

        path_out = op.join(folder_out, f"{name}.{file_format}")

        if file_format in ["json", "mat"]:

            if file_format == "json":
                with open(path_out, 'w', encoding=encoding) as f:
                    json.dump(stats, f)

            elif file_format == "mat":
                for key in stats:
                    if stats[key] is None:
                        stats[key] = np.nan
                savemat(path_out, {"data": stats})

        else:

            table = [[], []]
            for key in stats.keys():
                table[0].append(key)
                table[1].append(stats[key])

            if file_format == "xlsx":
                write_xlsx(table, path_out, verbosity)

            else:
                # Force comma or semicolon separator
                if file_format == "csv,":
                    separator = ","
                    folder_out = folder_out[:-1]
                elif file_format == "csv;":
                    separator = ";"
                    folder_out = folder_out[:-1]
                elif file_format[0:3] == "csv":  # Get the separator from local user (to get , or ;)
                    separator = get_system_csv_separator()
                else:  # For text files, tab separator
                    separator = "\t"

                write_text_table(table, separator, path_out, encoding=encoding, verbosity=verbosity)

    def save_json(self, folder_out, name=None, individual=False, include_metadata=True,
                  encoding="utf-8", use_relative_timestamps=False, verbosity=1):
        """Saves a sequence as a json file or files. This function is called by the :meth:`Sequence.save`
        method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files, or the complete path to the file.
            If one or more subfolders of the path do not exist, the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``. This parameter is
            ignored if ``folder_out`` already contains the name of the file.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`).

        encoding: str, optional
            The encoding of the file to save. By default, the file is saved in UTF-8 encoding. This input can take any
            of the
            `official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> sequence = Sequence("IrvingB/sequence_3.tsv")
        >>> sequence.save_json("IrvingB", "sequence_3")
        >>> sequence.save_json("IrvingB/sequence_3.json")
        """

        perc = 10  # Used for the progression percentage

        path_out = None
        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0 and not individual:
            if subfolders[-1].endswith(".json"):
                path_out = folder_out
            else:
                if name is None:
                    name = "out"
                if name.endswith(".json"):
                    path_out = op.join(folder_out, name)
                else:
                    path_out = op.join(folder_out, f"{name}.json")

        # Get the data
        data = self.to_json(include_metadata, use_relative_timestamps)

        # Save the data
        if not individual:
            with open(path_out, 'w', encoding=encoding) as f:
                json.dump(data, f)
        else:
            if name is None:
                name = "pose"
            for p in range(len(self.poses)):
                perc = show_progression(verbosity, p, len(self.poses), perc)
                with open(op.join(folder_out, f"{name}_{p}.json"), 'w', encoding=encoding) as f:
                    json.dump(data["Poses"][p], f)

    def save_mat(self, folder_out, name=None, individual=False, include_metadata=True, use_relative_timestamps=True,
                 verbosity=1):
        """Saves a sequence as a Matlab .mat file or files. This function is called by the :meth:`Sequence.save`
        method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Important
        ---------
        This function is dependent of the module `scipy <https://scipy.org/>`_.

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files, or the complete path to the file.
            If one or more subfolders of the path do not exist, the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``. This parameter is
            ignored if ``folder_out`` already contains the name of the file.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`).

        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> sequence = Sequence("DylanG/sequence_4.tsv")
        >>> sequence.save_mat("DylanG", "sequence_4")
        >>> sequence.save_mat("DylanG/sequence_4.mat")
        """
        perc = 10  # Used for the progression percentage

        path_out = None
        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0 and not individual:
            if subfolders[-1].endswith(".mat"):
                path_out = folder_out
            else:
                if name is None:
                    name = "out"
                if name.endswith(".mat"):
                    path_out = op.join(folder_out, name)
                else:
                    path_out = op.join(folder_out, f"{name}.mat")

        # Save the data
        if not individual:
            data_json = self.to_json(include_metadata, use_relative_timestamps)
            data_json["Poses"] = self.to_dict(use_relative_timestamps)
            for key in data_json:
                if data_json[key] is None:
                    data_json[key] = np.nan
                elif key == "processing_steps":
                    for i in range(len(data_json["processing_steps"])):
                        for param in data_json["processing_steps"][i]:
                            if data_json["processing_steps"][i][param] is None:
                                data_json["processing_steps"][i][param] = np.nan
            savemat(path_out, {"data": data_json})
        else:
            for p in range(len(self.poses)):
                if name is None:
                    name = "pose"
                data = self.poses[p].to_table(use_relative_timestamps)
                perc = show_progression(verbosity, p, len(self.poses), perc)
                savemat(op.join(folder_out, f"{name}_{p}.mat"), {"data": data})

    def save_excel(self, folder_out, name=None, individual=False, sheet_name="Data", include_metadata=True,
                   metadata_sheet_name="Metadata", use_relative_timestamps=True, verbosity=1):
        """Saves a sequence as an Excel .xlsx file or files. This function is called by the :meth:`Sequence.save`
        method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Important
        ---------
            This function is dependent of the module `openpyxl <https://pypi.org/project/openpyxl/>`_.

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files, or the complete path to the file.
            If one or more subfolders of the path do not exist, the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``. This parameter is
            ignored if ``folder_out`` already contains the name of the file.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

        sheet_name: str|None, optional
            The name of the sheet containing the data. If `None`, a default name will be attributed to the sheet
            (``"Sheet"``).

        include_metadata: bool, optional
            Whether to include the metadata in the Excel file (default: `True`). The metadata is saved in a separate
            sheet in the same Excel file.

        metadata_sheet_name: str|None, optional
            The name of the sheet containing the metadata. If `None`, a default name will be attributed to the sheet
            (``"Metadata"``).

        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> sequence = Sequence("Mr. Milkshake/sequence_5.tsv")
        >>> sequence.save_excel("Mr. Milkshake", "sequence_5")
        >>> sequence.save_excel("Mr. Milkshake/sequence_5.xlsx")
        """

        perc = 10  # Used for the progression percentage

        path_out = None
        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0 and not individual:
            if subfolders[-1].endswith(".xlsx") or subfolders[-1].endswith(".xls"):
                path_out = folder_out
            else:
                if name is None:
                    name = "out"
                if name.endswith(".xlsx") or name.endswith(".xls"):
                    path_out = op.join(folder_out, name)
                else:
                    path_out = op.join(folder_out, f"{name}.xlsx")

        # Save the data
        if not individual:
            data = self.to_table(use_relative_timestamps)
            if include_metadata:
                metadata = copy.deepcopy(self.metadata)
                metadata["processing_steps"] = json.dumps(metadata["processing_steps"])
            else:
                metadata = None
            write_xlsx(data, path_out, sheet_name, metadata, metadata_sheet_name, verbosity)

        else:
            for p in range(len(self.poses)):
                if name is None:
                    name = "pose"
                data = self.poses[p].to_table(use_relative_timestamps)
                perc = show_progression(verbosity, p, len(self.poses), perc)
                write_xlsx(data, op.join(folder_out, f"{name}_{p}.xlsx"), sheet_name, verbosity=0)

    def save_pickle(self, folder_out, name=None, individual=False, verbosity=1):
        """Saves a sequence by pickling it. This allows to reopen the sequence as a Sequence object.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files, or the complete path to the file.
            If one or more subfolders of the path do not exist, the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``. This parameter is
            ignored if ``folder_out`` already contains the name of the file.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> sequence = Sequence("Ms. Cobel/sequence_6.tsv")
        >>> sequence.save_pickle("Ms. Cobel", "sequence_6")
        >>> sequence.save_pickle("Ms. Cobel/sequence_6.pkl")
        """

        perc = 10  # Used for the progression percentage

        path_out = None
        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0 and not individual:
            if subfolders[-1].endswith(".pkl"):
                path_out = folder_out
            else:
                if name is None:
                    name = "out"
                if name.endswith(".pkl"):
                    path_out = op.join(folder_out, name)
                else:
                    path_out = op.join(folder_out, f"{name}.pkl")

        self.path = op.normpath(path_out)
        self.files = [op.split(self.path)[-1]]

        # Save the data
        if not individual:
            with open(path_out, "wb") as f:
                pickle.dump(self, f)

        else:
            for p in range(len(self.poses)):
                if name is None:
                    name = "pose"
                perc = show_progression(verbosity, p, len(self.poses), perc)
                with open(op.join(folder_out, f"{name}_{p}.pkl"), "wb") as f:
                    pickle.dump(self.poses[p], f)

    def save_txt(self, folder_out, name=None, file_format="csv", encoding="utf-8", individual=False,
                 include_metadata=True, use_relative_timestamps=True, verbosity=1):
        """Saves a sequence as .txt, .csv, .tsv, or custom extension files or file. This function is called by the
        :meth:`Sequence.save` method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files, or the complete path to the file.
            If one or more subfolders of the path do not exist, the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``. This parameter is
            ignored if ``folder_out`` already contains the name of the file.

        file_format: str, optional
            The file format in which to save the sequence. The file format can be ``"txt"``, ``"csv"`` (default) or
            ``"tsv"``. ``"csv;"`` will force the value separator on ``";"``, while ``"csv,"`` will force the separator
            on ``","``. By default, the function will detect which separator the system uses. ``"txt"`` and ``"tsv"``
            both separate the values by a tabulation. Any other string will not return an error, but rather be used as
            a custom extension. The data will be saved as in a text file (using tabulations as values separators).
            This parameter is ignored if ``folder_out`` already contains the name of the file.

        encoding: str, optional
            The encoding of the file to save. By default, the file is saved in UTF-8 encoding. This input can take any
            of the
            `official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`). The metadata is saved on the first lines
            of the file.

        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> sequence = Sequence("Ms. Casey/sequence_7.json")
        >>> sequence.save_txt("Ms. Casey", "sequence_7", "txt")
        >>> sequence.save_txt("Ms. Casey/sequence_7.csv")
        """

        perc = 10  # Used for the progression percentage

        path_out = None
        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0 and not individual:
            if "." in subfolders[-1]:
                path_out = folder_out
                file_format = op.splitext(subfolders[-1])[-1][1:]
            else:
                if name is None:
                    name = "out"
                if "." in name:
                    path_out = op.join(folder_out, name)
                else:
                    path_out = op.join(folder_out, f"{name}.{file_format}")

        # Force comma or semicolon separator
        if file_format == "csv,":
            separator = ","
            file_format = "csv"
        elif file_format == "csv;":
            separator = ";"
            file_format = "csv"
        elif file_format == "csv":  # Get the separator from local user (to get , or ;)
            separator = get_system_csv_separator()
        elif file_format == "txt":  # For text files, tab separator
            separator = "\t"
        else:
            separator = "\t"

        # Save the data
        if not individual:
            if include_metadata:
                metadata = self.metadata
            else:
                metadata = None
            write_text_table(self.to_table(use_relative_timestamps), separator, path_out, metadata,
                             None, encoding, verbosity)
        else:
            for p in range(len(self.poses)):
                if name is None:
                    name = "pose"
                if p == 0:
                    metadata = self.metadata
                else:
                    metadata = None
                write_text_table(self.poses[p].to_table(use_relative_timestamps),
                                 separator, op.join(folder_out, f"{name}_{p}.{file_format}"), metadata,
                                 encoding=encoding, verbosity=verbosity)
                perc = show_progression(verbosity, p, len(self.poses), perc)

    # === Magic methods ===
    def __len__(self):
        """Returns the number of poses in the sequence (i.e., the length of the attribute poses).

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of poses in the sequence.

        Example
        -------
        >>> sequence = Sequence("C:/Users/Dumbledore/Sequences/seq1/")
        >>> len(sequence)
        802701
        """
        return len(self.poses)

    def __getitem__(self, index):
        """Returns the pose of index specified by the parameter ``index``.

        Parameters
        ----------
        index: int
            The index of the pose to return.

        Returns
        -------
        Pose
            A pose from the sequence instance.

        Example
        -------
        >>> sequence = Sequence("C:/Users/Homer/Sequences/seq1/")
        >>> sequence[42]
        Timestamp: 0.7673687
        Relative timestamp: 0.7673687
        Joints (21):
            Head: (0.2580389, 0.4354536, 2.449435)
            Neck: (0.2200405, 0.2870165, 2.452467)
            SpineShoulder: (0.2213234, 0.2103061, 2.444264)
            SpineMid: (0.224096, -0.02492883, 2.409717)
            SpineBase: (0.2265415, -0.3467222, 2.352579)
            ShoulderLeft: (0.08861267, 0.1529641, 2.387205)
            ElbowLeft: (0.05989294, -0.05652162, 2.338059)
            WristLeft: (0.1408673, -0.2341767, 2.213683)
            HandLeft: (0.1808563, -0.2797168, 2.203833)
            ShoulderRight: (0.3932458, 0.1480468, 2.420666)
            ElbowRight: (0.410402, -0.09375393, 2.338974)
            WristRight: (0.3219678, -0.2662066, 2.203344)
            HandRight: (0.2747259, -0.3047626, 2.200738)
            HipLeft: (0.1522616, -0.3320134, 2.309463)
            KneeLeft: (0.1468181, -0.8557156, 2.233713)
            AnkleLeft: (0.08108322, -1.155779, 2.15636)
            FootLeft: (0.1320685, -1.193715, 2.080927)
            HipRight: (0.2934242, -0.3502887, 2.319931)
            KneeRight: (0.2045003, -0.8930826, 2.275977)
            AnkleRight: (0.2089309, -1.175371, 2.194727)
            FootRight: (0.2288543, -1.20977, 2.095591)
        """
        return self.poses[index]

    def __repr__(self):
        """Returns the :attr:`name` attribute of the sequence.

        Returns
        -------
        str
            The attribute :attr:`name` of the sequence instance.

        Examples
        --------
        >>> sequence = Sequence("C:/Users/Fiona/Sequences/seq1/")
        >>> print(sequence)
        seq1

        >>> sequence = Sequence("C:/Users/Fiona/Sequences/seq1/", name="my_sequence")
        >>> print(sequence)
        my_sequence
        """
        return self.name

    def __eq__(self, other):
        """Returns `True` if all the poses in the attribute :attr:`poses` have identical joints between the two
        :class:`Sequence` objects.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Sequence
            Another :class:`Sequence` object.
        """
        if len(self.poses) != len(other.poses):
            return False

        for pose_index in range(len(self.poses)):
            if self.poses[pose_index] != other.poses[pose_index]:
                return False

        return True


