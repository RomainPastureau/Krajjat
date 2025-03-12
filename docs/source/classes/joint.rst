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
.. automethod:: krajjat.classes.joint.Joint.__getitem__
.. automethod:: krajjat.classes.joint.Joint.__setitem__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.joint.Joint.set_joint_label
.. automethod:: krajjat.classes.joint.Joint.set_x
.. automethod:: krajjat.classes.joint.Joint.set_y
.. automethod:: krajjat.classes.joint.Joint.set_z
.. automethod:: krajjat.classes.joint.Joint.set_coordinate
.. automethod:: krajjat.classes.joint.Joint.set_position
.. automethod:: krajjat.classes.joint.Joint.set_to_zero
.. automethod:: krajjat.classes.joint.Joint.set_to_none


Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.joint.Joint.get_joint_label
.. automethod:: krajjat.classes.joint.Joint.get_x
.. automethod:: krajjat.classes.joint.Joint.get_y
.. automethod:: krajjat.classes.joint.Joint.get_z
.. automethod:: krajjat.classes.joint.Joint.get_coordinate
.. automethod:: krajjat.classes.joint.Joint.get_position

Predicates
^^^^^^^^^^
.. automethod:: krajjat.classes.joint.Joint.has_velocity_over_threshold
.. automethod:: krajjat.classes.joint.Joint.is_corrected
.. automethod:: krajjat.classes.joint.Joint.is_randomized
.. automethod:: krajjat.classes.joint.Joint.is_zero
.. automethod:: krajjat.classes.joint.Joint.is_none

Other methods
^^^^^^^^^^^^^
.. automethod:: krajjat.classes.joint.Joint.get_copy
.. automethod:: krajjat.classes.joint.Joint.convert_rotation

Private method
--------------
.. automethod:: krajjat.classes.joint.Joint._randomize_coordinates_keep_movement