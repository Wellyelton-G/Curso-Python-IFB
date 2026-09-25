# Resoluções — Aula 8

[Voltar à lista de resoluções](README.md) · [Guia da Aula 8](../Aula_08_API_REST_com_DRF.md)

Ponto de partida: projeto ao final da Aula 8 (`gabarito/aula_08`).

---

## Exercício 1 — Avaliações de um livro

> Crie o endpoint `GET /api/livros/{id}/avaliacoes/`, público, que devolve as avaliações de um livro.

**1. Serializer** — `catalog/serializers.py`. Acrescente `Review` ao import dos models:

```python
from .models import Book, Category, Loan, Review
```

E, no final do arquivo:

```python
class ReviewSerializer(serializers.ModelSerializer):
    """Exercício 1: avaliação em JSON, com o nome de quem avaliou."""

    user = serializers.CharField(source="user.username", read_only=True)  # o nome, e não o id

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]
```

Declarar o campo `user` com `source="user.username"` troca o id do usuário (o padrão de uma `ForeignKey`) pelo nome, que é mais útil para quem lê as avaliações.

**2. Action** — `catalog/api_views.py`. Acrescente `ReviewSerializer` ao import dos serializers:

```python
from .serializers import BookSerializer, CategorySerializer, LoanSerializer, ReviewSerializer
```

E, dentro do `BookViewSet`, logo depois da action `emprestar`:

```python
    @extend_schema(responses={200: ReviewSerializer(many=True)})
    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def avaliacoes(self, request, pk=None):
        """Exercício 1 — GET /livros/{id}/avaliacoes/: as avaliações do livro, das mais recentes às mais antigas."""
        book = self.get_object()
        reviews = book.reviews.select_related("user")
        # many=True: o serializer recebe uma lista e devolve uma lista em JSON
        return Response(ReviewSerializer(reviews, many=True).data)
```

Não é preciso mexer no `api_urls.py`: o router cria o endereço `livros/{id}/avaliacoes/` a partir do nome da action. A ordem "mais recentes primeiro" vem do `Meta.ordering` do model `Review` (Aula 5).

**Testes:**

```python
    def test_avaliacoes_do_livro(self):
        Review.objects.create(book=self.book, user=self.maria, rating=5, comment="Excelente")
        Review.objects.create(book=self.book, user=self.joao, rating=3)
        response = self.client.get(f"/api/livros/{self.book.id}/avaliacoes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([r["user"] for r in response.data], ["joao", "maria"])  # mais recentes primeiro
        self.assertEqual(response.data[1]["comment"], "Excelente")

    def test_avaliacoes_de_livro_inexistente(self):
        self.assertEqual(self.client.get("/api/livros/9999/avaliacoes/").status_code, 404)
```

---

## Exercício 2 — Limite de pedidos (throttling)

> Visitantes podem fazer até 100 pedidos por hora, e usuários logados até 1000. Passando do limite, a API deve responder 429.

**Arquivo:** `library/settings.py` · **Ação:** acrescentar duas chaves ao dicionário `REST_FRAMEWORK`, logo depois de `"DEFAULT_SCHEMA_CLASS"`

```python
    # Quem gera a descrição da API para a documentação automática
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Exercício 2: limite de pedidos (throttling). Passou do limite, a resposta é 429 Too Many Requests.
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # visitantes: contados pelo endereço IP
        "rest_framework.throttling.UserRateThrottle",  # usuários autenticados: contados pelo usuário
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}
```

**Por que limitar?** Sem limite, um programa com defeito (ou mal-intencionado) pode fazer milhares de pedidos por minuto e deixar o sistema lento para todos. As APIs públicas costumam informar esses limites na documentação.

**Como funciona:** o DRF guarda as contagens no **cache** do Django. Sem configuração, esse cache fica na memória de cada processo do servidor. É suficiente para o curso; em sistemas maiores, o cache costuma ficar num serviço compartilhado, como o Redis.

**Teste:** esperar 100 pedidos deixaria o teste lento, então ele diminui o limite para 3 por minuto só durante a execução. Acrescente três imports no topo de `catalog/tests.py`, nos grupos já existentes:

