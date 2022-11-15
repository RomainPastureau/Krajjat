# **Krajjat 1.9.0**
Kinect Realignment Algorithm for Joint Jumps And Twitches

Author: Romain Pastureau

## What is it?
This program allows to automatically "smoothen" Kinect data by correcting the artifacts due to the real-time body tracking of Kinect. Full details on the algorithm used for the correction can be found in the PDF file in this repository.

## How to

### Core functions
* Realign corrects the joints twitches and jumps for Kinect sequences, as mentioned above. 
* Rereference corrects the joints for general body movement for Kinect sequences. It substracts the position of one joint (by default, MidSpine) for each joint, for each pose of the sequence.
These functions can be applied to one video, all the videos of a folder, or can find all the videos recursively in subfolders of a directory. The input must be the path of a folder containing .json data for each frame of the recorded Kinect sequence.

### Graphic functions
The repository comes with a series of graphic functions that can
be used for visualizing Kinect data.
* Sequence Reader allows to read a sequence as a video.
* Sequence Realigner allows to correct a sequence, and compare side-by-side the original and the corrected sequence.
* Sequence Comparer allows to compare two sequences side-by-side.
* Pose Reader allows to read a sequence starting on a specific pose and to control the display of the poses with the arrow keys. It also allows to show the matching video images in the background, as an option.
* Velocity Plotter plots the velocity across time of all the joints from a sequence.
* Joint Temporal Plotter plots the temporal data (x, y, and z coordinates, distance travelled and velocity) from a joint of one or more sequences across time.

### Dependencies
* **Openpyxl** to process .xls and .xlsx documents
* **Pygame** for sequence visualization
* **Matplotlib** for plottings
* **Scipy** to show the audio wave on the plottings

## What's new?

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
* Version 1.11 will add the possibility to generate MP4, AVI or MKV videos from motion sequences as displayed in Pygame.
* Version 1.11 will add the calculation of correlation between a motion sequence and an audio file, or a group of sequences and audio files.
* Version 1.12 will (try to) perform automatic gesture segregation.

If you detect any bug, please contact me at r.pastureau@bcbl.eu

Thanks :)