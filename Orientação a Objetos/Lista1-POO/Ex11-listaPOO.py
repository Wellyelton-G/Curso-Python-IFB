# Importa ferramentas para criar classes abstratas
from abc import ABC, abstractmethod

# ===== Classe base (abstrata) para todos os tipos de veículos de transporte =====
class VeiculoTransporte(ABC):
    # Construtor que define atributos comuns a todos os veículos
    def __init__(self, placa, capacidade_passageiros):
        # Validação: a placa não pode estar vazia
        if not placa.strip():
            raise ValueError("A placa não pode ser vazia.")
        # Validação: a capacidade de passageiros deve ser positiva
        if capacidade_passageiros <= 0:
            raise ValueError("A capacidade de passageiros deve ser positiva.")

        self.placa = placa
        self.capacidade_passageiros = capacidade_passageiros

    # Método abstrato (obrigatório nas subclasses)
    @abstractmethod
    def calcular_custo_operacional(self):
        pass

# ===== Subclasse que representa um Ônibus, herda de VeiculoTransporte =====
class Onibus(VeiculoTransporte):
    def __init__(self, placa, capacidade_passageiros, consumo_por_km):
        # Chama o construtor da classe-pai (VeiculoTransporte)
        super().__init__(placa, capacidade_passageiros)

        # Valida que o consumo seja positivo
        if consumo_por_km <= 0:
            raise ValueError(" O consumo por km deve ser positivo.")

        self.consumo_por_km = consumo_por_km  # Ex: 0.3 litros por km

    def calcular_custo_operacional(self):
        preco_diesel = 6.00  # Valor fictício do litro do diesel
        return self.consumo_por_km * preco_diesel  # Fórmula do custo por km

# ===== Subclasse que representa um Metrô, também herda da classe-pai =====
class Metro(VeiculoTransporte):
    def __init__(self, placa, capacidade_passageiros, consumo_energia_por_km):
        super().__init__(placa, capacidade_passageiros)

        if consumo_energia_por_km <= 0:
            raise ValueError(" O consumo de energia por km deve ser positivo.")

        self.consumo_energia_por_km = consumo_energia_por_km  # Ex: 2.5 kWh por km

    def calcular_custo_operacional(self):
        preco_kwh = 0.80  # Valor fictício do kWh
        return self.consumo_energia_por_km * preco_kwh  # Cálculo do custo

# Lista para armazenar os veículos cadastrados
veiculos = []

# ===== Função principal com menu interativo no terminal =====
def menu():
    while True:
        # Mostra as opções do sistema
        print("\n=== GERENCIADOR DE VEÍCULOS PÚBLICOS ===")
        print("1. Cadastrar Ônibus")
        print("2. Cadastrar Metrô")
        print("3. Mostrar custos operacionais")
        print("0. Sair")

        opcao = input("Escolha uma opção: ").strip()

        # ===== Cadastro de ônibus =====
        if opcao == "1":
            try:
                placa = input("Placa do ônibus: ").strip()
                capacidade = int(input("Capacidade de passageiros: "))
                consumo = float(input("Consumo por km (litros/km): "))

                # Cria o objeto Onibus e adiciona à lista
                onibus = Onibus(placa, capacidade, consumo)
                veiculos.append(onibus)
                print(" Ônibus cadastrado com sucesso!")

            except ValueError as e:
                # Mostra mensagens de erro em caso de entradas inválidas
                print(e)

        # ===== Cadastro de metrô =====
        elif opcao == "2":
            try:
                placa = input("Placa do metrô: ").strip()
                capacidade = int(input("Capacidade de passageiros: "))
                consumo = float(input("Consumo por km (kWh/km): "))

                metro = Metro(placa, capacidade, consumo)
                veiculos.append(metro)
                print("Metrô cadastrado com sucesso!")

            except ValueError as e:
                print(e)

        # ===== Exibir custos operacionais de todos os veículos =====
        elif opcao == "3":
            if not veiculos:
                print(" Nenhum veículo cadastrado.")
            else:
                print("\n--- CUSTO OPERACIONAL POR QUILÔMETRO ---")
                for v in veiculos:
                    # Usa isinstance para descobrir o tipo de veículo
                    tipo = "Ônibus" if isinstance(v, Onibus) else "Metrô"
                    custo = v.calcular_custo_operacional()  # POLIMORFISMO
                    print(f"{tipo} | Placa: {v.placa} | Capacidade: {v.capacidade_passageiros} passageiros | Custo: R$ {custo:.2f}/km")

        # ===== Finalizar o programa =====
        elif opcao == "0":
            print(" Encerrando o sistema...")
            break

        # ===== Opção inválida =====
        else:
            print(" Opção inválida. Tente novamente.")

# ===== Ponto de entrada do programa =====
if __name__ == "__main__":
    menu()
