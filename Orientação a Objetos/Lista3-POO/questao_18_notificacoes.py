from abc import ABC, abstractmethod


class Notificador(ABC):
    @abstractmethod
    def enviar(self, mensagem):
        pass


class NotificadorEmail(Notificador):
    def enviar(self, mensagem):
        print(f"E-mail enviado: {mensagem}")


class NotificadorSMS(Notificador):
    def enviar(self, mensagem):
        print(f"SMS enviado: {mensagem}")


class NotificadorAplicativo(Notificador):
    def enviar(self, mensagem):
        print(f"Notificação no aplicativo: {mensagem}")


def enviar_notificacao(notificador, mensagem):
    # A função depende apenas da abstração Notificador.
    notificador.enviar(mensagem)


if __name__ == "__main__":
    notificadores = [NotificadorEmail(), NotificadorSMS(), NotificadorAplicativo()]
    for item in notificadores:
        enviar_notificacao(item, "Sua solicitação foi processada.")
