Installing Krajjat
==================

Install the toolbox
-------------------
.. warning::

    Installing the toolbox on Mac requires to **first install the portaudio library.** See the
    :ref:`paragraph below <portaudio>`.

**Krajjat** is a Python package in development. You can install the dev version by running the following command line:

.. tabs::

    .. tab:: Unix/macOS

        .. code-block:: bash

            python3 -m pip install -i https://test.pypi.org/simple/ krajjat

    .. tab:: Windows

        .. code-block:: bash

            py -m pip install -i https://test.pypi.org/simple/ krajjat

In the future, Krajjat will be available on the main PyPi release channel. You will be able to install it using:

.. tabs::

    .. tab:: Unix/macOS

        .. code-block:: bash

            python3 -m pip install krajjat

    .. tab:: Windows

        .. code-block:: bash

            py -m pip install krajjat

.. _portaudio:

Special care
------------

PyAudio and PortAudio
^^^^^^^^^^^^^^^^^^^^^
Krajjat uses the module `PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_ to read the audio in the
:doc:`display functions <display_functions>`. On Mac, installing PyAudio requires to first install portaudio via
homebrew:

.. code-block:: bash

    brew install portaudio

.. note::
    This command line will only work if Homebrew is installed on your Mac. Click `here <https://brew.sh/>`_ to install
    it.

FFmpeg
^^^^^^
Saving video files using the function :func:`~display_functions.save_video_sequence` requires to have FFmpeg installed
on your device. However, the toolbox will likely function without any issue as long as this one function is not used.
To install FFmpeg on your system, `click here <https://ffmpeg.org/>`_.
