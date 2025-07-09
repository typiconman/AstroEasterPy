from skyfield.api import load
from scipy.optimize import brentq
import numpy as np
import datetime
from datetime import timedelta

def load_ephemeris_for_year(year):
    """Load de440.bsp for 1549 <= year <= 2650, otherwise load de406.bsp."""
    if 1549 <= year <= 2650:
        eph = load('de440.bsp')
    else:
        eph = load('de406.bsp')
    return eph

def vernal_equinox(ts, eph, year):
    """Returns the a Skyfield Time Object with the instant of the vernal equinox for year"""
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
    mst = dt_utc + timedelta(minutes=offset_minutes)
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
    return next_sunday.date().strftime("%B %d")

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        year = int(sys.argv[1])
    else:
        year = 2025  # Default
        print("Usage: pascha-skyfield year. Year not specified, assuming 2025.")

    longitude = 35.2298  # degrees East
    ts = load.timescale()
    eph = load_ephemeris_for_year(year)

    ve_time = vernal_equinox(ts, eph, year)
    print("Vernal Equinox (UTC):", ve_time.utc_datetime().strftime('%Y-%m-%d %H:%M:%S'))
    ve_mst = mean_solar_time_utc(ve_time, longitude)
    print("Vernal Equinox (solar time at Jerusalem):", ve_mst.strftime('%Y-%m-%d %H:%M:%S'))
    full_moon = get_first_full_moon_after(ts, eph, ve_time)
    if full_moon is None:
        print("Error: a full moon was not found. Exiting.")
        sys.exit()

    print("Paschal full moon (UTC):", full_moon.utc_datetime().strftime('%Y-%m-%d %H:%M:%S'))
    full_moon_mst = mean_solar_time_utc(full_moon, longitude)
    print("Paschal full moon (solar time at Jerusalem):", full_moon_mst.strftime('%Y-%m-%d %H:%M:%S'))
    next_sunday = next_sunday_after_mean_solar_time(full_moon_mst)
    print(f"Easter in {year} is on {next_sunday}")
