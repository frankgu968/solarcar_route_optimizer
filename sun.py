# This is the sun
# Calculates the solar angles and insolation parameters
# Author: Frank Gu
# Date: July 1st, 2017

import math
from datetime import datetime
from datetime import timedelta


# location [lat long]
# Latitude + to N
# Longitude + to E
# Returns a list of Elevation,
def info(gTime, timezone, location):
    # Julian date calculation adapted from 'Practical Astronomy with your Calculator or Spreadsheet'
    # Not valid for Jan and Feb
    A = math.trunc(gTime.year / 100.)
    B = 2 - A + math.trunc(A / 4.)
    C = math.trunc(365.25 * gTime.year)
    D = math.trunc(30.6001 * (gTime.month + 1))
    day = gTime.day + (gTime.hour + (gTime.minute + gTime.second / 60.) / 60. - timezone) / 24.0

    # Julian date with time and timezone correction
    jd = B + C + D + day + 1720994.5

    # Julian Century
    jc = (jd - 2451545) / 36525

    # Geom Mean Long Sun (deg)
    gmls = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360.

    # Geom Mean Anom Sun (deg)
    gmas = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)

    # Eccentric Earth Orbit
    eec = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)

    # Sun Equation of Center
    sec = math.sin(math.radians(gmas)) * (1.914602 - jc * (0.004817 + 0.000014 * jc)) + \
          math.sin(math.radians(2 * gmas)) * (0.019993 - 0.000101 * jc) + math.sin(math.radians(3 * gmas)) * 0.000289

    # Sun True Longitude (degrees)
    stl = gmls + sec

    # Sun True Anom (degrees)
    sta = gmas + sec

    # Sun Rad Vector (AUs)
    # srv = 1.000001018 * (1 - eec * eec) / (1 + eec * math.cos(math.radians(sta)))

    # Sun App Long (deg)
    sal = stl - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * jc))

    # Mean Oblique Ecliptic (deg)
    moe = 23 + (26 + (21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))) / 60) / 60

    # Oblique Correction (deg)
    oc = moe + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * jc))

    # Sun Right Ascension (deg)
    # sra = 90 - math.degrees(math.atan2(math.cos(math.radians(sal)), math.cos(math.radians(oc))*math.sin(math.radians(sal))))

    # Sun Declination (deg)
    sd = math.degrees(math.asin(math.sin(math.radians(oc)) * math.sin(math.radians(sal))))

    # Var y
    vy = math.tan(math.radians(oc / 2)) * math.tan(math.radians(oc / 2))

    # Equation of Time
    eot = 4 * math.degrees(vy * math.sin(2 * math.radians(gmls)) - 2 * eec * math.sin(math.radians(gmas)) +
                           4 * eec * vy * math.sin(math.radians(gmas)) * math.cos(2 * math.radians(gmls)) -
                           0.5 * vy * vy * math.sin(4 * math.radians(gmls)) - 1.25 * eec * eec * math.sin(
        2 * math.radians(gmas)))

    # True Solar Time
    today = (gTime.hour + (gTime.minute + gTime.second / 60.) / 60.) / 24.0
    tst = (today * 1440 + eot + 4 * location[1] - 60 * timezone) % 1440

    # Hour Angle
    if tst < 0:
        ha = tst / 4. + 180.
    else:
        ha = tst / 4. - 180.

    # Solar Zenith Angle
    sza = math.degrees(math.acos(math.sin(math.radians(location[0])) * math.sin(math.radians(sd)) +
                                 math.cos(math.radians(location[0])) * math.cos(math.radians(sd)) * math.cos(
                                     math.radians(ha))))

    # Solar Elevation Angle
    sea = 90 - sza

    # Atmospheric Refraction Correction
    if sea > 85:
        ar = 0
    elif sea > 5:
        ar = (58.1 / math.tan(math.radians(sea)) - 0.07 / math.pow(math.tan(math.radians(sea)), 3) +
              0.000086 / math.pow(math.tan(math.radians(sea)), 5)) / 3600
    elif sea > -0.575:
        ar = (1735 - 518.2 * sea + 103.4 * math.pow(sea, 2) - 12.79 * math.pow(sea, 3) + 0.711 * math.pow(sea, 4)) / 3600.
    else:
        ar = -20.774 / (3600 * math.tan(math.radians(sea)))

    # Corrected elevation angle
    elevation = sea + ar

    if ha > 0:
        azimuth = (math.degrees(math.acos(((math.sin(math.radians(location[0])) * math.cos(math.radians(sza))) -
                                           math.sin(math.radians(sd))) / (
                                              math.cos(math.radians(location[0])) * math.sin(
                                                  math.radians(sza))))) + 180) % 360
    else:
        azimuth = (540 - math.degrees(math.acos(((math.sin(math.radians(location[0])) * math.cos(math.radians(sza))) -
                                                 math.sin(math.radians(sd))) / (
                                                    math.cos(math.radians(location[0])) * math.sin(
                                                        math.radians(sza)))))) % 360

    return [elevation, azimuth, eot, sd, jd]


