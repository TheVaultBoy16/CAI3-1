import pyotp
from cryptography.fernet import Fernet
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ⚙️ Genera una clave secreta para cifrar los OTP
# (en producción, guarda esta clave en una variable de entorno segura)
fernet_key = Fernet.generate_key()
fernet = Fernet(fernet_key)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def encrypt_secret(secret: str):
    return fernet.encrypt(secret.encode()).decode()


def decrypt_secret(encrypted_secret: str):
    return fernet.decrypt(encrypted_secret.encode()).decode()


def generate_otp_secret():
    return pyotp.random_base32()


def verify_otp(secret: str, code: str):
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
