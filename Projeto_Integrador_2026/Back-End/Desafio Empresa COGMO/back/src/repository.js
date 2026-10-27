const { db } = require('./db');

// TODO 1: retorne as estações ativas e a hora da última observação de cada
// estação. Ordene pelo nome. Dica: LEFT JOIN + MAX(observed_at).
function listStations() {
  throw new Error('TODO: implementar listStations');
}

// TODO 2: busque uma estação e a observação mais recente de cada métrica.
// Retorne null se a estação não existir.
function getSummary(stationId) {
  throw new Error('TODO: implementar getSummary');
}

// TODO 3: filtre por estação, métrica e limite de tempo. Retorne pontos em
// ordem crescente. Use parâmetros SQL; nunca concatene os valores da URL.
function getSeries(stationId, metric, fromIso, toIso) {
  throw new Error('TODO: implementar getSeries');
}

function stationExists(stationId) {
  return Boolean(db.prepare('SELECT 1 FROM stations WHERE id = ? AND active = 1').get(stationId));
}

module.exports = { listStations, getSummary, getSeries, stationExists };
