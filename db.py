import sqlite3
from typing import List, Optional, Union

DATABASE_PATH = 'data.db'
TABLE_PACIENTES = 'Pacientes'
TABLE_USUARIOS = 'usuario'

# Column names for Pacientes table
COLUMN_ID = 'id'
COLUMN_NOMBRE = 'nombre'
COLUMN_EDAD = 'edad'
COLUMN_DIAGNOSTICO = 'diagnostico'

# Column names for Usuarios table
COLUMN_USUARIO = 'usuario'
COLUMN_CONTRASEÑA = 'contraseña'


def handle_db_error(func):
    """Decorator to handle database errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            print(f"Database error in {func.__name__}: {e}")
            return None
    return wrapper


@handle_db_error
def init_db() -> None:
    """Initialize the database and create tables if they don't exist."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_PACIENTES} (
                {COLUMN_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {COLUMN_NOMBRE} TEXT NOT NULL,
                {COLUMN_EDAD} INTEGER NOT NULL,
                {COLUMN_DIAGNOSTICO} TEXT NOT NULL
            )
        ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_USUARIOS} (
                {COLUMN_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {COLUMN_USUARIO} TEXT NOT NULL UNIQUE,
                {COLUMN_CONTRASEÑA} TEXT NOT NULL
            )
        ''')
        conn.commit()


@handle_db_error
def agregar_paciente(nombre: str, edad: int, diagnostico: str) -> None:
    """Add a new patient to the database."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO {TABLE_PACIENTES} ({COLUMN_NOMBRE}, {COLUMN_EDAD}, {COLUMN_DIAGNOSTICO})
            VALUES (?, ?, ?)
        ''', (nombre, edad, diagnostico))
        conn.commit()


@handle_db_error
def obtener_pacientes() -> List[sqlite3.Row]:
    """Retrieve all patients from the database."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {TABLE_PACIENTES}')
        return cursor.fetchall()


@handle_db_error
def obtener_paciente_por_id(id: int) -> Optional[sqlite3.Row]:
    """Retrieve a patient by their ID."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {TABLE_PACIENTES} WHERE {COLUMN_ID} = ?', (id,))
        return cursor.fetchone()


@handle_db_error
def actualizar_paciente(id: int, nombre: str, edad: int, diagnostico: str) -> None:
    """Update a patient's information."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE {TABLE_PACIENTES}
            SET {COLUMN_NOMBRE} = ?, {COLUMN_EDAD} = ?, {COLUMN_DIAGNOSTICO} = ?
            WHERE {COLUMN_ID} = ?
        ''', (nombre, edad, diagnostico, id))
        conn.commit()


@handle_db_error
def eliminar_paciente(id: int) -> bool:
    """Delete a patient from the database. Returns True if deleted, False if not found."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {TABLE_PACIENTES} WHERE {COLUMN_ID} = ?', (id,))
        conn.commit()
        return cursor.rowcount > 0