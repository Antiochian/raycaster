# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 17:54:16 2019
DOOM-like RAYTRACER
@author: Antiochian
-------
CONTROLS:
Esc to quit
WSAD for movement
use the mouse to look around (or use Q and E to rotate view)
Press leftclick or space to "shoot" and destroy walls

You can edit the map file in MSpaint, and white pixels will be treated as empty space
-------
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
import os
from math import *
import numpy as np
from matplotlib.image import imread

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
blue = (0,0,255)
green = (0,0,255)
debug = (255, 107, 223)
grey = (20,20,20)
lightgrey = (191, 217, 198)

floorcolor = grey
roofcolor = lightgrey
debugcolor = debug
backgroundcolor = black

def importgrid():
    grid_dict = {}
    grid = imread('map.jpg')
    grid = np.rint(grid)
    
    #detect alpha channel
    if grid.shape[2] == 4:
        for x in range( grid.shape[1]):
            for y in range(grid.shape[0]):
                if all( grid[y,x] == [255,255,255,255]):
                    pass
                else:
                    grid_dict[(x,y)] = grid[y,x]
    elif grid.shape[2] == 3:
        for y in range(grid.shape[0]):
                if all( grid[y,x] == [255,255,255]):
                    pass
                else:
                    grid_dict[(x,y)] = grid[y,x]
    return grid_dict,grid

def gridmaker(): 
    #Import map file if possible
    if os.path.exists('map.jpg'):
        return importgrid()
    #make default map
    grid_dict = {}
    
    grid =       np.array([["A","A","A", "A","A","A", "A","A","A"]]) #"spacr" variable is just to keep matrix lined up.
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

def raycast(Px , Py , angle, projx):
    Ax, Ay , dAx, dAy, Bx, By , dBx, dBy = getintercepts( (Px,Py) , angle)
    nocollision = True
    while nocollision:
        distA = sqrt((Px-Ax)**2 + (Py-Ay)**2)
        distB = sqrt((Px-Bx)**2 + (Py-By)**2)
        if distA <= distB: #if A comes first
            if checkwall(Ax,Ay):
                return(Ax,Ay,distA)
                nocollision = False
            Ax += dAx
            Ay += dAy
        else:
            if checkwall(Bx,By):
                return(Bx,By,distB)
                nocollision = False
            Bx += dBx
            By += dBy
            
def drawwall(Wx,Wy,dist,projx):
    #takes raw coordinates as inputs
    Wx = Wx // gridsize
    Wy = Wy // gridsize
    
    if abs(Wx) > len(grid) or abs(Wy) > len(grid):
        newcolor = backgroundcolor #Out of bounds case
        height = 2
    else:
        m,K = 500,700
        shader = 1/(exp((dist - m) / K  )  + 1) #falloff effect
        color = walldict[(Wx,Wy)]
        newcolor = (int(shader*color[0]),int(shader*color[1]),int(shader*color[2]))
        height = 60*projdistance / dist
    offset =( Ny - height )/2
    colRect = pygame.Rect(projx,offset, 1,height) #1pixel thick rectangle spanning whole screen
    pygame.draw.rect(PROJ, newcolor, colRect)
    return
    
    
def test(playerpos, angle):
    """
    Test function used for debugging
    """
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

def applydrag(vel_x,vel_y,vel_z=None):
    speedsquared = vel_x**2 + vel_y**2   
    speed = sqrt(vel_x**2 + vel_y**2)
    if abs(vel_x) and abs(vel_y) > max_speed:
        return max_speed*np.sign(vel_x),max_speed*np.sign(vel_y),vel_z
    elif abs(vel_x) > max_speed:
        return max_speed*np.sign(vel_x),vel_y,vel_z
    elif abs(vel_y) > max_speed:
        return vel_x,max_speed*np.sign(vel_y),vel_z
    totaldrag =  dragcoeff*speedsquared
    if speed == 0:
        return vel_x, vel_y, vel_z 
    xdragaccel = -np.sign(vel_x)*abs(totaldrag * vel_x/speed)                  #split drag component-wise
    ydragaccel = -np.sign(vel_y)*abs(totaldrag * vel_y/ speed)
    vel_x += xdragaccel
    vel_y += ydragaccel
    if vel_z != None:
        zdragaccel = -9.81
        vel_z += zdragaccel
    return vel_x, vel_y,vel_z

