# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
'''
This script models the Nano-Mi's einzel lenses as a thick lens with an effective index of refraction and radius of curvature, with the location of the principal planes
estimated from COMSOL simulations. By drawing these analogies, it is possible to use matrix methods to provide ray tracing. In addition, the magnifications of the 
lens system(s) can be calculated.

The first part of the script uses matrix methods to do ray tracing. For the ray tracing functionality, an initial ray vector (consisting of the height and angle of 
the ray) must be specified. In addition, the positions and focal lengths of the lenses must be specified. The code will output a sketch showing the ray's trajectory
as it passes through the lens system

For the second part of the script, the magnification of the illumination system and the imaging system will be calculated. This part no longer assumes that the focal
lengths are known, but instead optimizes the focal lengths of the lenses in the illumination system so that the beam is demagnified as much as possible. 
In contrast, for the imaging system, the focal lengths are optimized so that the beam is magnified as much as possible. However, trying to magnify
as much as possible using scipy.minimize and related functions has been unsuccessful
'''

#Initial Ray Vector
h_0=0e-4#Initial height of the ray in meters
theta_0=5e-2 #Initial angle of the ray in radians
initial_ray=np.array([h_0,theta_0]) #The initial ray vector, with the first element indicating its height, the second indicating its angle relative to the optical axis


#Lens Parameters (Lens Physical Dimensions)
#These parameters are simply used for displaying the approximate position of each component of the lens in the ray tracing sketch. For example, Electrode_1_start_post=0 
#indicated that the bottom of the first electrode is at a vertical position of 0.
Electrode_1_start_pos=0
Outer_electrode_thickness=3.96875e-3
Outer_electrode_aperture_radius=(2.54e-3)/2
Electrode_gap=4.445e-3
Center_electrode_start_pos=Electrode_1_start_pos+Outer_electrode_thickness+Electrode_gap
Center_electrode_thickness=5.08e-3
Lens_center_position=Center_electrode_start_pos+Center_electrode_thickness/2
Center_electrode_aperture_radius=(6.35e-3)/2
Electrode_3_start_pos=Center_electrode_start_pos+Center_electrode_thickness+Electrode_gap
Lens_length=2*Outer_electrode_thickness+2*Electrode_gap+Center_electrode_thickness #Thickness of the entire lens

#Lens Parameters (optical values) (will be named the same way as Hecht Fig.6.5) Note: The location of H1 and H2 may change depending on the lens's power
d_lens=Lens_length #thickness of the lens in meters
H1=15.69e-3 #The location of the primary principal plane relative to the front of the lens at voltage ratio of 1, determined using COMSOL simulations
H2=d_lens-H1
#Focal Lengths (ONLY FOR RAY TRACING, NOT FOR MAGNIFICATION CALCULATIONS)
f1=0.01 #Focal length of lens 1 in meters
f2=0.01
f3=0.01
f4=0.01
f5=0.01

#Lens/Sample Locations
#The lens positions always refers to the position of the first electrode relative to the gun's filament
d1=0.12667 #Location of the front electrode of lens 1 relative to the gun (in meters)
d2=2*0.12667
d3=3*0.12667
d_sample=3*0.12667+0.02
d4=0.43
d5=0.47
d6=0.56
d7=0.67
d8=0.78
d_screen=0.89

#Functions

def R_matrix(f,d): #Determines the transfer/refraction matrices for a thick lens with focal length f and length d
    n_s=1 #index of refraction of free space
    n_l=d_lens*f/(H1*(2*f-H1))#Effective index of refraction of the lens, derived using thick lens relations
    R_1=(d_lens*f-2*f*H1+H1**2)/H1 #Effective radius of curvature of the front side, derived using thick lens relations. 
    D_1=(n_l-n_s)/R_1
    R_2=-R_1 #Due to lens symmetry, the back radius of curvature must be the negative of the front radius of curvature
    D_2=(n_s-n_l)/R_2
    refract_matrix_1=np.array([[1,0],[-D_1/n_l, n_s/n_l]]) #The refraction matrix of the ray entering the front of the lens
    translation_matrix=T_matrix(d_lens) #translation matrix from the ray moving a distance d_l within the lens
    refract_matrix_2=np.array([[1,0],[-D_2/n_s, n_l/n_s]]) #The refraction matrix of the ray exiting the back of the lens
    thick_lens_matrix=np.dot(refract_matrix_2, np.dot(translation_matrix,refract_matrix_1)) #matrix containing the net result experienced by the ray
    return [refract_matrix_1,translation_matrix,refract_matrix_2,thick_lens_matrix]

