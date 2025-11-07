from fastapi import FastAPI, HTTPException, Depends, Form
from pydantic import BaseModel
import pyotp
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

app = FastAPI()

# Simulamos una base de datos en memoria
fake_users_db = {
    "usuario@ejemplo.com": {
        "password": "123456",  # En producción deberías usar hash
        "otp_secret": None
    }
}


class LoginRequest(BaseModel):
    email: str
    password: str


class Verify2FARequest(BaseModel):
    email: str
    code: str


@app.post("/login")
def login(data: LoginRequest):
    user = fake_users_db.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Si el usuario no tiene 2FA configurado, lo generamos
    if not user["otp_secret"]:
        secret = pyotp.random_base32()
        user["otp_secret"] = secret
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=data.email, issuer_name="MiAppSegura"
        )

        # Generamos QR para escanear con Google Authenticator
        qr = qrcode.make(uri)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        buf.seek(0)

        return StreamingResponse(buf, media_type="image/png")

    return {"msg": "2FA ya configurado. Usa /verify-2fa para verificar."}


@app.post("/verify-2fa")
def verify_2fa(data: Verify2FARequest):
    user = fake_users_db.get(data.email)
    if not user or not user["otp_secret"]:
        raise HTTPException(status_code=404, detail="Usuario o 2FA no encontrado")

    totp = pyotp.TOTP(user["otp_secret"])
    if totp.verify(data.code, valid_window=1):
        return {"msg": "✅ Login exitoso"}
    else:
        raise HTTPException(status_code=401, detail="Código 2FA inválido")
