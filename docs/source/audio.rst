Audio
=====

Description
-----------
Default class for audio recordings matching a Sequence, typically the voice of the subject of the motion capture. This
class allows to perform a variety of transformations of the audio stream, such as getting the envelope, pitch and
formants of the speech.

Initialisation
--------------
.. autoclass:: classes.audio.Audio

Magic methods
-------------

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.audio.Audio.set_name

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.audio.Audio.get_path
.. automethod:: classes.audio.Audio.get_name
.. automethod:: classes.audio.Audio.get_samples
.. automethod:: classes.audio.Audio.get_sample
.. automethod:: classes.audio.Audio.get_number_of_samples
.. automethod:: classes.audio.Audio.get_timestamps
.. automethod:: classes.audio.Audio.get_duration
.. automethod:: classes.audio.Audio.get_frequency

Transformation functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.audio.Audio.get_envelope
.. automethod:: classes.audio.Audio.resample

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.audio.Audio.convert_to_table
.. automethod:: classes.audio.Audio.convert_to_json

Saving function
^^^^^^^^^^^^^^^
.. automethod:: classes.audio.Audio.save

Private methods
---------------
Initialisation functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.audio.Audio._define_name_init
.. automethod:: classes.audio.Audio._load_from_path
.. automethod:: classes.audio.Audio._load_from_samples
.. automethod:: classes.audio.Audio._fetch_files_from_folder
.. automethod:: classes.audio.Audio._load_samples
.. automethod:: classes.audio.Audio._load_single_sample_file
.. automethod:: classes.audio.Audio._load_audio_file
.. automethod:: classes.audio.Audio._read_wav
.. automethod:: classes.audio.Audio._read_text_file
.. automethod:: classes.audio.Audio._calculate_frequency
.. automethod:: classes.audio.Audio._calculate_timestamps

Saving functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.audio.Audio._save_json
.. automethod:: classes.audio.Audio._save_mat
.. automethod:: classes.audio.Audio._save_xlsx
.. automethod:: classes.audio.Audio._save_txt