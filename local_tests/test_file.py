from krajjat.analysis_functions import coherence
from krajjat.classes.audio import Audio
from krajjat.classes.experiment import Experiment
from krajjat.classes.sequence import Sequence
from krajjat.classes.subject import Subject

if __name__ == '__main__':

    # parent_folder = "C:/Users/romai/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/"
    parent_folder = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/"
    folder = parent_folder + "Gesture/01_Original_gesture/"
    folder_audio = parent_folder + "Audio/04_Trimmed_audio/"
    folder_out = parent_folder + "Gesture/02_Preprocessed_gesture/"
    folder_audio_out = parent_folder + "Audio/05_Resampled_audio/"
    folder_video_out = parent_folder + "Gesture/06_Video_skeleton_gesture/"
    folder_gesture_preprocessed = parent_folder + "Gesture/02_Preprocessed_gesture/"
    subjects = ["01_Araitz", "02_Ainhoa", "03_Amets", "04_Itziar", "05_Larraitz", "06_Laura"]
    shifts = {"01_Araitz": (80, 70), "02_Ainhoa": (40, 180), "03_Amets": (75, 150),
              "04_Itziar": (80, 70), "05_Larraitz": (70, 20), "06_Laura": (100, 140)}
    video = "R013"

    delays = {}
    paths_audio = {}
    preprocessed_sequences = []
    preprocessed_audios = []

    for subject in subjects:

        with open("../kinect_processing/delays.txt") as f:
            content = f.read().split("\n")
            for line in content:
                elements = line.split("\t")
                delays[folder_gesture_preprocessed + elements[0] + "/" + elements[1]] = float(elements[2])
                paths_audio[folder_gesture_preprocessed + subject + "/" + elements[1]] = folder_audio_out + subject + \
                                                                                         "/" + elements[1] + ".xlsx"

    path_video = parent_folder + "Audiovisual/03_Normalized_audiovisual/Normalized_bodies/"
    # sequence = Sequence(folder_out + subjects[0] + "/" + video + ".xlsx", name="R013")
    # single_joint_movement_plotter(sequence) # timestamp_start=50, timestamp_end=54)

    # sequence1 = Sequence(folder_out + subjects[0] + "/R011.xlsx", verbosity=0)
    # sequence2 = sequence1.trim(10, 30, True)
    # sequence3 = sequence2.trim(5, 10, True)
    # path_audio = folder_audio + subjects[0] + "/R011.wav"
    # audio1 = Audio(folder_audio + subjects[0] + "/R011.wav", verbosity=0)
    # sequence_reader(sequence1, path_video = path_video + subjects[0] + "/" + video + ".mp4", path_audio = path_audio,
    #                position_video="superimposed", resolution=0.5, color_joint_default="light blue", verbosity=1)
    # sequence1.print_stats()

    # single_joint_movement_plotter([sequence1, sequence2, sequence3])
    # joints_movement_plotter(sequence1, "acceleration", audio1, True)

    # audio_plotter(audio1)

    # color = convert_color("dark green")

    sequence1 = Sequence(folder_out + subjects[0] + "/R011.xlsx", verbosity=1)
    sequence2 = Sequence(folder_out + subjects[0] + "/R012.xlsx", verbosity=1)
    sequence3 = Sequence(folder_out + subjects[0] + "/R013.xlsx", verbosity=1)
    # sequence4 = Sequence(folder_out + subjects[1] + "/R032.xlsx", verbosity=0)
    # sequence5 = Sequence(folder_out + subjects[1] + "/R033.xlsx", verbosity=0)
    # sequence6 = Sequence(folder_out + subjects[1] + "/R034.xlsx", verbosity=0)
    # sequence7 = Sequence(folder_out + subjects[2] + "/R011.xlsx", verbosity=0)
    # sequence8 = Sequence(folder_out + subjects[2] + "/R012.xlsx", verbosity=0)
    # sequence9 = Sequence(folder_out + subjects[2] + "/R013.xlsx", verbosity=0)
    #

    audio1 = Audio(folder_audio + subjects[0] + "/R011.wav", verbosity=1)
    audio2 = Audio(folder_audio + subjects[0] + "/R012.wav", verbosity=1)
    audio3 = Audio(folder_audio + subjects[0] + "/R013.wav", verbosity=1)

    experiment = Experiment()
    subject1 = Subject("01_Araitz", gender="F", age=21)
    subject1.add_sequences(sequence1, sequence2, sequence3)
    subject1.add_audios(audio1, audio2, audio3)
    experiment.add_subject(subject1)

    coherence(experiment, color_line=["blue", "red"])

    import numpy as np

    np.ndarray([1, 2, 3])

    # audio4 = Audio(folder_audio + subjects[1] + "/R032.wav", verbosity=0)
    # intensity4 = audio4.get_intensity(8, verbosity=0)
    # audio5 = Audio(folder_audio + subjects[1] + "/R033.wav", verbosity=0)
    # intensity5 = audio5.get_intensity(8, verbosity=0)
    # audio6 = Audio(folder_audio + subjects[1] + "/R034.wav", verbosity=0)
    # intensity6 = audio6.get_intensity(8, verbosity=0)
    # audio7 = Audio(folder_audio + subjects[2] + "/R011.wav", verbosity=0)
    # intensity7 = audio7.get_intensity(8, verbosity=0)
    # audio8 = Audio(folder_audio + subjects[2] + "/R012.wav", verbosity=0)
    # intensity8 = audio8.get_intensity(8, verbosity=0)
    # audio9 = Audio(folder_audio + subjects[2] + "/R013.wav", verbosity=0)
    # intensity9 = audio9.get_intensity(8, verbosity=0)
    #

    # subject2 = Subject("02_Ainhoa", gender="F", age=38)
    # subject2.add_sequences([sequence4, sequence5, sequence6])
    # subject2.add_audios(intensity4, intensity5, intensity6)
    # subject3 = Subject("03_Amets", gender="F", age=32)
    # subject3.add_sequences(sequence7, sequence8, sequence9)
    # subject3.add_audios(intensity7, intensity8, intensity9)
    #
    # experiment.add_subject(subject1)
    # experiment.add_subject(subject2)
    # experiment.add_subject(subject3)
    #
    # experiment.print_subjects_details()
    #
    # correlation_with_audio(experiment, sequence_metric="distance", color_scheme="celsius")

    # import matplotlib.pyplot as plt
    # import seaborn as sns
    # sns.set()

    # ax = plt.subplot(3, 3, 1)
    # ax.plot(intensity1.get_timestamps(), intensity1.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence1.get_timestamps()[1:], sequence1.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 2)
    # ax.plot(intensity2.get_timestamps(), intensity2.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence2.get_timestamps()[1:], sequence2.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 3)
    # ax.plot(intensity3.get_timestamps(), intensity3.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence3.get_timestamps()[1:], sequence3.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 4)
    # ax.plot(intensity4.get_timestamps(), intensity4.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence4.get_timestamps()[1:], sequence4.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 5)
    # ax.plot(intensity5.get_timestamps(), intensity5.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence5.get_timestamps()[1:], sequence5.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 6)
    # ax.plot(intensity6.get_timestamps(), intensity6.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence6.get_timestamps()[1:], sequence6.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 7)
    # ax.plot(intensity7.get_timestamps(), intensity7.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence7.get_timestamps()[1:], sequence7.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 8)
    # ax.plot(intensity8.get_timestamps(), intensity8.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence8.get_timestamps()[1:], sequence8.get_joint_distance_as_list("HandRight"))
    #
    # ax = plt.subplot(3, 3, 9)
    # ax.plot(intensity9.get_timestamps(), intensity9.get_samples(), color="tab:orange")
    # ax2 = ax.twinx()
    # ax2.plot(sequence9.get_timestamps()[1:], sequence9.get_joint_distance_as_list("HandRight"))
    # plt.show()

    # from classes.subject import Subject
    # from datetime import datetime
    #
    # d1 = datetime(1994, 4, 24)
    # d2 = datetime.now()
    # d3 = datetime(1995, 1, 1)
    # d4 = datetime(1995, 4, 25)
    #
    # subject = Subject()
    # subject.set_age_from_dob(d1.day, d1.month, d1.year, d2.day, d2.month, d2.year)
    # audio = Audio(folder_audio + subjects[0] + "/" + video + ".wav", name="R013")
    # joints_movement_plotter(sequence)
    # plot_silhouette({"Head": 100, "HandLeft": 0, "HandRight": 50}, resolution=(1600, 540))
    # audio = Audio("D:/Downloads/A440.wav")
    # scipy.fft.fft(audio.samples)
    # audio_plotter(audio)
    # intensity = audio.get_intensity()
    # pitch = audio.get_pitch()
    # import matplotlib.pyplot as plt
    # plt.plot(pitch.timestamps, pitch.samples)
    # plt.show()

    # formant = audio.get_formant()
    # sequence1 = Sequence(folder_out + subjects[0] + "/" + video + ".xlsx", name="R013")
    # sequence2 = Sequence(folder_out + subjects[0] + "/" + "R014" + ".xlsx", name="R014")
    # sequence3 = Sequence(folder_out + subjects[0] + "/" + "R015" + ".xlsx", name="R015")
    # sequence4 = Sequence(folder_out + subjects[0] + "/" + "R016" + ".xlsx", name="R016")
    # single_joint_movement_plotter(sequence, "HandRight")
    # framerate_plotter([sequence1, sequence1, sequence1, sequence1, sequence1, sequence1, sequence1, sequence1])
    # sequence2 = sequence1.resample(8, verbosity=2)
    # common_displayer(sequence1, path_audio = folder_audio + subjects[0] + "/" + video + ".wav",
    #                   color_joint_default_seq1="orange", path_video = path_video + subjects[0] + "/" + video + ".mp4",
    #                   position_sequences="superimposed", zoom_level=2.9, shift=(-310, -153))
    # save_video_sequence(sequence1, path_audio = folder_audio + subjects[0] + "/" + video + ".wav",
    #                     color_joint_default_seq1="orange", path_video = path_video + subjects[0] + "/" + video + ".mp4",
    #                     position_sequences="superimposed", zoom_level=2.9, shift=(-310, -153),
    #                     path_output="D:/Downloads/Output/video.mp4", verbosity=2)

    # sequence1.save("D:/Downloads/sequence1.csv")
    # sequence1.poses[0].remove_joint("Head")

    # sequence1 = Sequence(folder_out + subjects[0] + "/" + video + ".xlsx", name="my_sequence")
    # sequence1.print_stats()
    # velocity_plotter(sequence1)

    # sequence2 = Sequence("D:/Downloads/sequence1.csv")

    # path1 = "C:/Users/romai/Documents/Word/Novels/"
    # path2 = "C:/Users/romai/"

    # compute_subpath(path1, path2)

    # sequence = Sequence(folder + subjects[0] + "/" + video + "/thisdoesntexist/", name="my_sequence")

    # audio = Audio(folder_audio + "01_Araitz/R018.wav")

    # audio = Audio("D:/Downloads/A440.wav")
    # scipy.fft.fft(audio.samples)
    # envelope = audio.get_envelope(0, 10)
    # resampled_audio = audio.resample(10, "cubic")
    # resampled_envelope = envelope.resample(10, "cubic")
    # resampled_audio_envelope = resampled_audio.get_envelope(None, None)
    # pitch = audio.get_pitch()
    # intensity = audio.get_intensity()
    # formant0 = audio.get_formant(1)
    # formant1 = audio.get_formant(2)
    #
    # import matplotlib.pyplot as plt
    # import seaborn as sns
    #
    # sns.set()
    #
    # plt.subplot(5, 2, 1)
    # plt.plot(audio.timestamps, audio.samples)
    # plt.title("Original audio")
    #
    # plt.subplot(5, 2, 2)
    # plt.plot(envelope.timestamps, envelope.samples)
    # plt.title("Envelope of the original audio")
    #
    # plt.subplot(5, 2, 3)
    # plt.plot(resampled_audio.timestamps, resampled_audio.samples)
    # plt.title("Resampled audio")
    #
    # plt.subplot(5, 2, 4)
    # plt.plot(resampled_envelope.timestamps, resampled_envelope.samples)
    # plt.title("Resampled envelope")
    #
    # plt.subplot(5, 2, 5)
    # plt.plot(resampled_audio_envelope.timestamps, resampled_audio_envelope.samples)
    # plt.title("Envelope of the resampled audio")
    #
    # plt.subplot(5, 2, 6)
    # plt.plot(pitch.timestamps, pitch.samples)
    # plt.title("Pitch")
    #
    # plt.subplot(5, 2, 7)
    # plt.plot(intensity.timestamps, intensity.samples)
    # plt.title("Intensity")
    #
    # plt.subplot(5, 2, 8)
    # plt.plot(formant0.timestamps, formant0.samples)
    # plt.plot(formant1.timestamps, formant1.samples)
    # plt.title("f1 & f2")
    # plt.show()
    #
    # import parselmouth
    #
    # import numpy as np
    #
    # snd = parselmouth.Sound("D:/Downloads/test_asa.wav")
    #
    # def draw_spectrogram(spectrogram, dynamic_range=70):
    #     X, Y = spectrogram.x_grid(), spectrogram.y_grid()
    #     sg_db = 10 * np.log10(spectrogram.values)
    #     plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
    #     plt.ylim([spectrogram.ymin, spectrogram.ymax])
    #     plt.xlabel("time [s]")
    #     plt.ylabel("frequency [Hz]")
    #
    # def draw_intensity(intensity):
    #     plt.plot(intensity.xs(), intensity.values.T, linewidth=3, color='w')
    #     plt.plot(intensity.xs(), intensity.values.T, linewidth=1)
    #     plt.grid(False)
    #     plt.ylim(0)
    #     plt.ylabel("intensity [dB]")
    #
    # plt.subplot(5, 2, 9)
    # intensity = snd.to_intensity()
    # spectrogram = snd.to_spectrogram()
    # #plt.figure()
    # draw_spectrogram(spectrogram)
    # plt.twinx()
    # draw_intensity(intensity)
    # plt.xlim([snd.xmin, snd.xmax])
    #
    #
    # def draw_pitch(pitch):
    #     # Extract selected pitch contour, and
    #     # replace unvoiced samples by NaN to not plot
    #     pitch_values = pitch.selected_array['frequency']
    #     pitch_values[pitch_values == 0] = np.nan
    #     plt.plot(pitch.xs(), pitch_values, 'o', markersize=5, color='w')
    #     plt.plot(pitch.xs(), pitch_values, 'o', markersize=2)
    #     plt.grid(False)
    #     plt.ylim(0, pitch.ceiling)
    #     plt.ylabel("fundamental frequency [Hz]")
    #
    # pitch = snd.to_pitch()
    # # If desired, pre-emphasize the sound fragment before calculating the spectrogram
    # pre_emphasized_snd = snd.copy()
    # pre_emphasized_snd.pre_emphasize()
    # spectrogram = pre_emphasized_snd.to_spectrogram(window_length=0.03, maximum_frequency=8000)
    #
    #
    # plt.subplot(5, 2, 10)
    # draw_spectrogram(spectrogram)
    # plt.twinx()
    # draw_pitch(pitch)
    # plt.xlim([snd.xmin, snd.xmax])
    # plt.show()

    # print(envelope)

    # sequences = load_sequences("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/Gesture/01_Original_gesture", recursive=True)

    # print(sequence1)
    # sequence.print_stats()
    # sequence_realigned_classic = sequence.correct_jitter(0.1, 3)
    # sequence2 = sequence1.correct_jitter(0.1, 500, window_unit="ms", method="cubic", verbose=1)
    # sequence3 = sequence2.re_reference()
    # p = folder_gesture_preprocessed + subjects[0] + "/" + video
    # sequence4 = sequence3.synchronize_with_audio(delays[p], paths_audio[p], trim=True)
    # sequence4 = sequence3.trim_to_audio(-delays[p], paths_audio[p])

    # print(paths_audio)
    # sequences = load_sequences_recursive(folder_out + subject)
    # for sequence in sequences:
    #     print("\n=== "+str(sequence.name)+" ===")
    #
    #     audio = Audio(paths_audio[folder + subject + "/" + sequence.name.split(".")[0]])
    #     #audio2 = audio.resample(8, "cubic", True)
    #     #save_audio(audio2, folder_audio_out + subject, name_out=sequence.name.split(".")[0], file_format="xlsx",
    #     #           individual=False)
    #     preprocessed_sequences.append(sequence)
    #     preprocessed_audios.append(audio)
    #
    # print("\n\nIgnored sequences:", ignored)
    # print("\n\nSequences with unmatching length:", unmatched)

    # # sequence2 = sequence1.resample(8, "cubic", True)
    # # sequence3 = sequence1.resample(16, "cubic", True)
    # # sequence4 = sequence1.resample(32, "cubic", True)
    # # sequence5 = sequence1.resample(64, "cubic", True)
    # sequences = [sequence1, sequence2, sequence3, sequence4, sequence5]
    # framerate_plotter(sequence1)
    # sequences = [sequence1, sequence2]
    # joint_temporal_plotter(sequences, "HandRight")

    # val = sequence1.get_time_between_two_poses(len(sequence1)-1, len(sequence1)-865)
    # print(val)
    # sequence2 = Sequence(folder+"/01_Original_gesture/"+subject+"/R019")
    # velocity_plotter(sequences[0])
    # sequences = [sequence1, sequence2]
    # framerate_plotter(sequence1)
    # sequence_reader(sequence5)
    # sequence_comparer(sequence1, sequence2)

    # save_stats(sequences, folder+"Stats_global.xlsx")
    # print(sequence1.poses[34])
    # sequence1 = Sequence(folder+"/Test/global.csv")
    # save_sequence(sequence1, folder + "/Test/", file_format="xlsx", individual=False)
    # save_sequence(sequence1, folder + "/Test/csv", file_format="csv", individual=True)
    # save_sequence(sequence1, folder + "/Test/xls", file_format="xls", individual=True)
    # save_sequence(sequence1, folder + "/Test/xlsx", file_format="xlsx", individual=True)

    # sequence2 = Sequence(folder + "Test/txt/")
    # save_sequence(sequence2, folder + "/Test/indiv", file_format="txt", individual=False)
    # save_sequence(sequence2, folder + "/Test/indiv", file_format="csv", individual=False)
    # save_sequence(sequence2, folder + "/Test/indiv", file_format="xls", individual=False)
    # save_sequence(sequence2, folder + "/Test/indiv", file_format="xlsx", individual=False)

    # print(delays)
    # print(paths_audio)
    #
    # print("Trimming...")
    # new_sequences = trim_sequences(sequences, delays, paths_audio)
    # print("Done.")
    # print(new_sequences)
