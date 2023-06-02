import random

import chardet
import math
import os
import json
import numpy as np
from scipy import interpolate
from classes.graph_element import *
from classes.joint import Joint

# Constants
UNITS = {"ns": 1000000000, "1ns": 1000000000, "10ns": 100000000, "100ns": 10000000,
         "µs": 1000000, "1µs": 1000000, "10µs": 100000, "100µs": 10000,
         "ms": 1000, "1ms": 1000, "10ms": 100, "100ms": 10,
         "s": 1, "sec": 1, "1s": 1, "min": 1 / 60, "mn": 1 / 60, "h": 1 / 3600, "hr": 1 / 3600,
         "d": 1 / 86400, "day": 1 / 86400}


# === Folder and path functions ===
def subfolder_creation(path):
    """Creates all the folders that don't exist in a path."""

    folders = path.split("/")  # We create a list of all the sub-folders of the path
    for folder in range(len(folders)):
        partial_path = ""
        for i in range(folder + 1):
            partial_path += folders[i] + "/"
        if "." in folders[i]:
            print("Not creating " + partial_path + " as it is not a valid folder.")
            break
        if not os.path.exists(partial_path):
            os.mkdir(partial_path)
            print("Creating folder: " + partial_path)


def get_difference_paths(sequences):
    """Returns a list of the subfolders differing between sequences paths.
    For instance, if the sequence A has a path as 'C:/Sequences/Raw/Subject1/Feb1/Sequence1' and the sequence B has a
    path as 'C:/Sequences/Resampled/Subject1/Mar1/Sequence1', the function will return the following list:
    [['Raw', 'Feb1'], ['Original', 'Mar1']]. """
    paths = []
    min_len = None

    for sequence in sequences:
        paths.append(sequence.path.split("/"))
        l = len(sequence.path.split("/"))
        if min_len is None:
            min_len = l
        elif min_len > l:
            min_len = l

    new_paths = [[] for _ in range(len(paths))]

    for i in range(min_len):
        keep = False
        for p in range(len(paths)):
            if paths[p][i] != paths[0][i]:
                keep = True
        if keep:
            for p in range(len(paths)):
                new_paths[p].append(paths[p][i])

    for p in range(len(paths)):
        if len(paths[p]) > min_len:
            for i in range(min_len, len(paths[p])):
                new_paths[p].append(paths[p][i])

    return new_paths


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


def align_two_sequences(sequence1, sequence2):
    """Checks if one sequence is a subset of another; if true, returns the index of the two sequences for
    synchronization"""

    subsequence1 = []
    for p in range(0, len(sequence1.poses)):
        subsequence1.append(sequence1.poses[p].joints["ElbowRight"].x)

    subsequence2 = []
    for p in range(0, len(sequence2.poses)):
        subsequence2.append(sequence2.poses[p].joints["ElbowRight"].x)

    if len(subsequence1) <= len(subsequence2):
        for i in range(0, len(subsequence2) - len(subsequence1)):
            if subsequence1 == subsequence2[i:i + len(subsequence1)]:
                return [0, i]
    else:
        for i in range(0, len(subsequence1) - len(subsequence2)):
            if subsequence2 == subsequence1[i:i + len(subsequence2)]:
                return [i, 0]

    return False


def get_names(sequences):
    names = []
    for sequence in sequences:
        names.append(sequence.name)
    return names


def get_system_separator():
    """Returns the separator (comma or semicolon) of the regional settings of the system; if it can't access it,
    returns a comma by default."""
    try:
        from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER
        a_reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        a_key = OpenKey(a_reg, r"Control Panel\International")
        separator = QueryValueEx(a_key, "sList")[0]
    except:
        print("Impossible to get the regional list separator, using default comma.")
        separator = ","
    finally:
        pass
    return separator


# Constant
SEPARATOR = get_system_separator()


def get_filetype_separator(path):
    if path.split(".")[-1] == "csv":  # Get the separator from local user (to get , or ;)
        separator = SEPARATOR
    else:  # For text or tsv files, tab separator
        separator = "\t"
    return separator


def show_percentage(verbose, current_iteration, total_value, next_percentage, step=10):
    """Shows the percentage of progression if verbose is equal to 1."""

    if verbose == 1 and current_iteration / total_value > next_percentage / 100:
        print(str(next_percentage) + "%", end=" ")
        next_percentage += step

    return next_percentage


def open_json(path):
    f = open(path, "r", encoding="utf-16-le")
    content = f.read()
    f.close()
    return json.loads(content)


def open_txt(path):
    rawdata = open(path, "rb").read()
    encoding = chardet.detect(rawdata)['encoding']

    file = open(path, "r", encoding=encoding)
    data = file.read().split("\n")
    file.close()
    return data


