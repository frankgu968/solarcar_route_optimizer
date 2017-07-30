# I use this file for tests; don't mind it...
# Author: Frank Gu
# Date: July 1st, 2017
# Dependencies: NumPy, ElementTree, matplotlib, tk

from timeit import default_timer as timer

# import step
# from datetime import datetime
# import car
import matplotlib.pyplot as plt

import config
import optimizer
import world


def main():
    # fname = raw_input('Please specify geometry file location: ')
    fname = './Data/array.msh'
    if config.USE_SMALL_ROUTE:
        world.preprocessWorld('./Data/waypoints.gpx',[])
    else:
        world.preprocessWorld('./Data/route_debug_full.gpx', [322, 633, 988, 1211, 1496, 1756, 2178, 2432, 2719])
    world.preprocessDebugWorld('./Data/WSC.route')
    world.loadDebugData('./Data/WSC.debug')
    world.importWorld(fname,'')

    # Set the initial conditions
    world.setInitialConditions()

    # world.simulate({})
    start = timer()
    optimizer.optimize()
    #world.simulate({})
    end = timer()

    print 'Compute time: ' + str(end - start)
    plt.ioff()
    plt.show()
    # Finds average solar power of array across the whole day
    # jd1 = 0
    # stp = step.step(1, 35, [-12.462827, 130.841782], 500.0, 1500., 130.,  0., 135., 0., [0.,0.], 0, 0.)
    # stp.timezone = 9.5
    # sc = car.car()
    # fname = './Data/array.msh'
    # sc.loadArray(fname)
    # for h in range(6,19):
    #     dt = datetime(2015, 10, 8, h, 00)
    #     stp.gTime = dt
    #     jd1 += sc.arrayOut(stp)
    # jd1 = jd1 / 7.5
    # print(jd1)

    return


if __name__ == "__main__":
    main()
