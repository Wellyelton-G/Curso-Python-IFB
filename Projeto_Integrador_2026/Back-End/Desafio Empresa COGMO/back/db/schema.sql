PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  river TEXT NOT NULL,
  municipality TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  station_id TEXT NOT NULL,
  metric TEXT NOT NULL CHECK (metric IN ('level', 'rain')),
  observed_at TEXT NOT NULL,
  value REAL NOT NULL,
  unit TEXT NOT NULL CHECK (unit IN ('m', 'mm/h')),
  source TEXT NOT NULL DEFAULT 'synthetic',
  UNIQUE (station_id, metric, observed_at),
  FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_observations_station_metric_time
  ON observations (station_id, metric, observed_at);