def open_xlsx(path):
    import openpyxl as op
    workbook = op.load_workbook(path)
    data = workbook[workbook.sheetnames[0]]

    # Get the labels (timestamp and joint labels) from the first row
    joints_labels = []
    for cell in data["1"]:
        joints_labels.append(str(cell.value))

    return data, joints_labels


def table_to_dict_joints(values):
    json_joints = []
    timestamp = None

    for value in values.keys():
        if value[-2:] == "_X":
            temp_dict = {}
            label = value[:-2]
            temp_dict["JointType"] = label
            temp_dict["Position"] = {"X": values[label + "_X"], "Y": values[label + "_Y"], "Z": values[label + "_Z"]}
            json_joints.append(temp_dict)
        elif value == "Timestamp":
            timestamp = values["Timestamp"]

    return json_joints, timestamp


def table_to_string(table, separator, perc, verbose):
    data = ""

    for i in range(len(table)):
        perc = show_percentage(verbose, i, len(table), perc)
        for j in range(len(table[i])):
            data += str(table[i][j])
            if j != len(table[i]) - 1:
                data += separator
        if i != len(table) - 1:
            data += "\n"

    return data


def excel_write(workbook_out, sheet_out, data, path, perc, verbose):
    for i in range(len(data)):
        perc = show_percentage(verbose, i, len(data), perc)
        for j in range(len(data[i])):
            sheet_out.cell(i + 1, j + 1, data[i][j])
    workbook_out.save(path)
    return perc


def resample_data(data, time_points, frequency, mode="linear"):
    """Resamples non-uniform data to a uniform time series according to a specific frequency."""
    np_data = np.array(data)
    np_time_points = np.array(time_points)
    interp = interpolate.interp1d(np_time_points, np_data, kind=mode)

    resampled_time_points = np.arange(min(time_points), max(time_points), 1 / frequency)
    resampled_data = interp(resampled_time_points)
    return resampled_data, resampled_time_points


def interpolate_data(data, time_points_incomplete, time_points_complete, mode="linear"):
    np_data = np.array(data)
    np_time_points = np.array(time_points_incomplete)
    np_time_points_complete = np.array(time_points_complete)
    interp = interpolate.interp1d(np_time_points, np_data, kind=mode)

    resampled_data = interp(np_time_points_complete)
    return resampled_data, np_time_points_complete

def get_color_scheme(name):

    colors_dict = {"red": (255, 0, 0, 255), "orange": (255, 102, 0, 255), "gold": (255, 204, 0, 255),
                   "yellow": (255, 255, 0, 255), "green": (153, 204, 0, 255), "teal": (32, 178, 170, 255),
                   "turquoise": (64, 224, 208, 255), "blue": (100, 149, 237, 255), "navy": (0, 0, 128, 255),
                   "purple": (138, 43, 226, 255), "white": (255, 255, 255, 255), "black": (0, 0, 0, 255),
                   "lightgrey": (64, 64, 64, 255), "grey": (128, 128, 128, 255), "darkgrey": (192, 192, 192, 255)}

    if type(name) is str:
        name = name.lower()

        detect_personalized_gradient = False

        colors = []

        if "_" in name:
            colors_names = name.split("_")
            for color in colors_names:
                color = color.lower()
                if color in colors_dict.keys():
                    detect_personalized_gradient = True
                    colors.append(colors_dict[color])
                else:
                    detect_personalized_gradient = False
                    break

        if detect_personalized_gradient == False:

            if name in ["simple", "default", "apples"]:
                colors = [colors_dict["green"], colors_dict["red"]]

            elif name == "celsius":
                colors = [colors_dict["turquoise"], colors_dict["green"], colors_dict["gold"],
                          colors_dict["orange"], colors_dict["red"]]

            elif name == "cividis":
                colors = [(0, 32, 78, 255), (254, 234, 90, 255)]

            elif name == "parula":
                colors = [(49, 41, 138, 255), (17, 134, 211, 255), (51, 183, 160, 255), (213, 186, 85, 255),
                          (249, 251, 9, 255)]

            elif name == "viridis":
                colors = [(66, 1, 86, 255), (57, 87, 140, 255), (32, 146, 140, 255), (96, 202, 96, 255),
                          (252, 233, 59, 255)]

            else:
                if name not in ["black_to_white", "black_and_white"]:
                    print("Invalid color scheme name, returning black to white")
                colors = [colors_dict["black"], colors_dict["white"]]

    elif type(name) is list:

        colors = ["" for _ in range(len(name))]

        for i in range(len(name)):
            if type(name[i]) is tuple:
                colors[i] = name[i]
                if len(name[i]) == 3:
                    name[i] = [name[i][0], name[i][1], name[i][2], 255]
                for j in range(len(name[i])):
                    if name[i][j] < 0 or name[i][j] > 255:
                        print("Invalid color index, returning black instead")
                        colors[i] = colors_dict["black"]
                        break
            elif type(name[i]) is str:
                if name[i] not in colors_dict.keys():
                    print("Invalid color name ("+str(name[i])+"), returning black instead")
                    colors[i] = colors_dict["black"]
                else:
                    print(name[i])
                    colors[i] = colors_dict[name[i]]

    return colors


