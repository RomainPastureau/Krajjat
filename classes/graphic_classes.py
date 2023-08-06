"""These classes allow to convert the data from :class:`Sequence`, :class:`Pose` and :class:`Joint` to display them
in the :doc:`graphic_functions`. All these classes and their methods should be considered private."""
import os
import pygame
from pygame import *
from pygame import gfxdraw

from tool_functions import load_joints_connections

# Colors
# colorJoint = (255, 216, 109)  # Color of the joints: yellow
COLOR_JOINT = (255, 255, 255)  # Color of the joints: white
COLOR_LINE = (93, 183, 247)  # Color of the lines: blue
COLOR_JOINT_CORRECTED = (0, 255, 0)  # Color of a joint that has been corrected: green
COLOR_JOINT_OVER_THRESHOLD = (255, 0, 0)  # Color of a joint with movement over threshold: red

# Sizes
SIZE_GJ = 10  # Size of the side of the squares for the joints
SIZE_GJ_HAND = 25  # Size of the side of the squares for the hands
SIZE_GJ_HEAD = 50  # Size of the side of the squares for the head
WIDTH_LINE = 10  # Width of the lines

# Surfaces
GJ = pygame.Surface((SIZE_GJ, SIZE_GJ))  # Surface for the joints
GJ_HAND = pygame.Surface((SIZE_GJ_HAND, SIZE_GJ_HAND))  # Surface for the hands
GJ_HEAD = pygame.Surface((SIZE_GJ_HEAD, SIZE_GJ_HEAD))  # Surface for the head

# Fill surfaces with the joint color
GJ.fill(COLOR_JOINT)
GJ_HAND.fill(COLOR_JOINT)
GJ_HEAD.fill(COLOR_JOINT)


class _GraphicWindow(object):
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
        self.pixel_meter_scale = self.height / height_window_in_meters

    def _convert_x(self, x, scale=1.0):
        """Converts the x "real" coordinate to a graphic coordinate to be displayed in the window.

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

    def _convert_y(self, y, scale=1):
        """Converts the y "real" coordinate to a graphic coordinate to be displayed in the window.

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


class _Timer(object):
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

    def _get_time(self):
        """Returns the value of the attribute :attr:`timer`.

        .. versionadded:: 2.0

        Returns
        -------
        float
            The time contained in the attribute :attr:`timer`, in milliseconds.
        """
        return self.timer

    def _reset(self):
        """Resets the timer to 0.

        .. versionadded:: 2.0
        """
        self.timer = 0

    def _update(self):
        """Adds the tick of the `pygame.time.Clock <https://www.pygame.org/docs/ref/time.html#pygame.time.Clock>`_
        object to the timer.

        .. versionadded:: 2.0
        """
        self.timer += self.clock.tick()


