def cosine_filter(nb_samples, par_cell, f_vect, ws_vect):
    """Creates and returns a filter used to get the envelope of an audio stream.

    Parameters
    ----------
    nb_samples: int
        The length of the filter. It should be equal to the amount of samples in the array to filter.
    par_cell: list(str)
        Array with "low", "high" or "notch".
    f_vect: list(float)
        Array with normalized frequencies (0 = 0 Hz; 1 = fsample/2).
    ws_vect: list(float)
        Array with normalized frequency width.

    Returns
    -------
    np.ndarray(float)
        Filter in the Fourier space
    """

    f_h = np.ones(nb_samples)

    for i in range(len(f_vect)):
        f = f_vect[i]
        ws = ws_vect[i]
        f_low = nb_samples * (f - ws / 2) / 2
        f_high = nb_samples * (f + ws / 2) / 2
        f_mult = np.zeros(nb_samples)

        if par_cell[i] == "low":
            f_mult[:int(f_low) + 1] = 1
            f_mult[int(np.ceil(f_high)):int(np.ceil((nb_samples + 1) / 2))] = 0
            f_mult[int(np.ceil(f_low)):int(f_high) + 1] = np.cos(
                (np.arange(int(np.ceil(f_low)), int(f_high) + 1) - f_low - 1) / (f_high - f_low) * np.pi / 2) ** 2
            f_mult[int(np.ceil((nb_samples + 1) / 2)):] = f_mult[int((nb_samples + 1) / 2) - 1:0:-1]

        elif par_cell[i] == "high":
            f_mult[:int(f_low) + 1] = 0
            f_mult[int(np.ceil(f_high)):int(np.ceil((nb_samples + 1) / 2))] = 1
            f_mult[int(np.ceil(f_low)):int(f_high) + 1] = np.sin(
                (np.arange(int(np.ceil(f_low)), int(f_high) + 1) - f_low - 1) / (f_high - f_low) * np.pi / 2) ** 2
            f_mult[int(np.ceil((nb_samples + 1) / 2)):] = f_mult[int((nb_samples + 1) / 2) - 1:0:-1]

        elif par_cell[i] == "notch":
            f_mult[:int(f_low) + 1] = 1
            f_mult[int(np.ceil(f_high)):int(np.ceil((nb_samples + 1) / 2))] = 1
            f_mult[int(np.ceil(f_low)):int(f_high) + 1] = np.cos(
                (np.arange(int(np.ceil(f_low)), int(f_high) + 1) - f_low - 1) / (f_high - f_low) * np.pi) ** 2
            f_mult[int(np.ceil((nb_samples + 1) / 2)):] = f_mult[int((nb_samples + 1) / 2) - 1:0:-1]

        else:
            raise ValueError("The filter must be low, high or notch")

        f_h = f_h * f_mult

    return f_h

def calculate_velocity(pose1, pose2, joint_label):
    """Given two poses and a joint label, returns the velocity of the joint, i.e. the distance travelled between the
    two poses, divided by the time elapsed between the two poses.

    .. versionadded:: 2.0

    Parameters
    ----------
    pose1: Pose
        The first Pose object, at the beginning of the movement.
    pose2: Pose
        The second Pose object, at the end of the movement.
    joint_label: str
        The label of the joint.

    Returns
    -------
    float
        The velocity of the joint between the two poses, in m/s.
    """

    # Get the distance travelled by a joint between two poses (meters)
    dist = calculate_distance(pose1.joints[joint_label], pose2.joints[joint_label])

    # Get the time elapsed between two poses (seconds)
    delay = calculate_delay(pose1, pose2)

    # Calculate the velocity (meters per seconds)
    velocity = dist / delay

    return velocity


def calculate_acceleration(pose1, pose2, pose3, joint_label):
    """Given three poses and a joint label, returns the acceleration of the joint, i.e. the difference of velocity
    between pose 1 and pose 2, and pose 2 and pose 3, over the time elapsed between pose 2 and pose 3.

    .. versionadded:: 2.0

    Parameters
    ----------
    pose1: Pose
        The first Pose object.
    pose2: Pose
        The second Pose object.
    pose3: Pose
        The third Pose object.
    joint_label: str
        The label of the joint.

    Returns
    -------
    float
        The velocity of the joint between the two poses, in m/s.
    """

    velocity1 = calculate_velocity(pose1, pose2, joint_label)
    velocity2 = calculate_velocity(pose2, pose3, joint_label)

    delay = calculate_delay(pose2, pose3)

    acceleration = (velocity2 - velocity1) # / np.power(delay, 2)

    return acceleration

def resample_images_to_frequency(images_paths, timestamps, frequency):
    """Given a series of images with specific timestamps, returns a new series of images and timestamps, resampled at
    a given frequency. For example, for images with timestamps at a rate of 20 Hz, and with a frequency set on 100 Hz,
    each image path will be copied 5 times with 5 different timestamps in the output. This can be used to obtain a
    video set at a defined framerate, regardless of the original frequency.

    .. versionadded:: 2.0

    Parameters
    ----------
    images_paths: list(str)
        A list of images paths.
    timestamps: list(float)
        A list of timestamps for each image path.
    frequency: int or float
        The frequency at which to resample the images (images per second).

    Returns
    -------
    list(str)
        A list of images paths.
    list(float)
        A list of timestamps.
    """
    number_of_frames = math.ceil(timestamps[-1] * frequency) + 1
    new_timestamps = []
    new_images = []
    t = 0
    duration = 1 / frequency

    for f in range(number_of_frames):
        new_timestamps.append(t)
        possible_times = [abs(i - t) for i in timestamps]
        index_image = possible_times.index(min(possible_times))
        new_images.append(images_paths[index_image])
        t += duration

    return new_images, new_timestamps

