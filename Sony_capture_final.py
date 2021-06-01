#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:43:08 2020

@author: karan kumar




  [Sony_Capture_Final.py] is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    [Sony_Capture_Final.py] is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Sony_Capture_Final.py  If not, see <https://www.gnu.org/licenses/>.

See also [github NanoMi project name] / nanomi.org

This Software is built around the Sony Alpha6000 Camera, using the gphoto library  it automatically takes a photo
and processes it into imagej

FFT_macro.ijm  is a marco that applies FFT to the photo provided 


"""
#NOTE THIS CODE ONLY WORKS ON LINUX SYSTEMS

from time import sleep
from datetime import datetime #read the date and time from computer 
from sh import gphoto2 as gp 
import sys

#sh allows us to use any program like a python function
import signal, os, subprocess


#first want to end gphoto process that initally starts when we turn on camera
#this way the python program can take and use the camera
def endgphoto2():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    
    #find gphoto and end it
    for line in out.splitlines():
        if b'gphoto2' in line:
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

            
# dating each file
shot_date = datetime.now().strftime('%Y-%m-%d') #get the computer date convert to a string
shot_time =datetime.now().strftime('%Y-%m-%d %H:%M:%S')# same as above now with time
#main name of file 
picID = "Sony A6000 Test"
image_save = picID + shot_time + '.jpeg' #this is the name of the image

#clear the SD this folder will be different for every camera
# use gphoto2 --list-folders to find the save folder
# for the sony 6000 in PC remote mode the only accesible folder is '/'

clearCommand =["--folder", "/", \
               "-R", "--delete-all-files"] # caution this will delete every file if you run this 

#try first with camera press or automate later with 
#--trigger-capture
cameraTrigger = ['--capture-image-and-download', '--filename' ,image_save ] # camera takes photo automatically and saves photo by date
#terminaltrigger = ['--capture-image-and-download --filename ' +image_save+'| imagej ] 
#terminalTrigger for future use maybe it can run the code faster                                                                        
downloadCommand = ["--get-all-files"] #in V4 the camera get all the files in directory '/'
                                                #and download to the computer
                                                
folder_name = picID + shot_date # save the folder by project and date 

save_location = '/home/admin/Desktop/gphoto/images' + folder_name # different if on another computer
save_directory ='/home/admin/Desktop/gphoto/images'

def createSaveFolder():
    try:
        os.mkdir(save_location)
        print('new folder created' , folder_name)
    except:
        print("Failed to save new folder")
        print("check and verify folder wasn't already made")
        os.chdir(save_location)

#this above will make folders based on date, if the folder was already created then 
#photos should go to the already created folder
        
def captureImage(): 
    gp(cameraTrigger)
    #sleep(3)
    gp(downloadCommand)
    gp(clearCommand)
    return True

                
def runImagej(): # maybe run with os.pipe
        cmd = ['imagej', '-macro' , '/home/admin/Desktop/gphoto/FFT_macro.ijm']
        process1 = subprocess.Popen(cmd)
        
endgphoto2() 
#gp(clearCommand)
def savephoto(): #take the photo and return true to keep taking photos
    while True:
        createSaveFolder()
        captureImage()
        return True
    
savephoto()
runImagej()

   


#quick example of opening imagej

#next step open imageJ run an FFT


#known bug
#first picutre will not save in created folder
 
