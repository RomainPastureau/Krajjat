Subject
=======

Description
-----------
Default class defining a subject, that can contain multiple sequences. This class can be used in the stats
functions to calculate variances across participants.

Initialisation
--------------
.. autoclass:: krajjat.classes.subject.Subject

Magic methods
-------------
.. automethod:: krajjat.classes.subject.Subject.__len__
.. automethod:: krajjat.classes.subject.Subject.__getitem__
.. automethod:: krajjat.classes.subject.Subject.__repr__
.. automethod:: krajjat.classes.subject.Subject.__eq__

Setter functions
----------------
.. automethod:: krajjat.classes.subject.Subject.set_name
.. automethod:: krajjat.classes.subject.Subject.set_group
.. automethod:: krajjat.classes.subject.Subject.set_gender
.. automethod:: krajjat.classes.subject.Subject.set_age
.. automethod:: krajjat.classes.subject.Subject.set_age_from_dob

Getter functions
----------------
.. automethod:: krajjat.classes.subject.Subject.get_name
.. automethod:: krajjat.classes.subject.Subject.get_group
.. automethod:: krajjat.classes.subject.Subject.get_gender
.. automethod:: krajjat.classes.subject.Subject.get_age
.. automethod:: krajjat.classes.subject.Subject.get_joint_labels
.. automethod:: krajjat.classes.subject.Subject.get_trial
.. automethod:: krajjat.classes.subject.Subject.get_trials
.. automethod:: krajjat.classes.subject.Subject.get_trials_id
.. automethod:: krajjat.classes.subject.Subject.get_number_of_trials
.. automethod:: krajjat.classes.subject.Subject.get_sequence
.. automethod:: krajjat.classes.subject.Subject.get_sequences
.. automethod:: krajjat.classes.subject.Subject.get_audio
.. automethod:: krajjat.classes.subject.Subject.get_audios
.. automethod:: krajjat.classes.subject.Subject.get_recording_session_duration
.. automethod:: krajjat.classes.subject.Subject.get_height
.. automethod:: krajjat.classes.subject.Subject.get_arm_length

Predicate functions
-------------------
.. automethod:: krajjat.classes.subject.Subject.has_sequence_in_each_trial
.. automethod:: krajjat.classes.subject.Subject.has_audio_in_each_trial
.. automethod:: krajjat.classes.subject.Subject.are_timestamps_equal_per_trial
.. automethod:: krajjat.classes.subject.Subject.are_frequencies_equal

Trial functions
---------------
.. automethod:: krajjat.classes.subject.Subject.add_trial
.. automethod:: krajjat.classes.subject.Subject.add_trials