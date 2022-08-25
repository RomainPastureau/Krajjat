import copy, json, os, random, sys
import random
import math

class Sequence(object):

    def __init__(self, folder):
        self.poses = []
        self.randomized = False

        if folder != None :
            self.folder = folder
            self.get_files()
            self.load_poses()
            self.load_relative_times()

        self.calculate_distance()

    def print_json(self, pose):
        data = self.poses[pose].get_json_data()
        print(json.dumps(data, indent=4))

    ##Opens a folder and gets all the .json files.
    def get_files(self):

        file_list = os.listdir(self.folder)
        self.files = ["" for i in range(len(file_list))]

        meta_found = False
        size = None

        for f in file_list :
            if f[-4:] == "json":
                self.files[int(f.split(".")[0].split("_")[1])] = f
            elif f[-4:] == "meta":
                meta_found = True
                size = self.get_meta(f)

        if "" in self.files :
            limit = self.files.index("")
            self.files = self.files[0:limit]
                
            if meta_found == False :
                raise Exception(".meta file not found.")
            else :
                if size > len(self.files) :
                    raise Exception("According to the .meta file, some .json files are "+
                                    "missing. The .meta file lists "+str(size)+" file(s) while "+
                                    str(len(self.files))+" .json file(s) have been found.")

        print(str(len(self.files))+" pose file(s) found.\n")

    def get_meta(self, file):
        f = open(self.folder+"/"+file, "r")
        fileread = f.read().split("\n")
        f.close()
        return(len(fileread))

    ##Opens all the .json files and saves them as Pose objects
    def load_poses(self, verbose=True):

        self.poses = []
        print("Opening poses...")
        j = 10
        for i in range(len(self.files)) :
            if i/len(self.files) > j/100 and verbose == True :
                print(str(j)+"%", end=" ")
                j += 10
            pose = Pose(i, self.folder + "/" + self.files[i])
            self.poses.append(pose)
         
        if verbose == True :
            print("100% - Done.\n")

    ##Loads all the times relative to the first frame
    def load_relative_times(self):
        t = self.poses[0].get_timestamp()
        for f in self.poses:
            f.set_relative_time(t)

    ##Calculates the distance travelled between two poses and divides it
    ##by the time between the two poses
    def calculate_distance(self):

        for f in range(1, len(self.poses)):

            for j in self.poses[0].joints.keys() :

                speed = self.get_speed(self.poses[f-1], self.poses[f], j)
                self.poses[f].joints[j].set_movement(speed)

    ##Gets the distance between two points (in meters)
    def get_distance(self, jointA, jointB):
        x = (jointB.x - jointA.x)**2
        y = (jointB.y - jointA.y)**2
        z = (jointB.z - jointA.z)**2
        
        return(math.sqrt(x + y + z))

    def getX(self, joint):
        return(joint.x)

    def getY(self, joint):
        return(joint.y)

    def getZ(self, joint):
        return(joint.z)

    ##Gets the delay between two frames (in tenth of microsecond - 10^-7)
    def get_delay(self, frameA, frameB):
        tA = frameA.get_timestamp()
        tB = frameB.get_timestamp()
        return(tB-tA)

    ##Gets the speed (in cm per second)
    def get_speed(self, pose1, pose2, joint):

        ##Gets distance between the same joint on two subsequent frames (meters)
        dist = self.get_distance(pose1.joints[joint], pose2.joints[joint])

        ##Gets the delay between the two frames (hundreds of seconds)
        delay = self.get_delay(pose1, pose2)/1000000000

        ##Gets the speed (m per hundreds of seconds, or cm per second)
        speed = dist/delay

        return(speed)

    ##Returns an array of timestamps
    def get_timestamps(self):

        timestamps = []
        for pose in self.poses :
            timestamps.append(pose.get_relative_time())

        return(timestamps)

    ##Creates an empty sequence with empty poses and empty joints
    def create_new_sequence(self):
        print("Creating an empty sequence...")
        self.new_sequence = Sequence(None)
        i = 10
        for p in range(len(self.poses)) :
            if p/len(self.poses) > i/100 :
                print(str(i)+"%", end=" ")
                i += 10
            pose = self.poses[p].get_clear_copy()
            self.new_sequence.poses.append(pose)
        self.new_sequence = self.copy_pose(self.new_sequence, 0)
        print("100% - Done.\n")

    ##Copies the joints from a pose that don't already exist in the target sequence
    def copy_pose(self, sequence, pose_number):
        for j in self.poses[pose_number].joints.keys():
            if j not in sequence.poses[pose_number].joints.keys() :
                sequence.poses[pose_number].joints[j] = self.copy_joint(pose_number, j)
        return(sequence)

    ##Copies a single joint
    def copy_joint(self, pose_number, joint_name):
        joint = copy.copy(self.poses[pose_number].get_joint(joint_name))
        return(joint)
    
    ##Realignement function
    def realign(self, speed_threshold, window, verbose=True):

        ##Copy the first pose and adds it to a new sequence
        self.create_new_sequence()

        print("Starting realignment...")

        ##Counters
        realigned_points = 0
        i = 10
        
        for p in range(1, len(self.poses)):

            if verbose:
                print("\nNew sequence:\n"+str(self.new_sequence.poses[p-1]))
                print("\n== POSE NUMBER "+str(p+1)+" ==")

            if p/len(self.poses) > i/100 and verbose == False:
                print(str(i)+"%", end=" ")
                i += 10

            ##Checks every joint
            for j in self.poses[0].joints.keys() :
                
                speed_before = self.get_speed(self.new_sequence.poses[p-1], self.poses[p], j)

                if verbose:
                    print(j+": "+str(speed_before))

                if j in self.new_sequence.poses[p].joints :

                    if verbose:
                        print("\tAlready corrected.")

                ##If speed over threshold
                elif speed_before > speed_threshold and p != len(self.poses) - 1 :

                    if verbose:
                        print("\tSpeed over threshold. Check in subsequent poses...")

                    ##Checks for every subsequent pose from the window
                    for k in range(p, min(p+window, len(self.poses))):

                        if verbose:
                            print("\t\tPose "+str(k+1)+":", end=" ")

                        speed = self.get_speed(self.new_sequence.poses[p-1], self.poses[k], j)

                        ##If one of the poses of the window is below threshold compared to previous pose
                        if speed < speed_threshold :

                            if verbose:
                                print("no threshold deviation compared to pose "+str(p+1)+".")
                                print("\t\t\tCorrecting for twitch...")

                            realigned_points = self.correction(p-1, k, j, realigned_points, verbose)
                                
                            break

                        elif k == p + window - 1 or k == len(self.poses) - 1 :

                            if verbose:
                                print("original deviation not found.")
                                print("\t\t\tCorrecting for jump...")

                            realigned_points = self.correction(p-1, k, j, realigned_points, verbose)
                                
                            break                            

                        else :

                            if verbose:
                                print("still over threshold.")

                    if verbose:
                        print("")

                else :

                    joint = self.copy_joint(p, j)
                    self.new_sequence.poses[p].add_joint(j, joint)
                    self.new_sequence.poses[p].joints[j].corrected = False

        print("100% - Done.\n")
        print("Realignment over. "+str(realigned_points)+" point(s) realigned over "+str(len(self.poses)*len(list(self.poses[0].joints.keys())))+".\n")

        return(self.new_sequence)

    ##Corrects one single joint (depending on the number of the frame)
