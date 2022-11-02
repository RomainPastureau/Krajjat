#!/usr/bin/env python
"""Krajjat 1.8
Kinect Realignment Algorithm for Joint Jumps And Twitches
Author: Romain Pastureau
This file contains the main core functions. This is the file
to run to realign one or more recordings.
"""
from collections import OrderedDict
from typing import List, Any

from classes import *
from scipy.io import wavfile
from tool_functions import *

__author__ = "Romain Pastureau"
__version__ = "1.8"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"


def save_sequence(sequence, folder_out, original_sequence=None, name_out="global", file_format="json", individual=True,
                  correct_timestamp=False, verbose=True):
    """Saves a realigned sequence in json, txt, csv or xlsx. In the first case, the original sequence is necessary
    in order to only modify the timestamp and xyz position from the original file; all the other formats lose the
    information from the original sequence. It is possible to save the data with one file per pose or a meta file."""

    # Automatic creation of all the folders of the path if they don't exist
    subfolder_creation(folder_out)

    file_format = file_format.strip(".")  # We remove the dot in the format
    if file_format == "xls":
        file_format = "xlsx"

    if verbose:
        if individual:
            print("Saving " + file_format.upper() + " individual files...")
        else:
            print("Saving " + file_format.upper() + " global file...")

    perc = 10  # Used for the progression percentage

    # If file format is JSON
    if file_format == "json":

        # Get the data
        if original_sequence is not None:
            data = merge_original_and_new_sequences(original_sequence, sequence, correct_timestamp, perc, verbose)
        else:
            data = sequence.get_json_joint_list(correct_timestamp)

        # Save the data
        if not individual:
            with open(folder_out + "/" + name_out + ".json", 'w', encoding="utf-16-le") as f:
                json.dump(data, f)
        else:
            for p in range(len(sequence.poses)):
                perc = show_percentage(verbose, p, len(sequence.poses), perc)
                with open(folder_out + "/frame_" + str(p) + ".json", 'w', encoding="utf-16-le") as f:
                    json.dump(data[p], f)

    elif file_format == "xlsx":
        import openpyxl as op
        workbook_out = op.Workbook()
        sheet_out = workbook_out.active

        # Save the data
        if not individual:
            data = sequence.get_table(correct_timestamp)
            excel_write(workbook_out, sheet_out, data, folder_out + "/" + name_out + ".xlsx", perc, verbose)

        else:
            for p in range(len(sequence.poses)):
                data = sequence.poses[p].get_table(correct_timestamp)
                perc = show_percentage(verbose, p, len(sequence.poses), perc)
                excel_write(workbook_out, sheet_out, data, folder_out + "/frame_" + str(p) + ".xlsx", perc, False)

    # If the file format is CSV or TXT
    else:

        # Force comma or semicolon separator
        if file_format == "csv,":
            separator = ","
            file_format = "csv"
        elif file_format == "csv;":
            separator = ";"
            file_format = "csv"
        elif file_format[0:3] == "csv":  # Get the separator from local user (to get , or ;)
            separator = get_system_separator()
        elif file_format == "txt":  # For text files, tab separator
            separator = "\t"
        else:
            separator = "\t"

        # Save the data
        if not individual:
            data = table_to_string(sequence.get_table(correct_timestamp), separator, perc, verbose)
            with open(folder_out + "/" + name_out + "." + file_format, 'w', encoding="utf-16-le") as f:
                f.write(data)
        else:
            for p in range(len(sequence.poses)):
                data = table_to_string(sequence.poses[p].get_table(correct_timestamp), separator, perc, False)
                perc = show_percentage(verbose, p, len(sequence.poses), perc)
                with open(folder_out + "/frame_" + str(p) + "." + file_format, 'w', encoding="utf-16-le") as f:
                    f.write(data)

    print("100% - Done.\n")


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


def save_stats(sequenceOrSequences, output_file, verbose=True):
    """Saves the sequence or sequences statistics and information in a table file (xlsx, csv or txt)."""

    # Automatic creation of all the folders of the path if they don't exist
    subfolder_creation("/".join(output_file.split("/")[:-1]))

    # Open the sequence or sequences
    if type(sequenceOrSequences) is Sequence:
        sequenceOrSequences = [sequenceOrSequences]
    elif type(sequenceOrSequences) is str:
        sequenceOrSequences = load_sequences_recursive(sequenceOrSequences)

    file_format = output_file.split(".")[-1]
    if file_format == "xls":
        file_format = "xlsx"
        output_file += "x"

    perc = 10  # Used for the progression percentage

    if verbose:
        print("Saving " + file_format.upper() + " stat file...")

    # Get the table
    global_stats = []
    for sequence in sequenceOrSequences:
        stats = sequence.get_stats(tabled=True)
        if global_stats == []:
            global_stats.append(stats[0].copy())
        global_stats.append(stats[1].copy())

    if file_format == "xlsx":
        import openpyxl as op
        workbook_out = op.Workbook()
        sheet_out = workbook_out.active
        excel_write(workbook_out, sheet_out, global_stats, output_file, perc, verbose)

    else:
        # Force comma or semicolon separator
        if file_format == "csv,":
            separator = ","
            output_file = output_file[:-1]
        elif file_format == "csv;":
            separator = ";"
            output_file = output_file[:-1]
        elif file_format[0:3] == "csv":  # Get the separator from local user (to get , or ;)
            separator = get_system_separator()
        elif file_format == "txt":  # For text files, tab separator
            separator = "\t"
        else:
            separator = "\t"

        data = table_to_string(global_stats, separator, perc, False)
        with open(output_file, 'w', encoding="utf-16-le") as f:
            f.write(data)

    print("100% - Done.")


