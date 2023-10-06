.. |br| raw:: html

   <br />

Display functions
=================

Description
-----------
Functions to display and compare sequences graphically.

Shortcuts
---------
While playing a sequence, the following keyboard shortcuts can perform some modifications.

First, the modifier keys A and B allow to modify a sequence independently of the other:

.. list-table:: Modifiers
    :widths: 30 70
    :header-rows: 1

    * - Modifier key
      - Action
    * - .. image:: /icons32/a.png
      - Applies the action to the first sequence only.
    * - .. image:: /icons32/b.png
      - Applies the action to the second sequence only.
    * - .. image:: /icons32/none.png
      - Applies the action to both sequences.

In the following shortcuts, the ones followed by an asterisk (*) can be applied to one of
the sequences only by using a modifier.

.. list-table:: General shortcuts
    :widths: 70 30
    :header-rows: 1

    * - Operation
      - Key or key combination
    * - Pause/Unpause
      - .. image:: /icons32/space.png
    * - Increase the display speed by 0.25
      - .. image:: /icons32/+.png
    * - Decrease the display speed by 0.25
      - .. image:: /icons32/-.png
    * - Next pose (manual or paused only)
      - .. image:: /icons32/right.png
    * - Previous pose (manual or paused only)
      - .. image:: /icons32/left.png
    * - Show/hide corrected joints*
      - .. image:: /icons32/c.png
    * - Assign new random background color*
      - .. image:: /icons32/g.png
    * - Show/hide bottom joints*
      - .. image:: /icons32/i.png
    * - Assign new random default joint color*
      - .. image:: /icons32/j.png
    * - Show/hide lines*
      - .. image:: /icons32/l.png
    * - Show/hide pose index
      - .. image:: /icons32/p.png
    * - Move the animation*
      - .. image:: /icons32/left_click.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/move.png

.. list-table:: Size shortcuts
    :widths: 70 30
    :header-rows: 1

    * - Operation
      - Key or key combination
    * - Zoom in*
      - .. image:: /icons32/scroll_up.png
    * - Zoom out*
      - .. image:: /icons32/scroll_down.png
    * - Increase default joint size*
      - .. image:: /icons32/ctrl.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_up.png
    * - Decrease default joint size*
      - .. image:: /icons32/ctrl.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_down.png
    * - Increase hand joint size*
      - .. image:: /icons32/alt.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_up.png
    * - Decrease hand joint size*
      - .. image:: /icons32/alt.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_down.png
    * - Increase head joint size*
      - .. image:: /icons32/ctrl.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/alt.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_up.png
    * - Decrease head joint size*
      - .. image:: /icons32/ctrl.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/alt.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_down.png
    * - Increase line width*
      - .. image:: /icons32/shift.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_up.png
    * - Decrease line width*
      - .. image:: /icons32/shift.png
        .. image:: /icons32/plus.png
        .. image:: /icons32/scroll_down.png


Functions
---------
.. autofunction:: display_functions.common_displayer
.. autofunction:: display_functions.sequence_reader
.. autofunction:: display_functions.sequence_comparer
.. autofunction:: display_functions.pose_reader
.. autofunction:: display_functions._process_events
.. autofunction:: display_functions.save_video_sequence

.. _keyword_arguments_display_functions:

Keyword arguments
-----------------
The functions :func:`common_displayer`, :func:`sequence_reader`, :func:`sequence_comparer` and :func:`pose_reader` allow
other arguments to be passed as keyword arguments, allowing for complete customisation of the display. These arguments
can be passed as the other arguments, but given their large number, they are not defined in the docstring of the
function; instead, they are defined in the table below.

For example, you can call:

.. code-block::

    >>> sequence = Sequence("C:/Users/Zoidberg/Recording/")
    >>> sequence_reader(sequence, color_joint_default="red", line_width=4)

.. note::

    Most of the following keyword arguments come in three variations: the first refers to both sequences, the second to
    the first sequence, and the last to the second sequence. For example, `shape_joint` sets the shape of the joints for
    both sequences (or the only sequence if only one is displayed), while `shape_joint_seq1` will set the shape of the
    joints for the first sequence, and `shape_joint_seq2` for the second sequence. The keyword arguments coming without
    variations

