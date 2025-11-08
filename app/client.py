import requests
from io import BytesIO
from PIL import Image


BASE_URL = "http://127.0.0.1:8000"


def register_user(email: str, password: str):
    print("\nRegistrando nuevo usuario...")
    response = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})

    if response.status_code == 200:
        print("Usuario registrado correctamente.")
        img = Image.open(BytesIO(response.content))
        img.show()
        print("Escanea este QR con FREEOTP.")
        print("Luego usa tu app para generar el código OTP de 6 dígitos.")
    else:
        print("Error al registrar:", response.text)


def login_user(email: str, password: str):
    print("\nIniciando sesión...")
    response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
    if response.status_code == 200:
        print("Credenciales correctas. Ahora verifica el código 2FA.")
        return True
    else:
        print("Error al iniciar sesión:", response.text)
        return False


def verify_otp(email: str):
    """Solicita al usuario el código OTP de su app y lo envía al servidor."""
    print("\nVerificación 2FA")
    code = input("Introduce el código de 6 dígitos de tu app 2FA: ").strip()

    if not code.isdigit() or len(code) != 6:
        print("Código inválido. Debe ser un número de 6 dígitos.")
        return

    response = requests.post(f"{BASE_URL}/verify-2fa", json={"email": email, "code": code})

    if response.status_code == 200:
        print("Verificación 2FA exitosa:", response.json())
    else:
        print("Código incorrecto o expirado:", response.text)


def main():
    print("\n=== Cliente 2FA ===")
    print("1 Registrar nuevo usuario")
    print("2 Iniciar sesión con usuario existente")
    choice = input("\nElige una opción [1/2]: ").strip()

    email = input("\nEmail: ").strip()
    password = input("Contraseña: ").strip()

    if choice == "1":
        register_user(email, password)
        input("\nPresiona ENTER cuando hayas escaneado el QR y estés listo para probar el código OTP...")
        verify_otp(email)
    elif choice == "2":
        if login_user(email, password):
            verify_otp(email)
    else:
        print("Opción no válida.")


if __name__ == "__main__":
    main()
