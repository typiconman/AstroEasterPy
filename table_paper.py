import datetime
import csv

from skyfield.api import load
from scipy.optimize import brentq
import numpy as np
import datetime

def load_ephemeris_for_year(year):
    """Load de440.bsp for 1549 <= year <= 2650, otherwise load de406.bsp."""
    if 1549 <= year <= 2650:
        eph = load('de440.bsp')
    else:
        eph = load('de406.bsp')
    return eph

def vernal_equinox(ts, eph, year):
    """Returns a Skyfield Time Object with the instant of the vernal equinox for year"""
    earth = eph['earth']
    sun = eph['sun']

    # Define a function returning Sun's apparent ecliptic longitude minus 0°
    def sun_longitude_minus_zero(jd):
        t = ts.tt(jd=jd)
        astrometric = earth.at(t).observe(sun).apparent()
        lon = astrometric.ecliptic_latlon(epoch='date')[1]
        # Wrap to [-180, 180) for robust root-finding
        return ((lon.degrees + 180) % 360) - 180

    # Estimate: Vernal equinox occurs around March 20
    t0 = ts.utc(year, 3, 18)
    t1 = ts.utc(year, 3, 22)
    jd0 = t0.tt
    jd1 = t1.tt

    # Root-finding to solve sun_longitude_minus_zero(jd) == 0
    eq_jd = brentq(sun_longitude_minus_zero, jd0, jd1)
    eq_time = ts.tt(jd=eq_jd)

    # Return as a Skyfield Time object (can use eq_time.utc_datetime(), eq_time.utc_iso(), etc.)
    return eq_time

def elongation_from_sun(ts, eph, jd):
    """Returns the Elongation of the moon from the sun in degrees at given Julian date jd."""
    t = ts.tt(jd=jd)
    earth = eph['earth']
    sun = eph['sun']
    moon = eph['moon']
    astrometric_sun = earth.at(t).observe(sun).apparent()
    astrometric_moon = earth.at(t).observe(moon).apparent()

    # Use ecliptic longitude in true equinox of date
    sun_lon = astrometric_sun.ecliptic_latlon(epoch='date')[1].degrees
    moon_lon = astrometric_moon.ecliptic_latlon(epoch='date')[1].degrees

    elong = (moon_lon - sun_lon) % 360
    return elong

def get_first_full_moon_after(ts, eph, time_after, window_days=30):
    """Returns a SkyField Time Object with the instant of the 
       first full moon after a given Skyfield Time object (time_after).
       If no moon found, returns None."""
    jd0 = time_after.tt
    jd1 = jd0 + window_days
    num_steps = int((jd1 - jd0) * 24) + 1  
    times = np.linspace(jd0, jd1, num_steps)
    values = [elongation_from_sun(ts, eph, jd) for jd in times]  # convert MJD to JD

    # Now look for where elongation crosses from <180 to >=180
    for i in range(len(values) - 1):
        if values[i] < 180 <= values[i + 1]:
            # Bracketed the full moon! Now root-find for elongation-180=0
            def elong_minus_180(jd):
                elong = elongation_from_sun(ts, eph, jd)
                return elong - 180
            
            fm_jd = brentq(elong_minus_180, times[i], times[i + 1], xtol=1e-9)
            fm_time = ts.tt(jd=fm_jd)
            return fm_time
    return None

def mean_solar_time_utc(time, longitude_deg):
    """Converts a Skyfield Time Object or UTC datetime to mean solar time at given longitude (in degrees east).
    
    Args:
        time: Skyfield Time object (or a Python datetime in UTC)
        longitude_deg: Longitude in degrees east (positive east, negative west)
    Returns:
        Python datetime object in local mean solar time.
    """
    # Skyfield Time: get UTC datetime
    if hasattr(time, 'utc_datetime'):
        # Skyfield Time object
        dt_utc = time.utc_datetime()
    else:
        dt_utc = time  # Assume it's already a datetime in UTC

    # Offset in minutes: 4 min per degree east
    offset_minutes = longitude_deg * 4
    # Compute mean solar time
    mst = dt_utc + datetime.timedelta(minutes=offset_minutes)
    return mst

def next_sunday_after_mean_solar_time(time):
    """
    Returns the month and day of the next Sunday after a Skyfield Time Object (or a Python datetime in UTC)
    """

    # Skyfield Time: get UTC datetime
    if hasattr(time, 'utc_datetime'):
        # Skyfield Time object
        dt = time.utc_datetime()
    else:
        dt = time  # Assume it's already a datetime in UTC

    # weekday(): Monday=0 ... Sunday=6
    days_until_sunday = (6 - dt.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7  # If already Sunday, go to next Sunday
    next_sunday = dt + datetime.timedelta(days=days_until_sunday)
    return next_sunday.date().strftime("%B %-d")

def julian_easter(year):
    """
    Use the Gaussian formulae to calculate Easter on the Alexandria Paschallion
    Warning: because of the hardcoded 13 below, only valid for 1900-2099
    """

    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    f = int((d + e + 114) / 31) #Month of pascha e.g. march=3
    g = ((d + e + 114) % 31) + 1 #Day of pascha in the month
    day = g + 13 # assume the Julian calendar offset is 13 days
    month = "March"
    if (day >= 35 and f == 3):
        month = "April"
        day  -= 31
    elif (day >= 31 and f == 4):
        month = "May"
        day  -= 30
    else:
        month = "April"
    
    return f"{month} {day}"

def gregorian_easter(year):
    """
    Formula for computing Gregorian Easter due to Meeus, Astronomical Algorithms
    """
    a = year % 19
    b = int(year / 100)
    c = year % 100
    d = int(b / 4)
    e = b % 4
    f = int((b + 8) / 25)
    g = int((b - f + 1) / 3)
    h = (19 * a + b - d - g + 15) % 30
    i = int(c / 4)
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = int((a + 11 * h + 22 * l) / 451)
    n = int((h + l - 7 * m + 114) / 31)
    p = (h + l - 7 * m + 114) % 31
    month = "March" if n == 3 else "April"
    return f"{month} {p + 1}"

def main():
    import sys

    longitude = 35.2298  # degrees East
    ts = load.timescale()

    with open('table.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Year', 'Vernal Equinox', 'Paschal Moon', 'Astronomical Easter', 'Gregorian Easter', 'Julian Easter'])

        for year in range(2025, 2076, 1):
            eph = load_ephemeris_for_year(year)

            ve_time = vernal_equinox(ts, eph, year)
            ve_mst = mean_solar_time_utc(ve_time, longitude)
            full_moon = get_first_full_moon_after(ts, eph, ve_time)
            if full_moon is None:
                print("Error: a full moon was not found. Exiting.")
                sys.exit()

            full_moon_mst = mean_solar_time_utc(full_moon, longitude)
            next_sunday = next_sunday_after_mean_solar_time(full_moon_mst)
            writer.writerow([year, ve_mst.strftime('%B %-d %H:%M'), full_moon_mst.strftime('%B %-d %H:%M'), next_sunday, gregorian_easter(year), julian_easter(year)])

if __name__ == "__main__":
    main()
    print("I finished creating table.csv")
