# Modelo de dados sugerido

O exercício permite que você ajuste o modelo, desde que explique a decisão e a API continue entregando o contrato.

## Tabelas

~~~text
stations
  id                 chave primária (texto)
  name               obrigatório
  river              obrigatório
  municipality       obrigatório
  active             booleano/integer

observations
  id                 chave primária
  station_id         chave estrangeira -> stations.id
  metric             level ou rain
  observed_at        texto ISO 8601 UTC
  value              número
  unit               m ou mm/h
  source             synthetic
  UNIQUE(station_id, metric, observed_at)
~~~

Cardinalidade: uma estação pode ter várias observações; cada observação pertence a uma estação (1:N). A combinação estação + métrica + horário impede duplicar a mesma observação ao executar o seed de novo.

Índices úteis para consultas: station_id e observed_at; station_id, metric e observed_at.

## Boas decisões para praticar

- Ligue PRAGMA foreign_keys = ON para cada conexão SQLite.
- Use placeholders de SQL para valores recebidos por parâmetros HTTP.
- Guarde as datas em UTC de forma consistente.
- Armazene o valor numérico original e a unidade declarada.
- Não misture nível e chuva na mesma série ou eixo.
- Use uma transação no seed para gravar o conjunto de amostras.
- Anote qualquer mudança de schema no README.

## Fonte da amostra

O script scripts/seed.js cria três estações fictícias e 73 horários de observação por métrica para cada uma. Os valores são determinísticos e gerados localmente. Nenhuma chave externa ou conexão com estação real é necessária.
