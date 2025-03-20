Graphic Classes
===============

Description
-----------
These classes allow to convert the data from :class:`Sequence`, :class:`Pose` and :class:`Joint` to display them
in the :doc:`../functions/display_functions`.

WindowArea
-------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.graphic_classes.WindowArea

Methods
^^^^^^^
.. automethod:: krajjat.classes.graphic_classes.WindowArea.set_resolution
.. automethod:: krajjat.classes.graphic_classes.WindowArea.set_blit_coordinates
.. automethod:: krajjat.classes.graphic_classes.WindowArea.set_elements
.. automethod:: krajjat.classes.graphic_classes.WindowArea.add_element
.. automethod:: krajjat.classes.graphic_classes.WindowArea.remove_element
.. automethod:: krajjat.classes.graphic_classes.WindowArea.set_height_window_in_meters
.. automethod:: krajjat.classes.graphic_classes.WindowArea.contains
.. automethod:: krajjat.classes.graphic_classes.WindowArea.convert_x
.. automethod:: krajjat.classes.graphic_classes.WindowArea.convert_y
.. automethod:: krajjat.classes.graphic_classes.WindowArea.get_resolution
.. automethod:: krajjat.classes.graphic_classes.WindowArea.fill
.. automethod:: krajjat.classes.graphic_classes.WindowArea.blit_background_surface
.. automethod:: krajjat.classes.graphic_classes.WindowArea.blit
.. automethod:: krajjat.classes.graphic_classes.WindowArea.show

Timer
-----

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.graphic_classes.Timer

Methods
^^^^^^^
.. automethod:: krajjat.classes.graphic_classes.Timer.set_timer
.. automethod:: krajjat.classes.graphic_classes.Timer.set_speed
.. automethod:: krajjat.classes.graphic_classes.Timer.get_timer
.. automethod:: krajjat.classes.graphic_classes.Timer.get_last_tick
.. automethod:: krajjat.classes.graphic_classes.Timer.get_last_full_second
.. automethod:: krajjat.classes.graphic_classes.Timer.reset
.. automethod:: krajjat.classes.graphic_classes.Timer.pause
.. automethod:: krajjat.classes.graphic_classes.Timer.unpause
.. automethod:: krajjat.classes.graphic_classes.Timer.update
.. automethod:: krajjat.classes.graphic_classes.Timer.end_update

GraphicSequence
---------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.graphic_classes.GraphicSequence

Methods
^^^^^^^
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence._load_poses
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence._load_joint_labels
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence._load_connections
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence._remove_ignored_joints
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence._add_entry_joint_surfaces
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence._generate_all_joint_surfaces
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.get_timestamp
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.get_duration
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.get_number_of_poses
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.get_current_pose_index
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_color_background
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_shape_joint
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_color_joint_default
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_color_joint_corrected
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_color_line
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_width_line
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_size_joint_default
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_size_joint_hand
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_size_joint_head
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_scale_joint
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_ignore_bottom
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_show_lines
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_show_joints_corrected
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_shift_x
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_shift_y
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_zoom_level
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.toggle_ignore_bottom
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.toggle_show_lines
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.toggle_show_joints_corrected
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_pose_from_timestamp
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.set_pose_from_index
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.next_pose
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.previous_pose
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.reset
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.apply_events
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.play
.. automethod:: krajjat.classes.graphic_classes.GraphicSequence.show_pose

GraphicPose
-----------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.graphic_classes.GraphicPose

Methods
^^^^^^^
.. automethod:: krajjat.classes.graphic_classes.GraphicPose._load_joints
.. automethod:: krajjat.classes.graphic_classes.GraphicPose.show_line
.. automethod:: krajjat.classes.graphic_classes.GraphicPose.show

GraphicJoint
------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.graphic_classes.GraphicJoint

Methods
^^^^^^^
.. automethod:: krajjat.classes.graphic_classes.GraphicJoint.convert_coordinates
.. automethod:: krajjat.classes.graphic_classes.GraphicJoint.rotate
.. automethod:: krajjat.classes.graphic_classes.GraphicJoint.show

Video
-----

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.graphic_classes.Video

Methods
^^^^^^^
.. automethod:: krajjat.classes.graphic_classes.Video._load_video
.. automethod:: krajjat.classes.graphic_classes.Video._set_frame_start
.. automethod:: krajjat.classes.graphic_classes.Video._load_frame
.. automethod:: krajjat.classes.graphic_classes.Video.get_timestamp
.. automethod:: krajjat.classes.graphic_classes.Video.get_duration
.. automethod:: krajjat.classes.graphic_classes.Video.get_number_of_frames
.. automethod:: krajjat.classes.graphic_classes.Video.get_fps
.. automethod:: krajjat.classes.graphic_classes.Video.get_current_frame_index
.. automethod:: krajjat.classes.graphic_classes.Video.set_frame_from_index
.. automethod:: krajjat.classes.graphic_classes.Video.set_frame_from_timestamp
.. automethod:: krajjat.classes.graphic_classes.Video.reset
.. automethod:: krajjat.classes.graphic_classes.Video.next_frame
.. automethod:: krajjat.classes.graphic_classes.Video.show_frame
.. automethod:: krajjat.classes.graphic_classes.Video.show

Keyword arguments
-----------------
For the accepted keyboard arguments, see :ref:`keyword_arguments_display_functions`.