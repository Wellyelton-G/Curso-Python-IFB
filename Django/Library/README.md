# Sistema de Biblioteca (Django)

Sistema web de gestão de acervo e empréstimos de uma biblioteca, desenvolvido em Django 5.2 como projeto da disciplina.

Este projeto corresponde ao estado final da **Aula 6** dos guias em [Guias_de_construção_e_implementacoes](Guias_de_construção_e_implementacoes/README.md). Lá está o passo a passo completo da construção, aula por aula, com explicação de cada parte do código.

---

## Funcionalidades

**Leitores**

- cadastro, login e recuperação de senha por e-mail
- acervo com capas, busca, filtros (categoria, idioma, ano, disponibilidade), ordenação e paginação
- busca avançada e histórico das próprias buscas, com opção de refazer
- empréstimo e devolução de livros, com prazo de 14 dias
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
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/>. O banco que acompanha o projeto já tem o superusuário `admin` (senha `admin123`), que deve ser usado apenas para estudo.

Comandos úteis:

```powershell
python manage.py popular_acervo    # cadastra 27 livros de exemplo em 6 categorias
python manage.py createsuperuser   # cria outro administrador
python manage.py test              # roda os 36 testes automatizados
```

---

## Estrutura

```
Library/
├── manage.py
├── requirements.txt
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
│   ├── admin.py                configuração do Admin
│   ├── tests.py                testes automatizados
│   └── management/commands/popular_acervo.py
├── templates/                  páginas HTML (base.html, catalog/, registration/)
└── Guias_de_construção_e_implementacoes/
    ├── README.md               roteiro das 6 aulas
    ├── Aula_01 ... Aula_06     guias passo a passo
    ├── gabarito/               o projeto ao final de cada aula
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
