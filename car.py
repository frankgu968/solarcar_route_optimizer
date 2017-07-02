# This is the car in simulation space
# Simulates the dynamic systems of the car and yields state outputs
# Author: Frank Gu
# Date: July 2nd, 2017

ELEC_LP_POWER = 15.     # Electrical low-power system power = 15 W

# -------------------- ARRAY START --------------------------------------------------
# Raw expected array input
# Includes array geometry and temperature effects
# Assumes array temperature = ambient (due to high speed free stream air)
def arrayIn():

    return


# Maximum Power Point Tracker consolidating tracking and conversion efficiency
def mpptOut():

    return
# -------------------- ARRAY END ----------------------------------------------------

# -------------------- BATTERY START ------------------------------------------------
# Battery output power and its effects on the battery SoC
def battOut():

    return
# -------------------- BATTERY END --------------------------------------------------

# -------------------- ELECTROMECHANICAL START --------------------------------------
# Calculates how much thurst on the wheels the motor will provide (N) given the power in
def motorForce():

    return


# Calculate how fast the car will drive
def calcSpeed():

    return
# -------------------- ELECTROMECHANICAL END ----------------------------------------





