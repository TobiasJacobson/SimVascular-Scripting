# Objective: Generate solver.inp and presolver.svpre files in a user friendly and efficient manner
#   -This will include boundary conditions (For now assume steady flow file)
# Application(s): Cylindrical Models with set boundary conditions (For Now)

# NOTES:
#   - Only passing fileName.svpre file

#####################################################
#                Class && Func Def                  #
#####################################################
class autoPre:
    def __init__(self, preFile):
        self.preFile = preFile
    def readPre(self):
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
        # Obtaining BCT values
        # print 'Fluid Density: ' + f_Density
        # print(f_Density.lstrip('fluid_density '))
        f_Density = f_Density.lstrip('fluid_density ')
        # print 'Fluid Viscosity: ' + f_Viscosity
        # print(f_Viscosity.lstrip('fluid_viscosity '))
        f_Viscosity = f_Viscosity.lstrip('fluid_viscosity ')
        # print 'Initial Pressure: ' + i_Pressure
        # print(i_Pressure.lstrip('initial_pressure '))
        initial_pressure = i_Pressure.lstrip('initial_pressure ')
        # print 'Initial Velocity: ' + i_Velocity
        # print(i_Velocity.lstrip('initial_velocity '))
        i_Velocity = i_Velocity.lstrip('initial_velocity ')
        # print 'Shape: ' + modelShape
        modelShape = modelShape.lstrip('bct_analytical_shape')
        modelShape = modelShape.lstrip()
        # print(modelShape)
        # print 'Period: ' + modelPeriod
        # print(modelPeriod.lstrip('bct_period '))
        modelPeriod = modelPeriod.lstrip('bct_period ')
        # print 'Point Number: ' + modelPointNumber
        # print(modelPointNumber.lstrip('bct_point_number '))
        modelPointNumber = modelPointNumber.lstrip('bct_point_number ')
        # print 'Fourier Number: ' + modelFourierModeNum
        # print(modelFourierModeNum.lstrip('bct_fourier_mode_number '))
        modelFourierModeNum = modelFourierModeNum.lstrip('bct_fourier_mode_number ')

        # Mesh adjacency
        mesh_and_adjncy_vtu ./mesh-complete/mesh-complete.mesh.vtu
        # Assigning surface ID's
        mesh_and_adjncy_vtu mesh-complete/mesh-complete.mesh.vtu
        set_surface_id_vtp mesh-complete/mesh-complete.exterior.vtp 1
        set_surface_id_vtp mesh-complete/mesh-surfaces/cap_segment1.vtp 2
        set_surface_id_vtp mesh-complete/mesh-surfaces/cap_segment1_2.vtp 2
        set_surface_id_vtp mesh-complete/mesh-surfaces/wall_segment1.vtp 2
        # BCT properties
        fluid_density f_Density
        fluid_viscosity f_Viscosity
        initial_pressure i_Pressure
        initial_velocity i_Velocity
        bct_analytical_shape modelShape
        bct_period modelPeriod
        bct_point_number modelPointNumber
        bct_fourier_mode_number modelFourierModeNum
        # Creating BCT file for the inlet
        bct_create ./mesh-complete/mesh-surfaces/cap_segment1.vtp cap_segment1.flow
        bct_merge_on
        bct_write_dat ./bct.dat
        bct_write_vtp ./bct.vtp
        # Setting boundary conditions (w/ a zero pressure set)
        noslip_vtp ./mesh-complete/walls_combined.vtp
        prescribed_velocities_vtp ./mesh-complete/mesh-surfaces/cap_segment1.vtp
        pressure_vtp ./mesh-complete/mesh-surfaces/cap_segment1_2.vtp 0
        # Writing simulation files
        write_restart restart.0.1
        write_geombc geombc.dat
        write_numstart 0



#####################################################
#                   Main                           #
####################################################
import os
os.chdir('/usr/local/sv')
# from sv import *
aP = autoPre("/Users/tobiasjacobson/Documents/Atom/preScripting/cylTest/Simulations/cylSim/cylSim.svpre")
aP.readPre()
