#!/usr/bin/env python
"""Krajjat 1.6
Kinect Realignment Algorithm for Joint Jumps And Twitches
Author: Romain Pastureau
This file contains all the classes used by the other files,
along with the realignment algorithm.
"""

import copy
import json
import math
import os
import random

__author__ = "Romain Pastureau"
__version__ = "1.6"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"


class Sequence(object):
    """Defines a motion sequence by opening an existing one or creating a new."""

    def __init__(self, folder):
        self.files = None  # List of the files in the target folder
        self.poses = []  # List of the poses in the sequence, ordered
        self.randomized = False  # Is necessary?

        # In the case where a folder is passed as argument,
        # we load the sequence
        if folder is not None:
            self.folder = folder
            self.get_files()  # Fetches all the .json files
            self.load_poses()  # Loads the .json files into poses
            self.load_relative_timestamps()  # Sets the relative time from the first pose for each pose

        self.calculate_velocity()

    def get_files(self):
        """Opens a folder and fetches all the .json files."""

        file_list: list[str] | list[bytes] = os.listdir(self.folder)  # List all the files in the folder
        self.files = ["" for _ in range(len(file_list))]  # Create an empty list the length of the files

        # Variable checking if a ".meta" file was found in the folder, ensuring its integrity.
        # All Kinect recordings must come with a .meta file containing all the timestamps for
        # the files contained in the folder.
        meta_found = False
        size = None

        # Here, we find all the files that are either .json or .meta in the folder.
        for f in file_list:

            # If a file is ".json", then we get its index from its name to order it correctly in the list.
            # This is necessary as some file systems will order frame_2.json after frame_11.json because,
            # alphabetically, "1" is before "2".
            if f[-4:] == "json":
                self.files[int(f.split(".")[0].split("_")[1])] = f

            # Here, we just check that there is indeed a ".meta" file in the folder, as a sign of integrity
            # of the data.
            elif f[-4:] == "meta":
                meta_found = True
                # Get the number of frames in the .meta file to compare it with the number of files in the folder.
                size = self.get_meta(f)

                # If there were files that weren't ".json" in the folder, then "self.files" is larger than the number of
        # frames. The list is thus ending by a series of empty strings that we trim.
        if "" in self.files:
            limit = self.files.index("")
            self.files = self.files[0:limit]

            # If no ".meta" file was found, we consider the folder integrity as being false.
            if not meta_found:
                raise Exception(".meta file not found.")

            # Otherwise, we compare that the number of frames announced by the .meta file is indeed equal to the
            # number of .json files. If it is not, we return an Exception.
            else:
                if size > len(self.files):
                    raise Exception("According to the .meta file, some .json files are " +
                                    "missing. The .meta file lists " + str(size) + " file(s) while " +
                                    str(len(self.files)) + " .json file(s) have been found.")

        print(str(len(self.files)) + " pose file(s) found.\n")

    def get_meta(self, file):
        """Opens the .meta file from a folder, and counts the amount of lines, which should reflect the amount
        of frames, and thus the amount of files. This allows to check the integrity of the data."""
        f = open(self.folder + "/" + file, "r")
        fileread = f.read().split("\n")
        f.close()
        return len(fileread)

    def load_poses(self, verbose=True):
        """Opens successively all the .json files, read them and creates a Pose object for each of them.
        If verbose is True, returns a progression percentage every 10%."""

        if verbose:
            print("Opening poses...")

        perc = 10  # Used for the progression percentage
        for i in range(len(self.files)):

            # Show percentage if verbose
            if verbose and i / len(self.files) > perc / 100:
                print(str(perc) + "%", end=" ")
                perc += 10

            # Create the Pose object, passes as parameter the index and the file path
            pose = Pose(i, self.folder + "/" + self.files[i])
            self.poses.append(pose)

        if verbose:
            print("100% - Done.\n")

    def load_relative_timestamps(self):
        """For all the poses, sets the relative time from the first pose, by subtracting the absolute UNIX time
        of the first pose from the absolute UNIX time of every pose."""
        t = self.poses[0].get_timestamp()
        for f in self.poses:
            f.set_relative_timestamp(t)
            
    def calculate_velocity(self):
        """Calculates the distance travelled by each joint between two poses, and divides it by the time elapsed
        between the poses."""

        for p in range(1, len(self.poses)):  # For each pose

            for j in self.poses[0].joints.keys():  # For each joint
                velocity = self.get_velocity(self.poses[p - 1], self.poses[p], j)  # Get the velocity
                self.poses[p].joints[j].set_velocity(velocity)  # Set the velocity

    def get_velocity(self, pose1, pose2, joint):
        """Given two poses and a joint, returns the velocity of the joint between the two poses. To do so, this
        function calculates the distance travelled by the joint between the two poses and divides it by the
        time elapsed between the two poses. The returned value is in cm/s."""

        # Get the distance travelled by a joint between two poses (meters)
        dist = self.get_distance(pose1.joints[joint], pose2.joints[joint])

        # Get the time elapsed between two poses (hundreds of seconds)
        delay = self.get_delay(pose1, pose2) / 1000000000

        # Calculate the velocity (meters per hundreds of seconds, or centimeters per second)
        velocity = dist / delay

        return velocity

    @staticmethod
    def get_distance(joint_a, joint_b):
        """Uses the Euclidian formula to calculate the distance between two joints. This can be used to calculate
        the distance travelled by one joint between two poses, or the distance between two joints on the same pose."""
        x = (joint_b.x - joint_a.x) ** 2
        y = (joint_b.y - joint_a.y) ** 2
        z = (joint_b.z - joint_a.z) ** 2

        return math.sqrt(x + y + z)

    @staticmethod
    def get_delay(frame_a, frame_b):
        """Returns the delay between two poses, in tenths of microsecond (10^-7)."""
        time_a = frame_a.get_timestamp()
        time_b = frame_b.get_timestamp()
        return time_b - time_a

    @staticmethod
    def get_x(joint):
        """Returns the x value of a joint."""
        return joint.x

    @staticmethod
    def get_y(joint):
        """Returns the y value of a joint."""
        return joint.y

    @staticmethod
    def get_z(joint):
        """Returns the z value of a joint."""
        return joint.z

    def realign(self, velocity_threshold, window, verbose=True):
        """Realignment function: detects twitches and jumps in a sequence, corrects them linearly and outputs
        a new realigned sequence. For more information on how the realignment is performed, see the documentation."""

        # Create an empty sequence, the same length in poses as the original, just keeping the timestamp information
        # for each pose.
        new_sequence = self.create_empty_sequence()

        # If verbose, show all the information. Else, show only the progress in percentage.
        print("Starting realignment...")

        # Define the counters
        realigned_points = 0
        perc = 10

        # For every pose starting on the second one
        for p in range(1, len(self.poses)):

            if verbose:
                print("\nNew sequence:\n" + str(new_sequence.poses[p - 1]))
                print("\n== POSE NUMBER " + str(p + 1) + " ==")

            if not verbose and p / len(self.poses) > perc / 100:
                print(str(perc) + "%", end=" ")
                perc += 10

            # For every joint
            for j in self.poses[0].joints.keys():

                # We get the cm/s travelled by the joint between this pose and the previous
                velocity_before = self.get_velocity(new_sequence.poses[p - 1], self.poses[p], j)

                if verbose:
                    print(j + ": " + str(velocity_before))

                # If we already corrected this joint, we ignore it to avoid overcorrection
                if j in new_sequence.poses[p].joints:

                    if verbose:
                        print("\tAlready corrected.")

                # If the velocity is over threshold, we check if it is a jump or a twitch
                elif velocity_before > velocity_threshold and p != len(self.poses) - 1:

                    if verbose:
                        print("\tVelocity over threshold. Check in subsequent poses...")

                    # We check the next poses (defined by the window) if the position of the joint comes back below
                    # threshold
                    for k in range(p, min(p + window, len(self.poses))):

                        if verbose:
                            print("\t\tPose " + str(k + 1) + ":", end=" ")

                        # Method 1 (original): get the subsequent velocities
                        velocity = self.get_velocity(new_sequence.poses[p - 1], self.poses[k], j)

                        # Method 2 (to test): get the distance over the time between the two first joints
                        # dist = self.get_distance(new_sequence.poses[p - 1].joints[joint], self.poses[k].joints[joint])
                        # delay = self.get_delay(new_sequence.poses[p - 1], new_sequence.poses[p]) / 1000000000
                        # velocity = dist / delay

                        # Twitch case: One of the poses of the window is below threshold compared to previous pose.
                        if velocity < velocity_threshold:

                            if verbose:
                                print("no threshold deviation compared to pose " + str(p + 1) + ".")
                                print("\t\t\tCorrecting for twitch...")

                            new_sequence, realigned_points = self.correction(new_sequence, p - 1, k,
                                                                             j, realigned_points, verbose)

                            break

                        # Jump case: No pose of the window is below threshold.
                        elif k == p + window - 1 or k == len(self.poses) - 1:

                            if verbose:
                                print("original deviation not found.")
                                print("\t\t\tCorrecting for jump...")

                            new_sequence, realigned_points = self.correction(new_sequence, p - 1, k,
                                                                             j, realigned_points, verbose)

                            break

                        # Wait: if there are still poses in the window, we continue.
                        else:

                            if verbose:
                                print("still over threshold.")

                    if verbose:
                        print("")

                # If we're still in threshold, there is no correction, we copy the joint
                else:

                    joint = self.copy_joint(p, j)
                    new_sequence.poses[p].add_joint(j, joint)
                    new_sequence.poses[p].joints[j].corrected = False

        print("100% - Done.\n")
        print("Realignment over. " + str(realigned_points) + " point(s) realigned over " + str(
            len(self.poses) * len(list(self.poses[0].joints.keys()))) + ".\n")

        return new_sequence

    def correction(self, new_sequence, start_pose_number, end_pose_number, joint_number, realigned_points, verbose):
        """Performs a jump or twitch correction"""

        # We extract the data from the joints at the beginning and at the end of the partial sequence to correct
        joint_before = new_sequence.poses[start_pose_number].joints[joint_number]
        joint_after = self.poses[end_pose_number].joints[joint_number]

        # If the starting and ending joint are the same, we don't correct, it means it is the last pose of the sequence
        if start_pose_number == end_pose_number:
            joint = self.copy_joint(start_pose_number, joint_number)
            new_sequence.poses[start_pose_number].add_joint(joint_number, joint)

            if verbose:
                print("\t\t\t\tDid not corrected joint " + str(start_pose_number) +
                      " as it is the last pose of the sequence.")

        # Otherwise we correct for all the intermediate joints
        for pose_number in range(start_pose_number + 1, end_pose_number):

            # If a joint was already corrected we don't correct it to avoid overcorrection
            if self.poses[pose_number].joints[joint_number].corrected:

                if verbose:
                    print("\t\t\t\tDid not corrected joint " + str(pose_number + 1) + " as it was already corrected.")

            # Otherwise we correct it
            else:

                # We get the new coordinates
                x, y, z = self.correct_joint(joint_before, joint_after, start_pose_number, pose_number, end_pose_number,
                                             verbose)

                # We copy the original joint, apply the new coordinates and add it to the new sequence
                joint = self.copy_joint(pose_number, joint_number)
                joint.correct_joint(x, y, z)
                new_sequence.poses[pose_number].add_joint(joint_number, joint)

                if verbose:
                    print("\t\t\t\tCorrecting joint: " + str(pose_number + 1) + ". Original coordinates: (" + str(
                        self.poses[pose_number].joints[joint_number].x) +
                          ", " + str(self.poses[pose_number].joints[joint_number].y) + ", " + str(
                        self.poses[pose_number].joints[joint_number].z) + ")")
                    print("\t\t\t\tPrevious joint: " + str(start_pose_number + 1) + ". (" + str(
                        new_sequence.poses[start_pose_number].joints[joint_number].x) +
                          ", " + str(new_sequence.poses[start_pose_number].joints[joint_number].y) + ", " + str(
                        new_sequence.poses[start_pose_number].joints[joint_number].z) + ")")
                    print("\t\t\t\tNext joint: " + str(end_pose_number + 1) + ". (" + str(
                        self.poses[end_pose_number].joints[joint_number].x) +
                          ", " + str(self.poses[end_pose_number].joints[joint_number].y) + ", " + str(
                        self.poses[end_pose_number].joints[joint_number].z) + ")")
                    print("\t\t\t\tCorrected joint " + str(pose_number + 1) + ". New coordinates: (" + str(
                        x) + ", " + str(y) + ", " + str(z) + ")\n")

                # To count the number of joints that were realigned overall
                realigned_points += 1

        return new_sequence, realigned_points

    def correct_joint(self, joint_before, joint_after, pose_before, pose_current, pose_after, verbose):
        """Corrects one single joint (depending on the time between frames)"""

        # We calculate the percentage of time elapsed between the pose at the beginning of the partial sequence to
        # correct and the pose at the end
        percentage_time = (self.poses[pose_current].timestamp - self.poses[pose_before].timestamp) / (
                self.poses[pose_after].timestamp - self.poses[pose_before].timestamp)

        if verbose:
            print("\t\t\t\tJoint " + str(pose_current + 1) + " positioned at " + str(
                percentage_time * 100) + " % between poses " + str(pose_before + 1) + " and " + str(
                pose_after + 1) + ".")

        # We correct linearly every joint. See the documentation for more precision.
        x = joint_before.x - percentage_time * (joint_before.x - joint_after.x)
        y = joint_before.y - percentage_time * (joint_before.y - joint_after.y)
        z = joint_before.z - percentage_time * (joint_before.z - joint_after.z)

        return x, y, z

    def create_empty_sequence(self, verbose=True):
        """Creates an empty sequence with empty poses and empty joints, with the same number of poses as
        the sequence in which it is created. The only data kept for the poses is the timestamp and relative
        timestamp."""

        if verbose:
            print("Creating an empty sequence...")
        new_sequence: Sequence = Sequence(None)

        # Used for the progression percentage
        perc = 10
        for p in range(len(self.poses)):

            # Show percentage if verbose
            if verbose and p / len(self.poses) > perc / 100:
                print(str(perc) + "%", end=" ")
                perc += 10

            pose = self.poses[p].get_clear_copy()  # Creates an empty pose with the same timestamp as the original
            new_sequence.poses.append(pose)  # Add to the sequence

        new_sequence = self.copy_pose(new_sequence, 0)

        if verbose:
            print("100% - Done.\n")

        return new_sequence

    def copy_pose(self, sequence, pose_number):
        """Copies the joints from a pose that doesn't already exist in the target sequence"""

        for i in self.poses[pose_number].joints.keys():  # For every joint

            # If this joint doesn't already exist in the new sequence, we copy it
            if i not in sequence.poses[pose_number].joints.keys():
                sequence.poses[pose_number].joints[i] = self.copy_joint(pose_number, i)

        return sequence

    def copy_joint(self, pose_number, joint_name):
        """Creates a copy of a single joint and returns it"""

        joint = copy.copy(self.poses[pose_number].get_joint(joint_name))

        return joint

    def get_timestamps(self):
        """Returns a list of all the timestamps (relative) from the poses"""

        timestamps = []
        for pose in self.poses:
            timestamps.append(pose.get_relative_timestamp())

        return timestamps
    
    def print_json(self, pose):
        """Print the original json data from a pose"""
        data = self.poses[pose].get_json_data()
        print(json.dumps(data, indent=4))

    def print_pose(self, pose):
        """Prints all the information relative to one pose"""
        txt = "Pose " + str(pose + 1) + " of " + str(len(self.poses)) + "\n"
        txt += str(self.poses[pose])
        print(txt)

    def randomize(self):
        """Randomizes the joints"""

        # Get the starting positions of all joints
        starting_positions = []
        for joint in self.poses[0].joints.keys():
            starting_positions.append(copy.copy(self.poses[0].joints[joint]))

        # Randomize new starting positions for joints
        randomized_positions = self.generate_random_joints()
        random.shuffle(randomized_positions)

        # Assign these new starting positions to the joints and moves the joints in every subsequent pose
        # in relation to the new starting positions
        joints_list = list(self.poses[0].joints.keys())
        for p in self.poses:
            for j in range(len(joints_list)):
                p.joints[joints_list[j]].move_joint_randomized(starting_positions[j], randomized_positions[j])
        self.randomized = True

    @staticmethod
    def generate_random_joints():
        """Creates uniform, random positions for the joints"""
        random_joints = []
        for i in range(21):
            x = random.uniform(-0.2, 0.2)
            y = random.uniform(-0.5, 0.5)
            z = random.uniform(-0.5, 0.5)
            j = Joint(None, [x, y, z])
            random_joints.append(j)
        return random_joints

    def __len__(self):
        """Return the amount of poses in the sequence"""
        return len(self.poses)


