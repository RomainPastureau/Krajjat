from krajjat.classes.sequence import Sequence
from src.krajjat.display_functions import *
from src.krajjat.tool_functions import *

if __name__ == '__main__':

    parent_folder = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/"
    folder = parent_folder + "Gesture/01_Original_gesture/"
    folder_original = parent_folder + "Gesture/02_Trimmed_original_gesture/"
    folder_audio = parent_folder + "Audio/04_Trimmed_audio/"
    folder_out = parent_folder + "Gesture/02_Preprocessed_gesture/"
    folder_audio_out = parent_folder + "Audio/05_Resampled_audio/"
    folder_video_out = parent_folder + "Gesture/06_Video_skeleton_gesture/"
    subjects = ["01_Araitz", "02_Ainhoa", "03_Amets", "04_Itziar", "05_Larraitz", "06_Laura"]
    shifts = {"01_Araitz": (80, 70), "02_Ainhoa": (40, 180), "03_Amets": (75, 150),
              "04_Itziar": (80, 70), "05_Larraitz": (70, 20), "06_Laura": (100, 140)}
    #video = "R013"

    delays = {}
    paths_audio = {}
    preprocessed_sequences = []
    preprocessed_audios = []

    sequence_orig = Sequence(folder_original + "02_Ainhoa/R059")
    sequence_reader(sequence_orig, path_video="D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/Audiovisual/03_Normalized_audiovisual/Normalized_bodies/02_Ainhoa/R059.mp4")


    sequence = Sequence(folder_out + "02_Ainhoa/R059.xlsx")
    sequence_reader(sequence, path_video="D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/Audiovisual/03_Normalized_audiovisual/Normalized_bodies/02_Ainhoa/R059.mp4",
                    position_video="superimposed", ignore_bottom=False, show_lines=True, type="square", color_joint=(255, 255, 255),
                    scale=1.7, shift_x=10, shift_y=80, ratio_joint=1.7, resolution=(950, 534))


    # for subject in subjects:
    #
    #     with open("../delays.txt") as f:
    #         content = f.read().split("\n")
    #         for line in content:
    #             elements = line.split("\t")
    #             delays[folder + elements[0] + "/" + elements[1]] = float(elements[2])
    #
    #             paths_audio[folder + subject + "/" + elements[1]] = folder_audio + subject + "/" + elements[1] + ".wav"
    #
    #     #sequences = [Sequence(folder + subject + "/R002")]
    #     sequences = load_sequences_recursive(folder + subject)
    #
    #     for sequence in sequences:
    #         print("\n=== "+str(sequence.name)+" ===")
    #
    #         if os.path.exists(paths_audio[folder + subject + "/" + sequence.name]):
    #             audio = Audio(paths_audio[folder + subject + "/" + sequence.name])
    #
    #         sequence_realigned = sequence.correct_jitter(0.1, 3, method="new", verbose=1)
    #
    #         try:
    #
    #             sequence_synced = sequence_realigned.synchronize_with_audio(delays[folder + subject + "/" + sequence.name],
    #                                                                         audio, True)
    #             sequence_synced.randomize()
    #         #pose_reader(sequence_synced, ignore_bottom=True, show_lines=False, type="circle", color_joint=(255, 255, 255), scale=1.7,
    #         #            shift_x=0, shift_y=0, ratio_joint=1.7, resolution=(950, 534),
    #         #            path_images="D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/img/001.png")
    #             save_video_sequence(sequence_synced, folder_video_out + subject + "/" + sequence.name + ".mp4", 25,
    #                                 shift_x=0, shift_y=0)

            # except Exception as ex:
            #
            #     print("\nIGNORING THIS SEQUENCE · Reason: "+str(ex))