# I use this file for tests; don't mind it...
# Author: Frank Gu
# Date: July 1st, 2017

from datetime import datetime

import car
import step


def main():
    stp = step.step(1, 35, [-12.462827, 130.841782], 500.0, 0., 135., 0., [0.,0.])

    stp.timezone = 9.5
    sc = car.car()
    #fname = raw_input('Please specify geometry file location: ')
    fname = '/home/frank/Desktop/test.msh'
    sc.loadArray(fname)
    #print(sc.arrayArea)
    dt = datetime(2015, 10, 18, 11, 00)
    stp.gTime = dt
    stp.pbattExp = 200
    stp.speed = 21.5
    # Finds average solar power of array across the whole day
    # jd1 = 0
    # for h in range(6,19):
    #     dt = datetime(2015, 10, 18, h, 00)
    #     stp.gTime = dt
    #     jd1 += sc.arrayOut(stp)
    # jd1 = jd1 / 7.5
    # print(jd1)

    temp = sc.calcStepTime(stp)
    print stp.speed
    print(temp)
    return


if __name__ == "__main__":
    main()
