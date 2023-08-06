Joint
=====

Description
-----------
Default class for joints, i.e. points in space at a specific timestamp. The methods in this class are mainly
handled by the methods in the class Pose, but some of them can be directly accessed.

Initialisation
--------------
.. autoclass:: classes.joint.Joint

Magic methods
-------------
.. automethod:: classes.joint.Joint.__repr__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.joint.Joint.set_joint_label
.. automethod:: classes.joint.Joint.set_x
.. automethod:: classes.joint.Joint.set_y
.. automethod:: classes.joint.Joint.set_z
.. automethod:: classes.joint.Joint.set_position
.. automethod:: classes.joint.Joint.set_to_zero

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.joint.Joint.get_joint_label
.. automethod:: classes.joint.Joint.get_x
.. automethod:: classes.joint.Joint.get_y
.. automethod:: classes.joint.Joint.get_z
.. automethod:: classes.joint.Joint.get_position
.. automethod:: classes.joint.Joint.get_has_velocity_over_threshold
.. automethod:: classes.joint.Joint.get_is_corrected
.. automethod:: classes.joint.Joint.get_is_randomized
.. automethod:: classes.joint.Joint.get_copy

Private methods
---------------
.. automethod:: classes.joint.Joint._correct_joint
.. automethod:: classes.joint.Joint._randomize_coordinates_keep_movement
.. automethod:: classes.joint.Joint._set_has_velocity_over_threshold
.. automethod:: classes.joint.Joint._set_is_corrected
