# Aula 6 — Relatórios, banco de dados e revisão geral

Sistema de Biblioteca com Django · Aula 6 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- Criar **relatórios** para a equipe: empréstimos, livros populares, leitores ativos, atrasados e empréstimos por categoria.
- Organizar o código em **módulos** com responsabilidades claras (`reports.py` e `exporters.py`).
- Gerar arquivos **PDF** e reaproveitar o CSV e o Excel.
- Ver **o que o banco faz por baixo do ORM**: o SQL gerado e as tabelas.
- Fazer **backup e restauração** dos dados.
- **Migrar de SQLite para PostgreSQL** (parte opcional), na ordem certa e sem perder dados.
- **Revisar o sistema inteiro**: como as peças se conectam e o que foi estudado em cada aula.

Ao final da aula o sistema está completo, e você consegue explicar como ele funciona, da URL até o banco de dados.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | Concluída | Concluída | Concluída | **Aula atual** | Publicação | API REST | Qualidade de código | Git em equipe |

## Antes de começar

- [ ] Ambiente virtual ativo.
- [ ] `python manage.py test` mostra 30 testes OK (Aula 5).
- [ ] Para os relatórios terem o que mostrar, faça alguns empréstimos com usuários diferentes e crie pelo Admin um ou dois empréstimos com prazo no passado.

---

## Parte 1 — Conceitos

### 1.1 Um formato comum para todos os relatórios

São 5 relatórios e 4 saídas (tela, CSV, Excel e PDF). Se cada combinação tivesse código próprio, seriam 20 trechos de código.

A saída é combinar um **formato comum de dados**: todo relatório devolve um dicionário com `headers` (cabeçalho) e `rows` (linhas).

```python
# Formato que todos os relatórios devolvem
{
    "headers": ["Título", "Autor(a)", "Empréstimos"],
    "rows": [
        ["Dom Casmurro", "Machado de Assis", 12],
        ["1984", "George Orwell", 9],
    ],
}
```

Com isso:

```
 5 funções de relatório  ──▶  { headers, rows }  ──▶  1 template HTML
 (reports.py)                  (formato comum)    ──▶  1 função de CSV    ┐
                                                   ──▶  1 função de Excel  ├ exporters.py
                                                   ──▶  1 função de PDF    ┘
```

São 9 peças em vez de 20, e um relatório novo ganha todos os formatos sem código extra.

### 1.2 `GROUP BY` com o ORM

Relatórios quase sempre são **contagens por grupo**: empréstimos por livro, por usuário, por categoria. No SQL isso se chama `GROUP BY`; no Django é o `annotate` com `Count` que já usamos:

```python
# Conta os empréstimos de cada livro
Book.objects.annotate(total=Count("loans"))
```

O Django transforma isso em:

```sql
SELECT catalog_book.*, COUNT(catalog_loan.id) AS total
FROM catalog_book LEFT JOIN catalog_loan ON catalog_loan.book_id = catalog_book.id
GROUP BY catalog_book.id
```

---

## Parte 2 — Relatórios

### Passo 1 — Instalar o reportlab

O `reportlab` gera arquivos PDF.

```powershell
pip install reportlab
```

O `requirements.txt` final fica assim:

```text
Django>=5.2,<6.0
Pillow
openpyxl
reportlab
```

### Passo 2 — Os relatórios

**Arquivo:** `catalog/reports.py` · **Ação:** criar

