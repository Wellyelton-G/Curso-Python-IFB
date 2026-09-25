# Resoluções — Aula 9

[Voltar à lista de resoluções](README.md) · [Guia da Aula 9](../Aula_09_Qualidade_de_Codigo_e_Concorrencia.md)

Ponto de partida: projeto ao final da Aula 9 (`gabarito/aula_09`).

---

## Exercício 1 — Cobrir a busca avançada e o formato inválido

> O relatório de cobertura mostra que a página de busca avançada e o erro de formato inválido na exportação (`/exportar/docx/`) nunca foram testados. Escreva os dois testes e confira que as linhas saíram do `Missing`.

No relatório da aula, a linha do `catalog/views.py` que falta aparece assim:

```text
catalog\views.py      201     27    87%   72, 91, 99, 143, 150-151, 159, ...
```

A linha 143 é o `return render(...)` da view `advanced_search`, e a 159 é o `raise Http404(...)` da `export_books`, quando o formato pedido não existe no dicionário `EXPORTERS`. (Os números podem variar um pouco no seu projeto: confira com `coverage html`.)

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar no final

```python
class Aula9ExerciseTests(TestCase):
    """Exercício 1 da Aula 9: cobrir linhas que o relatório de cobertura apontou."""

    def setUp(self):
        self.client.force_login(User.objects.create_user("maria", password="senha-forte-123"))

    def test_pagina_de_busca_avancada_abre(self):
        Book.objects.create(title="Duna", author="Frank Herbert", isbn="1111111111111", language="Português")
        response = self.client.get(reverse("catalog:advanced_search"))
        self.assertContains(response, "Busca avançada")
        self.assertContains(response, "Português")  # o idioma aparece como opção do filtro

    def test_formato_de_exportacao_invalido_da_404(self):
        response = self.client.get(reverse("catalog:export_books", args=["docx"]))
        self.assertEqual(response.status_code, 404)
```

- **O primeiro teste** não confere só que a página abre (código 200): confere que ela mostra o idioma do livro cadastrado como opção do filtro. Assim, o teste também verifica que a função `filter_choices()` levou os dados certos ao template.
- **O segundo teste** confirma que um formato desconhecido dá 404, e não um erro 500. É o tipo de caminho que ninguém testa à mão, porque só acontece quando alguém digita o endereço errado.

**Como conferir:**

```powershell
coverage run manage.py test
coverage report
```

As linhas 143 e 159 saem da coluna `Missing` do `catalog/views.py`, e a cobertura do arquivo sobe.

---

## Exercício 2 — O grupo de regras `SIM`

> Acrescente o grupo de regras `SIM` (simplificações) ao `select` do `pyproject.toml` e rode `ruff check .`. Entenda a sugestão que aparece e corrija o código.

**Arquivo:** `pyproject.toml` · **Ação:** alterar a linha do `select`

```toml
select = ["E", "W", "F", "I", "B", "DJ", "SIM"]  # Exercício 2: SIM = simplificações sugeridas
```

O `ruff check .` aponta um trecho do teste de concorrência:

```text
SIM105 Use `contextlib.suppress(threading.BrokenBarrierError)` instead of `try`-`except`-`pass`
   --> catalog\tests.py:569:13
    |
568 |           def espera_a_outra_pessoa(*args, **kwargs):
569 | /             try:
570 | |                 barreira.wait()  # as duas chegam aqui depois de conferir que "há cópia"
571 | |             except threading.BrokenBarrierError:
572 | |                 pass  # a outra thread não chegou (estava bloqueada esperando a primeira terminar)
    | |____________________^
```

**O que a regra diz:** um `try` cujo `except` só tem `pass` significa "ignore este erro". A biblioteca padrão tem uma forma mais curta e mais clara de dizer isso: `contextlib.suppress`.

**Arquivo:** `catalog/tests.py` · **Ação:** duas alterações

No topo, acrescente o import (o `ruff check --fix .` coloca na ordem):

```python
import contextlib
```

E, dentro do `ConcurrencyTests`, troque a função `espera_a_outra_pessoa` por:

```python
        def espera_a_outra_pessoa(*args, **kwargs):
            # Exercício 2: suppress ignora o erro indicado; se a outra thread não chegar
            # (bloqueada esperando a primeira terminar), a espera acaba e seguimos em frente
            with contextlib.suppress(threading.BrokenBarrierError):
                barreira.wait()  # as duas chegam aqui depois de conferir que "há cópia"
            return localdate_original(*args, **kwargs)
```

O comportamento é exatamente o mesmo: se a barreira for quebrada pelo `timeout`, o erro é ignorado e a função continua.

**Como conferir:** `ruff check .` volta a mostrar `All checks passed!`, e `python manage.py test catalog.tests.ConcurrencyTests` continua passando.

**Uma observação sobre regras de estilo:** nem toda sugestão do grupo `SIM` deixa o código mais fácil de ler para todo mundo. Uma equipe pode ativar o grupo e desligar regras específicas com `ignore = ["SIM108"]` no `pyproject.toml`. O importante é que a decisão seja da equipe e fique registrada no arquivo, e não que cada pessoa siga o seu gosto.

---

## Exercício 3 — Sem o modo `IMMEDIATE`

> Remova temporariamente a linha `"OPTIONS": {"transaction_mode": "IMMEDIATE"}` e rode o teste de concorrência. Explique, com suas palavras, a mensagem de erro que aparece. Depois restaure a linha.

Sem a linha, o teste falha:

```text
Exception in thread Thread-1 (tentar_emprestar):
...
django.db.utils.OperationalError: database is locked
...
AssertionError: Lists differ: ['emprestou'] != ['emprestou', 'recusado']
```

**Explicação.** No modo padrão do SQLite, uma transação começa só lendo: ela só pede permissão para escrever quando chega o primeiro `INSERT`. O que acontece no teste:

1. As duas threads abrem a transação e leem o livro. Ler, as duas podem ao mesmo tempo, e o `select_for_update` não trava nada, porque o SQLite o ignora.
2. As duas conferem que há uma cópia livre e se encontram na barreira.
3. A primeira pede permissão para escrever, consegue e grava o empréstimo.
4. A segunda também pede permissão para escrever, mas o banco já está reservado pela primeira. Esperar não adiantaria: para concluir a gravação, a primeira precisa que a segunda pare de ler, e a segunda está esperando a primeira. As duas ficariam esperando uma pela outra para sempre (um *deadlock*), então o SQLite desiste da segunda na hora, com `database is locked`.

Por isso a lista tem só um `"emprestou"`: a segunda thread terminou com uma exceção, sem chegar a registrar `"recusado"`.

Com o `IMMEDIATE`, a permissão para escrever é pedida **no início** da transação, antes de ler o livro. A segunda thread espera a primeira terminar por inteiro e só então lê o livro, já sem cópias, e recebe a mensagem normal ("Não há cópias disponíveis").

O defeito não sumiu sem o `IMMEDIATE`: nenhuma cópia foi emprestada duas vezes. Mas, para o usuário, um erro 500 no lugar de uma mensagem clara também é um defeito.

Restaure a linha e confira que o teste volta a passar.

---

## A classe de testes completa

O teste do Exercício 1 fica no final de `catalog/tests.py`, e a mudança do Exercício 2 fica dentro do `ConcurrencyTests`.

**Resultado esperado de `python manage.py test`:** 64 testes OK (os 62 da aula mais os 2 do Exercício 1).
