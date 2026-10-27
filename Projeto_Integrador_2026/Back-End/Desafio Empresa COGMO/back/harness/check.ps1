$ErrorActionPreference = 'Stop'
$base = 'http://localhost:3000/api'

Write-Host 'Conferindo API em' $base
$health = Invoke-RestMethod "$base/health"
if ($health.status -ne 'ok') { throw 'Health check inesperado.' }

$stationResult = Invoke-RestMethod "$base/stations"
if ($stationResult.data_mode -ne 'simulation') { throw 'A API precisa identificar os dados como simulados.' }
if ($stationResult.stations.Count -lt 1) { throw 'Nenhuma estação retornada. Rode npm run seed.' }

$id = $stationResult.stations[0].id
$summary = Invoke-RestMethod "$base/stations/$id/summary"
if (-not $summary.station -or -not $summary.latest) { throw 'Resumo incompleto.' }

$series = Invoke-RestMethod "$base/stations/$id/series?metric=level&hours=24"
if ($series.metric -ne 'level' -or $series.unit -ne 'm') { throw 'Contrato de nível inesperado.' }
if ($series.points.Count -lt 1) { throw 'Sem pontos na janela. Rode npm run seed.' }

$rain = Invoke-RestMethod "$base/stations/$id/series?metric=rain&hours=24"
if ($rain.metric -ne 'rain' -or $rain.unit -ne 'mm/h') { throw 'Contrato de chuva inesperado.' }

Write-Host 'OK: saúde, lista, resumo, nível e chuva.'
Write-Host 'Valores e locais são amostras sintéticas.'
