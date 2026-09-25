# Aula 9 — Qualidade de código e concorrência

Sistema de Biblioteca com Django · Aula 9 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- Usar um **verificador de estilo** e um **formatador** automáticos (`ruff`), como nos projetos profissionais.
- Medir a **cobertura de testes** (`coverage`) e usar o relatório para encontrar código sem teste.
- Separar as dependências de **desenvolvimento** das dependências de **produção**.
- Entender o que é uma **condição de corrida** (*race condition*) e reproduzir uma que existe hoje no empréstimo.
- Corrigir o defeito com **transações** e **travas no banco**, e provar a correção com um teste.

Ao final da aula, o código passa pelo `ruff` sem nenhum aviso, a cobertura de testes está acima de 90% e dois leitores não conseguem mais levar a mesma última cópia de um livro.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | **Aula atual** | Git em equipe |

## Antes de começar

- [ ] Ambiente virtual ativo e `python manage.py test` com 58 testes OK (Aula 8).
- [ ] Faça um commit no Git: o formatador vai alterar vários arquivos de uma vez, e é bom poder comparar.

---

## Parte 1 — Conceitos

### 1.1 Por que ferramentas de qualidade

Num projeto com várias pessoas, cada uma escreve de um jeito: aspas simples ou duplas, linhas longas ou curtas, imports em qualquer ordem. As revisões de código acabam discutindo espaços e vírgulas em vez do que importa. Além disso, alguns erros (uma variável que nunca é usada, um import esquecido) passam despercebidos até alguém executar aquele trecho.

Os projetos profissionais resolvem isso com duas ferramentas automáticas:

| Ferramenta | O que faz | Exemplo |
|---|---|---|
| **Verificador** (*linter*) | aponta erros prováveis e desvios das convenções | "`os` foi importado e nunca usado" |
| **Formatador** | reescreve o código num estilo único, sem mudar o que ele faz | troca `'texto'` por `"texto"`, quebra linhas longas |

O **`ruff`** faz as duas coisas, é muito rápido e se tornou o padrão em projetos Python recentes. Ele segue a **PEP 8**, o guia oficial de estilo do Python.

### 1.2 Cobertura de testes

A **cobertura** mede quais linhas do código foram executadas pelos testes. Uma cobertura de 90% significa que 10% das linhas nunca rodaram durante os testes: se houver um erro nelas, os testes não vão avisar.

Cobertura alta **não garante** que o código está certo (uma linha pode rodar sem que o teste confira o resultado), mas cobertura baixa **garante** que há código sem nenhuma verificação. O relatório serve principalmente para **encontrar o que ficou sem teste**.

### 1.3 Condição de corrida

Hoje, o empréstimo funciona em três etapas:

```
1. conta os empréstimos ativos do livro    →  "tem 1 cópia livre"
2. confere se a pessoa já está com o livro
3. grava o empréstimo
```

Imagine a Maria e o João clicando em **Emprestar** na última cópia **no mesmo instante**:

```
        Maria                              João
1. "tem 1 cópia livre"
                                   1. "tem 1 cópia livre"   (a Maria ainda não gravou)
3. grava o empréstimo
                                   3. grava o empréstimo
Resultado: dois empréstimos para uma cópia só.
```

Isso é uma **condição de corrida**: o resultado depende de quem chega primeiro, e entre "conferir" e "gravar" há um intervalo em que outra pessoa pode passar. Esse tipo de defeito é difícil de perceber, porque os testes comuns fazem um pedido de cada vez e nunca o reproduzem.

A correção tem duas partes:

- **Transação** (`transaction.atomic`): conferir e gravar passam a ser uma operação só. Se algo falhar no meio, nada é gravado.
- **Trava** (`select_for_update`): enquanto a Maria está emprestando, a linha do livro fica travada no banco. O pedido do João **espera** a Maria terminar e só então confere as cópias, e aí já não há nenhuma livre.

---

## Parte 2 — `ruff`: verificador e formatador

### Passo 1 — Dependências de desenvolvimento

O `ruff` e o `coverage` são usados só por quem desenvolve: o servidor não precisa deles. Por isso ficam num arquivo separado.

**Arquivo:** `requirements-dev.txt` · **Ação:** criar

