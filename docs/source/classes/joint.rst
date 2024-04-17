Joint
=====

Description
-----------
Default class for joints, i.e. points in space at a specific timestamp. The methods in this class are mainly
handled by the methods in the class Pose, but some of them can be directly accessed.

Initialisation
--------------
.. autoclass:: krajjat.classes.joint.Joint

Magic methods
-------------
.. automethod:: krajjat.classes.joint.Joint.__repr__
.. automethod:: krajjat.classes.joint.Joint.__eq__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.joint.Joint.set_joint_label
.. automethod:: krajjat.classes.joint.Joint.set_x
.. automethod:: krajjat.classes.joint.Joint.set_y
.. automethod:: krajjat.classes.joint.Joint.set_z
.. automethod:: krajjat.classes.joint.Joint.set_position
.. automethod:: krajjat.classes.joint.Joint.set_to_zero

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.joint.Joint.get_joint_label
.. automethod:: krajjat.classes.joint.Joint.get_x
.. automethod:: krajjat.classes.joint.Joint.get_y
.. automethod:: krajjat.classes.joint.Joint.get_z
.. automethod:: krajjat.classes.joint.Joint.get_position
.. automethod:: krajjat.classes.joint.Joint.get_has_velocity_over_threshold
.. automethod:: krajjat.classes.joint.Joint.get_is_corrected
.. automethod:: krajjat.classes.joint.Joint.get_is_randomized
.. automethod:: krajjat.classes.joint.Joint.get_is_zero
.. automethod:: krajjat.classes.joint.Joint.get_is_none
.. automethod:: krajjat.classes.joint.Joint.get_copy

Rotation function
^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.joint.Joint.convert_rotation

Private methods
---------------
.. automethod:: krajjat.classes.joint.Joint._correct_joint
.. automethod:: krajjat.classes.joint.Joint._randomize_coordinates_keep_movement
.. automethod:: krajjat.classes.joint.Joint._set_has_velocity_over_threshold
.. automethod:: krajjat.classes.joint.Joint._set_is_corrected
