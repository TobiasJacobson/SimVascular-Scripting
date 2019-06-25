# Objective: Write script to load previously existing SimVascular files and generate
#           a stenosis percentage based on user input
# Inputs: .ctgr file (The SVC contour section of artery)

import numpy  #as np

############################
# Structure:
#   - Read .ctgr file && find desired contour contourGroup
#   - Read in points from the .ctgr file, note wich are control and contour
#   - Find efficient way to alter segment size based on percentage input. (Erica rotate to 2D, better way??) (Convex hull,  Sum(Area of triangles) but only if ordered lists, if no geometric relation resort to brute force)
#   - If all goes well -> Reconfigure file and run preSolver, solver and post process??????
############################


#####################################################
#                      Func Def                     #
#####################################################
def multiply(v, G):
    result = []
    for i in range(len(G[0])): #this loops through columns of the matrix
        total = 0
        for j in range(len(v)): #this loops through vector coordinates & rows of matrix
            total += v[j] * G[j][i]
        result.append(total)
    return result



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
            data.append(re.findall('"([^"]*)"', iteration)) # ^ signifies start of string, * RE matches 0 or more (ab* will match 'a','ab' or 'abn' where n is n number of b's following), [] indicates a set of special characters

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


    # Alter segment size based on percentage input ---

    # Gather points from SVC file in --- Hard code for now
    centerData = [-1.90810359169811, 10.874778040444664, 20.961486548177369, 1]
    # Hard code for now
    pData = [[1, 0,0, -1.90810359169811], [0, 1, 0, 10.874778040444664], [0, 0, 1, 20.961486548177369], [0, 0, 0, 1]]

    # List of ones to be appended to pointsData
    onesArr = numpy.ones(43)

    # Converting points data to float, removing first column b/c they only store indicies
    cFdata = numpy.array(pointsData)
    cFdata = cFdata.astype(numpy.float)
    cFdata = cFdata[:,1:]

    # Transpose data for matrix mult.
    numpy.transpose(cFdata)
    

    # Appending onesArr to pointsData
    cFdata = numpy.concatenate((cFdata,onesArr[:,None]),axis=1)
    # cFdata = numpy.c_[cFdata, onesArr]
    print(cFdata) # Check if its been added

    # newPointsData = numpy.matmul(pointsData, centerData)
    # newPointsData = numpy.matmul(cFdata, centerData)

    # ---------- Checks for data ----------
    # for line in newPointsData:
    #     print line

    # for i in range(43):
    #     print pointsData[i]

    # for r in range(42):
    #     print cFdata[r]
    # -------------------------------------
    return



# Importing required repos
import sys
import numpy  #as np
import math
from numpy import genfromtxt
import pdb
import re
filename = "SVCTest"
contourGroup = 2
percentage = 60
alteringStenosis(filename, percentage, contourGroup)
