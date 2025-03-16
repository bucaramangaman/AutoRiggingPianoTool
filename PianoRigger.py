import maya.cmds as cmds
import mido
from mido import MidiFile

#here we define the global variables
octave=['C_','D_b','D_','E_b','E_','F_','G_b','G_','A_b','A_','B_b','B_']   #twelve values

def drawUI(): #Function that draw the window
    #check to see if window exists
    if cmds.window("UI_PianoRiggerPlayer", exists = True):
        cmds.deleteUI("UI_PianoRiggerPlayer")
    #create window
    cmds.window("UI_PianoRiggerPlayer", title = "Piano rigger & player", w=10, h=200, mnb = False, mxb = False)
    cmds.rowColumnLayout('rowColumn')
    cmds.columnLayout('controlContainer')
    
    cmds.text(label='Make sure the piano is facing the Z axis')
    cmds.separator(w=500,bgc=(1,1,1))
    cmds.text(label='1. Select the piano Group then click the button')
    cmds.button(label = "Create Main Control", w = 200, command="RigPiano()")
    
    cmds.text(label='2. Select the keys Group then click the button')
    cmds.textFieldGrp("UI_1stNote", label='1st keynote of the piano:',text='A0')
    cmds.button(label = "Create keys Controls", w = 200, command="RigPianoKeys()")
    
    cmds.text(label='3. Select each pedal by holding SHIFT, then click the button')
    cmds.button(label = "Create Pedal Controls", w = 200, command="RigPianoPedals()")
    
    cmds.text(label='4. Choose the MIDI piano file to read')
    cmds.button(label = "Browse files", w = 200, command="BrowseMidiFile()")
    
    cmds.text(label='5. Choose desired piano tracks')
    cmds.rowColumnLayout('checkBoxes',p='controlContainer')
    
    cmds.columnLayout('controlContainer1',p='controlContainer')
    cmds.text(label='6. Animate piano')
    drawUI.startFrame=cmds.intSliderGrp(label='Animation starting frame: ',v=10, f=True, min=5, fmx=1000)
    cmds.button('animateBtn', l = "Animate", w = 200, c="ClickedAnimated(midiInstance)", en=False)

    cmds.showWindow("UI_PianoRiggerPlayer") #shows window

def RigPiano():
    sel=cmds.ls(sl=True)
    controlsInstance.CurrentPart('piano')
    controlsInstance.CreateControls()
    cmds.parentConstraint(controlsInstance.ctrlList[0], sel) 
      
def RigPianoPedals():
    controlsInstance.CurrentPart('pedal')
    sel=cmds.ls(sl=True)
    i=0
    for each in sel:
        controlsInstance.CreateControls()
        cmds.matchTransform(controlsInstance.pedalCtrlList[i], each)
        cmds.parentConstraint(controlsInstance.pedalCtrlList[i], each)
        cmds.select(controlsInstance.pedalCtrlList[i]+'.cv[0:'+str(controlsInstance.cvPnts)+']')
        cmds.scale(0.25,0.25,0.25)
        cmds.move(0,0,5, r=True, os=True, wd=True, puv=True)
        cmds.makeIdentity(a=True,t=1)
        i+=1
    ParentControls(controlsInstance.pedalCtrlList, controlsInstance.ctrlList[0], 'Piano_Pedals_Grp')
    
def RigPianoKeys():
    controlsInstance.CurrentPart('key')
    sel=cmds.ls(sl=True)
    keysAmnt=cmds.listRelatives(sel)
    CleanList(keysAmnt)
    SortKeys(keysAmnt)
    i=0
    currNote=cmds.textFieldGrp("UI_1stNote", query=True, text=True)
    curveList=[]
    for each in keysAmnt:
        controlsInstance.CreateControls()
        cmds.matchTransform(controlsInstance.keyCtrlList[i], each)
        cmds.parentConstraint(controlsInstance.keyCtrlList[i], each)
        cmds.select(controlsInstance.keyCtrlList[i]+'.cv[0:'+str(controlsInstance.cvPnts)+']')
        cmds.scale(0.25,0.25,0.25)
        cmds.move(0,0,8, r=True, os=True, wd=True, puv=True)
        cmds.select(controlsInstance.keyCtrlList[i])
        cmds.makeIdentity(a=True,t=1)
        cmds.rename('key_'+currNote)
        currNote=NextKeyNote(currNote)
        curveList.append(cmds.ls(sl=True)[0])
        i+=1
    controlsInstance.keyCtrlList=curveList
    ParentControls(controlsInstance.keyCtrlList, controlsInstance.ctrlList[0], 'Piano_Keys_Grp')
    
