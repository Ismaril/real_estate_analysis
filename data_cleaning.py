import re
import pandas as pd
from collections import Counter


def data_cleaner():
    data = pd.read_csv("links_to_properties.csv")

    # drop some first unwanted stuff
    if "Unnamed: 0" in data.columns:
        data.drop(["Unnamed: 0"], axis=1, inplace=True)
    if "lastmod" in data.columns:
        data.drop(["lastmod"], axis=1, inplace=True)
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
    link: str
    for link in data["loc"]:
        split = link.split("/")
        property_type.append(split[5])
        type_of_sale.append(split[4])

    # get some feeling of property type statistics
    property_type_stats = Counter(property_type)
    print("Summary of property types: ", property_type_stats.most_common())

    # filter out next unwanted stuff
    data["Property type:"] = property_type
    data["Type of sale:"] = type_of_sale
    data.drop(["filter"], axis=1, inplace=True)
    data = data.loc[data["Property type:"] != "komercni"]
    data = data.loc[data["Property type:"] != "ostatni"]
    data = data.loc[data["Type of sale:"] != "pronajem"]
    data = data.loc[data["Type of sale:"] != "drazby"]
    data.drop(["Property type:"], axis=1, inplace=True)
    data.drop(["Type of sale:"], axis=1, inplace=True)

    # save cleaned dataset
    data: pd.DataFrame
    data.to_csv("links_to_properties_cleaned.csv")

    print(data)

data_cleaner()