"""Classes for time series derived from audio clips: Envelope, Intensity, Pitch and Formants."""
import copy
import pickle

import taglib
from scipy.io import wavfile, loadmat

from krajjat.classes.exceptions import EmptyAudioException, EmptyInstanceException
from krajjat.classes.timeseries import TimeSeries
from krajjat.tool_functions import *


class AudioDerivative(TimeSeries):
    """Parent class for the Envelope, Intensity, Pitch and Formant methods. Contains common methods for each of the
    subclasses.
    """

    def __init__(self, path_or_samples, frequency, kind, name=None, condition=None, verbosity=1):

        super().__init__(kind, path_or_samples, name, condition, verbosity)

        self.samples = np.ndarray([])
        self.timestamps = np.ndarray([])
        self.frequency = frequency

        if type(path_or_samples) is str:
            self._load_from_path(path_or_samples, verbosity)
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
        """
        self.condition = condition

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
            print(f"Opening audio from {self.path}...", end=" ")
        elif verbosity > 1:
            print(f"Opening audio from {self.path}...")
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
                self.metadata = metadata
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
                data, self.metadata = read_xlsx(self.path, verbosity=verbosity)

            else:
                data, self.metadata = read_text_table(self.path)

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

    def get_samples(self):
        """Returns the attribute :attr:`samples` of the audio derivative.

        .. versionadded:: 2.0

        Returns
        -------
        list(float) or numpy.ndarray(float64)
            An array containing the values for the audio derivative.
        """
        return self.samples

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

    def get_name(self):
        """Returns the attribute :attr:`name` of the audio derivative. Unless modified, the value of this attribute
        should be the same as the value of the original :attr:`Audio.name` attribute.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The value of the attribute :attr:`name` of the audio derivative.
        """
        return self.name

    def get_condition(self):
        """Returns the attribute :attr:`condition` of the AudioDerivative instance.

        .. versionadded:: 2.0

        Returns
        -------
        str
            The experimental condition in which the recording of the audio clip was originally performed.
        """
        return self.condition

    def get_number_of_samples(self):
        """Returns the length of the attribute :attr:`samples`.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of samples in the audio derivative.
        """
        return len(self.samples)

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
            name = self.name

        if type(self) is Formant:
            new_audio_derivative = type(self)(new_samples, self.frequency,
                                              formant_number=self.formant_number, name=name)
        else:
            new_audio_derivative = type(self)(new_samples, self.frequency, name=name)

        new_audio_derivative._set_attributes_from_other_object(self)
        new_audio_derivative.metadata["processing_steps"].append({"processing_type": "filter_frequencies",
                                                                  "filter_below": filter_below,
                                                                  "filter_over": filter_over})
        return new_audio_derivative

    def resample(self, frequency, window_size=1e7, overlap_ratio=0.5, mode="cubic", name=None, verbosity=1):
        """Resamples an audio derivative to the `frequency` parameter. This function first creates a new set of
        timestamps at the desired frequency, and then interpolates the original data to the new timestamps.

        .. versionadded:: 2.0

        Parameters
        ----------
        frequency: float
            The frequency, in hertz, at which you want to resample the audio derivative. A frequency of 4 will return
            samples at 0.25 s intervals.

        mode: str, optional
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
            print("Resampling at " + str(frequency) + " Hz (mode: " + str(mode) + ")...")
            print("\tPerforming the resampling...", end=" ")

        if window_size == 0 or window_size > len(self.samples) or window_size is None:
            window_size = len(self.samples)

        if overlap_ratio is None:
            overlap_ratio = 0

        samples_resampled, timestamps_resampled = resample_data(self.samples, self.timestamps, frequency,
                                                                window_size, overlap_ratio, mode, verbosity=verbosity)

        if name is None:
            name = self.name

        new_audio_derivative = type(self)(samples_resampled, timestamps_resampled, frequency, name)
        new_audio_derivative._set_attributes_from_other_object(self)

        if verbosity > 0:
            print("100% - Done.")
            print("\tOriginal " + self.kind.lower() + " had " + str(len(self.samples)) + " samples.")
            print("\tNew " + self.kind.lower() + " has " + str(len(new_audio_derivative.samples)) + " samples.\n")

        return new_audio_derivative

    def trim(self, start=None, end=None, name=None, verbosity=1, add_tabs=0):
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

        t = add_tabs * "\t"

        if start is None:
            start = self.timestamps[0]
            start_index = 0
        if end is None:
            end = self.timestamps[-1]
            end_index = -1

        if end < start:
            raise Exception("End timestamp should be inferior to beginning timestamp.")
        elif start < self.timestamps[0]:
            raise Exception(f"Starting timestamp ({start}) lower than the first timestamp of the AudioDerivative " +
                            f"instance ({self.timestamps[0]}).")
        elif start < 0:
            raise Exception(f"Starting timestamp ({start}) must be equal to or higher than 0.")
        elif end > self.timestamps[-1]:
            raise Exception(f"Ending timestamp ({end}) exceeds last timestamp of the AudioDerivative instance (" +
                            f"{self.timestamps[-1]}).")

        if name is None:
            name = self.name + " +TR"

        if start_index is None:
            start_index = int(np.floor(start * self.frequency))
            if self.timestamps[start_index] <= start:
                start_index += 1

        if verbosity > 1:
            print(t + f"Closest (above) starting timestamp from {start}: {self.timestamps[start_index]}")

        if end_index is None:
            end_index = int(np.ceil(end * self.frequency))
        if self.timestamps[end_index] >= end:
            end_index -= 1

        if verbosity > 1:
            print(t + f"Closest (below) starting timestamp from {end}: {self.timestamps[end_index]}")

        new_audio_derivative = type(self)(self.samples[start_index:end_index + 1],
                                          self.timestamps[start_index:end_index + 1],
                               self.frequency, name, self.condition, verbosity)

        return new_audio_derivative

    def print_details(self, include_name=True, include_condition=True, include_number_of_samples=True,
                      include_duration=True):
        """Prints a series of details about the AudioDerivative.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_name: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`name` to the printed string.
        include_condition: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`condition` to the printed string.
        include_number_of_samples: bool, optional
            If set on ``True`` (default), adds the length of the attribute :attr:`samples` to the printed string.
        include_duration: bool, optional
            If set on ``True`` (default), adds the duration of the Sequence to the printed string.
        """
        string = self.kind + " · "
        if include_name:
            string += "Name: " + str(self.name) + " · "
        if include_condition:
            string += "Condition: " + str(self.condition) + " · "
        if include_number_of_samples:
            string += "Number of samples: " + str(self.get_number_of_samples()) + " · "
        if include_duration:
            string += "Duration: " + str(round(self.get_duration(), 2)) + " s" + " · "
        if len(string) > 3:
            string = string[:-3]

        print(string)

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

    def __init__(self, samples, frequency, name=None, condition=None, verbosity=1):
        super().__init__(samples, frequency, "Envelope", name, condition, verbosity)


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
        super().__init__(samples, frequency, "Pitch", name, condition, verbosity)


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

    def __init__(self, samples, frequency, name=None, condition=None, verbosity=1):
        super().__init__(samples, frequency, "Intensity", name, condition, verbosity)


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
    def __init__(self, samples, frequency, formant_number=1, name=None, condition=None, verbosity=1):
        super().__init__(samples, frequency, "Formant", name, condition, verbosity)
        self.formant_number = formant_number
