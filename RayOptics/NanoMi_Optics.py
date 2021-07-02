import matplotlib.pyplot as plt 
import matplotlib
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, Slider, TextBox
import numpy as np
from scipy.optimize import fsolve
import argparse

from scipy.optimize.nonlin import nonlin_solve
from variables import *
from  warnings import filterwarnings
filterwarnings("ignore") #to ignore the numpy deprecation warning



###############################################################
#               Command Line Functionality                    #
###############################################################

parser = argparse.ArgumentParser(description='Optionally provide focal lengths and plot instructions via command line. Type "python NanoMi_optics.py -C1 x -C2 x -C3 x -theme d/l -update y/n", where x is the focal length; you can provide as many or none of these rguments (ex. python NanoMi_optics.py -C1 12.3 -C3 34.87 -theme d). \nIf an argument is not provided, it will default to values in variables.py', epilog="If you have any suggestions or questons, please let me know :)")
parser.add_argument("-C1", help='focal length of C1 [mm]')
parser.add_argument("-C2", help='focal length of C2 [mm]')
parser.add_argument("-C3", help='focal length of C3 [mm]')
parser.add_argument("-theme", help='type d for dark theme, l for light theme')
parser.add_argument("-update", help='type y to update current plot, n to create new graph')

args = parser.parse_args()

if args.C1 != None:
    Cf[0] = float(args.C1)
if args.C2 != None:
    Cf[1] = float(args.C2)
if args.C3 != None:
    Cf[2] = float(args.C3)

if args.theme != None:
    if args.theme.lower() == 'd':
        darkTheme = True
    elif args.theme.lower() == 'l':
        darkTheme = False

if args.update != None:
    if args.update.lower() == 'y':
        newGraph = False
    elif args.update.lower() == 'n':
        newGraph = True


if newGraph == None:
    newGraph = input("Select Mode:\n1. Update Graph \n2. New Graph \n")
    if newGraph == "1":
        newGraph = False 
    elif newGraph == "2":
        newGraph = True
    else:
        raise ValueError("Invalid Entry, Please Type 1 or 2")

if darkTheme == None:
    darkTheme = input("Select Theme:\n1. Light \n2. Dark \n")
    if darkTheme == "1":
        darkTheme = False
    elif darkTheme == "2":
        darkTheme = True
    else:
        raise ValueError("Invalid Entry, Please Type 1 or 2")




###############################################################
#                    Calculation Functions                    #
###############################################################
                 

def Mspc(d):   #transfer matrix for free space
    return np.array( [[1,d],[0,1]] , dtype=float)
 

def Mtl(f):    #transfer matrix for thin lens
    return np.array( [[1,0],[-1/f,1]] , dtype=float)
 

def A(f,a):    #Thin lens formula 1/f = 1/a + 1/A ||      A = (1/f - 1/a)^-1 
            # A ... image, a ... object, f ... focal length
    return (1/f - 1/a)**-1   
 

def f(a,A):    #focal length from known a,A
    return(1/a + 1/A)**-1
 

def Mag(a,AA): #magnification of a thin lens
    return -AA/a


def URcalc(f0,r0,A0,B0):
    return ((f0-B0)/A0)**(-1/r0)

def rOutS3CL(c1F,c2F,c3F,c1Z,c2Z,c3Z,smpZ,rGfun): #calculates probe for 3 CL system at sample
    #  inputs:    focal lengths and locations of CL1, CL2, CL3 and sample
    #             rGfun vector of the r, alpha [mm, rad] of rays from gun
    #  output     vector rOut3CL of beam at sample plane

    rOut3CL = np.matmul(Mspc(smpZ), Mtl(c3F)) 
    rOut3CL = np.matmul(rOut3CL, Mspc(c3Z))
    rOut3CL = np.matmul(rOut3CL,  Mtl(c2F))
    rOut3CL = np.matmul(rOut3CL,  Mspc(c2Z))
    rOut3CL = np.matmul(rOut3CL,  Mtl(c1F))
    rOut3CL = np.matmul(rOut3CL,  Mspc(c1Z))
    rOut3CL = np.matmul(rOut3CL,  rGfun)  #^Matrix Multiplication
    return rOut3CL