def get_color_points_on_gradient(color_scheme, no_points):
    if type(color_scheme) == str:
        color_scheme = get_color_scheme(color_scheme)

    colors = []
    for i in range(no_points + 1):
        colors.append(get_color_ratio(color_scheme, i / no_points))

    return colors


def get_color_ratio(colors, ratio, type="rgb", alpha=True):
    """Returns the color on a gradient scale in function of a ratio."""

    if 0 < ratio < 1:
        color_start = colors[int((ratio / (1 / (len(colors) - 1))))]
        color_end = colors[int((ratio / (1 / (len(colors) - 1)))) + 1]
    elif ratio >= 1:
        color_start = colors[-2]
        color_end = colors[-1]
        ratio = 1
    else:
        color_start = colors[0]
        color_end = colors[1]
        ratio = 0

    if int((ratio * (len(colors) - 1))) == 0 or ratio == 1:
        new_ratio = ratio
    else:
        new_ratio = (ratio * (len(colors) - 1)) % int((ratio * (len(colors) - 1)))

    diff_r = color_end[0] - color_start[0]
    diff_g = color_end[1] - color_start[1]
    diff_b = color_end[2] - color_start[2]
    if len(color_start) == 4:
        diff_a = color_end[3] - color_start[3]

    r = color_start[0] + diff_r * new_ratio
    g = color_start[1] + diff_g * new_ratio
    b = color_start[2] + diff_b * new_ratio

    if len(color_start) == 4 and alpha == True:
        a = color_start[3] + diff_a * new_ratio
        color = (int(r), int(g), int(b), int(a))

        if type == "rgb":
            return color
        elif type == "hex":
            return '#%02x%02x%02x%02x' % color

    else:
        color = (int(r), int(g), int(b))

        if type == "rgb":
            return color
        elif type == "hex":
            return '#%02x%02x%02x' % color


def get_joints_colors_qty_movement(joints_qty_movement, color_scheme="default"):
    joints_colors = {}

    # Get the min and max quantities of movement
    qty_mov = []
    for j in joints_qty_movement.keys():
        qty_mov.append(joints_qty_movement[j])
    min_qty = min(qty_mov)  # Determines min global velocity (green)
    max_qty = max(qty_mov)  # Determines max global velocity (red)

    colors = get_color_scheme(color_scheme)

    # Apply the colors to all joints
    for j in joints_qty_movement.keys():
        ratio = (joints_qty_movement[j] - min_qty) / (max_qty - min_qty)
        joints_colors[j] = get_color_ratio(colors, ratio, type="hex", alpha=False)

    return joints_colors


def get_scaled_audio(audio_array, max_velocity, verbose=1):
    new_audio_array = []

    if verbose > 0:
        print("Scaling audio...")

    perc = 10

    max_audio_array = max(audio_array)

    for i in range(len(audio_array)):
        perc = show_percentage(verbose, i, len(audio_array), perc)
        new_audio_array.append(audio_array[i] / max_audio_array * max_velocity)

    if verbose > 0:
        print("100% - Done.")

    return new_audio_array


def convert_timestamps(timestamps, images, frequency):
    number_of_frames = math.ceil(timestamps[-1] * frequency) + 1
    new_timestamps = []
    new_images = []
    t = 0
    duration = 1 / frequency

    for f in range(number_of_frames):
        new_timestamps.append(t)
        possible_times = [abs(i - t) for i in timestamps]
        index_image = possible_times.index(min(possible_times))
        new_images.append(images[index_image])
        t += duration

    return (new_timestamps, new_images)


def get_min_max_values(plot_dictionary):
    min_value = 0
    max_value = 0

    for key in plot_dictionary.keys():
        if plot_dictionary[key] is list:
            for series in plot_dictionary[key]:
                local_min = min(series.y)
                local_max = max(series.y)
                if local_min < min_value:
                    min_value = local_min
                if local_max > max_value:
                    max_value = local_max
        elif type(plot_dictionary[key]) is Graph:
            for plot in plot_dictionary[key].plots:
                local_min = min(plot.y)
                local_max = max(plot.y)
                if local_min < min_value:
                    min_value = local_min
                if local_max > max_value:
                    max_value = local_max
        else:
            if plot_dictionary[key] < min_value:
                min_value = plot_dictionary[key]
            if plot_dictionary[key] > max_value:
                max_value = plot_dictionary[key]

    return min_value, max_value


