Pose
====

Description
-----------
Default class for poses, i.e. group of joints at a specific timestamp. A pose, in the motion sequence, is the equivalent
of a frame in a video. The methods in this class are mainly handled by the methods in the class Sequence, but some of
them can be directly accessed.

Initialisation
--------------
.. autoclass:: krajjat.classes.pose.Pose

Magic methods
-------------
.. automethod:: krajjat.classes.pose.Pose.__repr__
.. automethod:: krajjat.classes.pose.Pose.__eq__

Public methods
--------------
Setter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.pose.Pose.set_timestamp

Getter functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.pose.Pose.get_joint
.. automethod:: krajjat.classes.pose.Pose.get_joint_labels
.. automethod:: krajjat.classes.pose.Pose.get_timestamp
.. automethod:: krajjat.classes.pose.Pose.get_relative_timestamp
.. automethod:: krajjat.classes.pose.Pose.get_copy

Joints functions
^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.pose.Pose.add_joint
.. automethod:: krajjat.classes.pose.Pose.generate_average_joint
.. automethod:: krajjat.classes.pose.Pose.remove_joint
.. automethod:: krajjat.classes.pose.Pose.remove_joints

Conversion functions
^^^^^^^^^^^^^^^^^^^^
.. automethod:: krajjat.classes.pose.Pose.convert_to_table
.. automethod:: krajjat.classes.pose.Pose.convert_to_json

Private methods
---------------
.. automethod:: krajjat.classes.pose.Pose._calculate_relative_timestamp
.. automethod:: krajjat.classes.pose.Pose._get_copy_with_empty_joints