def fMinCalc():
    URmax = lambda f: URcalc(f,2.503,9.709,-3.723) - 1
    fminSym = fsolve(URmax, x0=1)
    URmax = lambda f: URcalc(f,2.727,7.59,-0.811) - 1
    fminAsym = fsolve(URmax, x0=1)
    return fminSym, fminAsym


def linspace(start,step,num): #creates a linearly-spaced row vector
    vector = np.empty((1,num))
    for i in range(num):
        vector[0][i] = start + step*i
    return vector


def reset_routMax():
    global routMax
    routMax = np.zeros((2,1))
    return



###############################################################
#                    Plotting Functions                       #
###############################################################
 
def SymBox(x, w, h, col, text, ax): 
    #Draws a box along the (true) x-axis 
    # x = location of center point of box along x-axis

    Lbore = 25.4*0.1/2 # smaller diameter lens bore (ground outer electrodes)

    ax.add_patch(Rectangle((x-w/2,-h), w, h*2, edgecolor=col, facecolor='none', lw=LW)) #rectangle box
    ax.hlines(Lbore,x-w/2,x+w/2, colors = col) #top lens bore
    ax.hlines(-Lbore,x-w/2,x+w/2, colors = col) #bottom lens bore
    ax.vlines(x,-h,h, colors=col, linestyles='--') #electrode location in lens 
 
    ax.text(x,-h-0.2, text, fontsize = FS, color = col, rotation = 'horizontal', ha = 'center')
 
    return
 

def AptSmpl(x, h, flip, col, text, ax): 
    #centre, height, flip 1 nose on right, -1, nose on left, label
    # x = location of center point along (true) x-axis

    #Mover for aperture or sample
  
    Lng = 25
    Shrt = 3
    # Shrt, Lng distance from mid holder to sample or apt plane [mm], defined only within a function

    ax.add_patch(Rectangle((x+flip*Shrt,-h),-flip*Lng-flip*Shrt,2*h,edgecolor=col,facecolor='none',lw=LW))
    ax.vlines(x,h,-h, colors = col, linestyle = '--') #electrode location in lens
 
    ax.text(x-flip*10, -h-0.2, text, color = col, fontsize = FS, ha = 'center', rotation = 'horizontal')
 
    return


def LBoxA(x, h, col, text, ax): 
    
    # Assymetric lens box - draw Lens bore DIAMETER: 0.1" grounds, 0.25" central electrode
    Lng = 52.2
    Shrt = 11.6
    # Shrt, Lng distance from mid electrode to face of lens in [mm], defined only within a function, 
    Lbore = 25.4*0.1/2 # smaller diameter lens bore (ground outer electrodes)

    ax.add_patch(Rectangle((x+Shrt,-h),-Lng-Shrt,2*h,edgecolor=col,facecolor='none',lw=LW))
    
 
    ax.vlines(x, -h, h, colors=col, linestyles='--') # Electrode Location in lens 

    ax.hlines(-Lbore, x-Lng, x+Shrt, colors=col) # BOTTOM lens bore
    ax.hlines(Lbore, x-Lng, x+Shrt, colors=col ) # TOP lens bore    
 
    ax.text(x-10, -h-0.2, text, color = col, fontsize = FS, ha = 'center', rotation = 'horizontal')
 
    return 

 
def mvac(z0, d, rin): # transfer matrix for vacuum & plot of corresponding rays
    """ inputs:    z0    ... object location [mm] from source
                   d     ... distance in space traveled [mm]
                   rin   ... [height" of IN beam [mm]; angle of IN beam [rad]]; column vector
        outputs:   rout  ... height X [mm] OUT-beam, angle of OUT beam [rad] ; column vector
                   d     ... distance beam traveled along z [mm]
    """
    rout = np.matmul(Mspc(d), rin) # beam height X [mm], beam angle [rad] after propagation
 
    return rout, d


