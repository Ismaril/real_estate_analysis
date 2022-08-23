import scraper
import data_cleaning


def main(scrape_sitemaps=True,
         scrape_features=True,
         clean_features=True):

    if scrape_sitemaps:
        scraper.site_map_scraping(scraper.chrome_driver(headless=False))
        scraper.delete_unwanted_sitemap_files()
        data_cleaning.clean_raw_data()

    if scrape_features:
        scraper.properties_scraping(driver=scraper.chrome_driver(headless=True),
                                    dataset="links_to_properties/links_to_properties_cleaned.csv",
                                    batch_size=1000,
                                    max_nr_samples=None)

    if clean_features:
        data_cleaning.concatenate_batches()


if __name__ == '__main__':
    main(scrape_sitemaps=False,
         scrape_features=True,
         clean_features=False)

# todo: make some glossary to make repeating strings constants
