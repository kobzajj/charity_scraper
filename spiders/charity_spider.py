# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from charity_scraper.items import CharityItem
import re


class CharitySpider(Spider):
    name = 'charity_spider'
    allowed_urls = ['https://charitynavigator.org']
    start_urls = ['https://charitynavigator.org/index.cfm?bay=search.alpha']

    def parse(self, response):
        # Find all the urls for the directory pages that make up the full set of charities
        directory_urls = response.xpath('//*[@class="letters"][1]/a/@href').extract()
        for url in directory_urls:
            yield Request(url=url, callback=self.parse_directory_page)

    def parse_directory_page(self, response):
        # Find all the urls for the charity pages within the directory page
        charity_urls = response.xpath('//div[@class="mobile-padding charities"]/a/href').extract()
        for url in charity_urls:
            yield Request(url=url, callback=self.parse_charity_page)

    def parse_charity_page(self, response):
        # get the part of the page with the information we want using the xpath
        container = response.xpath('//div[@class="rating-wrapper"]')
        # split the page into three sections that have the items we are looking to scrape
        summary_section = container.xpath('.//div[@class="summaryBox"]')
        income_section = container.xpath('.//div[@class="summaryBox income-table"]')
        comp_section = container.xpath('.//div[@class="summaryBox cn-accordion-rating"]')

        # get all the information from each section
        # general information outside the container
        name = response.xpath('//h1[@class="charityname"]/text()').extract_first().strip()
        tagline = response.xpath('//h2[@class="tagline"]/text()').extract_first().strip()
        [category_l1, category_l2] = response.xpath('//p[@class="crumbs"]/text()').extract_first().strip().split(" : ")
        # scoring, mission, and attributes information within the rating wrapper container
        scoring_table = summary_section.xpath('.//div[@class="shadedtable"]')[0]
        score_overall = float(scoring_table.xpath('./table/tr[2]/td[2]/text()').extract_first().strip())
        score_financial = float(scoring_table.xpath('./table/tr[3]/td[2]/text()').extract_first().strip())
        score_acc_trans = float(scoring_table.xpath('./table/tr[4]/td[2]/text()').extract_first().strip())
        rating_list = ['one', 'two', 'three', 'four']
        rating_overall = rating_list.index(scoring_table.xpath('./table/tr[2]/td[3]/strong/svg/title/text()').extract_first().strip().split(" ")[0]) + 1
        rating_financial = rating_list.index(scoring_table.xpath('./table/tr[3]/td[3]/strong/svg/title/text()').extract_first().strip().split(" ")[0]) + 1
        rating_acc_trans = rating_list.index(scoring_table.xpath('./table/tr[4]/td[3]/strong/svg/title/text()').extract_first().strip().split(" ")[0]) + 1
        mission = summary_section.xpath('.//div[@class="summaryBox cn-table"]//p/text()').extract_first().strip()
        # information provided on form 990 - attribute legend: (binary encoded - each bit corresponds to an attribute)
        # 0x1 - independent voting board members
        # 0x2 - no material diversion of assets
        # 0x4 - audited financials prepared by independent accountant
        # 0x8 - does not provide loan(s) or receive loan(s) from related parties
        # 0x10 - documents board meeting minutes
        # 0x20 - provided copy of form 990 to organization's governing body in advance of filing
        # 0x40 - conflict of interest policy
        # 0x80 - whistleblower policy
        # 0x100 - records retention and destruction policy
        # 0x200 - CEO listed with salary
        # 0x400 - process for determining CEO compensation
        # 0x800 - board listed / board members not compensated
        # information provided on charity's webiste - attribute legend: (binary encoded - each bit corresponds to an attribute)
        # 0x1 - donor privacy policy
        # 0x2 - board members listed
        # 0x4 - audited financials
        # 0x8 - form 990
        # 0x10 - key staff listed
        metrics_table = summary_section.xpath('.//div[@class="shadedtable cn-accordion-rating"][2]/div/table')
        attributes_990 = 0
        attributes_website = 0
        for i in range(12):
            attributes_990 += 2**i * (re.search('/checked.gif', metrics_table.xpath('./tr[' + str(i+2) + ')]/td[3]/img/@src').extract_first()) is not None)
        for j in range(5):
            attributes_website += 2**j * (re.search('/checked.gif', metrics_table.xpath('./tr[' + str(i+15) + ')]/td[3]/img/@src').extract_first()) is not None)
        financial_table_keys = ['', '', 'contributions_gifts_grants', 'contributions_federated_campaigns', 'contributions_membership_dues',
                                 'contributions_fundraising_events', 'contributions_related_organizations', 'contributions_government_grants',
                                 'contributions_tot', 'revenue_program_service', 'primary_revenue_total', 'revenue_other', 'revenue_total',
                                 '', '', 'expenses_program', 'expenses_admin', 'expenses_fundraising', 'expenses_total', '', 'affiliate_payments',
                                 'excess', '', 'net_assets']
        financial_table_vals = [0 if income_section.xpath('./div/div/table/tr[' + str(i+1) + ']/td[2]/text()').extract_first() == '\xa0'
                                else int(income_section.xpath('./div/div/table/tr[' + str(i+1) + ']/td[2]/text()').extract_first().replace(',', '').replace('$', ''))
                                for i in range(0, 24)]

        # Initialize a new CharityItem instance for each charity.
        item = CharityItem()
        item['name'] = name
        item['tagline'] = tagline
        item['category_l1'] = category_l1
        item['category_l2'] = category_l2
        item['score_overall'] = score_overall
        item['score_financial'] = score_financial
        item['score_acc_trans'] = score_acc_trans
        item['rating_overall'] = rating_overall
        item['rating_financial'] = rating_financial
        item['rating_acc_trans'] = rating_acc_trans
        item['mission'] = mission
        item['attributes_990'] = attributes_990
        item['attributes_website'] = attributes_website
        for i in range(24):
            if financial_table_keys[i] != '':
                item[financial_table_keys[i]] = financial_table_vals[i]
        yield item
