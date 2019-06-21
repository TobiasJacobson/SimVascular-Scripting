# Objective: Write script to load previously existing SimVascular files and generate
#           a stenosis percentage based on user input
# Inputs: .ctgr file (The SVC contour section of artery)

# Importing required repos
import sys
import numpy as np
from numpy import genfromtxt
import pdb
import numpy as np
import re


############################
# Structure:
#   - Read .ctgr file && find desired contour contourGroup
#   - Read in points from the .ctgr file, note wich are control and non-control
#   - Find efficient way to alter segment size based on % input. (Erica rotate to 2D, better way??) (Convex hull,  Σ(Area of triangles) but only if ordered lists, if no geometric relation resort to brute force)
#   - If all goes well -> Reconfigure file and run preSolver, solver and post process??????
############################


#####################################################
#                      Func Def                     #
#####################################################
def alteringStenosis(fileName, percentage, contourGroup):
    # Read .ctgr file and create new output file to read to
    inFile = open(filename+'.ctgr', 'r')
    outFile = open(filename+str(int((1-st)*100))+'.ctgr','w+')

    # Iterate through given .ctgr file until desired segmentation is reached (i.e contourGroup is found)
    for seg in inFile:
        if '<contour id=\"'+str(contourGroup)+'\"' in seg:
            outFile.write(seg)
            break
        else:
            outFile.write(seg)


    # Read in points
    pointsList = [] # List of the points to be read from thecontour ID
    for iteration in inFile:
        if "<control_points>" in iteration:
            break
        else:
            outFile.write(iteration)

    for iteration in inFile:
        if "</control_points>" in iteration:
            break
        else:
            pointList.append(re.findall('"([^"]*)"', iteration)) # ^ signifies start of string, * RE matches 0 or more (ab* will match 'a','ab' or 'abn' where n is n number of b'es following )

    index = int(data[-1][0])

    for iteration in inFile:
        if "</contour_points>" in iteration:
            break
        else:
            outFile.write(iteration)

    for iteration in inFile:
        if "<contour_points>" in iteration:
            break
        else:
            pointList.append(re.findall('"([^"]*)"', iteration))


















            #
