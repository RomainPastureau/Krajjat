Example of processing
=====================

You have recorded motion capture data and you wish to process the data and perform some analysis. This page will
guide you though a simple processing pipeline using a one-minute recording as an example.

Data to download
----------------
To run this tutorial, you will need to download the following data:
    * `Kinect data <https://github.com/RomainPastureau/Krajjat/tree/main/example/test_kinect>`_
    * `Qualisys data <https://github.com/RomainPastureau/Krajjat/tree/main/example/test_qualisys>`_

Import the data
---------------
First, you will need to import the toolbox and the necessary classes and functions:

.. code-block:: python

    >>> from krajjat import Sequence  # To define a mocap sequence
    >>> from krajjat import Audio  # To define an audio sequence
    >>> from krajjat import display_functions as kdisp # To take a look at the sequences
    >>> from krajjat import plot_functions as kplot  # To make some plots

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
    using the :func:`~krajjat.io_functions.load_sequences` function. The loaded sequences will be returned as a list or
    a dictionary.

Display the sequence
--------------------

Let's first start by taking a look at the data. We can do it using either the :doc:`../functions/display_functions`,
or the :doc:`../functions/plot_functions`. The former will give you options to look at the film of the recording,
while the latter provides functions to visualize graphs of the mocap sequence.

First, let's visualize the tracked points. As we only want to see the joints, and not a skeleton, we will set
``show_lines`` on ``False``. We also want the joints to appear in blue over a dark grey background:

.. code-block:: python

    >>> kdisp.sequence_reader(sequence, show_lines=False, color_joint_default="sky blue", color_background=(20, 20, 20))

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
It is possible using the parameters from :func:`~krajjat.display_functions.sequence_reader` called ``path_audio`` and
``path_video``. Let's try:

.. code-block:: python

    >>> kdisp.sequence_reader(sequence, path_audio="test_kinect/audio_ainhoa_trimmed.wav",
    ... path_video="test_kinect/video_ainhoa.mp4", show_lines=False, color_joint_default="sky blue")

It looks like the skeleton and the video are not synchronized... It's normal! The audio and the video were
actually pre-processed and the first few seconds were cut so the video starts just before the speech starts. Let's
use the :func:`~krajjat.classes.sequence.Sequence.trim` function to cut the first few seconds of the video. We know that
we cut ``11.13`` seconds from the video, so let's do the same for the mocap sequence:

.. code-block:: python

    >>> sequence_trimmed = sequence.trim(11.13)
    >>> kdisp.sequence_reader(sequence_trimmed, path_audio="test_kinect/audio_ainhoa_trimmed.wav",
    ... path_video="test_kinect/video_ainhoa.mp4", show_lines=False, color_joint_default="sky blue")

Now, it works! Let's try to display the sequence and the video next to each other, instead of superimposed:

.. code-block:: python

    >>> kdisp.sequence_reader(sequence_trimmed, path_audio="test_kinect/audio_ainhoa_trimmed.wav",
    ... path_video="test_kinect/video_ainhoa.mp4", show_lines=False, color_joint_default="sky blue",
    ... color_background=(20, 20, 20), position_video="side")

.. tip::
    If you wish to start the sequence on a specific pose, you can set the parameter ``start_pose`` -
    however, you might prefer to also have directly a manual control on the poses. In that case,
    you will want to run the function :func:`~krajjat.display_functions.pose_reader`. It takes the exact same
    parameters as :func:`~krajjat.display_functions.sequence_reader`, but starts the video paused, allowing to
    use the arrow keys to move pose by pose.

Plot the data
-------------

Single joint
^^^^^^^^^^^^
The toolbox offers multiple ways to plot the data. The first is to simply plot the `x`, `y` and `z` coordinates
of a specific joint (here, ``"HandRight"``) on separate graphs, along with the distance travelled between each
timestamp:

.. code-block:: python

    >>> kplot.single_joint_movement_plotter(sequence, "HandRight", ["x", "y", "z", "distance"])

.. tip::
    If you wish to plot the movement for another joint, you can get a list of the joint labels from
    the Sequence by calling :func:`~krajjat.classes.sequence.Sequence.get_joint_labels`.

Let's now try to plot some derivatives of the distance travelled: velocity, acceleration and jerk.

.. code-block:: python

    >>> kplot.single_joint_movement_plotter(sequence, "HandRight", ["v", "a", "j"])
    krajjat.classes.exceptions.VariableSamplingRateException: sequence_ainhoa

This returns an error: it is indeed not possible to calculate derivatives of the distance as the
sampling rate of the sequence is variable. This is a common problem with Kinect, and it can be
solved via resampling:

.. code-block:: python

    >>> sequence_resampled = sequence.resample(20)

