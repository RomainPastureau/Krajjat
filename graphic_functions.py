"""Functions to display and compare sequences graphically."""

from classes.graphic_classes import *
from tool_functions import convert_color_rgba, create_subfolders, resample_images_to_frequency
import shutil
import os
#import cv2
import sys


def common_displayer(sequence1, sequence2=None, path_audio=None, path_video=None, position_sequences="side",
                     position_video="background", resolution=0.5, height_window_in_meters=3.0, full_screen=False,
                     manual=False, ignore_bottom=False, show_lines=True, show_joints_corrected=True, start_pose=0,
                     background_color_seq1="black", shape_joint_seq1="square", color_joint_default_seq1="white",
                     color_joint_corrected_seq1="sheen green", color_line_seq1="grey", width_line_seq1=1,
                     size_joint_default_seq1=10, size_joint_hand_seq1=20, size_joint_head_seq1=50, scale_joint_seq1=1,
                     shift_seq1=(0, 0), background_color_seq2="black", shape_joint_seq2="square",
                     color_joint_default_seq2="white", color_joint_corrected_seq2="sheen green", color_line_seq2="grey",
                     width_line_seq2=1, size_joint_default_seq2=10, size_joint_hand_seq2=20, size_joint_head_seq2=50,
                     scale_joint_seq2=1, shift_seq2=(0, 0), verbosity=1):

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
        The path of an audio file (ending in ``.wav``, ``.mp3`` or ``.ogg``) to read with the Sequence instance(s).

    path_video: str, optional
        The path of a video file (ending in ``.mp4``) to read behind or next to the Sequence instance(s).

    position_sequences: str, optional
        Defines if the sequences should be displayed next to each other (``"side"``, default), or on top of each other
        (``"superimposed"``).

    position_video: str, optional
        Defines if the video should be displayed behind the sequence(s) (``"background"``, default), or next to the
        sequence(s) (``"side"``)

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the Sequence instance(s). This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels.
            • A float, representing the ratio of the total screen width and height (default: 0.5); for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    height_window_in_meters: float, optional
        Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3).

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``, default) or not.

    manual: bool, optional
        If set on ``False`` (default), the poses of the Sequence will be displayed in real time. If set on ``True``,
        the poses will be static, allowing the user to move to the next or previous pose using the right or left arrow
        keys, respectively.

    zoom_level: float, optional
        Defines the zoom level compared to the
        
    ignore_bottom: bool, optional
        Defines if to ignore the joints and lines located in the lower half of the body (default value: ``False``).
        
    show_lines: bool, optional
        If set on ``True`` (default), the graphic sequence will include lines between certain joints, to create a
        skeleton. If set on ``False``, only the joints will be displayed.

    show_joints_corrected: bool, optional
        If set on ``True``, the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        will appear colored by ``color_joint_corrected_seq1`` and ``color_joint_corrected_seq2``. Otherwise, the joints
        will appear colored by their default color (``color_joint_default_seq1`` and ``color_joint_default_seq2``).

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    background_color_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The background color for the window (if only one sequence is displayed) or for the left half of the window
        (if two sequences are displayed). Default value: "black".

    shape_joint_seq1: str, optional
        The shape that the joints from the first sequence will have: "circle" (default) or "square".

    color_joint_default_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints from the first sequence (default: "white").

    color_joint_corrected_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        (default: "sheen green"), from the first sequence.

    color_line_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the lines between the joints from the first sequence (default: "grey").

    width_line_seq1: int, optional
        The width of the lines connecting the joints from the first sequence, in pixels (default: 1).

    size_joint_default_seq1: int, optional
        The radius (if ``shape_joint_seq1`` is set on "circle") or width/height (if ``shape_joint_seq1`` is set on
        "square"), in pixels, of the joints from the first sequence not covered by ``size_joint_head_seq1`` and
        ``size_joint_hand_seq1`` (default: 10).

    size_joint_hand_seq1: int, optional
        The radius (if ``shape_joint_seq1`` is set on "circle") or width/height (if ``shape_joint_seq1`` is set on
        "square"), in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft"
        joints (Kualysis), for the first sequence (default: 20).

    size_joint_head_seq1: int, optional
        The radius (if ``shape_joint_seq1`` is set on "circle") or width/height (if ``shape_joint_seq1`` is set on
        "square"), in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis), for the first sequence
        (default: 50).

    scale_joint_seq1: float, optional
        Scaling factor for the size of the joints (default: 1).

    shift_seq1: tuple(int, int), optional
        The number of pixels to shift the display of the joints from the first sequence on the horizontal and vertical
        axes, respectively (default: (0, 0)).

    background_color_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The background color for the right half of the window, if two sequences are displayed (default: "black").

    shape_joint_seq2: str, optional
        The shape that the joints from the second sequence will have: "circle" (default) or "square".

    color_joint_default_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints from the second sequence (default: "white").

    color_joint_corrected_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        (default: "sheen green"), from the second sequence.

    color_line_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the lines between the joints from the second sequence (default: "grey").

    width_line_seq2: int, optional
        The width of the lines connecting the joints from the second sequence, in pixels (default: 1).

    size_joint_default_seq2: int, optional
        The radius (if ``shape_joint_seq2`` is set on "circle") or width/height (if ``shape_joint_seq2`` is set on
        "square"), in pixels, of the joints from the second sequence not covered by ``size_joint_head_seq2`` and
        ``size_joint_hand_seq2`` (default: 10).

    size_joint_hand_seq2: int, optional
        The radius (if ``shape_joint_seq2`` is set on "circle") or width/height (if ``shape_joint_seq2`` is set on
        "square"), in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft"
        joints (Kualysis), for the second sequence (default: 20).

    size_joint_head_seq2: int, optional
        The radius (if ``shape_joint_seq2`` is set on "circle") or width/height (if ``shape_joint_seq2`` is set on
        "square"), in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis), for the second sequence
        (default: 50).

    scale_joint_seq2: float, optional
        Scaling factor for the size of the joints (default: 1).

    shift_seq2: tuple(int, int), optional
        The number of pixels to shift the display of the joints from the second sequence on the horizontal and vertical
        axes, respectively (default: (0, 0)).
        
    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    pygame.init()

    # Setting up the resolution
    if resolution is None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)
    elif isinstance(resolution, float):
        info = pygame.display.Info()
        resolution = (info.current_w * resolution, info.current_h * resolution)

    # Setting up the full screen mode
    if full_screen:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode(resolution)

    pygame.mouse.set_visible(True)  # Allows the mouse to be visible
    graphic_window = GraphicWindow(window, height_window_in_meters)  # Contains the window and resizing info

    # Generates a graphic sequence from the sequence
    animation1 = GraphicSequence(sequence1, graphic_window, start_pose, shape_joint_seq1, color_joint_default_seq1,
                                 color_joint_corrected_seq1, color_line_seq1, width_line_seq1, size_joint_default_seq1,
                                 size_joint_hand_seq1, size_joint_head_seq1, scale_joint_seq1, ignore_bottom,
                                 show_lines, show_joints_corrected, verbosity)
    animation2 = None
    if sequence2 is not None:
        animation2 = GraphicSequence(sequence1, graphic_window, start_pose, shape_joint_seq2, color_joint_default_seq2,
                                     color_joint_corrected_seq2, color_line_seq2, width_line_seq2,
                                     size_joint_default_seq2, size_joint_hand_seq2, size_joint_head_seq2,
                                     scale_joint_seq2, ignore_bottom, show_lines, show_joints_corrected, verbosity)

    window_right = pygame.Surface((resolution[0]//2, resolution[1]))
    background_color_seq1 = convert_color_rgba(background_color_seq1)
    window_right.fill((convert_color_rgba(background_color_seq2)))

    ctrl_modifier = False
    alt_modifier = False

    if position_sequences == "superimposed":
        horizontal_offset = 0
    else:
        horizontal_offset = graphic_window.center_x // 2

    run = True

    # Program loop
    while run:

        graphic_window.window.fill(background_color_seq1)
        if animation2 is not None:
            graphic_window.window.blit(window_right, (graphic_window.center_x, 0))

        for event in pygame.event.get():

            # Leave the program
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = False
                break

            # Toggle CTRL modifier
            if event.type == KEYDOWN and event.key in [K_LCTRL, K_RCTRL]:
                ctrl_modifier = True
            elif event.type == KEYUP and event.key in [K_LCTRL, K_RCTRL]:
                ctrl_modifier = False

            # Toggle ALT modifier
            if event.type == KEYDOWN and event.key in [K_LALT, K_RALT]:
                alt_modifier = True
            elif event.type == KEYUP and event.key in [K_LALT, K_RALT]:
                alt_modifier = False

            if event.type == MOUSEWHEEL:
                if ctrl_modifier and alt_modifier:
                    if event.y > 0:
                        animation1._set_size_joint_head(animation1.size_joint_head + 5)
                    if event.y < 0:
                        animation1._set_size_joint_head(animation1.size_joint_head - 5)
                elif ctrl_modifier:
                    if event.y > 0:
                        animation1._set_size_joint_default(animation1.size_joint_default + 5)
                    if event.y < 0:
                        animation1._set_size_joint_default(animation1.size_joint_default - 5)
                elif alt_modifier:
                    if event.y > 0:
                        animation1._set_size_joint_hand(animation1.size_joint_hand + 5)
                    if event.y < 0:
                        animation1._set_size_joint_hand(animation1.size_joint_hand - 5)

            if event.type == KEYDOWN and event.key == K_b:
                animation1._toggle_ignore_bottom()
                if sequence2 is not None:
                    animation2._toggle_ignore_bottom()
            elif event.type == KEYDOWN and event.key == K_c:
                animation1._toggle_show_joints_corrected()
                if sequence2 is not None:
                    animation2._toggle_show_joints_corrected()
            elif event.type == KEYDOWN and event.key == K_l:
                if verbosity > 0:
                    print("Toggling show_lines.")
                animation1._toggle_show_lines()
                if sequence2 is not None:
                    animation2._toggle_show_lines()

            if manual:
                if event.type == KEYDOWN and event.key == K_RIGHT:
                    animation1._next_pose()
                    if sequence2 is not None:
                        animation2._next_pose()
                elif event.type == KEYDOWN and event.key == K_LEFT:
                    animation1._previous_pose()
                    if sequence2 is not None:
                        animation2._next_pose()
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    manual = False

            else:
                if event.type == KEYDOWN and event.key == K_SPACE:
                    manual = True
                    animation1._unpause()
                    if sequence2 is not None:
                        animation2._unpause()

        if manual:
            animation1._show_pose(graphic_window, shift_x=shift_seq1[0], shift_y=shift_seq1[0])
        elif sequence2 is None:
            animation1._play(graphic_window, shift_x=shift_seq1[0], shift_y=shift_seq1[0])
        else:
            animation1._play(graphic_window, shift_x=shift_seq1[0]-horizontal_offset, shift_y=shift_seq1[0])
            animation2._play(graphic_window, shift_x=shift_seq2[0]+horizontal_offset, shift_y=shift_seq2[0])

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def sequence_reader(sequence, path_audio=None, path_video=None, position_video="background", resolution=0.5,
                    full_screen=False, ignore_bottom=False, show_lines=True, show_joints_corrected=True, start_pose=0,
                    background_color="black", shape_joint="circle", color_joint_default="white",
                    color_joint_corrected="sheen green", color_line="grey", width_line=1, size_joint_default=10,
                    size_joint_hand=20, size_joint_head=50, scale_joint=1, shift=(0, 0), verbosity=1):
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
        sequence(s) (``"side"``)

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the Sequence instance(s). This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels.
            • A float, representing the ratio of the total screen width and height (default: 0.5); for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``, default) or not.

    ignore_bottom: bool, optional
        Defines if to ignore the joints and lines located in the lower half of the body (default value: ``False``).

    show_lines: bool, optional
        If set on ``True`` (default), the graphic sequence will include lines between certain joints, to create a
        skeleton. If set on ``False``, only the joints will be displayed.

    show_joints_corrected: bool, optional
        If set on ``True``, the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        will appear colored by ``color_joint_corrected_seq1`` and ``color_joint_corrected_seq2``. Otherwise, the joints
        will appear colored by their default color (``color_joint_default_seq1`` and ``color_joint_default_seq2``).

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    background_color: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The background color for the window. Default value: "black".

    shape_joint: str, optional
        The shape that the joints will have: "circle" (default) or "square".

    color_joint_default: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints (default: "white").

    color_joint_corrected: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        (default: "sheen green").

    color_line: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the lines between the joints (default: "grey").

    width_line: int, optional
        The width of the lines connecting the joints, in pixels (default: 1).

    size_joint_default: int, optional
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"), in
        pixels, of the joints not covered by ``size_joint_head`` and ``size_joint_hand`` (default: 10).

    size_joint_hand: int, optional
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"), in
        pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft" joints
        (Kualysis) (default: 20).

    size_joint_head: int, optional
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"), in
        pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis) (default: 50).

    scale_joint: float, optional
        Scaling factor for the size of the joints (default: 1).

    shift: tuple(int, int), optional
        The number of pixels to shift the display of the joints on the horizontal and vertical axes, respectively
        (default: (0, 0)).

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    common_displayer(sequence, path_audio=path_audio, path_video=path_video, position_video=position_video,
                     resolution=resolution, full_screen=full_screen, ignore_bottom=ignore_bottom, show_lines=show_lines,
                     show_joints_corrected=show_joints_corrected, start_pose=start_pose,
                     background_color_seq1=background_color, shape_joint_seq1=shape_joint,
                     color_joint_default_seq1=color_joint_default, color_joint_corrected_seq1=color_joint_corrected,
                     color_line_seq1=color_line, width_line_seq1=width_line, size_joint_default_seq1=size_joint_default,
                     size_joint_hand_seq1=size_joint_hand, size_joint_head_seq1=size_joint_head,
                     scale_joint_seq1=scale_joint, shift_seq1=shift, verbosity=verbosity)


