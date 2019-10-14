import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import charity_nlp as cnlp
import charity_charts as cc

file_name = 'charities.csv'

# key operations in this file:
#     read csv file into pandas dataframe
#     process the missing values in the dataframe
#     unpack the attributes from 990 form and website to create booleans for each attribute
#     calculate key ratios from financial numbers and add to dataframe

def read_csv(f):
    return pd.read_csv(f, header=0)


# a subset of the charities scraped are missing most data, except for the name, category, and location
# add a boolean column to the dataframe to capture if a row has incomplete data so these can be filtered out as needed
# also produce some summary statistics of the incomplete rows (category, location, etc.) to ensure data is not biased based on the missing values
def process_missingvals(df):
    df['missing'] = df.isnull().any(axis=1)
    df_missing = df[df['missing'] == True]
    print('Rows with missing values: ' + str(df_missing.missing.count()) + " / " + str(df.shape[0]) + " total charities (" + str(round(df_missing.missing.count()/df.shape[0], 2)*100) + "%)")

    sns.set(font_scale=0.6)

    location_missing_dist = df['location_state'].groupby(df['missing']).value_counts(normalize=True).rename('percentage').reset_index()
    location_grid = sns.FacetGrid(location_missing_dist, col='missing', hue='missing', palette='Set1', height=6)
    location_grid.map(sns.barplot, "location_state", "percentage")
    for ax in location_grid.axes.flat:
        for label in ax.get_xticklabels():
            label.set_rotation(90)
    location_grid.fig.suptitle('Distribution of Missing vs. Non-Missing Values by State')
    # plt.show()
    category_missing_dist = df['category_l1'].groupby(df['missing']).value_counts(normalize=True).rename('percentage').reset_index()
    category_grid = sns.FacetGrid(category_missing_dist, col='missing', hue='missing', palette='Set1', height=6)
    category_grid.map(sns.barplot, "category_l1", "percentage")
    for ax in category_grid.axes.flat:
        for label in ax.get_xticklabels():
            label.set_rotation(90)
    category_grid.fig.suptitle('Distribution of Missing vs. Non-Missing Values by Category')
    # plt.show()

    return df


# unpack the attributes fields (attributes_990 and attributes_website) to see which attributes apply to which charities
# add columns to the dataframe for each attribute, and additional columns to sum up the attributes each charity has
def unpack_attributes(df):
    atts_990 = ['ind_board', 'no_asset_diversion', 'ind_accountant', 'no_related_loans', 'board_minutes', 'advance_990',
                'conf_int_policy', 'whistleblower_policy', 'records_policy', 'ceo_listed', 'ceo_comp_process', 'board_listed']
    atts_website = ['donor_priv_policy', 'board_members', 'audited_financials', 'form_990', 'key_staff']
    df['num_990_attributes'] = np.zeros(df.shape[0], dtype=int)
    df['num_website_attributes'] = np.zeros(df.shape[0], dtype=int)
    atts_990_mask = df['attributes_990']
    for att_ in atts_990:
        df[att_] = atts_990_mask % 2 == 1
        df['num_990_attributes'] += atts_990_mask % 2
        atts_990_mask //= 2
    atts_website_mask = df['attributes_website']
    for att_ in atts_website:
        df[att_] = atts_website_mask % 2 == 1
        df['num_website_attributes'] += atts_website_mask % 2
        atts_website_mask //= 2
    return df


# add fields to the dataframe for key financial ratios:
# program expense ratio - percent of total expenses spent on services delivered
# fundraising efficiency - fundraising expenses divided by total contributions
# working capital ratio (years) - number of years the charity can sustain itself from its net assets (net assets divided by total expenses)
def calculate_ratios(df):
    df['prog_expense_ratio'] = df['expenses_program'] / df['expenses_total']
    df['fund_efficiency'] = df['expenses_fundraising'] / df['contributions_tot']
    df['working_capital_ratio'] = df['net_assets'] / df['expenses_total']
    return df


charity_df = read_csv(file_name)
charity_df = process_missingvals(charity_df)
charity_df = unpack_attributes(charity_df)
charity_df = calculate_ratios(charity_df)
# charity_df = cnlp.preprocess_text(charity_df, 'mission')
# cnlp.create_wordcloud(charity_df, 'mission_nlp', 'All')
# cnlp.compare_wordclouds(charity_df)
# cnlp.sentiment_analysis(charity_df, 'score_overall')

print('Number of Charities: %d' %(charity_df['name'].count()))
print('Mean of overall score: %.2f' %(charity_df['score_overall'].mean()))
print('Standard Deviation of overall score: %.2f' %(charity_df['score_overall'].std()))
print('Total Revenue of Scraped Charitable Organizations: %.2f' %(charity_df['revenue_total'].sum()))
print('Total Expenses of Scraped Charitable Organizations: %.2f' %(charity_df['expenses_total'].sum()))

# map of charity counts by state
cc.create_state_map(charity_df, 'name', 'Number of Charities', 'count', 'magma')

# map of average overall score by state
cc.create_state_map(charity_df, 'score_overall', 'Average Score', 'mean', 'magma')

# 
cc.plot_distribution(charity_df, 'category_l1', 'Charity Category', stack_field='rating_overall', stack_title='Overall Rating')
cc.plot_distribution(charity_df, 'score_overall', 'Overall Score')
cc.plot_distribution(charity_df, 'revenue_total', 'Total Revenue', log_x=True)
cc.plot_distribution(charity_df, 'expenses_total', 'Total Expenses', log_x=True)
cc.plot_distribution(charity_df, 'excess', '2018 Excess (Revenue-Cost)', log_x=True)
cc.plot_distribution(charity_df, 'net_assets', 'Net Assets', log_x=True)
cc.plot_relationship(charity_df, 'net_assets', 'score_overall', 'Net Assets', 'Overall Score', log_x=True)
cc.plot_relationship(charity_df, 'excess', 'score_overall', 'Excess (Revenue-Cost)', 'Overall Score', log_x=True)
cc.plot_relationship(charity_df, 'revenue_total', 'score_overall', 'Total Revenue', 'Overall Score', log_x=True)
cc.plot_relationship(charity_df, 'prog_expense_ratio', 'score_overall', 'Program Expense Ratio', 'Overall Score')
cc.plot_relationship(charity_df, 'fund_efficiency', 'score_overall', 'Funding Efficiency', 'Overall Score')
cc.plot_relationship(charity_df, 'working_capital_ratio', 'score_overall', 'Working Capital Ratio', 'Overall Score')
cc.plot_relationship(charity_df, 'num_990_attributes', 'score_overall', 'Number of 990 Attributes', 'Overall Score')
cc.plot_relationship(charity_df, 'num_website_attributes', 'score_overall', 'Number of Website Attributes', 'Overall Score')