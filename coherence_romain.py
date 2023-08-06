import numpy as np
import matplotlib as plt

def plot_coherence(x, y, freq=8, window_size=4, overlap=2):

    x = np.array(x)
    y = np.array(y)
    y_flip = np.random.permutation(y)

    freq = 8  # Hz
    window_size = 4  # seconds
    overlap = 2  # seconds
    i = 0

    n = len(x)
    w = window_size * freq
    o = window_size * freq - overlap * freq

    x_segmented = np.zeros(shape=(int((n - w + 1) / (w - o)) + 1, window_size * freq))
    y_segmented = np.zeros(shape=(int((n - w + 1) / (w - o)) + 1, window_size * freq))
    y_flip_segmented = np.zeros(shape=(int((n - w + 1) / (w - o)) + 1, window_size * freq))

    for start_window in range(0, len(x) - (freq * window_size), (freq * window_size) - (freq * overlap)):
        x_segmented[i] = x[start_window:start_window + freq * window_size]
        y_segmented[i] = y[start_window:start_window + freq * window_size]
        y_flip_segmented[i] = y_flip[start_window:start_window + freq * window_size]
        i = i + 1

    fft_x = np.zeros(shape=(len(x_segmented), window_size * freq))
    fft_y = np.zeros(shape=(len(x_segmented), window_size * freq))
    fft_y_flip = np.zeros(shape=(len(x_segmented), window_size * freq))

    for segment in range(len(x_segmented)):
        fft_x[segment] = np.fft.fft(x_segmented[segment])
        fft_y[segment] = np.fft.fft(y_segmented[segment])
        fft_y_flip[segment] = np.fft.fft(y_flip_segmented[segment])

    fxx = np.mean(fft_x * np.conjugate(fft_x), 0)
    fyy = np.mean(fft_y * np.conjugate(fft_y), 0)
    fxy = np.mean(fft_x * np.conjugate(fft_y), 0)

    coherence_audio = (fxy * np.conj(fxy)) / (fyy * fxx)

    fxx = np.mean(fft_x * np.conjugate(fft_x), 0)
    fyy = np.mean(fft_y_flip * np.conjugate(fft_y_flip), 0)
    fxy = np.mean(fft_x * np.conjugate(fft_y_flip), 0)

    coherence_audio_flip = (fxy * np.conj(fxy)) / (fyy * fxx)

    print(coherence_audio)
    print(coherence_audio_flip)

    f = np.arange(0, freq, 1/window_size)
    print(f)

    plt.plot(f, coherence_audio)
    plt.plot(f, coherence_audio_flip)
    plt.xlabel('Frequency')
    plt.ylabel('Coherence')

    plt.show()