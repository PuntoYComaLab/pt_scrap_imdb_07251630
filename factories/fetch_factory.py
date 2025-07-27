from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from util import log_info, log_error
from config import HEADERS, SCRAPING_CONFIG
import time

# Constantes para los nombres de estrategia
ROTATIVE_STRATEGY = "rotative"
STANDARD_STRATEGY = "standard"

class FetchStrategy(ABC):
    """Estrategia base para fetching de páginas"""
    
    @abstractmethod
    def fetch(self, url, cookies=None, retries=None):
        pass

class StandardFetchStrategy(FetchStrategy):
    """Estrategia estándar con reintentos y backoff exponencial"""
    
    def fetch(self, url, cookies=None, retries=None):
        if retries is None:
            retries = SCRAPING_CONFIG['retries']
            
        log_info(f"Fetching: {url}")
        
        for i in range(retries):
            log_info(f"Intento {i+1}/{retries}")
            try:
                response = requests.get(
                    url, 
                    headers=HEADERS, 
                    timeout=SCRAPING_CONFIG['timeout'], 
                    cookies=cookies
                )
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                log_info(f"Successfully fetched {url} 🚀🚀🚀 !!")
                return soup, response
            except requests.exceptions.RequestException as e:
                time_sleep = self._get_next_time_to_wait(i+1)
                log_error(f"Error fetching {url} (Intento {i+1}/{retries}): {e}")
                log_error(f"Retrying in {time_sleep} seconds...")
                time.sleep(time_sleep)
        
        log_error(f"Failed to fetch {url} after {retries} attempts")
        return None, None
    
    def _get_next_time_to_wait(self, i):
        """Secuencia de Fibonacci para backoff"""
        if i == 0:
            return 1
        elif i == 1:
            return 1
        else:
            return self._get_next_time_to_wait(i-1) + self._get_next_time_to_wait(i-2)


class RotativeFetchStrategy(FetchStrategy):
    """Estrategia con proxy rotativo con reintentos y backoff exponencial"""
    
    """
    218.61.37.79	443	    China	                        660 ms
    34.41.115.197	3128	United States Council Bluffs	700 ms
    89.43.31.134	3128	Turkey	                        420 ms
    """
    proxies = [
        {"proxy":"http://34.41.115.197:3128","used":False},
        {"proxy":"http://89.43.31.134:3128","used":False},
        {"proxy":"http://218.61.37.79:443","used":False},
    ]
    
    def _reset_proxies(self):
        """Resetea el estado de los proxies a no usados"""
        for proxy in self.proxies:
            proxy['used'] = False

    def _get_rotated_proxy(self):
        """Obtiene un proxy rotativo no usado"""
        unused_proxies = [proxy['proxy'] for proxy in self.proxies if not proxy['used']]
        if not unused_proxies:
            log_info("Todos los proxies han sido usados, reseteando...")
            self._reset_proxies()
            unused_proxies = [proxy['proxy'] for proxy in self.proxies]
        
        proxy = unused_proxies[0]
        for p in self.proxies:
            if p['proxy'] == proxy:
                p['used'] = True
                break
        log_info(f"Usando proxy: {proxy}")
        return proxy    
    
    def fetch(self, url, cookies=None, retries=None):

        if retries is None:
            retries = SCRAPING_CONFIG['retries']
            
        log_info(f"Fetching: {url}")
        self._reset_proxies()  # Resetea proxies al inicio

        for i in range(retries):
            try:
                proxy_url = self._get_rotated_proxy()
                custom_proxy = {
                    "http": proxy_url,
                    "https": proxy_url
                }
                log_info(f"Intento {i+1}/{retries} con proxy {proxy_url}")

                response = requests.get(
                    url, 
                    proxies=custom_proxy,
                    headers=HEADERS, 
                    timeout=SCRAPING_CONFIG['timeout'], 
                    cookies=cookies
                )
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                log_info(f"Successfully fetched {url} 🚀🚀🚀 !!")
                return soup, response
            except requests.exceptions.RequestException as e:
                time_sleep = self._get_next_time_to_wait(i+1)
                log_error(f"Error fetching {url} (Intento {i+1}/{retries}): {e}")
                log_error(f"Retrying in {time_sleep} seconds...")
                time.sleep(time_sleep)
        
        log_error(f"Failed to fetch {url} after {retries} attempts")
        return None, None
    
    def _get_next_time_to_wait(self, i):
        """Secuencia de Fibonacci para backoff"""
        if i == 0:
            return 1
        elif i == 1:
            return 1
        else:
            return self._get_next_time_to_wait(i-1) + self._get_next_time_to_wait(i-2)

class FetchFactory:
    """Factory para crear estrategias de fetching"""
    
    @staticmethod
    def create_fetch_strategy(strategy=STANDARD_STRATEGY):
        if strategy == ROTATIVE_STRATEGY:
            return RotativeFetchStrategy()
        elif strategy == STANDARD_STRATEGY:
            return StandardFetchStrategy()
        else:
            raise ValueError(f"Estrategia desconocida: {strategy}")