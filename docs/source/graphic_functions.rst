.. |br| raw:: html

   <br />

Graphic functions
=================

Description
-----------
Functions to display and compare sequences graphically.

Shortcuts
---------
While playing a sequence, the following keyboard shortcuts can perform some modifications

+-------------------------------+-----------------------------------------------------------------+
| Operation                     | Key or key combination                                          |
+===============================+=================================================================+
| Pause/Unpause                 | .. image:: /icons32/space.png                                   |
+-------------------------------+-----------------------------------------------------------------+
| Show/hide lines               | .. image:: /icons32/l.png                                       |
+-------------------------------+-----------------------------------------------------------------+
| Show/hide bottom joints       | .. image:: /icons32/b.png                                       |
+-------------------------------+-----------------------------------------------------------------+
| Show/hide corrected joints    | .. image:: /icons32/c.png                                       |
+-------------------------------+-----------------------------------------------------------------+
| Show/hide pose index          | .. image:: /icons32/p.png                                       |
+-------------------------------+-----------------------------------------------------------------+

Functions
---------
.. autofunction:: graphic_functions.common_displayer
.. autofunction:: graphic_functions.sequence_reader
.. autofunction:: graphic_functions.sequence_comparer
.. autofunction:: graphic_functions.pose_reader

.. _keyword_arguments:

Keyword arguments
-----------------
The functions :func:`common_displayer`, :func:`sequence_reader`, :func:`sequence_comparer` and :func:`pose_reader` allow
other arguments to be passed as keyword arguments, allowing for complete customisation of the display. These arguments
must be passed as a dictionary, with one of the keys specified below and the value being of the proper type.

For example, you can call:

.. code-block::

    >>> sequence = Sequence("C:/Users/Zoidberg/Recording/")
    >>> sequence_reader(sequence, **kwargs={"color_joint_default": "red", "line_width": 4})

.. list-table:: Keyword arguments
    :widths: 20 25 40 15
    :header-rows: 1

    * - Keyword
      - Type
      - Description
      - Default value
    * - `background_color` |br| `background_color_seq1`
      - tuple(int, int, int, int) |br| tuple(int, int, int) |br| str
      - The background color for the window (if only one sequence is displayed) or for the left half of the window
        (if two sequences are displayed).
      - ``"black"``
    * - `background_color_seq2`
      - tuple(int, int, int, int) |br| tuple(int, int, int) |br| str
      - The background color for the right half of the window, if two sequences are displayed.
      - ``"black"``
