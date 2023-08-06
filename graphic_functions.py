#!/usr/bin/env python
"""krajjat 1.10
Kinect Realignment Algorithm for Joint Jumps And Twitches
Author: Romain Pastureau
This file contains the main graphic functions. This is the
file to run to use any of the graphic functions.
"""
import shutil

from io_functions import *
from classes.graphic_classes import *
from tool_functions import *
import cv2
import sys

__author__ = "Romain Pastureau"
__version__ = "1.10"
__email__ = "r.pastureau@bcbl.eu"
__license__ = "GPL"


def common_displayer(folder_or_sequence1, folder_or_sequence2=None, show_lines=True, ignore_bottom=False,
                     resolution=(1600, 900), full_screen=False, manual=False, show_image=False, path_images=None,
                     start_pose=0, realign=False, folder_save=None, superposed=False, type="square",
                     color_joint="default", shift_x=0, shift_y=0, scale=1, ratio_joint=1, velocity_threshold=10, w=3):
    # If folderOrSequence is a folder, we load the sequence; otherwise, we just attribute the sequence
    if folder_or_sequence1 is str:
        sequence1 = Sequence(folder_or_sequence1)
    else:
        sequence1 = folder_or_sequence1

    # Realignment and saving of the realignment
    if realign:
        sequence2 = sequence1.correct_jitter(velocity_threshold, w, verbose=False)
        if folder_save:
            save_sequences(sequence1, sequence2, folder_save)
    else:
        if folder_or_sequence2 is str:
            sequence2 = Sequence(folder_or_sequence2)
        else:
            sequence2 = folder_or_sequence2

    # If the resolution is None, we just create a window the size of the screen
    if resolution is None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)

    # We set to full screen
    if full_screen:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode(resolution)

    pygame.mouse.set_visible(True)  # Allows the mouse to be visible
    disp = _GraphicWindow(window)  # Contains the window and resizing info

    # Generates a graphic sequence from the sequence
    animation1 = _GraphicSequence(sequence1, disp, show_lines, ignore_bottom, start_pose, path_images,  scale)
    animation2 = None
    if sequence2 is not None:
        animation2 = _GraphicSequence(sequence2, disp, show_lines, ignore_bottom, start_pose, path_images, scale)

    program = True

    # Program loop
    while program:

        window.fill((0, 0, 0))  # Set background to black

        for ev in pygame.event.get():

            # Leave the program
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                program = False
                break

            if manual:
                if ev.type == KEYDOWN and ev.key == K_RIGHT:
                    animation1.next_pose()
                elif ev.type == KEYDOWN and ev.key == K_LEFT:
                    animation1.previous_pose()

        if manual:
            animation1.show_pose(window, show_lines, show_image, shift_x=shift_x, shift_y=shift_y, type=type,
                                 color_joint=color_joint, ratio=ratio_joint)
        elif sequence2 is None:
            animation1.show(window, show_lines, shift_x=shift_x, shift_y=shift_y, type=type, color_joint=color_joint,
                            ratio=ratio_joint)
        else:
            if superposed:
                animation1.show(window, show_lines, shift_x=shift_x, shift_y=shift_y, type=type,
                                color_joint=color_joint, ratio=ratio_joint)
                animation2.show(window, show_lines, shift_x=shift_x, shift_y=shift_y, type=type,
                                color_joint=color_joint, ratio=ratio_joint)
            else:
                animation1.show(window, show_lines, shift_x=-300+shift_x, shift_y=shift_y, type=type,
                                color_joint=color_joint, ratio=ratio_joint)
                animation2.show(window, show_lines, shift_x=300+shift_x, shift_y=shift_y, type=type,
                                color_joint=color_joint, ratio=ratio_joint)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def sequence_reader(folder_or_sequence, show_lines=True, ignore_bottom=False, resolution=(1600, 900),
                    full_screen=False, type="square", color_joint="default", scale=1, shift_x=0, shift_y=0,
                    ratio_joint=1):
    """Displays the joints of the sequence in real time and loops back to the beginning when over."""

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen, type=type,
                     color_joint=color_joint, scale=scale, shift_x=shift_x, shift_y=shift_y, ratio_joint=ratio_joint)