```python
"""Relatórios para a equipe da biblioteca.

Todo relatório é uma função que devolve o MESMO formato de dicionário:

    {"headers": ["Coluna 1", "Coluna 2"], "rows": [[valor, valor], [valor, valor]]}

Graças a esse "contrato", uma única página HTML, um único gerador de Excel
e um único gerador de PDF servem para todos os relatórios.
"""

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone

from .models import Book, Category, Loan


def all_loans():
    """Os 200 empréstimos mais recentes, com a situação de cada um."""
    # [:200] vira um LIMIT 200 no SQL: o banco devolve no máximo 200 linhas
    loans = Loan.objects.select_related("book", "user").order_by("-borrowed_at")[:200]
    rows = []
    for loan in loans:
        # A mesma lógica de situação usada na página "Meus empréstimos"
        if loan.returned_at:
            status = "Devolvido"
        elif loan.is_overdue:
            status = "Atrasado"
        else:
            status = "Em dia"
        rows.append([
            loan.book.title,
            loan.user.username,
            loan.borrowed_at.strftime("%d/%m/%Y"),  # strftime formata a data como texto
            loan.due_date.strftime("%d/%m/%Y"),
            status,
        ])
    return {"headers": ["Livro", "Leitor(a)", "Emprestado em", "Devolver até", "Situação"], "rows": rows}


def popular_books():
    """Os 20 livros mais emprestados de todos os tempos."""
    books = (
        Book.objects.annotate(total=Count("loans"))  # conta os empréstimos de cada livro (GROUP BY)
        .filter(total__gt=0)  # filtra pelo resultado da contagem (HAVING no SQL)
        .order_by("-total", "title")[:20]  # mais emprestados primeiro; empate: ordem alfabética
    )
    rows = [[book.title, book.author, book.total] for book in books]
    return {"headers": ["Título", "Autor(a)", "Empréstimos"], "rows": rows}


def active_readers():
    """Os 20 leitores que mais pegaram livros, e quantos estão com eles agora."""
    users = (
        User.objects.annotate(
            total=Count("loans"),  # todos os empréstimos da pessoa
            ativos=Count("loans", filter=Q(loans__returned_at__isnull=True)),  # só os não devolvidos
        )
        .filter(total__gt=0)
        .order_by("-total", "username")[:20]
    )
    rows = [[user.username, user.total, user.ativos] for user in users]
    return {"headers": ["Leitor(a)", "Empréstimos no total", "Com ele(a) agora"], "rows": rows}


def overdue_loans():
    """Empréstimos atrasados, do mais atrasado para o menos atrasado."""
    today = timezone.localdate()
    loans = (
        Loan.objects.filter(returned_at__isnull=True, due_date__lt=today)
        .select_related("book", "user")
        .order_by("due_date")  # prazo mais antigo = mais atrasado
    )
    # Subtrair duas datas dá um intervalo (timedelta); .days é o número de dias
    rows = [
        [loan.book.title, loan.user.username, loan.due_date.strftime("%d/%m/%Y"), (today - loan.due_date).days]
        for loan in loans
    ]
    return {"headers": ["Livro", "Leitor(a)", "Devolver até", "Dias de atraso"], "rows": rows}


def loans_by_category():
    """Quantos livros e quantos empréstimos cada categoria tem (um "GROUP BY")."""
    categories = Category.objects.annotate(
        # distinct=True: sem ele, cada livro seria contado uma vez para cada empréstimo que tem
        livros=Count("books", distinct=True),
        # books__loans atravessa duas relações: categoria -> livros -> empréstimos
        emprestimos=Count("books__loans"),
    ).order_by("-emprestimos", "name")
    rows = [[category.name, category.livros, category.emprestimos] for category in categories]
    return {"headers": ["Categoria", "Livros", "Empréstimos"], "rows": rows}


# "Cardápio" de relatórios: pedaço da URL -> (título, função que gera os dados).
# As funções aparecem sem parênteses: guardamos a função em si, para chamá-la depois.
REPORTS = {
    "emprestimos": ("Todos os empréstimos", all_loans),
    "populares": ("Livros mais emprestados", popular_books),
    "leitores": ("Leitores mais ativos", active_readers),
    "atrasados": ("Empréstimos atrasados", overdue_loans),
    "categorias": ("Empréstimos por categoria", loans_by_category),
}
```

#### Entendendo o código

- **Uma função por relatório**, todas devolvendo o mesmo formato.
- **`.filter(total__gt=0)` depois do `annotate`** filtra pelo resultado da contagem (no SQL, isso vira um `HAVING`). Assim ficam de fora os livros nunca emprestados.
- **Dois `Count` na mesma consulta** (`active_readers`): o total de empréstimos e, com `filter=Q(...)`, só os ativos.
- **`distinct=True`** em `loans_by_category`: quando juntamos categoria, livros **e** empréstimos, cada livro aparece uma vez para cada empréstimo que tem. Sem o `distinct`, um livro com 3 empréstimos seria contado 3 vezes.
- **`REPORTS`** liga o pedaço da URL (`populares`) ao título e à função. As funções aparecem sem parênteses: em Python, funções também são objetos e podem ser guardadas num dicionário para serem chamadas depois.

### Passo 3 — Os exportadores

Na Aula 4, o código do CSV e do Excel ficou dentro da view `export_books`. Agora os relatórios também precisam exportar, então é hora de levar esse código para um módulo próprio que qualquer view possa usar.

**Arquivo:** `catalog/exporters.py` · **Ação:** criar

```python
"""Funções que transformam uma tabela (cabeçalho + linhas) em arquivo para download.

Todas recebem os mesmos argumentos (filename, title, headers, rows) e devolvem
uma HttpResponse pronta. São usadas pela exportação do acervo e pelos relatórios.
"""

import csv  # módulo do Python para escrever arquivos CSV

from django.http import HttpResponse
from django.utils import timezone


def csv_response(filename, title, headers, rows):
    """CSV separado por ';' (o Excel em português abre direto).

    O parâmetro title não é usado aqui, mas existe para que as três funções
    tenham exatamente a mesma assinatura.
    """
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    # attachment: o navegador baixa o arquivo em vez de mostrar na tela
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")  # "BOM": faz o Excel reconhecer os acentos
    writer = csv.writer(response, delimiter=";")  # a resposta funciona como um arquivo aberto
    writer.writerow(headers)
    writer.writerows(rows)
    return response


def xlsx_response(filename, title, headers, rows):
    """Planilha Excel (.xlsx) com cabeçalho em negrito."""
    # Importados aqui dentro: a biblioteca só é carregada quando alguém pede um Excel
    from openpyxl import Workbook
    from openpyxl.styles import Font

    workbook = Workbook()
    sheet = workbook.active  # a primeira aba da planilha
    sheet.title = title[:31]  # o Excel não aceita nomes de aba com mais de 31 caracteres
    sheet.append(headers)
    for cell in sheet[1]:  # sheet[1] é a primeira linha (o cabeçalho)
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    workbook.save(response)  # grava a planilha direto na resposta
    return response


def pdf_response(filename, title, headers, rows):
    """PDF com título, data de geração e uma tabela listrada."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'

    # Documento A4 deitado (landscape): tabelas largas cabem melhor
    document = SimpleDocTemplate(response, pagesize=landscape(A4), title=title)
    styles = getSampleStyleSheet()  # estilos de texto prontos (Title, Normal...)

    # A tabela recebe uma lista de listas; a primeira linha é o cabeçalho.
    # repeatRows=1 repete o cabeçalho no topo de cada página nova.
    table = Table([headers] + [[str(value) for value in row] for row in rows], repeatRows=1)
    # Coordenadas no formato (coluna, linha); -1 significa "a última"
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),  # fundo escuro no cabeçalho
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),  # texto branco no cabeçalho
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # cabeçalho em negrito
        ("FONTSIZE", (0, 0), (-1, -1), 9),  # fonte 9 na tabela inteira
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),  # linhas de grade
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),  # linhas listradas
    ]))

    generated_at = timezone.localtime().strftime("%d/%m/%Y %H:%M")
    # build monta o documento a partir de uma lista de blocos, de cima para baixo
    document.build([
        Paragraph(title, styles["Title"]),
        Paragraph(f"Gerado em {generated_at}", styles["Normal"]),
        Spacer(1, 12),  # espaço em branco de 12 pontos
        table,
    ])
    return response


# Formato pedido na URL -> função que gera o arquivo
EXPORTERS = {
    "csv": csv_response,
    "xlsx": xlsx_response,
    "pdf": pdf_response,
}
```