class _GraphicSequence(object):
    """Graphical counterpart to the class  :class:`Sequence`. This class allows to convert the original coordinates of
    the joints into graphical coordinates.

    .. versionadded:: 2.0

    Parameters
    ----------
    sequence: Sequence
        A Sequence instance.

    graphic_window: _GraphicWindow
        The window object, where to display the sequence.

    show_lines: bool, optional
        If set on `True` (default), the graphic sequence will include lines between certain joints, to create a
        skeleton. If set on `False`, only the joints will be displayed.

    ignore_bottom: bool
        If set on `True`, the joints below the waist will not be displayed. If set on `False` (default), all the joints
        will be displayed. For a complete list of joints being displayed or not, see
        :ref:`Display the sequence <ignore_bottom>`.

    start_pose: int, optional
        The index of the pose at which to start the sequence.

    path_images: list(str), str or None, optional

    """

    def __init__(self, sequence, graphic_window, show_lines=True, ignore_bottom=False, start_pose=0, path_images=None,
                 scale=1):
        self.sequence = sequence  # Saves the original sequence
        self.graphic_window = graphic_window  # Saves the display information
        self.poses = []  # Contains the graphic poses
        self.load_sequence(show_lines, ignore_bottom, path_images, graphic_window, scale)
        self.time = _Timer()  # Creates a time variable
        self.reset()
        self.current_pose = start_pose

    def load_sequence(self, show_lines, ignore_bottom, path_images, disp, scale=1):
        """Turns a Sequence into a GraphicSequence"""
        print("Creating the graphic poses...")

        # Show percentage
        perc = 10
        has_images = None
        images = []

        # Gets the images (in order of the number before the extension) if the path is not none
        if path_images != None:
            if os.path.isdir(path_images):
                has_images = "multiple"
                files = os.listdir(path_images)
                images = ["" for i in range(len(files))]
                for file in files:
                    if file.split(".")[-1] in ["png", "jpg", "bmp"]:
                        images[int(file.split(".")[0].split("_")[1])] = path_images+"/"+file
            else:
                has_images = "single"

        # Loads the poses and images
        for p in range(len(self.sequence.poses)):
            if p / len(self.sequence.poses) > perc / 100:
                print(str(perc) + "%", end=" ")
                perc += 10
            pose = self.sequence.poses[p]
            if has_images == "multiple":
                self.poses.append(GraphicPose(pose, show_lines, ignore_bottom, images[p], disp, scale))
            elif has_images == "single":
                self.poses.append(GraphicPose(pose, show_lines, ignore_bottom, path_images, disp, scale))
            else:
                self.poses.append(GraphicPose(pose, show_lines, ignore_bottom, None, disp, scale))
        print("100% - Done.")

    def next_pose(self):
        """Iterates the current pose; if we reach the last pose, we restart from the beginning"""
        self.current_pose += 1
        if self.current_pose == len(self.sequence) - 1:
            self.reset()
        #print("Pose " + str(self.current_pose + 1) + " of " + str(len(self.poses)))
            
    def previous_pose(self):
        self.current_pose -= 1
        if self.current_pose == len(self.sequence) - 1:
            self.current_pose = len(self.poses) - 1
        #print("Pose " + str(self.current_pose + 1) + " of " + str(len(self.poses)))

    def reset(self):
        """Resets the current pose as the first one, and the time"""
        self.current_pose = 0
        self.time._reset()

    def get_events(self, ev):
        """Allows to go to the next pose when pressing the Right key, and the previous when pressing the Left"""
        if ev.type == KEYDOWN and ev.key == K_RIGHT:
            self.current_pose = (self.current_pose + 1) % len(self.sequence)
            print("Current pose: " + str(self.current_pose + 1) + "/" + str(len(self.sequence)))
        elif ev.type == KEYDOWN and ev.key == K_LEFT:
            self.current_pose = (self.current_pose + 1) % len(self.sequence)
            print("Current pose: " + str(self.current_pose + 1) + "/" + str(len(self.sequence)))

    def show(self, window, show_lines, show_image=False, shift_x=0, shift_y=0, type="square", color_joint="default",
             ratio=1):
        """Shows all the joints of the current pose, and iterates the next pose"""
        if self.sequence.poses[self.current_pose + 1].get_relative_timestamp() * 1000 < self.time._get_time():
            self.next_pose()
        self.poses[self.current_pose].show(window, show_lines, show_image, shift_x, shift_y, type, color_joint, ratio)
        self.time._update()

    def show_pose(self, window, show_lines, show_image, shift_x=0, shift_y=0, type="square", color_joint="default",
                  ratio=1):
        """Shows just one pose without automatic time iteration"""
        self.poses[self.current_pose].show(window, show_lines, show_image, shift_x, shift_y, type, color_joint, ratio)


