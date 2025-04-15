import datetime

def registrar_log(accion, detalle):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {accion} - {detalle}\n"
    try:
        with open("logs.txt", "a", encoding="utf-8") as archivo:
            archivo.write(linea)
    except Exception as e:
        print(f"Error al escribir en el log: {e}")
