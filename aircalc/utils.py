import json
import os
import pickle
from threading import Lock

base_dir = os.path.split(__file__)[0]
base_dir = os.path.split(base_dir)[0]
html_template = os.path.join(base_dir, 'aircalc', 'template', 'aircalc.html')

DEFAULT_SETTINGS = {
    'OBSERVATORY': 'Sutherland',
    "INPUTCSVFIELDS": ["BlockID", "ObjectName", "RA", "DEC"],
    "HORIZONRISEDEGREES": 23,
    "AIRMASSPLOTSUFFIX": '.airmass.png',
    "SKYPLOTSUFFIX": '.skyplot.png',
    "TIMEZONE": 'Africa/Johannesburg'
}


class JSONHandler:
    def __init__(self, json_file):
        self.lock = Lock()
        self.json_file = json_file

    def json_dict_from_file(self):
        self.lock.acquire()
        with open(self.json_file, 'r') as f:
            json_dict = json.load(f)
        self.lock.release()
        return json_dict

    def save_dict_to_json(self, dictionary):
        self.lock.acquire()
        json_string = json.dumps(dictionary, indent=2)
        dirname = os.path.dirname(self.json_file)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        with open(self.json_file, 'w') as f:
            f.write(json_string)
        self.lock.release()


def json_dict_from_file(json_file):
    return JSONHandler(json_file).json_dict_from_file()


def save_dict_to_json(dictionary, file_name):
    JSONHandler(file_name).save_dict_to_json(dictionary)


def gen_settings_file_name():
    return os.path.join(base_dir, 'settings.json')


def gen_observatory_file_name():
    return os.path.join(base_dir, 'observatory.p')


def save_settings(settings_dict):
    fname = gen_settings_file_name()
    save_dict_to_json(settings_dict, fname)


def load_settings():
    try:
        input_settings_dict = json_dict_from_file(gen_settings_file_name())
    except FileNotFoundError as e:
        print(e)
        save_settings(DEFAULT_SETTINGS)
        input_settings_dict = {}
    settings_dict = input_settings_dict.copy()
    for k, v in input_settings_dict.items():
        settings_dict[k.upper()] = v
    for k, v in DEFAULT_SETTINGS.items():
        input_settings_dict[k] = settings_dict.get(k, v)
    # print(input_settings_dict)
    return input_settings_dict


def load_pickle(filename):
    with open(filename, 'rb') as f:
        _obj = pickle.load(f)
    return _obj


def save_pickle(obj, filename):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)


SETTINGS = load_settings()
