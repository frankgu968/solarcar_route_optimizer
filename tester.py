# I use this file for tests; don't mind it...
# Author: Frank Gu
# Date: July 1st, 2017

from datetime import datetime

import sun


def main():
    dt = datetime(2015, 10, 18, 12, 30)
    sunInfo = sun.info(dt, 9.5, [-12.462827, 130.841782])
    jd1 = sun.irradiance(sunInfo)
    print(jd1)
    return


if __name__ == "__main__":
    main()
