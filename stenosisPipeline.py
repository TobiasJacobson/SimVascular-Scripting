# Current Objective: Write script for a complete pipeline that will:
#           (1) Apply stenosis on existing model (Well actually its individual segments)
#           (2) Generate a new model based on applied stenosis
#           (3) Generate a new mesh based on new model
#           (4) Run presolver
# Inputs: .ctgr file, percent stenosis, contour group to apply stenosis

# Global variables needed for more than one function call (Hence made global)
pathPoints = []
polyDataList = []

######################################################
#                      Func Def                      #
######################################################

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

    # Once segment and % have been validated, print creating...
    print('Creating: '+fileName+'-'+str(contourGroup)+'-'+str(percentage)+'.ctgr')
    # Creating output file
    outFile = open(fileName+'-'+str(contourGroup)+'-'+str(percentage)+'.ctgr','w+')

    # Iterate through given .ctgr file until desired segmentation is reached (i.e contourGroup is found)
    found = False # Will be used to track whether contourGroup is found
    for seg in inFile:
        if '<contour id=\"'+str(contourGroup)+'\"' in seg: # If found, break after writing ID line to outFile
            outFile.write(seg) # Write contour ID line to outFile
            found = True # Validating that contourSegment was found
            break
        else:
            outFile.write(seg) # Else write to file
    if found == False: # Edge case if contour group is not found
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
                foundCenterPoints.append(re.findall('"([^"]*)"', cText)) # Obtaining center data
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

    # Hmm...
    ct = int(pointsData[-1][0])

    # Takes the actual integers from segment to alter and copies them to array: pointsData
    count = 0
    for iteration in inFile:
        if "</contour_points>" in iteration:
            break
        else:
            if count == 0: # B/C otherwise first item in list is always a blank list for some reason
                count += 1
            else:
                stringLine = iteration
                pointsData.append(re.findall('"([^"]*)"', stringLine))
                # outFile.write(iteration) # This wrote original segment data to outfle creating a duplicate...


    ################################## Creating matrix called cVdataTranspose, i.e main matrix #################################
    # List of ones to be appended to pointsData matrix for matrix multiplication
    onesArr = numpy.ones(len(pointsData))

    # Converting pointsData to type: float, removing first column as it only contains indicies therefore isn't needed
    cVdata = numpy.array(pointsData)
    cVdata = cVdata.astype(numpy.float)
    cVdata = cVdata[:,1:]

    # Appending onesArr to pointsData
    cVdata = numpy.concatenate((cVdata,onesArr[:,None]), axis=1)

    # Transpose data for matrix multiplication
    cVdataTranspose = numpy.transpose(cVdata)
    # print cVdataTranspose # Used to check values of transposed data



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


    # Matrix multiplication of cVdataTranspose and dataMatrix -- Note: have to left multiply with dataMatrix
    newPointsData = numpy.matmul(matrixMain, cVdataTranspose)
    # print newPointsData # Used to check values of newPointsData
    newPointsData = newPointsData[:-1,:] # Removes all ones from bottom of matrix
    # Transposed scaled data back to original form
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

    # Finish writing rest data from inFile to outFile
    for line in inFile:
       outFile.write(line)

    # Final actions
    print("File Created")
    inFile.close()
    outFile.close()
    return # End of function alteringStenosis(x, y, z)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Next steps - generate model, mesh and prepare preSolver
