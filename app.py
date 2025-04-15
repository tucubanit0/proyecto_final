import logging
import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, abort
from werkzeug.exceptions import HTTPException
import db
from datetime import datetime

# Crear carpeta de logs si no existe
os.makedirs('logs', exist_ok=True)

# Función para registrar logs
def registrar_log(accion, detalle):
    ruta_log = os.path.join('logs', 'actividad.txt')
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(ruta_log, 'a', encoding='utf-8') as archivo:
        archivo.write(f"[{fecha_hora}] {accion}: {detalle}\n")

# Configurar Flask
app = Flask(__name__, template_folder='d:/clase/proyecto_final/templates')
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Logging general
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar base de datos
try:
    db.init_db()
except Exception as e:
    logger.error(f"Error al inicializar la base de datos: {e}")
    raise

# Rutas
@app.route('/')
def index():
    try:
        pacientes = db.obtener_pacientes()
        return render_template('index.html', pacientes=pacientes)
    except Exception as e:
        logger.error(f"Error al obtener pacientes: {e}")
        return render_template('error.html', message="No se pudo obtener la información de los pacientes.")

@app.route('/nuevo_paciente', methods=['GET', 'POST'])
def nuevo_paciente():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        diagnostico = request.form.get('diagnostico')

        if not nombre or not edad or not diagnostico:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('nuevo_paciente'))

        try:
            edad = int(edad)
            db.agregar_paciente(nombre, edad, diagnostico)
            registrar_log("Nuevo paciente", f"{nombre}, {edad} años, diagnóstico: {diagnostico}")
            flash('Paciente agregado exitosamente', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('La edad debe ser un número entero', 'error')
        except Exception as e:
            logger.error(f"Error al agregar paciente: {e}")
            flash('Error al agregar el paciente', 'error')

        return redirect(url_for('nuevo_paciente'))

    return render_template('nuevo_paciente.html')

@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    try:
        paciente = db.obtener_paciente_por_id(id)
        if not paciente:
            abort(404, description="Paciente no encontrado")
    except Exception as e:
        logger.error(f"Error obteniendo paciente con ID {id}: {e}")
        abort(500, description="Error obteniendo datos del paciente.")

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        diagnostico = request.form.get('diagnostico')

        if not nombre or not edad or not diagnostico:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('editar_paciente', id=id))

        try:
            edad = int(edad)
            db.actualizar_paciente(id, nombre, edad, diagnostico)
            registrar_log("Editar paciente", f"ID {id} actualizado a: {nombre}, {edad} años, diagnóstico: {diagnostico}")
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('La edad debe ser un número entero', 'error')
        except Exception as e:
            logger.error(f"Error al actualizar paciente con ID {id}: {e}")
            flash('Error al actualizar el paciente', 'error')

        return redirect(url_for('editar_paciente', id=id))

    return render_template('editar_paciente.html', paciente=paciente)

@app.route('/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_paciente(id):
    try:
        paciente = db.obtener_paciente_por_id(id)
        if not paciente:
            flash('Paciente no encontrado.', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            db.eliminar_paciente(id)
            registrar_log("Eliminar paciente", f"ID {id} eliminado.")
            flash('Paciente eliminado correctamente.', 'success')
            return redirect(url_for('index'))

        return render_template('confirmar_eliminar.html', paciente=paciente)
    except Exception as e:
        logger.error(f"Error al eliminar paciente: {e}")
        flash('Ocurrió un error al eliminar el paciente.', 'error')
        return redirect(url_for('index'))

@app.route('/logs')
def ver_logs():
    ruta_log = os.path.join('logs', 'actividad.txt')
    try:
        with open(ruta_log, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        lineas = ["No hay actividad registrada aún."]
    return render_template("ver_logs.html", logs=lineas)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return render_template('error.html', message=e.description), e.code
    logger.error(f"Excepción no controlada: {e}")
    return render_template('error.html', message="Ha ocurrido un error inesperado."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'False') == 'True')
