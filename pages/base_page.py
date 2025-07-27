from abc import ABC, abstractmethod
from factories.fetch_factory import FetchFactory
from util import log_error

class BasePage(ABC):
    """Clase base para todas las páginas web"""
    
    def __init__(self, url, custom_cookies=None):
        self.url = url
        self.custom_cookies = custom_cookies
        self.soup = None
        self.response = None
        self.fetch_strategy = FetchFactory.create_fetch_strategy()
    
    def load_page(self):
        self.soup, self.response = self.fetch_strategy.fetch(
            self.url, 
            self.custom_cookies
        )
        return self.soup is not None
    
    def get_element(self, selector, method='css'):
        """Obtiene un elemento de la página de forma segura"""
        if not self.soup:
            log_error("No se ha cargado la página")
            return None
        
        try:
            if method == 'css':
                return self.soup.select_one(selector)
            elif method == 'find':
                return self.soup.find(selector)
            else:
                log_error(f"Método no soportado: {method}")
                return None
        except Exception as e:
            log_error(f"Error obteniendo elemento {selector}: {e}")
            return None
    
    def get_elements(self, selector, method='css'):
        """Obtiene múltiples elementos de la página de forma segura"""
        if not self.soup:
            log_error("No se ha cargado la página")
            return []
        
        try:
            if method == 'css':
                return self.soup.select(selector)
            elif method == 'find_all':
                return self.soup.find_all(selector)
            else:
                log_error(f"Método no soportado: {method}")
                return []
        except Exception as e:
            log_error(f"Error obteniendo elementos {selector}: {e}")
            return []
    
    @abstractmethod
    def extract_data(self):
        pass 