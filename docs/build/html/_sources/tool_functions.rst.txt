Tool functions
==============

Description
-----------
Functions to perform simple tasks that can be used throughout the toolbox and beyond.

Functions
---------

Path functions
^^^^^^^^^^^^^^
.. autofunction:: tool_functions.find_common_parent_path
.. autofunction:: tool_functions.compute_subpath
.. autofunction:: tool_functions.get_difference_paths
.. autofunction:: tool_functions.create_subfolders
.. autofunction:: tool_functions.get_objects_paths

Name functions
^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.get_objects_names

Sequence comparison functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.compute_different_joints
.. autofunction:: tool_functions.align_two_sequences

File reading functions
^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.get_system_csv_separator
.. autofunction:: tool_functions.get_filetype_separator
.. autofunction:: tool_functions.read_json
.. autofunction:: tool_functions.read_text_table
.. autofunction:: tool_functions.read_xlsx
.. autofunction:: tool_functions.convert_data_from_qtm

File saving functions
^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.write_text_table
.. autofunction:: tool_functions.write_xlsx

Calculation functions
^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.resample_data
.. autofunction:: tool_functions.interpolate_data
.. autofunction:: tool_functions.calculate_distance
.. autofunction:: tool_functions.calculate_velocity
.. autofunction:: tool_functions.calculate_acceleration
.. autofunction:: tool_functions.calculate_delay
.. autofunction:: tool_functions.generate_random_joints
.. autofunction:: tool_functions.divide_in_windows

Color functions
^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.load_color_names
.. autofunction:: tool_functions.load_color_schemes
.. autofunction:: tool_functions.convert_colors_rgba
.. autofunction:: tool_functions.hex_color_to_rgb
.. autofunction:: tool_functions.rgb_color_to_hex
.. autofunction:: tool_functions.calculate_color_points_on_gradient
.. autofunction:: tool_functions.calculate_color_ratio
.. autofunction:: tool_functions.calculate_colors_by_values

Audio functions
^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.scale_audio
.. autofunction:: tool_functions.stereo_to_mono

Joint labels loading functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.load_kinect_joint_labels
.. autofunction:: tool_functions.load_qualisys_joint_labels
.. autofunction:: tool_functions.load_qualisys_joint_label_conversion
.. autofunction:: tool_functions.load_joints_connections
.. autofunction:: tool_functions.load_qualisys_to_kinect
.. autofunction:: tool_functions.load_joints_subplot_layout

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: tool_functions.show_progression
.. autofunction:: tool_functions.resample_images_to_frequency
.. autofunction:: tool_functions.get_min_max_values_from_plot_dictionary