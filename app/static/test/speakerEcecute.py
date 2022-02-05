# import required module

#import playsound
#import pdb; pdb.set_trace() 
# for playing note.wav file
#playsound.playsound('success.wav')
#print('playing sound using  playsound')

import pygame
from pygame import mixer
mixer.init()


#play with queue
QUEUE = False


if(QUEUE):
    
    pygame.mixer.music.load("success.wav")
    #sound1.play(2)
    pygame.mixer.music.play(2)
    #while pygame.mixer.music.get_busy() == True:
	#continue
    pygame.mixer.music.queue("fail.wav")
    while pygame.mixer.music.get_busy() == True:
        continue

else:
    pygame.mixer.music.load("success.wav")
    pygame.mixer.music.play(2)
    while pygame.mixer.music.get_busy() == True:
        continue

    pygame.mixer.music.load("fail.wav")
    pygame.mixer.music.play(2)
    while pygame.mixer.music.get_busy() == True:
        continue
