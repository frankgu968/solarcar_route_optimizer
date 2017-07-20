# This is the car in simulation space
# Simulates the dynamic systems of the car and yields state outputs
# Author: Frank Gu
# Date: July 2nd, 2017
import numpy as np

from scipy.optimize import fsolve

import sun
import world
import world_helpers


class car:
    # Static efficiency blobs
    ELEC_LP_POWER = 15. # Electrical low-power system power = 15 W
    MPPT_EFF = 0.97     # Average MPPT efficiency (97%)
    BAT_EFF = 0.85      # Battery Coulombic efficiency
    ARRAY_EFF = 0.243   # Solar panel nominal efficiency (24.3%)
    MOT_EFF = 0.95      # Motor efficiency (95%)

    # Car dependent parameters
    CDA = 0.1125           # Coefficient of Drag
    Ptire = 517e3       # Tire pressure (~75 psi)
#    alpha
#    beta =
    MASS = 250.         # Solar car mass (250 Kg)

    # Dynamic variables
    arrayArea = 0.  # Area of the solar array (m2)
    arrayGeometry = []  # Array geometry

    # -------------------- ARRAY START --------------------------------------------------
    # ELEMENT: ARRAY_GEOMETRY
    # Load array geometry file
    def loadArray(self, fname):
        mode = 0  # File parsing mode (0-Pass, 1-Node, 2-Elements)
        nodes = []  # Temporary container to hold nodes
        # Rotational matrix to reposition the aerobody to point
        tRot = np.array([[0, -1, 0],
                         [1, 0, 0],
                         [0, 0, 1]])

        # Read the mesh file lines
        with open(fname) as f:
            lines = f.read().splitlines()

        for line in lines:
            # Parsing nodes
            if mode == 1:
                if line == '$EndNodes':
                    mode = 0  # Completion of nodes block

                else:
                    items = line.split(' ')
                    if len(items) > 1:
                        node = np.array([float(items[1]), float(items[2]), float(items[3])])
                        nodes.append(node)
            # Parsing elements
            elif mode == 2:
                if line == '$EndElements':
                    mode = 0  # Completion of elements block

                else:
                    items = line.split(' ')
                    # We only care about the triangle features
                    if len(items) > 1 and items[1] == '2':
                        a = int(items[5])
                        b = int(items[6])
                        c = int(items[7])
                        v1 = np.subtract(nodes[b - 1] / 1000, nodes[a - 1] / 1000)
                        v2 = np.subtract(nodes[c - 1] / 1000, nodes[a - 1] / 1000)
                        arrNorm = np.cross(v1, v2)  # Normal vector
                        meshNorm = np.matmul(tRot, arrNorm)
                        self.arrayArea += 0.5 * np.linalg.norm(arrNorm)  # Rolling addition to array area
                        self.arrayGeometry.append(meshNorm)  # Store the normal vector
            else:
                if line == '$Nodes':
                    mode = 1

                elif line == '$Elements':
                    mode = 2
        return lines

    # ELEMENT: ARRAY
    # Raw expected array input
    # Includes array geometry and temperature effects
    # Assumes array temperature = ambient (due to high speed free stream air)
    def arrayIn(self, stepInfo):
        sunInfo = sun.info(stepInfo.gTime, stepInfo.timezone, stepInfo.location)
        insolation = sun.irradiance(sunInfo)  # The amount of power hitting the surface of the Earth
        power = 0.

        # Create the sun's unit vector with Azimuth and elevation
        sunVec = -np.array([np.sin(np.deg2rad(sunInfo[1])) * np.cos(np.deg2rad(sunInfo[0])),
                           np.cos(np.deg2rad(sunInfo[1])) * np.sin(np.deg2rad(sunInfo[0])),
                           np.sin(np.deg2rad(sunInfo[0]))])

        for meshElement in self.arrayGeometry:
            # Rotate the car in 3D with heading and elevation
            # Rotate the car's heading
            tRotation = np.array([  [np.cos(np.deg2rad(-stepInfo.heading)), -np.sin(-np.deg2rad(stepInfo.heading)), 0],
                                    [np.sin(np.deg2rad(-stepInfo.heading)), np.cos(-np.deg2rad(stepInfo.heading)), 0],
                                    [0, 0, 1]])
            tempVec = np.matmul(tRotation, meshElement)  # Transformed mesh element normal vector

            # Rotate the car's inclination
            # 1. Obtain the axis of rotation
            axis = np.cross(meshElement, np.array([meshElement[0], meshElement[1], 0]))
            # 2. Apply Euler-Rodrigues formula to create transformation matrix
            tElevation = world_helpers.rotation_matrix(axis, np.deg2rad(-stepInfo.inclination))
            # 3. Apply transformation
            meshVec = np.matmul(tElevation, tempVec)
            power += insolation * np.abs(0.5 * np.dot(sunVec, meshVec)) * self.ARRAY_EFF

        # TODO: Implement temperature effects on panel efficiency
        # TODO: Implement cloud coverage effects

        # Flat panel model; No consideration to array geometry
        #power = insolation * self.arrayArea * self.ARRAY_EFF * np.sin(np.deg2rad(sunInfo[0]))
        return power

    # ELEMENT: MPPT
    # Maximum Power Point Tracker consolidating tracking and conversion efficiency
    def arrayOut(self, stepInfo):
        arrRaw = self.arrayIn(stepInfo)
        powerOut = arrRaw * self.MPPT_EFF
        return powerOut

    # -------------------- ARRAY END ----------------------------------------------------

    # -------------------- BATTERY START ------------------------------------------------
    # ELEMENT: BATTERY
    # Battery output power and its effects on the battery SoC
    def battOut(self, stepInfo):
        powerBat = stepInfo.pbattExp * self.BAT_EFF
        return powerBat

    # -------------------- BATTERY END --------------------------------------------------

    # -------------------- TELEMETRY START ----------------------------------------------
    # ELEMENT: TELEMETRY
    def telemPower(self, stepInfo):
        return self.ELEC_LP_POWER
    # -------------------- TELEMETRY END ------------------------------------------------

    # -------------------- ELECTROMECHANICAL START --------------------------------------
    # Calculates how much thurst on the wheels the motor will provide (N) given the power in
    # Calling this will set the pout field of StepInfo
    def motorShaftPower(self, stepInfo):
        stepInfo.pout = self.arrayOut(stepInfo) + self.battOut(stepInfo)  # Power available for consumption
        pshaft = (stepInfo.pout - self.telemPower(stepInfo)) * self.MOT_EFF
        return pshaft

    # Calculate how fast the car will drive
    def calcStepTime(self, stepInfo):
        #pshaft = self.motorShaftPower(stepInfo)     # Shaft power delivered by motor
        pshaft = 1300
        # def f(x):
        #     return self.proll(x, stepInfo) + self.pgravity(x, stepInfo) + self.paero(x, stepInfo) - pshaft
        #
        # vStepMax = fsolve(f, 22.)   # Maximum speed attainable with the power given in m s-1
        vPrev = stepInfo.speed

        def f(y):
            return -0.5 * self.CDA * stepInfo.rho * np.power(y, 3)- self.MASS * y * world.g*np.sin(np.deg2rad(stepInfo.inclination))+(pshaft - self.proll(y,stepInfo))
        omega = fsolve(f, 0)

        def f(z):
            return stepInfo.stepDistance-(self.MASS * np.power(omega,2)*np.log((-omega+z)/(-omega+vPrev)) / (3 * (-0.5)*self.CDA*stepInfo.rho * np.power(omega,2)-self.MASS*world.g*np.sin(np.deg2rad(stepInfo.inclination))))
        airspeed = fsolve(f, vPrev)[0]  # The final resulting air speed of this step
        # ASSUMPTION: Only component of wind in direction of car travel affects the car; cross wind does not introduce any drag
        stepInfo.speed = airspeed + stepInfo.wind[0] * np.sin(np.deg2rad(90 - np.abs(stepInfo.wind[1] - stepInfo.heading)))  # Calculate ground speed

        # Not sure how to calculate the time... Will take the mid point between the speeds and approximate it...
        stepInfo.stepTime = stepInfo.stepDistance / ((vPrev+stepInfo.speed) / 2)

        # FIXME
        # # START INVALID TIME
        # time = self.MASS*omega * np.log((-omega + stepInfo.speed)/(-omega + vPrev)) / (3*-(0.5)*self.CDA*stepInfo.rho*np.power(omega,2)-self.MASS*world_helpers.g*np.sin(np.deg2rad(stepInfo.inclination)))
        #
        # # Above conclusion tested with below integration:
        # def integrand(v):
        #     return self.MASS * v / ((pshaft - self.proll(v, stepInfo))-0.5*self.CDA*stepInfo.rho*np.power(v,3)-self.MASS*world_helpers.g*np.sin(np.deg2rad(stepInfo.inclination)))
        #     #return self.MASS * v / ((964.54 - 250) - 0.5 * 0.1125 * 1.17 * np.power(v,3) - self.MASS * 9.81 * np.sin(np.deg2rad(stepInfo.inclination)))
        #
        # time = quad(integrand, vPrev, stepInfo.speed)
        # # END INVALID TIME
        return stepInfo.stepTime

    # -------------------- ELECTROMECHANICAL END ----------------------------------------
    # Misc calculators
    # ELEMENT: TIRE
    def proll(self, v, stepInfo):
        return 250

    # ELEMENT: AERO
    def paero(self, v, stepInfo):
        return 0.5 * self.CDA * stepInfo.rho * np.power(v, 3)

    # ELEMENT: GRAVITY
    def pgravity(self, v, stepInfo):
        return self.MASS * world_helpers.g * np.sin(np.deg2rad(stepInfo.inclination)) * v