# Path
def makePath(pointsList, pathName, contourName, radius):
    # Shortcut for function call Path.pyPath(), needed when calling SimVascular functions
    p = Path.pyPath()

    # Initializing path
    p.NewObject(pathName)
    print('Path name: ' + pathName)

    # Adding each point from pointsList to created path
    for pathPoint in pointsList:
        # print(pathPoint)
        p.AddPoint(pathPoint)

    # Adding path to repository
    p.CreatePath()

    # Importing created path from repository to the 'Paths' tab in GUI
    GUI.ImportPathFromRepos(pathName)
    GUI.ImportPathFromRepos(pathName,'Paths')
    # Repository.Delete(pathName)

    # Initializing variables and creating segmentations (Default to circle)
    Contour.SetContourKernel('Circle')
    pointsLength = len(pointsList)
    contourNameList = [pathName+'ct1', pathName+'ct2', pathName+'ct3', pathName+'ct4',pathName+'ct5', pathName+'ct6', pathName+'ct7', pathName+'ct8', pathName+'ct9']

    #  Shortcut for function call Contour.pyContour(), needed when calling SimVascular functions
    numEnd = p.GetPathPtsNum() # index at end of pointsList
    numSec = int((numEnd-1)/8)

    c = Contour.pyContour()
    c.NewObject(contourNameList[0], pathName, 0)
    c.SetCtrlPtsByRadius(pointsList[0], radius)
    c.Create()
    c.GetPolyData('1ctp')
    polyDataList.append('1ctp')

    c2 = Contour.pyContour()
    c2.NewObject(contourNameList[1], pathName, numSec)
    c2.SetCtrlPtsByRadius(pointsList[1], radius)
    c2.Create()
    c2.GetPolyData('2ctp')
    polyDataList.append('2ctp')

    c3 = Contour.pyContour()
    c3.NewObject(contourNameList[2], pathName, numSec*2)
    c3.SetCtrlPtsByRadius(pointsList[2], radius)
    c3.Create()
    c3.GetPolyData('3ctp')
    polyDataList.append('3ctp')

    c4 = Contour.pyContour()
    c4.NewObject(contourNameList[3], pathName, numSec*3)
    c4.SetCtrlPtsByRadius(pointsList[3], radius)
    c4.Create()
    c4.GetPolyData('4ctp')
    polyDataList.append('4ctp')

    c5 = Contour.pyContour()
    c5.NewObject(contourNameList[4], pathName, numSec*4)
    c5.SetCtrlPtsByRadius(pointsList[4], radius)
    c5.Create()
    c5.GetPolyData('5ctp')
    polyDataList.append('5ctp')

    c6 = Contour.pyContour()
    c6.NewObject(contourNameList[5], pathName, numSec*5)
    c6.SetCtrlPtsByRadius(pointsList[5], radius)
    c6.Create()
    c6.GetPolyData('6ctp')
    polyDataList.append('6ctp')

    c7 = Contour.pyContour()
    c7.NewObject(contourNameList[6], pathName, numSec*6)
    c7.SetCtrlPtsByRadius(pointsList[6], radius)
    c7.Create()
    c7.GetPolyData('7ctp')
    polyDataList.append('7ctp')

    c8 = Contour.pyContour()
    c8.NewObject(contourNameList[7], pathName, numSec*7)
    c8.SetCtrlPtsByRadius(pointsList[7], radius)
    c8.Create()
    c8.GetPolyData('8ctp')
    polyDataList.append('8ctp')

    c9 = Contour.pyContour()
    c9.NewObject(contourNameList[8], pathName, numSec*8)
    c9.SetCtrlPtsByRadius(pointsList[8], radius)
    c9.Create()
    c9.GetPolyData('9ctp')
    polyDataList.append('9ctp')

    # # Attempt at creating systematic list of names (cct0, cct1, cct2, etc..) for individual points along path based on pointsList length
    # contourNameList = [None] * pointsLength
    # index = 0
    # string = 'ctp'
    # cString = 'c'
    # callList = [None] * pointsLength
    # while index < (pointsLength):
    #     string = str(index) + string
    #     contourNameList.append(string)
    #     cString = string + str(index)
    #     callList.append(cString)
    #     # print(contourNameList[index])
    #     # print(callList)
    #     index += 1
    #
    # # create n number of objects based on pointsList length, adding each contour to repository
    # index = 0
    # while index < (pointsLength-1):
    #     callList[index] = Contour.pyContour()
    #     callList[index].NewObject(contourNameList[index], pathName, index)
    #     callList[index].SetCtrlPtsByRadius(pointsList[index], radius)
    #     callList[index].Create()
    #     callList[index].GetPolyData(contourNameList[index]+'p')
    #     index += 1

    # Importing contours from repository to 'Segmentations' tab in GUI
    GUI.ImportContoursFromRepos(contourName, contourNameList, pathName, 'Segmentations')

    return

