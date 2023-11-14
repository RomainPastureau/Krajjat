.. Krajjat documentation master file, created by
   sphinx-quickstart on Mon Jun 12 12:18:32 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: /img/krajjat-logo-black-cropped.png

Welcome on the **Krajjat** documentation!
=========================================

What is Krajjat?
----------------
Krajjat is a Python package developed for **processing motion capture data**, and finding relationships between the
rhythmicity of the tracked movements and of the **acoustic components of the speech**.
The toolbox allows to:

   • **Pre-process** the motion capture sequences, via functions for
     :ref:`de-jittering <correct_jitter>`,
     :ref:`re-referencing <re_reference>`,
     :ref:`trimming <trim>`,
     :ref:`resampling <resample>`, and
     :ref:`interpolating missing data <correct_zeros>`. See more details
     :ref:`here<processing_functions>`.
   • Get **basic information** about the sequences, via e.g. :meth:`~classes.sequence.Sequence.print_stats`.
   • Get **acoustic components** of the speech, such as the :ref:`envelope <get_envelope>`, the
     :ref:`intensity <get_intensity>`, the :ref:`pitch <get_pitch>`, or one
     of the :ref:`formants <get_formant>`.
   • **Convert the sequences** and save them in different formats (``.json``, ``.xlsx``, ``.txt``, ``.csv``, ``.tsv``
     or ``.mat``), using :meth:`~classes.sequence.Sequence.save`.
   • **Display the sequences** (:meth:`~display_functions.sequence_reader`), compare them side-by-side or superimposed
     (:meth:`~display_functions.sequence_comparer`), and save them as video files
     (:meth:`~display_functions.save_video_sequence`).
   • **Plot** the movement or acoustic variables, either for
     :ref:`a single joint <single_joint_movement_plotter>` or for
     :ref:`all of them <joints_movement_plotter>`.
   • **Perform statistical analyses** on the relationship between motion capture sequences and speech
     (:doc:`analysis functions <functions/analysis_functions>`).


Where do I start?
-----------------
Start :doc:`here <general/install>` to install the toolbox as a Python module. Once it is done, you can follow an
example provided :doc:`here <general/example>`.


Useful links
------------
* `GitHub repository <https://github.com/RomainPastureau/Krajjat>`_
* :ref:`Index of all the documented functions<genindex>`
* Documentation contents
   .. toctree::
      :maxdepth: 2

      general
      classes
      functions
      appendix
