# Resoluções — Aula 10

[Voltar à lista de resoluções](README.md) · [Guia da Aula 10](../Aula_10_Git_em_Equipe_e_Integracao_Continua.md)

Ponto de partida: projeto ao final da Aula 10 (`gabarito/aula_10`), no GitHub, com o CI e as regras da `main` configurados.

Os exercícios desta aula acontecem no GitHub, então as resoluções mostram o roteiro de comandos e o que se espera ver em cada etapa.

---

## Exercício 1 — Ver o CI barrar uma mudança

> Crie uma branch, estrague de propósito a formatação de um arquivo, faça o commit sem rodar o `ruff format` e abra um PR. Veja o CI falhar, encontre na aba Actions a mensagem que explica o problema, corrija e veja o PR ficar verde.

**1. A mudança "com defeito".** Na branch nova, troque as aspas duplas por simples numa linha do `catalog/models.py`:

```powershell
git switch main
git pull
git switch -c teste-ci
```

```python
    due_date = models.DateField('Devolver até')  # só a data do prazo, sem hora
```

```powershell
git add .
git commit -m "Teste do CI"
git push -u origin teste-ci
```

Abra o PR, como no Passo 9 da aula.

**2. O CI falha.** Na página do PR aparece **All checks have failed** e o X vermelho no check `qualidade`. Clique em **Details** (ou abra a aba **Actions**): o passo **Verificar o estilo do código (ruff)** está vermelho, e o passo dos testes nem chegou a rodar. Abrindo o passo com defeito:

```text
All checks passed!
unformatted: File would be reformatted
  --> catalog/models.py:90:33
   |
89 |     borrowed_at = models.DateTimeField("Emprestado em", auto_now_add=True)  # data e hora do empréstimo
   -     due_date = models.DateField('Devolver até')  # só a data do prazo, sem hora
90 +     due_date = models.DateField("Devolver até")  # só a data do prazo, sem hora
91 |     # Vazio (NULL) enquanto o livro não voltar; preenchido na devolução
   |

1 file would be reformatted, 25 files already formatted
Error: Process completed with exit code 1.
```

**Como ler:** o `All checks passed!` é do `ruff check`: nenhum erro provável. Quem falhou foi o `ruff format --check`, que mostra a linha como está (`-`) e como deveria estar (`+`). O `exit code 1` é o sinal de falha que todo programa de terminal devolve, e é assim que o GitHub sabe que o passo não passou. O botão de juntar continua bloqueado pela regra da `main`.

**3. A correção.** No computador, na mesma branch:

```powershell
ruff format .
git add .
git commit -m "Formata o código"
git push
```

O PR se atualiza sozinho, o CI roda de novo e fica verde. Como o PR não traz nenhuma mudança útil, feche-o sem juntar (**Close pull request**) e apague a branch:

```powershell
git switch main
git branch -D teste-ci
```

O `-D` (maiúsculo) apaga a branch mesmo que ela não tenha sido juntada. O `-d` (minúsculo) recusaria, para proteger contra a perda de trabalho.

**O que fica de lição:** o CI não impediu o commit nem o push (isso aconteceu no computador). Ele impediu que o código fora do padrão **entrasse na `main`**. Para não depender do CI, formate antes do commit, ou ative o **Format On Save** do VS Code (Aula 9).

---

## Exercício 2 — Selo do CI no README

> Crie um `README.md` na raiz do projeto, com um título, uma frase sobre o sistema e o selo do CI, que mostra se a última execução passou. Faça a mudança por uma branch e um PR, como qualquer outra.

```powershell
git switch main
git pull
git switch -c readme-com-selo
```

**Arquivo:** `README.md` (na pasta do `manage.py`) · **Ação:** criar

```markdown
# Sistema de Biblioteca

![CI](https://github.com/seu-usuario/biblioteca/actions/workflows/ci.yml/badge.svg)

Sistema de empréstimo de livros feito com Django, com páginas para leitores e equipe e uma API REST.
```