def get_frequency(time_vector):
    return (1 / (time_vector[1] - time_vector[0]))


def import_joints_conversions():
    file = open("res/qualisys_joints.txt")
    content = file.read().split("\n")
    file.close()

    joints_conversions = {}

    for line in content:
        elements = line.split("\t")
        joints_conversions[elements[0]] = elements[1]

    return (joints_conversions)


def convert_data_from_qtm(data, verbose=1):
    new_data = []
    save_data = False

    if verbose > 0:
        print("\n\tConverting data from Qualisys...")
    if verbose == 1:
        print("\t\tStandardizing joints labels...", end=" ")
    elif verbose > 1:
        print("\t\tStandardizing joints labels...")

    joints_conversions = import_joints_conversions()

    # First, we find where the data starts
    perc = 10
    for i in range(len(data)):
        elements = data[i].split("\t")

        if elements[0] == "MARKER_NAMES":
            header = "Timestamp"
            for j in range(1, len(elements)):

                # We remove the prefix by looking for a joint name in the label:
                if elements[j] not in joints_conversions.keys():
                    for label in joints_conversions.keys():
                        if label in elements[j]:
                            if verbose > 1:
                                print("\t\t\tChanging label name " + elements[j] + " to " +
                                      joints_conversions[label] + ".")
                            elements[j] = label
                            break

                header += "\t" + joints_conversions[elements[j]] + "_X"
                header += "\t" + joints_conversions[elements[j]] + "_Y"
                header += "\t" + joints_conversions[elements[j]] + "_Z"
            new_data.append(header)

            if verbose > 0:
                print("\t\tLabels standardized.")

        if elements[0] == "1":
            save_data = True
            if verbose > 0:
                print("\t\tConverting coordinates from mm to m...", end=" ")

        if save_data:

            perc = show_percentage(verbose, j, len(data), perc)
            line = ""

            for j in range(1, len(elements)):

                # We keep the timestamp in ms
                if j == 1:
                    line = elements[j]

                # We convert the joints coordinates in m
                else:
                    line += "\t" + str(float(elements[j]) / 1000)

            if line != "":
                new_data.append(line)

    if verbose > 0:
        print("100% - Done.")

    return (new_data)


def load_joints_connections(path):
    file = open("res/" + path)
    content = file.read().split("\n")
    connections = []

    for line in content:
        connections.append(line.split("\t"))

    return connections


def load_qualisys_to_kinect():
    file = open("res/qualisys_to_kinect.txt")
    content = file.read().split("\n")
    connections = {}

    for line in content:
        elements = line.split("\t")
        connections[elements[0]] = elements[1:]

    return connections


def load_kinect_joints():
    file = open("res/kinect_joints.txt")
    content = file.read().split("\n")
    return content


def generate_random_joints(number_of_joints):
    """Creates uniform, random positions for the joints"""
    random_joints = []
    for i in range(number_of_joints):
        x = random.uniform(-0.2, 0.2)
        y = random.uniform(-0.3, 0.3)
        z = random.uniform(-0.5, 0.5)
        j = Joint(None, x, y, z)
        random_joints.append(j)
    return random_joints


def load_joints_positions(plot_dictionary, joint_layout="auto"):
    if joint_layout == "auto":
        if "Chest" in plot_dictionary.keys():
            joint_layout = "qualisys"
        else:
            joint_layout = "kinect"

    if joint_layout == "kinect":
        file = open("res/joints_positions_kinect.txt")
    elif joint_layout == "qualisys":
        file = open("res/joints_positions_qualisys.txt")
    else:
        raise Exception("Wrong layout argument: should be 'kinect' or 'qualisys'.")

    content = file.read().split("\n")
    joints_positions = {}

    for line in content:
        elements = line.split("\t")
        joints_positions[elements[0]] = int(elements[1])

    return joints_positions, joint_layout


def calculate_velocity(pose1, pose2, joint):

    # Get the distance travelled by a joint between two poses (meters)
    dist = calculate_distance(pose1.joints[joint], pose2.joints[joint])

    # Get the time elapsed between two poses (seconds)
    delay = calculate_delay(pose1, pose2)

    # Calculate the velocity (meters per seconds)
    velocity = dist / delay

    return velocity


def calculate_distance(joint1, joint2):
    """Uses the Euclidian formula to calculate the distance between two joints. This can be used to calculate
    the distance travelled by one joint between two poses, or the distance between two joints on the same pose."""
    x = (joint2.x - joint1.x) ** 2
    y = (joint2.y - joint1.y) ** 2
    z = (joint2.z - joint1.z) ** 2

    return math.sqrt(x + y + z)


def calculate_delay(pose1, pose2):
    """Returns the delay between two poses, in seconds."""
    time_a = pose1.get_relative_timestamp()
    time_b = pose2.get_relative_timestamp()
    return time_b - time_a