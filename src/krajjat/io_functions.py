"""Functions to load and save multiple sequences, audio clips, and statistics."""
from krajjat.classes.sequence import Sequence
from krajjat.tool_functions import *
from krajjat.classes.exceptions import *
from krajjat.classes.audio import Audio


# === Loading functions ===
def load_sequences(input_folder, recursive=False, output_type="list", ignore_empty_sequences=True,
                   ignore_loading_errors=False, verbose=1):
    """Loads multiple sequences and returns a list or a dict containing them.

    .. versionadded:: 2.0

    Parameters
    ----------
    input_folder: str
        The absolute path of the directory in which to look for sequences (starting from the root of the drive, e.g.
        ``C:/Users/Desmond/Documents/Recordings``).

    recursive: bool, optional
        If set on ``True``, all the subdirectories of the ``input_folder`` will be analyzed to look for sequences.

    output_type: str, optional
        If set on ``"list"`` (default), the function will return a list of the loaded sequences. If set on ``"dict"``,
        the function will return a dict, in which each key will be the absolute path to the sequence, and the
        corresponding values will be the loaded sequences.

    ignore_empty_sequences: bool, optional
        If set on ``True`` (default), the function will not stop if it tries to load an empty file or folder. If set
        on ``False``, the function will stop at any :class:`EmptySequenceException`.

        .. note::
            If you set ``recursive`` on ``True``, you should also set ``ignore_empty_sequences`` on ``True``: as the
            recursive loading starts from the top, the first sequence this function will try to load is the parent
            folder, which will probably not contain any sequence. The function will then return an
            EmptySequenceException and stop if you set ``ignore_empty_sequences`` on ``False``.

    ignore_loading_errors: bool, optional
        If set on ``True``, the function will not stop if it tries to load a sequence that raises an
        :class:`InvalidPathException` or an :class:`ImpossibleTimeTravelException`. In that case, the sequences
        in question will not be added to the output of the function, and the reason of the error will be printed in the
        console if ``verbose`` is 1 or more. If set on ``False`` (default), any :class:`InvalidPathException` or
        :class:`ImpossibleTimeTravelException` will stop the function.

    verbose: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Returns
    -------
    list or dict
        A list or dict (defined by the parameter ``output_type``) of the loaded sequences. If the output is a dict,
        each key is the absolute path to the sequence, and the corresponding values are the loaded sequences.
    """

    # Read the content of a folder
    content = os.listdir(input_folder)

    # Output type
    if output_type.lower() == "list":
        sequences = []
    elif output_type.lower() == "dict":
        sequences = {}
    else:
        raise Exception('Wrong output type: "' + str(output_type) + '". The output type should be "list" or "dict".')

    # Going through the content
    for element in content:

        # Load sequences
        try:
            if verbose > 0:
                print("\n======= " + input_folder + "/" + element + " =======")
            sequence = Sequence(input_folder + "/" + element, name=element)

            if output_type.lower() == "list":
                sequences.append(sequence)

            elif output_type.lower() == "dict":
                sequences[input_folder + "/" + element] = sequence

        # Exceptions
        except InvalidPathException as ex:
            if ignore_loading_errors and verbose > 0:
                print(ex.message)
            elif not ignore_loading_errors:
                raise InvalidPathException(ex.path, "sequence", ex.reason)
        except ImpossibleTimeTravelException as ex:
            if ignore_loading_errors and verbose > 0:
                print(ex.message)
            elif not ignore_loading_errors:
                raise ImpossibleTimeTravelException(ex.index1, ex.index2, ex.timestamp1,
                                                    ex.timestamp2, ex.number_of_timestamps, ex.object_type)
        except EmptySequenceException as ex:
            if ignore_empty_sequences and verbose > 0:
                print(ex.message)
            elif not ignore_empty_sequences:
                raise EmptySequenceException()

            if recursive:
                if os.path.isdir(input_folder + "/" + element):
                    sequences_subdirectory = load_sequences(input_folder + "/" + element, True, output_type,
                                                            ignore_empty_sequences, ignore_loading_errors, verbose)
                    if output_type.lower() == "list":
                        sequences += sequences_subdirectory
                    elif output_type.lower() == "dict":
                        sequences.update(sequences_subdirectory)

    if verbose > 0:
        print(str(len(sequences)) + " sequence(s) have been loaded from the directory " + str(input_folder))

    return sequences