O `README.md` é a primeira coisa que o GitHub mostra na página do repositório. Ele é escrito em **Markdown**, o mesmo formato destes guias: o `#` marca um título, e o `![texto](endereço)` mostra uma imagem.

Troque `seu-usuario` pelo usuário do GitHub da dona do repositório. O endereço tem três partes que precisam bater com o projeto: o usuário, o nome do repositório (`biblioteca`) e o nome do arquivo do workflow (`ci.yml`).

```powershell
git add README.md
git commit -m "Cria o README com o selo do CI"
git push -u origin readme-com-selo
```

Abra o PR, peça a revisão, junte e apague a branch.

**Como conferir:** na página inicial do repositório, o README mostra um selo **CI | passing** em verde. Se a última execução na `main` falhar, o selo muda sozinho para **failing**, em vermelho. Se aparecer uma imagem quebrada, algum dos três nomes do endereço está errado.

**Dica:** na aba **Actions**, ao escolher o workflow **CI** à esquerda, o menu **...** (no canto direito) tem a opção **Create status badge**, que monta o endereço certo.

---

## Exercício 3 — Revisar uma mudança insegura

> A Pessoa A cria uma branch que, "para simplificar", troca `Loan.objects.filter(user=self.request.user)` por `Loan.objects.all()` no `LoanViewSet` do `catalog/api_views.py`, e abre um PR sem explicar o motivo. A Pessoa B revisa. Que problema essa mudança causa? O CI percebeu? Qual teste falhou? Feche o PR sem juntar.

**A mudança** (Pessoa A):

```python
    def get_queryset(self):
        return Loan.objects.all().select_related("book")
```

**O problema.** O `get_queryset` define quais empréstimos a API mostra para quem está pedindo. Com o filtro, cada pessoa vê só os seus. Sem ele, **qualquer usuário logado vê os empréstimos de todo mundo** em `GET /api/emprestimos/` e, pior, consegue **devolver o empréstimo de outra pessoa** com `POST /api/emprestimos/{id}/devolver/`, porque a devolução procura o empréstimo dentro desse mesmo `get_queryset`. É uma falha de segurança do tipo mais comum em APIs: acesso a dados de outras pessoas trocando um número no endereço.

**O CI percebeu.** O check `qualidade` fica vermelho, no passo dos testes:

```text
FAIL: test_cada_um_ve_so_os_proprios_emprestimos (catalog.tests.ApiTests...)
FAIL: test_nao_devolve_emprestimo_de_outra_pessoa (catalog.tests.ApiTests...)
FAILED (failures=2)
```

Os dois testes foram escritos na Aula 8 justamente para proteger essa regra.

**A revisão** (Pessoa B). Um bom comentário, na linha alterada, com **Request changes**:

> Sem o filtro por `self.request.user`, qualquer leitor logado passa a ver e a devolver os empréstimos dos outros (os testes `test_cada_um_ve_so_os_proprios_emprestimos` e `test_nao_devolve_emprestimo_de_outra_pessoa` falharam por isso). Qual era a ideia da simplificação? Se o objetivo for a equipe ver todos os empréstimos, dá para liberar só para `is_staff`, mantendo o filtro para os leitores.

O comentário explica o problema, aponta a evidência (os testes), pergunta o motivo e sugere um caminho. Nada nele fala da pessoa.

**Para refletir:** e se esses testes não existissem? O CI ficaria verde, e o defeito dependeria só da atenção de quem revisa. É por isso que as duas coisas andam juntas: os testes pegam o que já se sabe que precisa ser protegido, e a revisão pega o que ninguém pensou em testar. A pergunta "o que acontece se outra pessoa usar este endereço?" deve fazer parte de toda revisão de código que mexe com dados de usuários.

Feche o PR com **Close pull request** e apague a branch.

---

**Resultado esperado de `python manage.py test`:** 63 testes OK. Os exercícios desta aula não acrescentam testes ao projeto.
