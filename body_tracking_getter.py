import json, os, sys, wave

folders = ["01_Araitz", "02_Ainhoa", "03_Amets", "04_Itziar", "05_Larraitz", "06_Laura"]

def read_delays():

    delays = {}
    print("Delays...")
    with open(file="delays.txt", mode="r") as read_file:
        content = read_file.read().split("\n")
        for line in content:
            items = line.split("\t")
            if items[0] not in delays.keys():
                delays[items[0]] = {}
            delays[items[0]][items[1]] = float(items[4])*1/25
    print("Delays done.\n")

    return(delays)

def get_audio_durations(folders):

    print("Audios...")
    path = "F:/Body Tracking Recordings/Audio/05_No_Noise_Normalized/"
    durations = {}
    for f in folders :
        durations[f] = {}

    for folder in folders:
        for f in os.listdir(path+folder) :
            print(folder+" "+f)
            sound = wave.open(path+folder+"/"+f, "r")
            framerate = sound.getframerate()
            duration = sound.getnframes()/framerate
            durations[folder][f[:-4]] = duration

            with open(file="durations.txt", mode="a") as write_file:
                write_file.write(str(folder)+"\t"+str(f[:-4])+"\t"+str(duration)+"\n")
            
    print("Audios done.\n")

    return(durations)

def read_audio_durations():
    durations = {}
    for f in folders :
        durations[f] = {}
        
    with open(file="durations.txt", mode="r") as read_file:
        f = read_file.read().split("\n")
        for line in f:
            l = line.split("\t")
            if len(l) > 1:
                durations[l[0]][l[1]] = float(l[2])

    return(durations)

def get_original_lengths(folders):
    print("Original lengths...")
    path = "F:/Body Tracking Recordings/Video/01_Original_videos/"
    
    original_lengths = {}
    for f in folders :
        original_lengths[f] = {}
        
    for folder in folders :
        print(folder, end=" ")
        for subfolder in os.listdir(path+folder) :
            print(subfolder, end=" ")
            files = [f for f in os.listdir(path+folder+"/"+subfolder+"/") if f.endswith(".json")]
            with open(file=path+folder+"/"+subfolder+"/"+files[0], mode="r", encoding="utf-16-le") as read_file:
                content = json.load(read_file)
                t1 = content["Timestamp"]
            with open(file=path+folder+"/"+subfolder+"/frame_"+str(len(files)-1)+".json", mode="r", encoding="utf-16-le") as read_file:
                content = json.load(read_file)
                t2 = content["Timestamp"]
            length = (t2-t1)/10000000
            original_lengths[folder][subfolder] = length
            with open(file="original_lengths.txt", mode="a") as write_file:
                write_file.write(str(folder)+"\t"+str(subfolder)+"\t"+str(length)+"\n")
        print("\n")
        
    print("Original lengths done.\n")

    return(original_lengths)

def read_original_lengths():
    original_lengths = {}
    for f in folders :
        original_lengths[f] = {}
        
    with open(file="original_lengths.txt", mode="r") as read_file:
        f = read_file.read().split("\n")
        for line in f:
            l = line.split("\t")
            if len(l) > 1:
                original_lengths[l[0]][l[1]] = float(l[2])

    return(original_lengths)

def get_resampled_lengths(folders):
    print("Resampled lengths...")
    path = "F:/Body Tracking Recordings/Video/03_Resampled_videos/"
    resampled_lengths = {}
    for f in folders :
        resampled_lengths[f] = {}
    for folder in folders :
        print(folder, end=" ")
        for subfolder in os.listdir(path+folder) :
            print(subfolder, end=" ")
            f = path+folder+"/"+subfolder+"/frame_session.json"
            with open(file=f, mode="r") as read_file:
                content = json.load(read_file)
                poses = content["bodyTrackingFrameData"]
                length = (poses[-1]["TimeStamp"] - poses[0]["TimeStamp"])/10000000
                resampled_lengths[folder][subfolder] = length
            with open(file="resampled_lengths.txt", mode="a") as write_file:
                write_file.write(str(folder)+"\t"+str(subfolder)+"\t"+str(length)+"\n")
        print("\n")
    print("Resampled lengths done.")

    return(resampled_lengths)

def read_resampled_lengths():
    resampled_lengths = {}
    for f in folders :
        resampled_lengths[f] = {}
        
    with open(file="resampled_lengths.txt", mode="r") as read_file:
        f = read_file.read().split("\n")
        for line in f:
            l = line.split("\t")
            if len(l) > 1:
                resampled_lengths[l[0]][l[1]] = float(l[2])

    return(resampled_lengths)

def get_gestures(folders, delays, durations, original_lengths, resampled_lengths):

    print("Gestures...")
    path = "F:/Body Tracking Recordings/Video/02_Realigned_videos/"
    for folder in folders :
        for subfolder in os.listdir(path+folder) :
            print(folder+" "+subfolder)
            poses = []

            ##Write table header

            joints_list = ["Head", "Neck", "SpineShoulder", "SpineMid",
                        "SpineBase", "ShoulderLeft", "ElbowLeft",
                        "WristLeft", "HandLeft", "ShoulderRight",
                        "ElbowRight", "WristRight", "HandRight", "HipLeft",
                        "KneeLeft", "AnkleLeft", "FootLeft", "HipRight",
                        "KneeRight", "AnkleRight", "FootRight"]

            line = ["Timestamp"]
            for j in joints_list :
                line.append(j+"_X")
                line.append(j+"_Y")
                line.append(j+"_Z")
            poses.append(line)

            try:
                delay = original_lengths[folder][subfolder] - resampled_lengths[folder][subfolder] + delays[folder][subfolder]
            except:
                delay = 0
            
            files = [f for f in os.listdir(path+folder+"/"+subfolder+"/") if f.endswith(".json")]
            
            t0 = None
            
            for file in files :
                
                line = []
                with open(file=path+folder+"/"+subfolder+"/"+file, mode="r", encoding="utf-16-le") as read_file:
                    data = json.load(read_file)
                    if t0 == None :
                        t0 = data["Timestamp"]
                    timestamp = (data["Timestamp"] - t0)/10000000
                    timestamp -= delay

                    line.append(timestamp)
                    
                joints = data["Bodies"][0]["Joints"]

                joints_from_file = {}
                for j in joints :
                    joints_from_file[j["JointType"]] = [j["Position"]["X"], j["Position"]["Y"], j["Position"]["Z"]]

                for j in joints_list:
                    line.append(joints_from_file[j][0])
                    line.append(joints_from_file[j][1])
                    line.append(joints_from_file[j][2])
                poses.append(line)

            with open(file="F:/Body Tracking Recordings/Gestures/01_Raw_gestures/"+folder+"/"+subfolder+".txt", mode="w") as write_file :
                for q in poses :
                    for l in q :
                        write_file.write(str(l)+"\t")
                    write_file.write("\n")
    print("Gestures done.")              

def main():

    folders = ["01_Araitz", "02_Ainhoa", "03_Amets", "04_Itziar", "05_Larraitz", "06_Laura"]

    delays = read_delays()
    durations = read_audio_durations()
    original_lengths = read_original_lengths()
    resampled_lengths = read_resampled_lengths()
    
    print(original_lengths["05_Larraitz"])
    print(resampled_lengths["05_Larraitz"])
    print(durations["05_Larraitz"])
    print(delays["05_Larraitz"])

    get_gestures(folders, delays, durations, original_lengths, resampled_lengths)

if __name__ == '__main__':
    main()
