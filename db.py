import sqlite3
from typing import List, Optional
from werkzeug.security import generate_password_hash

DATABASE_PATH = 'data.db'
TABLE_PACIENTES = 'Pacientes'
TABLE_USUARIOS = 'usuario'

def obtener_conexion():
    return sqlite3.connect(DATABASE_PATH)

def handle_db_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            print(f"Database error in {func.__name__}: {e}")
            return None
    return wrapper

@handle_db_error
def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL,
                diagnostico TEXT NOT NULL
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_USUARIOS} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                contraseña TEXT NOT NULL
            )
        ''')
        conn.commit()

@handle_db_error
def agregar_paciente(nombre: str, edad: int, diagnostico: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Pacientes (nombre, edad, diagnostico) VALUES (?, ?, ?)', (nombre, edad, diagnostico))
        conn.commit()

@handle_db_error
def obtener_pacientes(limit=10, offset=0):
    conn = obtener_conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes LIMIT ? OFFSET ?", (limit, offset))
    pacientes = cursor.fetchall()
    conn.close()
    return pacientes

@handle_db_error
def contar_pacientes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Pacientes")
    total = cursor.fetchone()[0]
    conn.close()
    return total

@handle_db_error
def obtener_paciente_por_id(id: int) -> Optional[sqlite3.Row]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Pacientes WHERE id = ?', (id,))
        return cursor.fetchone()

@handle_db_error
def actualizar_paciente(id: int, nombre: str, edad: int, diagnostico: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE Pacientes SET nombre = ?, edad = ?, diagnostico = ? WHERE id = ?', (nombre, edad, diagnostico, id))
        conn.commit()

@handle_db_error
def eliminar_paciente(id: int) -> bool:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Pacientes WHERE id = ?', (id,))
        conn.commit()
        return cursor.rowcount > 0

@handle_db_error
def obtener_usuario(usuario: str) -> Optional[sqlite3.Row]:
    conn = obtener_conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario WHERE usuario = ?", (usuario,))
    user = cursor.fetchone()
    conn.close()
    return user

@handle_db_error
def agregar_usuario(usuario: str, contraseña_hash: str) -> bool:
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO usuario (usuario, contraseña) VALUES (?, ?)', (usuario, contraseña_hash))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

@handle_db_error
def buscar_pacientes_por_nombre(nombre: str, limit=10, offset=0):
    conn = obtener_conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    like_query = f"%{nombre}%"
    cursor.execute("SELECT * FROM Pacientes WHERE nombre LIKE ? LIMIT ? OFFSET ?", (like_query, limit, offset))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

@handle_db_error
def contar_pacientes_busqueda(nombre: str):
    conn = obtener_conexion()
    cursor = conn.cursor()
    like_query = f"%{nombre}%"
    cursor.execute("SELECT COUNT(*) FROM Pacientes WHERE nombre LIKE ?", (like_query,))
    total = cursor.fetchone()[0]
    conn.close()
    return total

@handle_db_error
def obtener_diagnosticos_unicos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT diagnostico FROM Pacientes ORDER BY diagnostico ASC")
    resultados = [row[0] for row in cursor.fetchall()]
    conn.close()
    return resultados

@handle_db_error
def buscar_pacientes_por_diagnostico(diagnostico: str, limit=10, offset=0):
    conn = obtener_conexion()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    like_query = f"%{diagnostico}%"
    cursor.execute('''
        SELECT * FROM Pacientes
        WHERE diagnostico LIKE ?
        LIMIT ? OFFSET ?
    ''', (like_query, limit, offset))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

@handle_db_error
def contar_pacientes_por_diagnostico(diagnostico: str):
    conn = obtener_conexion()
    cursor = conn.cursor()
    like_query = f"%{diagnostico}%"
    cursor.execute('''
        SELECT COUNT(*)
        FROM Pacientes
        WHERE diagnostico LIKE ?
    ''', (like_query,))
    total = cursor.fetchone()[0]
    conn.close()
    return total
