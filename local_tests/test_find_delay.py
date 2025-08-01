from datetime import datetime as dt
import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile
from find_delay import find_delay, resample, get_number_of_windows

# Load audio
audio_path = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Audio/Cleaned/S001.wav"
# audio_path = "D:/Downloads/S001.wav"
audio_wav = wavfile.read(audio_path)  # Read the WAV
audio_frequency = audio_wav[0]
audio_array = audio_wav[1]  # Turn to mono

# Load excerpt
excerpt_path = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Audio/Cut/S001/S001_R001.wav"
excerpt_wav = wavfile.read(excerpt_path)
excerpt_frequency = excerpt_wav[0]
excerpt_array = excerpt_wav[1]  # Turn to mono

path_figures = "D:/Downloads/"

for i in range(1, 10):
    print("-"*70)
    find_delay(audio_array, excerpt_array, audio_frequency, excerpt_frequency,
                       compute_envelope=True,
                       number_of_windows_env=20000, overlap_ratio_env=0.5,
                       number_of_windows_res=i, overlap_ratio_res=0.5,
                       resampling_rate=1000, resampling_mode="cubic",
                       filter_below=None, filter_over=50,
                       threshold=0.7, plot_figure=False, path_figure=path_figures+str(i)+".png",
                       verbosity=1)

# find_delay(audio_array, excerpt_array, audio_frequency, excerpt_frequency,
#                    compute_envelope=True,
#                    number_of_windows_env=20000, overlap_ratio_env=0.5,
#                    number_of_windows_res=10, overlap_ratio_res=0.5,
#                    resampling_rate=1000, resampling_mode="interp1d_cubic",
#                    filter_below=None, filter_over=50,
#                    threshold=0.7, plot_figure=False, path_figure=path_figures+"2.png",
#                    verbosity=1)
# find_delay(audio_array, excerpt_array, audio_frequency, excerpt_frequency,
#                    compute_envelope=True,
#                    number_of_windows_env=20000, overlap_ratio_env=0.5,
#                    number_of_windows_res=None, overlap_ratio_res=None,
#                    resampling_rate=1000, resampling_mode="cubic",
#                    filter_below=None, filter_over=50,
#                    threshold=0.7, plot_figure=False, path_figure=path_figures+"3.png",
#                    verbosity=1)
#
# find_delay(audio_array, excerpt_array, audio_frequency, excerpt_frequency,
#                    compute_envelope=True,
#                    number_of_windows_env=20000, overlap_ratio_env=0.5,
#                    number_of_windows_res=None, overlap_ratio_res=None,
#                    resampling_rate=1000, resampling_mode="interp1d_cubic",
#                    filter_below=None, filter_over=50,
#                    threshold=0.7, plot_figure=False, path_figure=path_figures+"4.png",
#                    verbosity=1)



# original_frequency = 3
# upper_limit = 10
# x = np.linspace(0, upper_limit, original_frequency*upper_limit, endpoint=False)
# y = np.cos(-x**2/6.0)
#
# time_before = dt.now()
# resampling_frequency = 50
# x1 = np.arange(0, max(x), 1 / resampling_frequency)
# y1 = resample(y, original_frequency, resampling_frequency, number_of_windows=None, overlap_ratio=None, method="cubic",
#               verbosity=2)
# print("Resampling performed in " + str(dt.now() - time_before))
#
# time_before = dt.now()
# resampling_frequency = 50
# x2 = np.arange(0, max(x), 1 / resampling_frequency)
# y2 = resample(y, original_frequency, resampling_frequency, number_of_windows=None, overlap_ratio=None, method="pchip",
#               verbosity=1)
# print("Resampling performed in " + str(dt.now() - time_before))
#
# time_before = dt.now()
# resampling_frequency = 50
# x3 = np.arange(0, max(x), 1 / resampling_frequency)
# y3 = resample(y, original_frequency, resampling_frequency, number_of_windows=None, overlap_ratio=None, method="akima",
#               verbosity=1)
# print("Resampling performed in " + str(dt.now() - time_before))
#
# plt.subplot(4, 1, 1)
# plt.plot(x, y, "k.-")
# plt.subplot(4, 1, 2)
# plt.plot(x1, y1, "r.-")
# plt.subplot(4, 1, 3)
# plt.plot(x2, y2, "b.-")
# plt.subplot(4, 1, 4)
# plt.plot(x3, y3, "g.-")
# plt.show()
