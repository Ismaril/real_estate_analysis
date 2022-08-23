import os
import time
import random
import send_mail
import numpy as np
import pandas as pd
import data_cleaning
import requests as requests
import patoolib  # work with zipped files

from selenium import common
from selenium import webdriver
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
]
DRIVER_ADDRESS = "chrome_driver/chromedriver.exe"
SITE_MAP = "https://www.sreality.cz/sitemap.xml"
DOWNLOADS = "C:/Users/lazni/Downloads"


def chrome_driver(headless=True, driver_address=DRIVER_ADDRESS):
    # with this option set to True desktop chrome application will not pop up
    options = webdriver.ChromeOptions()
    options.headless = headless
    options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')  # set useragent

    # this driver will act as a new desktop window of chrome (if not headless) and will load dynamic
    #   website, before it is scraped. Dynamic websites cannot be scraped with python requests. Lots of
    #   info would miss otherwise.
    driver = webdriver.Chrome(driver_address, options=options)

    # skip the page request after set time to wait
    driver.set_page_load_timeout(time_to_wait=15)
    return driver


def site_map_scraping(driver):
    """
    :param driver: insert driver that's gonna operate as artificial web-browser

    Scrape xml files that contain links to all web pages. Extract all links and put them
    into complete dataset. This function basically gets the whole sitemap.
    """
    xml_docs = pd.read_xml(
        requests.get(SITE_MAP,
                     headers={"User-Agent": random.choice(USER_AGENTS)}).text
    )["loc"]

    for url in xml_docs:
        # get url of a xml containing links to websites of all given properties, at a time of
        #    creation of this file there were like 5 links
        driver.get(url)
        time.sleep(4)

    # exit the artificial browser
    driver.quit()

    nr_of_xml_docs = len(xml_docs)
    all_links_dataframe = pd.DataFrame()
    for i in range(nr_of_xml_docs):
        # unzip all files that contain links to properties
        patoolib.extract_archive(f"{DOWNLOADS}/sitemap{i + 1}.xml.gz",
                                 outdir="C:/Users/lazni/Downloads")

        # read files that contain links to properties and put them all in a huge dataset
        all_links_dataframe = pd.concat([all_links_dataframe,
                                         pd.read_xml(f"{DOWNLOADS}/sitemap{i + 1}.xml")])

    # save df
    pd.DataFrame(all_links_dataframe).to_csv("links_to_properties/links_to_properties.csv")


def delete_unwanted_sitemap_files():
    """
    Delete all 'sitemap' files in downloads directory
    :return: None
    """
    for file in os.listdir(DOWNLOADS):
        if file.startswith("sitemap"):
            os.remove(f"{DOWNLOADS}/{file}")


def properties_scraping(driver,
                        dataset,
                        batch_size=1000,
                        max_nr_samples=None,
                        failed_request_limit=20):
    """

    :param driver: insert driver that's gonna operate as artificial web-browser
    :param dataset: dataset that contains links to websites
    :param batch_size: (number of rows) downloaded data will be saved in batches in case of lost connection
    :param max_nr_samples: set upper index as a filter of the dataset
    :param failed_request_limit: number of failed requests in a row to break the loop
    :return: *.csv
    """

    start_session = time.perf_counter()
    batches = os.listdir("C:/Users/lazni/PycharmProjects/Real_Estate_Analysis/batches")
    rescraping = False

    # if some data were already downloaded, continue based on last downloaded index.
    if batches:
        last_completed_index = int(max(int(item.split(".")[0]) for item in batches))
        data = pd.read_csv(dataset)

        # try to scrape unsuccessfully scraped links again if we scraped the whole dataset already
        # TODO: try to figure out why some data is not scraped even though it is present in webpage
        if data.shape[0] == last_completed_index:
            data_cleaning.concatenate_batches()
            # Todo: delete all files in batches
            data_cleaning.prepare_for_rescraping()
            rescraping = True

        # filter the dataset which contains links to webpages and continue scraping
        else:
            data = data[last_completed_index + 1:max_nr_samples]

    # scraping starts for the first time, and therefore start from the beginning of the
    #    source dataset which contains links to webpages
    else:
        data = pd.read_csv(dataset)[:max_nr_samples]

    final_dataframe = pd.DataFrame()
    average_iter_time = []
    timed_out_requests = 0
    timed_out_requests_total = 0

    # iterate through webpages and scrape
    # TODO: possibly remove zip data id
    for index_session, (link, id_) in enumerate(zip(data["loc"], data["id"])):
        start = time.perf_counter()

        # break out of loop if x requests are timed out, could be caused by lost internet connection,
        #     site currently unavailable or high ping
        if timed_out_requests == failed_request_limit:
            send_mail.send_email(
                subject=f"Scrapping stopped due to {failed_request_limit} timed  out requests in a row."
            )
            break

        # index_all_data = data.index[data["id"] == id_].tolist()[0] # todo: might delete this
        index_all_data = data.index[data["loc"] == link].tolist()[0]

        # get url of a desired website
        try:
            driver.get(link)
            driver.delete_all_cookies()
        # request timed out
        except common.exceptions.TimeoutException:
            print("Request timed out", "!" * 60, sep="\n")
            timed_out_requests += 1
            timed_out_requests_total += 1
            continue

        timed_out_requests = 0

        # Beautiful soup perhaps gonna return "MarkupResemblesLocatorWarning" but html is actually inputted
        #    inside, so it is probably false alarm
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # get labels (generally for all properties) from a given website
        #     Example: <label class="param-label ng-binding">Celková cena:</label>
        elements = soup.find_all("label", class_="param-label ng-binding")
        labels = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            labels.append(item.text)

        # get all the information that corresponds to a given property label on the website
        # Example: <span ng-if="item.type != 'link'" class="ng-binding ng-scope">5&nbsp;799&nbsp;000 Kč
        #     za nemovitost</span>
        elements = soup.find_all("span", class_="ng-binding ng-scope")
        information = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            information.append(item.text)

        # put all labels and all info regarding a given reality into and prepare them as a row
        dict_ = {}
        link_split = link.split("/")

        dict_["Link:"] = link
        # dict_["Id:"] = id_
        dict_["Nemovitost:"] = link_split[5]
        dict_["Typ:"] = link_split[6]
        location = link_split[7]
        location_split = location.split("-")
        dict_["Lokace:"] = f"{location_split[0].title()} {location_split[1]} {location_split[2]}"
        dict_["Řádek vytvořen:"] = time.ctime()

        valid_columns = ["Celková cena:", "Stavba:", "Stav objektu:",
                         "Vlastnictví:", "Zlevněno:", "Původní cena:",
                         "Plocha zastavěná:", "Užitná plocha:", "Plocha pozemku:",
                         "Plocha zahrady:"]
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
              f"Iter time: {iteration_time:.2f} sec\n")

        # saving rescraped data and end feature scraping for good
        if rescraping and index_session == data.shape[0] - 1:
            final_dataframe.to_csv(f"batches/rescraped.csv", encoding="UTF-8")
            break

        # save scraped data in batches based on specified batch size
        elif (index_session and index_session % batch_size == 0) or index_session == data.shape[0] - 1:
            print(f"Saving batch. Completed iterations total: {index_all_data}", end=f"\n{'-' * 60}\n")
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
    print(f"Scraping features took this session: {scraping_time:.2f} sec")
    print(f"Average time of all iterations: {np.mean(average_iter_time)} sec",
          "#" * 60,
          sep="\n")
    send_mail.send_email(subject="Scraping completed")

# C:\Users\lazni\PycharmProjects\Real_Estate_Analysis
