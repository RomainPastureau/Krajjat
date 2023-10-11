Experiment
==========

Description
-----------
Default class defining an experiment. An experiment object can contain multiple subjects, which themselves can
contain multiple sequences.

Initialisation
--------------
.. autoclass:: classes.experiment.Experiment

Setter functions
----------------
.. automethod:: classes.experiment.Experiment.set_name

Subject functions
-----------------
.. automethod:: classes.experiment.Experiment.add_subject
.. automethod:: classes.experiment.Experiment.get_subjects
.. automethod:: classes.experiment.Experiment.get_subjects_names
.. automethod:: classes.experiment.Experiment.get_subject_from_index
.. automethod:: classes.experiment.Experiment.get_subject_from_name
.. automethod:: classes.experiment.Experiment.remove_subject_from_index
.. automethod:: classes.experiment.Experiment.remove_subject_from_name
.. automethod:: classes.experiment.Experiment.get_subjects_from_group
.. automethod:: classes.experiment.Experiment.get_subjects_from_attribute
.. automethod:: classes.experiment.Experiment.get_number_of_subjects

Getter functions
----------------
.. automethod:: classes.experiment.Experiment.get_name
