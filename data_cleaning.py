import re

import numpy as np
import pandas as pd

data = pd.read_csv("links_to_properties.csv")

if "Unnamed: 0" in data.columns:
    data.drop(["Unnamed: 0"], axis=1, inplace=True)

if "lastmod" in data.columns:
    data.drop(["lastmod"], axis=1, inplace=True)

data.dropna(inplace=True)

# locate duplicates
to_be_deleted = []
for i, link in enumerate(data["loc"][:-1]):
    try:
        match = re.search("/.\d+", link)
        result = match.group()
        # if result in data["loc"].loc[i+1]:
        #     to_be_deleted.append(data["loc"].loc[i+1])
    except AttributeError:
        data = data[:i]
        print(len(data["loc"][:i]))
        print(len(data))
        break

filter_ = [False, True]*(len(data["loc"])//2)

data["filter"] = filter_
data = data.loc[data["filter"] == False]

# regex pro zjisteni o jakou nemovitost se jedna podle poctu "/"
for link in data["loc"][:100]:
    print(link)

# print(data["loc"])

