from direct.filter.CommonFilters import CommonFilters
from panda3d.core import *

class Player:
    def __init__(self, app):
        self.eyeExposure = 0.5
        self.app = app
        self.pos = (0, 0, 0)

    def setPos(self, x, y=0, z=0):
        '''
        Set the position of the player object
        '''
        if x is tuple or x is list:
            self.pos = x
        else:
            self.pos = (x, y, z)
        self.nodePath.setPos(*self.pos)

    def addToScene(self):
        '''
        Initialise the player in the currently loaded scene.
        '''
        pos = list(self.pos)
        pos[2] += 3.5
        self.app.camera.setPos(*pos)
        # Set up the collider shape around the camera
        self.colliderNodePath = self.app.camera.attachNewNode(CollisionNode('playerCollNode'))
        self.collider = CollisionTube(self.pos[0], self.pos[1], self.pos[2]+4, self.pos[0], self.pos[1], self.pos[2]+0.1, 0.9)
        self.colliderNodePath.node().addSolid(self.collider)
        self.colliderNodePath.show()
        # Set up the collider ray for gravity
        self.ray = CollisionRay(0, 0, 0, 0, 0, -1)
        self.colliderNodePath.node().addSolid(self.ray)
        # Add the collision handler
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.colliderNodePath, self.app.camera)
        # Add the gravity handler
        self.gravity = CollisionHandlerFloor()
        self.gravity.addCollider(self.colliderNodePath, self.app.camera)

        # Register the collision handlers with the collision traverser
        self.app.collisionTraverser.addCollider(self.colliderNodePath, self.pusher)
        self.app.collisionTraverser.addCollider(self.colliderNodePath, self.gravity)
