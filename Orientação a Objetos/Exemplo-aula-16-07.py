from abc import ABC, abstractmethod

class ClubeParticipante(ABC):
    def __init__(self, nome, pais, confederacao, ranking_fifa, gols_marcados, vitorias):
        self.nome = nome
        self.pais = pais
        self.confederacao = confederacao
        self.ranking_fifa = ranking_fifa
        self.gols_marcados = gols_marcados
        self.vitorias = vitorias

    def exibir_dados(self):
        print(f"Nome: {self.nome}")
        print(f"País: {self.pais}")
        print(f"Confederação: {self.confederacao}")
        print(f"Ranking FIFA: {self.ranking_fifa}")
        print(f"Gols Marcados: {self.gols_marcados}")
        print(f"Vitórias: {self.vitorias}")

    @abstractmethod
    def calcular_desempenho(self):
        pass

    @abstractmethod
    def gerar_relatorio_tecnico(self):
        pass

class ClubeUEFA(ClubeParticipante):
    def __init__(self, nome, pais, ranking_fifa, gols_marcados, vitorias):
        super().__init__(nome, pais, "UEFA", ranking_fifa, gols_marcados, vitorias)

    def calcular_desempenho(self):
        return self.vitorias * 3 + self.gols_marcados * 0.5

    def gerar_relatorio_tecnico(self):
        self.exibir_dados()
        desempenho = self.calcular_desempenho()
        print(f"Desempenho (UEFA): {desempenho:.2f}")

class ClubeCONMEBOL(ClubeParticipante):
    def __init__(self, nome, pais, ranking_fifa, gols_marcados, vitorias):
        super().__init__(nome, pais, "CONMEBOL", ranking_fifa, gols_marcados, vitorias)

    def calcular_desempenho(self):
        return self.vitorias * 3 + self.gols_marcados * 0.7

    def gerar_relatorio_tecnico(self):
        self.exibir_dados()
        desempenho = self.calcular_desempenho()
        print(f"Desempenho (CONMEBOL): {desempenho:.2f}")

# Testando as classes
if __name__ == "__main__":
    clube1 = ClubeUEFA("Real Madrid", "Espanha", 1, 10, 4)
    clube2 = ClubeCONMEBOL("Flamengo", "Brasil", 5, 8, 3)

    print("Relatório Técnico - UEFA:")
    clube1.gerar_relatorio_tecnico()
    print("\nRelatório Técnico - CONMEBOL:")
    clube2.gerar_relatorio_tecnico()