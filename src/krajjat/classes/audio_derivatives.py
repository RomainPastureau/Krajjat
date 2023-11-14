"""Classes for time series derived from audio clips: Envelope, Intensity, Pitch and Formants."""
from krajjat.classes.exceptions import ModuleNotFoundException
from krajjat.tool_functions import resample_data


class AudioDerivative(object):
	"""Parent class for the Envelope, Intensity, Pitch and Formant methods. Contains common methods for each of the
	subclasses.
	"""

	def __init__(self, samples, timestamps, frequency, kind, name=None, condition=None):
		self.samples = samples
		self.timestamps = timestamps
		self.frequency = frequency
		self.kind = kind
		self.name = name
		self.condition = condition

	def set_name(self, name):
		"""Sets the :attr:`name` attribute of the AudioDerivative instance. This name can be used as a way to identify
		the original Audio instance from which the AudioDerivative has been created.

		.. versionadded:: 2.0

		Parameters
		----------
		name : str
			A name to describe the audio derivative.
		"""
		self.name = name

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

		new_audio_derivative = type(self)(new_samples, self.timestamps, self.frequency, name)
		return new_audio_derivative

	def resample(self, frequency, mode="cubic", name=None, verbosity=1):
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

		samples_resampled, timestamps_resampled = resample_data(self.samples, self.timestamps, frequency, mode)

		if name is None:
			name = self.name

		new_audio_derivative = type(self)(samples_resampled, timestamps_resampled, frequency, name)

		if verbosity > 0:
			print("100% - Done.")
			print("\tOriginal" + self.kind.lower() + " had " + str(len(self.samples)) + " samples.")
			print("\tNew " + self.kind.lower() + " has " + str(len(new_audio_derivative.samples)) + " samples.\n")

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

	timestamps: list(float) or numpy.ndarray(float64)
		The timestamps of the samples.

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
	def __init__(self, samples, timestamps, frequency, name=None, condition=None):
		super().__init__(samples, timestamps, frequency, "Envelope", name, condition)


class Pitch(AudioDerivative):
	"""This class contains the values of the pitch of an audio clip.

	.. versionadded:: 2.0

	Parameters
	----------
	samples: list(float) or numpy.ndarray(float64)
		The pitch values.

	timestamps: list(float) or numpy.ndarray(float64)
		The timestamps of the samples.

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
	def __init__(self, samples, timestamps=None, frequency=None, name=None, condition=None):
		super().__init__(samples, timestamps, frequency, "Pitch", name, condition)


class Intensity(AudioDerivative):
	"""This class contains the values of the intensity of an audio clip.

	.. versionadded:: 2.0

	Parameters
	----------
	samples: list(float) or numpy.ndarray(float64)
		The intensity values.

	timestamps: list(float) or numpy.ndarray(float64)
		The timestamps of the samples.

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
	def __init__(self, samples, timestamps, frequency, name=None, condition=None):
		super().__init__(samples, timestamps, frequency, "Intensity", name, condition)


class Formant(AudioDerivative):
	"""This class contains the values of one of the formants of an audio clip.

	.. versionadded:: 2.0

	Parameters
	----------
	samples: list(float) or numpy.ndarray(float64)
		The formant values.

	timestamps: list(float) or numpy.ndarray(float64)
		The timestamps of the samples.

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
	def __init__(self, samples, timestamps, frequency, formant_number=1, name=None, condition=None):
		super().__init__(samples, timestamps, frequency, "Formant", name, condition)
		self.formant_number = formant_number