def mlens(z0, f, rin, zin, lens, crossoverPoints, Cmag): # transfer matrix for a thin lens & plot of corresponding rays from lens to image
    """ inputs:   z0     ... lens distance from source [mm] 
                  f      ... focal length [mm] 
                  rin    ... [height" of IN beam [mm]; angle of IN beam [rad]]; column vector
                  zin    ... location of object [mm] from source
                  lens   ... string name of the lens 
        outputs:  rout   ... [height X [mm] OUT-beam-at-image, angle of OUT-beam [rad]]; column vector
                  zout   ... image location Z [mm] from source
                  d      ... lens centre-image distance along z [mm]
                  MagOut ... magnification image/object
    """

    # locate image z & crossover 
    Mtmp = np.matmul(Mtl(f),Mspc(z0-zin)) # temporary matrix calculating transfer vacuum to lens, and lens
    d = -Mtmp[0,1]/Mtmp[1,1] # lens-to-image [mm] # for thin lens # AA = A(f,z0)
    z_out = d + z0 # image-to-source Z [mm] 
 
    # rout = [X, q] at OUT-face of lens 
    routIM = np.matmul(np.matmul(Mspc(d),Mtl(f)), rin) # r = [x,q] at image location
    rout = np.matmul(Mtl(f),rin) # r = [x,q] at OUT-face of lens - that is needed to vacuum propagation matrix and plot
   
    # calculate magnification X_image / X_obj
    MagOut = 1/Mtmp[1,1] # for thin lens: MagOut = Mag(z0,d) % or MagOut = Mag(z0,A(f,z0))
 
    #update graph
    i = Cfname.index(lens) # find index of lens 'Cx' where x is 1,2,3
    Cmag[i].set_text(lens + " Mag  = {:.3f}X".format(float(MagOut))) # print the MagOut 
    crossoverPoints[i].set_data(z0+f,0) # place a marker at crossover

    return rout, z_out, d, MagOut


def PlotCL3(UR, Cf, ray, fig, crossoverPoints, Cmag):
    #update graph title
    title = 'Lens UR:   C1 = {:.3f}'.format(UR[0]) + '   C2 = {:.3f}'.format(UR[1]) + '   C3 = {:.3f}'.format(UR[2]) + '\n\n   Condenser Apperture D = ' + str(CAdiam*1e3) + ' μm \n\n Lens focal length:  C1 = {:.3f}'.format(Cf[0]) + ' mm   C2 = {:.3f}'.format(Cf[1]) + ' mm  C3 = {:.3f}'.format(Cf[2]) + ' mm'
    fig.suptitle(title, color = plotColor, fontsize=FS*1.3, y=0.99, fontweight='semibold', fontstretch='expanded')    
    
    x, y = [], []
 
    # ~~~~~~~~ electron gun edge ray rG (max source radius, max angle) ~~~~~~~~~~~~~~      
    # ---- Source to C1 to Image 1 ---------
    z0 = 0
    rout1, d1 = mvac(0,Czz[0],ray) # ray propagation from source to C1
    x.append(z0)
    x.append(d1)
    y.append(ray[0][0])
    y.append(rout1[0][0])

    rout_C1, zout_C1, d_C1, Mag1 = mlens(Czz[0],Cf[0],rout1,0,'C1', crossoverPoints, Cmag) # effect of C1

    rout_Im1, d_Im1 = mvac(Czz[0],d_C1,rout_C1) # ray propagation in vacuum from C1 to Image 1 
    x.append(Czz[0])
    x.append(Czz[0]+d_Im1)
    y.append(rout_C1[0][0])
    y.append(rout_Im1[0][0])


    # ----- Image 1 to C2 to Image 2 -------
    rout2, d2 = mvac(Czz[0],Cz[1],rout_C1) # ray propagation in vacuum from C1 to C2      
    x.append(Czz[0])
    x.append(Czz[0]+d2)
    y.append(rout_C1[0][0])
    y.append(rout2[0][0])

    rout_C2,zout_C2,d_C2,Mag2 = mlens(Czz[1],Cf[1],rout2,0,'C2', crossoverPoints, Cmag) # effect of C2

    rout_Im2,d_Im2 = mvac(Czz[1],d_C2,rout_C2) # ray propagation in vacuum from C2 to Image 2 
    x.append(Czz[1])
    x.append(Czz[1]+d_Im2)
    y.append(rout_C2[0][0])
    y.append(rout_Im2[0][0])

       
    # ----- Image 2 to C3 to Image 3 ------- 
    rout3,d3 = mvac(Czz[1],Cz[2],rout_C2) # ray propagation in vacuum from C2 to C3 
    x.append(Czz[1])
    x.append(Czz[1]+d3)
    y.append(rout_C2[0][0])
    y.append(rout3[0][0])
        
    rout_C3,zout_C3,d_C3,Mag3 = mlens(Czz[2],Cf[2],rout3,0,'C3', crossoverPoints, Cmag) # effect of C3

    rout_Im3,d_Im3 = mvac(Czz[2],d_C3,rout_C3) # ray propagation in vacuum from C3 to Image 3
    x.append(Czz[2])
    x.append(Czz[2]+d_Im3)
    y.append(rout_C3[0][0])
    y.append(rout_Im3[0][0])


    # ----- C3 to sample plane ------
    rout_smpl,d_smpl = mvac(Czz[2],Smpl_z-Czz[2],rout_C3) # ray propagation in vacuum from C2 to C3
    x.append(Czz[2])
    x.append(Czz[2]+d_smpl)
    y.append(rout_C3[0][0])
    y.append(rout_smpl[0][0])


    global routMax  # finding the beam farthest from the optics axis
    if abs(rout_smpl[0]) > abs(routMax[0]): # finding the beam farthest from the optics axis                
        routMax = rout_smpl
        
    return x, y


