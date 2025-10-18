-- =========================================================
-- Lista_Consultas_Adicional_50.sql
-- Banco: plataforma_cursos
-- Mais 50 exercícios (41–90) com comandos SQL prontos (PostgreSQL)
-- =========================================================
-- \c plataforma_cursos

-- 41) Cursos publicados com preço >= 300, ordenados desc por preço.
SELECT id_curso, titulo, preco
FROM curso
WHERE publicado = TRUE AND preco >= 300
ORDER BY preco DESC, titulo;

-- 42) Alunos cujo nome começa com 'A' ou 'M'.
SELECT id_aluno, nome
FROM aluno
WHERE nome ILIKE 'A%%' OR nome ILIKE 'M%%'
ORDER BY nome;

-- 43) E-mails de alunos em formato minúsculo e domínio extraído.
SELECT email, LOWER(email) AS email_lower,
       SPLIT_PART(email, '@', 2) AS dominio
FROM aluno;

-- 44) Cursos com carga_horas entre 20 e 30 (inclusive).
SELECT id_curso, titulo, carga_horas
FROM curso
WHERE carga_horas BETWEEN 20 AND 30
ORDER BY carga_horas, titulo;

-- 45) Total de matrículas por status.
SELECT status, COUNT(*) AS qtde
FROM matricula
GROUP BY status
ORDER BY qtde DESC;

-- 46) Valor total pago (aprovado) por UF do aluno.
SELECT a.uf, SUM(p.valor) AS total_uf
FROM pagamento p
JOIN matricula m ON m.id_matricula = p.id_matricula
JOIN aluno a ON a.id_aluno = m.id_aluno
WHERE p.status = 'aprovado'
GROUP BY a.uf
ORDER BY total_uf DESC NULLS LAST;

-- 47) Cursos sem nenhuma aula (LEFT JOIN e IS NULL).
SELECT c.id_curso, c.titulo
FROM curso c
LEFT JOIN aula a ON a.id_curso = c.id_curso
WHERE a.id_aula IS NULL
ORDER BY c.titulo;

-- 48) Cursos com pelo menos uma avaliação nota 5.
SELECT DISTINCT c.id_curso, c.titulo
FROM curso c
JOIN avaliacao av ON av.id_curso = c.id_curso
WHERE av.nota = 5
ORDER BY c.titulo;

-- 49) Média de notas por curso (inclua cursos sem avaliação).
SELECT c.titulo, AVG(av.nota)::NUMERIC(10,2) AS media_nota
FROM curso c
LEFT JOIN avaliacao av ON av.id_curso = c.id_curso
GROUP BY c.titulo
ORDER BY media_nota DESC NULLS LAST, c.titulo;

-- 50) Ranking de alunos por total de pagamentos aprovados (SUM OVER).
WITH totais AS (
  SELECT a.id_aluno, a.nome, COALESCE(SUM(p.valor) FILTER (WHERE p.status='aprovado'),0) AS total
  FROM aluno a
  LEFT JOIN matricula m ON m.id_aluno = a.id_aluno
  LEFT JOIN pagamento p ON p.id_matricula = m.id_matricula
  GROUP BY a.id_aluno, a.nome
)
SELECT id_aluno, nome, total,
       RANK() OVER (ORDER BY total DESC) AS posicao
FROM totais
ORDER BY posicao, nome;

-- 51) Top 5 alunos por quantidade de matrículas.
SELECT a.id_aluno, a.nome, COUNT(m.id_matricula) AS qtd
FROM aluno a
LEFT JOIN matricula m ON m.id_aluno = a.id_aluno
GROUP BY a.id_aluno, a.nome
ORDER BY qtd DESC, a.nome
LIMIT 5;

-- 52) Cursos cujo título contém a palavra 'PostgreSQL' (ILIKE).
SELECT id_curso, titulo
FROM curso
WHERE titulo ILIKE '%%PostgreSQL%%'
ORDER BY titulo;

-- 53) Diferença entre preco e preco_pago médio por curso.
SELECT c.titulo,
       c.preco,
       AVG(m.preco_pago)::NUMERIC(10,2) AS preco_pago_medio,
       (c.preco - AVG(m.preco_pago))::NUMERIC(10,2) AS diferenca_media
FROM curso c
JOIN matricula m ON m.id_curso = c.id_curso
GROUP BY c.id_curso, c.titulo, c.preco
ORDER BY diferenca_media DESC;

