import pandas as pd
from datetime import datetime
import datetime as dt
from step2 import *
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
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

# def plot_2(df):
#     labels = df.columns[-5:]
#     last_5_week = df[df.columns[-5:]].applymap(lambda x : 1 if x >0.66 else 0).sum()/len(df)
#     fig, ax = plt.subplots(figsize = (6,1.2) )
#     ax.bar(range(5), last_5_week,  alpha = 0.8, width = 0.8)
#     for index, value in enumerate(last_5_week):
#         plt.text(index-0.3, value+0.1, "{:.2%}".format(value))
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['left'].set_visible(False)
#     ax.set_xticks(range(5))
#     ax.set_xticklabels(labels, fontsize='small')
#     # plt.tick_params(left = False)
#     plt.yticks([])
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

# def plot_3(df):
#     bin_labels = ['Minimally Flooded', 'Partially Flooded', 'Flooded']
#     level = pd.cut(df[df.columns[-1]],
#                               bins=[0, .33, .66, 1],
#                               labels=bin_labels)
#     freq = level.value_counts()/level.count()

#     level_y = pd.cut(df[df.columns[-2]],
#                               bins=[0, .33, .66, 1],
#                               labels=bin_labels)

#     freq_y = level_y.value_counts()/level_y.count()
#     fig = go.Figure()
#     fig.add_trace(go.Indicator(
#         mode = "number+delta",
#         value = freq.values[0]*100,
#         number = {'suffix' : '%'},
#         title = {"text": "Flooded"},
#         delta = {'reference': freq_y.values[0]*100, 'relative': False, "valueformat": ".2f"},
#         domain = {'x': [0, 0.33], 'y': [0, 1]}))


#     fig.add_trace(go.Indicator(
#         mode = "number+delta",
#         value = freq.values[1]*100,
#         number = {'suffix' : '%'},
#         title = {"text": "Partially Flooded"},
#         delta = {'reference': freq_y.values[1]*100, 'relative': False, "valueformat": ".2f"},
#         domain = {'x': [0.34, 0.66], 'y': [0, 1]}))


#     fig.add_trace(go.Indicator(
#         mode = "number+delta",
#         value = freq.values[2]*100,
#         number = {'suffix' : '%'},
#         title = {"text": "Minimally Flooded"},
#         delta = {'reference': freq_y.values[2]*100, 'relative': False, "valueformat": ".2f"},
#         domain = {'x': [0.67, 1], 'y': [0, 1]}))

#     # Layout
#     fig.update_layout(
#         grid={
#             'rows': 1,
#             'columns': 3,
#             'pattern': "independent"
#         },
#     )

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
        lambda x: 1 if x >= 0 else 0).sum()/len(df)
    last_n_week = df[columns].applymap(
        lambda x: 1 if x > 0.66 else 0).sum()/len(df)
    last_n_week_par = df[columns].applymap(
        lambda x: 1 if x > 0.33 and x <= 0.66 else 0).sum()/len(df)
    last_n_week_non = df[columns].applymap(
        lambda x: 1 if x <= 0.33 else 0).sum()/len(df)

    fig = go.Figure(data=[
        go.Bar(name='Flooded', x=last_n_week.index,
               y=last_n_week, marker_color='blue'),
        go.Bar(name='Partially Flooded', x=last_n_week.index,
               y=last_n_week_par, marker_color='orange'),
        go.Bar(name='Minimally Flooded',
               x=last_n_week.index, y=last_n_week_non,
               marker_color='red',
               text=last_n_week_all,
               texttemplate='%{text:.1%}',
               textposition='outside')])
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
                      height=400,)
    fig.update_yaxes(showticklabels=False, range=[0, 1.2])
    return fig

# def plot_2(df):

#     labels = df.columns[-5:]
#     last_5_week = df[df.columns[-5:]].applymap(lambda x : 1 if x >0.66 else 0).sum()/len(df)


#     fig, ax = plt.subplots(figsize = (6,1.2) )
#     ax.bar(range(5), last_5_week,  alpha = 0.8, width = 0.8)

#     for index, value in enumerate(last_5_week):
#         plt.text(index-0.3, value+0.1, "{:.2%}".format(value))
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['left'].set_visible(False)
#     ax.set_xticks(range(5))
#     ax.set_xticklabels(labels, fontsize='small')
#     # plt.tick_params(left = False)
#     plt.yticks([])
#     return fig


# def plot_3(df):

#     labels = df.columns[-5:]

#     last_5_week_par = df[df.columns[-5:]].applymap(lambda x : 1 if x >0.33 and x <= 0.66 else 0).sum()/len(df)


#     fig, ax = plt.subplots(figsize = (6,1.2) )
#     ax.bar(range(5), last_5_week_par,  alpha = 0.8, width = 0.8,color='orange')

#     for index, value in enumerate(last_5_week_par):
#         plt.text(index-0.3, value+0.005, "{:.2%}".format(value))
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['left'].set_visible(False)
#     ax.set_xticks(range(5))
#     ax.set_xticklabels(labels, fontsize='small')
#     # plt.tick_params(left = False)
#     plt.yticks([])
#     return fig

# def plot_4(df):

#     labels = df.columns[-5:]

#     last_5_week_non = df[df.columns[-5:]].applymap(lambda x : 1 if x <=0.33 else 0).sum()/len(df)


#     fig, ax = plt.subplots(figsize = (6,1.2) )
#     ax.bar(range(5), last_5_week_non,  alpha = 0.8, width = 0.8,color='red')

#     for index, value in enumerate(last_5_week_non):
#         plt.text(index-0.3, value+0.001, "{:.2%}".format(value))
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['left'].set_visible(False)
#     ax.set_xticks(range(5))
#     ax.set_xticklabels(labels, fontsize='small')
#     # plt.tick_params(left = False)
#     plt.yticks([])
#     return fig

def plot_status(df, start, df_pct):
    num, percent, percent2, mask, mask2 = cloud_free_percent(df_pct, start)
    start_last = dt.datetime.strptime(start, '%Y-%m-%d').date()
    start_last2 = (start_last - dt.timedelta(days=7)).strftime('%Y-%m-%d')
    bin_labels = ['Minimally Flooded', 'Partially Flooded', 'Flooded']

    level = pd.cut(df[start],
                   bins=[0, .33, .66, 1],
                   labels=bin_labels)
    freq = level.value_counts()/len(level) * mask

    level_y = pd.cut(df[start_last2],
                     bins=[0, .33, .66, 1],
                     labels=bin_labels)

    freq_y = level_y.value_counts()/len(level_y) * mask2
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
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )

    # # Layout
    # fig.update_layout(
    #     width=600,
    #     height=400,
    #     autosize=False,
    #     grid={
    #         'rows': 1,
    #         'columns': 3,
    #         'pattern': "coupled"
    #     },
    # )

    return fig
