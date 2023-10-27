"""Functions to display and compare sequences graphically."""

from classes.graphic_classes import *
from tool_functions import *
import shutil
import os
import sys
import pyaudio
import wave


def common_displayer(sequence1, sequence2=None, path_audio=None, path_video=None, position_sequences="side",
                     position_video="superimposed", resolution=0.5, height_window_in_meters=3.0, full_screen=False,
                     manual=False, start_pose=0, verbosity=1, **kwargs):
    """Common displayer function wrapped in all the other graphic functions. Allows to display one or two sequences,
    in a Pygame window, in a highly customizable way. A sequence can be displayed jointly with an audio file or a
    video file.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence1: Sequence
        A Sequence instance.

    sequence2: Sequence, optional
        A second, optional Sequence instance that can be displayed superimposed or next to the previous one, for
        comparison purposes.

    path_audio: str, optional
        The path of an audio file (``.wav`` format) to read with the Sequence instance(s).

    path_video: str, optional
        The path of a video file (ending in ``.mp4``) to read behind or next to the Sequence instance(s).

        .. note::
            The audio from the video will not be read. If you wish to hear audio, provide a .wav file in the parameter
            ``path_audio``.

    position_sequences: str, optional
        Defines if the sequences should be displayed next to each other (``"side"``, default), or on top of each other
        (``"superimposed"``).  This parameter is ignored if only one sequence is provided.

    position_video: str, optional
        Defines if the video should be displayed behind the sequence(s) (``"superimposed"``, default), or next to the
        sequence(s) (``"side"``)  This parameter is ignored if no video is provided.

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the Sequence instance(s). This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels.
            • A float, representing the ratio of the total screen width and height; for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
              Note: if a video is provided and set on the side of the sequence, or if two sequences are provided,
              side by side, the horizontal resolution will be set to be twice the size. A parameter of 0.5 on a screen
              that is 1920 × 1080 pixels will, in that case, create a window of 1920 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    height_window_in_meters: float, optional
        Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3.0).

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``) or not (``False``, default).

    manual: bool, optional
        If set on ``False`` (default), the poses of the Sequence will be displayed in real time. If set on ``True``,
        the poses will be static, allowing the user to move to the next or previous pose using the right or left arrow
        keys, respectively.

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict, optional
        A dictionary of optional arguments. See :ref:`keyword_arguments_display_functions`.
    """

    pygame.init()

    # Setting up the resolution
    info = pygame.display.Info()
    if resolution is None:
        resolution = (info.current_w, info.current_h)
    elif isinstance(resolution, float):
        if (position_sequences == "side" and sequence2 is not None) or \
                (position_video == "side" and path_video is not None):
            resolution = (int(info.current_w * resolution * 2), int(info.current_h * resolution))
        else:
            resolution = (int(info.current_w * resolution), int(info.current_h * resolution))

    if verbosity > 0:
        print("Window resolution: " + str(resolution))

    # Setting up the full screen mode
    if full_screen:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode(resolution)

    window_areas_elements = [["sequence1"], []]
    window_area_sequences = {"sequence1": 0}

    if sequence2 is not None:
        if position_sequences == "superimposed":
            window_areas_elements[0].append("sequence2")
            window_area_sequences["sequence2"] = 0
        elif position_sequences == "side":
            window_areas_elements[1].append("sequence2")
            window_area_sequences["sequence2"] = 1
    if path_video is not None:
        if position_video == "superimposed":
            window_areas_elements[0].append("video")
            if sequence2 is not None and position_sequences == "side":
                window_areas_elements[1].append("video")
        elif position_video == "side":
            window_areas_elements[1].append("video")

    if len(window_areas_elements[1]) == 0:
        window_areas = [WindowArea(resolution, (0, 0), window_areas_elements[0], height_window_in_meters)]
    else:
        window_areas = [WindowArea((resolution[0] // 2, resolution[1]), (0, 0), window_areas_elements[0],
                                   height_window_in_meters),
                        WindowArea((resolution[0] // 2, resolution[1]), (resolution[0] // 2, 0),
                                   window_areas_elements[1], height_window_in_meters)]

    # Generates a graphic sequence from the sequence
    animation1 = GraphicSequence(sequence1, window_areas[0], start_pose, verbosity,
                                 **kwargs_parser(kwargs, "_seq1"))
    animation2 = None
    if sequence2 is not None:
        if window_areas[0].contains("sequence2"):
            animation2 = GraphicSequence(sequence2, window_areas[0], start_pose, verbosity,
                                         **kwargs_parser(kwargs, "_seq2"))
        else:
            animation2 = GraphicSequence(sequence2, window_areas[1], start_pose, verbosity,
                                         **kwargs_parser(kwargs, "_seq2"))

    pygame.mouse.set_visible(True)
    pygame.key.set_repeat(500, 100)

    move_animation = None
    modifiers = {K_LCTRL: False, K_RCTRL: False, K_LALT: False, K_RALT: False, K_LSHIFT: False, K_RSHIFT: False,
                 K_a: False, K_b: False}
    steps = load_steps_gui()

    # Load the video
    video = None
    if path_video is not None:
        video = Video(path_video, window_areas[0].get_resolution())

    if window_areas[0].contains("video"):
        animation1.set_color_background("transparent")
    if len(window_areas) > 1:
        if window_areas[1].contains("video") and animation2 is not None:
            animation2.set_color_background("transparent")

    # Load the audio
    audio = None
    wavefile = None
    if path_audio is None and sequence1.path_audio is not None:
        path_audio = sequence1.path_audio
    if path_audio is not None:
        wavefile = wave.open(path_audio, "rb")
        p = pyaudio.PyAudio()
        audio = p.open(format=p.get_format_from_width(wavefile.getsampwidth()), channels=wavefile.getnchannels(),
                       rate=wavefile.getframerate(), output=True)

    timer = Timer(kwargs.get("speed", 1.0))
    if manual:
        timer.pause()
    last_recorded_second = 0
    last_recorded_pose = 0
    show_progress = kwargs.get("show_progress", True)
    if "font" in kwargs.keys():
        font = pygame.font.SysFont(kwargs.get("font"), int(resolution[1] * 0.04), True)
    else:
        font = pygame.font.Font("res/junction_bold.otf", int(resolution[1] * 0.04))
    font_color = kwargs.get("font_color", "white")
    progress_pose_text = str(animation1.get_current_pose_index() + 1) + "/" + \
                         str(animation1.sequence.get_number_of_poses())
    progress_time_text = format_time(timer.get_timer(), "ms", "mm:ss") + "/" + \
                         format_time(animation1.get_duration(), "ms", "mm:ss")
    progress_pose_surface = font.render(progress_pose_text, True, font_color)
    progress_time_surface = font.render(progress_time_text, True, font_color)

    run = True

    # Program loop
    while run:

        for i in range(len(window_areas)):
            window_areas[i].blit_background_surface()

        if audio is not None:
            chunk = int(timer.get_last_tick() * (wavefile.getframerate() / 1000))
            data = wavefile.readframes(chunk)
            audio.write(data)

        if video is not None:
            for i in range(len(window_areas)):
                if window_areas[i].contains("video"):
                    video.show(window_areas[i], timer)

        events = pygame.event.get()

        for event in events:

            # Leave the program
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = False

            # Toggle modifier keys
            for key in modifiers.keys():
                if event.type == KEYDOWN:
                    if event.key == key:
                        modifiers[key] = True
                if event.type == KEYUP:
                    if event.key == key:
                        modifiers[key] = False

            for i in range(len(window_areas)):
                if window_areas[i].contains("sequence1"):
                    manual, move_animation = _process_events(animation1, window_areas[i], K_a, K_b, 1, manual, event,
                                                             modifiers, steps, move_animation, verbosity)
                if window_areas[i].contains("sequence2"):
                    manual, move_animation = _process_events(animation2, window_areas[i], K_b, K_a, 2, manual, event,
                                                             modifiers, steps, move_animation, verbosity)

            # Speed
            if event.type == KEYDOWN and event.key == K_KP_PLUS:
                timer.set_speed(timer.speed + float(steps["speed"]))
                if verbosity > 0:
                    print("Speed: " + str(timer.speed))
            elif event.type == KEYDOWN and event.key == K_KP_MINUS:
                timer.set_speed(timer.speed - float(steps["speed"]))
                if verbosity > 0:
                    print("Speed: " + str(timer.speed))

            # Show the current pose
            if event.type == KEYDOWN and event.key == K_p:
                show_progress = not show_progress

            # Changing frames
            if manual:
                if event.type == KEYDOWN and event.key == K_RIGHT:
                    animation1.next_pose(timer, verbosity)
                    timer.set_timer(animation1.get_timestamp())
                    last_recorded_second = -1
                elif event.type == KEYDOWN and event.key == K_LEFT:
                    animation1.previous_pose(timer, verbosity)
                    timer.set_timer(animation1.get_timestamp())
                    last_recorded_second = -1

            # Pause
            if event.type == KEYDOWN and event.key == K_SPACE:
                if manual:
                    manual = False
                    timer.unpause()
                    if verbosity > 0:
                        print("Animation un-paused.")
                else:
                    manual = True
                    timer.pause()
                    if verbosity > 0:
                        print("Animations paused.")

        if manual:
            for i in range(len(window_areas)):
                if window_areas[i].contains("sequence1"):
                    animation1.show_pose(window_areas[i])
                if window_areas[i].contains("sequence2"):
                    animation2.show_pose(window_areas[i])
        else:
            for i in range(len(window_areas)):
                if window_areas[i].contains("sequence1"):
                    animation1.play(window_areas[i], timer)
                if window_areas[i].contains("sequence2"):
                    animation2.play(window_areas[i], timer)

        for i in range(len(window_areas)):
            window_areas[i].show(window)

        if show_progress:
            if animation1.current_pose_index != last_recorded_pose or \
                    timer.get_last_full_second() != last_recorded_second:
                progress_pose_text = str(animation1.get_current_pose_index() + 1) + "/" + \
                                     str(animation1.get_number_of_poses())
                progress_time_text = format_time(timer.timer, "ms", "mm:ss") + "/" + \
                                     format_time(animation1.get_duration(), "ms", "mm:ss")
                progress_pose_surface = font.render(progress_pose_text, True, font_color)
                progress_time_surface = font.render(progress_time_text, True, font_color)
            window.blit(progress_pose_surface, (window.get_width() - progress_pose_surface.get_width(),
                                                window.get_height() - progress_pose_surface.get_height() -
                                                progress_time_surface.get_height()))
            window.blit(progress_time_surface, (window.get_width() - progress_time_surface.get_width(),
                                                window.get_height() - progress_pose_surface.get_height()))

        if timer.update_marker:
            animation1.set_pose_from_timestamp(timer.timer, verbosity)
            if animation2 is not None:
                animation2.set_pose_from_timestamp(timer.timer, verbosity)
            if video is not None:
                video.set_frame_from_timestamp(timer.timer, verbosity)
            if audio is not None:
                try:
                    wavefile.setpos(int(timer.timer / 1000 * wavefile.getframerate()))
                except wave.Error:
                    pass
            timer.end_update()

        if verbosity > 1:
            if timer.get_last_full_second() != last_recorded_second:
                if animation1.current_pose_index != 0:
                    ratio = str(round(video.get_current_frame_index() / animation1.get_current_pose_index(), 3))
                elif video.current_frame_index == 0:
                    ratio = "0"
                else:
                    ratio = "∞"
                print("Time:",
                      str(int(timer.timer // 60000)).zfill(2) + ":" + str(int(timer.timer // 1000) % 60).zfill(2) +
                      "." + str(int(timer.timer % 1000)).zfill(3),
                      "Pose: " + str(animation1.get_current_pose_index()),
                      "Frame: " + str(video.get_current_frame_index()),
                      "Ratio: " + ratio,
                      "Difference: " + str(int(video.get_timestamp() - animation1.get_timestamp())) + " ms.\n")

        if timer.get_last_full_second() != last_recorded_second:
            last_recorded_second = timer.get_last_full_second()
        if animation1.current_pose_index != last_recorded_pose:
            last_recorded_pose = animation1.get_current_pose_index()

        timer.update()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def sequence_reader(sequence, path_audio=None, path_video=None, position_video="superimposed", resolution=0.5,
                    height_window_in_meters=3.0, full_screen=False, start_pose=0, verbosity=1, **kwargs):
    """Displays the joints of the sequence in real time and loops back to the beginning when over.

    .. versionadded: 2.0

    Note
    ----
    This function is a wrapper for the function :func:`common_displayer`.

    Parameters
    ----------
    sequence: Sequence
        A Sequence instance.

    path_audio: str, optional
        The path of an audio file (ending in ``.wav``, ``.mp3`` or ``.ogg``) to read with the Sequence instance(s).

    path_video: str, optional
        The path of a video file (ending in ``.mp4``) to read behind or next to the Sequence instance(s).

    position_video: str, optional
        Defines if the video should be displayed behind the sequence(s) (``"background"``, default), or next to the
        sequence(s) (``"side"``). This parameter is ignored if no video is provided.

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the Sequence instance(s). This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels.
            • A float, representing the ratio of the total screen width and height; for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
              Note: if a video is provided and set on the side of the sequence, or if two sequences are provided,
              side by side, the horizontal resolution will be set to be twice the size. A parameter of 0.5 on a screen
              that is 1920 × 1080 pixels will, in that case, create a window of 1920 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    height_window_in_meters: float, optional
        Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3.0).

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``) or not (``False``, default).

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict, optional
        A dictionary of optional arguments. See :ref:`keyword_arguments_display_functions`.
    """

    common_displayer(sequence, path_audio=path_audio, path_video=path_video, position_video=position_video,
                     resolution=resolution, height_window_in_meters=height_window_in_meters, full_screen=full_screen,
                     start_pose=start_pose, verbosity=verbosity, **kwargs)


def sequence_comparer(sequence1, sequence2, path_audio=None, path_video=None, position_sequences="side",
                      resolution=0.5, height_window_in_meters=3.0, full_screen=False, manual=False, start_pose=0,
                      verbosity=1, **kwargs):
    """Compares two sequences side by side or on top of each other.

    .. versionadded:: 2.0

    Note
    ----
    This function is a wrapper for the function :func:`common_displayer`.

    Parameters
    ----------
    sequence1: Sequence
        A first Sequence instance.

    sequence2: Sequence
        A second Sequence instance.

    path_audio: str, optional
        The path of an audio file (ending in ``.wav``, ``.mp3`` or ``.ogg``) to read with the Sequence instance(s).

    path_video: str, optional
        The path of a video file (ending in ``.mp4``) to read behind or next to the Sequence instance(s).

    position_sequences: str, optional
        Defines if the sequences should be displayed next to each other (``"side"``, default), or on top of each other
        (``"superimposed"``). This parameter is ignored if only one sequence is provided.

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the Sequence instance(s). This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels.
            • A float, representing the ratio of the total screen width and height; for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
              Note: if a video is provided and set on the side of the sequence, or if two sequences are provided,
              side by side, the horizontal resolution will be set to be twice the size. A parameter of 0.5 on a screen
              that is 1920 × 1080 pixels will, in that case, create a window of 1920 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    height_window_in_meters: float, optional
        Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3.0).

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``) or not (``False``, default).

    manual: bool, optional
        If set on ``False`` (default), the poses of the Sequence will be displayed in real time. If set on ``True``,
        the poses will be static, allowing the user to move to the next or previous pose using the right or left arrow
        keys, respectively.

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict, optional
        A dictionary of optional arguments. See :ref:`keyword_arguments_display_functions`.
    """

    common_displayer(sequence1, sequence2, path_audio=path_audio, path_video=path_video,
                     position_sequences=position_sequences, position_video="superimposed", resolution=resolution,
                     height_window_in_meters=height_window_in_meters, full_screen=full_screen, manual=manual,
                     start_pose=start_pose, verbosity=verbosity, **kwargs)


def pose_reader(sequence, start_pose=0, resolution=0.5, height_window_in_meters=3.0, full_screen=False, verbosity=1,
                **kwargs):
    """Reads a sequence and offers a manuel control over the poses, with the arrows of the keyboard.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence: Sequence
        A Sequence instance.

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the Sequence instance(s). This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels.
            • A float, representing the ratio of the total screen width and height; for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
              Note: if a video is provided and set on the side of the sequence, or if two sequences are provided,
              side by side, the horizontal resolution will be set to be twice the size. A parameter of 0.5 on a screen
              that is 1920 × 1080 pixels will, in that case, create a window of 1920 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    height_window_in_meters: float, optional
        Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3.0).

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``) or not (``False``, default).

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict, optional
        A dictionary of optional arguments. See :ref:`keyword_arguments_display_functions`.
    """

    common_displayer(sequence, start_pose=start_pose, resolution=resolution,
                     height_window_in_meters=height_window_in_meters, full_screen=full_screen, manual=True,
                     verbosity=verbosity, **kwargs)


def _process_events(animation, window_area, modif_this, modif_other, seq_num, manual, event, modifiers, steps,
                    move_animation, verbosity=1):
    """For one animation, gets the user input and modifies the attributes of the animation accordingly.

    .. versionadded:: 2.0

    Parameters
    ----------
    animation: GraphicSequence
        An instance of a GraphicSequence

    window_area: WindowArea
        The WindowArea instance the mouse currently is in.

    modif_this: int
        The Pygame integer code of a keyboard modifier key for this sequence (K_A for the first sequence, K_B for the
        second).

    modif_other: int
        The Pygame integer code of a keyboard modifier key for the other sequence (K_B for the first sequence,
        K_A for the second).

    seq_num: int
        The number of the animation (1 or 2).

    manual: bool
        The value of the variable ``manual`` from the function :func:`common_displayer`.

    event: `Pygame.event <https://www.pygame.org/docs/ref/event.html>`_)
        A Pygame event.

    modifiers: dict(int: bool)
        A dictionary containing the current state of the modifier keys (pressed or not).

    steps: dict(str: float)
        A dictionary containing the incrementing steps for each parameter.

    move_animation: dict or None
        An dictionary containing the starting position of the animation and the starting position of the mouse when a
        movement of the animation was initiated by the mouse, or None if no movement was initiated.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Returns
    -------
    manual: bool
        The variable ``manual`` from the function :func:`common_displayer`, that was passed as parameter.
    """

    if move_animation is not None:
        if "start_pos_anim" + str(seq_num) not in move_animation.keys():
            move_animation["start_pos_anim" + str(seq_num)] = (animation.shift_x, animation.shift_y)

    if modifiers[modif_this] or not (modifiers[modif_this] or modifiers[modif_other]):

        if event.type == MOUSEWHEEL:

            # size_joint_head
            if (modifiers[K_LCTRL] or modifiers[K_RCTRL]) and (modifiers[K_LALT] or modifiers[K_RALT]):
                if event.y > 0:
                    animation.set_size_joint_head(animation.size_joint_head + int(steps["size_joint_head"]))
                elif event.y < 0 and animation.size_joint_head > steps["size_joint_head"]:
                    animation.set_size_joint_head(animation.size_joint_head - int(steps["size_joint_head"]))
                if verbosity > 0 and event.y != 0:
                    print("Head joint size (sequence " + str(seq_num) + "): " + str(animation.size_joint_head))

            # size_joint_default
            elif modifiers[K_LCTRL] or modifiers[K_RCTRL]:
                if event.y > 0:
                    animation.set_size_joint_default(animation.size_joint_default + int(steps["size_joint_default"]))
                elif event.y < 0 and animation.size_joint_default > steps["size_joint_default"]:
                    animation.set_size_joint_default(animation.size_joint_default - int(steps["size_joint_default"]))
                if verbosity > 0 and event.y != 0:
                    print("Default joint size (sequence " + str(seq_num) + "): " + str(animation.size_joint_default))

            # size_joint_hand
            elif modifiers[K_LALT] or modifiers[K_RALT]:
                if event.y > 0:
                    animation.set_size_joint_hand(animation.size_joint_hand + int(steps["size_joint_hand"]))
                elif event.y < 0 and animation.size_joint_hand > steps["size_joint_hand"]:
                    animation.set_size_joint_hand(animation.size_joint_hand - int(steps["size_joint_hand"]))
                if verbosity > 0 and event.y != 0:
                    print("Hand joint size (sequence " + str(seq_num) + "): " + str(animation.size_joint_hand))

            # width_line
            elif modifiers[K_LSHIFT] or modifiers[K_RSHIFT]:
                if event.y > 0:
                    animation.set_width_line(animation.width_line + int(steps["width_line"]))
                elif event.y < 0 and animation.width_line > steps["width_line"]:
                    animation.set_width_line(animation.width_line - int(steps["width_line"]))
                if verbosity > 0 and event.y != 0:
                    print("Line width (sequence " + str(seq_num) + "): " + str(animation.width_line))

            else:
                if event.y > 0:
                    animation.set_zoom_level(animation.zoom_level + float(steps["zoom_level"]), window_area,
                                             pygame.mouse.get_pos())
                elif event.y < 0 and animation.width_line > steps["zoom_level"]:
                    animation.set_zoom_level(animation.zoom_level - float(steps["zoom_level"]), window_area,
                                             pygame.mouse.get_pos())
                if verbosity > 0 and event.y != 0:
                    print("Zoom level (sequence " + str(seq_num) + "): " + str(animation.zoom_level))

        elif event.type == KEYDOWN:

            # show_joints_corrected
            if event.key == K_c:
                animation.toggle_show_joints_corrected()
                if verbosity > 0:
                    print("Show joints corrected (sequence " + str(seq_num) + "): " +
                          str(animation.show_joints_corrected))

            # color_background
            elif event.key == K_g:
                animation.set_color_background(generate_random_color())
                if verbosity > 0:
                    print("Randomly changing background color (sequence " + str(seq_num) + "): " +
                          str(animation.color_background))

            # ignore_bottom
            elif event.key == K_i:
                animation.toggle_ignore_bottom()
                if verbosity > 0:
                    print("Ignore bottom (sequence " + str(seq_num) + "): " + str(animation.ignore_bottom))

            # color_joint
            elif event.key == K_j:
                animation.set_color_joint_default(generate_random_color())
                if verbosity > 0:
                    print("Randomly changing default joint color (sequence " + str(seq_num) + "): " +
                          str(animation.color_joint_default))

            # show_lines
            elif event.key == K_l:
                animation.toggle_show_lines()
                if verbosity > 0:
                    print("Show lines (sequence " + str(seq_num) + "): " + str(animation.show_lines))

            # Take a screenshot
            elif event.key == K_s:
                now = datetime.datetime.now()
                name = "screenshot_" + str(now) + ".png"
                cwd = os.getcwd()
                pygame.image.save(window_area.window_area, cwd + "/" + name)
                print("Screenshot saved as " + str(cwd) + "/" + name)

            elif modifiers[K_LSHIFT] or modifiers[K_RSHIFT]:
                if event.key == K_RIGHT:
                    animation.set_shift_x(animation.shift_x + steps["shift_x"])
                elif event.key == K_LEFT:
                    animation.set_shift_x(animation.shift_x - steps["shift_x"])
                elif event.key == K_DOWN:
                    animation.set_shift_y(animation.shift_y + steps["shift_y"])
                elif event.key == K_UP:
                    animation.set_shift_y(animation.shift_y - steps["shift_y"])
                if verbosity > 0 and event.key in [K_RIGHT, K_LEFT, K_DOWN, K_UP]:
                    print("Shift (sequence " + str(seq_num) + "): (" + str(animation.shift_x) + ", "
                          + str(animation.shift_y) + ")")

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            move_animation = {"start_pos_anim" + str(seq_num): (animation.shift_x, animation.shift_y),
                              "start_pos_mouse": pygame.mouse.get_pos()}

        elif event.type == MOUSEBUTTONUP and event.button == 1:
            move_animation = None
            if verbosity > 0:
                print("New starting position (sequence " + str(seq_num) + "): (" + str(animation.shift_x) + ", "
                      + str(animation.shift_y) + ")")

        elif event.type == MOUSEMOTION and move_animation is not None:
            animation.set_shift_x(move_animation["start_pos_anim" + str(seq_num)][0] -
                                  (move_animation["start_pos_mouse"][0] - pygame.mouse.get_pos()[0]))
            animation.set_shift_y(move_animation["start_pos_anim" + str(seq_num)][1] -
                                  (move_animation["start_pos_mouse"][1] - pygame.mouse.get_pos()[1]))

    return manual, move_animation


def save_video_sequence(sequence1, path_output, fps=25, sequence2=None, path_audio=None, path_video=None,
                        position_sequences="side", position_video="superimposed", resolution=(1920, 1080),
                        height_window_in_meters=3.0, frame_selection="lower", image_type="PNG", quality=5, verbosity=1,
                        **kwargs):
    """Creates a video from a sequence and saves it on the disk. The function generates images using Pygame, following
    all the arguments in parameters. Each image is then saved in a temporary folder. Using ffmpeg, a video is
    created, using the mpeg4 encoding.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence1: Sequence
        A Sequence instance.

    path_output: str
        The full path to the video file where to save the video, including the extension of the file (e.g.
        ``"C:/Recordings/Leorio/Session7/video_003.mp4"``.

        .. warning::
            Using ffmpeg, theoretically all output formats are supported; however, the output file generation was
            only tested with ``.mp4`` files. Compatibility with other formats is not guaranteed.

    fps: int, optional
        The number of frames per second in the output video. For each frame, the pose with the closest timestamp
        will be displayed.

    sequence2: Sequence, optional
        A second, optional Sequence instance that can be displayed superimposed or next to the previous one, for
        comparison purposes.

    path_audio: str, optional
        The path of an audio file (ending in .wav) to add to the video. If not provided, the video will be silent. If
        the audio is longer than the video, the part of the audio longer than the video will be cut.

    path_video: str, optional
        The path of a video file to add as a background to the skeleton.

    position_sequences: str, optional
        Defines if the sequences should be displayed next to each other (``"side"``, default), or on top of each other
        (``"superimposed"``). This parameter is ignored if only one sequence is provided.

    position_video: str, optional
        Defines if the video should be displayed behind the sequence(s) (``"superimposed"``, default), or next to the
        sequence(s) (``"side"``)  This parameter is ignored if no video is provided.

    resolution: tuple(int, int) or float or None, optional
        The resolution of the output video. This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels
              (default: (1920, 1080))
            • A float, representing the ratio of the total screen width and height; for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
              Note: if a video is provided and set on the side of the sequence, or if two sequences are provided,
              side by side, the horizontal resolution will be set to be twice the size. A parameter of 0.5 on a screen
              that is 1920 × 1080 pixels will, in that case, create a window of 1920 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    height_window_in_meters: float, optional
        Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3.0).

    frame_selection: str, optional
        Defines which pose or frame is selected based on the timestamp.

            • If set on ``"closest"`` (default), the closest frame/pose from the timestamp is used.
            • If set on ``"below"``, ``"lower"`` or ``"under"``, the closest frame/pose below the timestamp is used.
            • If set on ``"above"``, ``"higher"`` or ``"over"``, the closest frame/pose above the timestamp is used.

    image_type: str, optional
        Defines the image type for the video codec. This parameter can be set on "PNG" (default), or "JPEG". PNG format
        has a better quality than JPEG, but will result in a larger file size for the video.

    quality: int, optional
        The quality of the mpeg4 encoding for the video. The value should be between 1 and 31 (default: 5); a lower
        number induces a better quality, but a larger file size. For more details,
        `see FFmpeg resources <https://trac.ffmpeg.org/wiki/Encode/MPEG-4>`_.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict, optional
        A dictionary of optional arguments. See :ref:`keyword_arguments_display_functions`.
    """

    from subprocess import Popen, PIPE

    pygame.init()

    # Setting up the resolution
    if resolution is None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)
    elif isinstance(resolution, float):
        info = pygame.display.Info()
        if (position_sequences == "side" and sequence2 is not None) or \
                (position_video == "side" and path_video is not None):
            resolution = (int(info.current_w * resolution * 2), int(info.current_h * resolution))
        else:
            resolution = (int(info.current_w * resolution), int(info.current_h * resolution))

    if verbosity > 0:
        print("Window resolution: " + str(resolution))

    pygame.display.set_mode((1, 1))
    window = pygame.Surface(resolution)

    window_areas_elements = [["sequence1"], []]
    window_area_sequences = {"sequence1": 0}

    if sequence2 is not None:
        if position_sequences == "superimposed":
            window_areas_elements[0].append("sequence2")
            window_area_sequences["sequence2"] = 0
        elif position_sequences == "side":
            window_areas_elements[1].append("sequence2")
            window_area_sequences["sequence2"] = 1
    if path_video is not None:
        if position_video == "superimposed":
            window_areas_elements[0].append("video")
            if sequence2 is not None and position_sequences == "side":
                window_areas_elements[1].append("video")
        elif position_video == "side":
            window_areas_elements[1].append("video")

    if len(window_areas_elements[1]) == 0:
        window_areas = [WindowArea(resolution, (0, 0), window_areas_elements[0], height_window_in_meters)]
    else:
        window_areas = [WindowArea((resolution[0] // 2, resolution[1]), (0, 0), window_areas_elements[0],
                                   height_window_in_meters),
                        WindowArea((resolution[0] // 2, resolution[1]), (resolution[0] // 2, 0),
                                   window_areas_elements[1], height_window_in_meters)]

    # Generates a graphic sequence from the sequence
    animation1 = GraphicSequence(sequence1, window_areas[0], 0, verbosity,
                                 **kwargs_parser(kwargs, "_seq1"))
    animation2 = None
    if sequence2 is not None:
        if window_areas[0].contains("sequence2"):
            animation2 = GraphicSequence(sequence2, window_areas[0], 0, verbosity,
                                         **kwargs_parser(kwargs, "_seq2"))
        else:
            animation2 = GraphicSequence(sequence2, window_areas[1], 0, verbosity,
                                         **kwargs_parser(kwargs, "_seq2"))

    directory_output = "/".join(path_output.split("/")[:-1])
    create_subfolders(directory_output, verbosity)

    # Load the video
    video = None
    if path_video is not None:
        video = Video(path_video, window_areas[0].get_resolution())

    if window_areas[0].contains("video"):
        animation1.set_color_background("transparent")
    if len(window_areas) > 1:
        if window_areas[1].contains("video") and animation2 is not None:
            animation2.set_color_background("transparent")

    # Create the temporary folder
    tempfolder = "tempfolder_" + (path_output.split("/")[-1]).split(".")[0]
    if os.path.exists(tempfolder):
        print("A tempfolder has been found on path: " + str(tempfolder))
        user_input = input("Delete this tempfolder? y/n: ")
        if user_input.lower() == "y":
            shutil.rmtree(tempfolder)
        else:
            print("Function save_video_sequence aborted. Please change path_output parameter or delete the tempfolder.")
            return

    time = 0
    perc = 10
    total_number_of_frames = int(animation1.get_duration()//1000 * fps + 1)

    if verbosity > 0:
        print("Generating a video: ")
        print("\tDuration: " + str(format_time(animation1.get_duration(), "ms", "hh:mm:ss.ms")))
        print("\tFrames per second: " + str(fps))
        print("\tTotal number of frames: " + str(total_number_of_frames))

    image_type = image_type.upper()

    if image_type == "JPEG":
        codec = 'mjpeg'
    elif image_type == "PNG":
        codec = 'png'
    else:
        raise Exception('Wrong value for the parameter image_type: " + str(image_type) + ". Should be "JPEG" or "PNG".')

    if path_audio is None:
        p = Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-vcodec', codec, '-r',
                   str(fps), '-i', '-', '-vcodec', 'mpeg4', '-q:v', str(quality), '-r', str(fps), path_output],
                  stdin=PIPE)
    else:
        wavefile = wave.open(path_audio, "rb")
        duration_audio = wavefile.getsampwidth()/wavefile.getframerate()
        if duration_audio < animation1.get_duration():
            p = Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-vcodec', codec, '-r',
                       str(fps), '-i', '-', '-i', path_audio, '-vcodec', 'mpeg4', '-q:v', str(quality), '-r', str(fps),
                       path_output], stdin=PIPE)
        else:
            p = Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-vcodec', codec, '-r',
                       str(fps), '-i', '-', '-i', path_audio, '-vcodec', 'mpeg4', '-q:v', str(quality), '-r', str(fps),
                       '-shortest', path_output], stdin=PIPE)

    while time <= animation1.get_duration() / 1000:

        if verbosity > 1:
            if time == 0:
                print("")
            print("\tGenerating image " + str(int(fps * time) + 1) + " of " + str(total_number_of_frames) + "...",
                  end="\t")
            print("Time: " + str(format_time(time, "ms", "hh:mm:ss.ms")) + "/" +
                  str(format_time(animation1.get_duration(), "ms", "hh:mm:ss.ms")), end="\t")
        else:
            perc = show_progression(verbosity, fps * time, total_number_of_frames, perc, step=10)

        for i in range(len(window_areas)):
            window_areas[i].blit_background_surface()

        if video is not None:
            video.set_frame_from_timestamp(time*1000, frame_selection)
            if verbosity > 1:
                print("Frame video: " + str(video.get_current_frame_index() + 1) + "/" +
                      str(video.get_number_of_frames()), end="\t")
            for i in range(len(window_areas)):
                if window_areas[i].contains("video"):
                    video.show_frame(window_areas[i])

        animation1.set_pose_from_timestamp(time*1000, frame_selection)
        if verbosity > 1:
            print("Pose sequence1: " + str(animation1.get_current_pose_index() + 1) + "/" +
                  str(animation1.get_number_of_poses()), end="\t")
        if animation2 is not None:
            animation2.set_pose_from_timestamp(time*1000, frame_selection)
            if verbosity > 1:
                print("Pose sequence1: " + str(animation2.get_current_pose_index() + 1) + "/" +
                      str(animation2.get_number_of_poses()), end="\t")

        for i in range(len(window_areas)):
            if window_areas[i].contains("sequence1"):
                animation1.show_pose(window_areas[i])
            if window_areas[i].contains("sequence2"):
                animation2.show_pose(window_areas[i])

        for i in range(len(window_areas)):
            window_areas[i].show(window)

        pygame.display.flip()

        time += 1 / fps

        pygame.image.save(window, p.stdin, image_type.upper())

        if verbosity > 1:
            print("")

    p.stdin.close()
    p.wait()

    print("100% - Done.")
