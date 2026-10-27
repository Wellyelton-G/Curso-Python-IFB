# Chamadas de exemplo

Inicie a API com npm run dev antes de executar os exemplos.

~~~powershell
$base = 'http://localhost:3000/api'
Invoke-RestMethod "$base/health"
Invoke-RestMethod "$base/stations"
Invoke-RestMethod "$base/stations/EST-01/summary"
Invoke-RestMethod "$base/stations/EST-01/series?metric=level&hours=24"
Invoke-RestMethod "$base/stations/EST-01/series?metric=rain&hours=12"
~~~

Exemplo de resposta resumida:

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

A hora e os valores mudam conforme o seed; o JSON ilustra o formato. Confira também os erros:

~~~powershell
Invoke-RestMethod "$base/stations/NAO-EXISTE/summary"
Invoke-RestMethod "$base/stations/EST-01/series?metric=vento&hours=24"
Invoke-RestMethod "$base/stations/EST-01/series?metric=level&hours=100"
~~~

Essas três chamadas devem falhar com 404, 400 e 400. Os alunos podem adaptar a mensagem, mantendo código HTTP e estrutura do contrato.
