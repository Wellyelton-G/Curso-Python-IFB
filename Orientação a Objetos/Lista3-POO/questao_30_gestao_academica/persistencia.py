"""Persistencia JSON do sistema academico."""

import json
import os
import tempfile
from pathlib import Path

from excecoes import ArquivoDadosError
from modelos import (
    Aluno,
    Avaliacao,
    Coordenador,
    Curso,
    Disciplina,
    Frequencia,
    Professor,
    SistemaAcademico,
    Turma,
)


class RepositorioAcademico:
    def __init__(self, arquivo="dados_academicos.json"):
        self.arquivo = Path(arquivo)

    def salvar(self, sistema):
        dados = self._para_dict(sistema)
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        nome_temporario = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", delete=False, dir=self.arquivo.parent
            ) as temporario:
                json.dump(dados, temporario, ensure_ascii=False, indent=2)
                temporario.flush()
                os.fsync(temporario.fileno())
                nome_temporario = temporario.name
            os.replace(nome_temporario, self.arquivo)
        except OSError as erro:
            if nome_temporario:
                try:
                    Path(nome_temporario).unlink(missing_ok=True)
                except OSError:
                    pass
            raise ArquivoDadosError(f"Nao foi possivel salvar os dados: {erro}") from erro

    def carregar(self):
        if not self.arquivo.exists():
            return SistemaAcademico(), "Arquivo ainda nao existe; iniciado cadastro vazio."
        try:
            dados = json.loads(self.arquivo.read_text(encoding="utf-8"))
            return self._de_dict(dados), None
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as erro:
            return SistemaAcademico(), f"Arquivo corrompido ou invalido; iniciado cadastro vazio: {erro}"

    @staticmethod
    def _para_dict(sistema):
        return {
            "versao": 1,
            "alunos": [
                {"nome": a.nome, "matricula": a.matricula}
                for a in sistema.alunos.values()
            ],
            "professores": [
                {"nome": p.nome, "registro": p.registro}
                for p in sistema.professores.values()
            ],
            "coordenadores": [
                {"nome": c.nome, "registro": c.registro}
                for c in sistema.coordenadores.values()
            ],
            "disciplinas": [
                {"codigo": d.codigo, "nome": d.nome, "carga_horaria": d.carga_horaria}
                for d in sistema.disciplinas.values()
            ],
            "cursos": [
                {
                    "codigo": c.codigo,
                    "nome": c.nome,
                    "disciplinas": [d.codigo for d in c.disciplinas],
                }
                for c in sistema.cursos.values()
            ],
            "turmas": [
                {
                    "codigo": t.codigo,
                    "disciplina": t.disciplina.codigo,
                    "professor": t.professor.registro,
                    "matriculas": [
                        {
                            "aluno": m.aluno.matricula,
                            "frequencia": m.frequencia.percentual,
                            "avaliacoes": [
                                {"descricao": a.descricao, "valor": a.valor, "peso": a.peso}
                                for a in m.avaliacoes
                            ],
                        }
                        for m in t.matriculas
                    ],
                }
                for t in sistema.turmas.values()
            ],
        }

    @staticmethod
    def _de_dict(dados):
        if dados.get("versao") != 1:
            raise ValueError("Versao do arquivo nao suportada")
        sistema = SistemaAcademico()

        for item in dados["alunos"]:
            aluno = Aluno(item["nome"], item["matricula"])
            sistema.alunos[aluno.matricula] = aluno
        for item in dados["professores"]:
            professor = Professor(item["nome"], item["registro"])
            sistema.professores[professor.registro] = professor
        for item in dados["coordenadores"]:
            coordenador = Coordenador(item["nome"], item["registro"])
            sistema.coordenadores[coordenador.registro] = coordenador
        for item in dados["disciplinas"]:
            disciplina = Disciplina(item["codigo"], item["nome"], item["carga_horaria"])
            sistema.disciplinas[disciplina.codigo] = disciplina
        for item in dados["cursos"]:
            curso = Curso(item["codigo"], item["nome"])
            for codigo in item["disciplinas"]:
                curso.adicionar_disciplina(sistema.disciplinas[codigo])
            sistema.cursos[curso.codigo] = curso
        for item in dados["turmas"]:
            turma = Turma(
                item["codigo"],
                sistema.disciplinas[item["disciplina"]],
                sistema.professores[item["professor"]],
            )
            sistema.turmas[turma.codigo] = turma
            for dados_matricula in item["matriculas"]:
                matricula = turma.matricular_aluno(
                    sistema.alunos[dados_matricula["aluno"]]
                )
                matricula.frequencia = Frequencia(dados_matricula["frequencia"])
                matricula.avaliacoes = [
                    Avaliacao(a["valor"], a["descricao"], a["peso"])
                    for a in dados_matricula["avaliacoes"]
                ]
        return sistema
