# -*- coding: utf-8 -*-
from pages.imdb_home_page import IMDBHomePage
from pages.imdb_detail_page import IMDBDetailPage
from repositories.csv_repository import CSVRepository
from repositories.sqlite_repository import SQLiteRepository
from repositories.mysql_repository import MySQLRepository
from config import IMDB_TOP_MOVIES_URL, CUSTOM_COOKIES, SCRAPING_CONFIG
from util import log_info, log_error
import time
import random

from util.logging_utils import log_warning

class IMDBScraperMain:
    def __init__(self, custom_cookies=None, fetch_strategy="standard"):
        self.custom_cookies = custom_cookies or CUSTOM_COOKIES
        self.csv_repo = CSVRepository("imdb_top_movies")
        self.db_repo = SQLiteRepository()
        self.mysql_repo = MySQLRepository()
    
    def scrape_top_movies(self, max_movies=None):
        """Scrapes la lista de películas top usando IMDBHomePage"""
        home_page = IMDBHomePage(
            IMDB_TOP_MOVIES_URL, 
            self.custom_cookies
        )
        return home_page.extract_data(max_movies)
    
    def scrape_movie_details(self, movies_list):
        """Scrapes detalles adicionales usando IMDBDetailPage"""
        log_info(f"Encontradas {len(movies_list)} películas. Obteniendo detalles...")
        
        for i, movie in enumerate(movies_list):
            log_info(f"Procesando película {i+1}/{len(movies_list)}: {movie['title']}")
            
            if movie['detail_url']:
                detail_page = IMDBDetailPage(
                    movie['detail_url'], 
                    self.custom_cookies
                )
                metascore, actors = detail_page.extract_data()
                
                movie['metascore'] = metascore
                movie['actors'] = actors
            else:
                log_error(f"No se encontró URL de detalle para: {movie['title']}")
            
            # Pausa aleatoria para evitar bloqueos
            time.sleep(random.uniform(
                SCRAPING_CONFIG['delay_min'], 
                SCRAPING_CONFIG['delay_max']
            ))
        
        return movies_list
    
    def save_data(self, movies_data, save_to_csv=True, save_to_db=True, save_to_mysql=True):
        """Guarda los datos usando los repositorios"""
        results = {}
        
        # Limpiar datos antes de guardar (solo MySQL)
        log_info("Limpiando datos anteriores en MySQL...")
        
        # Guardar en todos los repositorios
        if save_to_csv:
            log_info("Guardando datos en CSV...")
            results['csv'] = self.csv_repo.save(movies_data)
        if save_to_db:
            self.db_repo.delete_all()
            log_info("Guardando datos en SQLite...")
            results['sqlite'] = self.db_repo.save(movies_data)
        if save_to_mysql:
            self.mysql_repo.delete_all()
            log_info("Guardando datos en MySQL...")
            results['mysql'] = self.mysql_repo.save(movies_data)
        
        return results
    
    def scrape_complete_data(self, max_movies=None, save_to_csv=True, save_to_db=True, save_to_mysql=True):
        """Proceso completo de scraping y guardado"""
        # Paso 1: Obtener lista de películas
        movies = self.scrape_top_movies(max_movies)

        if not movies:
            log_error("No se encontraron películas para procesar.")
            return []
        
        # Paso 2: Obtener detalles de cada película
        movies_with_details = self.scrape_movie_details(movies)
        
        # Paso 3: Guardar datos
        save_results = self.save_data(movies_with_details, save_to_csv, save_to_db, save_to_mysql)
        log_info(f"Resultados de guardado: {save_results}")
        
        return movies_with_details

def main():
    """
    Función principal
    """
    log_info("Iniciando scraping de IMDB")
    
    # Crear instancia del orquestador
    scraper_main = IMDBScraperMain()
    
    # Proceso completo
    movies_data = scraper_main.scrape_complete_data(
        # max_movies=2,  # Para pruebas
        save_to_csv=True,
        save_to_db=True,
        save_to_mysql=True
    )
    
    if not movies_data:
        log_error("No se obtuvieron datos. Saliendo.")
        return
    
    # Mostrar resumen
    log_info(f"Proceso completado. {len(movies_data)} películas procesadas.")
    log_info("Datos guardados en CSV, SQLite y MySQL.")

if __name__ == "__main__":
    main() 