.. tip::
    You can set the method used to interpolate the data via the parameter ``method``. See
    :func:`~krajjat.classes.sequence.Sequence.resample` for more information.

.. tip::
    You can plot the sampling rate of a sequence using the function :func:`~krajjat.plot_functions.framerate_plotter`:

    .. code-block:: python

        >>> kplot.framerate_plotter([sequence, sequence_resampled])

Now that we resampled our data, we can plot the derivatives:

.. code-block:: python

    >>> kplot.single_joint_movement_plotter(sequence_resampled, "HandRight", ["v", "a", "j"])

These measures can also be plotted in the frequency domain, just by setting the parameter ``domain``:

.. code-block:: python

    >>> kplot.single_joint_movement_plotter(sequence_resampled, "HandRight", ["d", "v", "a", "j"], domain="frequency")

.. tip::
    You can zoom in on a specific range of frequencies using the parameter ``xlim``, e.g. ``xlim=[1, 3]``.
    Because the line might seem a bit thin, you can also set the ``line_width`` to ``2``.

.. tip::
    When displaying time series in the frequency domain, the toolbox uses the function
    `scipy.signal.welch <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html?highlight=welch>`_.
    This function accepts to set the parameters:

        • ``nperseg``, which sets how many samples are taken per window to calculate the frequency. This
          defaults to 256, but a good value could be ``2/sequence.get_sampling_rate()`` (2-second windows).
        • ``window``, which defines what window to use - the default is ``"hann"`` (for *Hann* window),
          but an alternative could be ``"flattop"``. See the complete list of windows offered by scipy
          `here <https://docs.scipy.org/doc/scipy/reference/signal.windows.html>`_.

All the joints
^^^^^^^^^^^^^^
We can also plot one of these measures for all the joints. To do so, we need to use the function
:func:`~krajjat.plot_functions.joints_movement_plotter`:

.. code-block:: python

    >>> kplot.joints_movement_plotter(sequence_resampled, "velocity")

.. tip::
    The joints with the largest quantity of movement (as a sum) appear in red, while the ones with the less
    movement appear in green. It is possible to set the parameter ``color_scheme`` to one of the preset
    :doc:`../appendix/color_schemes`, or a personalized scheme set as a list of colors, such as
    ``["blue", "purple", "red"]``.

We can also overlay the audio to this plot, in order to see some correspondences in the shapes of the waves:

.. code-block:: python

    >>> audio = Audio("test_kinect/audio_ainhoa_trimmed.wav")
    >>> sequence_trimmed = sequence_resampled.trim(11.13)
    >>> sequence_trimmed.set_first_timestamp(0)
    >>> joints_movement_plotter(sequence_trimmed, "velocity", audio_or_derivative=audio, overlay_audio=True)

Get information
^^^^^^^^^^^^^^^
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

Pre-processing the sequence
---------------------------

Jitter correction and compare sequences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now that we have taken a good look at the data, we can see that it needs some pre-processing before the analysis. While
we already saw how to :ref:`resample <resample>` it to a constant sampling rate and how to :ref:`trim <trim>` it, we
might also want to :ref:`correct the jitter <correct_jitter>`, and :ref:`re-reference <re_reference>` the data.

Let's first correct the jitter. The toolbox uses the function :func:`krajjat.classes.sequence.Sequence.correct_jitter`,
which detects if the distance travelled by the different joints gets over a set threshold between two consecutive
frames. This threshold is set as a velocity, so we can work even if the framerate is not constant (a joint travelling
1 meter in 1 second will have the same velocity as a joint travelling 2 meters in 2 seconds).

Here, we will correct the jitter with a ``velocity_threshold`` of ``0.5`` meters per second. This means that, if between
two consecutive poses, the distance traveled by a joint divided by the time between these two poses is over 0.5,
the movement will be considered as jitter, and will be corrected.

The second parameter we need to set is ``window`` - defining whether a jitter movement is a *twitch* or a *jump*.
Basically, this parameter defines up to how many poses the function will check to see if the joint comes back within
threshold. We will set this parameter on ``3`` poses:

    • If the joint comes back more or less around where the jitter was detected within these 3 poses, the function will
      consider that it was a twitch - an artifact due to the poor detection of the position of the joint, that lasted 1
      or 2 poses. The function will correct the position of the poses in between to remove the anomalous movement.
    • Otherwise, if after 3 poses, the joint still didn't come back around its original position, it's a jump: another
      artefact due to the material missing the joint moving, and suddenly correcting for its new position. The function
      will try to smooth out this movement by interpolating where the joint was during these 3 poses.

You can get illustrations of how this function works on the :doc:`../general/dejittering` page.