#### Entendendo o código

As três funções têm a **mesma assinatura** `(filename, title, headers, rows)`. Por isso podem ficar num dicionário e ser escolhidas pelo formato: `EXPORTERS["pdf"](...)`. É a ideia de **polimorfismo** vista em orientação a objetos: coisas diferentes usadas do mesmo jeito. O CSV nem usa o `title`, mas recebe o parâmetro para manter a assinatura igual.

O PDF é montado com a parte `platypus` do reportlab, que funciona como blocos de montar: `Paragraph` é um bloco de texto, `Spacer` é um espaço em branco e `Table` é a tabela. O `document.build([...])` empilha os blocos de cima para baixo e grava o resultado na resposta.

### Passo 4 — As views

**Arquivo:** `catalog/views.py` · **Ação:** cinco alterações

**4.1)** No topo, apague a linha `import csv  # módulo do Python para escrever arquivos CSV`. Ela passou para o `exporters.py`.

**4.2)** Troque a linha `from django.http import Http404, HttpResponse, JsonResponse` por:

```python
from django.http import Http404, JsonResponse
```

**4.3)** Troque as duas linhas de import do nosso app (`from .forms ...` e `from .models ...`) por:

```python
from .exporters import EXPORTERS  # funções que geram CSV, Excel e PDF
from .forms import ReviewForm, SignUpForm
from .models import Book, Category, Loan, Review, SearchQuery
from .reports import REPORTS  # os relatórios da equipe
```

**4.4)** Substitua a view `export_books` inteira por esta versão, bem menor:

```python
@login_required
def export_books(request, file_format):
    """Baixa o resultado da busca atual em CSV, Excel ou PDF (mesmos filtros da listagem)."""
    # Só aceitamos os formatos que existem no dicionário EXPORTERS
    if file_format not in EXPORTERS:
        raise Http404("Formato desconhecido.")

    books = filter_books(request.GET)
    headers = ["Título", "Autor(a)", "ISBN", "Categoria", "Idioma", "Ano", "Disponíveis", "Total"]
    # Uma lista por livro, na mesma ordem do cabeçalho
    rows = [
        [b.title, b.author, b.isbn, b.category.name if b.category else "",
         b.language, b.edition_year or "", b.available, b.copies_total]
        for b in books
    ]
    export = EXPORTERS[file_format]  # escolhe a função certa (csv_response, xlsx_response...)
    return export("livros", "Acervo da biblioteca", headers, rows)
```

**4.5)** Acrescente no final do arquivo:

```python
# ---------- Relatórios (equipe) ----------


@staff_required
def reports_index(request):
    """Página com a lista de relatórios disponíveis."""
    # Pares (pedaço da URL, título) para o template montar os links
    reports = [(slug, title) for slug, (title, _) in REPORTS.items()]
    return render(request, "catalog/reports_index.html", {"reports": reports})


def get_report(slug):
    """Procura o relatório pelo pedaço da URL e já gera os dados.

    Não é uma view (não recebe request): é uma função auxiliar usada pelas duas views abaixo.
    """
    if slug not in REPORTS:
        raise Http404("Relatório não encontrado.")
    title, build = REPORTS[slug]
    return title, build()  # agora sim a função do relatório é chamada (com parênteses)


@staff_required
def report_detail(request, slug):
    """Mostra um relatório na tela, com botões para baixar."""
    title, data = get_report(slug)
    # **data espalha headers e rows no contexto
    context = {"slug": slug, "title": title, **data}
    return render(request, "catalog/report_detail.html", context)


@staff_required
def report_export(request, slug, file_format):
    """Baixa um relatório em CSV, Excel ou PDF."""
    if file_format not in EXPORTERS:
        raise Http404("Formato desconhecido.")
    title, data = get_report(slug)
    # Nome do arquivo com a data de hoje, ex.: relatorio-populares-2026-09-24
    filename = f"relatorio-{slug}-{timezone.localdate():%Y-%m-%d}"
    return EXPORTERS[file_format](filename, title, data["headers"], data["rows"])
```

A `export_books` perdeu cerca de 30 linhas e ainda ganhou o PDF. Os testes da Aula 4 (`test_exportar_csv_respeita_os_filtros` e `test_exportar_excel`) continuam valendo e confirmam que a mudança não quebrou nada.

### Passo 5 — URLs

**Arquivo:** `catalog/urls.py` · **Ação:** acrescentar quatro linhas no final da lista `urlpatterns`, logo abaixo da rota `staff_mark_returned`

