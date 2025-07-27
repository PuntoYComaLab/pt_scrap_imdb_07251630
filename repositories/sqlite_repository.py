import sqlite3
import os
from typing import List, Dict, Any
from repositories.base_repository import BaseRepository
from util import log_info, log_error

class SQLiteRepository(BaseRepository):
    """Repositorio que guarda datos en base de datos SQLite"""
    
    def __init__(self, db_name: str = "imdb_movies.db", data_dir: str = "data"):
        self.db_name = db_name
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, db_name)
        
        # Crear directorio si no existe
        os.makedirs(data_dir, exist_ok=True)
        
        # Inicializar la base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos con las tablas de películas, actores y relación"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla de películas
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS movies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        year TEXT,
                        rating TEXT,
                        duration INTEGER,
                        metascore TEXT,
                        detail_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabla de actores
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS actors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabla intermedia para relación muchos a muchos
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS movie_actors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        movie_id INTEGER NOT NULL,
                        actor_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (movie_id) REFERENCES movies (id),
                        FOREIGN KEY (actor_id) REFERENCES actors (id),
                        UNIQUE(movie_id, actor_id)
                    )
                ''')
                
                conn.commit()
                log_info(f"Base de datos inicializada: {self.db_path}")
        except Exception as e:
            log_error(f"Error inicializando base de datos: {e}")
    
    def _get_or_create_actor(self, cursor, actor_name):
        """Obtiene un actor existente o lo crea si no existe"""
        cursor.execute('SELECT id FROM actors WHERE name = ?', (actor_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]  # Retorna el ID del actor existente
        else:
            cursor.execute('INSERT INTO actors (name) VALUES (?)', (actor_name,))
            return cursor.lastrowid  # Retorna el ID del nuevo actor
    
    def save(self, data: List[Dict[str, Any]]) -> bool:
        """Guarda los datos en la base de datos"""
        if not data:
            log_error("No hay datos para guardar")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for movie in data:
                    # Insertar película
                    cursor.execute('''
                        INSERT INTO movies (title, year, rating, duration, metascore, detail_url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        movie.get('title', ''),
                        movie.get('year', ''),
                        movie.get('rating', ''),
                        movie.get('duration'),
                        movie.get('metascore', ''),
                        movie.get('detail_url', '')
                    ))
                    
                    movie_id = cursor.lastrowid
                    
                    # Procesar actores
                    actors = movie.get('actors', [])
                    for actor_name in actors:
                        if actor_name:
                            # Obtener o crear actor
                            actor_id = self._get_or_create_actor(cursor, actor_name)
                            
                            # Crear relación en tabla intermedia
                            try:
                                cursor.execute('''
                                    INSERT INTO movie_actors (movie_id, actor_id)
                                    VALUES (?, ?)
                                ''', (movie_id, actor_id))
                            except sqlite3.IntegrityError:
                                # La relación ya existe, ignorar
                                pass
                
                conn.commit()
                log_info(f"{len(data)} películas guardadas en la base de datos")
                return True
                
        except Exception as e:
            log_error(f"Error guardando datos en la base de datos: {e}")
            return False
    
    def delete_all(self) -> bool:
        """Elimina todas las películas, actores y relaciones de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM movie_actors')
                cursor.execute('DELETE FROM movies')
                cursor.execute('DELETE FROM actors')
                conn.commit()
                log_info("Todas las películas, actores y relaciones eliminadas de la base de datos")
                return True
        except Exception as e:
            log_error(f"Error eliminando datos de la base de datos: {e}")
            return False 