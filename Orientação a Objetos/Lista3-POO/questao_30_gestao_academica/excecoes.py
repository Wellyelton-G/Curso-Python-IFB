"""Excecoes especificas do sistema academico."""


class SistemaAcademicoError(Exception):
    """Classe-base para erros previstos pela aplicacao."""


class MatriculaDuplicadaError(SistemaAcademicoError):
    pass


class CadastroDuplicadoError(SistemaAcademicoError):
    pass


class PermissaoNegadaError(SistemaAcademicoError):
    pass


class EntidadeNaoEncontradaError(SistemaAcademicoError):
    pass


class AlunoNaoMatriculadoError(SistemaAcademicoError):
    pass


class DadosInvalidosError(SistemaAcademicoError):
    pass


class ArquivoDadosError(SistemaAcademicoError):
    pass