```python
    # Relatórios. <slug:...> aceita letras, números, hífen e sublinhado (ex.: "populares")
    path("equipe/relatorios/", views.reports_index, name="reports_index"),
    path("equipe/relatorios/<slug:slug>/", views.report_detail, name="report_detail"),
    path("equipe/relatorios/<slug:slug>/<str:file_format>/", views.report_export, name="report_export"),
```

### Passo 6 — Templates

**6.1) Link "Relatórios" no menu**

**Arquivo:** `templates/base.html` · **Ação:** acrescentar uma linha abaixo do link "Atrasados"

```html
          <a href="{% url 'catalog:overdue_loans' %}">Atrasados</a>
          <a href="{% url 'catalog:reports_index' %}">Relatórios</a>
```

**6.2) Botão de PDF no acervo**

**Arquivo:** `templates/catalog/book_list.html` · **Ação:** acrescentar uma linha abaixo do link "Baixar Excel"

```html
    <a class="btn" href="{% url 'catalog:export_books' 'pdf' %}?{{ request.GET.urlencode }}">Baixar PDF</a>
```

**6.3) Lista de relatórios**

**Arquivo:** `templates/catalog/reports_index.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}Relatórios · Biblioteca{% endblock %}
{% block content %}
  <h1>Relatórios</h1>
  <p class="muted">Escolha um relatório para ver na tela ou baixar em CSV, Excel ou PDF.</p>

  {# reports é a lista de pares (slug, título) montada na view a partir do dicionário REPORTS #}
  {% for slug, title in reports %}
    <div class="card actions" style="margin-top: 0;">
      <a href="{% url 'catalog:report_detail' slug %}"><strong>{{ title }}</strong></a>
      <span class="spacer"></span>
      {# A rota report_export recebe dois parâmetros: o relatório e o formato #}
      <a class="btn" href="{% url 'catalog:report_export' slug 'csv' %}">CSV</a>
      <a class="btn" href="{% url 'catalog:report_export' slug 'xlsx' %}">Excel</a>
      <a class="btn" href="{% url 'catalog:report_export' slug 'pdf' %}">PDF</a>
    </div>
  {% endfor %}
{% endblock %}
```

**6.4) Um template para todos os relatórios**

**Arquivo:** `templates/catalog/report_detail.html` · **Ação:** criar

```html
{% extends "base.html" %}
{% block title %}{{ title }} · Biblioteca{% endblock %}
{% block content %}
  <p><a href="{% url 'catalog:reports_index' %}">« Todos os relatórios</a></p>
  <h1>{{ title }}</h1>

  <div class="actions">
    {# length conta os itens de uma lista #}
    <span class="muted">{{ rows|length }} linha(s)</span>
    <span class="spacer"></span>
    <a class="btn" href="{% url 'catalog:report_export' slug 'csv' %}">Baixar CSV</a>
    <a class="btn" href="{% url 'catalog:report_export' slug 'xlsx' %}">Baixar Excel</a>
    <a class="btn" href="{% url 'catalog:report_export' slug 'pdf' %}">Baixar PDF</a>
  </div>

  {# Este template serve para QUALQUER relatório: ele só percorre cabeçalhos e linhas #}
  <div class="table-wrap" style="margin-top: 12px;">
    <table>
      <thead>
        <tr>
          {% for header in headers %}<th>{{ header }}</th>{% endfor %}
        </tr>
      </thead>
      <tbody>
        {# Dois for aninhados: um para as linhas, outro para os valores de cada linha #}
        {% for row in rows %}
          <tr>
            {% for value in row %}<td>{{ value }}</td>{% endfor %}
          </tr>
        {% empty %}
          <tr><td colspan="{{ headers|length }}" class="muted">Nenhum dado ainda.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
{% endblock %}
```

O template não sabe qual relatório está mostrando: ele apenas percorre `headers` e `rows`. É o formato comum da seção 1.1 em ação.

### Passo 7 — Testes

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar no final do arquivo

```python
class ReportTests(TestCase):
    """Testes da Aula 6: relatórios e exportação."""

    def setUp(self):
        self.equipe = User.objects.create_user("bibliotecaria", password="senha-forte-123", is_staff=True)
        self.leitor = User.objects.create_user("maria", password="senha-forte-123")
        self.popular = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
        self.outro = Book.objects.create(title="Iracema", author="José de Alencar", isbn="2222222222222")
        make_loan(self.popular, self.leitor, days=-5).mark_returned()  # empréstimo antigo, já devolvido
        make_loan(self.popular, self.leitor, days=-2)  # ainda com ela, e atrasado 2 dias
        make_loan(self.outro, self.leitor)  # em dia

    def test_leitor_comum_nao_ve_relatorios(self):
        self.client.force_login(self.leitor)
        response = self.client.get(reverse("catalog:reports_index"))
        self.assertEqual(response.status_code, 403)

    def test_todos_os_relatorios_abrem(self):
        from .reports import REPORTS

        self.client.force_login(self.equipe)
        for slug in REPORTS:
            # subTest: se um relatório falhar, a mensagem diz qual foi
            with self.subTest(relatorio=slug):
                response = self.client.get(reverse("catalog:report_detail", args=[slug]))
                self.assertEqual(response.status_code, 200)

    def test_livros_populares_em_ordem(self):
        from .reports import popular_books

        # Os relatórios são funções comuns: dá para testar sem passar por página nenhuma
        data = popular_books()
        self.assertEqual(data["rows"][0], ["Dom Casmurro", "Machado de Assis", 2])
        self.assertEqual(data["rows"][1], ["Iracema", "José de Alencar", 1])

    def test_relatorio_de_atrasados(self):
        from .reports import overdue_loans

        data = overdue_loans()
        self.assertEqual(len(data["rows"]), 1)
        self.assertEqual(data["rows"][0][3], 2)  # quarta coluna: 2 dias de atraso

    def test_exportar_em_todos_os_formatos(self):
        self.client.force_login(self.equipe)
        # Como cada tipo de arquivo começa: CSV com o BOM + "Livro", XLSX com "PK", PDF com "%PDF"
        inicio_esperado = {"csv": "Livro".encode("utf-8-sig"), "xlsx": b"PK", "pdf": b"%PDF"}
        for file_format, inicio in inicio_esperado.items():
            with self.subTest(formato=file_format):
                url = reverse("catalog:report_export", args=["emprestimos", file_format])
                response = self.client.get(url)
                self.assertTrue(response.content.startswith(inicio))

    def test_relatorio_inexistente_da_404(self):
        self.client.force_login(self.equipe)
        response = self.client.get(reverse("catalog:report_detail", args=["nao-existe"]))
        self.assertEqual(response.status_code, 404)
```

