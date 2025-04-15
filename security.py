import hashlib #generar los hashes de las contraseñas

# Función para generar un hash de una contraseña
def hash_password(password):
    # Utiliza SHA-256 para generar un hash de la contraseña
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    # Verifica si la contraseña proporcionada coincide con el hash almacenado
    return hash_password(password) == hashed_password