class GraphicPose(object):
    """Graphical counterpart to Pose: allows to convert the original coordinates into graphical coordinates"""

    def __init__(self, pose, show_lines, ignore_bottom, path_image, disp, scale=1):
        self.pose = pose  # Saves the original pose
        self.joints = {}  # Contains all the graphic joints
        self.image = None # Image to put below the joints
        self.load_joints(ignore_bottom, disp, scale)
        if show_lines:
            self.lines = []  # Contains the lines connecting the joints
            self.load_lines(ignore_bottom)
        if path_image != None:
            self.load_image(path_image, disp)

    def load_image(self, path_image, disp):
        #print("Loading image "+str(self.pose.no))
        image = pygame.image.load(path_image)
        image = pygame.transform.rotate(image, 180)
        self.image = pygame.transform.scale(image, (disp.width, disp.height))

    def load_joints(self, ignore_bottom, disp, scale=1):
        """Creates GraphicJoint elements for each joint of the pose"""
        for joint in self.pose.joints.keys():

            # If the variable ignore_bottom is true, we ignore the joints below the hips
            if not (ignore_bottom and joint in ["HipRight", "KneeRight", "AnkleRight", "FootRight",
                                                "HipLeft", "KneeLeft", "AnkleLeft", "FootLeft",
                                                "ThighRight", "ShinRight", "HeelRight", "ForefootOutRight",
                                                "ToetipRight", "ForefootInRight", "ThighLeft", "ShinLeft",
                                                "HeelLeft", "ForefootOutLeft", "ToetipLeft", "ForefootInLeft"]):
                self.joints[joint] = GraphicJoint(self.pose.joints[joint], disp, scale)

    def load_lines(self, ignore_bottom):
        """Creates and loads lines to join the joints"""
        connections = []

        # Kinect
        if "Head" in self.joints:
            connections = load_joints_connections("skeleton_connections_kinect_top.txt")
            if not ignore_bottom:  # If we don't ignore the joints below the hip, we add the lines connecting them
                connections += load_joints_connections("skeleton_connections_kinect_bottom.txt")

        # Qualisys
        elif "HeadTop" in self.joints:
            connections = load_joints_connections("skeleton_connections_qualisys_top.txt")
            if not ignore_bottom:  # If we don't ignore the joints below the hip, we add the lines connecting them
                connections += load_joints_connections("skeleton_connections_qualisys_bottom.txt")

        for connection in connections:
            self.lines.append(GraphicLine(self.joints[connection[0]], self.joints[connection[1]]))

    def show(self, window, show_lines, show_image, shift_x=0, shift_y=0, type="square", color_joint="default",
             ratio=1):
        """Shows a pose, with or without the lines"""
        if show_image and self.image != None:
            window.blit(self.image, (0, 0))
        if show_lines:
            for line in self.lines:
                line.show(window, shift_x=shift_x, shift_y=shift_y)
        for j in self.joints.keys():
            self.joints[j].show(window, shift_x, shift_y, type, color_joint, ratio)


