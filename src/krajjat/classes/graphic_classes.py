"""These classes allow to convert the data from :class:`Sequence`, :class:`Pose` and :class:`Joint` to display them
in the :doc:`graphic_functions`. All these classes and their methods should be considered private."""
import math

import pygame
from pygame.locals import *
from pygame import gfxdraw
import cv2
from krajjat.tool_functions import convert_color, load_joint_labels, load_joint_connections, show_progression


class WindowArea(object):
    """Defines the size of part of the window and allows to convert and scale the coordinates of the joints to be
    displayed.

    .. versionadded:: 2.0

    Parameters
    ----------
    resolution: tuple(int, int)
        A tuple containing the resolution of the window area, with horizontal and vertical number of pixels,
        respectively.

    blit_coordinates: tuple(int, int), optional
        A tuple containing the coordinates at which the graphic_window should be placed on the main window.

    elements: list(str), optional
        A list containing the elements that should be placed on the window area (e.g. ``"sequence1"`` or ``"video"``).

    height_window_in_meters: int or float, optional
        Defines the distance, in meters, represented by the vertical number of pixels of the window area
        (by default: 3).

    Attributes
    ----------
    window_area: pygame.Surface
        The pygame Surface containing the graphic elements, set during the initialisation.

    resolution: tuple(int, int)
        A tuple containing the width and height of the :attr:`window`, in pixels.

    width: int
        The width of the :attr:`window`, in pixels.

    height: int
        The height of the :attr:`window`, in pixels.

    center_x: int
        The mid-point on the x-axis of the :attr:`window`, in pixels.

    center_y: int
        The mid-point on the y-axis of the `:attr:`window`, in pixels.

    blit_coordinates: tuple(int, int)
        A tuple containing the coordinates at which the graphic_window should be placed on the main window.

    elements: list(str)
        A list containing the elements that should be placed on the window area (e.g. ``"sequence1"`` or ``"video"``).

    height_window_in_meters: float
        Defines the distance, in meters, represented by the vertical number of pixels of the window.

    pixel_meter_scale: float
        The real-life distance a pixel represents, in meters. For example, if the window area is 1000 pixels vertically,
        and the parameter :attr:`height_area_in_meters` is set on 1, each pixel will be equivalent to a square of 1 mm ×
        1 mm.
    """

    def __init__(self, resolution, blit_coordinates=(0, 0), elements=None, height_window_in_meters=3.0):
        self.resolution = resolution
        self.width = resolution[0]
        self.height = resolution[1]
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.window_area = pygame.Surface(resolution).convert_alpha()
        self.background_surface = pygame.Surface(resolution).convert_alpha()
        self.blit_coordinates = blit_coordinates
        self.elements = []
        if elements is not None:
            self.elements = elements
        self.height_window_in_meters = height_window_in_meters
        self.pixel_meter_scale = self.height / height_window_in_meters

    def set_resolution(self, resolution):
        """Sets the resolution of the window area, and updates the attributes :attr:`resolution`, attr:`width`,
        attr:`height`, attr:`center_x`, attr:`center_y` and attr:`window_area`.

        .. versionadded:: 2.0

        Parameters
        ----------
        resolution: tuple(int, int)
            A tuple containing the width and height of the :attr:`window`, in pixels.
        """
        self.resolution = resolution
        self.width = resolution[0]
        self.height = resolution[1]
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.window_area = pygame.Surface(resolution)

    def set_blit_coordinates(self, blit_coordinates):
        """Sets the attribute :attr:`blit_coordinates` of the window area.

        .. versionadded:: 2.0

        Parameters
        ----------
        blit_coordinates: tuple(int, int)
            A tuple containing the coordinates at which the graphic_window should be placed on the main window.
        """
        self.blit_coordinates = blit_coordinates

    def add_element(self, element):
        """Adds an element to the attribute :attr:`elements` of the window area.

        .. versionadded:: 2.0

        Parameters
        ----------
        element: str
            A string representing an element that should be displayed on the window area.
        """
        self.elements.append(element)

    def set_elements(self, elements):
        """Sets the attribute :attr:`elements` of the window area.

        .. versionadded:: 2.0

        Parameters
        ----------
        elements: list(str)
            A list containing the elements that should be placed on the window area (e.g. ``"sequence1"`` or
            ``"video"``).
        """
        self.elements = elements

    def remove_element(self, element):
        """Removes an element from the attribute :attr:`elements` of the window area, if it exists in the list.

        .. versionadded:: 2.0

        Parameters
        ----------
        element: str
            A string representing an element that should be removed from the window area.
        """
        if element in self.elements:
            self.elements.remove(element)

    def set_height_window_in_meters(self, height_window_in_meters):
        """Sets the attribute :attr:`height_window_in_meters`.

        .. versionadded:: 2.0

        Parameters
        ----------
        height_window_in_meters: float
            Defines the distance, in meters, represented by the vertical number of pixels of the window area
            (by default: 3).
        """
        self.height_window_in_meters = height_window_in_meters
        self.pixel_meter_scale = self.height / height_window_in_meters

    def contains(self, element):
        """Returns ``True`` if the element specified as parameter exists in the attribute :attr:`elements`.

        .. versionadded:: 2.0

        Parameters
        ----------
        element: str
            A string representing an element that may be contained in the window area.
        """
        return element in self.elements

    def convert_x(self, x, scale=1.0):
        """Converts the x "real" coordinate to a graphical coordinate to be displayed in the window area.

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
            The coordinate of the pixel on the x-axis of the window area.
        """
        return int(self.center_x - x * self.pixel_meter_scale * scale)

    def convert_y(self, y, scale=1.0):
        """Converts the y "real" coordinate to a graphical coordinate to be displayed in the window area.

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
            The coordinate of the pixel on the y-axis of the window area.
        """
        return int(self.center_y - y * self.pixel_meter_scale * scale)

    def get_resolution(self):
        """Returns a tuple containing the resolution of the window area.

        .. versionadded:: 2.0

        Returns
        -------
        tuple(int, int)
            The resolution of the window area, in pixels, horizontally and vertically, respectively.
        """
        return self.width, self.height

    def fill(self, color):
        """Fills the window with a given color.

        .. versionadded:: 2.0

        Parameters
        ----------
        tuple(int, int, int) or tuple(int, int, int, int)
            A RGB or RGBA color tuple.
        """
        self.background_surface.fill(color)

    def blit_background_surface(self):
        """Blits the background surface on the window area. This function can be used to paint the background surface
        in a specific color.

        .. versionadded:: 2.0
        """
        self.window_area.blit(self.background_surface, (0, 0))

    def blit(self, surface, position):
        """Blits a surface onto the window area, at a specified position.

        .. versionadded:: 2.0

        Parameters
        ----------
        surface: `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            A pygame Surface.

        position: tuple(int, int)
            The position on the window area where to place the top-left corner of the surface.
        """
        self.window_area.blit(surface, position)

    def show(self, window):
        """Blits the window area onto a window.

        .. versionadded:: 2.0

        Parameters
        ----------
        window: `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            A pygame Surface.
        """
        window.blit(self.window_area, self.blit_coordinates)


