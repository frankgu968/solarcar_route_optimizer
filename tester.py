# I use this file for tests; don't mind it...
# Author: Frank Gu
# Date: July 1st, 2017
# Dependencies: NumPy, ElementTree

import optimizer
import world


def main():
    # fname = raw_input('Please specify geometry file location: ')
    fname = './Data/array.msh'
    # world.preprocessWorld('./Data/waypoints.gpx', [20, 50])
    # world.preprocessDebugWorld('./Data/WSC.route')
    world.loadDebugData('./Data/WSC.debug')
    world.importWorld(fname,'')

    # Set the initial conditions
    world.setInitialConditions()

    #world.simulate({})

    optimizer.optimize()

    return


if __name__ == "__main__":
    main()
