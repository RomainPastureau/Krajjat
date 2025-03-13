"""Classes for time series derived from audio clips: Envelope, Intensity, Pitch and Formants."""
import copy
import pickle
from collections import OrderedDict

import taglib
from scipy.io import wavfile, loadmat, savemat

from krajjat.classes.exceptions import EmptyInstanceException
from krajjat.classes.time_series import TimeSeries
from krajjat.tool_functions import *

class AudioDerivative(TimeSeries):
    """Parent class for the Envelope, Intensity, Pitch and Formant methods. Contains common methods for each of the
    subclasses.
    """

    def __init__(self, kind, path_or_samples, frequency, name=None, condition=None, verbosity=1):
        super().__init__(kind, path_or_samples, name, condition, verbosity)

        self.samples = np.ndarray([])
        self.timestamps = np.ndarray([])
        self.frequency = frequency

        if type(path_or_samples) is str:
            self._load_from_path(verbosity)
        elif isinstance(path_or_samples, (list, np.ndarray)):
            self._load_from_samples(path_or_samples, frequency, verbosity)
        else:
            raise Exception("Invalid type for the argument path_or_samples: should be str or array.")

    def set_name(self, name):
        """Sets the :attr:`name` attribute of the AudioDerivative instance. This name can be used as a way to identify
        the original Audio instance from which the AudioDerivative has been created.

        .. versionadded:: 2.0

        Parameters
        ----------
        name : str
            A name to describe the audio derivative.

        Examples
        --------
        >>> aud = Audio("Recordings/Ross/audio.wav")
        >>> env = aud.get_envelope(filter_over=50)
        >>> env.set_name("Envelope 001")

        >>> pitch = Pitch("Recordings/Ross/pitch.tsv")
        >>> pitch.set_name("Pitch 001")
        """
        super().set_name(name)

    def set_condition(self, condition):
        """Sets the :py:attr:`condition` attribute of the AudioDerivative instance. This attribute can be used to save
        the experimental condition in which the AudioDerivative instance was recorded.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition: str
            The experimental condition in which the audio derivative was originally recorded.

        Examples
        --------
        >>> aud = Audio("Recordings/Rachel/audio.wav")
        >>> env = aud.get_envelope(filter_over=50)
        >>> env.set_condition("English")

        >>> pitch = Pitch("Recordings/Rachel/pitch.tsv")
        >>> pitch.set_condition("Spanish")
        """
        super().set_condition(condition)

    def _load_from_path(self, verbosity=1):
        """Loads the AudioDerivative data from the :attr:`path` provided during the initialization.

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
            print("Parameter path_or_samples detected as being a path.")

        super()._load_from_path(verbosity)

        self._load_samples(verbosity)

        if len(self.samples) == 0:
            raise EmptyInstanceException(self.kind)

    def _load_from_samples(self, samples, frequency, verbosity=1):
        """Loads the AudioDerivative data when samples and frequency have been provided upon initialisation.

        .. versionadded:: 2.0

        Parameters
        ----------
        samples: list(int) or numpy.ndarray(int)
            A list containing the samples, in chronological order.
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
        function calls either :meth:`AudioDerivative._load_single_sample_file` or
        :meth:`AudioDerivative._load_audio_file`.

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
            print(f"Opening {self.kind.lower()} from {self.path}...", end=" ")
        elif verbosity > 1:
            print(f"Opening {self.kind.lower()} from {self.path}...")
        perc = 10  # Used for the progression percentage

        # If the path is a folder, we load every single file
        if op.isdir(self.path):

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
            self._load_audio_derivative_file(verbosity)

    def _load_single_sample_file(self, sample_index, path, verbosity):
        """Loads the content of a single sample file into the AudioDerivative object. Depending on the file type, this
        function handles the content differently (see :ref:`Audio formats <wav_example>`).

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
            if op.splitext(self.path)[-1] not in [".csv", ".tsv", ".txt"]:
                if verbosity > 0:
                    print(f"Loading from non-standard extension {op.splitext(self.path)[-1]} as text...")

            separator = get_filetype_separator(file_extension[-1])

            # Open the file and read the data
            data, metadata = read_text_table(path)
            if sample_index == 0:
                self.metadata.update(metadata)
            self.samples[sample_index] = float(data[1][1])
            self.timestamps[sample_index] = float(data[1][0])

    def _load_audio_derivative_file(self, verbosity=1):
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
            print(f"\n\tOpening the {self.kind.lower()}...", end=" ")

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
                    if tag.lower() == "processing_steps":
                        self.metadata["processing_steps"] = json.loads("".join(file.tags[tag]))
                    elif tag.lower() == "formant_number":
                        self.metadata["formant_number"] = int(file.tags[tag][0])
                    else:
                        self.metadata[tag] = file.tags[tag][0]

            self._calculate_timestamps()

        elif file_extension == ".json":
            data = read_json(self.path)

            if len(data) == 0:
                raise EmptyInstanceException("Audio")

            self._load_json_metadata(data, verbosity)
            self.samples = np.array(data["Sample"])
            self.frequency = data["Frequency"]
            self._calculate_timestamps()

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
                if key == "Sample":
                    self.samples = pd.DataFrame(data["data"]["Sample"]).values.flatten()

                elif key == "Timestamp":
                    self.timestamps = pd.DataFrame(data["data"]["Timestamp"]).values.flatten()

                elif key == "Frequency":
                    self.frequency = data["data"]["Frequency"]

                elif key == "processing_steps" and len(data["data"]["processing_steps"]) == 0:
                    self.metadata["processing_steps"] = []

                else:
                    self.metadata[key] = data["data"][key]

            self._calculate_frequency()

        else:
            if file_extension not in [".csv", ".xlsx", ".tsv", ".txt"]:
                if verbosity > 0:
                    print(f"Loading from non-standard extension {file_extension} as text...")

            if self.path.split(".")[-1] == "xlsx":
                data, metadata = read_xlsx(self.path, verbosity=verbosity)
                if "processing_steps" in metadata.keys():
                    metadata["processing_steps"] = json.loads(metadata["processing_steps"])
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
        """Determines the frequency (number of samples per second) of the audio derivative by calculating the time
        elapsed between the two first timestamps. This function is automatically called when reading the timestamps and
        samples from a text file.

        .. versionadded:: 2.0
        """
        self.frequency = 1 / ((self.timestamps[-1] - self.timestamps[0]) / (len(self.timestamps) - 1))

    def _calculate_timestamps(self):
        """Calculates the timestamps of the samples from the frequency and the number of samples. This function
        is automatically called when initializing the AudioDerivative.

        .. versionadded:: 2.0
        """
        self.timestamps = np.arange(0, len(self.samples)) / self.frequency

    # === Getter functions ===
    def get_path(self):
        """Returns the attribute :attr:`path` of the AudioDerivative instance.

        . versionadded:: 2.0

        Returns
        -------
        str
            The path of the AudioDerivative instance.
        """
        return self.path

    def get_name(self):
        """Returns the attribute :attr:`name` of the AudioDerivative instance.

        . versionadded:: 2.0

        Returns
        -------
        str
            The name of the AudioDerivative instance.
        """
        return self.name

    def get_condition(self):
        """Returns the attribute :attr:`condition` of the AudioDerivative instance.

        . versionadded:: 2.0

        Returns
        -------
        str
            The condition of the AudioDerivative instance.
        """
        return self.condition

    def get_samples(self):
        """Returns the attribute :attr:`samples` of the audio derivative.

        .. versionadded:: 2.0

        Returns
        -------
        list(float) or numpy.ndarray(float64)
            An array containing the values for the audio derivative.
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
        """
        if len(self.samples) == 0:
            raise Exception(f"The {self.kind} does not have any sample.")
        elif not 0 <= sample_index < len(self.samples):
            raise Exception("The sample index must be between 0 and " + str(len(self.samples) - 1) + ". ")

        return self.samples[sample_index]

    def get_number_of_samples(self):
        """Returns the number of samples in the Audio derivative.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The amount of samples in the audio derivative.
        """
        return len(self.samples)

    def get_timestamps(self):
        """Returns the attribute :attr:`samples` of the audio derivative.

        .. versionadded:: 2.0

        Returns
        -------
        list(float) or numpy.ndarray(float64)
            An array containing the timestamps for each sample.
        """
        return self.timestamps

    def get_duration(self):
        """Returns the duration of the audio derivative, in seconds.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The duration of the audio derivative, in seconds.
        """
        return self.timestamps[-1]

    def get_frequency(self):
        """Returns the attribute :attr:`frequency` of the audio derivative.

        .. versionadded:: 2.0

        Returns
        -------
        int or float
            The frequency, in Hertz, at which the values in attr:`samples` are sampled.
        """
        return self.frequency

    def get_info(self, return_type="dict", include_path=True):
        """Returns information regarding the Audio derivative.

        .. versionadded:: 2.0

        Parameters
        ----------
        return_type: bool, optional
            If set on ``"dict"`` (default), the info is returned as an OrderedDict. If set on ``"table"``, the info
            is returned as a two-dimensional list, ready to be exported as a table. If set on ``"str"``, a printable
            string is returned.

        include_path: bool, optional
            If set on ``True``, the path of the audio derivative is included in the returned info (default).

        Returns
        -------
        OrderedDict
            An ordered dictionary where each descriptor is associated to its value. The included information fields are:

                • ``"Name"``: The :attr:`name` attribute of the audio derivative.
                • ``"Path"``: The :attr:`path` attribute of the audio derivative.
                • ``"Condition"``: The :attr:`condition` attribute of the audio derivative (if set).
                • ``"Frequency"``: Output of :meth:`AudioDerivative.get_frequency`.
                • ``"Number of samples"``: Output of :meth:`AudioDerivative.get_number_of_samples`.
                • ``"Duration"``: Output of :meth:`AudioDerivative.get_duration`.
        """
        infos = OrderedDict()
        infos["Name"] = self.name
        if include_path:
            infos["Path"] = self.path
        if self.condition is not None:
            infos["Condition"] = self.condition
        infos["Duration"] = self.get_duration()
        infos["Frequency"] = self.frequency
        infos["Number of samples"] = self.get_number_of_samples()

        if return_type.lower() in ["list", "table"]:
            table = [[], []]
            for key in infos.keys():
                table[0].append(key)
                table[1].append(infos[key])
            return table

        elif return_type.lower() == "str":
            return " · ".join([f"{key}: {infos[key]}" for key in infos.keys()])

        return infos

    # noinspection PyTupleAssignmentBalance
    # noinspection PyArgumentList
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
            Defines the name of the output audio derivative. If set on ``None``, the name will be the same as the
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
        AudioDerivative
            The AudioDerivative instance, with filtered values.
        """
        try:
            from scipy.signal import butter, lfilter
        except ImportError:
            raise ModuleNotFoundException("scipy", "apply a band-pass filter.")

        if filter_below not in [None, 0] and filter_over not in [None, 0]:
            if verbosity > 0:
                print("Applying a band-pass filter for frequencies between " + str(filter_below) + " and " +
                      str(filter_over) + " Hz...")
            b, a = butter(2, [filter_below, filter_over], "band", fs=self.frequency)
            new_samples = lfilter(b, a, self.samples)

        elif filter_below not in [None, 0]:
            if verbosity > 0:
                print("Applying a high-pass filter for frequencies over " + str(filter_below) + " Hz...")
            b, a = butter(2, filter_below, "high", fs=self.frequency)
            new_samples = lfilter(b, a, self.samples)

        elif filter_over not in [None, 0]:
            if verbosity > 0:
                print("Applying a low-pass filter for frequencies below " + str(filter_over) + " Hz...")
            b, a = butter(2, filter_over, "low", fs=self.frequency)
            new_samples = lfilter(b, a, self.samples)

        else:
            new_samples = self.samples

        if name is None:
            name = self.name + " +FF"

        if type(self) is Formant:
            new_audio_derivative = type(self)(new_samples, self.frequency, formant_number=self.formant_number,
                                              name=name, verbosity=verbosity)
        else:
            new_audio_derivative = type(self)(new_samples, self.frequency, name=name, verbosity=verbosity)

        new_audio_derivative._set_attributes_from_other_object(self)
        new_audio_derivative.metadata["processing_steps"].append({"processing_type": "filter_frequencies",
                                                                  "filter_below": filter_below,
                                                                  "filter_over": filter_over})
        return new_audio_derivative

    def resample(self, frequency, method="cubic", window_size=1e7, overlap_ratio=0.5, name=None, verbosity=1):
        """Resamples an audio derivative to the `frequency` parameter. This function first creates a new set of
        timestamps at the desired frequency, and then interpolates the original data to the new timestamps.

        .. versionadded:: 2.0

        Parameters
        ----------
        frequency: float
            The frequency, in hertz, at which you want to resample the audio derivative. A frequency of 4 will return
            samples at 0.25 s intervals.

        method: str, optional
            This parameter allows for all the values accepted for the ``kind`` parameter in the function
            :func:`scipy.interpolate.interp1d`: ``"linear"``, ``"nearest"``, ``"nearest-up"``, ``"zero"``,
            ``"slinear"``, ``"quadratic"``, ``"cubic"`` (default), ``"previous"``, and ``"next"``. See the
            `documentation for this Python module
            <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_ for more.

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
            Defines the name of the output audio derivative. If set on ``None``, the name will be the same as the
            original audio derivative, with the suffix ``"+RS"``.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        if verbosity > 0:
            print(f"Resampling the {self.kind} at {frequency} Hz (mode: {method})...")
            print("\tOriginal frequency: " + str(round(self.get_frequency(), 2)))
            print("\tPerforming the resampling...", end=" ")

        if window_size == 0 or window_size is None:
            window_size = len(self.samples)

        if overlap_ratio is None:
            overlap_ratio = 0

        samples_resampled, timestamps_resampled = resample_data(self.samples, self.timestamps, frequency,
                                                                window_size, overlap_ratio, method, verbosity=verbosity)

        if name is None:
            name = self.name + " +RS " + str(frequency)

        new_audio_derivative = type(self)(samples_resampled, frequency, name, verbosity=verbosity)
        new_audio_derivative._set_attributes_from_other_object(self)
        new_audio_derivative.metadata["processing_steps"].append({"processing_type": "resample",
                                                       "frequency": frequency,
                                                       "method": method,
                                                       "window_size": window_size,
                                                       "overlap_ratio": overlap_ratio})

        if verbosity > 0:
            print("100% - Done.")
            print(f"\tOriginal {self.kind.lower()} had {len(self.samples)} samples.")
            print(f"\tNew {self.kind.lower()} has {len(new_audio_derivative.samples)} samples.\n")

        return new_audio_derivative

    def trim(self, start=None, end=None, name=None, error_if_out_of_bounds=False, verbosity=1, add_tabs=0):
        """Trims an audio derivative according to a starting and an ending timestamps. Timestamps must be provided in
        seconds.

        .. versionadded:: 2.0

        Parameters
        ----------
        start: int or None, optional
            The timestamp after which the samples will be preserved. If set on ``None``, the beginning of the audio
            derivative will be set as the timestamp of the first sample.

        end: int or None, optional
            The timestamp before which the samples will be preserved. If set on ``None``, the end of the audio
            derivative will be set as the timestamp of the last sample.

        name: str or None, optional
            Defines the name of the output AudioDerivative instance. If set on ``None``, the name will be the same as
            the original AudioDerivative instance, with the suffix ``"+TR"``.

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
        AudioDerivative
            A new AudioDerivative instance containing a subset of the samples of the original.
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
            print(tabs + f"Trimming the {self.kind.lower()}:")
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

        new_audio_derivative = type(self)(self.samples[start_index:end_index + 1], self.frequency, name=name,
                                          condition=self.condition, verbosity=verbosity)
        new_audio_derivative._set_attributes_from_other_object(self)

        new_audio_derivative.metadata["processing_steps"].append({"processing_type": "trim",
                                                       "start": start,
                                                       "end": end})
        return new_audio_derivative

    def to_table(self):
        """Returns a list of lists where each sublist contains a timestamp and a sample. The first sublist contains the
        headers of the table. The output then resembles the table found in :ref:`Tabled formats <table_example>`.

        .. versionadded:: 2.0

        Returns
        -------
        list(list)
            A list of lists that can be interpreted as a table, containing headers, and with the timestamps and the
            sample value on each row.
        """
        table = [["Timestamp", "Sample"]]

        # For each pose
        for s in range(len(self.samples)):
            table.append([self.timestamps[s], self.samples[s]])

        return table

    def to_json(self, include_metadata=True):
        """Returns a list ready to be exported in JSON. The returned JSON data is a dictionary with three keys:
        "Timestamp" is the key to the list of timestamps, "Sample" is the key to the list of samples, and "Frequency"
        is the key to the sampling frequency of the AudioDerivative.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_metadata: bool, optional
            Whether to include the metadata in the file (default: `True`).

        Returns
        -------
        dict
            A dictionary containing the data of the audio derivative, ready to be exported in JSON.
        """

        if include_metadata:
            data = copy.deepcopy(self.metadata)
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
        """Returns a dictionary containing the data of the AudioDerivative.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_frequency: bool, optional
            If set on `True`, includes the frequency of the AudioDerivative in the output dictionary.

        Returns
        -------
        dict
            A dataframe containing the timestamps and samples of the AudioDerivative..
        """
        data_dict = {"Timestamp": self.timestamps, "Sample": self.samples}
        if include_frequency:
            data_dict["Frequency"] = self.frequency
        return data_dict

    def to_dataframe(self):
        """Returns a Pandas dataframe containing the data of the AudioDerivative.

        .. versionadded:: 2.0

        Returns
        -------
        Pandas.dataframe
            A dataframe containing the timestamps and samples of the AudioDerivative.
        """
        data_dict = self.to_dict(False)
        return pd.DataFrame(data_dict)

    def save(self, folder_out, name=None, file_format="json", encoding="utf-8", individual=False,
             include_metadata=True, verbosity=1):
        """Saves an audio derivative in a file or a folder. The function saves the sequence under
        ``folder_out/name.file_format``. All the non-existent subfolders present in the ``folder_out`` path will be
        created by the function. The function also updates the :attr:`path` attribute of the AudioDerivative.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str, optional
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them. If the string provided is empty (by default), the audio clip will be saved in
            the current working directory. If the string provided contains a file with an extension, the fields ``name``
            and ``file_format`` will be ignored.

        name: str or None, optional
            Defines the name of the file or files where to save the AudioDerivative. If set on ``None``, the name will
            be set on the attribute :attr:`name` of the AudioDerivative; if that attribute is also set on ``None``, the
            name will be set on ``"out"``. If ``individual`` is set on ``True``, each sample will be saved as a
            different file, having the index of the pose as a suffix after the name (e.g. if the name is ``"sample"``
            and the file format is ``"txt"``, the samples will be saved as ``sample_0.txt``, ``sample_1.txt``,
            ``sample_2.txt``, etc.).

        file_format: str or None, optional
            The file format in which to save the AudioDerivative. The file format must be ``"json"`` (default),
            ``"xlsx"``, ``"txt"``, ``"csv"``, ``"tsv"``, ``"wav"``, or, if you are a masochist, ``"mat"``. Notes:

                • ``"xls"`` will save the file with an ``.xlsx`` extension.
                • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
                • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
                  on ``,``. By default, the function will detect which separator the system uses.
                • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
                • Any other string will not return an error, but rather be used as a custom extension. The data will
                  be saved as in a text file (using tabulations as values separators).

        encoding: str, optional
            The encoding of the file to save (applicable for json and text-based files). By default, the
            file is saved in UTF-8 encoding. This input can take any of the
            official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        individual: bool, optional
            If set on ``False`` (default), the function will save the AudioDerivative in a unique file.
            If set on ``True``, the function will save each sample of the AudioDerivative in an individual file,
            appending an underscore and the index of the sample (starting at 0) after the name.
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
        """Saves an AudioDerivative as a json file or files. This function saves the AudioDerivative instance as
        ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the AudioDerivative. If set on ``None``, the name will
            be set on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the AudioDerivative in a unique file.
            If set on ``True``, the function will save each sample of the AudioDerivative in an individual file,
            appending an underscore and the index of the sample (starting at 0) after the name.

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
        """Saves an AudioDerivative as a Matlab .mat file or files. This function saves the AudioDerivative instance
        as ``folder_out/name.file_format``.

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
            Defines the name of the file or files where to save the AudioDerivative. If set on ``None``, the name will
            be set on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the AudioDerivative in a unique file.
            If set on ``True``, the function will save each sample of the AudioDerivative in an individual file,
            appending an underscore and the index of the sample (starting at 0) after the name.

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
                elif key == "processing_steps":
                    for i in range(len(data_json["processing_steps"])):
                        for param in data_json["processing_steps"][i]:
                            if data_json["processing_steps"][i][param] is None:
                                data_json["processing_steps"][i][param] = np.nan
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
        """Saves an AudioDerivative as an Excel .xlsx file or files. This function saves the AudioDerivative instance
        as ``folder_out/name.file_format``.

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
            Defines the name of the file or files where to save the AudioDerivative. If set on ``None``, the name will
            be set on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        individual: bool, optional
            If set on ``False`` (default), the function will save the AudioDerivative in a unique file.
            If set on ``True``, the function will save each sample of the AudioDerivative in an individual file, appending an
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
                metadata = copy.deepcopy(self.metadata)
                metadata["processing_steps"] = json.dumps(metadata["processing_steps"])
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
        """Saves an AudioDerivative by pickling it. This allows to reopen the content as an AudioDerivative object.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files, or the complete path to the file.
            If one or more subfolders of the path do not exist, the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the AudioDerivative. If set on ``None``, the name will
            be set on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``. This parameter
            is ignored if ``folder_out`` already contains the name of the file.

        individual: bool, optional
            If set on ``False`` (default), the function will save the AudioDerivative in a unique file.
            If set on ``True``, the function will save each sample of the AudioDerivative in an individual file,
            appending an underscore and the index of the sample (starting at 0) after the name.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
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
            for s in range(len(self.samples)):
                if name is None:
                    name = "pose"
                perc = show_progression(verbosity, s, len(self.samples), perc)
                with open(op.join(folder_out, f"{name}_{s}.pkl"), "wb") as f:
                    pickle.dump(self.samples[s], f)

    def save_wav(self, folder_out, name=None, include_metadata=True, verbosity=1):
        """Saves an AudioDerivative as a .wav file or files. This function saves the AudioDerivative instance as
        ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the AudioDerivative. If set on ``None``, the name will
            be set on ``"out"``.

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
                    if key == "processing_steps":
                        f.tags[key] = [json.dumps(self.metadata["processing_steps"])]
                    elif type(self.metadata[key]) == int:
                        f.tags[key] = [str(self.metadata[key])]
                    else:
                        f.tags[key] = [self.metadata[key]]

    def save_txt(self, folder_out, name=None, file_format="csv", encoding="utf-8", individual=False,
                 include_metadata=True, verbosity=1):
        """Saves an AudioDerivative as a .txt, .csv, .tsv, or custom extension file or files. This function saves
        the AudioDerivative instance as ``folder_out/name.file_format``.

        .. versionadded:: 2.0

        Parameters
        ----------
        folder_out: str
            The path to the folder where to save the file or files. If one or more subfolders of the path do not exist,
            the function will create them.

        name: str or None, optional
            Defines the name of the file or files where to save the AudioDerivative. If set on ``None``, the name will
            be set on ``"out"`` if individual is ``False``, or on ``"sample"`` if individual is ``True``.

        file_format: str, optional
            The file format in which to save the AudioDerivative clip. The file format can be ``"txt"``, ``"csv"``
            (default) or ``"tsv"``. ``"csv;"`` will force the value separator on ``";"``, while ``"csv,"`` will force
            the separator    on ``","``. By default, the function will detect which separator the system uses.
            ``"txt"`` and ``"tsv"`` both separate the values by a tabulation. Any other string will not return an error,
            but rather be used as a custom extension. The data will be saved as in a text file (using tabulations as
            values separators).

        encoding: str, optional
            The encoding of the file to save. By default, the file is saved in UTF-8 encoding. This input can take any
            of the
            `official Python accepted formats <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

        individual: bool, optional
            If set on ``False`` (default), the function will save the AudioDerivative in a unique file.
            If set on ``True``, the function will save each sample of the AudioDerivative in an individual file,
            appending an underscore and the index of the sample (starting at 0) after the name.

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
        """Returns a deep copy of the AudioDerivative object.

        .. versionadded:: 2.0

        Returns
        -------
        AudioDerivative
            A new AudioDerivative object, copy of the original.
        """
        return super().copy()

    def __len__(self):
        """Returns the number of samples in the audio derivative (i.e., the length of the attribute :attr:`samples`).

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of samples in the audio derivative.
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
        """
        return self.samples[index]

    def __repr__(self):
        """Returns the :attr:`name` attribute of the AudioDerivative.

        Returns
        -------
        str
            The attribute :attr:`name` of the AudioDerivative instance.
        """
        return self.name

    def __eq__(self, other):
        """Returns `True` if all the samples in the attribute :attr:`samples` have identical values between the two
        :class:`AudioDerivative` objects, and if the frequency is identical.

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


