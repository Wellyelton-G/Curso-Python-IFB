# Aula 7 — Publicando o sistema na internet

Sistema de Biblioteca com Django · Aula 7 de 10 · [Roteiro do curso](README.md)

## Objetivos da aula

- Entender a diferença entre **rodar localmente** e **publicar**.
- Separar o CSS e o JavaScript em **arquivos estáticos**.
- Tirar do código as **configurações sensíveis** (chave secreta, modo de depuração, endereços permitidos) e passá-las para **variáveis de ambiente**, guardadas num arquivo **`.env`**.
- Enviar o projeto ao **GitHub**.
- Publicar o sistema no **PythonAnywhere**, com um endereço como `https://seunome.pythonanywhere.com`.
- Saber **atualizar** o site publicado depois de mudar o código.

Ao final da aula, o sistema estará na internet, acessível pelo celular ou por qualquer computador.

| Aula 1 | Aula 2 | Aula 3 | Aula 4 | Aula 5 | Aula 6 | Aula 7 | Aula 8 | Aula 9 | Aula 10 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concluída | Concluída | Concluída | Concluída | Concluída | Concluída | **Aula atual** | API REST | Qualidade de código | Git em equipe |

## Antes de começar

- [ ] Ambiente virtual ativo e `python manage.py test` com 36 testes OK (Aula 6).
- [ ] Uma conta no **GitHub** (<https://github.com>), com o **Git** instalado no computador.
- [ ] Uma conta gratuita no **PythonAnywhere** (<https://www.pythonanywhere.com>, plano *Beginner*). O **nome de usuário** escolhido fará parte do endereço do site: `nomedousuario.pythonanywhere.com`.

---

## Parte 1 — Conceitos

### 1.1 Rodar localmente e publicar

| | Localmente | Publicado |
|---|---|---|
| Endereço | `http://127.0.0.1:8000` | `https://seunome.pythonanywhere.com` |
| Quem acessa | só o seu computador | qualquer pessoa na internet |
| Quem executa o Django | `python manage.py runserver` | um servidor web (no PythonAnywhere, o próprio serviço) |
| `DEBUG` | `True`: erros detalhados na tela | `False`: páginas de erro simples |
| Banco de dados | `db.sqlite3` do seu computador | um `db.sqlite3` próprio, no servidor |

O `runserver` foi feito para desenvolvimento. Num servidor, quem recebe os pedidos é um **servidor web**, que conversa com o Django por uma interface chamada **WSGI**. É por isso que existe o arquivo `library/wsgi.py`, que o Django criou lá na Aula 1.

### 1.2 Por que `DEBUG = False` em produção

Com `DEBUG = True`, qualquer erro mostra uma página detalhada: trechos do código, configurações, variáveis. Isso ajuda muito no desenvolvimento, mas na internet entregaria informações do sistema a qualquer visitante. Em produção, `DEBUG` precisa ser `False`.

Com `DEBUG = False`, duas coisas mudam:

- O Django **deixa de servir** os arquivos estáticos (CSS, JavaScript) e as imagens enviadas. Quem passa a entregá-los é o servidor web.
- O Django **só aceita** pedidos para os endereços listados em `ALLOWED_HOSTS`.

### 1.3 A chave secreta

O `SECRET_KEY` assina as sessões de login, os links de recuperação de senha e os tokens CSRF. Quem conhece a chave consegue forjar essas assinaturas. Como o código vai para o GitHub, a chave de produção **não pode estar escrita no código**: ela fica numa **variável de ambiente**, definida só no servidor.

Uma **variável de ambiente** é um valor com nome (`DJANGO_DEBUG=False`, por exemplo) que o sistema operacional entrega aos programas quando eles iniciam. O Python lê essas variáveis com `os.environ`. Assim, o mesmo código se comporta de um jeito no seu computador e de outro no servidor, sem nenhuma alteração.

### 1.4 Arquivos estáticos

Até agora o CSS e o JavaScript estavam dentro do `base.html`. Em produção, o normal é mantê-los em arquivos próprios, que o navegador guarda em cache e o servidor entrega sem passar pelo Django. O Django organiza isso assim:

- Os arquivos ficam na pasta `static/` do projeto.
- Nos templates, o endereço é gerado com `{% static 'css/style.css' %}`.
- No servidor, o comando `collectstatic` **copia** todos os arquivos estáticos (os nossos e os do Admin) para uma única pasta, `staticfiles/`, que o servidor web entrega diretamente.

### 1.5 O arquivo `.env`

Definir variáveis de ambiente uma a uma, a cada terminal aberto, é trabalhoso e fácil de esquecer. A prática mais comum é reuni-las num arquivo de texto chamado **`.env`**, na pasta do projeto:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=uma-chave-longa-e-aleatoria
DJANGO_ALLOWED_HOSTS=seunome.pythonanywhere.com
```

A biblioteca **`python-dotenv`** lê esse arquivo quando o Django inicia e coloca cada linha em `os.environ`. O `.env` sempre anda acompanhado de um arquivo-modelo:

| Arquivo | Vai para o GitHub? | Conteúdo |
|---|---|---|
| `.env` | **Não** (está no `.gitignore`) | os valores reais, inclusive a chave secreta |
| `.env.example` | Sim | só os **nomes** das variáveis, com comentários e sem valores secretos: serve de modelo |

Cada lugar onde o sistema roda (o seu computador, o servidor, o computador de um colega) tem o **seu próprio** `.env`, criado a partir do `.env.example`. Esse padrão aparece em praticamente todo projeto Python, Node.js ou Docker.

---

## Parte 2 — Preparando o projeto

### Passo 1 — Arquivos estáticos

Crie as pastas `static/css` e `static/js` ao lado do `manage.py`:

```powershell
mkdir static\css, static\js
```

**1.1) O CSS.** Crie o arquivo `static/css/style.css`. Abra o `templates/base.html`, **recorte** tudo o que está entre `<style>` e `</style>` (sem as duas tags) e cole no `style.css`. Depois selecione todo o texto colado e tire o recuo com `Shift+Tab` (pressione mais de uma vez, se preciso) até as linhas começarem na margem. Por fim, acrescente na primeira linha o comentário que aparece abaixo. O começo do arquivo fica assim:

```css
/* Estilos do sistema. Carregado por templates/base.html com {% static 'css/style.css' %}. */

/* 1) Cores do tema claro, guardadas em variáveis CSS */
:root {
  --bg: #f6f7f9;       /* fundo da página */
  --card: #ffffff;     /* fundo de cartões, tabelas e campos */
```

**1.2) O JavaScript.** Crie o arquivo `static/js/theme.js`. No `base.html`, recorte tudo o que está entre `<script>` e `</script>` no final da página (sem as duas tags), cole no `theme.js` e tire o recuo do mesmo jeito. O começo fica assim:

```javascript
// Tema claro/escuro: a escolha fica guardada no navegador (localStorage)
(function () {
  const root = document.documentElement; // a tag <html>
  const button = document.getElementById("theme-toggle");
```

**1.3) O `base.html`.** Agora faça três alterações no template.

Na **primeira linha** do arquivo, antes do `<!DOCTYPE html>`, acrescente:

```html
{% load static %}
```

No lugar do bloco `<style>...</style>` (que agora está vazio), coloque:

```html
  {# Os estilos ficam em static/css/style.css #}
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
```

No lugar do bloco `<script>...</script>` do final, coloque:

```html
  {# O script do tema fica em static/js/theme.js #}
  <script src="{% static 'js/theme.js' %}"></script>
```

- `{% load static %}` habilita a tag `{% static %}` neste template.
- `{% static 'css/style.css' %}` vira `/static/css/style.css`. Assim como o `{% url %}`, o endereço não é escrito à mão: se a configuração mudar, os templates acompanham.
- O `<script>` do autocompletar na `book_list.html` continua dentro do template, porque ele usa `{% url %}`, e tags do Django só funcionam dentro de templates, não em arquivos `.js`.

### Passo 2 — Configurações por variáveis de ambiente

Instale o `python-dotenv`:

```powershell
pip install python-dotenv
```

**Arquivo:** `library/settings.py` · **Ação:** quatro alterações

**2.1)** No topo, troque a linha `from pathlib import Path` por:

```python
import os  # para ler variáveis de ambiente
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv  # lê o arquivo .env (biblioteca python-dotenv)
```

**2.2)** Logo abaixo da linha `BASE_DIR = Path(__file__).resolve().parent.parent`, acrescente:

```python
# Carrega as variáveis do arquivo .env, se ele existir, para dentro de os.environ.
# Variáveis que já existem no sistema têm prioridade e não são substituídas.
load_dotenv(BASE_DIR / ".env")
```

**2.3)** Localize este trecho, que o Django criou na Aula 1 (a sua chave é diferente, porque cada projeto recebe uma):

```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-...'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
```

E substitua o trecho inteiro por:

```python
# Configurações sensíveis vêm de variáveis de ambiente (definidas no sistema ou no arquivo .env).
# No seu computador nenhuma precisa ser definida: os valores padrão servem para desenvolvimento.
# No servidor, elas ficam no arquivo .env, que nunca vai para o GitHub (veja a Aula 7).

# DJANGO_DEBUG: "True" no desenvolvimento, "False" no servidor.
# O "or" faz uma variável vazia no .env (ex.: "DJANGO_DEBUG=") valer como não definida.
DEBUG = (os.environ.get("DJANGO_DEBUG") or "True") == "True"

# Chave secreta usada para assinar sessões, links de redefinição de senha e tokens CSRF
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "django-insecure-chave-apenas-para-desenvolvimento"
if not DEBUG and SECRET_KEY.startswith("django-insecure"):
    # Impede que o site vá ao ar com a chave de desenvolvimento, que está publicada no GitHub
    raise ImproperlyConfigured("Defina a variável de ambiente DJANGO_SECRET_KEY.")

# Endereços pelos quais o site pode ser acessado, separados por vírgula (ex.: "maria.pythonanywhere.com").
# Com DEBUG=True e a lista vazia, o Django aceita localhost e 127.0.0.1.
ALLOWED_HOSTS = [host for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host]

# Formulários enviados por HTTPS a partir desses endereços passam pela proteção CSRF
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# Fora do desenvolvimento, os cookies de sessão e de CSRF só trafegam por HTTPS
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
```

**2.4)** Troque a linha `STATIC_URL = 'static/'` por:

```python
STATIC_URL = 'static/'  # endereço dos arquivos estáticos no navegador: /static/css/style.css
STATICFILES_DIRS = [BASE_DIR / 'static']  # pasta onde ficam os nossos CSS e JavaScript
STATIC_ROOT = BASE_DIR / 'staticfiles'  # pasta para onde o collectstatic copia tudo (usada no servidor)
```

#### Entendendo o código

- **`load_dotenv(BASE_DIR / ".env")`** procura o arquivo `.env` na pasta do projeto e copia cada linha dele para `os.environ`. Se o arquivo não existir, nada acontece. Se uma variável já estiver definida no sistema, ela vale mais que a do `.env`.
- **`os.environ.get("NOME")`** lê uma variável de ambiente e devolve `None` se ela não existir. No seu computador nenhuma variável foi definida, então tudo continua como antes: `DEBUG` ligado e a chave de desenvolvimento.
- **O `or`** cobre um descuido comum no `.env`: deixar a linha sem valor, como `DJANGO_SECRET_KEY=`. Nesse caso a variável existe, mas vale `""` (texto vazio). Como texto vazio conta como falso em Python, `"" or "padrão"` resulta em `"padrão"`.
- **`DEBUG = (...) == "True"`**: variáveis de ambiente são sempre texto. A comparação transforma o texto `"True"` no valor booleano `True`; qualquer outro valor (como `"False"`) vira `False`.
- **A verificação da chave** faz o sistema se recusar a iniciar se alguém desligar o `DEBUG` sem definir uma chave de verdade. É melhor um erro claro na hora da publicação do que um site no ar com uma chave que está no GitHub.
- **`ALLOWED_HOSTS`**: o texto `"maria.pythonanywhere.com,www.exemplo.com"` vira a lista `["maria.pythonanywhere.com", "www.exemplo.com"]`. O `if host` descarta itens vazios.
- **`CSRF_TRUSTED_ORIGINS`**: diz à proteção CSRF que formulários vindos de `https://` desses endereços são legítimos. No PythonAnywhere, o HTTPS é tratado antes de o pedido chegar ao Django, e sem esta linha o login poderia ser recusado com erro 403.
- **Cookies seguros**: com `DEBUG` desligado, os cookies de sessão e de CSRF só são enviados por HTTPS, o que evita que alguém na mesma rede os capture.

### Passo 3 — Testes da publicação

**Arquivo:** `catalog/tests.py` · **Ação:** trocar um import e acrescentar uma classe no final

Troque `from django.test import TestCase` por:

```python
from django.test import TestCase, override_settings
```

E acrescente no final do arquivo:

```python
class DeployTests(TestCase):
    """Testes da Aula 7: arquivos estáticos e funcionamento com DEBUG desligado."""

    def setUp(self):
        self.user = User.objects.create_user("maria", password="senha-forte-123")
        self.book = Book.objects.create(title="Dom Casmurro", author="Machado de Assis", isbn="1111111111111")
        self.client.force_login(self.user)

    def test_css_e_js_vem_de_arquivos_estaticos(self):
        response = self.client.get(reverse("catalog:book_list"))
        self.assertContains(response, "/static/css/style.css")
        self.assertContains(response, "/static/js/theme.js")

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_paginas_funcionam_com_debug_desligado(self):
        # Simula o servidor: DEBUG=False e apenas o endereço permitido
        for url in [reverse("catalog:book_list"), reverse("catalog:book_detail", args=[self.book.id]),
                    reverse("catalog:my_loans")]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_endereco_inexistente_da_404_sem_detalhes(self):
        response = self.client.get("/pagina-que-nao-existe/")
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Using the URLconf", status_code=404)  # sem a página técnica do DEBUG
```

- **`@override_settings(...)`** muda configurações só durante aquele teste. Assim dá para testar o comportamento de produção (`DEBUG=False`) sem mexer no `settings.py`.
- O último teste confirma que, com `DEBUG` desligado, um endereço inexistente mostra uma página 404 simples, sem a página técnica que lista as rotas do sistema.

Rode:

```powershell
python manage.py test
```

O resultado esperado é `Ran 39 tests ... OK`. Rode também o sistema com `python manage.py runserver` e confirme que o visual e o botão de tema continuam funcionando: agora eles vêm dos arquivos estáticos.

### Passo 4 — O `.env.example`, o `.gitignore` e o `requirements.txt`

**4.1) O modelo do `.env`.** Crie o arquivo `.env.example` na pasta do projeto (ao lado do `manage.py`):

**Arquivo:** `.env.example` · **Ação:** criar

```text
# Modelo do arquivo .env. Este arquivo VAI para o GitHub; o .env de verdade NÃO vai.
# Para usar: copie este arquivo com o nome .env e preencha os valores.
# Linhas começadas com # são comentários.

# True no computador, False no servidor
DJANGO_DEBUG=True

# Chave secreta. Obrigatória quando DJANGO_DEBUG=False. Gere uma com:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY=

# Endereços do site, separados por vírgula (no servidor: seunome.pythonanywhere.com)
DJANGO_ALLOWED_HOSTS=
```

No `.env` não há espaços em volta do `=` nem aspas nos valores.

**4.2) O `.gitignore`.**

**Arquivo:** `.gitignore` · **Ação:** substituir todo o conteúdo

```text
.venv/
__pycache__/
db.sqlite3
media/
staticfiles/
backup.json
.env
```

- **`.env`**: é aqui que ficará a chave secreta. Esta é a linha mais importante do arquivo.
- **`staticfiles/`**: é gerada pelo `collectstatic`.
- **O banco, as capas e o backup**: no servidor teremos um banco próprio.

**4.3) O `requirements.txt`.** Ele agora tem cinco dependências:

```text
Django>=5.2,<6.0
Pillow
openpyxl
reportlab
python-dotenv
```

### Passo 5 — Conferir as configurações de produção

O Django tem uma verificação própria para publicação. Para simular o servidor no seu computador, crie um `.env` a partir do modelo:

```powershell
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

O segundo comando imprime uma chave aleatória. Abra o `.env` no VS Code e preencha:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=cole-aqui-a-chave-gerada
DJANGO_ALLOWED_HOSTS=seunome.pythonanywhere.com
```

E rode:

```powershell
python manage.py check --deploy
```

Devem aparecer só dois avisos:

- **`security.W004` (HSTS):** um recurso que obriga o navegador a usar sempre HTTPS. É opcional e, configurado errado, pode deixar o site inacessível. Para o curso, não vamos ativá-lo.
- **`security.W008` (`SECURE_SSL_REDIRECT`):** pede que o Django redirecione HTTP para HTTPS. No PythonAnywhere, quem faz isso é a opção **Force HTTPS** do painel (Passo 11).

Teste também a proteção da chave: apague o valor da linha `DJANGO_SECRET_KEY=` (deixe só o nome e o sinal de igual) e rode `python manage.py check`. A resposta é `ImproperlyConfigured: Defina a variável de ambiente DJANGO_SECRET_KEY.`

**Ao terminar, volte o `.env` para desenvolvimento**, trocando a primeira linha para `DJANGO_DEBUG=True` (ou apague o arquivo `.env`). Com `DEBUG=False`, o `runserver` deixa de entregar o CSS e só aceita os endereços da lista, e o sistema local fica parecendo quebrado.

Se o projeto já usa Git desde a Aula 1, confirme que o `.env` está sendo ignorado:

```powershell
git status --ignored
```

O `.env` deve aparecer na seção **Ignored files**, e o `.env.example` entre os arquivos novos a enviar. Se o projeto ainda não usa Git, essa conferência é feita no Passo 7.

---

## Parte 3 — Enviando o código ao GitHub

### Passo 6 — Criar o repositório

1. Entre no GitHub e clique em **New repository** (o botão **+** no canto superior direito).
2. Dê o nome `biblioteca`, marque **Public** e **não** marque a opção de criar README nem `.gitignore` (o projeto já tem os seus).
3. Clique em **Create repository** e copie o endereço que aparece, no formato `https://github.com/seu-usuario/biblioteca.git`.

O repositório pode ser público porque não há nenhum segredo nele: a chave de produção fica só no `.env` do servidor.

### Passo 7 — Enviar o projeto

No terminal do VS Code, na pasta `biblioteca`:

```powershell
git init
git add .
git commit -m "Sistema de biblioteca pronto para publicação"
git branch -M main
git remote add origin https://github.com/seu-usuario/biblioteca.git
git push -u origin main
```

Se o projeto já usava Git desde a Aula 1, pule o `git init` e o `git branch -M main`. Na primeira vez, o Windows abre uma janela para você entrar na conta do GitHub.

Antes do `git commit`, confira com `git status` que **não** aparecem `.env`, `db.sqlite3`, `.venv/`, `media/` nem `staticfiles/`. Se aparecerem, o `.gitignore` não foi salvo corretamente. O `.env.example` deve aparecer.

Recarregue a página do repositório no GitHub: os arquivos do projeto devem estar lá.

---

## Parte 4 — Publicando no PythonAnywhere

As telas do PythonAnywhere mudam de vez em quando. Os nomes dos menus abaixo são os da versão em inglês do site; se algo estiver diferente, a documentação oficial do serviço para Django (<https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/>) é a referência.

Nos comandos abaixo, troque **`seunome`** pelo seu nome de usuário do PythonAnywhere e **`seu-usuario`** pelo do GitHub.

### Passo 8 — Baixar o projeto e instalar as dependências

No painel do PythonAnywhere, abra **Consoles → Bash**. Um terminal Linux abre no navegador. Rode:

```bash
git clone https://github.com/seu-usuario/biblioteca.git
cd biblioteca
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- O terminal do PythonAnywhere é **Linux**: a ativação do ambiente virtual é `source .venv/bin/activate`, e não `.\.venv\Scripts\Activate.ps1`.
- Se `python3.13` não existir, use a versão mais nova disponível (`python3.12`, `python3.11`...). Anote qual usou: ela será escolhida de novo no Passo 9.

O `.env` não veio do GitHub (ainda bem). Crie o do servidor a partir do modelo e gere uma chave:

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Selecione a chave impressa e copie-a (no console do navegador, selecionar com o mouse já copia; use o botão direito se precisar). Abra o `.env` no editor de texto do terminal:

```bash
nano .env
```

Deixe as três variáveis assim, colando a chave gerada:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=cole-aqui-a-chave-gerada
DJANGO_ALLOWED_HOSTS=seunome.pythonanywhere.com
```

No `nano`, as setas movem o cursor e o botão direito do mouse cola. Para salvar, `Ctrl+O` e depois `Enter`; para sair, `Ctrl+X`. Confira o conteúdo com `cat .env`.

Esta chave é **diferente** da que você usou para testar no seu computador, e não precisa ser igual: cada lugar tem a sua.

Ainda no console, prepare o banco e os arquivos estáticos:

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py popular_acervo
```

Esses comandos já leem o `.env` e rodam em modo de produção. O banco criado aqui é **novo e vazio**, separado do seu computador; por isso criamos de novo o superusuário e o acervo de exemplo.

### Passo 9 — Criar o site

1. Abra a aba **Web** e clique em **Add a new web app**.
2. Clique em **Next** na tela do endereço (`seunome.pythonanywhere.com`).
3. Escolha **Manual configuration** (e **não** a opção "Django", que criaria um projeto novo).
4. Escolha a **mesma versão do Python** usada no Passo 8 e clique em **Next** até terminar.

Na página do site que abriu, preencha:

| Seção | Campo | Valor |
|---|---|---|
| **Code** | Source code | `/home/seunome/biblioteca` |
| **Code** | Working directory | `/home/seunome/biblioteca` |
| **Virtualenv** | caminho | `/home/seunome/biblioteca/.venv` |

### Passo 10 — Configurar o arquivo WSGI

Ainda na aba **Web**, em **Code**, clique no link do **WSGI configuration file** (algo como `/var/www/seunome_pythonanywhere_com_wsgi.py`). O arquivo abre num editor. **Apague todo o conteúdo** e cole:

```python
import os
import sys

# Pasta do projeto no servidor
path = "/home/seunome/biblioteca"
if path not in sys.path:
    sys.path.insert(0, path)

# Arquivo de configurações do Django. As variáveis secretas vêm do .env,
# que o próprio settings.py carrega com load_dotenv().
os.environ["DJANGO_SETTINGS_MODULE"] = "library.settings"

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
```

Clique em **Save**.

Repare que este arquivo **não tem nenhum segredo**: ele só diz onde está o projeto e qual é o arquivo de configurações. Os valores de produção estão no `.env` criado no Passo 8.

### Passo 11 — Arquivos estáticos, imagens e HTTPS

Na aba **Web**, na seção **Static files**, cadastre duas linhas:

| URL | Directory |
|---|---|
| `/static/` | `/home/seunome/biblioteca/staticfiles` |
| `/media/` | `/home/seunome/biblioteca/media` |

Com `DEBUG` desligado, o Django não entrega esses arquivos; quem passa a entregá-los é o servidor do PythonAnywhere, a partir dessas pastas.

Na seção **Security**, ative **Force HTTPS**, para que o site seja sempre acessado com o cadeado.

### Passo 12 — Colocar no ar

No topo da aba **Web**, clique no botão verde **Reload**. Depois abra `https://seunome.pythonanywhere.com`.

Confira:

1. A tela de login aparece com o visual do sistema (CSS carregado) e o botão de tema funciona.
2. O login com o superusuário criado no Passo 8 funciona.
3. O acervo mostra os 27 livros do `popular_acervo`.
4. Empréstimo, devolução, busca e relatórios funcionam.
5. No Admin, envie uma capa para um livro: ela aparece no acervo.
6. Abra o site pelo celular.

Se aparecer **"Something went wrong"** ou a página não carregar, veja a seção **Log files** da aba **Web** e abra o **Error log**. A última mensagem do arquivo quase sempre aponta o problema.

---

## Parte 5 — Atualizando o site publicado

Sempre que mudar o sistema no seu computador:

**1. No seu computador**, depois de testar:

```powershell
git add .
git commit -m "Descreva a mudança"
git push
```

**2. No console Bash do PythonAnywhere:**

```bash
cd ~/biblioteca
source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

**3. Na aba Web**, clique em **Reload**.

Os passos do `pip install` e do `migrate` só mudam algo quando há dependências novas ou migrações novas, mas rodar sempre evita esquecimentos.

---

## Limites do plano gratuito

- **Renovação a cada três meses:** na aba **Web**, o botão **Run until 3 months from today** mantém o site no ar. Sem isso, ele é desativado (os arquivos não se perdem).
- **E-mails não são enviados:** a recuperação de senha continua usando o `EMAIL_BACKEND` de console, e o texto do e-mail aparece no **Server log** da aba **Web**. Um sistema real precisaria de um serviço de e-mail (via SMTP) e, no PythonAnywhere, de um plano pago.
- **Um site por conta e recursos limitados**, mais do que suficientes para o nosso sistema.

---

## Checkpoint

- [ ] O CSS e o JavaScript estão em `static/`, e o sistema continua igual localmente.
- [ ] `python manage.py test` mostra 39 testes OK.
- [ ] `check --deploy` mostra só os avisos W004 e W008.
- [ ] O código está no GitHub, com o `.env.example` e sem `.env`, `db.sqlite3`, `.venv/`, `media/` e `staticfiles/`.
- [ ] O site abre em `https://seunome.pythonanywhere.com`, com visual, login e empréstimos funcionando.
- [ ] Uma capa enviada pelo Admin aparece no site publicado.
- [ ] Você fez uma alteração pequena, enviou ao GitHub e atualizou o site seguindo a Parte 5.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| Site sem estilo (texto puro) | Mapeamento `/static/` ausente ou `collectstatic` não executado | Confira o Passo 11 e rode `python manage.py collectstatic` |
| Capas não aparecem no site | Mapeamento `/media/` ausente | Confira o Passo 11 |
| `Bad Request (400)` | O endereço não está em `DJANGO_ALLOWED_HOSTS` | Confira o `.env` do servidor (Passo 8) e clique em **Reload** |
| **403 CSRF** ao entrar | `CSRF_TRUSTED_ORIGINS` sem o endereço, ou acesso por endereço diferente do configurado | Confira o Passo 2.3 e o `DJANGO_ALLOWED_HOSTS` do `.env` |
| `ImproperlyConfigured: Defina a variável de ambiente DJANGO_SECRET_KEY` | O `.env` do servidor não existe, está em outra pasta ou a chave ficou vazia | O `.env` fica em `/home/seunome/biblioteca/`, ao lado do `manage.py`. Confira com `cat .env` |
| `ModuleNotFoundError: No module named 'dotenv'` | O `python-dotenv` não foi instalado | `pip install -r requirements.txt` com o `.venv` ativo |
| O site local ficou sem estilo depois do Passo 5 | O `.env` do computador ficou com `DJANGO_DEBUG=False` | Troque para `DJANGO_DEBUG=True` |
| O `.env` foi enviado ao GitHub | Faltou `.env` no `.gitignore` | Acrescente a linha, rode `git rm --cached .env`, faça commit e **gere uma chave nova** para o servidor: a antiga ficou pública |
| `ModuleNotFoundError: No module named 'django'` no Error log | Caminho do virtualenv errado na aba **Web** | Deve ser `/home/seunome/biblioteca/.venv` |
| `no such table` no site | O `migrate` não foi executado no servidor | Rode `python manage.py migrate` no console Bash |
| Mudanças não aparecem no site | Faltou o `git pull` ou o **Reload** | Siga a Parte 5 inteira |
| `git push` recusado | O repositório no GitHub foi criado com README | Rode `git pull origin main --allow-unrelated-histories` e depois `git push` |

---

## Resumo

Separamos o CSS e o JavaScript em arquivos estáticos, tiramos as configurações sensíveis do código, enviamos o projeto ao GitHub e o publicamos no PythonAnywhere.

O que ficou de ideia principal:

- **Desenvolvimento e produção** usam o mesmo código com configurações diferentes, lidas de **variáveis de ambiente**.
- **O arquivo `.env`** guarda essas variáveis e é carregado pelo `python-dotenv`. Ele fica fora do Git; o `.env.example`, sem segredos, vai para o repositório como modelo.
- **`DEBUG = False`** em produção: sem páginas de erro detalhadas e só com os endereços de `ALLOWED_HOSTS`.
- **A chave secreta** nunca vai para o repositório: ela fica no `.env` de cada lugar onde o sistema roda.
- **Arquivos estáticos** ficam em `static/`, são referenciados com `{% static %}` e reunidos pelo `collectstatic`; em produção, quem os entrega é o servidor web, assim como as imagens de `media/`.
- **O ciclo de atualização** é: testar, `commit`, `push`, `pull` no servidor, `migrate`, `collectstatic` e **Reload**.

---

## Exercícios

1. Crie uma página 404 com o visual do sistema. O Django usa o template `templates/404.html` quando `DEBUG = False` e o endereço não existe. Teste com `@override_settings(DEBUG=False, ...)`.
2. Faça o nome exibido no menu ("Biblioteca") vir de uma variável `LIBRARY_NAME` do `.env`, para que cada instalação possa ter o seu (por exemplo, "Biblioteca do Campus Brasília"). Dica: uma configuração no `settings.py`, um *context processor* e uma linha nova no `.env.example`.
3. Acrescente um rodapé com o nome da biblioteca e o ano atual. Dica: a tag `{% now "Y" %}`.

---

## Perguntas para revisar

<details>
<summary>1. Por que o <code>DEBUG</code> precisa ser <code>False</code> no servidor?</summary>

Com `DEBUG = True`, qualquer erro mostra uma página com trechos do código, configurações e variáveis, informações que não devem ficar expostas na internet.
</details>

<details>
<summary>2. Por que a chave secreta não pode estar no <code>settings.py</code> enviado ao GitHub?</summary>

Porque quem conhece a chave consegue forjar sessões de login, links de recuperação de senha e tokens CSRF. Como o repositório é público, a chave de produção fica no `.env` do servidor, que não vai para o GitHub.
</details>

<details>
<summary>3. Qual a diferença entre o <code>.env</code> e o <code>.env.example</code>?</summary>

O `.env` tem os valores reais (inclusive a chave secreta), é diferente em cada lugar onde o sistema roda e fica fora do Git. O `.env.example` tem só os nomes das variáveis, com comentários, vai para o repositório e serve de modelo para criar o `.env`.
</details>

<details>
<summary>4. O que o <code>collectstatic</code> faz e por que ele é necessário no servidor?</summary>

Ele copia todos os arquivos estáticos (os do projeto e os dos apps, como o Admin) para a pasta `STATIC_ROOT` (`staticfiles/`). Com `DEBUG = False`, o Django não entrega esses arquivos, e o servidor web passa a entregá-los a partir dessa pasta.
</details>

<details>
<summary>5. O banco do site publicado é o mesmo do seu computador?</summary>

Não. O `db.sqlite3` está no `.gitignore` e não vai para o GitHub. O servidor tem um banco próprio, criado com `migrate`. Para levar dados de um para o outro, use o backup com `dumpdata`/`loaddata` visto na Aula 6.
</details>

<details>
<summary>6. Quais são os passos para publicar uma alteração?</summary>

Testar localmente, `git commit` e `git push`; no servidor, `git pull`, `pip install -r requirements.txt`, `migrate` e `collectstatic`; e por fim **Reload** na aba **Web**.
</details>

---

## Fechamento

O sistema saiu do computador e está na internet. O caminho percorrido foi o de qualquer sistema web em Django: modelar os dados, construir as páginas, proteger o acesso, testar, e publicar com segurança.

Na próxima aula, o sistema ganha uma API REST, para que outros programas (aplicativos, scripts, outros sistemas) possam usá-lo.

---

Próxima aula: [Aula 8 — API REST da biblioteca com Django REST Framework](Aula_08_API_REST_com_DRF.md).
