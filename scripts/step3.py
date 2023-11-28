from datetime import datetime
import datetime as dt
from math import ceil
import pandas as pd
import numpy as np
import json
import geopandas as gpd
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import datapane as dp
from scripts.step2 import *
from scripts.definitions import *

def create_report(df_daily, df_pivot, watch, program, fields, start_string, col):
    '''
    Based on the daily and weekly flooding percentage results
    Generage a DataPane rerport including:
        - Current status
        - Historical status summary bar chart
        - Historical status heatmap 
        - Watch list
        - Status on map
    '''
    # Obtain program specific information from definitions
    aday = dt.datetime.now().date() - dt.timedelta(days = 6)
    start_last = (aday - dt.timedelta(days=aday.weekday()+1)).strftime('%Y-%m-%d')
    end_last = (aday + dt.timedelta(days=5 - aday.weekday())).strftime('%Y-%m-%d')
    season = field_bid_names[program][3]
    # Calculate the cloud free datepoints
    num, percent, percent2, mask, mask2 = cloud_free_percent(df_daily, start_last)
    # Step 3: add plots
    fig_history = history_plot(df_pivot, start_last, start_string)
    if percent < cloudy:
        fig_status = plot_cloudy_status(start_last, cloudy)
    else:
        fig_status = plot_status(df_pivot, start_last)
    heatmaps, cut_bins = all_heatmaps(df_pivot, col, start_last)
    search_plot = history_plot_by_id(df_daily, df_pivot)
    pct_map = map_plot(fields, df_pivot, program, start_last)
    # Step 4: upload to datapane
    start_last_text = datetime.strptime(start_last, '%Y-%m-%d').strftime("%b %d, %Y")
    end_last_text = datetime.strptime(end_last, '%Y-%m-%d').strftime("%b %d, %Y")
    last_update_text = datetime.strptime(end_string, '%Y-%m-%d').strftime("%b %d, %Y")
    program_name = field_bid_names[program][5] if not None else program
    page = dp.Page(
        title = program_name, 
        blocks = [
            dp.Text('# BirdSense #'),
            dp.Text(f'## Program - {program_name} ##'),
            dp.Text(f'## {season} ##'),
            dp.Text(f'### Weekly Report - {start_last_text} to {end_last_text} ###'),
            dp.Text(f'last update: {last_update_text}'),
            dp.Group(
                dp.BigNumber(heading='Total Fields', value=num),
                dp.BigNumber(heading='Fields with cloud-free data this week',
                value="{:.2%}".format(percent)
                #   change="{:.2%}".format(percent - percent2), is_upward_change=True), 
                    ), 
                columns=2
                ),  # check the upward = false
            dp.Text('## Flooding Status ##'),
            dp.Group(
                dp.Plot(
                    fig_status,
                    # Lots of white space here, so we can use a smaller height
                    responsive=True
                        ),
                dp.Plot(fig_history, responsive=True), 
                columns=2
                ),
            dp.Text(f'## Watch List for the week starting {start_last_text} ##'),
            dp.Text(f'* The Watch List only includes the fields in the contracted flooding period and with satellite data available this week.'),
            dp.Table(watch.style.background_gradient(cmap="autumn")),
            dp.Text('## Flooding Percentage by Fields ##'),
            dp.Select(
                blocks=[
                    dp.Plot(
                        heatmaps[i], 
                        label=f'Bids {int(cut_bins[i])} ~ {int(cut_bins[i+1])}') for i in range(len(heatmaps))
                        ] +
                        [dp.DataTable(df_pivot.round(3), label="Data Table")],
                        type=dp.SelectType.TABS
                        ),
            dp.Text('## Flooding Time Series Chart ##'),
            dp.Plot(search_plot),
            dp.Text('## Map of Flooding Status ##'),
            dp.Plot(pct_map)
            ]
                )
    return page


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
        colorbar=dict(title='Flooding %'),),
                    layout = go.Layout(
                        autosize=False, 
                        width=300,
                        height=800)
    )
    fig.update_layout(yaxis={"title": 'Weeks'},  # "tickangle": 45
                      xaxis={"title": 'Fields'})
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_visible=True)
    return fig


