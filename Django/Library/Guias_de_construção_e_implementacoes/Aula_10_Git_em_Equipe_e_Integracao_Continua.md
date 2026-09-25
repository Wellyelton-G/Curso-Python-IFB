# Aula 10 — Git em equipe e integração contínua

Sistema de Biblioteca com Django · Aula 10 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- Trabalhar em dupla no mesmo repositório, cada pessoa na sua **branch**.
- Propor mudanças com **pull requests** e fazer **revisão de código**.
- Configurar a **integração contínua** (GitHub Actions): o `ruff` e os testes rodam sozinhos a cada push.
- **Proteger a branch `main`**: nada entra sem pull request, revisão e verificações aprovadas.
- Entender por que acontecem **conflitos** e resolvê-los com calma.

Ao final da aula, o repositório funciona como o de uma equipe profissional: cada mudança passa por uma branch, um pull request, uma revisão e pelas verificações automáticas antes de chegar à `main`.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | **Aula atual** |

## Antes de começar

- [ ] `ruff check .` sem avisos e `python manage.py test` com 62 testes OK (Aula 9).
- [ ] O projeto no GitHub, no repositório `biblioteca` (Aula 7), com tudo enviado (`git status` sem pendências e `git push` feito).
- [ ] Uma dupla. Cada pessoa precisa de uma conta no GitHub.

**Estudando sem dupla?** Você pode fazer os dois papéis: siga os passos da Pessoa B numa segunda pasta, clonando o seu próprio repositório (Passo 2). Só a aprovação do pull request fica de fora, porque o GitHub não deixa ninguém aprovar a própria mudança (veja o Passo 6).

Nesta aula, a dupla é chamada de **Pessoa A** (dona do repositório) e **Pessoa B** (colaboradora). Nos exemplos, os nomes são Ana e Bruno.

---

## Parte 1 — Conceitos

### 1.1 Branches

Até aqui, todos os commits foram feitos direto na `main`. Numa equipe, isso vira um problema: se o Bruno enviar um trabalho pela metade, a `main` de todo mundo quebra.

Uma **branch** (ramo) é uma linha de trabalho separada. A pessoa cria uma branch a partir da `main`, faz os commits nela e, quando termina, **junta** (faz o *merge*) a branch de volta na `main`:

```
main   ──●──────────●───────●──   (sempre funcionando)
          \        /
prazo      ●──●──●                (o trabalho da Ana, em andamento)
```

Enquanto isso, a `main` continua estável e outras pessoas trabalham nas suas próprias branches.

### 1.2 Pull requests e revisão de código

Um **pull request** (PR) é um pedido feito no GitHub: "revisem as mudanças da minha branch e, se estiver tudo certo, juntem na `main`". A página do PR mostra as linhas alteradas, os comentários da revisão e o resultado das verificações automáticas.

Na **revisão de código**, outra pessoa lê as mudanças antes de elas entrarem. A revisão encontra defeitos, espalha o conhecimento pela equipe (mais gente passa a conhecer cada parte do sistema) e mantém o padrão do código. O revisor termina com uma de três respostas:

| Resposta | Significado |
|---|---|
| **Comment** | comentários ou perguntas, sem decisão |
| **Approve** | pode juntar |
| **Request changes** | precisa de ajustes antes de juntar |

### 1.3 Integração contínua

**Integração contínua** (*CI*, de *Continuous Integration*) significa verificar cada mudança automaticamente, assim que ela é enviada. No GitHub, isso é feito pelo **GitHub Actions**: a cada push, o GitHub prepara uma máquina virtual, instala o projeto e roda os mesmos comandos que rodamos no computador (`ruff` e testes). O resultado aparece como um sinal verde ou um X vermelho em cada commit e em cada PR.

O CI garante que "funciona no meu computador" também vale num computador limpo, e que ninguém esquece de rodar os testes antes de juntar uma mudança.

### 1.4 Conflitos

Quando duas branches alteram **linhas diferentes**, o Git junta as duas sozinho. Quando alteram **a mesma linha** de formas diferentes, o Git não tem como saber qual versão vale, e para: é um **conflito**. Resolver um conflito é decidir, com a equipe, como a linha deve ficar. Muitas vezes a resposta é combinar as duas mudanças.

