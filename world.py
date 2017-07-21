# This is the world that the solar car runs in. It's a static class consisted of steps that encapsulate
# the world information. Helper functions are provided in this class to load and manipulate world parameters.

import numpy as np
import xml.etree.ElementTree as ET

import car
import step
from world_helpers import haversine

g = 9.81  # Gravitational acceleration constant
steps = []  # Steps container
solarCar = {}  # Solar car container
SL_CONTROL_STOP = 16.67  # Control stop speed limit (ms-1)
SL_HIGHWAY = 36.1  # Highway speed limit (ms-1)

# DEBUG FACILITIES
DEBUG_AVG_WIND_SPD = 0.
DEBUG_AVG_WIND_VAR = 4


def importWorld(fn_array, fn_route):
    global solarCar
    solarCar = car.car()
    solarCar.loadArray(fn_array)

    return


# Generate random wind perturbations for the GA robustness
def createWind():
    return


# Generate random cloud coverage perturbations for the GA robustness
def createClouds():
    return


# Helper function to take in a [Lat, Long, Elevation, Type] file and computes heading, distance, inclination, time zone
# Arguments:
# input - Waypoint gpx file pathname
# controlStops - A list of the distance markers (km) for where control stops are at in increasing trip order
# output - preprocessed file output path and filename
def preprocessWorld(input, controlStops):
    processedRoot = ET.Element('Route')  # Root referenced to preprocessed root
    csIndex = 0  # Control stop index count

    tree = ET.parse(input)
    root = tree.getroot()
    for index, child in enumerate(root):
        # Get the waypoint parameters
        elevation = float(child[0].text)  # Elevation
        lon = float(child.attrib.get('lon'))  # Longitude
        lat = float(child.attrib.get('lat'))  # Latitude

        # Process the step information on the first step
        if index > 0:
            # Get previous waypoint parameters
            prevChild = root[index - 1]
            prevElevation = float(prevChild[0].text)  # Elevation
            prevLon = float(prevChild.attrib.get('lon'))  # Longitude
            prevLat = float(prevChild.attrib.get('lat'))  # Latitude

            # See http://www.movable-type.co.uk/scripts/latlong.html for details on calculations below
            # Calculate heading (TESTED)
            y = np.sin(np.deg2rad(lon - prevLon)) * np.cos(np.deg2rad(lat))
            x = np.cos(np.deg2rad(prevLat)) * np.sin(np.deg2rad(lat)) - \
                np.sin(np.deg2rad(prevLat) * np.cos(np.deg2rad(lat))) * np.cos(np.deg2rad(lon - prevLon))
            heading = (np.rad2deg(np.arctan2(y, x)) + 360) % 360

            # Set global speed limit
            speedLimit = SL_HIGHWAY  # Default value for the speed limit for a step

            # Set step type
            stepType = 0

            # Calculate step distance and add to total trip
            dist = haversine((prevLat, prevLon), (lat, lon))
            if index == 1:
                trip = dist
            else:
                prevTrip = float(processedRoot[index - 2].attrib.get('trip'))
                trip = prevTrip + dist

                # Set speed limit after control stop
                if processedRoot[index - 2].attrib.get('stepType') == '1':
                    speedLimit = SL_CONTROL_STOP

                if (csIndex < len(controlStops)) and (trip > controlStops[csIndex] * 1000. > prevTrip):
                    # A control stop has hit
                    processedRoot[index - 2].set('speedLimit',
                                                 str(SL_CONTROL_STOP))  # set the speed limit before the control stop
                    speedLimit = SL_CONTROL_STOP  # Set current step speed limit
                    stepType = 1  # Set step to be a control stop type
                    csIndex = csIndex + 1

            # Calculate inclination
            inclination = np.rad2deg(np.arctan2(elevation - prevElevation, dist))

            # Set Timezone
            timezone = 9.5  # We used a universal time based on the start line in Darwin (event time)

            # Add node to processedRoot
            b = ET.SubElement(processedRoot, 'step')
            b.set('lat', str(lat))
            b.set('lon', str(lon))
            b.set('heading', str(heading))
            b.set('inclination', str(inclination))
            b.set('dist', str(dist))
            b.set('trip', str(trip))
            b.set('timezone', str(timezone))
            b.set('speedLimit', str(speedLimit))
            b.set('stepType', str(stepType))

    # Write processedRoot into XML file
    newTree = ET.ElementTree(processedRoot)
    newTree.write('./Data/WSC.route')

    return processedRoot


# Polls weather API to get the updates for all the weather data in the
def loadMeterology():
    return


# Preprocess the waypoint gpx file including a simulated meterology data
def preprocessDebugWorld(input):
    tree = ET.parse(input)
    root = tree.getroot()
    stepNum = 1

    for child in root:
        if 15 > float(child.attrib.get('trip')) / 1000. > 10:
            cloud = 1  # Light overcast between 10 - 15 km of trip
        elif 25 > float(child.attrib.get('trip')) / 1000. > 20:
            cloud = 2  # Heavy overcast between 20 - 25 km of trip
        else:
            cloud = 0  # Clear skies elsewhere
        child.set('cloud', str(cloud))

        # Create declining temperature
        ambTemp = 35. - stepNum / 30.
        child.set('ambTemp', str(ambTemp))

        # Create random wind
        # Random Uniform direction distribution [0,359]
        child.set('windDir', str(np.random.randint(0, 359)))

        # Absolute value of Random Gaussian wind speed distribution ()
        child.set('windSpd', str(abs(np.random.normal(DEBUG_AVG_WIND_SPD, DEBUG_AVG_WIND_VAR))))

        stepNum = stepNum + 1

    # Write processedRoot into XML filedebugTree
    tree.write('./Data/WSC.debug')

    return


# Loads the step data with full meteorology etc. for debugging optimization algorithm
def loadDebugData(input):
    global steps
    steps = []  # Clear the container
    tree = ET.parse(input)
    root = tree.getroot()
    stepNum = 1

    for child in root:
        tempStep = step.step(stepNum,
                             float(child.attrib.get('ambTemp')),
                             [float(child.attrib.get('lat')), float(child.attrib.get('lon'))],
                             float(child.attrib.get('dist')),
                             float(child.attrib.get('trip')),
                             float(child.attrib.get('speedLimit')),
                             float(child.attrib.get('inclination')),
                             float(child.attrib.get('heading')),
                             float(child.attrib.get('cloud')),
                             [float(child.attrib.get('windSpd')), float(child.attrib.get('windDir'))],
                             int(child.attrib.get('stepType')),
                             float(child.attrib.get('timezone')))
        steps.append(tempStep)
        stepNum = stepNum + 1
    return


def simulate(pbatt_candidate):
    global solarCar

    for index, stp in enumerate(steps):
        stp.pbattExp = 450.
        stp.pbatt = stp.pbattExp + pbatt_candidate[index - 1]
        stp.advanceStep(solarCar)

        # Copy state variables
        if index < len(steps) - 1:
            steps[index + 1].eTime = stp.eTime
            steps[index + 1].gTime = stp.gTime
            steps[index + 1].speed = stp.speed

    return steps[-1].eTime