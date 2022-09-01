# names of columns in csv
LINK = "Link:"
LOC = "loc"
LOCATION = "Lokace:"
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

# efef
PROPERTIES = ("byt", "dum", "pozemek")  # source declaration for constant below
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
FLAT = PROPERTIES[0]
HOUSE = PROPERTIES[1]
LAND = PROPERTIES[2]

# links to websites (csv)
PROPERTIES_LINKS = "links_to_properties/links_to_properties.csv"
PROPERTIES_CLEANED_LINKS = "links_to_properties/links_to_properties_cleaned.csv"

# features of each property (csv)
FEATURES = "features/features_all.csv"
FEATURES_CLEANED = "features/features_cleaned.csv"

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

# local directories
DOWNLOADS = "C:/Users/lazni/Downloads"

# locations
TOWNS_PRAGUE = ["Praha"]
TOWNS_TOP_9 = ["Brno", "Ostrava", "Plzen", "Liberec", "Olomouc",
               "Ceske Budejovice", "Hrade Kralove", "Usti nad Labem",
               "Pardubice"]
TOWNS_REST = TOWNS_PRAGUE + TOWNS_TOP_9
NOT_VALID_TOWNS = ["Adeje", "Agia", "Agros", "Aguilas", "Aheloy", "Al", "Alanya",
                   "Algarrobo", "Algorfa", "Alicante", "Altea", "Aluthgama",
                   "Amarilla", "Anglerweg", "Annaberg", "Antalya", "Apartamentos",
                   "Aptera", "Arzl", "Aspe", "Avenida", "Avenue", "Avinguda",
                   "Avola", "Avtobus", "Ayia", "Baan", "Bad", "Badesi", "Balcik",
                   "Bar", "Barcelona", "Barriada", "Bayerisch", "Bdeneves",
                   "Becici", "Benagalbon", "Benahavis", "Benalauria", "Benalmadena",
                   "Benatky", "Benidorm", "Benijofar", "Benissa", "Bibinje", "Biograd",
                   "Bologna", "Bosana", "Brac", "Bratislava", "Brodarica", "Bus",
                   "Burgas", "Byala", "Cabo", "Cabopino", "Cagliari", "Calahonda",
                   "Calasetta", "Calasparra", "Callao", "Calle", "Camping", "Campobello",
                   "Cancun", "Cannigione", "Carevo", "Carrer", "Cartagena", "Cartama",
                   "Casares", "Cemagi", "Cesarica", "Ciovo", "Ciudad", "Costa",
                   "Country", "Crikvenica", "Cuevas", "Cuneo", "Czech", "Daskabat",
                   "Davos", "Daya", "Dehesa", "Desenzano", "Detroit", "Dolores",
                   "Dorfstra", "Drac", "Drapanos", "Duba", "Dubaj", "Dubrovnik",
                   "Duga", "El", "Elenite", "Eraclea", "Eracleamare", "Ericeira",
                   "Erpuzice", "Estepona", "Evan", "Famagusta", "Fasnia", "Fazana",
                   "Fieberbrunn", "Figueres", "Finestrat", "Five", "Formentera",
                   "Fraga", "Fuengirola", "Fugen", "Fulnek", "Gargellen",
                   "Geyersberg", "Golem", "Golf", "Gorica", "Goritsa",
                   "Gornji", "Gosau", "Gracani", "Grafenwiesen", "Gralska",
                   "Granadilla", "Grebastica", "Greslove", "Grobming", "Gruna",
                   "Gruzie", "Grygov", "Guardamar", "Habaraduwa", "Haidmuhle",
                   "Hinterstoder", "Hollersbach", "Hospental", "Hurghada", "Chalkidiki",
                   "Ibiza", "Ishem", "Jacarilla", "Jalan", "Jalubi", "Jonske", "Kableshkovo",
                   "Kali", "Kambia", "Kassandreia", "Kastela", "Kastellani", "Katschberg",
                   "Kavaja", "Kavarna", "Kokkino", "Korfu", "Kosharitsa", "Krk", "L", "La",
                   "Las", "Laz", "Lite", "Liznjan", "Lkan", "Lnare", "Lozenets", "Luxurious",
                   "Madrigal", "Mahmutlar", "Makarska", "Malaga", "Male", "Mandre", "Manilva",
                   "Mar", "Marathokefala", "Marbella", "Mattinata", "Miami", "Montesilvano",
                   "Moos", "Moraira", "Murciana", "Murter", "nan", "Nassfeld", "Neo",
                   "Nesebar", "Noruega", "Novalja", "Novelda", "Novi", "Novigrad", "Oberndorf",
                   "Omis", "Ondara", "Opatija", "Orihuela", "Oscadnica", "Pafos", "Pag", "Pagi",
                   "Pachino", "Pakostane", "Pangandaran", "Parque", "Pattaya", "Penthous", "Penthouse",
                   "Podgora", "Polen", "Polop", "Pomorie", "Portugalsko", "Posedarje", "Posna",
                   "Povljana", "Primorsko", "Primosten", "Privlaka", "Puerto", "Pula", "Pulpi",
                   "Punat", "Qerret", "Rab", "Ravda", "Razlog", "Rennweg", "Rentalsbcn", "Roatan",
                   "Rogachevo", "Rogoznica", "Rrashbull", "Safa", "Safaga", "Sahl", "San",
                   "Sandland", "Sankt", "Saranda", "Sassofortino", "Savudrija", "Scalea",
                   "Shengjin", "Schladming", "Schrattenberg", "Sidari", "Simuni", "Sira",
                   "Sirmione", "Sisan", "Sistiana", "Siviri", "Skil", "Slough", "Sofie",
                   "Sofitel", "Soma", "Sommatino", "Son", "Souvenirs", "Sozopol", "Spanelsko",
                   "Spiegelau", "Split", "Splitska", "Srbsko", "Srima", "St", "Starigrad",
                   "Sucuraj", "Sumartin", "Supetar", "Syvota", "Tabanan", "Talin", "Tankovo",
                   "Tauplitz", "The", "Torre", "Torremolinos", "Torrevieja", "Torrox",
                   "Tossa", "Treffen", "Trezzo", "Tribunj", "Trikomo", "Trogir", "Tulum",
                   "Turanj", "Turcianske", "Ugljan", "Ulcinj", "Umag", "Urbanizacion",
                   "Valencie", "Vera", "Via", "Villa", "Villajoyosa", "Villamartin", "Villaricos",
                   "Vinjerac", "Vinkuran", "Vir", "Waldschmidtstra", "Xabia", "Zahreb", "Zakynthos",
                   "Zell", ]
