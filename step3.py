import pandas as pd
from datetime import datetime
import datetime as dt
from step2 import *
import json
import geopandas as gpd
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from definitions import *

# def plot_1(df):
#     bin_labels = ['Minimally Flooded', 'Partially Flooded', 'Flooded']
#     minor = ['(<= 33%)', 'Minimally Flooded', '(33%~66%)','Partially Flooded', '(>66%)', 'Flooded']
#     level = pd.cut(df[df.columns[-1]],
#                               bins=[0, .33, .66, 1],
#                               labels=bin_labels)
#     freq = level.value_counts()/level.count()
#     fig, ax = plt.subplots(figsize = (2,1.2) )
#     ax.barh([0, 1, 2], freq[::-1], color = ['red', 'orange', 'blue'], alpha = 0.5, height = 0.8)
#     for index, value in enumerate(freq[::-1]):
#         plt.text(value, index-0.2, "{:.2%}".format(value))
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['bottom'].set_visible(False)
#     ax.spines['left'].set_visible(False)
#     ax.set_yticks([-0.2, 0.3, 0.8, 1.3, 1.8, 2.3])
#     # ax.set_yticks([0.5, 1.5, 2.5], minor=True )
#     ax.set_yticklabels(minor, fontsize='small')
#     plt.tick_params(left = False)
#     plt.xticks([])
#     return fig

def heatmap_plot(df, n, col, start):
    '''
    heatmap of percentage flooded,
    x is unique field id
    y is week starts days
    '''
    columns = df.iloc[:, col:].columns.tolist()[:-2]
    start_last = dt.datetime.strptime(start, '%Y-%m-%d').date()
    if dt.datetime.strptime(columns[-1], '%Y-%m-%d').date() > start_last:
        columns = columns[:-1]
    fig = go.Figure(data=go.Heatmap(
        z=df.loc[:, columns].T.round(3)*100,
        x=df.Unique_ID,
        y=columns,
        colorscale='RdBu',
        colorbar=dict(title='Flooding %'),)
    )
    fig.update_layout(yaxis={"title": 'Weeks'},  # "tickangle": 45
                      xaxis={"title": 'Fields'})
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_visible=False)
    return fig


def all_heatmaps(df, col, start):
    '''
    split fields into 5 groups and create heatmaps
    '''
    heatmaps = []
    df['Unique_ID'] = df['Bid_ID'] + "-" + df['Field_ID']
    df['group'] = df['Bid_ID'].apply(lambda x: x.split('-')[-1]).astype('int')
    df['group'], cut_bin = pd.qcut(
        df['group'], q=5, labels=range(5), retbins=True)
    for i in range(5):
        sub_df = df[df.group == i]
        fig = heatmap_plot(sub_df, i, col, start)
        heatmaps.append(fig)
    df.drop(['Unique_ID', 'group'], axis=1, inplace=True)
    return heatmaps, cut_bin


def history_plot(df, start, n=8):
    '''
    plot the last n weeks data with plotly
    '''
    columns = df.columns
    start_last = dt.datetime.strptime(start, '%Y-%m-%d').date()
    if dt.datetime.strptime(columns[-1], '%Y-%m-%d').date() > start_last:
        columns = columns[:-1]
    columns = columns[-n:]
    last_n_week_all = df[columns].applymap(
        lambda x: 1 if x >= 0 else 0).sum()/df[columns].count()
    last_n_week = df[columns].applymap(
        lambda x: 1 if x > 0.66 else 0).sum()/df[columns].count()
    last_n_week_par = df[columns].applymap(
        lambda x: 1 if x > 0.33 and x <= 0.66 else 0).sum()/df[columns].count()
    last_n_week_non = df[columns].applymap(
        lambda x: 1 if x <= 0.33 else 0).sum()/df[columns].count()

    fig = go.Figure(data=[
        go.Bar(name='Flooded', x=last_n_week.index,
               y=last_n_week.round(3), marker_color='#063970',
               text=last_n_week.round(3),
               texttemplate='%{text:.0%}',
               textposition="inside",
               textfont=dict(color='#eeeee4')),
        go.Bar(name='Partially Flooded', x=last_n_week.index,
               y=last_n_week_par.round(3), marker_color='#98aab9',
               text=last_n_week_par.round(3),
               texttemplate='%{text:.0%}',
               textposition="inside",
               textfont=dict(color='#515151')),
        go.Bar(name='Minimally Flooded',
               x=last_n_week.index, y=last_n_week_non.round(3),
               marker_color='#CE1212',
               text=last_n_week_non.round(3),
               texttemplate='%{text:.0%}',
               textposition='inside',
               textfont=dict(color='white'))])
    # Change the bar mode
    fig.update_layout(barmode='stack',
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=1.02,
                          xanchor="right",
                          x=1),
                      autosize=False,
                      width=800,
                      height=400,
                      title = {'text': 'Flooding Status for Last 8 Weeks (Cloud-Free Fields Only)',
                              'x': 0.5,'y': 0.9,
                              'xanchor': 'center',
                             'font': {'size': 16}}
                     )
    fig.update_yaxes(showticklabels=False, range=[0, 1.2])
    return fig


