"""Classes for time series derived from audio clips: Envelope, Intensity, Pitch and Formants."""

import numpy as np
from scipy.signal import butter, hilbert, lfilter

from classes.exceptions import ModuleNotFoundException
from tool_functions import resample_data, pad, add_delay


class AudioDerivative(object):
	"""Parent class for the Envelope, Intensity, Pitch and Formant methods. Contains common methods for each of the
	subclasses.

	.. versionadded:: 2.0

	Parameters
	----------
	samples: list(float) or numpy.ndarray(float64)
		An array containing the values for the audio derivative.
	timestamps: list(float) or numpy.ndarray(float64)
		An array of equal length to ``samples``, containing the timestamps for each sample.
	frequency: int or float
		The frequency, in Hertz, of the timestamps.
	kind: str or None
		The kind of audio derivative: ``"Envelope"``, ``"Pitch"``, ``"Intensity"``, ``"Formant"``, or ``None``.
	name: str or None, optional
		The name of the audio derivative. By default, this field is used to store the name of the audio clip the
		derivative comes from, with a suffix indicating the type of the audio derivative.
	condition: str or None, optional
        Optional field to represent in which experimental condition the audio derivative was originally recorded.

	Attributes
	----------
	samples: list(float) or numpy.ndarray(float64)
		An array containing the values for the audio derivative.
	timestamps: list(float) or numpy.ndarray(float64)
		An array of equal length to :attr:`samples`, containing the timestamps for each sample.
	frequency: int or float
		The frequency, in Hertz, at which the values in attr:`samples` are sampled.
	kind: str or None
		The kind of audio derivative: ``"Envelope"``, ``"Pitch"``, ``"Intensity"``, ``"Formant"``, or ``None``.
	name: str or None, optional
		The name of the audio derivative. By default, this field is used to store the name of the audio clip the
		derivative comes from, with a suffix indicating the type of the audio derivative.
    condition: str
        Defines in which experimental condition the audio derivative was recorded.
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

		new_audio_derivative = type(self)(new_samples, self.timestamps, self.frequency, name, verbosity=0)
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
			This parameter also allows for all the values accepted for the ``kind`` parameter in the function
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

		new_audio_derivative = type(self)(samples_resampled, timestamps_resampled, self.frequency, name)

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
	audio_or_samples: Audio or list(float) or numpy.ndarray(float64)
		An Audio instance, or an array containing the samples of an audio file. In the case where this parameter is an
		array, at least one of the parameters ``timestamps`` and ``frequency`` must be provided.

	timestamps: list(float) or numpy.ndarray(float64) or None, optional
		The timestamps of the samples. This parameter is ignored if ``audio_or_samples`` is an instance of
		:class:`Audio`.

	frequency: int or float or None, optional
		The frequency rate of the samples. This parameter is ignored if ``audio_or_samples`` is an instance of
		:class:`Audio`.

	name: str or None, optional
		Defines the name of the envelope. If set on ``None``, the name will be the same as the original Audio instance,
		with the suffix ``"(ENV)"``.

	condition: str or None, optional
        Optional field to represent in which experimental condition the original audio was clip recorded.

	verbosity: int, optional
		Sets how much feedback the code will provide in the console output:

		• *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
		• *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
		  current steps.
		• *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
		  may clutter the output and slow down the execution.

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

	def __init__(self, audio_or_samples, timestamps=None, frequency=None, name=None, condition=None, verbosity=1):

		if verbosity > 0:
			print("Creating an Envelope object...", end=" ")

		self.condition = condition

		# If the parameter is an array of samples
		if type(audio_or_samples) in [list, np.ndarray]:
			samples = np.abs(hilbert(audio_or_samples))
			if timestamps is None and frequency is not None:
				timestamps = [i / frequency for i in range(len(samples))]
			elif timestamps is not None and frequency is None:
				frequency = 1 / (timestamps[1] - timestamps[0])
			elif timestamps is None and frequency is None:
				raise Exception("If audio_or_samples is an array, at least one of the parameters timestamp or " +
								"frequency must be provided.")

		# If the parameter is an Audio object
		elif str(type(audio_or_samples)) == "<class 'classes.audio.Audio'>":
			samples = np.abs(hilbert(audio_or_samples.get_samples()))
			timestamps = audio_or_samples.get_timestamps()
			frequency = audio_or_samples.get_frequency()
			if name is None:
				name = audio_or_samples.get_name() + " (ENV)"

		else:
			raise Exception("Invalid type for the parameter audio_or_samples ( " + str(type(audio_or_samples)) + "). " +
							"The type should be list, numpy.ndarray or Audio.")

		if verbosity > 0:
			print("Done.")

		super().__init__(samples, timestamps, frequency, "Envelope", name, condition)


class Pitch(AudioDerivative):
	"""This class contains the values of the pitch of an audio clip.

	.. versionadded:: 2.0

	Parameters
	----------
	audio_or_samples: Audio or list(float) or numpy.ndarray(float64)
		An Audio instance, or an array containing the samples of an audio file. In the case where this parameter is an
		array, at least one of the parameters ``timestamps`` and ``frequency`` must be provided.

	timestamps: list(float) or numpy.ndarray(float64) or None, optional
		The timestamps of the samples. This parameter is ignored if ``audio_or_samples`` is an instance of
		:class:`Audio`.

	frequency: int or float or None, optional
		The frequency rate of the samples. This parameter is ignored if ``audio_or_samples`` is an instance of
		:class:`Audio`.

	name: str or None, optional
		Defines the name of the envelope. If set on ``None``, the name will be the same as the original Audio instance,
		with the suffix ``"(PIT)"``.

	condition: str or None, optional
        Optional field to represent in which experimental condition the original audio was clip recorded.

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

	# noinspection PyArgumentList
	def __init__(self, audio_or_samples, timestamps=None, frequency=None, name=None, condition=None, zeros_as_nan=False,
				 verbosity=1):
		if verbosity > 0:
			print("Creating a Pitch object...")

		try:
			from parselmouth import Sound
		except ImportError:
			raise ModuleNotFoundException("parselmouth", "get the pitch of an audio clip.")

		self.condition = condition

		# If the parameter is an array of samples
		if type(audio_or_samples) in [list, np.ndarray]:
			original_samples = np.array(audio_or_samples, dtype=np.float64)
			if timestamps is None and frequency is not None:
				timestamps = [i / frequency for i in range(len(original_samples))]
			elif timestamps is not None and frequency is None:
				frequency = 1 / (timestamps[1] - timestamps[0])
			elif timestamps is None and frequency is None:
				raise Exception("If audio_or_samples is an array, at least one of the parameters timestamp or " +
								"frequency must be provided.")

		# If the parameter is an Audio object
		elif str(type(audio_or_samples)) == "<class 'classes.audio.Audio'>":
			original_samples = np.array(audio_or_samples.get_samples(), dtype=np.float64)
			timestamps = audio_or_samples.timestamps
			frequency = audio_or_samples.frequency
			if name is None:
				name = audio_or_samples.get_name() + " (PIT)"

		else:
			raise Exception("Invalid type for the parameter audio_or_samples ( " + str(type(audio_or_samples)) + "). " +
							"The type should be list, numpy.ndarray or Audio.")

		if verbosity > 0:
			print("\tTurning the audio into a parselmouth object...", end=" ")

		parselmouth_sound = Sound(np.ndarray(np.shape(original_samples), dtype=np.float64, buffer=original_samples),
								  audio_or_samples.frequency)
		if verbosity > 0:
			print("Done.")
			print("\tGetting the pitch...", end=" ")

		pitch = parselmouth_sound.to_pitch(time_step=1 / frequency)

		if verbosity > 0:
			print("Done.")
			print("\tPadding the data...", end=" ")

		pitch, timestamps = pad(pitch.selected_array["frequency"], pitch.xs(), timestamps)

		if zeros_as_nan:
			pitch[pitch == 0] = np.nan

		if verbosity > 0:
			print("Done.")

		super().__init__(pitch, timestamps, frequency, "Pitch", name, condition)


