# Guia de construção: Desafio Backend COGMO com Python e Django

Este guia ensina, passo a passo e do zero, a construir em **Python + Django + SQLite** a API de monitoramento de rios e chuva pedida no desafio da Cogmo Technology.

Ele substitui o starter em Node.js/Express, mas cumpre **o mesmo contrato** descrito em `back/docs/CONTRATO_API.md`. Por isso, o roteiro oficial de conferência (`back/harness/check.ps1`) funciona sem nenhuma alteração.

> **Antes de começar:** o enunciado indica Node.js, Express e SQLite como *tecnologias de referência* e permite mudar a organização "desde que mantenha o contrato". Mesmo assim, **confirme com a Cogmo** que aceitam a entrega em Python antes de investir as horas do desafio.

> **Dados simulados:** todas as estações e leituras deste projeto são fictícias. Não representam rios reais e não servem para alertas ou decisões. A API deve sempre deixar isso claro (`"data_mode": "simulation"`).

---

## Sumário

1. [O que vamos construir](#1-o-que-vamos-construir)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Etapa 1: criar o ambiente e o projeto](#3-etapa-1-criar-o-ambiente-e-o-projeto)
4. [Etapa 2: configurar o Django](#4-etapa-2-configurar-o-django-configsettingspy)
5. [Etapa 3: modelar o banco](#5-etapa-3-modelar-o-banco-monitoringmodelspy)
6. [Etapa 4: seed repetível](#6-etapa-4-seed-repetível)
7. [Etapa 5: funções auxiliares](#7-etapa-5-funções-auxiliares-monitoringutilspy)
8. [Etapa 6: consultas (repository)](#8-etapa-6-consultas-ao-banco-monitoringrepositorypy)
9. [Etapa 7: rotas (views e urls)](#9-etapa-7-rotas-views-e-urls)
10. [Etapa 8: erro 500 em JSON](#10-etapa-8-erro-500-em-json-monitoringmiddlewarepy)
11. [Etapa 9: rodar e conferir](#11-etapa-9-rodar-e-conferir)
12. [Etapa 10: testes automáticos](#12-etapa-10-testes-automáticos-monitoringtestspy)
13. [Etapa 11: README, Git e entrega](#13-etapa-11-readme-git-e-entrega)
14. [Checklist final](#14-checklist-final)
15. [Problemas comuns](#15-problemas-comuns)
16. [Preparando a apresentação](#16-preparando-a-apresentação)
17. [Adicionais: extras para se destacar](#17-adicionais-extras-para-se-destacar)

---

## 1. O que vamos construir

Uma API HTTP que guarda **estações** e **observações** (nível do rio e chuva) em SQLite e entrega os dados que uma tela de monitoramento precisa.

| Método e rota | O que devolve |
|---|---|
| `GET /api/health` | `{"status":"ok","database":"ok"}` |
| `GET /api/stations` | Estações ativas, em ordem alfabética, com a hora da última leitura |
| `GET /api/stations/{id}/summary` | Dados da estação e a leitura mais recente de nível e de chuva |
| `GET /api/stations/{id}/series?metric=level&hours=24` | Histórico de uma métrica numa janela de 1 a 72 horas |

### Como as peças se encaixam

```text
Navegador / frontend
        │  GET /api/stations/EST-01/series?metric=rain&hours=12
        ▼
config/urls.py ──► monitoring/urls.py      (qual função atende cada endereço)
                          │
                          ▼
                 monitoring/views.py       (valida parâmetros, monta o JSON, define o HTTP)
                          │
                          ▼
                 monitoring/repository.py  (consultas ao banco, sempre parametrizadas)
                          │
                          ▼
                 monitoring/models.py ──► SQLite (data/monitoramento.sqlite)
```

Separar **rotas** (`views.py`) de **consultas** (`repository.py`) é uma exigência do desafio (tarefa 9).

### Equivalência com o starter em Node.js

| Starter Node.js | Neste guia (Django) |
|---|---|
| `src/server.js` (Express) | `monitoring/views.py` + `monitoring/urls.py` |
| `src/repository.js` | `monitoring/repository.py` |
| `src/db.js` + `db/schema.sql` | `monitoring/models.py` + migrations (o SQL é gerado com `sqlmigrate`) |
| `scripts/seed.js` | `monitoring/management/commands/seed.py` |
| `npm install` | `pip install -r requirements.txt` |
| `npm run seed` | `python manage.py seed` |
| `npm run dev` | `python manage.py runserver 3000` |
| `.env` com `dotenv` | `.env` com `python-dotenv` |
| `cors` | `django-cors-headers` |

### Estrutura final de pastas

```text
back-django/
├── .env.example
├── .gitignore
├── README.md
├── manage.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db/
│   └── schema.sql            ← gerado na Etapa 3, para a entrega
├── harness/
│   └── check.ps1             ← copiado de back/harness
└── monitoring/
    ├── __init__.py
    ├── apps.py
    ├── middleware.py
    ├── models.py
    ├── repository.py
    ├── tests.py
    ├── urls.py
    ├── utils.py
    ├── views.py
    ├── management/
    │   ├── __init__.py
    │   └── commands/
    │       ├── __init__.py
    │       └── seed.py
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py   ← gerado pelo Django
```

### Plano de tempo sugerido (16 a 24 h)

| Etapa | Tempo | Seções deste guia |
|---|---|---|
| 1. Explorar | 3-4 h | Ler `CONTRATO_API.md` e `MODELO_DE_DADOS.md`; seções 1 a 4 |
| 2. Preparar | 3-5 h | Seções 5 e 6 (modelos, migrations e seed) |
| 3. Construir | 5-7 h | Seções 7 a 10 (consultas, rotas e erros) |
| 4. Conferir | 3-5 h | Seções 11 e 12 (harness e testes) |
| 5. Apresentar | 2-3 h | Seções 13 a 16 (README, Git e apresentação) |

---

## 2. Pré-requisitos

- **Python 3.10 ou superior** (o Django 5.2 exige). Confira com `python --version`.
- **pip**, que já vem com o Python.
- **Git**.
- Um editor (VS Code, por exemplo).
- Windows PowerShell (os comandos abaixo usam PowerShell, como o resto do desafio).

Não é preciso nenhuma chave de API, conta ou serviço externo.

---

## 3. Etapa 1: criar o ambiente e o projeto

### 3.1 Criar a pasta e o ambiente virtual

O ambiente virtual (`.venv`) isola as bibliotecas deste projeto das do resto do computador.

```powershell
# dentro da pasta "Desafio Empresa COGMO"
mkdir back-django
cd back-django

python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação ("execution of scripts is disabled"), rode antes:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Com o ambiente ativo, o terminal mostra `(.venv)` no início da linha.

### 3.2 Instalar as dependências

Crie o arquivo `requirements.txt`:

```text
Django>=5.2,<6
django-cors-headers>=4.9
python-dotenv>=1.0
```

E instale:

```powershell
python -m pip install -r requirements.txt
```

| Biblioteca | Para que serve |
|---|---|
| Django | Framework web: rotas, ORM (acesso ao banco), migrations e comandos |
| django-cors-headers | Permite que a página do frontend (`localhost:5173`) chame a API |
| python-dotenv | Lê configurações do arquivo `.env` |

### 3.3 Criar o projeto e o app

```powershell
django-admin startproject config .
python manage.py startapp monitoring
```

- O **projeto** `config` guarda as configurações gerais.
- O **app** `monitoring` guarda o código do monitoramento (modelos, rotas e consultas).
- O ponto (`.`) no fim do primeiro comando cria o projeto na pasta atual, sem uma subpasta extra.

Apague o arquivo `monitoring/admin.py`: não vamos usar o painel administrativo.

Crie as pastas do comando de seed, cada uma com um arquivo `__init__.py` vazio:

```powershell
mkdir monitoring\management\commands
New-Item monitoring\management\__init__.py -ItemType File
New-Item monitoring\management\commands\__init__.py -ItemType File
```

### 3.4 Arquivos `.env.example`, `.env` e `.gitignore`

`.env.example` vai para o Git e mostra quais configurações existem:

```text
DB_PATH=./data/monitoramento.sqlite
CORS_ORIGIN=http://localhost:5173
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=troque-esta-chave-local
```

Copie para o `.env`, que é o arquivo usado de verdade e **não vai para o Git**:

```powershell
Copy-Item .env.example .env
```

`.gitignore`:

```text
.venv/
__pycache__/
*.pyc
.env
data/
*.sqlite
*.sqlite3
```

> O banco (`data/`) e o `.env` ficam fora do repositório, como pede o README do desafio. Quem baixar o projeto recria o banco com `migrate` e `seed`.

---

## 4. Etapa 2: configurar o Django (`config/settings.py`)

Substitua todo o conteúdo de `config/settings.py` por:

```python
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'apenas-para-desenvolvimento-local')
DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'corsheaders',
    'monitoring',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'monitoring.middleware.JsonErrorMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DB_PATH = Path(os.getenv('DB_PATH', BASE_DIR / 'data' / 'monitoramento.sqlite'))
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

CORS_ALLOWED_ORIGINS = [os.getenv('CORS_ORIGIN', 'http://localhost:5173')]
CORS_ALLOW_METHODS = ['GET', 'OPTIONS']
```

O que cada parte faz:

- **`INSTALLED_APPS`** tem só o necessário. Sem `admin`, `auth` e `sessions`, o banco fica com apenas as tabelas do desafio (e a tabela interna `django_migrations`).
- **`DB_PATH`** permite escolher outro caminho para o banco, como pede o README do desafio. A pasta `data/` é criada automaticamente.
- **`TIME_ZONE = 'UTC'` e `USE_TZ = True`** fazem o Django trabalhar sempre em UTC. Isso atende à regra "datas ISO 8601 em UTC".
- **`CORS_ALLOWED_ORIGINS`** libera a página do frontend local.
- **`JsonErrorMiddleware`** será criado na Etapa 8. Até lá, o servidor não sobe; isso é esperado.

> **Chave estrangeira no SQLite:** o desafio pede `PRAGMA foreign_keys = ON` em cada conexão. O Django já faz isso automaticamente para o SQLite. Vale citar isso no README e na apresentação.

Agora, `config/urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path('api/', include('monitoring.urls')),
]
```

Todas as rotas da API ficam no app e começam com `/api/`, o prefixo exigido pelo contrato.

---

## 5. Etapa 3: modelar o banco (`monitoring/models.py`)

### 5.1 Entendendo o modelo

```text
┌────────────────────────┐          ┌──────────────────────────────────┐
│ stations               │          │ observations                     │
├────────────────────────┤ 1     N  ├──────────────────────────────────┤
│ id (PK, texto)         │◄─────────│ id (PK, inteiro)                 │
│ name                   │          │ station_id (FK → stations.id)    │
│ river                  │          │ metric  ('level' | 'rain')       │
│ municipality           │          │ observed_at (data/hora UTC)      │
│ active                 │          │ value                            │
└────────────────────────┘          │ unit    ('m' | 'mm/h')           │
                                    │ source  ('synthetic')            │
                                    │ UNIQUE(station_id, metric,       │
                                    │        observed_at)              │
                                    └──────────────────────────────────┘
```

- **Chave primária (PK):** identificador único de cada linha.
- **Chave estrangeira (FK):** `observations.station_id` aponta para `stations.id`. Assim, toda observação pertence a uma estação que existe.
- **Cardinalidade 1:N:** uma estação tem muitas observações; cada observação tem uma estação.
- **UNIQUE (estação + métrica + horário):** impede gravar a mesma leitura duas vezes. É isso que torna o seed repetível.
- **CHECK:** o banco recusa métricas e unidades fora da lista.
- **Índice (estação, métrica, horário):** acelera a busca da série e da última leitura.

### 5.2 O código

```python
from django.db import models


class Station(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=120)
    river = models.CharField(max_length=120)
    municipality = models.CharField(max_length=120)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'stations'
        ordering = ['name']

    def __str__(self):
        return f'{self.id} - {self.name}'


class Observation(models.Model):
    class Metric(models.TextChoices):
        LEVEL = 'level', 'Nível'
        RAIN = 'rain', 'Chuva'

    class Unit(models.TextChoices):
        METERS = 'm', 'metros'
        MM_PER_HOUR = 'mm/h', 'milímetros por hora'

    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name='observations'
    )
    metric = models.CharField(max_length=10, choices=Metric.choices)
    observed_at = models.DateTimeField()
    value = models.FloatField()
    unit = models.CharField(max_length=10, choices=Unit.choices)
    source = models.CharField(max_length=20, default='synthetic')

    class Meta:
        db_table = 'observations'
        constraints = [
            models.UniqueConstraint(
                fields=['station', 'metric', 'observed_at'],
                name='uniq_observation_station_metric_time',
            ),
            models.CheckConstraint(
                condition=models.Q(metric__in=['level', 'rain']),
                name='check_observation_metric',
            ),
            models.CheckConstraint(
                condition=models.Q(unit__in=['m', 'mm/h']),
                name='check_observation_unit',
            ),
        ]
        indexes = [
            models.Index(
                fields=['station', 'metric', 'observed_at'],
                name='idx_obs_station_metric_time',
            ),
        ]

    def __str__(self):
        return f'{self.station_id} {self.metric} {self.observed_at:%Y-%m-%d %H:%M} = {self.value}'
```

Pontos importantes:

- `db_table = 'stations'` e `db_table = 'observations'` mantêm os mesmos nomes de tabela do `schema.sql` original.
- O campo `station` vira a coluna `station_id` no banco.
- `related_name='observations'` permite escrever `estacao.observations.all()` e usar `observations__observed_at` nas consultas.

### 5.3 Criar as tabelas (migrations)

```powershell
python manage.py makemigrations monitoring
python manage.py migrate
```

- `makemigrations` lê `models.py` e gera `monitoring/migrations/0001_initial.py`, uma receita de criação das tabelas.
- `migrate` executa a receita no SQLite e cria `data/monitoramento.sqlite`.

### 5.4 Gerar o `db/schema.sql` para a entrega

O desafio pede o schema SQL. O Django mostra o SQL exato que ele executou:

```powershell
mkdir db
python manage.py sqlmigrate monitoring 0001 | Out-File -Encoding utf8 db\schema.sql
```

O resultado será parecido com:

```sql
CREATE TABLE "stations" ("id" varchar(20) NOT NULL PRIMARY KEY, "name" varchar(120) NOT NULL,
  "river" varchar(120) NOT NULL, "municipality" varchar(120) NOT NULL, "active" bool NOT NULL);

CREATE TABLE "observations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "metric" varchar(10) NOT NULL, "observed_at" datetime NOT NULL, "value" real NOT NULL,
  "unit" varchar(10) NOT NULL, "source" varchar(20) NOT NULL,
  "station_id" varchar(20) NOT NULL REFERENCES "stations" ("id") DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "uniq_observation_station_metric_time" UNIQUE ("station_id", "metric", "observed_at"),
  CONSTRAINT "check_observation_metric" CHECK ("metric" IN ('level', 'rain')),
  CONSTRAINT "check_observation_unit" CHECK ("unit" IN ('m', 'mm/h')));

CREATE INDEX "idx_obs_station_metric_time" ON "observations" ("station_id", "metric", "observed_at");
```

### 5.5 Diferenças em relação ao schema original (registre no README)

O `MODELO_DE_DADOS.md` permite ajustes "desde que você explique a decisão". Estas são as diferenças desta versão:

| Original | Nesta versão | Por quê |
|---|---|---|
| `observed_at` como texto ISO com `Z` | Coluna `datetime` do Django, gravada em UTC (`2026-09-28 12:00:00`) | O Django converte para `datetime` do Python e compara datas com segurança. A API formata a saída com `Z`. |
| `ON DELETE CASCADE` no banco | `on_delete=models.CASCADE` no Django | O Django apaga as observações ao apagar a estação pelo ORM. |
| `PRAGMA foreign_keys = ON` no `db.js` | Feito automaticamente pelo Django | O backend SQLite do Django liga o PRAGMA em toda conexão. |

---

## 6. Etapa 4: seed repetível

O **seed** é a carga de dados de demonstração. Ele precisa ser **idempotente**: rodar duas vezes não pode duplicar nada.

No Django, criamos um **comando de gerenciamento**, que é o equivalente ao `npm run seed`.

Crie `monitoring/management/commands/seed.py`:

```python
import math
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from monitoring.models import Observation, Station
from monitoring.utils import current_hour_utc

STATIONS = [
    {'id': 'EST-01', 'name': 'Estação Aurora', 'river': 'Rio Aurora', 'municipality': 'Vila Aurora'},
    {'id': 'EST-02', 'name': 'Estação Vale Verde', 'river': 'Rio Verde', 'municipality': 'Vale Verde'},
    {'id': 'EST-03', 'name': 'Estação Campo Alto', 'river': 'Rio do Campo', 'municipality': 'Campo Alto'},
]


class Command(BaseCommand):
    help = 'Carrega estações e observações sintéticas (pode ser executado várias vezes).'

    @transaction.atomic
    def handle(self, *args, **options):
        for data in STATIONS:
            Station.objects.get_or_create(id=data['id'], defaults=data)

        end_hour = current_hour_utc()
        observations = []
        for index in range(73):
            observed_at = end_hour - timedelta(hours=72 - index)
            for station_index, data in enumerate(STATIONS):
                level = 1.05 + station_index * 0.24 + 0.08 * math.sin(index / 5 + station_index)
                if (index + station_index * 7) % 17 < 3:
                    rain = 0.4 + ((index + station_index) % 4) * 0.35
                else:
                    rain = 0
                observations.append(Observation(
                    station_id=data['id'], metric='level', observed_at=observed_at,
                    value=round(level, 2), unit='m',
                ))
                observations.append(Observation(
                    station_id=data['id'], metric='rain', observed_at=observed_at,
                    value=round(rain, 2), unit='mm/h',
                ))

        # ignore_conflicts=True vira INSERT OR IGNORE: a UNIQUE impede duplicatas.
        Observation.objects.bulk_create(observations, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f'Amostra simulada pronta ({Station.objects.count()} estações, '
            f'{Observation.objects.count()} observações).'
        ))
```

Como ele garante que não haverá duplicatas:

| Técnica | Efeito |
|---|---|
| `get_or_create` | Só cria a estação se o `id` ainda não existir |
| `bulk_create(..., ignore_conflicts=True)` | Gera `INSERT OR IGNORE`; se a combinação estação + métrica + horário já existe, a linha é ignorada |
| `@transaction.atomic` | Grava tudo ou nada, como pede o `MODELO_DE_DADOS.md` |

Os valores usam as mesmas fórmulas do `seed.js` original: 3 estações × 73 horários × 2 métricas = **438 observações**.

> O seed depende de `monitoring/utils.py` (próxima etapa). Crie esse arquivo antes de rodar o comando.

Para rodar e provar que é repetível (guarde esta saída como **evidência do seed**):

```powershell
python manage.py seed
python manage.py seed
```

As duas execuções devem mostrar `438 observações`. Se você rodar de novo **horas depois**, o total cresce, porque surgem horários novos. Isso é correto: os horários antigos não são duplicados.

---

## 7. Etapa 5: funções auxiliares (`monitoring/utils.py`)

Funções pequenas usadas em mais de um lugar:

```python
from datetime import timedelta, timezone

from django.http import JsonResponse
from django.utils import timezone as dj_timezone

UNITS = {'level': 'm', 'rain': 'mm/h'}


def to_iso_utc(value):
    """Converte datetime em texto ISO 8601 UTC terminado em Z (ou None)."""
    if value is None:
        return None
    return value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def current_hour_utc():
    """Agora em UTC, com minutos e segundos zerados."""
    return dj_timezone.now().replace(minute=0, second=0, microsecond=0)


def window(hours):
    """Devolve (inicio, fim) para as últimas `hours` horas."""
    end = current_hour_utc()
    return end - timedelta(hours=hours), end


def json_response(data, status=200):
    """JsonResponse em UTF-8 legível (mantém acentos sem \\u00e7)."""
    return JsonResponse(data, status=status, json_dumps_params={'ensure_ascii': False})


def error_response(status, code, message):
    return json_response({'error': {'code': code, 'message': message}}, status=status)
```

- **`to_iso_utc`** garante o formato do contrato: `2026-09-28T12:00:00Z`. O `isoformat()` do Python geraria `+00:00` no lugar de `Z`, por isso usamos `strftime`.
- **`UNITS`** é a lista de métricas aceitas e serve também para validar o parâmetro `metric`.
- **`error_response`** padroniza o JSON de erro `{"error": {"code": ..., "message": ...}}`.

---

## 8. Etapa 6: consultas ao banco (`monitoring/repository.py`)

Este arquivo corresponde aos três TODOs do `src/repository.js` original. **Só ele** acessa os models; as views apenas o chamam.

```python
"""Consultas ao banco. As views não acessam os models diretamente."""
from django.db.models import Max

from .models import Observation, Station
from .utils import to_iso_utc


def list_stations():
    stations = (
        Station.objects.filter(active=True)
        .annotate(updated_at=Max('observations__observed_at'))
        .order_by('name')
    )
    return [
        {
            'id': s.id,
            'name': s.name,
            'river': s.river,
            'municipality': s.municipality,
            'updated_at': to_iso_utc(s.updated_at),
        }
        for s in stations
    ]


def _latest(station, metric):
    return (
        Observation.objects.filter(station=station, metric=metric)
        .order_by('-observed_at')
        .first()
    )


def get_summary(station_id):
    station = Station.objects.filter(id=station_id, active=True).first()
    if station is None:
        return None

    level = _latest(station, 'level')
    rain = _latest(station, 'rain')
    return {
        'station': {
            'id': station.id,
            'name': station.name,
            'river': station.river,
            'municipality': station.municipality,
        },
        'latest': {
            'level_observed_at': to_iso_utc(level.observed_at) if level else None,
            'level_m': level.value if level else None,
            'rain_observed_at': to_iso_utc(rain.observed_at) if rain else None,
            'rain_mm_h': rain.value if rain else None,
        },
    }


def get_series(station_id, metric, start, end):
    rows = (
        Observation.objects.filter(
            station_id=station_id,
            metric=metric,
            observed_at__gte=start,
            observed_at__lte=end,
        )
        .order_by('observed_at')
        .values('observed_at', 'value')
    )
    return [{'timestamp': to_iso_utc(r['observed_at']), 'value': r['value']} for r in rows]


def station_exists(station_id):
    return Station.objects.filter(id=station_id, active=True).exists()
```

### O SQL por trás de cada consulta

O ORM do Django gera SQL **parametrizado**: os valores da URL vão separados do comando, nunca concatenados. Isso cumpre a tarefa 9 e evita SQL injection. Para a apresentação, este é o SQL equivalente:

| Função | SQL equivalente |
|---|---|
| `list_stations` | `SELECT s.*, MAX(o.observed_at) AS updated_at FROM stations s LEFT JOIN observations o ON o.station_id = s.id WHERE s.active = 1 GROUP BY s.id ORDER BY s.name` |
| `_latest` | `SELECT * FROM observations WHERE station_id = ? AND metric = ? ORDER BY observed_at DESC LIMIT 1` |
| `get_series` | `SELECT observed_at, value FROM observations WHERE station_id = ? AND metric = ? AND observed_at >= ? AND observed_at <= ? ORDER BY observed_at ASC` |
| `station_exists` | `SELECT 1 FROM stations WHERE id = ? AND active = 1 LIMIT 1` |

Para ver o SQL real gerado, use o shell do Django:

```powershell
python manage.py shell
```

```python
from monitoring.models import Observation
qs = Observation.objects.filter(station_id='EST-01', metric='rain').order_by('observed_at')
print(qs.query)
```

### Regras de dados atendidas aqui

- **Cada métrica com seu próprio horário:** `_latest` busca nível e chuva separadamente. Se não houver leitura, o valor e o horário ficam `None` (vira `null` no JSON); nunca se reaproveita a hora da outra métrica.
- **Ordem crescente:** `.order_by('observed_at')`.
- **Lacunas preservadas:** devolvemos só as linhas que existem. Nada de criar pontos para "completar" o gráfico.
- **Série vazia:** se não houver linhas, a lista volta vazia (`[]`).
- **Estações ativas e ordem alfabética:** `filter(active=True)` e `order_by('name')`.

---

## 9. Etapa 7: rotas (views e urls)

### 9.1 `monitoring/views.py`

As views recebem o pedido, **validam** os parâmetros, chamam o repository e definem o código HTTP.

```python
from django.db import connection
from django.views.decorators.http import require_GET

from . import repository
from .utils import UNITS, error_response, json_response, to_iso_utc, window

SIMULATION_MESSAGE = 'Amostra simulada. Não representa condições reais.'


@require_GET
def health(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return json_response({'status': 'ok', 'database': 'ok'})


@require_GET
def stations(request):
    return json_response({
        'data_mode': 'simulation',
        'stations': repository.list_stations(),
    })


@require_GET
def station_summary(request, station_id):
    result = repository.get_summary(station_id)
    if result is None:
        return error_response(404, 'station_not_found', 'Estação não encontrada.')
    return json_response({
        'data_mode': 'simulation',
        'message': SIMULATION_MESSAGE,
        'station': result['station'],
        'latest': result['latest'],
    })


@require_GET
def station_series(request, station_id):
    metric = request.GET.get('metric') or 'level'
    hours_text = request.GET.get('hours') or '24'

    if metric not in UNITS:
        return error_response(400, 'invalid_metric', 'metric deve ser level ou rain.')
    try:
        hours = int(hours_text)
    except ValueError:
        hours = 0
    if not 1 <= hours <= 72:
        return error_response(400, 'invalid_hours', 'hours deve ser um inteiro entre 1 e 72.')

    if not repository.station_exists(station_id):
        return error_response(404, 'station_not_found', 'Estação não encontrada.')

    start, end = window(hours)
    return json_response({
        'data_mode': 'simulation',
        'station_id': station_id,
        'metric': metric,
        'unit': UNITS[metric],
        'interval_minutes': 60,
        'from': to_iso_utc(start),
        'to': to_iso_utc(end),
        'points': repository.get_series(station_id, metric, start, end),
    })


def not_found(request, unknown_path=None):
    return error_response(404, 'not_found', 'Rota não encontrada.')
```

Detalhes que valem pontos:

- **Padrões do contrato:** sem `metric`, usa `level`; sem `hours`, usa `24`.
- **Validação de `hours`:** `int('abc')` e `int('1.5')` dão erro e viram `invalid_hours`; `0`, `-3` e `100` falham no teste `1 <= hours <= 72`.
- **Ordem das validações:** primeiro os parâmetros (400), depois a estação (404).
- **`from` e `to`** são os limites pedidos, arredondados para a hora cheia. Não precisam coincidir com leituras existentes.
- **`@require_GET`:** outros métodos (POST, DELETE) recebem 405.
- **Unidade sempre presente:** `unit` é `m` para nível e `mm/h` para chuva.

### 9.2 `monitoring/urls.py`

```python
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('health', views.health),
    path('stations', views.stations),
    path('stations/<str:station_id>/summary', views.station_summary),
    path('stations/<str:station_id>/series', views.station_series),
    re_path(r'^(?P<unknown_path>.*)$', views.not_found),
]
```

- As rotas **não terminam com barra**, exatamente como no contrato (`/api/stations`, e não `/api/stations/`).
- A última linha captura qualquer outro endereço dentro de `/api/` e responde 404 **em JSON**, em vez da página HTML padrão do Django.

---

## 10. Etapa 8: erro 500 em JSON (`monitoring/middleware.py`)

O contrato pede: em erro inesperado, responder 500 **sem** mostrar detalhes internos (stack trace). Um middleware intercepta qualquer exceção não tratada:

```python
import logging

from .utils import error_response

logger = logging.getLogger(__name__)


class JsonErrorMiddleware:
    """Transforma exceções não tratadas em JSON 500, sem stack trace."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception('Erro inesperado em %s', request.path)
        return error_response(500, 'internal_error', 'Não foi possível carregar os dados.')
```

O detalhe do erro aparece **no terminal** (para quem desenvolve), mas o cliente recebe apenas:

```json
{"error": {"code": "internal_error", "message": "Não foi possível carregar os dados."}}
```

---

## 11. Etapa 9: rodar e conferir

### 11.1 Subir o servidor

```powershell
python manage.py check          # procura erros de configuração
python manage.py migrate
python manage.py seed
python manage.py runserver 3000
```

A API sobe em `http://localhost:3000`. Abra `http://localhost:3000/api/health` no navegador: deve aparecer `{"status": "ok", "database": "ok"}`.

> Use a porta **3000**: o harness e o frontend do desafio esperam essa porta.

### 11.2 Rodar o roteiro oficial do desafio

Copie `back/harness/check.ps1` para `back-django/harness/` e, **em outro terminal**, com o servidor ligado:

```powershell
.\harness\check.ps1
```

Saída esperada:

```text
Conferindo API em http://localhost:3000/api
OK: saúde, lista, resumo, nível e chuva.
Valores e locais são amostras sintéticas.
```

### 11.3 Chamadas manuais (rotas válidas)

```powershell
$base = 'http://localhost:3000/api'
Invoke-RestMethod "$base/health"
Invoke-RestMethod "$base/stations"
Invoke-RestMethod "$base/stations/EST-01/summary"
Invoke-RestMethod "$base/stations/EST-01/series?metric=level&hours=24"
Invoke-RestMethod "$base/stations/EST-01/series?metric=rain&hours=12"
```

Exemplo real de resposta de série (os horários mudam conforme o momento do seed):

```json
{
  "data_mode": "simulation",
  "station_id": "EST-01",
  "metric": "rain",
  "unit": "mm/h",
  "interval_minutes": 60,
  "from": "2026-10-27T13:00:00Z",
  "to": "2026-10-27T16:00:00Z",
  "points": [
    {"timestamp": "2026-10-27T13:00:00Z", "value": 0.75},
    {"timestamp": "2026-10-27T14:00:00Z", "value": 1.1},
    {"timestamp": "2026-10-27T15:00:00Z", "value": 0.0},
    {"timestamp": "2026-10-27T16:00:00Z", "value": 0.0}
  ]
}
```

### 11.4 Chamadas manuais (erros)

O `Invoke-RestMethod` lança exceção em respostas 4xx. Para ver o código e o corpo, use `curl.exe`:

```powershell
curl.exe -i "http://localhost:3000/api/stations/NAO-EXISTE/summary"
curl.exe -i "http://localhost:3000/api/stations/EST-01/series?metric=vento&hours=24"
curl.exe -i "http://localhost:3000/api/stations/EST-01/series?metric=level&hours=100"
```

| Chamada | HTTP | `error.code` |
|---|---|---|
| `/stations/NAO-EXISTE/summary` | 404 | `station_not_found` |
| `/stations/NAO-EXISTE/series` | 404 | `station_not_found` |
| `/stations/EST-01/series?metric=vento` | 400 | `invalid_metric` |
| `/stations/EST-01/series?hours=100` | 400 | `invalid_hours` |
| `/stations/EST-01/series?hours=abc` | 400 | `invalid_hours` |
| `/api/rota-inexistente` | 404 | `not_found` |

Guarde essas saídas: elas são os **exemplos de chamadas válidas e inválidas** pedidos na entrega.

### 11.5 Olhar o banco diretamente (opcional)

```powershell
python manage.py dbshell
```

```sql
SELECT COUNT(*) FROM observations;
SELECT station_id, metric, COUNT(*) FROM observations GROUP BY station_id, metric;
.quit
```

> O `dbshell` precisa do programa `sqlite3` instalado. Sem ele, use o `python manage.py shell` ou uma extensão de SQLite no VS Code.

---

## 12. Etapa 10: testes automáticos (`monitoring/tests.py`)

Testes provam que as regras continuam valendo depois de cada mudança. O Django cria um **banco temporário** só para os testes, sem mexer no seu banco de desenvolvimento.

```python
from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from .models import Observation, Station
from .utils import current_hour_utc


class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed', verbosity=0)

    def test_seed_e_idempotente(self):
        antes = Observation.objects.count()
        call_command('seed', verbosity=0)
        self.assertEqual(Observation.objects.count(), antes)
        self.assertEqual(Station.objects.count(), 3)

    def test_lista_estacoes_em_ordem_alfabetica(self):
        body = self.client.get('/api/stations').json()
        self.assertEqual(body['data_mode'], 'simulation')
        nomes = [s['name'] for s in body['stations']]
        self.assertEqual(nomes, sorted(nomes))
        self.assertTrue(body['stations'][0]['updated_at'].endswith('Z'))

    def test_resumo_tem_horario_por_metrica(self):
        body = self.client.get('/api/stations/EST-01/summary').json()
        self.assertEqual(body['station']['id'], 'EST-01')
        self.assertIn('level_observed_at', body['latest'])
        self.assertIn('rain_mm_h', body['latest'])

    def test_serie_ordenada_e_com_unidade(self):
        body = self.client.get('/api/stations/EST-01/series?metric=level&hours=24').json()
        self.assertEqual(body['unit'], 'm')
        horarios = [p['timestamp'] for p in body['points']]
        self.assertEqual(horarios, sorted(horarios))
        self.assertTrue(all(h.endswith('Z') for h in horarios))

    def test_lacuna_nao_e_preenchida(self):
        apagado = current_hour_utc() - timedelta(hours=2)
        Observation.objects.filter(station_id='EST-01', metric='rain', observed_at=apagado).delete()
        body = self.client.get('/api/stations/EST-01/series?metric=rain&hours=4').json()
        self.assertEqual(len(body['points']), 4)

    def test_serie_vazia_retorna_lista_vazia(self):
        Observation.objects.filter(station_id='EST-02').delete()
        body = self.client.get('/api/stations/EST-02/series?hours=6').json()
        self.assertEqual(body['points'], [])

    def test_erros(self):
        casos = [
            ('/api/stations/NAO-EXISTE/summary', 404, 'station_not_found'),
            ('/api/stations/NAO-EXISTE/series', 404, 'station_not_found'),
            ('/api/stations/EST-01/series?metric=vento', 400, 'invalid_metric'),
            ('/api/stations/EST-01/series?hours=0', 400, 'invalid_hours'),
            ('/api/stations/EST-01/series?hours=73', 400, 'invalid_hours'),
            ('/api/stations/EST-01/series?hours=abc', 400, 'invalid_hours'),
        ]
        for url, status, code in casos:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()['error']['code'], code)

    def test_erro_inesperado_vira_500_sem_detalhes(self):
        with patch('monitoring.repository.list_stations', side_effect=RuntimeError('segredo')):
            response = self.client.get('/api/stations')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error']['code'], 'internal_error')
        self.assertNotIn('segredo', response.content.decode())
```

Rodar:

```powershell
python manage.py test
```

Resultado esperado: `Ran 8 tests ... OK`.

O teste `test_lacuna_nao_e_preenchida` mostra a regra das lacunas: numa janela de 4 horas existem 5 horários (início e fim incluídos). Apagamos 1, e a API devolve **4 pontos**, sem inventar o que falta.

---

## 13. Etapa 11: README, Git e entrega

### 13.1 Modelo de README para o projeto

Crie `back-django/README.md` com, no mínimo:

````markdown
# API de monitoramento (Python + Django)

> Dados simulados e fictícios. Não representam rios reais e não servem para alertas ou decisões.

## Requisitos
Python 3.10+ e pip.

## Como rodar (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed
python manage.py runserver 3000
```
Confira em http://localhost:3000/api/health. Testes: `python manage.py test`.
Roteiro de fumaça: `.\harness\check.ps1` (com o servidor ligado).

## Rotas
(tabela com as 4 rotas, parâmetros e exemplos de resposta)

## Banco de dados
(diagrama da seção 5.1, explicação de PK, FK, UNIQUE, CHECK e índice)
(diferenças em relação ao schema original, tabela da seção 5.5)

## Validações e erros
(tabela da seção 11.4)

## Decisões e limitações
- Por que Django e não Express.
- Datas gravadas como datetime UTC e formatadas com Z na saída.
- O seed usa a hora atual: rodar em outra hora adiciona horários novos, sem duplicar os antigos.
- Sem autenticação, previsão ou sensores reais (fora do escopo).

## Próximos passos
(ex.: paginação, cache, Docker, testes de carga)
````

### 13.2 Git

Faça commits pequenos, um por etapa. Isso conta na avaliação ("usar Git").

```powershell
git init
git add .
git commit -m "Cria projeto Django e configurações"
# ... depois de cada etapa:
git commit -am "Adiciona modelos e migration inicial"
git commit -am "Adiciona seed idempotente"
git commit -am "Implementa listagem, resumo e série"
git commit -am "Trata erros 400, 404 e 500 em JSON"
git commit -am "Adiciona testes e README"
```

Antes de cada commit, confira com `git status` que `.env`, `.venv/` e `data/` **não** aparecem na lista.

### 13.3 O que entregar

| Item pedido pela Cogmo | Onde está |
|---|---|
| Código com README atualizado | Pasta `back-django/` e `README.md` |
| Schema SQL | `db/schema.sql` (seção 5.4) |
| Evidência do seed | Print ou texto das duas execuções de `python manage.py seed` (seção 6) |
| Exemplos de chamadas válidas e inválidas | Saídas das seções 11.3 e 11.4 (pode criar `docs/EXEMPLOS.md`) |
| Diagrama ou descrição das relações | Seção "Banco de dados" do README (seção 5.1) |
| Apresentação curta | Seção 16 deste guia |

---

## 14. Checklist final

### Tarefas essenciais do desafio

- [ ] 1. SQLite inicializado pelas migrations, com chave estrangeira ligada (automática no Django).
- [ ] 2. Seed idempotente: `python manage.py seed` duas vezes mostra o mesmo total.
- [ ] 3. `GET /api/stations` lista estações ativas em ordem alfabética, com `updated_at`.
- [ ] 4. `GET /api/stations/{id}/summary` traz a leitura mais recente de nível e de chuva, cada uma com seu horário.
- [ ] 5. `GET /api/stations/{id}/series` filtra por estação, métrica e janela de 1 a 72 horas.
- [ ] 6. Datas ISO 8601 em UTC com `Z`, ordenadas da mais antiga para a mais recente.
- [ ] 7. 404 para estação inexistente, 400 para métrica ou janela inválida, sempre com JSON `{"error": {...}}`.
- [ ] 8. Lacunas preservadas: nenhum ponto inventado ou interpolado; série vazia retorna `points: []`.
- [ ] 9. Consultas parametrizadas (ORM) e rotas separadas das consultas (`views.py` × `repository.py`).

### Pronto para entregar

- [ ] Outra pessoa consegue rodar o projeto só seguindo o README.
- [ ] `.\harness\check.ps1` imprime `OK`.
- [ ] `python manage.py test` passa.
- [ ] Toda resposta de dados tem `"data_mode": "simulation"`.
- [ ] `.env` e o banco não estão no repositório.

### Critérios de avaliação (100 pontos)

| Critério | Pontos | Como este guia atende |
|---|---|---|
| API e contrato | 30 | Seções 9 e 10: rotas, códigos HTTP e mensagens em JSON |
| Banco e SQL | 25 | Seções 5 e 6: PK, FK, UNIQUE, CHECK, índice, seed repetível, ORM parametrizado |
| Regras de dados | 20 | Seções 7 e 8: UTC com `Z`, unidades, ordenação, filtros e lacunas |
| Organização e clareza | 15 | Estrutura de pastas da seção 1 e README da seção 13 |
| Demonstração e colaboração | 10 | Commits da seção 13.2 e roteiro da seção 16 |

---

## 15. Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `Activate.ps1 cannot be loaded` | Política de execução do PowerShell | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `ModuleNotFoundError: No module named 'django'` | Ambiente virtual não ativado | `.\.venv\Scripts\Activate.ps1` |
| `no such table: stations` | Migrations não aplicadas | `python manage.py migrate` |
| `Unknown command: 'seed'` | Falta `__init__.py` em `management/` ou `commands/` | Crie os dois arquivos vazios (seção 3.3) |
| Lista de estações vazia | Seed não executado | `python manage.py seed` |
| Série sem pontos | Seed rodado há mais de 72 horas | Rode o seed de novo |
| `DisallowedHost` | Acesso por um endereço fora de `ALLOWED_HOSTS` | Use `localhost` ou `127.0.0.1` |
| Página HTML de erro em vez de JSON | Rota fora de `/api/` ou middleware ausente | Confira `MIDDLEWARE` e a última linha de `monitoring/urls.py` |
| Frontend bloqueado por CORS | Origem diferente da configurada | Ajuste `CORS_ORIGIN` no `.env` e reinicie o servidor |
| Porta 3000 ocupada | Outro servidor (ex.: o Node) ligado | Feche o outro processo com Ctrl+C |
| Acentos como `ç` no JSON | Uso de `JsonResponse` direto | Use `json_response` de `utils.py` |

---

## 16. Preparando a apresentação

O guia do desafio pede que você conte:

1. **Onde estão as funções que você completou:** `monitoring/repository.py` (`list_stations`, `get_summary`, `get_series`), chamadas por `monitoring/views.py`.
2. **Como uma estação se relaciona às leituras:** relação 1:N pela chave estrangeira `observations.station_id → stations.id`, com UNIQUE em estação + métrica + horário.
3. **Como você conferiu uma consulta e um erro:** mostre o `check.ps1` passando, o `curl.exe -i` de um 404 e a saída de `python manage.py test`.
4. **O que foi mais difícil e o próximo passo:** por exemplo, formatar datas UTC com `Z`, ou entender a diferença entre janela pedida (`from`/`to`) e horários existentes. Próximos passos possíveis: paginação, cache, Docker ou um painel admin para cadastrar estações.

Roteiro de demonstração (5 minutos):

1. `python manage.py seed` duas vezes → mesmo total (seed repetível).
2. `GET /api/stations` → três estações em ordem alfabética.
3. `GET /api/stations/EST-01/summary` → horário de cada métrica.
4. `GET /api/stations/EST-01/series?metric=rain&hours=12` → unidade `mm/h` e ordem crescente.
5. `curl.exe -i .../stations/NAO-EXISTE/summary` → 404 em JSON.
6. `python manage.py test` → tudo verde.

> Conta mais uma solução correta e explicada do que uma arquitetura sofisticada. Entenda cada linha que você escrever.

---

## 17. Adicionais: extras para se destacar

Esta seção é **opcional**. Comece por ela só quando o checklist da seção 14 estiver completo: um extra não compensa uma tarefa essencial faltando.

### 17.0 Regras para qualquer extra

1. **Não quebre o contrato.** Rotas e campos novos podem ser adicionados; os existentes (`/health`, `/stations`, `/summary`, `/series`) continuam respondendo exatamente como antes.
2. **Fique dentro do escopo.** O desafio deixa de fora login, previsão por IA, sensores reais, alertas de risco, nuvem, filas e microsserviços. Os extras abaixo não entram nessas áreas.
3. **Um extra por vez, com teste e commit.** Assim, se algo der errado, basta desfazer aquele commit.
4. **Rode `python manage.py test` e `.\harness\check.ps1` depois de cada extra.**

### Mapa dos extras

| # | Extra | Esforço | Critério que reforça | Prioridade |
|---|---|---|---|---|
| 17.1 | Seed com lacunas de propósito | 1 h | Regras de dados (20) | Alta |
| 17.2 | Relatório de qualidade (`/quality`) | 2 h | Regras de dados (20), API (30) | Alta |
| 17.3 | Documentação interativa (OpenAPI + Swagger UI) | 2 h | Organização e clareza (15) | Alta |
| 17.4 | Padronização e cobertura de testes (Ruff + coverage) | 1 h | Organização e clareza (15) | Média |
| 17.5 | Integração contínua (GitHub Actions) | 1 h | Demonstração e colaboração (10) | Média |
| 17.6 | Estatísticas da janela (`/stats`) | 1 h | API (30) | Média |
| 17.7 | Exportar série em CSV (`/series.csv`) | 1 h | API (30) | Baixa |
| 17.8 | Health check que detecta banco fora do ar (503) | 30 min | API (30) | Baixa |
| 17.9 | Painel administrativo do Django | 1 h | Demonstração (10) | Baixa |

Se tiver pouco tempo, faça **17.1 + 17.2 + 17.3**: juntos, mostram cuidado com a qualidade dos dados, que é o centro deste desafio.

---

### 17.1 Seed com lacunas de propósito

**Por que fazer:** o seed original grava todas as horas, então a regra "não inventar leituras" nunca aparece na prática. Com lacunas de propósito, você **mostra ao vivo** que a API devolve a série com buracos, sem preenchê-los. Também dá para mostrar que, no resumo, nível e chuva têm horários diferentes quando um sensor para.

**Como vai funcionar:**

```powershell
python manage.py seed                            # como antes: dados completos
python manage.py seed --com-lacunas              # pula alguns horários
python manage.py seed --limpar --com-lacunas     # apaga tudo e recarrega com lacunas
```

O `--limpar` é necessário porque o seed é idempotente: se as leituras já existem, ele não as apaga. Para "criar" lacunas num banco que já está completo, é preciso começar do zero.

#### Passo 1: definir as regras das lacunas

As lacunas precisam ser **fixas**, e não aleatórias: assim, o resultado é sempre o mesmo e os testes não falham por acaso. No topo de `monitoring/management/commands/seed.py`, logo depois da lista `STATIONS`, adicione:

```python
def is_gap(index, station_index, metric):
    """Regras fixas de lacunas, para que o resultado seja sempre o mesmo.

    - Todas as estações: sensor desligado cerca de 1 vez a cada 10 horas.
    - EST-02: pluviômetro parado nas 2 últimas horas (o nível continua).
    """
    if (index + station_index * 3) % 10 == 7:
        return True
    return metric == 'rain' and station_index == 1 and index >= 71
```

- A primeira regra usa o resto da divisão (`%`) para pular mais ou menos 1 em cada 10 horas. O `station_index * 3` faz cada estação falhar em horários diferentes.
- A segunda regra simula um pluviômetro quebrado na EST-02: o nível continua chegando, a chuva não. É isso que vai mostrar horários diferentes no `/summary`.

#### Passo 2: aceitar as opções na linha de comando

Dentro da classe `Command`, antes do `handle`, adicione:

```python
    def add_arguments(self, parser):
        parser.add_argument(
            '--com-lacunas', action='store_true',
            help='Pula alguns horários para simular falhas de sensor.',
        )
        parser.add_argument(
            '--limpar', action='store_true',
            help='Apaga todas as observações antes de carregar.',
        )
```

`action='store_true'` significa: se a opção aparecer no comando, o valor é `True`; se não aparecer, é `False`. O Django troca o hífen por sublinhado, então `--com-lacunas` vira `options['com_lacunas']`.

#### Passo 3: usar as opções no `handle`

Substitua o `handle` inteiro por:

```python
    @transaction.atomic
    def handle(self, *args, **options):
        if options['limpar']:
            apagadas, _ = Observation.objects.all().delete()
            self.stdout.write(f'{apagadas} observações apagadas.')

        for data in STATIONS:
            Station.objects.get_or_create(id=data['id'], defaults=data)

        end_hour = current_hour_utc()
        observations = []
        for index in range(73):
            observed_at = end_hour - timedelta(hours=72 - index)
            for station_index, data in enumerate(STATIONS):
                level = 1.05 + station_index * 0.24 + 0.08 * math.sin(index / 5 + station_index)
                if (index + station_index * 7) % 17 < 3:
                    rain = 0.4 + ((index + station_index) % 4) * 0.35
                else:
                    rain = 0
                values = [('level', round(level, 2), 'm'), ('rain', round(rain, 2), 'mm/h')]
                for metric, value, unit in values:
                    if options['com_lacunas'] and is_gap(index, station_index, metric):
                        continue
                    observations.append(Observation(
                        station_id=data['id'], metric=metric, observed_at=observed_at,
                        value=value, unit=unit,
                    ))

        # ignore_conflicts=True vira INSERT OR IGNORE: a UNIQUE impede duplicatas.
        Observation.objects.bulk_create(observations, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f'Amostra simulada pronta ({Station.objects.count()} estações, '
            f'{Observation.objects.count()} observações).'
        ))
```

O que mudou em relação à seção 6:

- As duas métricas agora passam por um único laço (`for metric, value, unit in values`). Assim, a regra de lacuna é aplicada a cada uma separadamente.
- O `continue` pula a leitura quando ela deve faltar.
- O `--limpar` apaga as observações dentro da mesma transação: se algo der errado depois, nada é apagado.

#### Passo 4: conferir

```powershell
python manage.py seed --limpar --com-lacunas
# 438 observações apagadas.
# Amostra simulada pronta (3 estações, 392 observações).

python manage.py seed --com-lacunas
# Amostra simulada pronta (3 estações, 392 observações).   ← continua idempotente
```

Com o servidor ligado, veja o resumo da EST-02:

```json
"latest": {
  "level_observed_at": "2026-10-27T16:00:00Z",
  "level_m": 1.31,
  "rain_observed_at": "2026-10-27T14:00:00Z",
  "rain_mm_h": 0.0
}
```

O nível é das 16h, mas a última chuva registrada é das 14h. A API **não** reaproveitou o horário do nível, exatamente como pede o contrato.

> O `check.ps1` continua passando com lacunas, porque ainda existem pontos nas últimas 24 horas.

**Commit:** `git commit -am "Adiciona opções --com-lacunas e --limpar ao seed"`

---

### 17.2 Relatório de qualidade dos dados (`/quality`)

**Por que fazer:** a série mostra o que existe; o relatório mostra **o que falta**. Para quem trabalha com dados hidrológicos, saber que "a EST-02 tem 77% das leituras de chuva nas últimas 12 horas" é tão importante quanto o valor em si. Este extra transforma a regra das lacunas em informação útil.

**Rota nova:** `GET /api/stations/{station_id}/quality?metric=rain&hours=12`

**Resposta esperada:**

```json
{
  "data_mode": "simulation",
  "station_id": "EST-02",
  "metric": "rain",
  "interval_minutes": 60,
  "from": "2026-10-27T04:00:00Z",
  "to": "2026-10-27T16:00:00Z",
  "expected_points": 13,
  "found_points": 10,
  "missing_points": 3,
  "completeness_pct": 76.9,
  "missing_timestamps": ["2026-10-27T08:00:00Z", "2026-10-27T15:00:00Z", "2026-10-27T16:00:00Z"]
}
```

Numa janela de 12 horas existem **13** horários esperados, porque o início e o fim entram na conta (04h, 05h, ..., 16h).

#### Passo 1: a consulta (`repository.py`)

Primeiro, ajuste os imports no topo de `monitoring/repository.py`. As agregações extras (`Avg`, `Count`, `Min`, `Sum`) já ficam prontas para a seção 17.6:

```python
from datetime import timedelta

from django.db.models import Avg, Count, Max, Min, Sum
```

Depois, adicione a função no fim do arquivo:

```python
def get_quality(station_id, metric, start, end):
    existing = set(
        Observation.objects.filter(
            station_id=station_id,
            metric=metric,
            observed_at__gte=start,
            observed_at__lte=end,
        ).values_list('observed_at', flat=True)
    )

    expected = []
    current = start
    while current <= end:
        expected.append(current)
        current += timedelta(hours=1)

    missing = [to_iso_utc(t) for t in expected if t not in existing]
    found = len(expected) - len(missing)
    return {
        'expected_points': len(expected),
        'found_points': found,
        'missing_points': len(missing),
        'completeness_pct': round(100 * found / len(expected), 1),
        'missing_timestamps': missing,
    }
```

Como funciona:

1. `values_list('observed_at', flat=True)` busca **só os horários** que existem no banco. O `set` permite perguntar rapidamente "este horário existe?".
2. O `while` monta a lista de todos os horários **esperados**, de hora em hora.
3. Os horários esperados que não estão no `set` são as lacunas.
4. `completeness_pct` é a porcentagem encontrada, com uma casa decimal.

> **Atenção:** o relatório **descreve** as lacunas; ele não as preenche. A rota `/series` continua devolvendo só o que existe.

#### Passo 2: reaproveitar a validação (`views.py`)

A rota `/quality` usa os mesmos parâmetros da `/series` (`metric` e `hours`). Em vez de copiar a validação, vamos movê-la para uma função auxiliar. Adicione no topo de `monitoring/views.py`, depois de `SIMULATION_MESSAGE`:

```python
def _series_params(request):
    """Lê e valida metric e hours da URL. Devolve (metric, hours, erro)."""
    metric = request.GET.get('metric') or 'level'
    hours_text = request.GET.get('hours') or '24'

    if metric not in UNITS:
        return None, None, error_response(400, 'invalid_metric', 'metric deve ser level ou rain.')
    try:
        hours = int(hours_text)
    except ValueError:
        hours = 0
    if not 1 <= hours <= 72:
        return None, None, error_response(
            400, 'invalid_hours', 'hours deve ser um inteiro entre 1 e 72.'
        )
    return metric, hours, None


def _station_not_found():
    return error_response(404, 'station_not_found', 'Estação não encontrada.')
```

O `_` no início do nome é uma convenção do Python para dizer "função de uso interno deste arquivo".

Agora a `station_series` fica mais curta. Substitua-a por:

```python
@require_GET
def station_series(request, station_id):
    metric, hours, error = _series_params(request)
    if error:
        return error
    if not repository.station_exists(station_id):
        return _station_not_found()

    start, end = window(hours)
    return json_response({
        'data_mode': 'simulation',
        'station_id': station_id,
        'metric': metric,
        'unit': UNITS[metric],
        'interval_minutes': 60,
        'from': to_iso_utc(start),
        'to': to_iso_utc(end),
        'points': repository.get_series(station_id, metric, start, end),
    })
```

Na `station_summary`, troque a linha do 404 por `return _station_not_found()`.

> Isso é uma **refatoração**: o código muda, mas o comportamento não. Rode `python manage.py test` agora. Se os 8 testes da seção 12 continuarem passando, a refatoração está correta.

#### Passo 3: a view da rota nova

Adicione em `views.py`:

```python
@require_GET
def station_quality(request, station_id):
    metric, hours, error = _series_params(request)
    if error:
        return error
    if not repository.station_exists(station_id):
        return _station_not_found()

    start, end = window(hours)
    return json_response({
        'data_mode': 'simulation',
        'station_id': station_id,
        'metric': metric,
        'interval_minutes': 60,
        'from': to_iso_utc(start),
        'to': to_iso_utc(end),
        **repository.get_quality(station_id, metric, start, end),
    })
```

O `**` "espalha" o dicionário devolvido por `get_quality` dentro da resposta, como se você tivesse escrito cada campo à mão.

#### Passo 4: registrar a rota (`monitoring/urls.py`)

Adicione **antes** da linha do `re_path` (a captura de rotas desconhecidas precisa ser sempre a última):

```python
    path('stations/<str:station_id>/quality', views.station_quality),
```

#### Passo 5: testar

Crie o arquivo `monitoring/test_extras.py`. Os testes de todos os extras ficam nele, separados dos testes do essencial. O Django encontra automaticamente qualquer arquivo que comece com `test`.

```python
from unittest.mock import patch

from django.core.management import call_command
from django.db import OperationalError, connection
from django.test import TestCase

from .models import Observation


class ExtrasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed', '--com-lacunas', verbosity=0)

    # --- 17.1 seed com lacunas ---

    def test_seed_com_lacunas_tem_menos_observacoes(self):
        self.assertLess(Observation.objects.count(), 438)

    def test_seed_com_lacunas_e_idempotente(self):
        antes = Observation.objects.count()
        call_command('seed', '--com-lacunas', verbosity=0)
        self.assertEqual(Observation.objects.count(), antes)

    def test_limpar_recria_a_amostra_completa(self):
        call_command('seed', '--limpar', verbosity=0)
        self.assertEqual(Observation.objects.count(), 438)

    def test_resumo_mostra_horarios_diferentes_por_metrica(self):
        latest = self.client.get('/api/stations/EST-02/summary').json()['latest']
        self.assertNotEqual(latest['level_observed_at'], latest['rain_observed_at'])

    # --- 17.2 relatório de qualidade ---

    def test_qualidade_bate_com_a_serie(self):
        url = '/api/stations/EST-02/{}?metric=rain&hours=24'
        serie = self.client.get(url.format('series')).json()
        qualidade = self.client.get(url.format('quality')).json()
        self.assertEqual(qualidade['expected_points'], 25)
        self.assertEqual(qualidade['found_points'], len(serie['points']))
        self.assertEqual(qualidade['missing_points'], len(qualidade['missing_timestamps']))
        self.assertGreater(qualidade['missing_points'], 0)

    def test_qualidade_valida_parametros(self):
        response = self.client.get('/api/stations/EST-01/quality?hours=0')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/stations/NAO/quality')
        self.assertEqual(response.status_code, 404)
```

O teste `test_qualidade_bate_com_a_serie` é o mais importante: ele confere que **o relatório e a série contam a mesma história**. Os testes dos próximos extras serão acrescentados nesta mesma classe.

**Commit:** `git commit -am "Adiciona relatório de qualidade dos dados"`

---

### 17.3 Documentação interativa (OpenAPI + Swagger UI)

**Por que fazer:** quem avalia (ou a equipe de frontend) abre `http://localhost:3000/api/docs` e vê todas as rotas, parâmetros, exemplos e erros, com um botão **"Try it out"** para testar direto no navegador. É o formato de documentação de API mais usado no mercado.

**O que é cada coisa:**

- **OpenAPI** é um arquivo (YAML) que descreve a API de forma padronizada.
- **Swagger UI** é uma página pronta que lê esse arquivo e monta a documentação interativa.

Não é preciso instalar nada: o Swagger UI é carregado de uma CDN pública.

#### Passo 1: o arquivo `docs/openapi.yaml`

Crie a pasta `docs/` na raiz do projeto (ao lado de `manage.py`) e o arquivo `docs/openapi.yaml`:

```yaml
openapi: 3.0.3
info:
  title: API de monitoramento (dados simulados)
  version: 1.0.0
  description: >
    API do desafio Cogmo. Todas as estações e leituras são fictícias e
    não representam condições reais.
servers:
  - url: http://localhost:3000

paths:
  /api/health:
    get:
      summary: Verifica se a API e o banco respondem
      responses:
        '200':
          description: API e banco funcionando
          content:
            application/json:
              example: {status: ok, database: ok}

  /api/stations:
    get:
      summary: Lista as estações ativas em ordem alfabética
      responses:
        '200':
          description: Lista de estações
          content:
            application/json:
              example:
                data_mode: simulation
                stations:
                  - id: EST-01
                    name: Estação Aurora
                    river: Rio Aurora
                    municipality: Vila Aurora
                    updated_at: '2026-09-28T12:00:00Z'

  /api/stations/{station_id}/summary:
    get:
      summary: Leitura mais recente de nível e de chuva
      parameters:
        - $ref: '#/components/parameters/StationId'
      responses:
        '200':
          description: Resumo da estação
          content:
            application/json:
              example:
                data_mode: simulation
                message: Amostra simulada. Não representa condições reais.
                station: {id: EST-01, name: Estação Aurora, river: Rio Aurora, municipality: Vila Aurora}
                latest:
                  level_observed_at: '2026-09-28T12:00:00Z'
                  level_m: 1.42
                  rain_observed_at: '2026-09-28T12:00:00Z'
                  rain_mm_h: 0.6
        '404':
          $ref: '#/components/responses/StationNotFound'

  /api/stations/{station_id}/series:
    get:
      summary: Série histórica de uma métrica
      parameters:
        - $ref: '#/components/parameters/StationId'
        - $ref: '#/components/parameters/Metric'
        - $ref: '#/components/parameters/Hours'
      responses:
        '200':
          description: Pontos em ordem crescente; lacunas não são preenchidas
          content:
            application/json:
              example:
                data_mode: simulation
                station_id: EST-01
                metric: level
                unit: m
                interval_minutes: 60
                from: '2026-09-27T12:00:00Z'
                to: '2026-09-28T12:00:00Z'
                points:
                  - {timestamp: '2026-09-27T12:00:00Z', value: 1.34}
                  - {timestamp: '2026-09-27T13:00:00Z', value: 1.37}
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/StationNotFound'

  /api/stations/{station_id}/quality:
    get:
      summary: Completude da série e horários sem leitura (extra)
      parameters:
        - $ref: '#/components/parameters/StationId'
        - $ref: '#/components/parameters/Metric'
        - $ref: '#/components/parameters/Hours'
      responses:
        '200':
          description: Relatório de lacunas
          content:
            application/json:
              example:
                data_mode: simulation
                station_id: EST-02
                metric: rain
                interval_minutes: 60
                from: '2026-09-28T06:00:00Z'
                to: '2026-09-28T12:00:00Z'
                expected_points: 7
                found_points: 4
                missing_points: 3
                completeness_pct: 57.1
                missing_timestamps: ['2026-09-28T07:00:00Z', '2026-09-28T11:00:00Z', '2026-09-28T12:00:00Z']
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/StationNotFound'

components:
  parameters:
    StationId:
      name: station_id
      in: path
      required: true
      schema: {type: string, example: EST-01}
    Metric:
      name: metric
      in: query
      required: false
      schema: {type: string, enum: [level, rain], default: level}
    Hours:
      name: hours
      in: query
      required: false
      schema: {type: integer, minimum: 1, maximum: 72, default: 24}

  schemas:
    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code: {type: string}
            message: {type: string}

  responses:
    BadRequest:
      description: metric ou hours inválido
      content:
        application/json:
          schema: {$ref: '#/components/schemas/Error'}
          example: {error: {code: invalid_hours, message: hours deve ser um inteiro entre 1 e 72.}}
    StationNotFound:
      description: Estação inexistente
      content:
        application/json:
          schema: {$ref: '#/components/schemas/Error'}
          example: {error: {code: station_not_found, message: Estação não encontrada.}}
```

Dicas para ler e escrever o YAML:

- **A indentação é a estrutura.** Use sempre 2 espaços e **nunca** tab.
- **`components`** guarda peças reutilizáveis. `$ref: '#/components/parameters/Metric'` significa "use aqui o parâmetro `Metric` definido lá embaixo". Assim, `metric` e `hours` são descritos uma vez só e usados em várias rotas.
- Datas e códigos HTTP ficam **entre aspas** (`'200'`, `'2026-09-28T12:00:00Z'`) para o YAML não tentar convertê-los em número ou data.

#### Passo 2: a página `docs/swagger.html`

```html
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>API de monitoramento - documentação</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: '/api/openapi.yaml', dom_id: '#swagger-ui' });
  </script>
</body>
</html>
```

A versão fica fixa (`@5.17.14`) para a página não mudar sozinha quando sair uma versão nova.

#### Passo 3: servir os dois arquivos (`views.py`)

No topo de `monitoring/views.py`, ajuste os imports e crie a constante `DOCS_DIR`:

```python
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse

DOCS_DIR = Path(settings.BASE_DIR) / 'docs'
```

E adicione as duas views:

```python
@require_GET
def openapi_spec(request):
    content = (DOCS_DIR / 'openapi.yaml').read_text(encoding='utf-8')
    return HttpResponse(content, content_type='application/yaml; charset=utf-8')


@require_GET
def api_docs(request):
    content = (DOCS_DIR / 'swagger.html').read_text(encoding='utf-8')
    return HttpResponse(content, content_type='text/html; charset=utf-8')
```

#### Passo 4: rotas

Em `monitoring/urls.py`, antes do `re_path`:

```python
    path('openapi.yaml', views.openapi_spec),
    path('docs', views.api_docs),
```

#### Passo 5: conferir

1. Abra `http://localhost:3000/api/docs` no navegador.
2. Clique em `GET /api/stations/{station_id}/series` → **Try it out** → preencha `EST-01` → **Execute**.
3. Teste também `metric=vento` e veja o 400 documentado.

Para validar o YAML (opcional, mas recomendado):

```powershell
python -m pip install openapi-spec-validator
python -m openapi_spec_validator docs/openapi.yaml
# docs/openapi.yaml: OK
```

Acrescente o teste em `test_extras.py`:

```python
    # --- 17.3 documentação ---

    def test_documentacao(self):
        self.assertEqual(self.client.get('/api/docs').status_code, 200)
        spec = self.client.get('/api/openapi.yaml')
        self.assertContains(spec, 'openapi: 3.0.3')
```

> **Regra de ouro:** toda rota nova precisa entrar no `openapi.yaml`. Documentação desatualizada é pior que nenhuma. As seções 17.6 e 17.7 trazem o trecho de YAML de cada rota.

**Commit:** `git commit -am "Adiciona documentação OpenAPI e Swagger UI"`

---

### 17.4 Padronização e cobertura de testes (Ruff + coverage)

**Por que fazer:**

- **Ruff** é um *linter*: aponta imports sem uso, variáveis esquecidas, linhas longas e erros comuns. Também formata o código num estilo único.
- **coverage** mede **quanto do código os testes realmente executam**. Um número como "98% de cobertura" no README é um argumento forte na apresentação.

#### Passo 1: dependências de desenvolvimento

Ferramentas de desenvolvimento ficam separadas das dependências da aplicação. Crie `requirements-dev.txt`:

```text
-r requirements.txt
ruff>=0.6
coverage>=7.0
```

A linha `-r requirements.txt` inclui também as dependências normais. Instale:

```powershell
python -m pip install -r requirements-dev.txt
```

#### Passo 2: configuração (`pyproject.toml`)

Crie `pyproject.toml` na raiz do projeto:

```toml
[tool.ruff]
line-length = 110
extend-exclude = ["monitoring/migrations"]

[tool.ruff.lint]
select = ["E", "F", "I", "B"]

[tool.ruff.format]
quote-style = "single"

[tool.coverage.run]
source = ["monitoring", "config"]
omit = ["*/migrations/*", "config/asgi.py", "config/wsgi.py"]

[tool.coverage.report]
show_missing = true
```

| Configuração | Significado |
|---|---|
| `line-length = 110` | Tamanho máximo de linha |
| `extend-exclude` | Não analisa as migrations, que são geradas pelo Django |
| `select = ["E", "F", "I", "B"]` | Erros de estilo (E), erros lógicos (F), ordem dos imports (I) e armadilhas comuns (B) |
| `quote-style = "single"` | Mantém as aspas simples usadas neste guia |
| `omit` | Ignora arquivos gerados ou que não precisam de teste |

Acrescente ao `.gitignore`:

```text
.coverage
htmlcov/
```

#### Passo 3: usar

```powershell
ruff check .            # aponta problemas
ruff check . --fix      # corrige o que for automático (ex.: ordem dos imports)
ruff format .           # reformata todos os arquivos no mesmo estilo

coverage run manage.py test
coverage report         # tabela no terminal
coverage html           # relatório navegável em htmlcov/index.html
```

O `ruff format` pode quebrar em várias linhas alguns trechos deste guia. Isso é normal: o código continua o mesmo, só muda a aparência.

Exemplo de saída do `coverage report` com todos os extras:

```text
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
monitoring\management\commands\seed.py        39      0   100%
monitoring\middleware.py                      11      0   100%
monitoring\repository.py                      35      0   100%
monitoring\views.py                          100      7    93%   42, 45, ...
------------------------------------------------------------------------
TOTAL                                        400     10    98%
```

A coluna **Missing** mostra as linhas que nenhum teste executou: são as candidatas ao próximo teste.

> Não persiga 100% a qualquer custo. Cobertura alta com testes que não verificam nada (`assert True`) não vale. O que importa é testar as **regras** do desafio.

**Commit:** `git commit -am "Adiciona Ruff e coverage"`

---

### 17.5 Integração contínua (GitHub Actions)

**Por que fazer:** a cada `git push`, o GitHub roda sozinho o linter, os testes e o roteiro oficial do desafio numa máquina limpa. Se algo quebrar, você recebe um aviso. No README aparece um selo verde mostrando que o projeto está saudável. É prática padrão em empresas e mostra maturidade com Git, que vale pontos em "Demonstração e colaboração".

**Pré-requisitos:** o projeto num repositório do GitHub e a seção 17.4 concluída (o workflow usa o `requirements-dev.txt`).

#### Passo 1: o arquivo do workflow

Crie `.github/workflows/testes.yml` **na raiz do repositório**:

```yaml
name: testes

on:
  push:
  pull_request:

jobs:
  testes:
    runs-on: ubuntu-latest
    steps:
      - name: Baixar o código
        uses: actions/checkout@v4

      - name: Instalar o Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar dependências
        run: python -m pip install -r requirements-dev.txt

      - name: Linter
        run: ruff check .

      - name: Verificar configuração
        run: python manage.py check

      - name: Testes automáticos
        run: python manage.py test

      - name: Roteiro de fumaça (harness do desafio)
        run: |
          python manage.py migrate
          python manage.py seed
          python manage.py runserver 3000 &
          sleep 5
          pwsh ./harness/check.ps1
```

O que cada parte faz:

| Trecho | Significado |
|---|---|
| `on: push / pull_request` | Roda a cada envio de código e a cada pull request |
| `runs-on: ubuntu-latest` | Uma máquina Linux limpa, criada só para essa execução |
| `actions/checkout` | Baixa o seu código para essa máquina |
| `actions/setup-python` | Instala o Python 3.12 |
| `runserver 3000 &` | O `&` deixa o servidor rodando em segundo plano para o passo seguinte |
| `pwsh ./harness/check.ps1` | Roda o roteiro oficial do desafio (o PowerShell já vem instalado nas máquinas do GitHub) |

Não é preciso `.env`: as configurações têm valores padrão no `settings.py`.

> **Se o projeto Django estiver numa subpasta do repositório** (por exemplo, `back-django/`), acrescente logo abaixo de `runs-on`:
>
> ```yaml
>     defaults:
>       run:
>         working-directory: back-django
> ```

#### Passo 2: enviar e acompanhar

```powershell
git add .github
git commit -m "Adiciona integração contínua"
git push
```

No GitHub, abra a aba **Actions**. Um círculo amarelo significa "rodando", um ✓ verde significa "passou" e um ✗ vermelho significa "falhou". Clique na execução para ver qual passo falhou e a mensagem de erro.

#### Passo 3: selo no README

No topo do `README.md`, troque `USUARIO/REPOSITORIO` pelos dados do seu repositório:

```markdown
![testes](https://github.com/USUARIO/REPOSITORIO/actions/workflows/testes.yml/badge.svg)
```

---

### 17.6 Estatísticas da janela (`/stats`)

**Por que fazer:** um painel de monitoramento quase sempre mostra "nível máximo em 24 h" ou "chuva acumulada em 72 h". É um bom exercício de **agregação em SQL** (`MIN`, `MAX`, `AVG`, `SUM`, `COUNT`).

**Rota nova:** `GET /api/stations/{station_id}/stats?metric=rain&hours=72`

**Resposta esperada:**

```json
{
  "data_mode": "simulation",
  "station_id": "EST-01",
  "metric": "rain",
  "unit": "mm/h",
  "from": "2026-10-24T16:00:00Z",
  "to": "2026-10-27T16:00:00Z",
  "count": 66,
  "min": 0.0,
  "max": 1.45,
  "avg": 0.19,
  "accumulated_mm": 12.6
}
```

O campo `accumulated_mm` só aparece para **chuva**. Somar níveis de rio não tem significado físico.

#### Passo 1: a consulta (`repository.py`)

Os imports já foram ajustados na seção 17.2. Adicione:

```python
def get_stats(station_id, metric, start, end):
    result = Observation.objects.filter(
        station_id=station_id,
        metric=metric,
        observed_at__gte=start,
        observed_at__lte=end,
    ).aggregate(
        count=Count('id'),
        minimum=Min('value'),
        maximum=Max('value'),
        average=Avg('value'),
        total=Sum('value'),
    )
    average = result['average']
    return {
        'count': result['count'],
        'min': result['minimum'],
        'max': result['maximum'],
        'avg': round(average, 2) if average is not None else None,
        'total': round(result['total'], 2) if result['total'] is not None else None,
    }
```

`aggregate` faz o banco calcular tudo numa única consulta. O SQL equivalente é:

```sql
SELECT COUNT(id), MIN(value), MAX(value), AVG(value), SUM(value)
FROM observations
WHERE station_id = ? AND metric = ? AND observed_at >= ? AND observed_at <= ?
```

Sem leituras na janela, `COUNT` dá `0` e os outros dão `None` (vira `null` no JSON). Por isso existe o `if ... is not None`: `round(None)` geraria um erro.

#### Passo 2: a view

```python
@require_GET
def station_stats(request, station_id):
    metric, hours, error = _series_params(request)
    if error:
        return error
    if not repository.station_exists(station_id):
        return _station_not_found()

    start, end = window(hours)
    stats = repository.get_stats(station_id, metric, start, end)
    total = stats.pop('total')
    body = {
        'data_mode': 'simulation',
        'station_id': station_id,
        'metric': metric,
        'unit': UNITS[metric],
        'from': to_iso_utc(start),
        'to': to_iso_utc(end),
        **stats,
    }
    if metric == 'rain':
        # Leituras horárias em mm/h: somar os valores dá a chuva acumulada em mm.
        body['accumulated_mm'] = total
    return json_response(body)
```

**Por que somar dá milímetros?** Cada leitura vale para 1 hora. 0,6 mm/h durante 1 hora é igual a 0,6 mm. Somando todas as horas, temos o total em mm.

> **Limitação para registrar no README:** se houver lacunas, o acumulado fica **menor** que o real, porque as horas sem leitura não entram na soma. Combine com o `/quality` para saber o quanto confiar no número.

#### Passo 3: rota, documentação e testes

`urls.py`, antes do `re_path`:

```python
    path('stations/<str:station_id>/stats', views.station_stats),
```

`docs/openapi.yaml`, dentro de `paths:`:

```yaml
  /api/stations/{station_id}/stats:
    get:
      summary: Mínimo, máximo, média e chuva acumulada na janela (extra)
      parameters:
        - $ref: '#/components/parameters/StationId'
        - $ref: '#/components/parameters/Metric'
        - $ref: '#/components/parameters/Hours'
      responses:
        '200':
          description: Estatísticas; accumulated_mm só aparece para rain
          content:
            application/json:
              example:
                data_mode: simulation
                station_id: EST-01
                metric: rain
                unit: mm/h
                from: '2026-09-25T12:00:00Z'
                to: '2026-09-28T12:00:00Z'
                count: 66
                min: 0.0
                max: 1.45
                avg: 0.19
                accumulated_mm: 12.6
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/StationNotFound'
```

`test_extras.py`:

```python
    # --- 17.6 estatísticas ---

    def test_estatisticas_de_chuva_tem_acumulado(self):
        body = self.client.get('/api/stations/EST-01/stats?metric=rain&hours=72').json()
        self.assertIn('accumulated_mm', body)
        self.assertLessEqual(body['min'], body['avg'])
        self.assertLessEqual(body['avg'], body['max'])

    def test_estatisticas_de_nivel_nao_tem_acumulado(self):
        body = self.client.get('/api/stations/EST-01/stats?metric=level').json()
        self.assertNotIn('accumulated_mm', body)
        self.assertEqual(body['unit'], 'm')

    def test_estatisticas_sem_dados(self):
        Observation.objects.filter(station_id='EST-03').delete()
        body = self.client.get('/api/stations/EST-03/stats').json()
        self.assertEqual(body['count'], 0)
        self.assertIsNone(body['avg'])
```

**Commit:** `git commit -am "Adiciona estatísticas da janela"`

---

### 17.7 Exportar a série em CSV (`/series.csv`)

**Por que fazer:** muita gente que analisa dados abre tudo no Excel ou no Google Planilhas. Com um link, o arquivo é baixado pronto, com as colunas certas e a marcação de dados simulados.

**Rota nova:** `GET /api/stations/{station_id}/series.csv?metric=level&hours=24`

**Arquivo gerado** (`EST-01_level_3h.csv`):

```text
station_id,metric,timestamp,value,unit,data_mode
EST-01,level,2026-10-27T13:00:00Z,1.13,m,simulation
EST-01,level,2026-10-27T14:00:00Z,1.13,m,simulation
EST-01,level,2026-10-27T15:00:00Z,1.13,m,simulation
EST-01,level,2026-10-27T16:00:00Z,1.13,m,simulation
```

#### Passo 1: a view

Acrescente `import csv` no topo de `views.py` e adicione:

```python
@require_GET
def station_series_csv(request, station_id):
    metric, hours, error = _series_params(request)
    if error:
        return error
    if not repository.station_exists(station_id):
        return _station_not_found()

    start, end = window(hours)
    points = repository.get_series(station_id, metric, start, end)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="{station_id}_{metric}_{hours}h.csv"'
    )
    response.write(chr(0xFEFF))  # BOM: faz o Excel reconhecer os acentos
    writer = csv.writer(response)
    writer.writerow(['station_id', 'metric', 'timestamp', 'value', 'unit', 'data_mode'])
    for point in points:
        writer.writerow([
            station_id, metric, point['timestamp'], point['value'], UNITS[metric], 'simulation',
        ])
    return response
```

Pontos de atenção:

- **Reaproveitamento:** a view usa o mesmo `get_series` da rota JSON. A regra das lacunas vale aqui também, sem código novo.
- **`Content-Disposition: attachment`** faz o navegador **baixar** o arquivo em vez de mostrá-lo na tela.
- **`csv.writer`** cuida de aspas e vírgulas dentro dos valores. Nunca monte CSV juntando textos com `','.join(...)`.
- **BOM (caractere U+FEFF, escrito como `chr(0xFEFF)`)** é um caractere invisível no início do arquivo que avisa ao Excel que o texto está em UTF-8.
- **Os erros continuam em JSON** (400 e 404), como no resto da API.

#### Passo 2: rota, documentação e teste

`urls.py`, antes do `re_path`:

```python
    path('stations/<str:station_id>/series.csv', views.station_series_csv),
```

`docs/openapi.yaml`, dentro de `paths:`:

```yaml
  /api/stations/{station_id}/series.csv:
    get:
      summary: Série histórica para download em CSV (extra)
      parameters:
        - $ref: '#/components/parameters/StationId'
        - $ref: '#/components/parameters/Metric'
        - $ref: '#/components/parameters/Hours'
      responses:
        '200':
          description: Arquivo CSV com as colunas station_id, metric, timestamp, value, unit, data_mode
          content:
            text/csv:
              schema: {type: string}
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/StationNotFound'
```

`test_extras.py`:

```python
    # --- 17.7 CSV ---

    def test_csv(self):
        response = self.client.get('/api/stations/EST-01/series.csv?metric=level&hours=6')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        linhas = response.content.decode('utf-8-sig').strip().splitlines()
        self.assertEqual(linhas[0], 'station_id,metric,timestamp,value,unit,data_mode')
        self.assertTrue(linhas[1].endswith(',m,simulation'))
```

O `decode('utf-8-sig')` lê o texto já removendo o BOM.

**Commit:** `git commit -am "Adiciona exportação da série em CSV"`

---

### 17.8 Health check que detecta banco fora do ar (503)

**Por que fazer:** hoje, se o banco falhar, o `/api/health` cai no middleware e responde 500 genérico. Um health check útil diz **o que** está com problema. O código **503 (Service Unavailable)** significa "o serviço está temporariamente indisponível", que descreve melhor um banco fora do ar.

Substitua a view `health` e ajuste o import de `django.db`:

```python
from django.db import DatabaseError, connection


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except DatabaseError:
        return json_response({'status': 'error', 'database': 'error'}, status=503)
    return json_response({'status': 'ok', 'database': 'ok'})
```

Quando tudo funciona, a resposta continua **idêntica** ao contrato (`200 {"status":"ok","database":"ok"}`).

**Como testar algo que "quebra o banco"?** Com um **mock**: durante o teste, trocamos temporariamente o método que abre o cursor por um que sempre dá erro. Em `test_extras.py`:

```python
    # --- 17.8 health 503 ---

    def test_health_com_banco_fora_do_ar(self):
        with patch.object(connection, 'cursor', side_effect=OperationalError('sem banco')):
            response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['database'], 'error')
```

Fora do bloco `with`, tudo volta ao normal automaticamente.

**Commit:** `git commit -am "Health check responde 503 quando o banco falha"`

---

### 17.9 Painel administrativo do Django

**Por que fazer:** o Django gera de graça um painel web para ver, filtrar, criar e editar estações e observações. Na apresentação, você pode, por exemplo, **desativar uma estação** pelo painel e mostrar que ela some de `/api/stations`, provando a regra "só estações ativas".

> **Atenção ao escopo:** o painel exige um usuário com senha. Isso **não** é o "login" que o desafio deixa de fora: a API continua pública, e o painel é só uma ferramenta local de quem desenvolve. Explique isso no README e na apresentação. Se preferir não correr o risco de parecer fora do escopo, pule este extra.

#### Passo 1: ligar os apps e middlewares necessários (`settings.py`)

O painel depende de usuários, sessões e mensagens. Substitua `INSTALLED_APPS` e `MIDDLEWARE` e acrescente `TEMPLATES` e `STATIC_URL`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'monitoring',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'monitoring.middleware.JsonErrorMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = 'static/'
```

A ordem dos middlewares importa: `SessionMiddleware` precisa vir antes de `AuthenticationMiddleware`, e o `CorsMiddleware` continua em primeiro.

#### Passo 2: registrar os modelos (`monitoring/admin.py`)

Recrie o arquivo `monitoring/admin.py` (ele foi apagado na seção 3.3):

```python
from django.contrib import admin

from .models import Observation, Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'river', 'municipality', 'active']
    list_filter = ['active']
    search_fields = ['id', 'name', 'river', 'municipality']


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ['station', 'metric', 'observed_at', 'value', 'unit', 'source']
    list_filter = ['station', 'metric']
    date_hierarchy = 'observed_at'
    ordering = ['-observed_at']
```

| Opção | Efeito no painel |
|---|---|
| `list_display` | Colunas da tabela |
| `list_filter` | Filtros na lateral direita |
| `search_fields` | Caixa de busca |
| `date_hierarchy` | Navegação por ano, mês e dia |
| `ordering` | Leituras mais recentes primeiro |

#### Passo 3: rota (`config/urls.py`)

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('monitoring.urls')),
]
```

#### Passo 4: criar as tabelas e o usuário

```powershell
python manage.py migrate            # cria as tabelas de usuários e sessões
python manage.py createsuperuser    # pede nome, e-mail (pode deixar vazio) e senha
python manage.py runserver 3000
```

Acesse `http://localhost:3000/admin/` e entre com o usuário criado.

**Demonstração sugerida:**

1. Abra `/api/stations`: três estações.
2. No painel, abra a EST-03, desmarque **Active** e salve.
3. Recarregue `/api/stations`: duas estações. `/api/stations/EST-03/summary` agora responde 404.
4. Marque **Active** de novo.

> **No README:** registre que o banco passa a ter também as tabelas internas do Django (`auth_user`, `django_session` etc.) e que o painel é só para uso local. Nunca coloque usuário e senha no repositório.

**Commit:** `git commit -am "Adiciona painel administrativo"`

---

### 17.10 Fechando os extras

#### Estrutura final com todos os extras

```text
back-django/
├── .github/workflows/testes.yml      ← 17.5
├── docs/
│   ├── openapi.yaml                  ← 17.3
│   └── swagger.html                  ← 17.3
├── pyproject.toml                    ← 17.4
├── requirements-dev.txt              ← 17.4
└── monitoring/
    ├── admin.py                      ← 17.9
    ├── test_extras.py                ← 17.1 a 17.8
    └── ...                           (demais arquivos das seções 3 a 12)
```

#### Rotas finais

| Rota | Origem |
|---|---|
| `GET /api/health` | Contrato (503 quando o banco falha: 17.8) |
| `GET /api/stations` | Contrato |
| `GET /api/stations/{id}/summary` | Contrato |
| `GET /api/stations/{id}/series` | Contrato |
| `GET /api/stations/{id}/quality` | Extra 17.2 |
| `GET /api/stations/{id}/stats` | Extra 17.6 |
| `GET /api/stations/{id}/series.csv` | Extra 17.7 |
| `GET /api/docs` e `GET /api/openapi.yaml` | Extra 17.3 |
| `/admin/` | Extra 17.9 |

#### Conferência final

```powershell
ruff check .
python manage.py test           # com todos os extras: 20 testes
python manage.py seed --limpar --com-lacunas
python manage.py runserver 3000
# em outro terminal:
.\harness\check.ps1             # o contrato original continua passando
```

#### Atualize o README

Acrescente uma seção **"Extras implementados"** com:

- a lista de rotas novas e um exemplo de resposta de cada uma;
- como rodar o seed com lacunas;
- o link para `/api/docs`;
- o selo do GitHub Actions e a porcentagem de cobertura;
- as limitações (acumulado de chuva subestimado quando há lacunas; painel admin só para uso local).

#### Na apresentação

Escolha **um** extra para mostrar com calma; não tente mostrar todos. A sugestão mais forte em 2 minutos:

1. `python manage.py seed --limpar --com-lacunas`
2. `/api/stations/EST-02/summary` → nível às 16h, chuva às 14h: "cada métrica tem seu horário".
3. `/api/stations/EST-02/series?metric=rain&hours=12` → a série tem buracos e não foi preenchida.
4. `/api/stations/EST-02/quality?metric=rain&hours=12` → "77% de completude, faltam estes 3 horários".
5. Feche com: "a API não esconde nem inventa dados que não existem; ela informa o que falta".
