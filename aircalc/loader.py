import os.path
import webbrowser

import pandas as pd
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from aircalc.utils import SETTINGS, html_template


def load_csv(filename):
    df = pd.read_csv(filename, sep=',', header=0)
    return df[SETTINGS['INPUTCSVFIELDS']]


def save_csv(data_frame, filename_prefix):
    assert isinstance(data_frame, pd.DataFrame)
    data_frame.to_csv(filename_prefix+'.csv')


def save_html(data_frame, filename_prefix):
    assert isinstance(data_frame, pd.DataFrame)
    filename = filename_prefix + '.html'
    html_table = data_frame.to_html(classes="table table-hover table-striped", table_id="sortTable")
    env = Environment(loader=FileSystemLoader(os.path.dirname(html_template)))
    template = env.get_template(os.path.basename(html_template))
    render_dict = {
        'airmass_png': os.path.basename(filename_prefix + SETTINGS['AIRMASSPLOTSUFFIX']),
        'skyplot_png': os.path.basename(filename_prefix + SETTINGS['SKYPLOTSUFFIX']),
        'airmass_table': html_table
    }
    print(render_dict)
    output_html = template.render(**render_dict)
    with open(filename, 'w') as f:
        f.write(output_html)
    url = 'file:///' + os.path.realpath(filename).replace(os.path.sep, '/')
    webbrowser.open(url, new=0, autoraise=True)


if __name__ == '__main__':
    print(load_csv(r'F:\Observation List\My Test Observations.csv'))
