#!/usr/bin/env python
"""Krajjat 1.6
Kinect Realignment Algorithm for Joint Jumps And Twitches
Author: Romain Pastureau
This file contains the main core functions. This is the file
to run to realign one or more recordings.
"""

from classes import *
from scipy.io import wavfile

__author__ = "Romain Pastureau"
__version__ = "1.6"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"


def compute_different_joints(sequence1, sequence2, verbose=False):
    """Returns the number of joints having different coordinates between two sequences. Can be used to check how
    many joints have been realigned, for example."""
    different_joints = 0
    total_joints = 0

    for p in range(len(sequence1.poses)):  # For all the poses
        for j in sequence1.poses[p].joints.keys():  # For all the joints

            # We round the coordinates to 5 significant digits in order to account for rounding errors
            if round(sequence1.poses[p].joints[j].x, 5) == round(sequence2.poses[p].joints[j].x, 5) and \
                    round(sequence1.poses[p].joints[j].y, 5) == round(sequence2.poses[p].joints[j].y, 5) and \
                    round(sequence1.poses[p].joints[j].z, 5) == round(sequence2.poses[p].joints[j].z, 5):
                total_joints += 1

            else:
                # If verbose, we show the number of the pose, the name of the joint, and the coordinates of the
                # two sequences
                if verbose:
                    print("Pose n°" + str(p) + ", " + str(j))
                    print("X: " + str(sequence1.poses[p].joints[j].x) +
                          "; Y: " + str(sequence1.poses[p].joints[j].y) +
                          "; Z: " + str(sequence1.poses[p].joints[j].z))
                    print("X: " + str(sequence2.poses[p].joints[j].x) +
                          "; Y: " + str(sequence2.poses[p].joints[j].y) +
                          "; Z: " + str(sequence2.poses[p].joints[j].z))
                different_joints += 1
                total_joints += 1

    # We print the result
    print("Different joints: " + str(different_joints) + "/" + str(total_joints) + " (" + str(
        different_joints / total_joints) + "%).")

    return different_joints, total_joints


def save_json(original_sequence, new_sequence, folder_out, correct_timestamp=False, verbose=True):
    """Saves a realigned sequence as a series of json files, using the information from the original sequence
    to generate the structure - only the coordinates are """

    # Automatic creation of all the folders of the path if they don't exist
    folders = folder_out.split("/")  # We create a list of all the sub-folders of the path
    for folder in range(len(folders)):
        partial_path = ""
        for i in range(folder + 1):
            partial_path += folders[i] + "/"
        if not os.path.exists(partial_path):
            os.mkdir(partial_path)
            print("Creating folder: " + partial_path)

    print("Saving JSON files...")

    perc = 10  # Used for the progression percentage

    for p in range(len(original_sequence.poses)):

        # Show percentage if verbose
        if verbose and p / len(original_sequence.poses) > perc / 100:
            print(str(perc) + "%", end=" ")
            perc += 10

        # Get the original json data from the original sequence
        data = original_sequence.poses[p].get_json_data()

        # For each joint, rewrites the x, y and z coordinates
        for joint in range(len(data["Bodies"][0]["Joints"])):
            joint_type = data["Bodies"][0]["Joints"][joint]["JointType"]
            j = new_sequence.poses[p].joints[joint_type]
            data["Bodies"][0]["Joints"][joint]["Position"]["X"] = j.x
            data["Bodies"][0]["Joints"][joint]["Position"]["Y"] = j.y
            data["Bodies"][0]["Joints"][joint]["Position"]["Z"] = j.z

        # If the parameter is true, we change the timestamp by the relative timestamp
        if correct_timestamp:
            data["Timestamp"] = new_sequence.poses[p].relative_timestamp

        # We save the pose file
        file = original_sequence.poses[p].file.split("/")[-1]
        with open(folder_out + "/" + file, 'w', encoding="utf-16-le") as f:
            json.dump(data, f)

    print("- Done.\n")