# Model:
def makeContour(newObjectName, modelName):
    # Creating data to loft solid ------------------ #
    numSegs = 60 # Number of segments defaulted to 60

    # Declaring needed variables for lofting
    srcList = [] # contains SampleLoop generations

    # Apply SampleLoop and append to cList for each item of polyDataList
    Geom.SampleLoop(polyDataList[0], numSegs, polyDataList[0]+'s')
    srcList.append(polyDataList[0]+'s')

    Geom.SampleLoop(polyDataList[1], numSegs, polyDataList[1]+'s')
    srcList.append(polyDataList[1]+'s')

    Geom.SampleLoop(polyDataList[2], numSegs, polyDataList[2]+'s')
    srcList.append(polyDataList[2]+'s')

    Geom.SampleLoop(polyDataList[3], numSegs, polyDataList[3]+'s')
    srcList.append(polyDataList[3]+'s')

    Geom.SampleLoop(polyDataList[4], numSegs, polyDataList[4]+'s')
    srcList.append(polyDataList[4]+'s')

    Geom.SampleLoop(polyDataList[5], numSegs, polyDataList[5]+'s')
    srcList.append(polyDataList[5]+'s')

    Geom.SampleLoop(polyDataList[6], numSegs, polyDataList[6]+'s')
    srcList.append(polyDataList[6]+'s')

    Geom.SampleLoop(polyDataList[7], numSegs, polyDataList[7]+'s')
    srcList.append(polyDataList[7]+'s')

    Geom.SampleLoop(polyDataList[8], numSegs, polyDataList[8]+'s')
    srcList.append(polyDataList[8]+'s')

    # Loop AlignProfile for each set of two points. Aligning profiles to allow for lofting, meshing etc.
    # Geom.orientProfile('', x y z, tan(x y z), xyz in plane of obj, 'newOrient')
    # Note: Tan and cos are in degrees, not radians
    # print('Tan: ')
    L11 = math.tan(listPathPoints[0][0])
    L12 = math.tan(listPathPoints[0][1])
    L13 = math.tan(listPathPoints[0][2])
    LT1 = [L11, L12, L13]
    # print(LT1)

    L21 = math.tan(listPathPoints[1][0])
    L22 = math.tan(listPathPoints[1][1])
    L23 = math.tan(listPathPoints[2][2])
    LT2 = [L21, L22, L23]
    # print(LT2)

    L31 = math.tan(listPathPoints[2][0])
    L32 = math.tan(listPathPoints[2][1])
    L33 = math.tan(listPathPoints[2][2])
    LT3 = [L31, L32, L32]
    # print(LT3)

    L41 = math.tan(listPathPoints[3][0])
    L42 = math.tan(listPathPoints[3][1])
    L43 = math.tan(listPathPoints[3][2])
    LT4 = [L41, L42, L42]
    # print(LT4)

    L51 = math.tan(listPathPoints[4][0])
    L52 = math.tan(listPathPoints[4][1])
    L53 = math.tan(listPathPoints[4][2])
    LT5 = [L51, L52, L52]
    # print(LT5)

    L61 = math.tan(listPathPoints[5][0])
    L62 = math.tan(listPathPoints[5][1])
    L63 = math.tan(listPathPoints[5][2])
    LT6 = [L61, L62, L62]
    # print(LT6)

    L71 = math.tan(listPathPoints[6][0])
    L72 = math.tan(listPathPoints[6][1])
    L73 = math.tan(listPathPoints[6][2])
    LT7 = [L71, L72, L72]
    # print(LT7)

    L81 = math.tan(listPathPoints[7][0])
    L82 = math.tan(listPathPoints[7][1])
    L83 = math.tan(listPathPoints[7][2])
    LT8 = [L81, L82, L82]
    # print(LT8)

    L91 = math.tan(listPathPoints[8][0])
    L92 = math.tan(listPathPoints[8][1])
    L93 = math.tan(listPathPoints[8][2])
    LT9 = [L91, L92, L92]
    # print(LT9)
    # -------------------------------------- #
    # print('cos: ')
    C11 = math.cos(listPathPoints[0][0])
    C12 = math.cos(listPathPoints[0][1])
    C13 = math.cos(listPathPoints[0][2])
    LC1 = [C11, C12, C13]
    # print(LC1)

    C21 = math.cos(listPathPoints[1][0])
    C22 = math.cos(listPathPoints[1][1])
    C23 = math.cos(listPathPoints[2][2])
    LC2 = [C21, C22, C23]
    # print(LC2)

    C31 = math.cos(listPathPoints[2][0])
    C32 = math.cos(listPathPoints[2][1])
    C33 = math.cos(listPathPoints[2][2])
    LC3 = [C31, C32, C33]
    # print(LC3)

    C41 = math.cos(listPathPoints[3][0])
    C42 = math.cos(listPathPoints[3][1])
    C43 = math.cos(listPathPoints[3][2])
    LC4 = [C41, C42, C43]
    # print(LC4)

    C51 = math.cos(listPathPoints[4][0])
    C52 = math.cos(listPathPoints[4][1])
    C53 = math.cos(listPathPoints[4][2])
    LC5 = [C51, C52, C53]
    # print(LC5)

    C61 = math.cos(listPathPoints[5][0])
    C62 = math.cos(listPathPoints[5][1])
    C63 = math.cos(listPathPoints[5][2])
    LC6 = [C61, C62, C63]
    # print(LC6)

    C71 = math.cos(listPathPoints[6][0])
    C72 = math.cos(listPathPoints[6][1])
    C73 = math.cos(listPathPoints[6][2])
    LC7 = [C71, C72, C73]
    # print(LT7)

    C81 = math.cos(listPathPoints[7][0])
    C82 = math.cos(listPathPoints[7][1])
    C83 = math.cos(listPathPoints[7][2])
    LC8 = [C81, C82, C83]
    # print(LC8)

    C91 = math.cos(listPathPoints[8][0])
    C92 = math.cos(listPathPoints[8][1])
    C93 = math.cos(listPathPoints[8][2])
    LC9 = [C91, C92, C93]
    # print(LC9)

    # Used --> Geom.OrientProfile() but can also use --> Geom.AlignProfile()
    # Not entirely sure what it does tho...
    Geom.OrientProfile('1ctps', listPathPoints[0], LT1, LC1, 'newOrient1')
    Geom.OrientProfile('2ctps', listPathPoints[1], LT2, LC2, 'newOrient2')
    Geom.OrientProfile('3ctps', listPathPoints[2], LT3, LC3, 'newOrient3')
    Geom.OrientProfile('4ctps', listPathPoints[3], LT4, LC4, 'newOrient4')
    Geom.OrientProfile('5ctps', listPathPoints[4], LT5, LC5, 'newOrient5')
    Geom.OrientProfile('6ctps', listPathPoints[5], LT6, LC6, 'newOrient6')
    Geom.OrientProfile('7ctps', listPathPoints[6], LT7, LC7, 'newOrient7')
    Geom.OrientProfile('8ctps', listPathPoints[7], LT8, LC8, 'newOrient8')
    Geom.OrientProfile('9ctps', listPathPoints[8], LT9, LC9, 'newOrient9')

    # Creating values to loft solid
    objName = str(newObjectName)
    numSegsAlongLength = 30
    numPtsInLinearSampleAlongLength = 240 # Referenced elsewhere? In LoftSolid function? No other mention in scripting
    numLinearSegsAlongLength = 120
    numModes = 20
    useFFT = 0
    useLinearSampleAlongLength = 1
    Geom.LoftSolid(srcList, objName, numSegs, numSegsAlongLength, numLinearSegsAlongLength, numModes, useFFT, useLinearSampleAlongLength)

    # Importing PolyData from solid to repository
    GUI.ImportPolyDataFromRepos(str(newObjectName))

    # Adding caps to model
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
    print('Caps added to model')
    return