def plot_status(df, start):
    start_last = dt.datetime.strptime(start, '%Y-%m-%d').date()
    start_last2 = (start_last - dt.timedelta(days=7)).strftime('%Y-%m-%d')
    bin_labels = ['Minimally Flooded', 'Partially Flooded', 'Flooded']
    cnt = df.count()
    level = pd.cut(df[start],
                   bins=[-1, .33, .66, 1],
                   labels=bin_labels)
    freq = level.value_counts()/level.count()

    level_y = pd.cut(df[start_last2],
                     bins=[-1, .33, .66, 1],
                     labels=bin_labels)

    freq_y = level_y.value_counts()/level_y.count()
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=freq.values[0]*100,
        number={'suffix': '%', "font": {"size": 50}, "valueformat": ".0f"},
        title={"text": "Flooded<br>(66%-100%)"},
        delta={'reference': freq_y.values[0]*100,
               'relative': False, "valueformat": ".1f"},
        domain={'x': [0, 0.33], 'y': [0, 1]}))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=freq.values[1]*100,
        number={'suffix': '%', "font": {"size": 50}, "valueformat": ".0f"},
        title={"text": "Partially<br>Flooded<br>(33%-66%)"},
        delta={'reference': freq_y.values[1]*100,
               'relative': False, "valueformat": ".1f"},
        domain={'x': [0.34, 0.66], 'y': [0, 1]}))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=freq.values[2]*100,
        number={'suffix': '%', "font": {"size": 50}, "valueformat": ".0f"},
        title={"text": "Minimally<br>Flooded<br>(0-33%)"},
        delta={'reference': freq_y.values[2]*100,
               'relative': False, "valueformat": ".1f"},
        domain={'x': [0.67, 1], 'y': [0, 1]}))

    # Lots of white space here- can you remove some?
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        autosize=True,
        font=dict(
            size=20
        ),
        title = {'text': f'Flooding Status for the Week of {start} (Cloud-Free Fields Only)',
                              'x': 0.5,'y': 0.9,
                              'xanchor': 'center',
                             'font': {'size': 16}}
    )
    return fig

def map_plot(fields, df, start):
    '''
    this function take the geometry information from fieds,
    the flooding percentage results from last week,
    and plot a map
    '''
    # obtain geometry information and convert to dataframe
    df_geo = gpd.read_file(json.dumps(fields.getInfo()))
    # join the flooding percentage results to the geo dataframe
    merged_df = pd.merge(df_geo, df, 
                         left_on=['BidID','FieldID'], 
                         right_on= list(df.columns[:2]))
    merged_df['Flooding %'] = merged_df[start].round(3)*100
    merged_df['unique_id'] = merged_df['Bid_ID']+merged_df['Field_ID'] 
    merged_df.set_index('unique_id', inplace = True)
    merged_df['timeframe'] = 'Flooding from ' + merged_df['Flood_Start'] + ' to ' +merged_df['Flood_End']
    fig = px.choropleth_mapbox(
        merged_df,            # Data frame with values
        geojson = merged_df.geometry,                      # Geojson with geometries
        locations = merged_df.index,           
        hover_name = 'timeframe', 
        color = 'Flooding %',                # Name of the column of the data frame with the data to be represented
        mapbox_style = 'stamen-terrain',
        color_continuous_scale = 'RdBu',
        opacity = 0.7,
        center = dict(lat = 39.141, lon = -121.63),
        zoom = 8)
    fig.update_layout(height=800, width = 1000, 
                  autosize = True,
                  title = {'text': f'Flooding Status on Map for the week of {start}',
                              'x': 0.5,'y': 0.95,
                              'xanchor': 'center',
                             'font': {'size': 16}})
    return fig