def T_matrix(d): #The translation matrix of a ray travelling through space across an axial distance of d
    translation_matrix=np.array([[1, d], [0,1]])
    return translation_matrix


def ray_to_plot_array(x_array,ray): #Given an array of x values for plotting, returns the corresponding y value array
    y_array=[]
    for i in range(len(x_array)):
        translated_ray=np.dot(T_matrix(x_array[i]-x_array[0]),ray) #Finds the ray vector after it is translated by a axial distance of x_array[i]
        y=translated_ray[0]
        y_array.append(y)
    return np.array(y_array)

def image_distance(d_o,f): #Determines the image distance given the object distance and the focal length of the thick lens
    #The object distance will be defined as the distance between the source and the first principal plane
    #The image distance will be defined as the distance between the second principal plane and the image
    d_i=f**2/(d_o-f) + f
    return d_i

def magnification(d_o,f): #determines the magnification after passing through a thick lens with focal length f.
    d_i=image_distance(d_o,f) #determines the image distance using the thick lens equation
    M=-d_i/d_o
    return M


#Ray Vector Calculations
lens_1_enter_ray=np.dot(T_matrix(d1),initial_ray) #The ray vector upon arriving at the front electrode of lens 1
lens_1_passing_ray1=np.dot(R_matrix(f1,d_lens)[0],lens_1_enter_ray)
lens_1_passing_ray2=np.dot(R_matrix(f1,d_lens)[1],lens_1_passing_ray1)
lens_1_exit_ray=np.dot(R_matrix(f1,d_lens)[2],lens_1_passing_ray2) #The ray vector upon exiting the back electrode of lens 1

lens_2_enter_ray=np.dot(T_matrix(d2-(d1+d_lens)),lens_1_exit_ray) 
lens_2_passing_ray1=np.dot(R_matrix(f2,d_lens)[0],lens_2_enter_ray)
lens_2_passing_ray2=np.dot(R_matrix(f2,d_lens)[1],lens_2_passing_ray1)
lens_2_exit_ray=np.dot(R_matrix(f2,d_lens)[2],lens_2_passing_ray2)

lens_3_enter_ray=np.dot(T_matrix(d3-(d2+d_lens)),lens_2_exit_ray) 
lens_3_passing_ray1=np.dot(R_matrix(f3,d_lens)[0],lens_3_enter_ray)
lens_3_passing_ray2=np.dot(R_matrix(f3,d_lens)[1],lens_3_passing_ray1)
lens_3_exit_ray=np.dot(R_matrix(f3,d_lens)[2],lens_3_passing_ray2)

lens_4_enter_ray=np.dot(T_matrix(d4-(d3+d_lens)),lens_3_exit_ray) 
lens_4_passing_ray1=np.dot(R_matrix(f4,d_lens)[0],lens_4_enter_ray)
lens_4_passing_ray2=np.dot(R_matrix(f4,d_lens)[1],lens_4_passing_ray1)
lens_4_exit_ray=np.dot(R_matrix(f4,d_lens)[2],lens_4_passing_ray2)


#Plotting Ray Tracing

plt.figure()

plot_x_array_1=np.linspace(0,d1,num=50) #array of x values used for plotting the ray entering lens 1
plot_y_array_1=ray_to_plot_array(plot_x_array_1,initial_ray) #array of y values used for plotting the ray entering lens 1
plt.plot(plot_x_array_1,plot_y_array_1,'r-')

plot_x_lens_1_array=np.linspace(d1,d1+d_lens,num=20) #Ray travelling within lens 1
plot_y_lens_1_array=ray_to_plot_array(plot_x_lens_1_array,lens_1_passing_ray1)
plt.plot(plot_x_lens_1_array,plot_y_lens_1_array,'r-')

plot_x_lens_1_front=np.linspace(d1,d1,num=20) #array used for plotting out the front electrode of lens 1
plot_x_lens_1_back=np.linspace(d1+d_lens,d1+d_lens,num=20) #array used for plotting out the back electrode of lens 1
plot_y_lens_1=np.linspace(-0.5*d1,0.5*d1,num=len(plot_x_lens_1_front))
plt.plot(plot_x_lens_1_front,plot_y_lens_1,'b-') #Draws a line representing the first lens
plt.plot(plot_x_lens_1_back,plot_y_lens_1,'b-')

