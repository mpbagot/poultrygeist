#!/usr/bin/env python3
'''

Main File/Menu launcher for PoultryGeist

'''
import math
import random
import os
from game import Application

import pygame
from pygame.locals import *
# Initialise the sound system
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
# Load the sound and set it to loop
pygame.mixer.music.load('resources/generic/sounds/menu_music.mp3')

pygame.mixer.music.play(-1)
# Set the window height
(width, height) = (450, 500)
screen = pygame.display.set_mode((width, height))#pygame.FULLSCREEN)
video = True

play = False

# Initialise the game settings
options = {'audio': 'on', 'resolution': '720p', 'quality':'low'}

selectionint = 1
scene = 0


def button(str, coordx, coordy, buttonint):
   '''
   Draw a button to the screen
   '''
   # Initialise a font object
   font = pygame.font.Font(None,30)
   # Render a rect object
   buttontext = font.render(str, 1,(255,255,255))
   # Set the rect coordinates
   a = [coordx-buttontext.get_rect().width//2, coordy, buttontext.get_rect().width+50, 50]
   # Draw the background rectangle of the button
   pygame.draw.rect(screen, BLACK, a)
   if buttonint == selectionint :
      pygame.draw.rect(screen, RED, a)
   # Blit the text on the top of the button
   screen.blit(buttontext, (coordx-buttontext.get_rect().width//2+25, coordy+15))

BLACK = (0, 0, 0)
RED = (255, 0, 0)
# Load the background image
background_image = pygame.image.load("resources/generic/chicken.jpg").convert()

running = True

while running:

   # Blit the background image to screen
   screen.blit(background_image, [0, 0])

   if scene == 0:
      # Display the Main menu buttons
      button("Play", 200, 100, 1)
      button("Options", 200, 200, 2)
      button("Exit", 200, 300, 3)
      # Stop the selectionint from overflowing
      if selectionint >=3:
         selectionint =3

   if scene == 1:
      # Display the Options menu buttons
      button("Sound: "+options.get('audio').upper(), 200, 85, 1)
      button("Resolution: "+options.get('resolution'), 200, 185, 2)
      button("Quality: "+options.get('quality').title(), 200, 285, 3)
      button("Back", 200, 385, 4)
      if selectionint >=4:
         selectionint =4

   for event in pygame.event.get():
      if scene == 0:
         if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
               # Iterate the selected button
               selectionint-=1
            elif event.key in [pygame.K_RETURN]:
               if selectionint == 1:
                  # Play the game
                  running = False
                  video = False
                  app = Application(options.get('quality'))
                  app.loadSettings(options)
                  pygame.display.quit()
                  pygame.quit()
                  app.run()
               elif selectionint == 3:
                  # Exit the game
                  running = False
                  video = False
                  pygame.display.quit()
                  pygame.quit()
               elif selectionint == 2:
                  # Open the options menu
                  scene = 1

            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                selectionint+=1

      elif scene == 1:
         if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
               selectionint-=1
            elif event.key in [pygame.K_RETURN]:
               if selectionint == 1:
                  #sound toggle thing here
                  options['audio'] = 'off' if options['audio'] == 'on' else 'on'
                  pygame.mixer.music.set_volume(int(not pygame.mixer.music.get_volume()))
               elif selectionint == 2:
                  options['resolution'] = '1080p' if options['resolution'] == '720p' else '720p'
               elif selectionint == 3:
                  options['quality'] = 'super-low'
               elif selectionint == 4:
                  scene = 0

            elif event.key in [pygame.K_s, pygame.K_DOWN]:
               selectionint+=1

      if selectionint <=1:
         selectionint =1

   if video == True:
      pygame.display.flip()
