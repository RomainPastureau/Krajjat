Pose
====

Description
-----------
Default class for poses, i.e. group of joints at a specific timestamp. A pose, in the motion sequence, is the equivalent
of a frame in a video. The methods in this class are mainly handled by the methods in the class Sequence, but some of
them can be directly accessed.

Initialisation
--------------
.. autoclass:: classes.pose.Pose

Magic methods
-------------
.. automethod:: classes.pose.Pose.__repr__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.pose.Pose.set_timestamp

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.pose.Pose.get_joint
.. automethod:: classes.pose.Pose.get_joint_labels
.. automethod:: classes.pose.Pose.get_timestamp
.. automethod:: classes.pose.Pose.get_relative_timestamp
.. automethod:: classes.pose.Pose.get_copy

Joints functions
^^^^^^^^^^^^^^^^
.. automethod:: classes.pose.Pose.add_joint
.. automethod:: classes.pose.Pose.generate_average_joint
.. automethod:: classes.pose.Pose.remove_joint
.. automethod:: classes.pose.Pose.remove_joints

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: classes.pose.Pose.convert_to_table
.. automethod:: classes.pose.Pose.convert_to_json

Private methods
---------------
.. automethod:: classes.pose.Pose._calculate_relative_timestamp
.. automethod:: classes.pose.Pose._get_copy_with_empty_joints