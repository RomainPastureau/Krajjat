#!/usr/bin/env python
"""Krajjat 1.10
Kinect Realignment Algorithm for Joint Jumps And Twitches
Author: Romain Pastureau
This file contains the main graphic classes, mainly converting
the classes from the "sequence.py" file to be able to show them
graphically.
"""
import os

import pygame
from pygame import *

__author__ = "Romain Pastureau"
__version__ = "1.10"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"

from pygame import gfxdraw

from tool_functions import load_joints_connections

# Colors
#colorJoint = (255, 216, 109)  # Color of the joints: yellow
colorJoint = (255, 255, 255)  # Color of the joints: white
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


class GraphicDisplay(object):
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

    def __init__(self, sequence, show_lines, ignore_bottom, start_pose, path_images, disp, scale=1):
        self.sequence = sequence  # Saves the original sequence
        self.display = disp  # Saves the display information
        self.poses = []  # Contains the graphic poses
        self.load_sequence(show_lines, ignore_bottom, path_images, disp, scale)
        self.time = Time()  # Creates a time variable
        self.reset()
        self.current_pose = start_pose

    def load_sequence(self, show_lines, ignore_bottom, path_images, disp, scale=1):
        """Turns a Sequence into a GraphicSequence"""
        print("Creating the graphic poses...")

        # Show percentage
        perc = 10
        has_images = None

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
        self.time.reset()

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
        if self.sequence.poses[self.current_pose + 1].get_relative_timestamp() * 1000 < self.time.get_time():
            self.next_pose()
        self.poses[self.current_pose].show(window, show_lines, show_image, shift_x, shift_y, type, color_joint, ratio)
        self.time.update()

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
        self.x = disp.convert_x(self.joint.x, scale)
        self.y = disp.convert_y(self.joint.y, scale)

    def show(self, window, shift_x=0, shift_y=0, type="square", color_joint="default", ratio=1):
        """Displays the joint"""

        if type == "square":
            self.show_square(window, shift_x, shift_y, color_joint, ratio)
        elif type == "circle":
            self.show_circle(window, shift_x, shift_y, color_joint, ratio)

    def show_square(self, window, shift_x=0, shift_y=0, color_joint="default", ratio=1):

        # Not randomized: apply special joint sizes for head and hands
        if self.joint.joint_type in ["Head", "HeadFront"] and not self.joint.randomized:
            if ratio == 1:
                p = ptHead
            else:
                p = pygame.Surface((sizeHead*ratio, sizeHead*ratio))
        elif self.joint.joint_type in ["HandRight", "HandLeft", "HandInRight", "HandInLeft"] and \
                not self.joint.randomized:
            if ratio == 1:
                p = ptHand
            else:
                p = pygame.Surface((sizeHand*ratio, sizeHand*ratio))

        # Randomized: apply special joint sizes for hip, left shoulder and mid-spine
        elif self.joint.joint_type in ["SpineMid", "Chest"] and self.joint.randomized:
            if ratio == 1:
                p = ptHead
            else:
                p = pygame.Surface((sizeHead*ratio, sizeHead*ratio))
        elif self.joint.joint_type in ["ShoulderLeft", "Neck", "ShoulderTopLeft", "HeadRight"] and \
                self.joint.randomized:
            if ratio == 1:
                p = ptHand
            else:
                p = pygame.Surface((sizeHand*ratio, sizeHand*ratio))

        # Other joints: regular size
        else:
            if ratio == 1:
                p = pt
            else:
                p = pygame.Surface((size*ratio, size*ratio))

        # If a joint is corrected or over threshold, change the color
        if color_joint == "default":
            if self.joint.corrected:
                p.fill(colorJointCorrected)
            elif self.joint.movement_over_threshold:
                p.fill(colorJointOverThreshold)
            else:
                p.fill(colorJoint)
        else:
            p.fill(color_joint)

        # Show the joint in the window
        window.blit(p, (shift_x + self.x - p.get_width() // 2, shift_y + self.y - p.get_height() // 2))

    def show_circle(self, window, shift_x=0, shift_y=0, color_joint="default", ratio=1):

        shift_head = 0

        # Not randomized: apply special joint sizes for head and hands
        if self.joint.joint_type in ["Head", "HeadFront"] and not self.joint.randomized:
            radius = sizeHead * ratio
            shift_head = 15
        elif self.joint.joint_type in ["HandRight", "HandLeft", "HandInRight", "HandInLeft"] and \
            not self.joint.randomized:
            radius = sizeHand * ratio

        # Randomized: apply special joint sizes for hip, left shoulder and mid-spine
        elif self.joint.joint_type == ["SpineMid", "Chest"] and self.joint.randomized:
            radius = sizeHead * ratio
        elif self.joint.joint_type in ["ShoulderLeft", "Neck", "ShoulderTopLeft", "HeadRight"] and \
                self.joint.randomized:
            radius = sizeHand * ratio

        # Other joints: regular size
        else:
            radius = size * ratio

        # If a joint is corrected or over threshold, change the color
        if color_joint == "default":
            if self.joint.corrected:
                color = colorJointCorrected
            elif self.joint.movement_over_threshold:
                color = colorJointOverThreshold
            else:
                color = colorJoint
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
        pygame.draw.line(window, colorLine, (self.startX + shift_x, self.startY + shift_y),
                         (self.endX + shift_x, self.endY + shift_y), lineWidth)