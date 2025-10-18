-- =========================================================
-- Lista_Consultas.sql
-- Banco: plataforma_cursos
-- 40 exercícios com comandos SQL prontos (PostgreSQL)
-- =========================================================

-- Conectar no banco no psql, se necessário:
-- \c plataforma_cursos

-- 1) Listar nome, cidade, uf de todos os alunos.
SELECT nome, cidade, uf FROM aluno;

-- 2) Exibir titulo, nivel, preco de todos os cursos publicados.
SELECT titulo, nivel, preco FROM curso WHERE publicado = TRUE;

-- 3) Mostrar nome, especialidade de instrutores com e-mail não nulo.
SELECT nome, especialidade FROM instrutor WHERE email IS NOT NULL;

-- 4) Listar título das aulas do curso "PostgreSQL do Zero" ordenadas por ordem.
SELECT a.titulo
FROM aula a
JOIN curso c ON c.id_curso = a.id_curso
WHERE c.titulo = 'PostgreSQL do Zero'
ORDER BY a.ordem;

-- 5) Listar nome dos alunos e data_cadastro em ordem crescente de data.
SELECT nome, data_cadastro FROM aluno ORDER BY data_cadastro ASC;

-- 6) Cursos com preco < 200.
SELECT id_curso, titulo, preco FROM curso WHERE preco < 200;

-- 7) Alunos da UF = 'DF' ou 'GO'.
SELECT id_aluno, nome, uf FROM aluno WHERE uf IN ('DF','GO');

-- 8) Matrículas ativas a partir de 2025-03-01.
SELECT * FROM matricula WHERE status = 'ativa' AND data_matricula >= DATE '2025-03-01';

-- 9) Pagamentos método pix e status aprovado.
SELECT * FROM pagamento WHERE metodo = 'pix' AND status = 'aprovado';

-- 10) Aulas com duração entre 40 e 50 min (inclusive).
SELECT * FROM aula WHERE duracao_min BETWEEN 40 AND 50;

-- 11) Cursos ordenados por nivel e depois preco desc.
SELECT id_curso, titulo, nivel, preco
FROM curso
ORDER BY nivel, preco DESC;

-- 12) Alunos ordenados por cidade, exibindo uf como "Estado".
SELECT nome, cidade, uf AS "Estado" FROM aluno ORDER BY cidade;

-- 13) Instrutores ordenados por nome exibindo especialidade como "Área".
SELECT nome, especialidade AS "Área" FROM instrutor ORDER BY nome;

-- 14) Aulas de "DevOps na Prática" ordenadas por duracao_min desc.
SELECT a.titulo, a.duracao_min
FROM aula a
JOIN curso c ON c.id_curso = a.id_curso
WHERE c.titulo = 'DevOps na Prática'
ORDER BY a.duracao_min DESC;

-- 15) Exibir titulo e preco*0.9 como preco_com_desconto (10%).
SELECT titulo, ROUND(preco * 0.9, 2) AS preco_com_desconto FROM curso;

-- 16) Contar quantos cursos existem por nivel.
SELECT nivel, COUNT(*) AS qtde_cursos
FROM curso
GROUP BY nivel
ORDER BY nivel;

-- 17) Média de duracao_min das aulas por id_curso.
SELECT id_curso, AVG(duracao_min)::NUMERIC(10,2) AS media_duracao
FROM aula
GROUP BY id_curso
ORDER BY id_curso;

-- 18) Soma de valor de pagamentos aprovados por metodo.
SELECT metodo, SUM(valor) AS total
FROM pagamento
WHERE status = 'aprovado'
GROUP BY metodo
ORDER BY total DESC;

-- 19) Quantidade de alunos por uf.
SELECT uf, COUNT(*) AS qtde
FROM aluno
GROUP BY uf
ORDER BY qtde DESC;

