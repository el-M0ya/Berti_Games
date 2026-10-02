-- Votos de los visitantes.
--
-- Se guarda UN voto por persona y por juego (la llave primaria lo
-- garantiza). La persona se identifica con un id aleatorio que genera el
-- navegador, no con su IP: asi no hay que guardar datos personales.
--
-- direction:  1 = me gusta,  -1 = no me gusta

CREATE TABLE IF NOT EXISTS votes (
  game_id    TEXT    NOT NULL,
  client_id  TEXT    NOT NULL,
  direction  INTEGER NOT NULL CHECK (direction IN (-1, 1)),
  updated_at INTEGER NOT NULL,
  PRIMARY KEY (game_id, client_id)
);

-- Para sumar los votos de un juego rapido.
CREATE INDEX IF NOT EXISTS idx_votes_game ON votes (game_id);

-- Para limpiar votos viejos si algun dia hace falta.
CREATE INDEX IF NOT EXISTS idx_votes_fecha ON votes (updated_at);