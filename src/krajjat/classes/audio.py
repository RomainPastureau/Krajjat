"""Default class for audio recordings matching a Sequence, typically the voice of the subject of the motion capture.
This class allows to perform a variety of transformations of the audio stream, such as getting the envelope, pitch and
formants of the speech.
"""
from collections import OrderedDict

from find_delay import find_delay, find_delays
from scipy.signal import butter, lfilter, hilbert
from scipy.io import wavfile, loadmat, savemat
from parselmouth import Sound

from krajjat.classes.audio_derivatives import *
from krajjat.classes.timeseries import TimeSeries


class Audio(AudioDerivative):
    """Default class for audio clips matching a Sequence, typically the voice of the subject of the motion
    capture. This class allows to perform a variety of transformations of the audio stream, such as getting the
    envelope, pitch and formants of the speech.

    .. versionadded:: 2.0

    Parameters
    ----------
    path_or_samples: str or list(int) or numpy.ndarray(int)
        The path to the audio file, or a list containing the samples of an audio file. If the file is a path, it should
        either point to a `.wav` file, or to a file containing the timestamps and samples in a text form (`.json`,
        `.csv`, `.tsv`, `.txt` or `.mat`). It is also possible to point to a folder containing one file per sample.
        See :ref:`Audio formats <wav_example>` for the acceptable file types.

    frequency: int or float, optional
        The frequency, in Hz (or samples per sec) at which the parameter `path_or_samples` is set. This parameter
        will be ignored if ``path_or_samples`` is a path, but will be used to define the :attr:`timestamps` of the
        Audio object if ``path_or_samples`` is a list of samples.

    name: str, optional
        Defines a name for the Audio instance. If a string is provided, the attribute :attr:`name` will take
        its value. If not, see :meth:`Audio._define_name_init()`.

    condition: str or None, optional
        Optional field to represent in which experimental condition the audio was recorded.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Attributes
    ----------
    samples: np.ndarray(int)
        A list containing the audio samples, in chronological order.
    timestamps: np.ndarray(float)
        A list containing the timestamps matching each audio sample. Consequently, :attr:`samples` and
        :attr:`timestamps` should have the same length.
    frequency: int or float
        The amount of samples per second.
    name: str
        Custom name given to the audio. If no name has been provided upon initialisation, it will be defined by
        :meth:`Audio._define_name_init()`.
    condition: str
        Defines in which experimental condition the audio clip was recorded.
    metadata: dict
        A dictionary containing metadata about the recording, extracted from the file.
    path: str
        Path to the audio file passed as a parameter upon creation; if samples were provided, this attribute will be
        `None`.
    files: list(str)
        List of files contained in the path. The list will be of size 1 if the path points to a single file.
    kind: str
        A parameter that is set on ``"Audio"``, to differentiate it from the different types of AudioDerivative.

    Examples
    --------
    >>> seq1 = Audio("sequences/Chris/seq_001.tsv")
    >>> seq2 = Audio("sequences/Will/seq_001.xlsx", name="Will_001")
    >>> seq3 = Audio(name="Jonny_001")
    >>> from scipy.io import wavfile
    >>> freq, samples = wavfile.read("sequences/Guy/seq_001.wav")
    >>> seq4 = Audio(samples, freq, name="Guy_001", condition="English", time_unit="ms", system="Kinect", verbosity=0)
    """

    def __init__(self, path_or_samples, frequency=None, name=None, condition=None, verbosity=1):
        super().__init__("Audio", path_or_samples, name, condition, verbosity)

    # === Setter functions ===
    def set_name(self, name):
        """Sets the :attr:`name` attribute of the Audio instance. This name can be used as display functions or as
        a means to identify the audio.

        .. versionadded:: 2.0

        Parameters
        ----------
        name : str
            A name to describe the audio clip.

        Example
        -------
        >>> aud = Audio("C:/Users/Walter/Sequences/audio.wav")
        >>> aud.set_name("Audio 28980")
        """
        super().set_name(name)

    def set_condition(self, condition):
        """Sets the :py:attr:`condition` attribute of the Audio instance. This attribute can be used to save the
        experimental condition in which the Audio instance was recorded.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str
            The experimental condition in which the audio clip was recorded.

        Example
        -------
        >>> aud1 = Audio("C:/Users/Dwight/Sequences/English/seq.wav")
        >>> aud1.set_condition("English")
        >>> aud2 = Audio("C:/Users/Dwight/Sequences/Spanish/seq.wav")
        >>> aud2.set_condition("Spanish")
        """
        super().set_condition(condition)

    # === Loading functions ===
    def _load_from_path(self, verbosity=1):
        """Loads the audio data from the :attr:`path` provided during the initialization.

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

    def _load_from_samples(self, samples, frequency, verbosity=1):
        """Loads the audio data when samples and frequency have been provided upon initialisation.

        .. versionadded:: 2.0

        Parameters
        ----------
        samples: list(int) or numpy.ndarray(int)
            A list containing the audio samples, in chronological order.
        frequency: int or float
            The amount of samples per second.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        """

        if verbosity > 1:
            print("Parameter path_or_samples detected as being samples.")

        if not isinstance(samples, np.ndarray):
            self.samples = np.array(samples)
        else:
            self.samples = samples
        if frequency is not None:
            self.frequency = frequency
        else:
            raise Exception("If samples are provided, frequency cannot be None. Please provide a value for frequency.")

        self._calculate_timestamps()

    def _load_samples(self, verbosity=1):
        """Loads the single sample files or the global file containing all the samples. Depending on the input, this
        function calls either :meth:`Audio._load_single_sample_file` or :meth:`Audio._load_audio_file`.

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
            print(f"Opening audio from {self.path}...", end=" ")
        elif verbosity > 1:
            print(f"Opening audio from {self.path}...")
        perc = 10  # Used for the progression percentage

        # If the path is a folder, we load every single file
        if os.path.isdir(self.path):

            self.samples = np.zeros((len(self.files),))
            self.timestamps = np.zeros((len(self.files),))

            for i in range(len(self.files)):

                if verbosity > 1:
                    print(f"Loading file {i + 1} of {len(self.files)}: {self.files[i]}...", end=" ")

                # Show percentage if verbosity
                perc = show_progression(verbosity, i, len(self.files), perc)

                # Loads a file containing one timestamp and one sample
                self._load_single_sample_file(i, op.join(self.path, self.files[i]), verbosity)

                if verbosity > 1:
                    print("OK.")

            self._calculate_frequency()

            if verbosity > 0:
                print("100% - Done.")

        # Otherwise, we load the one file
        else:
            self._load_audio_file(verbosity)

    def _load_single_sample_file(self, sample_index, path, verbosity):
        """Loads the content of a single sample file into the Audio object. Depending on the file type, this function
        handles the content differently (see :ref:`Audio formats <wav_example>`).

        .. versionadded:: 2.0

        Parameters
        ----------
        sample_index: int
            The index of the sample to load.
        path: str
            The path of a file containing a single sample and timestamp.
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
            if sample_index == 0:
                self._load_json_metadata(data, verbosity)
            self.samples[sample_index] = data["Sample"]
            self.timestamps[sample_index] = data["Timestamp"]

        # Excel file
        elif file_extension == ".xlsx":
            data = read_xlsx(path, verbosity=verbosity)
            self.samples[sample_index] = float(data[1][1])
            self.timestamps[sample_index] = float(data[1][0])

        # Pickle file
        elif file_extension == ".pkl":
            with open(path, "rb") as f:
                content = pickle.load(f)
            self.samples[sample_index] = content["Sample"]
            self.timestamps[sample_index] = content["Timestamp"]

        # Text file
        else:
            if os.path.splitext(self.path)[-1] not in [".csv", ".tsv", ".txt"]:
                if verbosity > 0:
                    print(f"Loading from non-standard extension {os.path.splitext(self.path)[-1]} as text...")

            separator = get_filetype_separator(file_extension[-1])

            # Open the file and read the data
            data, metadata = read_text_table(path)
            if sample_index == 0:
                self.metadata.update(metadata)
            self.samples[sample_index] = float(data[1][1])
            self.timestamps[sample_index] = float(data[1][0])

    def _load_audio_file(self, verbosity=1):
        """Loads the content of a file containing all the samples of the audio stream. Depending on the file type, this
        function handles the content differently (see :ref:`Audio formats <wav_example>`).

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
            print("\n\tOpening the audio...", end=" ")

        file_extension = op.splitext(self.path)[-1]

        if file_extension == ".wav":
            audio_data = wavfile.read(self.path)
            self.frequency = audio_data[0]

            # Turn stereo to mono if the file is stereo
            if len(np.shape(audio_data[1])) != 1:
                self.samples = stereo_to_mono(audio_data[1], verbosity=verbosity)
            else:
                self.samples = audio_data[1]

            # Metadata
            with taglib.File(self.path) as file:
                for tag in file.tags:
                    self.metadata[tag] = file.tags[tag]

            self._calculate_timestamps()

        elif file_extension == ".json":
            data = read_json(self.path)

            if len(data) == 0:
                raise EmptyAudioException()

            self._load_json_metadata(data, verbosity)
            self.samples = np.array(data["Sample"])
            self.frequency = data["Frequency"]
            self._calculate_timestamps()

        # Pickle file
        elif file_extension == ".pkl":
            with open(self.path, "rb") as f:
                audio = pickle.load(f)
            for attr in audio.__dict__:
                self.__setattr__(attr, audio.__dict__[attr])

        # Mat file
        elif file_extension == ".mat":
            with open(self.path, "rb") as f:
                data = loadmat(f, simplify_cells=True)

            for key in data["data"]:
                if key == "Sample":
                    self.samples = pd.DataFrame(data["data"]["Sample"]).values.flatten()

                elif key == "Timestamp":
                    self.timestamps = pd.DataFrame(data["data"]["Timestamp"]).values.flatten()

                elif key == "Frequency":
                    self.frequency = data["data"]["Frequency"]

                else:
                    self.metadata[key] = data["data"][key]

            self._calculate_frequency()

        else:
            if file_extension not in [".csv", ".xlsx", ".tsv", ".txt"]:
                if verbosity > 0:
                    print(f"Loading from non-standard extension {file_extension} as text...")

            if self.path.split(".")[-1] == "xlsx":
                data, metadata = read_xlsx(self.path, verbosity=verbosity)
                self.metadata.update(metadata)

            else:
                data, metadata = read_text_table(self.path)
                self.metadata.update(metadata)

            if "Frequency" in self.metadata:
                self.frequency = self.metadata["Frequency"]
                del self.metadata["Frequency"]

            self.samples = np.array([data[i][1] for i in range(1, len(data))])
            self.timestamps = np.array([data[i][0] for i in range(1, len(data))])

            self._calculate_frequency()

        if verbosity:
            print("100% - Done.")

    def _load_json_metadata(self, data, verbosity=1):
        """Loads the data from the file apart from the samples, and saves it in the attribute :attr:`metadata`.

        .. versionadded:: 2.0

        Parameters
        ----------
        data: dict
            The data from the file containing the full audio, or containing the first sample of the audio clip.

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
            if key not in ["Sample", "Timestamp", "Frequency"]:
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

    def _calculate_frequency(self):
        """Determines the frequency (number of samples per second) of the audio by calculating the time elapsed between
        the two first timestamps. This function is automatically called when reading the timestamps and samples from
        a text file.

        .. versionadded:: 2.0
        """
        self.frequency = 1 / ((self.timestamps[-1] - self.timestamps[0]) / (len(self.timestamps) - 1))

    def _calculate_timestamps(self):
        """Calculates the timestamps of the audio samples from the frequency and the number of samples. This function
        is automatically called when reading the frequency and samples from an audio file, or when a list of samples
        and a frequency are passed as a parameters during the initialisation.

        .. versionadded:: 2.0
        """
        self.timestamps = np.arange(0, len(self.samples)) / self.frequency

    # === Getter functions ===
    def get_path(self):
        """Returns the attribute :attr:`path` of the Audio instance.

        . versionadded:: 2.0

        Returns
        -------
        str
            The path of the Audio instance.

        Example
        -------
        >>> audio = Audio("Recordings/Giacchino/01.wav")
        >>> audio.get_path()
        Recordings/Giacchino/01.wav
        """
        return self.path

    def get_name(self):
        """Returns the attribute :attr:`name` of the Audio instance.

        . versionadded:: 2.0

        Returns
        -------
        str
            The name of the Audio instance.

        Example
        -------
        >>> audio = Audio("Recordings/Williams/recording_02.wav")
        >>> audio.get_path()
        recording_02
        """
        return self.name

    def get_condition(self):
        """Returns the attribute :attr:`condition` of the Audio instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The experimental condition in which the recording of the audio clip was performed.

        Examples
        --------
        >>> audio = Audio("Recordings/Zimmer/recording_03.wav")
        >>> audio.get_condition()
        None
        >>> audio = Audio("Recordings/Djawadi/recording_04.wav", condition="Basque")
        >>> audio.get_condition()
        Basque
        """
        return self.condition

    def get_samples(self):
        """Returns the attribute :attr:`samples` of the Audio instance.

        . versionadded:: 2.0

        Returns
        -------
        np.ndarray(int|float)
            The samples of the Audio instance.

        Examples
        --------
        >>> audio = Audio("Recordings/Elfman/recording_05.wav")
        >>> audio.get_samples()
        array([0, 1, 3, 6, 2, 7, 13, 20, 12, 21, 11, 22, 10, 23])
        """
        return self.samples

    def get_sample(self, sample_index):
        """Returns the sample corresponding to the index passed as parameter.

        .. versionadded:: 2.0

        Parameters
        ----------
        sample_index: int
            The index of the sample.

        Returns
        -------
        int
            A sample from the sequence.

        Examples
        --------
        >>> audio = Audio("Recordings/Morricone/recording_06.wav")
        >>> audio.get_sample(42)
        7418880
        """
        if len(self.samples) == 0:
            raise Exception("The Audio does not have any sample.")
        elif not 0 <= sample_index < len(self.samples):
            raise Exception("The pose index must be between 0 and " + str(len(self.samples) - 1) + ". ")

        return self.samples[sample_index]

    def get_number_of_samples(self):
        """Returns the number of samples in the audio clip.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The amount of samples in the audio clip.

        Example
        -------
        >>> audio = Audio("Recordings/Richter/recording_07.wav")
        >>> audio.get_number_of_samples()
        22050
        """
        return len(self.samples)

    def get_timestamps(self):
        """Returns a list of the timestamps for every sample, in seconds.

        .. versionadded:: 2.0

        Returns
        -------
        np.ndarray(int|float)
            List of the timestamps of all the samples of the audio clip, in seconds.

        Example
        -------
        >>> audio = Audio("Recordings/Shapiro/recording_08.wav")
        >>> audio.get_timestamps()
        array([0.00000000e+00 2.26757370e-05 4.53514739e-05 6.80272109e-05
               9.07029478e-05 1.13378685e-04 1.36054422e-04 1.58730159e-04])
        """
        return self.timestamps

    def get_duration(self):
        """Returns the duration of the audio clip, in seconds.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The duration of the audio clip, in seconds.

        Example
        -------
        >>> audio = Audio("Recordings/Desplat/recording_09.wav")
        >>> audio.get_duration()
        42.48151
        """
        return self.timestamps[-1]

    def get_frequency(self):
        """Returns the frequency of the audio clip, in hertz.

        .. versionadded:: 2.0

        Returns
        -------
        int or float
            The frequency of the audio clip, in hertz.

        Example
        -------
        >>> audio = Audio("Recordings/MacQuayle/recording_10.wav")
        >>> audio.get_frequency()
        44100
        """
        return self.frequency

    def get_info(self, return_type="dict", include_path=True):
        """Returns information regarding the Audio clip.

        .. versionadded:: 2.0

        Parameters
        ----------
        return_type: bool, optional
            If set on ``"dict"`` (default), the info is returned as an OrderedDict. If set on ``"table"``, the info
            is returned as a two-dimensional list, ready to be exported as a table. If set on ``"str"``, a printable
            string is returned.

        include_path: bool, optional
            If set on ``True``, the path of the audio clip is included in the returned info (default).

        Returns
        -------
        OrderedDict
            An ordered dictionary where each descriptor is associated to its value. The included information fields are:

                • ``"Name"``: The :attr:`name` attribute of the audio clip.
                • ``"Path"``: The :attr:`path` attribute of the audio clip.
                • ``"Condition"``: The :attr:`condition` attribute of the audio clip (if set).
                • ``"Frequency"``: Output of :meth:`Audio.get_frequency`.
                • ``"Number of samples"``: Output of :meth:`Audio.get_number_of_samples`.
                • ``"Duration"``: Output of :meth:`Audio.get_duration`.

        Example
        -------
        >>> audio = Audio("Recordings/Reznor/recording_11.wav", include_path=False)
        >>> audio.get_info()
        Name: recording_11 · Duration: 0.5 · Frequency: 44100 · Number of samples: 22150
        """

        stats = OrderedDict()
        stats["Name"] = self.name
        if include_path:
            stats["Path"] = self.path
        if self.condition is not None:
            stats["Condition"] = self.condition
        stats["Duration"] = self.get_duration()
        stats["Frequency"] = self.frequency
        stats["Number of samples"] = self.get_number_of_samples()

        if return_type.lower() in ["list", "table"]:
            table = [[], []]
            for key in stats.keys():
                table[0].append(key)
                table[1].append(stats[key])
            return table

        elif return_type.lower() == "str":
            return " · ".join([f"{key}: {stats[key]}" for key in stats.keys()])

        return stats

    # === Transformation functions ===
    def get_envelope(self, window_size=1e6, overlap_ratio=0.5, filter_below=None, filter_over=None, name=None,
                     verbosity=1):
        """Calculates the envelope of an array, and returns it. The function can also optionally perform a band-pass
        filtering, if the corresponding parameters are provided.

        Parameters
        ----------
        window_size: int or None, optional
            The size of the windows (in samples) in which to cut the audio clip to calculate the envelope. Cutting the
            audio clips in windows allows, in the case where they are long, to speed up the computation. If this
            parameter is set on `None`, the window size will be set on the number of samples. A good value for this
            parameter is generally 1 million. If this parameter is set on 0, on None or on a number of samples bigger
            than the amount of samples in the Audio instance, the window size is set on the length of the samples.

        overlap_ratio: float or None, optional
            The ratio of samples overlapping between each window. If this parameter is not `None`, each window will
            overlap with the previous (and, logically, the next) for an amount of samples equal to the number of samples
            in a window times the overlap ratio. Then, only the central values of each window will be preserved and
            concatenated; this allows to discard any "edge" effect due to the windowing. If the parameter is set on
            `None` or 0, the windows will not overlap.

        filter_below: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the lowest frequency of the band-pass filter.

        filter_over: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the highest frequency of the band-pass filter.

        name: str or None, optional
            Defines the name of the envelope. If set on ``None``, the name will be the same as the original Audio
            instance, with the suffix ``"(ENV)"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        np.array
            The envelope of the original array.

        Example
        -------
        >>> audio = Audio("Recordings/Ross/recording_12.wav")
        >>> envelope = audio.get_envelope(filter_over=50)
        """

        if verbosity > 0:
            print("Creating an Envelope object...")

        if window_size == 0 or window_size is None:
            window_size = len(self.samples)

        if overlap_ratio is None:
            overlap_ratio = 0

        if name is None:
            name = self.name + " (ENV)"

        window_size = int(window_size)
        overlap = int(np.ceil(overlap_ratio * window_size))
        number_of_windows = get_number_of_windows(len(self.samples), window_size, overlap_ratio, True)

        # Hilbert transform
        if verbosity == 1:
            print("\tGetting the Hilbert transform...", end=" ")
        elif verbosity > 1:
            print("\tGetting the Hilbert transform...")
            print("\t\tDividing the samples in " + str(number_of_windows) + " window(s) of " + str(window_size) +
                  " samples, with an overlap of " + str(overlap) + " samples.")

        envelope_samples = np.zeros(len(self.samples))
        j = 0
        next_percentage = 10

        for i in range(number_of_windows):

            if verbosity == 1:
                while i / number_of_windows > next_percentage / 100:
                    print(str(next_percentage) + "%", end=" ")
                    next_percentage += 10

            # Get the Hilbert transform of the window
            array_start = i * (window_size - overlap)
            array_end = np.min([(i + 1) * window_size - i * overlap, len(self.samples)])
            if verbosity > 1:
                print("\t\t\tGetting samples from window " + str(i + 1) + "/" + str(number_of_windows) + ": samples " +
                      str(array_start) + " to " + str(array_end) + "... ", end=" ")
            hilbert_window = np.abs(hilbert(self.samples[array_start:array_end]))

            # Keep only the center values
            if i == 0:
                slice_start = 0
            else:
                slice_start = overlap // 2  # We stop one before if the overlap is odd

            if i == number_of_windows - 1:
                slice_end = len(hilbert_window)
            else:
                slice_end = window_size - int(np.ceil(overlap / 2))

            if verbosity > 1:
                print("\n\t\t\tKeeping the samples from " + str(slice_start) + " to " + str(slice_end) + " in the " +
                      "window: samples " + str(array_start + slice_start) + " to " + str(
                    array_start + slice_end) + "...",
                      end=" ")

            preserved_samples = hilbert_window[slice_start:slice_end]
            envelope_samples[j:j + len(preserved_samples)] = preserved_samples
            j += len(preserved_samples)

            if verbosity > 1:
                print("Done.")

        if verbosity == 1:
            print("100% - Done.")
        elif verbosity > 1:
            print("Done.")

        envelope = Envelope(envelope_samples, self.frequency, name, self.condition, verbosity=verbosity)

        envelope._set_attributes_from_other_object(self)
        envelope.metadata["processing_steps"].append({"processing_type": "get_envelope",
                                                      "original_audio": self.name, "original_path": self.path,
                                                      "window_size": window_size, "overlap_ratio": overlap_ratio,
                                                      "filter_below": filter_below, "filter_over": filter_over})

        # Filtering
        if filter_below is not None or filter_over is not None:
            envelope = envelope.filter_frequencies(filter_below, filter_over, name, verbosity)

        return envelope

    # noinspection PyArgumentList
    def get_pitch(self, method="parselmouth", filter_below=None, filter_over=None, name=None, zeros_as_nan=False,
                  verbosity=1):
        """Calculates the pitch of the voice in the audio clip, and returns a Pitch object.

        .. versionadded:: 2.0

        Parameters
        ----------
        method: str, optional
            Defines the pitch tracking method used. If set on ``"parselmouth"`` (default), the to_pitch method from
            Parselmouth will be used to get the pitch. If set on `"crepe"`, the CREPE Python module will be used.

        filter_below: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the lowest frequency of the band-pass filter.

        filter_over: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the highest frequency of the band-pass filter.

        name: str or None, optional
            Defines the name of the pitch. If set on ``None``, the name will be the same as the original Audio
            instance, with the suffix ``"(PIT)"``.

        zeros_as_nan: bool, optional
            If set on True, the values where the pitch is equal to 0 will be replaced by
            `numpy.nan <https://numpy.org/doc/stable/reference/constants.html#numpy.nan>`_ objects.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Pitch
            The pitch of the voice in the audio clip.

        Example
        -------
        >>> audio = Audio("Recordings/Silvestri/recording_13.wav")
        >>> pitch = audio.get_pitch(filter_over=50)
        """
        if verbosity > 0:
            print("Creating a Pitch object...")

        if method == "crepe":
            try:
                import crepe
            except ImportError:
                raise ModuleNotFoundException("crepe", "get the pitch of an audio clip.")

        samples = np.array(self.samples, dtype=np.float64)

        if verbosity > 0:
            if method == "parselmouth":
                print("\tTurning the audio into a parselmouth object...", end=" ")
            else:
                print("\tGetting the pitch from crepe...", end=" ")

        if method == "parselmouth":
            parselmouth_sound = Sound(np.ndarray(np.shape(samples), dtype=np.float64, buffer=samples), self.frequency)

            if name is None:
                name = self.name + " (PIT)"

            if verbosity > 0:
                print("Done.")
                print("\tGetting the pitch...", end=" ")

            parselmouth_pitch = parselmouth_sound.to_pitch(time_step=1 / self.frequency)

            if verbosity > 0:
                print("Done.")
                print("\tPadding the data...", end=" ")

            original_data_length = len(parselmouth_pitch.xs())
            samples, timestamps = pad(parselmouth_pitch.selected_array["frequency"], parselmouth_pitch.xs(),
                                      self.timestamps, verbosity=verbosity)

            if zeros_as_nan:
                samples[samples == 0] = np.nan

            if verbosity > 0:
                print(f"The calculated pitch contained {original_data_length} samples. Padding the data added "
                      f"{len(samples) - original_data_length} samples, to reach {len(samples)} samples.")

            pitch = Pitch(samples, self.frequency, self.name, self.condition, verbosity=verbosity)

        else:
            _, frequency, confidence, activation = crepe.predict(samples, self.frequency, viterbi=True)

            pitch = Pitch(frequency, self.frequency, self.name, self.condition, verbosity=verbosity)

        pitch._set_attributes_from_other_object(self)
        pitch.metadata["processing_steps"].append({"processing_type": "get_pitch",
                                                   "original_audio": self.name, "original_path": self.path,
                                                   "method": method, "zeros_as_nan": zeros_as_nan,
                                                   "filter_below": filter_below, "filter_over": filter_over})

        if filter_below is not None or filter_over is not None:
            pitch = pitch.filter_frequencies(filter_below, filter_over, name, verbosity)

        return pitch

    # noinspection PyArgumentList
    def get_intensity(self, filter_below=None, filter_over=None, name=None, zeros_as_nan=False, verbosity=1):
        """Calculates the intensity of the voice in the audio clip, and returns an Intensity object. The function can
        also optionally perform a band-pass filtering and a resampling, if the corresponding parameters are provided.

        .. versionadded:: 2.0

        Parameters
        ----------
        filter_below: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the lowest frequency of the band-pass filter.

        filter_over: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the highest frequency of the band-pass filter.

        name: str or None, optional
            Defines the name of the intensity. If set on ``None``, the name will be the same as the original Audio
            instance, with the suffix ``"(INT)"``.

        zeros_as_nan: bool, optional
            If set on True, the values where the intensity is equal to 0 will be replaced by
            `numpy.nan <https://numpy.org/doc/stable/reference/constants.html#numpy.nan>`_ objects.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Intensity
            The intensity of the voice in the audio clip.

        Example
        -------
        >>> audio = Audio("Recordings/Horner/recording_14.wav")
        >>> intensity = audio.get_intensity(filter_over=50)
        """
        if verbosity > 0:
            print("Creating an Intensity object...")

        samples = np.array(self.samples, dtype=np.float64)

        if verbosity > 0:
            print("\tTurning the audio into a parselmouth object...", end=" ")

        parselmouth_sound = Sound(np.ndarray(np.shape(samples), dtype=np.float64, buffer=samples), self.frequency)

        if name is None:
            name = self.name + " (INT)"

        if verbosity > 0:
            print("Done.")
            print("\tGetting the intensity...", end=" ")

        parselmouth_intensity = parselmouth_sound.to_intensity(time_step=1 / self.frequency)

        intensity_timestamps = add_delay(parselmouth_intensity.xs(), -parselmouth_intensity.xs()[0] % (1 / self.frequency))

        if verbosity > 0:
            print("Done.")
            print("\tPadding the data...", end=" ")

        samples, timestamps = pad(parselmouth_intensity.values[0], intensity_timestamps, self.timestamps,
                                  verbosity=verbosity)

        if zeros_as_nan:
            samples[samples == 0] = np.nan

        if verbosity > 0:
            print("Done.")

        intensity = Intensity(samples, self.frequency, name, self.condition, verbosity=verbosity)
        intensity._set_attributes_from_other_object(self)

        intensity.metadata["processing_steps"].append({"processing_type": "get_intensity",
                                                       "original_audio": self.name, "original_path": self.path,
                                                       "zeros_as_nan": zeros_as_nan,
                                                       "filter_below": filter_below, "filter_over": filter_over})

        if filter_below is not None or filter_over is not None:
            intensity = intensity.filter_frequencies(filter_below, filter_over, name, verbosity)

        return intensity

    # noinspection PyArgumentList
    def get_formant(self, formant_number=1, filter_below=None, filter_over=None, name=None, zeros_as_nan=False,
                    verbosity=1):
        """Calculates the formants of the voice in the audio clip, and returns a Formant object.

        .. versionadded:: 2.0

        Parameters
        ----------
        formant_number: int, optional.
            One of the formants of the voice in the audio clip (1 (default), 2, 3, 4 or 5).

        filter_below: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the lowest frequency of the band-pass filter.

        filter_over: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the highest frequency of the band-pass filter.

        name: str or None, optional
            Defines the name of the intensity. If set on ``None``, the name will be the same as the original Audio
            instance, with the suffix ``"(Fn)"``, with n being the formant number.

        zeros_as_nan: bool, optional
            If set on True, the values where the pitch is equal to 0 will be replaced by
            `numpy.nan <https://numpy.org/doc/stable/reference/constants.html#numpy.nan>`_ objects.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Formant
            The value of a formant of the voice in the audio clip.

        Example
        -------
        >>> audio = Audio("Recordings/Beck/recording_15.wav")
        >>> formant = audio.get_formant(formant_number=1, filter_over=50)
        """
        if verbosity > 0:
            print("Creating a Formant object...")

        if verbosity > 0:
            print("\tTurning the audio into a parselmouth object...", end=" ")

        samples = np.array(self.samples, dtype=np.float64)
        parselmouth_sound = Sound(np.ndarray(np.shape(samples), dtype=np.float64, buffer=samples), self.frequency)

        if verbosity > 0:
            print("Done.")
            print("\tGetting the formant...", end=" ")

        if name is None:
            name = self.name + " (F" + str(formant_number) + ")"

        parselmouth_formant = parselmouth_sound.to_formant_burg(time_step=1 / self.frequency)
        formant_timestamps = parselmouth_formant.xs()

        if verbosity > 0:
            print("Done.")
            print("\tPadding the data...", end=" ")

        number_of_points = parselmouth_formant.get_number_of_frames()
        f = np.zeros(number_of_points)
        for i in range(1, number_of_points + 1):
            t = parselmouth_formant.get_time_from_frame_number(i)
            f[i-1] = parselmouth_formant.get_value_at_time(formant_number=formant_number, time=t)
        f, timestamps = pad(f, formant_timestamps, self.timestamps)

        if verbosity > 0:
            print("Done.")

        formant = Formant(f, self.frequency, formant_number, name, self.condition, verbosity=verbosity)
        formant._set_attributes_from_other_object(self)

        formant.metadata["processing_steps"].append({"processing_type": "get_formant",
                                                     "original_audio": self.name, "original_path": self.path,
                                                     "formant_number": formant_number, "zeros_as_nan": zeros_as_nan,
                                                     "filter_below": filter_below, "filter_over": filter_over})

        if filter_below is not None or filter_over is not None:
            formant = formant.filter_frequencies(filter_below, filter_over, name, verbosity)

        return formant

    def get_derivative(self, derivative, filter_below=None, filter_over=None, resampling_frequency=None,
                       resampling_mode="pchip", res_window_size=1e7, res_overlap_ratio=0.5, timestamp_start=None,
                       timestamp_end=None, name=None, verbosity=1, **kwargs):

        """Computes and returns the requested AudioDerivative.

        .. versionadded:: 2.0

        Parameters
        ---------
        derivative: str
            The time series to be returned, among:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``
            • ``"pitch"``
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"`

        filter_below: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the lowest frequency of the band-pass filter.

        filter_over: int, float or None, optional
            If not ``None`` nor 0, this value will be provided as the highest frequency of the band-pass filter.`

        resampling_frequency: float
            The frequency, in hertz, at which you want to resample the audio clip. A frequency of 4 will return samples
            at 0.25 s intervals.

        resampling_mode: str, optional
            This parameter allows for all the values accepted for the ``kind`` parameter in the function
            :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
            ``"slinear"``, ``"quadratic"``, ``"cubic"``, ``"previous"``, and ``"next"``. See the `documentation
            for this Python module
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.
            This parameter also allows another special value, ``"take"``, which keeps one out of :math:`n` samples,
            where :math:`n` is equal to the original frequency divided by the resampling frequency. This allows for
            faster computation. Note that this function will return a warning if the resampling frequency is not an
            integer divider of the original frequency.

        res_window_size: int, optional
            The size of the windows in which to cut the audio samples to perform the resampling. Cutting long arrays
            in windows allows to speed up the computation. If this parameter is set on `None`, the window size will be
            set on the number of samples. A good value for this parameter is generally 10 million (1e7). If this
            parameter is set on 0, on None or on a number of samples bigger than the amount of samples in the Audio
            instance, the window size is set on the length of the samples.

        res_overlap_ratio: float, optional
            The ratio of samples overlapping between each window. If this parameter is not `None`, each window will
            overlap with the previous (and, logically, the next) for an amount of samples equal to the number of samples
            in a window times the overlap ratio. Then, only the central values of each window will be preserved and
            concatenated; this allows to discard any "edge" effect due to the windowing. If the parameter is set on
            `None` or 0, the windows will not overlap. By default, this parameter is set on 0.5, meaning that each
            window will overlap for half of their values with the previous, and half of their values with the next.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the
            output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the
            output.

        name: str or None, optional
            Defines the name of the output audio derivative. If set on ``None``, the name will be the same as the input
            audio clip, with suffixes matching the applied procedure (``"(ENV)"`` for envelope, ``"(PIT)"`` for pitch,
            ``"(INT)"`` for intensity, ``"(Fn)"`` for formant (with the n matching the requested formant), ``"+RS"``
            if a resampling was performed, ``"+TR"`` if a trimming was performed).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        **kwargs: dict
            Any of the parameters needed for the specific sub-functions: :meth:`Audio.get_envelope`,
            :meth:`Audio.get_pitch`, :meth:`Audio.get_intensity`, and :meth:`Audio.get_formant`.

        Returns
        -------
        AudioDerivative
            The requested AudioDerivative instance.

        Examples
        --------
        >>> audio = Audio("Recordings/Kondo/recording_16.wav")
        >>> envelope = audio.get_derivative("envelope", filter_over=50)
        >>> pitch = audio.get_derivative("pitch", filter_over=50, zeros_as_nan=True)
        >>> intensity = audio.get_derivative("intensity", filter_over=50, name="Kondo_intensity")
        >>> f1 = audio.get_derivative("formant", formant_number=1, filter_over=50)
        >>> f2 = audio.get_derivative("f2", filter_over=50)
        """

        if derivative == "audio":
            audio_derivative = self.filter_frequencies(filter_below, filter_over, name, verbosity)
        elif derivative == "envelope":
            audio_derivative = self.get_envelope(filter_below=filter_below, filter_over=filter_over, name=name,
                                                 verbosity=verbosity, **kwargs)
        elif derivative == "pitch":
            audio_derivative = self.get_pitch(filter_below=filter_below, filter_over=filter_over, name=name,
                                              verbosity=verbosity, **kwargs)
        elif derivative == "intensity":
            audio_derivative = self.get_intensity(filter_below=filter_below, filter_over=filter_over, name=name,
                                                  verbosity=verbosity, **kwargs)
        elif derivative in ["formant", "f1", "f2", "f3", "f4", "f5"]:
            if derivative != "formant" and "formant_number" not in kwargs:
                kwargs["formant_number"] = int(derivative[1])
            audio_derivative = self.get_formant(filter_below=filter_below, filter_over=filter_over, name=name,
                                                verbosity=verbosity, **kwargs)
        else:
            raise InvalidParameterValueException("derivative", derivative,
                                                 ["audio", "envelope", "pitch", "intensity", "formant"])

        if resampling_frequency is not None:
            audio_derivative = audio_derivative.resample(resampling_frequency, resampling_mode, res_window_size,
                                                         res_overlap_ratio, name, verbosity)

        if timestamp_start is not None or timestamp_end is not None:
            audio_derivative = audio_derivative.trim(timestamp_start, timestamp_end, name, verbosity)

        return audio_derivative

    # noinspection PyTupleAssignmentBalance
    def filter_frequencies(self, filter_below=None, filter_over=None, name=None, verbosity=1):
        """Applies a low-pass, high-pass or band-pass filter to the data in the attribute :attr:`samples`.

        .. versionadded: 2.0

        Parameters
        ----------
        filter_below: float or None, optional
            The value below which you want to filter the data. If set on None or 0, this parameter will be ignored.
            If this parameter is the only one provided, a high-pass filter will be applied to the samples; if
            ``filter_over`` is also provided, a band-pass filter will be applied to the samples.

        filter_over: float or None, optional
            The value over which you want to filter the data. If set on None or 0, this parameter will be ignored.
            If this parameter is the only one provided, a low-pass filter will be applied to the samples; if
            ``filter_below`` is also provided, a band-pass filter will be applied to the samples.

        name: str or None, optional
            Defines the name of the output audio. If set on ``None``, the name will be the same as the
            original audio derivative, with the suffix ``"+FF"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Audio
            The Audio instance, with filtered values.

        Example
        -------
        >>> audio = Audio("Recordings/Shore/recording_17.wav")
        >>> audio_ff = audio.filter_frequencies(filter_below=10, filter_over=50)
        """

        # Band-pass filter
        if filter_below not in [None, 0] and filter_over not in [None, 0]:
            if verbosity > 0:
                print("Applying a band-pass filter for frequencies between " + str(filter_below) + " and " +
                      str(filter_over) + " Hz...", end=" ")
            b, a = butter(2, [filter_below, filter_over], "band", fs=self.frequency)
            new_samples = lfilter(b, a, self.samples)

        # High-pass filter
        elif filter_below not in [None, 0]:
            if verbosity > 0:
                print("Applying a high-pass filter for frequencies over " + str(filter_below) + " Hz...", end=" ")
            b, a = butter(2, filter_below, "high", fs=self.frequency)
            new_samples = lfilter(b, a, self.samples)

        # Low-pass filter
        elif filter_over not in [None, 0]:
            if verbosity > 0:
                print("Applying a low-pass filter for frequencies below " + str(filter_over) + " Hz...", end=" ")
            b, a = butter(2, filter_over, "low", fs=self.frequency)
            new_samples = lfilter(b, a, self.samples)

        else:
            new_samples = self.samples

        if verbosity > 0:
            print("Done.")

        if name is None:
            name = self.name + " +FF"

        new_audio = Audio(new_samples, self.frequency, name, verbosity=0)
        new_audio._set_attributes_from_other_audio(self)

        new_audio.metadata["processing_steps"].append({"processing_type": "filter_frequencies",
                                                       "filter_below": filter_below, "filter_over": filter_over})
        return new_audio

    def resample(self, frequency, method="cubic", window_size=1e7, overlap_ratio=0.5, name=None, verbosity=1):
        """Resamples an audio clip to the `frequency` parameter. It first creates a new set of timestamps at the
        desired frequency, and then interpolates the original data to the new timestamps.

        .. versionadded:: 2.0

        Parameters
        ----------
        frequency: float
            The frequency, in hertz, at which you want to resample the audio clip. A frequency of 4 will return samples
            at 0.25 s intervals.

        method: str, optional
            This parameter allows for all the values accepted for the ``kind`` parameter in the function
            :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
            ``"slinear"``, ``"quadratic"``, ``"cubic"``, ``"previous"``, and ``"next"``. See the `documentation
            for this Python module
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.
            This parameter also allows another special value, ``"take"``, which keeps one out of :math:`n` samples,
            where :math:`n` is equal to the original frequency divided by the resampling frequency. This allows for
            faster computation. Note that this function will return a warning if the resampling frequency is not an
            integer divider of the original frequency.

        window_size: int, optional
            The size of the windows in which to cut the audio samples to perform the resampling. Cutting long arrays
            in windows allows to speed up the computation. If this parameter is set on `None`, the window size will be
            set on the number of samples. A good value for this parameter is generally 10 million (1e7). If this
            parameter is set on 0, on None or on a number of samples bigger than the amount of samples in the Audio
            instance, the window size is set on the length of the samples.

        overlap_ratio: float, optional
            The ratio of samples overlapping between each window. If this parameter is not `None`, each window will
            overlap with the previous (and, logically, the next) for an amount of samples equal to the number of samples
            in a window times the overlap ratio. Then, only the central values of each window will be preserved and
            concatenated; this allows to discard any "edge" effect due to the windowing. If the parameter is set on
            `None` or 0, the windows will not overlap. By default, this parameter is set on 0.5, meaning that each
            window will overlap for half of their values with the previous, and half of their values with the next.

        name: str or None, optional
            Defines the name of the output audio clip. If set on ``None``, the name will be the same as the input
            audio clip, with the suffix ``"+RS n"`` with n being the value of `frequency`.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        Audio
            A new audio clip containing resampled timestamps and samples.

        Warning
        -------
        This function allows both the **upsampling** and the **downsampling** of audio clips. However, during any of
        these operations, the algorithm only **estimates** the real values of the samples. You should then consider
        the upsampling (and the downsampling, to a lesser extent) with care.
        You can control the frequency of the original audio clip with :meth:`Audio.get_frequency()`.

        Example
        -------
        >>> audio = Audio("Recordings/Raine/recording_18.wav")
        >>> audio_resampled = audio.resample(2000, "cubic")
        """

        if verbosity > 0:
            print("Resampling the audio clip at " + str(frequency) + " Hz (mode: " + str(method) + ")...")
            print("\tOriginal frequency: " + str(round(self.get_frequency(), 2)))

        if verbosity > 0:
            print("\tPerforming the resampling...", end=" ")

        if window_size == 0 or window_size is None:
            window_size = len(self.samples)

        if overlap_ratio is None:
            overlap_ratio = 0

        resampled_audio_array, resampled_audio_times = resample_data(self.samples, self.timestamps, frequency,
                                                                     window_size, overlap_ratio, method,
                                                                     verbosity=verbosity)
        resampled_audio_array = list(resampled_audio_array)

        if name is None:
            name = self.name + " +RS " + str(frequency)

        new_audio = Audio(resampled_audio_array, frequency, name, verbosity=verbosity)
        new_audio.path = self.path

        if verbosity > 0:
            print("100% - Done.")
            print("\tOriginal audio had " + str(len(self.samples)) + " samples.")
            print("\tNew audio has " + str(len(new_audio.samples)) + " samples.\n")

        new_audio._set_attributes_from_other_audio(self)
        new_audio.metadata["processing_steps"].append({"processing_type": "resample",
                                                       "frequency": frequency,
                                                       "method": method,
                                                       "window_size": window_size,
                                                       "overlap_ratio": overlap_ratio})

        return new_audio

    def trim(self, start=None, end=None, name=None, error_if_out_of_bounds=False, verbosity=1, add_tabs=0):
        """Trims an audio clip according to a starting and an ending timestamps. Timestamps must be provided in seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        start: int or None, optional
            The timestamp after which the samples will be preserved (inclusive). If set on ``None``, or if set on a
            value lower than the first timestamp, the beginning of the audio will be set as the timestamp of the
            first sample.

        end: int or None, optional
            The timestamp before which the samples will be preserved (inclusive). If set on ``None``, or if set on a
            value higher than the last timestamp, the end of the audio will be set as the timestamp of the last sample.

        name: str or None, optional
            Defines the name of the output audio clip. If set on ``None``, the name will be the same as the input
            audio clip, with the suffix ``"+TR"``.

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
        Audio
            A new Audio instance containing a subset of the samples of the original.

        Example
        -------
        >>> audio = Audio("Recordings/Holt/recording_19.wav")
        >>> audio_trimmed = audio.trim(10, 15)
        """

        start_index = None
        end_index = None

        tabs = add_tabs * "\t"

        if start is None:
            start = self.timestamps[0]
            start_index = 0
        if end is None:
            end = self.timestamps[-1]
            end_index = -1

        if end < start:
            raise Exception("End timestamp should be inferior to beginning timestamp.")

        if error_if_out_of_bounds:
            if not 0 <= start <= self.get_duration():
                raise Exception(f"The start timestamp should be between 0 and {self.get_duration()}.")
            elif not 0 <= end <= self.get_duration():
                raise Exception(f"The end timestamp should be between 0 and {self.get_duration()}.")

        if verbosity > 0:
            print(tabs + "Trimming the audio:")
            print(tabs + "\tStarting timestamp: " + str(start) + " seconds")
            print(tabs + "\tEnding timestamp: " + str(end) + " seconds")
            print(tabs + "\tOriginal duration: " + str(self.get_duration()) + " seconds")
            print(tabs + "\tDuration after trimming: " + str(end - start) + " seconds")
        if verbosity == 1:
            print(tabs + "Starting the trimming...", end=" ")

        if name is None:
            name = self.name + " +TR"

        if start_index is None:
            start_index = int(np.floor(start * self.frequency))
            if start_index < 0:
                start_index = 0

        if verbosity > 1:
            print(tabs + f"Closest (above) starting timestamp from {start}: {self.timestamps[start_index]}")

        if end_index is None:
            end_index = int(np.ceil(end * self.frequency))
        if end_index > len(self.timestamps) - 1:
            end_index = len(self.timestamps) - 1

        if verbosity > 1:
            print(tabs + f"Closest (below) starting timestamp from {end}: {self.timestamps[end_index]}")

        new_audio = Audio(self.samples[start_index:end_index + 1], self.frequency, name, self.condition, verbosity)
        new_audio._set_attributes_from_other_audio(self)

        new_audio.metadata["processing_steps"].append({"processing_type": "trim",
                                                       "start": start,
                                                       "end": end})
        return new_audio

    def _set_attributes_from_other_audio(self, other):
        """Sets the attributes `condition`, `path` and `metadata` of the Audio from another instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Audio
            Another Audio instance, from which to copy some of the parameters.
        """
        self.path = other.path
        self.condition = other.condition
        self.metadata = copy.deepcopy(other.metadata)

    def find_excerpt(self, other, **kwargs):
        """This function tries to find the timestamp at which an excerpt of the current Audio instance begins.
        The computation is performed through cross-correlation, by first turning the audio clips into filtered envelopes
        and downsampling them to accelerate the processing. The function returns the timestamp or the index of the
        maximal correlation value, or `None` if this value is below threshold.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Audio
            An Audio instance, smaller than or of equal size to the current object, that is allegedly an excerpt from
            the current Audio instance. The amplitude, frequency or values do not have to match exactly the ones from
            the current Audio instance.

        **kwargs: dict
            Any of the parameters needed for the function
            `find_delay <https://find-delay.readthedocs.io/en/latest/find_delay.html>`_.

        Returns
        -------
        int, float, timedelta or None
            The sample index, timestamp or timedelta of the current Audio instance at which the excerpt can be found,
            or `None` if the excerpt is not contained in the current Audio instance.
        float or None, optional
            Optionally, if ``return_correlation_value`` is `True`, the correlation value at the corresponding
            index/timestamp.

        Example
        -------
        >>> audio = Audio("Recordings/Davis/recording_20.wav")
        >>> audio_excerpt = audio.trim(12, 15)
        >>> audio.find_excerpt(audio_excerpt, return_delay_format="s")
        12
        """
        return find_delay(self.samples, other.samples, self.frequency, other.frequency, **kwargs)

    def find_excerpts(self, excerpts, **kwargs):
        """This function tries to find the timestamp at which multiple excerpts of the current Audio instance begin.
        The computation is performed through cross-correlation, by first turning the audio clips into downsampled and
        filtered envelopes to accelerate the processing. For each excerpt, the function returns the timestamp of the
        maximal correlation value, or `None` if this value is below threshold.

        .. versionadded:: 2.0

        Parameters
        ----------
        excerpts: list(Audio)
            A list of Audio instances, smaller than or of equal size to the current object, that are all allegedly
            excerpts from current Audio instance. The amplitude, frequency or values do not have to match exactly the
            ones from the current Audio instance.

        **kwargs: dict
            Any of the parameters needed for the function
            `find_delay <https://find-delay.readthedocs.io/en/latest/find_delays.html>`_.

        Returns
        -------
        int|float|timedelta|None
            The sample index, timestamp or timedelta of array1 at which array2 can be found (defined by the parameter
            return_delay_format), or None if array1 is not contained in array2.

        float|None, optional
            Optionally, if return_correlation_value is True, the correlation value at the corresponding index/timestamp.

        Example
        -------
        >>> audio = Audio("Recordings/Beal/recording_21.wav")
        >>> audio_excerpt_1 = audio.trim(12, 15)
        >>> audio_excerpt_2 = audio.trim(15, 18)
        >>> audio_excerpt_3 = audio.trim(18, 21)
        >>> audio.find_excerpt([audio_excerpt_1, audio_excerpt_2, audio_excerpt_3], return_delay_format="s")
        [12, 15, 18]
        """
        return find_delays(self.samples, [other.samples for other in excerpts],
                           self.frequency, [other.frequency for other in excerpts], **kwargs)

    # === Conversion functions ===

    def to_table(self):
        """Returns a list of lists where each sublist contains a timestamp and a sample. The first sublist contains the
        headers of the table. The output then resembles the table found in :ref:`Tabled formats <table_example>`.

        .. versionadded:: 2.0

        Returns
        -------
        list(list)
            A list of lists that can be interpreted as a table, containing headers, and with the timestamps and the
            coordinates of the joints from the sequence on each row.

        Example
        -------
        >>> audio = Audio("Recordings/Elfman/recording_22.wav")
        >>> table = audio.to_table()
        >>> table[0:3]
        [["Timestamp", "Sample"],
         [0, 0.4815],
         [0.001, 0.1623],
         [0.002, 0.42]]
        """
        table = [["Timestamp", "Sample"]]

        # For each pose
        for s in range(len(self.samples)):
            table.append([self.timestamps[s], self.samples[s]])

        return table

    def to_json(self, include_metadata=True):
        """Returns a list ready to be exported in JSON. The returned JSON data is a dictionary with two keys:
        "Sample" is the key to the list of samples, while "Frequency" is the key to the sampling frequency of
        the audio clip.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`).

        Returns
        -------
        dict
            A dictionary containing the data of the audio clip, ready to be exported in JSON.

        Example
        -------
        >>> audio = Audio("Recordings/Newton-Howard/recording_23.wav")
        >>> json_data = audio.to_json()
        >>> json_data
        {"Timestamp": [0, 0.001, 0.002, 0.003], "Sample": [0, 0.4815, 0.1623, 0.42], "Frequency": 1000.0,
        "processing_steps": []}
        """

        if include_metadata:
            data = self.metadata.copy()
            for key in data:
                if type(data[key]) == datetime:
                    data[key] = str(data[key])
        else:
            data = {}

        data["Sample"] = self.samples.tolist()
        data["Timestamp"] = self.timestamps.tolist()
        data["Frequency"] = self.frequency

        return data

    def to_dict(self, include_frequency=True):
        """Returns a dictionary containing the data of the audio clip.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_frequency: bool, optional
            If set on `True`, includes the frequency of the audio clip in the output dictionary.

        Returns
        -------
        dict
            A dataframe containing the timestamps and samples of the audio clip.

            Example
        -------
        >>> audio = Audio("Recordings/Young/recording_24.wav")
        >>> dict_data = audio.to_dict()
        >>> dict_data
        {"Timestamp": [0, 0.001, 0.002, 0.003], "Sample": [0, 0.4815, 0.1623, 0.42], "Frequency": 1000.0}
        """
        data_dict = {"Timestamp": self.timestamps, "Sample": self.samples}
        if include_frequency:
            data_dict["Frequency"] = self.frequency
        return data_dict

    def to_dataframe(self):
        """Returns a Pandas dataframe containing the data of the audio clip.

        .. versionadded:: 2.0

        Returns
        -------
        Pandas.dataframe
            A dataframe containing the timestamps and samples of the audio clip.

        Example
        -------
        >>> audio = Audio("Recordings/Arnold/recording_25.tsv")
        >>> audio.to_dataframe()
            Timestamp   Sample
        0      0.000      4815
        1      0.001      1623
        2      0.002        42
        """
        data_dict = self.to_dict(False)
        return pd.DataFrame(data_dict)

    # === Saving functions ===
    def save(self, folder_out, name=None, file_format="json", encoding="utf-8", individual=False,
             include_metadata=True, verbosity=1):
        """Saves an audio clip in a file or a folder. The function saves the sequence under
        ``folder_out/name.file_format``. All the non-existent subfolders present in the ``folder_out`` path will be
        created by the function. The function also updates the :attr:`path` attribute of the Audio clip.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str, optional
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them. If the string provided is empty (by default), the audio clip will be saved in
            the current working directory. If the string provided contains a file with an extension, the fields ``name``
            and ``file_format`` will be ignored.

        name: str or None, optional
            Defines the name of the file or files where to save the audio clip. If set on ``None``, the name will be set
            on the attribute :attr:`name` of the audio clip; if that attribute is also set on ``None``, the name will be
            set on ``"out"``. If ``individual`` is set on ``True``, each sample will be saved as a different file,
            having the index of the pose as a suffix after the name (e.g. if the name is ``"sample"`` and the file
            format is ``"txt"``, the poses will be saved as ``sample_0.txt``, ``sample_1.txt``, ``sample_2.txt``, etc.).

        file_format: str or None, optional
            The file format in which to save the audio clip. The file format must be ``"json"`` (default), ``"xlsx"``,
            ``"txt"``, ``"csv"``, ``"tsv"``, ``"wav"``, or, if you are a masochist, ``"mat"``. Notes:

                • ``"xls"`` will save the file with an ``.xlsx`` extension.
                • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
                • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
                  on ``,``. By default, the function will detect which separator the system uses.
                • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
                • Any other string will not return an error, but rather be used as a custom extension. The data will
                  be saved as in a text file (using tabulations as values separators).

            .. warning::
                While it is possible to save audio clips as ``.mat`` or custom extensions, the toolbox will not
                recognize these files upon opening. The support for ``.mat`` and custom extensions as input may come in
                a future release, but for now these are just offered as output options.

        encoding: str, optional
            The encoding of the file to save (not applicable for WAV files). By default, the file is saved in UTF-8
            encoding. This input can take any of the
            official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        individual: bool, optional
            If set on ``False`` (default), the function will save the audio clip in a unique file.
            If set on ``True``, the function will save each sample of the audio clip in an individual file, appending an
            underscore and the index of the sample (starting at 0) after the name.
            This option is not available and will be ignored if ``file_format`` is set on ``"wav"``.

            .. warning::
                It is not recommended to save each sample in a different file. This incredibly tedious way of handling
                audio files has only been implemented to follow the same logic as for the Sequence files, and should be
                avoided.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`). This parameter does not apply to individually
            saved files.

                • For ``json`` files, the metadata is saved at the top level. Metadata keys will be saved next to the
                  ``"Poses"`` key.
                • For ``mat`` files, the metadata is saved at the top level of the structure.
                • For ``xlsx```files, the metadata is saved in a second sheet.
                • For ``pkl`` files, the metadata will always be saved as the object is saved as-is - this parameter
                  is thus ignored.
                • For ``wav`` files, the metadata is saved as tags in the file.
                • For all the other formats, the metadata is saved at the beginning of the file.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Examples
        --------
        >>> audio = Audio("Recordings/Bach/recording_26.wav")
        >>> audio.save("Recordings/Bach/recording_26.tsv")
        >>> audio.save("Recordings/Bach/recording_26.mat", include_metadata=False)
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
            self.save_json(folder_out, name, individual, include_metadata, encoding, verbosity)

        elif file_format == "mat":
            self.save_mat(folder_out, name, individual, include_metadata, verbosity)

        elif file_format == "xlsx":
            self.save_excel(folder_out, name, individual, include_metadata=include_metadata,
                            verbosity=verbosity)

        elif file_format in ["pickle", "pkl"]:
            self.save_pickle(folder_out, name, individual, verbosity)

        elif file_format == "wav":
            self.save_wav(folder_out, name, include_metadata, verbosity)

        else:
            self.save_txt(folder_out, name, file_format, encoding, individual, include_metadata, verbosity)

        if individual:
            self.path = op.join(folder_out, name)
        else:
            self.path = op.join(folder_out, name + "." + file_format)

        if verbosity > 0:
            print("100% - Done.")

    def save_json(self, folder_out, name=None, individual=False, include_metadata=True, encoding="utf-8",
                  verbosity=1):
        """Saves an audio clip as a json file or files. This function is called by the :meth:`Audio.save`
        method, and saves the Audio instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the audio clip. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the audio clip in a unique file.
            If set on ``True``, the function will save each sample of the audio clip in an individual file, appending an
            underscore and the index of the sample (starting at 0) after the name.

            .. warning::
                It is not recommended to save each sample in a different file. This incredibly tedious way of handling
                audio files has only been implemented to follow the same logic as for the Sequence files, and should be
                avoided.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`).

        encoding: str, optional
            The encoding of the file to save. By default, the file is saved in UTF-8 encoding. This input can take any
            of the
            `official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.


        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> audio = Audio("Recordings/Beethoven/recording_27.wav")
        >>> audio.save_json("Recordings/Beethoven/recording_27.json")
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

        data = self.to_json(include_metadata)

        if not individual:
            with open(path_out, 'w', encoding=encoding) as f:
                json.dump(data, f)
        else:
            if name is None:
                name = "pose"
            for s in range(len(self.samples)):
                perc = show_progression(verbosity, s, len(self.samples), perc)
                with open(op.join(folder_out, f"{name}_{s}.json"), 'w', encoding="utf-16-le") as f:
                    json.dump(data["Poses"][s], f)

        # Save the data
        if not individual:
            with open(path_out, 'w', encoding=encoding) as f:
                json.dump(data, f)
        else:
            if name is None:
                name = "sample"
            for s in range(len(self.samples)):
                perc = show_progression(verbosity, s, len(self.samples), perc)
                with open(op.join(folder_out, f"{name}_{s}.json"), 'w', encoding=encoding) as f:
                    json.dump({"Sample": self.samples[s], "Timestamp": self.timestamps[s]}, f)

    def save_mat(self, folder_out, name=None, individual=False, include_metadata=True, verbosity=1):
        """Saves an audio clip as a Matlab .mat file or files. This function is called by the :meth:`Audio.save`
        method, and saves the Audio instance as ``folder_out/name.file_format``.

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
            Defines the name of the file or files where to save the audio clip. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the audio clip in a unique file.
            If set on ``True``, the function will save each sample of the audio clip in an individual file, appending an
            underscore and the index of the sample (starting at 0) after the name.

            .. warning::
                It is not recommended to save each sample in a different file. This incredibly tedious way of handling
                audio files has only been implemented to follow the same logic as for the Sequence files, and should be
                avoided.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> audio = Audio("Recordings/Shostakovich/recording_28.wav")
        >>> audio.save_mat("Recordings/Shostakovich/recording_28.mat")
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
            data_json = self.to_json(include_metadata)
            for key in data_json:
                if data_json[key] is None:
                    data_json[key] = np.nan
            savemat(path_out, {"data": data_json})
        else:
            for s in range(len(self.samples)):
                if name is None:
                    name = "sample"
                data = {"sample": self.samples[s], "timestamp": self.timestamps[s]}
                perc = show_progression(verbosity, s, len(self.samples), perc)
                savemat(op.join(folder_out, f"{name}_{s}.mat"), {"data": data})

    def save_excel(self, folder_out, name=None, individual=False, sheet_name="Data", include_metadata=True,
                   metadata_sheet_name="Metadata", verbosity=1):
        """Saves an audio clip as an Excel .xlsx file or files. This function is called by the :meth:`Audio.save`
        method, and saves the Audio instance as ``folder_out/name.file_format``.

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
            Defines the name of the file or files where to save the audio clip. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the audio clip in a unique file.
            If set on ``True``, the function will save each sample of the audio clip in an individual file, appending an
            underscore and the index of the sample (starting at 0) after the name.

            .. warning::
                It is not recommended to save each sample in a different file. This incredibly tedious way of handling
                audio files has only been implemented to follow the same logic as for the Sequence files, and should be
                avoided.

        sheet_name: str|None, optional
            The name of the sheet containing the data. If `None`, a default name will be attributed to the sheet
            (``"Sheet"``).

        include_metadata: bool, optional
            Whether to include the metadata in the Excel file (default: `True`). The metadata is saved in a separate
            sheet in the same Excel file.

        metadata_sheet_name: str|None, optional
            The name of the sheet containing the metadata. If `None`, a default name will be attributed to the sheet
            (``"Metadata"``).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> audio = Audio("Recordings/Chopin/recording_29.wav")
        >>> audio.save_excel("Recordings/Chopin/recording_29.xlsx")
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

        data = self.to_table()

        # Save the data
        if not individual:
            if include_metadata:
                metadata = self.metadata
            else:
                metadata = None
            write_xlsx(data, path_out, sheet_name, metadata, metadata_sheet_name, verbosity)

        else:
            for s in range(len(self.samples)):
                if name is None:
                    name = "pose"
                data = [data[0], data[s + 1]]
                perc = show_progression(verbosity, s, len(self.samples), perc)
                write_xlsx(data, op.join(folder_out, f"{name}_{s}.xlsx"), sheet_name, verbosity=0)

    def save_pickle(self, folder_out, name=None, individual=False, verbosity=1):
        """Saves an audio clip by pickling it. This allows to reopen the audio clip as an Audio object.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files, or the complete path to the file.
            If one or more subfolders of the path do not exist, the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the audio. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``. This parameter is
            ignored if ``folder_out`` already contains the name of the file.

        individual: bool, optional
            If set on ``False`` (default), the function will save the audio clip in a unique file.
            If set on ``True``, the function will save each sample of the audio clip in an individual file, appending an
            underscore and the index of the sample (starting at 0) after the name.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> audio = Audio("Recordings/Saint-Saëns/recording_30.wav")
        >>> audio.save_pickle("Recordings/Saint-Saëns/recording_30.pkl")
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

        # Save the data
        if not individual:
            with open(path_out, "wb") as f:
                pickle.dump(self, f)

        else:
            for s in range(len(self.samples)):
                if name is None:
                    name = "pose"
                perc = show_progression(verbosity, s, len(self.samples), perc)
                with open(op.join(folder_out, f"{name}_{s}.pkl"), "wb") as f:
                    pickle.dump(self.samples[s], f)

    def save_wav(self, folder_out, name=None, include_metadata=True, verbosity=1):
        """Saves an audio clip as a .wav file or files. This function is called by the :meth:`Audio.save` method, and
        saves the Audio instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the audio clip. If set on ``None``, the name will be set
            on ``"out"``.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`). The metadata is saved on the first lines
            of the file. Note: due to WAV tags limitations, the case of the metadata might be modified.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Example
        -------
        >>> audio = Audio("Recordings/Mozart/recording_32.json")
        >>> audio.save_wav("Recordings/Mozart/recording_32.wav")
        """

        path_out = None
        subfolders = op.normpath(folder_out).split(os.sep)
        if len(subfolders) != 0:
            if "." in subfolders[-1]:
                path_out = folder_out
                file_format = op.splitext(subfolders[-1])[-1][1:]
            else:
                if name is None:
                    name = "out"
                if "." in name:
                    path_out = op.join(folder_out, name)
                else:
                    path_out = op.join(folder_out, f"{name}.wav")

        wavfile.write(path_out, self.frequency, self.samples)

        if include_metadata:
            with taglib.File(path_out, save_on_exit=True) as f:
                for key in self.metadata:
                    f.tags[key] = list(self.metadata[key])

    def save_txt(self, folder_out, name=None, file_format="csv", encoding="utf-8", individual=False,
                 include_metadata=True, verbosity=1):
        """Saves an audio clip as a .txt, .csv, .tsv, or custom extension file or files. This function is called by the
        :meth:`Audio.save` method, and saves the Audio instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the audio clip. If set on ``None``, the name will be set
            on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        file_format: str, optional
            The file format in which to save the audio clip. The file format can be ``"txt"``, ``"csv"`` (default) or
            ``"tsv"``. ``"csv;"`` will force the value separator on ``";"``, while ``"csv,"`` will force the separator
            on ``","``. By default, the function will detect which separator the system uses. ``"txt"`` and ``"tsv"``
            both separate the values by a tabulation. Any other string will not return an error, but rather be used as
            a custom extension. The data will be saved as in a text file (using tabulations as values separators).

        encoding: str, optional
            The encoding of the file to save. By default, the file is saved in UTF-8 encoding. This input can take any
            of the
            `official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        individual: bool, optional
            If set on ``False`` (default), the function will save the audio clip in a unique file.
            If set on ``True``, the function will save each sample of the audio clip in an individual file, appending an
            underscore and the index of the sample (starting at 0) after the name.

            .. warning::
                It is not recommended to save each sample in a different file. This incredibly tedious way of handling
                audio files has only been implemented to follow the same logic as for the Sequence files, and should be
                avoided.

        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`). The metadata is saved on the first lines
            of the file.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Examples
        --------
        >>> audio = Audio("Recordings/Vivaldi/recording_33.wav")
        >>> audio.save_txt("Recordings/Vivaldi/recording_33.txt")
        >>> audio.save_txt("Recordings/Vivaldi/recording_33.tsv", include_metadata=False)
        >>> audio.save_txt("Recordings/Vivaldi", "recording_33", "aaa", include_metadata=False)
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
            write_text_table(self.to_table(), separator, path_out, metadata, None, encoding,
                             verbosity=verbosity)
        else:
            table = self.to_table()
            for s in range(len(self.samples)):
                if name is None:
                    name = "sample"
                if s == 0:
                    metadata = self.metadata
                else:
                    metadata = None
                write_text_table([table[0], table[s+1]], separator,
                                 op.join(folder_out, f"{name}_{s}.{file_format}"), metadata,
                                 encoding=encoding, verbosity=0)
                perc = show_progression(verbosity, s, len(self.samples), perc)

    def copy(self):
        """Returns a deep copy of the Audio object.

        .. versionadded:: 2.0

        Returns
        -------
        Audio
            A new Audio object, copy of the original.

        Example
        -------
        >>> audio = Audio("Recordings/Tchaikovsky/recording_34.tsv")
        >>> audio_copy = audio.copy()
        """
        return super().copy()

    def __len__(self):
        """Returns the number of samples in the audio clip (i.e., the length of the attribute :attr:`samples`).

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of samples in the audio clip.

        Example
        -------
        >>> audio = Audio("Recordings/Din/recording_35.wav")
        >>> len(audio)
        88200
        """
        return len(self.samples)

    def __getitem__(self, index):
        """Returns the sample of index specified by the parameter ``index``.

        Parameters
        ----------
        index: int
            The index of the sample to return.

        Returns
        -------
        float
            A sample from the attribute :attr:`samples`.

        Example
        -------
        >>> audio = Audio("Recordings/Nayru/recording_36.wav")
        >>> audio[820]
        417
        """
        return self.samples[index]

    def __repr__(self):
        """Returns the :attr:`name` attribute of the audio clip.

        Returns
        -------
        str
            The attribute :attr:`name` of the Audio instance.

        Examples
        --------
        >>> audio = Audio("Recordings/Farore/recording_37.wav")
        >>> print(audio)
        recording_37

        >>> audio = Audio("Recordings/Farore/recording_37.wav", name="audio_37")
        >>> print(audio)
        audio_37
        """
        return self.name

    def __eq__(self, other):
        """Returns `True` if all the samples in the attribute :attr:`samples` have identical values between the two
        :class:`Audio` objects, and if the frequency is identical..

        .. versionadded:: 2.0

        Parameters
        ----------
        other: Audio
            Another :class:`Audio` object.
        """
        if len(self.samples) != len(other.samples):
            return False

        if self.frequency != other.frequency:
            return False

        return np.array_equal(self.samples, other.samples)
