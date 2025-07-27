import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any
from repositories.base_repository import BaseRepository
from util import log_info, log_error
import os

class MySQLRepository(BaseRepository):
    """Repositorio que guarda datos en base de datos MySQL"""
    
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = int(os.getenv('MYSQL_PORT', '3306'))
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', 'db_scrap')
        self.connection = None
        
        # Verificar conexión al inicializar
        self._test_connection()
    
    def _get_connection(self):
        """Obtiene una conexión a MySQL"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            log_error(f"Error conectando a MySQL: {e}")
            return None
    
    def _test_connection(self):
        """Prueba la conexión a MySQL"""
        connection = self._get_connection()
        if connection and connection.is_connected():
            log_info(f"Conectado a MySQL: {self.host}:{self.port}/{self.database}")
            connection.close()
        else:
            log_error("No se pudo conectar a MySQL")
    
    def _get_or_create_actor(self, cursor, actor_name):
        """Obtiene un actor existente o lo crea si no existe"""
        try:
            # Buscar actor existente
            cursor.execute('SELECT id FROM actors WHERE name = %s', (actor_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]  # Retorna el ID del actor existente
            else:
                # Crear nuevo actor
                cursor.execute('INSERT INTO actors (name, created_at) VALUES (%s, NOW())', (actor_name,))
                return cursor.lastrowid  # Retorna el ID del nuevo actor
        except Error as e:
            log_error(f"Error procesando actor {actor_name}: {e}")
            return None
    
    def save(self, data: List[Dict[str, Any]]) -> bool:
        """Guarda los datos en la base de datos MySQL"""
        if not data:
            log_error("No hay datos para guardar")
            return False
        
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            for movie in data:
                # Insertar película
                cursor.execute('''
                    INSERT INTO movies (title, year, rating, duration, metascore, detail_url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ''', (
                    movie.get('title', '').strip(),  # Obligatorio, si no existe da ''
                    int(y) if (y := movie.get('year')) and str(y).isdigit() else None,
                    float(r) if (r := movie.get('rating')) and str(r).replace('.', '', 1).isdigit() else None,
                    int(d) if (d := movie.get('duration')) and str(d).isdigit() else None,
                    int(m) if (m := movie.get('metascore')) and str(m).isdigit() else None,
                    movie.get('detail_url') or None  # Guarda None si está vacío o no existe
                ))
                
                movie_id = cursor.lastrowid
                
                # Procesar actores
                actors = movie.get('actors', [])
                for actor_name in actors:
                    if actor_name:
                        # Obtener o crear actor
                        actor_id = self._get_or_create_actor(cursor, actor_name)
                        
                        if actor_id:
                            # Crear relación en tabla intermedia
                            try:
                                cursor.execute('''
                                    INSERT INTO movie_actors (movies_id, actors_id, create_at)
                                    VALUES (%s, %s, NOW())
                                ''', (movie_id, actor_id))
                            except Error as e:
                                # La relación ya existe o hay error, ignorar
                                log_error(f"Error creando relación movie-actor: {e}")
                                pass
            
            connection.commit()
            log_info(f"{len(data)} películas guardadas en MySQL")
            return True
                
        except Error as e:
            log_error(f"Error guardando datos en MySQL: {e}")
            connection.rollback()
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def delete_all(self) -> bool:
        """Elimina todas las películas, actores y relaciones de la base de datos MySQL"""
        connection = self._get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # Eliminar en orden correcto por las foreign keys
            cursor.execute('DELETE FROM movie_actors')
            cursor.execute('DELETE FROM movies')
            cursor.execute('DELETE FROM actors')
            
            connection.commit()
            log_info("Todas las películas, actores y relaciones eliminadas de MySQL")
            return True
            
        except Error as e:
            log_error(f"Error eliminando datos de MySQL: {e}")
            connection.rollback()
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close() 