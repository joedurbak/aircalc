import warnings
from datetime import timezone
from datetime import datetime as dt

import pandas
from astropy.coordinates import SkyCoord
from astropy.time import Time
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
        observer = Observer.at_site(location_name, timezone=SETTINGS['TIMEZONE'])
        archive_time = dt.utcnow()
        observatory_loc_dict = {'archive_time': archive_time, 'observer': observer}
        save_pickle(observatory_loc_dict, location_pickle)
    return observer


OBSERVER = observatory_loc()
LOCATION = OBSERVER.location


def plot_targets(targets, obstime, file_prefix):
    for target in set(targets):
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
    plt.savefig(file_prefix+SETTINGS['AIRMASSPLOTSUFFIX'])
    plt.clf()

    for target in targets:
        plot_sky(target, OBSERVER, obstime)
    ax2 = plot_sky(_moon, OBSERVER, obstime)
    ax2.legend()
    plt.savefig(file_prefix + SETTINGS['SKYPLOTSUFFIX'])
    plt.clf()


def handle_target_list(target_list_df, plot=True, file_prefix='air'):
    targets = []
    csv_dicts = []
    radec = []
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
            'AirMass': airmass,
            'RiseTimeLocal': rise_time.datetime.strftime("%H:%M"),
            'SetTimeLocal': set_time.datetime.strftime("%H:%M")
        })
        if (ra, dec) not in radec:
            targets.append(target)
            radec.append((ra, dec))
    if plot:
        plot_targets(targets, obstime, file_prefix)
    return pandas.DataFrame(csv_dicts)