class Envelope(AudioDerivative):
    """This class contains the samples from the envelope of an audio clip.

    .. versionadded:: 2.0

    Parameters
    ----------
    samples: list(float) or numpy.ndarray(float64)
        The envelope values.

    frequency: int or float or None
        The frequency rate of the samples.

    name: str or None, optional
        Defines the name of the Envelope instance.

    condition: str or None, optional
        Optional field to represent in which experimental condition the original audio was clip recorded.

    Attributes
    ----------
    samples: list(float) or numpy.ndarray(float64)
        An array containing the samples of the envelope.

    timestamps: list(float) or numpy.ndarray(float64)
        An array of equal length to :attr:`samples`, containing the timestamps for each sample.

    frequency: int or float
        The frequency, in Hertz, at which the values in attr:`samples` are sampled.

    name: str or None
        A name to describe the envelope object.

    condition: str or None
        Defines in which experimental condition the original audio was clip recorded.
    """

    def __init__(self, samples, frequency=None, name=None, condition=None, verbosity=1):
        super().__init__("Envelope", samples, frequency, name, condition, verbosity)


class Pitch(AudioDerivative):
    """This class contains the values of the pitch of an audio clip.

    .. versionadded:: 2.0

    Parameters
    ----------
    samples: list(float) or numpy.ndarray(float64)
        The pitch values.


    frequency: int or float
        The frequency rate of the samples.

    name: str or None, optional
        Defines the name of the pitch. If set on ``None``, the name will be the same as the original Audio instance,
        with the suffix ``"(PIT)"``.

    condition: str or None, optional
        Optional field to represent in which experimental condition the original audio was clip recorded.

    Attributes
    ----------
    samples: list(float) or numpy.ndarray(float64)
        An array containing the values of the pitch.

    timestamps: list(float) or numpy.ndarray(float64)
        An array of equal length to :attr:`samples`, containing the timestamps for each sample.

    frequency: int or float
        The frequency, in Hertz, at which the values in attr:`samples` are sampled.

    name: str or None
        A name to describe the pitch object.

    condition: str or None
        Defines in which experimental condition the original audio was clip recorded.
    """

    def __init__(self, samples, frequency=None, name=None, condition=None, verbosity=1):
        super().__init__("Pitch", samples, frequency, name, condition, verbosity)


