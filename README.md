# **Krajjat 1.10.1**
Kinect Realignment Algorithm for Joint Jumps And Twitches

Author: Romain Pastureau

## What is it?
This program allows to automatically "smoothen" Kinect data by correcting the artifacts due to the real-time body tracking of Kinect. Full details on the algorithm used for the correction can be found in the PDF file in this repository.

## How to

### Core functions
* Realign corrects the joints twitches and jumps for Kinect sequences, as mentioned above. 
* Rereference corrects the joints for general body movement for Kinect sequences. It substracts the position of one joint (by default, MidSpine) for each joint, for each pose of the sequence.
* Synchronize/Trim aligns, and allows to trim the sequence to an audio stream.
* Resample allows to resample the coordinates (with constant or variable original frame rate) to a defined new sampling rate.
These functions can be applied to one video, all the videos of a folder, or can find all the videos recursively in subfolders of a directory. The input must be the path of a folder containing .json data for each frame of the recorded Kinect sequence.

### Graphic functions
The repository comes with a series of graphic functions that can be used for visualizing Kinect data.
* Sequence Reader allows to read a sequence as a video.
* Sequence Realigner allows to correct a sequence, and compare side-by-side the original and the corrected sequence.
* Sequence Comparer allows to compare two sequences side-by-side.
* Pose Reader allows to read a sequence starting on a specific pose and to control the display of the poses with the arrow keys. It also allows to show the matching video images in the background, as an option.
* Velocity Plotter plots the velocity across time of all the joints from a sequence.
* Joint Temporal Plotter plots the temporal data (x, y, and z coordinates, distance travelled and velocity) from a joint of one or more sequences across time.
* Skeleton Video Saver allows to generate a MP4 video from the skeleton data.

### Statistical functions
The repository contains a series of statistical functions allowing to compare two time series (typically, envelope of the speech and joint velocity).
* Correlation
* Cross-correlation (currently developed)
* Coherence (planned)
* ICA (independent component analysis, planned)
* PCA (principal component analysis, planned)
* Mutual information (planned)

### Dependencies
* **Openpyxl** to process .xls and .xlsx documents
* **Pygame** for sequence visualization
* **Matplotlib** for plottings
* **Scipy** to show the audio wave on the plottings

## What's new?

### Version 2.0 (23/04/2023)
* Adding support for the Qualisys system (44 joints).
* Documentation has been added. Finally.
* Possibility to generate a video (supported formats: MP4, AVI and MKV) of a motion sequence from a recording. Possibility to add audio.
* Handling of TSV and MAT files.
* Correlation, cross-correlation and coherence between a sequence or a series of sequences and a joint or an audio file.
* Allows to display correlation and cross-correlation results on a silhouette.
* Now handles all HTML color names for creating color schemes.
* Large code sweeping.
* Krajjat acronym now means <i>Kinetic Recordings Algorithms for Joint Jazzing in an All-in-one Toolbox</i>.
* Renamed functions to be more in adequation with their use.
* Added non-linear de-jittering and window selection based on time instead of number of poses.
* Added a large number of methods for Sequence objects.
* Added a correct_zeros function for QualiSys recordings.

### Version 1.11 (25/11/2022)
* Correction of the realignment algorithm. Toggle between one and the other with the argument "mode" set as "new" or "false".
* Correction of the gestion of time, relative_time is the one used by default now.
* Correlation between a sequence or a series of sequences and an audio file.

### Version 1.10 (15/11/2022)
* Trim a motion sequence according to delay and audio duration, or to starting and ending timestamps.
* Resample a motion sequence according to a frequency.
* Add a name to the sequences.
* Verbose has now three levels: 2 is for showing all the info, 1 is for showing some info, 0 is for being completely opaque. 
* Performance and code sweeping.

### Version 1.9 (02/11/2022)
* Save and open sequences in new formats, including .json, .txt, .csv, and .xlsx. For the csv files, choose the separator.
* Possibility to save the sequences under one file per pose or one meta-file for the whole sequence.
* Get the stats from recordings (duration, average framerate, minimum framerate, maximum framerate, number of poses) for one or more recordings, and output them as a table.
* Visualize the framerate across time using the framerate_visualizer function.
* Batch open many sequences in a list with batch_loader and batch_loader_recursive.
* Code sweeping.

### Version 1.8 (18/10/2022)
* Added a function to re-reference all the joints to a reference joint (default: SpineMid). As for the realignment, the function can be called for a single file, a whole folder or a recursive path. This function can also place the reference joint at the coordinate (0, 0, 0).
* Created a tool function that allows to return the unique differences between two paths. For example, if the inputs are "C:/Documents/Kinect/John/Videos/A001" and "C:/Documents/Kinect/Paul/Videos/A001", the function will return "John and "Paul".
* The Pose Reader now allows to show the image frames in the background of the poses.
* The Joint Temporal Plotter function now can plot more than one sequence, and align automatically sequences that are trimmed from others.
* In the classes file, changed the name of the variable "joint_number" to "joint_name".
 
## What's next?
* Version 1.13 will add coherence to the statistical tests performed by the toolbox.
* Version 2.0 will add compatibility with other MoCap systems (mainly, handling non-Kinect joint labels).
* Version 2.0 will come with general functions renaming and options for customization.

If you detect any bug, please contact me at r.pastureau@bcbl.eu

Thanks :)