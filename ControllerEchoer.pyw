import pygame
import os
from subprocess import Popen

# TODO: Down and button press same frame
###################################
# INIT
#

pygame.init()

# Screen setup
screen = pygame.display.set_mode((400, 100))
pygame.display.set_caption("Controller Echoer")
screen.fill((222, 225, 229))


# Buttons
ButtonX = 25
ButtonY = 25
ButtonWidth = 150
ButtonHeight = 50

# Button status

global REC
global PLAY

REC = False
PLAY = False

# Controllers

Filename = 'ControllerPlayback.ahk'

KeyTable = [ "c", "x", "z", "s", "q" ,"w" , 0 , "d",# Buttons: X, A, B, Y, Hard L, Hard R, UNUSED, Z
0, "ENTER", "E", "R", "t", "h", "g", "f",           # UNUSED, Start, Soft L, Soft R, D-pad UP, D-pad Right, D-pad Down, D-pad Left
"LEFT", "RIGHT", "UP", "DOWN",                      # Control Stick
"i", "k", "j", "l",                                 # C-stick - Up, Down, Left, Right
"LSHIFT"                                            # Control stick modifier button
    ]

joysticks = []

global currentJoy       # Current controller being used so we are not getting buttons from two controllers
currentJoy = -1

global Delay            # Delay BETWEEN button presses. This is for math so we can subtract the game clock from the last time
Delay = 0

####################################
#
# Functions

def Drawbutton(msg, x, y, w, h, wb):    # Draw GUI Buttons

    global REC
    global PLAY

    font = pygame.font.Font('freesansbold.ttf', int(h/2))

    # Correct gfx depending on which button is pressed
    if (REC == True and wb == 1) or (PLAY == True and wb == 2):
        pygame.draw.rect(screen, (139, 141, 142),(x,y,w,h))
        screen.blit( font.render("Stop", 0, (255, 0, 0)) , ((x+(w/4.5)), (y+(h/4))) )
    elif (REC == True and wb == 2) or (PLAY == True and wb == 1):
        pygame.draw.rect(screen, (175, 179, 181),(x,y,w,h))
        screen.blit( font.render("Waiting...", 0, (0, 0, 0)) , ((x+(w/15)), (y+(h/4))) )
    else:
        pygame.draw.rect(screen, (175, 179, 181),(x,y,w,h))
        screen.blit( font.render(msg, 0, (0, 0, 255)) , ((x+(w/4.5)), (y+(h/4))) )
        return


global CurrentFilePos
CurrentFilePos = 0

def GiveToAhk(KeyPress, etype, currentTick, out):

    global Delay
    global CurrentFilePos

    Offset = 20
    
    if Delay != 0:

        LastDelay = (currentTick-Delay)
        
        if LastDelay > 0:
            if (LastDelay-Offset) > 0:
                out.write( str("sleep (" + str(LastDelay-Offset)) + ", \"P\")\n")
        else:
            out.seek(CurrentFilePos)

    CurrentFilePos = out.tell()
    
    if etype == 10:
        out.write( str("Send {" + KeyPress +" down}\n") )
    elif etype == 11:
        out.write( str("Send {" + KeyPress +" up}\n") )
    else:
        print("wrong event handler")
    
    Delay = currentTick
    

# Axis 0    - Control Stick X
# Axis 1    - Control Stick Y
# Axis 2    - C-stcik Y
# Axis 3    - C-stick X
# Axis 4    - R
# Axis 5    - L

global CStickSpeed
CStickSpeed = [0, 0, 0, 0, 0]

global StickPos
StickPos = ["", "", "", "", "", "", ""]


def ButtonOut(controller, out, KeyPress, etype, currentTick):    # Record *button* inputs
    
    global currentJoy
    
    if currentJoy < 0:
        currentJoy = controller
    elif currentJoy != controller:
        print("nope: ", controller)
        return

    if KeyPress == KeyTable[4]:
        if StickPos[5] == "":
            StickPos[5] = KeyTable[4]
        elif StickPos[5] != "" and joysticks[controller].get_axis(5) <= -0.980:
            print("Hard press.")
        else:
            return
    elif KeyPress == KeyTable[5]:
        if StickPos[4] == "":
            StickPos[4] = KeyTable[5]
        elif StickPos[4] != "" and joysticks[controller].get_axis(4) <= -0.980:
            print("Hard press.")
        else:
            return
    
    GiveToAhk(KeyPress, etype, currentTick, out)