def getSunRiseSetTime(gTime, timezone, location):
    # Current day sunset time
    sunInfo = info(gTime, timezone, location)
    solarNoon = (720 - 4 * location[1] - sunInfo[2] + timezone * 60) / 1440
    hasr = math.degrees(math.acos(
        math.cos(math.radians(90.833)) / (math.cos(math.radians(location[0])) * math.cos(math.radians(sunInfo[3]))) -
        math.tan(math.radians(location[0])) * math.tan(math.radians(sunInfo[3]))))
    sunset = solarNoon + hasr * 4 / 1440

    # Increment day to calculate sunrise time for the next day
    sunInfo = info(gTime + timedelta(days=1), timezone, location)
    solarNoon = (720 - 4 * location[1] - sunInfo[2] + timezone * 60) / 1440
    hasr = math.degrees(math.acos(
        math.cos(math.radians(90.833)) / (math.cos(math.radians(location[0])) * math.cos(math.radians(sunInfo[3]))) -
        math.tan(math.radians(location[0])) * math.tan(math.radians(sunInfo[3]))))
    sunrise = solarNoon - hasr * 4 / 1440

    # Parse the datetime object of sunrise and sunset times
    dt_sunrise = datetime(2017, 10, gTime.day+1, int(sunrise*24), int(60*(sunrise-int(sunrise*24)/24)))
    dt_sunset = datetime(2017, 10, gTime.day, int(sunset*24), int(60*(sunset-int(sunset*24)/24)))
    return dt_sunrise, dt_sunset


def air_mass(h):
    # Input is elevation angle h in degrees
    temp = 1229 + math.pow(614*math.sin(math.radians(h)), 2)
    m = math.sqrt(temp) - 614*math.sin(math.radians(h))
    return m


def transmittance(m):
    # Input is air mass m
    tau = 0.56*(1/math.pow(math.e, 0.65*m) + 1/math.pow(math.e, 0.095*m))
    return tau


# Function is fragile for some combinations of time and GPS LatLong inputs
def irradiance(sunInfo):
    # Based on http://www.wsl.ch/staff/niklaus.zimmermann/programs/aml1_1.html
    # returns direct normal extraterrestrial solar irradiance and solar irradiance on earth's surface
    # irradiance = measure of instantaneous rate of energy delivered to a surface [W/m^2]
    m = air_mass(sunInfo[0])
    tau = transmittance(m)
    # direct normal extraterrestrial solar radiation
    io = 1367*(1 + 0.034*(math.cos(math.radians(360*sunInfo[4]))/365))
    # solar radiation on a horizontal plane on earth's surface with atmospheric attenuation
    ioh = io * tau * math.cos(math.radians(90 - sunInfo[0]))
    return ioh
