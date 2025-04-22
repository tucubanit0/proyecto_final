import os
import logging
from flask import Flask, request, render_template, redirect, url_for, session, flash, abort, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from datetime import datetime
import db
import csv
import io
import openpyxl
from db import obtener_pacientes

# Configurar Flask
app = Flask(__name__, template_folder='d:/clase/proyecto_final/templates')
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Configuración de logs
os.makedirs('logs', exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def registrar_log(accion, detalle):
    ruta_log = os.path.join('logs', 'actividad.txt')
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    usuario = session.get('usuario', 'Desconocido')
    with open(ruta_log, 'a', encoding='utf-8') as archivo:
        archivo.write(f"[{fecha_hora}] ({usuario}) {accion}: {detalle}\n")

# Inicializar base de datos
try:
    db.init_db()
except Exception as e:
    logger.error(f"Error al inicializar la base de datos: {e}")
    raise

@app.before_request
def requerir_login():
    rutas_abiertas = ['login', 'registro_usuario', 'static']
    if not session.get('usuario') and not any(r in request.endpoint for r in rutas_abiertas):
        return redirect(url_for('login'))

@app.route('/')
def index():
    try:
        por_pagina = 10
        pagina = int(request.args.get('pagina', 1))
        offset = (pagina - 1) * por_pagina
        busqueda = request.args.get('buscar', '').strip()
        filtro = request.args.get('filtro', 'nombre')  # puede ser 'nombre' o 'diagnostico'

        if busqueda:
            filtro = request.args.get('filtro', 'nombre')
            if filtro == 'diagnostico':
                pacientes = db.buscar_pacientes_por_diagnostico(busqueda, limit=por_pagina, offset=offset)
                total_pacientes = db.contar_pacientes_por_diagnostico(busqueda)
            else:
                pacientes = db.buscar_pacientes_por_nombre(busqueda, limit=por_pagina, offset=offset)
                total_pacientes = db.contar_pacientes_busqueda(busqueda)
        else:
            pacientes = db.obtener_pacientes(limit=por_pagina, offset=offset)
            total_pacientes = db.contar_pacientes()


        total_paginas = (total_pacientes + por_pagina - 1) // por_pagina

        return render_template('index.html', pacientes=pacientes, pagina=pagina,
                               total_paginas=total_paginas, buscar=busqueda, filtro=filtro)
    except Exception as e:
        logger.error(f"Error al obtener pacientes: {e}")
        return render_template('error.html', message="No se pudo obtener la lista de pacientes.")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contraseña = request.form.get('contraseña')
        user = db.obtener_usuario(usuario)
        if user and check_password_hash(user['contraseña'], contraseña):
            session['usuario'] = user['usuario']
            flash('Sesión iniciada correctamente', 'success')
            return redirect(url_for('index'))
        flash('Credenciales inválidas', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro_usuario():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contraseña = request.form.get('contraseña')
        if not usuario or not contraseña:
            flash('Todos los campos son obligatorios.', 'error')
        else:
            hash_contraseña = generate_password_hash(contraseña)
            exito = db.agregar_usuario(usuario, hash_contraseña)
            if exito:
                flash('Usuario registrado exitosamente.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error: el nombre de usuario ya existe.', 'error')
    return render_template('registro.html')

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
            registrar_log("Nuevo paciente", f"{session['usuario']} agregó a {nombre}, {edad} años, diagnóstico: {diagnostico}")
            flash('Paciente agregado exitosamente', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('La edad debe ser un número entero', 'error')

    diagnosticos = db.obtener_diagnosticos_unicos()
    return render_template('nuevo_paciente.html', diagnosticos=diagnosticos)

@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    paciente = db.obtener_paciente_por_id(id)
    if not paciente:
        abort(404)

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
            registrar_log("Editar paciente", f"{session['usuario']} editó ID {id}: {nombre}, {edad} años, diagnóstico: {diagnostico}")
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('La edad debe ser un número entero', 'error')

    diagnosticos = db.obtener_diagnosticos_unicos()
    return render_template('editar_paciente.html', paciente=paciente, diagnosticos=diagnosticos)

@app.route('/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_paciente(id):
    try:
        paciente = db.obtener_paciente_por_id(id)
        if not paciente:
            flash('Paciente no encontrado.', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            db.eliminar_paciente(id)
            registrar_log("Eliminar paciente", f"ID {id} eliminado ({paciente['nombre']}, {paciente['edad']} años, {paciente['diagnostico']})")
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

@app.route('/estadisticas')
def estadisticas():
    try:
        datos = db.obtener_cantidad_por_diagnostico()
        etiquetas = [row['diagnostico'] for row in datos]
        cantidades = [row['cantidad'] for row in datos]
        return render_template('estadisticas.html', etiquetas=etiquetas, cantidades=cantidades)
    except Exception as e:
        logger.error(f"Error al cargar estadísticas: {e}")
        flash('Error al cargar estadísticas.', 'error')
        return redirect(url_for('index'))
    

@app.route('/exportar/csv')
def exportar_csv():
    pacientes = obtener_pacientes(limit=1000000)  # ajusta si necesitas más
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Edad', 'Diagnóstico'])  # Encabezados
    for p in pacientes:
        writer.writerow([p['id'], p['nombre'], p['edad'], p['diagnostico']])  # Fixed key
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='pacientes.csv')


@app.route('/exportar/excel')
def exportar_excel():
    pacientes = obtener_pacientes(limit=1000000)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Pacientes'

    # Encabezados
    ws.append(['ID', 'Nombre', 'Edad', 'Diagnóstico'])

    # Datos
    for p in pacientes:
        ws.append([p['id'], p['nombre'], p['edad'], p['diagnostico']])  # Fixed key

    # Guardar en memoria
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output,
                     as_attachment=True,
                     download_name='pacientes.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'False') == 'True')
