## Aim of the project
The aim of the project was to get some
insight & feeling about current property
market (2022/2023).

## Process pipeline:
1.Getting the data
- downloading sitemap files, extracting and appending
all of them into one file (links to all webpages)
- cleaning the links to get only the ones concerned
with properties (flats, houses, lands)
- downloading and saving relevant features about each
property through requests and html parsing

2.Data cleaning
- cleaning downloaded feature dataset
- aggregating features into representative output,
for a given period of time (month)
- delete or archive all files that are no longer needed

3.Data visualisation
- visualise results separately for distinct locations
in CZE (like Prague, top 10 cities excluding Prague and \
the rest of republic) and property types

4.Repeating the process once per month


## Process is automated:
Input: Sitemap of www.sreality.cz \
Output: Plots / Data visualisation

## Limitation:
- Not getting banned by domain as robot.
- Since the program has to scrape cca 60_000 sites, scraping can take cca 50 hours.

## Todo:
Below tasks are here not mandatory but nice to have.
- Threading
- Scheduling a task to run the program every month.

## Status of the project:
Functional

## Result:
You can check all images/results in result directory

![prabyt](https://raw.githubusercontent.com/Ismaril/real_estate_analysis/main/result/Pra%20BYT.png)
