# This is the car in simulation space
# Simulates the dynamic systems of the car and yields state outputs
# Author: Frank Gu
# Date: July 2nd, 2017
import numpy as np

import sun


class car:
    ELEC_LP_POWER = 15. # Electrical low-power system power = 15 W
    arrayArea = 0.      # Area of the solar array (m2)
    ARRAY_EFF = 0.237   # Solar panel nominal efficiency (24.3%)
    MPPT_EFF = 0.97     # Average MPPT efficiency (97%)
    BAT_EFF = 0.85      # Battery Coulombic efficiency
    arrayGeometry = []  # Array geometry

    # -------------------- ARRAY START --------------------------------------------------
    # Load array geometry file
    def loadArray(self, fname):
        mode = 0    # File parsing mode (0-Pass, 1-Node, 2-Elements)
        nodes = []  # Temporary container to hold nodes

        # Read the mesh file lines
        with open(fname) as f:
            lines = f.read().splitlines()

        for line in lines:
            # Parsing nodes
            if mode == 1:
                if line == '$EndNodes':
                    mode = 0    # Completion of nodes block

                else:
                    items = line.split(' ')
                    if len(items) > 1:
                        node = np.array([float(items[1]), float(items[2]), float(items[3])])
                        nodes.append(node)
            # Parsing elements
            elif mode == 2:
                if line == '$EndElements':
                    mode = 0    # Completion of elements block

                else:
                    items = line.split(' ')
                    # We only care about the triangle features
                    if len(items) > 1 and items[1] == '2':
                        a = int(items[5])
                        b = int(items[6])
                        c = int(items[7])
                        v1 = np.subtract(nodes[b-1]/1000, nodes[a-1]/1000)
                        v2 = np.subtract(nodes[c-1]/1000, nodes[a-1]/1000)
                        arrNorm = np.cross(v1, v2)     # Normal vector
                        self.arrayArea += 0.5 * np.linalg.norm(arrNorm)     # Rolling addition to array area
                        self.arrayGeometry.append(arrNorm)                  # Store the normal vector
            else:
                if line == '$Nodes':
                    mode = 1

                elif line == '$Elements':
                    mode = 2
        return lines



    # Raw expected array input
    # Includes array geometry and temperature effects
    # Assumes array temperature = ambient (due to high speed free stream air)
    def arrayIn(self, stepInfo):
        sunInfo = sun.info(stepInfo.gTime, stepInfo.timezone, stepInfo.location)
        insolation = sun.irradiance(sunInfo)    # The amount of power hitting the surface of the Earth

        # TODO: Use the array mesh to calculate the effective solar collector normal area


        power = insolation * self.ARRAY_AREA * self.ARRAY_EFF
        return power


    # Maximum Power Point Tracker consolidating tracking and conversion efficiency
    def arrayOut(self, stepInfo):
        arrRaw = self.arrayIn(stepInfo)
        powerOut = arrRaw * self.MPPT_EFF
        return powerOut
    # -------------------- ARRAY END ----------------------------------------------------

    # -------------------- BATTERY START ------------------------------------------------
    # Battery output power and its effects on the battery SoC
    def battOut(self, stepInfo):
        powerBat = stepInfo.pbattExp * self.BAT_EFF
        return powerBat
    # -------------------- BATTERY END --------------------------------------------------

    # -------------------- ELECTROMECHANICAL START --------------------------------------
    # Calculates how much thurst on the wheels the motor will provide (N) given the power in
    def motorForce():

        return


    # Calculate how fast the car will drive
    def calcSpeed():

        return
    # -------------------- ELECTROMECHANICAL END ----------------------------------------





