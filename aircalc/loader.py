import pandas as pd

from aircalc.utils import SETTINGS


def load_csv(filename):
    df = pd.read_csv(filename, sep=',', header=0)
    return df[SETTINGS['INPUTCSVFIELDS']]


def save_csv(data_frame, filename):
    assert isinstance(data_frame, pd.DataFrame)
    data_frame.to_csv(filename)


if __name__ == '__main__':
    print(load_csv(r'F:\Observation List\My Test Observations.csv'))
