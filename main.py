import scraper
import data_cleaning

if __name__ == '__main__':
    # scraper.site_map_scraping(scraper.chrome_driver(headless=False))
    # scraper.delete_unwanted_sitemap_files()
    # data_cleaning.data_cleaner()
    scraper.properties_scraping(driver=scraper.chrome_driver(headless=True),
                                dataset="links_to_properties_cleaned.csv",
                                batch_size=1000,
                                max_nr_samples=1000)
