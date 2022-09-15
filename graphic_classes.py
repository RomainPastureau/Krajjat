#!/usr/bin/env python
"""Krajjat 1.6
Kinect Realignment Algorithm for Joint Jumps And Twitches
Author: Romain Pastureau
This file contains the main graphic classes, mainly converting
the classes from the "classes.py" file to be able to show them
graphically.
"""

import pygame
from pygame import *

__author__ = "Romain Pastureau"
__version__ = "1.6"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"

# Constants

# Colors
colorJoint = (255, 216, 109)  # Color of the joints: yellow
colorLine = (93, 183, 247)  # Color of the lines: blue
colorJointCorrected = (0, 255, 0)  # Color of a joint that has been corrected: green
colorJointOverThreshold = (255, 0, 0)  # Color of a joint with movement over threshold: red

# Sizes
size = 10  # Size of the side of the squares for the joints
sizeHand = 25  # Size of the side of the squares for the hands
sizeHead = 50  # Size of the side of the squares for the head
lineWidth = 10  # Width of the lines

# Surfaces
pt = pygame.Surface((size, size))  # Surface for the joints
ptHand = pygame.Surface((sizeHand, sizeHand))  # Surface for the hands
ptHead = pygame.Surface((sizeHead, sizeHead))  # Surface for the head

# Fill surfaces with the joint color
pt.fill(colorJoint)
ptHand.fill(colorJoint)
ptHead.fill(colorJoint)


class Display(object):
    """Contains the information of the window to produce the GUI"""

    def __init__(self, window):
        self.window = window
        self.width = window.get_width()
        self.height = window.get_height()
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.scale = 300

    def convert_x(self, x, scale=1):
        return int(self.center_x - x * self.scale * scale)

    def convert_y(self, y, scale=1):
        return int(self.center_y - y * self.scale * scale)


class Time(object):
    """Allows to set a timer"""

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.timer = 0

    def get_time(self):
        return self.timer

    def reset(self):
        self.timer = 0

    def update(self):
        tick = self.clock.tick()
        self.timer += tick


class GraphicSequence(object):
    """Graphical counterpart to Sequence: allows to convert the original coordinates into graphical coordinates"""

    def __init__(self, sequence, show_lines, ignore_bottom, start_pose, disp):
        self.sequence = sequence  # Saves the original sequence
        self.display = disp  # Saves the display information
        self.poses = []  # Contains the graphic poses
        self.load_sequence(show_lines, ignore_bottom, display)
        self.time = Time()  # Creates a time variable
        self.reset()
        self.currentPose = start_pose

    def load_sequence(self, show_lines, ignore_bottom, disp):
        """Turns a Sequence into a GraphicSequence"""
        for pose in self.sequence.poses:
            self.poses.append(GraphicPose(pose, show_lines, ignore_bottom, disp))

    def next_pose(self):
        """Iterates the current pose; if we reach the last pose, we restart from the beginning"""
        self.currentPose += 1
        if self.currentPose == len(self.sequence) - 1:
            self.reset()

    def reset(self):
        """Resets the current pose as the first one, and the time"""
        self.currentPose = 0
        self.time.reset()

    def get_events(self, ev):
        """Allows to go to the next pose when pressing the Right key, and the previous when pressing the Left"""
        if ev.type == KEYDOWN and ev.key == K_RIGHT:
            self.currentPose = (self.currentPose + 1) % len(self.sequence)
            print("Current pose: " + str(self.currentPose + 1) + "/" + str(len(self.sequence)))
        elif ev.type == KEYDOWN and ev.key == K_LEFT:
            self.currentPose = (self.currentPose + 1) % len(self.sequence)
            print("Current pose: " + str(self.currentPose + 1) + "/" + str(len(self.sequence)))

    def show(self, window, show_lines, show_image=False, shift_x=0, shift_y=0):
        """Shows all the joints of the current pose, and iterates the next pose"""
        if self.sequence.poses[self.currentPose + 1].get_relative_time() * 1000 < self.time.get_time():
            self.next_pose()
        self.poses[self.currentPose].show(window, show_lines, show_image, shift_x, shift_y)
        self.time.update()

    def show_pose(self, window, show_lines, show_image, shift_x=0, shift_y=0):
        """Shows just one pose without automatic time iteration"""
        self.poses[self.currentPose].show(window, show_lines, show_image, shift_x, shift_y)


