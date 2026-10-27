# Contrato HTTP compartilhado

Esta referência é igual para as trilhas backend e frontend. O backend é o responsável por implementá-la; o frontend pode usar o mock local enquanto a API não está pronta.

## Regras gerais

- Prefixo: /api
- Formato: JSON com UTF-8.
- Horários: ISO 8601 em UTC, com Z, por exemplo 2026-09-28T12:00:00Z.
- Tamanho das janelas: inteiro entre 1 e 72 horas.
- Métricas aceitas: level e rain.
- level é medido em metros (m); rain é medida em milímetros por hora (mm/h).
- Uma lacuna de horário continua sendo uma lacuna. Não preencher por interpolação.
- Este exercício usa dados simulados e fictícios.
- As datas de exemplo abaixo são ilustrativas.

## GET /api/health

Resposta 200:

~~~json
{"status":"ok","database":"ok"}
~~~

## GET /api/stations

Resposta 200:

~~~json
{
  "data_mode": "simulation",
  "stations": [
    {
      "id": "EST-01",
      "name": "Estação Aurora",
      "river": "Rio Aurora",
      "municipality": "Vila Aurora",
      "updated_at": "2026-09-28T12:00:00Z"
    }
  ]
}
~~~

Retorne todas as estações ativas em ordem alfabética pelo nome. A amostra tem três.

## GET /api/stations/{station_id}/summary

Resposta 200:

~~~json
{
  "data_mode": "simulation",
  "message": "Amostra simulada. Não representa condições reais.",
  "station": {
    "id": "EST-01",
    "name": "Estação Aurora",
    "river": "Rio Aurora",
    "municipality": "Vila Aurora"
  },
  "latest": {
    "level_observed_at": "2026-09-28T12:00:00Z",
    "level_m": 1.42,
    "rain_observed_at": "2026-09-28T12:00:00Z",
    "rain_mm_h": 0.6
  }
}
~~~

Cada métrica tem um horário próprio (level_observed_at ou rain_observed_at). Se não houver leitura, seu valor e seu horário podem ser null; não reutilize a hora da outra métrica. Estação desconhecida retorna 404.

## GET /api/stations/{station_id}/series?metric=level&hours=24

Parâmetros:

- metric: level ou rain. Padrão: level.
- hours: janela inteira de 1 a 72. Padrão: 24.

Resposta 200:

~~~json
{
  "data_mode": "simulation",
  "station_id": "EST-01",
  "metric": "level",
  "unit": "m",
  "interval_minutes": 60,
  "from": "2026-09-27T12:00:00Z",
  "to": "2026-09-28T12:00:00Z",
  "points": [
    {"timestamp": "2026-09-27T12:00:00Z", "value": 1.34},
    {"timestamp": "2026-09-27T13:00:00Z", "value": 1.37}
  ]
}
~~~

Retorne apenas observações dentro da janela e em ordem ascendente. Os campos from e to informam os limites solicitados; podem não coincidir com horários existentes. Resposta sem pontos usa points: [].

## Erros

Use o formato abaixo para estação inexistente (404), métrica inválida (400) ou horas fora do limite (400):

~~~json
{
  "error": {
    "code": "station_not_found",
    "message": "Estação não encontrada."
  }
}
~~~

Sugestões de códigos: station_not_found, invalid_metric, invalid_hours, internal_error. Não envie stack trace ao cliente.

## Conferência manual

~~~powershell
Invoke-RestMethod http://localhost:3000/api/health
Invoke-RestMethod http://localhost:3000/api/stations
Invoke-RestMethod 'http://localhost:3000/api/stations/EST-01/summary'
Invoke-RestMethod 'http://localhost:3000/api/stations/EST-01/series?metric=level&hours=24'
Invoke-RestMethod 'http://localhost:3000/api/stations/EST-01/series?metric=rain&hours=12'
~~~
