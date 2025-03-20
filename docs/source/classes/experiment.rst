Experiment
==========

Description
-----------
Default class defining an experiment. An experiment object can contain multiple subjects, which themselves can
contain multiple sequences.

Initialisation
--------------
.. autoclass:: krajjat.classes.experiment.Experiment

Magic methods
-------------
.. automethod:: krajjat.classes.experiment.Experiment.__len__
.. automethod:: krajjat.classes.experiment.Experiment.__getitem__

Name methods
------------
.. automethod:: krajjat.classes.experiment.Experiment.set_name
.. automethod:: krajjat.classes.experiment.Experiment.get_name

Subject methods
---------------
.. automethod:: krajjat.classes.experiment.Experiment.add_subject
.. automethod:: krajjat.classes.experiment.Experiment.add_subjects
.. automethod:: krajjat.classes.experiment.Experiment.get_subject
.. automethod:: krajjat.classes.experiment.Experiment.get_subjects
.. automethod:: krajjat.classes.experiment.Experiment.get_subjects_names
.. automethod:: krajjat.classes.experiment.Experiment.remove_subject
.. automethod:: krajjat.classes.experiment.Experiment.get_number_of_subjects

Other getter
------------
.. automethod:: krajjat.classes.experiment.Experiment.get_joint_labels

Dataframe methods
-----------------
.. automethod:: krajjat.classes.experiment.Experiment.get_dataframe
.. automethod:: krajjat.classes.experiment.Experiment.save_dataframe
