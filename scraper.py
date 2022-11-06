import os
import time
import random
import requests
import utilities
import numpy as np
import pandas as pd
import constants as c
import patoolib  # work with zipped files

from selenium import common
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def chrome_driver(is_headless: bool = True,
                  driver_address=c.DRIVER_ADDRESS) -> webdriver.Chrome:
    """
    This driver will act as a new desktop window of chrome (if not headless)
    and will load dynamic website, before it is scraped.
    Dynamic websites cannot be scraped with python requests, meaning page
    would not load all it's content.

    :param is_headless: If True, desktop chrome application will not pop up.
    :param driver_address: Path to driver.

    :return: webdriver.Chrome
    """

    options = webdriver.ChromeOptions()
    options.headless = is_headless
    options.add_argument(f'user-agent={random.choice(c.USER_AGENTS)}')  # Set user agent.

    driver = webdriver.Chrome(driver_address, options=options)

    return driver


def site_map_scraping():
    """
    Scrape xml files that contain links to all web pages.
    Extract all links and put them into one dataset.
    This function gets the complete sitemap.

    :return: None
    """
    driver = chrome_driver(is_headless=False)

    # The page has site map divided into multiple links.
    # Read directly from website.
    xml_docs = pd.read_xml(
        requests.get(c.SITE_MAP,
                     headers={"User-Agent": random.choice(c.USER_AGENTS)}).text
    )[c.LOC]

    # Get url of a xml containing links to websites of all given properties,
    #    at a time of creation of this file there were 5 links. (5 files)
    # Files that this downloads need to be later extracted.
    for url in xml_docs:
        driver.get(url)
        time.sleep(4)

    # Exit the artificial browser.
    driver.quit()

    nr_of_xml_docs = len(xml_docs)
    assert nr_of_xml_docs, "Xml sitemaps not reached."
    all_links_df = pd.DataFrame()
    for i in range(nr_of_xml_docs):
        # Unzip all files that contain links to properties.
        patoolib.extract_archive(f"{c.DOWNLOADS}/{c.SITEMAP}{i + 1}.xml.gz",
                                 outdir=c.DOWNLOADS)

        # Read files that contain links to properties and put them all in one dataset.
        all_links_df = pd.concat(
            [all_links_df,
             pd.read_xml(f"{c.DOWNLOADS}/{c.SITEMAP}{i + 1}.xml")]
        )

    # Save df.
    all_links_df.to_csv(c.PROPERTIES, index=False)


