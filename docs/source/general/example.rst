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
    The initialisation function of :func:`Sequence.__init__` can take some parameters, among which:
        • ``name``: by default, the name will be inferred from the file name (here, it will be ``sequence_ainhoa``),
          but we can set a custom name using this parameter.
        • ``verbosity``: it allows to set how much text will be printed while running the sub-functions. In all
          the functions of the toolbox, this parameter is defined on ``1`` by default, providing a moderate amount
          of text. Setting it on ``0`` allows to have the function running completely silent, while setting it on
          ``2`` or more allows to get more information.

.. tip::
    It is possible to load multiple sequences from a folder, or even recursively through multiple subdirectories,
    using the :func:`io_functions.load_sequences` function. The loaded sequences will be returned as a list or a
    dictionary.

Looking at the data
-------------------

Let's first start by taking a look at the data. We can do it using either the :doc:`display functions`, or the plot functions.
The former will give you options to look at the film of the recording, while the latter provides functions to
visualize graphs of the mocap sequence.
We can take a look at the data by using various visualisation functions. First, let's just show the tracked points.
As we only want to see the joints, and not a skeleton, we will set ``show_lines`` on ``False``. We also want the joints
to appear in blue over a dark grey background:

.. code-block:: python

    >>> sequence_reader(sequence, show_lines=False, color_joint="sky blue", color_background=(20, 20, 20))

This function (along with all of the :doc:`../functions/display_functions`) allow for deep customization. You can find
all of the details in the :ref:`keyword_arguments_display_functions`.

We can also plot how the joints velocity vary across time:

.. code-block:: python

    >>> velocity_plotter(sequence)

Finally, we can print some statistics about the current sequence.

.. code-block:: python

    >>> sequence.print_stats()

Pre-processing
--------------

We can apply some pre-processing. First, we will "smooth-out" the data by correcting the movements over 1 meter per
second if the movement doesn't come back to the original position under 3 poses:

.. code-block:: python

    >>> sequence.correct_jitter(velocity_threshold=1, window=3)

