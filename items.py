# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CharityItem(scrapy.Item):
    # general information
    name = scrapy.Field()
    tagline = scrapy.Field()
    category_l1 = scrapy.Field()
    category_l2 = scrapy.Field()
    # scoring information
    score_overall = scrapy.Field()
    score_financial = scrapy.Field()
    score_acc_trans = scrapy.Field()
    rating_overall = scrapy.Field()
    rating_financial = scrapy.Field()
    rating_acc_trans = scrapy.Field()
    # mission - text field with description of the charity's mission
    mission = scrapy.Field()
    # financial information - revenue
    contributions_tot = scrapy.Field()
    contributions_gifts_grants = scrapy.Field()
    contributions_federated_campaigns = scrapy.Field()
    contributions_membership_dues = scrapy.Field()
    contributions_fundraising_events = scrapy.Field()
    contributions_related_organizations = scrapy.Field()
    contributions_government_grants = scrapy.Field()
    revenue_program_service = scrapy.Field()
    primary_revenue_total = scrapy.Field()
    revenue_other = scrapy.Field()
    revenue_total = scrapy.Field()
    # financial information - expenses
    expenses_program = scrapy.Field()
    expenses_admin = scrapy.Field()
    expenses_fundraising = scrapy.Field()
    expenses_total = scrapy.Field()
    # financial information - overall
    affiliate_payments = scrapy.Field()
    excess = scrapy.Field()
    net_assets = scrapy.Field()
    # attributes - form 990
    attributes_990 = scrapy.Field()
    # attributes - website
    attributes_website = scrapy.Field()