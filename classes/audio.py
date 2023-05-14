from scipy.io import wavfile
from tool_functions import *
from scipy.signal import hilbert


class Audio(object):

    def __init__(self, path_or_samples, frequency=None, name=None):
        self.samples = []
        self.timestamps = []
        self.frequency = None
        self.name = name
        self.path = None
        self.files = None

        if type(path_or_samples) is str:
            self.load_from_path(path_or_samples)
        elif type(path_or_samples) is list:
            self.samples = path_or_samples
            self.frequency = frequency
        else:
            raise Exception("Invalid audio path or samples.")

        self.timestamps = [i / self.frequency for i in range(len(self.samples))]
        self.duration = len(self.samples) / self.frequency

        self.max_sample = max(self.samples)
        self.min_sample = min(self.samples)

        self.envelope = None
        self.max_sample_envelope = None
        self.min_sample_envelope = None
        self.calculate_envelope()

    # === Loading functions ===

    def load_from_path(self, path):

        self.path = path

        # If it's a folder, we fetch all the files
        if os.path.isdir(self.path):
            self.get_files()  # Fetches all the files
        self.load_samples()  # Loads the files into poses

        if len(self.samples) == 0:
            raise Exception("The path " + path + " is not a valid sequence.")

    def get_files(self):
        """Opens a folder and fetches all the individual files (.json, .csv, .txt or .xlsx)."""

        print("Fetching sample files...", end=" ")

        file_list = os.listdir(self.path)  # List all the files in the folder
        self.files = ["" for _ in range(len(file_list))]  # Create an empty list the length of the files

        # Here, we find all the files that are either .json or .meta in the folder.
        for f in file_list:

            # If a file has an accepted extension, we get its index from its name to order it correctly in the list.
            # This is necessary as some file systems will order frame_2.json after frame_11.json because,
            # alphabetically, "1" is before "2".
            if f.split(".")[-1] in ["json", "csv", "txt", "xlsx"]:
                self.files[int(f.split(".")[0].split("_")[1])] = f

        # If files that weren't of the accepted extension are in the folder, then "self.files" is larger than
        # the number of samples. The list is thus ending by a series of empty strings that we trim.
        if "" in self.files:
            limit = self.files.index("")
            self.files = self.files[0:limit]

        print(str(len(self.files)) + " sample file(s) found.")

    def load_samples(self, verbose=1):
        """Opens successively all the files, read them and adds the samples to the Audio object.
        If verbose is True, returns a progression percentage every 10%."""

        if verbose > 0:
            print("Opening audio from " + self.path + "...", end=" ")

        perc = 10  # Used for the progression percentage

        # If the path is a folder, we load every single file
        if os.path.isdir(self.path):

            for i in range(len(self.files)):

                if verbose > 1:
                    print("Loading file " + str(i) + " of " + str(len(self.files)) + ":" + self.path + "...", end=" ")

                # Show percentage if verbose
                perc = show_percentage(verbose, i, len(self.files), perc)

                # Loads a file containing one timestamp and one sample
                self.load_single_file(self.path + "/" + self.files[i])

                if verbose > 1:
                    print("OK.")

            self.calculate_frequency()

            if verbose > 0:
                print("100% - Done.\n")

        # Otherwise, we load the one file
        else:
            self.load_global_file(verbose)

    def load_single_file(self, path):

        # JSON file
        if path.split(".")[-1] == "json":
            data = open_json(path)
            self.samples.append(data["Samples"])
            self.timestamps.append(data["Timestamps"])

        # Excel file
        elif path.split(".")[-1] == "xlsx":
            import openpyxl as op
            workbook = op.load_workbook(path)
            sheet = workbook[workbook.sheetnames[0]]

            self.timestamps.append(float(sheet.cell(2, 1).value))
            self.samples.append(float(sheet.cell(2, 2).value))

        # Text file
        elif path.split(".")[-1] in ["txt", "csv"]:

            separator = get_filetype_separator(path)

            # Open the file and read the data
            data = open_txt(path)

            for s in range(1, len(data)):
                d = data[s].split(separator)
                self.timestamps.append(float(d[0][s]))
                self.samples.append(int(d[1][s]))

    def load_global_file(self, verbose=1):
        """Opens an audio file from a path and creates a list of samples and timestamps."""

        self.name = self.path

        if self.path.split(".")[-1] == "wav":
            self.read_wav(self.path, verbose)
        elif self.path.split(".")[-1] in ["xlsx", "json", "csv", "txt"]:
            self.read_txt(self.path, verbose)
        else:
            raise Exception("The path " + self.path + " is not a valid audio.")

    def read_wav(self, path, verbose=1):

        if verbose > 0:
            print("\n\tOpening the audio...", end=" ")

        audio_data = wavfile.read(path)
        self.frequency = audio_data[0]

        # Turn stereo to mono if the file is stereo
        if audio_data[1].shape[1] == 2:
            self.samples = self.stereo_to_mono(audio_data[1])
        else:
            self.samples = audio_data[1]

        if verbose > 0:
            print("Audio loaded.\n")

    def read_txt(self, path, verbose=1):

        if verbose > 0:
            print("Opening the audio...", end=" ")

        if path.split(".")[-1] == "json":
            data = open_json(path)
            self.samples = data["Samples"]
            self.frequency = data["Frequency"]

        elif path.split(".")[-1] == "xlsx":
            import openpyxl as op
            workbook = op.load_workbook(path)
            sheet = workbook[workbook.sheetnames[0]]

            joints_labels = []
            for cell in sheet["1"]:
                joints_labels.append(str(cell.value))

            # For each pose
            for s in range(2, len(sheet["A"])+1):

                if verbose > 1:
                    print("Loading sample " + str(s) + " of " + str(len(sheet["A"])) + "...", end=" ")

                self.timestamps.append(float(sheet.cell(s, 1).value))
                self.samples.append(int(sheet.cell(s, 2).value))

                if verbose > 1:
                    print("OK.")

            self.calculate_frequency()

        elif path.split(".")[-1] in ["csv", "txt"]:

            separator = get_filetype_separator(path)

            # Open the file and read the data
            data = open_txt(path)

            for s in range(1, len(data)):

                d = data[s].split(separator)

                if verbose > 1:
                    print("Loading sample " + str(s) + " of " + str(len(data)-1) + "...", end=" ")

                self.timestamps.append(float(d[0][s]))
                self.samples.append(int(d[1][s]))

                self.calculate_frequency()

                if verbose > 1:
                    print("OK.")

        if verbose:
            print("100% - Done.\n")

    # === Calculation functions ===

    def calculate_frequency(self):
        self.frequency = 1 / (self.timestamps[1] - self.timestamps[0])

    # === Modification functions ===

    @staticmethod
    def stereo_to_mono(sample_data, verbose=1):
        """Turns the sample data into mono by averaging the samples from the two channels."""

        if verbose > 0:
            print("\n\tConverting audio samples from stereo to mono...", end=" ")

        new_audio_array = []
        perc = 10

        for element in range(len(sample_data)):
            perc = show_percentage(verbose, element, len(sample_data), perc)
            new_audio_array.append(sample_data[element][0] + sample_data[element][1] // 2)

        if verbose > 0:
            print("100% - Done.")

        return new_audio_array

    def get_absolute_samples(self, verbose=1):
        """Returns a list of the absolute values of the samples (useful for plotting)"""

        if verbose > 0:
            print("Converting the audio samples to absolute values...")

        absolute_samples = []
        perc = 10

        for i in range(len(self.timestamps)):
            perc = show_percentage(verbose, i, len(self.timestamps), perc)
            absolute_samples.append(abs(self.samples[i]))
            if absolute_samples[i] == -32768:
                absolute_samples[i] = 32767

        if verbose > 0:
            print("100% - Done.\n")

    def resample(self, frequency, mode, verbose=1):
        """Resamples an audio file to a specific frequency."""

        if verbose > 0:
            print("Resampling the audio at "+str(frequency)+" Hz (mode: "+str(mode)+")...")
            print("\tPerforming the resampling...", end=" ")

        resampled_audio_array, resampled_audio_times = resample_data(self.samples, self.timestamps, frequency, mode)
        resampled_audio_array = list(resampled_audio_array)

        new_audio = Audio(resampled_audio_array, frequency)

        if verbose > 0:
            print("100% - Done.")
            print("\tOriginal audio had "+str(len(self.samples))+" samples.")
            print("\tNew audio has " + str(len(new_audio.samples)) + " samples.\n")

        return new_audio

    def calculate_envelope(self):
        """Calculates the envelope of the audio file."""
        self.envelope = np.abs(hilbert(self.samples))
        self.max_sample_envelope = max(self.envelope)
        self.min_sample_envelope = min(self.envelope)

    def resample_envelope(self, frequency, mode, verbose=1):
        """Resamples an audio file to a specific frequency."""

        if verbose > 0:
            print("Resampling the envelope of the audio at "+str(frequency)+" Hz (mode: "+str(mode)+")...")
            print("\tPerforming the resampling...", end=" ")

        resampled_envelope_array, resampled_envelope_times = resample_data(self.envelope, self.timestamps,
                                                                           frequency, mode)
        resampled_envelope_array = list(resampled_envelope_array)

        if verbose > 0:
            print("100% - Done.")
            print("\tOriginal audio had "+str(len(self.envelope))+" samples.")
            print("\tNew audio has " + str(len(resampled_envelope_array)) + " samples.\n")

        return resampled_envelope_array

    # === Getter functions ===

    def get_envelope(self):
        """Returns the envelope of the audio file."""
        return self.envelope

    def get_table(self):
        """Returns a list of lists containing the timestamps and samples of the audio file."""

        table = [["Timestamp", "Sample"]]

        # For each pose
        for s in range(len(self.samples)):
            table.append([self.timestamps[s], self.samples[s]])

        return table

    def get_json_samples(self):
        """Returns a json format containing the timestamps and the samples of the audio file."""

        data = {"Samples": self.samples, "Frequency": self.frequency}
        return data

    # === Saving functions ===

    def save(self, folder_out, name=None, file_format="xlsx", individual=False, verbose=1):
        """Saves the sequence in files in the path specified."""

        # Automatic creation of all the folders of the path if they don't exist
        subfolder_creation(folder_out)

        if name is None and self.name is not None:
            name = self.name
        elif name is None:
            name = "out"

        file_format = file_format.strip(".")  # We remove the dot in the format
        if file_format == "xls":
            file_format = "xlsx"

        if verbose > 0:
            if individual:
                print("Saving " + file_format.upper() + " individual files...")
            else:
                print(
                    "Saving " + file_format.upper() + " global file" + folder_out + name + "." + file_format + "...")

        # If file format is JSON
        if file_format == "json":
            self.save_json(folder_out, name, individual, verbose)

        # If file format is XLS or XLSX
        elif file_format == "xlsx":
            self.save_xlsx(folder_out, name, individual, verbose)

        # If file format is CSV or TXT
        else:
            self.save_txt(folder_out, file_format, name, individual, verbose)

        if verbose > 0:
            print("100% - Done.\n")

    def save_json(self, folder_out, name=None, individual=False, verbose=1):

        perc = 10  # Used for the progression percentage

        # Get the data
        data = self.get_json_samples()

        # Save the data
        if not individual:
            with open(folder_out + "/" + name + ".json", 'w', encoding="utf-16-le") as f:
                json.dump(data, f)
        else:
            for s in range(len(self.samples)):
                perc = show_percentage(verbose, s, len(self.samples), perc)
                with open(folder_out + "/sample_" + str(s) + ".json", 'w', encoding="utf-16-le") as f:
                    d = {"Samples": self.samples[s], "Timestamps": self.timestamps[s]}
                    json.dump(d, f)

    def save_xlsx(self, folder_out, name=None, individual=False, verbose=1):
        import openpyxl as op
        workbook_out = op.Workbook()
        sheet_out = workbook_out.active

        perc = 10  # Used for the progression percentage

        data = self.get_table()

        # Save the data
        if not individual:
            excel_write(workbook_out, sheet_out, data, folder_out + "/" + name + ".xlsx", perc, verbose)

        else:
            for s in range(len(self.samples)):
                d = [data[0], data[s+1]]
                perc = show_percentage(verbose, s, len(self.samples), perc)
                excel_write(workbook_out, sheet_out, d, folder_out + "/sample_" + str(s) + ".xlsx", perc, False)

    def save_txt(self, folder_out, file_format="csv", name=None, individual=False, verbose=1):

        perc = 10  # Used for the progression percentage

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
            data = table_to_string(self.get_table(), separator, perc, verbose)
            with open(folder_out + "/" + name + "." + file_format, 'w', encoding="utf-16-le") as f:
                f.write(data)
        else:
            for s in range(len(self.samples)):
                data = table_to_string(self.samples[s].convert_to_table(), separator, perc, False)
                perc = show_percentage(verbose, s, len(self.samples), perc)
                with open(folder_out + "/sample_" + str(s) + "." + file_format, 'w', encoding="utf-16-le") as f:
                    f.write(data)
