Dependencies
============

Here are the modules Krajjat uses to run properly.

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

Matplotlib and Seaborn
----------------------
`Matplotlib <https://matplotlib.org/>`_ is used for plotting the data in graphs, while
`Seaborn <https://seaborn.pydata.org/>`_ is used to make the graphs looking more attractive.

Openpyxl
--------
`openpyxl <https://openpyxl.readthedocs.io/en/stable/tutorial.html>`_ is used for opening and saving files in
`.xlsx` (Excel format).

Parselmouth
-----------
*To complete.*

Pygame
------
*To complete.*

cv2
---
*To complete.*

FFmpeg
------
`FFmpeg <https://ffmpeg.org/>`_ is necessary in order to generate videos with
:meth:`display_functions.save_video_sequence`.

.. warning::
    FFmpeg is not used as a Python module, but rather needs to be installed on your computer. While an installation of
    Krajjat using pip will install the other dependencies, you still need to manually install FFmpeg if you plan on
    using the toolbox to generate videos.