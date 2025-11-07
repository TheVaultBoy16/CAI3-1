from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
from fastapi.responses import StreamingResponse
import qrcode
import pyotp

from . import models, schemas, utils
from .database import SessionLocal, engine, Base

# Crea las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependencia para obtener una sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = utils.hash_password(user.password)
    otp_secret = utils.generate_otp_secret()
    otp_secret_encrypted = utils.encrypt_secret(otp_secret)

    new_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        otp_secret_encrypted=otp_secret_encrypted
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Crear URI para escanear con Google Authenticator
    uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(
        name=user.email, issuer_name="MiAppSegura"
    )

    # Generar QR
    qr = qrcode.make(uri)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not utils.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {"msg": "Introduce tu código 2FA en /verify-2fa"}


@app.post("/verify-2fa")
def verify_2fa(data: schemas.Verify2FA, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == data.email).first()
    if not db_user or not db_user.otp_secret_encrypted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o sin 2FA")

    decrypted_secret = utils.decrypt_secret(db_user.otp_secret_encrypted)

    if utils.verify_otp(decrypted_secret, data.code):
        return {"msg": "✅ Verificación 2FA exitosa"}
    else:
        raise HTTPException(status_code=401, detail="Código 2FA inválido")
