import json
import os

import numpy as np
from matplotlib import pyplot as plt
from scipy import signal
from scipy.signal import hilbert

from krajjat.classes.audio import Audio
from krajjat.classes.sequence import Sequence
from krajjat.tool_functions import format_time, get_number_of_windows

from datetime import datetime as dt

subject_name = "S001"
recording_name = "R001"
path_delays = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Audio/delays.json"

# audio = Audio("D:/Downloads/S001.wav")

#sequence = Sequence(f"D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Gesture/{subject_name}/{recording_name}.tsv",
#                    f"{subject_name}_{recording_name}")

#sequence.print_stats()

# Get the masters
test_uncut_audio = Audio("D:/Downloads/S001.wav")
test_excerpt = Audio("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Audio/Cut/S001/S001_R001.wav")
timestamp = test_uncut_audio.find_excerpt_starting_timestamp(test_excerpt, resampling_rate=44100, verbosity=2)
print(timestamp)

path_uncut_audios = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Audio/Cleaned/"
uncut_audios = os.listdir(path_uncut_audios)
all_delays = {}

# for path_uncut_audio in uncut_audios:
#     uncut_audio = Audio(path_uncut_audios + path_uncut_audio)
#     path_audios = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/Audio/Cut/" + \
#                   path_uncut_audio.split(".")[0] + "/"
#     files = os.listdir(path_audios)
#     excerpts = []
#     for i in range(len(files)):
#         excerpts.append(Audio(path_audios + files[i]))
#
#     timestamps = uncut_audio.find_excerpts_starting_timestamps(excerpts)
#
#     # if os.path.exists(path_delays):
#     #     with open(path_delays, "r") as f:
#     #         all_delays = json.load(f)
#
#     all_delays[path_uncut_audio.split(".")[0]] = {}
#     i = 0
#     for timestamp in timestamps:
#         t = format_time(timestamp*1000/uncut_audio.frequency, "ms", "hh:mm:ss.ms")
#         print(files[i].split(".")[0] + ": " + str(t))
#         all_delays[path_uncut_audio.split(".")[0]][files[i].split(".")[0]] = str(t)
#         i += 1
#
#     # with open(path_delays, "w") as f:
#     #     json.dump(all_delays, f)
#
#     del uncut_audio
