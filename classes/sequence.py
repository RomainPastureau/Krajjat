"""Default class for motion sequences in the toolbox. An instance of this class will be
one motion sequence. The class contains several methods to perform **pre-processing** or
**displaying summarized data** in text form (see public methods)."""

from collections import OrderedDict

from classes.pose import Pose
from classes.audio import Audio
from classes.exceptions import *
from tool_functions import *

from statistics import stdev
from datetime import datetime, timedelta


class Sequence(object):
    """Creates an instance from the class Sequence and returns a Sequence object, allowing to be manipulated for
    processing or displaying. Upon creation, the function tries to assign a name to it based on the provided
    name parameter or path parameter. It then proceeds to load the sequence if a path has been provided.

    .. versionadded:: 2.0

    Parameters
    ----------
    path: str or None, optional
        Absolute path to the motion sequence (starting from the root of the drive, e.g.
        ``C:/Users/Elliot/Documents/Recordings``). The path may point to a folder or a single file.
        For the acceptable file types, see :doc:`input`. If the path is ``None``, an empty sequence will be created.

    path_audio: str or None, optional
        Absolute path to an audio file corresponding to the sequence. The path should point to a .wav
        file. This path will be stored as an attribute of the Sequence object, and may be used automatically by
        functions using an audio file (typically, :py:meth:`Sequence.synchronize()` and :py:func:`sequence_reader()`).
        This parameter is however far from vital in the definition of a Sequence instance, and can be skipped safely.

    name: str or None, optional
        Defines a name for the Sequence instance. If a string is provided, the attribute :attr:`name` will take
        its value. If not, see :meth:`Sequence._define_name_init()`.

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
    randomized: bool
        Testifies if the starting position of the joints have been randomized by the function
        :meth:`Sequence.randomize()`. Is ``False`` upon initialisation.
    date_recording: datetime
        The date at which the recording was performed, extracted from the file.
    time_unit: str
        The time unit of the timestamps.
    """

    def __init__(self, path=None, path_audio=None, name=None, condition=None, time_unit="auto",
                 start_timestamps_at_zero=False, verbosity=1):

        self.path_audio = path_audio  # Path to the audio file matched with this series of gestures

        self.name = None  # Placeholder for the name of the sequence
        self._define_name_init(name, path, verbosity)  # Defines the name of the sequence
        self.condition = condition  # Experimental condition of the recording

        self.files = None  # List of the files in the target folder
        self.poses = []  # List of the poses in the sequence, ordered
        self.randomized = False  # True if the joints positions are randomized
        self.date_recording = None  # Placeholder for the date of the recording.
        self.time_unit = time_unit  # Time unit of the timestamps

        # In the case where a file or folder is passed as argument,
        # we load the sequence
        self.path = path  # Placeholder for the path

        if path is not None:
            self._load_from_path(verbosity)

        if start_timestamps_at_zero:
            self.set_first_timestamp(0)

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
        >>> seq = Sequence("C:/Users/Mario/Sequences/seq1/")
        >>> seq.set_name("Sequence story telling 7")
        """

        self.name = name

    def set_condition(self, condition):
        """Sets the :py:attr:`condition` attribute of the Sequence instance. This attribute can be used to save the
        experimental condition in which the sequence instance was recorded.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str
            The experimental condition in which the sequence was recorded.

        Example
        -------
        >>> seq1 = Sequence("C:/Users/Harold/Sequences/English/seq.xlsx")
        >>> seq1.set_condition("English")
        >>> seq2 = Sequence("C:/Users/Harold/Sequences/Spanish/seq.xlsx")
        >>> seq2.set_condition("Spanish")
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
            The absolute path to the .wav file corresponding to the sequence."""

        self.path_audio = path_audio

    def set_first_timestamp(self, first_timestamp):
        """Attributes a new timestamp to the first pose of the sequence and delays the timestamps of the other poses
        accordingly.

        .. versionadded:: 2.0

        Parameters
        ----------
        first_timestamp: float or int
            The new timestamp of the first pose of the sequence.

        Note
        ----
        If 0 is passed as a parameter, the absolute timestamps of the sequence will be equal to its relative timestamps.
        """
        timestamps = self.get_timestamps(relative=False)

        for p in range(len(self.poses)):
            self.poses[p].set_timestamp(timestamps[p] + first_timestamp)

    # === Loading functions ===
    def _define_name_init(self, name, path, verbosity=1):
        """Sets the name attribute for an instance of the Sequence class, using the name provided during the
        initialization, or the path. If no ``name`` is provided, the function will create the name based on the ``path``
        provided, by defining the name as the last element of the path hierarchy (last subfolder, or file name).
        For example, if ``path`` is ``"C:/Users/Darlene/Documents/Recording001/"``, the function will define the name
        on ``"Recording001"``. If both ``name`` and ``path`` are set on ``None``, the sequence name will be defined as
        ``"Unnamed sequence"``.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: str
            The name passed as parameter in :meth:`Sequence.__init__()`
        path: str
            The path passed as parameter in :meth:`Sequence.__init__()`
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        if name is not None:
            self.name = name
            if verbosity > 1:
                print("The provided name " + str(name) + " will be attributed to the sequence.")

        elif path is not None:
            if len(path.split("/")) >= 1:
                self.name = path.split("/")[-1]
            else:
                self.name = str(path)
            if verbosity > 1:
                print(
                    "No name was provided. Instead, the name " + str(self.name) + " was attributed by extracting it " +
                    "from the provided path.")

        else:
            self.name = "Unnamed sequence"
            if verbosity > 1:
                print("No name nor path was provided. The placeholder name " + str(
                    self.name) + " was attributed to the " +
                      "sequence.")

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

        # If it's a folder, we fetch all the files
        if not os.path.exists(self.path):
            if "." in self.path.split("/")[-1]:
                raise InvalidPathException(self.path, "sequence", "The file doesn't exist.")
            else:
                raise InvalidPathException(self.path, "sequence", "The folder doesn't exist.")

        if os.path.isdir(self.path):
            self._fetch_files_from_folder(verbosity)  # Fetches all the files
        else:
            self.files = self.path
        self._load_poses(verbosity)  # Loads the files into poses

        if len(self.poses) == 0:
            raise EmptySequenceException()

        self._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

    def _fetch_files_from_folder(self, verbosity=1):
        """Finds all the files ending with the accepted extensions (``.csv``, ``.json``, ``.tsv``, ``.txt``, or
        ``.xlsx``) in the folder defined by path, and orders the files according to their name.

        .. versionadded:: 2.0

        Note
        ----
        This functions ignores the elements of the directory defined by :attr:`path` if:
            •	They don’t have an extension
            •	They are a folder
            •	Their extension is not one of the accepted ones (``.csv``, ``.json``, ``.tsv``, ``.txt``, or
                ``.xlsx``)
            •	The file name does not contain an underscore (``_``)

        If a file has a valid extension, the function tries to detect an underscore (``_``) in the name. The file
        names should be ``xxxxxx_0.ext``, where ``xxxxxx`` can be any series of characters, ``0`` must be the index of
        the pose (with or without leading zeros), and ``ext`` must be an accepted extension (``.csv``, ``.json``,
        ``.tsv``, ``.txt``, or ``.xlsx``). The first pose of the sequence must have the index 0. If the file does not
        have an underscore in the name, it is ignored. The indices must be coherent with the chronological order of the
        timestamps.

        The function uses the number after the underscore to order the poses. This is due to differences in how file
        systems handle numbers without leading zeros: some place ``pose_11.json`` alphabetically before ``pose_2.json``
        (1 comes before 2), while some other systems place it after as 11 is greater than 2. In order to avoid these,
        the function converts the number after the underscore into an integer to place it properly according to its
        index.

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
        if verbosity > 0:
            print("Fetching sequence files...", end=" ")

        file_list = os.listdir(self.path)  # List all the files in the folder
        self.files = ["" for _ in range(len(file_list))]  # Create an empty list the length of the files

        extensions_found = []  # Save the valid extensions found in the folder

        # Here, we find all the files that are either .json or .meta in the folder.
        for f in file_list:

            # If a file has an accepted extension, we get its index from its name to order it correctly in the list.
            # This is necessary as some file systems will order frame_2.json after frame_11.json because,
            # alphabetically, "1" is before "2".

            # We check if the element has a dot, i.e. if it is a file. If not, it is a folder, and we ignore it.
            if "." in f:

                extension = f.split(".")[-1]  # We get the file extension
                if extension in ["json", "csv", "tsv", "txt", "xlsx"]:

                    if verbosity > 1:
                        print("\tAdding file: " + str(f))

                    if "_" in f:
                        self.files[int(f.split(".")[0].split("_")[1])] = f
                        if extension not in extensions_found:
                            extensions_found.append(extension)
                    else:
                        if verbosity > 1:
                            print("""\tIgnoring file (no "_" detected in the name): """ + str(f))

                    if len(extensions_found) > 1:
                        raise InvalidPathException(self.path, "sequence",
                                                   "More than one of the accepted extensions has been found in the " +
                                                   "provided folder: " + str(extensions_found[0]) + " and " +
                                                   str(extensions_found[1]))

                else:
                    if verbosity > 1:
                        print("\tIgnoring file (not an accepted filetype): " + str(f))

            else:
                if verbosity > 1:
                    print("\tIgnoring folder: " + str(f))

        # If files that weren't of the accepted extension are in the folder, then "self.files" is larger than
        # the number of frames. The list is thus ending by a series of empty strings that we trim.
        if "" in self.files:
            limit = self.files.index("")
            self.files = self.files[0:limit]

        for i in range(len(self.files)):
            if self.files[i] == "":
                raise InvalidPathException(self.path, "sequence", "At least one of the files is missing (index " +
                                           str(i) + ").")

        if verbosity > 0:
            print(str(len(self.files)) + " pose file(s) found.")

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

        if verbosity > 0:
            print("Opening sequence from " + self.path + "...", end=" ")

        perc = 10  # Used for the progression percentage

        # If the path is a folder, we load every single file
        if os.path.isdir(self.path):

            for i in range(len(self.files)):

                if verbosity > 1:
                    print("Loading file " + str(i) + " of " + str(len(self.files)) + ":" + self.path + "...", end=" ")

                # Show percentage if verbosity
                perc = show_progression(verbosity, i, len(self.files), perc)

                # Create the Pose object, passes as parameter the index and the file path
                self._load_single_pose_file(i, self.path + "/" + self.files[i], verbosity)

                if verbosity > 1:
                    print("OK.")

            if verbosity > 0:
                print("100% - Done.")

        # Otherwise, we load the one file
        else:
            self._load_sequence_file(verbosity)

    def _load_single_pose_file(self, pose_index, path, verbosity=1):
        """Loads the content of a single pose file into a Pose object. Depending on the file type, this function
        handles the content differently (see :doc:`input`).

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

        file_extension = path.split(".")[-1]

        # JSON file
        if file_extension == "json":
            data = read_json(path)
            if pose_index == 0:
                self._load_date_recording(data, verbosity)
            self._create_pose_from_json(data)

        # Excel file
        elif file_extension == "xlsx":
            data = read_xlsx(path)
            self._create_pose_from_table_row(data)

        elif file_extension in ["txt", "csv", "tsv"]:

            # Open the file and read the data
            data = read_text_table(path)
            self._create_pose_from_table_row(data)

        else:
            raise InvalidPathException(self.path, "sequence", "Invalid file extension: " + file_extension + ".")

    def _load_sequence_file(self, verbosity=1):
        """Loads the content of a global sequence file containing individual poses into Pose objects.
        Depending on the file type, this function handles the content differently (see :doc:`input`).

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

        # JSON file
        if self.path.split(".")[-1] == "json":

            # Open the file and read the data
            data = read_json(self.path)

            self._load_date_recording(data, verbosity)

            for p in range(len(data)):
                if verbosity > 1:
                    print("Loading pose " + str(p) + " of " + str(len(data)) + "...", end=" ")

                # Show percentage if verbosity
                perc = show_progression(verbosity, p, len(data), perc)

                # Create the Pose object, passes as parameter the index and the data
                self._create_pose_from_json(data[p])

                if verbosity > 1:
                    print("OK.")

        # Excel file
        elif self.path.split(".")[-1] == "xlsx":
            data = read_xlsx(self.path)

            # For each pose
            for p in range(len(data) - 1):

                if verbosity > 1:
                    print("Loading pose " + str(p) + " of " + str(len(data)) + "...", end=" ")

                self._create_pose_from_table_row(data, p + 1)

                if verbosity > 1:
                    print("OK.")

        # Text file (csv or txt)
        elif self.path.split(".")[-1] in ["csv", "tsv", "txt"]:

            data = read_text_table(self.path)

            # For each pose
            for p in range(len(data) - 1):

                if verbosity > 1:
                    print("Loading pose " + str(p) + " of " + str(len(data) - 1) + "...", end=" ")

                self._create_pose_from_table_row(data, p + 1)

                if verbosity > 1:
                    print("OK.")

        else:
            raise InvalidPathException(self.path, "sequence", "Invalid file extension: " +
                                       self.path.split(".")[-1] + ".")

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
                pose.add_joint(label, joint)

        self.poses.append(pose)

    def _create_pose_from_json(self, data):
        """Reads the content of a json file containing a single pose, and converts the content of a specified pose index
        into a pose object.

        .. versionadded:: 2.0

        Parameters
        ----------
        data: list or dict
            The content of a json file.
        """

        joints = data["Bodies"][0]["Joints"]
        timestamp = data["Timestamp"]

        pose = Pose(timestamp)
        for j in joints:
            joint = Joint(j["JointType"], j["Position"]["X"], j["Position"]["Y"], j["Position"]["Z"])
            pose.add_joint(j["JointType"], joint)

        self.poses.append(pose)

    def _load_date_recording(self, data, verbosity=1):
        """Loads the date of a recording from the information contained in the file(s). For recordings performed with
        the Qualisys system, the function simply gets the date from the line starting with ``"TIME_STAMP"``. For the
        recordings performed with Kinect, the timestamp value of the first pose is converted to a date.

        .. versionadded:: 2.0

        Parameters
        ----------

        data: dict or list
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
            print("Trying to find recording date...", end=" ")

        if type(data) is dict:
            if "Timestamp" in data.keys():
                self.date_recording = datetime(1, 1, 1) + timedelta(microseconds=data["Timestamp"] / 10)

        elif type(data) is list:
            if len(data) > 7:
                splitted = data[7].split("\t")
                if splitted[0] == "TIME_STAMP":
                    self.date_recording = datetime.fromisoformat(splitted[1].replace(",", ""))

        if verbosity > 1:
            if self.date_recording is not None:
                print("found: " + self.get_printable_date_recording())
            else:
                print("not found.")

    # === Calculation functions ===

    def _calculate_relative_timestamps(self):
        """For all the poses of the sequence, sets and converts the relative_timestamp attribute taking the first pose
        of the sequence as reference. This function is called internally any time a sequence is created. It first
        defines the unit if the attribute :attr:`time_unit` is set on ``"auto"``. To do so, it checks if the difference
        between the timestamps of the two first poses of the sequence:

            • If it is over 1000, the function presumes that the unit is in hundreds of ns (C# precision unit,
              Kinect output unit).
            • If it is between 1 and 1000, it presumes that the unit is in milliseconds (Qualisys output unit).
            • If it is below that threshold, or if there is only one pose in the sequence, it presumes that the unit
              is in seconds.

        Otherwise, it is possible to manually define the unit, among the following values: ``"ns"``, ``"1ns"``,
        ``"10ns"``, ``"100ns"``, ``"µs"``, ``"1µs"``, ``"10µs"``, ``"100µs"``, ``"ms"``, ``"1ms"``, ``"10ms"``,
        ``"100ms"``, ``"s"``, ``"sec"``, ``"1s"``, ``"min"``, ``"mn"``, ``"h"``, ``"hr"``, ``"d"``, ``"day"``.

        .. versionadded:: 2.0
        """
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

        # Validity check
        self.time_unit = self.time_unit.lower().replace(" ", "")  # Removes spaces
        units = ["ns", "1ns", "10ns", "100ns", "µs", "1µs", "10µs", "100µs", "ms", "1ms", "10ms", "100ms",
                 "s", "sec", "1s", "min", "mn", "h", "hr", "d", "day"]
        if self.time_unit not in units:
            raise Exception("Invalid time unit. Should be ns, µs, ms or s.")

        t = self.poses[0].get_timestamp()
        for p in range(len(self.poses)):
            if self.poses[p].timestamp - t < 0:
                raise ImpossibleTimeTravelException(p, 0, self.poses[p].timestamp, t, len(self.poses), "pose")
            elif p > 0:
                if self.poses[p].timestamp - self.poses[p - 1].timestamp < 0:
                    raise ImpossibleTimeTravelException(p, p-1, self.poses[p].timestamp, self.poses[p - 1].timestamp,
                                                        len(self.poses), "pose")
            self.poses[p]._calculate_relative_timestamp(t, self.time_unit)

    # === Getter functions ===

    def get_path(self):
        """Returns the attribute :attr:`path` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The path of the sequence.
        """
        return self.path

    def get_name(self):
        """Returns the attribute :attr:`name` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The name of the sequence.
        """
        return self.name

    def get_condition(self):
        """Returns the attribute :attr:`condition` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The experimental condition in which the recording of the sequence was performed.
        """
        return self.condition

    def get_joint_labels(self):
        """Returns the joint labels present in the first pose of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        list
            The list of the joint labels in the first pose of the sequence.
        """
        if len(self.poses) == 0:
            raise EmptySequenceException()

        return self.poses[0].get_joint_labels()

    def get_date_recording(self):
        """Returns the date and time of the recording as a datetime object, if it exists. If the date of the recording
        was not specified in the original file, the value will be None.

        .. versionadded:: 2.0

        Returns
        -------
        datetime
            The date and time of the first frame of the recording.
        """
        return self.date_recording

    def get_printable_date_recording(self):
        """Returns the date and time of the recording as a string, if it exists. The string returned will contain the
        weekday, day, month (in letters), year, hour, minutes and seconds (e.g. ``"Wednesday 21 October 2015,
        07:28:00"``) at which the recording was started. If the attribute date_recording of the sequence is None, the
        value returned is ``"No date found"``.

        .. versionadded:: 2.0

        Returns
        -------
        string
            A formatted string of the date of the recording.
        """
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

    def get_subject_height(self, verbosity=1):
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

        Parameters
        ----------
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
        """

        kinect_joints = ["Head", "Neck", "SpineShoulder", "SpineMid", "SpineBase", ["KneeRight", "KneeLeft"],
                         ["AnkleRight", "AnkleLeft"], ["FootRight", "FootLeft"]]
        qualisys_joints = ["HeadTop", ["ShoulderTopRight", "ShoulderTopLeft"], "Chest", ["WaistBackRight",
                                                                                         "WaistBackLeft",
                                                                                         "WaistFrontRight",
                                                                                         "WaistFrontLeft"],
                           ["KneeRight", "KneeLeft"],
                           ["AnkleRight", "AnkleLeft"], ["ForefootOutRight", "ForefootOutLeft"]]

        if "Head" in self.poses[0].joints.keys():
            list_joints = kinect_joints
        else:
            list_joints = qualisys_joints

        height_sum = 0  # Summing the heights through all poses to average

        if verbosity > 1:
            print("Calculating the height of the subject based on the poses...")

        for p in range(len(self.poses)):

            pose = self.poses[p]  # Current pose
            dist = 0  # Height for the current pose
            joints = []  # Joints and average joints

            # Getting the average joints
            for i in range(len(list_joints)):

                if type(list_joints[i]) is list:
                    joint = pose.generate_average_joint(list_joints[i], "Average", False)
                else:
                    joint = pose.joints[list_joints[i]]

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

        """
        kinect_joints = ["Shoulder", "Elbow", "Wrist", "Hand"]
        qualisys_joints = ["ShoulderTop", "Arm", "Elbow", "WristOut", "HandOut"]

        if "Head" in self.poses[0].joints.keys():
            list_joints = kinect_joints
        else:
            list_joints = qualisys_joints

        if side.lower() == "left":
            side = "Left"
        elif side.lower() == "right":
            side = "Right"
        else:
            raise Exception('Wrong side parameter: should be "left" or "right"')

        arm_length_sum = 0  # Summing the arm_lengths through all poses to average

        if verbosity > 1:
            print("Calculating the " + side.lower() + " arm length of the subject based on the poses...")

        for p in range(len(self.poses)):

            pose = self.poses[p]  # Current pose
            dist = 0  # Arm length for the current pose

            # Calculating the distance
            for i in range(len(list_joints) - 1):
                dist += calculate_distance(pose.joints[list_joints[i] + side], pose.joints[list_joints[i + 1] + side])

            if verbosity > 1:
                print("\t" + side + " arm length on frame " + str(p + 1) + "/" + str(len(self.poses)) + ": " + str(
                    round(dist, 3)) + " m.")
            arm_length_sum += dist

        arm_length = arm_length_sum / len(self.poses)

        if verbosity == 1:
            print("Average " + side.lower() + " arm length estimated at " + str(round(arm_length, 3)) + " m.")

        return arm_length

    def get_stats(self, tabled=False):
        """Returns a series of statistics regarding the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        tabled: bool, optional
            If set on False (default), the stats are returned as an OrderedDict. If set on True, the stats are returned
            as two-dimensional list.

        Returns
        -------
        OrderedDict or List(List)
            If the returned object is an OrderedDict, the keys are the title of a statistic, and the values are their
            matching value. If the returned object is a two-dimensional list, each sublist contains the title as the
            first element, and the value as the second element.
            The statistics included are:

                • ``"Path"``: The :attr:`path` attribute of the sequence.
                • ``"Date of recording"``: Output of :meth:`Sequence.get_printable_date_recording`.
                • ``"Duration"``: Output of :meth:`Sequence.get_duration` (seconds).
                • ``"Number of poses"``: Output of :meth:`Sequence.get_number_of_poses`.
                • ``"Subject height"``: Output of :meth:`Sequence.get_subject_height` (meters).
                • ``"Left arm length"``: Output of :meth:`Sequence.get_subject_arm_length` for the left arm (meters).
                • ``"Right arm length"``: Output of :meth:`Sequence.get_subject_arm_length` for the right arm (meters).
                • ``"Average framerate"``: Output of :meth:`Sequence.get_average_framerate`.
                • ``"SD framerate"``: Standard deviation of the framerate of the sequence.
                • ``"Min framerate"``: Output of :meth:`Sequence.get_min_framerate`.
                • ``"Max framerate"``: Output of :meth:`Sequence.get_max_framerate`.
                • ``"Average velocity X"``: Output of :meth:`Sequence.get_total_velocity_single_joint()` divided by the
                  total number of poses. This key has one entry per joint label.

        """
        stats = OrderedDict()
        stats["Path"] = self.path
        stats["Date of recording"] = self.get_printable_date_recording()
        stats["Duration"] = self.get_duration()
        stats["Number of poses"] = self.get_number_of_poses()

        # Height and distances stats
        stats["Subject height"] = self.get_subject_height(0)
        stats["Left arm length"] = self.get_subject_arm_length("left", 0)
        stats["Right arm length"] = self.get_subject_arm_length("right", 0)

        # Framerate stats
        frequencies, time_points = self.get_framerates()
        stats["Average framerate"] = self.get_average_framerate()
        stats["SD framerate"] = stdev(frequencies)
        stats["Min framerate"] = self.get_min_framerate()
        stats["Max framerate"] = self.get_max_framerate()

        # Movement stats
        for joint_label in self.poses[0].joints.keys():
            stats["Average velocity " + joint_label] = \
                self.get_total_velocity_single_joint(joint_label) / len(self.poses)

        if tabled:
            table = [[], []]
            for key in stats.keys():
                table[0].append(key)
                table[1].append(stats[key])
            return table

        return stats

    def get_poses(self):
        """Returns the attribute :attr:`poses` of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        list(Pose)
            A list containing all the Pose objects in the sequence, in chronological order.
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
        """
        if len(self.poses) == 0:
            raise EmptySequenceException()
        elif not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))

        return self.poses[pose_index]

    def get_pose_index_from_timestamp(self, timestamp, method="closest"):
        """Returns the closest pose index from the provided timestamp.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp: float
            A relative timestamp, in seconds.
        method: str, optional
            This parameter can take multiple values:

            • If set on ``"closest"`` (default), returns the closest pose index from the timestamp.
            • If set on ``"below"``, ``"lower"`` or ``"under"``, returns the closest pose index below the timestamp.
            • If set on ``"above"``, ``"higher"`` or ``"over"``, returns the closest pose index above the timestamp.

        Note
        ----
        If the provided timestamp matches exactly the timestamp of a pose from the sequence, the pose index is returned,
        and the parameter ``method`` is ignored.
        """

        if timestamp <= self.get_duration()/2:
            pose_index_before = 0
            pose_index_after = 0
            for pose_index in range(0, len(self.poses)):
                if self.poses[pose_index].relative_timestamp == timestamp:
                    return pose_index
                elif self.poses[pose_index].relative_timestamp < timestamp:
                    pose_index_before = pose_index
                    if pose_index != len(self.poses) - 1:
                        pose_index_after = pose_index + 1
                else:
                    break
        else:
            pose_index_before = len(self.poses)-1
            pose_index_after = len(self.poses)-1
            for pose_index in range(len(self.poses)-1, -1, -1):
                if self.poses[pose_index].relative_timestamp == timestamp:
                    return pose_index
                elif self.poses[pose_index].relative_timestamp > timestamp:
                    pose_index_after = pose_index
                    if pose_index != 0:
                        pose_index_before = pose_index - 1
                else:
                    break

        if method == "closest":
            if abs(timestamp - self.poses[pose_index_before].relative_timestamp) <= \
                    abs(timestamp - self.poses[pose_index_after].relative_timestamp):
                return pose_index_before
            else:
                return pose_index_after
        elif method in ["below", "lower", "under"]:
            return pose_index_before
        elif method in ["above", "higher", "over"]:
            return pose_index_after
        else:
            raise Exception('Invalid parameter "method": the value should be "lower", "higher" or "closest".')

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

            • If set on ``"closest"`` (default), returns the closest pose index from the timestamp.
            • If set on ``"below"``, ``"lower"`` or ``"under"``, returns the closest pose index below the timestamp.
            • If set on ``"above"``, ``"higher"`` or ``"over"``, returns the closest pose index above the timestamp.
        """
        return self.poses[self.get_pose_index_from_timestamp(timestamp, method)]

    def get_number_of_poses(self):
        """Returns the number of poses in the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of poses in the sequence.
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
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            List of the timestamps of all the poses of the sequence, in seconds.
        """

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

    def get_timestamps_for_metric(self, metric, relative=False, timestamp_start=None, timestamp_end=None):
        """Returns a list of the timestamps for every value of the metric provided, in seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        metric: str
            The metric of interest. Depending on this value, the returned timestamps will not be the same length.
            The value of ``metric`` can be either:

            • ``"x"``, for the values on the x axis (in meters); returns all the timestamps
            • ``"y"``, for the values on the y axis (in meters); returns all the timestamps
            • ``"z"``, for the values on the z axis (in meters); returns all the timestamps
            • ``"distance_hands"``, for the distance between the hands (in meters); returns all the timestamps
            • ``"distance"``, for the distance travelled (in meters); returns the timestamps except from the first
            • ``"distance_x"`` for the distance travelled on the x axis (in meters); returns the timestamps except
              from the first
            • ``"distance_y"`` for the distance travelled on the y axis (in meters); returns the timestamps except
              from the first
            • ``"distance_z"`` for the distance travelled on the z axis (in meters); returns the timestamps except
              from the first
            • ``"velocity"`` for the velocity (in meters per second); returns the timestamps except
              from the first
            • ``"acceleration"`` for the acceleration (in meters per second squared); returns the timestamps except
              from the two first ones
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared); returns the
              timestamps except from the two first ones

        relative: boolean
            Defines if the returned timestamps are relative to the first pose (in that case, the timestamp of the first
            pose will be 0), or the original timestamps.

        timestamp_start: float or None, optional
            If provided, the timestamps below this value will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the timestamps above this value will be ignored from the output.

        Returns
        -------
        list(float)
            List of the timestamps of the values described by the metric, in seconds.
        """

        if metric not in ["x", "y", "z", "distance_hands", "distance", "distance_x", "distance_y", "distance_z",
                          "velocity", "acceleration", "acceleration_abs"]:
            raise InvalidParameterValueException("metric", metric)

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        timestamps = []
        for p in range(len(self.poses)):
            pose = self.poses[p]
            if relative:
                t = pose.get_relative_timestamp()
            else:
                t = pose.get_timestamp()
            if timestamp_start <= t <= timestamp_end:
                if metric in ["distance", "distance_x", "distance_y", "distance_z", "velocity"] and p == 0:
                    pass
                elif metric in ["acceleration", "acceleration_abs"] and p in [0, 1]:
                    pass
                else:
                    timestamps.append(t)

        return timestamps

    def get_time_between_two_poses(self, pose_index1, pose_index2):
        """Returns the difference between the timestamps of two poses, in seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index1: int
            The index of the first pose.
        pose_index2: int
            The index of the second pose.

        Returns
        -------
        float
            The time difference (in seconds) between the two poses.

        Note
        ----
        If the index of the second pose is inferior to the index of the first pose, the difference will be negative.
        """
        timestamp1 = self.poses[pose_index1].relative_timestamp
        timestamp2 = self.poses[pose_index2].relative_timestamp
        return timestamp2 - timestamp1

    def get_duration(self):
        """Returns the duration of the sequence, in seconds.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The duration of the sequence, in seconds.
        """
        return self.poses[-1].relative_timestamp

    def get_framerates(self):
        """Returns a list of the frequencies of poses per second and a list of the matching timestamps. This function
        calculates, for each pose, the inverse of the time elapsed since the previous pose (in seconds), in order to
        obtain a list of framerates across time. It returns the list of framerates, and the corresponding timestamps
        (starting on the second pose).

        .. versionadded:: 2.0

        Returns
        -------
        list(float)
            Framerates for all the poses of the sequence, starting on the second pose.
        list(float)
            Timestamps of the sequence, starting on the second pose.

        Note
        ----
        Because the framerates are calculated by consecutive pairs of poses, the two lists returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """
        time_points = []
        framerates = []
        for p in range(1, len(self.poses) - 1):
            time_points.append(self.poses[p].relative_timestamp)
            framerate = 1 / (self.poses[p].relative_timestamp - self.poses[p - 1].relative_timestamp)
            framerates.append(framerate)

        return framerates, time_points

    def get_framerate(self):
        """Returns the number of poses per second of the sequence, only if this one is stable. If the frequency is
        variable, the function returns an error message.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The number of poses per second for the sequence if this number is stable.
        """
        framerates, _ = self.get_framerates()
        if framerates.count(framerates[0]) == len(framerates):
            return framerates[0]
        else:
            raise Exception("The framerate is variable, between " + str(self.get_min_framerate()) + " and " +
                            str(self.get_max_framerate()) + " poses per second (average " +
                            str(self.get_average_framerate()) + " poses per second.")

    def get_average_framerate(self):
        """Returns the average number of poses per second of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Average number of poses per second for the sequence.
        """
        average_frequency = (self.get_number_of_poses()-1) / self.get_duration()
        return average_frequency

    def get_min_framerate(self):
        """Returns the minimum frequency of poses per second of the sequence, which is equal to 1 over the maximum time
        between two poses in the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Minimum number of poses per second for the sequence.
        """
        framerates, time_points = self.get_framerates()
        return min(framerates)

    def get_max_framerate(self):
        """Returns the maximum frequency of poses per second of the sequence, which is equal to 1 over the minimum time
        between two poses in the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Maximum number of poses per second for the sequence.
        """
        framerates, time_points = self.get_framerates()
        return max(framerates)

    def get_joint_coordinate_as_list(self, joint_label, axis, timestamp_start=None, timestamp_end=None):
        """Returns a list of all the values for one specified axis of a specified joint label.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str
            The required axis (``"x"``, ``"y"`` or ``"z"``).
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A chronological list of the values (in meters) on one axis for the specified joint.

        Note
        ----
        The values returned by the function can be paired with the timestamps obtained with
        :meth:`Sequence.get_timestamps`.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)
        elif axis not in ["x", "y", "z"]:
            raise InvalidParameterValueException("axis", axis, ["x", "y", "z"])

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        values = []
        for p in range(len(self.poses)):
            if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
                values.append(self.poses[p].joints[joint_label].get_coordinate(axis))

        return values

    def get_joint_distance_as_list(self, joint_label, axis=None, timestamp_start=None, timestamp_end=None):
        """Returns a list of all the distances travelled for a specific joint. If an axis is specified, the distances
        are calculated on this axis only.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A chronological list of the distances travelled (in meters) for the specified joint.

        Note
        ----
        Because the velocities are calculated by consecutive poses, the list returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        values = []
        for p in range(1, len(self.poses)):
            if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
                values.append(calculate_distance(self.poses[p - 1].joints[joint_label],
                                                 self.poses[p].joints[joint_label], axis))
        return values

    def get_joint_velocity_as_list(self, joint_label, timestamp_start=None, timestamp_end=None):
        """Returns a list of all the velocities (distance travelled over time) for a specified joint.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A chronological list of the velocities (in meters per second) for the specified joint.

        Note
        ----
        Because the velocities are calculated by consecutive poses, the list returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        values = []
        for p in range(1, len(self.poses)):
            if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
                values.append(calculate_velocity(self.poses[p - 1], self.poses[p], joint_label))
        return values

    def get_joint_acceleration_as_list(self, joint_label, absolute=False, timestamp_start=None, timestamp_end=None):
        """Returns a list of all the accelerations (differences of velocity over time) for a specified joint.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration value. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A chronological list of the accelerations (in meters per second squared) for the specified joint.

        Note
        ----
        Because the accelerations are calculated by consecutive pairs of poses, the list returned by the function
        have a length of :math:`n-2`, with :math:`n` being the number of poses of the sequence.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        values = []
        for p in range(2, len(self.poses)):
            if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
                value = calculate_acceleration(self.poses[p - 2], self.poses[p - 1], self.poses[p], joint_label)
                if absolute:
                    values.append(abs(value))
                else:
                    values.append(value)
        return values

    def get_joint_metric_as_list(self, joint_label, time_series="velocity", timestamp_start=None, timestamp_end=None):
        """For a specified joint, returns a list containing one of its time series (x coordinate, y coordinate,
        z coordinate, distance travelled, velocity, or acceleration).

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        time_series: str, optional
            Defines the time_series to return to the list. This parameter can be:

            • ``"x"``, ``"y"`` or ``"z"``, to return the values of the coordinate on a specified axis, for each
              timestamp.
            • The ``"distance"`` travelled over time (in meters), between consecutive poses.
            • The ``"distance_x"``, ``"distance_y"`` or ``"distance_z"`` travelled over time on one axis (in meters),
              between consecutive poses.
            • The ``"velocity"``, defined by the distance travelled over time (in meters per second), between
              consecutive poses.
            • The ``"acceleration"``, defined by the velocity over time (in meters per second squared), between
              consecutive pairs of poses. ``"acceleration_abs"`` returns absolute values.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A chronological list of the velocities (in meters per second) for the specified joint.

        Note
        ----
        Because the distances and velocities are calculated by consecutive poses, the list returned by the
        function have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        Following the same idea, accelerations are calculate by consecutive pairs of poses. The list returned by the
        function would then have a length of :math:`n-2`.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if time_series in ["x", "y", "z"]:
            return self.get_joint_coordinate_as_list(joint_label, time_series, timestamp_start, timestamp_end)
        elif time_series == "distance":
            return self.get_joint_distance_as_list(joint_label, None, timestamp_start, timestamp_end)
        elif time_series.startswith("distance"):
            return self.get_joint_distance_as_list(joint_label, time_series[9:10], timestamp_start, timestamp_end)
        elif time_series == "velocity":
            return self.get_joint_velocity_as_list(joint_label, timestamp_start, timestamp_end)
        elif time_series == "acceleration":
            return self.get_joint_acceleration_as_list(joint_label, False, timestamp_start, timestamp_end)
        elif time_series == "acceleration_abs":
            return self.get_joint_acceleration_as_list(joint_label, True, timestamp_start, timestamp_end)
        else:
            raise InvalidParameterValueException("time_series", time_series, ["x", "y", "z", "distance", "distance_x",
                                                                              "distance_y", "distance_z", "velocity",
                                                                              "acceleration"])

    def get_single_coordinates(self, axis, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the values of the coordinates on a single axis for all the joints. The
        dictionary will contain the joints labels as keys, and a list of coordinates as values. The coordinates are
        returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str
            The axis from which to extract the coordinate: ``"x"``, ``"y"`` or ``"z"``.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and coordinates values on a specified axis as values (in meters),
            ordered chronologically.
        """

        dict_coordinates = OrderedDict()

        for joint_label in self.get_joint_labels():
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_coordinates[joint_label] = self.get_joint_coordinate_as_list(joint_label, axis,
                                                                              timestamp_start, timestamp_end)

        return dict_coordinates

    def get_distances(self, axis=None, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the joint labels as keys, and a list of distances (distance travelled between
        two poses) as values. Distances are calculated using the :func:`tool_functions.calculate_distance()` function,
        and are defined by the distance travelled between two poses (in meters). The distances are returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and lists of distances travelled as values (in meters), ordered
            chronologically.

        Note
        ----
        Because the distances are calculated between consecutive poses, the lists returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """

        dict_distances = OrderedDict()

        for joint_label in self.get_joint_labels():
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_distances[joint_label] = self.get_joint_distance_as_list(joint_label, axis,
                                                                          timestamp_start, timestamp_end)

        return dict_distances

    def get_distance_between_hands(self, timestamp_start=None, timestamp_end=None):
        """Returns a vector containing the distance (in meters) between the two hands across time. If the
        joint label system is Kinect, the distance will be calculated between ``"HandRight"`` and ``"HandLeft"``.
        If the joint label system is Qualisys, the distance will be calculated between ``"HandOutRight"`` and
        ``"HandOutLeft"``.

        .. versionadded:: 2.0

        Note
        ----
        This function is a wrapper for the function :meth:`Sequence.get_distance_between_joints`.

        Parameters
        ----------
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A list of distances between the two hands, in meters.
        """
        labels = self.get_joint_labels()
        if "HandRight" in labels:
            return self.get_distance_between_joints("HandRight", "HandLeft", timestamp_start, timestamp_end)
        elif "HandOutRight" in labels:
            return self.get_distance_between_joints("HandOutRight", "HandOutLeft", timestamp_start, timestamp_end)
        else:
            raise Exception("The Sequence does not contain valid hand joint labels.")

    def get_distance_between_joints(self, joint_label1, joint_label2, timestamp_start=None, timestamp_end=None):
        """Returns a vector containing the distance (in meters) between the two joints provided across time.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label1: str
            The label of the first joint (e.g., ``"Head"``).
        joint_label2: str
            The label of the second joint (e.g., ``"FootRight"``).
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A list of distances between the two specified joints, in meters.
        """
        labels = self.get_joint_labels()

        if joint_label1 not in labels:
            raise InvalidJointLabelException(joint_label1)
        if joint_label2 not in labels:
            raise InvalidJointLabelException(joint_label2)

        distances = []
        for p in self.poses:
            if timestamp_start < p.get_timestamp() < timestamp_end:
                distances.append(calculate_distance(p.get_joint(joint_label1), p.get_joint(joint_label2)))

        return distances

    def get_velocities(self, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the joint labels as keys, and a list of velocities (distance travelled over
        time between two poses) as values. Velocities are calculated using the
        :func:`tool_functions.calculate_velocity()` function, and are defined by the distance travelled between two
        poses (in meters), divided by the time elapsed between these two poses (in seconds). The velocities are
        returned in meters per second.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and lists of velocity as values (in meters per second), ordered
            chronologically.

        Note
        ----
        Because the velocities are calculated between consecutive poses, the lists returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """

        dict_velocities = OrderedDict()

        for joint_label in self.get_joint_labels():
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_velocities[joint_label] = self.get_joint_velocity_as_list(joint_label, timestamp_start, timestamp_end)

        return dict_velocities

    def get_accelerations(self, absolute=False, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the joint labels as keys, and a list of accelerations (differences of
        velocity over time between two poses) as values. Accelerations are calculated using the
        :func:`tool_functions.calculate_acceleration()` function, and are defined by the difference of velocity between
        two consecutive pairs of poses (in meters per second), divided by the time elapsed between these last pose of
        each pair (in seconds). The accelerations are returned in meters per second squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        absolute: boolean, optional
            If set on ``True``, returns the absolute acceleration values. If set on ``False`` (default), returns
            the original, signed acceleration values.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and lists of accelerations as values (in meters per second squared),
            ordered chronologically.

        Note
        ----
        Because the accelerations are calculated between consecutive pairs of poses, the lists returned by the function
        have a length of :math:`n-2`, with :math:`n` being the number of poses of the sequence.
        """

        dict_accelerations = OrderedDict()

        for joint_label in self.get_joint_labels():
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_accelerations[joint_label] = self.get_joint_acceleration_as_list(joint_label, absolute,
                                                                                  timestamp_start, timestamp_end)

        return dict_accelerations

    def get_time_series_as_list(self, metric, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing one of the metrics for all joints: coordinate, distance travelled, velocity
        or acceleration.

        .. versionadded:: 2.0

        Parameters
        ----------
        metric: str
            The metric to be returned, can be either:

            • ``"x"``, for the values on the x axis (in meters)
            • ``"y"``, for the values on the y axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters)
            • ``"distance_x"`` for the distance travelled on the x axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and the specified metric as a value.

        Note
        ----
        Because the distances and velocities are calculated between consecutive poses (apart from distance_hands), the
        lists returned by the function have a length of :math:`n-1`, with :math:`n` being the number of poses of the
        sequence. For accelerations, the lists returned have a length of :math:`n-2`.
        """
        if metric in ["x", "y", "z"]:
            return self.get_single_coordinates(metric, timestamp_start, timestamp_end, verbosity)
        elif metric == "distance":
            return self.get_distances(None, timestamp_start, timestamp_end, verbosity)
        elif metric == "distance_hands":
            return self.get_distance_between_hands(timestamp_start, timestamp_end)
        elif metric.startswith("distance"):
            return self.get_distances(metric[-2:], timestamp_start, timestamp_end, verbosity)
        elif metric == "velocity":
            return self.get_velocities(timestamp_start, timestamp_end, verbosity)
        elif metric == "acceleration":
            return self.get_accelerations(False, timestamp_start, timestamp_end, verbosity)
        elif metric == "acceleration_abs":
            return self.get_accelerations(True, timestamp_start, timestamp_end, verbosity)
        else:
            raise InvalidParameterValueException("metric", metric)

    def get_max_distance_whole_sequence(self, axis=None):
        """Returns the single maximum value of the distance travelled between two poses across every joint of the
        sequence. The distances are first calculated using the :meth:`Sequence.get_distances()` function. The distance
        travelled by a joint is returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        --------
        float
            Maximum value of the distance travelled between two poses across every joint of the sequence, in meters.
        """
        dict_distances = self.get_distances(axis)
        max_distance_whole_sequence = 0

        for joint_label in dict_distances.keys():
            local_maximum = max(dict_distances[joint_label])
            if local_maximum > max_distance_whole_sequence:
                max_distance_whole_sequence = local_maximum

        return max_distance_whole_sequence

    def get_max_velocity_whole_sequence(self):
        """Returns the single maximum value of the velocity across every joint of the sequence. The velocities are
        first calculated using the :meth:`Sequence.get_velocities()` function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocity is returned in meters per second.

        .. versionadded:: 2.0

        Returns
        --------
        float
            Maximum value of the velocity across every joint of the sequence, in meters per second.
        """
        dict_velocities = self.get_velocities()
        max_velocity_whole_sequence = 0

        for joint_label in dict_velocities.keys():
            local_maximum = max(dict_velocities[joint_label])
            if local_maximum > max_velocity_whole_sequence:
                max_velocity_whole_sequence = local_maximum

        return max_velocity_whole_sequence

    def get_max_acceleration_whole_sequence(self, absolute=True):
        """Returns the single maximum value of the acceleration across every joint of the sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_accelerations()` function. The acceleration is defined
        by the difference of velocity between two consecutive pairs of poses (in meters per second), divided by the time
        elapsed between these last pose of each pair (in seconds). The accelerations are returned in meters per second
        squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration value. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.

        Returns
        -------
        float
            Maximum value of the velocity across every joint of the sequence, in meters per second.
        """
        dict_accelerations = self.get_accelerations(absolute)
        max_acceleration_whole_sequence = 0

        for joint_label in dict_accelerations.keys():
            local_maximum = max(dict_accelerations[joint_label])
            if local_maximum > max_acceleration_whole_sequence:
                max_acceleration_whole_sequence = local_maximum

        return max_acceleration_whole_sequence

    def get_max_distance_single_joint(self, joint_label, axis=None):
        """Returns the maximum value of the distance travelled between two poses for a given joint, across the whole
        sequence. The distances are first calculated using the :meth:`Sequence.get_distances()` function. The distance
        travelled by a joint between two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        --------
        float
            Maximum value of the distance travelled for a given joint between two poses, in meters.
        """
        dict_distances = self.get_distances(axis)

        if joint_label not in dict_distances.keys():
            raise InvalidJointLabelException(joint_label)

        return max(dict_distances[joint_label])

    def get_max_velocity_single_joint(self, joint_label):
        """Returns the maximum value of the velocity for a given joint, across the whole sequence. The velocities are
        first calculated using the :meth:`Sequence.get_velocities()` function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocity is returned in meters per second.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        --------
        float
            Maximum value of the velocity for a given joint, in meters per second.
        """
        dict_velocities = self.get_velocities()

        if joint_label not in dict_velocities.keys():
            raise InvalidJointLabelException(joint_label)

        return max(dict_velocities[joint_label])

    def get_max_acceleration_single_joint(self, joint_label, absolute=True):
        """Returns the maximum value of the acceleration for a given joint, across the whole sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_accelerations()` function. The acceleration is defined
        by the difference of velocity between two consecutive pairs of poses (in meters per second), divided by the time
        elapsed between these last pose of each pair (in seconds). The accelerations are returned in meters per second
        squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration value. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.

        Returns
        -------
        float
            Maximum value of the acceleration for a given joint, in meters per second squared.
        """
        dict_accelerations = self.get_accelerations(absolute)

        if joint_label not in dict_accelerations.keys():
            raise InvalidJointLabelException(joint_label)

        return max(dict_accelerations[joint_label])

    def get_max_distance_per_joint(self, axis=None):
        """Returns the maximum value of the distance travelled between two poses for each joint of the sequence. The
        distances are first calculated using the :meth:`Sequence.get_distances()` function. The distance
        travelled by a joint between two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and maximum velocities as values (in meters per second).
        """
        dict_distances = self.get_distances(axis)
        max_distance_per_joint = OrderedDict()

        for joint_label in dict_distances.keys():
            max_distance_per_joint[joint_label] = max(dict_distances[joint_label])

        return max_distance_per_joint

    def get_max_velocity_per_joint(self):
        """Returns the maximum value of the velocity for each joint of the sequence. The velocities are
        first calculated using the :meth:`Sequence.get_velocities()` function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocities are returned in meters per second.

        .. versionadded:: 2.0

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and maximum velocities as values (in meters per second).
        """
        dict_velocities = self.get_velocities()
        max_velocity_per_joint = OrderedDict()

        for joint_label in self.get_joint_labels():
            max_velocity_per_joint[joint_label] = max(dict_velocities[joint_label])

        return max_velocity_per_joint

    def get_max_acceleration_per_joint(self, absolute=True):
        """Returns the maximum value of the acceleration for each joint of the sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_accelerations()` function. The acceleration is defined
        by the difference of velocity between two consecutive pairs of poses (in meters per second), divided by the time
        elapsed between these last pose of each pair (in seconds). The accelerations are returned in meters per second
        squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration values. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and maximum accelerations as values (in meters per second squared).
        """
        max_acceleration_per_joint = OrderedDict()

        for joint_label in self.get_joint_labels():
            max_acceleration_per_joint[joint_label] = self.get_max_acceleration_single_joint(joint_label, absolute)

        return max_acceleration_per_joint

    def get_total_distance_whole_sequence(self, axis=None):
        """Returns the sum of the distances travelled by every joint across all the poses of the sequence. This allows
        to provide a value representative of the global “quantity of movement” produced during the sequence. The
        distances are first calculated using the Sequence.get_distances() function. The distance travelled by a joint
        between two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        -------
        float
            Sum of the distances travelled across every joint and poses of the sequence, in meters.
        """
        total_distance_whole_sequence = 0
        dict_distances = self.get_distances(axis)

        for joint_label in dict_distances.keys():
            total_distance_whole_sequence += sum(dict_distances[joint_label])

        return total_distance_whole_sequence

    def get_total_velocity_whole_sequence(self):
        """Returns the sum of the velocities of every joint across all the poses of the sequence. This allows to
        provide a value representative of the global "quantity of movement" produced during the sequence. The
        velocities are first calculated using the Sequence.get_velocities() function. The velocity of a joint is
        defined by the distance travelled between two poses (in meters), divided by the time elapsed between these
        two poses (in seconds). The velocities are returned in meters per second.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Sum of the velocities across every joint and poses of the sequence, in meters per second.
        """
        total_velocity_whole_sequence = 0
        dict_velocities = self.get_velocities()

        for joint_label in dict_velocities.keys():
            total_velocity_whole_sequence += sum(dict_velocities[joint_label])

        return total_velocity_whole_sequence

    def get_total_acceleration_whole_sequence(self):
        """Returns the sum of the absolute accelerations of every joint across all the poses of the sequence. This
        allows to provide a value representative of the global "quantity of movement" produced during the sequence. The
        acceleration values are first calculated using the :meth:`Sequence.get_accelerations()` function. The
        acceleration is defined by the difference of velocity between two consecutive pairs of poses (in meters per
        second), divided by the time elapsed between these last pose of each pair (in seconds). The accelerations are
        returned in meters per second squared.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Sum of the accelerations across every joint and poses of the sequence, in meters per second squared.
        """
        total_acceleration_whole_sequence = 0
        dict_accelerations = self.get_accelerations(absolute=True)

        for joint_label in dict_accelerations.keys():
            total_acceleration_whole_sequence += sum(dict_accelerations[joint_label])

        return total_acceleration_whole_sequence

    def get_total_distance_single_joint(self, joint_label, axis=None):
        """Returns the total distance travelled for a given joint, across the whole sequence. The distances are first
        calculated using the Sequence.get_joint_distance_as_list() function. The distance travelled by a joint between
        two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        --------
        float
            Sum of the distances travelled across all poses for a single joint, in meters.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        return sum(self.get_joint_distance_as_list(joint_label, axis))

    def get_total_velocity_single_joint(self, joint_label):
        """Returns the sum of the velocities for a given joint, across the whole sequence. The velocities are first
        calculated using the Sequence.get_joint_velocity_as_list() function. The velocity of a joint is defined by the
        distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocity is returned in meters per second.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        --------
        float
            Sum of the velocities across all poses for a single joint, in meters per second.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        return sum(self.get_joint_velocity_as_list(joint_label))

    def get_total_acceleration_single_joint(self, joint_label):
        """Returns the sum of the absolute accelerations for a given joint, across the whole sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_joint_acceleration_as_list()` function. The
        acceleration is defined by the difference of velocity between two consecutive pairs of poses (in meters per
        second), divided by the time elapsed between these last pose of each pair (in seconds). The accelerations are
        returned in meters per second squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        --------
        float
            Sum of the accelerations across all poses for a single joint, in meters per second squared.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        return sum(self.get_joint_acceleration_as_list(joint_label, absolute=True))

    def get_total_distance_per_joint(self, axis=None):
        """Returns the sum of the distances travelled for each individual joint of the sequence. The distances are first
        calculated using the Sequence.get_total_distance_single_joint() function. The distance travelled between two
        poses of a joint is returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and sum of distances travelled across all poses as values (in meters).
        """
        total_distance_per_joint = OrderedDict()

        for joint_label in self.poses[0].joints.keys():
            total_distance_per_joint[joint_label] = self.get_total_distance_single_joint(joint_label, axis)

        return total_distance_per_joint

    def get_total_velocity_per_joint(self):
        """Returns the sum of the velocities for each individual joint of the sequence. The velocities are first
        calculated using the Sequence.get_total_velocity_single_joint() function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses (in
        seconds). The velocities are returned in meters per second.

        .. versionadded:: 2.0

        Returns
        ----------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and sum of velocities across all poses as values (in meters per
            second).
        """
        total_velocity_per_joint = OrderedDict()

        for joint_label in self.poses[0].joints.keys():
            total_velocity_per_joint[joint_label] = self.get_total_velocity_single_joint(joint_label)

        return total_velocity_per_joint

    def get_total_acceleration_per_joint(self):
        """Returns the sum of the absolute acceleration values for each individual joint of the sequence. The
        acceleration values are first calculated using the :meth:`Sequence.get_joint_acceleration_as_list()` function.
        The acceleration is defined by the difference of velocity between two consecutive pairs of poses (in meters per
        second), divided by the time elapsed between these last pose of each pair (in seconds). The accelerations are
        returned in meters per second squared.

        .. versionadded:: 2.0

        Returns
        ----------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and sum of absolute acceleration values across all poses as values
            (in meters per second squared).
        """
        total_velocity_per_joint = OrderedDict()

        for joint_label in self.poses[0].joints.keys():
            total_velocity_per_joint[joint_label] = self.get_total_velocity_single_joint(joint_label)

        return total_velocity_per_joint

    # === Correction functions ===

    def correct_jitter(self, velocity_threshold, window, window_unit="poses", method="default", name=None, verbosity=1):
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
                • If set on ``"old"``, the movement is corrected the same way as for default, but the method to check
                  the velocity threshold is based on an old, incorrect version of the algorithm. This option is
                  deprecated and has only been left there for version 2.0 for retro-compatibility and comparisons with
                  old, processed files. This method will be removed in an ulterior release.
                • This parameter also allows for all the values accepted for the ``kind`` parameter in the function
                  :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
                  ``"slinear"``, ``"quadratic"``, ``"cubic"``”, ``"previous"``, and ``"next"``. See the `documentation
                  for this Python module
                  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.
                  In case one of these values is used, all the corrected joints are first set to (0, 0, 0) by the
                  function, before calling the :meth:`Sequence.correct_zeros()` function to interpolate the missing
                  values.

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
        """

        dict_joints_to_correct = {}
        for key in self.poses[0].joints.keys():
            dict_joints_to_correct[key] = []

        if verbosity > 0:
            print("Correcting jumps and twitches...", end=" ")

        # Create an empty sequence, the same length in poses as the original, just keeping the timestamp information
        # for each pose.
        new_sequence = self._create_new_sequence_with_timestamps(verbosity)
        if name is None:
            new_sequence.name = self.name + " +CJ"
        else:
            new_sequence.name = name
        new_sequence.path = self.path

        # If verbosity, show all the information. Else, show only the progress in percentage.
        if verbosity > 0:
            if method in ["old", "default"]:
                print("\tPerforming realignment...", end=" ")
            else:
                print("\tDetecting jumps and twitches...", end=" ")

        # If the window unit is defined in ms, we convert it to s.
        if window_unit == "ms":
            window /= 1000
            window_unit = "s"

        # Define the counters
        realigned_points = 0
        jumps = 0
        twitches = 0
        perc = 10

        # For every pose starting on the second one
        for p in range(1, len(self.poses)):

            if verbosity > 1:
                print("\nNew sequence:\n" + str(new_sequence.poses[p - 1]))
                print("\n== POSE NUMBER " + str(p + 1) + " ==")

            perc = show_progression(verbosity, p, len(self.poses), perc)

            # If the window unit is defined in seconds, we calculate how many poses that is.
            if window_unit == "s":
                if verbosity > 1:
                    print("Calculating number of poses in the window...", end=" ")

                window_effective = 0
                time_diff = 0
                previous_time_diff = 0

                # Get window length in poses
                for i in range(p, len(self.poses)):
                    window_effective = i - p
                    time_diff = self.get_time_between_two_poses(p, i)
                    if time_diff >= window:
                        break
                    previous_time_diff = time_diff

                # We get the closest window from the target
                if p + window_effective != len(self.poses) - 1:
                    if abs(window - previous_time_diff) < abs(window - time_diff):
                        window_effective -= 1

                if verbosity > 1:
                    print("Window size: " + str(window_effective) + " (" + str(time_diff) + " s).")

            else:
                window_effective = window

            # For every joint
            for joint_label in self.poses[0].joints.keys():

                # We get the m/s travelled by the joint between this pose and the previous
                velocity_before = calculate_velocity(new_sequence.poses[p - 1], self.poses[p], joint_label)

                if verbosity > 1:
                    print(joint_label + ": " + str(velocity_before))

                # If we already corrected this joint, we ignore it to avoid overcorrection
                if joint_label in new_sequence.poses[p].joints:

                    if verbosity > 1:
                        print("\tAlready corrected.")

                # If the velocity is over threshold, we check if it is a jump or a twitch
                elif velocity_before > velocity_threshold and p != len(self.poses) - 1:

                    if verbosity > 1:
                        print("\tVelocity over threshold between poses " + str(p) + " and " + str(p + 1) + ".", end=" ")

                    self.poses[p].joints[joint_label]._set_has_velocity_over_threshold(True)

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
                        for k in range(p, min(p + window_effective, len(self.poses))):

                            if verbosity > 1:
                                print("\t\tPose " + str(k + 1) + ":", end=" ")

                            # Method 1 (original): get the subsequent velocities
                            if method == "old":
                                velocity = calculate_velocity(new_sequence.poses[p - 1], self.poses[k], joint_label)

                            # Method 2 (to test): get the distance over the time between the two first joints
                            else:
                                dist = calculate_distance(new_sequence.poses[p - 1].joints[joint_label],
                                                          self.poses[k].joints[joint_label])
                                delay = calculate_delay(new_sequence.poses[p - 1], new_sequence.poses[p])
                                velocity = dist / delay

                            # Twitch case: One of the poses of the window is below threshold compared to previous pose.
                            if velocity < velocity_threshold:

                                if verbosity > 1:
                                    print("velocity back under threshold defined by pose " + str(p) + ".")
                                    print("\t\t\tCorrecting for twitch...")

                                new_sequence, realigned_points = \
                                    self._correct_jitter_window(new_sequence, p - 1, k, joint_label, realigned_points,
                                                                verbosity)

                                if method not in ["old", "default"]:
                                    for i in range(p, k):
                                        dict_joints_to_correct[joint_label].append(i)

                                twitches += 1

                                break

                            # Jump case: No pose of the window is below threshold.
                            if k == p + window_effective - 1 or k == len(self.poses) - 1:

                                if verbosity > 1:
                                    print("velocity still over threshold at the end of the window.")
                                    print("\t\t\tCorrecting for jump...")

                                new_sequence, realigned_points = \
                                    self._correct_jitter_window(new_sequence, p - 1, k, joint_label, realigned_points,
                                                                verbosity)

                                if method not in ["old", "default"]:
                                    for i in range(p, k):
                                        dict_joints_to_correct[joint_label].append(i)

                                jumps += 1

                                break

                            # Wait: if there are still poses in the window, we continue.
                            else:

                                if verbosity > 1:
                                    print("still over threshold.")

                    if verbosity > 1:
                        print("")

                # If we're still in threshold, there is no correction, we copy the joint
                else:

                    joint = self.copy_joint(p, joint_label)
                    new_sequence.poses[p].add_joint(joint_label, joint)
                    new_sequence.poses[p].joints[joint_label]._is_corrected = False

        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

        if verbosity > 0:
            print("100% - Done.")

        # If we use one of the interpolation methods, we call the correct_zeros function
        if method not in ["old", "default"]:

            if verbosity > 0:
                print("\t" + str(realigned_points) + " point(s) with twitches and jumps detected.")
                print("\tSetting faulty joints to (0, 0, 0)...", end=" ")

            for joint_label in dict_joints_to_correct:
                for p in dict_joints_to_correct[joint_label]:
                    new_sequence.poses[p].joints[joint_label].set_to_zero()

            if verbosity > 0:
                print("100% - Done.")
                print("\tInterpolation of the data of the joints set to (0, 0, 0)...")

            new_sequence = new_sequence.correct_zeros(mode=method, name=name, verbosity=verbosity, add_tabs=2)

        if verbosity > 0:
            percentage = round((realigned_points / (len(self.poses) * len(list(self.poses[0].joints.keys())))) * 100, 1)
            print("De-jittering over. " + str(realigned_points) + " point(s) corrected over " + str(
                len(self.poses) * len(list(self.poses[0].joints.keys()))) + " (" + str(percentage) + "%).")
            print(str(jumps) + " jump(s) and " + str(twitches) + " twitch(es) corrected.\n")

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

        # We extract the data from the joints at the beginning and at the end of the partial sequence to correct
        joint_before = new_sequence.poses[start_pose_index].joints[joint_label]
        joint_after = self.poses[end_pose_index].joints[joint_label]

        # If the starting and ending joint are the same, we don't correct, it means it is the last pose of the sequence
        if start_pose_index == end_pose_index:
            joint = self.copy_joint(start_pose_index, joint_label)
            new_sequence.poses[start_pose_index + 1].add_joint(joint_label, joint)

            if verbosity > 1:
                print("\t\t\t\tDid not correct joint " + str(start_pose_index + 1) +
                      " as the window is of size 0 or the joint is the last pose of the sequence.")

        elif start_pose_index == end_pose_index - 1:
            joint = self.copy_joint(start_pose_index, joint_label)
            new_sequence.poses[start_pose_index + 1].add_joint(joint_label, joint)

            if verbosity > 1:
                print("\t\t\t\tDid not correct joint " + str(start_pose_index + 1) +
                      " as the window is of size 1.")

        # Otherwise we correct for all the intermediate joints
        for pose_number in range(start_pose_index + 1, end_pose_index):

            # If a joint was already corrected we don't correct it to avoid overcorrection
            if self.poses[pose_number].joints[joint_label]._is_corrected:

                if verbosity > 1:
                    print("\t\t\t\tDid not correct joint " + str(pose_number + 1) + " as it was already corrected.")

            # Otherwise we correct it
            else:

                x, y, z = self._correct_jitter_single_joint(joint_before, joint_after, start_pose_index, pose_number,
                                                            end_pose_index, verbosity)

                # We copy the original joint, apply the new coordinates and add it to the new sequence
                joint = self.copy_joint(pose_number, joint_label)
                joint._correct_joint(x, y, z)
                new_sequence.poses[pose_number].add_joint(joint_label, joint)

                if verbosity > 1:
                    print("\t\t\t\tCorrecting joint: " + str(pose_number + 1) + ". Original coordinates: (" + str(
                        self.poses[pose_number].joints[joint_label].x) +
                          ", " + str(self.poses[pose_number].joints[joint_label].y) + ", " + str(
                        self.poses[pose_number].joints[joint_label].z) + ")")
                    print("\t\t\t\tPrevious joint: " + str(start_pose_index + 1) + ". (" + str(
                        new_sequence.poses[start_pose_index].joints[joint_label].x) +
                          ", " + str(new_sequence.poses[start_pose_index].joints[joint_label].y) + ", " + str(
                        new_sequence.poses[start_pose_index].joints[joint_label].z) + ")")
                    print("\t\t\t\tNext joint: " + str(end_pose_index + 1) + ". (" + str(
                        self.poses[end_pose_index].joints[joint_label].x) +
                          ", " + str(self.poses[end_pose_index].joints[joint_label].y) + ", " + str(
                        self.poses[end_pose_index].joints[joint_label].z) + ")")
                    print("\t\t\t\tCorrected joint " + str(pose_number + 1) + ". New coordinates: (" + str(
                        x) + ", " + str(y) + ", " + str(z) + ")\n")

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
            print("\t\t\t\tJoint " + str(pose_index_current + 1) + " positioned at " + str(
                percentage_time * 100) + " % between poses " + str(pose_index_before + 1) + " and " + str(
                pose_index_after + 1) + ".")

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
        """

        if reference_joint_label == "auto":
            joints_labels = self.poses[0].joints.keys()
            if "SpineMid" in joints_labels:
                reference_joint_label = "SpineMid"
            elif "Chest" in joints_labels:
                reference_joint_label = "Chest"
            else:
                raise Exception("Automatic reference joint finder failed. Please enter a valid joint label as a " +
                                "reference joint.")

        if verbosity > 0:
            print("Re-referencing to " + str(reference_joint_label) + "...", end=" ")

        # Create an empty sequence, the same length in poses as the original, just keeping the timestamp information
        # for each pose.
        new_sequence = Sequence(None)
        if name is None:
            new_sequence.name = self.name + " +RF"
        else:
            new_sequence.name = name
        new_sequence.path = self.path

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
                joint = self.copy_joint(p, joint_label)
                joint._correct_joint(new_x, new_y, new_z)
                new_sequence.poses[p].add_joint(joint_label, joint)

                if verbosity > 1:
                    print(joint_label + ": ")
                    print("X: " + str(self.poses[p].joints[joint_label].x) + " -> " + str(new_x))
                    print("Y: " + str(self.poses[p].joints[joint_label].y) + " -> " + str(new_y))
                    print("Z: " + str(self.poses[p].joints[joint_label].z) + " -> " + str(new_z))

        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

        if verbosity > 0:
            print("100% - Done.")
            print("Re-referencing over.\n")
        return new_sequence

    def trim(self, start=None, end=None, use_relative_timestamps=False, name=None, verbosity=1, add_tabs=0):
        """Trims a sequence according to a starting timestamp (by default the beginning of the original sequence) and
        an ending timestamp (by default the end of the original sequence). Timestamps must be provided in seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        start: int or None, optional
            The timestamp after which the poses will be preserved. If set on ``None``, the beginning of the sequence
            will be set as the timestamp of the first pose.

        end: int or None, optional
            The timestamp before which the poses will be preserved. If set on ``None``, the end of the sequence will be
            set as the timestamp of the last pose.

        use_relative_timestamps: bool, optional
            Defines if the timestamps ``start`` and ``end`` refer to the original timestamps or the relative timestamps.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+TR"``.

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
        elif start < self.poses[0].timestamp and not use_relative_timestamps:
            raise Exception("Starting timestamp (" + str(start) + ") lower than the first timestamp of the sequence (" +
                            str(self.poses[0].timestamp) + ").")
        elif start < 0 and use_relative_timestamps:
            raise Exception("Starting timestamp (" + str(start) + ") must be equal to or higher than 0.")
        elif end > self.poses[-1].timestamp and not use_relative_timestamps:
            raise Exception("Ending timestamp (" + str(end) + ") exceeds last timestamp of the sequence (" +
                            str(self.poses[-1].timestamp) + ").")
        elif end > self.get_duration() and use_relative_timestamps:
            raise Exception("Ending timestamp (" + str(end) + ") exceeds the duration of the sequence (" +
                            str(self.get_duration()) + ").")

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
        new_sequence.path = self.path

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
                pose = self.copy_pose(p)
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

        return new_sequence

    def trim_to_audio(self, delay=0, audio=None, name=None, verbosity=1):
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
        """

        if audio is None:
            if self.path_audio is None:
                raise Exception("No audio path defined in the sequence, please specify one.")
            audio = Audio(self.path_audio, name=self.path_audio)

        if type(audio) is str:
            audio = Audio(audio, name=audio)

        if verbosity > 0:
            print("Trimming the sequence according to the duration of an audio file...")
            print("\tParameters:")
            print("\t\tSequence duration: " + str(self.get_duration()) + " s.")
            print("\t\tAudio duration: " + str(audio.duration) + " s.")

        if audio.duration > self.get_duration():
            print("\n\tSequence duration: " + str(self.get_duration()))
            print("\tAudio duration: " + str(audio.duration))
            raise Exception("Error: The duration of the audio exceeds the duration of the sequence.")
        elif verbosity > 0:
            print("\t\tMoving the beginning by a delay of " + str(delay) + " s.")
            print("\t\tIgnoring " + str(round(self.get_duration() - audio.duration - delay, 2)) +
                  " s at the end of the sequence.")

        new_sequence = self.trim(delay, audio.duration + delay, True, name, verbosity, 1)

        if abs(audio.duration - new_sequence.get_duration()) > 1:
            raise Exception("The duration of the audio is different of more than one second with the duration of the " +
                            "new sequence.")

        return new_sequence

    def resample(self, frequency, mode="cubic", name=None, verbosity=1):
        """Resamples a sequence with a constant or variable framerate to the `frequency` parameter. It first creates
        a new set of timestamps at the desired frequency, and then interpolates the original data to the new timestamps.

        .. versionadded:: 2.0

        Parameters
        ----------
        frequency: float
            The frequency, in hertz, at which you want to resample the sequence. A frequency of 4 will return resample
            joints at 0.25 s intervals.

        mode: str, optional
            This parameter also allows for all the values accepted for the ``kind`` parameter in the function
            :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
            ``"slinear"``, ``"quadratic"``, ``"cubic"``”, ``"previous"``, and ``"next"``. See the `documentation
            for this Python module
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.

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
        """

        if verbosity > 0:
            print("Resampling the sequence at " + str(frequency) + " Hz (mode: " + str(mode) + ")...")
            print("\tOriginal framerate: ")
            print("\t\tAverage: " + str(round(self.get_average_framerate(), 2)), end=" · ")
            print("Min: " + str(round(self.get_min_framerate(), 2)), end=" · ")
            print("Max: " + str(round(self.get_max_framerate(), 2)))
            print("\tCreating vectors...", end=" ")

        # Create an empty sequence
        new_sequence = Sequence(None)
        if name is None:
            new_sequence.name = self.name + " +RS" + str(frequency)
        else:
            new_sequence.name = name
        new_sequence.path = self.path

        # Define the percentage counter
        perc = 10

        # Define positions lists
        x_points = OrderedDict()
        y_points = OrderedDict()
        z_points = OrderedDict()
        time_points = []

        # Create vectors of position and time
        for p in range(len(self.poses)):

            perc = show_progression(verbosity, p, len(self.poses), perc)

            for j in self.poses[p].joints.keys():
                if p == 0:
                    x_points[j] = []
                    y_points[j] = []
                    z_points[j] = []
                x_points[j].append(self.poses[p].joints[j].x)
                y_points[j].append(self.poses[p].joints[j].y)
                z_points[j].append(self.poses[p].joints[j].z)
            time_points.append(self.poses[p].timestamp)

        if verbosity > 0:
            print("100% - Done.")
            print("\tPerforming the resampling...", end=" ")

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
            if verbosity > 1:
                print("\t\tJoint label: " + str(joint_label))
            perc = show_progression(verbosity, i, no_joints, perc)
            new_x_points[joint_label], new_time_points = resample_data(x_points[joint_label],
                                                                       time_points, frequency, mode, self.time_unit)
            new_y_points[joint_label], new_time_points = resample_data(y_points[joint_label],
                                                                       time_points, frequency, mode, self.time_unit)
            new_z_points[joint_label], new_time_points = resample_data(z_points[joint_label],
                                                                       time_points, frequency, mode, self.time_unit)
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
            for j in new_x_points.keys():
                x = new_x_points[j][p]
                y = new_y_points[j][p]
                z = new_z_points[j][p]
                joint_label = Joint(j, x, y, z)
                joint_label.joint_label = j
                pose.add_joint(j, joint_label)
            new_sequence.poses.append(pose)

        if verbosity > 0:
            print("100% - Done.")
            print("\tOriginal sequence had " + str(len(self.poses)) + " poses.")
            print("\tNew sequence has " + str(len(new_sequence.poses)) + " poses.\n")

        new_sequence._calculate_relative_timestamps()  # Sets the relative time from the first pose for each pose

        return new_sequence

    def correct_zeros(self, mode="cubic", name=None, min_duration_warning=0.1, verbosity=1, add_tabs=0):
        """Detects the joints set at (0, 0, 0) and correct their coordinates by interpolating the data from the
        neighbouring temporal points. Typically, this function is used to correct the zeroes set by the Qualisys system
        when a specific joint is not tracked. In the case where an edge pose (first or last pose of the sequence) has
        (0, 0, 0) coordinates, the closest non-zero coordinate is assigned to the pose. The (0, 0, 0) coordinates are
        then considered as missing and are new values are interpolated using `tool_functions.interpolate_data()`.

        .. versionadded:: 2.0

        Parameters
        ----------
        mode: str, optional
            This parameter also allows for all the values accepted for the ``kind`` parameter in the function
            :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
            ``"slinear"``, ``"quadratic"``, ``"cubic"``”, ``"previous"``, and ``"next"``. See the `documentation
            for this Python module
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.

        name: str or None, optional
            Defines the name of the output sequence. If set on ``None``, the name will be the same as the input
            sequence, with the suffix ``"+CZ"``.

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

"""

        t = add_tabs * "\t"

        if verbosity > 0:
            print(t + "Correcting the zeros (mode: " + str(mode) + ")...")
            print(t + "\tCreating vectors and finding zeros...", end=" ")

        # Create an empty sequence
        new_sequence = Sequence(None)
        if name is None:
            new_sequence.name = self.name + " +CZ"
        else:
            new_sequence.name = name
        new_sequence.path = self.path

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
        for joint_label in self.poses[0].joints.keys():
            counter_zeros[joint_label] = 0

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
                if (self.poses[p].joints[joint_label].x != 0 and self.poses[p].joints[joint_label].y != 0 and
                        self.poses[p].joints[joint_label].z != 0):

                    time_zeros = self.get_time_between_two_poses(p - counter_zeros[joint_label], p)
                    if time_zeros >= min_duration_warning:
                        if verbosity > 0:
                            print(t + "\t\t\tWarning: sequence of (0, 0, 0) coordinates of " + str(time_zeros) +
                                  " s for the joint " + str(joint_label) + ".")
                    counter_zeros[joint_label] = 0

                    # If these are the first non-zero coordinates, we create a non-zero coordinate
                    if p != 0 and len(x_points) == 0:
                        if verbosity > 1:
                            print(t + "\t\t\tThis is the first pose for the joint " + str(joint_label) + " having " +
                                  "non-zero coordinates. Creating a pose at timestamp 0 with these coordinates.")
                        x_points[joint_label].append(self.poses[p].joints[joint_label].x)
                        y_points[joint_label].append(self.poses[p].joints[joint_label].y)
                        z_points[joint_label].append(self.poses[p].joints[joint_label].z)
                        time_points[joint_label].append(self.poses[0].timestamp)

                    # We add the coordinates and timestamps
                    x_points[joint_label].append(self.poses[p].joints[joint_label].x)
                    y_points[joint_label].append(self.poses[p].joints[joint_label].y)
                    z_points[joint_label].append(self.poses[p].joints[joint_label].z)
                    time_points[joint_label].append(self.poses[p].timestamp)

                # If coordinate is zero
                else:

                    counter_zeros[joint_label] += 1

                    # If it's the last pose of the sequence
                    if p == len(self.poses) - 1:

                        time_zeros = self.get_time_between_two_poses(p - counter_zeros[joint_label], p)
                        if time_zeros >= min_duration_warning:
                            if verbosity > 0:
                                print(t + "\t\t\tWarning: sequence of (0, 0, 0) coordinates of " + str(time_zeros) +
                                      " s for the joint " + str(joint_label) + ".")

                        # If the vector is still empty, we add a first coordinate
                        if len(x_points) == 0:
                            if verbosity > 1:
                                print(t + "\t\t\tAll the coordinates for the joint " + str(joint_label) + " were " +
                                      "(0, 0, 0). Creating a pose at timestamp 0 with (0, 0, 0) coordinates.")
                            x_points[joint_label].append(self.poses[p].joints[joint_label].x)
                            y_points[joint_label].append(self.poses[p].joints[joint_label].y)
                            z_points[joint_label].append(self.poses[p].joints[joint_label].z)
                            time_points[joint_label].append(self.poses[0].timestamp)

                        # We copy the last coordinate we added to the vector as an ending point
                        if verbosity > 1:
                            print(
                                t + "\t\t\tThis is the last pose for the joint " + str(joint_label) + ", and it has " +
                                "(0, 0, 0) coordinates. Copying the last pose having non-zero coordinates to put at " +
                                "the end of the series.")
                        x_points[joint_label].append(x_points[joint_label][-1])
                        y_points[joint_label].append(y_points[joint_label][-1])
                        z_points[joint_label].append(z_points[joint_label][-1])
                        time_points[joint_label].append(self.poses[p].timestamp)

                    zero_points_detected += 1

                    if joint_label not in faulty_joints:
                        faulty_joints.append(joint_label)

                    if len(time_points[joint_label]) > 1:
                        t_diff = time_points[joint_label][-1] - time_points[joint_label][-2]
                        if t_diff > longest_zero:
                            longest_zero = t_diff

                total_joints += 1

            if verbosity > 1:
                if len(faulty_joints) == 0:
                    print(t + "\t\t\tNo joints found with coordinate (0, 0, 0).")
                else:
                    to_print = ""
                    if len(faulty_joints) == 1:
                        print(t + "\t\t\t 1 joint with coordinate (0, 0, 0) detected: ", end="")
                    else:
                        print(t + "\t\t\t" + str(len(faulty_joints)) + " joints with coordinate (0, 0, 0) detected: ",
                              end="")
                    for joint_label in faulty_joints:
                        to_print += joint_label + ", "
                    print(to_print[:-2])

        if verbosity == 1:
            print("100% - Done.")
        if verbosity > 0:
            print(t + "\t\t" + str(zero_points_detected) + " joints at coordinate (0, 0, 0) detected over " +
                  str(total_joints) + " (" + str(round(zero_points_detected / total_joints * 100, 2)) + "%).")
            print(t + "\t\t" + "Longest chain of zeros detected: " + str(longest_zero) + "s. ")

        if zero_points_detected != 0:
            if verbosity > 0:
                print(t + "\tPerforming the correction..", end=" ")

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
                new_x_points[joint_label], new_time_points = interpolate_data(x_points[joint_label],
                                                                              time_points[joint_label],
                                                                              self.get_timestamps(relative=False), mode)
                new_y_points[joint_label], new_time_points = interpolate_data(y_points[joint_label],
                                                                              time_points[joint_label],
                                                                              self.get_timestamps(relative=False), mode)
                new_z_points[joint_label], new_time_points = interpolate_data(z_points[joint_label],
                                                                              time_points[joint_label],
                                                                              self.get_timestamps(relative=False), mode)
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
                    x = new_x_points[joint_label][p]
                    y = new_y_points[joint_label][p]
                    z = new_z_points[joint_label][p]
                    joint = Joint(joint_label, x, y, z)
                    joint.joint_label = joint_label
                    joint._set_is_corrected(True)
                    pose.add_joint(joint_label, joint)
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

            return new_sequence

        else:
            if verbosity != 0:
                print(t + "No zero coordinate found, returning the original sequence.")
            return self

    def randomize(self, verbosity=1):
        """Returns a sequence that randomizes the starting position of all the joints of the original sequence. The
        randomization follows a uniform distribution:

            •	x coordinate randomized between -0.2 and 0.2
            •	y coordinate randomized between -0.3 and 0.3
            •	z coordinate randomized between -0.5 and 0.5

        The randomization preserves the direction of movement, timestamps and all the other metrics of the sequence;
        the starting position only of the joints is randomized, and the coordinates of the joints of the subsequent
        poses are adapted using the new starting position as reference.

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

        Returns
        -------
        Sequence
            A new sequence having the same amount of poses and timestamps as the original, but with randomized starting
            coordinates. The attribute :attr:`randomized` of this new Sequence will be set on `True`.
"""

        if verbosity > 0:
            print("Randomizing the starting points of the joints...")
            print("\tCreating a new sequence...", end=" ")

        new_sequence = Sequence(None)
        for p in range(len(self.poses)):
            new_sequence.poses.append(self.copy_pose(p))
        new_sequence.path = self.path

        if verbosity > 0:
            print("OK. \n\tRandomizing starting positions...", end=" ")

        # Get the starting positions of all joints
        starting_positions = []
        for joint_label in new_sequence.poses[0].joints.keys():
            starting_positions.append(new_sequence.poses[0].joints[joint_label].get_copy())

        # Randomize new starting positions for joints
        randomized_positions = generate_random_joints(len(new_sequence.poses[0].joints))
        # random.shuffle(randomized_positions)

        if verbosity > 0:
            print("OK. \n\tMoving the joints...", end=" ")

        # Assign these new starting positions to the joints and moves the joints in every subsequent pose
        # in relation to the new starting positions
        joints_labels = list(new_sequence.poses[0].joints.keys())
        for p in new_sequence.poses:
            for j in range(len(joints_labels)):
                p.joints[joints_labels[j]]._randomize_coordinates_keep_movement(starting_positions[j],
                                                                                randomized_positions[j])
        new_sequence.randomized = True
        new_sequence._calculate_relative_timestamps()

        if verbosity > 0:
            print("OK.")

        return new_sequence

    # === Copy and blank sequence creation functions ===

    def _create_new_sequence_with_timestamps(self, verbosity=1):
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

        Returns
        -------
        Sequence
            A :class:`Sequence` instance that has the same number of Pose objects as the original sequence in the
            :attr:`poses` attribute; however, for every Pose object, the attribute ``joints`` is an OrderedDict that has
            the joint labels as keys, but ``None`` as values, apart from the first pose, that preserves the coordinates
            for all the joints; the attributes ``pose_number`` and ``timestamp`` are preserved from the original
            sequence.
        """

        if verbosity > 0:
            print("\n\tCreating an empty sequence...", end=" ")
        new_sequence = Sequence(None)

        # Used for the progression percentage
        perc = 10
        for p in range(len(self.poses)):
            # Show percentage if verbosity
            perc = show_progression(verbosity, p, len(self.poses), perc)
            # Creates an empty pose with the same timestamp as the original
            pose = self.poses[p]._get_copy_with_empty_joints(False)
            new_sequence.poses.append(pose)  # Add to the sequence

        # Copy the joints from the first pose
        for joint_label in self.poses[0].joints.keys():  # For every joint

            # If this joint doesn't already exist in the new sequence, we copy it
            if joint_label not in new_sequence.poses[0].joints.keys():
                new_sequence.poses[0].joints[joint_label] = self.copy_joint(0, joint_label)

        if verbosity > 0:
            print("100% - Done.")

        return new_sequence

    def copy_pose(self, pose_index):
        """Returns a deep copy of a specified pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose to copy (starting at 0).

        Returns
        -------
        Pose
            The copy of a Pose instance.
        """

        if len(self.poses) == 0:
            raise EmptySequenceException()
        elif not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))

        pose = Pose(self.poses[pose_index].get_timestamp())

        for i in self.poses[pose_index].joints.keys():  # For every joint

            pose.joints[i] = self.copy_joint(pose_index, i)

        pose.relative_timestamp = self.poses[pose_index].get_relative_timestamp()

        return pose

    def copy_joint(self, pose_index, joint_label):
        """Returns a deep copy of a specified joint from a specified pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose to copy (starting at 0).

        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        -------
        Joint
            The copy of a Joint instance.
        """

        if len(self.poses) == 0:
            raise EmptySequenceException()
        elif not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))

        if joint_label not in self.poses[pose_index].get_joint_labels():
            raise InvalidJointLabelException(joint_label)

        joint = self.poses[pose_index].get_joint(joint_label).get_copy()

        return joint

    # === Print functions ===

    def print_pose(self, pose_index):
        """Prints the information related to one specific pose of the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose to copy (starting at 0).
        """
        if len(self.poses) == 0:
            raise EmptySequenceException()
        elif not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))
        txt = "Pose " + str(pose_index + 1) + " of " + str(len(self.poses)) + "\n"
        txt += str(self.poses[pose_index])
        print(txt)

    def print_stats(self):
        """Prints a series of statistics related to the sequence, using the output of the function
        :meth:`Sequence.get_stats()`.

        .. versionadded:: 2.0
        """
        stats = self.get_stats()
        for key in stats.keys():
            if key == "Duration":
                print(str(key) + ": " + str(stats[key]) + " s")
            elif key in ["Subject height", "Left arm length", "Right arm length"]:
                print(str(key) + ": " + str(round(stats[key], 3)) + " m")
            elif "Average velocity" in key:
                print(str(key) + ": " + str(round(stats[key] * 1000, 1)) + " mm/s")
            else:
                print(str(key) + ": " + str(stats[key]))

    def print_details(self, include_name=True, include_condition=True, include_date_recording=True,
                            include_number_of_poses=True, include_duration=True):
        """Prints a series of details about the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_name: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`name` to the printed string.
        include_condition: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`condition` to the printed string.
        include_date_recording: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`date_of_recording` to the printed string.
        include_number_of_poses: bool, optional
            If set on ``True`` (default), adds the length of the attribute :attr:`poses` to the printed string.
        include_duration: bool, optional
            If set on ``True`` (default), adds the duration of the Sequence to the printed string.
        """
        string = ""
        if include_name:
            string += "Name: " + str(self.name) + " · "
        if include_condition:
            string += "Condition: " + str(self.condition) + " · "
        if include_date_recording:
            string += "Date recording: " + str(self.get_printable_date_recording()) + " · "
        if include_number_of_poses:
            string += "Number of poses: " + str(self.get_number_of_poses()) + " · "
        if include_duration:
            string += "Duration: " + str(round(self.get_duration(), 2)) + " s" + " · "
        if len(string) > 3:
            string = string[:-3]

        print(string)

    # === Conversion functions ===
    def convert_to_table(self, use_relative_timestamps=False):
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
        """

        table = []

        # For each pose
        for p in range(len(self.poses)):
            if p == 0:
                table = self.poses[0].convert_to_table(use_relative_timestamps)
            else:
                table.append(self.poses[p].convert_to_table(use_relative_timestamps)[1])

        return table

    def convert_to_json(self, use_relative_timestamps=False):
        """Returns a list ready to be exported in JSON. The structure followed by the dictionary is the same as the
        output dictionary from Kinect, for compatibility purposes. The output then resembles the table found in
        :ref:`JSON formats <json_example>`.

        .. versionadded:: 2.0

        Parameters
        ----------
        use_relative_timestamps: bool, optional
            Defines if the timestamps used in the table are absolute (``False``) or relative to the first pose
            (``True``).

        Returns
        -------
        list
            A list containing the data of the sequence, ready to be exported in JSON.
        """

        data = []

        # For each pose
        for p in range(len(self.poses)):
            data.append(self.poses[p].convert_to_json(use_relative_timestamps))

        return data

    # === Miscellaneous functions ===

    def average_qualisys_to_kinect(self, joints_labels_to_exclude=None, remove_averaged_joints=False,
                                   remove_non_kinect_joints=False):
        """Creates missing Kinect joints from the Qualisys labelling system by averaging the distance between Qualisys
        joints. The new joints are located at the midpoint of the arithmetic distance between two or more joints. The
        list of averaged joints is set from the ``res/kualisys_to_kinect.txt`` file:

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
        remove_averaged_joints: bool, optional
            If ``True``, removes the joints that are part of an averaging from every pose of the sequence.
        remove_non_kinect_joints: bool, optional
            If ``True``, removes the joints from Qualisys that are not found in the Kinect labelling system.
        """

        joints_to_average = load_qualisys_to_kinect()
        joints_to_remove = ["ArmRight", "ArmLeft", "ThighRight", "ThighLeft", "ShinRight", "ShinLeft"]

        for p in range(len(self.poses)):

            for joint_label in joints_to_average.keys():

                if joint_label not in joints_labels_to_exclude:
                    self.poses[p].generate_average_joint(joints_to_average[joint_label], joint_label)
                    if remove_averaged_joints:
                        self.poses[p].remove_joints(joints_to_average[joint_label])

            if remove_non_kinect_joints:

                if p == 0:
                    list_kinect_joints = load_kinect_joint_labels()
                    for joint_label in self.poses[p].joints.keys():
                        if joint_label not in list_kinect_joints:
                            joints_to_remove.append(joint_label)

                self.poses[p].remove_joints(joints_to_remove)

    def average_joints(self, joints_labels_to_average, new_joint_label, remove_averaged_joints=False):
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
        """

        for pose in self.poses:

            pose.generate_average_joint(joints_labels_to_average, new_joint_label)

            if remove_averaged_joints:
                pose.remove_joints(joints_labels_to_average)

    def concatenate(self, other, delay):
        """Adds all the poses of another sequence at the end of the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: :class:`Sequence`
            The sequence to concatenate.
        delay: float
            The delay to apply, in seconds, between the last pose of the original sequence and the first pose of the
            new sequence.
        """

        last_pose_timestamp = self.poses[-1].timestamp

        for p in range(len(other.poses)):
            self.poses.append(other.poses[p])
            self.poses[p].timestamp = last_pose_timestamp + delay + self.poses[p].relative_timestamp

        self._calculate_relative_timestamps()

    # === Saving functions ===

    def save(self, folder_out="", name=None, file_format="json", individual=False, use_relative_timestamps=True,
             verbosity=1):
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
            ``"txt"``, ``"csv"``, ``"tsv"``, or, if you are a masochist, ``"mat"``. Notes:

                • ``"xls"`` will save the file with an ``.xlsx`` extension.
                • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
                • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
                  on ``,``. By default, the function will detect which separator the system uses.
                • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
                • Any other string will not return an error, but rather be used as a custom extension. The data will
                  be saved as in a text file (using tabulations as values separators).

            .. warning::
                While it is possible to save sequences as ``.mat`` or custom extensions, the toolbox will not recognize
                these files upon opening. The support for ``.mat`` and custom extensions as input may come in a future
                release, but for now these are just offered as output options.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

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
        """

        if folder_out == "":
            folder_out = os.getcwd()

        if not individual:
            subfolders = folder_out.split("/")
            if len(subfolders) != 0:
                if "." in subfolders[-1]:
                    folder_out = "/".join(subfolders[:-1])
                    name = ".".join(subfolders[-1].split(".")[:-1])
                    file_format = subfolders[-1].split(".")[-1]

        # Automatic creation of all the folders of the path if they don't exist
        create_subfolders(folder_out)

        if name is None and self.name is not None:
            name = self.name
        elif name is None:
            name = "out"

        file_format = file_format.strip(".")  # We remove the dot in the format
        if file_format == "xls":
            file_format = "xlsx"

        if verbosity > 0:
            if individual:
                print("Saving " + file_format.upper() + " individual files...")
            else:
                print("Saving " + file_format.upper() + " global file: " + folder_out.strip("/") + "/" + name + "." +
                      file_format + "...")

        if file_format == "json":
            self._save_json(folder_out, name, individual, use_relative_timestamps, verbosity)

        elif file_format == "mat":
            self._save_mat(folder_out, name, individual, use_relative_timestamps, verbosity)

        elif file_format == "xlsx":
            self._save_xlsx(folder_out, name, individual, use_relative_timestamps, verbosity)

        else:
            self._save_txt(folder_out, name, file_format, individual, use_relative_timestamps, verbosity)

        if individual:
            self.path = folder_out + name
        else:
            self.path = folder_out + name + file_format

        if verbosity > 0:
            print("100% - Done.")

    def save_stats(self, folder_out="", name=None, file_format="json", keys_to_exclude=None, keys_to_include=None,
                   verbosity=1):
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
        """

        if folder_out == "":
            folder_out = os.getcwd()

        subfolders = folder_out.split("/")
        if len(subfolders) != 0:
            if "." in subfolders[-1]:
                folder_out = "/".join(subfolders[:-1])
                name = ".".join(subfolders[-1].split(".")[:-1])
                file_format = subfolders[-1].split(".")[-1]

        # Automatic creation of all the folders of the path if they don't exist
        create_subfolders(folder_out)

        # Handling file format
        file_format = file_format.strip(".")  # We remove the dot in the format
        if file_format == "xls":
            file_format = "xlsx"

        stats = self.get_stats()
        if keys_to_exclude is not None:
            for key in keys_to_exclude:
                del stats[key]

        if keys_to_exclude is None and keys_to_include is not None:
            selected_stats = {}
            for key in keys_to_include:
                selected_stats[key] = stats[key]
            stats = selected_stats

        path_out = str(folder_out) + str(name) + "." + str(file_format)

        if file_format in ["json", "mat"]:

            if file_format == "json":
                with open(path_out, 'w', encoding="utf-16-le") as f:
                    json.dump(stats, f)

            elif file_format == "mat":
                try:
                    import scipy
                except ImportError:
                    raise ModuleNotFoundException("scipy", "save a file in .mat format.")
                scipy.io.savemat(path_out, {"data": stats})

        else:

            table = [[], []]
            for key in stats.keys():
                table[0].append(key)
                table[1].append(stats[key])

            if file_format == "xlsx":
                write_xlsx(stats, path_out, verbosity)

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
                elif file_format in ["txt", "tsv"]:  # For text files, tab separator
                    separator = "\t"
                else:
                    separator = "\t"

                write_text_table(stats, separator, folder_out, 0)

    def _save_json(self, folder_out, name=None, individual=False, use_relative_timestamps=False, verbosity=1):
        """Saves a sequence as a json file or files. This function is called by the :meth:`Sequence.save`
        method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

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
        """

        perc = 10  # Used for the progression percentage

        # Get the data
        data = self.convert_to_json(use_relative_timestamps)

        # Save the data
        if not individual:
            if name is None:
                name = "out"
            with open(folder_out + "/" + name + ".json", 'w', encoding="utf-16-le") as f:
                json.dump(data, f)
        else:
            if name is None:
                name = "pose"
            for p in range(len(self.poses)):
                perc = show_progression(verbosity, p, len(self.poses), perc)
                with open(folder_out + "/" + name + "_" + str(p) + ".json", 'w', encoding="utf-16-le") as f:
                    json.dump(data[p], f)

    def _save_mat(self, folder_out, name=None, individual=False, use_relative_timestamps=True, verbosity=1):
        """Saves a sequence as a Matlab .mat file or files. This function is called by the :meth:`Sequence.save`
        method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Important
        ---------
            This function is dependent of the module `scipy <https://scipy.org/>`_.

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

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
        """

        perc = 10  # Used for the progression percentage

        try:
            import scipy
        except ImportError:
            raise ModuleNotFoundException("scipy", "save a file in .mat format.")

        # Save the data
        if not individual:
            if name is None:
                name = "out"
            data = self.convert_to_json(use_relative_timestamps)
            scipy.io.savemat(folder_out + "/" + name + ".mat", {"data": data})
        else:
            for p in range(len(self.poses)):
                if name is None:
                    name = "pose"
                data = self.poses[p].convert_to_table(use_relative_timestamps)
                perc = show_progression(verbosity, p, len(self.poses), perc)
                scipy.io.savemat(folder_out + "/" + name + "_" + str(p) + ".mat", {"data": data})

    def _save_xlsx(self, folder_out, name=None, individual=False, use_relative_timestamps=True, verbosity=1):
        """Saves a sequence as an Excel .xlsx file or files. This function is called by the :meth:`Sequence.save`
        method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Important
        ---------
            This function is dependent of the module `openpyxl <https://pypi.org/project/openpyxl/>`_.

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

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
        """

        perc = 10  # Used for the progression percentage

        # Save the data
        if not individual:
            if name is None:
                name = "out"
            data = self.convert_to_table(use_relative_timestamps)
            write_xlsx(data, folder_out + "/" + name + ".xlsx", verbosity)

        else:
            for p in range(len(self.poses)):
                if name is None:
                    name = "pose"
                data = self.poses[p].convert_to_table(use_relative_timestamps)
                perc = show_progression(verbosity, p, len(self.poses), perc)
                write_xlsx(data, folder_out + "/" + name + "_" + str(p) + ".xlsx", 0)

    def _save_txt(self, folder_out, name=None, file_format="csv", individual=False, use_relative_timestamps=True,
                  verbosity=1):
        """Saves a sequence as .txt, .csv, .tsv, or custom extension files or file. This function is called by the
        :meth:`Sequence.save` method, and saves the Sequence instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the sequence. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"pose"`` if individual is ``True``.

        file_format: str, optional
            The file format in which to save the sequence. The file format can be ``"txt"``, ``"csv"`` (default) or
            ``"tsv"``. ``"csv;"`` will force the value separator on ``";"``, while ``"csv,"`` will force the separator
            on ``","``. By default, the function will detect which separator the system uses. ``"txt"`` and ``"tsv"``
            both separate the values by a tabulation. Any other string will not return an error, but rather be used as
            a custom extension. The data will be saved as in a text file (using tabulations as values separators).

        individual: bool, optional
            If set on ``False`` (default), the function will save the sequence in a unique file.
            If set on ``True``, the function will save each pose of the sequence in an individual file, appending an
            underscore and the index of the pose (starting at 0) after the name.

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
        """

        perc = 10  # Used for the progression percentage

        # Force comma or semicolon separator
        if file_format == "csv,":
            separator = ","
            file_format = "csv"
        elif file_format == "csv;":
            separator = ";"
            file_format = "csv"
        elif file_format[0:3] == "csv":  # Get the separator from local user (to get , or ;)
            separator = get_system_csv_separator()
        elif file_format == "txt":  # For text files, tab separator
            separator = "\t"
        else:
            separator = "\t"

        # Save the data
        if not individual:
            if name is None:
                name = "out"
            write_text_table(self.convert_to_table(use_relative_timestamps), separator,
                             folder_out + "/" + name + "." + file_format, verbosity)
        else:
            for p in range(len(self.poses)):
                if name is None:
                    name = "pose"
                write_text_table(self.poses[p].convert_to_table(use_relative_timestamps),
                                 separator, folder_out + "/" + name + "_" + str(p) + "." + file_format, 0)
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
        420
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
