# Questão 80 - Lista de Exercícios

## Enunciado

**80) Cursos cujo total de aulas > média de aulas por curso.**

## Solução SQL

```sql
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
```

## Explicação

Esta consulta SQL tem como objetivo retornar todos os cursos que possuem um total de aulas superior à média de aulas por curso.

### Passo a passo:

1. **CTE por_curso**: Calcula o total de aulas para cada curso agrupando pela coluna `id_curso`.

2. **CTE media**: Calcula a média de aulas considerando todos os cursos.

3. **SELECT principal**: 
   - Realiza JOIN entre a CTE `por_curso` e a tabela `curso` para obter o título do curso
   - Faz um JOIN CROSS (usando `JOIN media ON TRUE`) para disponibilizar a média calculada
   - Filtra apenas os cursos onde o total de aulas é maior que a média
   - Ordena o resultado em ordem decrescente pelo número de aulas

### Resultado esperado:

A consulta retorna o título do curso e a quantidade de aulas para todos os cursos que estão acima da média.
