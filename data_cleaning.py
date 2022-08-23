import os
import re
import pandas as pd
from collections import Counter


def clean_raw_data():
    """Filter all links to websites that are not relevant for us"""
    data = pd.read_csv("links_to_properties/links_to_properties.csv")
    data.dropna(inplace=True)

    # locate links to properties, break out once the pattern of links changes (properties on the site map
    #    are then followed by some not relevant pages)
    for i, link in enumerate(data["loc"][:-1]):
        try:
            match = re.search("/.\d+", link)
            match.group()
        except AttributeError:
            data = data[:i]  # cut off following webpages that are not relevant
            break

    # filter out duplicate webpages, site map has the same web pages 2x - CZ and EN language
    filter_duplicate_links = [False, True] * (len(data["loc"]) // 2)
    data["filter"] = filter_duplicate_links
    data = data.loc[data["filter"] == False]

    # find the property type and type of sale
    property_type = []
    type_of_sale = []
    property_id = []
    for link in data["loc"]:
        split = link.split("/")
        property_type.append(split[5])
        type_of_sale.append(split[4])
        property_id.append(split[-1])

    # get some feeling of property type statistics
    property_type_stats = Counter(property_type)
    print("Summary of property types: ", property_type_stats.most_common())

    # filter out next unwanted stuff
    data["Property type:"] = property_type
    data["Type of sale:"] = type_of_sale
    filter_ = (data["Property type:"] != "komercni") & \
              (data["Property type:"] != "ostatni") & \
              (data["Type of sale:"] != "pronajem") & \
              (data["Type of sale:"] != "drazby")
    data = data.loc[filter_]
    data.drop(["Unnamed: 0", "lastmod", "filter",
               "Property type:", "Type of sale:"],
              axis=1, inplace=True)

    # assign new column
    # todo: might be possible to delete?
    data["id"] = data["loc"].str.split("/")
    data["id"] = data["id"].str[-1]

    # save cleaned dataset
    data: pd.DataFrame
    data.to_csv("links_to_properties/test.csv")
    print(data)


def concatenate_batches():
    result = pd.DataFrame()
    for file in os.listdir("batches"):
        result = pd.concat([result, pd.read_csv(f"batches/{file}")])
    result.drop(["Unnamed: 0"], inplace=True, axis=1)
    result.to_csv("features/features_all.csv")
    print("Batches concatenated")


def clean_feature_data():
    data = pd.read_csv("features/features_all.csv")
    # todo: add more columns
    data.drop(["Unnamed: 0", "Link:", "Id:",
               "Řádek vytvořen:"], inplace=True, axis=1)

    # filter data where both of these are missing (also should remove duplicates from 'rescraping')
    filter_ = ~(pd.isna(data["Celková cena:"])) | ~(pd.isna(data["Zlevněno:"]))
    data = data.loc[filter_]

    # rename towns only to single word
    data["Lokace:"] = data["Lokace:"].str.split()
    data["Lokace:"] = data["Lokace:"].str[0]

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
    data = pd.read_csv("features/features_all.csv")
    filter_ = (pd.isna(data["Celková cena:"])) & (pd.isna(data["Zlevněno:"]))
    data = data.loc[filter_]["Link:"]
    data.rename(columns={"Link:": "col"}, inplace=True)
    data.to_csv("links_to_properties/links_to_properties_unsuccessful.csv")
    return pd.read_csv("links_to_properties/links_to_properties_unsuccessful.csv")


def delete_all_batches():
    pass
