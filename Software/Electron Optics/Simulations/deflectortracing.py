# -*- coding: utf-8 -*-
"""

@author: Darren

Deflectortracing.py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Deflectortracing.py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Deflectortracing.py.  If not, see <https://www.gnu.org/licenses/>.

See also https://github.com/NRC-NANOmi/NANOmi  / nanomi.org


This script imports electrostatic field data(from FEA simulations such as Comsol, etc)
to plot the trajectory of electrons within thefield. 

"""
import numpy as np
import matplotlib.pyplot as plt
import statistics as st

#Constants
m= 9.109383e-31  #mass of electron
q= -1.602176e-19 #electron charge
V_g= 50e3 #gun voltage
E_k=q*V_g #initial kinetic energy of electron
dt=1e-13 #time step
c= 2.99792e8 #speed of light


#dividing by 39.37 converts inches to meter

#Deflector plate positions
Lx=-0.1/39.37   
Rx=0.1/39.37

deflength = 0.4/39.37
defspace=0.22/39.37
defwidth= 0.275/39.37

z1=0.1/39.37
z2=z1+deflength+defspace


def_Lx= np.linspace (Lx,Lx,num=50)
def_Rx=np.linspace(Rx,Rx,num=50)

defz_1=np.linspace(z1,z1+deflength,num=50)
defz_2=np.linspace(z2,z2+deflength,num=50)

#plotting the deflectors on the graph to see their position, they are blue lines
plt.plot(def_Lx*1000,defz_1*1000,'b-')  
plt.plot(def_Lx*1000,defz_2*1000,'b-')
plt.plot(def_Rx*1000,defz_1*1000,'b-')
plt.plot(def_Rx*1000,defz_2*1000,'b-')

#Data/field limits
xmin=Lx
xmax=Rx
zmin=0
zmax=z2+deflength+0.1/39.37


#import file
file="125vnew.csv"  # file which contains electromagnetic field data
field=np.loadtxt(file, delimiter=',', skiprows=2,dtype=np.float64)
field[:,0]=field[:,0]/39.37
field[:,1]=field[:,1]/39.37

#narrow the field down 
#depending on the FEA software the electric field file could have 100,000 lines and more
#some of the lines may be outside of the area that we need for the trace
#it may be useful to filter the field array within the limits of the deflectors, use the below line
#filtered_field=field[(field[:,0]>=xmin) & (field[:,0]<=xmax) & (field[:,1]>=zmin) & (field[:,1]<=zmax)]

#find electron speed based on kinetic energy (relativistic formula)
def electron_speed(kE):
    gamma= (abs(kE))/(m*c**2)+1
    v= c* (1-(gamma)**(-2))**0.5
    return v

#find the electric field that is closest to the electron position 
def E_field (pos):
    x=pos[0]
    z=pos[1]
    index= np.abs((field[:,0]-x)**2+(field[:,1]-z)**2).argmin()
    closest_E= np.array([field[index,2],field[index,3]],dtype=np.float64)
    return closest_E

#find acceleration based on velocity and Electric field(relativitistic formula)
def find_acc(v, pos):
    E=E_field(pos)
    F=q*E
    speed=np.sqrt((v[0]**2 + v[1]**2))
    gamma= (1-speed**2/c**2)**(-0.5)
    acc= (1/(m*gamma))*(F-(np.dot(F,v)*v/c**2))
    return acc

#function to cauculate the shift of the electron based on initial and final positions
def find_shift(listofpos):
    shift_list=[]
    for i in range (len(listofpos)):
        sizeoflist=len(listofpos[i])
        finalpos=listofpos[i][sizeoflist-1]
        initialpos=listofpos[i][0]
        shift=abs(finalpos[0]-initialpos[0])
        shift_list.append(shift)
    
    return shift_list
    
#initial electrons at different x positions
x_electrons=np.linspace(-0.05/39.37,0.05/39.37,5)   
full_trajectory_list=[]
velocity_list=[]

# for loop to calculate the trajectory of each electron at different initial x positions
for i in range(len(x_electrons)):
    t=0 
    x=x_electrons[i]
    z= zmin
    position=np.array([x,z],dtype=np.float64)
    vx=0
    vz=electron_speed(E_k)
    velocity=np.array([vx,vz],dtype=np.float64)
    ax=0
    az=0
    acceleration=np.array([ax,az],dtype=np.float64)
    trajectory=[]
    angle_list=[]
    
    while(abs(position[0])<=xmax and position[1]<= zmax):
        trajectory.append(position)
        position=position+velocity*dt
        velocity=velocity+acceleration*dt
        acceleration=find_acc(velocity,position)
        t+=dt
        
        # if (position[1]<=z2 and position[1]>=(z1+deflength)):
        #     def_angle= abs(np.arctan(velocity[0]/velocity[1]))
        #     angle_list.append(def_angle)
        
    velocity_list.append(velocity)
    full_trajectory_list.append(np.array(trajectory))
    

#plot each trajectory as a red line
for i in range(len(full_trajectory_list)):
    plt.plot(full_trajectory_list[i][:,0]*1000,full_trajectory_list[i][:,1]*1000,'r-')
      

plt.xlabel('X-axis(mm)')    
plt.ylabel('Z-axis(mm)')
plt.title('Trajectory of electrons within +/- 125 V deflectors')


    
    
    
    