def JoystickOut(controller, out, AxisId, Axis, currentTick):     # Record *Axis* inputs

    global currentJoy
    global StickPos
    global CStickSpeed
    
    absAxis = abs(Axis)
        
    if currentJoy == controller and absAxis < 1 and AxisId < 6:
        
        if AxisId == 4 or AxisId == 5:
            if Axis <= -0.400 and StickPos[AxisId] != "":
                
                GiveToAhk(StickPos[AxisId], 11, currentTick, out) 
                StickPos[AxisId] = ""
                
        elif absAxis <= 0.150 and StickPos[AxisId] != "":
            
            GiveToAhk(StickPos[AxisId], 11, currentTick, out) 
            StickPos[AxisId] = ""

            #if StickPos[6] == KeyTable[24]:
            #    out.write( str("Send {" + KeyTable[24] +" up}\n") )
            #    StickPos[6] = ""

            #CStickSpeed[AxisId] = 0
    else:
        
        if absAxis <= 0.150 or absAxis >= 1 or AxisId >= 6:
            return

        if AxisId == 4 or AxisId == 5:
            # Ignore garabe trigger values
            if Axis <= -0.400 or Axis > 0.695:
                return
        
        if currentJoy < 0:            
            currentJoy = controller            
        elif currentJoy != controller:
            print("stick nope: ", controller)
            return

    if AxisId == 4 or AxisId == 5:        
        # If we are lightly pressing L or R...
        if Axis >= -0.400 and Axis < 0.695:
            if StickPos[AxisId] == "":
                StickPos[AxisId] = KeyTable[AxisId]#+6]
                # Send a button press
                GiveToAhk(StickPos[AxisId], 10, currentTick, out) 
        return     

    #Soft = 0

    
    #if (absAxis >= 0.200 and absAxis < 0.590) and AxisId == 0:     # Soft stick for control stick only and only Horz and down because thats the only way it works really :V kind of cheap i know
       
    #   if CStickSpeed[AxisId] == 0 or abs(absAxis-CStickSpeed[AxisId]) >= 0.050:
    #        CStickSpeed[AxisId] = absAxis
        
    #   elif StickPos[6] == "" and StickPos[AxisId] == "":
    #       out.write( str("Send {" + KeyTable[24] +" down}\n") )
    #       StickPos[6] = KeyTable[24]
    #       Soft = 1
            
    #elif AxisId == 1 and Axis > 0 and (absAxis >= 0.380 and absAxis < 0.590):
        
    #    if CStickSpeed[AxisId] == 0 or abs(absAxis-CStickSpeed[AxisId]) >= 0.063:
    #        CStickSpeed[AxisId] = absAxis
    #    elif StickPos[6] == "" and StickPos[AxisId] == "":
    #        out.write( str("Send {" + KeyTable[24] +" down}\n") )
    #        StickPos[6] = KeyTable[24]
    #        Soft = 1
        
    if absAxis >= 0.450: #or Soft == 1:                      # Hard stick

        Dir = 17
        if Axis < 0:    # Check if we are going the opposite directions
            Dir = 16
        
        if StickPos[AxisId] == "":
            
            StickPos[AxisId] = KeyTable[ (AxisId*2) +  Dir ]
            GiveToAhk(StickPos[AxisId], 10, currentTick, out)        
    return
    
#
#
#
#####################################

def KillAHK():
    Filelocation = os.path.dirname(os.path.realpath(__file__)) + "\\sleep.inc.ahk"
    Popen("taskkill /PID AutoHotKey.exe")
    Popen("start " + Filelocation , shell=True)
    Popen("taskkill /PID AutoHotKey.exe")
    
#####################################
#
# Main

