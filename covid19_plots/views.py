from django.shortcuts import render, HttpResponse

# Create your views here.

# LOG.info("imports ...")
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
import time

data_update_time = None

cumul_confir_df = None
cumul_deaths_df = None
daily_confir_df = None
daily_deaths_df = None

selected_country_l = None

def get_data():

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
get_data()

DEFAULT_PLOTLY_COLORS=['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                       'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                       'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                       'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                       'rgb(188, 189, 34)', 'rgb(23, 190, 207)']

def index(request):

    global data_update_time
    global selected_country_l
    
    # ---- get latest data if a day has elapsed
    if (data_update_time is None) or (time.time() - data_update_time > 86400):
        get_data()

    # ------------------
    # DISPLAY PLOTS
    # ------------------
    # LOG.info("plot ...")    

    # ---- parameters
    # selected_country_l = ['France', 'United Kingdom', 'Germany', 'Italy', 'Spain', 'Turkey', 'Israel', 'US', 'Brazil', 'India', 'Russia']
    if request.method == "POST":
        # import IPython; IPython.embed(colors='Neutral')
        selected_country_l = request.POST.getlist('selected_country_l')
    else:
        if selected_country_l is None:
            selected_country_l = ['France', 'United Kingdom']

    if selected_country_l is None:
        raise Exception("selected_country_l is None")   

    # import IPython; IPython.embed(colors='Neutral')
    # selected_country_l = ['US', 'Brazil', 'India', 'Russia']

    # to_plot_df, txt = cumul_confir_df, 'cumul confirmed'
    # to_plot_df, txt = daily_confir_df, 'daily confirmed'
    # to_plot_df, txt = cumul_deaths_df, 'cumul deaths'
    # to_plot_df, txt = daily_deaths_df, 'daily deaths'

    fig_html_jhu_nc = None
    fig_html_jhu_nd = None
    fig_html_owid_nc = None
    fig_html_owid_nd = None

    l = [ 
        # [cumul_confir_df, 'cumul confirmed', 'fig_html_jhu_nc'],
        # [daily_confir_df, 'daily confirmed', 'fig_html_jhu_nd'],
        [cumul_confir_df, 'cumul confirmed', 1, 1],
        [daily_confir_df, 'daily confirmed', 2, 1],
    #     [cumul_deaths_df, 'cumul deaths', 'fig_html_owid_nc'],
    #     [daily_deaths_df, 'daily deaths', 'fig_html_owid_nd'],
    ]

    context = {}

    # ---- create figure
    fig = go.Figure()

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["COVID-19: "+txt for to_plot_df, txt, row, col in l],
        vertical_spacing = 0.13,
        shared_xaxes=True,
    )
    
    for to_plot_df, txt, row, col in l:
        
        color_index = 0
   
        # ---- prepare plots
        for country_name in selected_country_l:
            
            confir_color = DEFAULT_PLOTLY_COLORS[(2*color_index)%len(DEFAULT_PLOTLY_COLORS)]
            death_color = DEFAULT_PLOTLY_COLORS[(2*color_index+1)%len(DEFAULT_PLOTLY_COLORS)]

           # ---- unfiltered
            fig.add_trace(
                go.Scatter(
                    x = to_plot_df['date'],
                    y = to_plot_df[country_name],
                    mode = 'markers',
                    name = country_name,
                    visible = 'legendonly',
                    marker_color = confir_color,
                ),
                row = row,
                col = col,
            )
          
            # ---- filtered
            fig.add_trace(
                go.Scatter(
                    x = to_plot_df['date'],
                    y = to_plot_df[country_name+' (7day)'],
                    mode = 'lines',
                    name = country_name+' (7d)',
                    line_color = death_color,
                ),
                row = row,
                col = col,
            )
            
            color_index += 1

        # ---- time slider
        fig.update_layout(
            # title = "COVID-19: "+txt,
            xaxis=dict(
                type="date"
            ),
            legend = dict(
                # x=0.01,
                # y=0.99,
                orientation = "h",
            ),
            font=dict(
                size=8,
                color="black"
            ),
            margin = dict(
                l = 20,
                r = 10,
                b = 10,
                t = 50,
                pad = 2,
            ),
        )

        fig.update_yaxes(automargin=True)

    # ---- show !
    # fig.show()

    country_l = sorted([c for c in cumul_confir_df.columns if ('(7day)' not in c) and c != 'date'])
    
    context = {
        'fig_html': fig.to_html(include_plotlyjs = False, full_html = False, default_height = '100%'),
        'country_l': country_l,
        'selected_country_l': selected_country_l,
    }

    return render(request, 'covid19_plots/index.html', context)

def edit(request):

    # import IPython; IPython.embed(colors='Neutral')

    global selected_country_l

    context = {
    }
    return render(request, 'covid19_plots/edit.html', context)  