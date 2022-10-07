import argparse

from aircalc.loader import load_csv, save_csv
from aircalc.coords import handle_target_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'observation_list_csv', type=str, help='file containing observation list'
    )
    parser.add_argument(
        'output_csv', type=str, help='to use for the output'
    )
    parser.add_argument('--noplot', default=False, action='store_true', help='turn off plots')

    args = parser.parse_args()
    observation_list = load_csv(args.observation_list_csv)
    output_filename = args.output_csv
    noplot = args.noplot
    df = handle_target_list(observation_list, not noplot)
    save_csv(df, output_filename)


if __name__ == '__main__':
    main()
