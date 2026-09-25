# Sistema de Biblioteca com Django — Roteiro das 10 aulas

Este roteiro apresenta a ordem das aulas, o que cada uma entrega e como usar os guias.

Ao longo de dez aulas construímos, do zero, um sistema web de biblioteca: publicado na internet, com uma API REST que outros programas podem usar, verificado por ferramentas de qualidade e mantido por uma equipe com Git e integração contínua. O objetivo não é só ter o sistema funcionando, e sim entender por que cada parte existe e como ela se conecta às outras.

---

## O sistema

| Para o leitor | Para a equipe da biblioteca |
|---|---|
| Criar conta, entrar e recuperar a senha | Cadastrar livros, capas e categorias pelo Admin |
| Ver o acervo com as capas | Ver empréstimos atrasados e registrar devoluções |
| Buscar, filtrar, ordenar e paginar | Ver com quem está cada livro |
| Emprestar e devolver livros | Relatórios (populares, leitores ativos, atrasados...) |
| Avaliar livros com nota e comentário | Baixar relatórios em CSV, Excel e PDF |
| Consultar o histórico das próprias buscas | |
| Alternar entre tema claro e escuro | |

---

## As aulas

| Aula | Guia | O que é construído | Conceitos principais |
|:---:|---|---|---|
| 1 | [Fundamentos, modelos e Admin](Aula_01_Fundamentos_Modelos_e_Admin.md) | Projeto, banco de dados e painel administrativo | ambiente virtual, projeto e app, models, ORM, migrações, Django Admin |
| 2 | [Login, páginas e empréstimos](Aula_02_Login_Paginas_e_Emprestimos.md) | Acervo, emprestar e devolver | views, URLs, templates, herança de templates, login, mensagens, GET e POST |
| 3 | [Equipe, busca, paginação e testes](Aula_03_Equipe_Busca_Paginacao_e_Testes.md) | Área da equipe, busca, paginação e testes | permissões, decorators, `Q`, `annotate`, `Paginator`, testes automatizados |
| 4 | [Categorias, busca avançada e exportação](Aula_04_Categorias_Busca_Avancada_e_Exportacao.md) | Categorias, filtros, ordenação, histórico, CSV e Excel, autocompletar | migração com dados existentes, `JSONField`, comandos próprios, refatoração, API JSON |
| 5 | [Contas, detalhes e avaliações](Aula_05_Contas_Detalhes_e_Avaliacoes.md) | Cadastro, recuperação de senha, página do livro, avaliações | formulários (`Form` e `ModelForm`), validação, `UniqueConstraint`, agregação |
| 6 | [Relatórios, banco de dados e revisão](Aula_06_Relatorios_Banco_de_Dados_e_Revisao.md) | Relatórios, PDF, backup e migração para PostgreSQL | `GROUP BY` com o ORM, geração de arquivos, backup e restauração, visão geral |
| 7 | [Publicação na internet](Aula_07_Publicacao_na_Internet.md) | O sistema no ar, em `seunome.pythonanywhere.com` | arquivos estáticos, variáveis de ambiente, `DEBUG` e segurança, GitHub, PythonAnywhere |
| 8 | [API REST com Django REST Framework](Aula_08_API_REST_com_DRF.md) | API da biblioteca com token, documentação interativa e um programa cliente | serializers, viewsets, routers, permissões, autenticação por token, status HTTP, comparação com FastAPI |
| 9 | [Qualidade de código e concorrência](Aula_09_Qualidade_de_Codigo_e_Concorrencia.md) | Código verificado e formatado, cobertura acima de 90% e empréstimo protegido contra pedidos simultâneos | `ruff`, `pyproject.toml`, `coverage`, condição de corrida, transações, `select_for_update`, testes com threads |
| 10 | [Git em equipe e integração contínua](Aula_10_Git_em_Equipe_e_Integracao_Continua.md) | Trabalho em dupla no mesmo repositório, com CI e a `main` protegida | branches, pull requests, revisão de código, conflitos, GitHub Actions, regras de branch |

As aulas devem ser seguidas na ordem: cada uma começa exatamente onde a anterior terminou.

---

## Como os guias estão organizados

Todas as aulas têm a mesma estrutura:

