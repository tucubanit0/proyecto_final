import logging
import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, abort
from werkzeug.exceptions import HTTPException
import db
from datetime import datetime



app = Flask(__name__, template_folder='d:/clase/proyecto_final/templates')
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Use environment variable for secret key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the database
try:
    db.init_db()
except Exception as e:
    logger.error(f"Failed to initialize the database: {e}")
    raise

@app.route('/')
def index():
    try:
        pacientes = db.obtener_pacientes()  # Fetch patients from the database
        return render_template('index.html', pacientes=pacientes)
    except Exception as e:
        logger.error(f"Error retrieving pacientes: {e}")
        return render_template('error.html', message="Failed to retrieve patient data.")

@app.route('/nuevo_paciente', methods=['GET', 'POST'])
def nuevo_paciente():
    if request.method == 'POST':
        # Get form data
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        diagnostico = request.form.get('diagnostico')
        
        if not nombre or not edad or not diagnostico:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('nuevo_paciente'))
        
        try:
            edad = int(edad)  # Validate edad as an integer
            db.agregar_paciente(nombre, edad, diagnostico)  # Save the new patient to the database
            flash('Paciente agregado exitosamente', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('La edad debe ser un número entero', 'error')
        except Exception as e:
            logger.error(f"Error adding new paciente: {e}")
            flash('Error al agregar el paciente', 'error')
        
        return redirect(url_for('nuevo_paciente'))
    
    # Render the form for GET requests
    return render_template('nuevo_paciente.html')

@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    try:
        paciente = db.obtener_paciente_por_id(id)  # Fetch patient by ID
        if not paciente:
            abort(404, description="Paciente no encontrado")
    except Exception as e:
        logger.error(f"Error fetching paciente with ID {id}: {e}")
        abort(500, description="Error retrieving patient data")
    
    if request.method == 'POST':
        # Get form data
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        diagnostico = request.form.get('diagnostico')
        
        if not nombre or not edad or not diagnostico:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('editar_paciente', id=id))
        
        try:
            edad = int(edad)  # Validate edad as an integer
            db.actualizar_paciente(id, nombre, edad, diagnostico)  # Update patient in the database
            flash('Paciente actualizado exitosamente', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('La edad debe ser un número entero', 'error')
        except Exception as e:
            logger.error(f"Error updating paciente with ID {id}: {e}")
            flash('Error al actualizar el paciente', 'error')
        
        return redirect(url_for('editar_paciente', id=id))
    
    return render_template('editar_paciente.html', paciente=paciente)

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return render_template('error.html', message=e.description), e.code
    logger.error(f"Unhandled exception: {e}")
    return render_template('error.html', message="An unexpected error occurred."), 500

@app.route('/eliminar_paciente/<int:id>', methods=['POST', 'GET'])
def eliminar_paciente(id):
    try:
        # Verify if the patient exists before attempting deletion
        paciente = db.obtener_paciente_por_id(id)
        if not paciente:
            flash('Paciente no encontrado.', 'error')
            return redirect(url_for('index'))
        
        # Perform the deletion
        db.eliminar_paciente(id)
        flash('Paciente eliminado correctamente.', 'success')
    except db.DatabaseError as db_err:
        logger.error(f"Database error while deleting paciente with ID {id}: {db_err}")
        flash('Error de base de datos al eliminar el paciente.', 'error')
    except Exception as e:
        logger.error(f"Unexpected error while deleting paciente with ID {id}: {e}")
        flash('Ocurrió un error inesperado al eliminar el paciente.', 'error')
    
    return redirect(url_for('index'))

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'False') == 'True')