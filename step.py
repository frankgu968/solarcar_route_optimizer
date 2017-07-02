# This is the means to traverse a single step in our virtual universe with the car
# Step-wise calculations and parameters
# Author: Frank Gu
# Date: July 2nd, 2017

class step:
    # These parameters represent the state of the system at the END of a step traversed
    # Environment states (populated during environment init)
    stepNum = 0.        # Step number
    ambTemp = 0.        # Ambient temperature (C)
    location = [0., 0.] # GPS [Lat, Long]
    stepDistance = 0.   # Length of the step (km)
    isControlStop = False # Control stop flag
    isEndOfDay = False    # OPTIMIZATION PARAMETER: End of day flag (ie. when to stop the car)
    inclination = 0.    # Inclination of the car (deg)
    heading = 0.        # Compass heading (0 deg -> N)
    cloud = 0.          # "Cloud factor"
    wind = [0., 0.]     # Wind [speed (kph), heading (deg 0->N)]

    # Car states    (populated during step advance)
    speed = 0.          # Speed of step (kph)
    isRegen = 0.        # Regenerative braking flag
    trip = 0.           # Distance traversed (km)
    pin = 0.            # Input power (W)
    pbatt = 0.          # Battery power (W)
    battSoC = 0.        # Battery state of charge (%)
    pout = 0.           # OPTIMIZATION PARAMETER: Power consumed (W) ie. power profile to run (GA candidates)
    pbattExp = 0.       # OPTIMIZATION PARAMETER: Prescribed battery power (W) ie. battery discharge profile (Init with profile)

    # Optimizer states (populated during step advance)
    eTime = 0.          # Elapsed race time (hours)
    gTime = 0.          # Global time (UTC format) ie. time on the clocks and watches


    # Advance one distance step forward
    # Uses function from "car" class
    def advanceStep(self):
        # Evaluate power in for this step


        # Evaluate available power output for this step


        # Evaluate average speed to traverse this step


        # Evaluate time taken
        return

    # Checks step advancement results against presets
    # Returns True iff constraints are met
    # Will set eTime = INF if constraints are not met
    def checkConstraints(self):

        self.eTime = float('inf') # Max out the elapsed time counter to invalidate result
        return False


    # Print the information for this step of optimization for debug and diagnostic purposes
    def printStep(self):

        return