def sequence_realigner(folder_or_sequence, velocity_threshold, w, folder_save=None, show_lines=True,
                       ignore_bottom=False, resolution=(1600, 900), full_screen=False, type="square",
                       color_joint="default", scale=1, shift_x=0, shift_y=0, ratio_joint=1):
    """Realigns a sequence, then displays the original and the realigned sequence side by side."""

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen, realign=True,
                     folder_save=folder_save, velocity_threshold=velocity_threshold, w=w, type=type,
                     color_joint=color_joint, scale=scale, shift_x=shift_x, shift_y=shift_y, ratio_joint=ratio_joint)


def sequence_comparer(folder_or_sequence1, folder_or_sequence2, show_lines=True, ignore_bottom=False,
                      resolution=(1600, 900), superposed=False, full_screen=False, type="square",
                      color_joint="default", scale=1, shift_x=0, shift_y=0, ratio_joint=1):
    """Compares two sequences side by side."""

    common_displayer(folder_or_sequence1, folder_or_sequence2, show_lines, ignore_bottom, resolution, full_screen,
                     superposed=superposed, type=type, color_joint=color_joint, scale=scale, shift_x=shift_x,
                     shift_y=shift_y, ratio_joint=ratio_joint)


def pose_reader(folder_or_sequence, start_pose=0, show_lines=True, show_image=True, ignore_bottom=False,
                resolution=(1600, 900), full_screen=False, path_images=None, type="square", color_joint="default",
                scale=1, shift_x=0, shift_y=0, ratio_joint=1):
    """Reads a sequence and offers a manuel control over the poses (with the arrows of the keyboard)."""

    common_displayer(folder_or_sequence, None, show_lines, ignore_bottom, resolution, full_screen, True,
                     show_image, start_pose=start_pose, path_images=path_images, type=type, color_joint=color_joint,
                     scale=scale, shift_x=shift_x, shift_y=shift_y, ratio_joint=ratio_joint)


def save_skeleton_video(sequence, output_name, frequency=25, show_lines=False, ignore_bottom=True, start_pose=0,
                        path_images=None, resolution=(950,534), shift_x=0, shift_y=0, full_screen=False, verbose=1):

    # If the resolution is None, we just create a window the size of the screen
    if resolution is None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)

    # We set to full screen
    if full_screen:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode(resolution)

    disp = _GraphicWindow(window)  # Contains the window and resizing info
    animation = _GraphicSequence(sequence, disp, show_lines, ignore_bottom, start_pose, path_images,  1.7)

    print("Generating images...", end=" ")

    # Create the temporary folder
    tempfolder = "tempfolder_"+(output_name.split("/")[-1]).split(".")[0]
    if os.path.exists(tempfolder):
        shutil.rmtree(tempfolder)
    create_subfolders(tempfolder)
    images = []
    perc = 10

    for pose in range(len(animation.poses)):

        if verbose > 1:
            if pose == 0:
                print("")
            print("\tGenerating image "+str(pose+1)+" of "+str(len(animation.poses))+"...")
        else:
            perc = show_progression(verbose, pose, len(animation.poses), perc, step=10)

        window.fill((0, 0, 0))
        animation.show_pose(window, show_lines, False, shift_x, shift_y, "circle", (255, 255, 255), 1.7)
        pygame.display.flip()
        img = tempfolder+"/s"+"{:05d}".format(pose)+".png"
        images.append(img)
        pygame.image.save(window, img)
        animation.next_pose()
    print("100% - Done.")
    print("Images generated.")
    print("Generating video...")

    timestamps = sequence.get_timestamps()
    #print(timestamps)
    #print(images)

    new_images, new_timestamps = resample_images_to_frequency(images, timestamps, frequency)
    #print(new_timestamps)
    #print(new_images)

    create_subfolders(output_name)

    #images = [img for img in os.listdir("temp_folder") if img.endswith(".png")]
    frame = cv2.imread(new_images[0])
    height, width, layers = frame.shape

    video = cv2.VideoWriter(output_name, 0, frequency, (width, height))

    for image in new_images:
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()

    print("Video generated.")

    shutil.rmtree(tempfolder)

    print("Temporary folder deleted.")

