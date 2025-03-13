"""Default metaclass for Sequence, Audio and AudioDerivative. Contains the methods that are common to all time series.
"""
import copy
import os
import os.path as op

import numpy as np
from scipy.io import savemat

from krajjat.classes.exceptions import InvalidPathException, EmptyInstanceException
from krajjat.tool_functions import sort_files_trailing_index, show_progression


class TimeSeries(object):

    def __init__(self, kind=None, path=None, name=None, condition=None, verbosity=1):

        # Type
        self.kind = kind

        # Path & files
        self.path = None
        if type(path) is str:
            self.path = op.normpath(path)
        self.files = None

        # Other attributes
        self.name = name
        self.condition = condition
        self._define_name_init(verbosity)

        # Metadata
        self.metadata = {"processing_steps": []}

    def _define_name_init(self, verbosity=1):
        """Sets the name attribute for an instance of the class, using the name provided during the
        initialization, or the path. If no ``name`` is provided, the function will create the name based on the ``path``
        provided, by defining the name as the last element of the path hierarchy (last subfolder, or file name).
        For example, if ``path`` is ``"C:/Users/Darlene/Documents/Recording001/"``, the function will define the name
        on ``"Recording001"``. If both ``name`` and ``path`` are set on ``None``, the object name will be defined as
        ``"Unnamed x"``, with x being the class name (``audio``, ``sequence``, or one of the audio derivatives).

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        if self.name is not None:
            if verbosity > 1:
                print(f"The provided name {self.name} will be attributed to the sequence.")

        elif self.path is not None:
            # Case where the path has a wildcard
            if "*" in op.split(self.path)[-1]:
                self.name = op.split(op.split(self.path)[0])[-1]
            else:
                self.name = op.splitext(op.split(self.path)[-1])[0]
            if verbosity > 1:
                print(f"No name was provided. Instead, the name {self.name} was attributed by extracting it from " +
                      f"the provided path.")

        else:
            self.name = "Unnamed " + self.kind.lower()
            if verbosity > 1:
                print(f"No name nor path was provided. The placeholder name {self.name} was attributed to the " +
                      f"sequence.")

    def _load_from_path(self, verbosity=1):
        """Loads the data from the :attr:`path` provided during the initialization.

        .. versionadded:: 2.0

        Parameters
        ----------
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        # If it's an existing folder, we set file on nothing
        if op.exists(self.path) and op.isdir(self.path):
            folder = self.path
            file = ""
        # Else we split the path between folder and file
        else:
            folder, file = op.split(self.path)

        # If the folder does not exist
        if not op.exists(folder):
            raise InvalidPathException(self.path, self.kind, "The folder doesn't exist.")

        # If the file contains a wildcard
        if "*" in file:
            self.files = sort_files_trailing_index(self.path, object_type=self.kind.lower(), verbosity=verbosity,
                                                   add_tabs=1)
            self.path = folder

        else:
            # If the file does not exist
            if not op.exists(op.join(folder, file)):
                raise InvalidPathException(self.path, self.kind, "The file doesn't exist.")

            # If it is a directory
            if op.isdir(self.path):
                self.files = sort_files_trailing_index(self.path,
                                                       accepted_extensions=["json", "csv", "mat", "pkl", "tsv", "txt", "xlsx"],
                                                       object_type=self.kind.lower(), verbosity=verbosity, add_tabs=1)

            else:
                self.files = [file]

    def _set_attributes_from_other_object(self, other):
        """Sets the attributes `condition`, `path` and `metadata` of the object from another instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        other: TimeSeries
            Another TimeSeries instance, from which to copy some of the parameters.
        """
        self.path = other.path
        self.condition = other.condition
        self.metadata = copy.deepcopy(other.metadata)

    def set_name(self, name):
        """Sets the :attr:`name` attribute of the instance. This name can be used as display functions or as
        a means to identify the object.

        .. versionadded:: 2.0

        Parameters
        ----------
        name : str
            A name to describe the instance.
        """

        self.name = name

    def set_condition(self, condition):
        """Sets the :attr:`condition` attribute of the instance. This attribute can be used to save the
        experimental condition in which the instance was recorded.

        .. versionadded:: 2.0

        Parameters
        ----------
        condition : str
            The experimental condition in which the instance was recorded.
        """
        self.condition = condition

    def copy(self):
        """Returns a deep copy of the object.

        .. versionadded:: 2.0

        Returns
        -------
        Audio
            A new object, copy of the original.
        """
        audio = copy.deepcopy(self)
        return audio