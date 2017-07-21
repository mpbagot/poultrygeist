# Import the Panda3D Python modules
from direct.task.Task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor

# Import the Panda3D C++ modules
from panda3d.core import *
# from panda3d.core import TransparencyAttrib, Vec3, Fog, LPoint3, VBase4, BitMask32
# from panda3d.core import AmbientLight, DirectionalLight
# from panda3d.core import WindowProperties,
from panda3d.physics import *
from panda3d.ai import *

# Import the RenderPipeline modules
from rpcore.util.movement_controller import MovementController

from copy import deepcopy

from entity import *
from player import *

class Scene:
	'''
	Holds all of the required details about a scene of the game. Including tasks
	and render tree for Panda3D.
	'''
	def addObject(self, modelName, pos=(0,0,0), scale=(1,1,1), instanceTo=None, isActor=False, key=None, anims={}, parent=None, hasPhysics=False, collider=None):
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
			# If physics need to be enabled, parent the object below a physics actor node
			if hasPhysics:
				actorNode = ActorNode("physics-node-"+modelName)
				# Parent to the chosen parent, either existing nodepath or the scene graph
				if parent is None:
					actorNodePath = self.renderTree.attachNewNode(actorNode)
				else:
					actorNodePath = self.models.get(parent).attachNewNode(actorNode)
				# Attach the actor to the physics manager
				self.app.physicsMgr.attachPhysicalNode(actorNode)
				# reparent the model to the actor node
				model.reparentTo(actorNodePath)
				colliderNodePath = self.addColliderNode(parent)
				if collider:
					colliderNodePath.node().addSolid(collider)
			else:
				# Parent the model to either the render tree or the parent
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

	def addColliderNode(self, parent=None):
		'''
		Add an empty colliderNode to the render tree
		'''
		if parent:
			return self.models.get(parent).attachNewNode(CollisionNode('cnode'))
		else:
			return self.renderTree.attachNewNode(CollisionNode('cnode'))

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
		A event hook method for running events when the scene is first loaded
		'''
		pass

	def exitScene(self):
		'''
		An event hook method for running events as the scene is exited
		'''
		pass

class MenuScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		'''
		Initialise and run any events BEFORE loading the scene
		'''
		self.app = app
		self.isPlayerControlled = False
		self.models = {}
		self.loader = app.loader
		self.renderTree = deepcopy(app.emptyRenderTree)

		# Add the play button
		# playButton = DirectButton(text=('normal','pressed','rollover','disabled'),
		# 						pos=(0,0,0), frameSize=(-0.3, 0.3, -0.1, 0.1),
		# 						text_scale=(0.3, 0.2))
		# Add the options menu button
		# Add the quit button


	def initScene(self):
		'''
		Run events upon starting the scene
		'''
		# Unhide the mouse and allow it free movement
		self.app.props.setMouseMode(WindowProperties.M_absolute)
		self.app.props.setCursorHidden(False)

	def exitScene(self):
		'''
		Run events upon exiting the scene
		'''
		# Hide the mouse and center it in the window
		self.app.props.setCursorHidden(True)
		self.app.props.setMouseMode(WindowProperties.M_relative)

	def eventRun(self, task):
		'''
		Run constantly updating events
		'''
		return Task.cont


class IntroScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		'''
		Initialise and run any events BEFORE loading the scene
		'''
		self.app = app
		self.isPlayerControlled = False
		self.models = {}
		self.loader = app.loader
		self.renderTree = deepcopy(app.emptyRenderTree)

		# Add the ground model
		self.addObject("ground.bam".format(app.quality), scale=(3.6,3.6,2), key="ground")

		# Add the barn
		barnModel = self.addObject("barn.bam".format(app.quality), scale=(1, 1, 1))

		# Create a corn model and add it in the bottom corner
		self.addObject("corn.egg".format(app.quality), pos=(-62, -62, 0), scale=(1, 1, 1.3), key="corn")

		# Iterate a 25x25 square for the corn
		for x in range(25):
			for z in range(25):
				# Use basic maths to create a 'lollypop' shape cutout
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

		# Add the two chickens and set the maximum velocity (force) on them
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

	def eventRun(self, task):
		'''
		Run any constant events for the scene
		'''
		# If the movement controller has finished its path then
		if self.app.controller and self.app.controller.clock_obj.get_frame_time() > self.app.controller.curve_time_end:
			# delete the motion controller
			self.app.controller = None
			# Load the first scene of the gameplay
			self.app.sceneMgr.loadScene(SceneOne(self.app))
		# Update the AI world
		self.AIworld.update()
		return Task.cont

	def initScene(self):
		'''
		Set up the movement controller and begin the motion path.
		'''
		# Make the motion path
		motionPath = (
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
		self.app.controller.play_motion_path(motionPath, 0.8)
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

	def fadeIn(self, task):
		'''
		Fade in the scene by fading a big, black rectangle
		'''
		# If more than 4 seconds have passed then finish the task
		if task.time > 4:
			self.fadeQuad.destroy()
			return
		# Get the alpha of the square
		alpha = task.time / 4
		# set the alpha level on the rectangle
		self.fadeQuad.setAlphaScale(1-alpha)
		return Task.cont

class SceneOne(Scene):
	def __init__(self, app):
		'''
		Initialise and run any events BEFORE loading the scene
		'''
		self.app = app
		self.isPlayerControlled = True
		self.models = {}
		self.loader = app.loader
		self.renderTree = deepcopy(app.emptyRenderTree)

		# Add the AIWorld
		self.aiWorld = AIWorld(self.renderTree)

		# Create a force node for the physics engine
		self.gravityForceNode = ForceNode('gravity')
		# Apply gravitational level of force to it
		gravityForce = LinearVectorForce(0, 0, -0.3)
		# Add the force to the force node
		self.gravityForceNode.addForce(gravityForce)
		# Attach the node to the tree
		gravityNodePath = self.renderTree.attachNewNode(self.gravityForceNode)
		# Add the force to the physics manager
		self.app.physicsMgr.addLinearForce(gravityForce)

		self.player = Player(self.app)
		self.player.addToScene()

		# self.groundNodePath = self.addColliderNode()
		# self.groundCollider = CollisionPlane()
		# self.groundNodePath.node().addSolid(self.groundCollider)
		# self.groundNodePath.show()

		# # Add the capsule shape for the player
		# playerColliderShape = BulletCapsuleShape(0.5, 3, ZUp)
		#
		# # Add the character controller
		# self.playerController = BulletCharacterControllerNode(playerColliderShape, 1, 'Player')
		# self.playerNodePath = self.renderTree.attachNewNode(self.playerController)
		# self.playerNodePath.setPos(0, 0, 3.2)
		# self.playerNodePath.setCollideMask(BitMask32.allOn())
		#
		# # Add the player to the bullet world
		# self.bulletWorld.attachCharacter(self.playerNodePath.node())
		#
		# debugNode = BulletDebugNode('Debug')
		# debugNode.showWireframe(True)
		# debugNode.showConstraints(True)
		# debugNode.showBoundingBoxes(True)
		# debugNode.showNormals(True)
		# debugNodePath = self.renderTree.attachNewNode(debugNode)
		# debugNodePath.show()
		#
		# self.bulletWorld.setDebugNode(debugNodePath.node())

	def eventRun(self, task):
		'''
		Run any constant events for the scene
		'''
		# Update the ai tasks
		self.aiWorld.update()
		# Update the physics of the world.
		# self.bulletWorld.doPhysics(task.time - self.app.sceneMgr.last)
		return Task.cont

	def initScene(self):
		'''
		Run any events AFTER loading the scene
		'''
		# Set the gravity on the physics world
		# self.bulletWorld.setGravity(Vec3(0, 0,-0.2))
		pass


def nullTask(task):
	return Task.cont
