from mpl_toolkits.mplot3d import Axes3D 
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from scipy import integrate
import math 
from scipy.interpolate import UnivariateSpline

#import constants for focal length

from scipy.constants import elementary_charge
from scipy.constants import m_e 

"""
    [Bell_field_sim.py] is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        Bell_field_sim.py is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with [Bell_field_sim.py].  If not, see <https://www.gnu.org/licenses/>.

See also [github NanoMi project name] / nanomi.org


"""





#make a simple cylinder to represent the magnet
#diameter of 1.8 inch = 4.57 cm
#height of 1.5 inch = 3.81cm
dC = 4.6 # rounded cm
rC = dC/2 # cm
hC = 3.8 #cm 
xC=np.linspace(-rC, rC, 100)
zC=np.linspace(-hC/2, hC/2, 100)
XC, ZC=np.meshgrid(xC, zC)
YC = np.sqrt((rC**2)-XC**2) #equation of circle x2 + y2 = r2

#values to give to functions
A = 2 #2mm 
A_cm = A*(10**-2) #cm 
B0 = 1 #tesla
npoints = 20
nsteps = (2*npoints)-1 #this way z=0 is included in z
#creat cylindrical coordinate system
r = np.linspace(-npoints,npoints,nsteps) #mm #r
p = np.linspace(0, 2*np.pi,nsteps) # phi
R,P = np.meshgrid(r,p) # create two array for ploting
e = np.linspace(-npoints,npoints,nsteps)
z = np.linspace(-npoints,npoints,nsteps) #mm convert to 2D array units ,
print(z)
# i don't e for any equations i just need it to make a proper 2D array without issues
E, Z = np.meshgrid(e,z) 

#convert to cartesian coordinates
X, Y = R*np.cos(P), R*np.sin(P) #meters



def  zField(z,a): # Bell field
  Bz = (B0)/(1+((z/a)**2))
  return Bz
  #z needs to statisfy condtion Bz = B0 at z=0
def rField(r,z,a): #(r/2)*(dertivate of zfield WRT z)
  Br = (z*r*B0)/((z**2) + (a**2)) 
  return Br


def FWHM3(yarray, xarray):
  #final method
  #THIS ONE WORKS
  
  # using UnivariateSpline find the width of the function
  #UnivariateSpline approximates the function with piecewise notation
  # look up spline 
  spline = UnivariateSpline(xarray, yarray-np.max(yarray)/2, s=0) 
  #s is a smoothing factor 
  
  #find the roots of the width 
  r1, r2 = spline.roots()
  #return the roots
  return r1, r2

BZ_2D =zField(Z,A_cm)#call the functions
BR_2D = rField(R,Z,A_cm) #a in cm

#plotting
#fig = plt.figure()
#ax = plt.axes(projection='3d')
#surf =ax.plot_surface(X,Y,BZ, cmap = cm.coolwarm)# plot zField
#surf2 =ax.plot_surface(X,Y,BR, cmap = cm.coolwarm) # plot rField

##cylinder plot only 1/2 is ploted we want both halfs
#rstride= 20 #idk
#cstride= 10 #idk
#cylinder1 = ax.plot_surface(XC, YC, ZC, color='g', alpha=0.5, rstride=rstride)
#cylinder2 = ax.plot_surface(XC, -YC, ZC, color='g', alpha=0.5, rstride=rstride)


#surf =ax.plot_surface(X,Y,BZ, cmap = cm.coolwarm)# plot zField
##surf2 =ax.plot_surface(X,Y,BR, cmap = cm.coolwarm) # plot rField

##make legend and labels
#surf.set_label("Field Strength (Tesla)")


#fig.colorbar(surf ,shrink=0.5) # make colorbar legend
#ax.set_xlabel("X axis (cm)")
#ax.set_ylabel("Y axis (cm)")
#ax.set_zlabel("magnet height from center (cm)")
#print(BZ)
#plt.show()



Bz = zField(z, A)
#FWHM method 1

#to draw the horizontal line
maximum = np.amax(Bz)


#FWHM method3 
FWHM3 = FWHM3(Bz, z)
r1 = FWHM3[0]
r2 = FWHM3[1]
print("FWHM3:",FWHM3)

#plot the glaser field and FWHM
plt.plot(z,Bz, label="a="+str(A)+'mm')
plt.hlines(maximum/2, r1, r2, colors='r', label="FWHM") #using fWHM3
plt.xlabel('Optical axis Z(mm)')
plt.ylabel('B Field (T)')
plt.title('Field Strength (Fixed Units)')
plt.legend()

plt.show()

# integral of bell field = (pi*a)/2
#plotting focal length as function of changing electron voltage

charge = elementary_charge #electron charge (C)
m_E= m_e # mass of electron (kg)

voltage =np.linspace(5,20, 10)# voltage V
half_width = A*(10**-2) # converts to meters
#focal length function takes field strength, voltage, a from above
def focal_length(B0, V, a): # voltage in kv
  V = V*1000
  num = 16*m_E*V
  den = charge*(B0**2)*np.pi*a
  return num/den

f = focal_length(B0, voltage, half_width)*(10**5)
plt.plot(voltage,f)
plt.xlabel("voltage (kv)")
plt.ylabel("focal length $10^-5$ m")
plt.title("Focal Length of Lens")
plt.show()

#more focal length plots for differnt a values
#to maximize f we minimize a 
half_width_array = np.arange(1,11)*(1*10**-3) #mm


for i in half_width_array:
  f2= focal_length(B0, voltage, i)*(10**4)
  plt.plot(voltage, f2, label="a= "+str(round(i,5))+"m")
  plt.legend()

plt.xlabel("Voltage, (kv)")
plt.ylabel("focal length ($10^-4$m)")
plt.title("Focal length for varying half widths")
plt.show()



  