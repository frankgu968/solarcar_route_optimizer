# This is the world that the solar car runs in. It's a static class consisted of steps that encapsulate
# the world information. Helper functions are provided in this class to load and manipulate world parameters.

import numpy as np
import xml.etree.ElementTree as ET

from world_helpers import haversine

g = 9.81        # Gravitational acceleration constant
steps = []      # Steps container

def importWorld(filename):

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
# controlStops - A list of the distance markers for where control stops are at
# output - preprocessed file output path and filename
def preprocessWorld(input, controlStops):
    processedRoot = ET.Element('Route')      # Root referenced to preprocessed root

    tree = ET.parse(input)
    root = tree.getroot()
    for index, child in enumerate(root):
        # Get the waypoint parameters
        elevation = float(child[0].text)    # Elevation
        lon = float(child.attrib.get('lon'))       # Longitude
        lat = float(child.attrib.get('lat'))       # Latitude

        # Process the step information on the first step
        if index > 0:
            # Get previous waypoint parameters
            prevChild = root[index-1]
            prevElevation = float(prevChild[0].text)  # Elevation
            prevLon = float(prevChild.attrib.get('lon'))  # Longitude
            prevLat = float(prevChild.attrib.get('lat'))  # Latitude

            # See http://www.movable-type.co.uk/scripts/latlong.html for details on calculations below
            # Calculate heading (TESTED)
            y = np.sin(np.deg2rad(lon - prevLon)) * np.cos(np.deg2rad(lat))
            x = np.cos(np.deg2rad(prevLat)) * np.sin(np.deg2rad(lat)) - \
                np.sin(np.deg2rad(prevLat) * np.cos(np.deg2rad(lat))) * np.cos(np.deg2rad(lon - prevLon))
            heading = (np.rad2deg(np.arctan2(y, x)) + 360) % 360

            # Calculate step distance and add to total trip
            dist = haversine((prevLat, prevLon), (lat, lon))
            if index == 1:
                trip = dist
            else:
                trip = float(processedRoot[index-2].attrib.get('trip')) + dist

            # Calculate inclination
            inclination = np.rad2deg(np.arctan2(elevation - prevElevation, dist))

            # Set Timezone
            timezone = 9.5  # TODO: Conditionally adjust this based on elapsed distance

            # Add node to processedRoot
            b = ET.SubElement(processedRoot, 'step')
            b.set('heading', str(heading))
            b.set('inclination', str(inclination))
            b.set('dist', str(dist))
            b.set('trip', str(trip))
            b.set('timezone', str(timezone))

    # Write processedRoot into XML file
    newTree = ET.ElementTree(processedRoot)
    newTree.write('./Data/WSC.route')

    return processedRoot

# Polls weather API to get the updates for all the weather data in the
def loadMeterology():
    return

# Preprocess the waypoint gpx file including a simulated meterology data
def preprocessDebugWorld(input, output):
    return

# Loads the step data with full meteorology etc. for debugging optimization algorithm
def loadDebugData(input):
    return
