# **Krajjat 1.99.15**
### ~~Kinect Realignment Algorithm for Joint Jumps And Twitches~~
### ~~Kinetic Recordings Algorithms for Joint Jazzing in an All-in-one Toolbox~~
### Kinetic Recordings And Juxtaposition of Jabbering Along That

Author: Romain Pastureau

## What is Krajjat?
Krajjat is a **Python module** allowing to handle **motion capture recordings** and to explore the relationship
between **body movements** and **speech**. More precisely, it contains a variety of functions allowing to 
**pre-process** sequences of tracked movements, to **display** them and to **analyze** them.
You can find more details in the [documentation](https://krajjat.readthedocs.io/en/latest/).

### Pre-processing
The pre-processing functions allow to:
* Automatically correct fast artifacts in the recordings (jumps and twitches of joints placement).
* Re-reference all the positions according to a specific joint.
* Trimming a motion sequence to the duration of an audio file, or to a defined duration.
* Resampling a motion sequence to a target frequency.
* Correcting zero values via interpolation.
All of these functions can be applied on single motion sequences, or on a batch of sequences.

### Display
The display functions allow to:
* Display a sequence pose by pose or in real time, with highly customizable visualization options.
* Display a sequence concurrently to an audio and/or a video file; the video file can be played below it or next to it.
* Display two sequences side by side, to compare before and after pre-processing, for example.
* Save any of the previous displays as a MP4 video.

### Analysis
The toolbox comes with a series of functions for analyses of the sequences to:
* Plot the values of the x, y and z coordinates, the distance travelled, and the absolute changes of speed and 
  acceleration across time for any given joint.
* Plot one of these values for all the joints, with the sub-plots organized according to their position in space.
* Get the envelope, the pitch, the intensity of the formants from an audio file containing speech.
* Performing the correlation, cross-correlation, coherence, ICA/PCA, or getting the mutual information between any of
  the kinetic properties of the joints and the acoustic properties of the speech - along with the statistics to compute 
  the significance of the relationship between the two arrays of values.

## How to
The best way to install the toolbox is to follow the recommendations in the 
[documentation](https://krajjat.readthedocs.io/en/latest/).

### Dependencies
* **Scipy** and **Numpy** for handling audio files and large numeric arrays
* **Matplotlib** and **Seaborn** for plottings
* **Pandas** to create dataframes for the analysis functions
* **chardet** to detect the encoding of files
* **Openpyxl** to process .xls and .xlsx documents
* **Pygame** for sequence visualization
* **OpenCV** and **PyAudio** for displaying video and audio
* **Parselmouth** to use Praat functions to process the audio files
* **FFmpeg** to save videos

## What's new?
See the [release notes](<https://krajjat.readthedocs.io/en/latest/release_notes.html>).

If you detect any bug, please contact me following [this link](mailto:r.pastureau@bcbl.eu).

Thanks :)