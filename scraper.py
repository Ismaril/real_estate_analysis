import random
import time
import pandas as pd
import requests as requests
from bs4 import BeautifulSoup
from selenium import webdriver
import patoolib  # work with zipped files

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
]
DRIVER_ADDRESS = "C:/Users/lazni/Downloads/chromedriver.exe"
SITE_MAP = "https://www.sreality.cz/sitemap.xml"


class Scraper:
    @staticmethod
    def _chrome_driver(headless=True, driver_address=DRIVER_ADDRESS):
        # with this option set to True desktop chrome application will not pop up
        options = webdriver.ChromeOptions()
        options.headless = headless

        # this driver will act as a new desktop window of chrome (if not headless) and will load dynamic
        #   website, before it is scraped. Dynamic websites cannot be scraped with python requests. Lots of
        #   info would miss otherwise.
        driver = webdriver.Chrome(driver_address, options=options)
        return driver

    @staticmethod
    def site_map(driver=None):
        xml_docs = pd.read_xml(
            requests.get(SITE_MAP, headers={"User-Agent": random.choice(USER_AGENTS)}).text
        )["loc"]
        for url in xml_docs:
            # get url of a xml containing links to websites of all given properties
            driver.get(url)
            time.sleep(4)

        # exit the artificial browser
        driver.quit()

        nr_of_xml_docs = len(xml_docs)

        for i in range(nr_of_xml_docs):
            path = "C:/Users/lazni/Downloads"
            patoolib.extract_archive(f"{path}/sitemap{i + 1}.xml.gz",
                                     outdir="C:/Users/lazni/Downloads")

            with open(f"{path}/sitemap{i + 1}.xml", "r") as file:
                data = file.read()
                data = pd.read_xml(data)
                data.to_csv(f"{path}/urls_{i + 1}.csv")

    @staticmethod
    def scrapping(driver=None):
        # get url of a desired website
        url = "https://www.sreality.cz/detail/prodej/byt/3+kk/praha-zabehlice-hlavni/697932"
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "lxml")

        # get labels (generally for all properties) from a given website
        elements = soup.find_all("label", class_="param-label ng-binding")
        # Example: <label class="param-label ng-binding">Celková cena:</label>
        labels = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            labels.append(item.text)

        # get all the information that corresponds to a given property label on the website
        elements = soup.find_all("span", class_="ng-binding ng-scope")
        # Example: <span ng-if="item.type != 'link'" class="ng-binding ng-scope">5&nbsp;799&nbsp;000 Kč za nemovitost</span>
        information = []
        for item in elements:
            item = BeautifulSoup(item.text, 'html.parser')
            information.append(item.text)

        # visualise the outpu
        for label, info in zip(labels, information):
            print(f"{label} {info}")

        # exit the artificial browser
        driver.quit()

    @classmethod
    def save_to_csv(cls):
        pass

    @classmethod
    def delete_unwanted_files(cls):
        pass

    @classmethod
    def main(cls):
        cls.site_map(cls._chrome_driver(headless=False))


# zavorky nebo ne?
Scraper().main()