plot_x_array_2=np.linspace(d1+d_lens,d2,num=50) #array of x values used for plotting the ray entering lens 2
plot_y_array_2=ray_to_plot_array(plot_x_array_2,lens_1_exit_ray) #array of y values used for plotting the ray entering lens 2
plt.plot(plot_x_array_2,plot_y_array_2, 'r-')

plot_x_lens_2_front=np.linspace(d2,d2,num=20)
plot_x_lens_2_back=np.linspace(d2+d_lens,d2+d_lens,num=20)
plot_y_lens_2=np.linspace(-0.5*d1,0.5*d1,num=len(plot_x_lens_2_front))
plt.plot(plot_x_lens_2_front,plot_y_lens_2,'b-')
plt.plot(plot_x_lens_2_back,plot_y_lens_2,'b-')

plot_x_lens_2_array=np.linspace(d2,d2+d_lens,num=20) #Ray travelling within lens 2
plot_y_lens_2_array=ray_to_plot_array(plot_x_lens_2_array,lens_2_passing_ray1)
plt.plot(plot_x_lens_2_array,plot_y_lens_2_array,'r-')

plot_x_array_3=np.linspace(d2+d_lens,d3,num=50) 
plot_y_array_3=ray_to_plot_array(plot_x_array_3,lens_2_exit_ray)
plt.plot(plot_x_array_3,plot_y_array_3, 'r-')

plot_x_lens_3_front=np.linspace(d3,d3,num=20)
plot_x_lens_3_back=np.linspace(d3+d_lens,d3+d_lens,num=20)
plot_y_lens_3=np.linspace(-0.5*d1,0.5*d1,num=len(plot_x_lens_3_front))
plt.plot(plot_x_lens_3_front,plot_y_lens_3,'b-')
plt.plot(plot_x_lens_3_back,plot_y_lens_3,'b-')

plot_x_lens_3_array=np.linspace(d3,d3+d_lens,num=20) #Ray travelling within lens 3
plot_y_lens_3_array=ray_to_plot_array(plot_x_lens_3_array,lens_3_passing_ray1)
plt.plot(plot_x_lens_3_array,plot_y_lens_3_array,'r-')

plot_x_array_4=np.linspace(d3+d_lens,d4,num=50) 
plot_y_array_4=ray_to_plot_array(plot_x_array_4,lens_3_exit_ray)
plt.plot(plot_x_array_4,plot_y_array_4, 'r-')

plot_x_lens_4_front=np.linspace(d4,d4,num=20)
plot_x_lens_4_back=np.linspace(d4+d_lens,d4+d_lens,num=20)
plot_y_lens_4=np.linspace(-0.5*d1,0.5*d1,num=len(plot_x_lens_4_front))
plt.plot(plot_x_lens_4_front,plot_y_lens_4,'b-')
plt.plot(plot_x_lens_4_back,plot_y_lens_4,'b-')

plot_x_lens_4_array=np.linspace(d4,d4+d_lens,num=20) #Ray travelling within lens 3
plot_y_lens_4_array=ray_to_plot_array(plot_x_lens_4_array,lens_4_passing_ray1)
plt.plot(plot_x_lens_4_array,plot_y_lens_4_array,'r-')

plot_x_array_5=np.linspace(d4+d_lens,d5,num=50) 
plot_y_array_5=ray_to_plot_array(plot_x_array_5,lens_4_exit_ray)
plt.plot(plot_x_array_5,plot_y_array_5, 'r-')

plt.xlabel('distance along optical axis (m)')
plt.ylabel('distance from optical axis (m)')
plt.title('Nano-Mi Thick Lens Approximate Ray Tracing')
plt.show()

'''Illumination System Focal Length Optimization and Magnification Calculations '''

desired_image_distance_3=d_sample-(d3+H2) #The image distance needed for the third lens to form a focused, demagnified image on the sample

def objective_illumination(f): #This is the function that is to be minimized for the illumination system (the magnification of the illumination system)
    #This assumes that we have 3 lenses in the illumination system.
    M1=magnification(d1+H1,f[0])
    image_distance_1=image_distance(d1+H1,f[0])
    object_distance_2=(d2+H1)-(d1+H2+image_distance_1)
    M2=magnification(object_distance_2,f[1])
    image_distance_2=image_distance(object_distance_2,f[1])
    object_distance_3=(d3+H1)-(d2+H2+image_distance_2)
    M3=magnification(object_distance_3,f[2])
    total_magnification=abs(M1*M2*M3)
    return total_magnification #This is the quantity that is to be minimized for the 3 lens system

