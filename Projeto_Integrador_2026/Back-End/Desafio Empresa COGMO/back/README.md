# Desafio Backend: API de monitoramento

**Guia amigável em PDF:** [DESAFIO_BACKEND_COGMO.pdf](DESAFIO_BACKEND_COGMO.pdf) — leia antes de começar; ele explica a missão, os passos e os termos do desafio.

**Proponente:** Cogmo Technology  
**Público:** alunos em formação, nível júnior  
**Tempo sugerido:** 16 a 24 horas, distribuídas em até 10 dias úteis  
**Tecnologias de referência:** Node.js, Express e SQLite

## Contexto

A Cogmo Technology propõe a construção do backend de uma pequena página de monitoramento de níveis de rio e chuva. O desafio é inspirado em uma aplicação de acompanhamento hidrológico, com o escopo reduzido para praticar rotas REST, organização de código e banco de dados.

A amostra incluída é sintética. Estações, locais, horários e valores foram criados para o exercício; não são leituras reais e não servem para alertas ou decisões.

## O que você vai construir

Uma API HTTP que guarda estações e observações em SQLite e oferece os dados que uma tela de monitoramento precisa. O contrato está em [docs/CONTRATO_API.md](docs/CONTRATO_API.md); o banco e os relacionamentos sugeridos estão em [docs/MODELO_DE_DADOS.md](docs/MODELO_DE_DADOS.md).

O projeto já tem a estrutura inicial, o schema sugerido, um gerador de amostras sintéticas e um servidor Express com pontos marcados como TODO. Complete o que falta em etapas pequenas. Você pode alterar a organização se mantiver o contrato.

## Tarefas essenciais

1. Inicializar SQLite usando o schema e manter chave estrangeira habilitada.
2. Fazer o seed idempotente: executar mais de uma vez não duplica estações e observações.
3. Implementar listagem de estações.
4. Implementar o resumo com a leitura mais recente de nível e chuva.
5. Implementar série por estação, variável e janela de 1 a 72 horas.
6. Retornar datas ISO 8601 em UTC, ordenadas da mais antiga para a mais recente.
7. Tratar estação inexistente, variável desconhecida e janela inválida com HTTP e JSON de erro coerentes.
8. Preservar lacunas: não inventar nem interpolar leituras que não existem.
9. Manter consultas parametrizadas e separar rotas das consultas SQL.

### Fora do escopo obrigatório

Login, permissões, previsão por inteligência artificial, conexão a sensores reais, alertas de risco, hospedagem em nuvem, filas, microsserviços e banco distribuído. Não procure nem compartilhe chaves de serviços reais.

## Como começar

Requisitos: Node.js 20 ou superior e npm.

~~~powershell
cd back
Copy-Item .env.example .env
npm install
npm run seed
npm run dev
~~~

A API sobe em http://localhost:3000. Confira http://localhost:3000/api/health e a referência de chamadas em [harness/EXEMPLOS.md](harness/EXEMPLOS.md). O roteiro automático de fumaça está em [harness/check.ps1](harness/check.ps1).

O banco local fica em back/data/monitoramento.sqlite. A variável DB_PATH permite escolher outro caminho. Não envie o arquivo .env nem dados locais para o repositório.

## Plano sugerido

- **Etapa 1 (3-4 h):** ler o contrato, iniciar o servidor e entender as tabelas.
- **Etapa 2 (3-5 h):** concluir e repetir o seed; consultar os dados com SQL.
- **Etapa 3 (5-7 h):** criar as rotas e conferir as respostas com exemplos.
- **Etapa 4 (3-5 h):** validar erros, unidades, ordenação e datas.
- **Etapa 5 (2-3 h):** preparar README, breve demonstração e retrospectiva.

A etapa seguinte não precisa esperar que tudo seja perfeito. Primeiro faça uma resposta simples correta; depois organize e melhore.

## Pronto para a entrega quando

- Os comandos de instalação, seed e inicialização funcionam a partir do README.
- O seed pode ser repetido sem duplicatas.
- As três rotas entregam o JSON descrito no contrato.
- A tela consegue obter estações, resumo e série sem depender de uma chave privada.
- Um leitor consegue entender tabelas, relacionamentos, validações e limitações olhando a documentação.
- A interface sempre deixa claro que os dados são simulados.

## O que entregar

1. Repositório ou pasta de código com o README atualizado.
2. Schema SQL e evidência do seed.
3. Exemplos de chamadas e respostas para rotas válidas e inválidas.
4. Um diagrama simples ou descrição das relações do banco.
5. Apresentação curta: decisão de modelagem, dificuldade encontrada e próxima melhoria.

### Critérios de avaliação (100 pontos)

- **API e contrato - 30:** endpoints corretos, HTTP e mensagens compreensíveis.
- **Banco e SQL - 25:** relacionamentos, chaves, integridade, seed repetível e consultas parametrizadas.
- **Regras de dados - 20:** datas UTC, unidade, ordenação, filtros e lacunas preservadas.
- **Organização e clareza - 15:** nomes, divisão simples de responsabilidades e instruções úteis.
- **Demonstração e colaboração - 10:** explicar escolhas, usar Git e registrar o que aprendeu.

Conta mais uma solução correta e explicada do que uma arquitetura sofisticada. Veja também [docs/CONTRATO_API.md](docs/CONTRATO_API.md), [docs/MODELO_DE_DADOS.md](docs/MODELO_DE_DADOS.md) e [harness/EXEMPLOS.md](harness/EXEMPLOS.md).
