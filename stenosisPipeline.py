# Current Objective: Write script for a complete pipeline that will:
#           (1) Apply stenosis on existing model (Well actually its individual segments)
#           (2) Generate a new model based on applied stenosis
#           (3) Generate a new mesh based on new model
#           (4) Run presolver
# Inputs: .ctgr file, percent stenosis, contour group to apply stenosis

### NOTES ###
# Change the directory path to location of files on your computer for any line containing # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Couldn't change 3D path point size (sorry they're so big)
# For more detailed mesh, change 'GlobalEdgeSize, [x]' in makeMesh function

# Global list needed for more than one function call (Hence made global)
polyDataList = []

#########################################################
#                  Function Definitions                 #
#########################################################

def alteringStenosis(fileName, percentage, contourGroup):
    # Check if given file exists in cwd
    try:
        inFile = open(fileName+'.ctgr', 'r')
    except:
        print("Unable to open given file")
        return

    # Check that given percent is valid (i.e. between 0-100)
    if percentage < 0 or percentage > 100:
        print('Percent given is not within a valid range')
        return

    # Once file and % have been validated create output file
    print('Creating: '+fileName+'-'+str(contourGroup)+'-'+str(percentage)+'.ctgr')
    outFile = open(fileName+'-'+str(contourGroup)+'-'+str(percentage)+'.ctgr','w+')

    # Iterate through given .ctgr file until desired segmentation is reached (i.e contourGroup is found)
    found = False # Will be used to track whether contourGroup is found
    for seg in inFile:
        if '<contour id=\"'+str(contourGroup)+'\"' in seg: # If found, break after writing ID line to outFile
            outFile.write(seg) # Write contour ID line to outFile
            found = True # Validating that contourSegment was found
            break
        else:
            outFile.write(seg) # Else write to outFile

    if found == False: # Edge case if contour group is not found && exits
        print('Segment does not exist in contour')
        return

    # Will store center data for desired segment (Needed later when scaling points)
    count = 0
    foundCenterPoints = []

    # Reading in points, making note of control vs contour points
    for iteration in inFile:
        if "<control_points>" in iteration:
            break
        else:
            cText = iteration
            if count == 1:
                foundCenterPoints.append(re.findall('"([^"]*)"', cText)) # Obtaining center data using Python Regex
            outFile.write(iteration)
            count += 1

    # Array of lists to store points
    pointsData = []

    # Copy and save data to the pointsData list
    for iteration in inFile:
        if "</control_points>" in iteration:
            break
        else:
            pointsData.append(re.findall('"([^"]*)"', iteration))  # '^' signifies start of string, '*' RE matches 0 or more (ab* will match 'a','ab' or 'abn'
                                                                   # where n is n number of b's following), [] indicates a set of special characters
    ct = int(pointsData[-1][0]) # Hmm... Yeah not really sure -- Ask Erica

    # Takes the actual integers from segment to alter and copies them to list: pointsData
    count = 0
    for iteration in inFile:
        if "</contour_points>" in iteration:
            break
        else:
            if count == 0: # B/C otherwise first item in list is always a blank list for some reason (Brute fix)
                count += 1
            else:
                stringLine = iteration
                pointsData.append(re.findall('"([^"]*)"', stringLine))

    ################################## Creating matrix called cVdataTranspose (converted data matrix transposed), i.e main matrix #################################
    # List of ones to be appended to pointsData matrix for matrix multiplication
    onesArr = numpy.ones(len(pointsData))

    # Converting pointsData to type: float, removing first column as it only contains indicies therefore isn't needed for multiplication
    cVdata = numpy.array(pointsData)
    cVdata = cVdata.astype(numpy.float)
    cVdata = cVdata[:,1:]

    # Appending onesArr to pointsData
    cVdata = numpy.concatenate((cVdata,onesArr[:,None]), axis=1)

    # Transpose data for matrix multiplication
    cVdataTranspose = numpy.transpose(cVdata)

    ################################## Creating overall matrix combining scalar, translation, and inverse translation matricies ##################################
    # Converting foundCenterPoints to floats and storing it in centerData
    centerData = numpy.array(foundCenterPoints)
    centerData = centerData.astype(numpy.float)
    print('Center for contour ' + contourGroup + ' found at: ' + str(centerData)) # Can be used to validate

    # Storing x, y, z data points for easy access (cd = center data )
    cdx = centerData[0][0] # x - position
    cdy = centerData[0][1] # y - position
    cdz = centerData[0][2] # z - position

    # Setting scalingFactor based on users input 'percentage'
    scalingFactor = math.sqrt(abs(percentage-100)/100.0) # Without abs(x-100) stenosis goes as 5 in mine = 95 applied, 40 in mine = 60 applied

    # Creating Scalar Matrix (with scalar as percent stenosis given)
    scalarMatrix = [[scalingFactor, 0, 0, 0], [0, scalingFactor, 0, 0], [0, 0, scalingFactor, 0], [0, 0, 0, 1]]

    # Creating Translation Matrix
    translationMatrix = [[1, 0,0, -cdx], [0, 1, 0, -cdy], [0, 0, 1, -cdz], [0, 0, 0, 1]]

    # Creating Inverse Translation matrix
    invTranslationMatrix = [[1, 0,0, cdx], [0, 1, 0, cdy], [0, 0, 1, cdz], [0, 0, 0, 1]]

    # Creating overall matrix
    intermediateMatrix = numpy.matmul(invTranslationMatrix, scalarMatrix)
    matrixMain = numpy.matmul(intermediateMatrix, translationMatrix)
    # import pdb; pdb.set_trace() # Needed for debugging matmul to create matrixMain
    # print matrixMain # Used to check values of transposed data

    # Matrix multiplication of cVdataTranspose and matrixMain -- Note: have to left multiply with matrixMain
    newPointsData = numpy.matmul(matrixMain, cVdataTranspose)
    # print newPointsData # Used to check values of newPointsData
    newPointsData = newPointsData[:-1,:] # Removes all ones from bottom of matrix
    # Scaled data transposed back to original form
    newDataTpose = numpy.transpose(newPointsData)
    # print newDataTpose # Used to check values of newDataTpose

    # Adding control points to the outFile
    outFile.write('            <control_points>\n')
    for i in range(ct+1):
        dl = newDataTpose[i,:]
        fStr = '<point id=\"{}\" x=\"{}\" y=\"{}\" z=\"{}\" />\n'.format(i,dl[0],dl[1],dl[2])
        outFile.write('                '+fStr)
    outFile.write('            </control_points>\n')

    # Adding contour points to the outFile
    outFile.write('            <contour_points>\n')
    for i in range(ct+1, numpy.shape(newDataTpose)[0]):
        dl = newDataTpose[i,:]
        fStr = '<point id=\"{}\" x=\"{}\" y=\"{}\" z=\"{}\" />\n'.format(i-ct-1,dl[0],dl[1],dl[2])
        outFile.write('                '+fStr)
    outFile.write('            </contour_points>\n')

    # Finish writing rest of data from inFile to outFile
    for line in inFile:
       outFile.write(line)

    # Final actions
    print("File Created")
    inFile.close()
    outFile.close()
    return fileName+'-'+str(contourGroup)+'-'+str(percentage)
     # End of function alteringStenosis(str, int, str)