def all_heatmaps(df, col, start):
    '''
    split fields into n groups and create heatmaps
    '''
    n = len(df)//100 +1
    heatmaps = []
    df['Unique_ID'] = df['Bid_ID'].apply(lambda x: x.split('-')[-1]) + "-" + df['Field_ID']
    df['group'] = df['Bid_ID'].apply(lambda x: x.split('-')[-1]).astype('int')
    df['group'], cut_bin = pd.qcut(
        df['group'], q=n, labels=range(n), retbins=True)
    for i in range(n):
        sub_df = df[df.group == i]
        fig = heatmap_plot(sub_df, i, col, start)
        heatmaps.append(fig)
    df.drop(['Unique_ID', 'group'], axis=1, inplace=True)
    return heatmaps, cut_bin


def history_plot(df, start_last_week, start_string, max_bar=8, cloudy = 0.1):
    '''
    plot the last n weeks data with plotly
    '''
    
    columns = df.columns.tolist()
    # calculate the number of full weeks n
    start_last = dt.datetime.strptime(start_last_week, '%Y-%m-%d').date()
    start_program = dt.datetime.strptime(start_string, '%Y-%m-%d').date()
    diff = start_last - start_program
    n = min(ceil((diff.days + 6)/7), max_bar)
    last = [' ']
    
    # if the last week is not a full week, remove it
    if dt.datetime.strptime(columns[-1], '%Y-%m-%d').date() > start_last:
        columns = columns[:-1] 
    
    week_columns = columns[-n:].copy()
    # all_columns = columns.copy()
    no_columns = []
    
    # hide the weeks with high cloudy percentage
    for column in week_columns:
        if df[column].count() < len(df)*cloudy:
            week_columns.remove(column)
            no_columns.append(column)
    print(week_columns, n)        
    # calculate the percentage of minimal, partial and flooded for each week
    last_n_week = df[week_columns].applymap(
        lambda x: 1 if x > 0.66 else 0).sum()/df[week_columns].count()
    last_n_week_par = df[week_columns].applymap(
        lambda x: 1 if x > 0.33 and x <= 0.66 else 0).sum()/df[week_columns].count()
    last_n_week_non = df[week_columns].applymap(
        lambda x: 1 if x <= 0.33 else 0).sum()/df[week_columns].count()
    
    # plot the historical flooding status
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
                      width=600,
                      height=300,
                      margin=dict(
                            l=25,
                            r=25,
                            b=50,
                            t=75,
                            pad=4),
                      xaxis = dict(
                          title='Start of the Weeks',
                          tickmode = 'array',
                          tickvals = week_columns),
                      title = {'text': 'Flooding Status for Last 8 Weeks (Cloud-Free Fields Only)',
                              'x': 0.5,'y': 0.9,
                              'xanchor': 'center',
                             'font': {'size': 16}},
                        annotations=[
                            dict(
                                x=week_columns[0],
                                xanchor='left',
                                y=1.2,
                                text="* Weeks with satellite data availability less than {:.0%} are excluded".format(cloudy),
                                showarrow=False
                                 )
                                     ]
                     )

    all_columns = week_columns + last

    fig.update_yaxes(showticklabels=False, range=[0, 1.3])
    fig.update_xaxes(range = [all_columns[0], all_columns[-1]])
    return fig