```powershell
python manage.py test
```

O resultado esperado é `Ran 36 tests ... OK`.

### Passo 8 — No navegador

1. Entre como superusuário e clique em **Relatórios**.
2. Abra cada relatório. Em **Empréstimos por categoria**, confira se os números fazem sentido.
3. Baixe um relatório em PDF e outro em Excel.
4. No acervo, filtre por uma categoria e clique em **Baixar PDF**: o arquivo traz só os livros filtrados.
5. Como `maria`, tente abrir `/equipe/relatorios/`: a resposta é 403.

---

## Parte 3 — O banco de dados por dentro

### 3.1 Onde estão os dados

Tudo está no arquivo `db.sqlite3`. A configuração foi criada pelo próprio Django na Aula 1, no `settings.py` (os comentários abaixo foram acrescentados só para explicar; no seu arquivo eles não aparecem):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # tipo de banco: SQLite
        'NAME': BASE_DIR / 'db.sqlite3',  # arquivo onde os dados ficam
    }
}
```

Cada model virou uma tabela com o nome `<app>_<model>`:

| Model | Tabela | Aula |
|---|---|---|
| `Book` | `catalog_book` | 1 |
| `Loan` | `catalog_loan` | 1 |
| `Category` | `catalog_category` | 4 |
| `SearchQuery` | `catalog_searchquery` | 4 |
| `Review` | `catalog_review` | 5 |
| `User` (do Django) | `auth_user` | 1 (criada pelo `migrate`) |

As tabelas e as ligações entre elas (FK = chave estrangeira):

```
                 ┌─────────────────┐
                 │ catalog_category│
                 │ id, name, ...   │
                 └───────▲─────────┘
                         │ category_id (FK, pode ser NULL)
┌────────────┐   ┌───────┴────────┐   ┌──────────────────┐
│ auth_user  │◀──│ catalog_loan   │──▶│ catalog_book     │
│ id,        │   │ book_id  (FK)  │   │ id, title, isbn, │
│ username,  │   │ user_id  (FK)  │   │ copies_total ... │
│ email ...  │   │ due_date ...   │   └───────▲──────────┘
└──▲─────▲───┘   └────────────────┘           │ book_id (FK)
   │     │       ┌────────────────┐   ┌───────┴──────────┐
   │     └───────│ catalog_search │   │ catalog_review   │
   │  user_id    │ query          │   │ book_id, user_id │──┐
   │             │ q, params(JSON)│   │ rating (1–5)     │  │
   │             └────────────────┘   │ UNIQUE(book,user)│  │
   └──────────────────────────────────┴──────────────────┘──┘
                                           user_id (FK)
```

### 3.2 O SQL que o ORM gera

No shell (`python manage.py shell`):

```python
from django.db.models import Count
from catalog.models import Book

# Monta a consulta (ainda sem executar) e mostra o SQL correspondente
consulta = Book.objects.annotate(total=Count("loans")).filter(total__gt=0)
print(consulta.query)
```

Aparece o SQL completo, com `LEFT OUTER JOIN`, `GROUP BY` e `HAVING`. Compare com a seção 1.2.

Também dá para ver o SQL de uma migração e quais migrações já foram aplicadas:

```powershell
python manage.py sqlmigrate catalog 0001
python manage.py showmigrations
```

### 3.3 Explorando o banco com uma ferramenta visual

Escolha uma opção:

- **DB Browser for SQLite** (<https://sqlitebrowser.org/>): abra o `db.sqlite3`. A aba **Browse Data** mostra os dados e a aba **Execute SQL** roda consultas.
- **VS Code**: instale a extensão **SQLite Viewer** e clique no `db.sqlite3`.

Experimente:

```sql
-- Livros em ordem alfabética
SELECT title, copies_total FROM catalog_book ORDER BY title;