# Next steps - generate model, mesh and prepare preSolver

# Path
def makePath(pointsList, newPathName, newContourName, percentage, contour):
    # Shortcut for function call Path.pyPath(), needed when calling SimVascular functions
    p = Path.pyPath()

    # Initializing path
    p.NewObject(newPathName)
    print('Path name: ' + newPathName)

    # Adding each point from pointsList to created path
    for pathPoint in pointsList:
        p.AddPoint(pathPoint)

    # Adding path to repository
    p.CreatePath()

    # Importing created path from repository to the 'Paths' tab in GUI
    GUI.ImportPathFromRepos(newPathName,'Paths')

    # Initializing variables and creating segmentations (Defaulted to circle)
    Contour.SetContourKernel('Circle')
    pointsLength = len(pointsList)

    # Shortcut for function call Contour.pyContour(), needed when calling SimVascular functions
    numEnd = p.GetPathPtsNum() # index at end of pointsList
    numSec = int((numEnd-1)/(pointsLength-1))

    # will calc radii (dist) here (since each segment/contour may vary in diameter)
    distances = []
    i = 0
    u = 0
    while i < pointsLength:
        xS1 = controlPointsList[u][0]
        xS2 = controlPointsList[u+1][0]
        yS1 = controlPointsList[u][1]
        yS2 = controlPointsList[u+1][1]
        zS1 = controlPointsList[u][2]
        zS2 = controlPointsList[u+1][2]
        allInts = ((xS2-xS1)**2)+((yS2-yS1)**2)+((zS2-zS1)**2)
        distances.append(math.sqrt(allInts))
        i += 1
        u += 2

    # Calculate radius reduction for specific contour group
    stenosisDistances = []
    dLen = len(distances)
    index = 0
    while index < (dLen-1):
        a1 = (math.pi)*(distances[index])*(distances[index])
        deltaA1 = a1*((100-percentage)/100)
        q = deltaA1/(math.pi)
        stenosisDistances.append(math.sqrt(q))
        index += 1

    # Creating new contour names --> going as newPathName + 'ct1', 'ct2' etc
    strs = 1
    newContourNameList = []
    while strs < (pointsLength+1):
        stAdd = newPathName + 'ct' + str(strs)
        newContourNameList.append(stAdd)
        strs += 1

    # Creating polyDataList --> going as '1ctp', '2ctp' etc
    strs = 1
    polyList = []
    while strs < (pointsLength+1):
        stAdd = str(strs) + 'ctp'
        polyList.append(stAdd)
        strs += 1

    # Creating new contours based on pointsList and collecting polyData for modeling
    index = 0
    while index < pointsLength:
        cCall = 'c' + str(index)
        cCall = Contour.pyContour()
        cCall.NewObject(newContourNameList[index], newPathName, numSec*index)
        if contour == str(index):
            cCall.SetCtrlPtsByRadius(pointsList[index], stenosisDistances[index])
            # cCall.SetCtrlPts(controlPointsList[index]) # Could resolve contour 0 distortion --> Tho still unsure of its arg inputs...
        else:
            cCall.SetCtrlPtsByRadius(pointsList[index], distances[index])
            # cCall.SetCtrlPts(controlPointsList[index]) # Could resolve contour 0 distortion --> Tho still unsure of its arg inputs...
        cCall.Create()
        cCall.GetPolyData(polyList[index])
        polyDataList.append(polyList[index])
        index += 1

    # Importing contours from repository to 'Segmentations' tab in GUI
    GUI.ImportContoursFromRepos(newContourName, newContourNameList, newPathName, 'Segmentations')
    return

