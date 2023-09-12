Release notes
=============

Version 2.0 (01/09/2023)
------------------------
* General
    * Krajjat acronym now means *Kinetic Recordings And Juxtaposition of Jabbering Along That*.
    * Alternatively, it can mean *Kinetic Recordings Algorithms for Joint Jazzing in an All-in-one Toolbox*.
    * Yes, it was a bad idea to have two Js in a row in an acronym.
    * Sphinx documentation added for each function and for the whole project.
    * Adding support for the Qualisys system (44 joints).
    * Now handles all HTML color names for creating color schemes.
    * Renamed functions and attributes to be more transparent with their use.
    * Added custom exceptions.
    * Large code sweeping.
* Sequence
    * Compatibility with TSV files in reading/writing, and with MAT files in writing only.
    * Added a correct_zeros function for Qualisys recordings.
    * Added non-linear de-jittering and window selection based on time instead of number of poses.
    * Added a large number of getter methods for Sequence objects.
* Audio
    * Adding AudioDerivatives classes: Envelope, Pitch, Intensity and Formant.
* Display functions
    * Possibility to generate a video (MP4) of a motion sequence from a recording.
    * Possibility to visualize the sequence on top of a video, or adding audio.
* Stats/Plot functions
    * Correlation, cross-correlation and coherence between a sequence or a series of sequences and a joint or an audio
      file.
    * Allows to display correlation and cross-correlation results on a silhouette.

Version 1.11 (25/11/2022)
-------------------------
* Correction of the realignment algorithm. Toggle between one and the other with the argument ``"mode"`` set as
  ``"new"`` or ``"false"``.
* Correction of the gestion of time, relative_time is the one used by default now.
* Correlation between a sequence or a series of sequences and an audio file.

Version 1.10 (15/11/2022)
-------------------------
* Trim a motion sequence according to delay and audio duration, or to starting and ending timestamps.
* Resample a motion sequence according to a frequency.
* Add a name to the sequences.
* Verbosity has now three levels: 2 is for showing all the info, 1 is for showing some info, 0 is for being completely
  opaque.
* Performance and code sweeping.

Version 1.9 (02/11/2022)
------------------------
* Save and open sequences in new formats, including .json, .txt, .csv, and .xlsx. For the csv files,
  option to choose the separator.
* Possibility to save the sequences under one file per pose or one meta-file for the whole sequence.
* Get the stats from recordings (duration, average framerate, minimum framerate, maximum framerate, number of poses)
  for one or more recordings, and output them as a table.
* Visualize the framerate across time using the framerate_visualizer function.
* Batch open many sequences in a list with ``batch_loader`` and ``batch_loader_recursive``.
* Code sweeping.

Version 1.8 (18/10/2022)
------------------------
* Added a function to re-reference all the joints to a reference joint (default: SpineMid). As for the realignment, the
  function can be called for a single file, a whole folder or a recursive path. This function can also place the
  reference joint at the coordinate (0, 0, 0).
* Created a tool function that allows to return the unique differences between two paths. For example, if the inputs are
  ``"C:/Documents/Kinect/John/Videos/A001"`` and ``"C:/Documents/Kinect/Paul/Videos/A001"``, the function will return
  ``"John"`` and ``"Paul"``.
* The Pose Reader now allows to show the image frames in the background of the poses.
* The Joint Temporal Plotter function now can plot more than one sequence, and align automatically sequences that are
  trimmed from others.
* In the classes file, changed the name of the variable ``"joint_number"`` to ``"joint_name"``.

.. note::
	Versions before 1.8 did not have release notes.