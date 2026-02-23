Tool functions
==============

Description
-----------
Functions to perform simple tasks that can be used throughout the toolbox and beyond.

Functions
---------

Path functions
^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.compute_subpath
.. autofunction:: krajjat.tool_functions.get_difference_paths
.. autofunction:: krajjat.tool_functions.get_objects_paths
.. autofunction:: krajjat.tool_functions.sort_files_trailing_index

Name functions
^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.get_objects_names

Sequence comparison functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.compute_different_joints
.. autofunction:: krajjat.tool_functions.align_two_sequences
.. autofunction:: krajjat.tool_functions.align_multiple_sequences
.. autofunction:: krajjat.tool_functions.sort_sequences_by_date

File reading functions
^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.get_system_csv_separator
.. autofunction:: krajjat.tool_functions.get_filetype_separator
.. autofunction:: krajjat.tool_functions.read_json
.. autofunction:: krajjat.tool_functions.read_text_table
.. autofunction:: krajjat.tool_functions.read_xlsx
.. autofunction:: krajjat.tool_functions.read_pandas_dataframe
.. autofunction:: krajjat.tool_functions.convert_data_from_qtm

File writing functions
^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.write_text_table
.. autofunction:: krajjat.tool_functions.write_xlsx

Calculation functions
^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.find_closest_value_index
.. autofunction:: krajjat.tool_functions.resample_data
.. autofunction:: krajjat.tool_functions.resample_window
.. autofunction:: krajjat.tool_functions.interpolate_data
.. autofunction:: krajjat.tool_functions.pad
.. autofunction:: krajjat.tool_functions.add_delay
.. autofunction:: krajjat.tool_functions.calculate_distance
.. autofunction:: krajjat.tool_functions.calculate_consecutive_distances
.. autofunction:: krajjat.tool_functions.calculate_euclidian_distances
.. autofunction:: krajjat.tool_functions.calculate_derivative
.. autofunction:: krajjat.tool_functions.calculate_delay
.. autofunction:: krajjat.tool_functions.generate_random_joints
.. autofunction:: krajjat.tool_functions.get_number_of_windows
.. autofunction:: krajjat.tool_functions.get_window_length
.. autofunction:: krajjat.tool_functions.divide_in_windows

Color functions
^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.load_color_names
.. autofunction:: krajjat.tool_functions.load_color_schemes
.. autofunction:: krajjat.tool_functions.hex_color_to_rgb
.. autofunction:: krajjat.tool_functions.rgb_color_to_hex
.. autofunction:: krajjat.tool_functions.convert_color
.. autofunction:: krajjat.tool_functions.convert_colors
.. autofunction:: krajjat.tool_functions.calculate_color_points_on_gradient
.. autofunction:: krajjat.tool_functions.calculate_color_ratio
.. autofunction:: krajjat.tool_functions.calculate_colors_by_values
.. autofunction:: krajjat.tool_functions.generate_random_color

Audio functions
^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.scale_audio
.. autofunction:: krajjat.tool_functions.stereo_to_mono
.. autofunction:: krajjat.tool_functions.remove_average

Internal loading functions
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.load_joint_labels
.. autofunction:: krajjat.tool_functions.load_qualisys_joint_label_conversion
.. autofunction:: krajjat.tool_functions.load_joint_connections
.. autofunction:: krajjat.tool_functions.load_qualisys_to_kinect
.. autofunction:: krajjat.tool_functions.load_joints_subplot_layout
.. autofunction:: krajjat.tool_functions.load_joints_silhouette_layout
.. autofunction:: krajjat.tool_functions.load_default_steps_gui

Time functions
^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.convert_timestamp_to_seconds
.. autofunction:: krajjat.tool_functions.format_time
.. autofunction:: krajjat.tool_functions.time_unit_to_datetime
.. autofunction:: krajjat.tool_functions.time_unit_to_timedelta

Miscellaneous functions
^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: krajjat.tool_functions.show_progression
.. autofunction:: krajjat.tool_functions.get_min_max_values_from_plot_dictionary
.. autofunction:: krajjat.tool_functions.kwargs_parser
.. autofunction:: krajjat.tool_functions.set_nested_dict
.. autofunction:: krajjat.tool_functions.has_nested_key