##    def correct_joint_old(self, joint, joint_before, joint_after, joint_no, total_joints):
##        #print(joint, joint_before, joint_after, joint_no, total_joints)
##        x = joint_before.x - (joint_no + 1) * ((joint_before.x - joint_after.x) / (total_joints + 1))
##        y = joint_before.y - (joint_no + 1) * ((joint_before.y - joint_after.y) / (total_joints + 1))
##        z = joint_before.z - (joint_no + 1) * ((joint_before.z - joint_after.z) / (total_joints + 1))
##        
##        return(x, y, z)

    ##Corrects one single joint (depending on the time between frames)
    def correct_joint(self, joint_before, joint_after, pose_before, pose_current, pose_after, verbose):

        percentage_time = (self.poses[pose_current].timestamp - self.poses[pose_before].timestamp) / (self.poses[pose_after].timestamp - self.poses[pose_before].timestamp)

        if verbose :
            print("\t\t\t\tJoint "+str(pose_current+1)+" positionned at "+str(percentage_time*100)+" % between poses "+str(pose_before+1)+" and "+str(pose_after+1)+".")
        
        x = joint_before.x - percentage_time * (joint_before.x - joint_after.x)
        y = joint_before.y - percentage_time * (joint_before.y - joint_after.y)
        z = joint_before.z - percentage_time * (joint_before.z - joint_after.z)

        return(x, y, z)

    ##Performs a jump or twitch correction
    def correction(self, start_pose_number, end_pose_number, joint_number, realigned_points, verbose):

        joint_before = self.new_sequence.poses[start_pose_number].joints[joint_number]
        joint_after = self.poses[end_pose_number].joints[joint_number]

        if start_pose_number == end_pose_number :
            joint = self.copy_joint(start_pose_number, joint_number)
            self.new_sequence.poses[start_pose_number].add_joint(joint_number, joint)

            if verbose :
                print("\t\t\t\tDid not corrected joint "+str(pose_number)+" as it is the last pose of the sequence.")

        for pose_number in range(start_pose_number+1, end_pose_number):

            if self.poses[pose_number].joints[joint_number].corrected == True :

                if verbose :
                    print("\t\t\t\tDid not corrected joint "+str(l+1)+" as it was already corrected.")

            else :

                x, y, z = self.correct_joint(joint_before, joint_after, start_pose_number, pose_number, end_pose_number, verbose)
                joint = self.copy_joint(pose_number, joint_number)
                joint.correct_joint(x, y, z)
                self.new_sequence.poses[pose_number].add_joint(joint_number, joint)
                if verbose:
                    print("\t\t\t\tCorrecting joint: "+str(pose_number+1)+". Original coordinates: ("+str(self.poses[pose_number].joints[joint_number].x)+
                    ", "+str(self.poses[pose_number].joints[joint_number].y)+", "+str(self.poses[pose_number].joints[joint_number].z)+")")                                                     
                    print("\t\t\t\tPrevious joint: "+str(start_pose_number+1)+". ("+str(self.new_sequence.poses[start_pose_number].joints[joint_number].x)+
                    ", "+str(self.new_sequence.poses[start_pose_number].joints[joint_number].y)+", "+str(self.new_sequence.poses[start_pose_number].joints[joint_number].z)+")")
                    print("\t\t\t\tNext joint: "+str(end_pose_number+1)+". ("+str(self.poses[end_pose_number].joints[joint_number].x)+
                    ", "+str(self.poses[end_pose_number].joints[joint_number].y)+", "+str(self.poses[end_pose_number].joints[joint_number].z)+")")
                    print("\t\t\t\tCorrected joint "+str(pose_number+1)+". New coordinates: ("+str(x)+", "+str(y)+", "+str(z)+")\n")

                realigned_points += 1

        return(realigned_points)

    ##Prints all the information relative to one pose
    def print_pose(self, pose):
        txt = "Pose "+str(pose+1)+" of "+str(len(self.poses))+"\n"
        txt += str(self.poses[pose])
        print(txt)

    def randomize(self):
        self.startingPositions = []
        for joint in self.poses[0].joints.keys() :
            self.startingPositions.append(copy.copy(self.poses[0].joints[joint]))
        self.randomizedPositions = self.generateRandomJoints()
        random.shuffle(self.randomizedPositions)
        joints_list = list(self.poses[0].joints.keys())
        for p in self.poses :
            for j in range(len(joints_list)) :
                p.joints[joints_list[j]].move_joint(self.startingPositions[j], self.randomizedPositions[j])
        self.randomized = True

    def generateRandomJoints(self):
        randomJoints = []
        for i in range(21):
            x = random.uniform(-0.2, 0.2)
            y = random.uniform(-0.5, 0.5)
            z = random.uniform(-0.5, 0.5)
            j = Joint(None, [x, y, z])
            randomJoints.append(j)
        return(randomJoints)

    def __len__(self):
        return(len(self.poses))