def main():
    (Px,Py) = (193,193)
    viewangle = -15
    clock = pygame.time.Clock()
    vel_x = 0
    vel_y = 0
    vel_z = None
    while True: #MAIN GAME LOOP#
        clock.tick(FPS)
        window.blit(PROJ,(0,0))
        PROJ.fill(floorcolor) #fill screen with floor color
        pygame.draw.rect(PROJ, roofcolor, (0,int(Ny/2),Nx,int(Ny/2)) )
        pygame.display.update()
        projx = 0 #possible error here if screen index starts at 1 or 0
        
        for event in pygame.event.get(): #detect events
            if event.type == pygame.QUIT or pygame.key.get_pressed()[27]: #detect attempted exit
                pygame.quit()
                sys.exit()
        viewangle += looksensitivity*pygame.mouse.get_rel()[0]
        

        if pygame.key.get_pressed()[101]: #rotate with E
            viewangle += turnspeed
        if pygame.key.get_pressed()[113]: #rotate with Q
            viewangle -= turnspeed
        if pygame.key.get_pressed()[119]: # Go FORWARD
            vel_x += speed*cos(radians(viewangle))
            vel_y += speed*sin(radians(viewangle))
        if pygame.key.get_pressed()[115]: #Go BACKWARD
            vel_x -= speed*cos(radians(viewangle))
            vel_y -= speed*sin(radians(viewangle))
        if pygame.key.get_pressed()[100]: #Strafe RIGHT
            vel_x -= speed*sin(radians(viewangle))
            vel_y += speed*cos(radians(viewangle))
        if pygame.key.get_pressed()[97]: #Strafe LEFT
            vel_x += speed*sin(radians(viewangle))
            vel_y -= speed*cos(radians(viewangle))
        
        vel_x,vel_y,vel_z = applydrag(vel_x,vel_y,vel_z)
        #vel_x,vel_y = degradevelocity(vel_x,vel_y)
        nextPx = Px + vel_x
        nextPy = Py + vel_y
        if checkwall(nextPx,nextPy):
            vel_x = 0
            vel_y = 0
        else:
            Px = nextPx
            Py = nextPy
                
        if pygame.key.get_pressed()[32] or pygame.mouse.get_pressed()[0]: #SHOOT GUN
            PROJ.fill(white) #fill screen with floor color
            pygame.display.update()
            targetx,targety,disttarget = raycast(Px, Py ,viewangle, projx)
            tx = targetx // gridsize
            ty = targety // gridsize
            if (tx,ty) in walldict.keys():
                del walldict[(tx,ty)]
        
        angle = viewangle - FOV/2
        for projx in range(projwidth):
            Wx,Wy,distW = raycast(Px, Py ,angle, projx)
            drawwall(Wx,Wy, distW, projx)
            angle += columnangle                                  

clock = pygame.time.Clock()
reboundcoeff = 0.05
Nx,Ny = 600,480
FPS = 60
speed = 800/FPS
playermass = 70
max_speed = 2*speed
dragcoeff = 0.01
turnspeed = 8
looksensitivity = 180/Nx #this is calibrated so one screen = 1 half turn 
gridsize = 32
FOV = 60 #degrees
walldict, grid = gridmaker()  

#derived parameters
projwidth,projheight = Nx,Ny
projdistance = (1/tan(radians(FOV/2))) * (projwidth/2) 
columnangle = FOV/projwidth #in degrees! # angle between rays/columns 

# set up surfaces
window = pygame.display.set_mode( (Nx,Ny) )
pygame.display.set_caption("Raycaster v3.5 - Press Esc To Quit...")
PROJ = pygame.Surface( (Nx,Ny))
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

main()
