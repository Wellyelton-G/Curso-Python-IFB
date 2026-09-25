# Sistema de Biblioteca (Django)

Sistema web de gestão de acervo e empréstimos de uma biblioteca, desenvolvido em Django 5.2 como projeto da disciplina.

Este projeto corresponde ao estado final da **Aula 10** dos guias em [Guias_de_construção_e_implementacoes](Guias_de_construção_e_implementacoes/README.md). Lá está o passo a passo completo da construção, aula por aula, com explicação de cada parte do código.

---

## Funcionalidades

**Leitores**

- cadastro, login e recuperação de senha por e-mail
- acervo com capas, busca, filtros (categoria, idioma, ano, disponibilidade), ordenação e paginação
- busca avançada e histórico das próprias buscas, com opção de refazer
- empréstimo e devolução de livros, com prazo de 21 dias (protegido contra dois pedidos simultâneos pela última cópia)
- página de cada livro com avaliações (nota de 1 a 5 e comentário) de quem já pegou o livro emprestado
- exportação do resultado da busca em CSV, Excel e PDF
- tema claro e escuro

**Equipe (usuários `is_staff`)**

- painel Admin para livros, capas, categorias, empréstimos, buscas e avaliações
- lista de empréstimos atrasados, com registro de devolução
- página "com quem está" para cada livro
- relatórios (empréstimos, livros populares, leitores ativos, atrasados, empréstimos por categoria), com exportação em CSV, Excel e PDF

---

## Como rodar

No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/>. O banco que acompanha o projeto já tem o superusuário `admin` (senha `admin123`), que deve ser usado apenas para estudo.

Comandos úteis:

```powershell
python manage.py popular_acervo    # cadastra 27 livros de exemplo em 5 categorias
python manage.py createsuperuser   # cria outro administrador
python manage.py test              # roda os 63 testes automatizados
python cliente_api.py              # programa de exemplo que consome a API (com o servidor rodando)
```

No servidor, basta o `requirements.txt`. O `requirements-dev.txt` acrescenta as ferramentas de qualidade, usadas no desenvolvimento:

```powershell
ruff check .                       # verifica o código (erros prováveis e estilo)
ruff format .                      # formata o código
coverage run manage.py test        # roda os testes medindo a cobertura
coverage report                    # mostra a cobertura (mínimo exigido: 90%)
```

---

## Estrutura

```
Library/
├── manage.py
├── requirements.txt            dependências do sistema
├── requirements-dev.txt        dependências do desenvolvimento (ruff, coverage)
├── pyproject.toml              configuração do ruff e do coverage
├── .github/                    integração contínua (workflows/ci.yml) e modelo de pull request
├── db.sqlite3                  banco de dados (SQLite)
├── media/book_covers/          capas enviadas
├── library/                    configurações do projeto (settings.py, urls.py)
├── catalog/                    app principal
│   ├── models.py               Category, Book, Loan, SearchQuery, Review
│   ├── views.py                lógica das páginas
│   ├── urls.py                 rotas do app
│   ├── forms.py                cadastro e avaliação
│   ├── reports.py              relatórios da equipe
│   ├── exporters.py            geração de CSV, Excel e PDF
│   ├── services.py             regras de empréstimo (usadas pelas páginas e pela API)
│   ├── serializers.py          API: conversão entre models e JSON
│   ├── api_views.py            API: viewsets
│   ├── api_urls.py             API: rotas
│   ├── permissions.py          API: permissões
│   ├── admin.py                configuração do Admin
│   ├── tests.py                testes automatizados
│   └── management/commands/popular_acervo.py
├── templates/                  páginas HTML (base.html, catalog/, registration/)
├── static/                     CSS e JavaScript (css/style.css, js/theme.js)
├── cliente_api.py              programa de exemplo que consome a API
└── Guias_de_construção_e_implementacoes/
    ├── README.md               roteiro das 10 aulas
    ├── Aula_01 ... Aula_10     guias passo a passo
    ├── gabarito/               o projeto ao final de cada aula
    ├── resolucoes/             resolução comentada dos exercícios
    └── versoes_anteriores/     guias antigos, apenas para consulta
```

---

## Principais endereços

| Endereço | Página |
|---|---|
| `/` | acervo (busca, filtros, paginação) |
| `/livros/<id>/` | detalhes do livro e avaliações |
| `/emprestimos/` | meus empréstimos |
| `/busca-avancada/` | busca avançada |
| `/historico/` | histórico de buscas |
| `/cadastro/` | criar conta |
| `/contas/login/` | entrar |
| `/contas/password_reset/` | recuperar senha |
| `/equipe/atrasados/` | empréstimos atrasados (equipe) |
| `/equipe/relatorios/` | relatórios (equipe) |
| `/admin/` | painel administrativo |

Em desenvolvimento, os e-mails de recuperação de senha aparecem no terminal onde o `runserver` está rodando.

---

## API REST

A API segue o padrão REST, com respostas em JSON. A documentação interativa fica em `/api/docs/`.

| Método | Endereço | Acesso | Operação |
|---|---|---|---|
| GET | `/api/livros/` | público | lista o acervo (aceita `q`, `categoria`, `idioma`, `disponivel`, `ordenar`) |
| GET | `/api/livros/{id}/` | público | consulta um livro |
| POST, PUT, PATCH, DELETE | `/api/livros/`, `/api/livros/{id}/` | equipe | cadastra, altera, apaga |
| POST | `/api/livros/{id}/emprestar/` | autenticado | empresta o livro |
| GET | `/api/categorias/` | público | lista as categorias |
| GET | `/api/emprestimos/` | autenticado | os empréstimos de quem fez o pedido |
| POST | `/api/emprestimos/{id}/devolver/` | autenticado | devolve |
| POST | `/api/token/` | público | troca usuário e senha por um token |

Os pedidos autenticados enviam o cabeçalho `Authorization: Token <token>`.

---

## Configuração para publicação

O `settings.py` lê as configurações sensíveis de variáveis de ambiente, que podem ficar num arquivo `.env` na pasta do projeto (carregado pelo `python-dotenv`). O `.env` não vai para o Git; o modelo é o `.env.example`. No computador nenhuma variável precisa ser definida; no servidor, elas são obrigatórias:

| Variável | Uso | Exemplo |
|---|---|---|
| `DJANGO_DEBUG` | `False` no servidor | `False` |
| `DJANGO_SECRET_KEY` | chave secreta de produção (nunca no repositório) | gerada com `get_random_secret_key()` |
| `DJANGO_ALLOWED_HOSTS` | endereços do site, separados por vírgula | `seunome.pythonanywhere.com` |

O passo a passo completo da publicação no PythonAnywhere está na [Aula 7](Guias_de_construção_e_implementacoes/Aula_07_Publicacao_na_Internet.md).

---

## Integração contínua

O arquivo `.github/workflows/ci.yml` roda o `ruff` e os testes com cobertura a cada push e a cada pull request no GitHub. O GitHub só executa workflows que estão na pasta `.github/` **da raiz do repositório**: como aqui o projeto fica dentro de `Django/Library/`, o arquivo serve de referência. Num repositório só com o projeto (como o `biblioteca` das aulas), ele funciona sem nenhuma alteração. O passo a passo está na [Aula 10](Guias_de_construção_e_implementacoes/Aula_10_Git_em_Equipe_e_Integracao_Continua.md).
