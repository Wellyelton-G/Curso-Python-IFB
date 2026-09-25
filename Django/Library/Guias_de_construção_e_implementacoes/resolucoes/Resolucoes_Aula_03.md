# Resoluções — Aula 3

[Voltar à lista de resoluções](README.md) · [Guia da Aula 3](../Aula_03_Equipe_Busca_Paginacao_e_Testes.md)

Ponto de partida: projeto ao final da Aula 3 (`gabarito/aula_03`).

---

## Exercício 1 — 5 livros por página

> Troque `BOOKS_PER_PAGE` para 5 e observe a paginação. Algum teste quebrou? Por quê?

**Resposta:** sim, um teste quebra:

```text
FAIL: test_paginacao_mostra_10_por_pagina (catalog.tests.BookListViewTests.test_paginacao_mostra_10_por_pagina)
AssertionError: 5 != 10
```

O teste foi escrito para a regra "10 livros por página". Ao mudar a regra, o teste avisa que o comportamento mudou. Isso **não é um defeito dos testes**, é exatamente o papel deles: toda mudança de comportamento precisa ser consciente.

Se a mudança fosse definitiva, o teste deveria acompanhar a nova regra. Uma forma de deixá-lo mais resistente é usar a própria constante no lugar do número fixo:

```python
from .views import BOOKS_PER_PAGE

# ... dentro do teste:
self.assertEqual(len(response.context["page_obj"]), BOOKS_PER_PAGE)
```

Depois do exercício, volte `BOOKS_PER_PAGE` para 10.

---

## Exercício 2 — E-mail na lista de atrasados

> Na página de atrasados, mostre também o e-mail do leitor.

**Arquivo:** `templates/catalog/overdue_loans.html` · **Ação:** duas alterações

```html
            <th>Leitor(a)</th>
            <th>E-mail</th>
```

```html
              <td>{{ loan.user.username }}</td>
              {# O e-mail é opcional no cadastro: default mostra um travessão quando está vazio #}
              <td>{{ loan.user.email|default:"—" }}</td>
```

A view já usa `select_related("book", "user")`, então o e-mail vem na mesma consulta.

---

## Exercício 3 — Teste de busca por ISBN

> Escreva o teste `test_busca_por_isbn` seguindo o modelo do `test_busca_por_autor`.

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar à classe `BookListViewTests`

```python
    def test_busca_por_isbn(self):
        # Exercício 3: um pedaço do ISBN já basta, porque a busca usa __icontains
        response = self.client.get(reverse("catalog:book_list"), {"q": "22222"})
        self.assertContains(response, "Capitães da Areia")
        self.assertNotContains(response, "Dom Casmurro")
```

O teste usa os dois livros criados no `setUp` da classe (ISBNs `1111111111111` e `2222222222222`).

---

## Exercício 4 (desafio) — `days_overdue`

> Crie no model `Loan` uma `@property` chamada `days_overdue`, que devolve o número de dias de atraso (0 se não houver atraso). Use-a na página de atrasados e escreva um teste para ela.

**Arquivo:** `catalog/models.py` · **Ação:** acrescentar à classe `Loan`, logo acima de `mark_returned`

```python
    @property
    def days_overdue(self):
        """Quantos dias de atraso o empréstimo tem hoje (0 se não estiver atrasado)."""
        if not self.is_overdue:
            return 0
        # Subtrair duas datas dá um timedelta; .days é o número de dias
        return (timezone.localdate() - self.due_date).days

    def mark_returned(self):
```

**Arquivo:** `templates/catalog/overdue_loans.html` · **Ação:** trocar o cabeçalho "Tempo de atraso" por "Dias de atraso" e a célula do `timesince` por:

```html
              {# days_overdue é a @property criada no model Loan #}
              <td>{{ loan.days_overdue }}</td>
```

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar à classe `LoanModelTests`

```python
    def test_days_overdue(self):
        # Exercício 4: 3 dias de atraso; em dia = 0; devolvido = 0
        atrasado = make_loan(self.book, self.user, days=-3)
        em_dia = make_loan(self.book, self.user, days=5)
        self.assertEqual(atrasado.days_overdue, 3)
        self.assertEqual(em_dia.days_overdue, 0)
        atrasado.mark_returned()
        self.assertEqual(atrasado.days_overdue, 0)
```

A property reaproveita `is_overdue`. Assim, a regra "o que é estar atrasado" continua num lugar só.

**Resultado esperado de `python manage.py test`:** 16 testes OK (os 14 da aula mais os 2 destas resoluções).
