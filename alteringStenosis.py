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
    pointsList = [] # List of the points to be read from thecontour ID
    pointsData = []

    # cCount = 0 # Count of the number of times "<contour_points>" occurs, keeps track of number of segments in a contour
        # ---> Don't actually need this becasue contourGroup says which one to change, no need to find the middle section for alterations

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

    # Takes actual integers from segment to alter
    for iteration in inFile:
        # print iteration
        if "</contour_points>" in iteration:
            break
        else:
            stringLine = iteration
            pointsData.append(re.findall('"([^"]*)"', stringLine))
            outFile.write(iteration)

    for iteration in inFile:
        # print iteration
        data.append(re.findall('"([^"]*)"', iteration))


    # Alter segment size ---
    # Checking other SVC alterations I see only mid segmentations being altered (B/c only 5 segments the stenosis occurs on the middle segment)

    # gather current points in 3xN matrix, scale by root(factor) which is 1xN, using the numpy.matmul(),
    # arguments are 2 arrays (matricies) and will return matrix of appropriate dimensions

    # Gather points from SVC file in ---
    # Hard coded for now
    centerData = [-1.90810359169811, 10.874778040444664, 20.961486548177369, 1]
    # Other points already collected

    # for line in pointsData:
    #     print line
    # for line in outFile:
    #     print line

    # Matric multiplication of centerData and pointsData returned to create newPointsData
    newPointsData = numpy.matmul(pointsData, centerData)
    for line in newPointsData:
        print line

    return



# Importing required repos
import sys
import numpy  #as np
from numpy import genfromtxt
import pdb
import re
filename = "SVCTest"
contourGroup = 2
percentage = 60
alteringStenosis(filename, percentage, contourGroup)