-- Quantidade de empréstimos por livro, do mais emprestado para o menos
SELECT b.title, COUNT(l.id) AS emprestimos
FROM catalog_book b LEFT JOIN catalog_loan l ON l.book_id = b.id
GROUP BY b.id
ORDER BY emprestimos DESC;
```

Consulte à vontade, mas evite alterar dados por fora do Django (com `UPDATE` ou `DELETE`): as regras dos models e das views não são aplicadas nesse caso.

O comando `python manage.py dbshell` também abre um terminal SQL, mas depende do programa `sqlite3` instalado, o que é raro no Windows. Por isso as ferramentas visuais são mais práticas.

### 3.4 Backup e restauração

O Django exporta todos os dados para um arquivo JSON que não depende do tipo de banco.

**Backup:**

```powershell
python -X utf8 manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --exclude admin.logentry --exclude sessions --indent 2 --output backup.json
```

| Parte do comando | Para quê |
|---|---|
| `-X utf8` | força o Python a usar UTF-8; sem isso, no Windows, os acentos podem virar `�` |
| `--natural-foreign --natural-primary` | identifica os usuários pelo `username`, e não só por um número |
| `--exclude contenttypes`, `auth.permission`, `admin.logentry`, `sessions` | tabelas internas que o `migrate` recria; se ficassem no backup, a restauração daria erro de duplicidade |
| `--indent 2` | deixa o JSON legível |
| `--output backup.json` | grava direto no arquivo, evitando problemas de codificação do `>` no PowerShell |

**Restauração num banco novo e vazio.** Para testar o backup, pare o `runserver` (`Ctrl+C`) e renomeie o banco atual, guardando-o por segurança:

```powershell
Rename-Item db.sqlite3 db_antigo.sqlite3
```

Sem o arquivo, o Django cria um banco novo e vazio no próximo comando. Crie as tabelas e carregue o backup:

```powershell
python manage.py migrate
python -X utf8 manage.py loaddata backup.json
```

Rode o `runserver` e confira os livros, os empréstimos e o login dos usuários. Se estiver tudo certo, apague o `db_antigo.sqlite3`: ele tem os mesmos dados e não deve ir para o GitHub na Aula 7. Se algo der errado, apague o `db.sqlite3` novo e renomeie o antigo de volta.

O backup **não inclui as imagens**, que ficam na pasta `media/`: copie essa pasta junto. O `backup.json` contém dados pessoais e senhas (criptografadas), então não o envie para o GitHub: acrescente `backup.json` ao `.gitignore`.

### 3.5 (Opcional) Migrando de SQLite para PostgreSQL

O SQLite é ótimo para aprender, mas sistemas com muitos usuários ao mesmo tempo costumam usar um banco servidor, como o PostgreSQL.

**A ordem dos passos importa.** O backup precisa ser feito enquanto o `settings.py` ainda aponta para o SQLite. Se a configuração for trocada antes, o `dumpdata` vai ler o banco novo, que está vazio.

**1. Backup do SQLite** (com o `settings.py` ainda sem alteração), usando o comando da seção 3.4:

```powershell
python -X utf8 manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --exclude admin.logentry --exclude sessions --indent 2 --output backup.json
```

**2. Instale o PostgreSQL** (<https://www.postgresql.org/download/>) e anote a senha do usuário `postgres` definida na instalação.

**3. Crie o usuário e o banco.** Abra o **SQL Shell (psql)**, que vem com o PostgreSQL, entre como `postgres` e rode:

```sql
-- Usuário que o Django vai usar para se conectar
CREATE USER biblioteca_user WITH PASSWORD 'troque-esta-senha';
-- Banco de dados, tendo esse usuário como dono
CREATE DATABASE biblioteca OWNER biblioteca_user;
```

Criar o banco com `OWNER biblioteca_user` é importante: a partir do PostgreSQL 15, um usuário que não é dono do banco não pode criar tabelas nele, e o `migrate` falharia com `permission denied for schema public`.

**4. Instale o driver** que conecta o Python ao PostgreSQL:

```powershell
pip install "psycopg[binary]"
```

E acrescente `psycopg[binary]` ao `requirements.txt`.

**5. Aponte o Django para o PostgreSQL.**

**Arquivo:** `library/settings.py` · **Ação:** substituir o bloco `DATABASES`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # tipo de banco: PostgreSQL
        'NAME': 'biblioteca',  # nome do banco criado no passo 3
        'USER': 'biblioteca_user',
        'PASSWORD': 'troque-esta-senha',
        'HOST': 'localhost',  # o PostgreSQL está rodando neste computador
        'PORT': '5432',  # porta padrão do PostgreSQL
    }
}
```

Num projeto real, senhas não ficam escritas no código: elas são lidas de variáveis de ambiente, por exemplo com `os.environ["DB_PASSWORD"]`. Para o estudo, deixamos assim.

**6. Crie as tabelas no PostgreSQL e restaure os dados:**

```powershell
python manage.py migrate
python -X utf8 manage.py loaddata backup.json
```

**7. Confira.** Rode `python manage.py runserver`, entre com os mesmos usuários e senhas de antes e veja se livros, empréstimos e avaliações estão todos lá. Rode também `python manage.py test`.

Guarde o `db.sqlite3` até ter certeza de que está tudo certo. Para voltar ao SQLite, basta restaurar o bloco `DATABASES` original.

---

## Parte 4 — Revisão geral

### 4.1 O projeto completo

