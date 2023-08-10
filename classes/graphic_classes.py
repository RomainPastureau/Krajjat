"""These classes allow to convert the data from :class:`Sequence`, :class:`Pose` and :class:`Joint` to display them
in the :doc:`graphic_functions`. All these classes and their methods should be considered private."""
import pygame
from pygame.locals import *
from pygame import gfxdraw

from tool_functions import convert_color_rgba, load_joint_labels, load_joints_connections, show_progression


class GraphicWindow(object):
    """Defines the size of the display window and allows to convert and scale the coordinates of the joints to be
    displayed.

    .. versionadded:: 2.0

    Parameters
    ----------
    window: pygame.Surface
        The main pygame Surface containing all the graphic elements.

    height_window_in_meters: int or float (optional)
        Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3).

    Attributes
    ----------
    window: pygame.Surface
        The main pygame Surface containing all the graphic elements, set during the initialisation.

    width: int
        The width of the ``window``, in pixels.

    height: int
        The height of the ``window``, in pixels.

    center_x: int
        The mid-point on the x-axis of the ``window``, in pixels.

    center_y: int
        The mid-point on the y-axis of the ``window``, in pixels.

    height_window_in_meters: float
        Defines the distance, in meters, represented by the vertical number of pixels of the window.

    pixel_meter_scale: float
        The real-life distance a pixel represents, in meters. For example, if the window is 1000 pixels vertically,
        and the parameter ``height_window_in_meters`` is set on 1, each pixel will be equivalent to a square of 1 mm ×
        1 mm.
    """

    def __init__(self, window, height_window_in_meters=3.0):
        self.window = window
        self.width = window.get_width()
        self.height = window.get_height()
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.height_window_in_meters = height_window_in_meters
        self.pixel_meter_scale = self.height / height_window_in_meters

    def _convert_x(self, x, scale=1.0):
        """Converts the x "real" coordinate to a graphical coordinate to be displayed in the window.

        .. versionadded:: 2.0

        Parameters
        ----------
        x: float
            The value on the x-axis of a coordinate.
        scale: float, optional
            The scale at which to convert the coordinate. A bigger scale will zoom in on the axis.

        Returns
        -------
        int
            The coordinate of the pixel on the x-axis of the window.
        """
        return int(self.center_x - x * self.pixel_meter_scale * scale)

    def _convert_y(self, y, scale=1.0):
        """Converts the y "real" coordinate to a graphical coordinate to be displayed in the window.

        .. versionadded:: 2.0

        Parameters
        ----------
        y: float
            The value on the y-axis of a coordinate.
        scale: float, optional
            The scale at which to convert the coordinate. A bigger scale will zoom in on the axis.

        Returns
        -------
        int
            The coordinate of the pixel on the y-axis of the window.
        """
        return int(self.center_y - y * self.pixel_meter_scale * scale)

    def _set_height_window_in_meters(self, height_window_in_meters):
        """Sets the attribute :attr:`height_window_in_meters`.

        .. versionadded:: 2.0

        Parameters
        ----------
        height_window_in_meters: float
            Defines the distance, in meters, represented by the vertical number of pixels of the window (by default: 3).
        """
        self.height_window_in_meters = height_window_in_meters
        self.pixel_meter_scale = self.height / height_window_in_meters


class Timer(object):
    """Creates and sets a timer.

    .. versionadded:: 2.0

    Attributes
    ----------
    clock: pygame.time.Clock
        A Pygame clock object.

    timer: float
        A timer, in milliseconds.
    """

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.timer = 0

    def _get_timer(self):
        """Returns the value of the attribute :attr:`timer`.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The time contained in the attribute :attr:`timer`, in milliseconds.
        """
        return self.timer

    def _set_timer(self, t):
        """Sets the timer at a specific value.

        .. versionadded:: 2.0

        Parameters
        ----------
        t: float
            The value, in milliseconds, to set the timer on.
        """
        self.timer = t

    def _reset(self):
        """Resets the timer to 0.

        .. versionadded:: 2.0
        """
        self.timer = 0

    def _update(self, speed=1):
        """Adds the tick of the `pygame.time.Clock <https://www.pygame.org/docs/ref/time.html#pygame.time.Clock>`_
        object to the timer.

        .. versionadded:: 2.0

        Parameters
        ----------
        speed: int, optional
            A factor that multiplies the tick of the clock (default: 1). A value of 2 would make the timer go twice
            as fast.
        """
        self.timer += self.clock.tick() * speed


