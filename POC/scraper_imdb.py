# scraper_imdb.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# Función de logging reutilizable

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)


HEADERS = {
    #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Connection': 'keep-alive',
}


def get_next_time_to_wait(i):
    """
    La secuencia de espera se da en secuencia de fibonacci
    params:
        i: int -> número de intento
    returns:
        int -> tiempo de espera en segundos para ese intento
    """
    if i == 0:
        return 1
    elif i == 1:
        return 1
    else:
        return get_next_time_to_wait(i-1) + get_next_time_to_wait(i-2)


def fetch_page(url, retries=3, custom_cookies=None):
    log_info(f"Fetching: {url}")
    for i in range(retries):
        log_info(f"Intento {i+1}/{retries}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10, cookies=custom_cookies) 
            response.raise_for_status()
            log_info(f"Successfully fetched 🚀🚀🚀 !!")
            return response
        except requests.exceptions.RequestException as e:
            time_sleep = get_next_time_to_wait(i+1)
            log_error(f"Error fetching {url} (Intento {i+1}/{retries}): {e}")
            log_error(f"Retrying in {time_sleep} seconds...")
            time.sleep(time_sleep) # Backoff fibonaci
    return None

# --- Funciones para Scraping ---

def parse_top_movies_list(soup, max_movies=50):
    log_info(">Init get movie list")
    
    movies_data = []
    movie_list = soup.select("#__next > main > div > div.ipc-page-content-container.ipc-page-content-container--center > section > div > div.ipc-page-grid.ipc-page-grid--bias-left > div > ul")

    if not movie_list:
        log_error("No se encontró la lista de películas. Revisa los selectores.")
        return movies_data

    count = 0
    for movie_item in movie_list[0].find_all("li"): 
        if count >= max_movies:
            break
        try:
            # Title
            title_element = movie_item.find('h3', class_='ipc-title__text')
            if title_element and '.' in title_element.text:
                title = title_element.text.split('.', 1)[1].strip()
            elif title_element:
                title = title_element.text.strip()
            else:
                title = 'N/A'

            # Year & Duration
            sub_details_element = movie_item.select(".cli-title-metadata-item") 
            year = 'N/A'
            duration = None
            if sub_details_element and len(sub_details_element) > 0:
                year = sub_details_element[0].text.strip() if sub_details_element[0].text else 'N/A'
            if sub_details_element and len(sub_details_element) > 1:
                duration_str = sub_details_element[1].text.strip() if sub_details_element[1].text else None
                duration = convert_duration_to_minutes(duration_str) if duration_str else None

            # Rating
            rating_element = movie_item.find('span', class_='ipc-rating-star--rating')
            rating = rating_element.text.strip() if rating_element and rating_element.text else 'N/A'

            # Detail URL
            detail_link_element = movie_item.find('a', class_='ipc-title-link-wrapper')
            detail_url = f"https://www.imdb.com{detail_link_element['href']}" if detail_link_element and 'href' in detail_link_element.attrs else None

            log_info(f"Title: {title}, Year: {year}, Rating: {rating}, Detail URL: {detail_url}")
            
            movies_data.append({
                'title': title,
                'year': year,
                'rating': rating,
                'detail_url': detail_url if detail_url else None,
                'duration': duration,
                'metascore': None,
                'actors': []
            })
            count += 1
        except AttributeError as e:
            log_error(f"Error al parsear un item de película en la lista principal: {e}")
            continue
    return movies_data

def parse_movie_detail(soup):
    log_info(">Ini parse movie detail")
    metascore = None
    actors = []

    try:
        metascore_element = soup.find('span', class_='sc-9fe7b0ef-0 hDuMnh metacritic-score-box')
        if metascore_element:
            metascore = metascore_element.text.strip()
            #print(f"Metascore: {metascore}")

        actors_list_section = soup.find('div', class_='sc-10bde568-7 bhMzVl')
        if actors_list_section:
            actor_elements = actors_list_section.find_all('a', class_='sc-10bde568-1 jBmamV')
            for actor_element in actor_elements[:3]: # Solo los 3 primeros
                #print(actor_element.text.strip())
                actors.append(actor_element.text.strip())

    except AttributeError as e:
        log_error(f"Error al parsear detalles de la película: {e}")

    return metascore, actors

def convert_duration_to_minutes(duration_str):
    # Ejemplo: "1h 30m" -> 90
    total_minutes = 0
    if 'h' in duration_str:
        hours_str = duration_str.split('h')[0].strip()
        total_minutes += int(hours_str) * 60
        duration_str = duration_str.split('h')[1].strip()
    if 'm' in duration_str:
        minutes_str = duration_str.replace('m', '').strip()
        total_minutes += int(minutes_str)
    return total_minutes if total_minutes > 0 else None

# --- Función principal de ejecución ---
def main():
    base_url = "https://www.imdb.com/chart/top/"
    #base_url = "https://www.imdb.com/es/chart/top/"
    log_info(f"Scraping: {base_url}")

    my_custom_cookies = {
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

    response = fetch_page(base_url,3,my_custom_cookies)
    if not response:
        log_error("No se pudo obtener la página principal. Saliendo.")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    movies = parse_top_movies_list(soup,2) # se coloco un top para poder hacer pruebas rapidas

    if not movies:
        log_error("No se encontraron películas para procesar.")
        return

    log_info(f"Encontradas {len(movies)} películas en la lista principal. Obteniendo detalles...")

    # movies_to_process = movies[:50]

    for i, movie in enumerate(movies):
        log_info(f"Procesando película {i+1}/{len(movies)}: {movie['title']}")
        if movie['detail_url']:
            detail_response = fetch_page(movie['detail_url'])
            if detail_response:
                detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                metascore, actors = parse_movie_detail(detail_soup)
                movie['metascore'] = metascore
                movie['actors'] = actors

                # print details to test
                # print(f"Detalles de {movie['title']}:")
                # print(f"  Duración: {movie['duration']} minutos")
                # print(f"  Metascore: {movie['metascore']}")
                # print(f"  Actores: {', '.join(movie['actors']) if movie['actors'] else 'N/A'}")
            else:
                log_error(f"No se pudo obtener la página de detalle para: {movie['title']}")
        else:
            log_error(f"No se encontró URL de detalle para: {movie['title']}")

        time.sleep(random.uniform(1, 3)) # Pausa aleatoria para evitar ser bloqueado

    # Exportar a CSV
    df = pd.DataFrame(movies)
    df.to_csv('imdb_top_50_movies.csv', index=False, encoding='utf-8')
    log_info("Datos exportados a imdb_top_50_movies.csv")

    # Aquí iría la parte de la base de datos (PostgreSQL/MySQL),
    # pero para un inicio básico, el CSV es un buen primer paso.

if __name__ == "__main__":
    main()