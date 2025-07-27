import json
import re
from pages.base_page import BasePage
from util import log_info, log_error, convert_duration_to_minutes
from config import SCRAPING_CONFIG

class IMDBHomePage(BasePage):
    """Página principal de IMDB que encapsula la lista de películas top"""
    
    def __init__(self, url, custom_cookies=None):
        super().__init__(url, custom_cookies)
        self.movies_data = []
    
    def _extract_next_js_data(self):
        """Extrae los datos del JSON de Next.js que contiene releaseYear y datos completos"""
        try:
            # Buscar el script con __NEXT_DATA__
            script_element = self.soup.find('script', id='__NEXT_DATA__')
            if not script_element:
                log_error("No se encontró el script __NEXT_DATA__")
                return []
            
            # Parsear el JSON
            json_data = json.loads(script_element.string)
            
            # Navegar a la estructura de datos
            chart_titles = json_data.get('props', {}).get('pageProps', {}).get('pageData', {}).get('chartTitles', {}).get('edges', [])
            
            if not chart_titles:
                log_error("No se encontraron datos de películas en el JSON")
                return []
            
            log_info(f"Películas encontradas en JSON Next.js: {len(chart_titles)}")
            
            movies_data = []
            for edge in chart_titles:
                node = edge.get('node', {})
                if not node:
                    continue
                
                # Extraer datos básicos
                title = node.get('titleText', {}).get('text', 'N/A')
                original_title = node.get('originalTitleText', {}).get('text', 'N/A')
                
                # Extraer año (ahora disponible)
                release_year = node.get('releaseYear', {})
                year = str(release_year.get('year', 'N/A')) if release_year else 'N/A'
                
                # Extraer rating
                ratings_summary = node.get('ratingsSummary', {})
                rating = str(ratings_summary.get('aggregateRating', 'N/A')) if ratings_summary else 'N/A'
                
                # Extraer duración (en segundos, convertir a minutos)
                runtime = node.get('runtime', {})
                duration_seconds = runtime.get('seconds', 0) if runtime else 0
                duration = duration_seconds // 60 if duration_seconds > 0 else None
                
                # Extraer descripción
                plot = node.get('plot', {})
                description = plot.get('plotText', {}).get('plainText', 'N/A') if plot else 'N/A'
                
                # Extraer géneros
                title_genres = node.get('titleGenres', {})
                genres = []
                if title_genres:
                    genre_list = title_genres.get('genres', [])
                    genres = [genre.get('genre', {}).get('text', '') for genre in genre_list if genre.get('genre', {}).get('text')]
                
                # Extraer URL de detalle
                detail_url = f"https://www.imdb.com/title/{node.get('id', '')}/"
                
                # Crear diccionario de datos
                movie_data = {
                    'title': title,
                    'original_title': original_title,
                    'year': year,
                    'rating': rating,
                    'duration': duration,
                    'description': description,
                    'genres': genres,
                    'detail_url': detail_url,
                    'actors': []  # Se llenará después con IMDBDetailPage
                }
                
                movies_data.append(movie_data)
            
            return movies_data
            
        except json.JSONDecodeError as e:
            log_error(f"Error parseando JSON de Next.js: {e}")
            return []
        except Exception as e:
            log_error(f"Error extrayendo datos de Next.js: {e}")
            return []
    
    def extract_data(self, max_movies=None):
        """Extrae datos de todas las películas de la lista"""
        if max_movies is None:
            max_movies = SCRAPING_CONFIG['max_movies']
        
        log_info(">Init get movie list")
        
        if not self.load_page():
            log_error("No se pudo cargar la página de películas top")
            return []
        
        # Extraer datos del JSON de Next.js
        movies_data = self._extract_next_js_data()
        if not movies_data:
            log_error("No se pudieron extraer datos de películas")
            return []
        
        # Limitar al número máximo de películas
        movies_data = movies_data[:max_movies]
        
        # Log de información para verificar datos
        for i, movie in enumerate(movies_data, 1):
            log_info(f"Película {i}: {movie['title']} ({movie['year']}) - Rating: {movie['rating']} - Duración: {movie['duration']} min")
        
        self.movies_data = movies_data
        return self.movies_data 