class Timer(object):
    """Creates and sets a timer.

    .. versionadded:: 2.0

    Attributes
    ----------
    clock: pygame.time.Clock
        A Pygame clock object.

    timer: float
        A timer, in milliseconds.

    speed: float
        A factor that multiplies the tick of the clock (default: 1). A value of 2 would make the timer go twice
        as fast.

    play: boolean
        A boolean indicating whether the timer is counting (``True``) or on pause (``False``).

    last_tick: int
        The value of the last tick (in milliseconds) added to the :attr:`timer`.

    last_full_second: int
        The value of the last second fully elapsed. For example, if the :attr:`timer` is set on 5263 ms, this function
        will return ``5``.

    update_marker: bool
        A boolean indicating if the timer has been modified. This boolean is initialised on ``False``, and turns to
        ``True`` whenever the method :meth:`Timer.reset` or :meth:`Timer.set` is called. This attribute is then used as
        a marker to know if other objects must be reset. The parameter should return to ``False`` by using the method
        :meth:`Timer.end_update`.
    """

    def __init__(self, speed=1.0):
        self.clock = pygame.time.Clock()
        self.timer = 0
        self.speed = speed
        self.play = True
        self.last_tick = 0
        self.last_full_second = 0
        self.update_marker = False

    def set_timer(self, t):
        """Sets the timer at a specific value.

        .. versionadded:: 2.0

        Parameters
        ----------
        t: float
            The value, in milliseconds, to set the timer on.
        """
        self.timer = t
        self.update_marker = True

    def set_speed(self, speed):
        """Sets the displaying speed.

        .. versionadded:: 2.0

        Parameters
        ----------
        speed: float
            A factor that multiplies the tick of the clock. A value of 2 would make the timer go twice as fast.
        """
        self.speed = speed

    def get_timer(self):
        """Returns the value of the attribute :attr:`timer`.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The time contained in the attribute :attr:`timer`, in milliseconds.
        """
        return self.timer

    def get_last_tick(self):
        """Returns the value of the attribute :attr:`last_tick`.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The value of the last tick added to the timer.
        """
        return self.last_tick

    def get_last_full_second(self):
        """Returns the value of the attribute :attr:`last_full_second`.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The value of the last second fully elapsed. For example, if the attribute :attr:`timer` is set on 5263 ms,
            this function will return ``5``.
        """
        return self.last_full_second

    def reset(self):
        """Resets the timer to 0, and sets the attribute :attr:`update_marker` to ``True``.

        .. versionadded:: 2.0
        """
        self.timer = 0
        self.update_marker = True

    def pause(self):
        """Sets the attribute :attr:`play` on ``False``, preventing the timer from being updated.

        .. versionadded:: 2.0
        """
        self.play = False

    def unpause(self):
        """Sets the attribute :attr:`play` on ``True``, reestablishing the updating of the timer.

        .. versionadded:: 2.0
        """
        self.play = True

    def update(self):
        """Adds the tick of the `pygame.time.Clock <https://www.pygame.org/docs/ref/time.html#pygame.time.Clock>`_
        object to the timer if the :attr:`play` is set on ``True``.

        .. versionadded:: 2.0
        """
        delta = self.clock.tick() * self.speed
        if self.play:
            self.last_tick = delta
            self.timer += delta
            self.last_full_second = self.timer // 1000
        else:
            self.last_tick = 0

    def end_update(self):
        """Sets the attribute :attr:`update_marker` to ``False``.

        .. versionadded:: 2.0
        """
        self.update_marker = False