class Intensity(AudioDerivative):
	"""This class contains the values of the intensity of an audio clip.

	.. versionadded:: 2.0

	Parameters
	----------
	samples: Audio or list(float) or numpy.ndarray(float64)
		The intensity values.

	timestamps: list(float) or numpy.ndarray(float64) or None, optional
		The timestamps of the intensity values.

	frequency: int or float or None, optional
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
	audio_or_samples: Audio or list(float) or numpy.ndarray(float64)
		An Audio instance, or an array containing the samples of an audio file. In the case where this parameter is an
		array, at least one of the parameters ``timestamps`` and ``frequency`` must be provided.

	timestamps: list(float) or numpy.ndarray(float64) or None, optional
		The timestamps of the samples. This parameter is ignored if ``audio_or_samples`` is an instance of
		:class:`Audio`.

	frequency: int or float or None, optional
		The frequency rate of the samples. This parameter is ignored if ``audio_or_samples`` is an instance of
		:class:`Audio`.

	name: str or None, optional
		Defines the name of the envelope. If set on ``None``, the name will be the same as the original Audio instance,
		with the suffix ``"(INT)"``.

	condition: str or None, optional
        Optional field to represent in which experimental condition the original audio was clip recorded.

	formant_number: int, optional
		The number of the formant to extract from the audio clip (default: 1 for f1).

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
	def __init__(self, audio_or_samples, timestamps=None, frequency=None, name=None, condition=None, formant_number=1,
				 verbosity=1):
		if verbosity > 0:
			print("Creating a Formant object...")

		try:
			from parselmouth import Sound
		except ImportError:
			raise ModuleNotFoundException("parselmouth", "get one of the formants of an audio clip.")

		self.condition = condition

		# If the parameter is an array of samples
		if type(audio_or_samples) in [list, np.ndarray]:
			original_samples = np.array(audio_or_samples, dtype=np.float64)
			if timestamps is None and frequency is not None:
				timestamps = [i / frequency for i in range(len(original_samples))]
			elif timestamps is not None and frequency is None:
				frequency = 1 / (timestamps[1] - timestamps[0])
			elif timestamps is None and frequency is None:
				raise Exception("If audio_or_samples is an array, at least one of the parameters timestamp or " +
								"frequency must be provided.")

		# If the parameter is an Audio object
		elif str(type(audio_or_samples)) == "<class 'classes.audio.Audio'>":
			original_samples = np.array(audio_or_samples.get_samples(), dtype=np.float64)
			timestamps = audio_or_samples.timestamps
			frequency = audio_or_samples.frequency
			if name is None:
				name = audio_or_samples.get_name() + " (" + str(formant_number) + ")"

		else:
			raise Exception("Invalid type for the parameter audio_or_samples ( " + str(type(audio_or_samples)) + "). " +
							"The type should be list, numpy.ndarray or Audio.")

		if verbosity > 0:
			print("\tTurning the audio into a parselmouth object...", end=" ")

		parselmouth_sound = Sound(np.ndarray(np.shape(original_samples), dtype=np.float64, buffer=original_samples),
								  audio_or_samples.frequency)

		if verbosity > 0:
			print("Done.")
			print("\tGetting the formant...", end=" ")

		formants = parselmouth_sound.to_formant_burg(time_step=1 / frequency)
		formants_timestamps = add_delay(formants.xs(), -1 / (2 * frequency))

		if verbosity > 0:
			print("Done.")
			print("\tPadding the data...", end=" ")

		number_of_points = formants.get_number_of_frames()
		f = []
		for i in range(1, number_of_points + 1):
			t = formants.get_time_from_frame_number(i)
			f.append(formants.get_value_at_time(formant_number=formant_number, time=t))
		f, timestamps = pad(f, formants_timestamps, timestamps)

		if verbosity > 0:
			print("Done.")

		super().__init__(f, timestamps, frequency, "Formant", name, condition)
		self.formant_number = formant_number
