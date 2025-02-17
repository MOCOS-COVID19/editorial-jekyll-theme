#!/usr/bin/env python
# coding: utf-8

import click
import datetime
from dateutil.parser import parse
import locale
import numpy as np
import os
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

HOSPITALIZATION_SCENARIO = '_hospitalizations'

CSV_NAME_MAP = {
    "pl_PL": {
        "p2.5": "dolne 2.5% modelowań",
        "p25": "dolne 25% modelowań",
        "p75": "górne 25% modelowań",
        "p97.5": "górne 2.5% modelowań",
        "mean": "średnia z modelowań"
      },
    "en_GB": {
          "p2.5": "2.5% percentile",
          "p25": "25% percentile",
          "p75": "75% percentile",
          "p97.5": "97.5% percentile",
          "mean": "point prediction"
        },
    "de_DE": {
          "p2.5": "Untere 2,5% der Modellierung",
          "p25": "Die unteren 25% der Modellierung",
          "p75": "Top 25% der Modellierung",
          "p97.5": "Top 2,5% der Modellierung",
          "mean": "Durchschnitt der Modellierung"
        }
}

MOVING_AVG_STR = {
    "pl_PL": "7-dn. średnia zdiagnozowanych zakażeń",
    "en_GB": "7 day moving average of detected cases",
    "de_DE": "7 Tage gleitender Durchschnitt der erkannten Fälle"
}

MOVING_AVG_STR2 = {
    "pl_PL": "7-dn. średnia<br>zdiagnozowanych zakażeń",
    "en_GB": "7 day moving average<br>of detected cases",
    "de_DE": "7 Tage gleitender Durchschnitt<br>der erkannten Fälle"
}

MOVING_AVG_D_STR = {
    "pl_PL": "7-dn. średnia przypadków śmiertelnych",
    "en_GB": "7 day moving average of death cases",
    "de_DE": "7 Tage gleitender Durchschnitt der Todesfälle"
}

MOVING_AVG_D_STR2 = {
    "pl_PL": "7-dn. średnia<br>przypadków śmiertelnych",
    "en_GB": "7 day moving average<br>of death cases",
    "de_DE": "7 Tage gleitender Durchschnitt<br>der Todesfälle"
}

MOVING_AVG_H_STR = {
    "pl_PL": "7-dn. średnia<br>liczby osób hospitalizowanych",
    "en_GB": "7 day moving average of hospitalized persons",
    "de_DE": "7 Tage gleitender Durchschnitt der<br>Anzahl der hospitalisierten Personen"
}

MOVING_AVG_H_STR2 = {
    "pl_PL": "7-dn. średnia<br>liczby osób wymagających<br>hospitalizacji",
    "en_GB": "7 day moving average of<br>number of persons requiring<br>hospitalization",
    "de_DE": "7 Tage gleitender Durchschnitt der<br>anzahl der Personen, die<br>einen Krankenhausaufenthalt benötigen"
}

NEW_CASES_STR = {
    "pl_PL": "dzienne wykryte przypadki zachorowań",
    "en_GB": "daily detected cases",
    "de_DE": "täglich erkannte Fälle"
}

TOO_HIGH_STR = {
    "pl_PL": "liczba dziennie zdiagnozowanych osób może być jeszcze wyższa",
    "en_GB": "daily detected cases might be even larger",
    "de_DE": "Anzahl der täglich entdeckten Fälle könnte noch größer sein"
}

NEW_DEATHS_STR = {
    "pl_PL": "dzienne przypadki śmiertelne w związku z COVID",
    "en_GB": "daily deaths related to COVID",
    "de_DE": "tägliche Todesfälle im Zusammenhang mit COVID"
}

NEW_HOSPITALIZATION_STR = {
    "pl_PL": "liczba osób hospitalizowanych",
    "en_GB": "number of hospitalized persons",
    "de_DE": "Anzahl der hospitalisierten Personen"
}

COLUMNS = ["p2.5", "p25", "mean", "p75", "p97.5"]

LINE_COLORS = {
    "p2.5":  'rgb(166,97,26)',
    "p25":   'rgb(223,194,125)',
    "p75":   'rgb(128,205,193)',
    "p97.5": 'rgb(1,133,113)',
    "mean":  'blue',
}