-- 20) Preço médio por categoria.
SELECT cat.nome AS categoria, AVG(c.preco)::NUMERIC(10,2) AS preco_medio
FROM curso c
JOIN categoria cat ON cat.id_categoria = c.id_categoria
GROUP BY cat.nome
ORDER BY preco_medio DESC;

-- 21) Cursos por instrutor com total >= 2 (HAVING).
SELECT i.nome AS instrutor, COUNT(*) AS total_cursos
FROM curso c
JOIN instrutor i ON i.id_instrutor = c.id_instrutor
GROUP BY i.nome
HAVING COUNT(*) >= 2
ORDER BY total_cursos DESC, i.nome;

-- 22) Pagamentos aprovados por curso com soma > 500.
SELECT c.titulo, SUM(p.valor) AS total_aprovado
FROM pagamento p
JOIN matricula m ON m.id_matricula = p.id_matricula
JOIN curso c ON c.id_curso = m.id_curso
WHERE p.status = 'aprovado'
GROUP BY c.titulo
HAVING SUM(p.valor) > 500
ORDER BY total_aprovado DESC;

-- 23) Aulas por curso com média de duração > 40 min.
SELECT c.titulo, AVG(a.duracao_min)::NUMERIC(10,2) AS media
FROM aula a
JOIN curso c ON c.id_curso = a.id_curso
GROUP BY c.titulo
HAVING AVG(a.duracao_min) > 40
ORDER BY media DESC;

-- 24) Matrículas ativas por curso com count >= 2.
SELECT c.titulo, COUNT(*) AS ativas
FROM matricula m
JOIN curso c ON c.id_curso = m.id_curso
WHERE m.status = 'ativa'
GROUP BY c.titulo
HAVING COUNT(*) >= 2
ORDER BY ativas DESC, c.titulo;

-- 25) Alunos por mês de cadastro.
SELECT DATE_TRUNC('month', data_cadastro)::DATE AS mes, COUNT(*) AS qtd
FROM aluno
GROUP BY 1
ORDER BY 1;

-- 26) Curso e nome do instrutor (JOIN).
SELECT c.titulo, i.nome AS instrutor
FROM curso c
JOIN instrutor i ON i.id_instrutor = c.id_instrutor
ORDER BY c.titulo;

-- 27) Nome do aluno, titulo do curso, status da matrícula.
SELECT a.nome AS aluno, c.titulo AS curso, m.status
FROM matricula m
JOIN aluno a ON a.id_aluno = m.id_aluno
JOIN curso c ON c.id_curso = m.id_curso
ORDER BY a.nome, c.titulo;

-- 28) Pagamentos (valor, método, status) com nome do aluno e titulo do curso.
SELECT a.nome AS aluno, c.titulo AS curso, p.valor, p.metodo, p.status
FROM pagamento p
JOIN matricula m ON m.id_matricula = p.id_matricula
JOIN aluno a ON a.id_aluno = m.id_aluno
JOIN curso c ON c.id_curso = m.id_curso
ORDER BY p.data_pagamento DESC;

-- 29) Aulas (titulo) com titulo do curso correspondente.
SELECT c.titulo AS curso, a.ordem, a.titulo AS aula
FROM aula a
JOIN curso c ON c.id_curso = a.id_curso
ORDER BY c.titulo, a.ordem;

-- 30) Avaliações: nome do aluno, titulo do curso, nota.
SELECT a.nome AS aluno, c.titulo AS curso, av.nota
FROM avaliacao av
JOIN aluno a ON a.id_aluno = av.id_aluno
JOIN curso c ON c.id_curso = av.id_curso
ORDER BY av.data_avaliacao DESC;

-- 31) Cursos com preco > média de todos os cursos.
SELECT id_curso, titulo, preco
FROM curso
WHERE preco > (SELECT AVG(preco) FROM curso)
ORDER BY preco DESC;

-- 32) Alunos sem nenhuma avaliação.
SELECT a.id_aluno, a.nome
FROM aluno a
WHERE NOT EXISTS (
  SELECT 1 FROM avaliacao av WHERE av.id_aluno = a.id_aluno
)
ORDER BY a.nome;

