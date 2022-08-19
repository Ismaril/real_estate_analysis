import os
import time
import random
import numpy as np
import pandas as pd
import requests as requests
import patoolib  # work with zipped files
from selenium import common
from bs4 import BeautifulSoup
from selenium import webdriver

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
    pd.DataFrame(all_links_dataframe).to_csv("links_to_properties.csv")


def delete_unwanted_sitemap_files():
    for file in os.listdir(DOWNLOADS):
        if file.startswith("sitemap"):
            os.remove(f"{DOWNLOADS}/{file}")


def properties_scraping(driver, dataset, batch_size=1000, max_nr_samples=None):
    start_global = time.perf_counter()
    # if some data were already downloaded, continue based on last downloaded index
    batches = os.listdir("C:/Users/lazni/PycharmProjects/Real_Estate_Analysis/batches")
    if batches:
        last_completed_index = int(max(int(item.split(".")[0]) for item in batches))
        data = pd.read_csv(dataset)[last_completed_index:max_nr_samples]

    # scraping starts for the first time
    else:
        data = pd.read_csv(dataset)[:max_nr_samples]

    final_dataframe = pd.DataFrame()
    average_iter_time = []

    for index_session, (link, id_) in enumerate(zip(data["loc"], data["id"])):
        start = time.perf_counter()
        index_all_data = data.index[data["id"] == id_].tolist()[0]

        try:
            # get url of a desired website
            driver.get(link)
            driver.delete_all_cookies()
        except common.exceptions.TimeoutException:
            print("Request timed out", "!" * 60, sep="\n")
            continue

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

        # put all labels and all info regarding a given reality into final dataset as a new row
        dict_ = {}

        link_split = link.split("/")
        dict_["link"] = link
        dict_["id"] = id_
        dict_["Nemovitost:"] = link_split[5]
        dict_["Typ:"] = link_split[6]
        location = link_split[7]
        location_split = location.split("-")
        dict_["Lokace:"] = location_split[0].title()
        for label, info in zip(labels, information):
            dict_[label] = info

        new_row = pd.DataFrame(dict_, index=[index_session])
        final_dataframe = pd.concat([final_dataframe, new_row], ignore_index=True)
        end = time.perf_counter()

        iteration_time = end - start
        average_iter_time.append(iteration_time)
        print(f"Iter curr session {index_session}, "
              f"Iter total: {index_all_data}, "
              f"Iter time: {iteration_time:.2f} sec")

        if index_session % batch_size == 0 or index_session == data.shape[0] - 1:
            print(f"Saving batch. Completed iterations total: {index_all_data}", end=f"\n{'-' * 60}\n")
            final_dataframe.to_csv(f"batches/{index_all_data}.csv", encoding="UTF-8")
            final_dataframe = pd.DataFrame()

    # exit the artificial browser
    driver.quit()
    end_global = time.perf_counter()
    scraping_time = end_global - start_global
    print(f"Scraping features took this session: {scraping_time:.2f} sec")
    print(f"Average time of all iterations: {np.mean(average_iter_time)} sec",
          "#" * 60,
          sep="\n")


# C:\Users\lazni\PycharmProjects\Real_Estate_Analysis
