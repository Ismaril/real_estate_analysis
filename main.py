import os
import scraper
import plotting
import data_cleaning
import constants as c


def main():
    if not os.listdir(c.LINKS):
        scraper.site_map_scraping()
        data_cleaning.delete_sitemap_files()
        data_cleaning.clean_raw_data()

    scraper.features_scraping(batch_size=1000,
                              max_nr_samples=None,
                              failed_request_limit=20)
    data_cleaning.clean_feature_data()
    data_cleaning.aggregate_feature_data()
    data_cleaning.archive_dataset()
    data_cleaning.delete_data()
    plotting.plot_all()


if __name__ == '__main__':
    main()