class GraphicJoint(object):
    """Graphical counterpart to Joint: allows to convert the original coordinates into graphical coordinates"""

    def __init__(self, joint, disp, scale=1):
        self.joint = joint  # Saves the original joint
        self.x = None
        self.y = None
        self.convert(disp, scale)

    def convert(self, disp, scale=1):
        """Converts the original coordinate into graphic coordinate"""
        self.x = disp._convert_x(self.joint.x, scale)
        self.y = disp._convert_y(self.joint.y, scale)

    def show(self, window, shift_x=0, shift_y=0, type="square", color_joint="default", ratio=1):
        """Displays the joint"""

        if type == "square":
            self.show_square(window, shift_x, shift_y, color_joint, ratio)
        elif type == "circle":
            self.show_circle(window, shift_x, shift_y, color_joint, ratio)

    def show_square(self, window, shift_x=0, shift_y=0, color_joint="default", ratio=1):

        # Not randomized: apply special joint sizes for head and hands
        if self.joint.joint_label in ["Head", "HeadFront"] and not self.joint._is_randomized:
            if ratio == 1:
                p = GJ_HEAD
            else:
                p = pygame.Surface((SIZE_GJ_HEAD * ratio, SIZE_GJ_HEAD * ratio))
        elif self.joint.joint_label in ["HandRight", "HandLeft", "HandInRight", "HandInLeft"] and \
                not self.joint._is_randomized:
            if ratio == 1:
                p = GJ_HAND
            else:
                p = pygame.Surface((SIZE_GJ_HAND * ratio, SIZE_GJ_HAND * ratio))

        # Randomized: apply special joint sizes for hip, left shoulder and mid-spine
        elif self.joint.joint_label in ["SpineMid", "Chest"] and self.joint._is_randomized:
            if ratio == 1:
                p = GJ_HEAD
            else:
                p = pygame.Surface((SIZE_GJ_HEAD * ratio, SIZE_GJ_HEAD * ratio))
        elif self.joint.joint_label in ["ShoulderLeft", "Neck", "ShoulderTopLeft", "HeadRight"] and \
                self.joint._is_randomized:
            if ratio == 1:
                p = GJ_HAND
            else:
                p = pygame.Surface((SIZE_GJ_HAND * ratio, SIZE_GJ_HAND * ratio))

        # Other joints: regular size
        else:
            if ratio == 1:
                p = GJ
            else:
                p = pygame.Surface((SIZE_GJ * ratio, SIZE_GJ * ratio))

        # If a joint is corrected or over threshold, change the color
        if color_joint == "default":
            if self.joint._is_corrected:
                p.fill(COLOR_JOINT_CORRECTED)
            elif self.joint._has_velocity_over_threshold:
                p.fill(COLOR_JOINT_OVER_THRESHOLD)
            else:
                p.fill(COLOR_JOINT)
        else:
            p.fill(color_joint)

        # Show the joint in the window
        window.blit(p, (shift_x + self.x - p.get_width() // 2, shift_y + self.y - p.get_height() // 2))

    def show_circle(self, window, shift_x=0, shift_y=0, color_joint="default", ratio=1):

        shift_head = 0

        # Not randomized: apply special joint sizes for head and hands
        if self.joint.joint_label in ["Head", "HeadFront"] and not self.joint._is_randomized:
            radius = SIZE_GJ_HEAD * ratio
            shift_head = 15
        elif self.joint.joint_label in ["HandRight", "HandLeft", "HandInRight", "HandInLeft"] and \
            not self.joint._is_randomized:
            radius = SIZE_GJ_HAND * ratio

        # Randomized: apply special joint sizes for hip, left shoulder and mid-spine
        elif self.joint.joint_label == ["SpineMid", "Chest"] and self.joint._is_randomized:
            radius = SIZE_GJ_HEAD * ratio
        elif self.joint.joint_label in ["ShoulderLeft", "Neck", "ShoulderTopLeft", "HeadRight"] and \
                self.joint._is_randomized:
            radius = SIZE_GJ_HAND * ratio

        # Other joints: regular size
        else:
            radius = SIZE_GJ * ratio

        # If a joint is corrected or over threshold, change the color
        if color_joint == "default":
            if self.joint._is_corrected:
                color = COLOR_JOINT_CORRECTED
            elif self.joint._has_velocity_over_threshold:
                color = COLOR_JOINT_OVER_THRESHOLD
            else:
                color = COLOR_JOINT
        else:
            color = color_joint

        # Show the joint in the window
        gfxdraw.aacircle(window, int(self.x + shift_x), int(self.y + shift_y) + shift_head, int(radius//2), color)
        gfxdraw.filled_circle(window, int(self.x + shift_x), int(self.y + shift_y) + shift_head, int(radius//2), color)

class GraphicLine(object):
    """Class defining lines between joints"""

    def __init__(self, joint1, joint2):
        self.startX = joint1.x
        self.startY = joint1.y
        self.endX = joint2.x
        self.endY = joint2.y

    def show(self, window, shift_x=0, shift_y=0):
        """Draws a line joining two joints"""
        pygame.draw.line(window, COLOR_LINE, (self.startX + shift_x, self.startY + shift_y),
                         (self.endX + shift_x, self.endY + shift_y), WIDTH_LINE)