def sequence_comparer(sequence1, sequence2, path_audio=None, path_video=None, position_sequences="side",
                      position_video="background", resolution=0.5, full_screen=False, manual=False,
                      ignore_bottom=False, show_lines=True, show_joints_corrected=True, start_pose=0,
                      background_color_seq1="black", shape_joint_seq1="square", color_joint_default_seq1="white",
                      color_joint_corrected_seq1="sheen green", color_line_seq1="grey", width_line_seq1=1,
                      size_joint_default_seq1=10, size_joint_hand_seq1=20, size_joint_head_seq1=50, scale_joint_seq1=1,
                      shift_seq1=(0, 0), background_color_seq2="black", shape_joint_seq2="square",
                      color_joint_default_seq2="white", color_joint_corrected_seq2="sheen green",
                      color_line_seq2="grey", width_line_seq2=1, size_joint_default_seq2=10, size_joint_hand_seq2=20,
                      size_joint_head_seq2=50, scale_joint_seq2=1, shift_seq2=(0, 0), verbosity=1):
    
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
        (``"superimposed"``).

    position_video: str, optional
        Defines if the video should be displayed behind the sequence(s) (``"background"``, default), or next to the
        sequence(s) (``"side"``)

    resolution: tuple(int, int) or float or None, optional
        The resolution of the Pygame window that will display the Sequence instance(s). This parameter can be:

            • A tuple with two integers, representing the width and height of the window in pixels.
            • A float, representing the ratio of the total screen width and height (default: 0.5); for example, setting
              this parameter on 0.5 on a screen that is 1920 × 1080 pixels will create a window of 960 × 540 pixels.
            • None: in that case, the window will be the size of the screen.

    full_screen: bool, optional
        Defines if the window will be set full screen (``True``, default) or not.

    manual: bool, optional
        If set on ``False`` (default), the poses of the Sequence will be displayed in real time. If set on ``True``,
        the poses will be static, allowing the user to move to the next or previous pose using the right or left arrow
        keys, respectively.

    ignore_bottom: bool, optional
        Defines if to ignore the joints and lines located in the lower half of the body (default value: ``False``).

    show_lines: bool, optional
        If set on ``True`` (default), the graphic sequence will include lines between certain joints, to create a
        skeleton. If set on ``False``, only the joints will be displayed.

    show_joints_corrected: bool, optional
        If set on ``True``, the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        will appear colored by ``color_joint_corrected_seq1`` and ``color_joint_corrected_seq2``. Otherwise, the joints
        will appear colored by their default color (``color_joint_default_seq1`` and ``color_joint_default_seq2``).

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    background_color_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The background color for the window (if only one sequence is displayed) or for the left half of the window
        (if two sequences are displayed). Default value: "black".

    shape_joint_seq1: str, optional
        The shape that the joints from the first sequence will have: "circle" (default) or "square".

    color_joint_default_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints from the first sequence (default: "white").

    color_joint_corrected_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        (default: "sheen green"), from the first sequence.

    color_line_seq1: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the lines between the joints from the first sequence (default: "grey").

    width_line_seq1: int, optional
        The width of the lines connecting the joints from the first sequence, in pixels (default: 1).

    size_joint_default_seq1: int, optional
        The radius (if ``shape_joint_seq1`` is set on "circle") or width/height (if ``shape_joint_seq1`` is set on
        "square"), in pixels, of the joints from the first sequence not covered by ``size_joint_head_seq1`` and
        ``size_joint_hand_seq1`` (default: 10).

    size_joint_hand_seq1: int, optional
        The radius (if ``shape_joint_seq1`` is set on "circle") or width/height (if ``shape_joint_seq1`` is set on
        "square"), in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft"
        joints (Kualysis), for the first sequence (default: 20).

    size_joint_head_seq1: int, optional
        The radius (if ``shape_joint_seq1`` is set on "circle") or width/height (if ``shape_joint_seq1`` is set on
        "square"), in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis), for the first sequence
        (default: 50).

    scale_joint_seq1: float, optional
        Scaling factor for the size of the joints (default: 1).

    shift_seq1: tuple(int, int), optional
        The number of pixels to shift the display of the joints from the first sequence on the horizontal and vertical
        axes, respectively (default: (0, 0)).

    background_color_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The background color for the right half of the window, if two sequences are displayed (default: "black").

    shape_joint_seq2: str, optional
        The shape that the joints from the second sequence will have: "circle" (default) or "square".

    color_joint_default_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints from the second sequence (default: "white").

    color_joint_corrected_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        (default: "sheen green"), from the second sequence.

    color_line_seq2: tuple(int, int, int), tuple(int, int, int, int) or str, optional
        The color of the lines between the joints from the second sequence (default: "grey").

    width_line_seq2: int, optional
        The width of the lines connecting the joints from the second sequence, in pixels (default: 1).

    size_joint_default_seq2: int, optional
        The radius (if ``shape_joint_seq2`` is set on "circle") or width/height (if ``shape_joint_seq2`` is set on
        "square"), in pixels, of the joints from the second sequence not covered by ``size_joint_head_seq2`` and
        ``size_joint_hand_seq2`` (default: 10).

    size_joint_hand_seq2: int, optional
        The radius (if ``shape_joint_seq2`` is set on "circle") or width/height (if ``shape_joint_seq2`` is set on
        "square"), in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft"
        joints (Kualysis), for the second sequence (default: 20).

    size_joint_head_seq2: int, optional
        The radius (if ``shape_joint_seq2`` is set on "circle") or width/height (if ``shape_joint_seq2`` is set on
        "square"), in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis), for the second sequence
        (default: 50).

    scale_joint_seq2: float, optional
        Scaling factor for the size of the joints (default: 1).

    shift_seq2: tuple(int, int), optional
        The number of pixels to shift the display of the joints from the second sequence on the horizontal and vertical
        axes, respectively (default: (0, 0)).

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.
    """

    common_displayer(sequence1, sequence2, path_audio=path_audio, path_video=path_video, 
                     position_sequences=position_sequences, position_video=position_video, resolution=resolution, 
                     full_screen=full_screen, manual=manual, ignore_bottom=ignore_bottom, show_lines=show_lines,
                     show_joints_corrected=show_joints_corrected, start_pose=start_pose,
                     background_color_seq1=background_color_seq1, shape_joint_seq1=shape_joint_seq1,
                     color_joint_default_seq1=color_joint_default_seq1, 
                     color_joint_corrected_seq1=color_joint_corrected_seq1, color_line_seq1=color_line_seq1, 
                     width_line_seq1=width_line_seq1, size_joint_default_seq1=size_joint_default_seq1,
                     size_joint_hand_seq1=size_joint_hand_seq1, size_joint_head_seq1=size_joint_head_seq1,
                     scale_joint_seq1=scale_joint_seq1, shift_seq1=shift_seq1,
                     background_color_seq2=background_color_seq2, shape_joint_seq2=shape_joint_seq2,
                     color_joint_default_seq2=color_joint_default_seq2,
                     color_joint_corrected_seq2=color_joint_corrected_seq2, color_line_seq2=color_line_seq2,
                     width_line_seq2=width_line_seq2, size_joint_default_seq2=size_joint_default_seq2,
                     size_joint_hand_seq2=size_joint_hand_seq2, size_joint_head_seq2=size_joint_head_seq2,
                     scale_joint_seq2=scale_joint_seq2, shift_seq2=shift_seq2, verbosity=verbosity)


def pose_reader(folder_or_sequence, start_pose=0, show_lines=True, show_image=True, ignore_bottom=False,
                resolution=(1600, 900), full_screen=False, path_images=None, type="square", color_joint="default",
                scale=1, shift_x=0, shift_y=0, ratio_joint=1):
    """Reads a sequence and offers a manuel control over the poses (with the arrows of the keyboard)."""

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen, True,
                     show_image, start_pose=start_pose, path_images=path_images, shape_joint=type, color_joint_default=color_joint,
                     scale=scale, shift_x=shift_x, shift_y=shift_y, ratio_joint=ratio_joint)


# def save_skeleton_video(sequence, output_name, frequency=25, show_lines=False, ignore_bottom=True, start_pose=0,
#                         path_images=None, resolution=(950,534), shift_x=0, shift_y=0, full_screen=False, verbose=1):
#
#     # If the resolution is None, we just create a window the size of the screen
#     if resolution is None:
#         info = pygame.display.Info()
#         resolution = (info.current_w, info.current_h)
#
#     # We set to full screen
#     if full_screen:
#         window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
#     else:
#         window = pygame.display.set_mode(resolution)
#
#     disp = GraphicWindow(window)  # Contains the window and resizing info
#     animation = GraphicSequence(sequence, disp, show_lines, ignore_bottom, start_pose, path_images, 1.7)
#
#     print("Generating images...", end=" ")
#
#     # Create the temporary folder
#     tempfolder = "tempfolder_"+(output_name.split("/")[-1]).split(".")[0]
#     if os.path.exists(tempfolder):
#         shutil.rmtree(tempfolder)
#     create_subfolders(tempfolder)
#     images = []
#     perc = 10
#
#     for pose in range(len(animation.poses)):
#
#         if verbose > 1:
#             if pose == 0:
#                 print("")
#             print("\tGenerating image "+str(pose+1)+" of "+str(len(animation.poses))+"...")
#         else:
#             perc = show_progression(verbose, pose, len(animation.poses), perc, step=10)
#
#         window.fill((0, 0, 0))
#         animation._show_pose(window, show_lines, False, shift_x, shift_y, "circle", (255, 255, 255), 1.7)
#         pygame.display.flip()
#         img = tempfolder+"/s"+"{:05d}".format(pose)+".png"
#         images.append(img)
#         pygame.image.save(window, img)
#         animation._next_pose()
#     print("100% - Done.")
#     print("Images generated.")
#     print("Generating video...")
#
#     timestamps = sequence.get_timestamps()
#     #print(timestamps)
#     #print(images)
#
#     new_images, new_timestamps = resample_images_to_frequency(images, timestamps, frequency)
#     #print(new_timestamps)
#     #print(new_images)
#
#     create_subfolders(output_name)
#
#     #images = [img for img in os.listdir("temp_folder") if img.endswith(".png")]
#     frame = cv2.imread(new_images[0])
#     height, width, layers = frame.shape
#
#     video = cv2.VideoWriter(output_name, 0, frequency, (width, height))
#
#     for image in new_images:
#         video.write(cv2.imread(image))
#
#     cv2.destroyAllWindows()
#     video.release()
#
#     print("Video generated.")
#
#     shutil.rmtree(tempfolder)
#
#     print("Temporary folder deleted.")
#
