import os
import re
import datetime
import numpy as np
import pandas as pd
import constants as c


def clean_raw_data():
    """
    Filter all links to websites that are not relevant for us

    :returns: None
    """
    data = pd.read_csv(c.PROPERTIES)
    data.dropna(inplace=True)
    data.rename(columns={c.LOC: c.LINK}, inplace=True)

    # locate links to properties, break out once the pattern of links changes
    #    (properties on the site map start from the beginning and are then
    #     followed by some not relevant pages)
    for i, link in enumerate(data[c.LINK]):
        try:
            match = re.search("/.\d+", link)
            match.group()
        except AttributeError:
            data = data[:i]  # cut off following webpages that are not relevant
            break

    # filter out duplicate webpages, site map has the same web pages
    #     2x - CZ and EN language. This means filter every other row
    filter_col = "filter"
    data[filter_col] = [False, True] * (len(data[c.LINK]) // 2)
    data = data.loc[data[filter_col] == False]

    # filter out links so that we have only private properties and only for sale
    property_type = "Property type:"
    sale_type = "Type of sale:"
    link_split = "link_split"
    data[link_split] = data[c.LINK].str.split("/")
    data[property_type] = data[link_split].str[5]
    data[sale_type] = data[link_split].str[4]

    filter_ = (data[property_type] != c.COMMERCIAL) & \
              (data[property_type] != c.OTHERS) & \
              (data[sale_type] != c.RENT) & \
              (data[sale_type] != c.AUCTION)
    data = data.loc[filter_]

    data.drop([c.LASTMOD,
               link_split,
               filter_col,
               property_type,
               sale_type],
              axis=1,
              inplace=True)

    # save cleaned dataset
    data.to_csv(c.PROPERTIES_CLEANED, index=False)

    print(data)


def concatenate_batches():
    """
    Concatenate all batches that were downloaded during feature
    scraping, into complete dataset

    :returns: None
    """
    result = pd.DataFrame()
    for file in os.listdir(c.BATCHES):
        result = pd.concat([result, pd.read_csv(f"{c.BATCHES}/{file}")])
    result.drop([c.UNNAMED], inplace=True, axis=1)  # todo: might delete?
    result.to_csv(c.FEATURES)
    print("Batches concatenated")


def clean_feature_data():
    """
    Clean and manipulate downloaded raw features into the state that can be
    aggregated later

    :returns: None
    """
    data = pd.read_csv(c.FEATURES)

    # filter data where total price or sale price are missing
    filter_ = ~(pd.isna(data[c.TOTAL_PRICE])) | ~(pd.isna(data[c.ON_SALE]))
    data = data.loc[filter_]

    # drop first unwanted stuff
    data.drop_duplicates(subset=[c.LINK], inplace=True)
    data.drop([c.UNNAMED,  # todo: check this
               c.LINK,
               c.DATETIME_SCRAPED], #todo: also might delete?
              inplace=True,
              axis=1)
    for column in [c.LAND_AREA, c.USABLE_AREA, c.GARDEN_AREA]:
        data = data.loc[data[column] != 1.0]

    # drop empty cells in usable area in flats & houses
    filter_ = (data[c.PROPERTY].isin([c.FLAT, c.HOUSE])) \
              & (pd.isna(data[c.USABLE_AREA]))
    data = data.loc[~filter_]

    # drop empty cells in usable area in houses & lands
    filter_ = data[c.PROPERTY].isin([c.LAND, c.HOUSE]) \
              & (pd.isna(data[c.LAND_AREA]))
    data = data.loc[~filter_]

    # todo: this I should update based on scraping of different source of cities
    # rename towns to single word, filter towns
    data[c.LOCATION] = data[c.LOCATION].str.split()
    data[c.LOCATION] = data[c.LOCATION].str[0]
    data[c.LOCATION] = data[c.LOCATION].astype(str)

    filter_ = data[c.LOCATION].apply(lambda x: True if x.isalpha() else False)
    data = data.loc[filter_]

    filter_ = data[c.LOCATION].notna() \
              & data[c.LOCATION].apply(lambda x: True if x != "nan" else False) \
              & ~data[c.LOCATION].isin(c.NOT_VALID_TOWNS)
    data = data.loc[filter_]

    # format price columns to floats (from strings)
    # not possible to apply to all columns at once because pd string
    #   function works only on series
    for column in [c.TOTAL_PRICE, c.ON_SALE, c.FORMER_PRICE]:
        data[column] = data[column].str.split("Kč")
        data[column] = data[column].str[0]
        data[column] = data[column].str.replace(r'\s', '', regex=True)
        data[column] = data[column].str.replace(r'\D', '', regex=True)
        data[column] = data[column].astype(float)

    # put together total prices and prices after sale
    data[c.TOTAL_PRICE] = np.where(data[c.TOTAL_PRICE].notna(),  # condition
                                   data[c.TOTAL_PRICE],  # True
                                   data[c.ON_SALE])  # False
    data[c.SALE] = data[c.FORMER_PRICE] - data[c.ON_SALE]

    # create a new column where is summed complete usable area
    # [condition, name of new column] = column
    data.loc[(data[c.PROPERTY] == c.FLAT) & data[c.GARDEN_AREA].isna(), c.TOTAL_AREA] = data[c.USABLE_AREA]
    data.loc[(data[c.PROPERTY] == c.FLAT) & data[c.GARDEN_AREA].notna(), c.TOTAL_AREA] = data[c.USABLE_AREA] + data[c.GARDEN_AREA]
    data.loc[(data[c.PROPERTY] == c.HOUSE), c.TOTAL_AREA] = data[c.USABLE_AREA] + data[c.LAND_AREA]
    data.loc[(data[c.PROPERTY] == c.LAND), c.TOTAL_AREA] = data[c.LAND_AREA]

    # create column of m2/price
    data[c.PRICE_M2] = data[c.TOTAL_PRICE] / data[c.TOTAL_AREA]
    data[c.PRICE_M2] = data[c.PRICE_M2].astype(int)
    print(data.info())
    data.to_csv(c.FEATURES_CLEANED)


def aggregate_feature_data():
    """
    Aggregate feature data into the state that can be used
    for plotting

    :returns: None
    """
    data = pd.read_csv(c.FEATURES_CLEANED)
    new_data = pd.DataFrame()

    # 0: aggregate Prague
    # 1: aggregate 9 biggest cities excluding prague
    # 2: aggregate rest of the republic (10 biggest cities excluded)
    for i in range(3):
        for type_ in c.TYPES_FLAT + c.TYPES_HOUSE + c.TYPES_LAND:
            if not i:
                filter_ = (data[c.LOCATION] == c.TOWNS_PRAGUE[0])\
                          & (data[c.TYPE] == type_)
            elif i == 1:
                filter_ = data[c.LOCATION].isin(c.TOWNS_TOP9)\
                          & (data[c.TYPE] == type_)
            else:
                filter_ = ~data[c.LOCATION].isin(c.TOWNS_PRAGUE + c.TOWNS_TOP9)\
                          & (data[c.TYPE] == type_)

            data_filtered = data.loc[filter_]

            # compute median of a given type of properties in a given area
            price = data_filtered[c.PRICE_M2].median()

            if not i:
                new_data[f"{c.SHORT_PRAGUE} {type_}"] = [price]
            elif i == 1:
                new_data[f"{c.SHORT_TOP9} {type_}"] = [price]
            else:
                new_data[f"{c.SHORT_REST} {type_}"] = [price]
    new_data[c.PERIOD] = [datetime.date.today()]

    try:
        prices_all_months = pd.read_csv(c.RESULTS)
        prices_all_months = pd.concat([prices_all_months, new_data])
        prices_all_months.to_csv(c.RESULTS, index=False)
    except pd.errors.EmptyDataError:
        new_data.to_csv(c.RESULTS, index=False)


def readable_time(seconds: int) -> str:
    """
    Convert seconds into hh:mm:ss

    :returns: str
    """
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


# todo: possible do delete in next scraping?
def prepare_for_rescraping():
    data = pd.read_csv(c.FEATURES)
    filter_ = (pd.isna(data[c.TOTAL_PRICE])) & (pd.isna(data[c.ON_SALE]))
    data = data.loc[filter_][c.LINK]
    data.to_csv("links_to_properties/links_to_properties_unsuccessful.csv")
    return pd.read_csv("archive/links_to_properties_unsuccessful.csv")


def archive_datasets():
    """
    Rename feature dataset and move it into new location - archive it.

    :return: None
    """
    file_number = len(os.listdir(c.ARCHIVE))

    # renames and also moves the file to new location
    os.rename(c.FEATURES, f"{c.ARCHIVE}/{file_number}.csv")


def delete_all_batches():
    """
    Delete all files that were formerly downloaded as
    batches of features from the next

    :return: None
    """
    for file in os.listdir(c.BATCHES):
        os.remove(f"{c.BATCHES}/{file}")

    os.remove(c.FEATURES_CLEANED)


def delete_unwanted_sitemap_files():
    """
    Delete all 'sitemap' files in downloads directory

    :returns: None
    """
    for file in os.listdir(c.DOWNLOADS):
        if file.startswith(c.SITEMAP):
            os.remove(f"{c.DOWNLOADS}/{file}")
