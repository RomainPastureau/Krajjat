import pygame, os
from pygame import *
from realigner import *

colorJoint = (255, 216, 109)
colorLine = (93, 183, 247)
lineWidth = 10

size = 10
sizeHand = 25
sizeHead = 50

pt = pygame.Surface((size, size))
ptHand = pygame.Surface((sizeHand, sizeHand))
ptHead = pygame.Surface((sizeHead, sizeHead))

pt.fill(colorJoint)
ptHand.fill(colorJoint)
ptHead.fill(colorJoint)

class Display(object):

    def __init__(self, window):
        self.window = window
        self.width = window.get_width()
        self.height = window.get_height()
        self.centerX = self.width//2
        self.centerY = self.height//2
        self.scale = 300

    def convertX(self, x, scale=1):
        return(int(self.centerX - x*self.scale*scale))

    def convertY(self, y, scale=1):
        return(int(self.centerY - y*self.scale*scale))

class Time(object):

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.timer = 0

    def getTime(self):
        return(self.timer)

    def reset(self):
        self.timer = 0

    def update(self):
        tick = self.clock.tick()
        self.timer += tick

class GraphicSequence(object):

    def __init__(self, sequence, showLines, ignoreBottom, startPose, display):
        self.sequence = sequence
        self.display = display
        self.loadSequence(showLines, ignoreBottom, display)
        self.time = Time()
        self.reset()
        self.currentPose = startPose

    def loadSequence(self, showLines, ignoreBottom, display):
        self.poses = []
        for pose in self.sequence.poses :
            self.poses.append(GraphicPose(pose, showLines, ignoreBottom, display))
            
    def nextPose(self):
        self.currentPose += 1
        if self.currentPose == len(self.sequence)-1 :
            self.reset()

    def reset(self):
        self.currentPose = 0
        self.time.reset()

    def getEvents(self, event):
        if event.type == KEYDOWN and event.key == K_RIGHT:
            self.currentPose = (self.currentPose + 1) % len(self.sequence)
            print("Current pose: "+str(self.currentPose+1)+"/"+str(len(self.sequence)))
        elif event.type == KEYDOWN and event.key == K_LEFT:
            self.currentPose = (self.currentPose + 1) % len(self.sequence)
            print("Current pose: "+str(self.currentPose+1)+"/"+str(len(self.sequence)))

    def show(self, window, showLines, showImage=False, shiftX=0, shiftY=0):
        if self.sequence.poses[self.currentPose+1].get_relative_time()*1000 < self.time.getTime() :
            self.nextPose()
        self.poses[self.currentPose].show(window, showLines, showImage, shiftX, shiftY)
        self.time.update()

    def showPose(self, window, showLines, showImage, shiftX=0, shiftY=0):
        self.poses[self.currentPose].show(window, showLines, showImage, shiftX, shiftY)

class GraphicPose(object):

    def __init__(self, pose, showLines, ignoreBottom, display):
        self.pose = pose
        self.loadJoints(ignoreBottom, display)
        if showLines:
            self.loadLines(ignoreBottom, display)

    def loadJoints(self, ignoreBottom, display):
        self.joints = {}
        for joint in self.pose.joints.keys() :
            if not (ignoreBottom and joint in ["KneeRight", "AnkleRight", "FootRight",
                                                  "KneeLeft", "AnkleLeft", "FootLeft"]) :
                self.joints[joint] = GraphicJoint(self.pose.joints[joint], display)

    def loadLines(self, ignoreBottom, display):
        self.lines = []
        self.lines.append(GraphicLine(self.joints["Head"], self.joints["Neck"], display))
        self.lines.append(GraphicLine(self.joints["Neck"], self.joints["SpineShoulder"], display))
        self.lines.append(GraphicLine(self.joints["SpineShoulder"], self.joints["SpineMid"], display))
        self.lines.append(GraphicLine(self.joints["SpineMid"], self.joints["SpineBase"], display))
        
        self.lines.append(GraphicLine(self.joints["SpineShoulder"], self.joints["ShoulderRight"], display))
        self.lines.append(GraphicLine(self.joints["ShoulderRight"], self.joints["ElbowRight"], display))
        self.lines.append(GraphicLine(self.joints["ElbowRight"], self.joints["WristRight"], display))
        self.lines.append(GraphicLine(self.joints["WristRight"], self.joints["HandRight"], display))

        self.lines.append(GraphicLine(self.joints["SpineShoulder"], self.joints["ShoulderLeft"], display))
        self.lines.append(GraphicLine(self.joints["ShoulderLeft"], self.joints["ElbowLeft"], display))
        self.lines.append(GraphicLine(self.joints["ElbowLeft"], self.joints["WristLeft"], display))
        self.lines.append(GraphicLine(self.joints["WristLeft"], self.joints["HandLeft"], display))

        self.lines.append(GraphicLine(self.joints["SpineBase"], self.joints["HipRight"], display))
        self.lines.append(GraphicLine(self.joints["SpineBase"], self.joints["HipLeft"], display))

        if ignoreBottom == False:
            self.lines.append(GraphicLine(self.joints["HipRight"], self.joints["KneeRight"], display))
            self.lines.append(GraphicLine(self.joints["KneeRight"], self.joints["AnkleRight"], display))
            self.lines.append(GraphicLine(self.joints["AnkleRight"], self.joints["FootRight"], display))

            self.lines.append(GraphicLine(self.joints["HipLeft"], self.joints["KneeLeft"], display))
            self.lines.append(GraphicLine(self.joints["KneeLeft"], self.joints["AnkleLeft"], display))
            self.lines.append(GraphicLine(self.joints["AnkleLeft"], self.joints["FootLeft"], display))

    def show(self, window, showLines, showImage, shiftX=0, shiftY=0):
        if showLines:
            for l in self.lines :
                l.show(window, shiftX=shiftX, shiftY=shiftY)
        for j in self.joints.keys() :
            self.joints[j].show(window, shiftX, shiftY)

