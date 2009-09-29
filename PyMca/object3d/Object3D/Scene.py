import numpy
import ObjectTree
import Object3DBase
import OpenGL.GLU as GLU
import weakref

DEBUG = 0 

class Scene:
    def __init__(self, name = 'Scene'):
        #self.tree = ObjectTree.ObjectTree('__Scene__', name)
        self.__sceneObject= Object3DBase.Object3D(name=name)
        self.__sceneObject.setSelected(True)
        ddict = {}
        ddict['common']={'anchor':[2, 2, 2]}
        #the zenith theta [z = r * cos(theta)] and azimuthal angles
        ddict['private'] = {'face':'top',
                            'theta': 0.0,
                            'phi':0.0} 
        self.__sceneObject.setConfiguration(ddict)
        self.tree = ObjectTree.ObjectTree(self.__sceneObject, name)
        self.__limits = [-100., -100., -100., 100., 100.0, 100.0]
        self.__observerPosition = [0.0, 0.0, 0.0]
        self.__autoScale = True
        self.__sceneObject.setLimits(-100., -100., -100., 100., 100.0, 100.0)
        
    def __getitem__(self, name):
        return self.tree.find(name)

    def name(self):
        return self.__sceneObject.name()

    def getObjectList(self):
        return self.tree.getList()

    def getObject3DProxy(self, name):
        #This is to avoid incrasing reference count ...
        return weakref.proxy(self[name].root[0])

    def getIndex(self, name):
        return self.tree.getList().index(name)

    def addObject(self, ob, legend = None, parent="Scene"):
        """
        Add an existing object to the scene.
        PARAMETERS:
                ob : the object to add
                Optional:
                    legend : the name of the object in this scene
                    parent : the name of the parent object
        """
        if legend is None:
            if hasattr(ob, 'name'):
                legend = ob.name()
            else:
                legend = "Unnamed"
                
        parentTree = self.tree.find(parent)
        if parentTree is None:
            raise ValueError, "Parent %s does not exist." % parent

        if legend in self.getObjectList():
            self.removeObject(legend)

        parentTree.addChild(ob, legend)

    def setThetaPhi(self, theta, phi):
        self.__sceneObject._configuration['private']['theta'] = theta
        self.__sceneObject._configuration['private']['phi'] = phi

    def getThetaPhi(self):
        return self.__sceneObject._configuration['private']['theta'],\
                self.__sceneObject._configuration['private']['phi']

    def applyCube(self, cubeFace=None):
        if cubeFace is not None:
            #this is for saving afterwards
            self.__sceneObject._configuration['private']['face'] = cubeFace
        else:
            cubeFace = self.__sceneObject._configuration['private']['face']

        #let's do the job
        xmin, ymin, zmin, xmax, ymax, zmax = self.getLimits()
        centerX = 0.5 * (xmax + xmin)
        centerY = 0.5 * (ymax + ymin)
        centerZ = 0.5 * (zmax + zmin)
        sceneConfig = self.__sceneObject._configuration 
        scale = sceneConfig['common']['scale']
        anchor = [centerX*scale[0], centerY*scale[1], centerZ*scale[2]]
        if cubeFace == 'front':
            M = self.getRotationMatrix(0.0, 90., 180.0, anchor)
            M = numpy.dot(self.getRotationMatrix(90., 0.0, 0.0, anchor), M)
        elif cubeFace == 'back':
            M = self.getRotationMatrix(0.0, 90., 0.0, anchor)
            M = numpy.dot(self.getRotationMatrix(-90., 0.0, 0.0, anchor), M)
        elif cubeFace == 'top':
            M = self.getRotationMatrix(0.0, 0.0, 0.0, anchor)
        elif cubeFace == 'bottom':
            M = self.getRotationMatrix(0.0, 180.0, 0.0, anchor)
        elif cubeFace == 'right':
            M = self.getRotationMatrix(0.0, 90.0, 90.0, anchor)
            M = numpy.dot(self.getRotationMatrix(0., 90.0, 0.0, anchor), M)
        elif cubeFace == 'left':
            M = self.getRotationMatrix(-90.0, 0.0, 0.0, anchor)
        elif 0 and cubeFace == 'd45':
            M = self.getRotationMatrix(0.0, 45.0, 45.0, anchor)
        else:
            #nicest
            M = self.getRotationMatrix(0.0, 90., 180.0, anchor)
            if 0:
                #front + theta = 45 + phi = 20
                M = numpy.dot(self.getRotationMatrix(90., 0.0, 0.0, anchor), M)
                M = numpy.dot(self.getRotationMatrix(0.0, 20.0, 45.0, anchor), M)
            else:
                #just the same
                M = numpy.dot(self.getRotationMatrix(90., 20.0, 45.0, anchor), M)
        #print "MATRIX   = ", M
        return M

    def gluLookAt(self, eyeX, eyeY, eyeZ,
			centerX, centerY, centerZ,
			upX, upY, upZ):
	F = numpy.array((centerX - eyeX, centerY - eyeY, centerZ - eyeZ),
			numpy.float)
	UP = numpy.array((upX, upY, upZ), numpy.float)

	M = numpy.zeros((4,4), numpy.float)
	M[0,0] = 1.0
	M[1,1] = 1.0
	M[2,2] = 1.0
	M[3,3] = 1.0

        fmod = numpy.sqrt(numpy.dot(F, F.T)) #numpy.linalg.norm(F)
	umod = numpy.sqrt(numpy.dot(UP, UP.T)) #numpy.linalg.norm(U)

        if (fmod <= 0.0) or (umod <= 0.0):
            return M

	F = F/fmod
	UP = UP/umod

	s = numpy.cross(F, UP)
	u = numpy.cross(s, F)

	M[0,0:3] = s
	M[1,0:3] = u
	M[2,0:3] = -F
	M = M.T		#is this due to a PyOpenGL problem?
			#if this because OpenGL gluLookAt man pages
			# suggest order orientation and it is not the case???

	# the translation -eyeX, -eyeY, -eyeZ
	if 0:
            # as pure matrix operation
            T = numpy.zeros((4,4), numpy.float)
            T[0,0] = 1.0
            T[1,1] = 1.0
            T[2,2] = 1.0
            T[3,0] = -eyeX
            T[3,1] = -eyeY
            T[3,2] = -eyeZ
            T[3,3] = 1.0
            M = numpy.dot(T, M)
        else:
	    #just compute the last row
	    M[3, 0] = -eyeX * M[0, 0] - eyeY * M[1, 0] - eyeZ * M[2, 0]
	    M[3, 1] = -eyeX * M[0, 1] - eyeY * M[1, 1] - eyeZ * M[2, 1]
	    M[3, 2] = -eyeX * M[0, 2] - eyeY * M[1, 2] - eyeZ * M[2, 2]	    
	return M

    def setSelectedObject(self, target):
        self.__sceneObject.setSelected(False)
        objectsList = self.getObjectList()
        for name in objectsList:
            item = self.tree.find(name)
            ob = item.root[0]
            if hasattr(ob, 'selected'):
                ob.setSelected(False)

        item = self.tree.find(target)
        if item is not None:
            ob = item.root[0]
            if hasattr(ob, 'selected'):
                ob.setSelected(True)
        if target == self.name():
            self.__sceneObject.setSelected(True)

    def getSelectedObject(self):
        selectedObject = None
        if self.__sceneObject.selected():
            selectedObject = self.name()
        else:
            objectsList = self.getObjectList()
            for name in objectsList:
                item = self.tree.find(name)
                ob = item.root[0]
                if ob.selected():
                    selectedObject = name
                    break
        return selectedObject

    def removeObject(self, name):
        """
        Delete an object.
        PARAMETERS :
                name : the name of the object to remove from scene
        """

        #find the objectTree
        objectTree = self.tree.find(name)
        if objectTree is None:
            if DEBUG:
                raise ValueError, "No object with name %s in tree." % name
            return
        self.tree.delChild(name)

    def clearTree(self):
        #del self.tree[1:]
        for legend in self.getObjectList():
            self.removeObject(legend)

    def setAutoScale(self, flag=True):
        if flag:
            self.__autoScale = True
        else:
            self.__autoScale = False

    def getAutoScale(self):
        return self.__autoScale

    def setObserverPosition(self, position):
        self.__observerPosition = position

    def getObserverPosition(self):
        return self.__observerPosition * 1

    def setLimits(self, limits):
        self.__limits = limits
        xmin, ymin, zmin, xmax, ymax, zmax = limits
        self.__sceneObject.setLimits(xmin, ymin, zmin, xmax, ymax, zmax)
        #this does not seem to be necessary
        #conf={'common':{'limits':self.__sceneObject.getLimits()*1}}
        #self.__sceneObject.setConfiguration(conf)

    def setOrthoLimits(self, xmin, ymin, zmin, xmax, ymax, zmax):
        self.__orthoLimits = [xmin, ymin, zmin, xmax, ymax, zmax]

    def getMinMax(self, a, b):
        if a > b:
            t = b * 1
            b = a * 1
            a = t
        return a, b

    def getLimits(self):
        if not self.__autoScale:
            return self.__limits
        objectList = self.getObjectList()

        n = len(objectList)
        if n < 2:
            return self.__limits

        ob = self.tree.find(objectList[1]).root[0]
        if hasattr(ob, 'getLimits'):
            limits = ob.getLimits()
            xmin0, ymin0, zmin0 = limits[0]
            xmax0, ymax0, zmax0 = limits[1]
            xScale, yScale,zScale = ob.getConfiguration()['common']['scale']
            xmin0 *= xScale
            ymin0 *= yScale
            zmin0 *= zScale
            xmax0 *= xScale
            ymax0 *= yScale
            zmax0 *= zScale
        else:
            limits = [[self.__limits[0], self.__limits[1], self.__limits[2]],
                      [self.__limits[3], self.__limits[4], self.__limits[5]]]                      
            xmin0, ymin0, zmin0 = limits[0]
            xmax0, ymax0, zmax0 = limits[1]

        #take care of wrong information due to scaling or not
        xmin0, xmax0 = self.getMinMax(xmin0, xmax0)
        ymin0, ymax0 = self.getMinMax(ymin0, ymax0)
        zmin0, zmax0 = self.getMinMax(zmin0, zmax0)

        if n > 2:
            for name in objectList[1:]:
                ob = self.tree.find(name).root[0]
                if hasattr(ob, 'getLimits'):
                    limits = ob.getLimits()
                    xmin, ymin, zmin = limits[0]
                    xmax, ymax, zmax = limits[1]
                    #correct for scale
                    xScale, yScale,zScale = ob.getConfiguration()['common']['scale']
                    xmin *= xScale
                    ymin *= yScale
                    zmin *= zScale
                    xmax *= xScale
                    ymax *= yScale
                    zmax *= zScale
                    xmin, xmax = self.getMinMax(xmin, xmax)
                    ymin, ymax = self.getMinMax(ymin, ymax)
                    zmin, zmax = self.getMinMax(zmin, zmax)
                    if xmin < xmin0:
                        xmin0 = xmin
                    if ymin < ymin0:
                        ymin0 = ymin
                    if zmin < zmin0:
                        zmin0 = zmin
                    if xmax > xmax0:
                        xmax0 = xmax
                    if ymax > ymax0:
                        ymax0 = ymax
                    if zmax > zmax0:
                        zmax0 = zmax
                        
        if zmax0 == zmin0:
            zmax0 = zmin0 + 1
            zmin0 -= 1
        if xmin0 == xmax0:
            d = 0.5 * (ymax0 - ymin0)
            xmin0 -= d
            xmax0 += d
        if ymin0 == ymax0:
            d = 0.5 * (xmax0 - xmin0)
            ymin0 -= d
            ymax0 += d
        self.setLimits([xmin0, ymin0, zmin0, xmax0, ymax0, zmax0])
        return self.__limits * 1

    def drawTree(self, tree):
        """
        Draw a tree.
        NOTES :
            'glPopName' happened BEFORE the recursive call :
                        we want to catch an object, not its parent
            'glPopMatrix'  happend AFTER this call, because the drawing matrix
                        is depending on its parent
        """
        for subTree in tree.childList():

            name = subTree.name()

            opengl.glPushMatrix()
            opengl.glPushName(self.scene.getIndex(name))

            self.scene[name].draw(self.selectedObject == name)
            opengl.glPopName()

            self.drawTree(subTree)
            opengl.glPopMatrix()

    def getRotationMatrix(self, xRot, yRot, zRot, anchor=None):
        """
        Angles given in degrees!!!!
        """
        M = numpy.zeros((4,4), numpy.float64)
        M[0, 0] = 1
        M[1, 1] = 1
        M[2, 2] = 1
        M[3, 3] = 1
        if (xRot == 0) and (yRot == 0) and (zRot == 0):
            return M

        if anchor is None:
            anchorPosition = [0.0, 0.0, 0.0]
        else:
            anchorPosition = anchor

        trans = M * 1
        rotX  = M * 1
        rotY  = M * 1
        rotZ  = M * 1

        #translation
        M[3, 0] = anchorPosition[0]
        M[3, 1] = anchorPosition[1]
        M[3, 2] = anchorPosition[2]
                                
        #this works
        #RotX
        angle = xRot * numpy.pi/180.
        cs = numpy.cos(angle)
        sn = numpy.sin(angle)
        rotX = numpy.zeros((4,4), numpy.float64)
        rotX[0,0] =  1
        rotX[1,1] =  1
        rotX[2,2] =  1
        rotX[3,3] =  1                    
        rotX[1,1] =  cs; rotX[1,2] = sn   
        rotX[2,1] = -sn; rotX[2,2] = cs

        #RotY
        angle = yRot * numpy.pi/180.
        cs = numpy.cos(angle)
        sn = numpy.sin(angle)
        rotY = numpy.zeros((4,4), numpy.float64)
        rotY[0,0] =  1
        rotY[1,1] =  1
        rotY[2,2] =  1
        rotY[3,3] =  1                    
        rotY[0,0] =  cs; rotY[0,2] = -sn   #inverted respect to the others
        rotY[2,0] =  sn; rotY[2,2] =  cs
                
        #RotZ
        angle = zRot * numpy.pi/180.
        cs = numpy.cos(angle)
        sn = numpy.sin(angle)
        rotZ = numpy.zeros((4,4), numpy.float64)
        rotZ[0,0] =  1
        rotZ[1,1] =  1
        rotZ[2,2] =  1
        rotZ[3,3] =  1                    
        rotZ[0,0] =  cs; rotZ[0,1] = sn   
        rotZ[1,0] = -sn; rotZ[1,1] = cs
        
        #The final rotation matrix
        rotMatrix = numpy.dot(rotZ,numpy.dot(rotY, rotX))

        #perform the in-place rotation
        #GL.glMultMatrixd(rotMatrix)

        #find out where the anchor goes under that rotation
        trans = numpy.zeros((4,4), numpy.double)
        trans[0,0] = 1.0
        trans[1,1] = 1.0
        trans[2,2] = 1.0
        trans[3,3] = 1.0
        trans[3,0] = anchorPosition[0]
        trans[3,1] = anchorPosition[1]
        trans[3,2] = anchorPosition[2]
        distance = numpy.dot(rotMatrix, trans)

        # and subtract it
        trans[3,0] = -distance[3,0]
        trans[3,1] = -distance[3,1]
        trans[3,2] = -distance[3,2]
        M = numpy.dot(trans, numpy.dot(rotMatrix,M))
        return M

if __name__ == "__main__":
    import Object3DBase
    w = Scene()
    o0 = Object3DBase.Object3D("DummyObject0")
    o1 = Object3DBase.Object3D("DummyObject1")
    o01 = Object3DBase.Object3D("DummyObject01")
    w.addObject(o0)
    w.addObject(o1)
    w.addObject(o01)
    print w.tree

    w.addObject(o0, parent="DummyObject01")
    print w.tree