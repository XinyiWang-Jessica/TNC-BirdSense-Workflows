import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def plot_1(df):
    bin_labels = ['Minimally Flooded', 'Partially Flooded', 'Flooded']
    minor = ['(<= 33%)', 'Minimally Flooded', '(33%~66%)','Partially Flooded', '(>66%)', 'Flooded']
    level = pd.cut(df[df.columns[-1]],
                              bins=[0, .33, .66, 1],
                              labels=bin_labels)
    freq = level.value_counts()/level.count()
    fig, ax = plt.subplots(figsize = (2,1.2) ) 
    ax.barh([0, 1, 2], freq[::-1], color = ['red', 'orange', 'blue'], alpha = 0.5, height = 0.8)
    for index, value in enumerate(freq[::-1]):
        plt.text(value, index-0.2, "{:.2%}".format(value))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([-0.2, 0.3, 0.8, 1.3, 1.8, 2.3])
    # ax.set_yticks([0.5, 1.5, 2.5], minor=True )
    ax.set_yticklabels(minor, fontsize='small')
    plt.tick_params(left = False)
    plt.xticks([])
    return fig

def plot_2(df):
    labels = df.columns[-5:]
    last_5_week = df[df.columns[-5:]].applymap(lambda x : 1 if x >0.66 else 0).sum()/len(df)
    fig, ax = plt.subplots(figsize = (6,1.2) ) 
    ax.bar(range(5), last_5_week,  alpha = 0.8, width = 0.8)
    for index, value in enumerate(last_5_week):
        plt.text(index-0.3, value+0.1, "{:.2%}".format(value))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticks(range(5))
    ax.set_xticklabels(labels, fontsize='small')
    # plt.tick_params(left = False)
    plt.yticks([])
    return fig

def heatmap_plot(df, n):
    fig = go.Figure(data=go.Heatmap(
        z=df.iloc[n*100:(n+1)*100,3:-1].T.round(3),
        x=df.Unique_ID[n*100:(n+1)*100],
        y=df.iloc[:,3:-1].columns,
        colorscale='RdBu'))
    fig.update_layout(xaxis_visible=False)  
    return fig      

def all_heatmaps(df):
    heatmaps = []
    df['Unique_ID'] = df['Bid_ID'] + "-" + df['Field_ID']
    for i in range(round(len(df)/100)):
        fig = heatmap_plot(df, i)
        heatmaps.append(fig)
    df.drop(['Unique_ID'], axis=1, inplace=True)
    return heatmaps


def plot_3(df):
    bin_labels = ['Minimally Flooded', 'Partially Flooded', 'Flooded']
    level = pd.cut(df[df.columns[-1]],
                              bins=[0, .33, .66, 1],
                              labels=bin_labels)
    freq = level.value_counts()/level.count()
    
    level_y = pd.cut(df[df.columns[-2]],
                              bins=[0, .33, .66, 1],
                              labels=bin_labels)

    freq_y = level_y.value_counts()/level_y.count()
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = freq.values[0]*100,
        number = {'suffix' : '%'},
        title = {"text": "Flooded"},
        delta = {'reference': freq_y.values[0]*100, 'relative': False, "valueformat": ".2f"},
        domain = {'x': [0, 0.33], 'y': [0, 1]}))


    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = freq.values[1]*100,
        number = {'suffix' : '%'},
        title = {"text": "Partially Flooded"},
        delta = {'reference': freq_y.values[1]*100, 'relative': False, "valueformat": ".2f"},
        domain = {'x': [0.34, 0.66], 'y': [0, 1]}))


    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = freq.values[2]*100,
        number = {'suffix' : '%'},
        title = {"text": "Minimally Flooded"},
        delta = {'reference': freq_y.values[2]*100, 'relative': False, "valueformat": ".2f"},
        domain = {'x': [0.67, 1], 'y': [0, 1]}))
    
    # Layout
    fig.update_layout(
        grid={
            'rows': 1,
            'columns': 3,
            'pattern': "independent"
        },
    )
    
    return fig