class GraphicJoint(object):

    def __init__(self, joint, display):
        self.joint = joint
        self.convert(display)

    def convert(self, display):            
        self.x = display.convertX(self.joint.x)
        self.y = display.convertY(self.joint.y)

    def show(self, window, shiftX=0, shiftY=0):
        if self.joint.joint_type == "Head" and self.joint.randomized == False :
            p = ptHead
        elif self.joint.joint_type == "HipLeft" and self.joint.randomized == True :
            p = ptHead
        elif self.joint.joint_type in ["HandRight", "HandLeft"] and self.joint.randomized == False :
            p = ptHand
        elif self.joint.joint_type in ["ShoulderLeft", "SpineMid"] and self.joint.randomized == True :
            p = ptHand
        else :
            p = pt
        
        if self.joint.corrected == True :
            p.fill((0, 255, 0))
        elif self.joint.move_much == True :
            p.fill((255, 0, 0))
        else :
            p.fill(colorJoint)

        window.blit(p, (shiftX+self.x-p.get_width()//2, shiftY+self.y-p.get_height()//2))

class GraphicLine(object):

    def __init__(self, joint1, joint2, display):
        self.startX = joint1.x
        self.startY = joint1.y
        self.endX = joint2.x
        self.endY = joint2.y

    def show(self, window, shiftX=0, shiftY=0):
        pygame.draw.line(window, colorLine, (self.startX+shiftX, self.startY+shiftY), (self.endX+shiftX, self.endY+shiftY), lineWidth)

def main(folder, speed_threshold, w, showLines=True, ignoreBottom=False, resolution=(1600, 900), fullScreen=False):

    sequence = Sequence(folder)
    new_sequence = sequence.realign(speed_threshold, w, verbose=False)

    ##Pygame configuration
    if resolution == None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)
        
    if fullScreen == True:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else :
        window = pygame.display.set_mode(resolution)

    pygame.mouse.set_visible(True)
    
    display = Display(window)

    animation1 = GraphicSequence(sequence, showLines, ignoreBottom, 0, display)
    animation2 = GraphicSequence(new_sequence, showLines, ignoreBottom, 0, display)

    program = True

    ##Program loop  
    while program == True :

        window.fill((0,0,0))

        for event in pygame.event.get():

            ##Leave the program
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) :
                program = False
                break

        animation1.show(window, showLines, -300)
        animation2.show(window, showLines, 300)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def sequenceComparer(sequence1, sequence2, showLines=True, ignoreBottom=False, resolution=(1600, 900), fullScreen=False):
    
    ##Pygame configuration
    if resolution == None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)
        
    if fullScreen == True:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else :
        window = pygame.display.set_mode(resolution)

    pygame.mouse.set_visible(True)
    
    display = Display(window)

    animation1 = GraphicSequence(sequence1, showLines, ignoreBottom, 0, display)
    animation2 = GraphicSequence(sequence2, showLines, ignoreBottom, 0, display)

    program = True

    ##Program loop  
    while program == True :

        window.fill((0,0,0))

        for event in pygame.event.get():

            ##Leave the program
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) :
                program = False
                break

        animation1.show(window, showLines, shiftX=-150)
        animation2.show(window, showLines, shiftX=150)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def sequenceReader(folder, showLines=True, ignoreBottom=False, resolution=(1600, 900), fullScreen=False):

    if folder is str:
        sequence = Sequence(folder)
    else :
        sequence = folder

    ##Pygame configuration
    if resolution == None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)
        
    if fullScreen == True:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else :
        window = pygame.display.set_mode(resolution)

    pygame.mouse.set_visible(True)
    
    display = Display(window)

    animation = GraphicSequence(sequence, showLines, ignoreBottom, 0, display)

    program = True

    ##Program loop  
    while program == True :

        window.fill((0,0,0))

        for event in pygame.event.get():

            ##Leave the program
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) :
                program = False
                break

        animation.show(window, showLines, 0)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def poseReader(folder, startPose=0, showLines=True, showImage=True, ignoreBottom=False, resolution=(1600,900), fullScreen=False):

    sequence = Sequence(folder)

    ##Pygame configuration
    if resolution == None:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)
        
    if fullScreen == True:
        window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else :
        window = pygame.display.set_mode(resolution)

    pygame.mouse.set_visible(True)
    
    display = Display(window)

    animation = GraphicSequence(sequence, showLines, ignoreBottom, startPose, display)

    program = True

    ##Program loop  
    while program == True :

        window.fill((0,0,0))

        for event in pygame.event.get():

            ##Leave the program
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) :
                program = False
                break

            animation.getEvents(event)

        animation.showPose(window, showLines, showImage)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
    