def load_audios(input_folder, recursive=False, output_type="list", ignore_empty_audios=True,
                ignore_loading_errors=False, verbose=1):
    """Loads multiple audio clips and returns a list or a dict containing them.

    .. versionadded:: 2.0

    Parameters
    ----------
    input_folder: str
        The absolute path of the directory in which to look for audio clips (starting from the root of the drive, e.g.
        ``C:/Users/Greg/Documents/Audio_clips``).

    recursive: bool, optional
        If set on ``True``, all the subdirectories of the ``input_folder`` will be analyzed to look for audio clips.

    output_type: str, optional
        If set on ``"list"`` (default), the function will return a list of the loaded audio clips. If set on ``"dict"``,
        the function will return a dict, in which each key will be the absolute path to the audio clip, and the
        corresponding values will be the loaded audio clip.

    ignore_empty_audios: bool, optional
        If set on ``True`` (default), the function will not stop if it tries to load an empty file or folder. If set
        on ``False``, the function will stop at any :class:`EmptyAudioException`.

        .. note::
            If you set ``recursive`` on ``True``, you should also set ``ignore_empty_audios`` on ``True``: as the
            recursive loading starts from the top, the first sequence this function will try to load is the parent
            folder, which will probably not contain any audio clip. The function will then return an
            EmptyAudioException and stop if you set ``ignore_empty_audios`` on ``False``.

    ignore_loading_errors: bool, optional
        If set on ``True``, the function will not stop if it tries to load an audio clip that raises an
        :class:`InvalidPathException` or a :class:`ImpossibleTimeTravelException`. In that case, the audio clips
        in question will not be added to the output of the function, and the reason of the error will be printed in the
        console if ``verbose`` is 1 or more. If set on ``False`` (default), any :class:`InvalidPathException` or
        :class:`ImpossibleTimeTravelException` will stop the function.

    verbose: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Returns
    -------
    list or dict
        A list or dict (defined by the parameter ``output_type``) of the loaded audio clips. If the output is a dict,
        each key is the absolute path to the audio clip, and the corresponding values are the loaded audio clips.
    """

    content = os.listdir(input_folder)

    # Output type
    if output_type.lower() == "list":
        audios = []
    elif output_type.lower() == "dict":
        audios = {}
    else:
        raise Exception('Wrong output type: "' + str(output_type) + '". The output type should be "list" or "dict".')

    # Going through the content
    for element in content:

        # Load sequences
        try:
            if verbose > 0:
                print("\n======= " + input_folder + "/" + element + " =======")
            audio = Audio(input_folder + "/" + element, name=element)

            if output_type.lower() == "list":
                audios.append(audio)

            elif output_type.lower() == "dict":
                audios[input_folder + "/" + element] = audio

        # Exceptions
        except InvalidPathException as ex:
            if ignore_loading_errors and verbose > 0:
                print(ex.message)
            elif not ignore_loading_errors:
                raise InvalidPathException(ex.path, "audio clip", ex.reason)
        except ImpossibleTimeTravelException as ex:
            if ignore_loading_errors and verbose > 0:
                print(ex.message)
            elif not ignore_loading_errors:
                raise ImpossibleTimeTravelException(ex.index1, ex.index2, ex.timestamp1,
                                                    ex.timestamp2, ex.number_of_timestamps, ex.object_type)
        except EmptyAudioException as ex:
            if ignore_empty_audios and verbose > 0:
                print(ex.message)
            elif not ignore_empty_audios:
                raise EmptyAudioException()

            if recursive:
                if os.path.isdir(input_folder + "/" + element):
                    audios_subdirectory = load_audios(input_folder + "/" + element, True, output_type,
                                                            ignore_empty_audios, ignore_loading_errors, verbose)
                    if output_type.lower() == "list":
                        audios += audios_subdirectory
                    elif output_type.lower() == "dict":
                        audios.update(audios_subdirectory)

    if verbose > 0:
        print(str(len(audios)) + " audio clip(s) have been loaded from the directory " + str(input_folder))

    return audios


