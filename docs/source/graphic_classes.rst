Graphic Classes
===============

Description
-----------
These classes allow to convert the data from :class:`Sequence`, :class:`Pose` and :class:`Joint` to display them
in the :doc:`graphic_functions`. All these classes and their methods should be considered private.

GraphicWindow
-------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.GraphicWindow

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.GraphicWindow._convert_x
.. automethod:: classes.graphic_classes.GraphicWindow._convert_y

Timer
-----

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.Timer

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.Timer._get_timer
.. automethod:: classes.graphic_classes.Timer._set_timer
.. automethod:: classes.graphic_classes.Timer._reset
.. automethod:: classes.graphic_classes.Timer._update

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
.. automethod:: classes.graphic_classes.GraphicSequence._set_shape_joint
.. automethod:: classes.graphic_classes.GraphicSequence._set_color_joint_default
.. automethod:: classes.graphic_classes.GraphicSequence._set_color_joint_corrected
.. automethod:: classes.graphic_classes.GraphicSequence._set_color_line
.. automethod:: classes.graphic_classes.GraphicSequence._set_width_line
.. automethod:: classes.graphic_classes.GraphicSequence._set_size_joint_default
.. automethod:: classes.graphic_classes.GraphicSequence._set_size_joint_hand
.. automethod:: classes.graphic_classes.GraphicSequence._set_size_joint_head
.. automethod:: classes.graphic_classes.GraphicSequence._set_scale_joint
.. automethod:: classes.graphic_classes.GraphicSequence._set_ignore_bottom
.. automethod:: classes.graphic_classes.GraphicSequence._set_show_lines
.. automethod:: classes.graphic_classes.GraphicSequence._set_show_joints_corrected
.. automethod:: classes.graphic_classes.GraphicSequence._toggle_ignore_bottom
.. automethod:: classes.graphic_classes.GraphicSequence._toggle_show_lines
.. automethod:: classes.graphic_classes.GraphicSequence._toggle_show_joints_corrected
.. automethod:: classes.graphic_classes.GraphicSequence._next_pose
.. automethod:: classes.graphic_classes.GraphicSequence._previous_pose
.. automethod:: classes.graphic_classes.GraphicSequence._reset
.. automethod:: classes.graphic_classes.GraphicSequence._apply_events
.. automethod:: classes.graphic_classes.GraphicSequence._play
.. automethod:: classes.graphic_classes.GraphicSequence._show_pose

GraphicPose
-----------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.GraphicPose

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.GraphicPose._load_joints
.. automethod:: classes.graphic_classes.GraphicPose._show_line
.. automethod:: classes.graphic_classes.GraphicPose._show

GraphicJoint
------------

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: classes.graphic_classes.GraphicJoint

Methods
^^^^^^^
.. automethod:: classes.graphic_classes.GraphicJoint._convert_coordinates
.. automethod:: classes.graphic_classes.GraphicJoint._rotate
.. automethod:: classes.graphic_classes.GraphicJoint._show