def realign_single(input_folder, output_folder, velocity_threshold, window, verbose):
    """Realigns one video and saves it in an output folder."""

    sequence = Sequence(input_folder)
    new_sequence = sequence.realign(velocity_threshold, window, verbose)
    save_sequence(sequence, new_sequence, output_folder)


def realign_folder(input_folder, output_folder, velocity_threshold, window, verbose):
    """Realigns all videos in a folder and saves them in an output folder."""

    contents = os.listdir(input_folder)

    for c in contents:
        if os.path.isdir(input_folder + "/" + c):
            print("======= " + c + " =======")
            if not os.path.exists(output_folder + "/" + c):
                os.mkdir(output_folder + "/" + c)
            realign_single(input_folder + "/" + c, output_folder + "/" + c, velocity_threshold, window, verbose)


def realign_recursive(input_folder, output_folder, velocity_threshold, window, verbose):
    """Realigns all videos in a recursive fashion, save them using the same folder structure."""

    contents = os.listdir(input_folder)

    for c in contents:
        if os.path.isdir(input_folder + "/" + c):
            subcontents = os.listdir(input_folder + "/" + c)
            for file_name in subcontents:
                if file_name.endswith('.json'):
                    print("======= " + input_folder + "/" + c + " =======")
                    realign_single(input_folder + "/" + c, output_folder + "/" + c, velocity_threshold, window, verbose)
                    break
            else:
                realign_recursive(input_folder + "/" + c, output_folder + "/" + c, velocity_threshold, window, verbose)


def re_reference_single(input_folder, output_folder, reference_joint, place_at_zero, verbose):
    """Realigns one video and saves it in an output folder."""

    sequence = Sequence(input_folder)
    new_sequence = sequence.re_reference(reference_joint, place_at_zero, verbose)
    save_sequence(sequence, new_sequence, output_folder)


def re_reference_folder(input_folder, output_folder, reference_joint, place_at_zero, verbose):
    """Realigns all videos in a folder and saves them in an output folder."""

    contents = os.listdir(input_folder)

    for c in contents:
        if os.path.isdir(input_folder + "/" + c):
            print("======= " + c + " =======")
            if not os.path.exists(output_folder + "/" + c):
                os.mkdir(output_folder + "/" + c)
            re_reference_single(input_folder + "/" + c, output_folder + "/" + c, reference_joint, place_at_zero,
                                verbose)


def re_reference_recursive(input_folder, output_folder, reference_joint, place_at_zero, verbose):
    """Realigns all videos in a recursive fashion, save them using the same folder structure."""

    contents = os.listdir(input_folder)

    for c in contents:
        if os.path.isdir(input_folder + "/" + c):
            subcontents = os.listdir(input_folder + "/" + c)
            for file_name in subcontents:
                if file_name.endswith('.json'):
                    print("======= " + input_folder + "/" + c + " =======")
                    re_reference_single(input_folder + "/" + c, output_folder + "/" + c, reference_joint, place_at_zero,
                                        verbose)
                    break
            else:
                re_reference_recursive(input_folder + "/" + c, output_folder + "/" + c, reference_joint, place_at_zero,
                                       verbose)


def load_sequences_folder(input_folder):
    """Opens sequences contained in a folder."""
    print("Loading sequences...")
    return (load_sequences(input_folder, False))


def load_sequences_recursive(input_folder):
    """Finds and opens sequences recursively from a folder."""
    print("Loading sequences recursively...")
    return (load_sequences(input_folder, True))


def load_sequences(input_folder, recursive=False):

    content = os.listdir(input_folder)
    sequences = []

    for c in content:
        try:
            print("======= " + input_folder + "/" + c + " =======")
            sequence = Sequence(input_folder + "/" + c)
            sequences.append(sequence)
        except Exception:
            print("The path " + input_folder + "/" + c + " is not a valid sequence.")
            if recursive:
                if os.path.isdir(input_folder + "/" + c):
                    sequences += load_sequences(input_folder + "/" + c, True)

    print("Sequences loaded.")

    return(sequences)

if __name__ == '__main__':
    # Define variables here
    folder = ""
    input_folder = ""
    output_folder = ""
    velocity_threshold = 10  # in cm per second
    window = 3  # max number of frames under which something is considered as a twitch, and over which a jump
    verbose = False  # if you want to see everything that the program does, put True
    reference_joint = "SpineMid"  # joint to be used as reference in the re-referencing
    place_at_zero = True  # if you want the re-referencing to place the reference joint at (0, 0, 0)

    # Realignment

    # For one recording
    # realign_single(input_folder, output_folder, velocity_threshold, window, verbose)

    # For many recordings in one directory
    # realign_folder(input_folder, output_folder, velocity_threshold, window, verbose)

    # For dealing with all the videos recursively
    # realign_recursive(input_folder, output_folder, velocity_threshold, window, verbose)

    # Re-referencing

    # For one recording
    # re_reference_single(input_folder, output_folder, reference_joint, place_at_zero, verbose)

    # For many recordings in one directory
    # re_reference_folder(input_folder, output_folder, reference_joint, place_at_zero, verbose)

    # For dealing with all the videos recursively
    re_reference_recursive(input_folder, output_folder, reference_joint, place_at_zero, verbose)
