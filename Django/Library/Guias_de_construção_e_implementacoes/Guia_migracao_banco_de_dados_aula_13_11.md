# Guia de Migração de Banco de Dados — Aula 13/11

Este guia explica, passo a passo e de forma didática, como migrar o banco de dados do sistema de biblioteca Django do SQLite para o PostgreSQL, garantindo backup e restauração dos dados sem perdas. Ideal para iniciantes!

---

## 1. O que é migração de banco de dados?

Migração é o processo de transferir todos os dados de um banco antigo (SQLite) para um novo (PostgreSQL), mantendo o funcionamento do sistema e os dados salvos.

---

## 2. Pré-requisitos

- Windows 10/11
- Python 3.8+ instalado
- VS Code instalado
- Projeto Django funcionando
- PostgreSQL instalado (https://www.postgresql.org/download/)
- pgAdmin instalado (opcional, para gerenciar o banco)

---

## 3. Passo a passo da migração

### 3.1. Instalar o driver do PostgreSQL
Abra o terminal do VS Code na pasta do projeto e execute:
```powershell
pip install psycopg2-binary
```

### 3.2. Criar o banco de dados PostgreSQL
1. Abra o pgAdmin ou outro gerenciador.
2. Crie um novo banco de dados (exemplo: `biblioteca`).
3. Crie um usuário e senha para acesso (anote para usar depois).

### 3.3. Configurar o Django para usar PostgreSQL
Abra o arquivo `library/settings.py` e localize a seção `DATABASES`. Substitua por:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'biblioteca',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Salve o arquivo.

### 3.4. Fazer backup dos dados do banco antigo (SQLite)
No terminal, execute:
```powershell
python manage.py dumpdata --output=db.json --indent 2
```
Isso cria o arquivo `db.json` com todos os dados do sistema.

### 3.5. Aplicar as migrações no novo banco (PostgreSQL)
No terminal, execute:
```powershell
python manage.py migrate
```
Isso cria todas as tabelas no novo banco.

### 3.6. Corrigir o arquivo de backup (se necessário)
- Abra o arquivo `db.json` no VS Code.
- Verifique se está salvo como UTF-8 (rodapé do VS Code).
- Corrija manualmente caracteres estranhos (exemplo: "O Senhor dos An�is" → "O Senhor dos Anéis").
- Salve o arquivo.

### 3.7. Restaurar os dados no novo banco
No terminal, execute:
```powershell
python manage.py loaddata db.json
```
Se aparecer erro de codificação, salve o arquivo novamente como UTF-8 e repita o comando.

---

## 4. Conferir se a migração foi bem-sucedida
- Acesse o Django Admin (`http://127.0.0.1:8000/admin/`).
- Verifique se todos os livros, usuários, empréstimos e histórico estão presentes.
- Teste as principais funcionalidades do sistema.

---

## 5. Dicas e cuidados
- Não apague o banco antigo até confirmar que tudo foi migrado.
- Se precisar importar novamente, limpe o banco novo antes (recrie o banco ou exclua as tabelas).
- Sempre salve arquivos JSON como UTF-8.
- Se usar imagens ou arquivos, eles ficam na pasta `media/` e não são migrados pelo banco.

---

## 6. Resumo dos comandos principais
```powershell
# Instalar driver do PostgreSQL
pip install psycopg2-binary

# Gerar backup do banco antigo
python manage.py dumpdata --output=db.json --indent 2

# Aplicar migrações no novo banco
python manage.py migrate

# Restaurar dados no novo banco
python manage.py loaddata db.json
```

---

## 7. Solução de problemas comuns
- **Erro de codificação (UnicodeDecodeError):**
  - Abra o arquivo no VS Code e salve como UTF-8.
  - Corrija manualmente caracteres estranhos.
- **Dados duplicados:**
  - Limpe o banco antes de importar novamente.
- **Dados ausentes:**
  - Verifique se todas as migrações foram aplicadas.

---

## 8. Finalização
Parabéns! Você migrou o banco de dados do sistema de biblioteca com sucesso. Se precisar de ajuda, peça orientação!

---

**Guia criado para estudantes iniciantes — Novembro/2025**
