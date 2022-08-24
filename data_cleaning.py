import os
import re
import pandas as pd
import constants as c
from collections import Counter


def clean_raw_data():
    """Filter all links to websites that are not relevant for us"""
    data = pd.read_csv(c.PROPERTIES_LINKS)
    data.dropna(inplace=True)
    data.rename(columns={c.LOC: c.LINK}, inplace=True)

    # locate links to properties, break out once the pattern of links changes
    #    (properties on the site map are then followed by some not relevant pages)
    for i, link in enumerate(data[c.LINK][:-1]):
        try:
            match = re.search("/.\d+", link)
            match.group()
        except AttributeError:
            data = data[:i]  # cut off following webpages that are not relevant
            break

    # filter out duplicate webpages, site map has the same web pages
    #     2x - CZ and EN language
    filter_duplicate_links = [False, True] * (len(data[c.LINK]) // 2)
    filter_col = "filter"
    data[filter_col] = filter_duplicate_links
    data = data.loc[data[filter_col] == False]

    # find the property type and type of sale
    property_type = []
    type_of_sale = []
    property_id = []
    for link in data[c.LINK]:
        split = link.split("/")
        property_type.append(split[5])
        type_of_sale.append(split[4])
        property_id.append(split[-1])

    # get some feeling of property type statistics
    property_type_stats = Counter(property_type)
    print("Summary of property types: ",
          property_type_stats.most_common())

    # filter out next unwanted stuff
    property_type_col = "Property type:"
    sale_type_col = "Type of sale:"
    data[property_type_col] = property_type
    data[sale_type_col] = type_of_sale

    filter_ = (data[property_type_col] != c.COMMERCIAL) & \
              (data[property_type_col] != c.OTHERS) & \
              (data[sale_type_col] != c.RENT) & \
              (data[sale_type_col] != c.AUCTION)
    data = data.loc[filter_]

    data.drop([c.UNNAMED,
               c.LASTMOD,
               filter_col,
               property_type_col,
               sale_type_col],
              axis=1, inplace=True)

    # save cleaned dataset
    data: pd.DataFrame
    data.to_csv(c.PROPERTIES_CLEANED_LINKS)
    print(data)


def concatenate_batches():
    result = pd.DataFrame()
    for file in os.listdir("batches"):
        result = pd.concat([result, pd.read_csv(f"batches/{file}")])
    result.drop([c.UNNAMED], inplace=True, axis=1)
    result.to_csv(c.FEATURES)
    print("Batches concatenated")


def clean_feature_data():
    data = pd.read_csv(c.FEATURES)
    # todo: add more columns
    data.drop([c.UNNAMED,
               c.LINK,
               c.DATETIME_SCRAPED],
              inplace=True, axis=1)

    # filter data where both of these are missing
    # (also should remove duplicates from 'rescraping')
    filter_ = ~(pd.isna(data[c.TOTAL_PRICE])) | ~(pd.isna(data[c.ON_SALE]))
    data = data.loc[filter_]

    # rename towns only to single word
    data[c.LOCATION] = data[c.LOCATION].str.split()
    data[c.LOCATION] = data[c.LOCATION].str[0]

    print(data.head())
    # todo: delete all data from batches
    pass


def readable_time(seconds: int):
    """Convert seconds into hh:mm:ss """
    mins_secs = divmod(seconds, 60)
    hrs_mins = divmod(mins_secs[0], 60)
    seconds = mins_secs[1]
    minutes = hrs_mins[1]
    hours = hrs_mins[0]
    result = ""

    for digit in (hours, minutes, seconds):
        result += f"0{digit} :" if digit < 10 else f"{digit} :"
    pre_result = list(result[:-1])
    pre_result[2] = "h"
    pre_result[6] = "m"
    pre_result[10] = "s"
    result = "".join(pre_result)

    return result


def prepare_for_rescraping():
    data = pd.read_csv(c.FEATURES)
    filter_ = (pd.isna(data[c.TOTAL_PRICE])) & (pd.isna(data[c.ON_SALE]))
    data = data.loc[filter_][c.LINK]
    data.to_csv("links_to_properties/links_to_properties_unsuccessful.csv")
    return pd.read_csv("links_to_properties/links_to_properties_unsuccessful.csv")


def delete_all_batches():
    pass


def delete_unwanted_sitemap_files():
    """
    Delete all 'sitemap' files in downloads directory
    :return: None
    """
    for file in os.listdir(c.DOWNLOADS):
        if file.startswith(c.SITEMAP):
            os.remove(f"{c.DOWNLOADS}/{file}")