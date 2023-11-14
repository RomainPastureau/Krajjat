Subject
=======

Description
-----------
Default class defining a subject, that can contain multiple sequences. This class can be used in the stats
functions to calculate variances across participants.

Initialisation
--------------
.. autoclass:: krajjat.classes.subject.Subject

Setter functions
----------------
.. automethod:: krajjat.classes.subject.Subject.set_name
.. automethod:: krajjat.classes.subject.Subject.set_group
.. automethod:: krajjat.classes.subject.Subject.set_gender
.. automethod:: krajjat.classes.subject.Subject.set_age
.. automethod:: krajjat.classes.subject.Subject.set_age_from_dob

Sequences functions
-------------------
.. automethod:: krajjat.classes.subject.Subject.add_sequence
.. automethod:: krajjat.classes.subject.Subject.load_sequence
.. automethod:: krajjat.classes.subject.Subject.get_sequences
.. automethod:: krajjat.classes.subject.Subject.get_sequence_from_index
.. automethod:: krajjat.classes.subject.Subject.get_sequence_from_name
.. automethod:: krajjat.classes.subject.Subject.remove_sequence_from_index
.. automethod:: krajjat.classes.subject.Subject.remove_sequence_from_name
.. automethod:: krajjat.classes.subject.Subject.get_sequences_from_condition
.. automethod:: krajjat.classes.subject.Subject.get_sequences_from_attribute
.. automethod:: krajjat.classes.subject.Subject.get_number_of_sequences

Getter functions
----------------
.. automethod:: krajjat.classes.subject.Subject.get_name
.. automethod:: krajjat.classes.subject.Subject.get_group
.. automethod:: krajjat.classes.subject.Subject.get_gender
.. automethod:: krajjat.classes.subject.Subject.get_age
.. automethod:: krajjat.classes.subject.Subject.get_subject_height
.. automethod:: krajjat.classes.subject.Subject.get_subject_arm_length
.. automethod:: krajjat.classes.subject.Subject.get_recording_session_duration
.. automethod:: krajjat.classes.subject.Subject.get_average_velocity_single_joint
.. automethod:: krajjat.classes.subject.Subject.get_average_velocities

Print functions
---------------
.. automethod:: krajjat.classes.subject.Subject.print_sequences_details
