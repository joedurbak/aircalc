import os
import warnings
import collections
from datetime import timezone
from datetime import datetime as dt
from datetime import timedelta as td

import pandas
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.coordinates import AltAz
from astropy import units as u
from astropy.utils.exceptions import AstropyDeprecationWarning
from matplotlib import pyplot as plt
from astroplan import Observer, FixedTarget
from astroplan.plots import plot_sky, plot_airmass
from astroplan import moon

from aircalc.utils import SETTINGS, gen_observatory_file_name, load_pickle, save_pickle

warnings.filterwarnings("ignore", category=AstropyDeprecationWarning)


def observatory_loc():
    location_name = SETTINGS['OBSERVATORY']
    location_pickle = gen_observatory_file_name()
    try:
        observatory_loc_dict = load_pickle(location_pickle)
        observer = observatory_loc_dict['observer']
    except FileNotFoundError:
        observer = Observer.at_site(location_name)
        archive_time = dt.utcnow()
        observatory_loc_dict = {'archive_time': archive_time, 'observer': observer}
        save_pickle(observatory_loc_dict, location_pickle)
    return observer


OBSERVER = observatory_loc()
LOCATION = OBSERVER.location


def radec_to_altaz(
        ra, dec, unit,
        observing_location=LOCATION,
):
    observing_time = Time(str(dt.utcnow()))
    aa = AltAz(location=observing_location, obstime=observing_time)
    coord = SkyCoord(ra, dec, unit=unit)
    altaz_coord = coord.transform_to(aa)
    alt = altaz_coord.alt.degree
    az = altaz_coord.az.degree
    return alt, az


def plot_targets(targets, obstime):
    for target in targets:
        # sun_set_tonight = OBSERVER.sun_set_time(time=obstime)
        # sun_rise_tonight = OBSERVER.sun_rise_time(time=obstime)
        plot_airmass(target, OBSERVER, obstime)
    _moon = moon.get_moon(obstime, location=LOCATION)
    _moon.name = 'Moon'
    moon_style = {'linestyle': '--', 'color': 'black'}
    print(_moon.name)
    ax = plot_airmass(
        _moon, OBSERVER, obstime, brightness_shading=True, style_kwargs=moon_style, altitude_yaxis=True
    )
    ax.legend()
    plt.show()

    for target in targets:
        plot_sky(target, OBSERVER, obstime)
    ax2 = plot_sky(_moon, OBSERVER, obstime)
    ax2.legend()
    plt.show()


def handle_target_list(target_list_df, plot=True):
    targets = []
    csv_dicts = []
    obstime = Time(str(dt.utcnow()))
    horizon = SETTINGS['HORIZONRISEDEGREES'] * u.degree
    for name, ra, dec, block_id in zip(
            target_list_df['ObjectName'], target_list_df['RA'], target_list_df['DEC'], target_list_df['BlockID']
    ):
        try:
            ra_coord = float(ra)
            dec_coord = float(dec)
            sky_coord = SkyCoord(ra_coord, dec_coord, unit=u.degree)
        except ValueError:
            unit = (u.hourangle, u.deg)
            sky_coord = SkyCoord('{} {}'.format(ra, dec), unit=unit)
        target = FixedTarget(sky_coord, name=name)
        aa = OBSERVER.altaz(target=target, time=obstime)
        if OBSERVER.is_night(time=obstime):
            time_which = 'nearest'
        else:
            time_which = 'next'
        rise_time = OBSERVER.target_rise_time(target=target, time=obstime, horizon=horizon, which=time_which)
        set_time = OBSERVER.target_set_time(target=target, time=obstime, horizon=horizon, which=time_which)
        airmass = aa.secz
        csv_dicts.append({
            'BlockID': block_id, 'RA': ra, 'DEC': dec, 'ObjectName': name,
            'AirMass': airmass, 'RiseTime': rise_time.iso, 'SetTime': set_time.iso,
        })
        targets.append(target)
    if plot:
        plot_targets(targets, obstime)
    return pandas.DataFrame(csv_dicts)