class Pose(object):
    """Defines a pose (frame) pertaining to a motion sequence."""

    def __init__(self, no, file):
        self.no = no  # Index of the pose in the sequence
        self.joints = {}  # Dictionary of joint objects
        self.timestamp = None  # Original timestamp of the pose
        self.relative_timestamp = None  # Timestamp relative to the first pose

        # If we create a pose from a file, we read it
        if file is not None:
            self.file = file
            self.read()

    def read(self):
        """Opens the file, reads the content and create the joints"""

        # Load the content
        data = self.get_json_data()

        # Get the timestamp
        self.timestamp = data["Timestamp"]
        
        # Read the joints
        self.read_joints(data)

    def get_json_data(self):
        """Reads and returns the contents of one json file"""
        
        # Open the file
        f = open(self.file, "r", encoding="utf-16-le")
        content = f.read()
        f.close()

        data = json.loads(content)

        return data

    def read_joints(self, data):
        """Reads all the joints from the json format"""
        for joint in data["Bodies"][0]["Joints"]:
            self.joints[joint["JointType"]] = Joint(joint)

    def add_joint(self, name, joint):
        """Adds a joint to the pose"""
        self.joints[name] = joint

    def get_joint(self, name):
        """Returns a joint object from the name of the joint"""
        return self.joints[name]

    def get_timestamp(self):
        """Return the original json timestamp"""
        return self.timestamp

    def set_timestamp(self, timestamp):
        """Sets the original json timestamp"""
        self.timestamp = timestamp

    def set_relative_timestamp(self, t):
        """Sets the relative time compared to the time from the first pose (in sec)"""
        self.relative_timestamp = (self.timestamp - t) / 10000000

    def get_relative_timestamp(self):
        """Gets the relative time of this pose compared to the first one"""
        return self.relative_timestamp

    def __repr__(self):
        """Prints all the joints"""
        txt = ""
        if len(list(self.joints.keys())) == 0:
            txt = "Empty list of joints."
        for j in self.joints.keys():
            txt += str(self.joints[j]) + "\n"
        return txt

    def get_clear_copy(self):
        """Creates a copy of the pose and returns it"""
        p = Pose(self.no, self.file)
        p.joints = {}
        p.set_timestamp(self.timestamp)
        p.relative_timestamp = self.relative_timestamp
        return p


