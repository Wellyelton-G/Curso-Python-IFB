def inicializar_assentos(num_assentos):
    return [False] * num_assentos

def reservar_assento(assentos, num_assento):
    if assentos[num_assento - 1]:
        print(f"O assento {num_assento} já está ocupado.")
    else:
        assentos[num_assento - 1] = True
        print(f"Assento {num_assento} reservado com sucesso.")

def liberar_assento(assentos, num_assento):
    if not assentos[num_assento - 1]:
        print(f"O assento {num_assento} já está livre.")
    else:
        assentos[num_assento - 1] = False
        print(f"Assento {num_assento} liberado com sucesso.")

def mostrar_mapa_ocupacao(assentos):
    print("Mapa de ocupação dos assentos:")
    for num, ocupado in enumerate(assentos, start=1):
        status = "ocupado" if ocupado else "livre"
        print(f"Assento {num}: {status}")

def main():
    num_assentos = 10
    assentos = inicializar_assentos(num_assentos)

    while True:
        print("\nMenu:")
        print("1. Reservar um assento")
        print("2. Liberar um assento")
        print("3. Mostrar mapa de ocupação")
        print("4. Sair")

        opcao = input("Escolha uma opção (1/2/3/4): ")

        if opcao == "1":
            num_assento = int(input("Digite o número do assento que deseja reservar: "))
            reservar_assento(assentos, num_assento)
        elif opcao == "2":
            num_assento = int(input("Digite o número do assento que deseja liberar: "))
            liberar_assento(assentos, num_assento)
        elif opcao == "3":
            mostrar_mapa_ocupacao(assentos)
        elif opcao == "4":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Escolha uma opção válida (1/2/3/4).")

if __name__ == "__main__":
    main()
