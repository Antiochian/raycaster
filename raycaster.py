# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 17:54:16 2019

v3.0
STILL VERY MUCH IN-PROGRESS!!
@author: Antiochian
-------
SIGN CONVENTION:
    
+---------> +x direction
|
|
|
v
+y direction

theta is measured backwards kinda, so that a theta of +90deg points in the NEGATIVE y-direction
"""
import pygame
import sys
from math import *
import numpy as np

def gridmaker():
    """
    Called at the start of program, defines the "walldict" dictionary of coordinates
    """
    grid_dict = {}
    
    spacr=grid = np.array([["A","A","A", "A","A","A", "A","A","A"]]) #"spacr" variable is just to keep matrix lined up.
    grid = np.append(grid,[["X", 0 , 0 ,  0 , 0 , 0 ,  0 , 0, "B"]],axis = 0)
    grid = np.append(grid,[["X", 0 , 0 ,  0 , 0 , 0 ,  0 , 0 ,"B"]],axis = 0)
    ########################--------------------------------------##########
    grid = np.append(grid,[["X", 0 , 0 ,  0 , 0 ,"D",  0 , 0, "B"]],axis = 0)
    grid = np.append(grid,[["X", 0 , 0 ,  0 , 0 ,"D",  0 , 0, "B"]],axis = 0)
    grid = np.append(grid,[["X", 0 , 0 ,  0 , 0 ,"D",  0 , 0, "B"]],axis = 0)
    ########################--------------------------------------##########
    grid = np.append(grid,[["X", 0 , 0 ,  0 , 0 , 0 ,  0 , 0, "B"]],axis = 0)
    grid = np.append(grid,[["X", 0 , 0 ,  0 , 0 , 0 ,  0 , 0, "B"]],axis = 0)
    grid = np.append(grid,[["Z","Z","Z", "Z","Z","Z", "Z","Z","Z"]],axis = 0)
    #grid = np.flipud(grid)
    
    for x in range( grid.shape[1]):
        for y in range(grid.shape[0]):
            if grid[y,x] == "A":
                grid_dict[(x,y)] = white
            elif grid[y,x] == "B":
                grid_dict[(x,y)] = black
            elif grid[y,x] == "X":
                grid_dict[(x,y)] = red
            elif grid[y,x] == "Z":
                grid_dict[(x,y)] = blue
            elif grid[y,x] == "D":
                grid_dict[(x,y)] = debugcolor
    return grid_dict,grid

def checkwall(x,y,GRID=False):
    """
    Inputs the xy coordinates (default) OR the GRID coordinates and returns True/False
    if there is/is not a wall present.
    """
    if not GRID: #if GRID = false, convert to GRID coordinates
        x = x // gridsize
        y = y // gridsize
    if abs(x) > len(grid) or abs(y) > len(grid): #out of bounds catch
        return True
    if (x,y) in walldict.keys():
        return True
    else:
        return False

def lookup(angle): #returns true if looking up
    # NOTE: "up" means in positive y-direction, i.e. down on visual grid
    angle = angle % 360
    if 0 < angle < 180:
        return True
    else:
        return False

def lookright(angle):
    angle = angle % 360
    if (0 <= angle < 90) or ( 270 < angle <= 360):
        return True
    else:
        return False
    
def getintercepts( playerpos , angle ): 
    (Px,Py) = playerpos
    angle = angle % 360
    """ input angle and position, returns Ax, Ay, Bx, By