```text
# Ferramentas usadas só no desenvolvimento (não são instaladas no servidor)
-r requirements.txt
ruff
coverage
```

A linha `-r requirements.txt` inclui todas as dependências de produção. Assim, um único comando instala tudo o que é preciso para desenvolver:

```powershell
pip install -r requirements-dev.txt
```

No PythonAnywhere, continua valendo o `pip install -r requirements.txt`, sem as ferramentas de desenvolvimento.

### Passo 2 — Configurar as ferramentas

**Arquivo:** `pyproject.toml` (na pasta do projeto, ao lado do `manage.py`) · **Ação:** criar

```toml
# Configuração das ferramentas de qualidade do projeto (Aula 9).
# O pyproject.toml é o arquivo padrão do Python para esse tipo de configuração.

[tool.ruff]
line-length = 120  # tamanho máximo de cada linha de código
extend-exclude = ["catalog/migrations"]  # as migrações são geradas pelo Django: não mexemos nelas

[tool.ruff.lint]
# Grupos de regras verificados:
#   E, W = estilo (PEP 8)      F = erros prováveis (variável não usada, import esquecido...)
#   I = ordem dos imports      B = armadilhas comuns do Python      DJ = boas práticas do Django
select = ["E", "W", "F", "I", "B", "DJ"]

[tool.ruff.format]
quote-style = "double"  # o formatador padroniza as aspas duplas em todo o código

[tool.coverage.run]
source = ["catalog", "library"]  # o código cuja cobertura queremos medir
omit = ["*/migrations/*", "*/tests.py", "library/asgi.py", "library/wsgi.py"]  # fora: migrações, testes e arquivos de servidor

[tool.coverage.report]
show_missing = true  # mostra os números das linhas que nenhum teste executou
skip_covered = true  # esconde os arquivos com 100% de cobertura
fail_under = 90  # o relatório falha se a cobertura total ficar abaixo de 90%
```

O arquivo usa o formato **TOML**: seções entre colchetes e pares `chave = valor`. Cada ferramenta lê só a sua seção (`[tool.ruff]`, `[tool.coverage...]`).

### Passo 3 — O verificador

```powershell
ruff check .
```

O ponto final significa "a pasta atual e tudo dentro dela". Se você seguiu as aulas com cuidado, deve aparecer um único aviso:

```text
I001 [*] Import block is un-sorted or un-formatted
  --> catalog\views.py:1:1
   ...
16 | | from .models import Book, Category, Loan, Review, SearchQuery
17 | | from .reports import REPORTS  # os relatórios da equipe
18 | | from . import services  # regras de empréstimo, compartilhadas com a API (Aula 8)
   | |______________________^
   ...
help: Organize imports
   ...
Found 1 error.
[*] 1 fixable with the `--fix` option.
```

A saída mostra o arquivo e a linha (`catalog\views.py:1:1`), o trecho com problema e, em `help`, como o `ruff` corrigiria. É um problema real, que entrou na Aula 8: a linha `from . import services` foi acrescentada no fim dos imports do app, fora da ordem. O código de regra (`I001`) diz o tipo do problema, e a documentação do `ruff` explica cada código. O `[*]` indica que o próprio `ruff` sabe corrigir:

```powershell
ruff check --fix .
```

Os imports do app ficam em ordem alfabética, com `from . import services` primeiro:

```python
from . import services  # regras de empréstimo, compartilhadas com a API (Aula 8)
from .exporters import EXPORTERS  # funções que geram CSV, Excel e PDF
from .forms import ReviewForm, SignUpForm
from .models import Book, Category, Loan, Review, SearchQuery
from .reports import REPORTS  # os relatórios da equipe
```

Se o seu código tiver outros avisos (uma variável sobrando, um import não usado), leia a mensagem, corrija e rode de novo até aparecer `All checks passed!`.

**Experimente:** acrescente `import os` no topo do `catalog/models.py` e rode `ruff check .`. Aparece `F401 'os' imported but unused`. Apague a linha depois.

### Passo 4 — O formatador

Primeiro, veja o que seria alterado, sem alterar nada:

```powershell
ruff format --check .
```