# Model:
def makeContour(newObjectName, modelName):
    numSegs = 120 # Number of segments defaulted to 120

    srcList = [] # contains SampleLoop generations

    # Apply SampleLoop and appending to srcList for each item of polyDataList
    for item in polyDataList:
        Geom.SampleLoop(item, numSegs, item+'s')
        srcList.append(item+'s')

    pointsLen = len(listPathPoints) # Length of listPathPoints

    # Tangent calls
    t3s = [0, 0, 0]
    tTot = [None]*pointsLen
    calls = 0
    while calls < (pointsLen-1):
        t3s[0] = math.tan(listPathPoints[calls][0])
        t3s[1] = math.tan(listPathPoints[calls][1])
        t3s[2] = math.tan(listPathPoints[calls][2])
        tTot[calls] = t3s
        calls += 1

    # Cosine calls
    c3s = [0, 0, 0]
    cTot = [None]*pointsLen
    calls = 0
    while calls < (pointsLen-1):
        c3s[0] = math.cos(listPathPoints[calls][0])
        c3s[1] = math.cos(listPathPoints[calls][1])
        c3s[2] = math.cos(listPathPoints[calls][2])
        cTot[calls] = c3s
        calls += 1

    # Used --> Geom.OrientProfile() but can also use --> Geom.AlignProfile() Not entirely sure what either do tho...
    # Geom.orientProfile('', x y z, tan(x y z), xyz in plane of obj, 'newOrient')
    # Note: Tan and cos are in degrees, not radians
    dev = 0 # Used to keep index
    while dev < (pointsLen-1):
        st1 = str(dev+1)+'ctps'
        st2 = 'newOrient'+str(dev+1)
        Geom.OrientProfile(str(st1), listPathPoints[dev], tTot[dev], cTot[dev], str(st2))
        dev += 1

    # Creating values to loft solid
    objName = str(newObjectName)
    numSegsAlongLength = 240
    numLinearSegsAlongLength = 240
    numModes = 20
    useFFT = 0
    useLinearSampleAlongLength = 1
    Geom.LoftSolid(srcList, objName, numSegs, numSegsAlongLength, numLinearSegsAlongLength, numModes, useFFT, useLinearSampleAlongLength)

    # Importing PolyData from solid to repository (No cap model)
    GUI.ImportPolyDataFromRepos(str(newObjectName))

    # Adding caps to model (Full cap model)
    VMTKUtils.Cap_with_ids(str(newObjectName),str(modelName),0,0)

    # Shortcut for function call Solid.pySolidModel(), needed when calling SimVascular functions
    s1 = Solid.pySolidModel()

    # Creating model
    Solid.SetKernel('PolyData')
    s1.NewObject('newModel')
    s1.SetVtkPolyData(str(modelName))
    s1.GetBoundaryFaces(90)
    print("Creating model: \nFaceID found: " + str(s1.GetFaceIds()))
    s1.WriteNative(os.getcwd() + "/" + str(newObjectName) + ".vtp")
    GUI.ImportPolyDataFromRepos(str(modelName))
    print('Caps added to model \n')
    return

