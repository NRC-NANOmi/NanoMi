
"""
 SphericalAberrationTrajectoryReader.py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

'''This file plots the trajectory of electrons that are initially released at some x distance away from the optical axis and calculates the spherical aberration and 
paraxial focal length using the alternative definition of focal length listed in the report. The file input should be a file exported from any of the 3D einzel lens COMSOL files
which is of the same format as the csv file attached in the same folder as this script.
'''

#Lens parameters scaling for plotting

Outer_electrode_thickness_scale=1
Electrode_gap_scale=1
Center_electrode_thickness_scale=1
Center_electrode_aperture_radius_scale=1
Outer_electrode_aperture_radius_scale=1
max_allowed_angle=0.05 #Only allow rays converging at a shallow angle to find the paraxial focal length and get more accurate fits for spherical aberration


#Lens parameters used for plotting
Electrode_1_start_pos=0
Outer_electrode_thickness=Outer_electrode_thickness_scale*3.96875e-3
Outer_electrode_aperture_radius=(Outer_electrode_aperture_radius_scale*2.54e-3)/2
Electrode_gap=Electrode_gap_scale*4.445e-3
Center_electrode_start_pos=Electrode_1_start_pos+Outer_electrode_thickness+Electrode_gap
Center_electrode_thickness=Center_electrode_thickness_scale*5.08e-3
Lens_center_position=Center_electrode_start_pos+Center_electrode_thickness/2
Center_electrode_aperture_radius=(Center_electrode_aperture_radius_scale*6.35e-3)/2
Electrode_3_start_pos=Center_electrode_start_pos+Center_electrode_thickness+Electrode_gap
Lens_length=2*Outer_electrode_thickness+2*Electrode_gap+Center_electrode_thickness #Length of the einzel lens
x_misalignment=0#5e-4 #misalignment of the third electrode along the x direction
y_misalignment=0

#Cropping a specific part of the E field array
x_min=-Center_electrode_aperture_radius #These four variables determine the x,y range that is being cropped from original potential/Efield plot (in m)
x_max=Center_electrode_aperture_radius
y_min=0
y_max=3.4e-2

fname="EinzelLens3D_0_6_VoltageRatio.csv" #The csv file containing all of the trajectory data, exported from COMSOL
data=np.float64(np.loadtxt(fname, delimiter=',', skiprows=9, usecols=(0,1,2,3,4,5,6,7))) #Opens the text file

filtered_data=data[(data[:,0]>=x_min) & (data[:,0]<=x_max) & (data[:,2]>=y_min) & (data[:,2]<=y_max)] #Crops the array

N_particles=np.int(np.max(filtered_data[:,3]))+1 #Total number of trajectories in the text file
list_of_trajectory=[] #Initializes list of trajectories
convergence_angle_list=[] #Forms convergence angle list
exit_angle_list=[] #Forms exit angle list

for i in range(N_particles):
    index=np.abs(filtered_data[(filtered_data[:,3]==i)][:,0]).argmin()
    convergence_angle=np.abs(np.arctan(np.divide(filtered_data[(filtered_data[:,3]==i)][:,5][index],filtered_data[(filtered_data[:,3]==i)][:,7][index])))
    exit_angle=np.abs(np.arctan(np.divide(filtered_data[filtered_data[:,3]==i][:,5][-1], filtered_data[filtered_data[:,3]==i][:,7][-1])))
    if exit_angle<=max_allowed_angle:
        list_of_trajectory.append(filtered_data[(filtered_data[:,3]==i)]) 
        convergence_angle_list.append(convergence_angle)
        exit_angle_list.append(exit_angle)
        #x_data.append(filtered_data[(filtered_data[:,3]==i)][0][0])
#Electrode positions displayed in plotting
electrode_1_x=np.linspace(Outer_electrode_aperture_radius,Outer_electrode_aperture_radius,num=100)
electrode_1_x_1=np.linspace(-Outer_electrode_aperture_radius,-Outer_electrode_aperture_radius,num=100)
electrode_1_y=np.linspace(Electrode_1_start_pos, Electrode_1_start_pos+Outer_electrode_thickness,num=100)
electrode_2_x=np.linspace(Center_electrode_aperture_radius,Center_electrode_aperture_radius,num=100)
electrode_2_x_1=np.linspace(-Center_electrode_aperture_radius,-Center_electrode_aperture_radius,num=100)
electrode_2_y=np.linspace(Center_electrode_start_pos,Center_electrode_start_pos+Center_electrode_thickness,num=100) 
electrode_3_x=np.linspace(Outer_electrode_aperture_radius+x_misalignment,Outer_electrode_aperture_radius+x_misalignment,num=100)
electrode_3_x_1=np.linspace(-Outer_electrode_aperture_radius+x_misalignment,-Outer_electrode_aperture_radius+x_misalignment,num=100)
electrode_3_y=np.linspace(Electrode_3_start_pos,Electrode_3_start_pos+Outer_electrode_thickness,num=100)

plt.figure()
plt.subplot(221)
plt.plot(electrode_1_x,electrode_1_y,'r-') #plots the edges of electrode 1
plt.plot(electrode_1_x_1,electrode_1_y,'r-')
plt.plot(electrode_2_x,electrode_2_y,'r-') #plots the edges of electrode 2
plt.plot(electrode_2_x_1,electrode_2_y,'r-')
plt.plot(electrode_3_x,electrode_3_y,'r-') #plots the edges of electrode 3
plt.plot(electrode_3_x_1,electrode_3_y,'r-')

for i in range(len(list_of_trajectory)):
    plt.plot(list_of_trajectory[i][:,0],list_of_trajectory[i][:,2],'b-')
    
plt.xlabel('X distance(m)')
plt.ylabel('Z distance(m)')
plt.title('Trajectory plot for trajectories with Alpha<='+str(max_allowed_angle)+'rad')

#Curve Fitting
guesses = (1, 0) #Initial guesses for fitting parameters
def fit_function(x, m, b):
    return  m*x+b

N_paraxial_ray=int(N_particles*0) #Chooses a certain trajectory to be the paraxial ray
Intersection_with_original_ray=list_of_trajectory[N_paraxial_ray][np.abs(list_of_trajectory[N_paraxial_ray][:,0]).argmin()][2]-(np.abs(list_of_trajectory[N_paraxial_ray][0,0])/np.tan(convergence_angle_list[N_paraxial_ray])) #The location of the secondary principal plane found using the original definition
Focal_point_z=list_of_trajectory[N_paraxial_ray][:,2][-1]-np.abs(list_of_trajectory[N_paraxial_ray][:,0][-1])/np.tan(exit_angle_list[N_paraxial_ray]) #The location where the line tangent to the exiting ray intersects the optical axis
Intersection_with_original_ray2=Focal_point_z-(np.abs(list_of_trajectory[N_paraxial_ray][0,0])/np.tan(exit_angle_list[N_paraxial_ray])) #The location of the secondary principal plane found using the alternative definition
paraxial_focal_length=list_of_trajectory[N_paraxial_ray][np.abs(list_of_trajectory[N_paraxial_ray][:,0]).argmin()][2]-Intersection_with_original_ray #The original definition of the focal length
paraxial_focal_length2=Focal_point_z-Intersection_with_original_ray2 #Alternative definition of focal length
x_data=np.square(convergence_angle_list)
x_data2=np.square(exit_angle_list)


axial_shift_list=[]
axial_shift_list2=[]
marginal_focal_length_list=[]
marginal_focal_length_list2=[]
for i in range(len(list_of_trajectory)):
    marginal_focal_length=list_of_trajectory[i][np.abs(list_of_trajectory[i][:,0]).argmin()][2]-Intersection_with_original_ray
    marginal_focal_point_z=list_of_trajectory[i][:,2][-1]-np.abs(list_of_trajectory[i][:,0][-1])/np.tan(exit_angle_list[i])
    Intersection=marginal_focal_point_z-(np.abs(list_of_trajectory[i][0,0])/np.tan(exit_angle_list[i]))
    marginal_focal_length2=marginal_focal_point_z-Intersection_with_original_ray2
    axial_shift_list.append(paraxial_focal_length-marginal_focal_length)
    axial_shift_list2.append(paraxial_focal_length2-marginal_focal_length2)
    marginal_focal_length_list.append(marginal_focal_length)
    marginal_focal_length_list2.append(marginal_focal_point_z)
    
y_data=axial_shift_list
y_data2=axial_shift_list2

fit_params,fit_cov = curve_fit(fit_function,x_data2,y_data2,p0=guesses,maxfev=10**5)
y_fit= fit_function(x_data2,*fit_params)
plt.subplot(222)
plt.plot(x_data2,y_data2, 'bo') #Plots the data calculated
plt.plot(x_data2,y_fit, 'r-')

#plt.plot(x_data,y_fit,'r-') #Plots the best fit curve
plt.xlabel("Exit Angle^2")
plt.ylabel("Axial Shift (m)")
plt.title("Axial Shift vs Exit Angle ^2 for trajectories with Exit Angle<="+str(max_allowed_angle)+'rad')

param_names = ['Spherical aberration coefficient(m)','y intercept(m)']
print ("Fit parameters:")
for i in range(len(fit_params)):
    print ('{} = {:.3e}'.format(param_names[i],fit_params[i]))
print("Paraxial focal length (m)= "+str(paraxial_focal_length2))
print("Center of Lens (m)= "+str(Intersection_with_original_ray2))
print("Lens Length= "+str(Lens_length))

plt.show()