Conflito não é erro de ninguém: é o Git pedindo ajuda para uma decisão que só uma pessoa pode tomar.

---

## Parte 2 — A equipe no mesmo repositório

### Passo 1 — Convidar a dupla (Pessoa A)

1. No repositório `biblioteca` do GitHub, abra **Settings** e, no menu à esquerda, **Collaborators**.
2. Clique em **Add people**, digite o usuário da Pessoa B e confirme.
3. A Pessoa B recebe um e-mail (ou um aviso no GitHub) e precisa **aceitar o convite**.

### Passo 2 — Clonar e preparar o projeto (Pessoa B)

A Pessoa B baixa o projeto e prepara o ambiente do zero, como qualquer pessoa que entrasse na equipe:

```powershell
git clone https://github.com/usuario-da-pessoa-a/biblioteca.git
cd biblioteca
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py test
```

O banco de dados (`db.sqlite3`) não está no GitHub, então o projeto da Pessoa B começa vazio. Para ter dados de exemplo:

```powershell
python manage.py createsuperuser
python manage.py popular_acervo
```

Também não é preciso criar o `.env`: sem ele, o `settings.py` usa os valores de desenvolvimento (Aula 7).

Confira a identidade que vai aparecer nos commits (cada pessoa, no seu computador):

```powershell
git config --global user.name
git config --global user.email
```

Se estiverem vazios, defina com `git config --global user.name "Seu Nome"` e `git config --global user.email "seu-email@exemplo.com"`, usando o mesmo e-mail da conta do GitHub.

---

## Parte 3 — Integração contínua com GitHub Actions

A Pessoa A faz esta parte. A Pessoa B acompanha.

### Passo 3 — O workflow

Um **workflow** é um arquivo que descreve o que o GitHub deve fazer e quando. Ele fica numa pasta com nome obrigatório: `.github/workflows/`, na raiz do repositório (a mesma pasta do `manage.py`).

**Arquivo:** `.github/workflows/ci.yml` · **Ação:** criar (crie as pastas `.github` e `workflows`)

```yaml
# Integração contínua (Aula 10).
# A cada push na main e a cada pull request, o GitHub prepara uma máquina Linux,
# instala o projeto e roda as mesmas verificações que rodamos no computador.
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  qualidade:
    runs-on: ubuntu-latest

    steps:
      - name: Baixar o código do repositório
        uses: actions/checkout@v4

      - name: Instalar o Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: pip  # guarda os pacotes baixados para as próximas execuções ficarem mais rápidas

      - name: Instalar as dependências
        run: pip install -r requirements-dev.txt

      - name: Verificar o estilo do código (ruff)
        run: |
          ruff check .
          ruff format --check .

      - name: Rodar os testes medindo a cobertura
        run: |
          coverage run manage.py test
          coverage report
```

#### Entendendo o arquivo

O arquivo usa o formato **YAML**, em que a **indentação** define a estrutura (como no Python). Use sempre espaços, nunca tabulação.

- **`on`**: quando o workflow roda. Aqui, a cada push na `main` e a cada pull request.
- **`jobs`**: as tarefas. Temos uma só, chamada `qualidade`, que roda numa máquina com Ubuntu Linux (`runs-on`).
- **`steps`**: os passos, executados em ordem. Se um deles falhar, os seguintes não rodam e o resultado fica vermelho.
- **`uses`**: usa uma ação pronta, publicada por outra pessoa ou empresa. A `actions/checkout` baixa o código do repositório, e a `actions/setup-python` instala o Python. O `@v4` e o `@v5` fixam a versão da ação.
- **`run`**: executa comandos no terminal da máquina. O `|` permite escrever vários comandos, um por linha.

Repare que os comandos são exatamente os da Aula 9. O CI não faz nada que você não possa fazer no seu computador: ele só garante que é feito **sempre**.

**Por que o `ruff format --check`, e não `ruff format`?** No CI, não queremos que o código seja alterado: queremos saber se alguém esqueceu de formatar. O `--check` só confere e falha se houver arquivo fora do padrão.

