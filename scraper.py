import os
import time
import random
import send_mail
import numpy as np
import pandas as pd
import data_cleaning
import constants as c
import requests as requests
import patoolib  # work with zipped files

from selenium import common
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

    # todo: might be possible to delete this
    # skip the page request after set time to wait
    # driver.set_page_load_timeout(time_to_wait=15)
    # driver.implicitly_wait(10)

    return driver


def site_map_scraping(driver):
    """
    Scrape xml files that contain links to all web pages. Extract all links and put them
    into one dataset. This function basically gets the whole sitemap.

    :param driver: insert driver that's gonna operate as artificial web-browser
    """

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
    pd.DataFrame(all_links_dataframe).to_csv(c.PROPERTIES, index=False)


def features_scraping(driver,
                      batch_size=1000,
                      max_nr_samples=None,
                      failed_request_limit=20):
    """
    Scrape features of a given property. Once a given number of properties has been scraped, save as a
    csv batch.

    :param driver: insert driver that's gonna operate as artificial web-browser
    :param batch_size: (number of rows) downloaded data will be saved in batches in case of lost connection
    :param max_nr_samples: set upper index as a filter of the dataset
    :param failed_request_limit: number of failed requests in a row to break the loop
    :return: None
    """

    start_session = time.perf_counter()
    batches = os.listdir(c.BATCHES)
    rescraping = False

    # if some data were already downloaded, continue based on last downloaded index.
    if batches:
        last_completed_index = int(max(int(item.split(".")[0]) for item in batches))
        data = pd.read_csv(c.PROPERTIES_CLEANED)

        # TODO: might be possible to delete this block ('if' only)
        # try to scrape unsuccessfully scraped links again if we scraped the whole
        #     dataset already
        if data.shape[0] == last_completed_index + 1:
            # data_cleaning.concatenate_batches()
            data = data_cleaning.prepare_for_rescraping()
            rescraping = True

        # filter the dataset which contains links to webpages and continue scraping
        else:
            data = data[last_completed_index + 1:max_nr_samples]

    # scraping starts for the first time, and therefore start from the beginning of the
    #    source dataset which contains links to webpages
    else:
        data = pd.read_csv(c.PROPERTIES_CLEANED)[:max_nr_samples]

    final_dataframe = pd.DataFrame()
    average_iter_time = []
    timed_out_requests = 0
    timed_out_requests_total = 0

    # iterate through webpages and scrape
    for index_session, link in enumerate(data[c.LINK]):
        start = time.perf_counter()

        # break out of loop if x requests are timed out, possibly by lost
        #     internet connection, site unavailable or high ping etc...
        if timed_out_requests == failed_request_limit:
            send_mail.send_email(
                subject=f"Scrapping stopped due to {failed_request_limit}"
                        f"timed  out requests in a row."
            )
            break

        index_all_data = data.index[data[c.LINK] == link].tolist()[0]

        # get url of a desired website
        try:
            driver.get(link)
            # todo: check how it behaves in next scraping. This function helped a ton
            #   because formerly some pages did not load fully and therefore its content could not be scraped
            x_path = '//*[@id="page-layout"]/div[2]/div[3]/div[3]/div/div/div/div/div[4]/h1/span/span[1]'
            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, x_path)))
            driver.delete_all_cookies()

        # request timed out
        except common.exceptions.TimeoutException:
            timed_out_requests += 1
            timed_out_requests_total += 1
            end = time.perf_counter()
            iteration_time = end - start
            average_iter_time.append(iteration_time)
            print("Request timed out, or webpage does not exist", "!" * 60,
                  f"Iter time: {iteration_time:.2f} sec",
                  link,
                  sep="\n",
                  end=f"\n{'-' * 60}\n")
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
        information = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            information.append(item.text)

        # todo: scrapovat taky stát aby se dala filtrovat zeme
        # put all labels and all info regarding a given reality into and prepare them as a row
        dict_ = {}
        link_split = link.split("/")

        dict_[c.LINK] = link
        dict_[c.PROPERTY] = link_split[5]
        dict_[c.TYPE] = link_split[6]
        location = link_split[7]
        location_split = location.split("-")
        dict_[
            c.LOCATION] = f"{location_split[0].title()} {location_split[1]} {location_split[2]}"  # todo: update
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

        for label, info in zip(labels, information):
            if label in valid_columns:
                dict_[label] = info

        # add all scraped data (in a format of row) as a new row into dataframe
        new_row = pd.DataFrame(dict_, index=[index_session])
        final_dataframe = pd.concat([final_dataframe, new_row], ignore_index=True)

        # iteration statistic metrics
        end = time.perf_counter()
        iteration_time = end - start
        average_iter_time.append(iteration_time)
        print(f"Iter curr session {index_session}, "
              f"Iter total: {index_all_data}, "
              f"Iter time: {iteration_time:.2f} sec",
              f"Average time of all iterations: {np.mean(average_iter_time):.2f} sec",
              f"{new_row.columns}",
              f"{link}"
              f"{'-' * 60}",
              sep="\n")

        if index_session % batch_size == 0:
            send_mail.send_email(f"Index: {index_session},"
                                 f"Avg i time {np.mean(average_iter_time):.2f}s")

        # todo: this might be possible to delete
        # saving rescraped data and end feature scraping for good
        if rescraping and index_session == data.shape[0] - 1:
            final_dataframe.to_csv(f"batches/rescraped.csv", encoding="UTF-8")
            break

        # save scraped data in batches based on specified batch size
        elif (index_session and index_session % batch_size == 0) \
                or index_session == data.shape[0] - 1:
            print(f"Saving batch. Completed iterations total: {index_all_data}",
                  f"\n{'-' * 60}\n")
            final_dataframe.to_csv(f"batches/{index_all_data}.csv", encoding="UTF-8")
            final_dataframe = pd.DataFrame()

            end_batch = time.perf_counter()
            time_batch = end_batch - start_session
            send_mail.send_email(
                subject=f"Completed rows: {index_all_data}",
                body=f"Session is running {data_cleaning.readable_time(int(time_batch))}\n"
                     f"Average time of all iterations: {np.mean(average_iter_time):.2f} sec\n"
                     f"Timed out requests: {timed_out_requests_total}")

    # exit the artificial browser
    driver.quit()

    # session statistic metrics
    end_session = time.perf_counter()
    scraping_time = end_session - start_session
    send_mail.send_email(subject="Scraping completed")
    print(f"Scraping features took this session: {scraping_time:.2f} sec")
    print(f"Average time of all iterations: {np.mean(average_iter_time)} sec",
          "#" * 60,
          sep="\n")

# C:\Users\lazni\PycharmProjects\Real_Estate_Analysis
# =KDYŽ(NEBO(Tabulka1[[#Tento řádek];[Sloupec8]]<>"";Tabulka1[[#Tento řádek];[Sloupec15]]<>"");1;0)
