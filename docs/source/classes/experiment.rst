Experiment
==========

Description
-----------
Default class defining an experiment. An experiment object can contain multiple subjects, which themselves can
contain multiple sequences.

Initialisation
--------------
.. autoclass:: krajjat.classes.experiment.Experiment

Setter functions
----------------
.. automethod:: krajjat.classes.experiment.Experiment.set_name

Subject functions
-----------------
.. automethod:: krajjat.classes.experiment.Experiment.add_subject
.. automethod:: krajjat.classes.experiment.Experiment.get_subjects
.. automethod:: krajjat.classes.experiment.Experiment.get_subjects_names
.. automethod:: krajjat.classes.experiment.Experiment.get_subject_from_index
.. automethod:: krajjat.classes.experiment.Experiment.get_subject_from_name
.. automethod:: krajjat.classes.experiment.Experiment.remove_subject_from_index
.. automethod:: krajjat.classes.experiment.Experiment.remove_subject_from_name
.. automethod:: krajjat.classes.experiment.Experiment.get_subjects_from_group
.. automethod:: krajjat.classes.experiment.Experiment.get_subjects_from_attribute
.. automethod:: krajjat.classes.experiment.Experiment.get_number_of_subjects

Getter functions
----------------
.. automethod:: krajjat.classes.experiment.Experiment.get_name
