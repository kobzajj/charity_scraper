import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
import chart_studio.plotly as py
from plotly.offline import plot
import plotly.express as px
from scipy import stats


# key operations in this file:
#     distribution of charities by location (maybe show a map visual) (done - maybe can zoom into counties)
#     distribution by location by category (11 categories - maybe can show a map with most frequent category by state) (need to figure this out)
#     distribution of categories and within it distribution by rating (done)
#     average score by state on a map (done) - maybe change this to rating?
#     distribution of revenue, cost, net assets, etc. (done - need to remove outliers)
#     relationship between score and revenue, cost, net assets, etc. - also with key financial indicators (done)
#     relationship between score and number of items on 990 / website
#     relationship between compensation of executives and overall financial standing (need to re-scrape to get comp info)
#     typical distribution of the expenses and revenue into categories
#     statistical significance of different states or categories that have higher average ratings

def create_state_map(df, field_name, title, statistic, color_scheme, by_pop=False):
    state_pop = {'CA': 39.6, 'TX': 29.7, 'FL': 21.2, 'NY': 19.5, 'PA': 12.8, 'IL': 12.7, 'OH': 11.7, 'GA': 10.5, 'NC': 10.3, 'MI': 10.0,
                 'NJ': 8.9, 'VA': 8.5, 'WA': 7.5, 'AZ': 7.2, 'MA': 6.9, 'TN': 6.8, 'IN': 6.7, 'MO': 6.1, 'MD': 6.0, 'WI': 5.8,
                 'CO': 5.7, 'MN': 5.6, 'SC': 5.1, 'AL': 4.9, 'LA': 4.7, 'KY': 4.5, 'OR': 4.2, 'OK': 3.9, 'CT': 3.6, 'PR': 3.2,
                 'UT': 3.2, 'IA': 3.2, 'NV': 3.0, 'AR': 3.0, 'MS': 3.0, 'KS': 2.9, 'NM': 2.1, 'NE': 1.9, 'WV': 1.8, 'ID': 1.8,
                 'HI': 1.4, 'NH': 1.4, 'ME': 1.3, 'MT': 1.1, 'RI': 1.1, 'DE': 1.0, 'SD': 0.9, 'ND': 0.8, 'AK': 0.7, 'DC': 0.7,
                 'VT': 0.6, 'WY': 0.6, 'VI': 0.1}

    py.sign_in('kobzajj', 'pBtRNtdf8xHNSz5l9KmB')

    # the territories are not on the mape so take them out (DC is also an outlier with 600+ charities per million)
    df = df[(df.location_state != 'PR') & (df.location_state != 'VI') & (df.location_state != 'DC')]

    df_group = df[df['location_state'].isnull() == False]
    group_functions = {field_name: [statistic]}
    df_group = df_group.groupby('location_state')
    analysis = df_group.agg(group_functions)
    if by_pop:
        statistic_pop_ratio = analysis[field_name][statistic] / list(map(lambda x: state_pop[x], df_group.groups.keys()))
        print(statistic_pop_ratio)
        trc = dict(
            type = 'choropleth',
            locations = list(df_group.groups.keys()),
            locationmode = 'USA-states',
            colorscale = color_scheme,
            z = list(statistic_pop_ratio)

        )
        lyt = dict(geo=dict(scope='usa'), title_text='Map of ' + title + ' per Million People by State', paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)')
    else:
        trc = dict(
            type='choropleth',
            locations=list(df_group.groups.keys()),
            locationmode='USA-states',
            colorscale=color_scheme,
            z=list(analysis[field_name][statistic])
        )
        lyt = dict(geo=dict(scope='usa'), title_text='Map of ' + title + ' by State', paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)')
    map_ = go.Figure(data=[trc], layout=lyt)
    plot_url = py.plot(map_)
    # plot(map_)

def plot_distribution(df, field_name, title, stack_field=None, stack_title='', log_x=False, nbins=None):
    py.sign_in('kobzajj', 'pBtRNtdf8xHNSz5l9KmB')

    df_not_missing = df[df[field_name].isnull() == False]
    if stack_field is not None:
        df_not_missing = df_not_missing[df_not_missing[stack_field].isnull() == False]
        fig = px.histogram(df_not_missing, x=field_name, color=stack_field,
                           title='Histogram of ' + title + ' Broken Down by ' + stack_title,
                           labels={field_name: title, stack_field: stack_title}, nbins=nbins)
    else:
        fig = px.histogram(df_not_missing, x=field_name, title='Histogram of ' + title,
                           labels={field_name: title}, log_x=log_x, nbins=nbins)
    plot_url = py.plot(fig)
    # plot(fig)

def plot_relationship(df, x, y, x_title, y_title, log_x=False, log_y=False, stack_field=None, stack_title=''):
    py.sign_in('kobzajj', 'pBtRNtdf8xHNSz5l9KmB')

    df_not_missing = df[df[x].isnull() == False]
    df_not_missing = df_not_missing[df_not_missing[y].isnull() == False]
    fig = px.scatter(df_not_missing, x=x, y=y, title='Relationship Between ' + x_title + ' and ' + y_title,
                     labels={x: x_title, y: y_title, stack_field: stack_title}, log_x=log_x, log_y=log_y, color=stack_field)
    plot_url = py.plot(fig)
    # plot(fig)

def plot_relationship_with_fit(df, x, y, x_title, y_title, log_x=False, log_y=False, stack_field=None, stack_title=''):
    # Generated linear fit
    slope, intercept, r_value, p_value, std_err = stats.linregress(df[x], df[y])
    line = slope * df[x] + intercept

    # Creating the dataset, and generating the plot
    trace1 = go.Scatter(
        x=df[x],
        y=df[y],
        mode='markers',
        marker=go.Marker(color='rgb(255, 127, 14)'),
        name='Data'
    )

    trace2 = go.Scatter(
        x=df[x],
        y=line,
        mode='lines',
        marker=go.Marker(color='rgb(31, 119, 180)'),
        name='Fit'
    )

    annotation = go.Annotation(
        x=3.5,
        y=23.5,
        text='$R^2 = 0.9551,\\Y = 0.716X + 19.18$',
        showarrow=False,
        font=go.Font(size=16)
    )
    layout = go.Layout(
        title='Linear Fit in Python',
        plot_bgcolor='rgb(229, 229, 229)',
        xaxis=go.XAxis(zerolinecolor='rgb(255,255,255)', gridcolor='rgb(255,255,255)'),
        yaxis=go.YAxis(zerolinecolor='rgb(255,255,255)', gridcolor='rgb(255,255,255)'),
        annotations=[annotation]
    )

    data = [trace1, trace2]
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig)
    # plot(fig)

def plot_bar(df, x, y, x_title, y_title):
    py.sign_in('kobzajj', 'pBtRNtdf8xHNSz5l9KmB')
    df_not_missing = df[df[x].isnull() == False]
    df_not_missing = df_not_missing[df_not_missing[y].isnull() == False]
    fig = px.bar(df, x=x, y=y, labels={x: x_title, y: y_title}, title='Bar Chart of ' + x_title + ' against ' + y_title)
    plot_url = py.plot(fig)
