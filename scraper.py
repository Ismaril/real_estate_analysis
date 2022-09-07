import os
import time
import random
import utilities
import numpy as np
import pandas as pd
import constants as c
import requests as requests
import patoolib  # work with zipped files

from selenium import common
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def chrome_driver(headless=True,
                  driver_address=c.DRIVER_ADDRESS):
    # with the option headless set to True, desktop chrome application will not pop up
    options = webdriver.ChromeOptions()
    options.headless = headless
    options.add_argument(f'user-agent={random.choice(c.USER_AGENTS)}')  # set user agent

    # this driver will act as a new desktop window of chrome (if not headless)
    #   and will load dynamic website, before it is scraped. Dynamic websites
    #   cannot be scraped with python requests. Lots of info would miss otherwise.
    driver = webdriver.Chrome(driver_address, options=options)

    return driver


def site_map_scraping():
    """
    Scrape xml files that contain links to all web pages. Extract all links and put them
    into one dataset. This function basically gets the whole sitemap.


    """
    driver = chrome_driver(headless=False)

    # read directly from website
    xml_docs = pd.read_xml(
        requests.get(c.SITE_MAP, headers={"User-Agent": random.choice(c.USER_AGENTS)}).text
    )[c.LOC]

    for url in xml_docs:
        # get url of a xml containing links to websites of all given properties,
        #    at a time of creation of this file there were like 5 links
        driver.get(url)
        time.sleep(4)

    # exit the artificial browser
    driver.quit()

    nr_of_xml_docs = len(xml_docs)
    all_links_dataframe = pd.DataFrame()
    for i in range(nr_of_xml_docs):
        # unzip all files that contain links to properties
        patoolib.extract_archive(f"{c.DOWNLOADS}/{c.SITEMAP}{i + 1}.xml.gz",
                                 outdir=c.DOWNLOADS)

        # read files that contain links to properties and put them all in one dataset
        all_links_dataframe = pd.concat(
            [all_links_dataframe,
             pd.read_xml(f"{c.DOWNLOADS}/{c.SITEMAP}{i + 1}.xml")]
        )

    # save df
    all_links_dataframe.to_csv(c.PROPERTIES, index=False)


