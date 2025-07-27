from pages.base_page import BasePage
from util import log_info, log_error
from config import SCRAPING_CONFIG

class IMDBDetailPage(BasePage):
    """Página de detalle de película que encapsula la información específica"""
    
    def __init__(self, url, custom_cookies=None):
        super().__init__(url, custom_cookies)
    
    def get_metascore(self):
        """Obtiene el metascore de la película"""
        metascore_element = self.get_element('span.sc-9fe7b0ef-0.hDuMnh.metacritic-score-box')
        if metascore_element:
            return metascore_element.text.strip()
        return None
    
    def get_actors(self):
        """Obtiene la lista de actores principales"""
        
        actor_elements = self.get_elements('a.sc-10bde568-1.jBmamV')    
        actors = []
        if actor_elements:
            for actor_element in actor_elements[:SCRAPING_CONFIG['max_actors']]:
                actor_name = actor_element.text.strip()
                if actor_name:
                    actors.append(actor_name)
        
        return actors
    
    def extract_data(self):
        """Extrae todos los datos de detalle de la película"""
        log_info(">Ini parse movie detail")
        
        if not self.load_page():
            log_error("No se pudo cargar la página de detalle")
            return None, []
        
        metascore = self.get_metascore()
        actors = self.get_actors()
        
        return metascore, actors 