# Mesh:
def makeMesh(vtpFile, vtkFile):
    # Meshing object
    MeshObject.SetKernel('TetGen')
    msh = MeshObject.pyMeshObject()
    msh.NewObject('newMesh')
    solidFn = os.getcwd() + '/' + str(vtpFile)
    msh.LoadModel(solidFn)
    msh.NewMesh()
    msh.SetMeshOptions('SurfaceMeshFlag',[1])
    msh.SetMeshOptions('VolumeMeshFlag',[1])
    msh.SetMeshOptions('GlobalEdgeSize',[0.25])
    msh.SetMeshOptions('MeshWallFirst',[1])
    msh.GenerateMesh()
    os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Simulations')
    fileName = os.getcwd() + "/" + str(vtkFile)
    msh.WriteMesh(fileName)
    msh.GetUnstructuredGrid('Mesh')
    Repository.WriteVtkUnstructuredGrid("Mesh","ascii",fileName)
    GUI.ImportUnstructedGridFromRepos('Mesh')
    print('Mesh generated')
    return

# preSolver:
def runpreSolver(svFile):
    # Running preSolver from created model
    try:
        os.system('/usr/local/sv/svsolver/2019-01-19/svpre' + str(svFile)) # Change the filename
        print('Running preSolver')
    except:
        print('Unable to run preSolver')
    return

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Gather path points to use contour
def gatherPoints(segFile):
    try:
        inputFile = open(segFile+'.ctgr', 'r')
    except:
        print("Unable to open given .ctgr file")
        return

    # Array of lists to store points
    segsData = []
    count = 0

    # Reading in points, making note of control vs contour points
    # Copy and save data to the pointsData list
    for iteration in inputFile:
        if "<pos" in iteration:
            segsData.append(re.findall('"([^"]*)"', iteration)) # Obtaining center data for each segment
    segsData = numpy.array(segsData)
    segsData = segsData.astype(numpy.float)
    return segsData

