# ================= Classes =================

class Funcionario:
    def __init__(self, nome, salario_base):
        self.nome = nome
        self.salario_base = salario_base

    def calcular_salario(self):
        return self.salario_base

    def exibir_dados(self):
        print(f"Nome: {self.nome}")
        print(f"Salário Base: R$ {self.salario_base:.2f}")


class FuncionarioComissionado(Funcionario):
    def __init__(self, nome, salario_base, comissao):
        super().__init__(nome, salario_base)
        self.comissao = comissao

    def calcular_salario(self):
        return self.salario_base + self.comissao

    def exibir_dados(self):
        print(f"Nome: {self.nome}")
        print(f"Salário Base: R$ {self.salario_base:.2f}")
        print(f"Comissão: R$ {self.comissao:.2f}")
        print(f"Salário Total: R$ {self.calcular_salario():.2f}")


# ================= Programa Principal =================

# Criando um funcionário comum
func1 = Funcionario("Ana", 3000.00)
print("=== Funcionário Comum ===")
func1.exibir_dados()
print(f"Salário Calculado: R$ {func1.calcular_salario():.2f}\n")

# Criando um funcionário comissionado
func2 = FuncionarioComissionado("Bruno", 2500.00, 800.00)
print("=== Funcionário Comissionado ===")
func2.exibir_dados()
print(f"Salário Calculado: R$ {func2.calcular_salario():.2f}")