-- 54) Número de aulas por curso, ordenado decrescente.
SELECT c.titulo, COUNT(a.id_aula) AS aulas
FROM curso c
LEFT JOIN aula a ON a.id_curso = c.id_curso
GROUP BY c.titulo
ORDER BY aulas DESC, c.titulo;

-- 55) Cursos e seu instrutor, mostrando também a categoria.
SELECT c.titulo, i.nome AS instrutor, cat.nome AS categoria
FROM curso c
JOIN instrutor i ON i.id_instrutor = c.id_instrutor
JOIN categoria cat ON cat.id_categoria = c.id_categoria
ORDER BY cat.nome, c.titulo;

-- 56) Alunos com matrículas 'trancada' ou 'concluida'.
SELECT DISTINCT a.id_aluno, a.nome
FROM aluno a
JOIN matricula m ON m.id_aluno = a.id_aluno
WHERE m.status IN ('trancada', 'concluida')
ORDER BY a.nome;

-- 57) Cursos publicados em 2025-03 (mês/ano da data_publicacao).
SELECT id_curso, titulo, data_publicacao
FROM curso
WHERE DATE_TRUNC('month', data_publicacao) = DATE '2025-03-01'
ORDER BY titulo;

-- 58) Percentual de cursos por nivel (proporção).
WITH tot AS (SELECT COUNT(*) AS n FROM curso)
SELECT nivel,
       COUNT(*) AS qtd,
       ROUND(100.0 * COUNT(*) / (SELECT n FROM tot), 2) AS percentual
FROM curso
GROUP BY nivel
ORDER BY qtd DESC;

-- 59) Ultima matrícula por aluno (usando MAX(data_matricula)).
SELECT a.id_aluno, a.nome, MAX(m.data_matricula) AS ultima_matricula
FROM aluno a
LEFT JOIN matricula m ON m.id_aluno = a.id_aluno
GROUP BY a.id_aluno, a.nome
ORDER BY ultima_matricula DESC NULLS LAST;

-- 60) Cursos com preço abaixo da mediana (aproximação via percentil_cont).
WITH stats AS (
  SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco) AS mediana FROM curso
)
SELECT c.id_curso, c.titulo, c.preco
FROM curso c, stats
WHERE c.preco < stats.mediana
ORDER BY c.preco;

-- 61) Pagamentos por método com contagem de aprovados e pendentes (FILTER).
SELECT metodo,
       COUNT(*) FILTER (WHERE status='aprovado') AS aprovados,
       COUNT(*) FILTER (WHERE status='pendente') AS pendentes,
       COUNT(*) FILTER (WHERE status='estornado') AS estornados
FROM pagamento
GROUP BY metodo
ORDER BY metodo;

-- 62) Alunos que possuem pelo menos 2 matrículas ativas.
SELECT a.id_aluno, a.nome, COUNT(*) AS qtd_ativas
FROM aluno a
JOIN matricula m ON m.id_aluno = a.id_aluno AND m.status='ativa'
GROUP BY a.id_aluno, a.nome
HAVING COUNT(*) >= 2
ORDER BY qtd_ativas DESC, a.nome;

-- 63) Cursos cujo instrutor é de nome que contém 'a' (case-insensitive).
SELECT c.titulo, i.nome AS instrutor
FROM curso c
JOIN instrutor i ON i.id_instrutor = c.id_instrutor
WHERE i.nome ILIKE '%%a%%'
ORDER BY i.nome, c.titulo;

-- 64) Duração total (min) de aulas por curso.
SELECT c.titulo, COALESCE(SUM(a.duracao_min),0) AS duracao_total
FROM curso c
LEFT JOIN aula a ON a.id_curso = c.id_curso
GROUP BY c.titulo
ORDER BY duracao_total DESC, c.titulo;

-- 65) Cursos sem nenhuma matrícula.
SELECT c.id_curso, c.titulo
FROM curso c
LEFT JOIN matricula m ON m.id_curso = c.id_curso
WHERE m.id_matricula IS NULL
ORDER BY c.titulo;

-- 66) Média de preços por categoria e nível.
SELECT cat.nome AS categoria, c.nivel, AVG(c.preco)::NUMERIC(10,2) AS preco_medio
FROM curso c
JOIN categoria cat ON cat.id_categoria = c.id_categoria
GROUP BY cat.nome, c.nivel
ORDER BY cat.nome, c.nivel;

