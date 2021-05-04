import pygame
import pygame.camera
from pygame.locals import *
import time


class Capture(object):
    def __init__(self):
        self.size = (640,480)
        # create a display surface. standard pygame stuff
        self.display = pygame.display.set_mode(self.size, 0)

        # this is the same as what we saw before
        self.clist = pygame.camera.list_cameras()
        print(self.clist)
        if not self.clist:
            raise ValueError("Sorry, no cameras detected.")
        self.cam = pygame.camera.Camera(self.clist[0], self.size)
        self.cam.start()

        # create a surface to capture to.  for performance purposes
        # bit depth is the same as that of the display surface.
        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

    def get_and_flip(self):
        # if you don't want to tie the framerate to the camera, you can check
        # if the camera has an image ready.  note that while this works
        # on most cameras, some will never return true.
        #if self.cam.query_image():
        #    print('query triggered')
        self.snapshot = self.cam.get_image()

        # blit it to the display surface.  simple!
        self.display.blit(self.snapshot, (0,0))
        pygame.display.flip()
        pygame.display.update()

    def main(self):
        going = True
        while going:
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    # close the camera safely
                    self.cam.stop()
                    going = False
                    print('Closed by user')

            self.get_and_flip()


pygame.init()
pygame.camera.init()

pygame.display.init()

'''
cam = pygame.camera.Camera("/dev/video0",(640,480))
cam.start()
image = cam.get_image()
cam.stop()

displayer = pygame.display.set_mode((640,480), 0)
#displayer.fill((255,255,255))
displayer.blit(image,(0,0))
pygame.display.update()
time.sleep(1)

camlist = pygame.camera.list_cameras()
#print(camlist)
if camlist:
    cam = pygame.camera.Camera(camlist[0],(640,480))
    cam.set_controls(hflip = True, vflip = False)
print (cam.get_controls())

'''
myCapture=Capture()
myCapture.main()