FILL_COLORS = {
    "p2.5":  None,
    "p25":   'rgba(166,97,26,0.2)',
    "mean":  'rgba(223,194,125,0.2)',
    "p75":   'rgba(128,205,193,0.2)',
    "p97.5": 'rgba(1,133,113,0.2)',
}

XAXIS_STR = {
"pl_PL": "Data",
"en_GB": "date",
"de_DE": "Datum"
}

PROGNOSIS_DIRS = {
    "pl_PL": "_prognosis_pl",
    "en_GB": "_prognosis_en",
    "de_DE": "_prognosis_de"
}

PROGNOSIS_TEMPLATES_DIR = '_prognosis_templates'
YAXIS_STR = MOVING_AVG_STR
YAXIS_D_STR = MOVING_AVG_D_STR

LAYOUT_TEMPLATE = {
    "xaxis": {
        "title": 'Data',
    },
    "yaxis": {
        "title": '7-dn. średnia nowych zakażeń',
        "hoverformat": ".0f"
    },
    "legend": {
        "orientation": "h",
        "xanchor": "center",
        "y": -.6,
        "x": 0.5
    },
    "hovermode": "x",
    "hoverlabel_namelength": -1,
    
}

def prepare_layout(language):
    layout = LAYOUT_TEMPLATE
    layout['xaxis']['title'] = XAXIS_STR[language]
    layout['yaxis']['title'] = YAXIS_STR[language]
    return layout

def prepare_layout_d(language):
    layout = LAYOUT_TEMPLATE
    layout['xaxis']['title'] = XAXIS_STR[language]
    layout['yaxis']['title'] = YAXIS_D_STR[language]
    return layout

def prepare_title(language):
    title = MOVING_AVG_STR2[language]
    return title

def prepare_title_d(language):
    title = MOVING_AVG_D_STR2[language]
    return title

def prepare_title_h(language):
    title = MOVING_AVG_H_STR2[language]
    return title

def handle_dates(x, format='%d/%m/%y'):
    newdate = pd.to_datetime(x, format=format)
    return newdate
    # return [d.strftime('%d %B, %Y') for d in newdate]

def apply_str_on_dates(newdate, format='%d %b %Y'):
    return newdate.strftime(format=format)


@click.group()
def cli1():
    pass

@click.group()
def cli2():
    pass

@click.group()
def cli3():
    pass

@click.group()
def cli4():
    pass


@cli1.command('main')
@click.argument("input_csv", type=str, default='scenario.csv')
@click.argument("cloned_repo_path", required=True, type=str, default='/mnt/e/Projects/MOCOS/mocos-covid19.github.io')
def main_function(input_csv, cloned_repo_path):
    fun(input_csv, cloned_repo_path)


