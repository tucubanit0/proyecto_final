from livereload import Server
from app import app  # Importa la instancia de Flask directamente

server = Server(app.wsgi_app)

# Vigila las carpetas necesarias
server.watch('templates/')
server.watch('static/css/')
server.watch('static/js/')

# Corre el servidor en 127.0.0.1:5500
server.serve(port=5500, host='127.0.0.1', debug=True)