Aparece algo como `13 files would be reformatted`. Para ver as mudanças em detalhe, use `ruff format --diff .`. Elas são só de forma, por exemplo:

```python
# antes (arquivo gerado pelo Django)
name = 'catalog'
# depois
name = "catalog"
```

Aplique a formatação:

```powershell
ruff format .
```

Rode os testes para confirmar que nada mudou no comportamento:

```powershell
python manage.py test
```

Os 58 testes continuam passando. O formatador garante isso: ele só muda a aparência do código.

**No VS Code**, dá para formatar sozinho ao salvar: instale a extensão **Ruff** (da Astral Software) e, nas configurações (`Ctrl+,`), ative **Format On Save** e escolha o Ruff como formatador padrão para Python.

---

## Parte 3 — Cobertura de testes

### Passo 5 — Medir

Em vez de `python manage.py test`, rode os testes "através" do `coverage`:

```powershell
coverage run manage.py test
coverage report
```

O relatório mostra, para cada arquivo, quantas linhas existem (`Stmts`), quantas nunca rodaram (`Miss`), a porcentagem coberta e **quais linhas** faltaram:

```text
Name                                            Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------
catalog\admin.py                                   37      6    84%   38, 43-48
catalog\api_views.py                               47      1    98%   84
catalog\management\commands\popular_acervo.py      13     13     0%   1-69
catalog\models.py                                  87      7    92%   20, 58, 100-101, 143, 147, 179
catalog\services.py                                12      1    92%   32
catalog\views.py                                  201     27    87%   72, 91, 99, 143, 150-151, 159, ...
...
-----------------------------------------------------------------------------
TOTAL                                             588     57    90%
```

Os números do seu projeto podem ser um pouco diferentes, conforme os exercícios feitos. Para uma visão mais confortável, gere o relatório em HTML:

```powershell
coverage html
```

Abra o arquivo `htmlcov/index.html` no navegador: cada arquivo aparece com as linhas não testadas destacadas em vermelho.

Acrescente ao `.gitignore` os arquivos que o `coverage` e os testes geram:

```text
.coverage
htmlcov/
test_db.sqlite3
```

### Passo 6 — Ler o relatório

O relatório aponta três lacunas importantes:

1. **`catalog/services.py`, linha 32**: é o `raise LoanError(f"Você já está com ...")`. A regra "não empresta o mesmo livro duas vezes" existe desde a Aula 2, e **nenhum teste** passa por ela: nem os testes das páginas, nem os da API.
2. **`popular_acervo.py`, 0%**: o comando da Aula 4 nunca foi testado.
3. **`catalog/admin.py`, linhas 43 a 48**: a ação "Marcar como devolvido" do Admin também não.

Nem toda linha vermelha precisa de teste. As linhas dos `__str__` dos models (em `models.py`), por exemplo, são simples e aparecem no Admin o tempo todo. O critério é **o risco**: regras de negócio sem teste são as primeiras a atacar.

### Passo 7 — Os testes que faltavam

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar imports e uma classe no final

Nos imports do topo, acrescente (o `ruff check --fix .` depois coloca tudo na ordem certa):

```python
from io import StringIO
```

```python
from django.core.management import call_command
```

```python
from . import services
```

E, no final do arquivo:

```python
class CoverageGapTests(TestCase):
    """Aula 9: testes que faltavam, encontrados com o relatório de cobertura."""

    def setUp(self):
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.book = Book.objects.create(
            title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111", copies_total=2
        )

    def test_nao_empresta_o_mesmo_livro_duas_vezes(self):
        # A regra existia desde a Aula 2, mas nenhum teste passava por ela
        services.borrow_book(self.book, self.maria)
        with self.assertRaisesMessage(services.LoanError, "Você já está com"):
            services.borrow_book(self.book, self.maria)
        self.assertEqual(Loan.objects.filter(user=self.maria).count(), 1)

    def test_comando_popular_acervo_nao_duplica(self):
        # call_command roda um comando do manage.py dentro do teste; StringIO guarda o que ele imprimiria
        call_command("popular_acervo", stdout=StringIO())
        call_command("popular_acervo", stdout=StringIO())  # rodar de novo não pode duplicar nada
        self.assertEqual(Book.objects.filter(isbn__startswith="9780000").count(), 27)
        self.assertEqual(Category.objects.count(), 5)

    def test_acao_do_admin_marca_como_devolvido(self):
        loan = make_loan(self.book, self.maria)
        admin = User.objects.create_superuser("admin", password="senha-forte-123")
        self.client.force_login(admin)
        # O formulário de ações do Admin envia o nome da ação e os ids marcados na lista
        self.client.post(
            reverse("admin:catalog_loan_changelist"),
            {"action": "marcar_como_devolvido", "_selected_action": [loan.id]},
        )
        loan.refresh_from_db()
        self.assertFalse(loan.is_active)
```

