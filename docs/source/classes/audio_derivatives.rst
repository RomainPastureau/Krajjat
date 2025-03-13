Audio derivatives
=================

Description
-----------
Classes for time series derived from audio clips: Envelope, Intensity, Pitch and Formants.

Initialisation
--------------

AudioDerivative
^^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.audio_derivatives.AudioDerivative

Note
^^^^
This class is a parent class for :class:`Envelope`, :class:`Pitch`, :class:`Intensity` and :class:`Formant`. This class
should not be called directly: instead, the methods should be called through the child classes when an object is
created by one of the instances of the class :class:`Audio`.

All of the following classes inherit from AudioDerivative: all the methods described above can then be used for any
object from the classes below.

Envelope
^^^^^^^^
.. autoclass:: krajjat.classes.audio_derivatives.Envelope

Pitch
^^^^^
.. autoclass:: krajjat.classes.audio_derivatives.Pitch

Intensity
^^^^^^^^^
.. autoclass:: krajjat.classes.audio_derivatives.Intensity

Formant
^^^^^^^
.. autoclass:: krajjat.classes.audio_derivatives.Formant

Magic methods
-------------
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.__len__
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.__getitem__
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.__repr__
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.__eq__

Public methods
--------------

Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.set_name
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.set_condition

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_path
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_name
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_condition
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_samples
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_sample
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_number_of_samples
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_timestamps
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_duration
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_frequency
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_info

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.filter_frequencies
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.resample
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.trim

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.to_table
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.to_json
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.to_dict
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.to_dataframe

Saving function
^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.save
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.save_json
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.save_mat
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.save_excel
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.save_pickle
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.save_wav
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.save_txt

Copy function
^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.copy

Private methods
---------------

Initialisation methods
^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._load_from_path
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._load_from_samples
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._load_samples
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._load_single_sample_file
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._load_audio_derivative_file
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._load_json_metadata
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._calculate_frequency
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative._calculate_timestamps

Special method
^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.Formant._load_formant_number