class Joint(object):
    """Defines a joint pertaining to a pose."""
    
    def __init__(self, data, coord=None):
        
        self.joint_type = None  # Label of the joint (e.g. "Head")
        
        # If we don't define a coordinate, then we read the data
        if coord is None:
            self.read_data(data)
            self.color = (255, 255, 255)  # Color white for the unchanged joints
            
        # Otherwise, we create a joint with new coordinates
        else:
            self.x = coord[0]
            self.y = coord[1]
            self.z = coord[2]
            self.color = (0, 255, 0)  # Color green for the corrected joints

        self.position = [self.x, self.y, self.z]  # List of the x, y and z coordinates of the joint
        self.velocity = None  # Velocity of the joint compared to the previous pose
        self.move_much = False  # True if this joint has moved above threshold during correction
        self.corrected = False  # True if this joint has been corrected by the algorithm
        self.randomized = False  # True if this joint coordinates have been randomly generated

    def read_data(self, data):
        """Reads the data from the json file and creates the corresponding attributes"""
        self.joint_type = data["JointType"]
        self.x = data["Position"]["X"]
        self.y = data["Position"]["Y"]
        self.z = data["Position"]["Z"]
        self.position = [self.x, self.y, self.z]

    def correct_joint(self, x, y, z):
        """Assigns new x, y and z coordinates to the joint and marks it as corrected"""
        self.x = x
        self.y = y
        self.z = z
        self.position = [self.x, self.y, self.z]
        self.corrected = True

    def set_move_much(self, move):
        """Defines that the displacement of a joint compared to the previous pose is above or below threshold"""
        self.move_much = move
        if move:
            self.color = (255, 50, 50)  # Color red for the joints above threshold
        else:
            self.color = (255, 255, 255)  # Color white for the joints below threshold

    def set_velocity(self, velocity):
        """Sets the velocity of the joint compared to the previous pose"""
        self.velocity = velocity

    def get_velocity(self):
        """Returns the velocity of the joint compared to the previous pose"""
        return self.velocity

    def get_copy(self):
        """Returns a copy of itself"""
        return copy.copy(self)

    def move_joint_randomized(self, origin, joint):
        """Changes the coordinates of a joint after randomization"""
        # print("Before: "+str(self.x)+", "+str(self.y)+", "+str(self.z))
        self.x = joint.x + (self.x - origin.x)
        self.y = joint.y + (self.y - origin.y)
        self.z = joint.z + (self.z - origin.z)
        self.randomized = True
        # print("After: "+str(self.x)+", "+str(self.y)+", "+str(self.z))

    def __repr__(self):
        """Returns a textual representation of the joint data"""
        txt = self.joint_type + ": (" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"
        txt += " - Shift: " + str(self.velocity)
        if self.move_much:
            txt += " OVER THRESHOLD"
        if self.corrected:
            txt += " CORRECTED"
        return txt