# Mesh:
def makeMesh(vtpFile, vtkFile):
    MeshObject.SetKernel('TetGen')
    msh = MeshObject.pyMeshObject()
    msh.NewObject('newMesh')
    solidFn = os.getcwd() + '/' + str(vtpFile)
    msh.LoadModel(solidFn)
    msh.NewMesh()
    msh.SetMeshOptions('SurfaceMeshFlag',[1])
    msh.SetMeshOptions('VolumeMeshFlag',[1])
    msh.SetMeshOptions('GlobalEdgeSize',[0.08])
    msh.SetMeshOptions('MeshWallFirst',[1])
    msh.GenerateMesh()
    os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Simulations') # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    fileName = os.getcwd() + "/" + str(vtkFile)
    msh.WriteMesh(fileName)
    msh.GetUnstructuredGrid('Mesh')
    Repository.WriteVtkUnstructuredGrid("Mesh","ascii",fileName)
    GUI.ImportUnstructedGridFromRepos('Mesh')
    print('Mesh generated')
    return

# preSolver:
def runpreSolver(svFile):
    try:
        os.system('/usr/local/sv/svsolver/2019-01-19/svpre' + str(svFile))
        print('Running preSolver')
    except:
        print('Unable to run preSolver')
    return

# Gathering path points from oroginal contour to use for new contour
def gatherPoints(segFile):
    try:
        inputFile = open(segFile+'.ctgr', 'r')
    except:
        print("Unable to open given .ctgr file")
        return

    # Array of lists to store points
    segsData = []
    count = 0

    # Reading in points, making note of control vs contour points && Copy and save data to the pointsData list
    for iteration in inputFile:
        if "<pos" in iteration:
            segsData.append(re.findall('"([^"]*)"', iteration)) # Obtaining center data for each segment
    segsData = numpy.array(segsData)
    segsData = segsData.astype(numpy.float)
    return segsData

# Gathering control points to calculate radii for setting control points
def gatherControlPoints(segFile): # .ctgr file
    try:
        inFile = open(segFile+'.ctgr', 'r')
        print('File opened succesfully')
    except:
        print("Unable to open given .ctgr file")
        return

    count = 0
    add = False
    controlPoints = []

    for line in inFile:
        if "<control_points>" in line:
            count = 0
            add = True
        if "</control_points>" in line:
            add = False
        if add:
            if count != 0:
                controlPoints.append(re.findall('"([^"]*)"', line))
            count += 1
    controlPoints = numpy.array(controlPoints)
    controlPoints = controlPoints.astype(numpy.float)
    controlPoints = controlPoints[:,1:]
    return controlPoints

####################################################
#                   Main                           #
####################################################

# Importing various repos.
import os
from sv import *
import sys
import numpy
from numpy import genfromtxt
import pdb
import re
import math
import os.path
import operator

# # Clearing repository (Still no way to remove from GUI tho so I still have issues, but Fanwei is addressing this)
# objs = Repository.List()
# for name in objs:
#     Repository.Delete(name)

# ------- Change based on desired alterations ------- #
mainCTGRfile = 'SVC'
contourGroupToAlter = '2'
percentStenosis = 50
svpreFile = 'idealSim2.svpre'
# --------------------------------------------------- #

# Defaulted to these below, change if you want
newPthName = mainCTGRfile + '_copy_Path'
newSegNAme = mainCTGRfile + '_copy_Segment'
modelNoCap = mainCTGRfile + '_noCapMod'
modelWithCap = mainCTGRfile + '_fullMod'
meshVtp = modelNoCap + '.vtp'
meshVtk = mainCTGRfile + '_OutFile.vtk'

# Various variables needed
stenosisCTGRfile = "None"
controlPointsList = []
pathPoints = []

# Change cwd to SimV project --> Segmentations
os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Segmentations') # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
print('Current directory: ' + os.getcwd())

# Gathering segment radii
controlPointsList = gatherControlPoints(mainCTGRfile)

# Stenosis function call
print('Applying stenosis:')
stenosisCTGRfile = alteringStenosis(mainCTGRfile, percentStenosis, contourGroupToAlter)

# Gathering points from given model
print('\nGathering points & making path:')
pathPoints = gatherPoints(stenosisCTGRfile)
listPathPoints = pathPoints.tolist() # Conversion from numpy array to python list to allow for valid makePath function call
makePath(listPathPoints, newPthName, newSegNAme, percentStenosis, contourGroupToAlter)

# Change cwd to SimV project --> Models
os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Models') # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
print('Current directory: ' + os.getcwd())
# Contour function call
print('Create new contour:')
makeContour(modelNoCap, modelWithCap)

# Mesh function call
print('Create new mesh:')
makeMesh(meshVtp, meshVtk)

# preSolver function call
print('Running preSolver: \n')
runpreSolver(svpreFile)
