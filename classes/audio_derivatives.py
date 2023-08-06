from collections.abc import Iterable

import numpy as np
from scipy.signal import butter, hilbert, lfilter

from tool_functions import resample_data


class AudioDerivative(object):

    def __init__(self, samples, timestamps, frequency):
        self.samples = samples
        self.timestamps = timestamps
        self.frequency = frequency
        pass

    def get_samples(self):
        return self.samples

    def get_timestamps(self):
        return self.timestamps

    def get_frequency(self):
        return self.frequency

    def filter_frequencies(self, filter_below, filter_over):
        print(self.frequency)
        if filter_below not in [None, 0] and filter_over not in [None, 0]:
            b, a = butter(2, [filter_below, filter_over], "band", fs=self.frequency)
            self.samples = lfilter(b, a, self.samples)
        elif filter_below not in [None, 0]:
            b, a = butter(2, filter_below, "high", fs=self.frequency)
            self.samples = lfilter(b, a, self.samples)
        elif filter_over not in [None, 0]:
            b, a = butter(2, filter_over, "low", fs=self.frequency)
            self.samples = lfilter(b, a, self.samples)

    def resample(self, frequency, mode, verbose=1):

        if verbose > 0:
            print("Resampling at "+str(frequency)+" Hz (mode: "+str(mode)+")...")
            print("\tPerforming the resampling...", end=" ")

        samples_resampled, timestamps_resampled = resample_data(self.samples, self.timestamps, frequency, mode)
        new_envelope = Envelope(samples_resampled, timestamps_resampled, self.frequency)

        if verbose > 0:
            print("100% - Done.")
            print("\tOriginal audio had "+str(len(self.samples))+" samples.")
            print("\tNew audio has " + str(len(new_envelope.samples)) + " samples.\n")

        return new_envelope


class Envelope(AudioDerivative):

    def __init__(self, audio_or_samples, timestamps=None, frequency=None):

        self.samples = None

        if type(audio_or_samples) in [list, np.ndarray]:
            self.samples = audio_or_samples
            self.timestamps = timestamps
            self.frequency = frequency

        elif str(type(audio_or_samples)) == "<class 'classes.audio.Audio'>":
            self.samples = np.abs(hilbert(audio_or_samples.get_samples()))
            self.timestamps = audio_or_samples.get_timestamps()
            self.frequency = audio_or_samples.get_frequency()

        super().__init__(self.samples, self.timestamps, self.frequency)


class Pitch(AudioDerivative):

    def __init__(self):
        super().__init__()