def setupGraph(withSliders):
    global plotColor

    if darkTheme:
        matplotlib.rc('axes',edgecolor='w')
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.subplots_adjust(top=0.88, bottom=0.18)
        fig.set_facecolor(plotColor)
        ax.set_facecolor(plotColor)
        plotColor = [1,1,1]
    else:
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.subplots_adjust(top=0.88, bottom=0.18)

    ax.axis([0, FX, -FY, FY])
    ax.set_xlabel('Z [mm]', color = plotColor)
    ax.set_ylabel('X [mm]', color = plotColor)

    #Drawing Permanent Things in the Background
    SymBox(AnodeLoc,30,PlH,ColAnode,'Anode', ax)  #draw Anode
    SymBox(DefLoc,10.2,PlH,ColStig,'Stig = Deflect.', ax) #draw stig deflect
    AptSmpl(CAloc,PlH,1,plotColor,'Cond. Apert', ax) #draw cond apert #since Cond Apert is black, use plotColor to switch it to white in dark mode
    AptSmpl(Smpl_z,PlH,-1,ColSmpl,'Sample', ax) # draw sample
    SymBox(Czz[0],ThSymLens,PlH,ColSymLens,'C1', ax) # draw C1        
    LBoxA(Czz[1],PlH,ColAssLens,'C2', ax)            # draw C2
    LBoxA(Czz[2],PlH,ColAssLens,'C3', ax)            # draw C3
    ax.axhline(0, 0, 1, color = red, linestyle = '--') # draw red dashed line on x-axis

    #initialize things that will be drawn and updated
    drawnRays, Cmag, crossoverPoints = [], [], []

    for i in range(len(rays)):
        drawnRays.append( ax.plot([], lw=LW, color = rayColors[i])[0] )

    for i in range(len(Cf)):
        Cmag.append( ax.text(Czz[i] + 5, -1, '', color='k', fontsize = FS, rotation = 'vertical', backgroundcolor = lightGray) )
        crossoverPoints.append( ax.plot([], 'go')[0] )

    extremeInfo = ax.text(300,1.64,'', color = plotColor, fontsize = 'medium', ha = 'center')


    if withSliders == True:
        sliders, textboxes = [], []
        for i in range(len(Cf)):
            # Create the Sliders & Accompanying Textboxes
            slider_ax = plt.axes([0.05, 0.092-0.04*i, 0.85, 0.02]) # x,y,w,h of slider 
            sliders.append( Slider(slider_ax, Cfname[i], slider_min, slider_max, initcolor='none', valinit = Cf[i]) )
            sliders[i].valtext.set_visible(False)
            textbox_ax = plt.axes([0.92, 0.091-0.04*i, 0.035, 0.03]) # x,y,w,h of textbox
            textboxes.append( TextBox(textbox_ax, '', color = [0.95,0.95,0.95], initial = round(Cf[i],3)) )
            ax.text(650,-2.22-i*0.2,'mm')

        return fig, ax, drawnRays, Cmag, crossoverPoints, extremeInfo, sliders, textboxes
   
    else:
        return fig, ax, drawnRays, Cmag, crossoverPoints, extremeInfo