class GraphicPose(object):
    """Graphical counterpart to Pose: allows to convert the original coordinates into graphical coordinates"""

    def __init__(self, pose, show_lines, ignore_bottom, disp):
        self.pose = pose  # Saves the original pose
        self.joints = {}  # Contains all the graphic joints
        self.load_joints(ignore_bottom, disp)
        if show_lines:
            self.lines = []  # Contains the lines connecting the joints
            self.load_lines(ignore_bottom)

    def load_joints(self, ignore_bottom, disp):
        """Creates GraphicJoint elements for each joint of the pose"""
        for joint in self.pose.joints.keys():

            # If the variable ignore_bottom is true, we ignore the joints below the hips
            if not (ignore_bottom and joint in ["KneeRight", "AnkleRight", "FootRight",
                                                "KneeLeft", "AnkleLeft", "FootLeft"]):
                self.joints[joint] = GraphicJoint(self.pose.joints[joint], disp)

    def load_lines(self, ignore_bottom):
        """Creates and loads lines to join the joints"""
        self.lines.append(GraphicLine(self.joints["Head"], self.joints["Neck"]))
        self.lines.append(GraphicLine(self.joints["Neck"], self.joints["SpineShoulder"]))
        self.lines.append(GraphicLine(self.joints["SpineShoulder"], self.joints["SpineMid"]))
        self.lines.append(GraphicLine(self.joints["SpineMid"], self.joints["SpineBase"]))

        self.lines.append(GraphicLine(self.joints["SpineShoulder"], self.joints["ShoulderRight"]))
        self.lines.append(GraphicLine(self.joints["ShoulderRight"], self.joints["ElbowRight"]))
        self.lines.append(GraphicLine(self.joints["ElbowRight"], self.joints["WristRight"]))
        self.lines.append(GraphicLine(self.joints["WristRight"], self.joints["HandRight"]))

        self.lines.append(GraphicLine(self.joints["SpineShoulder"], self.joints["ShoulderLeft"]))
        self.lines.append(GraphicLine(self.joints["ShoulderLeft"], self.joints["ElbowLeft"]))
        self.lines.append(GraphicLine(self.joints["ElbowLeft"], self.joints["WristLeft"]))
        self.lines.append(GraphicLine(self.joints["WristLeft"], self.joints["HandLeft"]))

        self.lines.append(GraphicLine(self.joints["SpineBase"], self.joints["HipRight"]))
        self.lines.append(GraphicLine(self.joints["SpineBase"], self.joints["HipLeft"]))

        # If we don't ignore the joints below the hip, we add the lines connecting these joints
        if not ignore_bottom:
            self.lines.append(GraphicLine(self.joints["HipRight"], self.joints["KneeRight"]))
            self.lines.append(GraphicLine(self.joints["KneeRight"], self.joints["AnkleRight"]))
            self.lines.append(GraphicLine(self.joints["AnkleRight"], self.joints["FootRight"]))

            self.lines.append(GraphicLine(self.joints["HipLeft"], self.joints["KneeLeft"]))
            self.lines.append(GraphicLine(self.joints["KneeLeft"], self.joints["AnkleLeft"]))
            self.lines.append(GraphicLine(self.joints["AnkleLeft"], self.joints["FootLeft"]))

    def show(self, window, show_lines, shift_x=0, shift_y=0):
        """Shows a pose, with or without the lines"""
        if show_lines:
            for line in self.lines:
                line.show(window, shift_x=shift_x, shift_y=shift_y)
        for j in self.joints.keys():
            self.joints[j].show(window, shift_x, shift_y)


class GraphicJoint(object):
    """Graphical counterpart to Joint: allows to convert the original coordinates into graphical coordinates"""

    def __init__(self, joint, disp):
        self.joint = joint  # Saves the original joint
        self.x = None
        self.y = None
        self.convert(disp)

    def convert(self, disp):
        """Converts the original coordinate into graphic coordinate"""
        self.x = disp.convert_x(self.joint.x)
        self.y = disp.convert_y(self.joint.y)

    def show(self, window, shift_x=0, shift_y=0):
        """Displays the joint"""

        # Not randomized: apply special joint sizes for head and hands
        if self.joint.joint_type == "Head" and not self.joint.randomized:
            p = ptHead
        elif self.joint.joint_type in ["HandRight", "HandLeft"] and not self.joint.randomized:
            p = ptHand

        # Randomized: apply special joint sizes for hip, left shoulder and mid-spine
        elif self.joint.joint_type == "HipLeft" and self.joint.randomized:
            p = ptHead
        elif self.joint.joint_type in ["ShoulderLeft", "SpineMid"] and self.joint.randomized:
            p = ptHand

        # Other joints: regular size
        else:
            p = pt

        # If a joint is corrected or over threshold, change the color
        if self.joint.corrected:
            p.fill(colorJointCorrected)
        elif self.joint.move_much:
            p.fill(colorJointOverThreshold)
        else:
            p.fill(colorJoint)

        # Show the joint in the window
        window.blit(p, (shift_x + self.x - p.get_width() // 2, shift_y + self.y - p.get_height() // 2))


class GraphicLine(object):
    """Class defining lines between joints"""

    def __init__(self, joint1, joint2):
        self.startX = joint1.x
        self.startY = joint1.y
        self.endX = joint2.x
        self.endY = joint2.y

    def show(self, window, shift_x=0, shift_y=0):
        """Draws a line joining two joints"""
        pygame.draw.line(window, colorLine, (self.startX + shift_x, self.startY + shift_y),
                         (self.endX + shift_x, self.endY + shift_y), lineWidth)
