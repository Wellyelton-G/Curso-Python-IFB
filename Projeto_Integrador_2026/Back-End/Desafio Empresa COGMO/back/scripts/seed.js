require('dotenv').config();
const { db, filePath } = require('../src/db');

const stations = [
  { id: 'EST-01', name: 'Estação Aurora', river: 'Rio Aurora', municipality: 'Vila Aurora' },
  { id: 'EST-02', name: 'Estação Vale Verde', river: 'Rio Verde', municipality: 'Vale Verde' },
  { id: 'EST-03', name: 'Estação Campo Alto', river: 'Rio do Campo', municipality: 'Campo Alto' }
];

const insertStation = db.prepare(
  'INSERT OR IGNORE INTO stations (id, name, river, municipality) VALUES (@id, @name, @river, @municipality)'
);
const insertObservation = db.prepare(
  "INSERT OR IGNORE INTO observations (station_id, metric, observed_at, value, unit, source) VALUES (@station_id, @metric, @observed_at, @value, @unit, 'synthetic')"
);

const seed = db.transaction(() => {
  for (const station of stations) insertStation.run(station);

  const endHour = Math.floor(Date.now() / 3600000) * 3600000;
  for (let index = 0; index < 73; index += 1) {
    const timestamp = new Date(endHour - (72 - index) * 3600000).toISOString();

    stations.forEach((station, stationIndex) => {
      const level = 1.05 + stationIndex * 0.24
        + 0.08 * Math.sin(index / 5 + stationIndex);
      const rain = ((index + stationIndex * 7) % 17 < 3)
        ? 0.4 + ((index + stationIndex) % 4) * 0.35
        : 0;

      insertObservation.run({
        station_id: station.id,
        metric: 'level',
        observed_at: timestamp,
        value: Number(level.toFixed(2)),
        unit: 'm'
      });
      insertObservation.run({
        station_id: station.id,
        metric: 'rain',
        observed_at: timestamp,
        value: Number(rain.toFixed(2)),
        unit: 'mm/h'
      });
    });
  }
});

seed();
const counts = db.prepare('SELECT COUNT(*) AS count FROM observations').get();
console.log('Amostra simulada pronta em ' + filePath + ' (' + counts.count + ' observações).');
db.close();
