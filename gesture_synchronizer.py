from realigner import *
from body_tracking_getter import *

def synchronize_gesture(input_folder, output_folder, subject, video):

    sequence = Sequence(input_folder+"/"+subject+"/"+video)
    original_start = sequence.poses[0].timestamp
    print(original_start)
    original_end = sequence.poses[-1].timestamp
    print(original_end)
    original_duration = original_end - original_start

    new_sequence = Sequence(None)

    #for p in sequence.poses :
        #p.timestamp = p.timestamp - original_start

    delays = read_delays()
    durations = read_audio_durations()
    original_lengths = read_original_lengths()
    resampled_lengths = read_resampled_lengths()

    try:
        delay = original_lengths[subject][video] - resampled_lengths[subject][video] + delays[subject][video]
    except:
        delay = 0

    files = [f for f in os.listdir(path+folder+"/"+subfolder+"/") if f.endswith(".json")]
            
    for p in range(len(sequence.poses)) :
        
        timestamp = (p.timestamp - original_start)/10000000
        timestamp -= delay

        if 0 <= timestamp <= durations[subject][video] :
            sequence.copy_pose(new_sequence, p)
            new_sequence.poses[p].timestamp = timestamp*10000000
        
    save_json(sequence, sequence, output_folder)

if __name__ == '__main__':

    main_folder = "G:/BodyLingual/"

    input_folder = main_folder+"Recordings/Gesture/02_Realigned_gesture"
    output_folder = main_folder+"Recordings/Gesture/03_Synchronized_gesture"
    subject = "02_Ainhoa"
    video = "R077"

    

    synchronize_gesture(input_folder, output_folder, subject, video)
