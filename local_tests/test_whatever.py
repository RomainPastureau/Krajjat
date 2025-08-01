from krajjat.classes.sequence import Sequence
from krajjat.display_functions import sequence_reader
from krajjat.plot_functions import joints_movement_plotter, single_joint_movement_plotter
from krajjat.tool_functions import read_xlsx

# sequence = Sequence(
#     "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/Gesture/01_Original_gesture/02_Ainhoa/R077",
# verbosity=2)
# print(sequence.metadata)
# print(sequence.get_date_recording())
# sequence.save("../src/krajjat/example/sequence_ainhoa.json")

#sequence = Sequence("../src/krajjat/example/sequence_ainhoa.json", verbosity=2)
#print(str(sequence.metadata["Timestamp"]))


path_parent = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/"
path_output_sequences = path_parent + "Gesture/02 - Preprocessed/"
subject_name = "S001"
recording = "R018"

table = read_xlsx("D:/OneDrive/Documents/BCBL/05_BodyLingual/Documents/Participants & Videos/Recordings Lund.xlsx")
video_number = None
delay = None
for row in table:
    if row[0] == subject_name:
        if row[3] == recording:
            video_number = row[2]
            delay = row[8]

sequence = Sequence(path_output_sequences + subject_name + "/" + recording + ".tsv")
#single_joint_movement_plotter(sequence, "HandInRight", domain="frequency")
#joints_movement_plotter(sequence, "velocity", "frequency")
path_audio = path_parent + "Audio/Recut/" + subject_name + "/" + subject_name + "_" + recording + ".wav"
path_video = path_parent + "Mocap/Romain_S001/Data/master_" + video_number + "_Miqus_10_24050.avi"
sequence_reader(sequence, path_audio, path_video, timestamp_video_start=delay, x_axis="-x", y_axis="z",
                size_joint_head=10, size_joint_hand=10)

my_sequence = Sequence("C:/mocap/avatar3/scene_with_darth_vader.json")
my_sequence.print_stats()