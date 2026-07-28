from abc import ABC, abstractmethod

# Esta é a classe abstrata 'ClubeParticipante'.
# Ela age como um 'molde' ou 'contrato' para todos os clubes que participarão de algo.
# Define o que todo clube deve ter e o que todo clube deve ser capaz de fazer,
# mas não implementa essas ações por completo, deixando-as para as subclasses.
class ClubeParticipante(ABC):
    # O construtor '__init__' define os atributos básicos que todo clube deve ter.
    def __init__(self, nome, pais, confederacao, ranking_fifa, gols_marcados, vitorias):
        self.nome = nome
        self.pais = pais
        self.confederacao = confederacao
        self.ranking_fifa = ranking_fifa
        self.gols_marcados = gols_marcados
        self.vitorias = vitorias

    # Este é um método concreto que todas as subclasses herdam e podem usar diretamente.
    def exibir_dados(self):
        print(f"Nome: {self.nome}")
        print(f"País: {self.pais}")
        print(f"Confederação: {self.confederacao}")
        print(f"Ranking FIFA: {self.ranking_fifa}")
        print(f"Gols Marcados: {self.gols_marcados}")
        print(f"Vitórias: {self.vitorias}")

    # '@abstractmethod' indica que este método DEVE ser implementado pelas subclasses.
    # A classe 'ClubeParticipante' não sabe como calcular o desempenho, pois isso varia por confederação.
    @abstractmethod
    def calcular_desempenho(self):
        pass

    # Similarmente, este método DEVE ser implementado pelas subclasses.
    @abstractmethod
    def gerar_relatorio_tecnico(self):
        pass

# 'ClubeUEFA' é uma subclasse concreta que herda de 'ClubeParticipante'.
# Ela implementa os detalhes específicos para clubes da UEFA.
class ClubeUEFA(ClubeParticipante):
    # O construtor chama o construtor da classe pai ('super().__init__')
    # e define automaticamente a confederação como "UEFA".
    def __init__(self, nome, pais, ranking_fifa, gols_marcados, vitorias):
        super().__init__(nome, pais, "UEFA", ranking_fifa, gols_marcados, vitorias)

    # Implementação específica do cálculo de desempenho para clubes da UEFA.
    # Aqui, a lógica é `vitorias * 3 + gols_marcados * 0.5`.
    def calcular_desempenho(self):
        return self.vitorias * 3 + self.gols_marcados * 0.5

    # Implementação específica do relatório técnico para clubes da UEFA.
    # Utiliza 'exibir_dados' herdado e seu próprio 'calcular_desempenho'.
    def gerar_relatorio_tecnico(self):
        self.exibir_dados()
        desempenho = self.calcular_desempenho()
        print(f"Desempenho (UEFA): {desempenho:.2f}")

# 'ClubeCONMEBOL' é outra subclasse concreta, focada em clubes da CONMEBOL.
# Ela também herda de 'ClubeParticipante' e implementa seus métodos abstratos.
class ClubeCONMEBOL(ClubeParticipante):
    # Construtor para clubes da CONMEBOL, definindo a confederação como "CONMEBOL".
    def __init__(self, nome, pais, ranking_fifa, gols_marcados, vitorias):
        super().__init__(nome, pais, "CONMEBOL", ranking_fifa, gols_marcados, vitorias)

    # Implementação específica do cálculo de desempenho para clubes da CONMEBOL.
    # Repare que a lógica é ligeiramente diferente: `vitorias * 3 + gols_marcados * 0.7`.
    # Isso demonstra POLIMORFISMO: o mesmo método se comporta de maneira diferente.
    def calcular_desempenho(self):
        return self.vitorias * 3 + self.gols_marcados * 0.7

    # Implementação do relatório técnico para clubes da CONMEBOL.
    def gerar_relatorio_tecnico(self):
        self.exibir_dados()
        desempenho = self.calcular_desempenho()
        print(f"Desempenho (CONMEBOL): {desempenho:.2f}")

# Este bloco 'if __name__ == "__main__":' é para testar as classes quando o script é executado diretamente.
if __name__ == "__main__":
    # Criamos instâncias (objetos) das nossas classes concretas.
    clube1 = ClubeUEFA("Real Madrid", "Espanha", 1, 10, 4)
    clube2 = ClubeCONMEBOL("Flamengo", "Brasil", 5, 8, 3)

    print("Relatório Técnico - UEFA:")
    # Chamamos o método 'gerar_relatorio_tecnico' para o objeto 'clube1' (UEFA).
    clube1.gerar_relatorio_tecnico()
    print("\nRelatório Técnico - CONMEBOL:")
    # Chamamos o mesmo método para o objeto 'clube2' (CONMEBOL).
    # O resultado será diferente devido à implementação polimórfica de 'calcular_desempenho'.
    clube2.gerar_relatorio_tecnico()

# Resumo dos Conceitos Principais neste código:
# 1. Classe Abstrata (`ClubeParticipante`): Define uma interface comum e obriga as subclasses a implementarem certos métodos.
# 2. Herança: `ClubeUEFA` e `ClubeCONMEBOL` herdam características e comportamentos de `ClubeParticipante`.
# 3. Polimorfismo: Diferentes classes (subclasses) respondem ao mesmo método (`calcular_desempenho` e `gerar_relatorio_tecnico`)
#    de maneiras diferentes, de acordo com sua própria implementação.
# Este é um ótimo exemplo de como usar a Programação Orientada a Objetos para criar um código flexível e organizado.
