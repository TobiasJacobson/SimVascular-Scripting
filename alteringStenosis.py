# Previous Objective: Write script to load previously existing SimVascular files and generate
#           a stenosis percentage based on user input
# Current Objective: Write script for a complete pipeline that will: (1) Apply stenosis on existing model,
#           (2) Generate a new model based on stenosis (3) Generate a new mesh based on new model (4) Run presolver
# Inputs: .ctgr, file percent stenosis, and contour group to apply stenosis


# Global variables needed for other function calls
ctgrFile = ""
pathPoints = []
paths = []


#####################################################
#                      Func Def                     #
#####################################################

def alteringStenosis(fileName, percentage, contourGroup):
    # Check if given file exists in cwd
    try:
        inFile = open(fileName+'.ctgr', 'r')
        ctgrFile = fileName
    except:
        print("Unable to open given file")
        return

    # Check that given percent is valid (i.e. between 0-100)
    if percentage < 0 or percentage > 100:
        print('Percent given is not within a valid range')
        return

    # Once input file has been validated, then create output file
    outFile = open(fileName+'-'+str(contourGroup)+'-'+str(percentage)+'.ctgr','w+')

    ###################### Reading input file and copying information until contour section is reached ######################
    # Iterate through given .ctgr file until desired segmentation is reached (i.e contourGroup is found)
    found = False # Will be used to track whether contourGroup is found
    for seg in inFile:
        if '<contour id=\"'+str(contourGroup)+'\"' in seg: # If found, break after writing ID line to outFile
            outFile.write(seg) # Write contour ID line to outFile
            found = True # Validating that contourSegment was found
            break
        else:
            outFile.write(seg) # Else write to file
    if found == False:
        print('Segment does not exist in contour')
        return

    # Once segment has been validated, print creating...
    print('Creating: '+fileName+'-'+str(contourGroup)+'-'+str(percentage)+'.ctgr')

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

    #########################################################################################################################


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

    ############################################################################################################################


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

    #############################################################################################################################################################

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
        print(pathPoint)
        p.AddPoint(pathPoint)

    # Adding path to repository
    p.CreatePath()

    # Importing created path from repository to the 'Paths' tab in GUI
    GUI.ImportPathFromRepos(pathName)
    GUI.ImportPathFromRepos(pathName,'Paths')

    # Initializing variables and creating segmentations (Default to circle)
    Contour.SetContourKernel('Circle')
    pointsLength = len(pointsList)
    contourNameList = [pathName + 'ct1', pathName + 'ct2']

    #  Shortcut for function call Contour.pyContour(), needed when calling SimVascular functions
    c = Contour.pyContour()

    # Creating 2 control segmentations for caps of the cylinder
    c.NewObject(contourNameList[0], pathName, 0)
    c.SetCtrlPtsByRadius(pointsList[0], radius+1)
    c.Create()
    c.GetPolyData('1ctp')

    numTwo = p.GetPathPtsNum() # index at end of pointsList
    c2 = Contour.pyContour()
    c2.NewObject(contourNameList[1], pathName, numTwo-1)
    c2.SetCtrlPtsByRadius(pointsList[1], radius+1)
    c2.Create()
    c2.GetPolyData('2ctp')

    ## Attempt at creating systematic list of names (cct0, cct1, cct2, etc..) for individual points along path based on  pointsList length
    # index = 0
    # string = 'cct'
    # while index < (pointsLength):
    #     string += str(index)
    #     contourNameList.append(string)
    #     print(contourNameList[index])
    #     index += 1
    #
    # # create n number of objects based on pointsList length, adding each contour to repository
    # index = 0
    # while index < (pointsLength-1):
    #     c.NewObject(contourNameList[index], pathName, index)
    #     c.SetCtrlPtsByRadius(pointsList[index], radius)
    #     c.Create()
    #     index += 1

    # Importing contours from repository to 'Segmentations' tab in GUI
    GUI.ImportContoursFromRepos(contourName, contourNameList, pathName, 'Segmentations')

    return

# Model:
def makeContour(newObjectName, modelName, polyVtp):
    # Creating data to loft solid
    numSegs = 60 # Number of segments defaulted to 60