def get_velocities_joints(sequence, audio=None):
    """Returns the velocity of each of the joints across time, in order to plot it."""

    joints_movement = {}
    joints_velocity = {}
    times = sequence.get_timestamps()[1:]
    max_velocity = 0
    joints_qty_movement = {}
    audio_array = []
    audio_times = []

    for j in sequence.poses[0].joints:
        movement = []
        velocity = []

        for p in range(1, len(sequence.poses)):

            # Distance
            j1 = sequence.poses[p - 1].joints[j]
            j2 = sequence.poses[p].joints[j]
            dist = sequence.get_distance(j1, j2)
            movement.append(dist)

            # Velocity
            vel = sequence.get_velocity(sequence.poses[p - 1], sequence.poses[p], j)
            if vel > max_velocity:
                max_velocity = vel
            velocity.append(vel)

        joints_movement[j] = movement
        joints_velocity[j] = velocity
        joints_qty_movement[j] = sum(velocity)

    if audio is not None:

        print("Opening the audio...")

        audio_data = wavfile.read(audio)
        fq = audio_data[0]
        audio_array = audio_data[1]

        audio_times = list(range(len(audio_array)))

        perc = 10
        for i in range(len(audio_times)):
            if i / len(audio_times) > perc / 100:
                print(str(perc) + "%", end=" ")
                perc += 10
            audio_array[i] = abs(audio_array[i])
            if audio_array[i] == -32768:
                audio_array[i] = 32767
            audio_times[i] = audio_times[i] * (1 / fq)

        print("100% - Done.\n")

    return joints_velocity, joints_qty_movement, max_velocity, times, audio_array, audio_times


def realign_single(input_folder, output_folder, velocity_threshold, window, verbose):
    """Realigns one video and saves it in an output folder."""

    sequence = Sequence(input_folder)
    new_sequence = sequence.realign(velocity_threshold, window, verbose)
    save_json(sequence, new_sequence, output_folder)


def realign_folder(input_folder, output_folder, velocity_threshold, window, verbose):
    """Realigns all videos in a folder and saves them in an output folder."""

    contents = os.listdir(input_folder)

    for c in contents:
        if os.path.isdir(input_folder+"/"+c):
            print("======= " + c + " =======")
            if not os.path.exists(output_folder+"/"+c):
                os.mkdir(output_folder+"/"+c)
            realign_single(input_folder+"/"+c, output_folder+"/"+c, velocity_threshold, window, verbose)


def realign_recursive(input_folder, output_folder, velocity_threshold, window, verbose):
    """Realigns all videos in a recursive fashion, save them using the same folder structure."""

    contents = os.listdir(input_folder)

    for c in contents:
        if os.path.isdir(input_folder+"/"+c):
            subcontents = os.listdir(input_folder+"/"+c)
            for file_name in subcontents:
                if file_name.endswith('.json'):
                    print("======= " + input_folder + "/" + c + " =======")
                    if not os.path.exists(output_folder + "/" + c):
                        os.mkdir(output_folder + "/" + c)
                    realign_single(input_folder + "/" + c, output_folder + "/" + c, velocity_threshold, window, verbose)
                    break
            else:
                realign_recursive(input_folder+"/"+c, output_folder+"/"+c, velocity_threshold, window, verbose)


if __name__ == '__main__':

    # Define variables here
    folder = ""
    input_folder = folder+"01_Original_gestures"
    output_folder = folder+"02_Realigned_gestures"
    velocity_threshold = 10  # in cm per second
    window = 3  # max number of frames under which something is considered as a twitch, and over which a jump
    verbose = False  # if you want to see everything that the program does, put True

    # For one recording
    realign_single(input_folder, output_folder, velocity_threshold, window, verbose)

    # For many recordings in one directory
    realign_folder(input_folder, output_folder, velocity_threshold, window, verbose)

    # For dealing with all the videos recursively
    realign_recursive(input_folder, output_folder, velocity_threshold, window, verbose)
