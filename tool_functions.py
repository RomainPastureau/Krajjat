import os
import json


def subfolder_creation(path):
    """Creates folders that don't exist in a path."""

    folders = path.split("/")  # We create a list of all the sub-folders of the path
    for folder in range(len(folders)):
        partial_path = ""
        for i in range(folder + 1):
            partial_path += folders[i] + "/"
        if not os.path.exists(partial_path):
            os.mkdir(partial_path)
            print("Creating folder: " + partial_path)


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
        subsequence1.append(sequence1.poses[p].joints["HandRight"].x)

    subsequence2 = []
    for p in range(0, len(sequence2.poses)):
        subsequence2.append(sequence2.poses[p].joints["HandRight"].x)

    if len(subsequence1) <= len(subsequence2):
        for i in range(0, len(subsequence2) - len(subsequence1)):
            if subsequence1 == subsequence2[i:i + len(subsequence1)]:
                return [0, i]
    else:
        for i in range(0, len(subsequence1) - len(subsequence2)):
            if subsequence2 == subsequence1[i:i + len(subsequence2)]:
                return [i, 0]

    return False


def get_difference_paths(sequences):
    paths = []
    min_len = None

    for sequence in sequences:
        paths.append(sequence.path.split("/"))
        l: int = len(sequence.path.split("/"))
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
    else:  # For text files, tab separator
        separator = "\t"
    return separator


def show_percentage(verbose, current_iteration, total_value, next_percentage, step=10):
    """Shows the percentage of progression if verbose."""

    if verbose and current_iteration / total_value > next_percentage / 100:
        print(str(next_percentage) + "%", end=" ")
        next_percentage += step

    return next_percentage


def open_json(path):
    f = open(path, "r", encoding="utf-16-le")
    content = f.read()
    f.close()
    return json.loads(content)


def open_txt(path):
    file = open(path, "r", encoding="utf-16-le")
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


def table_to_json_joints(values):

    json_joints = []
    timestamp = None

    for value in values.keys():
        if value[-2:] == "_X":
            temp_dict = {}
            label = value[:-2]
            temp_dict["JointType"] = label
            temp_dict["Position"] = {"X": values[label+"_X"], "Y": values[label+"_Y"], "Z": values[label+"_Z"]}
            json_joints.append(temp_dict)
        elif value == "Timestamp":
            timestamp = values["Timestamp"]

    return json_joints, timestamp


def merge_original_and_new_sequences(original_sequence, new_sequence, correct_timestamp, perc, verbose):

    for p in range(len(original_sequence.poses)):
        data_original = original_sequence.poses[p].get_json_data()
        data_new = new_sequence.poses[p].get_json_joint_list(correct_timestamp)

        perc = show_percentage(verbose, p, len(original_sequence.poses), perc)

        for joint in range(len(data_original["Bodies"][0]["Joints"])):
            data_original["Bodies"][0]["Joints"][joint]["JointType"] = \
                data_new["Bodies"][0]["Joints"][joint]["JointType"]
            data_original["Bodies"][0]["Joints"][joint]["Position"]["X"] = \
                ["Bodies"][0]["Joints"][joint]["Position"]["X"]
            data_original["Bodies"][0]["Joints"][joint]["Position"]["Y"] = \
                data_new["Bodies"][0]["Joints"][joint]["Position"]["X"]
            data_original["Bodies"][0]["Joints"][joint]["Position"]["Z"] = \
                data_new["Bodies"][0]["Joints"][joint]["Position"]["X"]

        if correct_timestamp:
            data_original["Timestamp"] = data_new["Timestamp"]

    return(data_original)

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
            sheet_out.cell(i+1, j+1, data[i][j])
    workbook_out.save(path)
    return perc
