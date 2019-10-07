import numpy as np
import pandas as pd

file_name = 'charities.csv'

# key operations in this file:
#     read csv file into pandas dataframe
#     process the missing values in the dataframe
#     unpack the attributes from 990 form and website to create booleans for each attribute
#     calculate key ratios from financial numbers and add to dataframe

def read_csv(f):
    return pd.read_csv(f, header=0)


def process_missingvals(df):
    pass


def unpack_attributes(df):
    pass


def calculate_ratios(df):
    pass


charity_df = process_csv(file_name)