def find_common_parent_path(*paths, separator="/"):
    """Finds the common root to a series of paths. If the root of the paths is different, the function returns an
    empty string.

    .. versionadded:: 2.0

    Parameters
    ----------
    paths: str
        The paths, or a list of paths preceded by an asterisk ``*``. If only one path is provided or if the list
        contains only one element, this element will be returned by the function.
    separator: str
        The separator symbol between the elements of the path (default: ``"/"``).

    Returns
    -------
    str
        The common parent path between the paths passed as parameters.

    Example
    -------
    >>> path1 = "C:/Users/Olivia/Documents/Word/Novels/Celsius 233.docx"
    >>> path2 = "C:/Users/Olivia/Documents/Word/Novels/Arrogance and Preconception.docx"
    >>> path3 = "C:/Users/Olivia/Documents/Word/Documentation/Krajjat documentation.docx"
    >>> path4 = "C:/Users/Olivia/Documents/Excel/Results/Results_1.xlsx"
    >>> path5 = "C:/Users/Olivia/Documents/Excel/Results/Results_2.xlsx"
    >>> path6 = "C:/Users/Olivia/Documents/Contract.pdf"
    >>> print(find_common_parent_path(path1, path2, path3, path4, path5, path6))
    C:/Users/Olivia/Documents/
    >>> print(find_common_parent_path(*[path1, path2, path3, path4, path5, path6]))
    C:/Users/Olivia/Documents/
    """

    # If there is only one path, we return it
    if len(paths) == 1:
        return paths[0]

    paths_separated = []
    min_length = None

    # We separate the paths by their separator ("/")
    for path in paths:
        sub_paths = path.split(separator)
        paths_separated.append(sub_paths)
        if min_length is None:
            min_length = len(sub_paths)
        elif len(sub_paths) < min_length:
            min_length = len(sub_paths)

    # We check if all the parent paths are the same up to the shortest path
    common_parent_path = []
    add_path = True
    for i in range(min_length):
        for j in range(1, len(paths_separated)):
            if not paths_separated[j - 1][i] == paths_separated[j][i]:
                add_path = False
                break

        if add_path:
            common_parent_path.append(paths_separated[0][i])

    common_parent_path = separator.join(common_parent_path)

    return common_parent_path

    # Path functions
    def test_find_common_parent_path(self):
        path_1 = "A:/a/a/a/a/a/a/a/a/a"
        path_2 = "A:/a/a/a/a/a/a/a/a/a"
        path_3 = "A:/a/a/a/a/a/a/a/a/a/"
        path_4 = "A:/a/a/a/a/a/b/a/a/a"
        path_5 = "A:/b/a/a/a/a/a/a/a/a"
        path_6 = "A:"
        path_7 = "A:/"
        path_8 = "B:/a/a/a/a/a/a/a/a/a"
        path_9 = "A:/a/a/a/a/a/a/a/b/a"

        path_1b = "A:\\a\\a\\a\\a\\a\\a\\a\\"
        path_2b = "A:\\a\\a\\"

        assert find_common_parent_path(path_1, path_3) == "A:/a/a/a/a/a/a/a/a/a"
        assert find_common_parent_path(path_1, path_4) == "A:/a/a/a/a/a"
        assert find_common_parent_path(path_1, path_5) == "A:"
        assert find_common_parent_path(path_1, path_6) == "A:"
        assert find_common_parent_path(path_1, path_7) == "A:"
        assert find_common_parent_path(path_1, path_8) == ""
        assert find_common_parent_path(path_1, path_9) == "A:/a/a/a/a/a/a/a"
        assert find_common_parent_path(path_1, path_2, path_3, path_4, path_5) == "A:"
        assert find_common_parent_path(*[path_1, path_2, path_3, path_4, path_5]) == "A:"
        assert find_common_parent_path(path_6, path_7) == "A:"
        assert find_common_parent_path(path_1b, path_2b, separator="\\") == "A:\\a\\a"

    def _set_has_velocity_over_threshold(self, has_velocity_over_threshold):
        """Sets the value of the attribute :attr:`_has_velocity_over_threshold`. This function is used by
        :meth:`.Sequence.correct_jitter()`.

        .. versionadded:: 2.0

        Parameters
        ----------
        has_velocity_over_threshold: bool
            If `True`, the velocity of this joint, compared to the previous joint, has been found to be over threshold
            defined in the parameters of :meth:`.Sequence.correct_jitter()`.
        """
        self._velocity_over_threshold = has_velocity_over_threshold

    def _set_is_rereferenced(self, is_rereferenced):
        """Sets the value of the attribute :attr:`_is_rereferenced`.

        .. versionadded:: 2.0

        Parameters
        ----------
        is_rereferenced: bool
            If `True`, the coordinates of this joint have been modified by :meth:`.Sequence.re_reference()`.
        """
        self._rereferenced = is_rereferenced

    def _set_is_dejittered(self, is_dejittered):
        """Sets the value of the attribute :attr:`_is_dejittered`.

        .. versionadded:: 2.0

        Parameters
        ----------
        is_dejittered: bool
            If `True`, the coordinates of this joint have been modified by :meth:`.Sequence.correct_jitter()`.
        """
        self._dejittered = is_dejittered

    def _set_is_zero_corrected(self, is_zero_corrected):
        """Sets the value of the attribute :attr:`_is_zero_corrected`.

        .. versionadded:: 2.0

        Parameters
        ----------
        is_zero_corrected: bool
            If `True`, the coordinates of this joint have been modified by :meth:`.Sequence.correct_zeros()`.
        """
        self._interpolated = is_zero_corrected

    def get_average_sampling_rate(self):
        """Returns the average number of poses per second of the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Average number of poses per second for the sequence.

        Example
        -------

        """
        average_frequency = (self.get_number_of_poses() - 1) / self.get_duration()
        return average_frequency

    def get_min_sampling_rate(self):
        """Returns the minimum frequency of poses per second of the sequence, which is equal to 1 over the maximum time
        between two poses in the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Minimum number of poses per second for the sequence.
        """
        framerates = self.get_sampling_rates()
        return min(framerates)

    def get_max_sampling_rate(self):
        """Returns the maximum frequency of poses per second of the sequence, which is equal to 1 over the minimum time
        between two poses in the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Maximum number of poses per second for the sequence.
        """
        framerates = self.get_sampling_rates()
        return max(framerates)

    def get_joint_coordinate_as_array(self, joint_label, axis, timestamp_start=None, timestamp_end=None):
        """Returns a numpy array of all the values for one specified axis of a specified joint label.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str
            The required axis (``"x"``, ``"y"`` or ``"z"``).
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        numpy.ndarray(float)
            A chronological numpy array of the values (in meters) on one axis for the specified joint.

        Note
        ----
        The values returned by the function can be paired with the timestamps obtained with
        :meth:`Sequence.get_timestamps`.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)
        elif axis not in ["x", "y", "z"]:
            raise InvalidParameterValueException("axis", axis, ["x", "y", "z"])

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        values = np.zeros(len(self.poses))
        start = None
        end = None
        for p in range(len(self.poses)):
            if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
                if start is None:
                    start = p
                values[p] = self.poses[p].joints[joint_label].get_coordinate(axis)
            elif start is not None and end is None:
                end = p

        return values[start:end]

    def get_joint_distance_as_array(self, joint_label, axis=None, timestamp_start=None, timestamp_end=None):
        """Returns a list of all the distances travelled for a specific joint. If an axis is specified, the distances
        are calculated on this axis only.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        numpy.ndarray(float)
            A chronological numpy array of the distances travelled (in meters) for the specified joint.

        Note
        ----
        Because the velocities are calculated by consecutive poses, the list returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        values = np.zeros(len(self.poses) - 1)
        for p in range(1, len(self.poses)):
            if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
                values[p - 1] = calculate_distance(self.poses[p - 1].joints[joint_label],
                                                   self.poses[p].joints[joint_label],
                                                   axis)
        return values

    def get_joint_velocity_as_array(self, joint_label, timestamp_start=None, timestamp_end=None):
        """Returns a list of all the velocities (distance travelled over time) for a specified joint.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        numpy.ndarray(float)
            A chronological numpy array of the velocities (in meters per second) for the specified joint.

        Note
        ----
        Because the velocities are calculated by consecutive poses, the list returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        # values = np.zeros(len(self.poses) - 1)
        distances = self.get_joint_distance_as_array(joint_label, None, timestamp_start, timestamp_end)
        values = calculate_derivative(distances, "velocity", window_length=np.min((len(distances), 7)),
                                      freq=self.get_sampling_rate())
        # for p in range(1, len(self.poses)):
        #     if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
        #         values[p - 1] = calculate_velocity(self.poses[p - 1], self.poses[p], joint_label)
        return values

    def get_joint_acceleration_as_array(self, joint_label, absolute=False, timestamp_start=None, timestamp_end=None):
        """Returns a list of all the accelerations (differences of velocity over time) for a specified joint.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration value. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        numpy.ndarray(float)
            A chronological numpy array of the accelerations (in meters per second squared) for the specified joint.

        Note
        ----
        Because the accelerations are calculated by consecutive pairs of poses, the list returned by the function
        have a length of :math:`n-2`, with :math:`n` being the number of poses of the sequence.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if timestamp_start is None:
            timestamp_start = self.poses[0].get_timestamp()
        if timestamp_end is None:
            timestamp_end = self.poses[-1].get_timestamp()

        values = np.zeros(len(self.poses) - 2)
        for p in range(2, len(self.poses)):
            if timestamp_start <= self.poses[p].get_timestamp() <= timestamp_end:
                value = calculate_acceleration(self.poses[p - 2], self.poses[p - 1], self.poses[p], joint_label)
                if absolute:
                    values[p - 2] = abs(value)
                else:
                    values[p - 2] = value
        return values

    def get_joint_metric_as_array(self, joint_label, time_series="velocity", timestamp_start=None, timestamp_end=None):
        """For a specified joint, returns a list containing one of its time series (x coordinate, y coordinate,
        z coordinate, distance travelled, velocity, or acceleration).

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        time_series: str, optional
            Defines the time_series to return to the list. This parameter can be:

            • ``"x"``, ``"y"`` or ``"z"``, to return the values of the coordinate on a specified axis, for each
              timestamp.
            • The ``"distance"`` travelled over time (in meters), between consecutive poses.
            • The ``"distance_x"``, ``"distance_y"`` or ``"distance_z"`` travelled over time on one axis (in meters),
              between consecutive poses.
            • The ``"velocity"``, defined by the distance travelled over time (in meters per second), between
              consecutive poses.
            • The ``"acceleration"``, defined by the velocity over time (in meters per second squared), between
              consecutive pairs of poses. ``"acceleration_abs"`` returns absolute values.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        numpy.ndarray(float)
            A chronological list of the velocities (in meters per second) for the specified joint.

        Note
        ----
        Because the distances and velocities are calculated by consecutive poses, the list returned by the
        function have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        Following the same idea, accelerations are calculate by consecutive pairs of poses. The list returned by the
        function would then have a length of :math:`n-2`.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        if time_series in ["x", "y", "z"]:
            return self.get_joint_coordinate_as_array(joint_label, time_series, timestamp_start, timestamp_end)
        elif time_series == "distance":
            return self.get_joint_distance_as_array(joint_label, None, timestamp_start, timestamp_end)
        elif time_series.startswith("distance"):
            return self.get_joint_distance_as_array(joint_label, time_series[9:10], timestamp_start, timestamp_end)
        else:
            array = self.get_joint_distance_as_array(joint_label, None, timestamp_start, timestamp_end)
            derivative = calculate_derivative(array, time_series)
            # timestamps = self.get_timestamps()[1:]
            print(time_series, derivative)
            return derivative
        # elif time_series == "velocity":
        #     return self.get_joint_velocity_as_array(joint_label, timestamp_start, timestamp_end)
        # elif time_series == "acceleration":
        #     return self.get_joint_acceleration_as_array(joint_label, False, timestamp_start, timestamp_end)
        # elif time_series == "acceleration_abs":
        #     return self.get_joint_acceleration_as_array(joint_label, True, timestamp_start, timestamp_end)
        # else:
        #     raise InvalidParameterValueException("time_series", time_series, ["x", "y", "z", "distance", "distance_x",
        #                                                                       "distance_y", "distance_z", "velocity",
        #                                                                       "acceleration"])

    def get_single_coordinates(self, axis, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the values of the coordinates on a single axis for all the joints. The
        dictionary will contain the joints labels as keys, and a list of coordinates as values. The coordinates are
        returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str
            The axis from which to extract the coordinate: ``"x"``, ``"y"`` or ``"z"``.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and coordinates values on a specified axis as values (in meters),
            ordered chronologically.
        """

        dict_coordinates = OrderedDict()

        for joint_label in self.joint_labels:
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_coordinates[joint_label] = self.get_joint_coordinate_as_array(joint_label, axis,
                                                                               timestamp_start, timestamp_end)

        return dict_coordinates

    def get_distances(self, axis=None, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the joint labels as keys, and a list of distances (distance travelled between
        two poses) as values. Distances are calculated using the :func:`tool_functions.calculate_distance()` function,
        and are defined by the distance travelled between two poses (in meters). The distances are returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and lists of distances travelled as values (in meters), ordered
            chronologically.

        Note
        ----
        Because the distances are calculated between consecutive poses, the lists returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """

        dict_distances = OrderedDict()

        for joint_label in self.joint_labels:
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_distances[joint_label] = self.get_joint_distance_as_array(joint_label, axis,
                                                                           timestamp_start, timestamp_end)

        return dict_distances

    def get_distance_between_hands(self, timestamp_start=None, timestamp_end=None):
        """Returns a vector containing the distance (in meters) between the two hands across time. If the
        joint label system is Kinect, the distance will be calculated between ``"HandRight"`` and ``"HandLeft"``.
        If the joint label system is Qualisys, the distance will be calculated between ``"HandOutRight"`` and
        ``"HandOutLeft"``.

        .. versionadded:: 2.0

        Note
        ----
        This function is a wrapper for the function :meth:`Sequence.get_distance_between_joints`.

        Parameters
        ----------
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A list of distances between the two hands, in meters.
        """
        labels = self.joint_labels
        if "HandRight" in labels:
            return self.get_distance_between_joints("HandRight", "HandLeft", timestamp_start, timestamp_end)
        elif "HandOutRight" in labels:
            return self.get_distance_between_joints("HandOutRight", "HandOutLeft", timestamp_start, timestamp_end)
        else:
            raise Exception("The Sequence does not contain valid hand joint labels.")

    def get_distance_between_joints(self, joint_label1, joint_label2, timestamp_start=None, timestamp_end=None):
        """Returns a vector containing the distance (in meters) between the two joints provided across time.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label1: str
            The label of the first joint (e.g., ``"Head"``).
        joint_label2: str
            The label of the second joint (e.g., ``"FootRight"``).
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.
        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        Returns
        -------
        list(float)
            A list of distances between the two specified joints, in meters.
        """
        labels = self.joint_labels

        if joint_label1 not in labels:
            raise InvalidJointLabelException(joint_label1)
        if joint_label2 not in labels:
            raise InvalidJointLabelException(joint_label2)

        distances = []
        for p in self.poses:
            if timestamp_start < p.get_timestamp() < timestamp_end:
                distances.append(calculate_distance(p.get_joint(joint_label1), p.get_joint(joint_label2)))

        return distances

    def get_velocities(self, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the joint labels as keys, and a list of velocities (distance travelled over
        time between two poses) as values. Velocities are calculated using the
        :func:`tool_functions.calculate_velocity()` function, and are defined by the distance travelled between two
        poses (in meters), divided by the time elapsed between these two poses (in seconds). The velocities are
        returned in meters per second.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and lists of velocity as values (in meters per second), ordered
            chronologically.

        Note
        ----
        Because the velocities are calculated between consecutive poses, the lists returned by the function
        have a length of :math:`n-1`, with :math:`n` being the number of poses of the sequence.
        """

        dict_velocities = OrderedDict()

        for joint_label in self.joint_labels:
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_velocities[joint_label] = self.get_joint_velocity_as_array(joint_label, timestamp_start, timestamp_end)

        return dict_velocities

    def get_accelerations(self, absolute=False, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing the joint labels as keys, and a list of accelerations (differences of
        velocity over time between two poses) as values. Accelerations are calculated using the
        :func:`tool_functions.calculate_acceleration()` function, and are defined by the difference of velocity between
        two consecutive pairs of poses (in meters per second), divided by the time elapsed between these last pose of
        each pair (in seconds). The accelerations are returned in meters per second squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        absolute: boolean, optional
            If set on ``True``, returns the absolute acceleration values. If set on ``False`` (default), returns
            the original, signed acceleration values.

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        --------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and lists of accelerations as values (in meters per second squared),
            ordered chronologically.

        Note
        ----
        Because the accelerations are calculated between consecutive pairs of poses, the lists returned by the function
        have a length of :math:`n-2`, with :math:`n` being the number of poses of the sequence.
        """

        dict_accelerations = OrderedDict()

        for joint_label in self.joint_labels:
            if verbosity > 1:
                print(str(joint_label), end=" ")
            dict_accelerations[joint_label] = self.get_joint_acceleration_as_array(joint_label, absolute,
                                                                                   timestamp_start, timestamp_end)

        return dict_accelerations

    def get_time_series_as_list(self, metric, timestamp_start=None, timestamp_end=None, verbosity=1):
        """Returns a dictionary containing one of the metrics for all joints: coordinate, distance travelled, velocity
        or acceleration.

        .. versionadded:: 2.0

        Parameters
        ----------
        metric: str
            The metric to be returned, can be either:

            • ``"x"``, for the values on the x-axis (in meters)
            • ``"y"``, for the values on the y-axis (in meters)
            • ``"z"``, for the values on the z axis (in meters)
            • ``"distance_hands"``, for the distance between the hands (in meters)
            • ``"distance"``, for the distance travelled (in meters)
            • ``"distance_x"`` for the distance travelled on the x-axis (in meters)
            • ``"distance_y"`` for the distance travelled on the y-axis (in meters)
            • ``"distance_z"`` for the distance travelled on the z axis (in meters)
            • ``"velocity"`` for the velocity (in meters per second)
            • ``"acceleration"`` for the acceleration (in meters per second squared)
            • ``"acceleration_abs"`` for the absolute acceleration (in meters per second squared)

        timestamp_start: float or None, optional
            If provided, the return values having a timestamp below the one provided will be ignored from the output.

        timestamp_end: float or None, optional
            If provided, the return values having a timestamp above the one provided will be ignored from the output.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.

        Returns
        -------
        OrderedDict(str: list(float))
            Dictionary with joint labels as keys, and the specified metric as a value.

        Note
        ----
        Because the distances and velocities are calculated between consecutive poses (apart from distance_hands), the
        lists returned by the function have a length of :math:`n-1`, with :math:`n` being the number of poses of the
        sequence. For accelerations, the lists returned have a length of :math:`n-2`.
        """
        if metric in ["x", "y", "z"]:
            return self.get_single_coordinates(metric, timestamp_start, timestamp_end, verbosity)
        elif metric == "distance":
            return self.get_distances(None, timestamp_start, timestamp_end, verbosity)
        elif metric == "distance_hands":
            return self.get_distance_between_hands(timestamp_start, timestamp_end)
        elif metric.startswith("distance"):
            return self.get_distances(metric[-2:], timestamp_start, timestamp_end, verbosity)
        else:
            distances = self.get_distances(None, timestamp_start, timestamp_end, verbosity)
            values = {}
            for joint_label in distances:
                values[joint_label] = calculate_derivative(distances, metric, self.get_sampling_rate())
            return values
        # elif metric == "velocity":
        #     return self.get_velocities(timestamp_start, timestamp_end, verbosity)
        # elif metric == "acceleration":
        #     return self.get_accelerations(False, timestamp_start, timestamp_end, verbosity)
        # elif metric == "acceleration_abs":
        #     return self.get_accelerations(True, timestamp_start, timestamp_end, verbosity)
        # else:
        #     raise InvalidParameterValueException("metric", metric)

    def get_max_coordinate_whole_sequence(self, axis, absolute=False):
        """Returns the single maximum value of all the joints and for the whole sequence of a coordinate on a specified
        axis, in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str
            The axis from which to get the maximum coordinate: ``"x"``, ``"y"`` or ``"z"``.

        absolute: bool, optional
            If set on `True`, returns the maximum absolute value. Otherwise (default), returns the maximum value.

        Returns
        --------
        float
            Maximum value of a coordinate on a specified axis, in meters.
        """
        dict_coordinate = self.get_single_coordinates(axis)
        max_distance_whole_sequence = 0

        for joint_label in dict_coordinate.keys():
            if absolute:
                local_maximum = np.max(np.abs(dict_coordinate[joint_label]))
            else:
                local_maximum = np.max(dict_coordinate[joint_label])
            if local_maximum > max_distance_whole_sequence:
                max_distance_whole_sequence = local_maximum

        return max_distance_whole_sequence

    def get_max_distance_whole_sequence(self, axis=None):
        """Returns the single maximum value of the distance travelled between two poses across every joint of the
        sequence. The distances are first calculated using the :meth:`Sequence.get_distances()` function. The distance
        travelled by a joint is returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        --------
        float
            Maximum value of the distance travelled between two poses across every joint of the sequence, in meters.
        """
        dict_distances = self.get_distances(axis)
        max_distance_whole_sequence = 0

        for joint_label in dict_distances.keys():
            local_maximum = max(dict_distances[joint_label])
            if local_maximum > max_distance_whole_sequence:
                max_distance_whole_sequence = local_maximum

        return max_distance_whole_sequence

    def get_max_velocity_whole_sequence(self):
        """Returns the single maximum value of the velocity across every joint of the sequence. The velocities are
        first calculated using the :meth:`Sequence.get_velocities()` function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocity is returned in meters per second.

        .. versionadded:: 2.0

        Returns
        --------
        float
            Maximum value of the velocity across every joint of the sequence, in meters per second.
        """
        dict_velocities = self.get_velocities()
        max_velocity_whole_sequence = 0

        for joint_label in dict_velocities.keys():
            local_maximum = max(dict_velocities[joint_label])
            if local_maximum > max_velocity_whole_sequence:
                max_velocity_whole_sequence = local_maximum

        return max_velocity_whole_sequence

    def get_max_acceleration_whole_sequence(self, absolute=True):
        """Returns the single maximum value of the acceleration across every joint of the sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_accelerations()` function. The acceleration is defined
        by the difference of velocity between two consecutive pairs of poses (in meters per second), divided by the time
        elapsed between these last pose of each pair (in seconds). The accelerations are returned in meters per second
        squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration value. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.

        Returns
        -------
        float
            Maximum value of the velocity across every joint of the sequence, in meters per second.
        """
        dict_accelerations = self.get_accelerations(absolute)
        max_acceleration_whole_sequence = 0

        for joint_label in dict_accelerations.keys():
            local_maximum = max(dict_accelerations[joint_label])
            if local_maximum > max_acceleration_whole_sequence:
                max_acceleration_whole_sequence = local_maximum

        return max_acceleration_whole_sequence

    def get_max_distance_single_joint(self, joint_label, axis=None):
        """Returns the maximum value of the distance travelled between two poses for a given joint, across the whole
        sequence. The distances are first calculated using the :meth:`Sequence.get_distances()` function. The distance
        travelled by a joint between two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        --------
        float
            Maximum value of the distance travelled for a given joint between two poses, in meters.
        """
        dict_distances = self.get_distances(axis)

        if joint_label not in dict_distances.keys():
            raise InvalidJointLabelException(joint_label)

        return max(dict_distances[joint_label])

    def get_max_velocity_single_joint(self, joint_label):
        """Returns the maximum value of the velocity for a given joint, across the whole sequence. The velocities are
        first calculated using the :meth:`Sequence.get_velocities()` function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocity is returned in meters per second.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        --------
        float
            Maximum value of the velocity for a given joint, in meters per second.
        """
        dict_velocities = self.get_velocities()

        if joint_label not in dict_velocities.keys():
            raise InvalidJointLabelException(joint_label)

        return max(dict_velocities[joint_label])

    def get_max_acceleration_single_joint(self, joint_label, absolute=True):
        """Returns the maximum value of the acceleration for a given joint, across the whole sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_accelerations()` function. The acceleration is defined
        by the difference of velocity between two consecutive pairs of poses (in meters per second), divided by the time
        elapsed between these last pose of each pair (in seconds). The accelerations are returned in meters per second
        squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration value. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.

        Returns
        -------
        float
            Maximum value of the acceleration for a given joint, in meters per second squared.
        """
        dict_accelerations = self.get_accelerations(absolute)

        if joint_label not in dict_accelerations.keys():
            raise InvalidJointLabelException(joint_label)

        return max(dict_accelerations[joint_label])

    def get_max_distance_per_joint(self, axis=None):
        """Returns the maximum value of the distance travelled between two poses for each joint of the sequence. The
        distances are first calculated using the :meth:`Sequence.get_distances()` function. The distance
        travelled by a joint between two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and maximum velocities as values (in meters per second).
        """
        dict_distances = self.get_distances(axis)
        max_distance_per_joint = OrderedDict()

        for joint_label in dict_distances.keys():
            max_distance_per_joint[joint_label] = max(dict_distances[joint_label])

        return max_distance_per_joint

    def get_max_velocity_per_joint(self):
        """Returns the maximum value of the velocity for each joint of the sequence. The velocities are
        first calculated using the :meth:`Sequence.get_velocities()` function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocities are returned in meters per second.

        .. versionadded:: 2.0

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and maximum velocities as values (in meters per second).
        """
        dict_velocities = self.get_velocities()
        max_velocity_per_joint = OrderedDict()

        for joint_label in self.joint_labels:
            max_velocity_per_joint[joint_label] = max(dict_velocities[joint_label])

        return max_velocity_per_joint

    def get_max_acceleration_per_joint(self, absolute=True):
        """Returns the maximum value of the acceleration for each joint of the sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_accelerations()` function. The acceleration is defined
        by the difference of velocity between two consecutive pairs of poses (in meters per second), divided by the time
        elapsed between these last pose of each pair (in seconds). The accelerations are returned in meters per second
        squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        absolute: boolean, optional
            If set on ``True`` (default), returns the maximum absolute acceleration values. If set on ``False``, returns
            the maximum acceleration value, even if a negative value has a higher absolute value.

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and maximum accelerations as values (in meters per second squared).
        """
        max_acceleration_per_joint = OrderedDict()

        for joint_label in self.joint_labels:
            max_acceleration_per_joint[joint_label] = self.get_max_acceleration_single_joint(joint_label, absolute)

        return max_acceleration_per_joint

    def get_total_distance_whole_sequence(self, axis=None):
        """Returns the sum of the distances travelled by every joint across all the poses of the sequence. This allows
        to provide a value representative of the global “quantity of movement” produced during the sequence. The
        distances are first calculated using the Sequence.get_distances() function. The distance travelled by a joint
        between two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        -------
        float
            Sum of the distances travelled across every joint and poses of the sequence, in meters.
        """
        total_distance_whole_sequence = 0
        dict_distances = self.get_distances(axis)

        for joint_label in dict_distances.keys():
            total_distance_whole_sequence += sum(dict_distances[joint_label])

        return total_distance_whole_sequence

    def get_total_velocity_whole_sequence(self):
        """Returns the sum of the velocities of every joint across all the poses of the sequence. This allows to
        provide a value representative of the global "quantity of movement" produced during the sequence. The
        velocities are first calculated using the Sequence.get_velocities() function. The velocity of a joint is
        defined by the distance travelled between two poses (in meters), divided by the time elapsed between these
        two poses (in seconds). The velocities are returned in meters per second.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Sum of the velocities across every joint and poses of the sequence, in meters per second.
        """
        total_velocity_whole_sequence = 0
        dict_velocities = self.get_velocities()

        for joint_label in dict_velocities.keys():
            total_velocity_whole_sequence += sum(dict_velocities[joint_label])

        return total_velocity_whole_sequence

    def get_total_acceleration_whole_sequence(self):
        """Returns the sum of the absolute accelerations of every joint across all the poses of the sequence. This
        allows to provide a value representative of the global "quantity of movement" produced during the sequence. The
        acceleration values are first calculated using the :meth:`Sequence.get_accelerations()` function. The
        acceleration is defined by the difference of velocity between two consecutive pairs of poses (in meters per
        second), divided by the time elapsed between these last pose of each pair (in seconds). The accelerations are
        returned in meters per second squared.

        .. versionadded:: 2.0

        Returns
        -------
        float
            Sum of the accelerations across every joint and poses of the sequence, in meters per second squared.
        """
        total_acceleration_whole_sequence = 0
        dict_accelerations = self.get_accelerations(absolute=True)

        for joint_label in dict_accelerations.keys():
            total_acceleration_whole_sequence += sum(dict_accelerations[joint_label])

        return total_acceleration_whole_sequence

    def get_total_distance_single_joint(self, joint_label, axis=None):
        """Returns the total distance travelled for a given joint, across the whole sequence. The distances are first
        calculated using the Sequence.get_joint_distance_as_list() function. The distance travelled by a joint between
        two poses is defined in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        --------
        float
            Sum of the distances travelled across all poses for a single joint, in meters.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        return sum(self.get_joint_distance_as_array(joint_label, axis))

    def get_total_velocity_single_joint(self, joint_label):
        """Returns the sum of the velocities for a given joint, across the whole sequence. The velocities are first
        calculated using the Sequence.get_joint_velocity_as_list() function. The velocity of a joint is defined by the
        distance travelled between two poses (in meters), divided by the time elapsed between these two poses
        (in seconds). The velocity is returned in meters per second.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        --------
        float
            Sum of the velocities across all poses for a single joint, in meters per second.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        return sum(self.get_joint_velocity_as_array(joint_label))

    def get_total_acceleration_single_joint(self, joint_label):
        """Returns the sum of the absolute accelerations for a given joint, across the whole sequence. The acceleration
        values are first calculated using the :meth:`Sequence.get_joint_acceleration_as_list()` function. The
        acceleration is defined by the difference of velocity between two consecutive pairs of poses (in meters per
        second), divided by the time elapsed between these last pose of each pair (in seconds). The accelerations are
        returned in meters per second squared.

        .. versionadded:: 2.0

        Parameters
        ----------
        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        --------
        float
            Sum of the accelerations across all poses for a single joint, in meters per second squared.
        """
        if joint_label not in self.poses[0].joints.keys():
            raise InvalidJointLabelException(joint_label)

        return sum(self.get_joint_acceleration_as_array(joint_label, absolute=True))

    def get_total_distance_per_joint(self, axis=None):
        """Returns the sum of the distances travelled for each individual joint of the sequence. The distances are first
        calculated using the Sequence.get_total_distance_single_joint() function. The distance travelled between two
        poses of a joint is returned in meters.

        .. versionadded:: 2.0

        Parameters
        ----------
        axis: str or None, optional
            If specified, the returned distances travelled will be calculated on a single axis. If ``None`` (default),
            the distance travelled will be calculated based on the 3D coordinates.

        Returns
        -------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and sum of distances travelled across all poses as values (in meters).
        """
        total_distance_per_joint = OrderedDict()

        for joint_label in self.poses[0].joints.keys():
            total_distance_per_joint[joint_label] = self.get_total_distance_single_joint(joint_label, axis)

        return total_distance_per_joint

    def get_total_velocity_per_joint(self):
        """Returns the sum of the velocities for each individual joint of the sequence. The velocities are first
        calculated using the Sequence.get_total_velocity_single_joint() function. The velocity of a joint is defined by
        the distance travelled between two poses (in meters), divided by the time elapsed between these two poses (in
        seconds). The velocities are returned in meters per second.

        .. versionadded:: 2.0

        Returns
        ----------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and sum of velocities across all poses as values (in meters per
            second).
        """
        total_velocity_per_joint = OrderedDict()

        for joint_label in self.poses[0].joints.keys():
            total_velocity_per_joint[joint_label] = self.get_total_velocity_single_joint(joint_label)

        return total_velocity_per_joint

    def get_total_acceleration_per_joint(self):
        """Returns the sum of the absolute acceleration values for each individual joint of the sequence. The
        acceleration values are first calculated using the :meth:`Sequence.get_joint_acceleration_as_list()` function.
        The acceleration is defined by the difference of velocity between two consecutive pairs of poses (in meters per
        second), divided by the time elapsed between these last pose of each pair (in seconds). The accelerations are
        returned in meters per second squared.

        .. versionadded:: 2.0

        Returns
        ----------
        OrderedDict(str: float)
            Dictionary with joint labels as keys, and sum of absolute acceleration values across all poses as values
            (in meters per second squared).
        """
        total_velocity_per_joint = OrderedDict()

        for joint_label in self.poses[0].joints.keys():
            total_velocity_per_joint[joint_label] = self.get_total_velocity_single_joint(joint_label)

        return total_velocity_per_joint

    def get_fill_level_per_joint(self):
        """For each joint, returns the ratio of poses for which the coordinates are not equal to (0, 0, 0).

        .. versionadded:: 2.0

        Returns
        --------
        dict(str: float)
            A dictionary where each key is a joint label, and each value is the ratio (between 0 and 1) of poses where
            the coordinates of the joint are not equal to (0, 0, 0).
        """
        fill_levels = {}
        for joint_label in self.joint_labels:
            fill_levels[joint_label] = self.get_fill_level_single_joint(joint_label)

        return fill_levels

    def copy_pose(self, pose_index):
        """Returns a deep copy of a specified pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose to copy (starting at 0).

        Returns
        -------
        Pose
            The copy of a Pose instance.
        """

        if len(self.poses) == 0:
            raise EmptySequenceException()
        elif not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))

        pose = Pose(self.poses[pose_index].get_timestamp())

        for i in self.poses[pose_index].joints.keys():  # For every joint

            pose.joints[i] = self.copy_joint(pose_index, i)

        pose.relative_timestamp = self.poses[pose_index].get_relative_timestamp()

        return pose

    def copy_joint(self, pose_index, joint_label):
        """Returns a deep copy of a specified joint from a specified pose.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose to copy (starting at 0).

        joint_label: str
            The label of the joint (e.g. ``"Head"``).

        Returns
        -------
        Joint
            The copy of a Joint instance.
        """

        if len(self.poses) == 0:
            raise EmptySequenceException()
        elif not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))

        if joint_label not in self.poses[pose_index].get_joint_labels():
            raise InvalidJointLabelException(joint_label)

        joint = self.poses[pose_index].get_joint(joint_label).copy()

        return joint

    def print_pose(self, pose_index):
        """Prints the information related to one specific pose of the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose to copy (starting at 0).
        """
        if len(self.poses) == 0:
            raise EmptySequenceException()
        elif not 0 <= pose_index < len(self.poses):
            raise InvalidPoseIndexException(pose_index, len(self.poses))
        txt = "Pose " + str(pose_index + 1) + " of " + str(len(self.poses)) + "\n"
        txt += str(self.poses[pose_index])
        print(txt)

    # === Print functions ===

    def print_details(self, include_name=True, include_condition=True, include_date_recording=True,
                      include_number_of_poses=True, include_duration=True, add_tabs=0):
        """Prints a series of details about the sequence.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_name: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`name` to the printed string.
        include_condition: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`condition` to the printed string.
        include_date_recording: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`date_of_recording` to the printed string.
        include_number_of_poses: bool, optional
            If set on ``True`` (default), adds the length of the attribute :attr:`poses` to the printed string.
        include_duration: bool, optional
            If set on ``True`` (default), adds the duration of the Sequence to the printed string.
        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.
        """
        t = add_tabs * "\t"

        string = t
        if include_name:
            string += "Name: " + str(self.name) + " · "
        if include_condition:
            string += "Condition: " + str(self.condition) + " · "
        if include_date_recording:
            string += "Date recording: " + str(self.get_date_recording("str")) + " · "
        if include_number_of_poses:
            string += "Number of poses: " + str(self.get_number_of_poses()) + " · "
        if include_duration:
            string += "Duration: " + str(time_unit_to_timedelta(self.get_duration())) + " s  · "
        if len(string) > 3:
            string = string[:-3]

        print(string)

    def _fetch_files_from_folder(self, verbosity=1):
        """Finds all the files ending with the accepted extensions (``.csv``, ``.json``, ``.tsv``, ``.txt``, or
        ``.xlsx``) in the folder defined by path, and orders the files according to their name.

        .. versionadded:: 2.0

        Note
        ----
        This functions ignores the elements of the directory defined by :attr:`path` if:
            •	They don’t have an extension
            •	They are a folder
            •	Their extension is not one of the accepted ones (``.csv``, ``.json``, ``.tsv``, ``.txt``, or
                ``.xlsx``)
            •	The file name does not contain an underscore (``_``)

        If a file has a valid extension, the function tries to detect an underscore (``_``) in the name. The file
        names should be ``xxxxxx_0.ext``, where ``xxxxxx`` can be any series of characters, ``0`` must be the index of
        the sample (with or without leading zeros), and ``ext`` must be an accepted extension (``.csv``, ``.json``,
        ``.tsv``, ``.txt``, or ``.xlsx``). The first pose of the sequence must have the index 0. If the file does not
        have an underscore in the name, it is ignored. The indices must be coherent with the chronological order of the
        timestamps.

        The function uses the number after the underscore to order the samples. This is due to differences in how file
        systems handle numbers without leading zeros: some place ``sample_11.json`` alphabetically before
        ``sample_2.json`` (1 comes before 2), while some other systems place it after as 11 is greater than 2. In order
        to avoid these, the function converts the number after the underscore into an integer to place it properly
        according to its index.

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
        if verbosity > 0:
            print("Fetching sample files...", end=" ")

        file_list = os.listdir(self.path)  # List all the files in the folder
        self.files = ["" for _ in range(len(file_list))]  # Create an empty list the length of the files

        extensions_found = []  # Save the valid extensions found in the folder

        # Here, we find all the files that are either .json or .meta in the folder.
        for f in file_list:

            # If a file has an accepted extension, we get its index from its name to order it correctly in the list.
            # This is necessary as some file systems will order sample_2.json after sample_11.json because,
            # alphabetically, "1" is before "2".

            # We check if the element has a dot, i.e. if it is a file. If not, it is a folder, and we ignore it.
            if "." in f:

                extension = f.split(".")[-1]  # We get the file extension
                if extension in ["json", "csv", "tsv", "txt", "xlsx"]:

                    if verbosity > 1:
                        print("\tAdding file: " + str(f))

                    if "_" in f:
                        self.files[int(f.split(".")[0].split("_")[1])] = f
                        if extension not in extensions_found:
                            extensions_found.append(extension)
                    else:
                        if verbosity > 1:
                            print("""\tIgnoring file (no "_" detected in the name): """ + str(f))

                    if len(extensions_found) > 1:
                        raise InvalidPathException(self.path, "audio clip",
                                                   "More than one of the accepted extensions has been found in the " +
                                                   "provided folder: " + str(extensions_found[0]) + " and " +
                                                   str(extensions_found[1]))

                else:
                    if verbosity > 1:
                        print("\tIgnoring file (not an accepted filetype): " + str(f))

            else:
                if verbosity > 1:
                    print("\tIgnoring folder: " + str(f))

        # If files that weren't of the accepted extension are in the folder, then "self.files" is larger than
        # the number of samples. The list is thus ending by a series of empty strings that we trim.
        if "" in self.files:
            limit = self.files.index("")
            self.files = self.files[0:limit]

        for i in range(len(self.files)):
            if self.files[i] == "":
                raise InvalidPathException(self.path, "audio clip", "At least one of the files is missing (index " +
                                           str(i) + ").")

        print(str(len(self.files)) + " sample file(s) found.")

    # === Print functions ===
    def print_details(self, include_name=True, include_condition=True, include_frequency=True,
                      include_number_of_samples=True, include_duration=True, add_tabs=0):
        """Prints a series of details about the audio clip.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_name: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`name` to the printed string.
        include_condition: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`condition` to the printed string.
        include_frequency: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`frequency` to the printed string.
        include_number_of_samples: bool, optional
            If set on ``True`` (default), adds the length of the attribute :attr:`samples` to the printed string.
        include_duration: bool, optional
            If set on ``True`` (default), adds the duration of the Sequence to the printed string.
        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.
        """
        t = add_tabs * "\t"

        string = t + "Audio clip · "
        if include_name:
            string += "Name: " + str(self.name) + " · "
        if include_condition:
            string += "Condition: " + str(self.condition) + " · "
        if include_frequency:
            string += "Frequency: " + str(self.frequency) + " Hz · "
        if include_number_of_samples:
            string += "Number of samples: " + str(self.get_number_of_samples()) + " · "
        if include_duration:
            t = self.get_duration()
            string += "Duration: " + str(time_unit_to_timedelta(t)) + " · "
        if len(string) > 3:
            string = string[:-3]

        print(string)

    # == Print functions ==
    def print_subjects_details(self, include_trials=False, include_name=True, include_condition=True,
                               include_date_recording=True, include_number_of_poses=True, include_duration=True,
                               add_tabs=0):
        """Prints details on each Subject instance.

        .. versionadded:: 2.0

        Parameters
        ----------
        include_trials: bool, optional
            If set on `True`, the printed output will contain details from each trial contained in the subject.
        include_name: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`name` to the printed string.
        include_condition: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`condition` to the printed string.
        include_date_recording: bool, optional
            If set on ``True`` (default), adds the attribute :attr:`date_of_recording` to the printed string.
        include_number_of_poses: bool, optional
            If set on ``True`` (default), adds the length of the attribute :attr:`poses` to the printed string.
        include_duration: bool, optional
            If set on ``True`` (default), adds the duration of the Sequence to the printed string.
        add_tabs: int, optional
            Adds the specified amount of tabulations to the verbosity outputs. This parameter may be used by other
            functions to encapsulate the verbosity outputs by indenting them. In a normal use, it shouldn't be set
            by the user.
        """

        t = add_tabs * "\t"
        # Header
        if len(self.subjects) == 1:
            title = t + f"==   Experiment {self.name}, with {len(self.subjects)} subject.   =="
        else:
            title = t + f"==   Experiment {self.name}, with {len(self.subjects)} subjects.   =="
        print(t + "=" * len(title))
        print(title)
        print(t + "=" * len(title) + str("\n"))

        # Subjects
        i = 0
        for subject_name in self.subjects.keys():
            subject = self.subjects[subject_name]
            # print(t + f"Subject {i + 1}/{len(self.subjects)}: {subject_name}")
            subject.print_sequences_details(include_trials, include_name, include_condition, include_date_recording,
                                            include_number_of_poses, include_duration, 1 + add_tabs)
            if i != len(self.subjects) - 1:
                print("")
            i += 1