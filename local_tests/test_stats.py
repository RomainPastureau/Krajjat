from matplotlib import pyplot as plt

from krajjat import *
from krajjat.classes.audio import Audio
from krajjat.classes.sequence import Sequence
from krajjat.plot_functions import plot_silhouette, joints_movement_plotter

if __name__ == '__main__':

    parent_folder = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/"
    folder_gesture_raw = parent_folder + "Gesture/01_Original_gesture/"
    folder_audio = parent_folder + "Audio/04_Trimmed_audio/"
    folder_gesture_preprocessed = parent_folder + "Gesture/02_Preprocessed_gesture/"
    folder_audio_out = parent_folder + "Audio/05_Resampled_audio/"
    subjects = ["01_Araitz", "02_Ainhoa", "03_Amets", "04_Itziar", "05_Larraitz", "06_Laura"]

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
                paths_audio[
                    folder_gesture_preprocessed + subject + "/" + elements[1]] = folder_audio_out + subject + "/" + \
                                                                                 elements[1] + ".xlsx"

    # 1. Load a sequence
    sequence = Sequence(folder_gesture_preprocessed + subjects[0] + "/R008.xlsx")

    # correlation_with_joint(sequence, "HandRight")
    plot_dictionary = {'Head': 0.12474215926736097, 'Neck': 0.0739548036084773, 'SpineShoulder': 0.07015252277603765,
                       'SpineMid': 0.0, 'SpineBase': 0.11630088361987487, 'ShoulderLeft': 0.18376662286925116,
                       'ElbowLeft': 0.11213095128489707, 'WristLeft': 0.32004472300330467,
                       'HandLeft': 0.34808968559604364, 'ShoulderRight': 0.3906875622753516,
                       'ElbowRight': 0.5592188363748134, 'WristRight': 0.8294378983295317, 'HandRight': 1.0,
                       'HipLeft': 0.1732782134894747, 'KneeLeft': 0.01827109513212487, 'AnkleLeft': 0.04623417946230854,
                       'FootLeft': 0.019863644401920743, 'HipRight': 0.0996624174944813,
                       'KneeRight': 0.0894717022704954, 'AnkleRight': 0.11144630019264572,
                       'FootRight': 0.11649838347472798}
    # plot_dictionary = {"Head": 0.5}
    # plot_silhouette(plot_dictionary)
    # #color_scheme = "cividis"
    # color_scheme = "celsius"
    # plot_silhouette(plot_dictionary, min_scale=0, max_scale=0.5, show_scale=True,
    #                 color_scheme=color_scheme, resolution=(900,900), full_screen=False)

    # 2. Printing functions
    # sequence.print_stats()
    # sequence.print_pose(5)

    # 3. Visualisation functions
    # sequence_reader(sequence, type="circle", ignore_bottom=False, color_joint=(255, 255, 0), ratio_joint=1, show_lines=True)
    # pose_reader(sequence, start_pose=0)
    # save_skeleton_video(sequence, parent_folder + "video.mp4")

    # 4. Processing functions
    # sequence1 = Sequence(folder_gesture_raw + subjects[0] + "/R008")
    # sequence2 = Sequence(folder_gesture_preprocessed + subjects[0] + "/R008.xlsx")
    # sequence_realigned = sequence.realign(0.1, 3)
    # sequence_comparer(sequence1, sequence2)
    # sequence_rereferenced = sequence_realigned.re_reference()
    # sequence_resampled = sequence_rereferenced.resample(8)
    # sequence_reader(sequence, type="circle", ignore_bottom=False, color_joint=(255, 255, 0), ratio_joint=1,
    #                show_lines=True)

    # 5. Plotting functions
    # framerate_plotter([sequence1, sequence2])

    # sequence = Sequence(folder_gesture_raw+subjects[0]+"/R008")
    joints_movement_plotter(sequence)

    audio = Audio(paths_audio[folder_gesture_preprocessed + subjects[0] + "/R008"])

    import matplotlib.pyplot as plot

    # Plot the sine waves - subplot 1
    plot.subplot(521)
    plot.grid(True, which='both')
    plot.xlabel('time')
    plot.ylabel('amplitude')
    # Create method audio.get_timestamps()
    plot.plot(sequence.get_timestamps()[:-1], sequence.get_joint_velocity_as_array("HandRight"))
    print("Timestamps: ", len(sequence.get_timestamps()[:-1]))
    print("Sequence: ", len(sequence.get_joint_velocity_as_array("HandRight")))
    envelope = audio.get_envelope()
    print("Audio: ", len(envelope.samples[:-1]))

    plot.subplot(522)
    plot.grid(True, which='both')
    plot.xlabel('time')
    plot.ylabel('amplitude')
    # Create method audio.get_timestamps()
    plot.plot(sequence.get_timestamps()[:-1], audio.get_envelope()[:-1])

    # Plot the coherence - subplot 2
    import matplotlib

    plot.subplot(523)
    coh, f = plot.cohere(sequence.get_joint_velocity_as_array("HandRight"),
                         audio.get_envelope()[:len(envelope) - 1], 32, 8, detrend=matplotlib.mlab.detrend_linear)
    plot.ylabel('coherence, matplotlib')

    plot.subplot(524)
    import scipy

    x = sequence.get_joint_velocity_as_array("HandRight")
    y = audio.get_envelope()[:len(envelope) - 1]

    f, coh = scipy.signal.coherence(x, y, fs=8.0, nperseg=32, window='hann', detrend="linear")

    # print("Coherence between two signals:")
    print(coh)
    # print("Frequencies of the coherence vector:")
    print(f)
    plot.grid(True, which='both')
    plot.plot(f, coh)
    plot.ylabel('coherence, scipy')

    plot.subplot(525)

    new_seq = []
    avg = sum(sequence.get_joint_velocity_as_array("HandRight")) / len(sequence.get_joint_velocity_as_array("HandRight"))
    for sample in sequence.get_joint_velocity_as_array("HandRight"):
        new_seq.append(sample - avg)
    fft_seq = scipy.fft.fft(new_seq)
    y = scipy.fft.fftfreq(len(new_seq), 0.125)
    plot.plot(y, fft_seq)
    plot.ylabel('fft sequence')

    plot.subplot(526)
    fft_envelope = scipy.fft.fft(envelope.samples[:len(envelope) - 1])
    y = scipy.fft.fftfreq(len(envelope.samples[:len(envelope) - 1]), 0.125)
    plot.plot(y, fft_envelope)
    plot.ylabel('fft envelope')

    plot.subplot(527)
    vector = scipy.array(sequence.get_joint_velocity_as_array("HandRight"))
    f, t, Sxx = scipy.signal.spectrogram(vector, 8.0, "hamming")
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    plot.subplot(528)
    vector = scipy.array(audio.get_envelope()[:len(envelope) - 1])
    f, t, Sxx = scipy.signal.spectrogram(vector, 8.0, "hamming")
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    plot.subplot(529)
    import numpy


    def crossSpectrum(x, y, nperseg=32):
        # -------------------Remove mean-------------------
        cross = numpy.zeros(nperseg, dtype='complex128')
        for ind in range(x.size // nperseg):
            xp = x[ind * nperseg: (ind + 1) * nperseg]
            yp = y[ind * nperseg: (ind + 1) * nperseg]
            xp = xp - numpy.mean(xp)
            yp = yp - numpy.mean(xp)

            # Do FFT
            cfx = numpy.fft.fft(xp)
            cfy = numpy.fft.fft(yp)

            # Get cross spectrum
            cross += cfx.conj() * cfy
        freq = numpy.fft.fftfreq(nperseg)
        return cross, freq


    y1 = numpy.array(sequence.get_joint_velocity_as_array("HandRight"))
    y2 = numpy.array(audio.get_envelope()[:len(envelope) - 1])

    p11, freq = crossSpectrum(y1, y1)
    p22, freq = crossSpectrum(y2, y2)
    p12, freq = crossSpectrum(y1, y2)

    # coherence
    coh = numpy.abs(p12) ** 2 / p11.real / p22.real
    plt.plot(freq[freq > 0], coh[freq > 0])
    plt.xlabel('Normalized frequency')
    plt.ylabel('Coherence')

    plot.subplot(5, 2, 10)

    x = numpy.array(sequence.get_joint_velocity_as_array("HandRight"))
    y = numpy.array(audio.get_envelope()[:len(envelope) - 1])
    y_flip = numpy.random.permutation(y)

    freq = 8  # Hz
    window_size = 4  # seconds
    overlap = 2  # seconds
    i = 0

    n = len(x)
    w = window_size * freq
    o = window_size * freq - overlap * freq

    x_segmented = numpy.zeros(shape=(int((n - w + 1) / (w - o)) + 1, window_size * freq))
    y_segmented = numpy.zeros(shape=(int((n - w + 1) / (w - o)) + 1, window_size * freq))
    y_flip_segmented = numpy.zeros(shape=(int((n - w + 1) / (w - o)) + 1, window_size * freq))

    for start_window in range(0, len(x) - (freq * window_size), (freq * window_size) - (freq * overlap)):
        x_segmented[i] = x[start_window:start_window + freq * window_size]
        y_segmented[i] = y[start_window:start_window + freq * window_size]
        y_flip_segmented[i] = y_flip[start_window:start_window + freq * window_size]
        i = i + 1

    fft_x = numpy.zeros(shape=(len(x_segmented), window_size * freq))
    fft_y = numpy.zeros(shape=(len(x_segmented), window_size * freq))
    fft_y_flip = numpy.zeros(shape=(len(x_segmented), window_size * freq))

    for segment in range(len(x_segmented)):
        fft_x[segment] = numpy.fft.fft(x_segmented[segment])
        fft_y[segment] = numpy.fft.fft(y_segmented[segment])
        fft_y_flip[segment] = numpy.fft.fft(y_flip_segmented[segment])

    fxx = numpy.mean(fft_x * numpy.conjugate(fft_x), 0)
    fyy = numpy.mean(fft_y * numpy.conjugate(fft_y), 0)
    fxy = numpy.mean(fft_x * numpy.conjugate(fft_y), 0)

    coherence_audio = (fxy * numpy.conj(fxy)) / (fyy * fxx)

    fxx = numpy.mean(fft_x * numpy.conjugate(fft_x), 0)
    fyy = numpy.mean(fft_y_flip * numpy.conjugate(fft_y_flip), 0)
    fxy = numpy.mean(fft_x * numpy.conjugate(fft_y_flip), 0)

    coherence_audio_flip = (fxy * numpy.conj(fxy)) / (fyy * fxx)

    print(coherence_audio)
    print(coherence_audio_flip)

    f = numpy.arange(0, 8, 0.25)
    print(f)

    plt.plot(f, coherence_audio)
    plt.plot(f, coherence_audio_flip)
    plt.xlabel('Frequency')
    plt.ylabel('Coherence')

    # from multitaper_spectrogram_python import *
    #
    # # Set spectrogram params
    # fs = 8  # Sampling Frequency
    # frequency_range = [0, 4]  # Limit frequencies from 0 to 25 Hz
    # time_bandwidth = 3  # Set time-half bandwidth
    # num_tapers = 5  # Set number of tapers (optimal is time_bandwidth*2 - 1)
    # window_params = [4, 1]  # Window size is 4s with step size of 1s
    # min_nfft = 0  # No minimum nfft
    # detrend_opt = 'constant'  # detrend each window by subtracting the average
    # multiprocess = True  # use multiprocessing
    # n_jobs = 4  # use 3 cores in multiprocessing
    # weighting = 'unity'  # weight each taper at 1
    # plot_on = True  # plot spectrogram
    # return_fig = False  # do not return plotted spectrogram
    # clim_scale = False  # do not auto-scale colormap
    # verbose = True  # print extra info
    # xyflip = False  # do not transpose spect output matrix
    #
    # import numpy
    # data = numpy.array(audio.get_envelope()[:len(audio.envelope)-1])
    #
    # # Compute the multitaper spectrogram
    # spect, stimes, sfreqs = multitaper_spectrogram(data, fs, frequency_range, time_bandwidth, num_tapers, window_params,
    #                                                min_nfft, detrend_opt, multiprocess, n_jobs,
    #                                                weighting, plot_on, return_fig, clim_scale, verbose, xyflip)
    #
    plot.show()
    # print(audio.samples)
    # print(max(audio.samples))

    # sequence = Sequence(folder_out+subjects[0]+"/R008.xlsx")
    # audio = Audio(folder_audio_out+subjects[0]+"/R008.xlsx")

    # sequences = load_sequences_recursive(folder_gesture_preprocessed + subjects[0])
    # audio = []

    # sequence = Sequence(folder_gesture_preprocessed + subjects[4] + "/R035.xlsx")
    # audio = Audio(folder_audio_out + subjects[0] + "/R008.xlsx")
    # sequence = Sequence("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Lund/01_Delphine/mocap_data/Romain_001/Data/delphine_r0001.tsv")
    # sequence = Sequence(folder_gesture_raw+subjects[0]+"/R013")
    # sequence.print_stats()
    # sequence.save("D:/Downloads/mat_test", file_format="mat")
    # sequence_reader(sequence)
    # sequence.print_stats()
    # sequence2 = sequence.correct_zeros()
    # sequence2 = sequence.realign(0.2, 100)
    # joint_temporal_plotter([sequence, sequence2], "WristOutRight")
    # velocity_plotter(sequence2)

    # for sequence in sequences:
    #    audio.append(Audio(paths_audio[folder_gesture_preprocessed + subjects[0] + "/" + sequence.name[0:4]]))
    # correlation_with_audio(sequence, audio, color_scheme="celsius")
    # correlation_with_joint(sequence, "HandRight", color_scheme="celsius")
    # cross_correlation_with_audio(sequence, audio)

    # coherence_with_audio(sequence, audio)
    # coherence_with_audio(sequences, audio)

    # for subject in [subjects[0]]:
    #    sequences = load_sequences_recursive(folder_out + subject)
    #    for sequence in sequences:
    #        print("\n=== "+str(sequence.name)+" ===")
    #        print(subject)
    #        audio = Audio(folder_audio_out + subject + "/" + sequence.name.split(".")[0] + ".xlsx")
    #        audio2 = audio.resample(8, "cubic", True)
    #        save_audio(audio2, folder_audio_out + subject, name_out=sequence.name.split(".")[0], file_format="xlsx",
    #                   individual=False)
    #        preprocessed_sequences.append(sequence)
    #        preprocessed_audios.append(audio)
    #
    # correlation_with_audio(sequence, audio)
    # correlation_with_joint(sequence, "HandRight")
    # cross_correlation_with_audio(preprocessed_sequences, preprocessed_audios, lag=-0.375, window=2)
    # cross_correlation_with_joint(preprocessed_sequences, "HandRight", window=2)
    # correlation_with_audio(preprocessed_sequences, preprocessed_audios)

    # for subject in subjects:
    #
    #     sequences = load_sequences_recursive(folder + subject)
    #
    #     ignored = []
    #     unmatched = []
    #
    #     for sequence in sequences:
    #         print("\n=== "+str(sequence.name)+" ===")
    #
    #         if os.path.exists(paths_audio[folder + subject + "/" + sequence.name]):
    #             audio = Audio(paths_audio[folder + subject + "/" + sequence.name])
    #             sequence2 = sequence.realign(0.1, 3, method="new", verbose=1)
    #             sequence3 = sequence2.re_reference()
    #             sequence4 = sequence3.resample(8, "cubic", True)
    #
    #             try:
    #
    #                 sequence5 = sequence4.synchronize(delays[folder + subject + "/" + sequence.name], audio, True)
    #
    #             except Exception as ex:
    #
    #                 print("\nIGNORING THIS SEQUENCE · Reason: "+str(ex))
    #                 ignored.append(sequence.name)
    #
    #             else:
    #
    #                 audio2 = audio.resample(8, "cubic", True)
    #                 preprocessed_sequences.append(sequence5)
    #                 preprocessed_audios.append(audio2)
    #
    #                 if len(sequence5.poses) != len(audio2.samples):
    #                     unmatched.append(sequence.name)
    #                     print(len)
    #                     print("/!\ Unmatching number of poses in the sequence (" + str(len(sequence5.poses)) +
    #                           ") and samples in the audio (" + str(len(audio2.samples)) + ".")
    #
    #                 save_sequence(sequence5, folder_out+subject, name_out=sequence.name, file_format="xlsx",
    #                               individual=False, correct_timestamp=True)
    #                 save_audio(audio2, folder_audio+subject, name_out=sequence.name, file_format="xlsx", individual=False)
    #
    #         else:
    #             print("\nIGNORING THIS SEQUENCE · Reason: Audio file doesn't exist.")
    #             ignored.append(sequence.name)
    #
    # coherence_with_audio(preprocessed_sequences, preprocessed_audios)