def compareSequences(sequence1, sequence2):

    different_joints = 0
    total_joints = 0

    for p in range(len(sequence1.poses)) :
        for j in sequence1.poses[p].joints.keys() :
            if round(sequence1.poses[p].joints[j].x, 5) == round(sequence2.poses[p].joints[j].x, 5) and\
            round(sequence1.poses[p].joints[j].y, 5) == round(sequence2.poses[p].joints[j].y, 5) and\
            round(sequence1.poses[p].joints[j].z, 5) == round(sequence2.poses[p].joints[j].z, 5) :
                total_joints += 1
            else :
                #print("Pose n°"+str(p)+", "+str(j))
                #print("X: "+str(sequence1.poses[p].joints[j].x)+"; Y: "+str(sequence1.poses[p].joints[j].y)+"; Z: "+str(sequence1.poses[p].joints[j].z))
                #print("X: "+str(sequence2.poses[p].joints[j].x)+"; Y: "+str(sequence2.poses[p].joints[j].y)+"; Z: "+str(sequence2.poses[p].joints[j].z))
                different_joints += 1
                total_joints += 1

    print("Different joints: "+str(different_joints)+"/"+str(total_joints)+" ("+str(different_joints/total_joints)+"%).")

    return(different_joints, total_joints)

class Pose(object):

    def __init__(self, no, file):
        self.no = no
        self.joints = {}
        self.timestamp = None

        if file != None :
            self.file = file
            self.read()

    ##Reads the contents of one json file
    def read(self):
        f = open(self.file, "r", encoding="utf-16-le")
        content = f.read()
        f.close()

        data = json.loads(content)

        self.timestamp = data["Timestamp"]
        self.read_joints(data)

    def get_json_data(self):
        f = open(self.file, "r", encoding="utf-16-le")
        content = f.read()
        f.close()

        data = json.loads(content)

        return(data)

    ##Reads all the joints from the json format
    def read_joints(self, data):
        for joint in data["Bodies"][0]["Joints"] :
            self.joints[joint["JointType"]] = Joint(joint)

    def add_joint(self, name, joint):
        self.joints[name] = joint

    def get_joint(self, name):
        return(self.joints[name])

    ##Returns the original json timestamp
    def get_timestamp(self):
        return(self.timestamp)

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    ##Sets the relative time compared to the time from the first pose (in sec)
    def set_relative_time(self, t):
        self.relative_time = (self.timestamp - t)/10000000

    ##Gets the relative time of this pose compared to the first one
    def get_relative_time(self):
        return(self.relative_time)

    ##Prints all the joints
    def __repr__(self):
        txt = ""
        if len(list(self.joints.keys())) == 0 :
            txt = "Empty list of joints."
        for j in self.joints.keys():
            txt += str(self.joints[j])+"\n"
        return(txt)

    def get_clear_copy(self):
        p = Pose(self.no, self.file)
        p.joints = {}
        p.set_timestamp(self.timestamp)
        p.relative_time = self.relative_time
        return(p)