def CleanList(the_list):
    #remove hidden objects in list and Surfaceshape nodes
    i=0
    j=0     #ensures amount of loops not more that the lenght of list
    if 'SurfaceShape' in the_list[0]:  
        the_list.pop(0)
    while j<len(the_list):
        try:
            if cmds.getAttr(str(the_list[i])+'.visibility') == 0:
                    the_list.pop(i)
            else:
                i+=1
        except:
            the_list.pop(i)
        j+=1

def SortKeys(the_list): #PENDIENTE
    #In case keys are not in alphabetical order from L-R, this function sorts by pivot location on world
    the_list.sort(key=pivotPos)
    
def pivotPos(e):
    return cmds.getAttr(str(e)+'.rotatePivotX') 

def NextKeyNote(curr_note):
    #returns the note that corresponds to the next on the right of the current note
    curr_octave=int(curr_note[1:2])
    curr_note=curr_note[0:1]+'_'+curr_note[2:3]
    if curr_note[0:1] == 'B' and curr_note[2:3] == '':  #Check if Is last Octave
        curr_octave += 1
        new_note=octave[0]
    else:
        i=0
        each = octave[i]
        while each != curr_note:
            i += 1
            each = octave[i]
        new_note = octave[i+1]      
    return new_note.replace('_',str(curr_octave))  
    
def ParentControls(child,parent,name):
    group=cmds.group(child, n=name)
    cmds.parent(group,parent)
    
class pianoControls:
    def __init__(self):
        self.part=None
        self.mainCtrlCoords=[1,[[-20,0,-21],[20,0,-21],[20,0,22],[-20,0,22],[-20,0,-21]],[0,1,2,3,4]]
        self.keyCtrlCoords=[3,[[0,0,-4],[-0.5,0,-3],[-1,0,0],[-0.75,0,3],[0,0,4],[0.75,0,3],[1,0,0],[0.5,0,-3],[0,0,-4]],[0,0,0,1,2,3,4,5,6,6,6]]
        self.cvPnts=8
        
        self.ctrlList=[]
        self.keyCtrlList=[]
        self.pedalCtrlList=[]
    def CreateControls(self):
        if self.part=='piano':
            self.ctrlList.append(cmds.curve(n='Piano_MainCTrl', d=self.mainCtrlCoords[0],p=self.mainCtrlCoords[1],k=self.mainCtrlCoords[2]))
        if self.part=='key':
            self.keyCtrlList.append(cmds.curve(d=self.keyCtrlCoords[0],p=self.keyCtrlCoords[1],k=self.keyCtrlCoords[2]))
        if self.part=='pedal':
            self.pedalCtrlList.append(cmds.curve(n='Piano_PedalCTrl_1', d=self.keyCtrlCoords[0],p=self.keyCtrlCoords[1],k=self.keyCtrlCoords[2]))

    def CurrentPart(self, current):
        self.part=current

#Adjust key pivots
def KeyPivot():
    sel = cmds.ls(sl=True)  # Get selection.
    z=-3.295267 #amount should be modular for any size - fix
    for each in sel:
        cmds.xform(each, cpc=True)
        cmds.select(each)
        cmds.move(0,0,z, each+'.scalePivot', each+'.rotatePivot', r=True)

