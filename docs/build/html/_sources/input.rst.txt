Compatible files
================

This page describes the structure of the files accepted by the toolbox. As of the most recent version, the accepted
file extensions are ``.csv``, ``.json``, ``.tsv``, ``.txt``, and ``.xlsx``. The toolbox accepts files containing the
entire information for a sequence (global files), or directories containing a series of files with the same extension,
with each file containing the information relative to a pose. In that case, the file names should be ``xxxxxx_0.ext``,
where ``xxxxxx`` can be any series of characters, ``0`` must be the index of the pose (with or without leading zeros),
and ``ext`` must be an accepted extension (``.csv``, ``.json``, ``.tsv``, ``.txt``, or ``.xlsx``). The first pose of the
sequence must have the index 0. If the file does not have an underscore in the name, it is ignored. The indices must be
coherent with the chronological order of the timestamps.

Sequences
---------

.. _table_example:

Tabled formats
^^^^^^^^^^^^^^
For ``.csv`` (comma-separated values), ``.xlsx`` (Microsoft Excel files), ``.tsv`` (tabulation-separated values) or
``.txt`` (text) files, the first line must always be the labels, with the first being ``"Timestamp"`` and the
subsequent labels being in group of three columns for each joint: respectively, one for the X, Y and Z coordinates.
Line 2 (in case of a single pose file) or lines 2 and on (in case of a global, sequence file) should contain the
timestamps in chronological order and the X, Y and Z coordinates for each joint. As an example, a file with two joints
and three poses should look like this:

+-----------+--------+--------+--------+-------------+-------------+-------------+
| Timestamp | Head_X | Head_Y | Head_Z | HandRight_X | HandRight_Y | HandRight_Z |
+===========+========+========+========+=============+=============+=============+
| 0         | 0.400  | 0.80   | 1.50   | 1.60        | 2.300       | 4.2         |
+-----------+--------+--------+--------+-------------+-------------+-------------+
| 0.125     | 0.1123 | 0.5813 | 0.2134 | 0.5589      | 0.1442      | 0.3337      |
+-----------+--------+--------+--------+-------------+-------------+-------------+
| 0.250     | 0.2008 | 0.0512 | 0.1519 | 0.2018      | 0.1515      | 0.1300      |
+-----------+--------+--------+--------+-------------+-------------+-------------+

.. note::
    Global ``.tsv`` files that are output from the QualiSys software will be detected automatically and do not need any
    type of processing to be used.

.. _json_example:

JSON format
^^^^^^^^^^^
For ``.json`` (JavaScript object notation) single-pose files, the structure must be a dictionary with at least two
entries: ``"Timestamp"`` and ``"Bodies"``. The value for ``"Bodies"`` must be a list containing a new dictionary with
an entry called ``"Joints"``. The value for ``"Joints"`` must be a dictionary containing an entry for each joint, under
the form of a dictionary with at least two keys: ``"JointType"``, which value is a string containing the label of the
joint, and ``"Position"``. The value for ``"Position"`` must be a final dictionary containing at least the three
entries ``"X"``, ``"Y"`` and ``"Z"``, with their coordinates as values. As an example, the data from the two first
lines in the table above should look like this in json form:

.. code-block:: json

    {"Timestamp": 0,
       "Bodies":
        [
            {"Joints":
                [
                    {"JointType": "Head",
                     "Position":
                        {"X": 0.400,
                         "Y": 0.80,
                         "Z": 1.50}
                    },
                    {"JointType": "HandRight",
                     "Position":
                        {"X": 1.60,
                         "Y": 2.300,
                         "Z": 4.2}
                    }
                ]
            }
        ]
    }

If the file is a global file, containing multiple poses, each pose must be an element of a list, with the structure of
each element being the same as described above. Note that dictionary entries other than the ones mentioned above will
be ignored by the toolbox.

Audio files
-----------

.. _wav_example:

WAV files
^^^^^^^^^
As of version 2.0, ``.wav`` files (Waveform Audio File Format) are the only accepted audio input files in the toolbox.
Other formats may be supported in the future. Upon opening, the toolbox will automatically detect the sample rate of the
file.

Text formats
^^^^^^^^^^^^
The audio samples can also be opened when they are in text form, as long as the files contain the samples and their
matching timestamps. Accepted formats are the same as for the Sequence files: ``.csv``, ``.json``, ``.tsv``, ``.txt``,
and ``.xlsx``.

Here is an acceptable table containing the formants of an audio file sampled at 8 Hz:

+-----------+--------+
| Timestamp | Sample |
+===========+========+
|         0 |      0 |
+-----------+--------+
|     0.125 |     -2 |
+-----------+--------+
|      0.25 |      3 |
+-----------+--------+
|     0.375 |     -4 |
+-----------+--------+
|       0.5 |     -5 |
+-----------+--------+
|     0.625 |      1 |
+-----------+--------+
|      0.75 |     63 |
+-----------+--------+
|     0.875 |      0 |
+-----------+--------+
|         1 |     -1 |
+-----------+--------+

In ``.json``, the content should be a dictionary with two entries, ``"Timestamp"`` and ``"Sample"``, both having a
list as values:

.. code-block:: json

    {"Timestamp":
        [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1],
     "Sample":
        [0, -2, 3, -4, -5, 1, 63, 0, -1]
    }

.. note::
    It is possible to have individual files for every sample. In that case, the name of the folder containing the
    individual audio samples should be passed as parameter upon creation of the :class:`Audio` object. This incredibly
    tedious way of opening and saving audio files has only been implemented to follow the same logic as for the Sequence
    files, and should be avoided.