"""
    if lookup(angle) and lookright(angle):
        """FIRST QUADRANT 0 <= angle < 90
        """
        if angle == 0:
            angle += 1e-8 #this fuzz prevents divide-by-zero errors  
        Ay = (Py // gridsize + 1 ) * gridsize #next horizontal line
        Ax = Px + (Ay - Py)/tan(radians(angle))
        
        dAy = gridsize
        dAx = dAy / tan(radians( angle))
        
        Bx = (Px // gridsize + 1 ) * gridsize
        By = Py + (Bx - Px)*tan(radians(angle)) 
        
        dBx = gridsize
        dBy = dBx * tan(radians(angle))       
    elif lookup(angle) and (not lookright(angle)):
        """OPTION B:
    ray is in 2nd quadrant: angle: 90 < angle < 180
     X   |   """
        if angle == 180:
            angle -= 1e-8
        Ay = (Py // gridsize + 1 ) * gridsize #Ay > Py
        Ax = Px - (Ay - Py)/tan(radians(180 - angle)) #Ax < Px
        
        dAy = gridsize #positive
        dAx = - dAy / tan(radians(180 - angle)) #negative     
        
        #VERTICAL INTERSECTS
        Bx = (Px // gridsize)*gridsize - 1 #prev vert line
        By = Py +  abs((Bx - Px)*tan(radians(180 - angle))) #By > Py
        
        dBx = -gridsize #negative
        dBy = dBx * - tan(radians(180 - angle)) #positive ; minus sign is to keep Y increasing   
    elif (not lookup(angle) ) and (not lookright(angle)):
        """        
    OPTION C:
    ray is in 3rd quadrant, angle: 180 < 270
         """
        if angle == 180:
            angle += 1e8
        Ay = (Py // gridsize ) * gridsize - 1 #prev horizontal line
        Ax = Px + (Ay - Py)/tan(radians(angle - 180)) #note (Ay - Py) is negative
        
        dAy = -gridsize #negative
        dAx = dAy /tan(radians(angle - 180)) #negative     
        
        #VERTICAL INTERSECTS
        Bx = (Px // gridsize)*gridsize - 1 #prev vert line
        By = Py + (Bx - Px)*tan(radians(angle - 180)) #minus sign is from tangent
        
        dBx = -gridsize #negative
        dBy = dBx*tan(radians(angle - 180)) #negative
   
    elif (not lookup(angle) ) and lookright(angle):                
        """        
    OPTION D:
    ray is in 4th quadrant
         """     
        if angle == 360:
            angle -= 1e-8 #this fuzz prevents divide-by-zero errors  
        Ay = (Py // gridsize) * gridsize - 1 #prev horizontal line
        Ax = Px + abs((Ay - Py)/tan(radians(360 - angle))) #this minus sign is from the tangent 
        
        dAy = -gridsize
        dAx = dAy / -tan(radians(360 - angle)) #positive
        
        Bx = (Px // gridsize + 1 ) * gridsize #increasing
        By = Py - (Bx - Px)*tan(radians(360 - angle)) #decreasing
        
        dBx = gridsize
        dBy = dBx * -tan(radians(360 - angle))
    return Ax, Ay , dAx, dAy, Bx, By , dBx, dBy

def drawwall(Wx,Wy,dist,projx):
    #takes raw coordinates as inputs
    Wx = Wx // gridsize
    Wy = Wy // gridsize
    
    if abs(Wx) > len(grid) or abs(Wy) > len(grid):
        color = backgroundcolor #Out of bounds case
    else:
        color = walldict[(Wx,Wy)]
    
    height = gridsize*projdistance / dist
    offset =( Ny - height )/2
    colRect = pygame.Rect(projx,offset, 1,height) #1pixel thick rectangle spanning whole screen
    pygame.draw.rect(PROJ, color, colRect)
    return
    
    
def test(playerpos, angle):
    print("Test initiated. (Px,Py) = ",playerpos," ; angle = ",angle)
    angle = angle % 360
    (Px,Py) = playerpos
    Ax, Ay , dAx, dAy, Bx, By , dBx, dBy = getintercepts( (Px,Py) , angle)         
    nocollision = True
    L = 0
    while nocollision:
        L += 1
        distA = sqrt((Px-Ax)**2 + (Py-Ay)**2)
        distB = sqrt((Px-Bx)**2 + (Py-By)**2)
        if distA <= distB: #if A comes first
            print(Ax//gridsize,Ay//gridsize)
            if checkwall(Ax,Ay):
                print("FINAL COLLISION.")
                nocollision = False
            Ax += dAx
            Ay += dAy
        else:
            print(Bx//gridsize,By//gridsize)
            if checkwall(Bx,By):
                print("FINAL COLLISION.")
                nocollision = False
            Bx += dBx
            By += dBy  
    return

def main():
    (Px,Py) = (193,193)
    viewangle = -15
    clock = pygame.time.Clock()
    while True: #MAIN GAME LOOP#
        clock.tick(FPS)
        window.blit(PROJ,(0,0))
        PROJ.fill(backgroundcolor)
        pygame.display.update()
        projx = 0 #possible error here if screen index starts at 1 or 0
        
        for event in pygame.event.get(): #detect events
            if event.type == pygame.QUIT: #detect attempted exit
                pygame.quit()
                sys.exit()
        if pygame.key.get_pressed()[101]:
            viewangle += turnspeed
            print("-----",viewangle,"degrees --------")
            test((Px,Py),viewangle)
        if pygame.key.get_pressed()[113]:
            viewangle -= turnspeed
            print("-----",viewangle,"degrees --------")
            test((Px,Py),viewangle)
        if pygame.key.get_pressed()[119]: # Go FORWARD
            print("forward")
            Px += speed*cos(radians(viewangle))
            Py += speed*sin(radians(viewangle))
        if pygame.key.get_pressed()[115]: #Go BACKWARD
            Px -= speed*cos(radians(viewangle))
            Py -= speed*sin(radians(viewangle))
        if pygame.key.get_pressed()[100]: #Strafe RIGHT
            Px += 0.6*speed*sin(radians(viewangle))
            Py += 0.6*speed*cos(radians(viewangle))
        if pygame.key.get_pressed()[97]: #Strafe LEFT
            Px -= 0.6*speed*sin(radians(viewangle))
            Py -= 0.6*speed*cos(radians(viewangle))
        angle = viewangle - FOV/2
        for projx in range(projwidth):
            Ax, Ay , dAx, dAy, Bx, By , dBx, dBy = getintercepts( (Px,Py) , angle)  
            nocollision = True
            L = 0
            while nocollision:
                L += 1
#                if L > len(grid):
#                    print("--- #",L,"------")
#                    print("Angle: ",angle)
#                    print(Ax,Ay)
#                    print(Bx,By)
#                if round(angle,1) == viewangle:
#                    print("-----",angle,"-----")
#                    print(Ax,Ay)
#                    print(Bx,By)    
                distA = sqrt((Px-Ax)**2 + (Py-Ay)**2)
                distB = sqrt((Px-Bx)**2 + (Py-By)**2)
                if distA <= distB: #if A comes first
                    if checkwall(Ax,Ay):
                        drawwall(Ax,Ay,distA,projx)
                        nocollision = False
                    Ax += dAx
                    Ay += dAy
                else:
                    if checkwall(Bx,By):
                        drawwall(Bx,By,distB,projx)
                        nocollision = False
                    Bx += dBx
                    By += dBy                    
                            
            angle += columnangle
    
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
blue = (0,0,255)
green = (0,0,255)
debug = (255, 107, 223)
grey = (20,20,20)
clock = pygame.time.Clock()
topcolor = white
rightcolor = black
leftcolor = red
bottomcolor = blue
barriercolor = debug
wallcolor = white
backgroundcolor = grey
debugcolor = debug

speed = 25
turnspeed = 8
FPS = 12
gridsize = 64
FOV = 60 #degrees
Nx,Ny = 600,480
walldict, grid = gridmaker()  

#derived parameters
projwidth,projheight = Nx,Ny
projdistance = (1/tan(radians(FOV/2))) * (projwidth/2) 
columnangle = FOV/projwidth #in degrees! # angle between rays/columns 

# set up surfaces
window = pygame.display.set_mode( (Nx,Ny) )
pygame.display.set_caption("Raycaster v3")
PROJ = pygame.Surface( (Nx,Ny))

main()

    
    
    