#MIDI FILES PROCESSING
#
def AnimateKeys(messageList, tpf, startFrame):
    fstPianoNote_name=str(controlsInstance.keyCtrlList[0]).replace('key_','')
    fstPianoNote_num=pianoNoteName2keyNoteNum(fstPianoNote_name)
    keyUpAngle = 0    #neutral angle for the keys
    keyDownAngle = 4.5  #max angle at which the key can be pushed
    #speed at which keys move
    keyUpVel=1.5 #Frames that take the key to hit bottom
    keyDownVel=2 #Frames that take the key to return to neutral position
    noteDuration=3.0/7.0    #notes keep sounding after release,
    
    #'note-on' carries a time value (tick), which tells how much is lasts
    #'note_off' message type in take not implemented, yet
    currentTick=startFrame*tpf
    for message in messageList:          
        if message.type == 'note_on' or message.type == 'note_off':
            #get midi note and convert to piano note number
            midiNoteNum=message.note
            pianoKeyNum=midiNoteNum2keyNoteNum(midiNoteNum)
            
            #search for the matching controller in keyCtrlList
            controller=str(controlsInstance.keyCtrlList[pianoKeyNum-fstPianoNote_num])
            
            #set keyframes:
            #print('tick: '+str(currentTick)) 
            currentTick += message.time
            currentFrame = currentTick / tpf
            #test: print('-->frame: '+str(currentFrame)+', note: '+str(controller)+' , vel: '+str(message.velocity)+' , time: '+str(message.time/tpf))
            currAngle=cmds.getAttr(controller+'.rotateX',t=currentFrame)
            #1.verrify if its pressed or released, then key position accordingly
            if message.velocity != 0:
                prevFrame=cmds.findKeyframe(controller, time=(currentFrame,currentFrame), which="previous") 
                prevAngle = cmds.getAttr(controller+'.rotateX',t=prevFrame)
                #a. key before is being pressed
                if not currAngle == keyUpAngle:     #if it is in the middle of movement (not 0)
                    nextFrame=cmds.findKeyframe(controller, time=(currentFrame,currentFrame), which="next" )
                    nextAngle = cmds.getAttr(controller+'.rotateX',t=nextFrame)
                    if nextAngle == keyUpAngle: #currently going down
                        #key the point at which it starts to reverse
                        reversePoint=(currentFrame-prevFrame)/3
                        cmds.setKeyframe(controller,at='rotateX',v=currAngle,t=prevFrame+reversePoint)
                        #test: print('1)o) t: '+str(prevFrame+reversePoint)+', v: '+str(currAngle))
                        #then delete next key                
                        cmds.selectKey(controller,at='rotateX',t=(nextFrame,nextFrame),k=True)
                        cmds.cutKey(an='keys',clear=True)
                    elif not prevAngle == keyDownAngle:     #currently going up
                        #delete prev key                
                        cmds.selectKey(controller,at='rotateX',t=(prevFrame,prevFrame),k=True)
                        cmds.cutKey(an='keys',clear=True)
                        #set new prev key
                        newPrevFrame=cmds.findKeyframe(controller, time=(currentFrame,currentFrame), which="previous")
                        if newPrevFrame < (currentFrame-keyDownVel):
                            cmds.setKeyframe(controller,at='rotateX',v=keyUpAngle,t=currentFrame-keyDownVel)
                            #test: print('3) t: '+str(currentFrame-keyDownVel)+', v: '+str(keyUpAngle))
                else:
                    #check if there is a keyframe between [currentFrame-keyUpVel,currentFrame]
                    currStartFrame=currentFrame-keyUpVel
                    if prevFrame > currStartFrame:
                        reversePoint=(prevFrame-currStartFrame)/2
                        reverseAngle=cmds.getAttr(controller+'.rotateX',t=prevFrame-reversePoint)
                        cmds.setKeyframe(controller,at='rotateX',v=reverseAngle,t=prevFrame-reversePoint)
                        #test: print('1)x) t: '+str(prevFrame-reversePoint)+', v: '+str(reverseAngle))
                        #then delete key                
                        cmds.selectKey(controller,at='rotateX',t=(prevFrame,prevFrame),k=True)
                        cmds.cutKey(an='keys',clear=True)
                    else:
                        cmds.setKeyframe(controller,at='rotateX',v=keyUpAngle,t=currentFrame-keyUpVel)
                        #test: print('1)z) t: '+str(currentFrame-keyUpVel)+', v: '+str(keyUpAngle))
                #b. New position
                cmds.setKeyframe(controller,at='rotateX',v=keyDownAngle,t=currentFrame)
                #test: print('2) t: '+str(currentFrame)+', v: '+str(keyDownAngle))
            else:
                #a. Key current position minus some distance (noteDuration) 
                frameAdjustment = (message.time / tpf) * noteDuration  
                newFrame = currentFrame-frameAdjustment
                newAngle = cmds.getAttr(controller+'.rotateX',t=newFrame) 
                #check if it is in the middle of movement
                #position after newFrame
                nextFrame=cmds.findKeyframe(controller, time=(newFrame,newFrame), which="next" )
                nextAngle = cmds.getAttr(controller+'.rotateX',t=nextFrame) 
                #position before newFrame
                prevFrame=cmds.findKeyframe(controller, time=(newFrame,newFrame), which="previous") 
                prevAngle = cmds.getAttr(controller+'.rotateX',t=prevFrame) 
                if (not newAngle == keyDownAngle) and (not nextAngle == keyUpAngle):
                    reversePoint=(nextFrame-newFrame)/3
                    reverseAngle=cmds.getAttr(controller+'.rotateX',t=newFrame+reversePoint) #nextFrame+reversePoint
                    #delete previous key                
                    cmds.selectKey(controller,at='rotateX',t=(prevFrame,prevFrame),k=True)
                    cmds.cutKey(an='keys',clear=True)  
                    #key newFrame
                    cmds.setKeyframe(controller,at='rotateX',v=keyDownAngle,t=newFrame)
                    #test: print('1)a) t: '+str(newFrame)+', v: '+str(keyDownAngle))
                    #key the point at which it starts to reverse
                    cmds.setKeyframe(controller,at='rotateX',v=reverseAngle,t=newFrame+reversePoint)  
                    #test: print('2)a) t: '+str(newFrame+reversePoint)+', v: '+str(reverseAngle))                      
                else:
                    #Key for return to neutral position  
                    cmds.setKeyframe(controller,at='rotateX',v=keyDownAngle,t=newFrame)
                    #test: print('1)b) t: '+str(newFrame)+', v: '+str(keyDownAngle))
                    if (nextFrame < (newFrame+keyDownVel)) and (not nextFrame == prevFrame):
                        reversePoint=((newFrame+keyDownVel)-nextFrame)/2
                        reverseAngle=cmds.getAttr(controller+'.rotateX',t=newFrame+reversePoint)
                        #delete next key                
                        cmds.selectKey(controller,at='rotateX',t=(nextFrame,nextFrame),k=True)
                        cmds.cutKey(an='keys',clear=True)
                        cmds.setKeyframe(controller,at='rotateX',v=reverseAngle,t=newFrame+reversePoint)
                        #test: print('2)b) t: '+str(newFrame+reversePoint)+', v: '+str(reverseAngle))
                    else:
                        cmds.setKeyframe(controller,at='rotateX',v=keyUpAngle,t=newFrame+keyDownVel)
                        #test: print('2)c) t: '+str(newFrame+keyDownVel)+', v: '+str(keyUpAngle))
                        if prevAngle == keyUpAngle:
                            #delete prev key                
                            cmds.selectKey(controller,at='rotateX',t=(prevFrame,prevFrame),k=True)
                            cmds.cutKey(an='keys',clear=True)
        elif message.type == 'control_change':       
            currentTick += message.time
            currentFrame = currentTick / tpf

