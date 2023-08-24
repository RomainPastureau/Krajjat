Graphic Classes
===============

Description
-----------
These classes allow to convert the data from :class:`Sequence`, :class:`Pose` and :class:`Joint` to display them
in the :doc:`display_functions`.

WindowArea
-------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.WindowArea

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.WindowArea.set_resolution
.. automethod:: classes.graphic_classes.WindowArea.set_blit_coordinates
.. automethod:: classes.graphic_classes.WindowArea.set_elements
.. automethod:: classes.graphic_classes.WindowArea.add_element
.. automethod:: classes.graphic_classes.WindowArea.remove_element
.. automethod:: classes.graphic_classes.WindowArea.set_height_window_in_meters
.. automethod:: classes.graphic_classes.WindowArea.contains
.. automethod:: classes.graphic_classes.WindowArea.convert_x
.. automethod:: classes.graphic_classes.WindowArea.convert_y
.. automethod:: classes.graphic_classes.WindowArea.get_resolution
.. automethod:: classes.graphic_classes.WindowArea.fill
.. automethod:: classes.graphic_classes.WindowArea.blit_background_surface
.. automethod:: classes.graphic_classes.WindowArea.blit
.. automethod:: classes.graphic_classes.WindowArea.show

Timer
-----

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.Timer

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.Timer.set_timer
.. automethod:: classes.graphic_classes.Timer.set_speed
.. automethod:: classes.graphic_classes.Timer.get_timer
.. automethod:: classes.graphic_classes.Timer.get_last_tick
.. automethod:: classes.graphic_classes.Timer.get_last_full_second
.. automethod:: classes.graphic_classes.Timer.reset
.. automethod:: classes.graphic_classes.Timer.pause
.. automethod:: classes.graphic_classes.Timer.unpause
.. automethod:: classes.graphic_classes.Timer.update
.. automethod:: classes.graphic_classes.Timer.end_update

GraphicSequence
---------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.GraphicSequence

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.GraphicSequence._load_poses
.. automethod:: classes.graphic_classes.GraphicSequence._load_joint_labels
.. automethod:: classes.graphic_classes.GraphicSequence._load_connections
.. automethod:: classes.graphic_classes.GraphicSequence._add_entry_joint_surfaces
.. automethod:: classes.graphic_classes.GraphicSequence._generate_all_joint_surfaces
.. automethod:: classes.graphic_classes.GraphicSequence.get_timestamp
.. automethod:: classes.graphic_classes.GraphicSequence.get_duration
.. automethod:: classes.graphic_classes.GraphicSequence.get_number_of_poses
.. automethod:: classes.graphic_classes.GraphicSequence.get_current_pose_index
.. automethod:: classes.graphic_classes.GraphicSequence.set_color_background
.. automethod:: classes.graphic_classes.GraphicSequence.set_shape_joint
.. automethod:: classes.graphic_classes.GraphicSequence.set_color_joint_default
.. automethod:: classes.graphic_classes.GraphicSequence.set_color_joint_corrected
.. automethod:: classes.graphic_classes.GraphicSequence.set_color_line
.. automethod:: classes.graphic_classes.GraphicSequence.set_width_line
.. automethod:: classes.graphic_classes.GraphicSequence.set_size_joint_default
.. automethod:: classes.graphic_classes.GraphicSequence.set_size_joint_hand
.. automethod:: classes.graphic_classes.GraphicSequence.set_size_joint_head
.. automethod:: classes.graphic_classes.GraphicSequence.set_scale_joint
.. automethod:: classes.graphic_classes.GraphicSequence.set_ignore_bottom
.. automethod:: classes.graphic_classes.GraphicSequence.set_show_lines
.. automethod:: classes.graphic_classes.GraphicSequence.set_show_joints_corrected
.. automethod:: classes.graphic_classes.GraphicSequence.set_shift_x
.. automethod:: classes.graphic_classes.GraphicSequence.set_shift_y
.. automethod:: classes.graphic_classes.GraphicSequence.set_zoom_level
.. automethod:: classes.graphic_classes.GraphicSequence.toggle_ignore_bottom
.. automethod:: classes.graphic_classes.GraphicSequence.toggle_show_lines
.. automethod:: classes.graphic_classes.GraphicSequence.toggle_show_joints_corrected
.. automethod:: classes.graphic_classes.GraphicSequence.set_pose_from_timestamp
.. automethod:: classes.graphic_classes.GraphicSequence.set_pose_from_index
.. automethod:: classes.graphic_classes.GraphicSequence.next_pose
.. automethod:: classes.graphic_classes.GraphicSequence.previous_pose
.. automethod:: classes.graphic_classes.GraphicSequence.reset
.. automethod:: classes.graphic_classes.GraphicSequence.apply_events
.. automethod:: classes.graphic_classes.GraphicSequence.play
.. automethod:: classes.graphic_classes.GraphicSequence.show_pose

GraphicPose
-----------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.GraphicPose

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.GraphicPose._load_joints
.. automethod:: classes.graphic_classes.GraphicPose.show_line
.. automethod:: classes.graphic_classes.GraphicPose.show

GraphicJoint
------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.GraphicJoint

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.GraphicJoint.convert_coordinates
.. automethod:: classes.graphic_classes.GraphicJoint.rotate
.. automethod:: classes.graphic_classes.GraphicJoint.show

Video
-----

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.Video

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.Video._load_video
.. automethod:: classes.graphic_classes.Video._load_frame
.. automethod:: classes.graphic_classes.Video.get_timestamp
.. automethod:: classes.graphic_classes.Video.get_duration
.. automethod:: classes.graphic_classes.Video.get_number_of_frames
.. automethod:: classes.graphic_classes.Video.get_fps
.. automethod:: classes.graphic_classes.Video.get_current_frame_index
.. automethod:: classes.graphic_classes.Video.set_frame_from_index
.. automethod:: classes.graphic_classes.Video.set_frame_from_timestamp
.. automethod:: classes.graphic_classes.Video.reset
.. automethod:: classes.graphic_classes.Video.next_frame
.. automethod:: classes.graphic_classes.Video.show_frame
.. automethod:: classes.graphic_classes.Video.show

Keyword arguments
-----------------
For the accepted keyboard arguments, see :ref:`keyword_arguments_display_functions`.