def main():

    global REC
    global PLAY
    global currentJoy
    global Delay
                    
    pygame.draw.rect(screen, (0, 0, 0), (ButtonX+2, ButtonY+2, ButtonWidth+1, ButtonHeight+1) ) # Draw button shadows
    pygame.draw.rect(screen, (0, 0, 0), ((ButtonX+ButtonWidth+50)+2, ButtonY+2, ButtonWidth+1, ButtonHeight+1) )

    clock = pygame.time.Clock()

    Filelocation = os.path.dirname(os.path.realpath(__file__)) + "\\" + Filename
    
    running = True
    # Main loop
    
    while running:
        
        #clock.tick(60)

        now = pygame.time.get_ticks()
    
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
              running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                
                mouse = pygame.mouse.get_pos() # See where the mouse is
                              
                if ButtonX+ButtonWidth > mouse[0] > ButtonX and ButtonY+ButtonHeight > mouse[1] > ButtonY and PLAY == False: # Make it so you can't press the other button if one is activated  

                    # If we are here it means we just pushed the REC button
                    
                    if REC == False: # If this is a new recording (aka False = it is not on) clear previous inputs...
  
                        currentJoy = -1 # We don't know which controller to use yet
                        Delay = 0         # There is no delay between buttons yet
                        
                        ahk = open(Filename, 'w')  # Open
                        ahk.truncate()                               # and clear file
                        
                        ahk.write("#Include sleep.inc.ahk\n\n") # Include high percision sleep
                        ahk.write("Loop\n{\n")              # Loop playback

                        print(ahk)
                        
                        # Look for all the connected joysticks
                        for i in range(0, pygame.joystick.get_count()):
                            
                            joysticks.append(pygame.joystick.Joystick(i))   # create an Joystick object in our list
                            joysticks[-1].init()                            # initialize them all (-1 means loop forever)
                            
                            print ("Detected joystick '",joysticks[-1].get_name(),"'") # print a statement telling what the name of the controller is
                        
                    else:       # ... otherwise if we are ending the recording...

                        print((pygame.time.get_ticks()-Delay))
                        ahk.write( str("Sleep " + str( (pygame.time.get_ticks()-Delay)) + "\n"))   # Set loop delay
                        ahk.write("}")
                        ahk.close()  # Close the file

                    # Flip button after we press it
                    REC = not REC
                    
                elif ((ButtonX+ButtonWidth+50)+ButtonWidth) > mouse[0] > (ButtonX+ButtonWidth+50) and ButtonY+ButtonHeight > mouse[1] > ButtonY and REC == False:

                    # We are here if we pressed the PLAY button
                    
                    if os.path.isfile(Filelocation):    # Check if a playback file exists

                        # If it does then we can do stuff with it
                        if PLAY == False:
                            # Play it if we want to
                            Popen("start " + Filelocation , shell=True)
                        else:
                            # Or kill it
                            KillAHK()
                        
                        # Flip button after we press it
                        PLAY = not PLAY
            
            # Monitor button presses if we are recording            
            if REC == True and event.type == pygame.JOYBUTTONDOWN:
               
                # If we are recording and there is a button press go here
                ButtonOut(event.joy, ahk, KeyTable[event.button], event.type, now)
                
            if REC == True and event.type == pygame.JOYBUTTONUP:

                # If we are recording and there is a button release go here
                ButtonOut(event.joy, ahk, KeyTable[event.button], event.type, now)
                
            if REC == True and event.type == pygame.JOYAXISMOTION:
                # If we are recording and there is a joystick input go here
                JoystickOut(event.joy, ahk, event.axis, event.value, now)
            
        # Draw and keep buttons updated
        Drawbutton("REC*", ButtonX, ButtonY, ButtonWidth, ButtonHeight, 1)        
        Drawbutton("PLAY", (ButtonX+ButtonWidth+50), ButtonY, ButtonWidth, ButtonHeight, 2)
        
        # Update screen
        pygame.display.update()

##
##########################################


main()
KillAHK() # Kill autokey just incase
pygame.quit()
