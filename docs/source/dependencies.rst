Dependencies
============

Here are the modules Krajjat uses to run properly:
    * `SciPy <https://docs.scipy.org/doc/scipy/>`_ for handling `.wav` files and getting the audio envelope, and for
      saving files in `.mat` format (Matlab)
    * `NumPy <https://numpy.org/>`_ for saving `.wav` files, and handling arrays for other dependencies.
    * Matplotlib
    * `openpyxl <https://openpyxl.readthedocs.io/en/stable/tutorial.html>`_ for opening and saving files in `.xlsx`
      (Excel format)
    * Parselmouth
    * Pygame
    * cv2


Moreover, it is necessary to have `FFmpeg <https://ffmpeg.org/>`_ installed on your computer in order to generate
videos with :meth:`display_functions.create_sequence_video`.