def constraint_illumination(f): #constrains the third image distance in the illumination system to be equal to its desired value
    #This constraint is so that a demagnified image is formed at the sample.
    image_distance_1=image_distance(d1+H1,f[0])
    object_distance_2=(d2-(d1+H2))-image_distance_1
    image_distance_2=image_distance(object_distance_2,f[1])
    object_distance_3=(d3-(d2+H2))-image_distance_2
    image_distance_3=image_distance(object_distance_3,f[2])
    return abs(image_distance_3-desired_image_distance_3) #This line constrains the difference between the image distance of lens 3 and the distance between lens 3 and the sample to be equal to 0


cons_illumination={'type' : 'eq', 'fun' : constraint_illumination} #Constraint dictionary
cons_illumination= [cons_illumination] #list of constraint dictionaries to be inputted into the minimize function
min_focal_length=6e-3 #minimum allowed focal length; approximately what the Nano-Mi's lenses' minimum focal length will be
max_focal_length=1e-1 #maximum allowed focal length; when focal length is too high, spherical aberration tends to be greater 
bound=(min_focal_length,max_focal_length) #Bounds allowed for focal lengths
array_of_guess=np.linspace(min_focal_length,max_focal_length/4,num=6) #initial guesses for the minimize function.


list_of_illumination_solution=[]
list_of_illumination_magnification=[]

for i in range(len(array_of_guess)): #iterates through guesses for lens 1
    for j in range(len(array_of_guess)): #iterates through guesses for lens 2
        for k in range(len(array_of_guess)): #iterates through guesses for lens 3
            illumination_system_solution=minimize(objective_illumination,[array_of_guess[i],array_of_guess[j],array_of_guess[k]],method='SLSQP',bounds=(bound,bound,bound),constraints=cons_illumination,options={'ftol':1e-4,'maxiter':5000, 'eps':1e-6})
            f1_opt=illumination_system_solution.x[0]
            f2_opt=illumination_system_solution.x[1]
            f3_opt=illumination_system_solution.x[2]
            M1=magnification(d1+H1,f1_opt)
            image_distance_1=image_distance(d1+H1,f1_opt)
            object_distance_2=(d2-(d1+H2)-image_distance_1)
            M2=magnification(object_distance_2,f2_opt)
            image_distance_2=image_distance(object_distance_2,f2_opt)
            object_distance_3=(d3-(d2+H2))-image_distance_2
            M3=magnification(object_distance_3,f3_opt)
            image_distance_3=image_distance(object_distance_3,f3_opt)
            total_magnification_illumination=abs(M1*M2*M3)
            if illumination_system_solution.success==True and abs(image_distance_3-desired_image_distance_3)<=1e-2*desired_image_distance_3:
                list_of_illumination_solution.append([f1_opt,f2_opt,f3_opt])
                list_of_illumination_magnification.append(total_magnification_illumination)
                

list_of_illumination_magnification=np.array(list_of_illumination_magnification)
list_of_illumination_solution=np.array(list_of_illumination_solution)
if np.shape(list_of_illumination_solution[0])==0:
    print('No optimal solution found for three lens system')
else:
    print("Gun-Sample Magnification:"+str(np.min(list_of_illumination_magnification)))
    print("Focal Lengths Needed:"+str(list_of_illumination_solution[list_of_illumination_magnification.argmin()]))
    
    
'''Imaging System Focal Length Optimization and Magnification Calculations '''
desired_image_distance_5=d_screen-(d8+H2) #The image distance needed for the 8th lens to form a focused, magnified image on the screen

def objective_imaging(f): #This is the function that is to be minimized for the imaging system (the negative of the magnification of the illumination system)
    #This assumes that we have 5 lenses in the imaging system.
    object_distance_1=(d4+H1-d_sample)
    M1=magnification(object_distance_1,f[0])
    image_distance_1=image_distance(object_distance_1,f[0])
    object_distance_2=(d5+H1)-(d4+H2+image_distance_1)
    M2=magnification(object_distance_2,f[1])
    image_distance_2=image_distance(object_distance_2,f[1])
    object_distance_3=(d6+H1)-(d5+H2+image_distance_2)
    M3=magnification(object_distance_3,f[2])
    image_distance_3=image_distance(object_distance_3,f[2])
    object_distance_4=(d7+H1)-(d6+H2+image_distance_3)
    M4=magnification(object_distance_4,f[3])
    image_distance_4=image_distance(object_distance_4,f[3])
    object_distance_5=(d8+H1)-(d7+H2+image_distance_4)
    M5=magnification(object_distance_5,f[4])
    total_magnification=-np.abs(M1*M2*M3*M4*M5)
    
    return total_magnification #This is the quantity that is to be minimized for the 3 lens system