**E o `coverage report`?** Por causa do `fail_under = 90` do `pyproject.toml` (Aula 9), ele falha se a cobertura cair abaixo de 90%. Uma mudança sem testes pode ser barrada pelo CI.

### Passo 4 — O modelo de pull request

Quando alguém abre um PR, o GitHub pode preencher a descrição com um modelo. Isso ajuda a lembrar do que o revisor precisa saber.

**Arquivo:** `.github/pull_request_template.md` · **Ação:** criar

```markdown
## O que mudou

<!-- Descreva a mudança em poucas linhas. Ex.: "Prazo de empréstimo passa de 14 para 21 dias." -->

## Por quê

<!-- O motivo da mudança. Se houver uma issue relacionada, cite o número: "Resolve #12". -->

## Como testar

<!-- O passo a passo para quem vai revisar conferir a mudança. -->

## Conferência

- [ ] Rodei `ruff check .` e `ruff format .`
- [ ] Rodei `python manage.py test` e todos os testes passaram
- [ ] Acrescentei ou ajustei testes para a mudança
```

O que está entre `<!--` e `-->` é um comentário: aparece para quem escreve, mas não na página do PR.

### Passo 5 — Enviar e ver o CI rodando

Esta é a **última vez** que alguém faz commit direto na `main`: no próximo passo, ela será protegida.

```powershell
git add .github
git commit -m "Adiciona integração contínua e modelo de pull request"
git push
```

No GitHub, abra a aba **Actions**. Aparece uma execução com o nome do commit. Clique nela e depois em **qualidade** para ver cada passo sendo executado, com a mesma saída que aparece no seu terminal. Em alguns minutos, cada passo fica com um sinal verde.

Volte à página inicial do repositório: ao lado do último commit aparece o sinal verde (ou um X vermelho, se algo falhou). Se falhar, clique no X, veja qual passo falhou, leia a mensagem, corrija no computador e envie de novo.

A Pessoa B atualiza o projeto dela:

```powershell
git pull
```

---

## Parte 4 — Protegendo a `main`

### Passo 6 — Regras para a branch `main` (Pessoa A)

1. No repositório, abra **Settings** e, no menu à esquerda, **Rules** e depois **Rulesets**.
2. Clique em **New ruleset** e escolha **New branch ruleset**.
3. Preencha:
   - **Ruleset Name:** `proteger-main`
   - **Enforcement status:** **Active**
   - Em **Target branches**, clique em **Add target** e escolha **Include default branch** (a `main`).
4. Em **Branch rules**, marque:
   - **Restrict deletions** e **Block force pushes** (já vêm marcadas): ninguém apaga a `main` nem reescreve a história dela.
   - **Require a pull request before merging**, com **Required approvals** igual a **1**: toda mudança precisa de um PR aprovado por outra pessoa.
   - **Require status checks to pass**: clique em **Add checks**, digite `qualidade` e escolha o job do nosso workflow. Assim, um PR só pode ser juntado com o CI verde.
5. Clique em **Create**.

A partir de agora, um `git push` direto na `main` é recusado pelo GitHub. Todo o trabalho passa por branches e PRs.

**Estudando sem dupla?** Deixe **Required approvals** em **0**. A regra do PR e a do CI continuam valendo.

**Repositório privado?** No plano gratuito do GitHub, as regras só valem em repositórios **públicos**. O repositório da Aula 7 foi criado como público.

---

## Parte 5 — Duas tarefas ao mesmo tempo

Agora, a dupla recebe duas tarefas, e cada pessoa trabalha na sua **ao mesmo tempo**:

- **Ana (Pessoa A):** a biblioteca decidiu aumentar o prazo de empréstimo de 14 para 21 dias.
- **Bruno (Pessoa B):** leitores estão perguntando se o prazo conta fins de semana. O comentário do código precisa deixar claro que são dias corridos.

As duas tarefas mexem na mesma linha do `catalog/services.py`, e é de propósito: é assim que vamos provocar um conflito na Parte 7. Façam os Passos 7 e 8 **em paralelo**, cada pessoa no seu computador, **antes** de qualquer PR ser juntado.

