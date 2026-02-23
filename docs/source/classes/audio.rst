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
.. automethod:: krajjat.classes.audio.Audio.get_condition
.. automethod:: krajjat.classes.audio.Audio.get_samples
.. automethod:: krajjat.classes.audio.Audio.get_sample
.. automethod:: krajjat.classes.audio.Audio.get_number_of_samples
.. automethod:: krajjat.classes.audio.Audio.get_timestamps
.. automethod:: krajjat.classes.audio.Audio.get_duration
.. automethod:: krajjat.classes.audio.Audio.get_frequency
.. automethod:: krajjat.classes.audio.Audio.get_sampling_rate
.. automethod:: krajjat.classes.audio.Audio.get_info

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

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.filter_frequencies
.. automethod:: krajjat.classes.audio.Audio.resample
.. automethod:: krajjat.classes.audio.Audio.trim

Delay finding
^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.find_excerpt
.. automethod:: krajjat.classes.audio.Audio.find_excerpts

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.to_table
.. automethod:: krajjat.classes.audio.Audio.to_json
.. automethod:: krajjat.classes.audio.Audio.to_dict
.. automethod:: krajjat.classes.audio.Audio.to_dataframe

Saving function
^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.save
.. automethod:: krajjat.classes.audio.Audio.save_json
.. automethod:: krajjat.classes.audio.Audio.save_mat
.. automethod:: krajjat.classes.audio.Audio.save_excel
.. automethod:: krajjat.classes.audio.Audio.save_pickle
.. automethod:: krajjat.classes.audio.Audio.save_wav
.. automethod:: krajjat.classes.audio.Audio.save_txt

Copy function
^^^^^^^^^^^^^
.. automethod:: krajjat.classes.audio.Audio.copy