def updateGraph(event): #for dynamically updating graph when dynamic updating is selected
    global axbackground_1
    axbackground_1 = fig_1.canvas.copy_from_bbox(ax_1.bbox)

    for i in range(len(textboxes)):     
        textboxes[i].set_val(round(sliders[i].val, 3)) #<---- This was causing the program to crash
    
    reset_routMax()

    new_Cf = [sliders[0].val, sliders[1].val, sliders[2].val] 
    new_UR = [URcalc(f0=new_Cf[0],r0=2.503,A0=9.709,B0=-3.723), URcalc(f0=new_Cf[1],r0=2.727,A0=7.59, B0=-0.811), URcalc(f0=new_Cf[2],r0=2.727,A0=7.59, B0=-0.811)] #needs to run before plots, introduces calcs of excitation voltages used later
    
    # update the drawn rays, reset the extreme information
    for i in range(len(rays)):
        drawnRays_1[i].set_data(PlotCL3(new_UR, new_Cf, rays[i], fig_1, crossoverPoints_1, Cmag_1))
    extremeInfo_1.set_text('EXTREME beam DIAMETER @ sample = {:.2f}'.format(routMax[0][0]*1e6*2) + ' nm  & convergence SEMI angle = {:.2f}'.format(routMax[1][0]*1e3)+' mrad')
    
    # restore background
    fig_1.canvas.restore_region(axbackground_1)

    # redraw the rays
    for ray in drawnRays_1:
        ax_1.draw_artist(ray)
 
    fig_1.canvas.blit(ax_1.bbox)
    #fig.canvas.flush_events() <--- this is causing the program to crash

    return


def createNewGraph(event): #for creating new graph when dynamic updating is not selected
    fig_2, ax_2, drawnRays_2, Cmag_2, crossoverPoints_2, extremeInfo_2 = setupGraph(withSliders=False)

    reset_routMax()
    new_Cf = [sliders[0].val, sliders[1].val, sliders[2].val] 
    new_UR = [URcalc(f0=new_Cf[0],r0=2.503,A0=9.709,B0=-3.723), URcalc(f0=new_Cf[1],r0=2.727,A0=7.59, B0=-0.811), URcalc(f0=new_Cf[2],r0=2.727,A0=7.59, B0=-0.811)] #needs to run before plots, introduces calcs of excitation voltages used later
    
    fig_2.canvas.draw()   #note that the first draw comes before setting data 

    for i in range(len(textboxes)):     
        textboxes[i].set_val(round(sliders[i].val, 2)) 

    for i in range(len(rays)):
        drawnRays_2[i].set_data(PlotCL3(new_UR, new_Cf, rays[i], fig_2, crossoverPoints_2, Cmag_2))
    extremeInfo_2.set_text('EXTREME beam DIAMETER @ sample = {:.2f}'.format(routMax[0][0]*1e6*2) + ' nm  & convergence SEMI angle = {:.2f}'.format(routMax[1][0]*1e3)+' mrad')
    
    # redraw the rays
    for ray in drawnRays_2:
        ax_2.draw_artist(ray)
    
    plt.show()


#these functions are for upating the slider if textbox value changes, and vice-versa; DO NOT RENAME THEM
def updateSlider1(value):
    sliders[0].set_val(float(value))
    return
def updateSlider2(value):
    sliders[1].set_val(float(value))
    return
def updateSlider3(value):
    sliders[2].set_val(float(value))
    return
def updateTextbox1(event):
    textboxes[0].set_val(round(sliders[0].val, 3))
    return
def updateTextbox2(event):
    textboxes[1].set_val(round(sliders[1].val, 3))
    return
