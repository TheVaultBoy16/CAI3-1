# CAI3-1
CAI3-1 (sencilla, fasi, para toda la familia)


Preparación del entorno:

sudo apt update && sudo apt install uvicorn -y

pip install fastapi uvicorn sqlalchemy pyotp qrcode pillow bcrypt requests

Alternativamente:

sudo apt install python3-uvicorn python3-fastapi python3-sqlalchemy python3-pyotp python3-qrcode python3-pillow python3-bcrypt python3-requests 

Arrancar servidor:

uvicorn app.main:app --reload

Pruebas cliente:

python client.py 
