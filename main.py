#!/usr/bin/env python3
"""

PoultryGeist
You'll Be Running Chicken

"""
# Import the Python Panda3D modules
from direct.showbase.ShowBase import ShowBase
from direct.filter.CommonFilters import *
from direct.task.Task import Task

# Import the main render pipeline class
from rpcore import RenderPipeline

import sys
from time import sleep
import math

#Import the C++ Panda3D modules
from panda3d.core import WindowProperties, AntialiasAttrib
from panda3d.core import KeyboardButton, load_prc_file_data
from panda3d.core import LVector3

#Import the external files from this project
from scene import *

class Application(ShowBase):
	'''
	The default Application class which holds the code for
	Panda3D to run the game
	'''
	def __init__(self):
		# Set the model quality, (super-low, low or high)
		self.quality = "high"
		print("[>] PoultryGeist:\t      Setting Model Resolution to {}".format(
		self.quality.upper()))

		# Run the standard Showbase init if running in super-low resolution mode
		if self.quality == 'super-low':
			super().__init__()

		#Modify the Panda3D config on-the-fly
		#In this case, edit the window title
		load_prc_file_data("", """window-title PoultryGeist
								  threading-model /Draw
								  multisamples 2
								  framebuffer-multisample 1
							   """)

		# Set the window size
		self.width, self.height = (800, 600)

		# Initialise the movement controller
		self.controller = None

		# Do some stuff if the game is running at normal or high resolution
		if self.quality != 'super-low':
			# Construct and create the pipeline
			self.render_pipeline = RenderPipeline()
			self.render_pipeline.create(self)
			# Enable anti-aliasing for the game
			render.setAntialias(AntialiasAttrib.MAuto)
			# Set the time pipeline lighting simulation time
			self.render_pipeline.daytime_mgr.time = "20:15"

		# Turn off normal mouse controls
		self.disableMouse()

		# Hide the cursor
		props = WindowProperties()
		props.setCursorHidden(True)
		props.setMouseMode(WindowProperties.M_relative)
		# Lower the FOV to make the game more difficult
		self.win.requestProperties(props)
		self.camLens.setFov(60)

		# Register the buttons for movement
		# TODO remove this and overhaul the button handling
		self.w_button = KeyboardButton.ascii_key('w'.encode())
		self.s_button = KeyboardButton.ascii_key('s'.encode())

		self.switch_button = KeyboardButton.ascii_key('p'.encode())

		# Initialise the SceneManager
		self.sceneMgr = SceneManager(self)

		# Add the sceneMgr events to run as a task
		taskMgr.add(self.sceneMgr.runSceneTasks, "scene-tasks")

	def move(self, forward, dir, elapsed):
		'''
		Move the camera forward or backwards
		For testing ONLY at the moment
		'''
		if forward:
			self.sceneMgr.focus += dir * elapsed * 30
		else:
			self.sceneMgr.focus -= dir * elapsed * 30
		# Set the position of the camera based on the direction
		self.camera.setPos(self.sceneMgr.focus - (dir * 5))

class SceneManager:
	'''
	The SceneManager to handle the events and tasks of each scene as well as
	handle scene swapping.
	'''
	def __init__(self, app):
		self.app = app
		self.scene = None
		self.loadScene(MenuScene(app))

		# Set the current viewing target
		self.focus = LVector3(55, -55, 20)
		self.heading = 180
		self.pitch = 0
		self.mousex = 0
		self.mousey = 0
		self.last = 0
		self.mousebtn = [0, 0, 0]

	def loadScene(self, scene):
		'''
		Load a new scene into the game
		'''
		self.sceneFrame = 1
		# TODO Fix this to actually work
		# if self.scene:
		# 	for child in self.app.render.getChildren():
		# 		child.detachNode()
		# 		print(child)
		self.scene = scene
		self.app.render = self.scene.renderTree
		# for child in scene.renderTree.getChildren():
		# 	child.reparentTo(self.app.render)
		if self.app.quality == 'super-low':
			# set up auto shaders
			self.app.render.setShaderAuto()

	def runSceneTasks(self, task):
		'''
		Run the event update for the current scene
		'''
		if self.sceneFrame == 2:
			# Run the scene events immediately after loading the scene
			self.scene.initScene()

		if self.scene.isPlayerControlled:
			# Run the camera control task if the scene allows for it
			self.controlCamera(task)
		else:
			# Bob the camera aggresively if using a predetermined motion path
			self.bobCamera(task, 15)

		self.handleButtons(task)

		# Update the width and height of the window in case it gets resized
		self.app.width = self.app.win.getXSize()
		self.app.height = self.app.win.getYSize()

		# Iterate the current frame
		self.sceneFrame += 1
		# Store the frame time for the next loop
		self.last = task.time
		# Run the scenes standard events
		return self.scene.eventRun(task)

	def handleButtons(self, task):
		elapsed = task.time - self.last
		# Get a 3D vector of the camera's direction
		dir = self.app.camera.getMat().getRow3(1)
		# Alias the really long function to a short name
		is_down = base.mouseWatcherNode.is_button_down
		# Check for a w press and move forward
		if is_down(self.app.w_button):
			# Make the camera bob slightly
			self.app.move(True, dir, elapsed)
		# Check for an s press and move backwards
		if is_down(self.app.s_button):
			self.app.move(False, dir, elapsed)
		# Check for a scene switch and switch the scene
		if is_down(self.app.switch_button):
			self.loadScene(MenuScene(self.app) if isinstance(self.scene, IntroScene) else IntroScene(self.app))


	def controlCamera(self, task):
		'''
		Control the camera to move more nicely
		'''
		# Get the change in time since the previous frame
		elapsed = task.time - self.last
		# Get the cursor and X, Y position of it
		mousePos = self.app.win.getPointer(0)
		x = mousePos.getX()
		y = mousePos.getY()
		# Get the change in mouse position
		if self.app.win.movePointer(0, int(self.app.width/2), int(self.app.height/2)):
			# And set the heading and pitch accordingly
			self.heading = self.heading - (x - self.app.width//2) * 0.2
			self.pitch = self.pitch - (y - self.app.height//2) * 0.2

		# Limit the camera pitch
		if self.pitch < -75:
			self.pitch = -75
		if self.pitch > 75:
			self.pitch = 75
		# Rotate the camera accordingly
		self.app.camera.setHpr(self.heading, self.pitch, 0)
		# Get a 3D vector of the camera's direction
		dir = self.app.camera.getMat().getRow3(1)
		# If this is the first frame then set elapsed to 0
		if self.last == 0:
			elapsed = 0

		# TODO Dunno what this is for
		self.focus = self.app.camera.getPos() + (dir * 5)
		return Task.cont

	def bobCamera(self, task, magnitude=5, speed=4):
		'''
		Bob the camera up and down
		'''
		# Bob the head, because the camera is controlled automatically
		pitch = self.app.camera.getP() + math.sin(math.radians(task.time)*180*speed) * magnitude * ((task.time-self.last)/0.167)
		# Rotate the camera accordingly
		self.app.camera.setP(pitch)

# Run the application
Application().run()