### Passo 7 — A branch da Ana (Pessoa A)

Comece sempre da `main` atualizada e crie a branch:

```powershell
git switch main
git pull
git switch -c prazo-21-dias
```

O `git switch -c` cria a branch e já passa a trabalhar nela. Dê nomes curtos, que digam o que a branch faz. Confira com `git branch`: a branch atual aparece marcada com `*`.

**Arquivo:** `catalog/services.py` · **Ação:** alterar a linha do `LOAN_DAYS`

```python
LOAN_DAYS = 21  # prazo padrão de empréstimo, em dias
```

Toda mudança de regra vem com um teste que a confirma.

**Arquivo:** `catalog/tests.py` · **Ação:** acrescentar no final

```python
class LoanPeriodTests(TestCase):
    """Aula 10: a biblioteca aumentou o prazo de empréstimo para 21 dias."""

    def test_prazo_do_emprestimo_e_de_21_dias(self):
        maria = User.objects.create_user("maria", password="senha-forte-123")
        book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
        loan = services.borrow_book(book, maria)
        # O prazo é contado a partir de hoje
        self.assertEqual(loan.due_date, timezone.localdate() + timedelta(days=21))
```

Confira, faça o commit e envie a branch ao GitHub:

```powershell
ruff check .
ruff format .
python manage.py test
git add .
git commit -m "Aumenta o prazo de empréstimo para 21 dias"
git push -u origin prazo-21-dias
```

O `-u origin prazo-21-dias` cria a branch também no GitHub e liga as duas. Nos próximos envios dessa branch, basta `git push`.

### Passo 8 — A branch do Bruno (Pessoa B)

```powershell
git switch main
git pull
git switch -c comentario-prazo
```

**Arquivo:** `catalog/services.py` · **Ação:** alterar a linha do `LOAN_DAYS`

```python
LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias corridos (contando fins de semana e feriados)
```

```powershell
git add .
git commit -m "Explica que o prazo é em dias corridos"
git push -u origin comentario-prazo
```

### Passo 9 — Abrir os pull requests (as duas pessoas)

Logo depois do push, o GitHub mostra no repositório um aviso amarelo com o botão **Compare & pull request**. Clique nele (ou vá em **Pull requests**, **New pull request** e escolha a sua branch em **compare**).

1. Confira no topo: **base: main** ← **compare: sua branch**.
2. O título já vem com a mensagem do commit. A descrição vem com o modelo do Passo 4: preencha cada seção.
3. À direita, em **Reviewers**, escolha a outra pessoa da dupla.
4. Clique em **Create pull request**.