class GraphicSequence(object):
    """Graphical counterpart to the class :class:`Sequence`. This class allows to convert the original coordinates of
    the joints into graphical coordinates.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence: Sequence
        A Sequence instance.

    graphic_window: GraphicWindow
        The window object, where to display the sequence.

    start_pose: int, optional
        The index of the pose at which to start the sequence.

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
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the joints not covered by ``size_joint_head`` and ``size_joint_hand`` (default: 10).

    size_joint_hand: int, optional
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft" joints
        (Kualysis) (default: 20).

    size_joint_head: int, optional
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis) (default: 50).

    scale_joint: float, optional
        Scaling factor for the size of the joints (default: 1).

    ignore_bottom: bool, optional
        Defines if to ignore the joints and lines located in the lower half of the body (default value: ``False``).

    show_lines: bool, optional
        If set on `True` (default), the graphic sequence will include lines between certain joints, to create a
        skeleton. If set on `False`, only the joints will be displayed.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Attributes
    ----------
    sequence: Sequence
        The Sequence instance, passed as parameter upon initialisation.

    current_pose: int
        The index of the pose currently being in display. It is initialised with the value from the parameter
        ``start_pose``.

    poses: list(_GraphicPose)
        List of all the :class:`_GraphicPose` objects counterparts of the :class:`Pose` objects.

    timer: Timer
        A :class:`Timer` object.

    shape_joint: str
        The shape that the joints will have: "circle" (default) or "square". Can be modified via
        :meth:`_GraphicSequence._shape_joint`.

    color_joint_default: tuple(int, int, int, int)
        The color of the joints (default: "white"). Can be modified via
        :meth:`_GraphicSequence._set_color_joint_default`.

    color_joint_corrected: tuple(int, int, int, int)
        The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
        (default: "green"). Can be modified via :meth:`_GraphicSequence._set_color_joint_corrected`.

    color_line: tuple(int, int, int, int)
        The color of the lines between the joints (default: "grey"). Can be modified via
        :meth:`_GraphicSequence._set_color_line`.

    width_line: int
        The width of the lines connecting the joints, in pixels (default: 1). Can be modified via
        :meth:`_GraphicSequence._set_width_line`.

    size_joint_default: int
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the joints not covered by ``size_joint_head`` and ``size_joint_hand`` (default: 10).
        Can be modified via :meth:`_GraphicSequence._set_size_joint_default`.

    size_joint_hand: int
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft" joints
        (Kualysis) (default: 20). Can be modified via :meth:`_GraphicSequence._set_size_joint_hand`.

    size_joint_head: int
        The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
        in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis) (default: 50).
        Can be modified via :meth:`_GraphicSequence._set_size_joint_head`.

    scale_joint: float
        Scaling factor for the size of the joints (default: 1). Can be modified via :meth:`_GraphicSequence._set_scale`.

    joints_to_show: list(str)
        A list of joint labels to be displayed.

    joint_labels_top: list(str)
        A list of the joints from the top of the body, loaded from ``res/kinect_joint_labels_top.txt`` or
        ``res/kualisys_joint_labels_top.txt``.

    joint_labels_all: list(str)
        A list of all the joints from the body, concatenating the list from :attr:`joint_labels_top` to the list
        contained in either ``res/kinect_joint_labels_bottom.txt`` or
        ``res/kualisys_joint_labels_top.txt``.

    connections_to_show: list(list(str, str))
        A list of the connections that will be displayed as lines between joints.

    connections_top: list(list(str, str))
        A list of the connections from the top of the body, loaded from ``res/kinect_skeleton_connections_top.txt`` or
        ``res/kualisys_skeleton_connections_top.txt``.

    connections_all: list(list(str, str))
        A list of all the connections from the body, concatenating the list from :attr:`connections_top` to the list
        contained in either ``res/kinect_skeleton_connections_bottom.txt`` or
        ``res/kualisys_skeleton_connections_bottom.txt``.

    ignore_bottom: bool
        Defines if to ignore the joints and lines located in the lower half of the body (default value: ``False``). Can
        be modified via :meth:`_GraphicSequence._set_ignore_bottom`.

    show_lines: bool
        Defines if to show the lines connecting the joints (default: ``True``). Can be modified via
        :meth:`_GraphicSequence._set_show_lines`.

    joint_surfaces: dict(str: `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_)
        A dictionary containing the different `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_ objects
        representing single joints.
    """

    def __init__(self, sequence, graphic_window, start_pose=0, shape_joint="circle", color_joint_default="white",
                 color_joint_corrected="sheen green", color_line="grey", width_line=1, size_joint_default=10,
                 size_joint_hand=20, size_joint_head=50, scale_joint=1, ignore_bottom=False, show_lines=True,
                 show_joints_corrected=True, verbosity=1):

        self.sequence = sequence
        self.current_pose = start_pose
        self.poses = []

        self._load_joint_labels()
        self._load_connections()

        self._set_ignore_bottom(ignore_bottom)
        self._load_poses(graphic_window, verbosity)
        self._set_show_lines(show_lines)

        self.joint_surfaces = {}
        self.shape_joint = shape_joint
        self.color_joint_default = convert_color_rgba(color_joint_default)
        self.color_joint_corrected = convert_color_rgba(color_joint_corrected)
        self.color_line = convert_color_rgba(color_line)
        self.width_line = width_line
        self.size_joint_head = size_joint_head
        self.size_joint_hand = size_joint_hand
        self.size_joint_default = size_joint_default
        self.scale_joint = scale_joint
        self._set_show_joints_corrected(show_joints_corrected)
        self._generate_all_joint_surfaces()

        self.timer = Timer()
        self._reset()

    def _load_poses(self, graphic_window, verbosity=1):
        """Converts a :class:`Sequence` into a :class:`_GraphicSequence` and add them to the :attr:`poses`
        attribute.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            The window object, where to display the sequence.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """

        if verbosity > 0:
            print("Creating the graphic poses...")

        # Show percentage
        perc = 10

        # Loads the poses and images
        for p in range(len(self.sequence.poses)):
            if verbosity == 1:
                perc = show_progression(verbosity, p, len(self.sequence.poses), perc)
            elif verbosity > 1:
                print("\tLoading pose " + str(p+1) + " of " + str(len(self.sequence.poses)) + "...")
            self.poses.append(GraphicPose(self.sequence.poses[p], graphic_window, verbosity))

        if verbosity > 0:
            print("100% - Done.")

    def _load_joint_labels(self):
        """Loads two lists of joint labels, :attr:`joint_labels_top` and :attr:`joint_labels_all`, defining which joints
        will be displayed depending if the attribute :attr:`ignore_bottom` is set on ``True`` or ``False``. The joint
        labels list are loaded from ``res/kinect_joint_labels_top.txt`` and ``res/kinect_joint_labels_bottom.txt`` or
        ``res/kualisys_joint_labels_top.txt`` and ``res/kualisys_joint_labels_bottom.txt``.

        .. versionadded:: 2.0
        """
        self.joint_labels_top = []
        self.joint_labels_all = []

        joints = self.sequence.get_joint_labels()

        if "Head" in joints:
            self.joint_labels_top = load_joint_labels("kinect_joint_labels_top.txt")
            self.joint_labels_all = load_joint_labels("kinect_joint_labels_top.txt")
            self.joint_labels_all += load_joint_labels("kinect_joint_labels_bottom.txt")
        elif "HeadTop" in joints:
            self.joint_labels_top = load_joint_labels("kualisys_joint_labels_top.txt")
            self.joint_labels_all = load_joint_labels("kualisys_joint_labels_top.txt")
            self.joint_labels_all += load_joint_labels("kualisys_joint_labels_bottom.txt")

    def _load_connections(self):
        """Loads the list of pairs of joints that will be connected by a line. This function automatically recognizes
        the system (Kinect or Kualisys) and creates two lists of connections, one for the top of the body (loaded
        from ``res/kinect_skeleton_connections_top.txt`` or ``res/kualisys_skeleton_connections_top.txt``), and one
        concatenating this list with the connections for the bottom of the body (loaded from
        ``res/kinect_skeleton_connections_bottom.txt`` or ``res/kualisys_skeleton_connections_bottom.txt``), which will
        be ignored if :attr:ignore_bottom is set on ``True``.

        .. versionadded:: 2.0
        """

        self.connections_top = []
        self.connections_all = []

        # Kinect
        if "Head" in self.joint_labels_all:
            self.connections_top = load_joints_connections("kinect_skeleton_connections_top.txt")
            self.connections_all = load_joints_connections("kinect_skeleton_connections_top.txt")
            self.connections_all += load_joints_connections("kinect_skeleton_connections_bottom.txt")

        # Qualisys
        elif "HeadTop" in self.joint_labels_all:
            self.connections_top = load_joints_connections("kualisys_skeleton_connections_top.txt")
            self.connections_all = load_joints_connections("kualisys_skeleton_connections_top.txt")
            self.connections_all += load_joints_connections("kualisys_skeleton_connections_bottom.txt")

    def _add_entry_joint_surfaces(self, entry, size, color):
        """Adds or modifies an entry in the dictionary of Surface objects :attr:`joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        entry: str
            The name of the entry. Typically, it should be "joint_X_Y" where:

                • X is the size of the joint, influenced by its position on the body (default, hand or head)
                • Y is the color of the joint, depending on if it was corrected or not (default or corrected).

        size: int
            The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
            in pixels, of the joint.

        color: tuple(int, int, int, int)
            The color of the joint.
        """
        if self.shape_joint == "circle":
            joint_surface = pygame.Surface((size * self.scale_joint + 2, size * self.scale_joint + 2)).convert_alpha()
            joint_surface.fill((0, 0, 0, 0))
            gfxdraw.aacircle(joint_surface, size//2, size//2, int((size * self.scale_joint) // 2), color)
            gfxdraw.filled_circle(joint_surface, size//2, size//2, int((size * self.scale_joint) // 2), color)

        elif self.shape_joint == "square":
            joint_surface = pygame.Surface((size * self.scale_joint, size * self.scale_joint)).convert_alpha()
            joint_surface.fill((0, 0, 0, 0))
            joint_surface.fill(color)

        else:
            raise Exception("Wrong value for the parameter shape_joint: " + str(self.shape_joint) + ". Its value " +
                            'should be "circle" or "square".')

        self.joint_surfaces[entry] = joint_surface

    def _generate_all_joint_surfaces(self):
        """Generates all the Surface objects in :attr:`self.joint_surfaces.`

        .. versionadded:: 2.0
        """
        self._add_entry_joint_surfaces("joint_default_default", self.size_joint_default, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_hand_default", self.size_joint_hand, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_head_default", self.size_joint_head, self.color_joint_default)

        if self.show_joints_corrected:
            self._add_entry_joint_surfaces("joint_default_corrected", self.size_joint_default,
                                           self.color_joint_corrected)
            self._add_entry_joint_surfaces("joint_hand_corrected", self.size_joint_hand, self.color_joint_corrected)
            self._add_entry_joint_surfaces("joint_head_corrected", self.size_joint_head, self.color_joint_corrected)
        else:
            self._add_entry_joint_surfaces("joint_default_corrected", self.size_joint_default, self.color_joint_default)
            self._add_entry_joint_surfaces("joint_hand_corrected", self.size_joint_hand, self.color_joint_default)
            self._add_entry_joint_surfaces("joint_head_corrected", self.size_joint_head, self.color_joint_default)

    def _set_shape_joint(self, shape_joint):
        """Sets the attribute :attr:`shape_joint`, and re-generates the Surface objects in :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        shape_joint: str
            The shape that the joints will have: "circle"  or "square".
        """
        if shape_joint not in ["circle", "square"]:
            raise Exception('Invalid value: the attribute shape_joint should be "circle" or "square", not ' +
                            str(shape_joint))
        self.shape_joint = shape_joint
        self._generate_all_joint_surfaces()

    def _set_color_joint_default(self, color):
        """Sets the attribute :attr:`color_joint_default`, and re-generates the relevant Surface objects in
        :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        color: tuple(int, int, int), tuple(int, int, int, int) or str
            The color of the joint (default: "white"). This parameter can be:

            • A RGB or RGBA tuple (e.g. (255, 255, 255) or (255, 255, 255, 255)). In the case of an RGBA tuple, the last
              number is used for opacity.
            • A hexadecimal value, with a leading number sign (``"#"``), with or without opacity value.
            • A string containing one of the
              `140 HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_).
        """
        self.color_joint_default = convert_color_rgba(color)

        self._add_entry_joint_surfaces("joint_default_default", self.size_joint_default, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_hand_default", self.size_joint_hand, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_head_default", self.size_joint_head, self.color_joint_default)

    def _set_color_joint_corrected(self, color):
        """Sets the attribute :attr:`color_joint_corrected`, and re-generates the relevant Surface objects in
        :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        color: tuple(int, int, int), tuple(int, int, int, int) or str
            The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
            (default: "green"). This parameter can be:

            • A RGB or RGBA tuple (e.g. (255, 255, 255) or (255, 255, 255, 255)). In the case of an RGBA tuple, the last
              number is used for opacity.
            • A hexadecimal value, with a leading number sign (``"#"``), with or without opacity value.
            • A string containing one of the
              `140 HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_).
        """
        self.color_joint_corrected = convert_color_rgba(color)

        self._add_entry_joint_surfaces("joint_default_corrected", self.size_joint_default, self.color_joint_corrected)
        self._add_entry_joint_surfaces("joint_hand_corrected", self.size_joint_hand, self.color_joint_corrected)
        self._add_entry_joint_surfaces("joint_head_corrected", self.size_joint_head, self.color_joint_corrected)

    def _set_color_line(self, color):
        """Sets the attribute :attr:`color_line`.

        .. versionadded:: 2.0

        Parameters
        ----------
        color: tuple(int, int, int), tuple(int, int, int, int) or str
            The color of the lines between the joints (default: "grey"). This parameter can be:

            • A RGB or RGBA tuple (e.g. (255, 255, 255) or (255, 255, 255, 255)). In the case of an RGBA tuple, the last
              number is used for opacity.
            • A hexadecimal value, with a leading number sign (``"#"``), with or without opacity value.
            • A string containing one of the
              `140 HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_).
        """
        self.color_joint_corrected = convert_color_rgba(color)

    def _set_width_line(self, width):
        """Sets the attribute :attr:`width_line`.

        .. versionadded:: 2.0

        Parameters
        ----------
        width: int
            The width of the lines connecting the joints.
        """
        self.width_line = width

    def _set_size_joint_default(self, size):
        """Sets the attribute :attr:`size_joint_default`, and re-generates the relevant Surface objects in
        :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        size: int
            The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
            in pixels, of the joints not covered by ``size_joint_head`` and ``size_joint_hand`` (default: 10).
        """
        self.size_joint_default = size

        self._add_entry_joint_surfaces("joint_default_default", self.size_joint_default,  self.color_joint_default)
        self._add_entry_joint_surfaces("joint_default_corrected", self.size_joint_default, self.color_joint_corrected)

    def _set_size_joint_hand(self, size):
        """Sets the attribute :attr:`size_joint_hand`, and re-generates the relevant Surface objects in
        :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        size: int
            The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
            in pixels, of the "HandRight" and "HandLeft" joints (Kinect) or the "HandOutRight" and "HandOutLeft" joints
            (Kualysis) (default: 20).
        """
        self.size_joint_hand = size

        self._add_entry_joint_surfaces("joint_hand_default", self.size_joint_hand,  self.color_joint_default)
        self._add_entry_joint_surfaces("joint_hand_corrected", self.size_joint_hand, self.color_joint_corrected)

    def _set_size_joint_head(self, size):
        """Sets the attribute :attr:`size_joint_head`, and re-generates the relevant Surface objects in
        :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        size: int
            The radius (if ``shape_joint`` is set on "circle") or width/height (if ``shape_joint`` is set on "square"),
            in pixels, of the "Head" joint (Kinect) or the "HeadFront" joint (Kualysis) (default: 50).
        """
        self.size_joint_head = size

        self._add_entry_joint_surfaces("joint_head_default", self.size_joint_head,  self.color_joint_default)
        self._add_entry_joint_surfaces("joint_head_corrected", self.size_joint_head, self.color_joint_corrected)

    def _set_scale_joint(self, scale_joint):
        """Sets the attribute :attr:`scale_joint`, and re-generates the relevant Surface objects in
        :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        scale_joint: float
            Scaling factor for the size of the joints (default: 1).
        """
        self.scale_joint = scale_joint
        self._generate_all_joint_surfaces()

    def _set_ignore_bottom(self, ignore_bottom):
        """Sets the attribute :attr:`ignore_bottom` and updates the attribute :attr:``connections``, which contains
        a list of the lines that will be displayed.

        .. versionadded:: 2.0

        Parameters
        ----------
        ignore_bottom: bool, optional
            If set on `True`, the joints below the waist will not be displayed. If set on `False` (default), all the
            joints will be displayed. For a complete list of joints being displayed or not, see
            :ref:`Display the sequence <ignore_bottom>`.
        """
        self.ignore_bottom = ignore_bottom
        if self.ignore_bottom:
            self.connections_to_show = self.connections_top
            self.joints_to_show = self.joint_labels_top
        else:
            self.connections_to_show = self.connections_all
            self.joints_to_show = self.joint_labels_all

    def _set_show_lines(self, show_lines):
        """Sets the attribute :attr:`show_lines`.

        .. versionadded:: 2.0

        Parameters
        ----------
        show_lines: bool
            If set on `True` (default), the graphic sequence will include lines between certain joints, to create a
            skeleton. If set on `False`, only the joints will be displayed.
        """
        self.show_lines = show_lines

    def _set_show_joints_corrected(self, show_joints_corrected):
        """Sets the attribute :attr:`show_joints_corrected`.

        .. versionadded:: 2.0

        Parameters
        ----------
        show_joints_corrected: bool
            If set on ``True``, the joints corrected by :meth:`Sequence.correct_jitter` or
            :meth:`Sequence.correct_zeros` will appear colored by :attr:`color_joint_corrected`. Otherwise, the joints
            will appear colored by :attr:`color_joint_default`.
        """
        self.show_joints_corrected = show_joints_corrected
        self._generate_all_joint_surfaces()

    def _toggle_ignore_bottom(self):
        """Sets the attribute :attr:`ignore_bottom` on the opposite of its current value.

        ..versionadded:: 2.0
        """
        self._set_ignore_bottom(not self.ignore_bottom)

    def _toggle_show_lines(self):
        """Sets the attribute :attr:`show_lines` on the opposite of its current value.

        ..versionadded:: 2.0
        """
        self._set_show_lines(not self.show_lines)

    def _toggle_show_joints_corrected(self):
        """Sets the attribute :attr:`show_joints_corrected` on the opposite of its current value.

        ..versionadded:: 2.0
        """
        self._set_show_joints_corrected(not self.show_joints_corrected)

    def _unpause(self):
        """Sets the timer on the current pose timestamp after un-pausing the display of the poses.

        .. versionadded:: 2.0
        """
        self.timer._set_timer(self.poses[self.current_pose].pose.get_relative_timestamp() * 1000)

    def _next_pose(self, verbosity=1):
        """Increments the parameter :attr:`current_pose`; if the last pose is reached, the function
        :meth:`_GraphicSequence.reset` is called.

        .. versionadded:: 2.0

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.current_pose += 1
        if self.current_pose == len(self.sequence) - 1:
            self._reset()

        if verbosity > 1:
            print("Pose " + str(self.current_pose + 1) + " of " + str(len(self.poses)))
            
    def _previous_pose(self, verbosity=1):
        """Decrements the parameter :attr:`current_pose`; if the first pose is reached, the pose is set on the last
        one from the sequence.

        .. versionadded:: 2.0

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.current_pose -= 1
        if self.current_pose == len(self.sequence) - 1:
            self.current_pose = len(self.poses) - 1

        if verbosity > 1:
            print("Pose " + str(self.current_pose + 1) + " of " + str(len(self.poses)))

    def _reset(self):
        """Sets the current pose to the first of the sequence, and resets the timer to 0.

        .. versionadded:: 2.0
        """
        self.current_pose = 0
        self.timer._reset()

    def _apply_events(self, event, verbosity=1):
        """Gets a Pygame keypress event, and calls the :func:`_GraphicSequence._next_pose` if the key pressed is the
        right arrow key, or :func:`_GraphicSequence._previous_pose` if the key pressed is the left arrow key.

        .. versionadded:: 2.0

        Parameters
        ----------
        event: `Pygame.event <https://www.pygame.org/docs/ref/event.html>`_
            A Pygame event.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        if event.type == KEYDOWN and event.key == K_RIGHT:
            self._next_pose(verbosity)
        elif event.type == KEYDOWN and event.key == K_LEFT:
            self._previous_pose(verbosity)

    def _play(self, graphic_window, shift_x=0, shift_y=0):
        """Displays on the window object the poses in real time.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.

        shift_x: int, optional
            The number of pixels to shift the display of the joints on the horizontal axis (default: 0).

        shift_y: int, optional
            The number of pixels to shift the display of the joints on the vertical axis (default: 0).
        """
        if self.sequence.poses[self.current_pose + 1].get_relative_timestamp() * 1000 < self.timer._get_timer():
            self._next_pose()
        self.poses[self.current_pose]._show(graphic_window, self.joint_surfaces, self.joints_to_show,
                                            self.connections_to_show, self.color_line, self.width_line, self.show_lines,
                                            shift_x, shift_y)
        self.timer._update()

    def _show_pose(self, graphic_window, shift_x=0, shift_y=0):
        """Displays the pose with the index :attr:`current_pose` on the ``window`` object.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.

        shift_x: int, optional
            The number of pixels to shift the display of the joints on the horizontal axis (default: 0).

        shift_y: int, optional
            The number of pixels to shift the display of the joints on the vertical axis (default: 0).
        """
        self.poses[self.current_pose]._show(graphic_window, self.joint_surfaces, self.joints_to_show,
                                            self.connections_to_show, self.color_line, self.width_line, self.show_lines,
                                            shift_x, shift_y)
        self.timer._update()
        self.timer._set_timer(self.poses[self.current_pose].pose.get_relative_timestamp() * 1000)


class GraphicPose(object):
    """Graphical counterpart to the class :class:`Pose`. This class allows to save the :class:`_GraphicJoint` objects.

    .. versionadded:: 2.0

    Parameters
    ----------
    pose: Pose
        A Pose instance.

    graphic_window: GraphicWindow
        The window object, where to display the sequence.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Attributes
    ----------
    pose: Pose
        The Pose instance, passed as parameter upon initialisation.

    joints: dict(str: _GraphicJoint)
        List of all the :class:`_GraphicJoint` objects counterparts of the :class:`Joint` objects.
    """

    def __init__(self, pose, graphic_window, verbosity=1):
        self.pose = pose
        self.joints = {}
        self._load_joints(graphic_window, verbosity)

    def _load_joints(self, graphic_window, verbosity=1):
        """Creates :class:`_GraphicJoint` elements for each joint of the pose and add them to the :attr:`joints`
        attribute.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            The window object, where to display the sequence.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        for joint_label in self.pose.joints.keys():
            if verbosity > 1:
                print("\t\tLoading " + str(joint_label) + "...")
            self.joints[joint_label] = GraphicJoint(self.pose.joints[joint_label], graphic_window, verbosity)

    def _show_line(self, graphic_window, connection, color_line, width_line, shift_x=0, shift_y=0):
        """Shows a single line between two joints specified in ``connection`` on the ``window`` object.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.

        connection: str(list, list)
            A list of two joint labels to connect by a line.

        color_line: tuple(int, int, int, int)
            The color of the lines connecting the joints.

        width_line: int
            The width, in pixels, of the lines connecting the joints.

        shift_x: int, optional
            The number of pixels to shift the display of the joints on the horizontal axis (default: 0).

        shift_y: int, optional
            The number of pixels to shift the display of the joints on the vertical axis (default: 0).
        """
        joint1 = self.joints[connection[0]]
        joint2 = self.joints[connection[1]]

        pygame.draw.line(graphic_window.window, color_line, (joint1.x + shift_x, joint1.y + shift_y),
                         (joint2.x + shift_x, joint2.y + shift_y), width_line)

    def _show(self, graphic_window, joint_surfaces, joints_to_show, connections_to_show, color_line, width_line,
              show_lines, shift_x=0, shift_y=0):
        """Displays the pose on the ``window`` object.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.

        joint_surfaces: dict(str: `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_)
            A dictionary containing the different `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            objects representing single joints.

        joints_to_show: list(str)
            A list of joint labels to be displayed.

        connections_to_show: list(list(str, str))
            A list of lines to be displayed to connect joints.

        color_line: tuple(int, int, int, int)
            The color of the lines connecting the joints.

        width_line: int
            The width, in pixels, of the lines connecting the joints.

        show_lines: bool, optional
            Defines if to show the lines connecting the joints (default: ``True``).

        shift_x: int, optional
            The number of pixels to shift the display of the joints on the horizontal axis (default: 0).

        shift_y: int, optional
            The number of pixels to shift the display of the joints on the vertical axis (default: 0)."""

        if show_lines:
            for connection in connections_to_show:
                self._show_line(graphic_window, connection, color_line, width_line, shift_x, shift_y)
        for j in self.joints.keys():
            if j in joints_to_show:
                self.joints[j]._show(graphic_window, joint_surfaces, shift_x, shift_y)


class GraphicJoint(object):
    """Graphical counterpart to the class :class:`Joint`. This class allows to convert the original coordinates and save
    them into graphical coordinates.

    .. versionadded:: 2.0

    Parameters
    ----------
    joint: Joint
        A Joint instance.

    graphic_window: GraphicWindow
        The window object, where to display the sequence.

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    Attributes
    ----------
    joint: Joint
        The Joint instance passed as parameter upon initialisation.

    x: float
        The x coordinate, in pixels.

    y: float
        The y coordinate, in pixels.
    """

    def __init__(self, joint, graphic_window, verbosity=1):
        self.joint = joint
        self.x = None
        self.y = None
        self._convert_coordinates(graphic_window, verbosity)

    def _convert_coordinates(self, graphic_window, verbosity=1):
        """Converts the original coordinates into graphic coordinates.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            The window object, where to display the sequence.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.x = graphic_window._convert_x(self.joint.x, 1)
        if verbosity > 1:
            print("\t\t\tCoordinate x (" + str(self.joint.x) + "): " + str(self.x))
        self.y = graphic_window._convert_y(self.joint.y, 1)
        if verbosity > 1:
            print("\t\t\tCoordinate y (" + str(self.joint.y) + "): " + str(self.y))

    def _rotate(self, graphic_window, yaw=0, pitch=0, roll=0):
        """Sets the attributes :attr:`x` and :attr:`y` given three rotations from the original coordinates: yaw, pitch
        and roll.

        .. versionadded:: 2.0

        Warning
        -------
        This function is experimental as of version 2.0.

        Parameters
        ----------
        graphic_window: GraphicWindow
            The window object, where to display the sequence.

        yaw: float, optional
            The angle of yaw, or rotation on the x axis, in degrees (default: 0).

        pitch: float, optional
            The angle of pitch, or rotation on the y axis, in degrees (default: 0).

        roll: float, optional
            The angle of roll, or rotation on the z axis, in degrees (default: 0).
        """
        rot_x, rot_y, rot_z = self.joint.convert_rotation(yaw, pitch, roll)
        self.x = graphic_window._convert_x(rot_x, 1)
        self.y = graphic_window._convert_y(rot_y, 1)

    def _show(self, graphic_window, joint_surfaces, shift_x=0, shift_y=0):
        """Displays the joint on the ``window`` surface.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: GraphicWindow
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.

        joint_surfaces: dict(str: `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_)
            A dictionary containing the elements representing the joints that can be displayed.

        shift_x: int, optional
            The number of pixels to shift the display of the joints on the horizontal axis (default: 0).

        shift_y: int, optional
            The number of pixels to shift the display of the joints on the vertical axis (default: 0)."""

        location = "_default"
        correction = "_default"

        if self.joint.get_is_randomized():
            if self.joint.joint_label in ["SpineMid", "Chest"]:
                location = "_head"
            elif self.joint.joint_label in ["ShoulderLeft", "Neck", "ShoulderTopLeft", "HeadRight"]:
                location = "_hand"

        else:
            if self.joint.joint_label in ["Head", "HeadFront"]:
                location = "_head"
            elif self.joint.joint_label in ["HandRight", "HandLeft", "HandOutRight", "HandOutLeft"]:
                location = "_hand"
            correction = "_default"

        if self.joint.get_is_corrected():
            correction = "_corrected"

        half_width = joint_surfaces["joint" + location + correction].get_width() // 2
        half_height = joint_surfaces["joint" + location + correction].get_height() // 2

        graphic_window.window.blit(joint_surfaces["joint" + location + correction], (self.x + shift_x - half_width,
                                                                                     self.y + shift_y - half_height))