####################################################
#                   Main                           #
####################################################

# Importing required repos
import os
from sv import *

# os.chdir('/usr/local')
import sys
import numpy
from numpy import genfromtxt
import pdb
import re
import math
import os.path
import operator

# Clearing repository of '_____', else gives error of duplicates (Still no way to remove from GUI tho so I still have issues)
objs = Repository.List()
for name in objs:
    Repository.Delete(name)

# Gathering points from given model
os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Segmentations')
pathPoints = gatherPoints('LPA_main')
listPathPoints = pathPoints.tolist() # Conversion from numpy array to python list to allow for valid makePath function call
# print(listPathPoints)
makePath(listPathPoints, 'LPA_main_copy', 'LPA_copy_Segment', 0.35)

# Stenosis function call
os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Segmentations')
alteringStenosis('LPA_main', 75, '2')
print('Stenosis applied \n')

# Contour function call
print('Create new contour: \n')
os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Models')
print('Current directory: ' + os.getcwd())
makeContour('LPA_newCont', 'LPA_newModel')

# Mesh function call
print('Create new mesh: \n')
os.chdir('/Users/tobiasjacobson/Documents/Atom/genStenosis/Models')
makeMesh('LPA_newCont.vtp', 'LPA_newContOutFile.vtk')

# preSolver function call
# print('Running preSolver: \n')
# runpreSolver('idealSim2.svpre')
