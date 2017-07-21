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
        if x is not int:
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
        self.nodePath = self.app.sceneMgr.scene.addColliderNode()
        self.app.camera.setPos(*pos)
        self.app.camera.reparentTo(self.nodePath)
        self.collider = CollisionTube(self.pos[0], self.pos[1], self.pos[2]+4, self.pos[0], self.pos[1], self.pos[2]+0.1, 0.9)
        self.nodePath.node().addSolid(self.collider)
        self.nodePath.show()