#### Entendendo o código

- **`assertRaisesMessage(Erro, "trecho")`** confere que o bloco `with` levanta aquele tipo de erro com aquele trecho na mensagem. O primeiro teste chama o `services.py` diretamente, sem passar por página nem API: a regra é testada no lugar onde ela mora.
- **`call_command("popular_acervo")`** executa um comando do `manage.py` dentro do teste. Rodá-lo duas vezes confere a idempotência prometida na Aula 4: continuam existindo 27 livros e 5 categorias.
- **O teste do Admin** envia o mesmo formulário que o navegador envia quando você escolhe uma ação e clica em **Ir**: o nome da ação e os ids marcados.

Rode de novo:

```powershell
ruff check --fix .
ruff format .
coverage run manage.py test
coverage report
```

São 61 testes, e a cobertura total sobe para cerca de 94%.

---

## Parte 4 — A condição de corrida

### Passo 8 — Um banco de testes em arquivo

Para reproduzir dois pedidos simultâneos, o teste vai usar duas **threads**: duas linhas de execução rodando ao mesmo tempo dentro do mesmo programa. O banco de testes padrão do SQLite fica **na memória** e não lida bem com isso: em vez de deixar as duas threads avançarem, ele trava a tabela inteira e dá erro. Os testes precisam de um banco **em arquivo**, que se comporta como o banco real.

