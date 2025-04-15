# Utilizar este script para migrar datos de un archivo CSV a una base de datos SQLite.
# Revisa que las columnas en el csv empiecen con mayúscula y en el db.py con minúscula y sin tilde 
# Debe verse así:
#f'''INSERT INTO {TABLE} (nombre, edad, diagnostico) VALUES (?, ?, ?)''',
                    #(row['Nombre'], int(row['Edad']), row['Diagnóstico'])
import csv
import sqlite3

CSV_FILE = 'data.csv'
DB_FILE = 'data.db'
TABLE = 'Pacientes'

def migrar_csv_a_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cursor.execute(
                    f'''INSERT INTO {TABLE} (nombre, edad, diagnostico) VALUES (?, ?, ?)''',
                    (row['Nombre'], int(row['Edad']), row['Diagnóstico'])
                )
        conn.commit()
    print("Migración completada.")

if __name__ == '__main__':
    migrar_csv_a_db()