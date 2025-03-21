Example of processing
=====================

You have recorded motion capture data and you wish to process the data and perform some analysis. This page will
guide you though a simple processing pipeline using a one-minute recording as an example.

Data to download
----------------
To run this tutorial, you will need to download the following data:
    * Kinect data
    * Qualisys data

Importing the data
------------------

First, you will need to import the toolbox and the necessary classes and functions:

.. code-block:: python

    >>> from krajjat.classes.sequence import Sequence  # To define a mocap sequence
    >>> from krajjat.classes.audio import Audio  # To define an audio sequence
    >>> from krajjat.display_functions import * # To take a look at the sequences
    >>> from krajjat.plot_functions import *  # To make some plots

We can then open the sequence by specifying its path. Let's say we have our data saved as ``"sequence1.json"``:

.. code-block:: python

    >>> sequence = Sequence("test_kinect/sequence_ainhoa.json")
    Opening sequence from test_kinect\sequence_ainhoa.json... 10% 20% 30% 40% 50% 60% 70% 80% 90% 100% - Done.

.. tip::
    The initialisation function of :class:`~krajjat.classes.sequence.Sequence` can take some parameters, among which:
        • ``name``: by default, the name will be inferred from the file name (here, it will be ``sequence_ainhoa``),
          but we can set a custom name using this parameter.
        • ``verbosity``: it allows to set how much text will be printed while running the sub-functions. In all
          the functions of the toolbox, this parameter is defined on ``1`` by default, providing a moderate amount
          of text. Setting it on ``0`` allows to have the function running completely silent, while setting it on
          ``2`` or more allows to get more information.

.. tip::
    It is possible to load multiple sequences from a folder, or even recursively through multiple subdirectories,
    using the :func:`~krajjat.io_functions.load_sequences` function. The loaded sequences will be returned as a list or a
    dictionary.

Display the sequence
--------------------

Let's first start by taking a look at the data. We can do it using either the :doc:`../functions/display_functions`,
or the :doc:`../functions/plot_functions`. The former will give you options to look at the film of the recording,
while the latter provides functions to visualize graphs of the mocap sequence.

 First, let's visualize the tracked points. As we only want to see the joints, and not a skeleton, we will set
``show_lines`` on ``False``. We also want the joints to appear in blue over a dark grey background:

.. code-block:: python

    >>> sequence_reader(sequence, show_lines=False, color_joint_default="sky blue", color_background=(20, 20, 20))

.. tip::
    While the film runs, you can control the display with your mouse and keyboard. A summary of these controls can
    be found on the :doc:`../functions/display_functions` page, but here are some essentials:
    • You can set the **zoom level** with the scrolling wheel of your mouse.
    • You can **drag the skeleton** around using the left button of your mouse.
    • You can **pause** the video by pressing the space bar.
    • Once paused, you can **move pose to the next or previous pose** by pressing the left and right arrow keys.
    • You can toggle **showing connecting lines** on the skeleton by pressing the L key.
    • You can **save a screenshot** of the current pose by pressing the S key. This will save in the current working
      directory.

.. tip::
    This function (along with all of the :doc:`../functions/display_functions`) allow for deep customization. You can
    find all of the details in the :ref:`keyword_arguments_display_functions`.

Displaying the motion capture video is one thing, but what if we added, on top, the audio and video recording?
It is possible using the parameters from `~krajjat.display_functions.sequence_reader` called ``path_audio`` and
``path_video``. Let's try:

.. code-block:: python

    >>> sequence_reader(sequence, path_audio="test_kinect/audio_ainhoa_trimmed.wav",
    ... path_video="test_kinect/video_ainhoa.mp4", show_lines=False, color_joint_default="sky blue")

It looks like the skeleton and the video are not synchronized... It's normal! The audio and the video were
actually pre-processed and the first few seconds were cut so the video starts just before the speech starts. Let's
use the `~krajjat.classes.sequence.Sequence.trim` function to cut the first few seconds of the video. We know that
we cut ``11.13`` seconds from the video, so let's do the same for the mocap sequence:

.. code-block:: python

    >>> sequence_trimmed = sequence.trim(11.13)
    >>> sequence_reader(sequence_trimmed, path_audio="test_kinect/audio_ainhoa_trimmed.wav",
    ... path_video="test_kinect/video_ainhoa.mp4", show_lines=False, color_joint_default="sky blue")

Now, it works! Let's try to display the sequence and the video next to each other, instead of superimposed:

.. code-block:: python

    >>> sequence_reader(sequence_trimmed, path_audio="test_kinect/audio_ainhoa_trimmed.wav",
    ... path_video="test_kinect/video_ainhoa.mp4", show_lines=False, color_joint_default="sky blue",
    ... color_background=(20, 20, 20), position_video="side")

.. tip::
    If you wish to start the sequence on a specific pose, you can set the parameter ``start_pose`` -
    however, you might prefer to also have directly a manual control on the poses. In that case,
    you will want to run the function `~krajjat.display_functions.pose_reader`. It takes the exact same
    parameters as `~krajjat.display_functions.sequence_reader`, but starts the video paused, allowing to
    use the arrow keys to move pose by pose.

Plot the data
-------------
The toolbox offers multiple ways to plot the data. The first is to simply plot the `x`, `y` and `z` coordinates
of a specific joint (here, ``"HandRight"``) on separate graphs, along with the distance travelled between each
timestamp:

.. code-block:: python

    >>> single_joint_movement_plotter(sequence, "HandRight", ["x", "y", "z", "distance"])

.. tip::
    If you wish to plot the movement for another joint, you can get a list of the joint labels from
    the Sequence by calling `~krajjat.classes.sequence.Sequence.get_joint_labels`.

Let's now try to plot some derivatives of the distance travelled: velocity, acceleration and jerk.

.. code-block:: python

    >>> single_joint_movement_plotter(sequence, "HandRight", ["v", "a", "j"])
    krajjat.classes.exceptions.VariableSamplingRateException: sequence_ainhoa

This returns an error: it is indeed not possible to calculate derivatives of the distance as the
sampling rate of the sequence is variable. This is a common problem with Kinect, and it can be
solved via resampling:

.. code-block:: python

    >>> sequence_resampled = sequence.resample(20)

.. tip::
    You can set the method used to interpolate the data via the parameter ``method``. See
    `~krajjat.classes.sequence.Sequence.resample` for more information.

Now that we resampled our data, we can plot the derivatives:

.. code-block:: python

    >>> single_joint_movement_plotter(sequence_resampled, "HandRight", ["v", "a", "j"])

These measures can also be plotted in the frequency domain, just by setting the parameter ``domain``:

.. code-block:: python

    >>> single_joint_movement_plotter(sequence_resampled, "HandRight", ["d", "v", "a", "j"], domain="frequency")

.. tip::
    You can zoom in on a specific range of frequencies using the parameter ``xlim``, e.g. ``xlim=[1, 3]``.
    Because the line might seem a bit thin, you can also set the ``line_width`` to ``2``.

We can also plot one of these measures for all the joints. To do so, we need to use the function
`~krajjat.plot_functions.joints_movement_plotter`:

.. code-block:: python

    >>> joints_movement_plotter(sequence_resampled, "velocity")

.. tip::
    The joints with the largest quantity of movement (as a sum) appear in red, while the ones with the less
    movement appear in green. It is possible to set the parameter ``color_scheme`` to one of the preset
    :doc:`color_schemes`, or a personalized scheme set as a list of colors, such as ``["blue", "purple", "red"]``.

We can also overlay the audio to this plot, in order to see some correspondences in the shapes of the waves:

.. code-block:: python

    >>> audio = Audio("test_kinect/audio_ainhoa_trimmed.wav")
    >>> sequence_trimmed = sequence_resampled.trim(11.13)
    >>> sequence_trimmed.set_first_timestamp(0)
    >>> joints_movement_plotter(sequence_trimmed, "velocity", audio_or_derivative=audio, overlay_audio=True)

Finally, we can print some statistics about the current sequence.

.. code-block:: python

    >>> print(sequence.get_info(return_type="str"))
    Name: sequence_ainhoa
    Path: test_kinect\sequence_ainhoa.json
    Condition: None
    Duration: 79.0833823 s
    Number of poses: 1269
    Number of joint labels: 21
    Date of recording: Tuesday 10 August 2021, 15:08:40
    Subject height: 1.62 m
    Left arm length: 0.508 m
    Right arm length: 0.508 m
    Stable sampling rate: False
    Average sampling rate: 16.345829847776503
    SD sampling rate: 1.9394353845232761
    Min sampling rate: 4.232300835329216
    Max sampling rate: 21.118209175860837

Pre-processing
--------------
Now that we have taken a good look at the data, we can consider analyzing it. Before we can do so, though,
we need first to pre-process the data.

The first step will consist in removing the jitter that we could observe when we displayed the sequence:

.. code-block:: python

    >>> sequence.correct_jitter(velocity_threshold=1, window=3)

Analysis
--------
To be filled.
