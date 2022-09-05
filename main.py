import data_cleaning
import scraper
import plotting


def main(scrape_sitemaps=True,
         scrape_features=True,
         clean_features=True,
         plot_data=True):

    if scrape_sitemaps:
        scraper.site_map_scraping(scraper.chrome_driver(headless=False))
        data_cleaning.delete_unwanted_sitemap_files()
        data_cleaning.clean_raw_data()

    if scrape_features:
        scraper.features_scraping(driver=scraper.chrome_driver(headless=True),
                                  batch_size=1_000,
                                  max_nr_samples=None)

    if clean_features:
        data_cleaning.concatenate_batches()
        data_cleaning.clean_feature_data()
        data_cleaning.aggregate_feature_data()
        data_cleaning.archive_datasets()
        data_cleaning.delete_all_batches()

    if plot_data:
        plotting.plot_all()


if __name__ == '__main__':
    main(scrape_sitemaps=True,
         scrape_features=False,
         clean_features=False,
         plot_data=False)
