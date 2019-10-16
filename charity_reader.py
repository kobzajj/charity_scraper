import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import charity_nlp as cnlp
import charity_charts as cc
import locale

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

    df['leader_comp'] = df['leader_comp'].replace('Not compensated', 0)
    df['leader_comp'] = df['leader_comp'].replace('None reported', np.nan)

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

locale.setlocale(locale.LC_ALL, '')

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
print('Total Revenue of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['revenue_total'].sum(), grouping=True)))
print('Total Contributions of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['contributions_tot'].sum(), grouping=True)))
print('Total Expenses of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['expenses_total'].sum(), grouping=True)))

print('Average Revenue of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['revenue_total'].mean(), grouping=True)))
print('Average Contributions of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['contributions_tot'].mean(), grouping=True)))
print('Average Expenses of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['expenses_total'].mean(), grouping=True)))
print('Average Excess of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['excess'].mean(), grouping=True)))
print('Maximum Excess of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['excess'].max(), grouping=True)))
print('Minmum Excess of Scraped Charitable Organizations: %s' %(locale.currency(charity_df['excess'].min(), grouping=True)))

print('Maximum Contributions of Scraped Charitable Organizations: %s - %s' %(charity_df.loc[charity_df['contributions_tot'] == charity_df['contributions_tot'].max()]['name'], locale.currency(charity_df['contributions_tot'].max(), grouping=True)))
print('Minmum Contributions of Scraped Charitable Organizations: %s - %s' %(charity_df.loc[charity_df['contributions_tot'] == charity_df['contributions_tot'].min()]['name'], locale.currency(charity_df['contributions_tot'].min(), grouping=True)))

print(charity_df['rating_overall'].mean())
print('4 Stars: %d (%.0f%%)' %(charity_df[charity_df['rating_overall']==4]['name'].count(), charity_df[charity_df['rating_overall']==4]['name'].count() / charity_df.shape[0] * 100))
print('3 Stars: %d (%.0f%%)' %(charity_df[charity_df['rating_overall']==3]['name'].count(), charity_df[charity_df['rating_overall']==3]['name'].count() / charity_df.shape[0] * 100))
print('2 Stars: %d (%.0f%%)' %(charity_df[charity_df['rating_overall']==2]['name'].count(), charity_df[charity_df['rating_overall']==2]['name'].count() / charity_df.shape[0] * 100))
print('1 Stars: %d (%.0f%%)' %(charity_df[charity_df['rating_overall']==1]['name'].count(), charity_df[charity_df['rating_overall']==1]['name'].count() / charity_df.shape[0] * 100))
print('0 Stars: %d (%.0f%%)' %(charity_df[charity_df['rating_overall']==0]['name'].count(), charity_df[charity_df['rating_overall']==0]['name'].count() / charity_df.shape[0] * 100))
print('Missing: %d (%.0f%%)' %(charity_df[charity_df['rating_overall'].isnull()]['name'].count(), charity_df[charity_df['rating_overall'].isnull()]['name'].count() / charity_df.shape[0] * 100))

# # map of charity counts by state
# cc.create_state_map(charity_df, 'name', 'Number of Charities', 'count', 'magma')

# # map of charity counts per million people by state
# cc.create_state_map(charity_df, 'name', 'Number of Charities', 'count', 'magma', by_pop=True)

# # map of average overall score by state
# cc.create_state_map(charity_df, 'score_overall', 'Average Score', 'mean', 'magma')

# # distribution of charities by category, with breakdown by rating (4 to 1) layered on top
cc.plot_distribution(charity_df.sort_values(by=['category_l1', 'rating_overall']), 'category_l1', 'Charity Category', stack_field='rating_overall', stack_title='Overall Rating')

# cc.plot_bar(charity_df.sort_values(by=['category_l1']), 'category_l1', 'contributions_tot', 'Category', 'Total Contributions')

# # distribution of overall score across all charities
# cc.plot_distribution(charity_df.sort_values(by=['rating_overall']), 'score_overall', 'Overall Score', stack_field='rating_overall', stack_title='Overall Rating', nbins=80)

charity_df['log_revenue'] = np.log10(charity_df['revenue_total'])

# # distribution of revenue across all charities
# cc.plot_distribution(charity_df.sort_values(by=['rating_overall']), 'log_revenue', 'Log Base 10 of Total Revenue', stack_field='rating_overall', stack_title='Overall Rating', nbins=80)
#
# # distribution of expenses across all charities
# cc.plot_distribution(charity_df, 'expenses_total', 'Total Expenses')
#
# # distribution of excess (revenue minus cost) across all charities
# cc.plot_distribution(charity_df, 'excess', '2018 Excess (Revenue-Cost)')
#
# # distribution of net assets across all charities
# cc.plot_distribution(charity_df, 'net_assets', 'Net Assets')
#
# # relationship between net assets and overall score
# cc.plot_relationship(charity_df, 'net_assets', 'score_overall', 'Net Assets', 'Overall Score', log_x=True)
#
# # relationship between excess (revenue minus cost) and overall score
# cc.plot_relationship(charity_df, 'excess', 'score_overall', 'Excess (Revenue-Cost)', 'Overall Score', log_x=True)
#
# # relationship between total revenue and overall score
# cc.plot_relationship(charity_df, 'revenue_total', 'score_overall', 'Total Revenue', 'Overall Score', log_x=True)
#
# # relationship between program / expense ratio and overall score
# cc.plot_distribution(charity_df.sort_values(by=['rating_overall']), 'prog_expense_ratio', 'Program Expense Ratio', nbins=40, stack_field='rating_overall', stack_title='Overall Rating')
# cc.plot_relationship(charity_df, 'prog_expense_ratio', 'score_overall', 'Program Expense Ratio', 'Overall Score', stack_field='rating_overall', stack_title='Overall Rating')

# cc.plot_relationship_with_fit(charity_df, 'prog_expense_ratio', 'score_overall', 'Program Expense Ratio', 'Overall Score', stack_field='rating_overall', stack_title='Overall Rating')

# # relationship between funding efficiency and overall score
# cc.plot_relationship(charity_df, 'fund_efficiency', 'score_overall', 'Funding Efficiency', 'Overall Score', stack_field='rating_overall', stack_title='Overall Rating')

# charity_df_no_wc_outliers = charity_df[['working_capital_ratio', 'score_overall']]
# charity_df_no_wc_outliers = charity_df_no_wc_outliers.loc[charity_df_no_wc_outliers['working_capital_ratio'].apply(lambda x: np.abs(x - charity_df_no_wc_outliers['working_capital_ratio'].mean()) / charity_df_no_wc_outliers['working_capital_ratio'].std() < 3)]

# relationship between working capital ratio and overall score
# cc.plot_relationship(charity_df, 'working_capital_ratio', 'score_overall', 'Working Capital Ratio', 'Overall Score', stack_field='rating_overall', stack_title='Overall Rating')
# cc.plot_relationship(charity_df_no_wc_outliers, 'working_capital_ratio', 'score_overall', 'Working Capital Ratio', 'Overall Score', stack_field='rating_overall', stack_title='Overall Rating')

charity_df.dropna(axis=0, subset=['leader_comp'])

# # analysis of leader compensation
# cc.plot_distribution(charity_df, 'leader_comp', 'Leader Compensation', nbins=50)
#
# cc.plot_relationship(charity_df, 'leader_comp', 'excess', 'Leader Compensation', 'Excess (Revenue-Cost)', stack_field='rating_overall', stack_title='Overall Rating')

# cc.plot_relationship(charity_df, 'num_990_attributes', 'score_overall', 'Number of 990 Attributes', 'Overall Score')
# cc.plot_relationship(charity_df, 'num_website_attributes', 'score_overall', 'Number of Website Attributes', 'Overall Score')