```python
from django.core.cache import cache  # Exercício 2 (Aula 8)
```

```python
from rest_framework.settings import api_settings  # Exercício 2 (Aula 8)
```

```python
from rest_framework.throttling import AnonRateThrottle  # Exercício 2 (Aula 8)
```

E, na primeira linha do arquivo:

```python
import unittest.mock
```

O teste:

```python
    def test_limite_de_pedidos_para_visitantes(self):
        # Diminui o limite só neste teste: 3 pedidos por minuto
        rates = {**api_settings.DEFAULT_THROTTLE_RATES, "anon": "3/min"}
        with unittest.mock.patch.object(AnonRateThrottle, "THROTTLE_RATES", rates):
            respostas = [self.client.get("/api/livros/").status_code for _ in range(4)]
        self.assertEqual(respostas, [200, 200, 200, 429])  # o quarto pedido é recusado
```

- **`unittest.mock.patch.object(...)`** troca um atributo por outro valor só dentro do bloco `with` e depois devolve o original. Aqui ele troca a tabela de limites lida pelo `AnonRateThrottle`.
- **O `cache.clear()` no `setUp`** da classe (veja abaixo) zera as contagens antes de cada teste. Sem ele, os pedidos de um teste contariam para o próximo.

---

## Exercício 3 — Exportar o acervo inteiro para CSV

> Crie a função `exportar_csv()`, que percorre todas as páginas de `/api/livros/` e grava o acervo num arquivo CSV.

**Arquivo:** `cliente_api.py` · **Ação:** três alterações

Acrescente `import csv` aos imports:

```python
import csv
import sys
from getpass import getpass  # lê a senha sem mostrá-la na tela
```

Acrescente a função logo antes da `obter_token`:

```python
def exportar_csv(caminho="acervo.csv"):
    """Exercício 3: percorre TODAS as páginas de /livros/ e grava o acervo num arquivo CSV."""
    livros = []
    url = f"{BASE_URL}/livros/"
    while url:  # a última página tem "next": null, que vira None em Python e encerra o laço
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        livros.extend(dados["results"])
        url = dados["next"]  # endereço da próxima página, montado pela própria API
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:  # utf-8-sig: acentos certos no Excel
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["id", "título", "autor", "disponíveis"])
        for livro in livros:
            escritor.writerow([livro["id"], livro["title"], livro["author"], livro["available"]])
    print(f"{len(livros)} livro(s) exportado(s) para {caminho}.")
```

E, no `main`, logo depois da listagem:

```python
    listar_livros(input("Buscar livros (Enter para ver todos): ").strip())
    if input("Exportar o acervo inteiro para acervo.csv? (s/N) ").strip().lower() == "s":
        exportar_csv()  # Exercício 3
```

**O ponto central é o laço `while url`.** A API devolve 10 livros por página e informa, no campo `next`, o endereço da página seguinte. Na última página, `next` vale `null` no JSON, que vira `None` em Python e encerra o laço. O cliente não precisa saber quantas páginas existem nem montar os endereços: ele segue o que a API indica.

O `encoding="utf-8-sig"` grava o mesmo BOM visto na exportação da Aula 4, para o Excel reconhecer os acentos.

**Como conferir:** com o acervo de exemplo (27 livros), a exportação percorre 3 páginas e o arquivo fica com 28 linhas (o cabeçalho e os 27 livros).

---

## A classe de testes completa

Os testes dos Exercícios 1 e 2 ficam juntos, no final de `catalog/tests.py`:

```python
class Aula8ExerciseTests(APITestCase):
    """Testes das resoluções dos exercícios da Aula 8."""

    def setUp(self):
        cache.clear()  # o throttling guarda as contagens no cache: cada teste começa do zero
        self.maria = User.objects.create_user("maria", password="senha-forte-123")
        self.joao = User.objects.create_user("joao", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
```

**Resultado esperado de `python manage.py test`:** 61 testes OK (os 58 da aula mais os 3 destas resoluções).
