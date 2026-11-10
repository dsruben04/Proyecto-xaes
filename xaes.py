import sys,os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def derivar_key_iv(contrasenya:bytes, sal:bytes) -> tuple: 
    pbkdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sal,
        iterations=10000
    )
    derivado=pbkdf.derive(contrasenya)
    clave=derivado[:16]
    iv=derivado[16:]
    return (clave,iv)

if __name__ == "__main__":
    
    if len(sys.argv)<3:
        print("Uso: ./xaes.py [-e|-d] <contraseña>", file = sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    contrasenya: bytes = sys.argv[2].encode()

    datos_input = sys.stdin.buffer.read()

    if sys.argv[1] == '-e':
        
        sal :bytes = os.urandom(8)
        key, iv = derivar_key_iv(contrasenya, sal)
        relleno = padding.PKCS7(128).padder()
        datos_llenos = relleno.update(datos_input) + relleno.finalize() #Rellena los datos imput con el padding

        cifrador = Cipher(algorithms.AES(key), modes.CBC(iv))
        encriptador = cifrador.encryptor()
        datos_cifrados = encriptador.update(datos_llenos) +encriptador.finalize()
        output= b'Salted__' + sal + datos_cifrados
        sys.stdout.buffer.write(output)


    elif sys.argv[1] == '-d':
        if datos_input[:8] != b'Salted__': 
            print("Error, el archivo no compienza por 'Salted__'")
            sys.exit(1)
        sal = datos_input[8:16]
        datos_cifrados = datos_input[16:]

        key, iv = derivar_key_iv(contrasenya, sal)

        cifrador = Cipher(algorithms.AES(key), modes.CBC(iv))
        descifrador = cifrador.decryptor()
        datos_descifrados_relleno = descifrador.update(datos_cifrados) + descifrador.finalize()

        quitar_relleno = padding.PKCS7(128).unpadder()
        sol = quitar_relleno.update(datos_descifrados_relleno) + quitar_relleno.finalize()

        sys.stdout.buffer.write(sol)
    