```
biblioteca/
├── manage.py                     ← comandos (runserver, migrate, test, popular_acervo...)
├── requirements.txt              ← dependências
├── db.sqlite3                    ← o banco de dados
├── media/book_covers/            ← capas enviadas
├── library/                      ← PROJETO
│   ├── settings.py               ← configurações (apps, idioma, templates, login, e-mail, banco)
│   └── urls.py                   ← URLs principais: admin/, contas/ e o app na raiz
├── catalog/                      ← APP
│   ├── models.py                 ← Category, Book, Loan, SearchQuery, Review          (Aulas 1, 4, 5)
│   ├── admin.py                  ← painel administrativo                               (Aulas 1, 4, 5)
│   ├── urls.py                   ← rotas do app                                        (Aulas 2 a 6)
│   ├── views.py                  ← a lógica de cada página                             (Aulas 2 a 6)
│   ├── forms.py                  ← SignUpForm, ReviewForm                              (Aula 5)
│   ├── reports.py                ← relatórios                                          (Aula 6)
│   ├── exporters.py              ← CSV, Excel, PDF                                     (Aula 6)
│   ├── tests.py                  ← 36 testes automatizados                             (Aulas 3 a 6)
│   ├── migrations/               ← histórico do banco (0001, 0002, 0003)
│   └── management/commands/
│       └── popular_acervo.py     ← comando de dados de exemplo                         (Aula 4)
└── templates/
    ├── base.html                 ← layout, menu, tema, mensagens                       (Aula 2)
    ├── registration/             ← login, cadastro, recuperação de senha               (Aulas 2 e 5)
    └── catalog/                  ← páginas do app                                      (Aulas 2 a 6)
```

### 4.2 O caminho completo de um clique em "Emprestar"

Acompanhe o que acontece quando a Maria clica em **Emprestar** no livro de id 7. Cada etapa foi construída em alguma aula:

| # | Onde | O que acontece | Aula |
|---|---|---|---|
| 1 | `book_list.html` | o botão está num `<form method="post">` com `{% csrf_token %}` | 2 |
| 2 | Navegador | envia `POST /livros/7/emprestar/` com o token e o cookie de sessão | 2 |
| 3 | Middlewares do Django | conferem o CSRF e identificam o usuário pela sessão (`request.user`) | 2 |
| 4 | `library/urls.py` → `catalog/urls.py` | a rota `livros/<int:book_id>/emprestar/` chama `borrow_book(request, book_id=7)` | 2 |
| 5 | `@login_required`, `@require_POST` | conferem se ela está logada e se o pedido é POST | 2 |
| 6 | `views.borrow_book` | `get_object_or_404` busca o livro; a view aplica as regras (há cópia? ela já está com ele?) | 2 |
| 7 | `Book.copies_available` | o model calcula a disponibilidade (ORM → SQL → banco) | 1 |
| 8 | `Loan.objects.create(...)` | o ORM gera um `INSERT INTO catalog_loan ...` | 1 |
| 9 | `messages.success` + `redirect` | a mensagem fica guardada e o navegador vai para `/emprestimos/` | 2 |
| 10 | `views.my_loans` → `my_loans.html` | um novo GET monta a lista, herdando o `base.html`, e a mensagem aparece uma vez | 2 |
| 11 | `tests.py` | `test_emprestar_cria_emprestimo` e os outros testes garantem que tudo isso continua funcionando | 3 |

Conseguir explicar essa tabela com as próprias palavras é um bom sinal de que o funcionamento do Django foi compreendido.

### 4.3 O que foi estudado em cada aula

| Aula | Conceitos |
|---|---|
| 1 | ambiente virtual, projeto e app, `settings.py`, models (campos, `ForeignKey`, `Meta`, `__str__`, `@property`, métodos), migrações, Admin, ORM no shell |
| 2 | URLs (`path`, `include`, parâmetros, nomes, namespace), views (`render`, `redirect`, `get_object_or_404`), templates (herança, `{{ }}`, `{% %}`, filtros), login e logout, GET e POST, CSRF, mensagens, Post/Redirect/Get, arquivos de mídia |
| 3 | autorização (403), decorators próprios, busca com `Q`, `annotate` com `F` e `Count` (problema N+1), `Paginator` e `{% querystring %}`, testes automatizados |
| 4 | evolução de models com dados existentes, `SET_NULL`, `JSONField`, comandos próprios, refatoração, lista de valores permitidos, download de arquivos (CSV, Excel), API JSON e `fetch` |
| 5 | formulários (`Form`, `ModelForm`, `UserCreationForm`), validação com `clean_<campo>`, `instance` e `commit=False`, `UniqueConstraint`, `choices`, `aggregate`, recuperação de senha e e-mail |
| 6 | `GROUP BY`/`HAVING` com o ORM, `distinct` em contagens, módulos com responsabilidade única, formato comum de dados e polimorfismo, PDF, SQL gerado pelo ORM, backup e restauração, PostgreSQL |

### 4.4 Boas práticas que apareceram ao longo do curso

1. **Regras de negócio no model** (`mark_returned`, `copies_available`, `was_borrowed_by`), e não espalhadas por views e templates.
2. **Não confiar no navegador:** esconder um botão não é segurança; toda regra é conferida de novo na view.
3. **POST para tudo que altera dados**, sempre com `{% csrf_token %}` e seguido de redirect.
4. **Filtrar pelo dono** (`user=request.user`) para ninguém mexer nos dados de outra pessoa.
5. **Nomes de rotas** (`{% url %}`, `reverse`) em vez de endereços escritos à mão.
6. **Não repetir código:** `base.html`, `filter_books`, `staff_required`, `EXPORTERS`.
7. **Listas de valores permitidos** para tudo que vem da URL (`ORDER_OPTIONS`, `REPORTS`, `EXPORTERS`).
8. **Testes automatizados** para poder mudar o código com segurança.

---

## Checkpoint final

