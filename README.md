# **Krajjat 1.8.0**
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

## What's new?

### Version 1.8
* Added a function to re-reference all the joints to a reference joint (default: SpineMid). As for the realignment, the function can be called for a single file, a whole folder or a recursive path. This function can also place the reference joint at the coordinate (0, 0, 0).
* Created a tool function that allows to return the unique differences between two paths. For example, if the inputs are "C:/Documents/Kinect/John/Videos/A001" and "C:/Documents/Kinect/Paul/Videos/A001", the function will return "John and "Paul".
* The Pose Reader now allows to show the image frames in the background of the poses.
* The Joint Temporal Plotter function now can plot more than one sequence, and 
* In the classes file, changed the name of the variable "joint_number" to "joint_name".
 
## What's next?
* Version 1.9 will add the possibility of working with different formats. Global .json files will be usable, along with .txt, .csv, .xls, .xlsx and .mat files.
* Version 1.9 will add the possibility to trim a motion sequence according to starting and ending timestamps.
* Version 1.9 will add a function to know the minimum, maximum and average framerate of a recording and to visualize a graph of the framerate across time. It will also furnish a list of this data in the form of an Excel file.
* Version 1.10 will add the possibility to resample the data as in Matlab.
* Version 1.10 will also perform some performance and code sweeping.

If you detect any bug, please contact me at r.pastureau@bcbl.eu

Thanks :)