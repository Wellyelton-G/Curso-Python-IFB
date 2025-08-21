class Estudante:
    def __init__(self, nome, notas):
        self.nome = nome
        self.notas = notas

    def calcular_media(self):
        if len(self.notas) == 0:
            return 0
        return sum(self.notas) / len(self.notas)

    def situacao(self):
        media = self.calcular_media()
        return "Aprovado" if media >= 6.0 else "Reprovado"

    def exibir_dados(self):
        print(f"Nome: {self.nome}")
        print(f"Notas: {self.notas}")
        print(f"Média: {self.calcular_media():.2f}")
        print(f"Situação: {self.situacao()}")

# Solicita dados do usuário
estudantes = []
quantidade = int(input("Quantos estudantes deseja cadastrar? "))

for i in range(quantidade):
    nome = input(f"\nDigite o nome do estudante {i+1}: ")
    notas = []
    for j in range(3):
        nota = float(input(f"Digite a nota {j+1} de {nome}: "))
        notas.append(nota)
    estudantes.append(Estudante(nome, notas))

print("\n=== Resultados ===")
for estudante in estudantes:
    estudante.exibir_dados()
    print()