Na página do PR, lá embaixo, aparece o CI rodando (**Some checks haven't completed yet**) e, logo em seguida, o resultado. Enquanto não houver o sinal verde e uma aprovação, o botão de juntar fica bloqueado: é a regra do Passo 6 funcionando.

---

## Parte 6 — Revisão de código

### Passo 10 — Revisar o PR da Ana (Pessoa B)

O Bruno abre o PR da Ana (aba **Pull requests**) e clica em **Files changed**. Ali aparecem as linhas removidas (em vermelho) e acrescentadas (em verde).

1. Passe o mouse sobre uma linha e clique no **+** azul que aparece: é assim que se comenta um trecho específico. Por exemplo, na linha do teste: "Boa, o teste confere o prazo a partir de hoje."
2. Quando terminar, clique em **Review changes** (ou **Submit review**), escolha **Approve** e confirme.

**O que olhar numa revisão:**

- A mudança faz o que a descrição diz? Faz só isso?
- Há teste para o comportamento novo?
- Os nomes e os comentários estão claros para quem vier depois?
- Há algum risco de segurança? (Por exemplo, uma consulta que deixou de filtrar pelo usuário logado.)
- O CI está verde?

**Como comentar:** comente o código, não a pessoa. "Esse `if` não cobre o caso de zero cópias" é melhor que "você esqueceu o zero". Perguntas também ajudam: "O que acontece se o livro não tiver categoria?". Se a mudança precisar de ajustes, escolha **Request changes**. A autora faz novos commits na mesma branch, envia com `git push`, e o PR se atualiza sozinho.

### Passo 11 — Juntar o PR da Ana (Pessoa A)

Com a aprovação e o CI verde, o botão **Merge pull request** fica disponível.

1. Clique em **Merge pull request** e depois em **Confirm merge**.
2. Clique em **Delete branch**: a branch já cumpriu o seu papel. O histórico dos commits continua na `main`.

No computador, a Ana volta para a `main`, traz a versão nova e apaga a branch local:

```powershell
git switch main
git pull
git branch -d prazo-21-dias
```

Na aba **Actions**, aparece uma nova execução do CI: agora na `main`, por causa do `push` que o merge fez.

---

## Parte 7 — Resolvendo um conflito

### Passo 12 — O conflito aparece (Pessoa B)

Abra agora o PR do Bruno. No lugar do botão de juntar, aparece:

```text
This branch has conflicts that must be resolved
Conflicting files: catalog/services.py
```

O PR da Ana mudou a linha do `LOAN_DAYS` na `main`, e a branch do Bruno mudou a mesma linha. O Git não sabe qual das duas vale.

O Bruno resolve no computador. Primeiro, traz a `main` atualizada do GitHub e tenta juntá-la na sua branch:

```powershell
git switch comentario-prazo
git fetch origin
git merge origin/main
```

- **`git fetch origin`** baixa as novidades do GitHub sem alterar nenhum arquivo.
- **`git merge origin/main`** junta a `main` do GitHub na branch atual.

O Git avisa:

```text
Auto-merging catalog/services.py
CONFLICT (content): Merge conflict in catalog/services.py
Automatic merge failed; fix conflicts and then commit the result.
```

E o `git status` mostra o arquivo em conflito:

```text
Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both modified:   catalog/services.py
```

### Passo 13 — Entendendo as marcações

Abra o `catalog/services.py`. O Git escreveu as duas versões no arquivo, separadas por marcações:

```text
<<<<<<< HEAD
LOAN_DAYS = 14  # prazo padrão de empréstimo, em dias corridos (contando fins de semana e feriados)
=======
LOAN_DAYS = 21  # prazo padrão de empréstimo, em dias
>>>>>>> origin/main
```

| Trecho | O que é |
|---|---|
| entre `<<<<<<< HEAD` e `=======` | a versão da branch atual (a do Bruno) |
| entre `=======` e `>>>>>>> origin/main` | a versão que está chegando (a da `main`, com a mudança da Ana) |

Nenhuma das duas está certa sozinha. A da Ana tem o prazo novo, e a do Bruno tem o comentário melhor. A resolução certa **combina as duas**. Apague as marcações e as duas linhas e deixe:

```python
LOAN_DAYS = 21  # prazo padrão de empréstimo, em dias corridos (contando fins de semana e feriados)
```

O VS Code ajuda: acima das marcações aparecem as opções **Accept Current Change** (fica a sua), **Accept Incoming Change** (fica a que chegou) e **Accept Both Changes** (ficam as duas, uma embaixo da outra). Aqui nenhuma resolve sozinha: a linha precisa ser editada à mão.

**Em caso de dúvida, pergunte.** Se o Bruno não soubesse se o prazo novo era mesmo 21 dias, o certo seria conversar com a Ana antes de decidir. Escolher uma versão sem entender a outra é a forma mais comum de desfazer, sem querer, o trabalho de alguém.

### Passo 14 — Concluir a resolução

Confira que não sobrou nenhuma marcação e que tudo funciona. Os testes são a melhor forma de saber se a combinação ficou certa: se o Bruno tivesse mantido o 14, o teste da Ana falharia.

```powershell
ruff check .
python manage.py test
```

Depois, marque o conflito como resolvido e conclua o merge:

```powershell
git add catalog/services.py
git commit -m "Resolve conflito com a main"
git push
```

O PR do Bruno se atualiza: o aviso de conflito some e o CI roda de novo. A Ana revisa e aprova, o Bruno junta e apaga a branch, e as duas pessoas atualizam a `main`:

```powershell
git switch main
git pull
git branch -d comentario-prazo
```

O histórico mostra como as linhas de trabalho se juntaram:

```powershell
git log --oneline --graph
```

No topo aparecem os commits de merge criados pelo GitHub (`Merge pull request #2 from ...`), o commit "Resolve conflito com a main" e os commits da Ana e do Bruno, ligados por linhas que mostram onde cada branch saiu da `main` e onde voltou. Cada commit tem um código próprio (como `250cd4e`), diferente em cada repositório.

**Se precisar desistir no meio:** `git merge --abort` desfaz a tentativa de merge e deixa a branch como estava antes do `git merge origin/main`.

### Passo 15 — Como evitar conflitos grandes

Conflitos pequenos são normais. Os grandes, que tomam uma tarde, costumam ter as mesmas causas, e dá para evitá-las:

- **Branches curtas:** uma tarefa por branch, com PR aberto em poucos dias.
- **`main` atualizada:** antes de começar uma tarefa, `git switch main` e `git pull`. Em tarefas longas, traga a `main` para a sua branch de vez em quando (`git fetch origin` e `git merge origin/main`).
- **Formatador em todo mundo:** se só uma pessoa roda o `ruff format`, as outras veem conflitos em linhas que só mudaram de aspas. O CI da Parte 3 garante que todos formatam.
- **Conversa:** se duas pessoas vão mexer no mesmo arquivo, vale combinar antes.

---

## Checkpoint

- [ ] A aba **Actions** mostra execuções verdes do CI.
- [ ] Um `git push` direto na `main` é recusado pelo GitHub.
- [ ] Os dois PRs foram revisados, aprovados e juntados, e as branches foram apagadas.
- [ ] O `LOAN_DAYS` na `main` é `21`, com o comentário dos dias corridos.
- [ ] Você resolveu um conflito, entendendo o que era cada versão.
- [ ] `python manage.py test` mostra 63 testes OK nos dois computadores.

Se o sistema está publicado no PythonAnywhere, atualize o servidor como na Aula 7 (`git pull` no console e **Reload** na aba **Web**). O prazo novo passa a valer para os próximos empréstimos.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| A aba **Actions** não mostra nada | O arquivo não está em `.github/workflows/` na raiz do repositório | Confira o caminho e o nome da pasta (`workflows`, no plural) |
| `Invalid workflow file` | Erro de indentação no YAML | Use só espaços e alinhe como no Passo 3 |
| CI vermelho no `ruff format --check`, mas no seu computador passa | O `ruff format` foi rodado depois do commit, ou não foi rodado | Rode `ruff format .`, faça um commit e envie |
| CI vermelho no `coverage report` | Cobertura abaixo de 90% | Escreva testes para as linhas listadas em `Missing` |
| `No module named ...` no CI | A biblioteca foi instalada no seu `.venv`, mas não está no `requirements.txt` | Acrescente ao `requirements.txt` e envie |
| `remote rejected ... Changes must be made through a pull request` | Push direto na `main`, bloqueado pela regra | Crie uma branch (`git switch -c nome`), envie e abra um PR |
| `fatal: The current branch ... has no upstream branch` | Primeiro push de uma branch nova | `git push -u origin nome-da-branch` |
| `Permission denied` no push da Pessoa B | O convite de colaboração não foi aceito | Aceite o convite no e-mail ou em <https://github.com/notifications> |
| O botão de juntar continua bloqueado | Falta aprovação ou o CI ainda não terminou | Veja a lista de pendências no final da página do PR |
| O check `qualidade` não aparece na lista do Passo 6 | O CI ainda não rodou nenhuma vez | Faça o Passo 5 e volte à configuração |
| O Git abre um editor de texto estranho no commit | Faltou o `-m "mensagem"` | No Vim, digite `:wq` e Enter para salvar e sair |
| Os testes demoram vários minutos | O cálculo das senhas é lento de propósito (dificulta ataques) | É normal: cada `create_user` e login leva um tempo |

---

## Resumo

O repositório passou a funcionar como o de uma equipe: branches para cada tarefa, pull requests revisados, verificações automáticas e uma `main` protegida.

O que ficou de ideia principal:

- **Branch** é uma linha de trabalho separada. A `main` só recebe trabalho pronto.
- **Pull request** é o pedido para juntar uma branch, com espaço para revisão e para o resultado do CI.
- **Revisão de código** encontra defeitos e espalha o conhecimento. Comente o código, não a pessoa.
- **Integração contínua** roda as verificações a cada push, num computador limpo. O workflow fica em `.github/workflows/`.
- **Regras na `main`** tornam o processo obrigatório: PR, aprovação e CI verde.
- **Conflito** acontece quando duas branches mudam a mesma linha. Resolver é decidir como a linha deve ficar, muitas vezes combinando as duas mudanças. Os testes confirmam se a decisão ficou certa.

---

## Exercícios

1. Crie uma branch, estrague de propósito a formatação de um arquivo (por exemplo, troque aspas duplas por simples numa linha), faça o commit **sem** rodar o `ruff format` e abra um PR. Veja o CI falhar, encontre na aba **Actions** a mensagem que explica o problema, corrija e veja o PR ficar verde.
2. Crie um `README.md` na raiz do projeto (a pasta do `manage.py`), com um título, uma frase sobre o sistema e o selo do CI, que mostra se a última execução passou:
   ```markdown
   ![CI](https://github.com/seu-usuario/biblioteca/actions/workflows/ci.yml/badge.svg)
   ```
   Faça a mudança por uma branch e um PR, como qualquer outra.
3. Revisão em dupla: a Pessoa A cria uma branch que, "para simplificar", troca `Loan.objects.filter(user=self.request.user)` por `Loan.objects.all()` no `LoanViewSet` do `catalog/api_views.py`, e abre um PR sem explicar o motivo. A Pessoa B revisa. Que problema essa mudança causa? O CI percebeu? Qual teste falhou? Feche o PR sem juntar (**Close pull request**).

---

## Perguntas para revisar

<details>
<summary>1. Por que não trabalhar direto na <code>main</code>?</summary>

Porque a `main` é a versão de todo mundo, e é dela que sai o que vai para o servidor. Trabalho pela metade ou com defeito na `main` atrapalha a equipe inteira. Na branch, a pessoa trabalha à vontade, e a mudança só entra na `main` depois de revisada e verificada.
</details>

<details>
<summary>2. Se os testes já rodam no meu computador, por que rodar no CI?</summary>

Porque o CI roda sempre, para todo mundo, num computador limpo. Ele pega o que a gente esquece (rodar os testes antes do push, formatar o código) e o que só funciona no nosso computador (uma biblioteca instalada no `.venv` mas ausente do `requirements.txt`).
</details>

<details>
<summary>3. O que significam as marcações <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code>, <code>=======</code> e <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code>?</summary>

Elas separam as duas versões de um trecho em conflito: a primeira parte é a versão da branch atual (`HEAD`), e a segunda é a versão que está chegando. A pessoa decide como o trecho deve ficar, apaga as marcações, e conclui com `git add` e `git commit`.
</details>

<details>
<summary>4. No conflito da aula, por que não bastava escolher uma das duas versões?</summary>

Porque cada versão tinha uma mudança válida: a da Ana, o prazo de 21 dias; a do Bruno, o comentário explicando os dias corridos. Escolher uma delas desfaria o trabalho da outra pessoa. A resolução correta combinou as duas na mesma linha.
</details>

<details>
<summary>5. Para que serve exigir uma aprovação antes de juntar um PR?</summary>

Para garantir que toda mudança seja lida por pelo menos mais uma pessoa. A revisão encontra defeitos que os testes não cobrem (como um problema de segurança ou um nome confuso) e faz com que mais de uma pessoa conheça cada parte do sistema.
</details>

---

## Encerramento do curso

O sistema começou como duas classes, `Book` e `Loan`, e terminou com páginas, painel administrativo, busca, relatórios, testes, publicação na internet, uma API que qualquer programa pode usar, verificações automáticas de qualidade e um fluxo de trabalho em equipe. Todo esse caminho passa pelas ideias que se repetiram em cada aula: regras de negócio num lugar só, segurança verificada no servidor, testes para mudar o código com confiança, ferramentas escolhidas conforme o contexto e mudanças revisadas antes de chegar à versão de todo mundo.

[Voltar ao roteiro do curso](README.md)
