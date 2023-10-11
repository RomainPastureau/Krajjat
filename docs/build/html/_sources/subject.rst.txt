Subject
=======

Description
-----------
Default class defining a subject, that can contain multiple sequences. This class can be used in the stats
functions to calculate variances across participants.

Initialisation
--------------
.. autoclass:: classes.subject.Subject

Setter functions
----------------
.. automethod:: classes.subject.Subject.set_name
.. automethod:: classes.subject.Subject.set_group
.. automethod:: classes.subject.Subject.set_gender
.. automethod:: classes.subject.Subject.set_age
.. automethod:: classes.subject.Subject.set_age_from_dob

Sequences functions
-------------------
.. automethod:: classes.subject.Subject.add_sequence
.. automethod:: classes.subject.Subject.load_sequence
.. automethod:: classes.subject.Subject.get_sequences
.. automethod:: classes.subject.Subject.get_sequence_from_index
.. automethod:: classes.subject.Subject.get_sequence_from_name
.. automethod:: classes.subject.Subject.remove_sequence_from_index
.. automethod:: classes.subject.Subject.remove_sequence_from_name
.. automethod:: classes.subject.Subject.get_sequences_from_condition
.. automethod:: classes.subject.Subject.get_sequences_from_attribute
.. automethod:: classes.subject.Subject.get_number_of_sequences

Getter functions
----------------
.. automethod:: classes.subject.Subject.get_name
.. automethod:: classes.subject.Subject.get_group
.. automethod:: classes.subject.Subject.get_gender
.. automethod:: classes.subject.Subject.get_age
.. automethod:: classes.subject.Subject.get_subject_height
.. automethod:: classes.subject.Subject.get_subject_arm_length
.. automethod:: classes.subject.Subject.get_recording_session_duration
.. automethod:: classes.subject.Subject.get_average_velocity_single_joint
.. automethod:: classes.subject.Subject.get_average_velocities

Print functions
---------------
.. automethod:: classes.subject.Subject.print_sequences_details