.. list-table:: Keyword arguments
    :widths: 20 25 40 15
    :header-rows: 1

    * - Keyword
      - Type
      - Description
      - Default value
    * - `ignore_bottom` |br| `ignore_bottom_seq1` |br| `ignore_bottom_seq2`
      - bool
      - Defines if to ignore the joints and lines located in the lower half of the body.
      - ``False``
    * - `show_lines` |br| `show_lines_seq1` |br| `show_lines_seq2`
      - bool
      - If set on ``True``, the graphic sequence will include lines between certain joints, to create a skeleton. If set
        on ``False``, only the joints will be displayed.
      - ``True``
    * - `show_joint_corrected` |br| `show_joint_corrected_seq1` |br| `show_joint_corrected_seq2`
      - bool
      - If set on ``True``, the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        will appear colored by ``color_joint_corrected``.
      - ``True``
    * - `shape_joint` |br| `shape_joint_seq1` |br| `shape_joint_seq2`
      - str
      - The shape that the joints will have: ``"circle"`` (default) or ``"square"``.
      - ``"circle"``
    * - `color_background` |br| `color_background_seq1` |br| `color_background_seq2`
      - tuple(int, int, int, int) |br| tuple(int, int, int) |br| str
      - The background color for the window (if only one sequence is displayed) or for one half of the window
        (if two sequences are displayed).
      - ``"black"``
    * - `color_joint` |br| `color_joint_seq1` |br| `color_joint_seq2` |br| `color_joint_default`
        |br| `color_joint_default_seq1` |br| `color_joint_default_seq2`
      - tuple(int, int, int, int) |br| tuple(int, int, int) |br| str
      - The color of the joints.
      - ``"white"``
    * - `color_joint_corrected` |br| `color_joint_corrected_seq1` |br| `color_joint_corrected_seq2`
      - tuple(int, int, int, int) |br| tuple(int, int, int) |br| str
      - The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`.
      - ``"sheen green"``
    * - `color_line` |br| `color_line_seq1` |br| `color_line_seq2`
      - tuple(int, int, int, int) |br| tuple(int, int, int) |br| str
      - The color of the lines between the joints.
      - ``"grey"``
    * - `width_line` |br| `width_line_seq1` |br| `width_line_seq2`
      - int
      - The width of the lines connecting the joints, in pixels.
      - ``1``
    * - `size_joint_default` |br| `size_joint_default_seq1` |br| `size_joint_default_seq2`
      - int
      - The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the joints not covered by ``size_joint_head`` and ``size_joint_hand``.
      - ``10``
    * - `size_joint_hand` |br| `size_joint_hand_seq1` |br| `size_joint_hand_seq2`
      - int
      - The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft" joints
        (Kualysis).
      - ``20``
    * - `size_joint_head` |br| `size_joint_head_seq1` |br| `size_joint_head_seq2`
      - int
      - The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis).
      - ``50``
    * - `scale_joint` |br| `scale_joint_seq1` |br| `scale_joint_seq2`
      - float
      - Scaling factor for the size of the joints.
      - ``1``
    * - `shift` |br| `shift_seq1` |br| `shift_seq2`
      - tuple(int, int)
      - The number of pixels to shift the display of the joints from the first sequence on the horizontal and vertical
        axes, respectively.
      - ``(0, 0)``
    * - `zoom_level` |br| `zoom_level_seq1` |br| `zoom_level_seq2`
      - float
      - Defines the zoom level compared to the original view. A zoom level of 2 will make the joints appear twice as
        close.
      - ``1``
    * - `speed`
      - float
      - The speed at which to display the sequences.
      - ``1``
    * - `font`
      - str
      - The name of a font present in the system files (e.g. ``"Arial"``). If no font is provided, the embedded font
        ``res/junction_bold.otf`` will be used.
      - N/A
    * - `font_color`
      - tuple(int, int, int, int) |br| tuple(int, int, int) |br| str
      - The color of the font indicating the current pose and time marker.
      - ``"white"``
    * - `show_progress`
      - bool
      - If set on ``True``, shows the current pose and timestamp in the bottom right corner.
      - ``True``