if __name__ == '__main__':
    #main("D:/OneDrive/Documents/BCBL/05 - BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - Original/", speed_threshold=10, w=3)
    #sequenceReader("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - 20, 3/", True, True)
    #poseReader("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - 20, 3/", 718, True, True)

##    file = open("sequences.txt", "r")
##    fileread = file.read().split("\n")
##    file.close()
##    done = []
##    for line in fileread:
##        if line != "":
##            done.append([line.split("\t")[0], line.split("\t")[1]])
##
##    path = "F:/Body Tracking Recordings/Video/"
##    sub = os.listdir(path+"01_Original_videos/")
##    diff_joints = []
##    tot_joints = []
##    percentage = []
##    for s in sub :
##        vid_og = os.listdir(path+"01_Original_videos/"+s)
##        vid_re = os.listdir(path+"02_Realigned_videos/"+s)
##
##        for v in vid_og :
##            if v in vid_re :
##                print("Video: "+v+" - ", end="")
##                if [s, v] not in done :
##                    sq_og = Sequence(path+"01_Original_videos/"+s+"/"+v)
##                    sq_re = Sequence(path+"02_Realigned_videos/"+s+"/"+v)
##                    d, t = compareSequences(sq_og, sq_re)
##                    del sq_og
##                    del sq_re
##                    diff_joints.append(d)
##                    tot_joints.append(t)
##                    percentage.append(d/t)
##                    file = open("sequences.txt", "a")
##                    file.write(s+"\t"+v+"\t"+str(d)+"\t"+str(t)+"\t"+str(d/t)+"\n")
##                    file.close()
##                else :
##                    print("Sequences already processed.")
##
##    print(sum(percentage)/len(percentage))
##    print(sum(diff_joints)/sum(tot_joints))


##    file = open("sequences.txt", "r")
##    fileread = file.read().split("\n")
##    file.close()
##    corrected = []
##    joints = []
##    avg = []
##    for line in fileread:
##        if line != "":
##            l = line.split("\t")
##            corrected.append(int(l[2]))
##            joints.append(int(l[3]))
##            avg.append(float(l[4]))
##
##    print(str(sum(corrected)))
##    print(str(sum(joints)))
##    print(str(sum(corrected)/sum(joints)))
##    print(str(sum(avg)/len(avg)))
                       
##
    sequence1 = Sequence("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - 10, 3")
##    sequenceReader("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - 10, 3")
    sequence2 = Sequence("D:/OneDrive/Documents/BCBL/05_BodyLingual/Stimuli/Recordings/Main/Video/Example (02_Ainhoa)/R077 - 10, 3")
    sequence2.randomize()
    sequenceReader(sequence1, True, True)
    #sequenceComparer(sequence1, sequence2, False, True)
##    print(compareSequences(sequence1, sequence2))