1. **Objetivos da aula.**
2. **Antes de começar:** uma checagem rápida de que a aula anterior está funcionando.
3. **Conceitos:** a ideia por trás do que será feito, explicada antes do código.
4. **Passo a passo:** cada passo indica o **arquivo** e a **ação** (criar, substituir todo o conteúdo ou alterar um trecho). O código vem comentado, e depois dele há uma seção **Entendendo o código**.
5. **Checkpoint:** como conferir se tudo funciona.
6. **Problemas comuns:** os erros mais frequentes e como resolvê-los.
7. **Resumo, exercícios e perguntas de revisão**, com as respostas escondidas para você tentar antes.

### Recomendações

- **Digite o código** sempre que possível, em vez de copiar e colar. Digitar obriga a ler com atenção, e os pequenos erros de digitação ensinam a interpretar mensagens de erro.
- **Leia as mensagens de erro de baixo para cima.** A última linha costuma dizer o problema (`NameError`, `TemplateDoesNotExist`...), e as linhas de cima mostram onde ele aconteceu.
- **Salve os arquivos** (`Ctrl+S`) antes de testar. O servidor do Django recarrega sozinho quando um arquivo `.py` muda.
- **Use o Git.** Ao final de cada aula, faça um commit (`git add .` e `git commit -m "Aula 1 concluída"`). Se algo quebrar, é fácil voltar.
- **Nomes no código em inglês, textos em português.** Variáveis, funções e classes seguem o costume da área e estão em inglês; o que o usuário vê na tela está em português.

---

## O que é preciso ter instalado

- **Python 3.10 ou mais novo**: <https://www.python.org/downloads/>. No Windows, marque **"Add python.exe to PATH"** durante a instalação.
- **VS Code**: <https://code.visualstudio.com/>, com a extensão **Python** da Microsoft.
- **Git**: <https://git-scm.com/downloads>. É recomendado desde a Aula 1 e obrigatório na Aula 7.
- Para a Aula 7: contas gratuitas no **GitHub** (<https://github.com>) e no **PythonAnywhere** (<https://www.pythonanywhere.com>).
- Para a Aula 10: uma dupla, cada pessoa com a sua conta no GitHub.
- Python básico e **orientação a objetos** (classes, herança, métodos), que aparecem o tempo todo no Django.

Os comandos dos guias são para o **PowerShell** do Windows, o terminal padrão do VS Code nesse sistema. Quando há diferença no Linux ou no macOS, ela está indicada.

---

## Versões

| Pacote | Versão | Para quê | Entra na aula |
|---|---|---|---|
| Django | 5.2 | o framework web | 1 |
| Pillow | 11 ou mais nova | guardar imagens (capas) | 1 |
| openpyxl | 3.1 | gerar planilhas Excel | 4 |
| reportlab | 4 ou mais nova | gerar PDF | 6 |
| python-dotenv | 1.0 ou mais nova | ler o arquivo `.env` | 7 |
| djangorestframework | 3.15 ou mais nova | construir a API REST | 8 |
| drf-spectacular | 0.27 ou mais nova | documentação interativa da API | 8 |
| requests | 2 | o programa cliente da API | 8 |
| ruff | 0.16 ou mais nova | verificador e formatador de código (só no desenvolvimento) | 9 |
| coverage | 7 | cobertura de testes (só no desenvolvimento) | 9 |

Os guias usam o template tag `{% querystring %}`, que existe a partir do Django 5.1. A Aula 9 usa a opção `transaction_mode` do SQLite, que também chegou no Django 5.1. Por isso o Django precisa ser da versão 5.1 ou mais nova.

---

## Gabarito

A pasta [gabarito](gabarito/) contém o projeto completo **ao final de cada aula** (`aula_01` a `aula_10`), com o código comentado e testado. Serve para comparar com o seu código quando algo não funcionar. As instruções para rodar um gabarito estão no [README da pasta](gabarito/README.md).

---

## Resoluções dos exercícios

A pasta [resolucoes](resolucoes/) traz a resolução comentada e testada de todos os exercícios, aula por aula. Ela está separada dos guias para que o professor decida quando liberá-la.

---

## Versões anteriores

Os guias usados nas aulas de novembro de 2025 estão na pasta [versoes_anteriores](versoes_anteriores/), apenas para consulta. Os guias das aulas acima substituem todos eles: o conteúdo útil (banco de dados, migração para PostgreSQL, busca, paginação) foi revisado, corrigido e incorporado às aulas.
