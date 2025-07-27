# Configuración del proyecto IMDB Scraper

# URLs
IMDB_BASE_URL = "https://www.imdb.com"
IMDB_TOP_MOVIES_URL = f"{IMDB_BASE_URL}/chart/top/"

# Headers para requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Connection': 'keep-alive',
}

# Cookies personalizadas para evitar bloqueos
CUSTOM_COOKIES = {
    'session-id': '143-4325845-0165363',
    'session-id-time': '2082787201l',
    'ubid-main': '133-1336161-3652037',
    'ad-oo': '16',
    'gpc-cache': '1',
    'ci': 'eyJpc0dkcHIiOmZhbHNlfQ',
    'international-seo': 'es',
    'session-token': 'DzycU9KULiQ3aoUqDdyPpJOmGht6iPduFoQ3VtC6/qEFV4MuPlqPJOPSUkfVPSkgNXZw4pITupCEdngDxi4KkJD0oQaCz7oDLGkzv8qOfuAt3bfZ5GAmOiS+H5jeg7qGde8vLQMsAybd5wduSMzoau+tTFc9xYICwd5ZtjXdOrEsgaAMd9u5OqhTJXnVEP0LO0l6DOjA6wsxPhL2wcptgZJSgQaPjakHMNIGGlFOUhXt3h47BJEZiMRwvbzzsGn7XdXI79pPnKXjJbfig07LGsPa+gNdwQyyB+fX8qIUNomj6NYQvalOrWJol8YLLBZMxFVP/MwRFV5qoSJNCQEOxPTZXs7Ypqwy',
    'csm-hit': 'adb:adblk_yes&t:1753472042888&tb:S2H6XEVH53GJ3B67NQCS+b-8GQ3VFDQGAXT7F483H6F|1753472042887'
}

# Configuración de scraping
SCRAPING_CONFIG = {
    'max_movies': 250,  # Número máximo de películas a extraer
    'retries': 4,      # Número de reintentos para requests
    'timeout': 10,     # Timeout para requests en segundos
    'delay_min': 1,    # Delay mínimo entre requests (segundos)
    'delay_max': 3,    # Delay máximo entre requests (segundos)
    'max_actors': 200,   # Número máximo de actores a extraer por película
}


# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s [%(levelname)s] %(message)s',
    'handlers': ['StreamHandler'],
} 