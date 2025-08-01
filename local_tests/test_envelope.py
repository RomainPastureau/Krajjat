import numpy as np
from matplotlib import pyplot as plt
from krajjat.classes.audio import Audio
from datetime import datetime as dt

##############################################
### TEST ENVELOPE WITH WINDOWS AND OVERLAP ###
##############################################

# subject_name = "S001"
# recording_name = "R001"
#
# audio = Audio("D:/Downloads/S001.wav")
#
# sample_start = 0
# sample_end = len(audio.samples)
#
# time_before = dt.now()
# envelope_total = audio.get_envelope(None, None, 0, 50, verbosity = 0)
# time_after = dt.now()
# print("Envelope total: " + str(time_after - time_before) + "\n")
#
# windows = [i for i in range(200, 50200, 200)]
#
# overlaps = [0, 2, 3]
#
# correlations = []
# precisions = []
# times = []
#
# i = 0
#
# for overlap in overlaps:
#     correlation = []
#     precision = []
#     time = []
#
#     for window in windows:
#         time_before = dt.now()
#         if overlap == 0 :
#             envelope_windows = audio.get_envelope(window, 0, 0, 50, verbosity = 0)
#         else:
#             envelope_windows = audio.get_envelope(window, window//overlap, 0, 50, verbosity=0)
#         time_after = dt.now()
#         corr = np.corrcoef(envelope_windows, envelope_total)[1, 0]
#         prec = np.mean(np.abs((envelope_total.samples-envelope_windows.samples)/envelope_total.samples))
#
#         correlation.append(corr*100)
#         precision.append(100 - (prec * 100))
#         time_delta = time_after - time_before
#         time.append((time_delta.total_seconds()))
#
#         #print("Envelope " + str(window) + ": " + str(time_after - time_before) + " (corr: " + str(corr * 100) + ", prec: " +
#         #      str(100 - (prec * 100)) + ")")
#
#         print(str(window) + "\t" + str(time_delta.total_seconds()) + "\t" + str(corr * 100) + "\t" + str(100 - (prec * 100)))
#
#         #plt.plot(envelope_windows.samples, label=str(window))
#         # plt.subplot(5, 3, i+1)
#         # plt.plot(envelope_total.samples, label="total")
#         # plt.plot(envelope_windows.samples, label=str(window))
#         # plt.legend(loc="upper right")
#         #plt.ylim([0, 15000])
#         #i += 1
#
#     correlations.append(correlation)
#     precisions.append(precision)
#     times.append(time)
#
# #plt.show()
#
# for i in range(len(overlaps)):
#     plt.subplot(3, len(overlaps), i*3 + 1)
#     plt.plot(windows, correlations[i], color="red")
#     plt.ylim([99, 100.english])
#     plt.title("Corr, overlap: " + str(overlaps[i]))
#     plt.subplot(3, len(overlaps), i*3 + 2)
#     plt.plot(windows, precisions[i], color="green")
#     plt.ylim([99, 100.english])
#     plt.title("Prec, overlap: " + str(overlaps[i]))
#     plt.subplot(3, len(overlaps), i*3 + 3)
#     plt.plot(windows, times[i], color="orange")
#     plt.ylim([0, 10])
#     plt.title("Time, overlap: " + str(overlaps[i]))
# plt.show()

##########################################
### TEST ENVELOPE WITH LONG AUDIO FILE ###
##########################################

path_audio = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Audio/Cleaned/S001.wav"
audio = Audio(path_audio)
# time_before = dt.now()
# envelope_full = audio.get_envelope(None, None, None, 50, None)
# time_elapsed = dt.now() - time_before
# print(time_elapsed)

#np.save("D:/Downloads/envelope_full", envelope_full.samples)
envelope_full = np.load("D:/Downloads/envelope_full.npy")

time_before = dt.now()
envelope_windows = audio.get_envelope(10000, 5000, 0, 50)
time_elapsed = dt.now() - time_before
print(time_elapsed)

corr = np.corrcoef(envelope_windows.samples, envelope_full)[1, 0]
prec = np.mean(np.abs((envelope_full-envelope_windows.samples)/envelope_full))

print("Correlation: " + str(corr))
print("Precision: " + str(prec))

plt.subplot(3, 1, 1)
plt.plot(envelope_full[0:100000])

plt.subplot(3, 1, 2)
plt.plot(envelope_windows.samples[0:100000])

plt.subplot(3, 1, 3)
plt.plot(np.abs(envelope_full[10000000:11000000] - envelope_windows.samples[10000000:11000000]))
plt.show()