def save_sequences(sequence_or_sequences, folder_out="", names=None, file_format="json", individual=False,
                   use_relative_timestamps=True, keep_subdirectory_structure=True, verbose=1):
    """Saves one or multiple Sequence instances on the disk.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence_or_sequences: Sequence or list(Sequence)
        A Sequence instance or a list of Sequence instances.

    folder_out: str, optional
        The path in which to save the sequences. If one or more subfolders of the path do not exist, they will be
        created automatically.

    names: list(str) or None, optional
        The names to give to the saved sequences. If set on None, the attribute :attr:`Sequence.name` will be used
        to name the output file or folder. If a list of names is provided, the list must be the same length as the
        parameter ``sequence_or_sequences``. If ``sequence_or_sequences`` is a single Sequence instance, or is a list
        containing a single Sequence instance, ``names`` can be a string. If you provide a name, do not provide the
        file extension with it: provide the extension in the parameter ``file_format`` instead.

    file_format: str, optional
        The file format in which to save the sequences. The file format must be ``"json"`` (default), ``"xlsx"``,
        ``"txt"``, ``"csv"``, ``"tsv"``, or, if you are a masochist, ``"mat"``. Notes:

            • ``"xls"`` will save the files with an ``.xlsx`` extension.
            • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
            • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
              on ``,``. By default, the function will detect which separator the system uses.
            • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
            • Any other string will not return an error, but rather be used as a custom extension. The data will
              be saved as in a text file (using tabulations as values separators).

        .. warning::
            While it is possible to save sequences as ``.mat`` or custom extensions, the toolbox will not recognize
            these files upon opening. The support for ``.mat`` and custom extensions as input may come in a future
            release, but for now these are just offered as output options.

    individual: bool, optional
        If set on ``False`` (default), the function will save each sequence in a unique file.
        If set on ``True``, the function will save each pose of the sequences in an individual file, appending an
        underscore and the index of the pose (starting at 0) after the name.

    use_relative_timestamps: bool, optional
        Defines if the timestamps that will be saved are absolute (``False``) or relative to the first pose (``True``).

    keep_subdirectory_structure: bool, optional
        If set on ``True``, sequences in distinct subfolders will remain separated according to the same structure in
        the output directory. For example, if two sequences have for original paths
        ``C:/Recordings/Subject_01/March_14/recording.json`` and ``C:/Recordings/Subject_02/May_04/recording.json``,
        and the ``folder_out`` provided is ``D:/Resampled/``, the recordings will be saved as
        ``D:/Resampled/Subject_01/March_14/recording.json`` and ``D:/Resampled/Subject_02/May_04/recording.json``.

    verbose: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
        """

    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]

    if names is not None:
        if type(names) is str:
            names = [names]
        if len(names) != len(sequence_or_sequences):
            raise Exception("The number of names (" + str(len(names)) + ") is not the same as the number of " +
                            "sequences provided (" + str(len(sequence_or_sequences)) + ").")

    # Handling file format
    file_format = file_format.strip(".")  # We remove the dot in the format
    if file_format == "xls":
        file_format = "xlsx"

    common_path = ""
    if keep_subdirectory_structure:
        common_path = find_common_parent_path(get_objects_paths(sequence_or_sequences))

    for s in range(len(sequence_or_sequences)):
        if keep_subdirectory_structure:
            path_out = folder_out + "/" + compute_subpath(common_path, sequence_or_sequences[s].get_path()) + "/"
        else:
            path_out = folder_out

        if verbose > 0:
            print("Saving sequence " + str(s) + "/" + str(len(sequence_or_sequences)))

        if names is None:
            sequence_or_sequences[s].save(path_out, None, file_format, individual, use_relative_timestamps, verbose)
        else:
            sequence_or_sequences[s].save(path_out, str(names[s]), file_format, individual, use_relative_timestamps,
                                          verbose)

    if verbose > 0:
        if len(sequence_or_sequences) == 1:
            print("1 sequence saved.")
        else:
            print(str(len(sequence_or_sequences)) + " sequences saved.")