#key the starting position of all piano keys and clear from previous animations
def SetUpKeys():
    for each in controlsInstance.keyCtrlList:
        cmds.cutKey(each,cl=True)
        cmds.setKeyframe(str(each),at='rotateX', v=0,t=1)
  
#Clicked animate button, animate checked tracks
def ClickedAnimated(midiInstance):
    startFrame=cmds.intSliderGrp(drawUI.startFrame,q=True,v=True)
    SetUpKeys()
    tpf=midiInstance.GetTicksPerFrame()
    checkBoxesList = cmds.rowColumnLayout('checkBoxes', query=True, childArray=True )
    i=1
    for checkBox in checkBoxesList:
        isChecked = cmds.checkBox(checkBox ,query=True, value=True)
        if isChecked:
            AnimateKeys(midiInstance.mid.tracks[i], tpf, startFrame)   
        i+=1
    cmds.button('animateBtn',edit=True,en=False)
    
#Collect midi and scene data
def ReadMIDIfile(midiFilePath):
    global midiInstance
    midiInstance = midiClass(midiFilePath)
    #print(midiInstance.mid)    #print(dir(mid.tracks[0]))
    
    #remove previous tracks if any
    checkBoxesList = cmds.rowColumnLayout('checkBoxes', query=True, childArray=True )
    if checkBoxesList != None:
        i=0
        for checkBox in checkBoxesList:
                cmds.deleteUI(checkBox,control=True)
    #get list of possible tracks to be played
    i=0
    for track in midiInstance.mid.tracks:
        name = track.name
        if i>0:
            if name == '':
                name='Untitled Track-'+str(i)
            cmds.rowColumnLayout('checkBoxes', edit=True, numberOfColumns=i)
            cmds.checkBox( label=name, p='checkBoxes')
        i+=1
    cmds.button('animateBtn',edit=True,en=True)
    
