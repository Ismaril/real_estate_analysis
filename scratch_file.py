import os

import pandas as pd


result = pd.DataFrame()
for file in os.listdir("batches"):
    result = pd.concat([result, pd.read_csv(f"batches/{file}")])
result.drop(["Unnamed: 0"], inplace=True, axis=1)
result.to_csv("features_all.csv")


# dataset = pd.read_csv("links_to_properties_cleaned.csv")
# for link, id_ in zip(dataset["loc"].head(), dataset["id"].head()):
#     print(dataset.index[dataset["id"] == id_].tolist()[0])
