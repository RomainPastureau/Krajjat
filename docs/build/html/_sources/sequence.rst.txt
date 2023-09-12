Sequence
========

Description
-----------
Default class for motion sequences in the toolbox. An instance of this class will be
one motion sequence. The class contains several methods to perform **pre-processing** or
**displaying summarized data** in text form (see public methods).

Initialisation
--------------
.. autoclass:: classes.sequence.Sequence

Magic methods
-------------
.. autoclass:: classes.sequence.Sequence.__len__
.. autoclass:: classes.sequence.Sequence.__getitem__
.. autoclass:: classes.sequence.Sequence.__repr__
.. autoclass:: classes.sequence.Sequence.__eq__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.set_name
.. automethod:: classes.sequence.Sequence.set_path_audio
.. automethod:: classes.sequence.Sequence.set_first_timestamp

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.get_path
.. automethod:: classes.sequence.Sequence.get_name
.. automethod:: classes.sequence.Sequence.get_poses
.. automethod:: classes.sequence.Sequence.get_pose
.. automethod:: classes.sequence.Sequence.get_number_of_poses
.. automethod:: classes.sequence.Sequence.get_joint_labels
.. automethod:: classes.sequence.Sequence.get_date_recording
.. automethod:: classes.sequence.Sequence.get_printable_date_recording
.. automethod:: classes.sequence.Sequence.get_timestamps
.. automethod:: classes.sequence.Sequence.get_time_between_two_poses
.. automethod:: classes.sequence.Sequence.get_duration
.. automethod:: classes.sequence.Sequence.get_framerates
.. automethod:: classes.sequence.Sequence.get_framerate
.. automethod:: classes.sequence.Sequence.get_average_framerate
.. automethod:: classes.sequence.Sequence.get_min_framerate
.. automethod:: classes.sequence.Sequence.get_max_framerate
.. automethod:: classes.sequence.Sequence.get_joint_coordinate_as_list
.. automethod:: classes.sequence.Sequence.get_joint_distance_as_list
.. automethod:: classes.sequence.Sequence.get_joint_velocity_as_list
.. automethod:: classes.sequence.Sequence.get_velocities
.. automethod:: classes.sequence.Sequence.get_max_velocity_whole_sequence
.. automethod:: classes.sequence.Sequence.get_max_velocity_single_joint
.. automethod:: classes.sequence.Sequence.get_max_velocity_per_joint
.. automethod:: classes.sequence.Sequence.get_total_velocity_whole_sequence
.. automethod:: classes.sequence.Sequence.get_total_velocity_single_joint
.. automethod:: classes.sequence.Sequence.get_total_velocity_per_joint
.. automethod:: classes.sequence.Sequence.get_subject_height
.. automethod:: classes.sequence.Sequence.get_subject_arm_length
.. automethod:: classes.sequence.Sequence.get_stats

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.correct_jitter
.. automethod:: classes.sequence.Sequence.re_reference
.. automethod:: classes.sequence.Sequence.trim
.. automethod:: classes.sequence.Sequence.trim_to_audio
.. automethod:: classes.sequence.Sequence.resample
.. automethod:: classes.sequence.Sequence.correct_zeros
.. automethod:: classes.sequence.Sequence.randomize

Copy functions
^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.copy_pose
.. automethod:: classes.sequence.Sequence.copy_joint

Print functions
^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.print_pose
.. automethod:: classes.sequence.Sequence.print_stats

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.convert_to_table
.. automethod:: classes.sequence.Sequence.convert_to_json

Saving functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.save
.. automethod:: classes.sequence.Sequence.save_stats

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence.average_qualisys_to_kinect
.. automethod:: classes.sequence.Sequence.average_joints
.. automethod:: classes.sequence.Sequence.concatenate

Private methods
---------------
Initialisation functions
^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence._define_name_init
.. automethod:: classes.sequence.Sequence._load_from_path
.. automethod:: classes.sequence.Sequence._fetch_files_from_folder
.. automethod:: classes.sequence.Sequence._load_poses
.. automethod:: classes.sequence.Sequence._load_single_pose_file
.. automethod:: classes.sequence.Sequence._load_sequence_file
.. automethod:: classes.sequence.Sequence._create_pose_from_table_row
.. automethod:: classes.sequence.Sequence._create_pose_from_json
.. automethod:: classes.sequence.Sequence._load_date_recording
.. automethod:: classes.sequence.Sequence._calculate_relative_timestamps

Correction functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence._correct_jitter_window
.. automethod:: classes.sequence.Sequence._correct_jitter_single_joint

Saving functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence._save_json
.. automethod:: classes.sequence.Sequence._save_mat
.. automethod:: classes.sequence.Sequence._save_xlsx
.. automethod:: classes.sequence.Sequence._save_txt

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.sequence.Sequence._create_new_sequence_with_timestamps