**Arquivo:** `library/settings.py` · **Ação:** acrescentar a chave `"TEST"` ao bloco `DATABASES`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        # Aula 9: nos testes, um banco em arquivo (e não na memória), para o teste de concorrência
        # funcionar como no sistema real. O Django cria e apaga esse arquivo sozinho.
        "TEST": {"NAME": BASE_DIR / "test_db.sqlite3"},
    }
}
```

### Passo 9 — Um teste que reproduz o defeito

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar imports e uma classe no final

Nos imports do topo, acrescente:

```python
import threading
import unittest.mock
```

```python
from django.db import connection
```

E troque `from django.test import TestCase, override_settings` por:

```python
from django.test import TestCase, TransactionTestCase, override_settings
```

No final do arquivo:

```python
class ConcurrencyTests(TransactionTestCase):
    """Aula 9: duas pessoas tentam pegar a última cópia exatamente ao mesmo tempo."""

    def test_duas_pessoas_nao_levam_a_ultima_copia(self):
        book = Book.objects.create(
            title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111", copies_total=1
        )
        maria = User.objects.create_user("maria", password="x")
        joao = User.objects.create_user("joao", password="x")

        # A "barreira" faz as duas threads esperarem uma pela outra num ponto do código:
        # logo depois de conferir as cópias e antes de gravar o empréstimo.
        barreira = threading.Barrier(2, timeout=2)
        localdate_original = timezone.localdate

        def espera_a_outra_pessoa(*args, **kwargs):
            try:
                barreira.wait()  # as duas chegam aqui depois de conferir que "há cópia"
            except threading.BrokenBarrierError:
                pass  # a outra thread não chegou (estava bloqueada esperando a primeira terminar)
            return localdate_original(*args, **kwargs)

        resultados = []

        def tentar_emprestar(usuario):
            try:
                services.borrow_book(Book.objects.get(pk=book.pk), usuario)
                resultados.append("emprestou")
            except services.LoanError:
                resultados.append("recusado")
            finally:
                connection.close()  # cada thread usa a sua própria conexão com o banco

        with unittest.mock.patch("catalog.services.timezone.localdate", side_effect=espera_a_outra_pessoa):
            threads = [threading.Thread(target=tentar_emprestar, args=(u,)) for u in (maria, joao)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        self.assertEqual(sorted(resultados), ["emprestou", "recusado"])
        self.assertEqual(Loan.objects.filter(book=book).count(), 1)
```

#### Entendendo o código

Este é o teste mais elaborado do curso. Vale ler com calma.

**O problema de reproduzir o defeito.** Duas threads raramente chegam ao mesmo ponto no mesmo instante. Para o defeito aparecer **sempre**, o teste força o pior caso: as duas conferem as cópias e só então seguem para gravar.

**Como o teste força isso:**

1. **`threading.Barrier(2)`** é um ponto de encontro: a primeira thread que chama `barreira.wait()` fica parada até a segunda também chamar. Aí as duas seguem juntas.
2. **Onde colocar a barreira?** Entre "conferir" e "gravar", o `services.py` chama `timezone.localdate()` para calcular o prazo. O **`unittest.mock.patch`** troca essa função, só durante o teste, por `espera_a_outra_pessoa`, que espera na barreira e depois devolve a data de verdade.
3. **`threading.Thread(target=..., args=(u,))`** cria uma thread que executa `tentar_emprestar(u)`. O `start()` inicia a thread e o `join()` espera ela terminar.
4. **O `timeout=2` da barreira** existe para a versão corrigida: nela, a segunda thread fica bloqueada esperando a primeira, e nunca chega à barreira. Depois de 2 segundos, a primeira desiste de esperar (`BrokenBarrierError`) e segue.

**Detalhes técnicos:**

- **`TransactionTestCase`**: o `TestCase` comum envolve cada teste numa transação única, o que impediria as threads de enxergarem o que as outras gravaram. O `TransactionTestCase` grava de verdade no banco de testes e o limpa depois.
- **`connection.close()`**: cada thread abre a sua própria conexão com o banco, e ela precisa ser fechada ao final.

**Resultado esperado:** um empréstimo feito e um recusado, com um único empréstimo gravado.

Rode só este teste:

```powershell
python manage.py test catalog.tests.ConcurrencyTests
```

Ele **falha**, e é isso que queremos ver:

```text
AssertionError: Lists differ: ['emprestou', 'emprestou'] != ['emprestou', 'recusado']
```

As duas pessoas emprestaram a única cópia. O defeito está reproduzido.

### Passo 10 — A correção

**Arquivo:** `catalog/services.py` · **Ação:** duas alterações

**10.1)** Troque os imports do topo por:

```python
from datetime import timedelta  # representa um intervalo de tempo (ex.: 14 dias)

from django.db import transaction
from django.utils import timezone

from .models import Book, Loan

LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias
```

**10.2)** Substitua a função `borrow_book` inteira:

```python
def borrow_book(book, user):
    """Cria um empréstimo do livro para o usuário e devolve o Loan criado.

    Levanta LoanError se alguma regra não for cumprida.
    """
    # Aula 9: conferir e gravar precisam acontecer como uma coisa só (uma transação).
    # Se algo der errado no meio, nada é gravado.
    with transaction.atomic():
        # Relê o livro TRAVANDO a linha dele até o fim da transação. Se outra pessoa estiver
        # emprestando o mesmo livro agora, este pedido espera ela terminar antes de continuar.
        book = Book.objects.select_for_update().get(pk=book.pk)

        # Regra 1: precisa haver cópia disponível
        if book.copies_available == 0:
            raise LoanError(f"Não há cópias disponíveis de “{book.title}”.")

        # Regra 2: a pessoa não pode estar com este mesmo livro ainda sem devolver
        if book.loans.filter(user=user, returned_at__isnull=True).exists():
            raise LoanError(f"Você já está com “{book.title}”.")

        # Tudo certo: calcula o prazo e cria o empréstimo
        due_date = timezone.localdate() + timedelta(days=LOAN_DAYS)
        return Loan.objects.create(book=book, user=user, due_date=due_date)
```

- **`with transaction.atomic():`** abre uma transação. Tudo o que acontece dentro do bloco é gravado junto, ao final. Se um erro interromper o bloco (inclusive o nosso `LoanError`), nada é gravado.
- **`select_for_update()`** lê o livro e **trava a linha dele** até a transação terminar. Outro pedido que tente travar a mesma linha fica esperando. Quando a trava é liberada, ele relê os dados e já encontra o empréstimo da primeira pessoa.

Rode o teste de novo:

```powershell
python manage.py test catalog.tests.ConcurrencyTests
```

Ele ainda falha, mas de um jeito diferente:

```text
django.db.utils.OperationalError: database is locked
AssertionError: Lists differ: ['emprestou'] != ['emprestou', 'recusado']
```

Agora só uma pessoa emprestou, mas a outra recebeu um **erro** em vez da mensagem "Não há cópias disponíveis". Numa página, isso seria um erro 500.

**Por quê?** O `select_for_update` funciona no **PostgreSQL** e no **MySQL**, mas o **SQLite não tem travas por linha** e simplesmente ignora o comando. O que impediu o segundo empréstimo foi outra coisa: o SQLite só permite uma escrita por vez no banco inteiro, e a segunda thread, sem conseguir escrever, desistiu com erro.

### Passo 11 — O ajuste para o SQLite

O SQLite tem um modo em que cada transação **reserva a escrita logo no começo**. Com ele, a segunda thread espera a primeira terminar desde o início da transação, em vez de descobrir o conflito só na hora de gravar.

**Arquivo:** `library/settings.py` · **Ação:** acrescentar a chave `"OPTIONS"` ao bloco `DATABASES`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        # Aula 9: cada transação já começa reservando a escrita no banco. No SQLite, é isso que
        # faz dois empréstimos simultâneos acontecerem um de cada vez (o select_for_update é ignorado).
        "OPTIONS": {"transaction_mode": "IMMEDIATE"},
        # Aula 9: nos testes, um banco em arquivo (e não na memória), para o teste de concorrência
        # funcionar como no sistema real. O Django cria e apaga esse arquivo sozinho.
        "TEST": {"NAME": BASE_DIR / "test_db.sqlite3"},
    }
}
```

Rode o teste mais uma vez:

```powershell
python manage.py test catalog.tests.ConcurrencyTests
```

Agora ele **passa**, em cerca de 2 segundos (o tempo da barreira esperando a segunda thread, que está bloqueada). Uma pessoa empresta e a outra recebe a mensagem normal de "Não há cópias disponíveis".

As três etapas, resumidas:

| Versão | Duas pessoas, última cópia, mesmo instante |
|---|---|
| Original (Aula 8) | as duas levam a cópia |
| `atomic` + `select_for_update` | uma leva; a outra recebe erro "database is locked" |
| mais `transaction_mode: IMMEDIATE` | uma leva; a outra é recusada com a mensagem normal |

**E no PostgreSQL?** Lá o `select_for_update` já resolve sozinho, e a opção `transaction_mode` não existe (ela é só do SQLite). Por isso o código do `services.py` fica com as duas proteções: a trava vale para qualquer banco, e a configuração cuida do SQLite. Se você migrou para o PostgreSQL na Aula 6, retire o `"OPTIONS"` do bloco `DATABASES` do PostgreSQL.

### Passo 12 — Tudo junto

```powershell
ruff check --fix .
ruff format .
coverage run manage.py test
coverage report
```

O resultado esperado é `Ran 62 tests ... OK`, `All checks passed!` e cobertura total em torno de 94%. Faça um commit.

---

## Checkpoint

- [ ] `ruff check .` mostra `All checks passed!`.
- [ ] `ruff format --check .` mostra que todos os arquivos já estão formatados.
- [ ] `coverage report` mostra a cobertura total acima de 90%, sem erro.
- [ ] Você viu o teste de concorrência **falhar** antes da correção e **passar** depois.
- [ ] `python manage.py test` mostra 62 testes OK.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ruff` ou `coverage` não é reconhecido | Ferramentas não instaladas ou `.venv` inativo | `pip install -r requirements-dev.txt` com o `.venv` ativo |
| O `ruff` aponta problemas nas migrações | Falta o `extend-exclude` | Confira o `pyproject.toml` (Passo 2) |
| `Coverage failure: total of 88 is less than fail-under=90` | Cobertura abaixo do mínimo | Escreva testes para as linhas listadas em `Missing` |
| `No data to report` | Rodou `coverage report` sem o `coverage run` antes | Rode `coverage run manage.py test` primeiro |
| O teste de concorrência dá `database table is locked` | O banco de testes está na memória | Confira a chave `"TEST"` do Passo 8 |
| O teste de concorrência demora muito ou trava | Barreira sem `timeout` | Confira o `threading.Barrier(2, timeout=2)` |
| `TypeError ... transaction_mode` | Django anterior à versão 5.1 | `pip install "Django>=5.2,<6.0"` |
| Sobra um arquivo `test_db.sqlite3` | Os testes foram interrompidos no meio | Pode apagar; ele já está no `.gitignore` |

---

## Resumo

O código passou a seguir um estilo único e verificado por ferramenta, ganhamos uma medida objetiva do que está testado e corrigimos um defeito que nenhum teste comum encontraria.

O que ficou de ideia principal:

- **`ruff check`** aponta problemas; **`ruff format`** padroniza o estilo. Os dois são configurados no **`pyproject.toml`**.
- **Dependências de desenvolvimento** ficam em `requirements-dev.txt`, separadas das de produção.
- **Cobertura** mostra o que nunca foi executado pelos testes. Serve para achar lacunas (como uma regra de negócio sem teste), não como garantia de qualidade.
- **Condição de corrida** acontece quando há um intervalo entre conferir e gravar. A correção é fazer as duas coisas numa **transação** com **trava**.
- **Testes de concorrência** precisam forçar o pior caso (com uma barreira), e só assim o defeito aparece sempre.
- **Cada banco tem suas particularidades:** o `select_for_update` resolve no PostgreSQL; o SQLite precisa do modo `IMMEDIATE`.

---

## Exercícios

1. O relatório de cobertura mostra que a página de busca avançada e o erro de formato inválido na exportação (`/exportar/docx/`) nunca foram testados. Escreva os dois testes e confira que as linhas saíram do `Missing`.
2. Acrescente o grupo de regras `SIM` (simplificações) ao `select` do `pyproject.toml` e rode `ruff check .`. Entenda a sugestão que aparece e corrija o código.
3. Remova temporariamente a linha `"OPTIONS": {"transaction_mode": "IMMEDIATE"}` e rode o teste de concorrência. Explique, com suas palavras, a mensagem de erro que aparece. Depois restaure a linha.

---

## Perguntas para revisar

<details>
<summary>1. Qual a diferença entre o <code>ruff check</code> e o <code>ruff format</code>?</summary>

O `ruff check` aponta problemas: erros prováveis (variáveis não usadas, imports esquecidos) e desvios de convenção. O `ruff format` reescreve o código num estilo único (aspas, quebras de linha, espaços), sem mudar o comportamento.
</details>

<details>
<summary>2. Cobertura de 100% significa que o código não tem erros?</summary>

Não. Significa que todas as linhas foram executadas pelos testes, mas um teste pode executar uma linha sem conferir se o resultado está certo. Cobertura baixa, por outro lado, garante que há código sem nenhuma verificação.
</details>

<details>
<summary>3. Por que os testes comuns nunca encontraram a condição de corrida?</summary>

Porque fazem um pedido de cada vez: o primeiro empréstimo termina antes de o segundo começar. O defeito só aparece quando dois pedidos se intercalam entre "conferir" e "gravar", e o teste de concorrência força essa situação com threads e uma barreira.
</details>

<details>
<summary>4. O que o <code>select_for_update</code> faz?</summary>

Lê a linha do banco e a trava até o fim da transação. Outros pedidos que tentem travar a mesma linha esperam; quando a trava é liberada, eles leem os dados já atualizados.
</details>

<details>
<summary>5. Por que o <code>ruff</code> e o <code>coverage</code> ficam no <code>requirements-dev.txt</code>?</summary>

Porque só são usados durante o desenvolvimento. O servidor não precisa deles para rodar o sistema, e instalar só o necessário deixa a publicação mais leve e com menos pontos de falha.
</details>

---

Próxima aula: [Aula 10 — Git em equipe e integração contínua](Aula_10_Git_em_Equipe_e_Integracao_Continua.md).
