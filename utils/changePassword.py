from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature
from datetime import datetime, timedelta
from models.user import TokenPayload
from database.client import db_client
import os

from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv("SECRET")
db = db_client


def generate_reset_token(email: str):
    # Crear un serializador con un tiempo de expiración de 15 minutos
    serializer = TimedJSONWebSignatureSerializer(SECRET, expires_in=900)

    try:
        # Crear la carga útil del token con el email y la fecha de expiración
        expiration = datetime.utcnow() + timedelta(minutes=15)
        token_payload = {"email": email, "exp": str(expiration)}
        print(token_payload)
        # Generar el token
        token = serializer.dumps(token_payload).decode("utf-8")
        return token
    except Exception as e:
        # Proporcionar detalles específicos sobre la excepción
        raise HTTPException(
            status_code=500, detail=f"Error al generar el token: {str(e)}"
        )


def send_password_reset_email(email, reset_link):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    sender_email = smtp_username
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Recuperación de contraseña"
    message["From"] = sender_email
    message["To"] = receiver_email

    # HTML body
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Recuperación de Contraseña - Egresoft</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
</head>
<body style="background-color: #f8f9fa; padding: 20px;">

    <div class="container" style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">

        <h2 class="text-center mb-4">Recuperación de Contraseña</h2>

        <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta.</p>

        <p class="text-center">
            <a href="{reset_link}" class="btn btn-primary">Restablecer Contraseña</a>
        </p>

        <p>Este enlace expirará en 15 minutos.</p>

        <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.</p>

    </div>

    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

</body>
</html>

    """

    # Attach HTML body to the message
    message.attach(MIMEText(html, "html"))

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def verify_token(token: str):
    # Buscar el token en la base de datos
    token_data = db.password_reset_tokens.find_one({"token": token})
    if not token_data:
        raise HTTPException(status_code=400, detail="Token no válido")

    try:
        # Crear un serializador con la misma clave secreta
        serializer = TimedJSONWebSignatureSerializer(SECRET, expires_in=900)

        # Deserializar el token y obtener la carga útil
        token_payload = serializer.loads(token)

        # Obtener el email de la carga útil
        email = token_payload["email"]

        # Obtener la fecha de expiración de la carga útil y convertirla a datetime
        expiration_str = token_payload["exp"]
        expiration = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S.%f")

        # Verificar la expiración del token
        if datetime.utcnow() > expiration:
            raise HTTPException(status_code=400, detail="Token expirado")

        # Resto de la lógica según sea necesario
        return email
    except SignatureExpired:
        # Manejar el caso en que el token ha expirado
        raise HTTPException(status_code=400, detail="Token expirado")
    except BadSignature:
        # Manejar el caso en que la firma del token es inválida
        raise HTTPException(status_code=400, detail="Token no válido")
    except Exception as e:
        # Manejar otras excepciones que puedan ocurrir
        raise HTTPException(
            status_code=500, detail=f"Error al verificar el token: {str(e)}"
        )


def update_password(email, new_password):
    # Actualizar la contraseña en la base de datos
    db.graduates.update_one({"email": email}, {"$set": {"password": new_password}})

    # Eliminar el token de restablecimiento de la base de datos
    db.password_reset_tokens.delete_one({"email": email})
