# Objective: Generate solver.inp and presolver.svpre files in a user friendly and efficient manner
#   -This will include boundary conditions (For now assume steady flow file)
# Application(s): Cylindrical Models with boundary conditions

# NOTES:
#   - Only passing fileName.svpre file

class autoPre:
    def __init__(self, preFile):
        self.preFile = preFile
    def readPre(self):
        print("Hello my name is " + self.name + "\n")
        f = open(self.preFile)
        lines = f.readlines()
        f_Density = lines[4]
        f_Viscosity = lines[5]
        i_Pressure = lines[6]
        i_Velocity = lines[7]
        modelShape = lines[9]
        modelPeriod = lines[10]
        modelPointNumber = lines[11]
        modelFourierModeNum = lines[12]
        f.close()
        # Check to see if values have been
        print 'Fluid Density: ' + f_Density
        print 'Fluid Viscosity: ' + f_Viscosity
        print 'Initial Pressure: ' + i_Pressure
        print 'Initial Velocity: ' + i_Velocity
        print 'Shape: ' + modelShape
        print 'Period: ' + modelPeriod
        print 'Point Number: ' + modelPointNumber
        print 'Fourier Number: ' + modelFourierModeNum

        # mesh_and_adjncy_vtu(cylSim.svpre)
        bct_merge_on()
        noslip_vtp("bct.vtp")
        prescribed_velocities_vtp("bct.vtp")
        if not pressure:
            zero_pressure_vtp("bct.vtp")
        if pressure:
            pressure_vtp("")

###########
# from sv import *
# fileR("/Users/tobiasjacobson/Documents/Atom/preScripting/cylTest/Simulations/cylSim/cylSim.svpre")
# fileR("/Users/tobiasjacobson/Documents/Atom/preScripting/PT2_3Y_04.svpre")


#####################################################
#                   Main                           #
####################################################
import os
from sv import *
aP = autoPre("/Users/tobiasjacobson/Documents/Atom/preScripting/cylTest/Simulations/cylSim/cylSim.svpre") #/usr/local/sv/svsolver/2019-01-19/svpre) #PT2_3Y_04.svpre)
aP.readPre()