class GraphicSequence(object):
    """Graphical counterpart to the class :class:`Sequence`. This class allows to convert the original coordinates of
    the joints into graphical coordinates.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence: Sequence
        A Sequence instance.

    graphic_window: WindowArea
        The window object, where to display the sequence.

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    x_axis: str, optional
        Sets which axis should be matched to the x display axis (default `"x"`, can be `"y"` or `"z"` too).

    y_axis: str, optional
        Sets which axis should be matched to the y display axis (default `"y"`, can be `"x"` or `"z"` too).

    verbosity: int, optional
        Sets how much feedback the code will provide in the console output:

        • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
        • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
          current steps.
        • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
          may clutter the output and slow down the execution.

    **kwargs: dict
        A dictionary of optional arguments. See a complete list of the optional arguments in
        :ref:`keyword_arguments_display_functions`.

    Attributes
    ----------
    sequence: Sequence
        The Sequence instance, passed as parameter upon initialisation.

    current_pose_index: int
        The index of the pose currently being in display. It is initialised with the value from the parameter
        ``start_pose``.

    poses: list(_GraphicPose)
        List of all the :class:`_GraphicPose` objects counterparts of the :class:`Pose` objects.

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
        A list of the joints from the top of the body, loaded from :func:`tool_functions.load_joint_labels`.

    joint_labels_all: list(str)
        A list of all the joints from the body, loaded from :func:`tool_functions.load_joint_labels`.

    connections_to_show: list(list(str, str))
        A list of the connections that will be displayed as lines between joints.

    connections_top: list(list(str, str))
        A list of the connections from the top of the body, loaded from ``res/kinect_skeleton_connections.txt`` or
        ``res/kualisys_skeleton_connections.txt``.

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

    shift_x: int
        The number of pixels to shift the display of the joints on the horizontal axis. Can
        be modified via :meth:`_GraphicSequence._set_shift_x`.

    shift_y: int
        The number of pixels to shift the display of the joints on the vertical axis. Can
        be modified via :meth:`_GraphicSequence._set_shift_y`.

    zoom_level: float
        Defines the zoom level compared to the original view. A zoom level of 2 will make the joints appear twice as
        close.
    """

    def __init__(self, sequence, graphic_window, start_pose=0, x_axis="x", y_axis="y", verbosity=1, **kwargs):

        self.sequence = sequence
        self.current_pose_index = start_pose
        self.poses = []

        self.joint_labels_top = []
        self.joint_labels_all = []
        self._load_joint_labels()

        self.connections_top = []
        self.connections_all = []
        self._load_connections()

        self.ignore_bottom = None
        self.connections_to_show = []
        self.joints_to_show = []
        self.ignored_joints = kwargs.get("ignored_joints", [])
        self.set_ignore_bottom(kwargs.get("ignore_bottom", False))

        self._load_poses(graphic_window, x_axis, y_axis, verbosity)
        self.show_lines = kwargs.get("show_lines", True)
        self.color_background = kwargs.get("color_background", "black")

        self.joint_surfaces = {}
        self.shape_joint = kwargs.get("shape_joint", "circle")
        self.color_joint_default = convert_color(kwargs.get("color_joint", "white"), "RGB", True)
        self.color_joint_default = convert_color(kwargs.get("color_joint_default", self.color_joint_default), "RGB", True)
        self.color_joint_corrected = convert_color(kwargs.get("color_joint_corrected", "sheen green"), "RGB", True)
        self.color_line = convert_color(kwargs.get("color_line", "grey"), "RGB", True)
        self.width_line = kwargs.get("width_line", 1)
        self.size_joint_head = kwargs.get("size_joint_head", 50)
        self.size_joint_hand = kwargs.get("size_joint_hand", 20)
        self.size_joint_default = kwargs.get("size_joint_default", 10)
        self.scale_joint = kwargs.get("scale_joint", 1)
        self.shift_x = kwargs.get("shift", (0, 0))[0]
        self.shift_y = kwargs.get("shift", (0, 0))[1]
        self.zoom_level = kwargs.get("zoom_level", 1)
        self.show_joints_corrected = True
        self.set_show_joints_corrected(kwargs.get("show_joints_corrected", True))
        self._generate_all_joint_surfaces()

    def _load_poses(self, graphic_window, x_axis="x", y_axis="y", verbosity=1):
        """Converts a :class:`Sequence` into a :class:`_GraphicSequence` and add them to the :attr:`poses`
        attribute.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: WindowArea
            The window object, where to display the sequence.

        x_axis: str, optional
            Sets which axis should be matched to the x display axis (default `"x"`, can be `"y"` or `"z"` too).

        y_axis: str, optional
            Sets which axis should be matched to the y display axis (default `"y"`, can be `"x"` or `"z"` too).

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
            self.poses.append(GraphicPose(self.sequence.poses[p], graphic_window, x_axis, y_axis, verbosity))

        if verbosity > 0:
            print("100% - Done.")

    def _load_joint_labels(self):
        """Loads two lists of joint labels, :attr:`joint_labels_top` and :attr:`joint_labels_all`, defining which joints
        will be displayed depending if the attribute :attr:`ignore_bottom` is set on ``True`` or ``False``. The joint
        labels list are loaded from ``res/kinect_joint_labels.txt`` or ``res/kualisys_joint_labels.txt``.

        .. versionadded:: 2.0
        """

        joints = self.sequence.get_joint_labels()

        if "Head" in joints:
            self.joint_labels_top = load_joint_labels("kinect", "top")
            self.joint_labels_all = load_joint_labels("kinect", "all")
        elif "HeadTop" in joints:
            self.joint_labels_top = load_joint_labels("kualisys", "top", "new")
            self.joint_labels_all = load_joint_labels("kualisys", "all", "new")

    def _load_connections(self):
        """Loads the list of pairs of joints that will be connected by a line. This function automatically recognizes
        the system (Kinect or Kualisys) and creates two lists of connections, one for the top of the body (loaded
        from ``res/kinect_skeleton_connections.txt``), and one concatenating this list with the connections for the
        bottom of the body, which will be ignored if :attr:ignore_bottom is set on ``True``.

        .. versionadded:: 2.0
        """

        # Kinect
        if "Head" in self.joint_labels_all:
            self.connections_top = load_joint_connections("kinect", "top")
            self.connections_all = load_joint_connections("kinect", "all")

        # Qualisys
        elif "HeadTop" in self.joint_labels_all:
            self.connections_top = load_joint_connections("qualisys", "top")
            self.connections_all = load_joint_connections("qualisys", "all")

        for connection in self.connections_top:
            keep = True
            for joint_label in connection:
                if joint_label not in self.sequence.get_joint_labels():
                    keep = False
                    break
            if not keep:
                self.connections_top.remove(connection)

        for connection in self.connections_all:
            keep = True
            for joint_label in connection:
                if joint_label not in self.sequence.get_joint_labels():
                    keep = False
                    break
            if not keep:
                self.connections_all.remove(connection)

    def _remove_ignored_joints(self):
        if len(self.ignored_joints) > 0:
            if type(self.ignored_joints) is str:
                self.ignored_joints = [self.ignored_joints]
            for ignored_joint in self.ignored_joints:
                self.joints_to_show.remove(ignored_joint)

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

    def get_timestamp(self):
        """Returns the timestamp of the current frame, in milliseconds.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The timestamp of the current frame, in milliseconds.
        """
        return self.sequence.poses[self.current_pose_index].get_relative_timestamp() * 1000

    def get_duration(self):
        """Returns the duration of the sequence, in milliseconds.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The duration of the sequence, in milliseconds.
        """
        return self.sequence.get_duration() * 1000

    def get_number_of_poses(self):
        """Returns the number of poses in the sequence.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The number of poses in the sequence.
        """
        return self.sequence.get_number_of_poses()

    def get_current_pose_index(self):
        """Returns the index of the pose currently being displayed.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The index of the pose currently being displayed.
        """
        return self.current_pose_index

    def set_color_background(self, color):
        """Sets the attribute :attr:`color_background`.

        .. versionadded:: 2.0

        Parameters
        ----------
        color: tuple(int, int, int), tuple(int, int, int, int) or str
            The color displayed in the background of the sequence (default: "black"). This parameter can be:

            • A RGB or RGBA tuple (e.g. (255, 255, 255) or (255, 255, 255, 255)). In the case of an RGBA tuple, the last
              number is used for opacity.
            • A hexadecimal value, with a leading number sign (``"#"``), with or without opacity value.
            • A string containing one of the
              `140 HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_).
        """
        self.color_background = convert_color(color, "RGB", True)

    def set_shape_joint(self, shape_joint):
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

    def set_color_joint_default(self, color):
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
        self.color_joint_default = convert_color(color, "RGB", True)

        self._add_entry_joint_surfaces("joint_default_default", self.size_joint_default, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_hand_default", self.size_joint_hand, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_head_default", self.size_joint_head, self.color_joint_default)

    def set_color_joint_corrected(self, color):
        """Sets the attribute :attr:`color_joint_corrected`, and re-generates the relevant Surface objects in
        :attr:`self.joint_surfaces`.

        .. versionadded:: 2.0

        Parameters
        ----------
        color: tuple(int, int, int), tuple(int, int, int, int) or str
            The color of the joints corrected by :meth:`Sequence.correct_jitter` or :meth:`Sequence.correct_zeros`
            (default: "sheen green"). This parameter can be:

            • A RGB or RGBA tuple (e.g. (255, 255, 255) or (255, 255, 255, 255)). In the case of an RGBA tuple, the last
              number is used for opacity.
            • A hexadecimal value, with a leading number sign (``"#"``), with or without opacity value.
            • A string containing one of the
              `140 HTML/CSS color names <https://en.wikipedia.org/wiki/X11_color_names>`_).
        """
        self.color_joint_corrected = convert_color(color, "RGB", True)

        self._add_entry_joint_surfaces("joint_default_corrected", self.size_joint_default, self.color_joint_corrected)
        self._add_entry_joint_surfaces("joint_hand_corrected", self.size_joint_hand, self.color_joint_corrected)
        self._add_entry_joint_surfaces("joint_head_corrected", self.size_joint_head, self.color_joint_corrected)

    def set_color_line(self, color):
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
        self.color_joint_corrected = convert_color(color, "RGB", True)

    def set_width_line(self, width):
        """Sets the attribute :attr:`width_line`.

        .. versionadded:: 2.0

        Parameters
        ----------
        width: int
            The width of the lines connecting the joints.
        """
        self.width_line = width

    def set_size_joint_default(self, size):
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

        self._add_entry_joint_surfaces("joint_default_default", self.size_joint_default, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_default_corrected", self.size_joint_default, self.color_joint_corrected)

    def set_size_joint_hand(self, size):
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

        self._add_entry_joint_surfaces("joint_hand_default", self.size_joint_hand, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_hand_corrected", self.size_joint_hand, self.color_joint_corrected)

    def set_size_joint_head(self, size):
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

        self._add_entry_joint_surfaces("joint_head_default", self.size_joint_head, self.color_joint_default)
        self._add_entry_joint_surfaces("joint_head_corrected", self.size_joint_head, self.color_joint_corrected)

    def set_scale_joint(self, scale_joint):
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

    def set_ignore_bottom(self, ignore_bottom):
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
        self._remove_ignored_joints()

    def set_show_lines(self, show_lines):
        """Sets the attribute :attr:`show_lines`.

        .. versionadded:: 2.0

        Parameters
        ----------
        show_lines: bool
            If set on `True` (default), the graphic sequence will include lines between certain joints, to create a
            skeleton. If set on `False`, only the joints will be displayed.
        """
        self.show_lines = show_lines

    def set_show_joints_corrected(self, show_joints_corrected):
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

    def set_shift_x(self, shift_x):
        """Sets the attribute :attr:`shift_x`.

        .. versionadded:: 2.0

        Parameters
        ----------
        shift_x: int
            The number of pixels to shift the sequence on the horizontal axis.
        """
        self.shift_x = shift_x

    def set_shift_y(self, shift_y):
        """Sets the attribute :attr:`shift_y`.

        .. versionadded:: 2.0

        Parameters
        ----------
        shift_y: int
            The number of pixels to shift the sequence on the horizontal axis.
        """
        self.shift_y = shift_y

    def set_zoom_level(self, zoom_level, window_area, mouse_pos):
        """Sets the attribute :attr:`zoom_level`.

        .. versionadded:: 2.0

        Parameters
        ----------
        zoom_level: float
            Defines the zoom level compared to the original view. A zoom level of 2 will make the joints appear twice as
            close.
        window_area: WindowArea
            A WindowArea object.
        mouse_pos: tuple(int, int)
            The position of the mouse, in pixels.
        """
        ratio_horizontal = mouse_pos[0] / window_area.width
        ratio_vertical = mouse_pos[1] / window_area.height

        pixel_difference_horizontal = (zoom_level - self.zoom_level) * window_area.width//2
        pixel_difference_vertical = (zoom_level - self.zoom_level) * window_area.height//2

        self.set_shift_x(round(self.shift_x - (ratio_horizontal * pixel_difference_horizontal)))
        self.set_shift_y(round(self.shift_y - (ratio_vertical * pixel_difference_vertical)))

        self.zoom_level = round(zoom_level, 2)

    def toggle_ignore_bottom(self):
        """Sets the attribute :attr:`ignore_bottom` on the opposite of its current value.

        ..versionadded:: 2.0
        """
        self.set_ignore_bottom(not self.ignore_bottom)

    def toggle_show_lines(self):
        """Sets the attribute :attr:`show_lines` on the opposite of its current value.

        ..versionadded:: 2.0
        """
        self.set_show_lines(not self.show_lines)

    def toggle_show_joints_corrected(self):
        """Sets the attribute :attr:`show_joints_corrected` on the opposite of its current value.

        ..versionadded:: 2.0
        """
        self.set_show_joints_corrected(not self.show_joints_corrected)

    def set_pose_from_timestamp(self, timestamp, method="lower", verbosity=1):
        """Sets the attribute :attr:`current_pose` from the value of the timer.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp: float
            A timestamp, in milliseconds.

        method: str
            Defines which pose is selected based on the timestamp.

            • If set on ``"closest"`` (default), the closest pose from the timestamp is selected.
            • If set on ``"below"``, ``"lower"`` or ``"under"``, the closest pose below the timestamp is selected.
            • If set on ``"above"``, ``"higher"`` or ``"over"``, the closest pose above the timestamp is selected.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        if verbosity > 1:
            print("Setting pose with timestamp below " + str(round((timestamp + 1) / 1000, 3)) + ": ", end="")
        self.current_pose_index = self.sequence.get_pose_index_from_timestamp(round((timestamp + 1) / 1000, 3), method)
        if verbosity > 1:
            print("Pose " + str(self.current_pose_index) + ".")

    def set_pose_from_index(self, pose_index, timer):
        """Sets the attribute :attr:`current_pose` from the value specified in the timer.

        .. versionadded:: 2.0

        Parameters
        ----------
        pose_index: int
            The index of the pose.
        timer: Timer
            A Timer instance.
        """
        self.current_pose_index = pose_index
        timer.set_timer(self.get_timestamp())

    def next_pose(self, timer, verbosity=1):
        """Increments the parameter :attr:`current_pose`; if the last pose is reached, the function
        :meth:`_GraphicSequence.reset` is called.

        .. versionadded:: 2.0

        timer: Timer
            A Timer object.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.current_pose_index += 1
        if self.current_pose_index == len(self.sequence):
            self.reset(timer)

        if verbosity > 1:
            print("Pose " + str(self.current_pose_index + 1) + " of " + str(len(self.poses)))

    def previous_pose(self, timer, verbosity=1):
        """Decrements the parameter :attr:`current_pose`; if the first pose is reached, the pose is set on the last
        one from the sequence.

        .. versionadded:: 2.0

        timer: Timer
            A Timer object.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.current_pose_index -= 1
        if self.current_pose_index == - 1:
            self.current_pose_index = len(self.poses) - 1
            timer.set_timer(self.sequence.poses[self.current_pose_index].get_relative_timestamp() * 1000)

        if verbosity > 1:
            print("Pose " + str(self.current_pose_index + 1) + " of " + str(len(self.poses)))

    def reset(self, timer):
        """Sets the current pose to the first of the sequence, and resets the timer to 0.

        .. versionadded:: 2.0

        timer: Timer
            A Timer object.
        """
        self.current_pose_index = 0
        timer.reset()

    def apply_events(self, event, timer, verbosity=1):
        """Gets a Pygame keypress event, and calls the :func:`_GraphicSequence._next_pose` if the key pressed is the
        right arrow key, or :func:`_GraphicSequence._previous_pose` if the key pressed is the left arrow key.

        .. versionadded:: 2.0

        Parameters
        ----------
        event: `Pygame.event <https://www.pygame.org/docs/ref/event.html>`_
            A Pygame event.

        timer: Timer
            A Timer object.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        if event.type == KEYDOWN and event.key == K_RIGHT:
            self.next_pose(timer, verbosity)
        elif event.type == KEYDOWN and event.key == K_LEFT:
            self.previous_pose(timer, verbosity)

    def play(self, window_area, timer):
        """Displays on the window object the poses in real time.

        .. versionadded:: 2.0

        Parameters
        ----------
        window_area: WindowArea
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.
        timer: Timer
            A Timer object.
        """
        window_area.fill(self.color_background)
        if self.current_pose_index == len(self.sequence.poses) - 1:
            self.next_pose(timer)
        else:
            while self.sequence.poses[self.current_pose_index + 1].get_relative_timestamp() * 1000 <= timer.get_timer():
                self.next_pose(timer)
                if self.current_pose_index == len(self.sequence.poses) - 1:
                    break
        self.poses[self.current_pose_index].show(window_area, self.joint_surfaces, self.joints_to_show,
                                                 self.connections_to_show, self.color_line, self.width_line,
                                                 self.show_lines, self.shift_x, self.shift_y, self.zoom_level)

    def show_pose(self, window_area):
        """Displays the pose with the index :attr:`current_pose` on the ``window`` object.

        .. versionadded:: 2.0

        Parameters
        ----------
        window_area: WindowArea
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.
        """
        window_area.fill(self.color_background)
        self.poses[self.current_pose_index].show(window_area, self.joint_surfaces, self.joints_to_show,
                                                 self.connections_to_show, self.color_line, self.width_line,
                                                 self.show_lines, self.shift_x, self.shift_y, self.zoom_level)


class GraphicPose(object):
    """Graphical counterpart to the class :class:`Pose`. This class allows to save the :class:`_GraphicJoint` objects.

    .. versionadded:: 2.0

    Parameters
    ----------
    pose: Pose
        A Pose instance.

    graphic_window: WindowArea
        The window object, where to display the sequence.

    x_axis: str, optional
        Sets which axis should be matched to the x display axis (default `"x"`, can be `"y"` or `"z"` too).

    y_axis: str, optional
        Sets which axis should be matched to the y display axis (default `"y"`, can be `"x"` or `"z"` too).

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

    def __init__(self, pose, graphic_window, x_axis="x", y_axis="y", verbosity=1):
        self.pose = pose
        self.joints = {}
        self._load_joints(graphic_window, x_axis, y_axis, verbosity)

    def _load_joints(self, graphic_window, x_axis="x", y_axis="y", verbosity=1):
        """Creates :class:`_GraphicJoint` elements for each joint of the pose and add them to the :attr:`joints`
        attribute.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: WindowArea
            The window object, where to display the sequence.

        x_axis: str, optional
            Sets which axis should be matched to the x display axis (default `"x"`, can be `"y"` or `"z"` too).

        y_axis: str, optional
            Sets which axis should be matched to the y display axis (default `"y"`, can be `"x"` or `"z"` too).

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
            self.joints[joint_label] = GraphicJoint(self.pose.joints[joint_label], graphic_window, x_axis, y_axis,
                                                    verbosity)

    def show_line(self, graphic_window, connection, color_line, width_line, shift_x=0, shift_y=0, zoom_level=1):
        """Shows a single line between two joints specified in ``connection`` on the ``window`` object.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: WindowArea
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

        zoom_level: float, optional
            Defines the zoom level compared to the original view. A zoom level of 2 will make the joints appear twice as
            close.
        """

        try:
            joint1 = self.joints[connection[0]]
            joint2 = self.joints[connection[1]]

            if joint1.x is not None and joint1.y is not None and joint2.x is not None and joint2.y is not None:
                pygame.draw.line(graphic_window.window_area, color_line,
                                 ((joint1.x + shift_x) * zoom_level, (joint1.y + shift_y) * zoom_level),
                                 ((joint2.x + shift_x) * zoom_level, (joint2.y + shift_y) * zoom_level),
                                 width_line)

        except KeyError:
            pass

    def show(self, graphic_window, joint_surfaces, joints_to_show, connections_to_show, color_line, width_line,
             show_lines, shift_x=0, shift_y=0, zoom_level=1):
        """Displays the pose on the ``window`` object.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: WindowArea
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
            The number of pixels to shift the display of the joints on the vertical axis (default: 0).

        zoom_level: float, optional
            Defines the zoom level compared to the original view. A zoom level of 2 will make the joints appear twice as
            close.
            """

        if show_lines:
            for connection in connections_to_show:
                self.show_line(graphic_window, connection, color_line, width_line, shift_x, shift_y, zoom_level)
        for j in self.joints.keys():
            if j in joints_to_show and self.joints[j].x is not None and self.joints[j].y is not None:
                self.joints[j].show(graphic_window, joint_surfaces, shift_x, shift_y, zoom_level)


class GraphicJoint(object):
    """Graphical counterpart to the class :class:`Joint`. This class allows to convert the original coordinates and save
    them into graphical coordinates.

    .. versionadded:: 2.0

    Parameters
    ----------
    joint: Joint
        A Joint instance.

    graphic_window: WindowArea
        The window object, where to display the sequence.

    x_axis: str, optional
        Sets which axis should be matched to the x display axis (default `"x"`, can be `"y"` or `"z"` too).

    y_axis: str, optional
        Sets which axis should be matched to the y display axis (default `"y"`, can be `"x"` or `"z"` too).

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

    def __init__(self, joint, graphic_window, x_axis="x", y_axis="y", verbosity=1):
        self.joint = joint
        self.x = None
        self.y = None
        self.convert_coordinates(graphic_window, x_axis, y_axis, verbosity)

    def convert_coordinates(self, graphic_window, x_axis="x", y_axis="y", verbosity=1):
        """Converts the original coordinates into graphic coordinates.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: WindowArea
            The window object, where to display the sequence.

        x_axis: str, optional
            Sets which axis should be matched to the x display axis (default `"x"`, can be `"y"` or `"z"` too).

        y_axis: str, optional
            Sets which axis should be matched to the y display axis (default `"y"`, can be `"x"` or `"z"` too).

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        factor_x = 1
        factor_y = 1
        if x_axis[0] == "-":
            factor_x = -1
            x_axis = x_axis[1]
        if y_axis[0] == "-":
            factor_y = -1
            y_axis = y_axis[1]

        if self.joint.get_coordinate(x_axis) is not None:
            self.x = graphic_window.convert_x(factor_x * self.joint.get_coordinate(x_axis), 1)
            if verbosity > 1:
                print("\t\t\tCoordinate x (" + str(self.joint.x) + "): " + str(self.x))
        else:
            self.x = None

        if self.joint.get_coordinate(y_axis) is not None:
            self.y = graphic_window.convert_y(factor_y * self.joint.get_coordinate(y_axis), 1)
            if verbosity > 1:
                print("\t\t\tCoordinate y (" + str(self.joint.y) + "): " + str(self.y))
        else:
            self.y = None

    def rotate(self, graphic_window, yaw=0, pitch=0, roll=0):
        """Sets the attributes :attr:`x` and :attr:`y` given three rotations from the original coordinates: yaw, pitch
        and roll.

        .. versionadded:: 2.0

        Warning
        -------
        This function is experimental as of version 2.0.

        Parameters
        ----------
        graphic_window: WindowArea
            The window object, where to display the sequence.

        yaw: float, optional
            The angle of yaw, or rotation on the x-axis, in degrees (default: 0).

        pitch: float, optional
            The angle of pitch, or rotation on the y-axis, in degrees (default: 0).

        roll: float, optional
            The angle of roll, or rotation on the z axis, in degrees (default: 0).
        """
        rot_x, rot_y, rot_z = self.joint.rotate(yaw, pitch, roll)
        self.x = graphic_window.convert_x(rot_x, 1)
        self.y = graphic_window.convert_y(rot_y, 1)

    def show(self, graphic_window, joint_surfaces, shift_x=0, shift_y=0, zoom_level=1):
        """Displays the joint on the ``window`` surface.

        .. versionadded:: 2.0

        Parameters
        ----------
        graphic_window: WindowArea
            A GraphicWindow instance containing a `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
            element on which to display the sequence.

        joint_surfaces: dict(str: `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_)
            A dictionary containing the elements representing the joints that can be displayed.

        shift_x: int, optional
            The number of pixels to shift the display of the joints on the horizontal axis (default: 0).

        shift_y: int, optional
            The number of pixels to shift the display of the joints on the vertical axis (default: 0).

        zoom_level: float, optional
            Defines the zoom level compared to the original view. A zoom level of 2 will make the joints appear twice as
            close.
            """

        location = "_default"
        correction = "_default"

        if self.joint.is_randomized():
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

        if self.joint.is_corrected():
            correction = "_corrected"

        half_width = joint_surfaces["joint" + location + correction].get_width() // 2
        half_height = joint_surfaces["joint" + location + correction].get_height() // 2

        graphic_window.window_area.blit(joint_surfaces["joint" + location + correction],
                                        ((self.x + shift_x) * zoom_level - half_width,
                                    (self.y + shift_y) * zoom_level - half_height))


class Video(object):
    """This class allows to store and display a video in a :class:`WindowArea`.

    .. versionadded:: 2.0

    Parameters
    ----------
    path: str
        The path of the video file.

    resolution: tuple(int, int)
        The resolution of the window area, where the video should be displayed.

    timestamp_video_start: float or None, optional
        If specified, indicates what timestamp of the video (in seconds) matches the start of the sequence.

    Attributes
    ----------
    path: str
        The path of the video file.

    resolution: tuple(int, int)
        The resolution of the window area, where the video should be displayed.

    timestamp_video_start: float
        Indicates what timestamp of the video (in seconds) matches the start of the sequence (by default, set at 0).

    fps: float
        The framerate of the video.

    number_of_frames: int
        The number of frames in the video.

    current_frame_index: int
        The index of the frame currently displayed.

    current_frame_surface: `pygame.Surface <https://www.pygame.org/docs/ref/surface.html>`_
        A pygame Surface containing a frame of the video.

    time_next_frame: int
        The value of the timer at which the next frame should be displayed.

    video: cv2.VideoCapture
        A VideoCapture object.
    """

    def __init__(self, path, resolution, timestamp_video_start):
        self.path = path
        self.resolution = resolution
        if timestamp_video_start is None:
            self.timestamp_video_start = 0
        else:
            self.timestamp_video_start = timestamp_video_start
        self.play = True
        self.fps = 0
        self.number_of_frames = 0
        self.current_frame_index = 0
        self.current_frame_surface = None
        self.time_next_frame = 0
        self.frame_start = 0
        self.video = None
        self._load_video()

    def _load_video(self):
        """Loads the video upon creating the video object.

        .. versionadded:: 2.0
        """
        self.video = cv2.VideoCapture(self.path)
        if not self.video.isOpened():
            raise Exception("Error opening the video file")

        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.number_of_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.time_next_frame = 1 / self.fps * 1000
        self._set_frame_start()
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)
        self._load_frame()

    def _set_frame_start(self):
        self.frame_start = int(self.timestamp_video_start * self.fps)
        self.current_frame_index = self.frame_start

    def _load_frame(self):
        """Loads the next frame of the video and turns it in a pygame surface.

        .. versionadded:: 2.0
        """
        success, frame = self.video.read()
        frame = cv2.resize(frame, self.resolution, interpolation=cv2.INTER_AREA)
        self.current_frame_surface = pygame.image.frombuffer(frame.tobytes(), self.resolution, "BGR")

    def get_timestamp(self):
        """Returns the timestamp of the frame currently being displayed.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The timestamp of the frame currently being displayed, in milliseconds.
        """
        return self.current_frame_index * 1/self.fps * 1000

    def get_duration(self):
        """Returns the duration of the video, in seconds.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The duration of the video, in milliseconds.
        """
        return (self.number_of_frames - self.frame_start) / self.fps * 1000

    def get_number_of_frames(self):
        """Returns the total number of frames in the video.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The total number of frames in the video.
        """
        return self.number_of_frames - self.frame_start

    def get_fps(self):
        """Returns the framerate of the video.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The number of frames per second of the video.
        """
        return self.fps

    def get_current_frame_index(self):
        """Returns the index of the frame currently being displayed.

        .. versionadded:: 2.0

        Returns
        -------
        int
            The index of the frame currently being displayed.
        """
        return self.current_frame_index

    def set_frame_from_index(self, frame_index, verbosity=1):
        """Sets the frame to be displayed.

        .. versionadded:: 2.0

        Parameters
        ----------
        frame_index: int
            The index of the target frame.
        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        self.current_frame_index = frame_index
        if verbosity > 1:
            print("Frame " + str(frame_index+1) + " of " + str(self.number_of_frames))
        if self.current_frame_index == self.number_of_frames - 1:
            self.time_next_frame = -1
        else:
            self.time_next_frame = (self.current_frame_index - self.frame_start + 1) / self.fps * 1000
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_index)
        self._load_frame()

    def set_frame_from_timestamp(self, timestamp, method="lower", verbosity=1):
        """Sets the frame depending on a :class:`Timer` object.

        .. versionadded:: 2.0

        Parameters
        ----------
        timestamp: float
            A timestamp, in milliseconds.

        method: str
            Defines which frame is selected based on the timestamp.

            • If set on ``"closest"`` (default), the closest frame from the timestamp is selected.
            • If set on ``"below"``, ``"lower"`` or ``"under"``, the closest frame below the timestamp is selected.
            • If set on ``"above"``, ``"higher"`` or ``"over"``, the closest frame above the timestamp is selected.

        verbosity: int, optional
            Sets how much feedback the code will provide in the console output:

            • *0: Silent mode.* The code won’t provide any feedback, apart from error messages.
            • *1: Normal mode* (default). The code will provide essential feedback such as progression markers and
              current steps.
            • *2: Chatty mode.* The code will provide all possible information on the events happening. Note that this
              may clutter the output and slow down the execution.
        """
        if method in ["below", "lower", "under"]:
            frame_index = int(self.fps * timestamp / 1000) + self.frame_start
        elif method in ["above", "higher", "over"]:
            frame_index = math.ceil(self.fps * timestamp / 1000) + self.frame_start
        elif method == "closest":
            frame_index = round(self.fps * timestamp / 1000) + self.frame_start
        else:
            raise Exception('Invalid parameter "method": the value should be "lower", "higher" or "closest".')

        if frame_index >= self.number_of_frames:
            self.set_frame_from_index(self.number_of_frames - 1, verbosity)
        else:
            self.set_frame_from_index(frame_index, verbosity)

    def reset(self, verbosity=1):
        """Resets the video to the first frame.

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
        self.set_frame_from_index(self.frame_start, verbosity)
        self.time_next_frame = 1 / self.fps * 1000

    def next_frame(self):
        """Loads the next frame of the video, or resets the video if the last frame has been reached.

        .. versionadded:: 2.0
        """
        self.current_frame_index += 1
        self.time_next_frame += 1 / self.fps * 1000
        if self.current_frame_index < self.number_of_frames - 1:
            self._load_frame()

    def show_frame(self, window_area):
        """Shows the current :attr:`current_frame_surface` in a provided window_area, without updating the timer,
        compared to :meth:`show`.

        .. versionadded:: 2.0

        Parameters
        ----------
        window_area: WindowArea
            The :class:`WindowArea` instance where to blit the video frame.
        """
        window_area.blit(self.current_frame_surface, (0, 0))

    def show(self, window_area, timer):
        """Shows the current :attr:`current_frame_surface` in a provided window_area, and loads the next frame based
        on the timer.

        .. versionadded:: 2.0

        Parameters
        ----------
        window_area: WindowArea
            The :class:`WindowArea` instance where to blit the video frame.
        timer: Timer
            A :class:`Timer` instance.
        """

        while self.time_next_frame != -1 and timer.timer > self.time_next_frame:
            self.next_frame()
        window_area.blit(self.current_frame_surface, (0, 0))
