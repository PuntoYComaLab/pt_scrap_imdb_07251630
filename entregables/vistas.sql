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