-- 1. Obtener las 5 películas con mayor promedio de duración por década.**

WITH RankedMovies AS (
          SELECT
              title,
              year,
              duration,
              FLOOR(year / 10) * 10 AS decada,
              ROW_NUMBER() OVER (PARTITION BY FLOOR(year / 10) * 10 ORDER BY duration DESC) AS rn
          FROM
              movies
      )
      SELECT
          title,
          year,
          duration,
          decada
      FROM
          RankedMovies
      WHERE
          rn <= 5;

-- 2. **Calcular la desviación estándar de las calificaciones por año.**

      SELECT
          year,
          round(STDDEV(rating),2) AS std_dev
      FROM
          movies
      GROUP BY
          year
      order by year;

--  3.  **Detectar películas con más de un 20% de diferencia entre calificación IMDB y Metascore (normalizado).**
-- _Consideración:_ Se observó que el _rating_ de IMDb se presenta en una escala de 0 a 10, mientras que el Metascore va de 0 a 100. Para una comparación justa, el Metascore se ha normalizado dividiéndolo por 10.

   
      SELECT
        title,
        year,
        detail_url,
        rating,
        metascore,
        ROUND(ABS(rating - metascore / 10), 2) AS diferencia,
        ROUND(ABS(rating - metascore / 10) / rating * 100, 2) AS diferencia_porcentual
      FROM
        movies
      WHERE
        rating IS NOT NULL
        AND metascore IS NOT NULL
        AND rating IS NOT NULL
        AND ABS(rating - metascore / 10) / rating > 0.20
      ORDER BY diferencia_porcentual
     

--  4.  **Crear una vista que relacione películas y actores, y permita filtrar por actor principal.**
--      _Consideración:_ Dado que no hay un campo explícito que indique al "actor principal" en la página de IMDb ni en la estructura de datos obtenida, se asume para esta consulta que **el primer actor en la lista asociada a una película es el actor principal.**

      
      CREATE VIEW vista_peliculas_actor_principal AS
      SELECT
      m.id AS movie_id,
      m.title,
      a.id AS actor_id,
      a.name AS actor_name
      FROM (
      SELECT
          ma.movies_id,
          ma.actors_id,
          ROW_NUMBER() OVER (PARTITION BY ma.movies_id ORDER BY ma.actors_id) AS orden
      FROM movie_actors ma
      ) sub
      JOIN movies m ON m.id = sub.movies_id
      JOIN actors a ON a.id = sub.actors_id
      WHERE sub.orden = 1;
      -- Consulta de prueba
      -- SELECT * FROM vista_peliculas_actor_principal;
    
