newGraph = None
darkTheme =  None


FS = 8     # font size 
FX = 600   # figure x-axis size
FY = 1.8   # figure y-axis size
LW = 1     # line width

AnodeLoc = 39.1 # Anode location [mm] along Z = 1.539" from tip 
CAdiam = 0.02 # Condenser aperture diameter in [mm]  300 um diameter condenser aperture
CAloc = 192.4 # 192.4 2021-01-01; Distance of Condenser Aperture from Source
DefLoc = 407.8+10.2/2 # location of deflector when stig used as deflector 20210101

ThSymLens = 63.8 # lens mechanical thickness [mm]
ThStig = 25.4    # stigmator mechanical thickness [mm]
ThDef = 48.3     # deflector mechanical thickness [mm]
ThApt = 20.32    # aperture mechanical holder thickness [mm]
ThSmpl = 20.32   # sample holder mehcanical thickness [mm]

PlH = 1.5


Cf = [13, 35, 10.68545] #manual guess, best so far when using 
Cfname = ['C1', 'C2', 'C3']
   
Czz = [257.03, 349, 517] #lens distances from source in [mm]                          #values for playing, Czz ... distance from tip 
Cz = [ Czz[0], Czz[1]-Czz[0], Czz[2]-Czz[1] ] #Cz is distance between lens (mm)         

Smpl_z = 528.9 #source-to-sample [mm]
Scr_z = 972.7  #Source to fluorscent screen with 6-way cross in place.


slider_min, slider_max = 0.1, 40

ColAssLens = [0.3, 0.75, 0.75] #color for lens outline
ColSymLens = [0.3, 0.9, 0.65] 
ColStig = [0.5, 0.3, 0.8]
ColDefl = [0, 0, 0]
ColApt = [0, 0, 0]
ColSmpl = [1, 0.7, 0]
ColAnode = [0.5, 0, 0.3]

red = [0.8,0,0]
lightGray = [240/255,240/255,240/255]
plotColor = [0,0,0] #DO NOT change this




import numpy as np 

rG = np.array([ [1.5e-2], [(CAdiam/2 - 1.5e-2)/CAloc] ])  #W pin, condenser aperture angle limited as per location and diameter  
rGr0 = np.array([ [0], [(CAdiam/2)/CAloc] ]) # @ r = 0, angle limited by CA   
rGq0 = np.array([ [rG[0][0]], [0] ]) # @r = tip edge, parallel to opt. axis      
rGC = np.array([ [-1*rG[0][0]], [(CAdiam/2 + abs(rG[0][0]))/CAloc] ]) #  @ -rG, angle up to +CA edge CRAZY BEAM

rG_color = [0.9, 0, 0]
rGr0_color = [0.0, 0.7, 0]
rGq0_color = [0.0, 0, 0.8]
rGC_color = [0.7, 0.4, 0]

rays = [rG, rGr0, rGq0, rGC] #add rays to this list
rayColors = [rG_color, rGr0_color, rGq0_color, rGC_color] #add color of each ray in same order as rays