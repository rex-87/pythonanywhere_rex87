from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
import time
import datetime as dt
import json

data_update_time = None

cumul_confir_df = None
cumul_deaths_df = None
daily_confir_df = None
daily_deaths_df = None

selected_country_l = None

def download_data():

    global data_update_time

    # ---- raw csv to df
    # LOG.info("get data from https://github.com/CSSEGISandData/COVID-19 ...")
    confir_df = pd.read_csv(r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv').transpose().reset_index()
    deaths_df = pd.read_csv(r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv').transpose().reset_index()

    # ---- create date column from index
    # LOG.info("create date column from index ...")
    global cumul_confir_df
    global cumul_deaths_df
    cumul_confir_df = confir_df.loc[4:,:].rename(columns={'index':'date'})
    cumul_deaths_df = deaths_df.loc[4:,:].rename(columns={'index':'date'})

    # ---- use appropriate date format for plotly
    # LOG.info("use appropriate date format for plotly ...")
    cumul_confir_df.date = pd.to_datetime(cumul_confir_df.date)    
    cumul_deaths_df.date = pd.to_datetime(cumul_deaths_df.date)    

    # ---- rename columns with country names
    # LOG.info("rename columns with country names ...")
    country_count = 266   
    for c in range(country_count):
        cumul_confir_df = cumul_confir_df.rename(columns={c:"{}; {}".format(confir_df.loc[1, c], confir_df.loc[0, c]).replace('; nan', '')})
        cumul_deaths_df = cumul_deaths_df.rename(columns={c:"{}; {}".format(deaths_df.loc[1, c], deaths_df.loc[0, c]).replace('; nan', '')})

    # ---- daily processing
    # LOG.info("process cumul data to get daily data ...")  
    global daily_confir_df
    global daily_deaths_df
    daily_confir_df = pd.DataFrame()
    daily_deaths_df = pd.DataFrame()
    daily_confir_df['date'] = cumul_confir_df.loc[:, 'date']
    daily_deaths_df['date'] = cumul_deaths_df.loc[:, 'date']
    for c in range(1, country_count+1):
        
        # ---- confirmed cases
        daily_confir_df[cumul_confir_df.columns[c]] = cumul_confir_df[cumul_confir_df.columns[c]].diff()
        cumul_confir_df[cumul_confir_df.columns[c]+' (7day)'] = round(cumul_confir_df[cumul_confir_df.columns[c]].rolling(7, center =True).sum()/7)
        daily_confir_df[cumul_confir_df.columns[c]+' (7day)'] = round(daily_confir_df[cumul_confir_df.columns[c]].rolling(7, center =True).sum()/7)        
        
        # ---- deaths
        daily_deaths_df[cumul_deaths_df.columns[c]] = cumul_deaths_df[cumul_deaths_df.columns[c]].diff()
        cumul_deaths_df[cumul_deaths_df.columns[c]+' (7day)'] = round(cumul_deaths_df[cumul_deaths_df.columns[c]].rolling(7, center =True).sum()/7)
        daily_deaths_df[cumul_deaths_df.columns[c]+' (7day)'] = round(daily_deaths_df[cumul_deaths_df.columns[c]].rolling(7, center =True).sum()/7)

    data_update_time = time.time()

# ---- get data when web app starts
download_data()

def home(request):

    # import IPython; IPython.embed(colors='Neutral')
    context = {}
    return render(request, 'corona/home.html', context)

def data(request):

    global data_update_time
    global selected_country_l

    global cumul_confir_df
    global cumul_deaths_df
    global daily_confir_df
    global daily_deaths_df
    
    # ---- get latest data if a day has elapsed
    if (data_update_time is None) or (time.time() - data_update_time > 86400):
        download_data()

    chart = {

        'title': {
            'text': 'COVID-19 confirmed cases (cumulative)'
        },

        'subtitle': {
            'text': 'Source: github.com/CSSEGISandData/COVID-19'
        },

        'yAxis': {
            'title': {
                'text': 'Number of cases'
            }
        },

        'xAxis': {
            'title': {
                'text': 'Date'
            },
            'type': 'datetime'
        },

        'legend': {
            'layout': 'vertical',
            'align': 'right',
            'verticalAlign': 'middle'
        },

        'plotOptions': {
            'series': {
                'cursor': 'pointer',
                'pointStart':  list(cumul_confir_df['date'])[0].timestamp()*1000,
                # 'pointStart':  int(list(cumul_confir_df['date'])[0].timestamp()),
                'pointInterval': 60 * 60 * 24 * 1000,
            }
        },

        'series': [{
            'name': 'United Kingdom',
            'data': list(cumul_confir_df['United Kingdom']),
        }, {
            'name': 'France',
            'data': list(cumul_confir_df['France']),
        }],

        'tooltip': {
            'shared': True,
            'crosshairs': True,
        },

        'responsive': {
            'rules': [{
                'condition': {
                    'maxWidth': 500
                },
                'chartOptions': {
                    'legend': {
                        'layout': 'horizontal',
                        'align': 'center',
                        'verticalAlign': 'bottom'
                    }
                }
            }]
        }

    }

    return JsonResponse(chart)
