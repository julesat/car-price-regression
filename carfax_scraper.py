#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.support.ui import Select
from fake_useragent import UserAgent
import time
import random

url = 'http://www.carfax.com/robots.txt'
response  = requests.get(url)
# print(response.text

philly = {'url': 'https://www.carfax.com/Used-Cars-in-Philadelphia-PA_c4927', 'zipcode': 19107}

def pull_car_listings(location=philly, num_pages=55):
    """
    Navigating carfax.com, retrieving html from each page of search results and saving BeautifulSoup objects to a text file.
    """
    
    def randomize_user():
    
        options = Options()
        options.add_argument("window-size=1400,700")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches",["enable-automation"])
        user_agent = UserAgent().random
        options.add_argument(f'user-agent={user_agent}')
        return options

    def insert_pause():
        time.sleep(1+2*random.random())
        
    def long_pause():
        time.sleep(4+2*random.random())
    
    def select_search_radius():
        insert_pause() 
        driver.find_element_by_xpath("//a[.//h4[text()='Location']]").click()

        # WebDriverWait(driver, 1+10*random.random()).until(element_to_be_clickable((By.CLASS_NAME, 'accordion-title'))).click()
        # select = Select(driver.find_element_by_class_name('accordion-title'))
        # select.select_by_index(0)
        insert_pause()      
        
    def click_next():
        WebDriverWait(driver, 10*random.random()).until(element_to_be_clickable((By.CSS_SELECTOR, 
                        'button.primary-blue.pagination__button.pagination__button--right'))).click()

    def append_page():
        html = driver.page_source
        soup = bs(html)
        soup_list.append(soup)
        
        with open(location['name']+'_soup_progress.txt', 'a') as f:
            f.write(str(html) + 'BREAKHERE')
                
        
    soup_list = []
    
    with webdriver.Firefox() as driver:
        
        driver.get('https://www.carfax.com/')
        insert_pause()

        driver.get(location['url'])
        insert_pause()

        driver.find_element_by_xpath("//a[.//h4[text()='Location']]").click()
        insert_pause()

        driver.find_element_by_name('zip').clear()
        insert_pause()

        driver.find_element_by_name('zip').send_keys(location['zipcode'])
        insert_pause()
        
        # hit 'Search'
        # wait = WebDriverWait(driver, 1+10*random.random()).until(element_to_be_clickable((By.CSS_SELECTOR, 
        #                             '.button.expanded.searchForm-submit-btn'))).click()
        # insert_pause()
        insert_pause()

        
        append_page()

        try:
            for i in range(num_pages):
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                insert_pause()
                click_next()

                append_page()

                long_pause()

        except Exception as e: 
            # save progress
            print('iteration ' + str(i))
            print(e)
            soup_list_prettified = [k.prettify() for k in soup_list]
            list_with_break_word = [m + 'BREAKHERE' for m in soup_list_prettified]
            list_as_one = "".join(list_with_break_word)
            with open('soup_list.txt', 'w') as file:   
                file.write(list_as_one)

        time.sleep(5)
    return soup_list



def build_car_df(soup_list):
    """
    Parse a list of BeautifulSoup objects to store car details in a Pandas dataframe. 
    """
    
    pages = []

    # looping through results pages
    for i, soup in enumerate(soup_list):
        if type(soup) == str:
            soup = bs(soup)

        details_list = []

        for listing in soup.find_all(class_='srp-list-item'):
            details = [x.text.strip() for x in listing.find_all(class_='srp-list-item-basic-info-value')]
            details_list.append({x.split(': ')[0] : x.split(': ')[1] for x in details})

        details_df = pd.DataFrame(details_list)

        prices =        [x.text.split(' ')[1].replace('$', '').replace(',', '') 
                          for x in soup.find_all(class_='srp-list-item-price')]
        price_diff = [re.sub(r'[$,\s]','', x.text) for x in soup.find_all('div', class_='value-difference')]
        
        # encode difference from carfax value as positive or negative
        for i, x in enumerate(price_diff):
            x = x.replace('below','-').replace('above','+')
            price_diff[i] = int(x[-1] + x[:-1])

        location =      [x.find('span').text.strip() for x in soup.find_all(class_='srp-list-item-dealership-location')]

        model_info =    [x.text for x in soup.find_all(class_='srp-list-item-basic-info-model')]
        model_year =    [x.split(' ')[0] for x in model_info]
        manufacturer =  [x.split(' ')[1] for x in model_info]
        car_model =     [x.split(' ')[2] for x in model_info]

        damage =        [x.text for x in soup.select('.title.title--noAccident')]
        service_count = [int(x['data-count']) for x in soup.find_all(class_='count')]
        options =       [x.text.split('with ')[1] if len(x.text.split('with ')) > 1 else ''
                          for x in soup.find_all(class_='srp-list-item-options-descriptions')]

        # getting descriptive data from inset box
        owner_history = [x.contents[1].find(class_='description').text
                         for x in soup.find_all(class_='srp-list-item-pillars-list')]      


        index = range(i*25, i*25+25)

        car_df = pd.DataFrame({'index': index, 'price': prices, 'price_diff': price_diff,
                               'year': model_year, 'make': manufacturer, 
                               'model': car_model, 'damage': damage, 'service': service_count, 
                              'history': owner_history, 'options': options, 'location': location})

        car_df = pd.concat((car_df, details_df), axis=1)
        car_df.columns = car_df.columns.str.lower()

        # merge two differently named features for same data
        car_df.rename(columns={'body type': 'body_type'}, inplace=True)

        if 'body style' in car_df.columns:
            if 'body_type' in car_df.columns:
                car_df['body_type'] = car_df['body style'].fillna('') + car_df['body_type'].fillna('')
            else:
                car_df['body_type'] = car_df['body style']
            car_df.drop('body style', axis=1, inplace=True)

        pages.append(car_df)
    cars = pd.concat(pages)

    return cars


