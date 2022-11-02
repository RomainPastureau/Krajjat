from core_functions import *
from graphic_functions import *

if __name__ == '__main__':
    folder = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Retellings/Gesture/"
    subject = "01_Araitz"
    video = "R018"

    sequences = load_sequences_folder(folder+"01_Original_gesture/"+subject)
    #sequence1 = Sequence(folder+"/01_Original_gesture/"+subject+"/"+video)
    #sequence2 = Sequence(folder+"/01_Original_gesture/"+subject+"/R019")
    #velocity_plotter(sequences[0])
    #sequences = [sequence1, sequence2]
    #framerate_plotter(sequences)
    save_stats(sequences, folder+"stats.xlsx")
    #print(sequence1.poses[34])
    #sequence1 = Sequence(folder+"/Test/global.csv")
    #save_sequence(sequence1, folder + "/Test/", file_format="xlsx", individual=False)
    # save_sequence(sequence1, folder + "/Test/csv", file_format="csv", individual=True)
    # save_sequence(sequence1, folder + "/Test/xls", file_format="xls", individual=True)
    # save_sequence(sequence1, folder + "/Test/xlsx", file_format="xlsx", individual=True)

    #sequence2 = Sequence(folder + "Test/txt/")
    #save_sequence(sequence2, folder + "/Test/indiv", file_format="txt", individual=False)
    #save_sequence(sequence2, folder + "/Test/indiv", file_format="csv", individual=False)
    #save_sequence(sequence2, folder + "/Test/indiv", file_format="xls", individual=False)
    #save_sequence(sequence2, folder + "/Test/indiv", file_format="xlsx", individual=False)