def plot_status(df, start):
    '''
    classify the flooding percentage to 3 catergories, 
    creat indicators of the percentage of minimal, partially, and fully flooded.
    and compare with last week
    '''
    start_last = dt.datetime.strptime(start, '%Y-%m-%d').date()
    start_text = start_last.strftime("%b %d, %Y")
    start_last2 = (start_last - dt.timedelta(days=7)).strftime('%Y-%m-%d')
    bin_labels = ['Minimally Flooded', 'Partially Flooded', 'Flooded']
    # cnt = df.count()
    level = pd.cut(df[start],
                   bins=[-1, .33, .66, 1],
                   labels=bin_labels)
    freq = level.value_counts()/level.count()
    print(freq)
    level_y = pd.cut(df[start_last2],
                     bins=[-1, .33, .66, 1],
                     labels=bin_labels)
    
    freq_y = level_y.value_counts()/level_y.count()
    #sort by index
    freq.sort_index(ascending=True, inplace = True)
    freq_y.sort_index(ascending=True, inplace = True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=freq.values[2]*100,
        number={'suffix': '%', "font": {"size": 50}, "valueformat": ".0f"},
        title={"text": "Flooded<br>(66%-100%)"},
        delta={'reference': freq_y.values[2]*100,
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
        value=freq.values[0]*100,
        number={'suffix': '%', "font": {"size": 50}, "valueformat": ".0f"},
        title={"text": "Minimally<br>Flooded<br>(0-33%)"},
        delta={'reference': freq_y.values[0]*100,
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
        title = {'text': f'Flooding Status for the Week of {start_text} (Cloud-Free Fields Only)',
                              'x': 0.5,'y': 0.9,
                              'xanchor': 'center',
                             'font': {'size': 16}}
    )
    return fig


def plot_cloudy_status(start, cloudy = 0.15):
    '''
    if the cloud free fields percentage is below the threshold, hide the status plot
    '''
    start_text = dt.datetime.strptime(start, '%Y-%m-%d').strftime("%b %d, %Y")
    fig = go.Figure()
    fig.add_annotation(text = "* Status is not shown if the satellite data availability is less than {:.0%}.".format(cloudy),
                    #    align ='left',
                       showarrow = False,
                       xref="paper",
                       yref="paper",
                       font=dict(size=14),
                       x = 0.05,
                       y = 1,
                       )
    fig.update_layout(
        height=400,
        autosize=True,
        font=dict(size=20),
        plot_bgcolor="rgba(0,0,0,0)",
        title = {'text': f'Flooding Status for the Week of {start_text} (Cloud-Free Fields Only)',
                              'x': 0.5,'y': 0.9,
                              'xanchor': 'center',
                             'font': {'size': 16}}
    )
    fig.update_xaxes(visible=False)  
    fig.update_yaxes(visible=False)
    return fig


def map_plot(fields, df, program, start):
    '''
    this function take the geometry information from fieds,
    the flooding percentage results from last week,
    and plot a map
    '''
    start_text = dt.datetime.strptime(start, '%Y-%m-%d').strftime("%b %d, %Y")
    # obtain geometry information and convert to dataframe
    df_geo = gpd.read_file(json.dumps(fields.getInfo()))
    
    # Change name to satanderd name
    df_geo = standardize_names(df_geo, 'Bid_ID', field_bid_names[program][0])
    df_geo = standardize_names(df_geo, 'Field_ID', field_bid_names[program][1])
    # Join the flooding percentage results to the geo dataframe
    merged_df = pd.merge(df_geo, df, 
                         left_on=['Bid_ID','Field_ID'], 
                         right_on= list(df.columns[:2]))
    merged_df['Flooding %'] = merged_df[start].round(3)*100
    merged_df['week'] = f'Week starting on {start}'
    
    # Look for the center and zoom of the map presentation
    box_boundary = merged_df['geometry'].bounds
    lon_min = box_boundary['minx'].min()
    lon_max = box_boundary['maxx'].max()
    lat_min = box_boundary['miny'].min()
    lat_max = box_boundary['maxy'].max()
    center = dict(lat = (lat_min + lat_max) / 2, lon = (lon_min + lon_max) / 2)
    max_bound = max(abs(lon_min-lon_max), abs(lat_min-lat_max)) * 111
    zoom = 12.8 - np.log(max_bound)
    
    # Check if the input dataframe include flooding start and end tats
    if 'Flood_start' in merged_df.columns:
        columns = ['Bid_ID', 'Field_ID', 'Flood Start', 'Flood End']
        hover='Bid_ID: %{customdata[0]}<br>' + \
            'Field_ID: %{customdata[1]}<br>' + \
            'Flood Start: %{customdata[2]}<br>' + \
            'Flood End: %{customdata[3]}<br>'
    else:
        columns = ['Bid_ID', 'Field_ID']
        hover='Bid_ID: %{customdata[0]}<br>' + 'Field_ID: %{customdata[1]}<br>' 
    
    # Map plot
    fig = px.choropleth_mapbox(
        data_frame = merged_df,            # Data frame with values
        geojson = fields.getInfo(),                      # Geojson with geometries
        locations = 'id', 
        # featureidkey="id",
        hover_name = 'week', 
        hover_data = columns,
        color = 'Flooding %',            # Name of the column of the data frame with the data to be represented
        mapbox_style = 'open-street-map',
        color_continuous_scale = 'RdBu',
        opacity = 0.7,
        center = center,
        zoom = zoom
    )
    # Add the fieds without data to the map
    no_data_fields = go.Choroplethmapbox(
        geojson=fields.getInfo(),
        locations=merged_df[merged_df['Flooding %'].isna()]['id'],
        marker_line_width=1,
        marker_line_color='gray',
        z=[0] * len(merged_df[merged_df['Flooding %'].isna()]['id']),
        showscale=False,
        customdata=merged_df[columns],
        hovertemplate=hover
    )
    fig.add_trace(no_data_fields)
    fig.update_layout(
        height=800, 
        width = 1000, 
        autosize = True,
        title = {'text': f'Flooding Status for the week starting on {start_text}',
                 'x': 0.5,'y': 0.95,
                 'xanchor': 'center',
                 'font': {'size': 16}
                 }
    )
    return fig


def history_plot_by_id(df_daily, df_weekly):
    '''
    This function takes the daily flooding status table
    return a interactive plot with filter function by bid_id
    '''
    # data preparation
    df_daily_clean = df_daily.groupby(['Unique_ID', 'Date'])\
                            .agg({'pct_flood': 'mean', 'Field_ID' : 'first'}).reset_index()
    df_daily_clean = df_daily_clean.dropna()
    # create Unique_ID for table merge and formate the flood start/end dates to datetime type
    df_weekly['Unique_ID'] = df_weekly['Bid_ID'] + '_' + df_weekly['Field_ID']
    df_weekly['Flood Start'] = pd.to_datetime(df_weekly['Flood Start'])
    df_weekly['Flood End'] = pd.to_datetime(df_weekly['Flood End'])
    # merge the flood start and end dates from weekly table to daily table
    df_daily_clean = pd.merge(df_daily_clean, 
                              df_weekly[['Unique_ID', 'Flood Start', 'Flood End']], 
                              on = ['Unique_ID'], how = 'left')
    df_daily_clean['FieldID_date'] = df_daily_clean['Field_ID'] + ': ' \
                                + df_daily_clean['Flood Start'].apply(lambda x : x.strftime("%b %d")) + ' to ' \
                                + df_daily_clean['Flood End'].apply(lambda x : x.strftime("%b %d, %Y"))
    
    bid_ids = sorted(df_daily.dropna()['Bid_ID'].unique())
    unique_ids = df_daily_clean['Unique_ID'].unique()
    # build a menu for each Bid_ID
    # add a choice of all the fields   
    menus = [dict(
        label = "All",
        method = "update",
        args = [{"visible": [True] * len(unique_ids) + [False] * len(unique_ids)},
               {"title": "Flooding status history for all fields"}
                ])]

    # add one choice for each Bid_ID
    for bid_id in bid_ids:
        visibility = [True if bid_id in unique_id else False for unique_id in unique_ids] \
                    + [True if bid_id == select_id else False for select_id in bid_ids]
        # print(visibility)
        menus.append(dict(
            label = bid_id,
            method = "update",
            args = [{"visible": visibility},
                    {"title": f"Flooding time series for {bid_id}"}
                   ]))
        
    # Initialize figure
    fig = go.Figure()
    
    # Add Trace for each unique id
    for unique_id in unique_ids:
        # filter data for the selected unique_id
        df_select = df_daily_clean[df_daily_clean['Unique_ID'] == unique_id]
        
        fig.add_trace(
            go.Scatter(x = df_select.Date,
                       y = df_select['pct_flood']*100,
                       name = min(df_select.FieldID_date),
                       # mode = 'lines'
                  ))
    
    # Add shaded area indicating flooding period for each bid_id
    for bid_id in bid_ids:
        df_select = df_weekly[df_weekly['Bid_ID'] == bid_id].reset_index()
        start = min(df_select['Flood Start'])
        end = max(df_select['Flood End'])
        fig.add_trace(
            go.Scatter(x = [start, 
                            end], 
                       y = [100, 100],
                       mode='lines',                # 'lines' mode to connect the points
                       fill='tozeroy',              # 'tozeroy' fills below the curve
                       fillcolor='rgba(0, 0, 255, 0.2)',  # Color and opacity of the shaded area
                       name='Contracted Flooding Period',
                       line_width = 0,
                       visible = False,
                       )
        )
        
    # add dropdown menus and format the plot layout
    fig.update_layout(
        updatemenus = [
            dict(
                type = "dropdown",
                direction = "down",
                
                buttons = menus,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=-0.3,
                xanchor="left",
                y=1,
                yanchor="top"
            )],
        annotations=[
        dict(text="Select a Bid ID:", showarrow=False,
        x= -0.3, y=1.1, xref="paper", yref="paper", align="left")
        ],
        yaxis={"title": 'Flooding %'},
        plot_bgcolor='white',
        showlegend = True,
    )

    # format plot
    fig.update_yaxes(range=[-5, 101],
                     gridcolor='lightgrey')
    fig.update_xaxes(range=[min(df_daily.Date), dt.datetime.now().date()],
                     )
    return fig