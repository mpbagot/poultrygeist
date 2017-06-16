# Import the AI modules
from panda3d.ai import *
from panda3d.core import CollisionTraverser

from direct.showbase.Audio3DManager import Audio3DManager
from direct.task.Task import Task

class Chicken:
    def __init__(self, scene, pos):
        self.scene = scene
        self.pos = pos

        # Set up some AI variables
        self.modelNodePath = scene.addObject('barn.bam', pos=pos, scale=(0.3, 0.3, 0.3), isActor=True, anims={})
        self.aiChar = AICharacter("chicken", self.modelNodePath, 300, 0.05, 1)
        self.aiBehaviour = self.aiChar.getAiBehaviors()

        # Set up the 3D sound handler
        self.audio3d = Audio3DManager(scene.app.sfxManagerList[0], scene.app.camera)
        self.chickenSound = self.audio3d.loadSfx('resources/generic/sounds/chicken_cluck.ogg')
        self.audio3d.attachSoundToObject(self.chickenSound, self.modelNodePath)

        # Add the collision Traverser to the app object
        self.scene.app.cTrav = CollisionTraverser()
        # Setup automatic sound velocity determination
        self.audio3d.setSoundVelocityAuto(self.chickenSound)
        self.audio3d.setListenerVelocityAuto()

        # Initialise the distance checking variables
        self.distance = self.modelNodePath.getDistance(self.scene.app.camera)
        self.lastDistance = 12
        self.framesOfEscape = 0

    def update(self, task=None):
        '''
        Run the checks on the environment and adjust the AI
        '''
        if self.distance <= 11 and self.distance > 8:
            if self.lastDistance <= 8 or self.lastDistance > 11:
                # turn to player
                self.modelNodePath.lookAt(self.scene.app.camera)
                # Play the sound quietly
                # self.chickenSound.setVolume(0.3)
                if self.chickenSound.status() != self.chickenSound.PLAYING:
                    self.chickenSound.play()

            # If we are in the 'escape range' then start counting the four seconds
            if self.lastDistance > 8:
                self.framesOfEscape += 1
                if self.framesOfEscape > 120:
                    # stop the chase if the player has evaded the chicken
                    self.aiBehaviour.removeAi('pursue')
                    # self.aiBehaviour.seek(self.initialSpawn, 0.2)
                    self.framesOfEscape =  0
            else:
                # Reset the timer if the chicken catches up again
                self.framesOfEscape = 0

        # If the chicken gets too close then begin the chase
        elif self.distance <= 8 and self.distance > 5:
            if self.lastDistance > 8 or self.lastDistance <= 5:
                # chase at low velocity
                if self.aiBehaviour.behaviorStatus('pursue') != 'active':
                    self.aiBehaviour.pursue(self.scene.app.camera)
                self.aiChar.setMaxForce(8)
                # play sound on loop quietly
                self.chickenSound.setLoop(True)
                if self.chickenSound.status() != self.chickenSound.PLAYING:
                    self.chickenSound.play()

        # If the chicken is really close then basically sprint after the player
        if self.distance <= 5 and self.lastDistance > 5:
            # chase at high velocity
            if self.aiBehaviour.behaviorStatus('pursue') != 'active':
                self.aiBehaviour.pursue(self.scene.app.camera)
            self.aiChar.setMaxForce(27)
            # play sound on loop loudly
            self.chickenSound.setLoop(True)
            if self.chickenSound.status() != self.chickenSound.PLAYING:
                self.chickenSound.play()

        # Adjust the distances for the next update
        self.lastDistance = self.distance
        self.distance = self.modelNodePath.getDistance(self.scene.app.camera)

        # If running as a task, then return for the task to continue
        if task:
            return Task.cont
