import os
import re
import datetime
import numpy as np
import pandas as pd
import constants as c
import utilities


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


def clean_feature_data():
    """
    Clean and manipulate downloaded raw features into the state that can be
    aggregated later

    :returns: None
    """
    data = pd.read_csv(c.FEATURES_ALL)

    # filter data where total price or sale price are missing
    filter_ = ~(pd.isna(data[c.TOTAL_PRICE])) | ~(pd.isna(data[c.ON_SALE]))
    data = data.loc[filter_]

    # drop first unwanted stuff
    data.drop_duplicates(subset=[c.LINK], inplace=True)
    for column in [c.LAND_AREA, c.USABLE_AREA, c.GARDEN_AREA]:
        data = data.loc[data[column] != 1.0]
    # todo: write this in a general way through regex ...not statically
    filter_ = data[c.TOTAL_PRICE] == " Kč za nemovitost"
    data = data.loc[~filter_]

    # drop empty cells in usable area in flats & houses
    filter_ = (data[c.PROPERTY].isin([c.FLAT, c.HOUSE])) \
              & (pd.isna(data[c.USABLE_AREA]))
    data = data.loc[~filter_]

    # drop empty cells in land area in houses & lands
    filter_ = data[c.PROPERTY].isin([c.LAND, c.HOUSE]) \
              & (pd.isna(data[c.LAND_AREA]))
    data = data.loc[~filter_]

    # this block written in plain python (would it be possible with pandas only?)
    towns = []
    is_foreign = []
    for location, location2 in zip(data[c.LOCATION], data[c.LOCATION2]):

        # let top 9 cities have their full name
        for town in c.TOWNS_TOP9:
            location_merged = "".join(location.split("-")).lower()
            if town in location_merged:
                towns.append(town)
                break
        else:
            towns.append(location)

        # locate foreign countries
        for country in c.FOREIGN_COUNTRIES:
            if country in location2:
                is_foreign.append(True)
                break
        else:
            is_foreign.append(False)

    data[c.LOCATION] = towns
    data[c.IS_FOREIGN] = is_foreign

    # rename towns to single word
    data[c.LOCATION] = data[c.LOCATION].str.split("-")
    data[c.LOCATION] = data[c.LOCATION].str[0]
    data[c.LOCATION] = data[c.LOCATION].astype(str)

    # multiple filters of location
    filter_ = data[c.LOCATION].notna() \
              & data[c.LOCATION].apply(lambda x: True if x.isalpha() else False) \
              & data[c.LOCATION].apply(lambda x: True if x != "nan" else False) \
              & ~data[c.IS_FOREIGN] == True
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

    # save
    data.to_csv(c.FEATURES_CLEANED, index=False)


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
                filter_ = (data[c.LOCATION] == c.TOWNS_PRAGUE[0]) \
                          & (data[c.TYPE] == type_)
            elif i == 1:
                filter_ = data[c.LOCATION].isin(c.TOWNS_TOP9) \
                          & (data[c.TYPE] == type_)
            else:
                filter_ = ~data[c.LOCATION].isin(c.TOWNS_PRAGUE + c.TOWNS_TOP9) \
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

    utilities.csv_concatenation(main_file=c.RESULTS,
                                new_data=new_data)


def archive_dataset():
    """
    Rename feature dataset and move it into new location - archive it.

    :return: None
    """
    file_number = len(os.listdir(c.ARCHIVE))

    # renames and also moves the file to new location
    os.rename(c.FEATURES_ALL, f"{c.ARCHIVE}/{file_number}.csv")


def delete_data():
    """
    Delete and clear all files that are not gonna be needed.

    :return: None
    """
    with open("completed_index.txt", "w") as file:
        file.write("")

    os.remove(c.FEATURES_CLEANED)
    os.remove(c.PROPERTIES)
    os.remove(c.PROPERTIES_CLEANED)


def delete_sitemap_files():
    """
    Delete all 'sitemap' files in downloads directory

    :returns: None
    """
    for file in os.listdir(c.DOWNLOADS):
        if file.startswith(c.SITEMAP):
            os.remove(f"{c.DOWNLOADS}/{file}")
