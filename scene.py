# Import the Panda3D Python modules
from direct.task.Task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor

# Import the Panda3D C++ modules
from panda3d.core import TransparencyAttrib, Vec3, Fog, LPoint3, VBase4
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.bullet import BulletWorld
from panda3d.ai import *

# Import the RenderPipeline modules
from rpcore.util.movement_controller import MovementController

from entity import *

class Scene:
	'''
	Holds all of the required details about a scene of the game. Including tasks
	and render tree for Panda3D.
	'''
	def addObject(self, modelName, pos=(0,0,0), scale=(1,1,1), instanceTo=None, isActor=False, key=None, anims={}, parent=None):
		'''
		Adds a model to the Scenes render tree
		'''
		# Automatically adjust the model path
		modelName = 'resources/{}/'.format(self.app.quality)+modelName

		# Check if the model is being instanced to an existing model
		if instanceTo is None:
			# Load the model into the engine
			model = self.loadModel(modelName, isActor, anims)
			# Set the position and scale of the model
			model.setPos(*pos)
			model.setScale(*scale)
			# Parent the model to either the render tree or the parent (if applicable)
			model.reparentTo(self.renderTree if parent is None else self.models.get(parent))
		else:
			# If the model is being instanced to an existing model
			model = self.addInstance(pos, scale, instanceTo)

		# Add the model to the scenes model dictionary
		self.models[key if key is not None else len(self.models)] = model

		# If the game is running under the RenderPipeline, initialise the model
		if self.app.quality != 'super-low' and modelName.endswith('.bam'):
			self.app.render_pipeline.prepare_scene(model)

		# Return the model nodepath
		return model

	def addInstance(self, pos, scale, instanceTo):
		'''
		Adds an Instance of the chosen model to the scene.
		'''
		# Create a new empty node and attach it to the render tree
		model = self.renderTree.attachNewNode("model_placeholder")

		# Set the position and scale of the model
		model.setPos(*pos)
		model.setScale(*scale)

		# Instance the model to the chosen object
		self.models[instanceTo].instanceTo(model)

		# Return the nodepath
		return model

	def loadModel(self, modelName, isActor, anims):
		'''
		Load the model into the engine and return it.
		'''
		# Check if the model is an Actor or static model
		if isActor:
			# Add the model as an Actor with the required animations
			return Actor(modelName, anims)
		else:
			# Add the model as a static model
			return self.loader.loadModel(modelName)

	def initScene(self):
		'''
		A placeholder function for running events when the scene is first loaded
		'''
		pass

class MenuScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		self.app = app
		self.isPlayerControlled = False
		self.models = {}
		self.loader = app.loader
		self.renderTree = app.render

	def eventRun(self, task):
		return Task.cont


class IntroScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		self.app = app
		self.isPlayerControlled = False
		self.models = {}
		self.loader = app.loader
		self.renderTree = app.render

		# Add the ground model
		self.addObject("ground.bam".format(app.quality), scale=(3.6,3.6,2), key="ground")

		# Add the barn
		barnModel = self.addObject("barn.bam".format(app.quality), scale=(1, 1, 1))

		# Create a corn model and add it in the bottom corner
		self.addObject("corn.egg".format(app.quality), pos=(-62, -62, 0), scale=(1, 1, 1.3), key="corn")

		# Iterate a 25x25 square for the corn
		for x in range(25):
			for z in range(25):
				# Use amazing maths skills to create a 'lollypop' shape cutout
				if (x-12)**2+(z-12)**2 > 25 and (abs(x-12) > 1 or z > 12):
					# Add a corn instance to the scene
					self.addObject("corn.egg".format(app.quality), (x*5, z*5, 0), instanceTo="corn")

		# Add the AI World
		self.AIworld = AIWorld(self.renderTree)

		# Add generic linear fog on super-low quality mode
		if app.quality == 'super-low':
			fog = Fog("corn_fog")
			# Set the fog colour
			fog.setColor(0.8,0.8, 0.8)
			# Set the density of the fog
			fog.setExpDensity(0.005)
			# Add the fog to the scene
			self.renderTree.setFog(fog)
			# Set the scene's background colour
			base.setBackgroundColor(0.635, 0.454, 0.494)
			# Add the sun lamp spotlight
			# light = DirectionalLight('light')
			# light.setColor(VBase4(1, 1, 1, 1))
			# lightNodePath = render.attachNewNode(light)
			# lightNodePath.setPos(10, -80, 7)
			# lightNodePath.lookAt(barnModel)
			# self.renderTree.setLight(lightNodePath)

	def eventRun(self, task):
		'''
		Run a non-stop check for the completion of the motion path
		'''
		if self.app.controller and self.app.controller.clock_obj.get_frame_time() > self.app.controller.curve_time_end:
			# delete the motion controller
			self.app.controller = None
			# Load the first scene of the gameplay
			self.app.sceneMgr.loadScene(SceneOne(self.app))
		self.AIworld.update()
		return Task.cont

	def initScene(self):
		'''
		Set up the movement controller and begin the motion path.
		'''
		# Make the motion path
		mopath = (
			(Vec3(0, -63, 4), Vec3(0, 0, 0)),
			(Vec3(0, -63, 4), Vec3(0, 0, 0)),
			(Vec3(0, -63, 4), Vec3(0, 0, 0)),
			(Vec3(0, -56, 4), Vec3(-90, -10, 0)),
			(Vec3(0, -52, 4), Vec3(0, -70, 0)),
			(Vec3(0, -46, 4), Vec3(90, 0, 20)),
			(Vec3(0, -40, 4), Vec3(0, 0, 0)),
			(Vec3(0, -30, 4), Vec3(0, 0, 0)),
			(Vec3(0, -20, 4), Vec3(0, 0, 0)),
			(Vec3(5, -10, 4), Vec3(-40, 0, -5)),
			(Vec3(5, -9, 4), Vec3(-190, 0, 0)),
			(Vec3(5, -4, 4), Vec3(-190, 0, -5)),
			(Vec3(4, 0, 0.5), Vec3(-190, 80, 0))
			)
		# Create the controller for movement
		self.app.controller = MovementController(self.app)
		# Set the initial position
		self.app.controller.set_initial_position(Vec3(0, -63, 4), Vec3(0, 0, 0))
		# Run the setup on the movement controller
		self.app.controller.update_task = self.app.addTask(nullTask, 'meh')
		# Play the pre-defined motion path
		self.app.controller.play_motion_path(mopath, 0.8)
		# Remove the player movement controls
		self.app.taskMgr.remove(self.app.controller.update_task)

		# Unhide the 2d overlay.
		self.app.aspect2d.show()
		self.app.render2d.show()

		# set up the black image
		self.fadeQuad = OnscreenImage(image='resources/generic/fade.png',pos=(-0.5, 0, 0), scale=(2, 1, 1))
		self.fadeQuad.setTransparency(TransparencyAttrib.MAlpha)

		# Add the fadein transition
		self.app.taskMgr.add(self.fadeIn, 'fade-task')

		# Add the two chickens
		self.chickenOne = Chicken(self, (20, -50, 0))
		self.chickenOne.aiChar.setMaxForce(30)
		self.chickenTwo = Chicken(self, (-20, -40, 0))
		self.chickenTwo.aiChar.setMaxForce(30)

		# Add them to the AI World
		self.AIworld.addAiChar(self.chickenOne.aiChar)
		self.AIworld.addAiChar(self.chickenTwo.aiChar)

		# Enable the pursue behaviour
		self.chickenOne.aiBehaviour.pursue(self.app.camera)
		self.chickenTwo.aiBehaviour.pursue(self.app.camera)

	def fadeIn(self, task):
		'''
		Fade in the scene by fading a big, black rectangle
		'''
		# If more than two seconds have passed then finish the task
		if task.time > 4:
			self.fadeQuad.destroy()
			return
		# Get the alpha of the square
		alpha = task.time / 4
		# set the alpha level on the rectangle
		self.fadeQuad.setAlphaScale(1-alpha)
		# print(dir(self.fadeQuad))
		return Task.cont

class SceneOne(Scene):
	def __init__(self, app):
		self.app = app
		self.isPlayerControlled = True
		self.models = {}
		self.loader = app.loader
		self.renderTree = app.render

		# Add the AIWorld
		self.aiWorld = AIWorld(self.renderTree)

	def eventRun(self, task):
		self.aiWorld.update()
		return Task.cont

	def initScene(self):
		# Add the physics world and set the gravity on it
		self.bulletWorld = BulletWorld()
		self.bulletWorld.setGravity(Vec3(0, 0, -9.81))


def nullTask(task):
	return Task.cont
