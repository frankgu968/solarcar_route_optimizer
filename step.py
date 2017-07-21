# This is the means to traverse a single step in our virtual universe with the car
# Step-wise calculations and parameters
# Author: Frank Gu
# Date: July 2nd, 2017

from datetime import timedelta

class step:
    # These parameters represent the state of the system at the END of a step traversed
    # Environment states (populated during environment init)
    stepNum = 0.            # Step number
    ambTemp = 0.            # Ambient temperature (C)
    location = [0., 0.]     # GPS [Lat, Long]
    stepDistance = 0.       # Length of the step (km)
    trip = 0.               # Distance traversed (km)
    stepType = 0            # 0 - Ordinary step; 1 - Control stop; 2 - End of day / beginning of day transition
    inclination = 0.        # Inclination of the car (deg)
    heading = 0.            # Compass heading (0 deg -> N)
    cloud = 0.              # "Cloud factor"
    wind = [0., 0.]         # Wind [speed (kph), heading (deg 0->N)]
    rho = 1.11              # Local air density (kg m-3)
    speedLimit = 0.         # Step speed limit (km/h)

    # Car states    (populated during step advance)
    speed = 0.          # Speed of step (kph)
    isRegen = 0.        # Regenerative braking flag

    pin = 0.            # Input power (W)
    pbatt = 0.          # Battery power (W)
    battSoC = 0.        # Battery state of charge (%)
    pout = 0.           # OPTIMIZATION PARAMETER: Power consumed (W) ie. power profile to run (GA candidates)
    pbattExp = 0.       # OPTIMIZATION PARAMETER II: Prescribed battery power (W) ie. battery discharge profile (Init with profile)

    # Optimizer states (populated during step advance)
    eTime = 0.          # Elapsed race time (hours)
    gTime = 0.          # Global time (UTC format) ie. time on the clocks and watches
    timezone = 0        # Timezone offset from UTC time
    stepTime = 0.       # Time to traverse this step (s)


    # Class constructor
    def __init__(self, _stepNum, _ambTemp, _location, _stepDist, _trip, _speedLimit, _inclination, _heading, _cloud, _wind, _stepType, _timezone):
        self.stepNum = _stepNum
        self.ambTemp = _ambTemp
        self.location = _location
        self.stepDistance = _stepDist
        self.trip = _trip
        self.speedLimit = _speedLimit
        self.inclination = _inclination
        self.heading = _heading
        self.cloud = _cloud
        self.wind = _wind
        self.stepType = _stepType
        self.timezone = _timezone

    # Advance one distance step forward
    # Uses function from "car" class to transition the previous step state into new state
    # Assumes previous step result is already copied into current step data containers
    def advanceStep(self, car):
        # Check for the step properties
        # TODO: Implement control stop logic
        # TODO: Implement end-of-day / beginning-of-day logic

        # Evaluate car's step performance
        car.calcStepTime(self)

        # Advance elapsed time
        self.eTime = self.eTime + self.stepTime

        # Advance global time
        self.gTime = self.gTime + timedelta(seconds=self.stepTime)
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

    # Clears the non-step dependent information
    def clean(self):
        self.pbatt = 0.
        self.eTime = 0.
        self.stepTime = 0.
        self.gTime = {}
        self.speed = 0.
        self.pout = 0.
        self.battSoC = 0.
        self.pin = 0.