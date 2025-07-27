-- Creación del índice
CREATE INDEX idx_rating_year ON movies (rating DESC, year);
-- Consulta de prueba
-- SELECT title, year, detail_url, rating FROM movies ORDER BY rating DESC, year;
-- Tiempos de ejecución comparativos:
-- Antes del índice   : 0.001749 segundos
-- Después del índice : 0.001044 segundos