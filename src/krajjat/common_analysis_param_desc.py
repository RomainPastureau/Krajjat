"""Common function to perform a multimodal analysis of the motion capture and audio signals. This function can
    perform power spectrum, correlation and coherence analyses, at the subject level or the trial level, before
    plotting a graph or a silhouette and returning the results.

    .. versionadded:: 2.0

    This internal function is designed to be called by specific analysis wrappers like `power_spectrum()`,
    `correlation()`, and `coherence()` and is not intended to be called directly.

    Parameters
    ----------

    General parameters
    ~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    experiment_or_dataframe: Experiment, pandas.DataFrame, str or list(any)
        The input data to analyse. This parameter can be:

            • A :class:`Experiment` instance, containing the full dataset to be analysed.
            • A `pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_,
              generally generated from :meth:`Experiment.get_dataframe()`.
            • The path of a file containing a pandas DataFrame, generally generated from
              :class:`Experiment.save_dataframe()`.
            • A list combining any of the above types. In that case, all the dataframes will be merged sequentially.

    analysis : str
        The type of analysis to perform. Must be one of: `"power spectrum"`, `"correlation"`, `"coherence"`.

    method : str
        The method to use for the analysis. The values this parameter accepts depend on the value in ``analysis``:

            • For `"power spectrum"`: ``"fft"`` or ``"welch"``.
            • For `"correlation"`: ``"pingouin"`` (alt: ``"pg"``,  or ``"numpy"``.
            • For `"coherence"`, this parameter is ignored.

    sampling_rate : int|str|float, optional
        Sampling rate of the signals. By default, this value is set on ``"auto"``: in that case, the sampling rate
        is inferred from the dataframes. Otherwise, this value must be equal to the one of the dataframe or the
        experiment object.

    Dataframe filtering
    ~~~~~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    groups : list(str)|str|None, optional
        Restricts the analysis to subjects with the specified groups. This parameter can be:

            • A single group.
            • A list of groups.
            • ``None`` (default): the dataframe will not be filtered by group.

    conditions : list(str)|str|None, optional
        Restricts the analysis to trials with the specified conditions. This parameter can be:

            • A single condition.
            • A list of conditions.
            • ``None`` (default): the dataframe will not be filtered by condition.

    subjects : list(str)|str|None, optional
        Restricts the analysis to the specified subjects. This parameter can be:

            • A single subject.
            • A list of subjects.
            • ``None`` (default): all subjects will be considered.

    trials : dict(str: list(str))|list(str)|str|None, optional
        Restricts the analysis to the specified trials. This parameter can be:

            • A single trial.
            • A list of trials.
            • A dictionary mapping subjects or groups to a list of trials.
            • ``None`` (default): all trials will be considered.

    Targets
    ~~~~~~~
    .. rubric:: Parameters

    sequence_measure : list(str)|str, optional
        The sequence measure(s) from the mocap modalities to include in the analysis (e.g., ``"velocity"``,
        ``"acceleration"``). If experiment_or_dataframe is or contains a dataframe, the specified measures must appear
        in its measure column. When provided as a list, each sequence measure is paired with each audio_measure to
        generate separate entries in both the results and the plot dictionary. By default, the value of this parameter
        is ``"auto"``: the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"mocap"``. This parameter can also take the following values:

            • For the x-coordinate: ``"x"``, ``"x_coord"``, ``"coord_x"``, or ``"x_coordinate"``.
            • For the y-coordinate: ``"y"``, ``"y_coord"``, ``"coord_y"``, or ``"y_coordinate"``.
            • For the z-coordinate: ``"z"``, ``"z_coord"``, ``"coord_z"``, or ``"z_coordinate"``.
            • For all the coordinates: ``"xyz"``, ``"coordinates"``, ``"coord"``, ``"coords"``, or ``"coordinate"``.
            • For the consecutive distances: ``"d"``, ``"distances"``, ``"dist"``, ``"distance"``,  or ``0``.
            • For the consecutive distances on the x-axis: ``"dx"``, ``"distance_x"``, ``"x_distance"``, ``"dist_x"``,
              or ``"x_dist"``.
            • For the consecutive distances on the y-axis: ``"dy"``, ``"distance_y"``, ``"y_distance"``, ``"dist_y"``,
              or ``"y_dist"``.
            • For the consecutive distances on the z-axis: ``"dz"``, ``"distance_z"``, ``"z_distance"``, ``"dist_z"``,
              or ``"z_dist"``.
            • For the velocity: ``"v"``, ``"vel"``, ``"velocity"``, ``"velocities"``, ``"speed"``, or ``1``.
            • For the acceleration: ``"a"``, ``"acc"``, ``"acceleration"``, ``"accelerations"``, or ``2``.
            • For the jerk: ``"j"``, ``"jerk"``, or ``3``.
            • For the snap: ``"s"``, ``"snap"``, ``"joust"`` or ``4``.
            • For the crackle: ``"c"``, ``"crackle"``, or ``5``.
            • For the pop: ``"p"``, ``"pop"``, or ``6``.

    audio_measure : list(str)|str|None, optional
        The audio measure(s) from the audio modality to include in the analysis (e.g., "envelope", "pitch"). If
        experiment_or_dataframe is or contains a dataframe, the specified measures must appear in its measure column.
        When provided as a list, each sequence measure is paired with each sequence_measure to generate separate
        entries in both the results and the plot dictionary. By default, the value of this parameter is ``"auto"``:
        the function will automatically detect the values in the column ``measure`` when the value in
        the column ``modality`` is ``"audio"``. This parameter can also take the following values:

            • ``"audio"``, for the original sample values.
            • ``"envelope"``.
            • ``"pitch"``.
            • ``"f1"``, ``"f2"``, ``"f3"``, ``"f4"``, ``"f5"`` for the values of the corresponding formant.
            • ``"intensity"``.

    target_measure : str|tuple|list, optional
        The reference signal or label to compare against (for `"correlation"` and `"coherence"` analyses only).
        This value can be:

            • A joint label (if only one `sequence_measure` is specified)
            • A tuple containing a sequence measure and a joint label
            • An audio measure
            • A list containing multiple of the above (in that case, each entry must be a string or a tuple).

    series : str|None, optional
        A column name from the dataframe to split data into subsets (e.g., `"group"`, `"condition"`, `"trial"`). Each
        subset will create a new entry in the results and the plot dictionary.

    average : str|None, optional
        Defines the level of averaging:

            • ``"subject"``: average across subjects.
            • ``"trial"``: average across trials.
            • ``None``: no averaging; the full dataset is used.

    Result format
    ~~~~~~~~~~~~~
    .. rubric:: Parameters

    result_type : str, optional
        The type of the results computed and returned by the function. This parameter can be:

            • ``"average"`` (alternatives: ``"raw"``, ``"avg"``, default): in that case, the values plotted and
              returned will be the values computed during the analysis, averaged if ``"average"`` is set.
            • ``"z-scores"` (alternatives: ``"z"``, ``"zscores"``, ``"z-score"``, ``"zscore"``, ``"zeta"``): in that
              case, the values plotted will be the z-scores computed against the randomly permuted values. The
              parameters ``permutation_level`` and ``number_of_randperms`` must be set. Note that the returned Result
              instance will contain both the raw/average results and the z-scores.

    permutation_level : str|None, optional
        This parameter determines how permutations are applied:

            • `"whole"`: permutations are done on the pooled data.
            • `"individual"`: permutations are done separately for each subject or trial (depending on the value of
              ``average``: if ``average`` is set to ``"subject"``, permutations are done separately for each subject,
              while if ``average`` is set to ``"trial"``, permutations are done separately for each trial). This value
              can also be set to the same value as in ``"average"``.
            • ``None`` (default): no permutations are calculated. This value is not allowed if ``return_values ==
              "z-scores"``.

    number_of_randperms: int, optional
        How many random permutations to calculate. Only used if `permutation_level` is set to ``"whole"`` or
        ``"individual"``. An average of the calculated random permutations is then calculated, in order to calculate
        a z-score.

    random_seed : int|None, optional
        Fixes the seed for reproducible random permutations. Default: ``None``: the random permutations will change
        on each execution.

    specific_frequency : float|list(float)|None, optional
        Frequency (or list of frequencies) to extract from the result. If set, silhouette plots are generated. This
        parameter is ignored if ``analysis == "correlation"``.

    freq_atol : float|int, optional
        Absolute tolerance for matching the specific frequency (default: 0.1).

    include_audio : bool, optional
        If ``True``, includes audio signals in the set of labels to analyse.

    Plot parameters
    ~~~~~~~~~~~~~~~
    .. rubric:: Parameters

    color_line_series : list|str|None, optional
        Color(s) to use when plotting time-frequency graphs. If this parameter is a list, a color will be
        attributed to each series. If this parameter is a string, the same color is attributed to all series. Each
        color can take a number of forms:

            • The `HTML/CSS name of a color <https://en.wikipedia.org/wiki/X11_color_names>`_ (e.g. ``"red"`` or
              ``"blanched almond"``),
            • The hexadecimal code of a color, starting with a number sign (``#``, e.g. ``"#ffcc00"`` or ``"#c0ffee"``).
            • The RGB or RGBA tuple of a color (e.g. ``(153, 204, 0)`` or ``(77, 77, 77, 255)``).

    color_line_perm: list|str|None, optional
        Color to use for the permutations when plotting time-frequency graphs. If this parameter is a list, a color
        will be attributed to each series. If this parameter is a string, the same color is attributed to all series.

    title: str|None, optional
        If set, the title of the plot. Otherwise, an automatic title will be generated.

    width_line : int|float
        Width of plotted lines.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: optional
        Additional arguments passed to :func:`plot_functions.plot_silhouette` or
        :func:`plot_functions.plot_body_graphs`.

    Returns
    -------
    Results
        A Results instance containing the analysis parameters and the results as attributes:

            • ``frequencies`` contains the frequencies corresponding to the results, if the analysis is in the
               frequency domain.
            • ``averages`` contains the results of the analysis, averaged across the specified level of averaging.
            • ``stds`` contains the standard deviations of the results.
            • ``averages_perm`` contains the averages of the random permutations, if they were computed.
            • ``stds`` contains the standard deviations of the random permutations.
            • ``z_scores`` contains the z-scores of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``p_values`` contains the p-values of the analysis, if ``return_type`` was set on ``z-scores``.
            • ``plot_dictionary`` contains the plot dictionary that can be directly passed to ``plot_silhouette`` or
              ``plot_body_graphs``.
    """