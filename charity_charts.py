import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go
import chart_studio.plotly as py
from plotly.offline import plot
import plotly.express as px


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

def create_state_map(df, field_name, statistic, color_scheme):
    df_group = df[df['location_state'].isnull() == False]
    group_functions = {field_name: [statistic]}
    df_group = df_group.groupby('location_state')
    analysis = df_group.agg(group_functions)
    trc = dict(
        type = 'choropleth',
        locations = list(df_group.groups.keys()),
        locationmode = 'USA-states',
        colorscale = color_scheme,
        z = list(analysis[field_name][statistic])
    )
    lyt = dict(geo = dict(scope = 'usa'))
    map_ = go.Figure(data=[trc], layout=lyt)
    plot(map_)

def plot_distribution(df, field_name, stack_field=None):
    df_not_missing = df[df[field_name].isnull() == False]
    if stack_field is not None:
        df_not_missing = df_not_missing[df_not_missing[stack_field].isnull() == False]
        fig = px.histogram(df_not_missing, x=field_name, color=stack_field)
    else:
        fig = px.histogram(df_not_missing, x=field_name)
    plot(fig)

def plot_relationship(df, x, y):
    df_not_missing = df[df[x].isnull() == False]
    df_not_missing = df_not_missing[df_not_missing[y].isnull() == False]
    fig = px.scatter(df_not_missing, x=x, y=y)
