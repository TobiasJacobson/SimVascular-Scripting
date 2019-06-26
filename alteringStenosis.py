# Objective: Write script to load previously existing SimVascular files and generate
#           a stenosis percentage based on user input
# Inputs: .ctgr file (The SVC contour section of artery), percent stenosis, and contour group to apply stenosis


############################
# Structure:
#   - Read .ctgr file && find desired contour contourGroup
#   - Read in points from the .ctgr file, note wich are control and contour
#   - Find efficient way to alter segment size based on percentage input. (Erica rotate to 2D, better way??) (Convex hull,
#       Sum(Area of triangles) but only if ordered lists, if no geometric relation resort to brute force)
#   - If all goes well -> Reconfigure file and run preSolver, solver and post process??????
############################


#####################################################
#                      Func Def                     #
#####################################################

def alteringStenosis(fileName, percentage, contourGroup):
    # Open .ctgr file and create new output file to read to
    inFile = open(fileName+'.ctgr', 'r')
    outFile = open(fileName+str(percentage)+'.ctgr','w+')
    data =[]
    # Iterate through given .ctgr file until desired segmentation is reached (i.e contourGroup is found)
    for seg in inFile:
        # print seg
        if '<contour id=\"'+str(contourGroup)+'\"' in seg:
            outFile.write(seg)
            break
        else:
            outFile.write(seg)


    # Reading in points, making note of control vs contour points
    pointsData = []


    for iteration in inFile:
        # print iteration
        if "<control_points>" in iteration:
            break
        else:
            outFile.write(iteration)

    for iteration in inFile:
        # print iteration
        if "</control_points>" in iteration:
            break
        else:
            data.append(re.findall('"([^"]*)"', iteration)) # ^ signifies start of string, * RE matches 0 or more (ab* will match 'a','ab' or 'abn'
                                                            # where n is n number of b's following), [] indicates a set of special characters

    # Takes actual integers from segment to alter and adds to pointsData
    count = 0
    for iteration in inFile:
        # print iteration
        if "</contour_points>" in iteration:
            break
        else:
            if count == 0: # B/C otherwise first item in list is always a blank for some reason
                count += 1
            else:
                stringLine = iteration
                pointsData.append(re.findall('"([^"]*)"', stringLine))
                outFile.write(iteration)

    # Adding rest of inFile to outFile
    for iteration in inFile:
        # print iteration
        stringRest = iteration
        outFile.write(stringRest)
        data.append(re.findall('"([^"]*)"', iteration))


    # Alter segment size based on percentage input -----------------

    ################################## Creating matrix cVdataTranspose, i.e main matrix ##################################
    # List of ones to be appended to pointsData matrix
    onesArr = numpy.ones(43)
    # Converting pointsData to float, removing first column b/c they only store indicies therefore aren't needed
    cVdata = numpy.array(pointsData)
    cVdata = cVdata.astype(numpy.float)
    cVdata = cVdata[:,1:]
    # Appending onesArr to pointsData
    cVdata = numpy.concatenate((cVdata,onesArr[:,None]), axis=1)
    # cVdata = numpy.c_[cVdata, onesArr] # Another way to append onesArr
    # print(cVdata) # Check if its been added
    # Transpose data for matrix multiplication
    cVdataTranspose = numpy.transpose(cVdata)
    # print cVdataTranspose # Check if its been transposed correctly
    ######################################################################################################################

    ################################## Creating overal matrix of scalar, translation, and inverse translation ##################################
    # Hard coded for now
    centerData = [-1.90810359169811, 10.874778040444664, 20.961486548177369, 1]
    factor = math.sqrt(percentage/100.0)
    # Creating Scalar Matrix (with scalar as percent stenosis given)
    scalarMatrix = [[factor, 0, 0, 0], [0, factor, 0, 0], [0, 0, 0, factor, 0], [0, 0, 0, 1]]
    # Creating Translation Matrix
    translationMatrix = [[1, 0,0, 1.90810359169811], [0, 1, 0, -10.874778040444664], [0, 0, 1, -20.961486548177369], [0, 0, 0, 1]]
    # Creating Inverse Translation matrix
    invTranslationMatrix = [[1, 0,0, -1.90810359169811], [0, 1, 0, 10.874778040444664], [0, 0, 1, 20.961486548177369], [0, 0, 0, 1]]
    # Overall Matrix created
    matrixMain = numpy.matmul(scalarMatrix, translationMatrix)
    matrixMainTwo = numpy.matmul(matrixMain, invTranslationMatrix)
    print matrixMain
    ############################################################################################################################################

    # Matrix multiplication of cVdataTranspose and dataMatrix (43x4 matrix and a 4x4 matrix leaves a 43sx4) # Note: have to left  multiply with dataMatrix
    newPointsData = numpy.matmul(matrixMain, cVdataTranspose)
    # newPointsData = newPointsData[:-1,:] # Removes ones from bottom of matrix
    # print newPointsData # Check if matricies have been multiplied correctly


    # scaledData = numpy.dot(newPointsData, scalarMatrix)
    scaledData = numpy.dot(newPointsData, scalarMatrix)
    # scaledData = numpy.multiply(newPointsData, factor)
    print scaledData

    return # End of function


#####################################################
#                   Main                           #
####################################################


# Importing required repos
import sys
import numpy  #as np
import math
from numpy import genfromtxt
import pdb
import re
import math


# Initializing data for function call
filename = "SVCTest" # File to be read from (i.e. 0% stenosis .ctgr file)
contourGroup = 2 # Contour group to be altered (i.e. Where stenosis is applied)
percentage = 60 # Desired Stenosis percentage

# Function call
alteringStenosis(filename, percentage, contourGroup)