def features_scraping(batch_size=1000,
                      max_nr_samples=None,
                      failed_request_limit=20):
    """
    Scrape features of a given property. Once a given number of properties has been scraped, save as a
    csv batch.

    :param batch_size: (number of rows) downloaded data will be saved in batches in case of lost connection
    :param max_nr_samples: set upper index as a filter of the dataset
    :param failed_request_limit: number of failed requests in a row to break the loop
    :return: None
    """

    session_time = utilities.Performance()
    session_time.start()

    driver = chrome_driver(headless=False)
    batches = os.listdir(c.BATCHES)
    data = pd.read_csv(c.PROPERTIES_CLEANED)
    final_dataframe = pd.DataFrame()
    average_iter_time = []
    timed_out_requests = 0
    timed_out_requests_total = 0

    # if some data were already downloaded, continue based on last downloaded index.
    if batches:
        last_completed_index = int(max(int(item.split(".")[0]) for item in batches))

        # filter the dataset which contains links to webpages and continue scraping
        data = data[last_completed_index + 1:max_nr_samples]

    # scraping starts for the first time, and therefore start from the beginning of the
    #    source dataset which contains links to webpages
    else:
        data = data[:max_nr_samples]

    # iterate through webpages and scrape
    for index_session, link in enumerate(data[c.LINK]):
        iteration_time = utilities.Performance()
        iteration_time.start()

        # break out of loop if x requests are timed out, possibly by lost
        #     internet connection, site unavailable or high ping etc...
        if timed_out_requests == failed_request_limit:
            utilities.send_email(
                subject=f"Scrapping stopped due to {failed_request_limit}"
                        f"timed  out requests in a row."
            )
            break

        index_all_data = data.index[data[c.LINK] == link].tolist()[0]

        # get url of a desired website
        try:
            driver.get(link)

            # with WebDriverWait program will wait till the specified x path is found in a given webpage.
            # this means that the page has content and we will wait till javascript loads.
            # previously I encountered a problem where data were present in the page, but nothing was scraped
            x_path = '//*[@id="page-layout"]/div[2]/div[3]/div[3]/div/div/div/div/div[4]/h1/span/span[1]'
            WebDriverWait(driver, 6).until(ec.presence_of_element_located((By.XPATH, x_path)))

            driver.delete_all_cookies()

        # request timed out
        except common.exceptions.TimeoutException:
            timed_out_requests += 1
            timed_out_requests_total += 1
            iteration_time = iteration_time.end()
            average_iter_time.append(iteration_time)
            print("Request timed out, or webpage does not exist",
                  f"Iter time: {iteration_time:.2f} sec",
                  link,
                  sep="\n",
                  end=c.SEPARATOR)
            continue

        timed_out_requests = 0

        # Beautiful soup perhaps gonna return "MarkupResemblesLocatorWarning"
        #    but html is actually inputted inside, so it is probably false alarm
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # get labels (generally for all properties) from a given website
        #     Example: <label class="param-label ng-binding">Celková cena:</label>
        elements = soup.find_all("label", class_="param-label ng-binding")
        labels = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            labels.append(item.text)

        # get all the information that corresponds to a given property label on the website
        # Example: <span ng-if="item.type != 'link'" class="ng-binding ng-scope">5&nbsp;
        #     799&nbsp;000 Kč za nemovitost</span>
        elements = soup.find_all("span", class_="ng-binding ng-scope")
        features = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            features.append(item.text)

        # find town and state based on class
        elements = soup.find_all("span", class_="location-text ng-binding")
        location = ""
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            location += item.text

        # put all labels and all features regarding a given reality into dict and prepare them as a row.
        # note, that we also take location again (here directly from link), due to inconsistency
        #   of format in the webpage.
        dict_ = {}
        link_split = link.split("/")
        dict_[c.LINK] = link
        dict_[c.PROPERTY] = link_split[5]
        dict_[c.TYPE] = link_split[6]
        dict_[c.LOCATION] = link_split[7]
        dict_[c.LOCATION2] = location
        dict_[c.DATETIME_SCRAPED] = time.ctime()

        valid_columns = [c.TOTAL_PRICE,
                         c.STRUCTURE,
                         c.STATE_OF_OBJECT,
                         c.OWNERSHIP,
                         c.ON_SALE,
                         c.FORMER_PRICE,
                         c.USABLE_AREA,
                         c.LAND_AREA,
                         c.GARDEN_AREA]

        for label, info in zip(labels, features):
            if label in valid_columns:
                dict_[label] = info

        # add all scraped data as a new row into dataframe
        new_row = pd.DataFrame(dict_, index=[index_session])
        final_dataframe = pd.concat([final_dataframe, new_row], ignore_index=True)

        # iteration statistic metrics
        iteration_time = iteration_time.end()
        average_iter_time.append(iteration_time)
        print(f"Iter curr session {index_session}, "
              f"Iter total: {index_all_data}, "
              f"Iter time: {iteration_time:.2f} sec",
              f"Average time of all iterations: {np.mean(average_iter_time):.2f} sec",
              new_row.columns,
              link,
              sep="\n",
              end=c.SEPARATOR)

        # save scraped data in batches based on specified batch size
        if (index_session and index_session % batch_size == 0) \
                or index_session == data.shape[0] - 1:
            final_dataframe.to_csv(f"batches/{index_all_data}.csv", encoding="UTF-8", index=False)
            final_dataframe = pd.DataFrame()
            utilities.send_email(
                subject=f"Completed rows: {index_all_data}",
                body=f"Session is running {utilities.readable_time(int(session_time.end()))}\n"
                     f"Average time of all iterations: {np.mean(average_iter_time):.2f} sec\n"
                     f"Timed out requests: {timed_out_requests_total}")
            print(f"Saving batch. Completed iterations total: {index_all_data}\n",
                  end=c.SEPARATOR)

    # exit the artificial browser
    driver.quit()

    # session statistic metrics
    utilities.send_email(subject="Scraping completed", body="")
    print(f"Scraping features took this session: {session_time.end():.2f} sec",
          f"Average time of all iterations: {np.mean(average_iter_time)} sec",
          sep="\n",
          end=c.SEPARATOR)