.. code-block:: python

    >>> sequence_cj = sequence.correct_jitter(velocity_threshold=0.5, window=3)

Let's see what our changes look like, using the function :func:`~krajjat.plot_functions.sequence_comparer`:

.. code-block:: python

    >>> kdisp.sequence_comparer(sequence, sequence_cj)

.. tip::
    On the right side of the window, the jitter-corrected sequence has its corrected joints in green. You can set
    this color manually with the parameter ``color_joint_corrected``.

.. tip:: Window resolution
    By default, the display windows are set on 50% of the horizontal and vertical resolution of your screen. As we
    display two sequences side to side, this ratio becomes 100% horizontally; you can customize this by setting the
    parameter ``resolution`` to a float (e.g. ``0.4`` will result in a window that is 40% of your vertical screen size,
    and 2×40% = 80% of your horizontal screen size) or a tuple to directly set the window resolution (e.g.
    ``(1920 × 1080)``). You can also choose to go fullscreen with the parameter ``fullscreen=True``. In that case,
    press Escape to quit.

Re-referencing
^^^^^^^^^^^^^^
Another step that can be performed is to re-reference the data, i.e. to set the movements of all the joints relative
to another (typically, one that does not move a lot, like ``SpineMid``).

Let's try this (be sure to work on the jitter_corrected sequence, output of the previous function we used):

.. code-block:: python

    >>> sequence_reref = sequence_cj.re_reference("SpineMid")

Once again, we can compare our changes:

.. code-block:: python

    >>> kdisp.sequence_comparer(sequence_cj, sequence_reref)

The sequence on the right is all green - which makes sense, we modified the value of all the joints. Just press the
letter C on your keyboard to toggle the view of the corrected joints.

Trimming the sequence to the audio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The next step is to make sure that our sequence and our audio are the same duration. We already know that we need to
trim 11.13 seconds from the beginning of the sequence to synchronize the two:

.. code-block:: python

    >>> sequence_tr = sequence_reref.trim(11.13)

Now, let's compare the duration of the sequence and the audio:

.. code-block:: python

    >>> print(sequence_tr.get_duration())
    67.9100086
    >>> audio = Audio("test_kinect/audio_ainhoa_trimmed.wav")
    >>> print(audio.get_duration())
    63.40264583333333

The audio is slightly shorter than the sequence. It is important to have the same duration in both, so that we can then
get the same amount of samples to perform the analyses. Thankfully, the function
:func:`~krajjat.classes.sequence.Sequence.trim_to_audio` allows to trim the sequence to the audio pretty easily:

.. code-block:: python

    >>> sequence_tr_audio = sequence_tr.trim_to_audio(audio=audio)

.. tip::
    This function also allows to pass the path to a WAV file as a parameter, instead of an
    :class:`~krajjat.classes.audio.Audio` object.

.. tip::
    We can also combine both :func:`~krajjat.classes.sequence.Sequence.trim` and
    :func:`~krajjat.classes.sequence.Sequence.trim_to_audio` by setting the delay of 11.13 as the first parameter
    of the latter function:

    .. code-block:: python

        >>> sequence_tr_audio = sequence_tr.trim_to_audio(11.13, audio)

.. tip::
    If you wish to visualize the sequence superimposed over a video file after trimming, you can use the parameter
    ``timestamp_video_start`` of any of the :doc:`../functions/display_functions`. Set this parameter on the same
    start value than the one you used for the trimming.

Resampling, filtering, and keeping track of the pre-processing steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Finally, we will resample the sequence to 20 Hz to ensure a constant sampling rate, and apply a band-pass filter using
:func:`~krajjat.classes.sequence.Sequence.filter_frequencies`. This last step will allow us to get rid of the very low
oscillations (below 0.1 Hz). If you set a value for ``filter_over``, make sure that it is **less** than half of the
sampling rate of the sequence.

.. code-block:: python

    >>> sequence_resampled = sequence_tr_audio.resample(20)
    >>> sequence_ff = sequence_resampled.filter_frequencies(filter_below=0.1, filter_over=8)

We have performed six pre-processing steps so far: jitter correction, re-referencing, trimming, trimming to audio,
resampling, and frequency filtering. In order to keep track of all of these steps, we can check the attribute
:attr:``~krajjat.classes.sequence.Sequence.metadata`` of the sequence. A lot of things might be in there, because the
metadata imports the data from the original file. The data we are interested in is in the key ``"processing_steps``.
This is a list, where each element matches, in order, a processing step, with all the parameters used.

