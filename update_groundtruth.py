import pandas as pd
import numpy as np
from pathlib import Path
import click

ASSETS = 'assets'
DATASETS = 'datasets'
PL_CSV = 'pl.csv'
HOSPITAL = 'hospital'
DETECTIONS = 'detections'
DETECTIONS_WITHOUT_REINFECTIONS = 'detections_without_reinfections'
DEATHS = 'deaths'

@click.group()
def cli_pl():
    pass


@cli_pl.command()
def pl():
    run_pl()


def get_gt_for_pl_cases_and_deaths():
    df =
    pass


def get_gt_for_pl_hospital_beds():
    df3 = pd.read_csv('age/data.csv')
    df3 = df3.query('country == "Poland"').query('indicator == "Daily hospital occupancy"').sort_values('date')
    # df3['date'] = df3['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d") - pd.Timedelta('1day'))
    df3['7day_mean'] = df3['value'].rolling(7, min_periods=1).mean()
    df3 = df3[['date', 'value', '7day_mean']]
    print(df3.tail(n=14))
    return df3


def run_pl():
    pl_path = Path(ASSETS) / DATASETS / PL_CSV
    print(pl_path)
    hospital_beds = get_gt_for_pl_hospital_beds()
    #df = pd.read_csv(pl_path)

    #df.to_csv(pl_path)


cli = click.CommandCollection(sources=[cli_pl])
if __name__ == '__main__':
    cli()
