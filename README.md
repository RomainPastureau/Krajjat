# **Krajjat 1.6.1**
Kinect Realignment Algorithm for Joint Jumps And Twitches

Author: Romain Pastureau

## What is it
This program allows to automatically "smoothen" Kinect data by
correcting the artifacts due to the real-time body tracking of
Kinect. Full details on the algorithm used for the correction
can be found in the PDF file in this repository.

## How to

### Core functions
Correct the joints for one video, all the videos of a folder, 
or find all the videos recursively in subfolders of a directory.
The input must be the path of a folder containing .json data
for each frame of the recorded Kinect sequence.

### Graphic functions
The repository comes with a series of graphic functions that can
be used for visualizing Kinect data.
* Sequence Reader allows to read a sequence as a video.
* Sequence Realigner allows to correct a sequence, and compare
side-by-side the original and the corrected sequence.
* Sequence Comparer allows to compare two sequences side-by-side.
* Pose Reader allows to read a sequence starting on a specific pose
and to control the display of the poses with the arrow keys.
* Velocity Plotter plots the velocity across time of all the joints
from a sequence.
* Joint Temporal Plotter plots the temporal data (x, y, and z 
coordinates, distance travelled and velocity) from a joint of a 
sequence across time.

If you detect any bug, please contact me at r.pastureau@bcbl.eu

Thanks :)