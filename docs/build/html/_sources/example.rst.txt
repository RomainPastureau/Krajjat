Example of processing
=====================

You have recorded motion capture data and you wish to process the data and perform some analysis. This page will
guide you though a simple processing pipeline using a one-minute recording as an example.

Importing the data
------------------

First, you will need to import the toolbox.

.. code-block:: python

    >>> from krajjat import *
    >>> from krajjat.classes import *

We will then open the sequence by specifying its path. Let's say we have our data saved as ``"sequence1.csv"``:

.. code-block:: python

    >>> sequence = Sequence("C:/Users/Farnsworth/MoCap/sequence1.csv")
    Opening sequence from C:/Users/Farnsworth/MoCap/sequence1.csv... 100% - Done.

.. note::
    It is possible to load multiple sequences from a folder, or even recursively through multiple subdirectories,
    using the :func:`io_functions.load_sequences` function. The loaded sequences will be returned as a list or a
    dictionary.

Looking at the data
-------------------

We can take a look at the data by using various visualisation functions. First, let's just show the tracked points.
As we only want to see the joints, and not a skeleton, we will set ``show_lines`` on ``False``. We also want the joints
to appear in blue over a dark grey background:

.. code-block:: python

    >>> sequence_reader(sequence, show_lines=False, color_joint="sky blue", color_background=(20, 20, 20))

This function (along with all of the :doc:`display_functions`) allow for deep customization. You can find all of the
details in the :ref:`keyword_arguments_display_functions`.

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

