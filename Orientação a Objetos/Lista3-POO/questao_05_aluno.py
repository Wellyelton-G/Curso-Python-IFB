"""Questao 5: encapsulamento de validacao e da regra academica."""


class Aluno:
    """Calcula a média e determina a situação acadêmica."""

    def __init__(self, nome, nota1, nota2):
        self.nome = nome
        self.nota1 = self._validar_nota(nota1)
        self.nota2 = self._validar_nota(nota2)

    @staticmethod
    def _validar_nota(nota):
        # staticmethod e adequado porque a validacao nao usa self.
        if not 0 <= nota <= 10:
            raise ValueError("A nota deve estar entre 0 e 10.")
        return nota

    def calcular_media(self):
        return (self.nota1 + self.nota2) / 2

    def verificar_situacao(self):
        # Testamos da maior faixa para a menor, evitando condicoes sobrepostas.
        media = self.calcular_media()
        if media >= 6:
            return "Aprovado"
        if media >= 4:
            return "Recuperação"
        return "Reprovado"

    def exibir_resultado(self):
        print(f"Aluno: {self.nome}")
        print(f"Média: {self.calcular_media():.2f}")
        print(f"Situação: {self.verificar_situacao()}")


if __name__ == "__main__":
    aluno = Aluno("Marina", 7.5, 5.5)
    aluno.exibir_resultado()