def updateTextbox3(event):
    textboxes[2].set_val(round(sliders[2].val, 3))
    return




###############################################################
#                   Start of Main Program                     #
###############################################################

 
UR = [URcalc(f0=Cf[0],r0=2.503,A0=9.709,B0=-3.723), URcalc(f0=Cf[1],r0=2.727,A0=7.59, B0=-0.811), URcalc(f0=Cf[2],r0=2.727,A0=7.59, B0=-0.811)] # calculate 
fminSym, fminAsym = fMinCalc() # needs to run before plots, introduces calcs of excitation voltages used later
routMax = np.zeros((2,1)) #a global variable for the max probe diameter; need to reset it each time a plot of the rays is generated


fig_1, ax_1, drawnRays_1, Cmag_1, crossoverPoints_1, extremeInfo_1, sliders, textboxes = setupGraph(withSliders=True)

# fig.canvas.manager.full_screen_toggle() # turn on default fullscreen mode

fig_1.canvas.draw()   #note that the first draw comes before setting data 

axbackground_1 = fig_1.canvas.copy_from_bbox(ax_1.bbox) #save permanent background 

plt.show(block=False)

if newGraph: #if we want to create a new graph 
    #create an OK button that will create the new graph when pressed
    button_axes = plt.axes([0.96, 0.051, 0.03, 0.03]) 
    button = Button(button_axes, 'OK', color =(0.8,0.8,0.8))
    button.on_clicked(createNewGraph)
    #update sliders and textboxes 
    for i in range(len(sliders)):
        sliders[i].on_changed(eval("updateTextbox"+str(i+1)))
        textboxes[i].on_submit(eval("updateSlider"+str(i+1)))

else: #if we want to dynamically update current graph
    #update sliders and textboxes 
    for i in range(len(sliders)):
        sliders[i].on_changed(updateGraph)
        textboxes[i].on_submit(eval("updateSlider"+str(i+1)))

    
#update the drawn rays, reset the extreme information
for i in range(len(rays)):
    drawnRays_1[i].set_data(PlotCL3(UR, Cf, rays[i], fig_1, crossoverPoints_1, Cmag_1))
extremeInfo_1.set_text('EXTREME beam DIAMETER @ sample = {:.2f}'.format(routMax[0][0]*1e6*2) + ' nm  & convergence SEMI angle = {:.2f}'.format(routMax[1][0]*1e3)+' mrad')


#Trying out optional keybinds: press d to toggle b/w dark and light mode
def on_key(event):
    global plotColor
    if event.key.lower() == 'd' and plotColor == [0,0,0]:
        fig_1.set_facecolor(plotColor)
        ax_1.set_facecolor(plotColor)
        plotColor = [1,1,1]
        extremeInfo_1.set_color(plotColor)
        ax_1.set_xlabel('Z [mm]', color = plotColor)
        ax_1.set_ylabel('X [mm]', color = plotColor)
        updateGraph(event)
        plt.show()
    elif event.key.lower() == 'd' and plotColor == [1,1,1]:
        fig_1.set_facecolor(plotColor)
        ax_1.set_facecolor(plotColor)
        plotColor = [0,0,0]
        extremeInfo_1.set_color(plotColor)
        ax_1.set_xlabel('Z [mm]', color = plotColor)
        ax_1.set_ylabel('X [mm]', color = plotColor)
        updateGraph(event)
        plt.show()
fig_1.canvas.mpl_connect('key_press_event', on_key)


plt.show()


###############################################################
#                   Start of Finding Min Probe                #
###############################################################

print("\nDetermining Minimum Probe For All Beams\n")

### find min for probe ALL beams considered simultaneously
# Question: at each lens settings, what is the minimum of max(all beams) at the sample plane
# this section is only optimizing CL focal length with fixed CL position, CA diameter and sample position
 
# rG;   rGr0 = [0 rG(2)]' ->  r = 0;  rGq0 = [rG(1) 0]' -> parallel to axis
# ;  rGC -> CRAZY beam ... starts max negative r and max angle from neg to pos. size of CA
 
