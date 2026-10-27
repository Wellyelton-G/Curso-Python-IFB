require('dotenv').config();

const express = require('express');
const cors = require('cors');
const repository = require('./repository');

const app = express();
const port = Number(process.env.PORT || 3000);
const origin = process.env.CORS_ORIGIN || 'http://localhost:5173';

app.use(cors({ origin }));
app.use(express.json());

function sendError(res, status, code, message) {
  return res.status(status).json({ error: { code, message } });
}

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', database: 'ok' });
});

app.get('/api/stations', (_req, res, next) => {
  try {
    res.json({ data_mode: 'simulation', stations: repository.listStations() });
  } catch (error) {
    next(error);
  }
});

app.get('/api/stations/:stationId/summary', (req, res, next) => {
  try {
    const result = repository.getSummary(req.params.stationId);
    if (!result) return sendError(res, 404, 'station_not_found', 'Estação não encontrada.');
    res.json({
      data_mode: 'simulation',
      message: 'Amostra simulada. Não representa condições reais.',
      station: result.station,
      latest: result.latest
    });
  } catch (error) {
    next(error);
  }
});

app.get('/api/stations/:stationId/series', (req, res, next) => {
  const metric = req.query.metric || 'level';
  const hoursText = req.query.hours || '24';
  const hours = Number(hoursText);

  if (!['level', 'rain'].includes(metric)) {
    return sendError(res, 400, 'invalid_metric', 'metric deve ser level ou rain.');
  }
  if (!Number.isInteger(hours) || hours < 1 || hours > 72) {
    return sendError(res, 400, 'invalid_hours', 'hours deve ser um inteiro entre 1 e 72.');
  }

  try {
    if (!repository.stationExists(req.params.stationId)) {
      return sendError(res, 404, 'station_not_found', 'Estação não encontrada.');
    }

    const to = new Date();
    to.setUTCMinutes(0, 0, 0);
    const from = new Date(to.getTime() - hours * 60 * 60 * 1000);
    const fromIso = from.toISOString();
    const toIso = to.toISOString();
    const rows = repository.getSeries(req.params.stationId, metric, fromIso, toIso);
    const unit = metric === 'level' ? 'm' : 'mm/h';

    res.json({
      data_mode: 'simulation',
      station_id: req.params.stationId,
      metric,
      unit,
      interval_minutes: 60,
      from: fromIso,
      to: toIso,
      points: rows
    });
  } catch (error) {
    next(error);
  }
});

app.use((_req, res) => sendError(res, 404, 'not_found', 'Rota não encontrada.'));
app.use((error, _req, res, _next) => {
  // O detalhe fica no terminal para ajudar no desenvolvimento, não na resposta.
  console.error(error);
  sendError(res, 500, 'internal_error', 'Não foi possível carregar os dados.');
});

app.listen(port, () => {
  console.log('API demonstrativa em http://localhost:' + port);
});
