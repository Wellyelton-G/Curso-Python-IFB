# Gabarito das aulas

Cada pasta contém o projeto completo **como ele fica ao final da aula correspondente**:

| Pasta | Estado do projeto |
|---|---|
| `aula_01` | modelos `Book` e `Loan`, Admin configurado |
| `aula_02` | login, acervo, emprestar e devolver, tema claro e escuro |
| `aula_03` | área da equipe, busca, paginação e 14 testes |
| `aula_04` | categorias, busca avançada, histórico, exportação CSV e Excel, comando `popular_acervo` e 22 testes |
| `aula_05` | cadastro, recuperação de senha, página do livro, avaliações e 30 testes |
| `aula_06` | relatórios, exportação em PDF e 36 testes (sistema completo) |

Use o gabarito para **comparar** com o seu código quando algo não funcionar. Tentar resolver sozinho antes de olhar a resposta ajuda muito a fixar o conteúdo.

## Como rodar um gabarito

As pastas não trazem o banco de dados nem o ambiente virtual. Para rodar, por exemplo, o gabarito da Aula 6, abra o PowerShell dentro da pasta `aula_06` e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py popular_acervo
python manage.py runserver
```

O comando `popular_acervo` existe a partir da Aula 4. Nas pastas `aula_01` a `aula_03`, pule essa linha e cadastre alguns livros pelo Admin.

Para rodar os testes automatizados (a partir da Aula 3):

```powershell
python manage.py test
```

## Comparando com o seu projeto

No VS Code dá para comparar dois arquivos lado a lado: clique com o botão direito no seu arquivo, escolha **Select for Compare**, depois clique com o botão direito no arquivo do gabarito e escolha **Compare with Selected**.
