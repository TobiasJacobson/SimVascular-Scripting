# Objective: Write script to load previously existing SimVascular files and generate
#           a stenosis percentage based on user input
# Inputs: .ctgr, file percent stenosis, and contour group to apply stenosis

#####################################################
#                      Func Def                     #
#####################################################

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
    print 'Center Found At: ' + str(centerData) # Can be used to validate

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

    ##################################################################################################################################################################

    # Matrix multiplication of cVdataTranspose and dataMatrix -- Note: have to left multiply with dataMatrix
    newPointsData = numpy.matmul(matrixMain, cVdataTranspose)
    # print newPointsData # Used to check values of newPointsData
    newPointsData = newPointsData[:-1,:] # Removes all ones from bottom of matrix
    # Transposed scaled data back to original form
    newDataTpose = numpy.transpose(newPointsData)
    # print newDataTpose # Used to check values of newDataTpose

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
import numpy
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