def cases(input_csv, language):
    traces = []
    df=pd.read_csv(input_csv)
    df = df.iloc[:30] # show only next thirty days even if you have more
    print(df.iloc[:7]['dates'])
    df['dates']=df['dates'].apply(handle_dates)
    df['dates1']=df['dates'].apply(apply_str_on_dates)
    dates_with_14_days_before = sorted(list(set(df['dates'].apply(lambda x: x - pd.Timedelta('14days')).apply(apply_str_on_dates).to_numpy()).union(set(df['dates1'].to_numpy()))))
    
    # print(df['dates1'])
    df2 = pd.read_csv('https://raw.githubusercontent.com/KITmetricslab/covid19-forecast-hub-de/master/data-truth/MZ/truth_MZ-Incident%20Cases_Poland.csv')
    
    df2=df2.query('location == "PL"').sort_values('date')#.set_index('date')
    df2['datetime'] = df2['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
    all_dates = set(pd.date_range(start=df2['datetime'].min(), end=df2['datetime'].max()))
    existing_dates = set(df2['datetime'])
    missing_dates = all_dates - existing_dates
    if len(missing_dates) > 0:
        for missing_date in missing_dates:
            df2 = df2.append({'date': missing_date.strftime(format='%Y-%m-%d'), 'value': np.nan}, ignore_index=True)
    df2 = df2.sort_values('date')

    df2['date']=df2['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d")-pd.Timedelta('1day')).apply(apply_str_on_dates)
    
    moving = df2.set_index('date')['value'].rolling(7, min_periods=1).mean().reset_index()
    df2 = df2[df2['date'].isin(dates_with_14_days_before)]
    moving = moving[moving['date'].isin(dates_with_14_days_before)]
    # print(df2['date'])
    # exit()
    traces.append(go.Scatter(
            x=df2['date'],
            y=df2['value'].values.tolist(),
            name=NEW_CASES_STR[language],
            fill="none",
            mode="markers",
            marker_color="black"
        ))

    traces.append(go.Scatter(
            x=moving['date'],
            y=moving['value'].values.tolist(),
            name=MOVING_AVG_STR[language],
            fill="none",
            mode="lines",
            marker_color="black"
        ))
    for column in COLUMNS:
    
        traces.append(go.Scatter(
            x=df['dates1'],
            y=df[column].values.tolist(),
            name=CSV_NAME_MAP[language][column],
            fill="none" if column =="p2.5" else "tonexty",
            mode="lines",
            line_color=LINE_COLORS[column],
            fillcolor=FILL_COLORS[column]
        ))
    date=df.iloc[0]['dates'].strftime("%Y%m%d")
    if date == '20220103':
        # exception!
        df = df[df["p97.5"] >= 149000]
        traces.append(go.Scatter(
            x=df['dates1'],
            y=[150000] * len(df['dates1']),
            name=TOO_HIGH_STR[language],
            mode='lines',
            line={'dash': 'dot', 'width': 10},
            line_color='red'))
    fig = go.Figure(data=traces, layout=prepare_layout(language))
    fig.update_xaxes(tickformat='%d-%b-%y')
    
    
    return fig, date


def deaths(input_csv, language):
    traces = []
    df=pd.read_csv(input_csv)
    df = df.iloc[:30] # show only next thirty days even if you have more
    print(df.iloc[:7]['dates'])
    df['dates']=df['dates'].apply(handle_dates)
    df['dates1']=df['dates'].apply(apply_str_on_dates)
    dates_with_14_days_before = sorted(list(set(df['dates'].apply(lambda x: x - pd.Timedelta('14days')).apply(apply_str_on_dates).to_numpy()).union(set(df['dates1'].to_numpy()))))
    
    # print(df['dates1'])
    df2 = pd.read_csv('https://raw.githubusercontent.com/KITmetricslab/covid19-forecast-hub-de/master/data-truth/MZ/truth_MZ-Incident%20Deaths_Poland.csv')
    
    df2=df2.query('location == "PL"').sort_values('date')#.set_index('date')
    df2['datetime'] = df2['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
    all_dates = set(pd.date_range(start=df2['datetime'].min(), end=df2['datetime'].max()))
    existing_dates = set(df2['datetime'])
    missing_dates = all_dates - existing_dates
    if len(missing_dates) > 0:
        for missing_date in missing_dates:
            df2 = df2.append({'date': missing_date.strftime(format='%Y-%m-%d'), 'value': np.nan}, ignore_index=True)
    df2 = df2.sort_values('date')

    df2['date']=df2['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d")-pd.Timedelta('1day')).apply(apply_str_on_dates)
    
    moving = df2.set_index('date')['value'].rolling(7, min_periods=1).mean().reset_index()
    df2 = df2[df2['date'].isin(dates_with_14_days_before)]
    moving = moving[moving['date'].isin(dates_with_14_days_before)]
    # print(df2['date'])
    # exit()
    traces.append(go.Scatter(
            x=df2['date'],
            y=df2['value'].values.tolist(),
            name=NEW_DEATHS_STR[language],
            fill="none",
            mode="markers",
            marker_color="black"
        ))

    traces.append(go.Scatter(
            x=moving['date'],
            y=moving['value'].values.tolist(),
            name=MOVING_AVG_D_STR[language],
            fill="none",
            mode="lines",
            marker_color="black"
        ))
    for column in COLUMNS:
    
        traces.append(go.Scatter(
            x=df['dates1'],
            y=df[column].values.tolist(),
            name=CSV_NAME_MAP[language][column],
            fill="none" if column =="p2.5" else "tonexty",
            mode="lines",
            line_color=LINE_COLORS[column],
            fillcolor=FILL_COLORS[column]
        ))
    fig = go.Figure(data=traces, layout=prepare_layout_d(language))
    fig.update_xaxes(tickformat='%d-%b-%y')

    date=df.iloc[0]['dates'].strftime("%Y%m%d")
    return fig, date



def hospitalizations(input_csv, language):
    traces = []
    df=pd.read_csv(input_csv)
    df = df.iloc[:30] # show only next thirty days even if you have more
    print(df.iloc[:7]['dates'])
    df['dates']=df['dates'].apply(handle_dates)
    df['dates1']=df['dates'].apply(apply_str_on_dates)
    dates_with_14_days_before = sorted(list(set(df['dates'].apply(lambda x: x - pd.Timedelta('14days')).apply(apply_str_on_dates).to_numpy()).union(set(df['dates1'].to_numpy()))))
    
    # print(df['dates1'])
    df2 = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/hospitalicuadmissionrates/csv/data.csv')
    df2=df2.query('country == "Poland"').query('indicator == "Daily hospital occupancy"').sort_values('date')#.set_index('date')
    df2['datetime'] = df2['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
    all_dates = set(pd.date_range(start=df2['datetime'].min(), end=df2['datetime'].max()))
    existing_dates = set(df2['datetime'])
    missing_dates = all_dates - existing_dates
    if len(missing_dates) > 0:
        for missing_date in missing_dates:
            df2 = df2.append({'date': missing_date.strftime(format='%Y-%m-%d'), 'value': np.nan}, ignore_index=True)
    df2 = df2.sort_values('date')

    df2['date']=df2['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d")-pd.Timedelta('1day')).apply(apply_str_on_dates)
    
    moving = df2.set_index('date')['value'].rolling(7, min_periods=1).mean().reset_index()
    df2 = df2[df2['date'].isin(dates_with_14_days_before)]
    moving = moving[moving['date'].isin(dates_with_14_days_before)]
    # print(df2['date'])
    # exit()
    traces.append(go.Scatter(
            x=df2['date'],
            y=df2['value'].values.tolist(),
            name=NEW_HOSPITALIZATION_STR[language],
            fill="none",
            mode="markers",
            marker_color="black"
        ))

    traces.append(go.Scatter(
            x=moving['date'],
            y=moving['value'].values.tolist(),
            name=MOVING_AVG_H_STR[language],
            fill="none",
            mode="lines",
            marker_color="black"
        ))
    for column in COLUMNS:
    
        traces.append(go.Scatter(
            x=df['dates1'],
            y=df[column].values.tolist(),
            name=CSV_NAME_MAP[language][column],
            fill="none" if column =="p2.5" else "tonexty",
            mode="lines",
            line_color=LINE_COLORS[column],
            fillcolor=FILL_COLORS[column]
        ))
    fig = go.Figure(data=traces, layout=prepare_layout_d(language))
    fig.update_xaxes(tickformat='%d-%b-%y')

    date=df.iloc[0]['dates'].strftime("%Y%m%d")
    return fig, date

def fun(input_csv, cloned_repo_path):
    date = None
    scenario_type = None
    for language in ['pl_PL', 'en_GB', 'de_DE']:
        locale.setlocale(locale.LC_ALL, language)
        title_text = None
        filename = input_csv.split('/')[-1]
        if (filename.startswith('scenario') or 'detections' in filename) and 'death' not in filename and 'hospitalization' not in filename:
            fig, date = cases(input_csv, language)
            scenario_type = '' # default
            title_text = prepare_title(language)
        else:
            if 'death' in filename:
                fig, date = deaths(input_csv, language)
                scenario_type = '_deaths'
                title_text = prepare_title_d(language)
            elif 'hospitalization' in filename:
                fig, date = hospitalizations(input_csv, language)
                scenario_type = HOSPITALIZATION_SCENARIO
                title_text = prepare_title_h(language)
        if date not in input_csv:
            print(f'ignoring the file - inconsistency in dates: {date} vs {input_csv}')
            return
        elif (datetime.datetime.now() - parse(date)).days > 50:
            print(f'date {date} is too old (older than 50 days from now), ignoring')
            return
        else:
            savedir = Path(f"{cloned_repo_path}/assets/images/reports/{date}/")
            savedir.mkdir(exist_ok=True)
            fig.update_layout(yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text=title_text)), xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='')))
            if date == '20220103' and scenario_type == '':
                scenario = filename[35:36]
                
                fig.write_html(str(savedir/f"prognoza_{language[:2]}{scenario_type}_{scenario}.html"))
                fig.write_image(str(savedir/f"prognoza_{language[:2]}{scenario_type}_{scenario}.png"))
            else:
                fig.write_html(str(savedir/f"prognoza_{language[:2]}{scenario_type}.html"))
                fig.write_image(str(savedir/f"prognoza_{language[:2]}{scenario_type}.png"))

            click.echo(f"Written chart files to {savedir}")
    if date not in input_csv:
        print(f'ignoring the file - inconsistency in dates: {date} vs {input_csv}')
    else:
        add_prognosis_fun(date=date, overwrite=False, scenario_type=scenario_type)
    print('END')

@cli2.command()
@click.argument("cloned_repo_path", required=True, type=str, default='.')
def batch(cloned_repo_path):
    forecasts_dir = os.path.join(cloned_repo_path, 'assets', 'forecasts')
    listdir = list(os.listdir(forecasts_dir))
    for csv_file in listdir:
        if csv_file.endswith('.csv'):
            print(os.path.join(forecasts_dir, csv_file))
            fun(os.path.join(forecasts_dir, csv_file),
                          cloned_repo_path)

@cli3.command()
def mz():
    df1 = pd.read_csv('https://raw.githubusercontent.com/KITmetricslab/covid19-forecast-hub-de/master/data-truth/MZ/truth_MZ-Incident%20Cases_Poland.csv')

    df1 = df1.query('location == "PL"').sort_values('date')#.set_index('date')
    df1['date']=df1['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d")-pd.Timedelta('1day')).apply(apply_str_on_dates)
    df1['7day']=df1['value'].rolling(7, min_periods=1).sum()
    print(df1.tail(n=14))
    df2 = pd.read_csv('https://raw.githubusercontent.com/KITmetricslab/covid19-forecast-hub-de/master/data-truth/MZ/truth_MZ-Incident%20Deaths_Poland.csv')

    df2 = df2.query('location == "PL"').sort_values('date')#.set_index('date')
    df2['date']=df2['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d")-pd.Timedelta('1day')).apply(apply_str_on_dates)
    df2['7day'] = df2['value'].rolling(7, min_periods=1).sum()
    print(df2.tail(n=14))

    df3 = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/hospitalicuadmissionrates/csv/data.csv')
    print(df3.columns)
    df3 = df3.query('country == "Poland"').sort_values('date')#.set_index('date')
    df3['date']=df3['date'].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d")-pd.Timedelta('1day')).apply(apply_str_on_dates)
    df3['7day'] = df3['value'].rolling(7, min_periods=1).sum()
    print(df3.tail(n=14))

PROGNOSIS_TEMPLATE_KEYWORDS_TO_FORMAT = {
'%datedotreversed%': '%d.%m.%Y',
'%date%': '%Y%m%d',
'%datedot%': '%Y.%m.%d'
}

@cli4.command()
@click.argument('date', required=True, type=str)
@click.argument('overwrite', type=bool, default=False)
def add_prognosis(date, overwrite):
    add_prognosis_fun(date, overwrite, scenario_type=None)

def add_prognosis_fun(date, overwrite, scenario_type=None):
    if date == '20220103':
        print(f'special date detected {date}, not using template')
        return False
    format = '%Y%m%d'
    try:
      real_date = datetime.datetime.strptime(date, format)
      print("This is the correct date string format.")
    except ValueError:
      print(f"Input date: {date} is the incorrect date string format. It should be {format}")
    for lang, dir in PROGNOSIS_DIRS.items():
        mode = f'{lang}-no_hosp'
        if scenario_type == HOSPITALIZATION_SCENARIO:
            mode = lang
            overwrite = True
        
        prognosis_filename = os.path.join(dir, f'{date}.md')
        if os.path.exists(prognosis_filename):
            if not overwrite:
                print(f'overwrite set to false, omitting this one (lang={lang}, date={date})...')
                continue
        content = []
        with open(os.path.join(PROGNOSIS_TEMPLATES_DIR, f'{mode}.md'), 'r') as f:
            content = f.read()
        for keyword, format in PROGNOSIS_TEMPLATE_KEYWORDS_TO_FORMAT.items():
            content = content.replace(keyword, real_date.strftime(format))
        with open(prognosis_filename, 'w') as f:
            f.write(content)


cli = click.CommandCollection(sources=[cli1, cli2, cli3, cli4])
if __name__ == '__main__':
    cli()