# parameters to optimize, Cf(1:3), Czz(1:3), smpl_Z, CAdiam,
  
#specify values and step of focal lengths to be explored for minimum probe size

 
C1f = linspace(fminSym, 0.1, 41)  #I ripped these 'num' values from MATLAB, need to find a better way eventually
C2f = linspace(fminAsym, 0.1, 163)
C3f = linspace(fminAsym, 0.1, 63) # ^focal lengths of lens in [mm]
 
 
 
MPr = np.empty( ( len(C1f[0]), len(C2f[0]), len(C3f[0]), 4 ) ) #initializing a 4D matrix 
MPq = np.empty( ( len(C1f[0]), len(C2f[0]), len(C3f[0]), 4 ) ) #initializing a 4D matrix 
 
 
for jj in range(0, len(C1f[0])):  #****** C1f, C2f, C3f are np.array objects, so we need to index into the row using Cxf[0] to access the row of values. To access the ith element, Cxf[0][i]. This is unlike lists, where we can directly index into the list 
    for kk in range(0, len(C2f[0])):
        for ll in range(0, len(C3f[0])):
            MPr[jj,kk,ll,0] , MPq[jj,kk,ll,0] = rOutS3CL(C1f[0][jj],C2f[0][kk],C3f[0][ll],Cz[0],Cz[1],Cz[2],Smpl_z - Czz[2],rG)   # rG ray
            MPr[jj,kk,ll,1] , MPq[jj,kk,ll,1] = rOutS3CL(C1f[0][jj],C2f[0][kk],C3f[0][ll],Cz[0],Cz[1],Cz[2],Smpl_z - Czz[2],rGr0) # rGr0 ray  
            MPr[jj,kk,ll,2] , MPq[jj,kk,ll,2] = rOutS3CL(C1f[0][jj],C2f[0][kk],C3f[0][ll],Cz[0],Cz[1],Cz[2],Smpl_z - Czz[2],rGq0) # rGq0 ray
            MPr[jj,kk,ll,3] , MPq[jj,kk,ll,3] = rOutS3CL(C1f[0][jj],C2f[0][kk],C3f[0][ll],Cz[0],Cz[1],Cz[2],Smpl_z - Czz[2],rGC)  # rGC ray
 
# MPr ... 1,2,3 dimensions go throug Cf1, Cf2, Cf3. 4th dimension goes through rG, rGr0,rGq0,rGC  
# MPq ... same as above for angle
 
MPrMx4 = np.amax(np.abs(MPr), axis = 3) # find max probe among all rays @ fixed C1,C2 and C3
 
MPrGlobal = np.amin(np.abs(MPrMx4)) # min probe radius among all lens settings
 
print('\nGlobal min probe diameter = ', MPrGlobal*1e6*2 ,' nm')
 
MPloc = np.where(MPrMx4 == MPrGlobal) # at which C1, C2 adn C3 does the probe have a min 
jj = MPloc[0][0] 
kk = MPloc[1][0] 
ll = MPloc[2][0]
 
# now find the focal length and Ur values @ smallest probe
Cf = [ C1f[0][jj], C2f[0][kk], C3f[0][ll] ] # new Cf values
UR = [ URcalc(f0=Cf[0],r0=2.503,A0=9.709,B0=-3.723), URcalc(f0=Cf[1],r0=2.727,A0=7.59, B0=-0.811), URcalc(f0=Cf[2],r0=2.727,A0=7.59, B0=-0.811) ]  # new UR values

reset_routMax()

#intialize new graph
fig_1, ax_1, drawnRays_1, Cmag_1, crossoverPoints_1, extremeInfo_1 = setupGraph(withSliders=False)
 
# plot the optics for the minimum probe diameter
for i in range(len(rays)):
    drawnRays_1[i].set_data(PlotCL3(UR, Cf, rays[i], fig_1, crossoverPoints_1, Cmag_1))
extremeInfo_1.set_text('EXTREME beam DIAMETER @ sample = {:.2f}'.format(routMax[0][0]*1e6*2) + ' nm  & convergence SEMI angle = {:.2f}'.format(routMax[1][0]*1e3)+' mrad')

plt.show()




    