class midiClass:
    def __init__(self,midiFilePath):
        self.filePath= midiFilePath
        self.mid = MidiFile(self.filePath, clip=True)   #Readable file
        self.tpb = self.mid.ticks_per_beat      #Ticks per beat
        self.bpm = mido.tempo2bpm(self.Tempo())      #beats per minute
    
    #gets Beats per minute from file
    def Tempo(self):
        for meta in self.mid.tracks[0]:
            if meta.type == 'set_tempo':
                return meta.tempo
                
    def GetTicksPerFrame(self):
        ticksPerMin = self.tpb * self.bpm
        framesPerMin = GetFPS() * 60.0    # 1 min = 60 sec, .0 to force float
        return ticksPerMin/framesPerMin

def midiNoteNum2keyNoteNum(midiVal):
    midi2note=20    #piano first possible note corresponds to midi's 21th, so 21/1/A0(midi/piano/note) https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
    return midiVal-midi2note
        
def keyNoteNum2midiNoteNum(noteVal):
    note2midi=20    #piano first possible note corresponds to midi's 21th, so 21/1/A0(midi/piano/note) https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
    return noteVal+note2midi

def pianoNoteName2keyNoteNum(noteName):
    i=1
    currNote='A0'
    while currNote != noteName:
        i+=1
        currNote=NextKeyNote(currNote)
    return i   
    
#Browse files
def BrowseMidiFile():
    #here we are opening the midi file
    midiFilePath=cmds.fileDialog2(cap="importing the midi file",ff="*.mid",fm=4)
    ReadMIDIfile(midiFilePath[0]) 

#Get the fps from the scene
def GetFPS():
    timeUnit = cmds.currentUnit(query=True, time=True)
    #switch case scenario
    if timeUnit == 'film':
        return 24
    elif timeUnit == 'pal':
        return 25
    elif timeUnit == 'ntsc':
        return 30
    elif timeUnit == 'ntscf':
        return 60
    elif timeUnit == 'show':
        return 48
    elif timeUnit == 'game':
        return 15
    elif timeUnit == 'palf':
        return 50
    else:
        return 24   #in case not identified fps is in use, just default 24fps

#Running here:
#creates global instance for the controls
controlsInstance=pianoControls()

drawUI()
#BrowseMidiFile()