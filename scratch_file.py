import pandas as pd

dataset = pd.read_csv("links_to_properties_cleaned.csv")
for link, id_ in zip(dataset["loc"].head(), dataset["id"].head()):
    print(dataset.index[dataset["id"] == id_].tolist()[0])
