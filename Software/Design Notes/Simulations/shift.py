# -*- coding: utf-8 -*-
"""

@author: Darren

Shift.py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shift. py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Shift.py.  If not, see <https://www.gnu.org/licenses/>.

See also https://github.com/NRC-NANOmi/NANOmi  / nanomi.org


This script is used to plot and calculate the shift of electrons 
between different deflector voltages which can be set. It is similar to tilt.py.
"""

import numpy as np
import matplotlib.pyplot as plt

m= 9.109383e-31  #mass of electron
q= -1.602176e-19 #electron charge
V_g= 50e3 #gun voltage
E_k=q*V_g #initial kinetic energy of electron 
c= 2.99792e8 #speed of light
dt=1e-13

#Voltage difference on top and bottom deflector plates 
V1x=50   
V2x=-50
Ez=0



# Lx=-0.1/39.37   
# Rx=0.1/39.37

deflength = 0.4/39.37  #length of deflector
defspace=0.22/39.37 # vertical space between top and bottom deflectors
defgap=0.2/39.37 # horizontal gap between left and right deflectors

maxshift=10e-9   #maximum deviation of the electron path from the original axis (in the x axis)
tiltangle=12e-3  
maxtiltangle=14e-3#tilt angle desired
maxplane =20e-3 #maximum vertical shift of the electron path (in z axis) 
# z1=0
# z2=z1+deflength+defspace

# def_Lx= np.linspace (Lx,Lx,num=50)
# def_Rx=np.linspace(Rx,Rx,num=50)

# defz_1=np.linspace(z1,z1+deflength,num=50)
# defz_2=np.linspace(z2,z2+deflength,num=50)

# #plotting the deflectors on the graph to see their position, they are blue lines
# plt.plot(def_Lx,defz_1,'b-')  
# plt.plot(def_Lx,defz_2,'b-')
# plt.plot(def_Rx,defz_1,'b-')
# plt.plot(def_Rx,defz_2,'b-')

xmax=0.1/39.37 # deflector plate is at 0.1 inch
zmax=deflength+defspace+deflength+maxplane

def electron_speed(kE):
    gamma= (abs(kE))/(m*c**2)+1
    v= c* (1-(gamma)**(-2))**0.5
    return v

def find_acc(v, E):
    F=q*E
    speed=np.sqrt((v[0]**2 + v[1]**2))
    gamma= (1-speed**2/c**2)**(-0.5)
    acc= (1/(m*gamma))*(F-(np.dot(F,v)*v/c**2))
    return acc

trajectory_list=[]
velocity_list=[]
position_list=[]
angle_list=[]

def vcombofinder():
    E1x=V1x/defgap  #calculating constant e-field of bottom deflectors
    E1=np.array([E1x,Ez],dtype=np.float64)
    E2x=V2x/defgap   #calculating constant e-field of top deflectors
    E2=np.array([E2x,Ez],dtype=np.float64)
    x=0
    z=0
    position=np.array([x,z],dtype=np.float64)
    vx=0
    vz=electron_speed(E_k)
    velocity=np.array([vx,vz],dtype=np.float64)
    ax=0
    az=0
    acceleration=np.array([ax,az],dtype=np.float64)
    trajectory=[]
    E_zero=np.array([0,0],dtype=np.float64)
    
    while (position[1]<=zmax):
        trajectory.append(position)
        position=position+velocity*dt
        velocity=velocity+acceleration*dt
        if (position[1]<=(deflength)):
            acceleration=find_acc(velocity,E1) 
        elif(position[1]<=(deflength+defspace)):
            acceleration=find_acc(velocity,E_zero)
        elif (position[1]<(deflength+defspace+deflength)):
            acceleration=find_acc(velocity,E2)
        else: 
            acceleration=find_acc(velocity,E_zero)
        
    trajectory_list.append(np.array(trajectory))
    angle_list.append(np.arctan(velocity[0]/velocity[1]))
                    
vcombofinder()

plt.plot(trajectory_list[0][:,0]*1000,trajectory_list[0][:,1]*1000,'r-')

plt.xlabel('X-axis(mm)')
plt.ylabel('Z-axis(mm)')
plt.title('Shift at 50keV')

    