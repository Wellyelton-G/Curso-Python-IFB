"""Excecoes especificas do sistema academico."""


class SistemaAcademicoError(Exception):
    """Classe-base para erros previstos pela aplicacao."""


# Ter uma excecao para cada tipo de problema permite que outras camadas do
# programa tratem os erros sem depender do texto de suas mensagens.
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
