Sequence
========

Description
-----------
Default class for motion sequences in the toolbox. An instance of this class will be
one motion sequence. The class contains several methods to perform **pre-processing** or
**displaying summarized data** in text form (see public methods).

Initialisation
--------------
.. autoclass:: krajjat.classes.sequence.Sequence

Magic methods
-------------
.. automethod:: krajjat.classes.sequence.Sequence.__len__
.. automethod:: krajjat.classes.sequence.Sequence.__getitem__
.. automethod:: krajjat.classes.sequence.Sequence.__repr__
.. automethod:: krajjat.classes.sequence.Sequence.__eq__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.set_name
.. automethod:: krajjat.classes.sequence.Sequence.set_condition
.. automethod:: krajjat.classes.sequence.Sequence.set_path_audio
.. automethod:: krajjat.classes.sequence.Sequence.set_first_timestamp
.. automethod:: krajjat.classes.sequence.Sequence.set_date_recording

Pose functions
^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.add_pose
.. automethod:: krajjat.classes.sequence.Sequence.add_poses

Getter functions
^^^^^^^^^^^^^^^^

General
"""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_path
.. automethod:: krajjat.classes.sequence.Sequence.get_name
.. automethod:: krajjat.classes.sequence.Sequence.get_condition
.. automethod:: krajjat.classes.sequence.Sequence.get_system
.. automethod:: krajjat.classes.sequence.Sequence.get_joint_labels
.. automethod:: krajjat.classes.sequence.Sequence.get_number_of_joints
.. automethod:: krajjat.classes.sequence.Sequence.get_date_recording
.. automethod:: krajjat.classes.sequence.Sequence.get_subject_height
.. automethod:: krajjat.classes.sequence.Sequence.get_subject_arm_length
.. automethod:: krajjat.classes.sequence.Sequence.get_info
.. automethod:: krajjat.classes.sequence.Sequence.get_fill_level

Poses
"""""
.. automethod:: krajjat.classes.sequence.Sequence.get_poses
.. automethod:: krajjat.classes.sequence.Sequence.get_pose
.. automethod:: krajjat.classes.sequence.Sequence.get_pose_index_from_timestamp
.. automethod:: krajjat.classes.sequence.Sequence.get_pose_from_timestamp
.. automethod:: krajjat.classes.sequence.Sequence.get_number_of_poses

Time
""""
.. automethod:: krajjat.classes.sequence.Sequence.get_timestamps
.. automethod:: krajjat.classes.sequence.Sequence.get_time_between_poses
.. automethod:: krajjat.classes.sequence.Sequence.get_duration

Sampling rate
"""""""""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_sampling_rate
.. automethod:: krajjat.classes.sequence.Sequence.get_sampling_rates
.. automethod:: krajjat.classes.sequence.Sequence.has_stable_sampling_rate

Metrics
"""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_measure
.. automethod:: krajjat.classes.sequence.Sequence.get_extremum_measure
.. automethod:: krajjat.classes.sequence.Sequence.get_sum_measure

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. _correct_jitter:
.. automethod:: krajjat.classes.sequence.Sequence.correct_jitter
.. _re_reference:
.. automethod:: krajjat.classes.sequence.Sequence.re_reference
.. _trim:
.. automethod:: krajjat.classes.sequence.Sequence.trim
.. automethod:: krajjat.classes.sequence.Sequence.trim_to_audio
.. _filter_frequencies:
.. automethod:: krajjat.classes.sequence.Sequence.filter_frequencies
.. _resample:
.. automethod:: krajjat.classes.sequence.Sequence.resample
.. _interpolate_missing_data:
.. automethod:: krajjat.classes.sequence.Sequence.interpolate_missing_data
.. automethod:: krajjat.classes.sequence.Sequence.randomize

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.to_table
.. automethod:: krajjat.classes.sequence.Sequence.to_json
.. automethod:: krajjat.classes.sequence.Sequence.to_dict
.. automethod:: krajjat.classes.sequence.Sequence.to_dataframe

Saving functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.save
.. automethod:: krajjat.classes.sequence.Sequence.save_info
.. automethod:: krajjat.classes.sequence.Sequence.save_json
.. automethod:: krajjat.classes.sequence.Sequence.save_mat
.. automethod:: krajjat.classes.sequence.Sequence.save_excel
.. automethod:: krajjat.classes.sequence.Sequence.save_pickle
.. automethod:: krajjat.classes.sequence.Sequence.save_txt

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.average_qualisys_to_kinect
.. automethod:: krajjat.classes.sequence.Sequence.average_joints
.. automethod:: krajjat.classes.sequence.Sequence.concatenate
.. automethod:: krajjat.classes.sequence.Sequence.copy
.. automethod:: krajjat.classes.sequence.Sequence.print_all

Private methods
---------------
Initialisation functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence._define_name_init
.. automethod:: krajjat.classes.sequence.Sequence._set_time_unit
.. automethod:: krajjat.classes.sequence.Sequence._load_from_path
.. automethod:: krajjat.classes.sequence.Sequence._load_poses
.. automethod:: krajjat.classes.sequence.Sequence._load_single_pose_file
.. automethod:: krajjat.classes.sequence.Sequence._load_sequence_file
.. automethod:: krajjat.classes.sequence.Sequence._create_pose_from_table_row
.. automethod:: krajjat.classes.sequence.Sequence._create_pose_from_json
.. automethod:: krajjat.classes.sequence.Sequence._set_timestamps_time_unit
.. automethod:: krajjat.classes.sequence.Sequence._load_json_metadata
.. automethod:: krajjat.classes.sequence.Sequence._load_date_recording
.. automethod:: krajjat.classes.sequence.Sequence._set_joint_labels
.. automethod:: krajjat.classes.sequence.Sequence._apply_joint_labels
.. automethod:: krajjat.classes.sequence.Sequence._set_system
.. automethod:: krajjat.classes.sequence.Sequence._calculate_relative_timestamps

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence._correct_jitter_window
.. automethod:: krajjat.classes.sequence.Sequence._correct_jitter_single_joint

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence._create_new_sequence_with_timestamps
.. automethod:: krajjat.classes.sequence.Sequence._set_attributes_from_other_sequence