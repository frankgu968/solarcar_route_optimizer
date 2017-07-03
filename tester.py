# I use this file for tests; don't mind it...
# Author: Frank Gu
# Date: July 1st, 2017

from datetime import datetime

import car
import step


def main():
    stp = step.step(1, 35, [-12.462827, 130.841782], 1.0, 0., 0., 0., [0.,0.])
    dt = datetime(2015, 10, 18, 12, 30)
    #sunInfo = sun.info(dt, 9.5, [-12.462827, 130.841782])
    stp.gTime = dt
    stp.timezone = 9.5
    sc = car.car()
    fname = raw_input('Please specify geometry file location: ')
    sc.loadArray(fname)
    jd1 = sc.arrayArea

    print(jd1)
    return


if __name__ == "__main__":
    main()