def features_scraping(batch_size: int = 1000,
                      max_nr_samples: int = None,
                      failed_request_limit: int = 20,
                      mail_notification: bool = True):
    """
    Scrape features of a given property.
    Once a given number of properties has been scraped, save as a csv batch.

    :param batch_size: Number of rows to be appended in one batch to csv.
    :param max_nr_samples: Condition to stop scraping at a given index.
    :param failed_request_limit: Number of failed requests in a row to break the loop and stop scraping.
    :param mail_notification: Send out mails with progress info.

    :return: None
    """

    # Measure time performance of complete scraping process.
    session_time = utilities.Performance()
    session_time.start()

    driver = chrome_driver(is_headless=True)
    features_exist = os.listdir(c.FEATURES)
    data = pd.read_csv(c.PROPERTIES_CLEANED)
    batch_df = pd.DataFrame()
    average_iter_time = []
    timed_out_requests = 0
    timed_out_requests_total = 0

    # If some data were already downloaded, continue based on last downloaded index.
    if features_exist:
        with open("completed_index.txt", "r") as file:
            last_completed_index = int(file.read())

        # Filter the dataset which contains links to webpages and continue scraping.
        data = data[last_completed_index + 1:max_nr_samples]

    # Scraping starts for the first time, and therefore start from the beginning of the
    #    source dataset which contains links to webpages.
    else:
        data = data[:max_nr_samples]

    # Iterate through webpages and scrape.
    for index_session, link in enumerate(data[c.LINK]):

        # Measure time performance of iteration
        iteration_time = utilities.Performance()
        iteration_time.start()

        # Completed rows of the whole link dataset.
        index_all_data = data.index[data[c.LINK] == link].tolist()[0]

        # Break out of loop if x requests are timed out, possibly by lost
        #     internet connection, site unavailable or high ping etc...
        if timed_out_requests == failed_request_limit:
            utilities.send_email(
                subject=f"Scrapping stopped due to {failed_request_limit}"
                        f"timed  out requests in a row."
            )
            break

        # Get a desired website
        try:
            driver.get(link)

            # With WebDriverWait program will wait till the specified x path is found in a given webpage.
            # This means that the page has content and we will wait till javascript loads.
            # Previously I encountered a problem where data were present in the page, but nothing was scraped
            x_path = '//*[@id="page-layout"]/div[2]/div[3]/div[3]/div/div/div/div/div[4]/h1/span/span[1]'
            WebDriverWait(driver, 6).until(ec.presence_of_element_located((By.XPATH, x_path)))

            driver.delete_all_cookies()

        # Request timed out.
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

        # If no problem encountered during scraping a page:
        timed_out_requests = 0

        # Beautiful soup perhaps gonna return "MarkupResemblesLocatorWarning"
        #    but html is actually inputted inside, so it is probably false alarm
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Get labels (generally for all properties) from a given website.
        # Example: <label class="param-label ng-binding">Celková cena:</label>
        elements = soup.find_all("label", class_="param-label ng-binding")
        labels = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            labels.append(item.text)

        # Get all the information that corresponds to a given property label on the website.
        # Example: <span ng-if="item.type != 'link'" class="ng-binding ng-scope">5&nbsp;
        #     799&nbsp;000 Kč za nemovitost</span>
        elements = soup.find_all("span", class_="ng-binding ng-scope")
        features = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            features.append(item.text)

        # Find town and state based on class. (there is only one element per page)
        elements = soup.find_all("span", class_="location-text ng-binding")
        location = ""
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            location += item.text

        # Put all labels and all features regarding a given reality into dict and prepare them as a row.
        # Note, that we also take location again (here directly from link), due to inconsistency
        #   of string format in the webpage.
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

        # assign each feature to correct column name / dict key.
        for label, feature in zip(labels, features):
            if label in valid_columns:
                dict_[label] = feature

        # Add all scraped data as a new row into dataframe.
        new_row = pd.DataFrame(dict_, index=[index_session])
        batch_df = pd.concat([batch_df, new_row], ignore_index=True)

        # Iteration statistics. (Serves as a visualisation during scraping)
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

        # Save scraped data in batches based on specified batch size.
        if (index_session and index_session % batch_size == 0) \
                or index_session == data.shape[0] - 1:

            # Save last completed iteration.
            with open("completed_index.txt", "w") as file:
                file.write(str(index_all_data))

            # Concatenate everything already scraped with current batch.
            utilities.csv_concatenation(main_file=c.FEATURES_ALL,
                                        new_data=batch_df)
            batch_df = pd.DataFrame()

            if mail_notification:
                utilities.send_email(
                    subject=f"Completed rows: {index_all_data}",
                    body=f"Session is running {utilities.readable_time(int(session_time.end()))}\n"
                         f"Average time of all iterations: {np.mean(average_iter_time):.2f} sec\n"
                         f"Timed out requests: {timed_out_requests_total}")
                print(f"Saving batch. Completed iterations total: {index_all_data}\n",
                      end=c.SEPARATOR)

    # Exit the artificial browser.
    driver.quit()

    # Session statistics.
    utilities.send_email(subject="Scraping completed", body="")
    print(f"Scraping features took this session: {session_time.end():.2f} sec",
          f"Average time of all iterations: {np.mean(average_iter_time)} sec",
          sep="\n",
          end=c.SEPARATOR)