- [ ] O menu da equipe tem **Atrasados**, **Relatórios** e **Admin**.
- [ ] Os cinco relatórios abrem e podem ser baixados em CSV, Excel e PDF.
- [ ] O acervo exporta em PDF respeitando os filtros.
- [ ] `python manage.py test` mostra 36 testes OK.
- [ ] Um backup feito com `dumpdata` foi restaurado num banco novo, com os acentos corretos.
- [ ] (Opcional) O sistema roda no PostgreSQL.
- [ ] A tabela "O caminho completo de um clique em Emprestar" faz sentido para você.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `No module named 'reportlab'` | Biblioteca não instalada | `pip install reportlab` |
| `NameError: name 'HttpResponse' is not defined` | Algum trecho de `views.py` ainda usa `HttpResponse` | Confira se a `export_books` foi trocada pela versão nova (Passo 4.4) |
| `NameError: name 'csv' is not defined` | Mesmo caso acima | Mesmo caso acima |
| Contagem de "Livros" por categoria inflada | Falta `distinct=True` | `Count("books", distinct=True)` |
| `loaddata` dá `IntegrityError ... duplicate key` | O backup incluiu `contenttypes` ou `auth.permission` | Refaça o `dumpdata` com os `--exclude` da seção 3.4 |
| `UnicodeDecodeError` ou `�` no backup | Codificação do Windows | Use `python -X utf8 manage.py ...` |
| `permission denied for schema public` (PostgreSQL) | O usuário não é dono do banco | `ALTER DATABASE biblioteca OWNER TO biblioteca_user;` |
| Dados sumiram depois de migrar para o PostgreSQL | O `dumpdata` foi feito depois de trocar o `settings.py` | Volte o `settings.py` para SQLite, refaça o backup e siga a ordem da seção 3.5 |
| `Error loading psycopg` | Driver não instalado | `pip install "psycopg[binary]"` |

---

## Exercícios finais

1. Crie o relatório "Livros nunca emprestados" (título, autor e categoria dos livros sem empréstimos). Basta escrever uma função e acrescentar uma linha ao `REPORTS`: o relatório já aparece na lista e pode ser exportado nos três formatos.
2. No relatório de leitores, acrescente uma coluna com a quantidade de avaliações de cada leitor. Atenção ao problema do `distinct`.
3. Escreva um teste para o relatório `loans_by_category`.

**Projetos para ir além:**

4. **Limite de empréstimos:** cada leitor pode ter no máximo 3 livros ao mesmo tempo. Implemente a regra, mostre uma mensagem clara e escreva os testes.
5. **Renovação:** um botão "Renovar" em "Meus empréstimos" que acrescenta 7 dias ao prazo, uma única vez e só se o empréstimo não estiver atrasado.
6. **Fila de espera:** quando um livro está indisponível, o leitor entra numa fila, e a equipe vê a fila na página "Com quem está?". Pense no model (`Waitlist`), na regra de unicidade e na ordem da fila.
7. **Multas:** calcule uma multa de R$ 1,00 por dia de atraso e mostre-a em "Meus empréstimos" e num relatório novo.

---

## Perguntas para revisar

<details>
<summary>1. Por que todos os relatórios devolvem o mesmo formato de dicionário?</summary>

Para que um único template e um único exportador de cada formato sirvam para todos. Um relatório novo é só uma função, e ganha tela, CSV, Excel e PDF sem código extra.
</details>

<details>
<summary>2. Qual o papel do <code>distinct=True</code> em <code>Count("books", distinct=True)</code>?</summary>

Quando a consulta junta categorias, livros e empréstimos, cada livro aparece uma vez para cada empréstimo que tem. O `distinct` faz o banco contar cada livro uma única vez.
</details>

<details>
<summary>3. Por que o backup exclui <code>contenttypes</code> e <code>auth.permission</code>?</summary>

Porque o `migrate` recria essas tabelas automaticamente no banco novo. Se estivessem no backup, o `loaddata` tentaria inseri-las de novo e daria erro de chave duplicada.
</details>

<details>
<summary>4. Na migração para o PostgreSQL, por que o backup precisa ser feito antes de mexer no <code>settings.py</code>?</summary>

Porque o `dumpdata` lê o banco configurado naquele momento. Se o `settings.py` já apontar para o PostgreSQL (vazio), o backup sai vazio e os dados do SQLite não são levados.
</details>

<details>
<summary>5. Onde fica cada tipo de código no projeto?</summary>

Dados e regras de negócio: `models.py`. O que cada página faz: `views.py`. Quais endereços existem: `urls.py`. Como as páginas aparecem: `templates/`. Formulários e validação: `forms.py`. Relatórios: `reports.py`. Geração de arquivos: `exporters.py`. Verificação automática: `tests.py`. Configuração geral: `settings.py`.
</details>

---

## Fechamento

As funcionalidades do sistema estão completas: autenticação, permissões, busca, relatórios, exportação, avaliações e testes automatizados, e cada parte está onde está por um motivo que foi discutido em aula.

Falta um passo: por enquanto, o sistema só existe no seu computador. Na próxima aula ele vai para a internet.

Para continuar estudando depois do curso:

- **Class-Based Views** (`ListView`, `DetailView`, `CreateView`): outra forma de escrever views, com menos repetição.
- **Django REST Framework**: APIs completas, para aplicativos de celular ou interfaces em JavaScript.
- **Documentação oficial do Django**, com tutorial em português: <https://docs.djangoproject.com/pt-br/5.2/intro/>.

---

Próxima aula: [Aula 7 — Publicando o sistema na internet](Aula_07_Publicacao_na_Internet.md).