class Joint(object):

    def __init__(self, data, coord=None):
        if coord == None :
            self.read_data(data)
            self.color = (255, 255, 255)
        else :
            self.x = coord[0]
            self.y = coord[1]
            self.z = coord[2]
            self.color = (0, 255, 0)
        self.movement = None
        self.move_much = False
        self.corrected = False
        self.randomized = False
        
    def read_data(self, data):
        self.joint_type = data["JointType"]
        self.x = data["Position"]["X"]
        self.y = data["Position"]["Y"]
        self.z = data["Position"]["Z"]
        self.position = [self.x, self.y, self.z]
        
    def correct_joint(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.corrected = True
        
    def set_move_much(self, move):
        self.move_much = move
        if move == True :
            self.color = (255, 50, 50)
        else :
            self.color = (255, 255, 255)

    def set_movement(self, movement):
        self.movement = movement

    def get_movement(self, movement):
        return(self.movement)

    def get_copy(self):
        return(copy.copy(self))

    def move_joint(self, origin, joint):
        #print("Before: "+str(self.x)+", "+str(self.y)+", "+str(self.z))
        self.x = joint.x + (self.x - origin.x)
        self.y = joint.y + (self.y - origin.y)
        self.z = joint.z + (self.z - origin.z)
        self.randomized = True
        #print("After: "+str(self.x)+", "+str(self.y)+", "+str(self.z))

    def __repr__(self):
        txt = self.joint_type+": ("+str(self.x)+", "+str(self.y)+", "+str(self.z)+")"
        txt += " - Shift: "+str(self.movement)
        if self.move_much == True :
            txt += " OVER THRESHOLD"
        if self.corrected == True :
            txt += " CORRECTED"
        return(txt)

def save_json(original_sequence, new_sequence, folder_out):

    i = 10

    folders = folder_out.split("/")

    for k in range(len(folders)):
        f = ""
        for l in range(k+1):
            f += folders[l] + "/"
        if not os.path.exists(f):
            os.mkdir(f)
            print("Creating folder: "+f)

    print("Saving JSON files...")
    
    for p in range(len(original_sequence.poses)):
        
        if p/len(original_sequence.poses) > i/100 :
            print(str(i)+"%", end=" ")
            i += 10
            
        data = original_sequence.poses[p].get_json_data()
        file = original_sequence.poses[p].file

        for joint in range(len(data["Bodies"][0]["Joints"])):
            
            joint_type = data["Bodies"][0]["Joints"][joint]["JointType"]
            j = new_sequence.poses[p].joints[joint_type]
            data["Bodies"][0]["Joints"][joint]["Position"]["X"] = j.x
            data["Bodies"][0]["Joints"][joint]["Position"]["Y"] = j.y
            data["Bodies"][0]["Joints"][joint]["Position"]["Z"] = j.z

        file = original_sequence.poses[p].file.split("/")[-1]

        with open(folder_out+"/"+file, 'w', encoding="utf-16-le") as f:
            json.dump(data, f)

    print("- Done.\n")

def main(input_folder, output_folder, speed_threshold, window, verbose):
    sequence = Sequence(input_folder)
    new_sequence = sequence.realign(speed_threshold, window, verbose)
    save_json(sequence, new_sequence, output_folder)
    
if __name__ == '__main__':
    
    ## Define the directories here
    main_dir = "D:/OneDrive/Documents/BCBL/05_BodyLingual/Recordings/Main/Video"
    input_dir = "01_Original_videos"
    output_dir = "02_Realigned_videos"
    subject = "02_Ainhoa"

    ##Define variables here
    speed_threshold = 10 ##in cm per second
    window = 3 ##max number of frame before which something is considered as a twitch, and after which is considered as a jump
    verbose = False ##if you want to see everything that the program does, put True

    ##For one recording
    ##recording = "R077"
    ##main(main_dir+"/"+input_dir+"/"+subject+"/"+recording, main_dir+"/"+output_dir+"/"+subject+"/"+recording, speed_threshold, window, verbose)

    ##For a whole directory
    directories = os.listdir(main_dir+"/"+input_dir+"/"+subject)
    for d in directories:
        if d[0] == "R" and len(d) == 4:
            print("======= "+d+" =======")
            main(main_dir+"/"+input_dir+"/"+subject+"/"+d, main_dir+"/"+output_dir+"/"+subject+"/"+d, speed_threshold, window, verbose)