##################################################################################################################################################################
##################################################################################################################################################################
    # To-Do
    # Gather polyData : Seems to be in vtp file under 'Models' section

    # Issue: Current guess why it doesn't work, seems to be that no contour.pyContour exists previously or no getPolydata called.
    # Sol?: Create new path based on previously existing and call getPolyData?? Problem for another day

    # Declaring needed variables for lofting
    srcList = [] # contains SampleLoop generations

    # Loop SampleLoop and append cList
    Geom.SampleLoop(polyVtp, numSegs, polyVtp+'s')
    srcList.append(polyVtp+'s')

    # Loop AlignProfile for each set of two points
    # Aligning profiles to allow for lofting, meshing etc.
    for x in range(len(srcList)-1):
        Geom.AlignProfile(srcList[x], srcList[x+1], 'ct'+str(x)+'psa', 0)
##################################################################################################################################################################
##################################################################################################################################################################
    objName = str(newObjectName)
    numSegsAlongLength = 12
    numPtsInLinearSampleAlongLength = 240 # Referenced elsewhere? In LoftSolid function? No other mention in scripting
    numLinearSegsAlongLength = 120
    numModes = 20
    useFFT = 0
    useLinearSampleAlongLength = 1

    # Lofting solid using created values
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
    msh.SetMeshOptions('GlobalEdgeSize',[0.75])
    msh.SetMeshOptions('MeshWallFirst',[1])
    msh.GenerateMesh()
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
def gatherPointsForMesh(pthFile):
    try:
        inputFile = open(pthFile+'.pth', 'r')
    except:
        print("Unable to open given .pth file")
        return

    # Array of lists to store points
    pathsData = []

    # Reading in points, making note of control vs contour points
    for iteration in inputFile:
        if "<control_points>" in iteration:
            break

    # Copy and save data to the pointsData list
    for iteration in inputFile:
        if "</control_points>" in iteration:
            break
        else:
            line = re.findall('"([^"]*)"', iteration)
                                                    # '^' signifies start of string, '*' RE matches 0 or more (ab* will match 'a','ab' or 'abn'
            # line = map(float, line)                                      # where n is n number of b's following), [] indicates a set of special characters
            pathsData.append(line)
    pathsData = numpy.array(pathsData)
    pathsData = pathsData.astype(numpy.float)
    pathsData = pathsData[:,1:]
    print(pathsData)
    return pathsData

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


# while givePath == 'y' or givePath == 'Y' or givePath == 'yes' or givePath == 'Yes':
#     pth = input('Enter the .pth file to be read \n')
#     temp = gatherPointsForMesh(str(pth))
#     pathPoints.append(temp)
#     givePath = input('Do you want to enter another pth file? (y/n) \n')
#     if givePath == 'n' or givePath == 'N' or givePath == 'no' or givePath == 'No':
#         break
os.chdir('/Users/tobiasjacobson/Documents/Atom/preScripting/cylTest/Paths')
pathPoints = gatherPointsForMesh('path1')
listPathPoints = pathPoints.tolist()
# print(pathPoints)
# # print(pathPoints) # Check if points have been read correctly
makePath(listPathPoints, 'path1', 'newTest', 1)
#
# # Stenosis function call
# # os.chdir(str(simPath)+'/Segmentations')
# os.chdir('/Users/tobiasjacobson/Documents/Atom')
alteringStenosis('SVCTest', 75, '2')
print('Stenosis applied \n')
#
#
# # Contour function call
# print('Create new contour: \n')
# # Allow decision to alter lofting paramters? Use default
# # os.chdir('/Users/tobiasjacobson/Documents/Atom/preScripting/cylTest/Simulations/cylSim')
# # print('Current directory: ' + os.getcwd())
# # polyVtpList = []
# makeContour('testObj', 'testMod', 'cylDemo.vtp')

# Mesh function call
# print('Create new mesh: \n')
# Need vtp filename and vtk filename
# os.chdir('/Users/tobiasjacobson/Documents/Atom/preScripting/cylTest/Simulations/cylSim')
# makeMesh('cylinder', 'cylinder')

# preSolver function call
# print('Running preSolver: \n')
# runpreSolver('cylinderSim.svpre')
