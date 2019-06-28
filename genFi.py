# Objective: Generate solver.inp and presolver.svpre files in a user friendly and efficient manner
#   -This will include boundary conditions (For now assume steady flow file)
# Application(s): Cylindrical Models with set boundary conditions (For Now)


#####################################################
#                      Func Def                     #
#####################################################
def generateDefault():
    print("\n")
    ############# First check whether files already exist, if so, remove them from cwd #############
    # # Test cases
    # if os.path.exists('./fileTest.txt'):
    #     print('removing previously existing fileTest.txt')
    #     os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/fileTest.txt')
    # if os.path.exists('./cylinderSim.txt'):
    #     print('removing previously existing cylinderSim.txt')
    #     os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/cylinderSim.txt')
    # Real cases
    if os.path.exists('./cylinderSim.svpre'):
        print('removing previously existing cylinderSim.svpre')
        os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/cylinderSim.svpre')
    if os.path.exists('./solver.inp'):
        print('removing previously existing solver.inp')
        os.remove('/Users/tobiasjacobson/Documents/Atom/preScripting/solver.inp')
    ############# generate solver.inp file #############
    f = open("solver.inp", "a+") # Real case
    # f = open("fileTest.txt", "a+") # Test case
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
    pre = open("cylinderSim.svpre", "a+") # Real case
    # pre = open("cylinderSim.txt", "a+") # Test case
    preContent = ["mesh_and_adjncy_vtu ./mesh-complete/mesh-complete.mesh.vtu",\
    "set_surface_id_vtp mesh-complete/walls_combined.vtp 1", "set_surface_id_vtp mesh-complete/mesh-surfaces/cap_segment1.vtp 2",
    "set_surface_id_vtp mesh-complete/mesh-surfaces/cap_segment1_2.vtp 3", "fluid_density 1.06", "fluid_viscosity 0.04", "initial_pressure 0", \
    "initial_velocity 0.0001 0.0001 0.0001", "bct_analytical_shape parabolic", "bct_period 1.0", "bct_point_number 2", "bct_fourier_mode_number 1","bct_merge_on", \
    "bct_create ./mesh-complete/mesh-surfaces/cap_segment1.vtp cap_segment1.flow", "bct_write_dat", "bct_write_vtp", "write_geombc ./geombc.dat.1", \
    "write_restart ./restart.0.1", "write_numstart 0", "prescribed_velocities_vtp ./mesh-complete/mesh-surfaces/cap_segment1.vtp", \
    "pressure_vtp ./mesh-complete/mesh-surfaces/cap_segment1_2.vtp 0", "noslip_vtp ./mesh-complete/walls_combined.vtp"]
    for newTxt in range(len(preContent)):
        pre.write(preContent[index2] + "\n")
        index2 += 1
    ############# Altering files #############
    print("[cylinderSim.svpre] && [solver.inp] generated sucessfully")
    print("To alter a file, enter 'nano' followed by the name of the file you want to change") # Would use Atom but not all would have it
    print("To see contents of the current directory type 'ls' ")


#####################################################
#                   Main                           #
####################################################

# Imports needed
import os
import fileinput
import sys
# Moving from root directory to desired directory
os.chdir('/Users/tobiasjacobson/Documents/Atom/preScripting')
# Actual function call
generateDefault()

