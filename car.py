# This is the car in simulation space
# Simulates the dynamic systems of the car and yields state outputs
# Author: Frank Gu
# Date: July 2nd, 2017
import sun

ELEC_LP_POWER = 15.     # Electrical low-power system power = 15 W
ARRAY_AREA  = 6         # Area of the solar array (m2)
ARRAY_EFF   = 0.237     # Solar panel nominal efficiency (24.3%)
MPPT_EFF    = 0.97      # Average MPPT efficiency (97%)
BAT_EFF     = 0.85      # Battery Coulombic efficiency

# -------------------- ARRAY START --------------------------------------------------
# Raw expected array input
# Includes array geometry and temperature effects
# Assumes array temperature = ambient (due to high speed free stream air)
def arrayIn(stepInfo):
    sunInfo = sun.info(stepInfo.gTime, stepInfo.timezone, stepInfo.location)
    insolation = sun.irradiance(sunInfo)    # The amount of power hitting the surface of the Earth

    # TODO: Use the array mesh to calculate the effective solar collector normal area


    power = insolation * ARRAY_AREA * ARRAY_EFF
    return power


# Maximum Power Point Tracker consolidating tracking and conversion efficiency
def arrayOut(stepInfo):
    arrRaw = arrayIn(stepInfo)
    powerOut = arrRaw * MPPT_EFF
    return powerOut
# -------------------- ARRAY END ----------------------------------------------------

# -------------------- BATTERY START ------------------------------------------------
# Battery output power and its effects on the battery SoC
def battOut(stepInfo):
    powerBat = stepInfo.pbattExp * BAT_EFF
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





