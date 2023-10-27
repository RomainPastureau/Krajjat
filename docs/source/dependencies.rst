Dependencies
============

As of the most recent version, Krajjat relies on 10 other python packages and 1 software in order to run all the
functions properly. When installing Krajjat, all the dependencies should install automatically. However, **you may
encounter some issues with PyAudio**: if you do so, check the corresponding paragraph below. You will also need to
install FFmpeg if you want to create videos from the toolbox.

chardet
-------
`Chardet <https://chardet.readthedocs.io/en/latest/>`_ is used when opening a text file, to automatically detect the
encoding.

cv2
---
`OpenCV <https://opencv.org/>`_ is used to read the frames from the video files in the display functions.

Matplotlib and Seaborn
----------------------
`Matplotlib <https://matplotlib.org/>`_ is used for plotting the data in graphs, while
`Seaborn <https://seaborn.pydata.org/>`_ is used to make the graphs looking more attractive.

Numpy
-----
`NumPy <https://numpy.org/>`_ is used to handle large arrays for faster computation:

    * `array <https://numpy.org/doc/stable/reference/generated/numpy.array.html>`_ and
      `ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_ types are used to perform faster
      computation on large arrays.
    * `NaN <https://numpy.org/doc/stable/reference/constants.html#numpy.NaN>`_ (acronym of Not A Number) is used to
      in order to replace missing data. This allows to not plot the missing data as zero values.

.. note::
    The Audio object uses ndarrays by default for all of its values. In a future version of the toolbox, it is planned
    to turn the lists in Sequence and Pose to ndarrays for faster computation.

Openpyxl
--------
`openpyxl <https://openpyxl.readthedocs.io/en/stable/tutorial.html>`_ is used for opening and saving files in
`.xlsx` (Excel format).

Parselmouth
-----------
`Parselmouth <https://parselmouth.readthedocs.io/en/stable/>`_ is used for computing the intensity, the pitch and the
formants of the voice included in audio clips (the envelope is computed via SciPy).

PyAudio
-------
`PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_ is a module allowing to read audio streams. It is used
in the toolbox to read audio files in the :doc:`display_functions`.

.. warning::
    On Windows, PyAudio should install without any issue. However:

        * On Mac, you should first ensure that ``portaudio`` has been installed, using the command line
          ``brew install portaudio``.
        * On Linux, you should also be sure to have `portaudio <https://portaudio.com/>`_ installed.

Pygame
------
`Pygame <https://www.pygame.org/news>`_ is a module allowing to display graphic elements in a window. While originally
designed for creating video games, in Krajjat it is used for:

    * Displaying the sequences in all of the :doc:`display_functions`.
    * Displaying the silhouette in :doc:`plot_functions`.

Scipy
-----
`SciPy <https://docs.scipy.org/doc/scipy/>`_ is used for:

    * Reading and writing `.wav` files, using `scipy.io.wavfile.read <https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html>`_
      and `scipy.io.wavfile.write <https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html>`_
    * Getting the audio envelope using a hilbert transform, using `scipy.signal.hilbert <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.hilbert.html>`_
    * Applying band-pass filters, using `scipy.signal.butter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>`_
      and `scipy.signal.lfilter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html>`_
    * Saving files in `.mat` format (Matlab), using `scipy.io.savemat <https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.savemat.html>`_
    * Interpolating data using the `scipy.interpolate.interp1d <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_
      function

FFmpeg
------
`FFmpeg <https://ffmpeg.org/>`_ is necessary in order to generate videos with
:meth:`display_functions.save_video_sequence`.

.. warning::
    FFmpeg is not used as a Python module, but rather needs to be installed on your computer. While an installation of
    Krajjat using pip will install the other dependencies, you still need to manually install FFmpeg if you plan on
    using the toolbox to generate videos.