def save_audios(audio_or_audios, folder_out="", names=None, file_format="json", individual=False,
                keep_subdirectory_structure=True, verbose=1):
    """Saves one or multiple Audio instances on the disk.

    .. versionadded:: 2.0

    Parameters
    ----------
    audio_or_audios: Audio or list(Audio)
        An Audio instance or a list of Audio instances.

    folder_out: str, optional
        The path in which to save the audio clips. If one or more subfolders of the path do not exist, they will be
        created automatically.

    names: list(str), str or None, optional
        The names to give to the saved audio clips. If set on None, the attribute :attr:`Audio.name` will be used
        to name the output file or folder. If a list of names is provided, the list must be the same length as the
        parameter ``audio_or_audios``. If ``audio_or_audios`` is a single Audio instance, or is a list containing a
        single Audio instance, ``names`` can be a string. If you provide a name, do not provide the file extension
        with it: provide the extension in the parameter ``file_format`` instead.

    file_format: str, optional
        The file format in which to save the sequences. The file format must be ``"json"`` (default), ``"xlsx"``,
        ``"txt"``, ``"csv"``, ``"tsv"``, ``"wav"``, or, if you are a masochist, ``"mat"``. Notes:

            • ``"xls"`` will save the files with an ``.xlsx`` extension.
            • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
            • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
              on ``,``. By default, the function will detect which separator the system uses.
            • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
            • ``"wav"`` files can be opened with any compatible software; that being said, wav files that have been
              heavily downsampled may sound unintelligible.
            • Any other string will not return an error, but rather be used as a custom extension. The data will
              be saved as in a text file (using tabulations as values separators).

        .. warning::
            While it is possible to save audio clips as ``.mat`` or custom extensions, the toolbox will not recognize
            these files upon opening. The support for ``.mat`` and custom extensions as input may come in a future
            release, but for now these are just offered as output options.

    individual: bool, optional
        If set on ``False`` (default), the function will save each audio clip in a unique file.
        If set on ``True``, the function will save each sample of each audio clip in an individual file, appending an
        underscore and the index of the pose (starting at 0) after the name.

        .. note::
            This incredibly tedious way of opening and saving audio files has only been implemented to follow the same
            logic as for the Sequence files, and should be avoided.

    keep_subdirectory_structure: bool, optional
        If set on ``True``, audio clips in distinct subfolders will remain separated according to the same structure in
        the output directory. For example, if two audio clips have for original paths
        ``C:/Recordings/Subject_01/April_27/recording.wav`` and ``C:/Recordings/Subject_02/October_21/recording.wav``,
        and the ``folder_out`` provided is ``D:/Resampled/``, the recordings will be saved as
        ``D:/Resampled/Subject_01/April_27/recording.wav`` and ``D:/Resampled/Subject_02/October_21/recording.wav``.

    verbose: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
        """

    if type(audio_or_audios) is Audio:
        audio_or_audios = [audio_or_audios]

    if names is not None:
        if type(names) is str:
            names = [names]
        if len(names) != len(audio_or_audios):
            raise Exception("The number of names (" + str(len(names)) + ") is not the same as the number of " +
                            "audio clips provided (" + str(len(audio_or_audios)) + ").")

    # Handling file format
    file_format = file_format.strip(".")  # We remove the dot in the format
    if file_format == "xls":
        file_format = "xlsx"

    common_path = ""
    if keep_subdirectory_structure:
        common_path = find_common_parent_path(get_objects_paths(audio_or_audios))

    for s in range(len(audio_or_audios)):
        if keep_subdirectory_structure:
            path_out = folder_out + "/" + compute_subpath(common_path, audio_or_audios[s].get_path()) + "/"
        else:
            path_out = folder_out

        if verbose > 0:
            print("Saving audio clip " + str(s) + "/" + str(len(audio_or_audios)))

        if names is None:
            audio_or_audios[s].save(path_out, None, file_format, individual, verbose)
        else:
            audio_or_audios[s].save(path_out, str(names[s]), file_format, individual, verbose)

    if verbose > 0:
        if len(audio_or_audios) == 1:
            print("1 audio clip saved.")
        else:
            print(str(len(audio_or_audios)) + " audio clips saved.")


