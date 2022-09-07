# names of columns in csv
LINK = "Link:"
LOC = "loc"
LOCATION = "Lokace:"
LOCATION2 = "Lokace_:"
UNNAMED = "Unnamed: 0"
LASTMOD = "lastmod"
DATETIME_SCRAPED = "Řádek vytvořen:"
TOTAL_PRICE = "Celková cena:"
ON_SALE = "Zlevněno:"
PROPERTY = "Nemovitost:"
TYPE = "Typ:"
STRUCTURE = "Stavba:"
STATE_OF_OBJECT = "Stav objektu:"
OWNERSHIP = "Vlastnictví:"
FORMER_PRICE = "Původní cena:"
USABLE_AREA = "Užitná plocha:"
LAND_AREA = "Plocha pozemku:"
GARDEN_AREA = "Plocha zahrady:"
SALE = "Sleva:"
TOTAL_AREA = "Celková plocha:"
PRICE_M2 = "Cena metr2"
PERIOD = "Měsíc"
IS_FOREIGN = "Je zahraniční:"

# specifications
# TYPES_PROPERTIES is declaration for constant below (watch index position here)
TYPES_PROPERTIES = ("byt", "dum", "pozemek")
TYPES_FLAT = ["1+kk", "1+1",
              "2+kk", "2+1",
              "3+kk", "3+1",
              "4+kk", "4+1",
              "5+kk", "5+1",
              "6-a-vice", "atypicky"]

TYPES_HOUSE = ["rodinny", "chata", "chalupa", "vila",
               "na-klic", "zemedelska-usedlost", "pamatka"]

TYPES_LAND = ["bydleni", "pole", "les", "zahrada", "ostatni-pozemky",
              "louka", "komercni", "sady-vinice", "rybnik"]

BUILD = ("Cihlová", "Panelová", "Smíšená", "Skeletová",
         "Montovaná", "Kamenná", "Dřevěná")

# simple strings
COMMERCIAL = "komercni"
OTHERS = "ostatni"
RENT = "pronajem"
AUCTION = "drazby"
SITEMAP = "sitemap"
SHORT_PRAGUE = "Pra"
SHORT_TOP9 = "T_9"
SHORT_REST = "Oth"
SEPARATOR = f"\n{'-' * 60}\n"
FLAT = TYPES_PROPERTIES[0]
HOUSE = TYPES_PROPERTIES[1]
LAND = TYPES_PROPERTIES[2]
TOWNS_TOP9_T = f"Brno, Ostrava, Plzeň, Liberec, Olomouc, České Budějovice," \
               f"Hradec Králové, Ustí nad Labem, Pardubice"
TOWNS_REST_T = "Celá ČR mimo 10 největších měst"

# directories
BATCHES = "batches"
ARCHIVE = "archive"
LINKS = "links_to_properties"
DOWNLOADS = "C:/Users/lazni/Downloads"

# csv datasets
PROPERTIES = "links_to_properties/links_to_properties.csv"
PROPERTIES_CLEANED = "links_to_properties/links_to_properties_cleaned.csv"
FEATURES = "features/features_all.csv"
FEATURES_CLEANED = "features/features_cleaned.csv"
RESULTS = "result/prices_all_months.csv"

# user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
]

# address to chrome driver (exe)
DRIVER_ADDRESS = "chrome_driver/chromedriver.exe"

# sitemap (xml)
SITE_MAP = "https://www.sreality.cz/sitemap.xml"

# locations
TOWNS_PRAGUE = ["praha"]

TOWNS_TOP9 = ["brno", "ostrava", "plzen", "liberec", "olomouc", "ceskebudejovice",
              "hradeckralove", "ustinadlabem", "pardubice"]

TOWNS_REST = TOWNS_PRAGUE + TOWNS_TOP9

FOREIGN_COUNTRIES = ["Španělsko", "Polsko", "Bulharsko"]  # todo: update these


