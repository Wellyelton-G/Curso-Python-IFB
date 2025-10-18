-- =========================================================
-- Script: plataforma_cursos.sql
-- Banco: plataforma_cursos
-- Domínio: EAD (cursos on-line)
-- DDL + INSERTs
-- =========================================================

-- Criação do banco (execute no psql com usuário com permissão)
-- DROP DATABASE IF EXISTS plataforma_cursos;
-- CREATE DATABASE plataforma_cursos;
-- \c plataforma_cursos

-- Limpeza (ordem respeitando FKs)
DROP TABLE IF EXISTS avaliacao;
DROP TABLE IF EXISTS pagamento;
DROP TABLE IF EXISTS matricula;
DROP TABLE IF EXISTS aula;
DROP TABLE IF EXISTS curso;
DROP TABLE IF EXISTS aluno;
DROP TABLE IF EXISTS instrutor;
DROP TABLE IF EXISTS categoria;

-- ========================
-- Tabelas (DDL)
-- ========================

CREATE TABLE categoria (
  id_categoria   SERIAL PRIMARY KEY,
  nome           VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE instrutor (
  id_instrutor   SERIAL PRIMARY KEY,
  nome           VARCHAR(80) NOT NULL,
  especialidade  VARCHAR(100),
  email          VARCHAR(120) UNIQUE
);

CREATE TABLE aluno (
  id_aluno       SERIAL PRIMARY KEY,
  nome           VARCHAR(80) NOT NULL,
  email          VARCHAR(120) UNIQUE,
  cidade         VARCHAR(60),
  uf             CHAR(2),
  data_cadastro  DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE curso (
  id_curso       SERIAL PRIMARY KEY,
  titulo         VARCHAR(120) NOT NULL,
  nivel          VARCHAR(20)  NOT NULL CHECK (nivel IN ('Iniciante','Intermediário','Avançado')),
  preco          NUMERIC(10,2) NOT NULL,
  carga_horas    INTEGER       NOT NULL,
  id_instrutor   INTEGER       NOT NULL REFERENCES instrutor(id_instrutor),
  id_categoria   INTEGER       NOT NULL REFERENCES categoria(id_categoria),
  publicado      BOOLEAN       NOT NULL DEFAULT TRUE,
  data_publicacao DATE         NOT NULL
);

CREATE TABLE aula (
  id_aula        SERIAL PRIMARY KEY,
  id_curso       INTEGER NOT NULL REFERENCES curso(id_curso) ON DELETE CASCADE,
  ordem          INTEGER NOT NULL,
  titulo         VARCHAR(120) NOT NULL,
  duracao_min    INTEGER NOT NULL,
  UNIQUE (id_curso, ordem)
);

CREATE TABLE matricula (
  id_matricula   SERIAL PRIMARY KEY,
  id_aluno       INTEGER NOT NULL REFERENCES aluno(id_aluno),
  id_curso       INTEGER NOT NULL REFERENCES curso(id_curso),
  data_matricula DATE    NOT NULL,
  status         VARCHAR(20) NOT NULL CHECK (status IN ('ativa','trancada','concluida')),
  preco_pago     NUMERIC(10,2) NOT NULL,
  UNIQUE (id_aluno, id_curso)
);

CREATE TABLE pagamento (
  id_pagamento   SERIAL PRIMARY KEY,
  id_matricula   INTEGER NOT NULL REFERENCES matricula(id_matricula) ON DELETE CASCADE,
  data_pagamento DATE    NOT NULL,
  valor          NUMERIC(10,2) NOT NULL,
  metodo         VARCHAR(20) NOT NULL CHECK (metodo IN ('boleto','pix','credito','debito')),
  status         VARCHAR(20) NOT NULL CHECK (status IN ('aprovado','pendente','estornado'))
);

CREATE TABLE avaliacao (
  id_avaliacao   SERIAL PRIMARY KEY,
  id_aluno       INTEGER NOT NULL REFERENCES aluno(id_aluno) ON DELETE CASCADE,
  id_curso       INTEGER NOT NULL REFERENCES curso(id_curso) ON DELETE CASCADE,
  nota           INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5),
  comentario     TEXT,
  data_avaliacao DATE NOT NULL,
  UNIQUE (id_aluno, id_curso)
);

-- ========================
-- Dados (INSERTs)
-- ========================

-- Categorias
INSERT INTO categoria (nome) VALUES
('Programação'), ('Banco de Dados'), ('DevOps'), ('Redes'), ('Design');

-- Instrutores
INSERT INTO instrutor (nome, especialidade, email) VALUES
('Carla Souza', 'Python e Data Science', 'carla@exemplo.com'),
('Luís Andrade', 'PostgreSQL e Modelagem', 'luis@exemplo.com'),
('Renata Prado', 'DevOps e Cloud', 'renata@exemplo.com'),
('João Galvão', 'Redes e Segurança', 'joao@exemplo.com'),
('Mirela Santos', 'UX/UI', 'mirela@exemplo.com');

-- Alunos
INSERT INTO aluno (nome, email, cidade, uf, data_cadastro) VALUES
('Ana Beatriz', 'ana@aluno.com', 'Brasília', 'DF', '2025-01-10'),
('Pedro Ivo', 'pedro@aluno.com', 'Goiânia', 'GO', '2025-02-03'),
('Marina Lopes', 'marina@aluno.com', 'São Paulo', 'SP', '2025-02-18'),
('Rafael Dias', 'rafael@aluno.com', 'Belo Horizonte', 'MG', '2025-03-02'),
('Sofia Nunes', 'sofia@aluno.com', 'Rio de Janeiro', 'RJ', '2025-03-15'),
('Caio Farias', 'caio@aluno.com', 'Curitiba', 'PR', '2025-03-20'),
('Lívia Rocha', 'livia@aluno.com', 'Fortaleza', 'CE', '2025-04-05'),
('Bruno Pires', 'bruno@aluno.com', 'Salvador', 'BA', '2025-04-18');

-- Cursos
INSERT INTO curso (titulo, nivel, preco, carga_horas, id_instrutor, id_categoria, publicado, data_publicacao) VALUES
('PostgreSQL do Zero', 'Iniciante',  199.90, 20, 2, 2, TRUE, '2025-02-10'),
('Modelagem Relacional', 'Intermediário', 249.90, 24, 2, 2, TRUE, '2025-03-01'),
('Python para Dados', 'Intermediário', 299.90, 30, 1, 1, TRUE, '2025-02-20'),
('DevOps na Prática', 'Intermediário', 349.90, 28, 3, 3, TRUE, '2025-03-10'),
('Redes Essenciais', 'Iniciante',    179.90, 18, 4, 4, TRUE, '2025-01-25'),
('Segurança em Redes', 'Avançado',   399.90, 26, 4, 4, TRUE, '2025-04-02'),
('UX para Iniciantes', 'Iniciante',  149.90, 16, 5, 5, TRUE, '2025-02-05'),
('Administração PostgreSQL', 'Avançado', 449.90, 32, 2, 2, TRUE, '2025-04-12');

-- Aulas (2–4 por curso, durações variadas)
INSERT INTO aula (id_curso, ordem, titulo, duracao_min) VALUES
(1,1,'Instalação e psql',25),(1,2,'SELECT/WHERE/ORDER',35),(1,3,'JOINs básicos',40),
(2,1,'Normalização',30),(2,2,'Chaves e FKs',35),(2,3,'Projeto lógico',40),
(3,1,'Pandas Básico',45),(3,2,'Limpeza de Dados',50),
(4,1,'CI/CD Conceitos',30),(4,2,'Docker Essentials',45),(4,3,'Infra como Código',40),
(5,1,'Camada de Rede',35),(5,2,'TCP/UDP',30),
(6,1,'Firewall e IDS',50),(6,2,'Criptografia',55),
(7,1,'Princípios de UX',25),(7,2,'Wireframes',30),
(8,1,'Configuração',40),(8,2,'Backup & Tuning',45),(8,3,'Replicação',50);

-- Matrículas (status variados; preços com desconto possíveis)
INSERT INTO matricula (id_aluno, id_curso, data_matricula, status, preco_pago) VALUES
(1,1,'2025-02-12','concluida',179.90),
(1,3,'2025-02-25','ativa',299.90),
(1,8,'2025-04-20','ativa',449.90),
(2,1,'2025-02-15','concluida',199.90),
(2,2,'2025-03-05','ativa',229.90),
(3,3,'2025-03-02','trancada',299.90),
(3,4,'2025-03-12','ativa',329.90),
(4,5,'2025-03-04','ativa',179.90),
(4,6,'2025-04-10','ativa',379.90),
(5,1,'2025-03-18','concluida',189.90),
(5,6,'2025-04-15','trancada',399.90),
(6,4,'2025-03-25','ativa',349.90),
(6,2,'2025-03-28','ativa',239.90),
(7,7,'2025-04-08','ativa',149.90),
(7,1,'2025-04-18','ativa',199.90),
(8,2,'2025-04-20','ativa',249.90),
(8,8,'2025-04-25','ativa',439.90);

-- Pagamentos
INSERT INTO pagamento (id_matricula, data_pagamento, valor, metodo, status) VALUES
(1,'2025-02-12',179.90,'pix','aprovado'),
(2,'2025-02-25',299.90,'credito','aprovado'),
(3,'2025-04-20',449.90,'boleto','pendente'),
(4,'2025-02-15',199.90,'debito','aprovado'),
(5,'2025-03-05',229.90,'pix','aprovado'),
(6,'2025-03-02',299.90,'credito','estornado'),
(7,'2025-03-12',329.90,'credito','aprovado'),
(8,'2025-03-04',179.90,'pix','aprovado'),
(9,'2025-04-10',379.90,'credito','aprovado'),
(10,'2025-03-18',189.90,'debito','aprovado'),
(11,'2025-04-15',399.90,'pix','pendente'),
(12,'2025-03-25',349.90,'credito','aprovado'),
(13,'2025-03-28',239.90,'pix','aprovado'),
(14,'2025-04-08',149.90,'debito','aprovado'),
(15,'2025-04-18',199.90,'pix','aprovado'),
(16,'2025-04-20',249.90,'credito','aprovado'),
(17,'2025-04-25',439.90,'pix','aprovado');

-- Avaliações
INSERT INTO avaliacao (id_aluno, id_curso, nota, comentario, data_avaliacao) VALUES
(1,1,5,'Curso introdutório excelente','2025-02-20'),
(2,1,4,'Bom ritmo e prática útil','2025-02-22'),
(5,1,5,'Clareza nas explicações','2025-03-25'),
(1,3,4,'Conteúdo sólido, poderia ter mais projetos','2025-03-10'),
(3,4,3,'Bom, mas poderia aprofundar CI/CD','2025-03-25'),
(4,5,5,'Didática ótima','2025-03-15'),
(6,4,4,'Gostei do módulo de Docker','2025-04-01'),
(8,8,5,'Essencial pra admin do PG','2025-04-30');

-- Fim do script
