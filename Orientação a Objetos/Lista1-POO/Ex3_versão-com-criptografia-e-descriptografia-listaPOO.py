class Criptografo:
    def __init__(self, frase):
        self.frase = frase

    def criptografar(self):
        # Dicionário com as trocas: vogal -> número
        mapa = {
            "a": "4",
            "e": "3",
            "i": "1",
            "o": "0",
            "u": "8"
        }

        texto_final = ""
        for letra in self.frase:
            if letra.lower() in mapa:
                texto_final += mapa[letra.lower()]
            else:
                texto_final += letra
        return texto_final

    def descriptografar(self):
        # Dicionário com as trocas inversas: número -> vogal
        mapa_inverso = {
            "4": "a",
            "3": "e",
            "1": "i",
            "0": "o",
            "8": "u"
        }

        texto_final = ""
        for letra in self.frase:
            if letra in mapa_inverso:
                texto_final += mapa_inverso[letra]
            else:
                texto_final += letra
        return texto_final


# Programa principal
if __name__ == "__main__":
    frase = input("Digite uma frase: ")

    # Criar objeto e criptografar
    cript = Criptografo(frase)
    frase_criptografada = cript.criptografar()

    # Criar outro objeto para descriptografar
    descript = Criptografo(frase_criptografada)
    frase_descriptografada = descript.descriptografar()

    print("\n=== RESULTADOS ===")
    print("Frase original:       ", frase)
    print("Frase criptografada:  ", frase_criptografada)
    print("Frase descriptografada:", frase_descriptografada)