-- 67) Primeira aula (menor ordem) de cada curso.
WITH primeiras AS (
  SELECT id_curso, MIN(ordem) AS min_ordem
  FROM aula
  GROUP BY id_curso
)
SELECT c.titulo, a.titulo AS primeira_aula, a.ordem
FROM primeiras p
JOIN aula a ON a.id_curso = p.id_curso AND a.ordem = p.min_ordem
JOIN curso c ON c.id_curso = a.id_curso
ORDER BY c.titulo;

-- 68) Última aula (maior ordem) de cada curso (window function).
SELECT c.titulo, a.titulo AS ultima_aula, a.ordem
FROM (
  SELECT a.*, ROW_NUMBER() OVER (PARTITION BY id_curso ORDER BY ordem DESC) AS rn
  FROM aula a
) a
JOIN curso c ON c.id_curso = a.id_curso
WHERE a.rn = 1
ORDER BY c.titulo;

-- 69) Cursos com avaliações média >= 4.
SELECT c.titulo, AVG(av.nota)::NUMERIC(10,2) AS media
FROM curso c
JOIN avaliacao av ON av.id_curso = c.id_curso
GROUP BY c.titulo
HAVING AVG(av.nota) >= 4
ORDER BY media DESC, c.titulo;

-- 70) Alunos e quantidade de cursos avaliados.
SELECT a.nome, COUNT(av.id_avaliacao) AS qtde_avaliacoes
FROM aluno a
LEFT JOIN avaliacao av ON av.id_aluno = a.id_aluno
GROUP BY a.nome
ORDER BY qtde_avaliacoes DESC, a.nome;

-- 71) Cursos com preço acima de todos os cursos do nível 'Iniciante' (ALL).
SELECT id_curso, titulo, preco
FROM curso
WHERE preco > ALL (SELECT preco FROM curso WHERE nivel = 'Iniciante')
ORDER BY preco DESC;

-- 72) Cursos com preço menor do que algum curso de 'Avançado' (ANY).
SELECT id_curso, titulo, preco
FROM curso
WHERE preco < ANY (SELECT preco FROM curso WHERE nivel = 'Avançado')
ORDER BY preco;

-- 73) Alunos sem matrícula (NOT EXISTS).
SELECT a.id_aluno, a.nome
FROM aluno a
WHERE NOT EXISTS (
  SELECT 1 FROM matricula m WHERE m.id_aluno = a.id_aluno
)
ORDER BY a.nome;

-- 74) Pagamentos por mês (ano-mês) e total aprovado.
SELECT TO_CHAR(data_pagamento, 'YYYY-MM') AS ano_mes,
       SUM(valor) FILTER (WHERE status='aprovado') AS total_aprovado
FROM pagamento
GROUP BY 1
ORDER BY 1;

-- 75) Cursos com pelo menos 1 matrícula 'concluida'.
SELECT DISTINCT c.id_curso, c.titulo
FROM curso c
JOIN matricula m ON m.id_curso = c.id_curso
WHERE m.status = 'concluida'
ORDER BY c.titulo;

-- 76) Percentual de matrículas por status (em relação ao total).
WITH tot AS (SELECT COUNT(*) AS n FROM matricula)
SELECT status,
       COUNT(*) AS qtd,
       ROUND(100.0 * COUNT(*) / (SELECT n FROM tot), 2) AS percentual
FROM matricula
GROUP BY status
ORDER BY qtd DESC;

-- 77) Cursos e receita total (pagamentos aprovados) ordenada decrescente.
SELECT c.titulo, COALESCE(SUM(p.valor) FILTER (WHERE p.status='aprovado'),0) AS receita
FROM curso c
LEFT JOIN matricula m ON m.id_curso = c.id_curso
LEFT JOIN pagamento p ON p.id_matricula = m.id_matricula
GROUP BY c.titulo
ORDER BY receita DESC, c.titulo;

-- 78) Intervalo (dias) entre data_publicacao do curso e primeira matrícula dele.
WITH primeira_m AS (
  SELECT id_curso, MIN(data_matricula) AS primeira
  FROM matricula
  GROUP BY id_curso
)
SELECT c.titulo, c.data_publicacao, pm.primeira,
       (pm.primeira - c.data_publicacao) AS dias_ate_primeira_matricula
FROM curso c
LEFT JOIN primeira_m pm ON pm.id_curso = c.id_curso
ORDER BY dias_ate_primeira_matricula;

-- 79) Nota média por instrutor (média das notas dos cursos daquele instrutor).
SELECT i.nome AS instrutor, AVG(av.nota)::NUMERIC(10,2) AS media_instrutor
FROM instrutor i
JOIN curso c ON c.id_instrutor = i.id_instrutor
JOIN avaliacao av ON av.id_curso = c.id_curso
GROUP BY i.nome
ORDER BY media_instrutor DESC NULLS LAST, i.nome;

