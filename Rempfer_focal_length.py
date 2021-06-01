import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

"""
    [Rempfer_focal_length.py] is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        [Rempfer_focal_length.py]is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with [Rempfer_focal_length.py].  If not, see <https://www.gnu.org/licenses/>.

See also [github NanoMi project name] / nanomi.org



This script is meant to visualize the focal length of an eiznel lens based on Rempfer(1985) with some back of hand numbers


Gertude F. Rempfer. Unipotential electrostatic lenses: Paraxial proper-
ties and aberrations of focal length and focal point. American Institute
of Physics, 1985.


"""
#constants
#Variables named after Rempfer 1985

a = [86.83, 78.36, 69.89,61.42] #mm source to front grating
b = [38.47, 46.97, 55.41,63.88]#mm lens to back grating
d=  [804.3,795.83,787.36,778.89] #mm back grating to screen
e1 = 125*(10**-6) #micrometer spacing of front grating 
e2 = 125*(10**-6) #micrometer spacing of back grating 
                  # both converted to meters
Z0= 125.3 #mm source to lens 

#a and Z0 are negative since they're measure going right from the object plane

#test with different powers later
# i assume these will be way bigger
E1 = np.linspace(5,20,5)*(10**-2) #  front magnification in meters
E2 = np.linspace(4,20,5)*(10**-2) #  back magnification in meters 


#starting voltage ratio from 0.3-1
Vc = 15 #KV
V1 = np.linspace(5,15,5) #KV
V2 = np.linspace(1.5,2,5) #KV

def voltage_ratio(Vc,Vl):
    Vr = Vl/Vc
    return Vr

V_ratio =voltage_ratio(Vc,V1)
V_ratio_2 = voltage_ratio(Vc,V2)

# these values should be between 10mm and 2cm
#10mm comes from Sean and Suliat

def image_source(E, b, d):
    M = E/e2 # back grating magnification
    z = b - (d/(M-1))
    return z
    
    

# function for image magnification m

#demagnify should give us  0<m<1 values for all values
def image_magnification(E_front, E_back, image,b,a):
    M1 = E_front/e1 #front magnification
    M2 = E_back/e2 #back magnification
   
    m = (M1/M2)*((b-image)/a)
    return m



def focal_length(image,mag):
    F = (Z0-image)/((1/mag)-mag)
    return F

#first attempt


#def focal_distance(image,mag):
    #G = image - f*mag
    #return G
#g = focal_distance(zi,m)




#want minimum at V_ratio =1    

#all empty lists to apppend to
Z = [] # image distance
M = [] # magnification m
F = [] # focal length
Z.clear()
M.clear()
F.clear()
for i in range(len(b)): # for every grid spacing find the image soruce distance
    # find the magnificaition 
    # find the focal length 
    z = image_source(E2,b[i] ,d[i])
    m = image_magnification(E1,E2,z, b[i], a[i])
    f = focal_length(z ,m)
    Z.append(z)
    M.append(m)
    F.append(f)
 
    
for i in range(0,1): # for every grid spacing plot the focal length as a function of the voltage ratio
    plt.scatter(V_ratio,F[i], linestyle=':',)
#make a function fit 

def exp_fit(x,a,b): # intial fit looks exponential
    return a*np.exp(b*x) # x here should be the voltage ratios

#apply the curve fit to the function find the parameters a,b



parameters, pcov  = curve_fit(exp_fit,V_ratio, F[0])
print("The parameters are: ", parameters)


fs = 12 #fontsize
plt.plot(V_ratio, exp_fit(V_ratio, *parameters), 'b-', label = 'fit: a=%5.3f, b = %5.3f' %tuple(parameters))



plt.ylabel("focal length (mm)", fontsize=fs)
plt.xlabel("voltage ratio", fontsize=fs) 
plt.title("Focal length as function of Voltage ratio")
plt.legend(loc = 'best')
plt.show()
#plot with varying a and B values

#print("magnification", M)
