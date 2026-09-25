# Resoluções — Aula 7

[Voltar à lista de resoluções](README.md) · [Guia da Aula 7](../Aula_07_Publicacao_na_Internet.md)

Ponto de partida: projeto ao final da Aula 7 (`gabarito/aula_07`).

---

## Exercício 1 — Página 404 própria

> Crie uma página 404 com o visual do sistema. O Django usa o template `templates/404.html` quando `DEBUG = False` e o endereço não existe.

**Arquivo:** `templates/404.html` · **Ação:** criar

```html
{% extends "base.html" %}
{# Exercício 1: o Django usa este template quando DEBUG=False e o endereço não existe #}
{% block title %}Página não encontrada · Biblioteca{% endblock %}
{% block content %}
  <div class="card" style="max-width: 560px; margin: 40px auto;">
    <h1>Página não encontrada</h1>
    <p>O endereço <code>{{ request_path }}</code> não existe ou foi removido.</p>
    <p><a class="btn btn-primary" href="{% url 'catalog:book_list' %}">Voltar ao acervo</a></p>
  </div>
{% endblock %}
```

Não é preciso mexer em views nem em URLs: o Django procura um template com esse nome exato. A variável `request_path` é enviada pelo próprio Django, com o endereço que não foi encontrado.

**Como conferir:** com `DEBUG = True` (o padrão local), continua aparecendo a página técnica amarela do Django. Para ver a página nova no computador, simule produção deixando o `.env` do computador assim:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=qualquer-chave-so-para-este-teste
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

E rode o servidor com:

```powershell
python manage.py runserver --insecure
```

- `127.0.0.1,localhost` em `DJANGO_ALLOWED_HOSTS` é necessário porque, com `DEBUG` desligado, nem o endereço local é aceito se não estiver na lista (a resposta seria `Bad Request (400)`).
- O `--insecure` faz o `runserver` continuar entregando o CSS mesmo com `DEBUG` desligado. Ele serve só para testes locais; no servidor quem entrega o CSS é o PythonAnywhere.

Abra `http://127.0.0.1:8000/nao-existe/`. Nesse modo o **login não funciona**, porque os cookies passam a exigir HTTPS e o `runserver` usa HTTP; para ver a página 404 não é preciso entrar. **Ao terminar, volte o `.env` para `DJANGO_DEBUG=True`.**

**Teste:**

```python
    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_pagina_404_propria(self):
        response = self.client.get("/pagina-que-nao-existe/")
        self.assertContains(response, "Página não encontrada", status_code=404)
        self.assertContains(response, "/pagina-que-nao-existe/", status_code=404)
```

---

## Exercício 2 — Nome da biblioteca por variável de ambiente

> Faça o nome exibido no menu vir de uma variável `LIBRARY_NAME` do `.env`.

**1. Configuração** — `library/settings.py`, logo antes das linhas de cookies seguros:

```python
# Exercício 2: nome exibido no menu e no rodapé (cada instalação pode ter o seu)
LIBRARY_NAME = os.environ.get("LIBRARY_NAME", "Biblioteca")
```

**2. Context processor** — `catalog/context_processors.py` · **Ação:** criar

```python
from django.conf import settings


def library_name(request):
    """Exercício 2: deixa o nome da biblioteca (settings.LIBRARY_NAME) disponível em todos os templates."""
    return {"library_name": settings.LIBRARY_NAME}
```

Se você fez o desafio da Aula 2, o arquivo já existe com a função `loan_counter`: acrescente a função nova no mesmo arquivo, e o `from django.conf import settings` no topo.

**3. Registro** — `library/settings.py`, na lista `context_processors` de `TEMPLATES`:

```python
                'django.contrib.messages.context_processors.messages',
                'catalog.context_processors.library_name',  # Exercício 2
```

**4. Template** — `templates/base.html`, trocando o primeiro link do menu:

```html
      {# Exercício 2: library_name vem do context processor catalog.context_processors.library_name #}
      <a href="{% url 'catalog:book_list' %}"><strong>{{ library_name }}</strong></a>
```

**5. Modelo do `.env`** — `.env.example`, no final, para que quem instalar o sistema saiba que a variável existe:

```text
# Exercício 2: nome da biblioteca exibido no menu e no rodapé
LIBRARY_NAME=Biblioteca
```

**Para usar**, acrescente a linha ao `.env` com o nome desejado. No servidor, abra o `.env` com `nano .env` no console Bash, acrescente a linha abaixo, salve e clique em **Reload** na aba **Web**:

```text
LIBRARY_NAME=Biblioteca do Campus Brasília
```

Nenhuma linha de código muda de um lugar para outro: só o `.env`.

**Por que usar `settings` e não ler `os.environ` direto no context processor?** Porque assim todas as configurações ficam num lugar só (`settings.py`), e os testes podem trocá-las com `@override_settings`, como abaixo.

**Teste:**

```python
    @override_settings(LIBRARY_NAME="Biblioteca do IFB")
    def test_nome_da_biblioteca_vem_da_configuracao(self):
        response = self.client.get(reverse("catalog:book_list"))
        self.assertContains(response, "Biblioteca do IFB")
```

---

## Exercício 3 — Rodapé com o ano atual

> Acrescente um rodapé com o nome da biblioteca e o ano atual.

**Arquivo:** `templates/base.html` · **Ação:** acrescentar logo depois do `</main>`

```html
  {# Exercício 3: {% now "Y" %} escreve o ano atual; o rodapé muda sozinho na virada do ano #}
  <footer class="muted" style="text-align: center; padding: 24px 16px;">
    {{ library_name }} · {% now "Y" %}
  </footer>
```

`{% now %}` usa os mesmos códigos de formato do filtro `date`: `"Y"` é o ano com quatro dígitos, `"d/m/Y"` seria a data completa. O rodapé usa o `library_name` do Exercício 2; se fizer este exercício sozinho, troque por um texto fixo.

**Teste:**

```python
    def test_rodape_com_o_ano_atual(self):
        from django.utils import timezone

        response = self.client.get(reverse("catalog:book_list"))
        self.assertContains(response, str(timezone.localdate().year))
```

---

## A classe de testes completa

```python
class Aula7ExerciseTests(TestCase):
    """Testes das resoluções dos exercícios da Aula 7."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.client.force_login(self.user)
```

Os três métodos de teste mostrados acima ficam dentro dela. O `override_settings` já foi importado na Aula 7.

**Resultado esperado de `python manage.py test`:** 42 testes OK (os 39 da aula mais os 3 destas resoluções).
