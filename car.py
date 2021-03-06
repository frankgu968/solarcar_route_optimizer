# This is the car in simulation space
# Simulates the dynamic systems of the car and yields state outputs
# Author: Frank Gu
# Date: July 2nd, 2017
import numpy as np

from scipy.optimize import fsolve

import config
import sun
import world
import world_helpers


class car:
    # Static efficiency blobs
    ELEC_LP_POWER = 15. # Electrical low-power system power = 15 W
    MPPT_EFF = 0.97     # Average MPPT efficiency (97%)
    BAT_DISCHARGE_EFF = 0.85      # Battery discharging efficiency
    BAT_CHARGE_EFF = 0.85         # Battery charging efficiency
    ARRAY_EFF = 0.243   # Solar panel nominal efficiency (24.3%)
    MOT_EFF = 0.95      # Motor efficiency (95%)
    DIFFUSE_EFF = 0.3   # Diffuse array collector power factor (30%)

    # Car dependent parameters
    BATT_CAPACITY = 6300    # Battery capacity (Wh)
    CDA = 0.1125            # Coefficient of Drag
    Ptire = 517e3           # Tire pressure (~75 psi)
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
        self.arrayGeometry = np.asarray(self.arrayGeometry)
        return lines

    # ELEMENT: ARRAY
    # Raw expected array input
    # Includes array geometry and temperature effects
    # Assumes array temperature = ambient (due to high speed free stream air)
    def arrayIn(self, stepInfo, mode=0):
        if mode == 2:
            # End of day directional charging
            sunInfo = sun.info(stepInfo.gTime, stepInfo.timezone, stepInfo.location)
            insolation = sun.irradiance(sunInfo)  # The amount of power hitting the surface of the Earth

            normalSunVec = np.array(
                [0, 0, -1])  # Assumes that the sun panel's geometric normal is pointing directly at the sun
            meshPowerMat = np.matmul(self.arrayGeometry, normalSunVec) * 0.5 * insolation * self.ARRAY_EFF
            # Mesh elements receiving direct sunlight
            meshDirect = np.extract(np.ma.masked_less(meshPowerMat, 0.), meshPowerMat)

            # Mesh elements receiving diffuse sunlight
            # ASSUMPTION: Panel elements facing indirectly towards the sun will receive same solar collection efficiency
            # as those directly due to Gochermann high-angle refraction crystal lamination
            meshDiffuse = np.extract(np.ma.masked_greater(meshPowerMat, 0.), meshPowerMat) * (-1.0)
            power = np.sum(meshDirect) + np.sum(meshDiffuse)
        else:
            sunInfo = sun.info(stepInfo.gTime, stepInfo.timezone, stepInfo.location)
            insolation = sun.irradiance(sunInfo)  # The amount of power hitting the surface of the Earth

            if config.ARRAY_MESH_CALCULATION:
                # Create the sun's unit vector with relative to the car's heading and azimuth
                modSunVec = -np.array([np.sin(np.deg2rad(sunInfo[1] - stepInfo.heading)) * np.cos(np.deg2rad(sunInfo[0] - stepInfo.inclination)),
                                   np.cos(np.deg2rad(sunInfo[1] - stepInfo.heading)) * np.sin(np.deg2rad(sunInfo[0] - stepInfo.inclination)),
                                   np.sin(np.deg2rad(sunInfo[0] - stepInfo.inclination))])

                meshPowerMat = np.matmul(self.arrayGeometry, modSunVec) * 0.5 * insolation * self.ARRAY_EFF
                # Mesh elements receiving direct sunlight
                meshDirect = np.extract(np.ma.masked_less(meshPowerMat, 0.), meshPowerMat)
                # Mesh elements receiving diffuse sunlight
                # ASSUMPTION: Panel elements facing away from the Sun vector will receive ambient power
                # FIXME: Tune the ambient diffuse term. (power contribution = Ambient efficieny * unitPower)
                meshDiffuse = np.extract(np.ma.masked_greater(meshPowerMat, 0.), meshPowerMat) * (-self.DIFFUSE_EFF)
                power = np.sum(meshDirect) + np.sum(meshDiffuse)

                # sunVec = -np.array([np.sin(np.deg2rad(sunInfo[1])) * np.cos(np.deg2rad(sunInfo[0])),
                #                     np.cos(np.deg2rad(sunInfo[1])) * np.sin(np.deg2rad(sunInfo[0])),
                #                     np.sin(np.deg2rad(sunInfo[0]))])
                #
                # tRotation = np.array([[np.cos(np.deg2rad(-stepInfo.heading)), -np.sin(-np.deg2rad(stepInfo.heading)), 0],
                #                       [np.sin(np.deg2rad(-stepInfo.heading)), np.cos(-np.deg2rad(stepInfo.heading)), 0],
                #                       [0, 0, 1]])
                #
                # power = 0
                # for meshElement in self.arrayGeometry:
                #     # Rotate the car in 3D with heading and elevation
                #     # Rotate the car's heading
                #
                #     tempVec = np.matmul(tRotation, meshElement)  # Transformed mesh element normal vector
                #
                #     # Rotate the car's inclination
                #     # 1. Obtain the axis of rotation
                #     axis = np.cross(meshElement, np.array([meshElement[0], meshElement[1], 0]))
                #     # 2. Apply Euler-Rodrigues formula to create transformation matrix
                #     tElevation = world_helpers.rotation_matrix(axis, np.deg2rad(-stepInfo.inclination))
                #     # 3. Apply transformation
                #     meshVec = np.matmul(tElevation, tempVec)
                #     unitPower = insolation * (0.5 * np.dot(sunVec, meshVec)) * self.ARRAY_EFF
                #
                #     if unitPower > 0:
                #         power += unitPower
                #     else:
                #
                #         power += -0.3 * unitPower

            else:
                # Flat panel model; No consideration to array geometry
                power = insolation * self.arrayArea * self.ARRAY_EFF * np.sin(90-np.deg2rad(np.abs(sunInfo[0]-stepInfo.inclination)))

        # TODO: Implement temperature effects on panel efficiency
        # TODO: Implement cloud coverage effects

        stepInfo.pin = power
        return power

    # ELEMENT: MPPT
    # Maximum Power Point Tracker consolidating tracking and conversion efficiency
    # Input - stepInfo: The step object that the car is operating in
    #       - mode    : 0 -> Regular driving step; 2 -> end of day, array pointing towards the sun
    def arrayOut(self, powerIn):
        powerOut = powerIn * self.MPPT_EFF
        return powerOut

    # -------------------- ARRAY END ----------------------------------------------------

    # -------------------- BATTERY START ------------------------------------------------
    # ELEMENT: BATTERY
    # Battery output power and its effects on the battery SoC
    # FIXME: Better battery discharge modeling algorithm
    def battOut(self, stepInfo):
        powerBat = 0

        # Check that there is still battery
        if stepInfo.battSoC > 0:
            powerBat = stepInfo.pbatt * self.BAT_DISCHARGE_EFF

        return powerBat

    # Battery charging and its effects on battery SoC
    # Input - Power (Watts)
    #       - Duration (minutes)
    # FIXME: Better battery charge modeling algorithm
    def battIn(self, stepInfo, power, duration):
        stepInfo.battSoC += 100 * (power * duration / 60) / self.BATT_CAPACITY * self.BAT_CHARGE_EFF

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
        stepInfo.pout = self.arrayOut(self.arrayIn(stepInfo)) + self.battOut(stepInfo)  # Power available for consumption
        pshaft = (stepInfo.pout - self.telemPower(stepInfo)) * self.MOT_EFF
        return pshaft

    # Calculate how fast the car will drive
    def calcStepTime(self, stepInfo):
        pshaft = self.motorShaftPower(stepInfo)     # Shaft power delivered by motor

        # TODO: Fix below algorithm to be more stable and less computational heavy!
        # def f(x):
        #     return self.proll(x, stepInfo) + self.pgravity(x, stepInfo) + self.paero(x, stepInfo) - pshaft
        #
        # vStepMax = fsolve(f, 22.)   # Maximum speed attainable with the power given in m s-1
        vPrev = stepInfo.speed
        def f(y):
            return -0.5 * self.CDA * stepInfo.rho * np.power(y, 3)- self.MASS * y * world.g*np.sin(np.deg2rad(stepInfo.inclination))+(pshaft - self.proll(y,stepInfo))
        # NOTE: fsolve becomes unstable with too high/low guess values. The highest speed limit is selected as a good assumption since the solution can only lie close or below it.
        omega = fsolve(f, config.SL_HIGHWAY)

        def f(z):
            return stepInfo.stepDistance-(self.MASS * np.power(omega,2)*np.log((-omega+z)/(-omega+vPrev)) / (3 * (-0.5)*self.CDA*stepInfo.rho * np.power(omega,2)-self.MASS*world.g*np.sin(np.deg2rad(stepInfo.inclination))))
        # NOTE: fsolve initial guess = vPrev considering that the next step speed shouldn't deviate too much from the first step
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

        # Decrease remaining battery charge
        stepInfo.battSoC -= 100 * (stepInfo.pbatt * (stepInfo.stepTime / 3600) / self.BATT_CAPACITY)

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

