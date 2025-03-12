Audio
=====

Description
-----------
Default class for audio recordings matching a Sequence, typically the voice of the subject of the motion capture. This
class allows to perform a variety of transformations of the audio stream, such as getting the envelope, pitch and
formants of the speech.

Initialisation
--------------
.. autoclass:: krajjat.classes.audio.Audio

Magic methods
-------------
.. automethod:: krajjat.classes.audio.Audio.__len__
.. automethod:: krajjat.classes.audio.Audio.__getitem__
.. automethod:: krajjat.classes.audio.Audio.__eq__
.. automethod:: krajjat.classes.audio.Audio.__repr__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.set_name
.. automethod:: krajjat.classes.audio.Audio.set_condition

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.get_path
.. automethod:: krajjat.classes.audio.Audio.get_name
.. automethod:: krajjat.classes.audio.Audio.get_samples
.. automethod:: krajjat.classes.audio.Audio.get_sample
.. automethod:: krajjat.classes.audio.Audio.get_number_of_samples
.. automethod:: krajjat.classes.audio.Audio.get_timestamps
.. automethod:: krajjat.classes.audio.Audio.get_duration
.. automethod:: krajjat.classes.audio.Audio.get_frequency

Copy function
^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.copy

Transformation functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. _get_envelope:
.. automethod:: krajjat.classes.audio.Audio.get_envelope
.. _get_pitch:
.. automethod:: krajjat.classes.audio.Audio.get_pitch
.. _get_intensity:
.. automethod:: krajjat.classes.audio.Audio.get_intensity
.. _get_formant:
.. automethod:: krajjat.classes.audio.Audio.get_formant
.. automethod:: krajjat.classes.audio.Audio.get_derivative
.. automethod:: krajjat.classes.audio.Audio.resample

Delay finding
^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.find_excerpt
.. automethod:: krajjat.classes.audio.Audio.find_excerpts

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.convert_to_table
.. automethod:: krajjat.classes.audio.Audio.convert_to_json
.. automethod:: krajjat.classes.audio.Audio.convert_to_dict
.. automethod:: krajjat.classes.audio.Audio.convert_to_dataframe

Saving function
^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.save
.. automethod:: krajjat.classes.audio.Audio.save_json
.. automethod:: krajjat.classes.audio.Audio.save_mat
.. automethod:: krajjat.classes.audio.Audio.save_excel
.. automethod:: krajjat.classes.audio.Audio.save_pickle
.. automethod:: krajjat.classes.audio.Audio.save_wav
.. automethod:: krajjat.classes.audio.Audio.save_txt

Private methods
---------------
Initialisation functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio._define_name_init
.. automethod:: krajjat.classes.audio.Audio._load_from_path
.. automethod:: krajjat.classes.audio.Audio._load_from_samples
.. automethod:: krajjat.classes.audio.Audio._load_samples
.. automethod:: krajjat.classes.audio.Audio._load_single_sample_file
.. automethod:: krajjat.classes.audio.Audio._load_audio_file
.. automethod:: krajjat.classes.audio.Audio._load_json_metadata
.. automethod:: krajjat.classes.audio.Audio._calculate_frequency
.. automethod:: krajjat.classes.audio.Audio._calculate_timestamps

Other function
^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio._set_attributes_from_other_audio