Audio derivatives
=================

Description
-----------
Classes for time series derived from audio clips: Envelope, Intensity, Pitch and Formants.

AudioDerivative
---------------

Note
^^^^
This class is a parent class for :class:`Envelope`, :class:`Pitch`, :class:`Intensity` and :class:`Formant`. This class
should not be called directly: instead, the methods should be called through the child classes when an object is
created by one of the instances of the class :class:`Audio`.

Initialisation
^^^^^^^^^^^^^^
.. autoclass:: krajjat.classes.audio_derivatives.AudioDerivative

Methods
^^^^^^^
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.set_name
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_samples
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_timestamps
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_frequency
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_name
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.get_number_of_samples
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.filter_frequencies
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.resample
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.__len__
.. automethod:: krajjat.classes.audio_derivatives.AudioDerivative.__getitem__

All of the following classes inherit from AudioDerivative: all the methods described above can then be used for any
object from the classes below.

Envelope
--------
.. autoclass:: krajjat.classes.audio_derivatives.Envelope

Pitch
-----
.. autoclass:: krajjat.classes.audio_derivatives.Pitch

Intensity
---------
.. autoclass:: krajjat.classes.audio_derivatives.Intensity

Formant
-------
.. autoclass:: krajjat.classes.audio_derivatives.Formant