def constraint_imaging(f): #constrains the third image distance to be equal to its desired value (creates a magnified and focused image on the screen)
    object_distance_1=(d4+H1-d_sample)
    image_distance_1=image_distance(object_distance_1,f[0])
    object_distance_2=(d5+H1)-(d4+H2+image_distance_1)
    image_distance_2=image_distance(object_distance_2,f[1])
    object_distance_3=(d6+H1)-(d5+H2+image_distance_2)
    image_distance_3=image_distance(object_distance_3,f[2])
    object_distance_4=(d7+H1)-(d6+H2+image_distance_3)
    image_distance_4=image_distance(object_distance_4,f[3])
    object_distance_5=(d8+H1)-(d7+H2+image_distance_4)
    image_distance_5=image_distance(object_distance_5,f[4])
    return np.abs(image_distance_5-desired_image_distance_5) #This line constrains the difference between the image distance of lens 5 and the distance between lens 5 and the sscreen to be equal to 0

cons_imaging={'type' : 'eq', 'fun' : constraint_imaging} #Constraint dictionary
cons_imaging= [cons_imaging] #list of constraint dictionaries to be inputted into the minimize function
min_focal_length=6e-3 #minimum allowed focal length; approximately what the Nano-Mi's lenses' minimum focal length will be
max_focal_length=1e-1 #maximum allowed focal length; when focal length is too high, spherical aberration tends to be greater 
bound=(min_focal_length,max_focal_length) #Bounds allowed for focal lengths
array_of_guess=np.linspace(min_focal_length,max_focal_length/12,num=12) #initial guesses for the minimize function.

list_of_imaging_solution=[]
list_of_imaging_magnification=[]

for i in range(len(array_of_guess)): #iterates through guesses for lens 4,5,6
    for j in range(len(array_of_guess)): #iterates through guesses for lens 7
        for k in range(len(array_of_guess)): #iterates through guesses for lens 8
            imaging_system_solution=minimize(objective_imaging,[array_of_guess[i],array_of_guess[i],array_of_guess[i],array_of_guess[j],array_of_guess[k]],method='SLSQP',bounds=(bound,bound,bound,bound,bound),constraints=cons_imaging,options={'ftol':1e-5,'maxiter':20000, 'eps':1e-10})
            f4_opt=imaging_system_solution.x[0]
            f5_opt=imaging_system_solution.x[1]
            f6_opt=imaging_system_solution.x[2]
            f7_opt=imaging_system_solution.x[3]
            f8_opt=imaging_system_solution.x[4]
            object_distance_1=(d4+H1-d_sample)
            M1=magnification(object_distance_1,f4_opt)
            image_distance_1=image_distance(object_distance_1,f4_opt)
            object_distance_2=(d5+H1)-(d4+H2+image_distance_1)
            M2=magnification(object_distance_2,f5_opt)
            image_distance_2=image_distance(object_distance_2,f5_opt)
            object_distance_3=(d6+H1)-(d5+H2+image_distance_2)
            M3=magnification(object_distance_3,f6_opt)
            image_distance_3=image_distance(object_distance_3,f6_opt)
            object_distance_4=(d7+H1)-(d6+H2+image_distance_3)
            M4=magnification(object_distance_4,f7_opt)
            image_distance_4=image_distance(object_distance_4,f7_opt)
            object_distance_5=(d8+H1)-(d7+H2+image_distance_4)
            M5=magnification(object_distance_5,f8_opt)
            image_distance_5=image_distance(object_distance_5,f8_opt)
            total_magnification_imaging=abs(M1*M2*M3*M4*M5)
                    
            if imaging_system_solution.success==True and abs(image_distance_5-desired_image_distance_5)<=1e-3*desired_image_distance_5:
                list_of_imaging_solution.append([f4_opt,f5_opt,f6_opt,f7_opt,f8_opt])
                list_of_imaging_magnification.append(total_magnification_imaging)

list_of_imaging_magnification=np.array(list_of_imaging_magnification)
list_of_imaging_solution=np.array(list_of_imaging_solution)
if np.shape(list_of_imaging_solution[0])==0:
    print('No optimal solution found for imaging system')
else:
    print("Sample-Screen Magnification:"+str(np.max(list_of_imaging_magnification)))
    print("Focal Lengths:"+str(list_of_imaging_solution[list_of_imaging_magnification.argmax()]))
