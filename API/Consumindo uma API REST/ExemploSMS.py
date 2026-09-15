from twilio.rest import Client
account_sid = "SEU_ACCOUNT_SID_TWILIO"
auth_token = "SEU_AUTH_TOKEN_TWILIO"
client = Client(account_sid, auth_token)
message = client.messages.create(
 from_="+SEU_TELEFONE_TWILIO",
 body="Olá estudante do IFB, é uma satisfação ter você aqui, aproveite a jornada.",
 to='+TELEFONE_DESTINO='
)
print(message.sid)