-- 33) Instrutores que não possuem cursos de nivel 'Avançado'.
SELECT i.id_instrutor, i.nome
FROM instrutor i
WHERE NOT EXISTS (
  SELECT 1 FROM curso c
  WHERE c.id_instrutor = i.id_instrutor
    AND c.nivel = 'Avançado'
)
ORDER BY i.nome;

-- 34) Cursos com mais de 2 aulas.
SELECT c.id_curso, c.titulo
FROM curso c
WHERE (SELECT COUNT(*) FROM aula a WHERE a.id_curso = c.id_curso) > 2
ORDER BY c.titulo;

-- 35) Alunos com valor total pago (aprovado) acima de 400.
SELECT a.id_aluno, a.nome, SUM(p.valor) AS total_pago
FROM pagamento p
JOIN matricula m ON m.id_matricula = p.id_matricula
JOIN aluno a ON a.id_aluno = m.id_aluno
WHERE p.status = 'aprovado'
GROUP BY a.id_aluno, a.nome
HAVING SUM(p.valor) > 400
ORDER BY total_pago DESC;

-- 36) Matrículas realizadas no mesmo mês da data_publicacao do curso.
SELECT a.nome AS aluno, c.titulo AS curso, m.data_matricula, c.data_publicacao
FROM matricula m
JOIN curso c ON c.id_curso = m.id_curso
JOIN aluno a ON a.id_aluno = m.id_aluno
WHERE DATE_TRUNC('month', m.data_matricula) = DATE_TRUNC('month', c.data_publicacao)
ORDER BY m.data_matricula;

-- 37) Para cada nivel, curso mais caro (window ROW_NUMBER).
WITH ranked AS (
  SELECT nivel, id_curso, titulo, preco,
         ROW_NUMBER() OVER (PARTITION BY nivel ORDER BY preco DESC) AS rk
  FROM curso
)
SELECT nivel, id_curso, titulo, preco
FROM ranked
WHERE rk = 1
ORDER BY nivel;

-- 38) Top 3 cursos por soma de pagamentos aprovados (window).
WITH totais AS (
  SELECT c.id_curso, c.titulo, SUM(p.valor) AS total
  FROM pagamento p
  JOIN matricula m ON m.id_matricula = p.id_matricula
  JOIN curso c ON c.id_curso = m.id_curso
  WHERE p.status = 'aprovado'
  GROUP BY c.id_curso, c.titulo
)
SELECT id_curso, titulo, total
FROM totais
ORDER BY total DESC
LIMIT 3;

-- 39) Diferença (dias) entre data_matricula e primeiro pagamento por matrícula.
WITH primeiro_pag AS (
  SELECT id_matricula, MIN(data_pagamento) AS primeira_data
  FROM pagamento
  GROUP BY id_matricula
)
SELECT m.id_matricula, a.nome AS aluno, c.titulo AS curso,
       m.data_matricula, pp.primeira_data,
       (pp.primeira_data - m.data_matricula) AS dias_ate_pagamento
FROM matricula m
LEFT JOIN primeiro_pag pp ON pp.id_matricula = m.id_matricula
JOIN aluno a ON a.id_aluno = m.id_aluno
JOIN curso c ON c.id_curso = m.id_curso
ORDER BY m.id_matricula;

-- 40) Nota média por curso e ranking (DENSE_RANK).
WITH medias AS (
  SELECT c.id_curso, c.titulo, AVG(av.nota)::NUMERIC(10,2) AS media
  FROM curso c
  LEFT JOIN avaliacao av ON av.id_curso = c.id_curso
  GROUP BY c.id_curso, c.titulo
)
SELECT id_curso, titulo, media,
       DENSE_RANK() OVER (ORDER BY media DESC NULLS LAST) AS posicao
FROM medias
ORDER BY posicao, titulo;

-- Fim da lista
