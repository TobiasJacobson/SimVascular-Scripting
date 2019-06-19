

def generateDefault():
    ############# First check whether files already exist, if so, remove them from cwd #############
    if os.path.exists('./fileTest1.txt'):
        print('removing fileTest1.txt')
        os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/fileTest1.txt')
    if os.path.exists('./fileTest.txt'):
        print('removing fileTest.txt')
        os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/fileTest.txt')
    if os.path.exists('./cylinderSim.txt'):
        print('removing cylinderSim.txt')
        os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/cylinderSim.txt')
    if os.path.exists('./cylinderSim1.txt'):
        print('removing cylinderSim1.txt')
        os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/cylinderSim1.txt')
    # if os.path.exists('./solver.inp'):
    #     print('removing /solver.inp')
    #     os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/solver.inp')
    ############# generate solver.inp file #############
    # f = open("solver.inp", "a+")
    f = open("fileTest.txt", "a+")
    fileContent = ["Density: ", "Viscosity: ", " ", "Number of Timesteps: ", "Time Step Size: ", " ", "Number of Timesteps between Restarts: ", \
     "Number of Force Surfaces: ", "Surface ID's for Force Calculation: ", "Force Calculation Method: ", "Print Average Solution: ", \
     "Print Error Indicators: ", " ", "Time Varying Boundary Conditions From File: ", " ", "Step Construction: ", " ", \
     "Number of Resistance Surfaces: ", "List of Resistance Surfaces: ", "Resistance Values: ", " ", "Pressure Coupling: ", \
     "Number of Coupled Surfaces: ", " ", "Backflow Stabilization Coefficient: ", "Residual Control: ", "Residual Criteria: ", "Minimum Required Iterations: ", \
     "svLS Type: ", "Number of Krylov Vectors per GMRES Sweep: ", "Number of Solves per Left-hand-side Formation: ", "Tolerance on Momentum Equations: ", \
     "Tolerance on Continuity Equations: ", "Tolerance on svLS NS Solver: ", "Maximum Number of Iterations for svLS NS Solver: ", "Maximum Number of Iterations for svLS Momentum Loop: ", \
     "Maximum Number of Iterations for svLS Continuity Loop: ", "Time Integration Rule: ", "Time Integration Rho Infinity: ", "Flow Advection Form: ", \
     "Quadrature Rule on Interior: ", "Quadrature Rule on Boundary: "]

    defaultFile = ["1.06", "0.04", " ", "100", "0.0004", " ", "10", "1", "1", "Velocity Based", "True", "False", " ", "True", " ", "1 2 3 4", " ", \
     "1", "3", "16000", " ", "Implicit", "1", " ", "0.2", "True", "0.01", "3", "NS", "100", "1", "0.05", "0.4", "0.4", "1", "2", "400", "Second Order", \
     "0.5", "Convective", "2", "3"]
    index1 = 0
    index2 = 0
    for txt in range(len(fileContent)):
        f.write(fileContent[index1] + defaultFile[index1] + "\n")
        index1 += 1
    f.close()
    ############# generate filename.svpre file #############
    # pre = open("cylinderSim.svpre", "a+")
    pre = open("cylinderSim.txt", "a+")
    preContent = ["mesh_and_adjncy_vtu mesh-complete/mesh-complete.mesh.vtu", "set_surface_id_vtp mesh-complete/mesh-complete.exterior.vtp 1", \
    "set_surface_id_vtp mesh-complete/mesh-surfaces/cap_segment1.vtp 2", "set_surface_id_vtp mesh-complete/mesh-surfaces/cap_segment1_2.vtp 3", \
    "fluid_density 1.06", "fluid_viscosity 0.04", "initial_pressure 0", "initial_velocity 0.0001 0.0001 0.0001", \
    "prescribed_velocities_vtp mesh-complete/mesh-surfaces/cap_segment1.vtp", "bct_analytical_shape parabolic", "bct_period 1.0", \
    "bct_point_number 2", "bct_fourier_mode_number 1", "bct_create mesh-complete/mesh-surfaces/cap_segment1.vtp cap_segment1.flow", \
    "bct_write_dat bct.dat", "bct_write_vtp bct.vtp", "pressure_vtp mesh-complete/mesh-surfaces/cap_segment1_2.vtp 0", \
    "noslip_vtp mesh-complete/walls_combined.vtp", "write_geombc geombc.dat.1", "write_restart restart.0.1"]
    for newTxt in range(len(preContent)):
        pre.write(preContent[index2] + "\n")
        index2 += 1
    ############# Altering files #############

    keepChange = 1
    while keepChange:
        userInp = raw_input('Would you like to alter any files? (Y/N)\n')
        if userInp == 'yes' or userInp == 'y' or userInp == "Yes" or userInp == 'Y':
            fileInp = raw_input("Enter the name of the file you'd like to change: [the solver.inp] [cylinderSim.svpre] \n")
            if (fileInp == 'solver.inp'):
                with open('/Users/tobiasjacobson/Documents/Atom/preScripting/fileTest.txt') as pr:
                    content = pr.readlines()
                    for thing in content:
                        sys.stdout.write(thing)
                    with open('fileTest.txt') as myfile:
                        newChange = 1
                        while newChange:
                            alterFile = raw_input("Which line will you change?\n")
                            if alterFile in myfile.read():
                                addFile = raw_input("What will you replace it with?\n")
                                fin = open("fileTest.txt")
                                fout = open("fileTest.txt", "wt")
                                # fin = open("solver.inp")
                                # fout = open("solver.inp1", "wt")
                                for line in fin:
                                    fout.write( line.replace(alterFile, addFile) )
                                fin.close()
                                fout.close()
                                # os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/fileTest.txt')
                                # os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/solver.inp')
                                newChange = 0
                                print('File altered')
                            else:
                                print('Line does not exist')
            elif (fileInp == 'cylinderSim.svpre'):
                with open('/Users/tobiasjacobson/Documents/Atom/preScripting/cylinderSim.txt') as fr:
                    content2 = fr.readlines()
                    for thing2 in content2:
                        sys.stdout.write(thing2)
                    alterFile2 = raw_input("Which line will you change?\n")
                    addFile2 = raw_input("What will you replace it with?\n")
                    fin = open("cylinderSim.txt")
                    fout = open("cylinderSim1.txt", "wt")
                    # fin = open("cylinderSim.svpre")
                    # fout = open("cylinderSim1.svpre", "wt")
                    for line in fin:
                        fout.write( line.replace(alterFile2, addFile2) )
                    fout.close()
                    # os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/cylinderSim.txt')
                    fin.close()
                    # os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/cylinderSim.svpre')
                    print('File altered')
            else:
                print('Not a valid file')
        elif userInp == 'n' or userInp == 'No' or userInp == 'no' or userInp == 'N':
            print('Program Exited')
            keepChange = 0
        else:
            print('Not a valid input')
    pre.close()

###############################
#             Main            #
###############################

import os
import fileinput
import sys
# Moving from root directory to desired directory
os.chdir('/Users/tobiasjacobson/Documents/Atom/preScripting')
generateDefault()