.. code-block:: python

    >>> print(sequence_resampled.metadata["processing_steps"])
    [{'processing_type': 'correct_jitter', 'velocity_threshold': 0.5, 'window': 3, 'window_unit': 'poses', 'method': 'default', 'correct_twitches': True, 'correct_jumps': True},
     {'processing_type': 're_reference', 'reference_joint_label': 'SpineMid', 'place_at_zero': True},
     {'processing_type': 'trim', 'start': 11.13, 'end': 79.0833823, 'use_relative_timestamps': False},
     {'processing_type': 'trim', 'start': 0, 'end': np.float64(63.40264583333333), 'use_relative_timestamps': True},
     {'processing_type': 'resample', 'frequency': 20, 'method': 'cubic', 'window_size': 10000000.0, 'overlap_ratio': 0.5},
     {'processing_type': 'filter_frequencies', 'filter_below': 0.1, 'filter_over': 8}]

Saving the data
^^^^^^^^^^^^^^^
Our pre-processing is done, we can now save our sequence in the format we choose, among:

    • :ref:`JSON <json_example>`, which will save the data in text form with nested lists and dictionaries.
    • Excel (``.xlsx``).
    • Matlab (``.mat``).
    • Pickle (``.pkl``), which serializes the data in non-readable form.
    • CSV, which will save the data as a table in text form, with coma-separated (or semicolon, depending on your
      localization) values.
    • TSV, TXT or custom extensions, which will save the data as a table in text form, with tab-separated values.

All table formats follow the standard :ref:`detailed here <table_example>`. We will choose here to save the data in TSV
format:

.. code-block:: python

    >>> sequence_ff.save("test_kinect/sequence_preprocessed.tsv")

.. tip::
    You can choose whether you want to save the metadata in the file or not (by default, the metadata is saved).
    The metadata is saved differently depending on the format:

        • For JSON files, the metadata is saved at the top level. Metadata keys will be saved next to the "Poses" key.
        • For MAT files, the metadata is saved at the top level of the structure.
        • For Excel files, the metadata is saved in a second sheet.
        • For pkl files, the metadata will always be saved as the object is saved as-is - this parameter is thus ignored.
        • For all the other formats, the metadata is saved at the beginning of the file.

Pre-processing the audio
------------------------
Pre-processing the audio file will only consist in getting an audio derivative, resampling it, and applying a band-pass
filter to it.

.. tip::
    If our audio file was longer than our sequence, we could also use the :func:`~krajjat.classes.audio.Audio.trim`
    function, which works the same way as for the sequence. But, as we already saw, here we do not need that, as it is
    the sequence that is longer than the audio.

We can get one of four audio derivatives:

    • The envelope, via :func:`~krajjat.classes.audio.Audio.get_envelope`.
    • The intensity, via :func:`~krajjat.classes.audio.Audio.get_intensity`.
    • The pitch, via :func:`~krajjat.classes.audio.Audio.get_pitch`.
    • One of the formants, via :func:`~krajjat.classes.audio.Audio.get_formant`.

All of these functions (apart for the envelope) make use of `parselmouth <https://parselmouth.readthedocs.io/en/stable/>`_,
which is a Python library making use of the Praat software. In our case, we will get the envelope and the pitch:

.. code-block:: python

    >>> audio = Audio("test_kinect/audio_ainhoa_trimmed.wav")
    >>> envelope = audio.get_envelope()
    >>> envelope_resampled = envelope.resample(20)
    >>> envelope_ff = envelope_resampled.filter_frequencies(0.1, 8)
    >>> envelope_ff.save("test_kinect/envelope.tsv")
    >>> pitch = audio.get_pitch()
    >>> pitch_resampled = pitch.resample(20)
    >>> pitch_ff = pitch_resampled.filter_frequencies(0.1, 8)
    >>> pitch_ff.save("test_kinect/pitch.tsv")

.. note::
    While the calculation of the envelope is optimized, and pretty fast, the other derivatives can be resource-intensive
    and take some time to calculate. If you are batch processing many audio files, make sure to progressively delete the
    objects you do not need to use.

Analysis
--------
Our sequence is ready, along with the envelope and pitch of the audio. We can now start to analyze our data!

**Coming up next as soon as the analyses functions are ready!**

Use of other data
-----------------
If you followed this tutorial, you should now be able to follow the same steps with the
`Qualisys files <https://github.com/RomainPastureau/Krajjat/tree/main/example/test_qualisys>`_. The processing should
be very similar, with the following exceptions:

    • The sequence in already has a stable sampling rate of 200 Hz, but we recommend that you downsample the sequence
      anyway to 50 Hz (you can then apply a band pass filter between 0.1 and 20 Hz). Do the same for the audio.
    • Some data is missing: you need to interpolate it using the functions :func:`~krajjat.classes.sequence.Sequence.interpolate_missing_data`.
    • The audio delay is 4.166 seconds.
