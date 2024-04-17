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

Getter functions
^^^^^^^^^^^^^^^^

General
"""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_path
.. automethod:: krajjat.classes.sequence.Sequence.get_name
.. automethod:: krajjat.classes.sequence.Sequence.get_condition
.. automethod:: krajjat.classes.sequence.Sequence.get_joint_labels
.. automethod:: krajjat.classes.sequence.Sequence.get_date_recording
.. automethod:: krajjat.classes.sequence.Sequence.get_printable_date_recording
.. automethod:: krajjat.classes.sequence.Sequence.get_subject_height
.. automethod:: krajjat.classes.sequence.Sequence.get_subject_arm_length
.. automethod:: krajjat.classes.sequence.Sequence.get_stats

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
.. automethod:: krajjat.classes.sequence.Sequence.get_timestamps_for_metric
.. automethod:: krajjat.classes.sequence.Sequence.get_time_between_two_poses
.. automethod:: krajjat.classes.sequence.Sequence.get_duration

Framerate
"""""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_framerates
.. automethod:: krajjat.classes.sequence.Sequence.get_framerate
.. automethod:: krajjat.classes.sequence.Sequence.get_average_framerate
.. automethod:: krajjat.classes.sequence.Sequence.get_min_framerate
.. automethod:: krajjat.classes.sequence.Sequence.get_max_framerate

Metrics: single joint
"""""""""""""""""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_joint_coordinate_as_list
.. automethod:: krajjat.classes.sequence.Sequence.get_joint_distance_as_list
.. automethod:: krajjat.classes.sequence.Sequence.get_joint_velocity_as_list
.. automethod:: krajjat.classes.sequence.Sequence.get_joint_acceleration_as_list
.. automethod:: krajjat.classes.sequence.Sequence.get_joint_metric_as_list

Metrics: all joints
"""""""""""""""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_single_coordinates
.. automethod:: krajjat.classes.sequence.Sequence.get_distances
.. automethod:: krajjat.classes.sequence.Sequence.get_distance_between_hands
.. automethod:: krajjat.classes.sequence.Sequence.get_distance_between_joints
.. automethod:: krajjat.classes.sequence.Sequence.get_velocities
.. automethod:: krajjat.classes.sequence.Sequence.get_accelerations
.. automethod:: krajjat.classes.sequence.Sequence.get_time_series_as_list

Metrics: max values
"""""""""""""""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_max_distance_whole_sequence
.. automethod:: krajjat.classes.sequence.Sequence.get_max_velocity_whole_sequence
.. automethod:: krajjat.classes.sequence.Sequence.get_max_acceleration_whole_sequence
.. automethod:: krajjat.classes.sequence.Sequence.get_max_distance_single_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_max_velocity_single_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_max_acceleration_single_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_max_distance_per_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_max_velocity_per_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_max_acceleration_per_joint

Metrics: total values
"""""""""""""""""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_total_distance_whole_sequence
.. automethod:: krajjat.classes.sequence.Sequence.get_total_velocity_whole_sequence
.. automethod:: krajjat.classes.sequence.Sequence.get_total_acceleration_whole_sequence
.. automethod:: krajjat.classes.sequence.Sequence.get_total_distance_single_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_total_velocity_single_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_total_acceleration_single_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_total_distance_per_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_total_velocity_per_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_total_acceleration_per_joint

Fill level
""""""""""
.. automethod:: krajjat.classes.sequence.Sequence.get_fill_level_single_joint
.. automethod:: krajjat.classes.sequence.Sequence.get_fill_level_per_joint

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. _correct_jitter:
.. automethod:: krajjat.classes.sequence.Sequence.correct_jitter
.. _re_reference:
.. automethod:: krajjat.classes.sequence.Sequence.re_reference
.. _trim:
.. automethod:: krajjat.classes.sequence.Sequence.trim
.. automethod:: krajjat.classes.sequence.Sequence.trim_to_audio
.. _resample:
.. automethod:: krajjat.classes.sequence.Sequence.resample
.. _correct_zeros:
.. automethod:: krajjat.classes.sequence.Sequence.correct_zeros
.. automethod:: krajjat.classes.sequence.Sequence.randomize

Copy functions
^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.copy_pose
.. automethod:: krajjat.classes.sequence.Sequence.copy_joint

Print functions
^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.print_pose
.. automethod:: krajjat.classes.sequence.Sequence.print_stats
.. automethod:: krajjat.classes.sequence.Sequence.print_details

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.convert_to_table
.. automethod:: krajjat.classes.sequence.Sequence.convert_to_json

Saving functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.save
.. automethod:: krajjat.classes.sequence.Sequence.save_stats

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence.average_qualisys_to_kinect
.. automethod:: krajjat.classes.sequence.Sequence.average_joints
.. automethod:: krajjat.classes.sequence.Sequence.concatenate

Private methods
---------------
Initialisation functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence._define_name_init
.. automethod:: krajjat.classes.sequence.Sequence._load_from_path
.. automethod:: krajjat.classes.sequence.Sequence._fetch_files_from_folder
.. automethod:: krajjat.classes.sequence.Sequence._load_poses
.. automethod:: krajjat.classes.sequence.Sequence._load_single_pose_file
.. automethod:: krajjat.classes.sequence.Sequence._load_sequence_file
.. automethod:: krajjat.classes.sequence.Sequence._create_pose_from_table_row
.. automethod:: krajjat.classes.sequence.Sequence._create_pose_from_json
.. automethod:: krajjat.classes.sequence.Sequence._load_date_recording
.. automethod:: krajjat.classes.sequence.Sequence._calculate_relative_timestamps

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence._correct_jitter_window
.. automethod:: krajjat.classes.sequence.Sequence._correct_jitter_single_joint

Saving functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence._save_json
.. automethod:: krajjat.classes.sequence.Sequence._save_mat
.. automethod:: krajjat.classes.sequence.Sequence._save_xlsx
.. automethod:: krajjat.classes.sequence.Sequence._save_txt

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.sequence.Sequence._create_new_sequence_with_timestamps