def save_stats(sequence_or_sequences, folder_out="", name="stats", file_format="json", individual=False,
               keys_to_exclude=None, keys_to_include=None, verbose=1):
    """Saves the statistics of one or multiple sequences on the disk.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence_or_sequences: Sequence or list(Sequence)
        A Sequence instance or a list of Sequence instances.

    folder_out: str, optional
        The path in which to save the stats. If one or more subfolders of the path do not exist, they will be
        created automatically. If the string provided is empty (by default), the stats will be saved in
        the current working directory. If the string provided contains a file with an extension, the fields ``name``
        and ``file_format`` will be ignored.

    name: str, optional
        Defines the name of the file where to save the stats. By default, it is set on ``"stats"``. If ``individual``
        is set on ``True``, the :attr:`classes.sequence.Sequence.name` will be appended to the name defined in this
        function for each file.

    file_format: str, optional
        The file format in which to save the stats. The file format must be ``"json"`` (default), ``"xlsx"``,
        ``"txt"``, ``"csv"``, ``"tsv"``, or, if you are a masochist, ``"mat"``. Notes:

            • ``"xls"`` will save the files with an ``.xlsx`` extension.
            • Any string starting with a dot will be accepted (e.g. ``".csv"`` instead of ``"csv"``).
            • ``"csv;"`` will force the value separator on ``;``, while ``"csv,"`` will force the separator
              on ``,``. By default, the function will detect which separator the system uses.
            • ``"txt"`` and ``"tsv"`` both separate the values by a tabulation.
            • Any other string will not return an error, but rather be used as a custom extension. The data will
              be saved as in a text file (using tabulations as values separators).

    individual: bool, optional
        If set on ``False`` (default), the function will save the stats of all the sequences in the same file, with one
        entry/row per sequence.
        If set on ``True``, the function will save the stats of each sequence individually, by appending the attribute
        :attr:`classes.sequence.Sequence.name` of each sequence to the parameter ``name`` of this function. If the
        attribute :attr:`classes.sequence.Sequence.name` of a Sequence is set on ``None``, a number will be appended
        instead.

    keys_to_exclude: list(str) or None, optional
        A list of the stats that you do not wish to save. Each string must be a valid entry among the keys saved by the
        function :meth:`classes.sequence.Sequence.get_stats`. If set on ``None``, all the stats will be saved, unless
        some keys are specified in ``keys_to_include``.

    keys_to_include: list(str) or None, optional
        A list of the stats that you wish to save. Each string must be a valid entry among the keys saved by the
        function :meth:`classes.sequence.Sequence.get_stats`. If set on ``None``, all the stats will be saved, unless
        some keys are specified in ``keys_to_exclude``. If at least one key is entered, all the absent keys will not be
        saved. This parameter will only be considered if ``keys_to_exclude`` is None.

    verbose: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    # Automatic creation of all the folders of the path if they don't exist
    os.makedirs("/".join(folder_out.split("/")[:-1]), exist_ok=True)

    # Open the sequence or sequences
    if type(sequence_or_sequences) is Sequence:
        sequence_or_sequences = [sequence_or_sequences]

    if folder_out == "":
        folder_out = os.getcwd()
    if folder_out[-1] != "/":
        folder_out.append("/")

    if not individual:
        subfolders = folder_out.split("/")
        if len(subfolders) != 0:
            if "." in subfolders[-1]:
                folder_out = "/".join(subfolders[:-1])
                name = ".".join(subfolders[-1].split(".")[:-1])
                file_format = subfolders[-1].split(".")[-1]

    # Handling file format
    file_format = file_format.strip(".")  # We remove the dot in the format
    if file_format == "xls":
        file_format = "xlsx"

    if not individual:

        path_out = str(folder_out) + str(name) + "." + str(file_format)

        if verbose > 0:
            print("Saving stat file for " + str(len(sequence_or_sequences)) + " sequences under " + str(path_out) +
                  "...")

        global_stats = {}
        i = 1
        for sequence in sequence_or_sequences:
            stats = sequence.get_stats()
            if keys_to_exclude is not None:
                for key in keys_to_exclude:
                    del stats[key]

            if keys_to_exclude is None and keys_to_include is not None:
                selected_stats = {}
                for key in keys_to_include:
                    selected_stats[key] = stats[key]
                stats = selected_stats

            if sequence.name is None:
                global_stats[i] = stats
                i += 1
            else:
                global_stats[sequence.name] = stats

        if file_format in ["json", "mat"]:

            if file_format == "json":
                with open(path_out, 'w', encoding="utf-16-le") as f:
                    json.dump(global_stats, f)

            elif file_format == "mat":
                try:
                    import scipy
                except ImportError:
                    raise ModuleNotFoundException("scipy", "save a file in .mat format.")
                scipy.io.savemat(path_out, {"data": global_stats})

        else:

            table = []
            for seq in global_stats:
                row = [seq]
                if len(table) == 0:
                    title = ["Sequence"]
                    for key in global_stats[seq].keys():
                        title.append(key)
                    table.append(title)
                for key in global_stats[seq].keys():
                    row.append(global_stats[seq][key])
                table.append(row)

            if file_format == "xlsx":
                write_xlsx(global_stats, path_out, verbose)

            else:
                # Force comma or semicolon separator
                if file_format == "csv,":
                    separator = ","
                    folder_out = folder_out[:-1]
                elif file_format == "csv;":
                    separator = ";"
                    folder_out = folder_out[:-1]
                elif file_format[0:3] == "csv":  # Get the separator from local user (to get , or ;)
                    separator = get_system_csv_separator()
                elif file_format in ["txt", "tsv"]:  # For text files, tab separator
                    separator = "\t"
                else:
                    separator = "\t"

                write_text_table(global_stats, separator, folder_out, 0)

    else:

        i = 1
        for sequence in sequence_or_sequences:
            if sequence.name is None:
                name_sequence = i
                i += 1
            else:
                name_sequence = sequence.name
            sequence.save_stats(folder_out + "/", name_sequence, file_format, keys_to_exclude, keys_to_include, verbose)
