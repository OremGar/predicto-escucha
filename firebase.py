from firebase_admin import messaging

def EnviaNotificacion(titulo, cuerpo, destinos):
    message = messaging.MulticastMessage(
        tokens=destinos,
        notification=messaging.Notification(
        title=titulo,
        body=cuerpo
        ),
    )

    return messaging.send_multicast(message)
    