class Intensity(AudioDerivative):
    """This class contains the values of the intensity of an audio clip.

    .. versionadded:: 2.0

    Parameters
    ----------
    samples: list(float) or numpy.ndarray(float64)
        The intensity values.

    frequency: int or float
        The frequency rate of the samples.

    name: str or None, optional
        Defines the name of the Intensity instance.

    condition: str or None, optional
        Optional field to represent in which experimental condition the original audio was clip recorded.

    Attributes
    ----------
    samples: list(float) or numpy.ndarray(float64)
        An array containing the values of the intensity.

    timestamps: list(float) or numpy.ndarray(float64)
        An array of equal length to :attr:`samples`, containing the timestamps for each sample.

    frequency: int or float
        The frequency, in Hertz, at which the values in attr:`samples` are sampled.

    name: str or None
        A name to describe the intensity object.

    condition: str or None
        Defines in which experimental condition the original audio was clip recorded.
    """

    def __init__(self, samples, frequency=None, name=None, condition=None, verbosity=1):
        super().__init__("Intensity", samples, frequency, name, condition, verbosity)


class Formant(AudioDerivative):
    """This class contains the values of one of the formants of an audio clip.

    .. versionadded:: 2.0

    Parameters
    ----------
    samples: list(float) or numpy.ndarray(float64)
        The formant values.

    frequency: int or float
        The frequency rate of the samples.

    formant_number: int
        The number of the formant to extract from the audio clip (default: 1 for f1).

    name: str or None, optional
        Defines the name of the Formant instance.

    condition: str or None, optional
        Optional field to represent in which experimental condition the original audio was clip recorded.

    Attributes
    ----------
    samples: list(float) or numpy.ndarray(float64)
        An array containing the values of the formant.

    timestamps: list(float) or numpy.ndarray(float64)
        An array of equal length to :attr:`samples`, containing the timestamps for each sample.

    frequency: int or float
        The frequency, in Hertz, at which the values in attr:`samples` are sampled.

    name: str or None
        A name to describe the intensity object.

    condition: str or None
        Defines in which experimental condition the original audio was clip recorded.

    formant_number: int
        The number of the formant (e.g., 1).
    """

    # noinspection PyArgumentList
    def __init__(self, samples, frequency=None, formant_number=1, name=None, condition=None, verbosity=1):
        super().__init__("Formant", samples, frequency, name, condition, verbosity)
        self.formant_number = formant_number
        self._load_formant_number()

    def _load_formant_number(self):
        if "formant_number" in self.metadata:
            self.formant_number = int(self.metadata["formant_number"])
        elif "FORMANT_NUMBER" in self.metadata:
            self.formant_number = int(self.metadata["FORMANT_NUMBER"])

    def _set_attributes_from_other_object(self, other):
        super()._set_attributes_from_other_object(other)
        if "formant_number" in dir(other):
            self.formant_number = other.formant_number

