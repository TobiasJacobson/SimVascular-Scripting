# Objective: Write script to load previously existing SimVascular files and generate
#           a stenosis percentage based on user input
# Inputs: .ctgr file (The SVC contour section of the artery), percent stenosis, and contour group to apply stenosis

#####################################################
#                      Func Def                     #
#####################################################

def alteringStenosis(fileName, percentage, contourGroup):
    # Open .ctgr file and create new output file to write to
    inFile = open(fileName+'.ctgr', 'r')
    outFile = open(fileName+'-'+str(contourGroup)+'-'+str(percentage)+'.ctgr','w+')
    print('Creating: ' + fileName + '-' + str(contourGroup) + '-' + str(percentage) + '.ctgr')

    ###################### Reading input file and copying information until contour section is reached ######################
    # Iterate through given .ctgr file until desired segmentation is reached (i.e contourGroup is found)
    for seg in inFile:
        if '<contour id=\"'+str(contourGroup)+'\"' in seg: # If found, break
            outFile.write(seg) # Write contour ID line to outFile
            break
        else:
            outFile.write(seg) # Else a write to file

    # Will store center data for desired segment
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

    # Array/Matrix to store points
    pointsData = []
    data =[] # Not really used besides in this section...

    # ^ signifies start of string, * RE matches 0 or more (ab* will match 'a','ab' or 'abn' where n is n number of b's following), [] indicates a set of special characters
    for iteration in inFile:
        if "</control_points>" in iteration:
            break
        else:
            pointsData.append(re.findall('"([^"]*)"', iteration))

    # Stores ...
    ct = int(pointsData[-1][0])

    # Takes the actual integers from segment to alter and copies them to pointsData
    count = 0
    for iteration in inFile:
        if "</contour_points>" in iteration:
            break
        else:
            if count == 0: # B/C otherwise first item in list is always a blank for some reason
                count += 1
            else:
                stringLine = iteration
                pointsData.append(re.findall('"([^"]*)"', stringLine))
                # outFile.write(iteration) # This wrote original contour group 2 data to outfle...

    #########################################################################################################################


    ################################## Creating matrix called cVdataTranspose, i.e main matrix #################################
    # List of ones to be appended to pointsData matrix
    onesArr = numpy.ones(45)

    # Converting pointsData to type: float, removing first column b/c it only contains indicies therefore isn't needed
    cVdata = numpy.array(pointsData)
    cVdata = cVdata.astype(numpy.float)
    cVdata = cVdata[:,1:]

    # Appending onesArr to pointsData
    cVdata = numpy.concatenate((cVdata,onesArr[:,None]), axis=1)
    # cVdata = numpy.vstack((cVdata, onesArr)) # Another way to append onesArr
    # cVdata = numpy.c_[cVdata, onesArr] # Another way to append onesArr

    # Transpose data for matrix multiplication
    cVdataTranspose = numpy.transpose(cVdata)
    # print cVdataTranspose

    ############################################################################################################################


    ################################## Creating overal matrix of scalar, translation, and inverse translation ##################################
    # Hard coded center for segment 2
    # centerData = [-1.90810359169811, 10.874778040444664, 20.961486548177369, 1]

    # Converting foundCenterPoints to floats and stored in centerData
    centerData = numpy.array(foundCenterPoints)
    centerData = centerData.astype(numpy.float)
    # centerData = numpy.append(centerData, oneList)
    print 'Center Found At: ' + str(centerData)
    cdOne = centerData[0][0]
    cdTwo = centerData[0][1]
    cdThree = centerData[0][2]
    # print cdOne
    # print cdTwo
    # print cdThree

    # Setting factor based on users input
    factor = math.sqrt(abs(percentage-100)/100.0) # Without abs(x-100) stenosis goes as 5 in mine = 95 applied, 40 in mine = 60 applied

    # Creating Scalar Matrix (with scalar as percent stenosis given)
    scalarMatrix = [[factor, 0, 0, 0], [0, factor, 0, 0], [0, 0, factor, 0], [0, 0, 0, 1]]

    # Creating Translation Matrix
    translationMatrix = [[1, 0,0, -cdOne], [0, 1, 0, -cdTwo], [0, 0, 1, -cdThree], [0, 0, 0, 1]]

    # Creating Inverse Translation matrix
    invTranslationMatrix = [[1, 0,0, cdOne], [0, 1, 0, cdTwo], [0, 0, 1, cdThree], [0, 0, 0, 1]]

    # Overall Matrix created
    matrixS = numpy.matmul(invTranslationMatrix, scalarMatrix)
    matrixMain = numpy.matmul(matrixS, translationMatrix)
    # import pdb; pdb.set_trace() # Needed for debugging
    # print matrixMain

    ############################################################################################################################################

    # Matrix multiplication of cVdataTranspose and dataMatrix (43x4 matrix and a 4x4 matrix leaves a 43x4) # Note: have to left multiply with dataMatrix
    newPointsData = numpy.matmul(matrixMain, cVdataTranspose)
    # print newPointsData
    newPointsData = newPointsData[:-1,:] # Removes ones from bottom of matrix
    # Transposed scaled data back to original form
    newDataTpose = numpy.transpose(newPointsData)
    # print newDataTpose

    # Adding control points to the outFile
    outFile.write('            <control_points>\n')
    for i in xrange(ct+1):
        dl = newDataTpose[i,:]
        fStr = '<point id=\"{}\" x=\"{}\" y=\"{}\" z=\"{}\" />\n'.format(i,dl[0],dl[1],dl[2])
        outFile.write('                '+fStr)
    outFile.write('            </control_points>\n')

    # Adding contour points to the outFile
    outFile.write('            <contour_points>\n')
    for i in xrange(ct+1, numpy.shape(newDataTpose)[0]):
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


####################################################
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
import os.path

# Initializing for function call
fileInput = raw_input("Enter the name of the file to be read from: \n")
contourInput = raw_input("Enter the number of the contour you'd like to change: \n")
percentInput = raw_input("What percent stenosis are you applying: \n")

# Function call
alteringStenosis(fileInput, float(percentInput), contourInput)
