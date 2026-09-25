# Resoluções — Aula 2

[Voltar à lista de resoluções](README.md) · [Guia da Aula 2](../Aula_02_Login_Paginas_e_Emprestimos.md)

Ponto de partida: projeto ao final da Aula 2 (`gabarito/aula_02`).

---

## Exercício 1 — Prazo de 21 dias

> Mude o prazo de empréstimo para 21 dias. Quantos lugares do código precisaram ser alterados?

**Arquivo:** `catalog/views.py` · **Ação:** alterar uma linha

```python
LOAN_DAYS = 21  # prazo padrão de empréstimo, em dias
```

**Resposta:** apenas **um** lugar. A view usa a constante para calcular o prazo (`timedelta(days=LOAN_DAYS)`), e a mensagem mostra a data já calculada. É exatamente para isso que servem as constantes: se o número 14 estivesse escrito direto em vários pontos do código, seria fácil esquecer algum.

---

## Exercício 2 — Capa em "Meus empréstimos"

> Em `my_loans.html`, mostre a capa do livro numa nova primeira coluna.

**Arquivo:** `templates/catalog/my_loans.html` · **Ação:** duas alterações

No cabeçalho, acrescente a coluna antes de "Livro":

```html
          <tr>
            <th>Capa</th>
            <th>Livro</th>
```

No corpo, acrescente a célula logo depois de `<tr>`:

```html
            <tr>
              <td>
                {# Mesma lógica da book_list, só que chegando ao livro por loan.book #}
                {% if loan.book.image %}
                  <img class="cover" src="{{ loan.book.image.url }}" alt="Capa de {{ loan.book.title }}">
                {% else %}
                  <div class="cover">sem capa</div>
                {% endif %}
              </td>
              {# loan.book segue a ForeignKey até o livro #}
```

Como a view já usa `select_related("book")`, mostrar a capa não gera nenhuma consulta extra ao banco.

---

## Exercício 3 — Coluna de ISBN

> No acervo, acrescente uma coluna com o ISBN, usando a classe `muted`.

**Arquivo:** `templates/catalog/book_list.html` · **Ação:** duas alterações

```html
            <th>Autor(a)</th>
            <th>ISBN</th>
            <th>Disponíveis</th>
```

```html
              <td>{{ book.author }}</td>
              <td class="muted">{{ book.isbn }}</td>
```

Lembrete: a quantidade de `<td>` de cada linha precisa ser igual à quantidade de `<th>` do cabeçalho, senão as colunas ficam desalinhadas.

---

## Exercício 4 (desafio) — Contador de empréstimos no menu

> Ao lado de "Meus empréstimos", mostre quantos livros a pessoa tem com ela no momento. Dá para fazer só no template? Por que seria melhor calcular na view?

**Só no template não dá.** `{{ user.loans.count }}` funciona, mas conta **todos** os empréstimos, inclusive os devolvidos. A linguagem de templates não permite chamar `filter(returned_at__isnull=True)`, porque ela não aceita métodos com argumentos. E isso é proposital: consultas ao banco não devem ficar no template.

**Na view também tem um problema.** O menu está no `base.html`, que aparece em **todas** as páginas. Calcular na view obrigaria a repetir o mesmo código em todas as views.

**A solução do Django para esse caso é um *context processor*:** uma função que acrescenta variáveis ao contexto de todos os templates, do mesmo jeito que o `{{ user }}` aparece em qualquer página.

**Arquivo:** `catalog/context_processors.py` · **Ação:** criar

```python
def loan_counter(request):
    """Coloca em TODOS os templates a quantidade de livros que o usuário está com ele agora.

    Um context processor é uma função que recebe o request e devolve um dicionário.
    O Django junta esse dicionário ao contexto de todas as páginas, como faz com {{ user }}.
    """
    if not request.user.is_authenticated:
        return {}  # visitante sem login: nada a acrescentar
    count = request.user.loans.filter(returned_at__isnull=True).count()
    return {"active_loans_count": count}
```

**Arquivo:** `library/settings.py` · **Ação:** registrar o context processor na lista `context_processors` de `TEMPLATES`

```python
                'django.contrib.messages.context_processors.messages',
                'catalog.context_processors.loan_counter',  # contador de empréstimos no menu
```

**Arquivo:** `templates/base.html` · **Ação:** trocar o link "Meus empréstimos"

```html
        {# active_loans_count vem do context processor catalog.context_processors.loan_counter #}
        <a href="{% url 'catalog:my_loans' %}">Meus empréstimos ({{ active_loans_count }})</a>
```

**Como conferir:** entre com a `maria`. O menu mostra "Meus empréstimos (0)". Empreste um livro: passa para "(1)". Devolva: volta para "(0)".

**Custo:** o context processor roda uma consulta a cada página carregada. Para um contador simples isso é aceitável; para cálculos pesados, seria melhor guardar o resultado em cache.
