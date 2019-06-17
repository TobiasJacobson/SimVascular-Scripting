#pathMaker(List fo 3D points, name of path, name of contour, radius)
    # Assuming points won't cross or overlap
    # Pass list of radii? In case of non-uniform vessels
    # Contour type? How to take in levelSet, splinePoly, or Polygon selections?



# def of function for path making, lofting, and meshing
def pathMaker(pointsList, pathName, contourName, radius):
    # Shortcut for function call Path.pyPath() needed when calling SimVascular functions
    p = Path.pyPath()

    # Initializing path
    p.NewObject(pathName)
    print('Path name: ' + pathName)

    # Adding each point from pointsList to current path
    for pathPoint in pointsList:
        p.AddPoint(pathPoint)

    # Adding path to repository
    p.CreatePath()

    # Importing created path from repository to the 'Paths' tab in GUI
    GUI.ImportPathFromRepos(pathName)
    GUI.ImportPathFromRepos(pathName,'Paths')

    # Initializing variables and creating contour, default to circle
    Contour.SetContourKernel('Circle')
    index = 0
    pointsLength = len(pointsList)
    contourNameList = [pathName + 'ct1', pathName + 'ct2']

    #  Shortcut for function call Contour.pyContour() needed when calling SimVascular functions
    c = Contour.pyContour()

    # Creating contours at each segment for pointsList
    c.NewObject(contourNameList[0], pathName, 0)
    c.SetCtrlPtsByRadius(pointsList[0], radius+1)
    c.Create()
    c.GetPolyData('1ctp')

    numTwo = p.GetPathPtsNum() # index at end of points list
    c2 = Contour.pyContour()
    c2.NewObject(contourNameList[1], pathName, numTwo-1)
    c2.SetCtrlPtsByRadius(pointsList[1], radius+1)
    c2.Create()
    c2.GetPolyData('2ctp')

    ### Attempt at creating systematic list of names (cct0, cct1, cct2, etc..) for individual points along path based on  pointsList length
    ### string = 'cct'
    ### while index < (pointsLength):
    ###     string += str(index)
    ###     contourNameList.append(string)
    ###     print(contourNameList[index])
    ###     index += 1

    ### create n number of objects based on pointsList length, adding each contour to repository
    ### index = 0
    ### while index < (pointsLength-1):
    ###     c.NewObject(contourNameList[index], pathName, index)
    ###     c.SetCtrlPtsByRadius(pointsList[index], radius)
    ###     c.Create()
    ###     index += 1

    # Importing contours from repository to 'Segmentations' tab in GUI
    GUI.ImportContoursFromRepos(contourName, contourNameList, pathName, 'Segmentations')
    print('Finished creating contours')

    # Gathering data to loft solid
    numSegs = 60
    Geom.SampleLoop('1ctp', numSegs, '1ctps')
    Geom.SampleLoop('2ctp', numSegs, '2ctps')
    cList = ['1ctps', '2ctps']

    # Aligning profile to allow for lofting, meshing etc.
    Geom.AlignProfile('1ctps', '2ctps', 'ct2psa', 0)

    # Declaring needed variables for lofting
    srcList = ['1ctps', '2ctps'] #'ct3psa']
    objName ='loft'
    numSegsAlongLength = 12
    numPtsInLinearSampleAlongLength = 240 # Referenced elsewhere? In LoftSolid function? No other mention in scripting
    numLinearSegsAlongLength = 120
    numModes = 20
    useFFT = 0
    useLinearSampleAlongLength = 1

    # Lofting solid using created values
    Geom.LoftSolid(srcList, objName, numSegs, numSegsAlongLength, numLinearSegsAlongLength, numModes, useFFT, useLinearSampleAlongLength)
    # Importing PolyData from solid to repository
    GUI.ImportPolyDataFromRepos('loft')

    # Adding caps to model
    VMTKUtils.Cap_with_ids('loft','cap',0,0)


    # Function shortcut for calling built-in functions
    s1 = Solid.pySolidModel()

    #
    Solid.SetKernel('PolyData')
    s1.NewObject('cyl')
    s1.SetVtkPolyData('cap')
    s1.GetBoundaryFaces(90)
    print("Creating model: \nFaceID found: " + str(s1.GetFaceIds()))
    s1.WriteNative(os.getcwd() + "/cylinder.vtp")
    GUI.ImportPolyDataFromRepos('cap')
    print('Caps added')


    # Meshing object
    MeshObject.SetKernel('TetGen')
    msh = MeshObject.pyMeshObject()
    msh.NewObject('mesh')
    solidFn = os.getcwd() + '/cylinder.vtp'
    msh.LoadModel(solidFn)
    msh.NewMesh()
    msh.SetMeshOptions('SurfaceMeshFlag',[1])
    msh.SetMeshOptions('VolumeMeshFlag',[1])
    msh.SetMeshOptions('GlobalEdgeSize',[0.75])
    msh.SetMeshOptions('MeshWallFirst',[1])
    msh.GenerateMesh()
    fileName = os.getcwd() + "/cylinder.vtk"
    msh.WriteMesh(fileName)
    msh.GetUnstructuredGrid('ug')
    Repository.WriteVtkUnstructuredGrid("ug","ascii",fileName)
    GUI.ImportUnstructedGridFromRepos('ug')

    return

# Must import to use/call simVascular executables
from sv import *
import os

# Moving from root directory
os.chdir('/Users/tobiasjacobson/Documents/Atom/solidtest')
print('Current directory: ' + print(os.getcwd()))

# Cleaning repository
objs = Repository.List()
for name in objs:
    Repository.Delete(name)

# Calling function pathMaker
pathMaker(([[0.0,0.0,0.0],[10.0,10.0,10.0]]), 'path1', 'segment1',1.0)
