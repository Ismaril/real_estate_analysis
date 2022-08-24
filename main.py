import scraper
import data_cleaning
import constants as c


def main(scrape_sitemaps=True,
         scrape_features=True,
         clean_features=True):

    if scrape_sitemaps:
        scraper.site_map_scraping(scraper.chrome_driver(headless=False))
        data_cleaning.delete_unwanted_sitemap_files()
        data_cleaning.clean_raw_data()

    if scrape_features:
        scraper.properties_scraping(driver=scraper.chrome_driver(headless=True),
                                    dataset=c.PROPERTIES_CLEANED_LINKS,
                                    batch_size=1_000,
                                    max_nr_samples=None)

    if clean_features:
        data_cleaning.concatenate_batches()


if __name__ == '__main__':
    main(scrape_sitemaps=False,
         scrape_features=True,
         clean_features=False)