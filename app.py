from flask import Flask, request, render_template, redirect, url_for, session, flash
import logging
import db
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key from environment variables

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
            # Save the new patient to the database
            db.agregar_paciente(nombre, edad, diagnostico)
            flash('Paciente agregado exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error adding new paciente: {e}")
            flash('Error al agregar el paciente', 'error')
            return redirect(url_for('nuevo_paciente'))
    
    # Render the form for GET requests
    return render_template('nuevo_paciente.html')

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return render_template('error.html', message=e.description), e.code
    logger.error(f"Unhandled exception: {e}")
    return render_template('error.html', message="An unexpected error occurred."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Use environment variables for debug mode