-- 80) Cursos cujo total de aulas > média de aulas por curso.
WITH por_curso AS (
  SELECT id_curso, COUNT(*) AS aulas FROM aula GROUP BY id_curso
), media AS (
  SELECT AVG(aulas) AS m FROM por_curso
)
SELECT c.titulo, pc.aulas
FROM por_curso pc
JOIN curso c ON c.id_curso = pc.id_curso
JOIN media ON TRUE
WHERE pc.aulas > media.m
ORDER BY pc.aulas DESC;

-- 81) Alunos da região Sudeste (SP, RJ, MG, ES).
SELECT id_aluno, nome, uf
FROM aluno
WHERE uf IN ('SP','RJ','MG','ES')
ORDER BY nome;

-- 82) Títulos de cursos com INITCAP (formatação de título).
SELECT INITCAP(titulo) AS titulo_formatado
FROM curso
ORDER BY titulo_formatado;

-- 83) Cursos com desconto médio (preco - preco_pago médio) > 50.
SELECT c.titulo, (c.preco - AVG(m.preco_pago))::NUMERIC(10,2) AS desconto_medio
FROM curso c
JOIN matricula m ON m.id_curso = c.id_curso
GROUP BY c.titulo, c.preco
HAVING (c.preco - AVG(m.preco_pago)) > 50
ORDER BY desconto_medio DESC;

-- 84) Alunos com pagamentos estornados (listar aluno e quantidade).
SELECT a.nome, COUNT(*) AS estornos
FROM pagamento p
JOIN matricula m ON m.id_matricula = p.id_matricula
JOIN aluno a ON a.id_aluno = m.id_aluno
WHERE p.status = 'estornado'
GROUP BY a.nome
ORDER BY estornos DESC, a.nome;

-- 85) Cursos com maior ticket médio (SUM(valor aprovado) / qtd matrículas).
WITH base AS (
  SELECT c.id_curso, c.titulo,
         SUM(p.valor) FILTER (WHERE p.status='aprovado') AS receita,
         COUNT(DISTINCT m.id_matricula) AS qtd_mat
  FROM curso c
  LEFT JOIN matricula m ON m.id_curso = c.id_curso
  LEFT JOIN pagamento p ON p.id_matricula = m.id_matricula
  GROUP BY c.id_curso, c.titulo
)
SELECT id_curso, titulo,
       (receita / NULLIF(qtd_mat,0))::NUMERIC(10,2) AS ticket_medio
FROM base
ORDER BY ticket_medio DESC NULLS LAST, titulo;

-- 86) Cursos publicados entre 2025-02-01 e 2025-03-31.
SELECT id_curso, titulo, data_publicacao
FROM curso
WHERE data_publicacao BETWEEN DATE '2025-02-01' AND DATE '2025-03-31'
ORDER BY data_publicacao, titulo;

-- 87) Aulas com duração acima da média geral de duração.
WITH media AS (SELECT AVG(duracao_min) AS m FROM aula)
SELECT a.id_aula, a.titulo, a.duracao_min
FROM aula a, media
WHERE a.duracao_min > media.m
ORDER BY a.duracao_min DESC;

-- 88) Cursos cujo instrutor não tem e-mail cadastrado (LEFT JOIN + IS NULL).
SELECT c.titulo, i.nome AS instrutor
FROM curso c
LEFT JOIN instrutor i ON i.id_instrutor = c.id_instrutor
WHERE i.email IS NULL
ORDER BY c.titulo;

-- 89) Alunos com nome e e-mail concatenados.
SELECT nome || ' <' || email || '>' AS contato
FROM aluno
ORDER BY nome;

-- 90) Distribuição de notas (1 a 5) por curso (pivot simples com FILTER).
SELECT c.titulo,
       COUNT(*) FILTER (WHERE av.nota=1) AS n1,
       COUNT(*) FILTER (WHERE av.nota=2) AS n2,
       COUNT(*) FILTER (WHERE av.nota=3) AS n3,
       COUNT(*) FILTER (WHERE av.nota=4) AS n4,
       COUNT(*) FILTER (WHERE av.nota=5) AS n5
FROM curso c
LEFT JOIN avaliacao av ON av.id_curso = c.id_curso
GROUP BY c.titulo
ORDER BY c.titulo;
