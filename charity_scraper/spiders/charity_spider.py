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
        charity_urls = response.xpath('//div[@class="mobile-padding charities"]/a/@href').extract()
        for url in charity_urls:
            yield Request(url=url, callback=self.parse_charity_page)

    def parse_charity_page(self, response):
        # first scrape the information that's on all the charity pages, regardless of whether it is rated or not
        name = response.xpath('//h1[@class="charityname"]/text()').extract_first().strip()
        tagline = response.xpath('//h2[@class="tagline"]/text()').extract_first().strip()
        [category_l1, category_l2] = response.xpath('//p[@class="crumbs"]/text()').extract_first().strip().split(" : ")

        # Initialize a new CharityItem instance for each charity.
        item = CharityItem()
        item['name'] = name
        item['tagline'] = tagline
        item['category_l1'] = category_l1
        item['category_l2'] = category_l2

        location_line_flag = 1 * (re.search('([a-zA-Z]+)(\s?)[,][\s][A-Z]{2}[\s]([\d]{5})', re.sub('[\r\n\t\xa0]+', ' ', response.xpath('//div[@id="leftnavcontent"]/div/p[1]/text()').extract()[1]).strip()) is None)
        location = re.split('[\r\n\t\xa0,]+', response.xpath('//div[@id="leftnavcontent"]/div/p[1]/text()').extract()[1 + location_line_flag])
        if '' in location:
            location.remove('')
        if len(location) == 3:
            location_city = location[0].strip()
            location_state = location[1].strip()
            location_zip = location[2].strip()
            item['location_city'] = location_city
            item['location_state'] = location_state
            item['location_zip'] = location_zip

        # the rest of the fields can only be filled in if the charity has a rating, so can check if the container object is found in the xpath
        # get the part of the page with the information we want using the xpath
        container = response.xpath('//div[@class="rating-wrapper"]')
        if container:
            # split the page into three sections that have the items we are looking to scrape
            summary_section = container.xpath('.//div[@class="summaryBox"]')
            income_section = container.xpath('.//div[@class="summaryBox income-table"]')

            # get all the information from each section
            # general information outside the container

            # scoring, mission, and attributes information within the rating wrapper container
            scoring_table = summary_section.xpath('.//div[@class="shadedtable"]')[0]
            score_overall = float(scoring_table.xpath('./table/tr[2]/td[2]/text()').extract_first().strip())
            score_financial = float(scoring_table.xpath('./table/tr[3]/td[2]/text()').extract_first().strip())
            score_acc_trans = float(scoring_table.xpath('./table/tr[4]/td[2]/text()').extract_first().strip())
            rating_list = ['one', 'two', 'three', 'four']
            rating_overall_xpath = scoring_table.xpath('./table/tr[2]/td[3]/strong/svg/title/text()').extract_first()
            if rating_overall_xpath is not None:
                rating_overall = rating_list.index(rating_overall_xpath.strip().split(" ")[0]) + 1
            else:
                rating_overall = 0
            rating_financial_xpath = scoring_table.xpath('./table/tr[3]/td[3]/strong/svg/title/text()').extract_first()
            if rating_financial_xpath is not None:
                rating_financial = rating_list.index(rating_financial_xpath.strip().split(" ")[0]) + 1
            else:
                rating_financial = 0
            rating_acc_trans_xpath = scoring_table.xpath('./table/tr[3]/td[3]/strong/svg/title/text()').extract_first()
            if rating_acc_trans_xpath is not None:
                rating_acc_trans = rating_list.index(rating_acc_trans_xpath.strip().split(" ")[0]) + 1
            else:
                rating_acc_trans = 0
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
                if metrics_table.xpath('./tr[' + str(i+2) + ']/td[3]/img/@src').extract_first() is None:
                    continue
                attributes_990 += 2**i * (re.search('/checked.gif', metrics_table.xpath('./tr[' + str(i+2) + ']/td[3]/img/@src').extract_first()) is not None)
            for j in range(5):
                if metrics_table.xpath('./tr[' + str(j+15) + ']/td[3]/img/@src').extract_first() is None:
                    continue
                attributes_website += 2**j * (re.search('/checked.gif', metrics_table.xpath('./tr[' + str(j+15) + ']/td[3]/img/@src').extract_first()) is not None)
            financial_table_keys = ['', '', 'contributions_gifts_grants', 'contributions_federated_campaigns', 'contributions_membership_dues',
                                     'contributions_fundraising_events', 'contributions_related_organizations', 'contributions_government_grants',
                                     'contributions_tot', 'revenue_program_service', 'primary_revenue_total', 'revenue_other', '',
                                     '', '', 'expenses_program', 'expenses_admin', 'expenses_fundraising', '', '', 'affiliate_payments',
                                     'excess', '', 'net_assets']
            financial_table_vals = [0 if ((income_section.xpath('./div/div/table/tr[' + str(i+1) + ']/td[2]/text()').extract_first() == '\xa0') or (income_section.xpath('./div/div/table/tr[' + str(i+1) + ']/td[2]/text()').extract_first() is None))
                                    else int(income_section.xpath('./div/div/table/tr[' + str(i+1) + ']/td[2]/text()').extract_first().replace(',', '').replace('$', ''))
                                    for i in range(0, 24)]
            revenue_total = financial_table_vals[financial_table_keys.index('primary_revenue_total')] + financial_table_vals[financial_table_keys.index('revenue_other')]
            expenses_total = financial_table_vals[financial_table_keys.index('expenses_program')] + financial_table_vals[financial_table_keys.index('expenses_admin')] + financial_table_vals[financial_table_keys.index('expenses_fundraising')]

            leader_comp = container.xpath('.//div[@class="summaryBox cn-accordion-rating"][2]/div/table/tr[2]/td[1]/span/text()').extract_first().strip().replace(',', '').replace('$', '')

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
            item['expenses_total'] = expenses_total
            item['revenue_total'] = revenue_total
            item['leader_comp'] = leader_comp
        yield item
